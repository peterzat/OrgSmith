"""charter stage: parse and validate recipes/<slug>/ORG-CHARTER.md.

Pure. Extracts the fenced yaml block as structured fields and the
surrounding prose as the narrative brief, validates the Charter contract,
and writes companies/<slug>-metadata/charter.json.
"""

from __future__ import annotations

import re

import yaml

from .namescreen import screen_charter
from .paths import OrgPaths
from .schemas import Charter, dump_json, write_model
from .state import load_state, save_state, sha256_file

_YAML_BLOCK = re.compile(r"^```yaml\s*$(.*?)^```\s*$", re.MULTILINE | re.DOTALL)


def parse_charter_md(text: str, slug: str) -> Charter:
    match = _YAML_BLOCK.search(text)
    if not match:
        raise SystemExit("ORG-CHARTER.md has no fenced ```yaml block")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise SystemExit("charter yaml block must be a mapping")
    if "narrative" in data:
        raise SystemExit("narrative belongs in prose, not the yaml block")

    prose = (text[: match.start()] + text[match.end() :]).strip()
    prose = re.sub(r"^#\s+.*$", "", prose, count=1, flags=re.MULTILINE).strip()
    if not prose:
        raise SystemExit("ORG-CHARTER.md needs a narrative brief around the yaml block")
    data["narrative"] = prose

    charter = Charter(**data)
    if charter.slug != slug:
        raise SystemExit(
            f"charter slug {charter.slug!r} does not match recipe directory {slug!r}"
        )
    return charter


def run_charter(paths: OrgPaths) -> int:
    if not paths.charter_md.exists():
        raise SystemExit(f"no recipe at {paths.charter_md}")

    charter = parse_charter_md(paths.charter_md.read_text("utf-8"), paths.slug)
    # The screen fires here, before any model tokens are spent on the org.
    problems = screen_charter(charter)
    if problems:
        for msg, _ in problems:
            print(f"charter: {msg}")
        raise SystemExit(
            "charter: name screen failed; rename the org in the recipe "
            "(see the pre-commit checklist in docs/RECIPE-FORMAT.md)"
        )
    # Write only when the derivation actually moves (BACKLOG:
    # charter-redump-drift). `/forge` runs this stage unconditionally, so the
    # advertised resume ("kill the session, re-run /forge <slug>") used to
    # rewrite a committed fixture's charter.json with every field the schema
    # had gained since it was generated -- inert, but a dirty tree on an
    # artifact the project calls frozen.
    #
    # Compared on rendered bytes rather than on the recipe's hash: charter.json
    # is a function of the recipe AND the schema, so a recipe-hash guard would
    # hide exactly the drift this entry is about. Compared rather than blocked
    # outright (which is what run_scaffold does): scaffold can afford the
    # blunter guard because re-running it would wipe merged enrichment prose,
    # while re-deriving a charter loses nothing, so the only thing worth
    # suppressing is a no-op write.
    #
    # This pairs with test_committed_charter_regenerates_byte_identical, which
    # keeps every pinned fixture's committed charter equal to a fresh derive.
    # Together they close the loop: a committed charter is never stale, so a
    # resume never rewrites one, so the tree stays clean.
    rendered = dump_json(charter)
    if paths.charter_json.exists() and (
        paths.charter_json.read_text("utf-8") == rendered
    ):
        print(f"charter: {paths.charter_json} is current, nothing to do")
    else:
        write_model(paths.charter_json, charter)
        print(f"charter: wrote {paths.charter_json}")

    state = load_state(paths)
    state.mark_done("charter", inputs_hash=sha256_file(paths.charter_md))
    save_state(paths, state)
    return 0
