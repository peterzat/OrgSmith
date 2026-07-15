"""Mechanical screen of generated names against well-known real firms.

Deterministic, offline, stdlib-only. Three enforcement points share this
module: the charter and scaffold generation gates (which fail before any
model tokens are spent) and the NAME-01 validator rule (which has no
grandfather: it reads only charter and foundation, artifacts every org
has). The committed list is a screen, not a guarantee; it covers
flagship firms a US professional-services corpus could plausibly
collide with.
"""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from pathlib import Path

REAL_FIRMS = Path(__file__).parent / "data" / "real_firms.txt"

# Trailing legal-form suffixes carry no identity: "McKinsey & Company"
# and "McKinsey" must normalize identically.
_LEGAL_SUFFIXES = {
    "llc", "llp", "lp", "pllc", "plc", "pc", "pa", "inc", "ltd", "co",
    "corp", "company", "corporation", "incorporated",
}
# Connectives only. Business words (group, partners, advisors) are NOT
# dropped: stripping them would reduce "Foley Group" to "foley" and
# over-fire on every surname.
_STOPWORDS = {"and", "of", "the"}

Finding = tuple[str, str]  # (message, target) -- the validator's shape


def normalize(name: str) -> tuple[str, ...]:
    """Canonical token form: NFKD -> ascii, lowercase, '&' -> 'and',
    non-alphanumerics -> spaces, trailing legal suffixes stripped,
    connectives dropped."""
    text = unicodedata.normalize("NFKD", name)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("&", " and ")
    tokens = re.sub(r"[^a-z0-9]+", " ", text).split()
    while tokens and tokens[-1] in _LEGAL_SUFFIXES:
        tokens.pop()
    return tuple(t for t in tokens if t not in _STOPWORDS)


def domain_key(domain: str) -> str:
    """Domains compare with the TLD stripped and separators collapsed:
    'mckinsey.com' and 'McKinsey & Company' meet at 'mckinsey'."""
    host = domain.strip().lower().rsplit("@", 1)[-1]
    parts = [p for p in host.split(".") if p]
    if len(parts) > 1:
        parts = parts[:-1]
    return re.sub(r"[^a-z0-9]+", "", "".join(parts))


def load_firms(path: Path = REAL_FIRMS) -> list[str]:
    firms = []
    for line in path.read_text("utf-8").splitlines():
        entry = line.split("#", 1)[0].strip()
        if entry:
            firms.append(entry)
    return firms


class FirmIndex:
    """Matching semantics, deliberately asymmetric: org-like strings flag
    when a firm is the whole normalized name or appears as a contiguous
    token run ("McKinsey Group LLC" contains McKinsey); person names flag
    only on exact equality (the Morgan-Stanley-the-person class; a
    generated "Sarah Morgan" must not trip over Morgan Stanley). No fuzzy
    matching: determinism is worth more than recall here."""

    def __init__(self, firms: list[str]):
        self.by_tokens: dict[tuple[str, ...], str] = {}
        self.by_domain_key: dict[str, str] = {}
        for firm in firms:
            tokens = normalize(firm)
            if tokens:
                self.by_tokens.setdefault(tokens, firm)
                self.by_domain_key.setdefault("".join(tokens), firm)

    def match_org(self, name: str) -> str | None:
        tokens = normalize(name)
        if not tokens:
            return None
        exact = self.by_tokens.get(tokens)
        if exact:
            return exact
        for entry, firm in self.by_tokens.items():
            n = len(entry)
            if n < len(tokens) and any(
                tokens[i : i + n] == entry
                for i in range(len(tokens) - n + 1)
            ):
                return firm
        return None

    def match_person(self, name: str) -> str | None:
        tokens = normalize(name)
        return self.by_tokens.get(tokens) if tokens else None

    def match_domain(self, domain: str) -> str | None:
        key = domain_key(domain)
        return self.by_domain_key.get(key) if key else None


@lru_cache(maxsize=1)
def default_index() -> FirmIndex:
    return FirmIndex(load_firms())


def screen_charter(charter) -> list[Finding]:
    """Findings for the recipe-authored names: org name and domain."""
    idx = default_index()
    findings = []
    hit = idx.match_org(charter.name)
    if hit:
        findings.append((
            f"org name {charter.name!r} collides with real firm {hit!r}",
            "charter.json",
        ))
    hit = idx.match_domain(charter.domain)
    if hit:
        findings.append((
            f"domain {charter.domain!r} collides with real firm {hit!r}",
            "charter.json",
        ))
    return findings


def screen_foundation(foundation) -> list[Finding]:
    """Findings for the generated names: external orgs and all people."""
    idx = default_index()
    findings = []
    for xo in foundation.external_orgs:
        hit = idx.match_org(xo.name)
        if hit:
            findings.append((
                f"external org {xo.id} name {xo.name!r} collides with "
                f"real firm {hit!r}",
                "foundation.json",
            ))
    for person in [*foundation.people, *foundation.external_people]:
        hit = idx.match_person(person.name)
        if hit:
            findings.append((
                f"person {person.id} name {person.name!r} collides with "
                f"real firm {hit!r}",
                "foundation.json",
            ))
    return findings
