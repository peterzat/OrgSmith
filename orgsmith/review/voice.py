"""Measure cross-document voice tics, deterministically and with no model
(M12, cross-document-voice).

The board's largest finding is that every genre collapses to one template
across authors, and `review/metrics.py` is structurally blind to it (it can
only flag prose that repeats, not prose that fails to vary). This instrument
does not fix that: no ledger owns "is this the same rhetorical figure", so any
single count here is taste wearing a decimal point. What it does is print a
PRE-REGISTERED set of patterns and count each one, so the tic is reported as a
RANGE across strict and loose readings rather than as one number. The strict
readings land in the single digits and disagree with each other; the plain
words sweep up ordinary English. Both are shown, and nothing here gates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .corpus import prose_text

# Pre-registered patterns. The point of printing them is that the reader sees
# exactly what was counted: the "34 occurrences" the board reported is not
# reproducible, and the spread below is why. Ordered strictest to loosest.
VOICE_PATTERNS: list[tuple[str, str, str]] = [
    (
        "antithesis-strict-now-than-later",
        "rather ... now/early ... than ... later/late (the temporal contrast, "
        "strictly read)",
        r"rather\b[^.]{0,60}?\b(?:now|early)\b[^.]{0,60}?\bthan\b"
        r"[^.]{0,60}?\b(?:later|late)\b",
    ),
    (
        "antithesis-strict-now-than",
        "rather ... (now|early|first) ... than (the contrast without its "
        "second pole)",
        r"rather\b[^.]{0,60}?\b(?:now|early|first)\b[^.]{0,60}?\bthan\b",
    ),
    (
        "antithesis-loose-rather-word-than",
        "rather <word> ... than (any near-adjacent rather/than pairing)",
        r"rather\s+\w+\b[^.]{0,60}?\bthan\b",
    ),
    (
        "antithesis-plain-rather-than",
        "the plain words 'rather than' (sweeps up ordinary English)",
        r"\brather than\b",
    ),
    (
        "two-asks-opener",
        "'Two asks. First ... Second ...' engagement-email opener",
        r"\btwo asks\b",
    ),
    (
        "workstreams-heading",
        "a 'Workstreams' section heading (the kickoff-memo template)",
        r"\bworkstreams\b",
    ),
    (
        "next-steps-heading",
        "a 'Next Steps' section heading (kickoff and deck closer)",
        r"\bnext steps\b",
    ),
]


@dataclass
class VoiceTic:
    name: str
    description: str
    pattern: str
    occurrences: int
    docs: int  # documents containing at least one occurrence


def measure_voice(docs: dict[str, object]) -> tuple[list[VoiceTic], int]:
    """Count each pre-registered pattern across the authored corpus. Returns
    (tics, total_docs). Deterministic and RNG-free; a pure function of the
    authored prose, so it re-measures identically."""
    proses = {doc_id: prose_text(d) for doc_id, d in docs.items()}
    tics: list[VoiceTic] = []
    for name, description, pattern in VOICE_PATTERNS:
        rx = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        occ = 0
        hit_docs = 0
        for text in proses.values():
            n = len(rx.findall(text))
            occ += n
            if n:
                hit_docs += 1
        tics.append(
            VoiceTic(
                name=name,
                description=description,
                pattern=pattern,
                occurrences=occ,
                docs=hit_docs,
            )
        )
    return tics, len(proses)
