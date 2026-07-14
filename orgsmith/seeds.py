"""Stable per-entity RNG streams.

All randomness in pure stages derives from the charter's master seed plus a
string path naming the consumer (e.g. "foundation.roster", "docplan.dates").
Adding a new consumer never disturbs existing streams, which is what keeps
regeneration byte-stable as the pipeline grows.
"""

import hashlib
import random


def derive_seed(master: int, *parts: str) -> int:
    key = f"{master}|" + "|".join(parts)
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def rng(master: int, *parts: str) -> random.Random:
    return random.Random(derive_seed(master, *parts))
