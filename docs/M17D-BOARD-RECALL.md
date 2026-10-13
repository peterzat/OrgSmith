# M17d board recall probe: evidence standard, fixed 2026-10-13

Does the review board find less when it is handed more to read? Written and
committed **before** any reviewer is dispatched, so the reading cannot be
chosen after the counts exist. SPEC.md (2026-10-13) criterion six.

Nothing here gates. No number below is a threshold, and no test tier or
validator rule reads this file.

## Why this probe exists

`board-yield-at-scale` in BACKLOG.md measured findings per sampled document
falling from 0.725 (`northgate-staffing`, 51 documents read) to 0.048
(`calderwood-partners`, 168 read) at the same coverage band. Two readings fit
and they point opposite ways: the large org is genuinely cleaner, or a
reviewer handed 168 documents reads less closely than one handed 51. M18 is
roughly twelve times calderwood, so which reading is true decides whether
the board can say anything about the flagship.

Nothing could separate the readings because nobody knew what the board
*should* find. This probe supplies that: known defects, planted identically,
read from a short and a long reading list.

## The setup

`tools/plant_defects.py calderwood-partners --seed 20261013 --small 50`
writes two scratch copies of the committed org with the same twelve plants,
differing only in `review/sample.json`:

- **small**: the twelve planted documents plus 38 others, 50 in all, about
  the size of the northgate reading list;
- **large**: all 168 authored documents, the calderwood reading list.

The plants are fixed in the tool, one document each, and the answer key
(which documents) is written outside both copies:

- **Eight anachronisms**, each in a document dated at least four years before
  the reference existed: Slack, Zoom as the default meeting, Microsoft Teams,
  automatic meeting transcription, ChatGPT, the pandemic, Loom, Notion.
- **Four assistant-voice tics**: "I hope this helps...", "Certainly. Here
  is a concise summary...", "Great question!...", "In summary, this
  document has outlined...".

Each sentence carries no digit and no name, so it collides with no ledger
value or planned mention, and is appended to an existing paragraph so it
reads as the author's own prose. The committed org is only read.

Per list, two reviewers on `claude-opus-5-5` at `xhigh`, fresh contexts:
`narrative_consistency` (whose question names tools and events that
postdate a document) and `document_plausibility` (register). Each follows
`forge-reviewer` from the git worktree pinned at `ac4c1e2`, which contains
neither the tool nor this file, and none is told that defects were planted,
that a second list exists, or that this is a measurement. Each is given
calderwood's real validator line.

## Scoring, fixed now

A plant is **found** at a list size when any finding from either reviewer at
that size names it: the finding lists the planted document in `docs` and its
summary or evidence contains the plant's token (case-insensitive: `Slack`,
`Zoom`, `Teams`, `transcribed automatically`, `ChatGPT`, `pandemic`, `Loom`,
`Notion`, `hope this helps`, `Certainly`, `Great question`, `this document
has outlined`), or the finding is corpus-level (empty `docs`) and quotes
the token. A finding that lists a planted document for some other reason is
not credited. Recall is found plants over twelve, reported per list, per
kind, and per dimension. Each reviewer's total findings and findings per
sampled document are reported beside it, since yield is the quantity the
backlog entry measured.

## What counts

- **The instrument degrades with reading load**: large-list recall is **three
  or more plants** below small-list recall.
- **No measurable degradation**: the two differ by **at most one plant**.
- A difference of two is **inconclusive**.
- If both lists find all twelve, the plants were too easy to discriminate
  anything, and the result is a ceiling, not a clean bill.

## The prediction, written down

Expected: the instrument degrades. Small-list recall of nine or more of
twelve, large-list recall of eight or fewer, a gap of three or more. The
assistant-voice tics are louder than the anachronisms and should survive
the long list better.

## What this cannot settle

- **A false-positive rate.** Recall on planted defects says nothing about how
  often the board invents a finding against prose that is fine;
  `board-negative-control` stays open.
- **Variance.** One reviewer per dimension per list. A one-plant difference
  is noise until replicated.
- **Plant realism.** These defects are cleaner than a generator's real ones.
  A board that finds these may still miss a re-skinned memo; recall here is
  an upper bound on recall for subtle defects.
- **Six dimensions.** Two dimensions read, not the full board.

## The tool, hashed at registration

| file | sha256 |
| --- | --- |
| `tools/plant_defects.py` | `febb1e0e05604dfcf4a2e7a5c10657cfed9c970b38caef49240f7d5259542701` |

## Amendment log

- (none yet)
