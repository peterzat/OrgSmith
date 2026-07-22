"""M15 persona voice v2: structured per-person style specs.

One pure function is the twin: run_acl writes its output to
ledger/style_specs.json (published ground truth), STY-01 recomputes and
compares, and authoring contexts derive per-author brief guidance from the
same call, so no two consumers can drift. Draws come only from per-person
`foundation.style` streams, so a knob-off charter draws zero values and a
roster edit cannot perturb another person's spec.
"""

from __future__ import annotations

from ..schemas import StyleSpec, StyleSpecsLedger
from ..seeds import rng

_REGISTERS = ("crisp", "warm", "formal", "plainspoken", "structured")
_SENTENCES = ("short", "medium", "long")
_GREETINGS = (
    "Hi {first},",
    "Hello {first},",
    "{first},",
    "Good morning {first},",
    "Dear {first},",
)
_CLOSINGS = ("Best", "Regards", "Thanks", "Best regards", "Sincerely")
_HABITS = (
    "prefers numbered lists over bullet points",
    "avoids lists entirely and writes in paragraphs",
    "keeps paragraphs to two or three sentences",
    "opens with the conclusion before the detail",
    "closes with one clear next step",
    "sets context in a sentence before making any request",
)
_TICS = (
    "'Two asks. First... Second...' as an opener",
    "the 'rather X now than Y later' antithesis",
    "a 'Workstreams' heading followed by 'Next Steps'",
    "closing epigrams or aphorisms",
    "'In short,' as a paragraph opener",
    "'Let me be direct:' and similar throat-clearing",
)


def derive_style_specs(charter, foundation) -> StyleSpecsLedger:
    """Every roster person's spec, roster order. Empty when the knob is off
    (and run_acl then writes no ledger, so STY-01 grandfathers by charter)."""
    specs = []
    if charter.doc_culture.style_specs:
        for p in foundation.people:
            r = rng(charter.seed, "foundation.style", p.id)
            specs.append(
                StyleSpec(
                    person=p.id,
                    voice_register=r.choice(_REGISTERS),
                    sentence_length=r.choice(_SENTENCES),
                    greeting=r.choice(_GREETINGS),
                    closing=r.choice(_CLOSINGS),
                    habits=sorted(r.sample(_HABITS, 2)),
                    banned_tics=sorted(r.sample(_TICS, 2)),
                )
            )
    return StyleSpecsLedger(slug=charter.slug, specs=specs)
