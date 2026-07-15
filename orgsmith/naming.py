"""Filename realism with safety rails.

Names look like a real file share (dates, versions, FINAL) but must satisfy
portability rules; the planner enforces them at build time and validators
re-check committed orgs.
"""

from __future__ import annotations

import re
import unicodedata

FORBIDDEN_CHARS = set('<>:"/\\|?*')
WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}
MAX_RELPATH = 180


def check_filename(name: str) -> list[str]:
    problems = []
    if any(ch in FORBIDDEN_CHARS for ch in name):
        problems.append(f"forbidden character in {name!r}")
    if any(ord(ch) < 32 for ch in name):
        problems.append(f"control character in {name!r}")
    if name.endswith((" ", ".")):
        problems.append(f"trailing space/dot in {name!r}")
    stem = name.split(".")[0].upper()
    if stem in WINDOWS_RESERVED:
        problems.append(f"windows reserved name {name!r}")
    if unicodedata.normalize("NFC", name) != name:
        problems.append(f"not NFC-normalized: {name!r}")
    return problems


def check_relpath(relpath: str) -> list[str]:
    problems = []
    if len(relpath) > MAX_RELPATH:
        problems.append(f"path longer than {MAX_RELPATH}: {relpath!r}")
    parts = relpath.split("/")
    if "" in parts:
        problems.append(f"absolute path or empty component: {relpath!r}")
    if ".." in parts:
        problems.append(f"parent-directory component: {relpath!r}")
    for part in parts:
        problems.extend(check_filename(part))
    return problems


def strip_control(text: str, keep: str = "\n\t") -> str:
    """Neutralize control characters in untrusted strings bound for a
    terminal (escape sequences can rewrite or hide earlier output).
    Control characters not in `keep` become U+FFFD."""
    return "".join(
        "�" if unicodedata.category(ch) == "Cc" and ch not in keep else ch
        for ch in text
    )


def sanitize_component(text: str) -> str:
    """Make an arbitrary display string safe as one path component while
    keeping it readable (spaces preserved)."""
    text = unicodedata.normalize("NFC", text)
    text = "".join("-" if ch in FORBIDDEN_CHARS else ch for ch in text)
    text = re.sub(r"\s+", " ", text).strip(" .")
    return text
