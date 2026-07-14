"""author --ingest: validate and merge an authoring deliverable.

All-or-nothing: every problem across the whole deliverable is reported and
nothing is written unless the batch is clean. Placeholder discipline is the
core check: required facts present, no unbriefed fact ids, sigblocks only
where they belong.
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import ValidationError

from ..airlock import clear_outstanding, match_outstanding
from ..artifacts import load_engagements, load_manifest
from ..paths import OrgPaths
from ..schemas import (
    AuthoringDeliverable,
    DocBrief,
    DocIR,
    dump_json,
    surface_in_text,
)
from ..state import load_state, save_state, sha256_file

_PLACEHOLDER = re.compile(r"\{\{fact:([^}]*)\}\}")


def docir_path(paths: OrgPaths, doc_id: str) -> Path:
    return paths.docir_dir / f"{doc_id.replace(':', '')}.json"


def _chunks(doc: DocIR) -> str:
    chunks: list[str] = []
    for b in doc.blocks:
        chunks.append(b.text)
        chunks.extend(b.items)
        chunks.extend(b.header)
        for row in b.rows:
            chunks.extend(row)
    return "\n".join(chunks)


def placeholders_in(doc: DocIR) -> list[str]:
    return _PLACEHOLDER.findall(_chunks(doc))


def _check_doc(doc: DocIR, brief: DocBrief) -> list[str]:
    problems = []
    if len(doc.blocks) < 2:
        problems.append("fewer than 2 blocks")
    for i, b in enumerate(doc.blocks):
        if b.kind in ("heading", "paragraph") and not b.text.strip():
            problems.append(f"block {i} ({b.kind}) has empty text")
        if b.kind == "list" and not b.items:
            problems.append(f"block {i} (list) has no items")
        if b.kind == "table" and not b.rows:
            problems.append(f"block {i} (table) has no rows")

    used = placeholders_in(doc)
    briefed = {f.id for f in brief.facts}
    missing = sorted(briefed - set(used))
    if missing:
        problems.append(f"missing required placeholders: {', '.join(missing)}")
    unknown = sorted(set(used) - briefed)
    if unknown:
        problems.append(f"unbriefed fact ids used: {', '.join(unknown)}")

    people = {p.id for p in brief.authors} | {p.id for p in brief.participants}
    sigblocks = [b for b in doc.blocks if b.kind == "sigblock"]
    for b in sigblocks:
        if not b.signers:
            problems.append("sigblock without signers")
        bad = sorted(set(b.signers) - people)
        if bad:
            problems.append(f"sigblock signers not in brief: {', '.join(bad)}")
    if brief.genre == "engagement_letter" and not sigblocks:
        problems.append("engagement_letter requires a sigblock")
    if brief.genre == "meeting_minutes" and not any(
        b.kind in ("list", "table") for b in doc.blocks
    ):
        problems.append("meeting_minutes requires an attendee/action list or table")
    return problems


def run_ingest(paths: OrgPaths, deliverable_path: Path) -> int:
    state = load_state(paths)
    if not deliverable_path.exists():
        raise SystemExit(f"ingest: no such file {deliverable_path}")
    try:
        deliverable = AuthoringDeliverable.model_validate_json(
            deliverable_path.read_text("utf-8")
        )
    except ValidationError as err:
        print(f"ingest: deliverable rejected (schema):\n{err}")
        return 1

    order = match_outstanding(paths, state, "author", deliverable.work_order_id)
    briefs = {b.doc_id: b for b in order.docs}
    got = [d.doc_id for d in deliverable.docs]

    problems = []
    if len(set(got)) != len(got):
        problems.append("duplicate doc_id entries")
    unknown = sorted(set(got) - set(briefs))
    if unknown:
        problems.append(f"doc ids not in work order: {', '.join(unknown)}")
    missing = sorted(set(briefs) - set(got))
    if missing:
        problems.append(f"work-order docs not delivered: {', '.join(missing)}")
    facts = load_engagements(paths).fact_index()
    for doc in deliverable.docs:
        if doc.doc_id in briefs:
            brief = briefs[doc.doc_id]
            for p in _check_doc(doc, brief):
                problems.append(f"{doc.doc_id}: {p}")
            # Defense in depth: money/date surface forms must arrive only
            # via placeholders. A literal match means the author somehow
            # learned (or guessed) a ledger value.
            text = _chunks(doc)
            for brief_fact in brief.facts:
                fact = facts.get(brief_fact.id)
                if fact and fact.kind in ("money", "date") and (
                    fact.rendered in text
                ):
                    problems.append(
                        f"{doc.doc_id}: literal value of {fact.id} in prose; "
                        f"write the placeholder instead"
                    )
            # Required mentions: check against placeholder-resolved text so
            # a client name arriving via its fact placeholder still counts.
            resolved = _PLACEHOLDER.sub(
                lambda m: facts[m.group(1)].rendered
                if m.group(1) in facts
                else m.group(0),
                text,
            )
            signers = {
                s for b in doc.blocks if b.kind == "sigblock" for s in b.signers
            }
            for mention in brief.mentions:
                if surface_in_text(mention.surface, resolved):
                    continue
                if mention.kind == "person" and mention.entity in signers:
                    continue
                problems.append(
                    f"{doc.doc_id}: missing required mention "
                    f"{mention.surface!r} ({mention.entity})"
                )

    if problems:
        print("ingest: deliverable rejected:")
        for p in problems:
            print(f"  - {p}")
        return 1

    paths.docir_dir.mkdir(parents=True, exist_ok=True)
    for doc in deliverable.docs:
        target = docir_path(paths, doc.doc_id)
        target.write_text(dump_json(doc), encoding="utf-8")
        doc_state = state.doc(doc.doc_id)
        doc_state.authored_hash = sha256_file(target)
        state.docs[doc.doc_id] = doc_state

    clear_outstanding(state, "author")
    manifest = load_manifest(paths)
    remaining = [
        e
        for e in manifest
        if e.authoring == "batchable" and state.doc(e.doc_id).authored_hash is None
    ]
    if not remaining:
        state.mark_done("author")
    save_state(paths, state)
    print(
        f"ingest: merged {len(deliverable.docs)} docs; "
        f"{len(remaining)} batchable docs remaining"
    )
    return 0
