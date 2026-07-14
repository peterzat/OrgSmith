"""Unit tier: hard-case enforcement end to end.

A hard-case org (signature-page fee, filename-only minutes date) authored
through the scripted airlock renders and validates clean; ingest rejects
deliverables that surface a non-body fact in text; the LOC validator rules
fail deliberately corrupted copies in both directions.
"""

import json
import shutil
from datetime import date

import pytest

from orgsmith.artifacts import (
    load_charter,
    load_engagements,
    load_foundation,
    load_manifest,
    load_work_order,
)
from orgsmith.assemble import run_assemble
from orgsmith.authoring.contexts import run_next_batch
from orgsmith.authoring.ingest import run_ingest as ingest_author
from orgsmith.fabric.engagements import render_date
from orgsmith.paths import OrgPaths
from orgsmith.render import run_render
from orgsmith.render.docx import render_docx
from orgsmith.render.pdf import render_pdf
from orgsmith.render.styles import style_pack
from orgsmith.schemas import Block, DocIR
from orgsmith.state import load_state
from orgsmith.validate import run_validate

from conftest import (
    build_hardcase_stages,
    run_authoring,
    run_enrichment,
    scripted_authoring,
)

pytestmark = pytest.mark.unit


def _sig_fee(paths):
    facts = load_engagements(paths).fact_index()
    return next(
        f for f in facts.values() if f.location_policy == "signature_page"
    )


def _filename_fact(paths):
    facts = load_engagements(paths).fact_index()
    return next(f for f in facts.values() if f.location_policy == "filename")


def _entry_hosting(paths, fact_id):
    for entry in load_manifest(paths):
        if any(k.fact_id == fact_id for k in entry.key_facts):
            return entry
    raise AssertionError(f"no manifest entry hosts {fact_id}")


def _people_index(paths):
    foundation = load_foundation(paths)
    return {p.id: {"name": p.name, "title": p.title} for p in foundation.people}


# --- clean end-to-end -------------------------------------------------------


@pytest.fixture(scope="module")
def hard_rendered_org(tmp_path_factory):
    paths = build_hardcase_stages(tmp_path_factory.mktemp("hard-rendered"))
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_assemble(paths) == 0
    return paths


@pytest.fixture()
def org_copy(hard_rendered_org, tmp_path):
    shutil.copytree(hard_rendered_org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(hard_rendered_org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=hard_rendered_org.slug)


def test_hard_case_org_validates_clean(hard_rendered_org):
    assert run_validate(hard_rendered_org) == 0


def test_fee_only_on_signature_page(hard_rendered_org):
    from orgsmith.validate.rules import Context

    fee = _sig_fee(hard_rendered_org)
    entry = _entry_hosting(hard_rendered_org, fee.id)
    ctx = Context.load(hard_rendered_org)
    pages = ctx.doc_pages(entry)
    assert len(pages) >= 2, "sig page break should force a second page"
    assert fee.rendered in pages[-1]
    assert all(fee.rendered not in p for p in pages[:-1])


def test_minutes_date_only_in_filename(hard_rendered_org):
    from pathlib import PurePosixPath

    from orgsmith.validate.rules import Context

    md = _filename_fact(hard_rendered_org)
    entry = _entry_hosting(hard_rendered_org, md.id)
    assert md.rendered in PurePosixPath(entry.path).name
    ctx = Context.load(hard_rendered_org)
    assert md.rendered not in ctx.doc_text(entry)


# --- ingest rejections ------------------------------------------------------


@pytest.fixture(scope="module")
def hard_batch(tmp_path_factory):
    """Hard-case org with the first authoring work order outstanding.
    Failed ingests are all-or-nothing, so tests share the org."""
    paths = build_hardcase_stages(tmp_path_factory.mktemp("hard-batch"))
    run_enrichment(paths)
    assert run_next_batch(paths) == 0
    state = load_state(paths)
    wo = load_work_order(paths.workorders_dir / state.outstanding["author"])
    return paths, wo


def _tampered_reply(paths, wo, genre, extra_block):
    reply = scripted_authoring(wo)
    brief = next(b for b in wo.docs if b.genre == genre)
    doc = next(d for d in reply["docs"] if d["doc_id"] == brief.doc_id)
    doc["blocks"].append(extra_block)
    target = paths.workorders_dir / "tampered-reply.json"
    target.write_text(json.dumps(reply))
    return target


def test_ingest_rejects_sig_fact_placeholder(hard_batch, capsys):
    paths, wo = hard_batch
    fee = _sig_fee(paths)
    reply = _tampered_reply(
        paths, wo, "engagement_letter",
        {"kind": "paragraph", "text": "Fee per {{fact:%s}} as agreed." % fee.id},
    )
    assert ingest_author(paths, reply) == 1
    assert "signature-page-only" in capsys.readouterr().out


def test_ingest_rejects_sig_fact_literal(hard_batch, capsys):
    paths, wo = hard_batch
    fee = _sig_fee(paths)
    reply = _tampered_reply(
        paths, wo, "engagement_letter",
        {"kind": "paragraph", "text": f"The fee is {fee.rendered}."},
    )
    assert ingest_author(paths, reply) == 1
    assert "literal value" in capsys.readouterr().out


def test_ingest_rejects_filename_date_in_any_form(hard_batch, capsys):
    paths, wo = hard_batch
    md = _filename_fact(paths)
    long_form = render_date(date.fromisoformat(str(md.value)))
    reply = _tampered_reply(
        paths, wo, "meeting_minutes",
        {"kind": "paragraph", "text": f"The session was held {long_form}."},
    )
    assert ingest_author(paths, reply) == 1
    assert "its only home" in capsys.readouterr().out


def test_ingest_rejects_sigblock_in_filename_dated_doc(hard_batch, capsys):
    paths, wo = hard_batch
    brief = next(b for b in wo.docs if b.genre == "meeting_minutes")
    reply = _tampered_reply(
        paths, wo, "meeting_minutes",
        {"kind": "sigblock", "signers": [brief.authors[0].id]},
    )
    assert ingest_author(paths, reply) == 1
    assert "dated by filename only" in capsys.readouterr().out


# --- corruption: LOC rules fail both directions -----------------------------


def test_fee_leaked_into_body_fails_loc01(org_copy, capsys):
    fee = _sig_fee(org_copy)
    entry = _entry_hosting(org_copy, fee.id)
    charter = load_charter(org_copy)
    docir = DocIR(
        doc_id=entry.doc_id,
        blocks=[
            Block(kind="paragraph", text=f"Body leaks the fee: {fee.rendered}."),
            Block(kind="sigblock", signers=[entry.authors[0]]),
        ],
    )
    render_pdf(
        docir, entry, style_pack(charter), "Corruptor", _people_index(org_copy),
        org_copy.share_dir / entry.path, sig_fact_text=fee.rendered,
    )
    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out
    assert "LOC-01" in out and "leaked" in out


def test_fee_missing_from_signature_page_fails_loc01(org_copy, capsys):
    fee = _sig_fee(org_copy)
    entry = _entry_hosting(org_copy, fee.id)
    charter = load_charter(org_copy)
    docir = DocIR(
        doc_id=entry.doc_id,
        blocks=[
            Block(kind="paragraph", text="A letter that forgot its fee."),
            Block(kind="sigblock", signers=[entry.authors[0]]),
        ],
    )
    render_pdf(
        docir, entry, style_pack(charter), "Corruptor", _people_index(org_copy),
        org_copy.share_dir / entry.path,
    )
    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out
    assert "LOC-01" in out and "missing from the signature page" in out


def test_minutes_date_leaked_into_text_fails_loc02(org_copy, capsys):
    md = _filename_fact(org_copy)
    entry = _entry_hosting(org_copy, md.id)
    charter = load_charter(org_copy)
    docir = DocIR(
        doc_id=entry.doc_id,
        blocks=[
            Block(kind="paragraph", text=f"Held on {md.rendered}."),
            Block(kind="list", items=["Attendee One"]),
        ],
    )
    (org_copy.share_dir / entry.path).write_bytes(
        render_docx(
            docir, entry, style_pack(charter), "Corruptor",
            _people_index(org_copy),
        )
    )
    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out
    assert "LOC-02" in out and "appears in extractable text" in out


def test_minutes_filename_without_surface_fails_loc02(org_copy, capsys):
    md = _filename_fact(org_copy)
    ledger = org_copy.engagements_json
    text = ledger.read_text()
    needle = f'"rendered": "{md.rendered}"'
    assert needle in text
    ledger.write_text(text.replace(needle, '"rendered": "1999-01-01"', 1))
    assert run_validate(org_copy) == 1
    out = capsys.readouterr().out
    assert "LOC-02" in out and "missing from filename" in out
