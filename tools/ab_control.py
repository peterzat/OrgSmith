#!/usr/bin/env python3
"""Derive the M17c control arm's recipe from the treatment arm's.

The controlled proof (SPEC.md 2026-08-03) needs one recipe generated twice
with the M17b knobs as the only variable. Writing two recipes by hand would
make that a claim; deriving one from the other mechanically makes it a
property, and `tests/test_unit_ab_control.py` asserts the two charters differ
in exactly the fields named in `ARM_KNOBS` and nowhere else.

Deterministic, offline, and model-free. Run from the repo root:

    python tools/ab_control.py quillon-harbor --root scratch/<control-root>

The narrative prose is copied byte-for-byte rather than re-emitted. It is
carried into charter.json verbatim and handed to the model in every authoring
brief, so a single reflowed line would mean the two arms authored against
different instructions and the experiment would be measuring that instead.
The yaml block IS re-emitted (comments in it are lost), which is fine: the
control recipe is a derived artifact under gitignored `scratch/`, never a
maintained file.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from orgsmith.charter import _YAML_BLOCK  # noqa: E402

# The M17b knobs, and the entire difference between the two arms. Adding a
# knob to the recipe without deciding which arm it belongs to is the mistake
# this tuple exists to make loud: the test diffs the two charters against
# exactly this list, so an undeclared knob fails rather than silently
# confounding the measurement.
ARM_KNOBS: tuple[tuple[str, str], ...] = (
    ("doc_culture", "outline_variety"),
    ("doc_culture", "client_facing_reports"),
    ("engagements", "scope"),
)


def strip_arm_knobs(text: str) -> tuple[str, list[str]]:
    """(control recipe markdown, the knob paths actually removed).

    Removing a knob rather than setting it false is deliberate: absence is
    what a pre-M17b recipe looks like, and `engagements.scope` has no false
    to set. It also means the control exercises the same knob-off path every
    committed fleet org already runs.
    """
    match = _YAML_BLOCK.search(text)
    if not match:
        raise SystemExit("ORG-CHARTER.md has no fenced ```yaml block")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise SystemExit("charter yaml block must be a mapping")

    removed: list[str] = []
    for section, key in ARM_KNOBS:
        block = data.get(section)
        if isinstance(block, dict) and key in block:
            del block[key]
            removed.append(f"{section}.{key}")

    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100)
    control = f"{text[: match.start()]}```yaml\n{body}```\n{text[match.end():]}"
    return control, removed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument(
        "--root",
        type=Path,
        required=True,
        help="destination root; the recipe lands at <root>/recipes/<slug>/",
    )
    ap.add_argument(
        "--source-root",
        type=Path,
        default=Path("."),
        help="where the treatment recipe lives (default: repo root)",
    )
    args = ap.parse_args(argv)

    src = args.source_root / "recipes" / args.slug / "ORG-CHARTER.md"
    if not src.is_file():
        raise SystemExit(f"no treatment recipe at {src}")

    control, removed = strip_arm_knobs(src.read_text())
    if not removed:
        raise SystemExit(
            f"{src} declares none of {[f'{s}.{k}' for s, k in ARM_KNOBS]}. "
            "That recipe is already a control arm; deriving from it would "
            "produce two identical arms and measure nothing."
        )

    dest = args.root / "recipes" / args.slug / "ORG-CHARTER.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(control)
    print(f"control arm: stripped {', '.join(removed)} -> {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
