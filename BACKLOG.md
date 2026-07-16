# Backlog

Durable register of considered proposals that were deferred, scoped out, or
rejected. Read before drafting a new SPEC.md; swept at turn close.


### pdf-newline-flattening
- **The PDF renderer silently flattens `\n` inside a paragraph block while the DOCX renderer honors it as `<w:br/>`.** `render/pdf.py:90` emits `<p>{text}</p>`, and HTML collapses newlines to spaces; an author using the same convention that works in DOCX gets a smeared line in PDF. Affects the committed fixture `gladepoint-strategies` `d:0008`, whose addressee block renders as one run-on line. Validates clean because no rule checks line breaks.
- **Why deferred:** out of scope for M7 (the quality instrument); found BY the M7 board rather than planned. Fixing it re-renders a frozen fixture's committed bytes, which is its own decision.
- **Revisit criteria:** any turn that touches `render/pdf.py`, or the first fixture regeneration that would re-render an affected PDF, or a board finding that reports the same smear on a new org.
- **Origin:** spec 2026-07-16 (found by the review board during the model A/B; see docs/MODEL-AB.md finding 3).
