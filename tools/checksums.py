#!/usr/bin/env python3
"""Regenerate CHECKSUMS.md: a SHA-256 rollup per committed org.

Deterministic and offline. For each of the eight committed fleet orgs, hashes
every committed file under companies/<slug>/ and companies/<slug>-metadata/ in
sorted path order (relpath\\0 then the file's SHA-256), then a fleet digest over
the per-org lines. dev-mini is the test fixture and is excluded.

Run from the repo root: `python tools/checksums.py` (writes CHECKSUMS.md), or
`python tools/checksums.py --check` (exit 1 if CHECKSUMS.md is stale).
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ORGS = [
    "ashcombe-advisory", "brackenridge-civil", "calderwood-partners",
    "hollowell-ip", "meridian-actuarial", "northgate-staffing",
    "saltmarsh-environmental", "verdant-health",
]


def _org_files(slug: str) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", f"companies/{slug}", f"companies/{slug}-metadata"],
        capture_output=True, text=True, check=True,
    ).stdout.split("\n")
    return sorted(f for f in out if f)


def _rollup(slug: str) -> tuple[str, int]:
    h = hashlib.sha256()
    n = 0
    for rel in _org_files(slug):
        h.update(rel.encode("utf-8") + b"\0")
        h.update(hashlib.sha256(Path(rel).read_bytes()).digest())
        n += 1
    return h.hexdigest(), n


def render() -> str:
    rows = []
    fleet = hashlib.sha256()
    for slug in ORGS:
        digest, n = _rollup(slug)
        rows.append((slug, digest, n))
        fleet.update(f"{slug}:{digest}\n".encode())
    lines = [
        "# Checksum manifest — OrgSmith v2.1.1",
        "",
        "SHA-256 rollup per committed org, over every committed file under",
        "`companies/<slug>/` and `companies/<slug>-metadata/` in sorted path order",
        "(each entry hashes `relpath\\0` then the file's SHA-256). Regenerate with",
        "`python tools/checksums.py`. The fleet digest is the SHA-256 of the",
        "per-org `slug:digest` lines in the table order. `dev-mini` is the test",
        "fixture and is excluded.",
        "",
        "| org | files | sha256 |",
        "| --- | ---: | --- |",
    ]
    for slug, digest, n in rows:
        lines.append(f"| {slug} | {n} | `{digest}` |")
    total = sum(n for _, _, n in rows)
    lines.append(f"| **fleet** | {total} | `{fleet.hexdigest()}` |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    out = Path("CHECKSUMS.md")
    content = render()
    if "--check" in argv:
        if not out.exists() or out.read_text() != content:
            print("CHECKSUMS.md is stale; run: python tools/checksums.py")
            return 1
        print("CHECKSUMS.md is current.")
        return 0
    out.write_text(content)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
