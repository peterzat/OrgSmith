"""Unit tier: per-document section skeletons (M17b, part B).

M17's board, in its own sharpest note (`rf:voice-7`): per-person voice
genuinely works now, and what recurs is the per-genre OUTLINE. Two kickoff
memos by two authors two years apart came back as the same memo re-skinned,
because every fresh-context author was asked for the same document.

What is under test here is the PLUMBING and the two structural properties,
which is all this turn can prove. That authored prose stops converging is
settled by the next generation, and no test here asserts it.
"""

import json
import shutil

import pytest

from orgsmith.docplan.registry import OUTLINES, REGISTRY, assign_outlines
from orgsmith.paths import OrgPaths
from orgsmith.validate import run_validate

from conftest import (
    build_culture_stages,
    build_knobbed_stages,
    build_pure_stages,
)

pytestmark = pytest.mark.unit

ON = "  outline_variety: true\n"


class _Charter:
    """The two fields `assign_outlines` reads, and nothing else."""

    def __init__(self, seed=4242, on=True):
        self.seed = seed
        self.doc_culture = type("dc", (), {"outline_variety": on})()


def _rows(genre, n, engagement="E-2019-001"):
    return [(genre, "batchable", engagement)] * n


# --- the pool ---------------------------------------------------------------


def test_every_pool_has_at_least_two_variants():
    """A single-variant pool cannot deliver the no-adjacent-repeat property
    at all, and would quietly degrade to the behaviour this turn exists to
    remove."""
    for genre, pool in OUTLINES.items():
        assert len(pool) >= 2, genre


def test_outline_ids_are_unique_within_and_across_pools():
    """`render_params["outline"]` carries the id alone, so a duplicate would
    make two variants indistinguishable in the manifest."""
    seen = set()
    for genre, pool in OUTLINES.items():
        ids = [o.id for o in pool]
        assert len(ids) == len(set(ids)), genre
        assert not (set(ids) & seen), genre
        seen |= set(ids)


def test_every_pool_belongs_to_an_authored_genre():
    """A pool for a genre nothing plans, or for a static one, would deal
    skeletons no author ever sees."""
    authored = {r.genre for r in REGISTRY if r.authoring == "batchable"}
    assert set(OUTLINES) <= authored, set(OUTLINES) - authored


def test_no_variant_forbids_a_form_it_also_requires():
    """The self-contradiction that would make a genre unauthorable: a
    skeleton demanding a table it also forbids can never be satisfied."""
    for genre, pool in OUTLINES.items():
        for outline in pool:
            required = {s.form for s in outline.sections}
            assert not (required & set(outline.forbids)), (
                f"{genre}/{outline.id} requires and forbids "
                f"{sorted(required & set(outline.forbids))}"
            )


def test_minutes_never_forbid_a_list_and_letters_never_forbid_a_sigblock():
    """Two forms other mechanisms require: MENT-01 reads the attendee names
    a minutes list carries, and LOC-01 puts an engagement letter's fee on
    its signature page."""
    for outline in OUTLINES["meeting_minutes"]:
        assert "list" not in outline.forbids, outline.id
    for outline in OUTLINES["engagement_letter"]:
        assert "sigblock" not in outline.forbids, outline.id
        assert any(s.form == "sigblock" for s in outline.sections), outline.id


def test_variants_differ_in_what_a_document_contains():
    """The whole point. Variants that differ only in section NAMING would
    leave the underlying document identical, which is the defect. Compared
    on form sequence plus forbidden kinds, never on directive wording."""
    for genre, pool in OUTLINES.items():
        shapes = {tuple(s.form for s in o.sections) for o in pool}
        assert len(shapes) == len(pool), (
            f"{genre}: two variants share a block-form sequence, so they ask "
            f"for the same document -- and the variety measurement, which "
            f"counts distinct block shapes, would silently undercount"
        )


# --- the deal ---------------------------------------------------------------


def test_knob_off_assigns_nothing():
    assert assign_outlines(_Charter(on=False), _rows("kickoff_memo", 5)) == [
        None
    ] * 5


def test_the_deal_is_deterministic_across_runs():
    rows = _rows("status_report", 12)
    assert assign_outlines(_Charter(), rows) == assign_outlines(_Charter(), rows)


def test_a_different_seed_deals_differently():
    rows = _rows("status_report", 12)
    a = assign_outlines(_Charter(seed=1), rows)
    b = assign_outlines(_Charter(seed=2), rows)
    assert a != b, "the deal must depend on the charter seed"


def test_no_two_consecutive_documents_of_a_genre_share_a_skeleton():
    for genre in OUTLINES:
        got = assign_outlines(_Charter(), _rows(genre, 40))
        for i in range(1, len(got)):
            assert got[i] != got[i - 1], f"{genre} repeats at {i}: {got}"


def test_no_two_documents_of_one_genre_in_one_engagement_share_a_skeleton():
    """The second property, and the one shuffled cycles would NOT deliver:
    concurrent engagements interleave in the global genre order, so two
    cycles could put the same variant at two positions of one engagement.

    Asserted over the guaranteed regime (up to k-1 documents per engagement,
    see `assign_outlines`) and with the two engagements interleaved, which
    is the case a contiguous deal would get right by accident.
    """
    for genre, pool in OUTLINES.items():
        rows = []
        for _ in range(len(pool) - 1):
            rows.append((genre, "batchable", "E-2019-001"))
            rows.append((genre, "batchable", "E-2019-002"))
        got = assign_outlines(_Charter(), rows)
        for eid in ("E-2019-001", "E-2019-002"):
            mine = [o for (_, _, e), o in zip(rows, got) if e == eid]
            assert len(mine) == len(set(mine)), f"{genre}/{eid}: {mine}"


def test_the_guaranteed_regime_covers_every_fleet_engagement(tmp_path):
    """The bound is only useful if real orgs sit inside it. No engagement in
    the knobbed fixture takes more than k-1 documents of any pooled genre,
    so the guarantee above is the operative one and the degradation below is
    a corner rather than the common case."""
    paths = build_culture_stages(tmp_path, ON)
    counts: dict = {}
    for line in paths.manifest_jsonl.read_text().splitlines():
        entry = json.loads(line)
        if entry["authoring"] != "batchable" or entry["genre"] not in OUTLINES:
            continue
        key = (entry["genre"], entry["engagement"])
        counts[key] = counts.get(key, 0) + 1
    assert counts
    for (genre, engagement), n in counts.items():
        assert n <= len(OUTLINES[genre]) - 1, (
            f"{genre} in {engagement} takes {n} documents against a pool of "
            f"{len(OUTLINES[genre])}; widen the pool or accept a reuse"
        )


def test_an_engagement_that_outruns_the_pool_reuses_rather_than_fails():
    """Past the bound, both constraints cannot hold at once. The degradation
    is a repeat inside one engagement -- never a crash, and never an adjacent
    repeat, because OUT-01 enforces adjacency as a rule."""
    genre = "status_report"
    n = len(OUTLINES[genre])
    got = assign_outlines(_Charter(), _rows(genre, n + 3))
    assert len(got) == n + 3
    assert all(g is not None for g in got)
    assert len(set(got)) == n, "every variant should have been used"
    assert len(got) > len(set(got)), "past the bound, a variant must repeat"
    for i in range(1, len(got)):
        assert got[i] != got[i - 1], "adjacency survives pool exhaustion"


def test_genres_draw_from_independent_streams():
    """Per-genre streams, so adding documents of one genre cannot move
    another genre's deal."""
    rows_a = _rows("kickoff_memo", 6)
    rows_b = _rows("kickoff_memo", 6) + _rows("status_report", 6)
    got_a = assign_outlines(_Charter(), rows_a)
    got_b = assign_outlines(_Charter(), rows_b)[:6]
    assert got_a == got_b


def test_static_and_derived_rows_are_skipped_without_consuming_a_draw():
    """A derived duplicate is a byte copy of its source; giving it a
    skeleton would be meaningless, and letting it consume a draw would make
    the deal depend on the noise knobs."""
    genre = "kickoff_memo"
    clean = _rows(genre, 4)
    noisy = []
    for row in clean:
        noisy += [row, (genre, "derived", "E-2019-001")]
    got_noisy = assign_outlines(_Charter(), noisy)
    assert [g for g in got_noisy if g is not None] == assign_outlines(
        _Charter(), clean
    )
    assert got_noisy[1::2] == [None] * 4


def test_a_genre_with_no_pool_is_left_unassigned():
    """Mail carries no pool on purpose: a 110-word note has one shape."""
    assert assign_outlines(_Charter(), _rows("internal_email", 3)) == [None] * 3


# --- the plan ---------------------------------------------------------------


def test_knob_off_plans_no_outline(tmp_path):
    paths = build_pure_stages(tmp_path)
    for line in paths.manifest_jsonl.read_text().splitlines():
        assert "outline" not in json.loads(line)["render_params"]


def test_the_knob_moves_only_render_params(tmp_path):
    """Inertness at the manifest level: turning it on adds one render_params
    key and touches nothing else -- no date, no author, no path, no fact."""
    off = build_pure_stages(tmp_path / "off")
    on = build_culture_stages(tmp_path / "on", ON)

    def entries(paths):
        return [
            json.loads(line)
            for line in paths.manifest_jsonl.read_text().splitlines()
        ]

    off_e, on_e = entries(off), entries(on)
    assert len(off_e) == len(on_e)
    assigned = 0
    for a, b in zip(off_e, on_e):
        params = dict(b["render_params"])
        assigned += "outline" in params
        params.pop("outline", None)
        assert a["render_params"] == params, a["path"]
        assert {k: v for k, v in a.items() if k != "render_params"} == {
            k: v for k, v in b.items() if k != "render_params"
        }, a["path"]
    assert assigned, "the knob is on; some document must carry a skeleton"


def test_every_batchable_document_of_a_pooled_genre_gets_one(tmp_path):
    paths = build_culture_stages(tmp_path, ON)
    for line in paths.manifest_jsonl.read_text().splitlines():
        entry = json.loads(line)
        has = "outline" in entry["render_params"]
        want = entry["authoring"] == "batchable" and entry["genre"] in OUTLINES
        assert has == want, entry["path"]


# --- OUT-01 -----------------------------------------------------------------


@pytest.fixture(scope="module")
def outlined_org(tmp_path_factory):
    return build_knobbed_stages(tmp_path_factory.mktemp("out01"))


@pytest.fixture()
def outlined_copy(outlined_org, tmp_path):
    shutil.copytree(outlined_org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(outlined_org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=outlined_org.slug)


def _report(paths, capsys):
    capsys.readouterr()
    assert run_validate(paths, as_json=True) in (0, 1)
    return json.loads(capsys.readouterr().out)


def _findings(payload):
    return [f for f in payload["findings"] if f["rule"] == "OUT-01"]


def test_out_01_runs_clean_on_a_knob_on_org(outlined_org, capsys):
    payload = _report(outlined_org, capsys)
    assert "OUT-01" in payload["rules_run"]
    assert not _findings(payload)


def test_out_01_skips_visibly_when_the_knob_is_off(tmp_path, capsys):
    paths = build_pure_stages(tmp_path)
    payload = _report(paths, capsys)
    assert "OUT-01" not in payload["rules_run"]
    (skip,) = [s for s in payload["skipped"] if s["rule"] == "OUT-01"]
    assert "outline_variety" in skip["reason"]


def _rewrite(paths, mutate):
    lines = []
    for line in paths.manifest_jsonl.read_text().splitlines():
        entry = json.loads(line)
        mutate(entry)
        lines.append(json.dumps(entry))
    paths.manifest_jsonl.write_text("\n".join(lines) + "\n")


def test_out_01_catches_a_tampered_outline(outlined_copy, capsys):
    done = []

    def mutate(entry):
        if done or entry["render_params"].get("outline") is None:
            return
        pool = [o.id for o in OUTLINES[entry["genre"]]]
        current = entry["render_params"]["outline"]
        entry["render_params"]["outline"] = next(
            i for i in pool if i != current
        )
        done.append(entry["path"])

    _rewrite(outlined_copy, mutate)
    assert done
    findings = _findings(_report(outlined_copy, capsys))
    assert findings
    assert "does not recompute from the charter" in findings[0]["message"]


def test_out_01_catches_a_deleted_outline(outlined_copy, capsys):
    """A knob ON with its record missing is a failure, never a skip."""
    done = []

    def mutate(entry):
        if not done and entry["render_params"].get("outline") is not None:
            entry["render_params"].pop("outline")
            done.append(entry["path"])

    _rewrite(outlined_copy, mutate)
    assert done
    findings = _findings(_report(outlined_copy, capsys))
    assert findings
    assert "carries no outline" in findings[0]["message"]


def test_out_01_catches_an_outline_on_a_derived_document(outlined_copy, capsys):
    done = []

    def mutate(entry):
        if not done and entry["authoring"] == "derived":
            entry["render_params"]["outline"] = "km-narrative"
            done.append(entry["path"])

    _rewrite(outlined_copy, mutate)
    assert done, "the knobbed org plans no derived documents"
    findings = _findings(_report(outlined_copy, capsys))
    assert findings
    assert "the deal assigns none" in findings[0]["message"]


# --- the brief and ingest conformance (B2) ----------------------------------


@pytest.fixture(scope="module")
def briefed(tmp_path_factory):
    """A knob-on org with one authoring batch outstanding."""
    from orgsmith.authoring.contexts import run_next_batch

    from conftest import run_enrichment

    paths = build_knobbed_stages(tmp_path_factory.mktemp("outline-brief"))
    run_enrichment(paths)
    assert run_next_batch(paths) == 0
    return paths


@pytest.fixture()
def briefed_copy(briefed, tmp_path):
    """A per-test copy of the briefed org.

    Ingesting a batch clears it from `state.author_batches`, so the tests
    below would consume the module fixture's only outstanding batch for each
    other. Each gets its own tree instead.
    """
    shutil.copytree(briefed.root / "recipes", tmp_path / "recipes")
    shutil.copytree(briefed.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=briefed.slug)


def _wo(paths):
    from conftest import sole_author_wo

    return sole_author_wo(paths)


def test_the_brief_states_the_skeleton_and_what_it_forbids(briefed):
    from conftest import committed_outlines

    outlines = committed_outlines(briefed)
    order = _wo(briefed)
    checked = 0
    for brief in order.docs:
        outline = outlines.get(brief.doc_id)
        if outline is None:
            continue
        assert "STRUCTURE FOR THIS DOCUMENT" in brief.guidance
        for section in outline.sections:
            assert section.directive in brief.guidance, brief.doc_id
        for forbidden in outline.forbids:
            assert forbidden in brief.guidance.split("must contain NO")[-1]
        checked += 1
    assert checked


def test_a_knob_off_brief_carries_no_outline_text(tmp_path):
    from orgsmith.authoring.contexts import run_next_batch

    from conftest import run_enrichment, sole_author_wo

    paths = build_pure_stages(tmp_path)
    run_enrichment(paths)
    assert run_next_batch(paths) == 0
    for brief in sole_author_wo(paths).docs:
        assert "STRUCTURE FOR THIS DOCUMENT" not in brief.guidance


def test_a_knob_off_work_order_is_byte_identical(tmp_path):
    """The inertness claim, at the bytes. Nothing was added to `DocBrief`:
    the skeleton reaches the author through `guidance`, where every other
    structural instruction already lives, so a knob-off work order is the
    file it was before this feature existed."""
    from orgsmith.authoring.contexts import run_next_batch
    from orgsmith.state import load_state

    from conftest import run_enrichment

    def emit(root):
        paths = build_pure_stages(root)
        run_enrichment(paths)
        assert run_next_batch(paths) == 0
        ref = next(iter(load_state(paths).author_batches.values()))
        return (paths.workorders_dir / ref.workorder).read_bytes()

    first = emit(tmp_path / "a")
    second = emit(tmp_path / "b")
    assert first == second
    assert b"outline" not in first


def _deliver(paths, order, outlines, mutate=None):
    from conftest import scripted_authoring

    payload = scripted_authoring(order, outlines)
    if mutate:
        mutate(payload)
    return payload


def _ingest(paths, order, payload, name):
    from orgsmith.authoring.ingest import run_ingest as ingest_author

    reply = paths.workorders_dir / f"{name}.json"
    reply.write_text(json.dumps(payload))
    return ingest_author(paths, reply)


def _outlined_doc(order, outlines, predicate):
    for brief in order.docs:
        outline = outlines.get(brief.doc_id)
        if outline is not None and predicate(outline):
            return brief.doc_id, outline
    return None, None


def test_a_conforming_deliverable_passes(briefed_copy, capsys):
    from conftest import committed_outlines

    order = _wo(briefed_copy)
    outlines = committed_outlines(briefed_copy)
    capsys.readouterr()
    assert _ingest(briefed_copy, order, _deliver(briefed_copy, order, outlines), "ok") == 0


def test_a_forbidden_block_kind_is_rejected(briefed_copy, capsys):
    """The half that actually kills the blocker. "The same five numbered
    owners in the same order" cannot recur in a variant that may not
    contain a list -- but only because the ban is enforced rather than
    suggested."""
    from conftest import committed_outlines

    order = _wo(briefed_copy)
    outlines = committed_outlines(briefed_copy)
    doc_id, outline = _outlined_doc(
        order, outlines, lambda o: "list" in o.forbids
    )
    assert doc_id, "no briefed document forbids a list"

    def mutate(payload):
        for doc in payload["docs"]:
            if doc["doc_id"] == doc_id:
                doc["blocks"].append(
                    {"kind": "list", "items": ["One", "Two", "Three"]}
                )

    capsys.readouterr()
    assert _ingest(
        briefed_copy, order, _deliver(briefed_copy, order, outlines, mutate), "forbidden"
    ) == 1
    out = capsys.readouterr().out
    assert f"outline {outline.id!r} forbids list blocks" in out


def test_a_missing_required_form_is_rejected(briefed_copy, capsys):
    """A table section quietly reverting to prose is the failure the block
    count alone cannot see: paragraphs pad the count while the document goes
    back to the shape every sibling has."""
    from conftest import committed_outlines

    order = _wo(briefed_copy)
    outlines = committed_outlines(briefed_copy)
    # Whichever counted form this batch happens to offer. Keying off a
    # specific one would make the test depend on which documents the first
    # batch drew, which is batch luck rather than behaviour.
    form = None
    for candidate in ("table", "list", "sigblock"):
        doc_id, outline = _outlined_doc(
            order, outlines, lambda o, c=candidate: any(
                s.form == c for s in o.sections
            )
        )
        if doc_id:
            form = candidate
            break
    assert form, "no briefed document requires a counted form"
    want = sum(1 for s in outline.sections if s.form == form)

    def mutate(payload):
        for doc in payload["docs"]:
            if doc["doc_id"] == doc_id:
                doc["blocks"] = [
                    {"kind": "paragraph", "text": "Padding."}
                    if b["kind"] == form
                    else b
                    for b in doc["blocks"]
                ]

    capsys.readouterr()
    assert _ingest(
        briefed_copy, order, _deliver(briefed_copy, order, outlines, mutate), "noform"
    ) == 1
    out = capsys.readouterr().out
    assert f"outline {outline.id!r} calls for {want} {form} block(s)" in out


def test_a_document_with_too_few_blocks_is_rejected(briefed_copy, capsys):
    from conftest import committed_outlines

    order = _wo(briefed_copy)
    outlines = committed_outlines(briefed_copy)
    doc_id, outline = _outlined_doc(
        order, outlines, lambda o: len(o.sections) >= 3
    )
    assert doc_id

    def mutate(payload):
        for doc in payload["docs"]:
            if doc["doc_id"] == doc_id:
                doc["blocks"] = doc["blocks"][:1]

    capsys.readouterr()
    assert _ingest(
        briefed_copy, order, _deliver(briefed_copy, order, outlines, mutate), "short"
    ) == 1
    assert "every section needs at least one block" in capsys.readouterr().out


def test_conformance_is_not_an_ordering_check(briefed_copy, capsys):
    """Deliberately permissive on order. The goal is to make convergence
    structurally hard, not authoring brittle: a document that covers the
    right material in a defensible order has already stopped being its
    sibling."""
    from conftest import committed_outlines

    order = _wo(briefed_copy)
    outlines = committed_outlines(briefed_copy)

    def mutate(payload):
        for doc in payload["docs"]:
            # A sigblock must stay last for the renderer; everything before
            # it is fair game.
            body = [b for b in doc["blocks"] if b["kind"] != "sigblock"]
            sig = [b for b in doc["blocks"] if b["kind"] == "sigblock"]
            doc["blocks"] = list(reversed(body)) + sig

    capsys.readouterr()
    assert _ingest(
        briefed_copy, order, _deliver(briefed_copy, order, outlines, mutate), "reordered"
    ) == 0


def test_ingest_reads_the_manifest_not_the_brief(briefed_copy):
    """The skeleton has one definition, in the plan. A deliverable cannot
    talk its way out by disagreeing with the guidance it was handed, because
    the check never reads the guidance."""
    from orgsmith.authoring.contexts import outline_for
    from orgsmith.artifacts import load_manifest

    entries = {e.doc_id: e for e in load_manifest(briefed_copy)}
    order = _wo(briefed_copy)
    for brief in order.docs:
        entry = entries[brief.doc_id]
        from_manifest = outline_for(entry)
        if from_manifest is None:
            continue
        assert from_manifest.id == entry.render_params["outline"]


# --- variety, measured as counts (B3) ---------------------------------------
#
# The capability measurement, and the honest limit of what this turn can
# prove. Counts of distinct block shapes under a SCRIPTED author, never a
# similarity score: the scripted author writes the same sentence every time,
# so any lexical number here would measure the test double. Whether real
# prose stops converging is the next generation's question, and nothing here
# claims otherwise.


def _signatures(paths):
    """genre -> set of block-kind sequences, over authored documents.

    Block KINDS, not `structure.shape_tokens`. The shape tokens bucket
    paragraph and list lengths, so they would move with how many
    placeholders a document happens to carry -- length noise, not skeleton
    variety. The kind sequence is exactly what an outline determines.

    Derived documents are excluded: a duplicate is a byte copy of its
    source, so counting it would credit the noise stages with variety.
    """
    from orgsmith.artifacts import load_manifest
    from orgsmith.naming import doc_id_filename
    from orgsmith.schemas import DocIR

    out: dict = {}
    for entry in load_manifest(paths):
        if entry.authoring != "batchable":
            continue
        path = paths.docir_dir / doc_id_filename(entry.doc_id, ".json")
        if not path.exists():
            continue
        doc = DocIR.model_validate_json(path.read_text("utf-8"))
        out.setdefault(entry.genre, set()).add(
            tuple(b.kind for b in doc.blocks)
        )
    return out


def _doc_counts(paths):
    from orgsmith.artifacts import load_manifest

    counts: dict = {}
    for entry in load_manifest(paths):
        if entry.authoring == "batchable":
            counts[entry.genre] = counts.get(entry.genre, 0) + 1
    return counts


@pytest.fixture(scope="module")
def variety(tmp_path_factory):
    """The same recipe authored twice: knob off, knob on."""
    from conftest import run_authoring, run_enrichment

    root = tmp_path_factory.mktemp("variety")
    off = build_pure_stages(root / "off")
    on = build_culture_stages(root / "on", ON)
    for paths in (off, on):
        run_enrichment(paths)
        run_authoring(paths)
    return off, on


def test_knob_off_yields_exactly_one_shape_per_genre(variety):
    """The baseline the board described: every document of a genre is the
    same document. Under a scripted author that is literally true, which is
    what makes the knob-on count below meaningful rather than incidental."""
    off, _on = variety
    sigs = _signatures(off)
    assert sigs
    for genre, shapes in sigs.items():
        assert len(shapes) == 1, f"{genre}: {shapes}"


def test_knob_on_yields_a_shape_per_variant_the_corpus_can_reach(variety):
    """`min(pool size, documents of that genre)` -- the most distinct shapes
    the corpus has room for. Fewer would mean the deal repeated a variant it
    did not have to."""
    _off, on = variety
    sigs = _signatures(on)
    counts = _doc_counts(on)
    assert sigs
    checked = 0
    for genre, shapes in sigs.items():
        if genre not in OUTLINES:
            # No pool: this genre is expected to keep its single shape.
            assert len(shapes) == 1, f"{genre}: {shapes}"
            continue
        want = min(len(OUTLINES[genre]), counts[genre])
        assert len(shapes) >= want, (
            f"{genre}: {len(shapes)} distinct shapes over {counts[genre]} "
            f"documents against a pool of {len(OUTLINES[genre])}; expected "
            f"at least {want}"
        )
        checked += 1
    assert checked, "no pooled genre was authored"


def test_the_knob_strictly_increases_variety_somewhere(variety):
    """Stated as a comparison rather than as an absolute, so it cannot pass
    on a corpus that happened to be varied for some other reason."""
    off, on = variety
    off_sigs, on_sigs = _signatures(off), _signatures(on)
    improved = [
        genre
        for genre in on_sigs
        if len(on_sigs[genre]) > len(off_sigs.get(genre, set()))
    ]
    assert improved, "the knob changed no genre's shape count"
    assert set(improved) <= set(OUTLINES), (
        f"a genre with no pool gained shapes: {set(improved) - set(OUTLINES)}"
    )


def test_this_module_never_reaches_for_the_review_instrument():
    """A guard on the test file itself, as the module grows.

    The scripted author writes the same sentence every time, so any lexical
    or structural SCORE computed here would measure the test double and then
    read as evidence about prose. Variety is counted, never scored --
    enforced by asserting this module imports nothing from
    `orgsmith.review`, which is where every similarity number lives.
    """
    source = __import__("pathlib").Path(__file__).read_text()
    imports = [
        line.strip()
        for line in source.splitlines()
        if line.strip().startswith(("import ", "from "))
    ]
    offenders = [line for line in imports if "orgsmith.review" in line]
    assert not offenders, (
        f"this module imports from orgsmith.review ({offenders}); variety is "
        f"asserted as counts of distinct block shapes, never as a similarity "
        f"number"
    )
