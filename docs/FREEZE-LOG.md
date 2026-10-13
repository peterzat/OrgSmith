# Freeze log: the carve-out history

Moved verbatim out of CLAUDE.md on 2026-10-13 (M17d), so the always-loaded
conventions file states the current rules and this file keeps how they came
to be. Nothing here is a rule that CLAUDE.md does not also state. Newest
first. Each section is quoted exactly as CLAUDE.md carried it.

A document dated before 2026-10-13 that cites "CLAUDE.md" for a carve-out,
a turn's non-claims, or the mail residual (`docs/M17C-RUN-LOG.md` does,
three times) is citing a section that now lives here.

## Mail-org carve-out (M17e): OPEN as of 2026-10-13

Approved by the user on 2026-10-13 ("1. approved") against BACKLOG
`mail-orgs-recipient-mention-carve-out`. Scope: `ashcombe-advisory`,
`hollowell-ip` and `meridian-actuarial`, each regenerated once, wholesale,
through the live airlock, to close both halves of the mail-mention device:
`mail.exempt_recipient_mentions` for person-to-person mail and the new
`mail.broadcasts_address_the_list` for list mail. The same regeneration adopts
`doc_culture.overview_cites_finished_work` (M17e) and M17d's business-day
engagement starts, partner oversight and a declared 2020. The other seven
committed orgs may not move. Measured before regeneration with
`tools/mail_device.py`: every person-to-person body names its recipient in
full (39 of 39, 20 of 20, 24 of 24), from 85, 46 and 62 planned recipient
mentions.

## The hard rules' history clauses

From the "Additive evolution" rule: "This rule was SUSPENDED for the v2.0
window (M8-M11) by user decision and is **restored as of M11b**: the fleet is
regenerated, re-frozen, and pinned fleet-wide again (`tests/test_org_regen.py`,
`PINNED = SLUGS`). The `seeds.py` per-stream discipline was never relaxed —
it is what keeps a single generation reproducible."

From the "Committed fixtures are frozen" rule: "The M8-M11 carve-out for the
v2.0 reset is **closed as of M11b**: the new seven-org fleet is generated and
the pin is restored fleet-wide (`tests/test_org_regen.py`, `PINNED = SLUGS`),
not scoped to `dev-mini`."

## Capability turn (M17b): NO CARVE-OUT, and none is open (2026-08-02)

M17b answered both of M17's board blockers with capability only. **No
committed org's ledgers, manifest, or authored prose was regenerated**, so
every finding the README quotes against the exemplar is still present in it.
`PINNED = SLUGS` was enforced fleet-wide and green at every commit, including
mid-turn.

Four knobs landed, all default-off with inert schema defaults on the existing
`orgsmith/<kind>@<ver>` schema ids, drawing only from NEW `seeds.py` streams
(`fabric.engagements.scope`, `docplan.outline`), proven inert against the
frozen fleet before anything adopted them: `engagements.scope`,
`doc_culture.client_facing_reports`, `doc_culture.outline_variety`, and the
`GenreRule.scope_refs` registry column. Two validator rules (`SCOPE-01`,
`OUT-01`) grandfather by charter in the AFF-01/STY-01 idiom: skip visibly with
the knob off, fail when a knob is on and its artifact is missing.

Each knob rewrote all nine `charter.json` files and all nine data cards, since
`dump_json` serializes every field and `datacard._knob_rows` walks the charter
model. Re-emission order when metrics move: metrics/report, then
`tools/checksums.py`, then `data-card` for all nine (the cards quote their own
checksum row).

`orgsmith/review/structure.py` is a MEASUREMENT and may never gate: no
threshold it produces enters a test tier or a validator rule. Two same-genre
status reports SHOULD share a shape.

What this turn does NOT claim, and no doc may imply: that authored prose
improved. The outline work is proven as plumbing and as block-shape counts
under the scripted author; the next generation settles the rest. "Impossible
by construction" is an overclaim -- a finite pool cycles, and the guarantees
are stated exactly in `assign_outlines`. `rf:voice-3` (a paraphrased move
across five genres) is beyond both the structural axis and the outline work.

## Frozen-fixture carve-out, answer-key turn (M17): CLOSED as of 2026-08-02

The M17 carve-out is **closed**. `northgate-staffing` was regenerated once,
wholesale, under a recipe enriched with existing knobs (departmental ACL, mail
threads with mundane traffic and both mention exemptions, scans with an OCR
layer, signature-page and filename-date hard cases) plus
`graph_targets.alias_agreement`, then boarded and re-frozen. `PINNED = SLUGS`
is enforced fleet-wide again and was green at every commit, including mid-turn.

Additive evolution was never suspended and remains in force. Both knobs added
this turn (`graph_targets.alias_agreement`,
`mail.exempt_recipient_mentions`) landed default-off with inert schema
defaults on the existing `orgsmith/<kind>@<ver>` schema ids, drew nothing from
existing seed streams, and were proven inert against the frozen fleet before
the exemplar turned them on. A test now asserts both halves of that
grandfathering: an org that adopted a knob runs its rule clean, and an org
that did not still skips visibly. Any post-turn capability lands the same way.

`evals/`, `acl.json`, `GENERATION-REPORT.md`, `review/`, `baselines/`,
`DATA-CARD.md`, and PERMISSIONS.md remain derived and may always be
re-emitted. Regenerating a committed org's ledgers, manifest, or authored
prose again requires a fresh, user-approved carve-out.

**The mail demonstrators were deliberately left out** (user decision,
2026-08-02). `hollowell-ip` and `meridian-actuarial` still carry the
full-name-in-body device described below; the
`mail.exempt_recipient_mentions` knob that would close it is landed and
proven inert, but the orgs were not re-run. Their data cards record it.

Residual on the exemplar, recorded not fixed (board findings are published,
never prose-fixed): the recipient exemption removed the *requirement* from
person-to-person mail (no such message plans a recipient mention), but not the
surface: 8 of 14 still name a recipient in the body by authorial choice.
Distribution-list mail keeps the requirement outright, because the To header
carries the list address rather than member names, so MENT-01 still needs the
body mention. The result is a broadcast that greets one person by
first name and then names them in full to the room. Closing that needs
either a mention model that understands list membership or a planner that
stops giving a broadcast a single participant, and it is its own unit of
work.

## Frozen-fixture carve-out, realism wave (M13-M16): CLOSED as of M16 (2026-07-28)

The realism-wave carve-out is **closed**. All eight fleet orgs plus `dev-mini`
were regenerated wholesale under the wave's knobs and re-frozen: the fixtures
are frozen again, `PINNED = SLUGS` is enforced fleet-wide
(`tests/test_org_regen.py`), and it was green at every mid-wave commit. Additive
evolution is **restored** exactly as at M11b: any post-wave capability lands as
a default-off recipe knob with inert schema defaults on the existing
`orgsmith/<kind>@<ver>` schema ids, drawing randomness only from NEW `seeds.py`
streams, proven inert against the frozen fleet (loads, validates clean, and
re-derives byte-identical structure) before any org turns it on. The per-stream
seed discipline was never relaxed. `evals/`, `acl.json`, `GENERATION-REPORT.md`,
`review/`, and PERMISSIONS.md remain derived and may always be re-emitted;
regenerating a committed org's ledgers, manifest, or authored prose again
requires a fresh, user-approved carve-out.

Known residual, recorded not fixed (board is read-only; fixing needs a new
carve-out): in the two mail demonstrators, forge-author workers put an email
recipient's full name in the message body to satisfy the ingest mention check.
The related `hollowell-ip` `To:/Cc:` duplicated-header banner is fixed as of
v2.1.1: the renderer strips an authored header banner from `.eml` bodies and
`doc_text` reads the transport headers, so MENT-01 still finds the recipient,
and a committed test asserts no fleet mail body carries a header banner. The
full-name-in-body device remains: a proper fix (exempt an email's recipient
from its required body mentions, the way `exempt_author_mentions` exempts the
author, then re-render the mail orgs) is its own unit of work.

