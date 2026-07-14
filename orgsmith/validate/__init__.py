"""orgsmith validate: deterministic org lint.

Every rule checks the generated org against its own ground truth. ERROR
findings mean the org contradicts its ledger (exit 1); a clean run exits
0. Rules never call a model.
"""

from __future__ import annotations

import json

from ..paths import OrgPaths
from .rules import RULES, Context


def run_validate(paths: OrgPaths, as_json: bool = False, only=None) -> int:
    ctx = Context.load(paths)
    selected = RULES if not only else [r for r in RULES if r.id in set(only)]
    if only and len(selected) != len(set(only)):
        known = {r.id for r in RULES}
        raise SystemExit(f"validate: unknown rule ids: {sorted(set(only) - known)}")

    findings = []
    skipped = []
    for rule in selected:
        reason = rule.available(ctx)
        if reason is not None:
            skipped.append({"rule": rule.id, "reason": reason})
            continue
        for message, target in rule.check(ctx):
            findings.append(
                {"rule": rule.id, "severity": rule.severity,
                 "message": message, "target": target}
            )

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
        for s in skipped:
            print(f"SKIP {s['rule']}: {s['reason']}")
        for f in findings:
            print(f"{f['severity']} {f['rule']} [{f['target']}] {f['message']}")
        print(
            f"validate: {ran} rules run, {len(skipped)} skipped, "
            f"{len(errors)} errors, {len(findings) - len(errors)} warnings"
        )
    return 1 if errors else 0
