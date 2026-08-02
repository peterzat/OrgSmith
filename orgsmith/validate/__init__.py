"""orgsmith validate: deterministic org lint.

Every rule checks the generated org against its own ground truth. ERROR
findings mean the org contradicts its ledger (exit 1); a clean run exits
0. Rules never call a model.
"""

from __future__ import annotations

import json

from ..naming import strip_control
from ..paths import OrgPaths
from .rules import RULES, Context


def collect(ctx: Context, selected=None) -> tuple[list[dict], list[dict]]:
    """Run rules against a loaded context, returning (findings, skipped) as
    plain dicts. Shared by run_validate and the report's integrity dashboard
    so the two cannot drift."""
    findings: list[dict] = []
    skipped: list[dict] = []
    for rule in RULES if selected is None else selected:
        reason = rule.available(ctx)
        if reason is not None:
            skipped.append({"rule": rule.id, "reason": reason})
            continue
        for message, target in rule.check(ctx):
            findings.append(
                {"rule": rule.id, "severity": rule.severity,
                 "message": message, "target": target}
            )
    return findings, skipped


def run_validate(paths: OrgPaths, as_json: bool = False, only=None) -> int:
    ctx = Context.load(paths)
    selected = RULES if not only else [r for r in RULES if r.id in set(only)]
    if only and len(selected) != len(set(only)):
        known = {r.id for r in RULES}
        raise SystemExit(f"validate: unknown rule ids: {sorted(set(only) - known)}")

    findings, skipped = collect(ctx, selected)

    errors = [f for f in findings if f["severity"] == "ERROR"]
    ran = len(selected) - len(skipped)
    if as_json:
        print(
            json.dumps(
                {
                    "slug": paths.slug,
                    "rules_run": [
                        r.id for r in selected
                        if r.id not in {s["rule"] for s in skipped}
                    ],
                    "skipped": skipped,
                    "findings": findings,
                    "counts": {"ERROR": len(errors),
                               "WARN": len(findings) - len(errors)},
                    "ok": not errors,
                },
                indent=2,
            )
        )
    else:
        # Findings quote unconstrained ledger strings (`LedgerCheck.name`,
        # `GraphEdge.src`, `AclGrant.person`, `Person.reports_to`) and
        # third-party parser exception text, none of which pydantic
        # constrains. Validating an org tree obtained from someone else is a
        # supported operation, so an ANSI escape smuggled through any of them
        # would reach the terminal and could rewrite or hide earlier
        # findings -- exactly what `strip_control` exists to stop.
        #
        # Sanitized at the printer rather than at each interpolation site:
        # one place cannot be forgotten, and it covers the rules that do not
        # yet quote with `!r` as well as every rule added later. `keep=""`
        # drops newlines too, so a smuggled newline cannot forge a second
        # finding line. Matches the ingest and score printers.
        # (SECURITY.md, carried NOTE, closed 2026-08-02.)
        #
        # `str()` before sanitizing: `strip_control` iterates its argument and
        # so requires a `str`, while the f-string it replaced coerced anything.
        # Rules yield `str` targets today, but they build paths constantly and
        # a yielded `Path` or `int` would raise out of the one printer that
        # must survive bad input. Coercion restores that robustness here rather
        # than relying on every rule author to remember it.
        for s in skipped:
            print(
                f"SKIP {strip_control(str(s['rule']), keep='')}: "
                f"{strip_control(str(s['reason']), keep='')}"
            )
        for f in findings:
            print(
                f"{strip_control(str(f['severity']), keep='')} "
                f"{strip_control(str(f['rule']), keep='')} "
                f"[{strip_control(str(f['target']), keep='')}] "
                f"{strip_control(str(f['message']), keep='')}"
            )
        print(
            f"validate: {ran} rules run, {len(skipped)} skipped, "
            f"{len(errors)} errors, {len(findings) - len(errors)} warnings"
        )
    return 1 if errors else 0
