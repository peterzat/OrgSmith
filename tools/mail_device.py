#!/usr/bin/env python3
"""Count the mail-mention device in one org (M17e).

The device has two halves, and this counts each where it lives:

- **Planned:** mentions the plan REQUIRES in a mail body that a real note
  would carry in its headers instead. On person-to-person mail that is a
  recipient (To/Cc names them); on list-addressed mail it is any drawn
  colleague (the To header carries only the list).
- **Authored:** mail bodies that name a recipient in full anyway. A plan can
  stop requiring a name and an author can still write it, which is often
  what a real note does when a colleague is copied, so this is reported, not
  judged.

A measurement for the M17e write-up; it gates nothing. Deterministic and
offline:

    python tools/mail_device.py hollowell-ip [--root DIR]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from orgsmith.artifacts import load_foundation, load_manifest  # noqa: E402
from orgsmith.paths import OrgPaths  # noqa: E402
from orgsmith.render.eml import eml_recipients  # noqa: E402
from orgsmith.review.corpus import load_authored, prose_text  # noqa: E402


def count(paths: OrgPaths) -> dict:
    foundation = load_foundation(paths)
    names = {p.id: p.name for p in foundation.people}
    names.update({x.id: x.name for x in foundation.external_people})
    authored = load_authored(paths)
    out = {
        "mail": 0, "direct": 0, "lists": 0,
        "planned_recipient_mentions": 0, "planned_list_mentions": 0,
        "direct_bodies_naming_a_recipient": 0, "list_bodies_naming_a_colleague": 0,
    }
    internal = {p.id for p in foundation.people}
    for e in load_manifest(paths):
        if e.format != "eml" or e.authoring != "batchable":
            continue
        out["mail"] += 1
        body = prose_text(authored[e.doc_id]) if e.doc_id in authored else ""
        planned = {m.entity for m in e.mentions}
        if e.render_params.get("dl"):
            out["lists"] += 1
            drawn = set(e.participants) - set(e.authors)
            out["planned_list_mentions"] += len(planned & drawn)
            if any(names[p] in body for p in internal - set(e.authors) if p in names):
                out["list_bodies_naming_a_colleague"] += 1
        else:
            out["direct"] += 1
            recipients = set(eml_recipients(e.authors, e.participants)) - set(e.authors)
            out["planned_recipient_mentions"] += len(planned & recipients)
            if any(names[p] in body for p in recipients if p in names):
                out["direct_bodies_naming_a_recipient"] += 1
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug")
    ap.add_argument("--root", type=Path, default=Path("."))
    args = ap.parse_args(argv)
    print(json.dumps({"slug": args.slug, **count(OrgPaths(root=args.root, slug=args.slug))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
