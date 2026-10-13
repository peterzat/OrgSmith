"""Unit tier: a distribution-list broadcast names no one it was not about
(M17e, `mail.broadcasts_address_the_list`).

Mundane mail draws one or two colleagues per note. On a list-addressed note
the To header carries only the list, so those names had to appear in the
body: the M17 board found a broadcast that greeted one person by first name
and then named them in full to the room
(`mundane-broadcast-names-a-recipient-in-the-body`).
"""

from __future__ import annotations

import json

import pytest

from orgsmith.artifacts import load_manifest
from orgsmith.validate import run_validate

from conftest import build_culture_stages, run_enrichment

pytestmark = pytest.mark.unit

_FORMAT = "  format_mix: {docx: 12, pdf: 3, xlsx: 5, eml: 4}\n"
_MAIL = (
    "  mail:\n"
    "    business_hours: [9, 17]\n"
    "    max_thread_depth: 3\n"
    "    mundane_emails: 6\n"
    "    distribution_lists: 1\n"
)
_ON = "    broadcasts_address_the_list: true\n"


def _broadcasts(paths):
    return [e for e in load_manifest(paths) if e.render_params.get("dl")]


@pytest.fixture(scope="module")
def off(tmp_path_factory):
    return build_culture_stages(tmp_path_factory.mktemp("off"), _FORMAT + _MAIL)


@pytest.fixture(scope="module")
def on(tmp_path_factory):
    return build_culture_stages(tmp_path_factory.mktemp("on"), _FORMAT + _MAIL + _ON)


def test_off_a_broadcast_still_carries_drawn_recipients(off):
    casts = _broadcasts(off)
    assert casts, "the fixture planned no list-addressed note"
    assert all(e.participants for e in casts)
    assert all(
        any(m.entity in e.participants for m in e.mentions) for e in casts
    ), "with the knob off a broadcast still requires its drawn recipients"


def test_on_a_broadcast_has_no_individual_recipient(on):
    casts = _broadcasts(on)
    assert casts
    for e in casts:
        assert e.participants == [], e.path
        assert not [m for m in e.mentions if m.entity != e.authors[0]], e.path


def test_only_broadcasts_change(off, on):
    """The recipient draw still runs, so no later note moves: every other
    internal note plans exactly as before, and each broadcast keeps its path,
    date, authors and render params. Documents outside the mail genre are not
    checked here: the mentions a broadcast stops forcing count toward
    `min_mentions_per_person`, so with that floor on, the top-up pass may name
    the same person elsewhere (docs/RECIPE-FORMAT.md)."""
    a = {e.doc_id: e for e in load_manifest(off)}
    b = {e.doc_id: e for e in load_manifest(on)}
    assert a.keys() == b.keys()
    for doc_id, x in a.items():
        y = b[doc_id]
        if x.render_params.get("dl"):
            assert (x.path, x.date, x.authors, x.render_params) == (
                y.path, y.date, y.authors, y.render_params
            )
        elif x.genre == "internal_email":
            assert x.model_dump() == y.model_dump(), doc_id


def test_the_brief_tells_the_author_to_address_the_group(on):
    from orgsmith.artifacts import load_work_order
    from orgsmith.authoring.contexts import run_next_batch
    from orgsmith.state import load_state

    run_enrichment(on)
    prev = -1
    while True:
        assert run_next_batch(on) == 0
        n = len(load_state(on).author_batches)
        if n == prev:
            break
        prev = n
    cast_ids = {e.doc_id for e in _broadcasts(on)}
    briefs = [
        b
        for ref in load_state(on).author_batches.values()
        for b in load_work_order(on.workorders_dir / ref.workorder).docs
        if b.doc_id in cast_ids
    ]
    assert briefs and all("address the group, not one person" in b.guidance for b in briefs)
    assert all(b.participants == [] for b in briefs)


def test_dl_01_fails_a_broadcast_given_a_recipient_with_the_knob_on(on, tmp_path, capsys):
    import shutil

    from orgsmith.paths import OrgPaths

    shutil.copytree(on.root / "recipes", tmp_path / "recipes")
    shutil.copytree(on.root / "companies", tmp_path / "companies")
    paths = OrgPaths(root=tmp_path, slug=on.slug)
    lines = paths.manifest_jsonl.read_text().splitlines()
    out = []
    planted = False
    for line in lines:
        e = json.loads(line)
        if e.get("render_params", {}).get("dl") and not planted:
            e["participants"] = [e["authors"][0]]
            planted = True
        out.append(json.dumps(e))
    paths.manifest_jsonl.write_text("\n".join(out) + "\n")
    capsys.readouterr()
    run_validate(paths, as_json=True, only=["DL-01"])
    report = json.loads(capsys.readouterr().out)
    assert any("broadcasts_address_the_list" in f["message"] for f in report["findings"])
