"""Seeded per-company style pack.

One firm, one look: font family, accent color, and letterhead are fixed by
the recipe seed so every document from the same org reads as one house
style. Font families are portable names with generic fallbacks; .docx
carries the name, PDF rendering falls back gracefully when absent.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..schemas import Charter
from ..seeds import rng

_FAMILIES = [
    ("Georgia", "serif"),
    ("Times New Roman", "serif"),
    ("Arial", "sans-serif"),
    ("Verdana", "sans-serif"),
    ("Cambria", "serif"),
]

_ACCENTS = ["1F3A5F", "4A2E2A", "1E4D2B", "3B3060", "5A4632"]


@dataclass(frozen=True)
class StylePack:
    font_family: str
    font_generic: str  # css generic fallback
    accent_hex: str  # RRGGBB, no '#'
    letterhead_lines: tuple[str, ...]


def style_pack(charter: Charter) -> StylePack:
    rand = rng(charter.seed, "render.styles")
    family, generic = rand.choice(_FAMILIES)
    accent = rand.choice(_ACCENTS)
    return StylePack(
        font_family=family,
        font_generic=generic,
        accent_hex=accent,
        letterhead_lines=(charter.name, f"www.{charter.domain}"),
    )
