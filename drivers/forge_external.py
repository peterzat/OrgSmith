"""Provider-neutral authoring driver: generate an org without the Claude Code
harness, using a bring-your-own-token provider.

This is the first non-skill implementation of OrgSmith's published interface:
`WorkOrder JSON -> AuthorAdapter -> Deliverable JSON`. It sits in the exact
position a `forge-author` worker sits, consume a work order, author the
deliverable, hand it to `orgsmith ... --ingest`, but the author is a
user-configured API model instead of the ambient session.

Off by default: with no provider selected the driver is inert and exits 0
without mutating anything. Enable it by setting `ORGSMITH_AUTHOR_PROVIDER`
(and the provider's key); see `--check` and docs/BYO-AUTHORING.md.

Usage:
    python -m drivers.forge_external --check
    python -m drivers.forge_external <slug> [--provider NAME] [--root DIR]
                                            [--only enrich|author]
                                            [--max-retries N] [--dry-run]

The airlock is untouched: `orgsmith` still never calls a model or the
network. This driver does, from outside the `orgsmith/` package, and drives
the same deterministic CLI verbs the skills drive.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from orgsmith.paths import OrgPaths, org_paths
from orgsmith.schemas import AuthoringDeliverable, EnrichmentDeliverable
from orgsmith.state import load_state

from .config import (
    author_effort,
    base_url_for,
    key_for,
    load_provider_env,
    missing_requirements,
    model_for,
    providers_env_path,
    select_provider,
    selected_provider_name,
)
from .providers import DEFAULT_MAX_TOKENS, call_provider

SYSTEM_PROMPT = """\
You are an author inside a synthetic-organization document-generation
pipeline. You receive one work-order JSON and produce ONLY the deliverable
JSON it asks for.

Writing quality:
- A reader must believe a person at this firm wrote this in that year. Match
  the org narrative's voice, vary sentence rhythm, avoid any template feel,
  and use no modern AI-assistant tone. Nothing may read as though one person
  wrote every document.
- Era-appropriate: nothing in the text may postdate the document's date
  (tools, idioms, events).
- Placeholders are sacred: every briefed fact id must appear as
  {{fact:<id>}} exactly, with the id verbatim including its prefix. You never
  know the underlying value; never write a number, date, or name where a
  placeholder belongs. Write so the substituted value reads naturally.
- People are only those named in the briefs, with their exact names and
  titles. Invent no people, organizations, addresses, amounts, or dates.
- Every surface string in a brief's `mentions` list must appear verbatim in
  that document's text (sigblock signers cover themselves).
- Respect the genre structure each brief's `guidance` describes.

Output contract:
- Follow the work order's `instructions` field exactly; it is the binding
  contract, including the exact `schema_id` and `work_order_id` to echo.
- Output ONLY the deliverable JSON: a single JSON object, no prose, no
  explanation, no markdown code fences.
"""


class DriverError(Exception):
    """A hard stop: the run cannot continue and must fail loudly."""


@dataclass(frozen=True)
class Resolved:
    provider: object  # drivers.config.Provider
    base_url: str
    model: str
    generator_model: str
    effort: str
    timeout: int
    max_tokens: int
    max_retries: int


# --- model reply parsing ---------------------------------------------------


def extract_json(text: str) -> dict:
    """Return the first balanced top-level JSON object in `text`.

    Tolerates code fences and surrounding prose by scanning from the first
    `{` to its matching `}`, honoring string literals so a brace inside a
    string does not miscount. Raises DriverError when no balanced object is
    found, so the caller can fold it into the repair loop.
    """
    start = text.find("{")
    if start == -1:
        raise DriverError("no JSON object in reply")
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                fragment = text[start : i + 1]
                try:
                    return json.loads(fragment)
                except ValueError as err:
                    raise DriverError(f"reply is not valid JSON ({err})") from None
    raise DriverError("unbalanced JSON object in reply")


def _user_prompt(work_order_json: str, feedback: str | None) -> str:
    prompt = (
        "Here is your work order as JSON. Follow its `instructions` field "
        "exactly and output ONLY the deliverable JSON it describes, nothing "
        "else.\n\n" + work_order_json
    )
    if feedback:
        prompt += (
            "\n\n---\nYour previous reply was rejected:\n"
            + feedback
            + "\n\nFix every problem and resend the COMPLETE deliverable JSON "
            "(all documents), with no other text."
        )
    return prompt


# --- orgsmith CLI plumbing -------------------------------------------------


def run_cli(paths: OrgPaths, verb: str, *extra: str) -> tuple[int, str]:
    """Run a deterministic `orgsmith` verb as a subprocess and return
    (returncode, combined stdout+stderr). Always pins `--root` so the
    subprocess resolves the same tree the driver does, regardless of cwd."""
    cmd = [
        sys.executable, "-m", "orgsmith", verb, paths.slug, *extra,
        "--root", str(paths.root),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


# --- one work order: author, validate, ingest, repair ----------------------


def author_and_ingest(
    paths: OrgPaths, resolved: Resolved, verb: str, wo_path: Path, deliverable_cls
) -> None:
    """Author one work order and ingest it, repairing on rejection.

    `verb` is the orgsmith verb whose `--ingest` merges this deliverable
    ("foundation" or "author"). A None from the provider (fail-open adapter)
    is a hard stop here: a missing document breaks the pipeline. On an
    `--ingest` (or local schema) rejection, the model is re-prompted with the
    rejection text, up to `resolved.max_retries` times, then fails loudly.
    """
    work_order_json = wo_path.read_text("utf-8")
    wo_id = json.loads(work_order_json)["id"]
    reply_path = paths.workorders_dir / f"reply-{wo_id.replace(':', '-')}.json"

    feedback: str | None = None
    for attempt in range(resolved.max_retries + 1):
        label = f"attempt {attempt + 1}/{resolved.max_retries + 1}"
        text = call_provider(
            resolved.provider,
            system=SYSTEM_PROMPT,
            user=_user_prompt(work_order_json, feedback),
            model=resolved.model,
            timeout=resolved.timeout,
            max_tokens=resolved.max_tokens,
        )
        if text is None:
            raise DriverError(
                f"{resolved.provider.name} returned no content for {wo_id} "
                f"(see stderr for the reason)"
            )
        try:
            obj = extract_json(text)
        except DriverError as err:
            feedback = f"{err}. Resend ONLY the deliverable JSON object."
            print(f"  {wo_id}: {err} ({label})")
            continue
        obj["generator"] = {
            "model": resolved.generator_model,
            "effort": resolved.effort,
        }
        try:
            deliverable_cls.model_validate(obj)
        except ValidationError as err:
            feedback = f"Schema validation failed:\n{err}"
            print(f"  {wo_id}: local schema check failed ({label})")
            continue
        reply_path.write_text(
            json.dumps(obj, ensure_ascii=False, indent=2), "utf-8"
        )
        rc, out = run_cli(paths, verb, "--ingest", str(reply_path))
        if rc == 0:
            print(f"  {wo_id}: ingested ({reply_path.name})")
            return
        feedback = out.strip()
        print(f"  {wo_id}: ingest rejected ({label})")
    raise DriverError(
        f"{wo_id}: still rejected after {resolved.max_retries} retries:\n{feedback}"
    )


# --- the two model passes --------------------------------------------------


def run_pure_stages(paths: OrgPaths) -> None:
    """The deterministic, model-free stages before authoring. Idempotent, so
    a resume re-runs them harmlessly."""
    for args in (
        ("charter",),
        ("foundation", "--scaffold"),
        ("fabric",),
        ("docplan",),
    ):
        rc, out = run_cli(paths, *args)
        if rc != 0:
            raise DriverError(f"{' '.join(args)} failed:\n{out}")


def drive_enrichment(paths: OrgPaths, resolved: Resolved) -> None:
    rc, out = run_cli(paths, "foundation", "--emit-context")
    if rc != 0:
        raise DriverError(f"foundation --emit-context failed:\n{out}")
    state = load_state(paths)
    if state.stage_done("foundation_enrich"):
        print("foundation enrichment: already merged")
        return
    name = state.outstanding.get("foundation")
    if not name:
        print("foundation enrichment: nothing to author")
        return
    print(f"foundation enrichment: authoring {name} via {resolved.provider.name}")
    author_and_ingest(
        paths, resolved, "foundation",
        paths.workorders_dir / name, EnrichmentDeliverable,
    )


def _drain_author_batches(paths: OrgPaths, resolved: Resolved) -> int:
    """Author and ingest every outstanding author batch, serially. Each
    successful ingest clears its batch from state, so reloading finds the
    next; a repair-exhausted batch raises and aborts the run. Returns the
    number drained."""
    count = 0
    while True:
        state = load_state(paths)
        if not state.author_batches:
            return count
        wo_id, ref = next(iter(state.author_batches.items()))
        print(
            f"authoring batch {wo_id} ({len(ref.doc_ids)} docs) "
            f"via {resolved.provider.name}"
        )
        author_and_ingest(
            paths, resolved, "author",
            paths.workorders_dir / ref.workorder, AuthoringDeliverable,
        )
        count += 1


def drive_authoring(paths: OrgPaths, resolved: Resolved) -> None:
    while True:
        rc, out = run_cli(paths, "author", "--next-batch")
        if rc != 0:
            raise DriverError(f"author --next-batch failed:\n{out}")
        if "all batchable docs authored" in out:
            print("authoring: all batchable docs authored")
            return
        drained = _drain_author_batches(paths, resolved)
        if drained == 0:
            raise DriverError(
                f"author --next-batch emitted no batch and did not report "
                f"completion:\n{out}"
            )
        rc, out = run_cli(paths, "render")
        if rc != 0:
            raise DriverError(f"render failed:\n{out}")


def finish(paths: OrgPaths) -> int:
    """The pure closing stages. `validate` failing is surfaced and returned,
    not raised: it is a report on the org, not a driver fault."""
    for verb in ("render", "assemble", "acl", "validate", "report"):
        rc, out = run_cli(paths, verb)
        if out.strip():
            print(out.strip())
        if rc != 0:
            if verb == "validate":
                print("validate reported problems (see above).")
                return rc
            raise DriverError(f"{verb} failed:\n{out}")
    return 0


def drive_org(
    slug: str, root: Path | None, resolved: Resolved, only: str | None
) -> int:
    paths = org_paths(slug, root)
    run_pure_stages(paths)
    if only != "author":
        drive_enrichment(paths, resolved)
    if only != "enrich":
        drive_authoring(paths, resolved)
        return finish(paths)
    return 0


# --- preflight and entry point ---------------------------------------------


def check(explicit: str | None) -> int:
    path = providers_env_path()
    file_state = "present" if path.exists() else "absent"
    name = selected_provider_name(explicit)
    if name is None:
        print("BYO authoring: OFF (no provider selected).")
        print(f"  config file: {path} ({file_state})")
        print(
            "  to enable: set ORGSMITH_AUTHOR_PROVIDER to one of "
            "openai|anthropic|google|openrouter|local, plus its api key."
        )
        print("  see docs/BYO-AUTHORING.md.")
        return 0
    try:
        provider = select_provider(explicit)
    except KeyError as err:
        print(f"BYO authoring: ERROR {err}", file=sys.stderr)
        return 2
    assert provider is not None
    print(f"BYO authoring: provider={provider.name} shape={provider.shape}")
    print(f"  base_url: {base_url_for(provider) or '(unset)'}")
    print(f"  model:    {model_for(provider) or '(unset)'}")
    print(f"  effort:   {author_effort()}")
    key_state = "present" if key_for(provider) is not None else "absent"
    print(f"  api key:  {key_state} ({provider.key_env})")
    print(f"  config:   {path} ({file_state})")
    missing = missing_requirements(provider)
    if missing:
        print(f"  NOT READY: missing {', '.join(missing)}", file=sys.stderr)
        return 1
    print("  ready.")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drivers.forge_external",
        description="Generate an OrgSmith org via a bring-your-own-token provider.",
    )
    parser.add_argument("slug", nargs="?", help="recipe/org slug, e.g. dev-mini")
    parser.add_argument("--root", type=Path, default=None, help="repo root")
    parser.add_argument(
        "--provider", default=None,
        help="override ORGSMITH_AUTHOR_PROVIDER for this run",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="report the configured provider and readiness, then exit",
    )
    parser.add_argument(
        "--only", choices=["enrich", "author"], default=None,
        help="restrict which model pass runs (pure stages always run)",
    )
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument(
        "--dry-run", action="store_true",
        help="resolve the provider and print what would run, without calling it",
    )
    return parser


def main(argv=None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    load_provider_env()

    if args.check:
        return check(args.provider)

    try:
        provider = select_provider(args.provider)
    except KeyError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2

    if provider is None:
        print("BYO authoring is off (no provider selected); nothing to do.")
        print(
            "set ORGSMITH_AUTHOR_PROVIDER to enable, or run /forge under "
            "Claude Code. `--check` shows the current config; see "
            "docs/BYO-AUTHORING.md."
        )
        return 0

    if args.slug is None:
        parser.error("a slug is required to author (or pass --check)")

    missing = missing_requirements(provider)
    if missing:
        print(
            f"error: provider {provider.name} is not ready: missing "
            f"{', '.join(missing)}",
            file=sys.stderr,
        )
        print(
            "run `python -m drivers.forge_external --check` for details",
            file=sys.stderr,
        )
        return 1

    model = model_for(provider)
    resolved = Resolved(
        provider=provider,
        base_url=base_url_for(provider),
        model=model,
        generator_model=f"{provider.name}:{model}",
        effort=author_effort(),
        timeout=args.timeout,
        max_tokens=args.max_tokens,
        max_retries=args.max_retries,
    )

    if args.dry_run:
        print(
            f"[dry-run] would author {args.slug} via {resolved.provider.name} "
            f"/ {resolved.model} at effort {resolved.effort} "
            f"(base_url {resolved.base_url})"
        )
        return 0

    try:
        return drive_org(args.slug, args.root, resolved, args.only)
    except DriverError as err:
        print(f"\nBYO driver stopped: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
