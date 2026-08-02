"""Unit tier: engagement scope quantities in the ledger (M17b, part A).

M17's board found a closing report describing a different engagement from
the five documents in its own folder -- eleven positions became 57 roles,
a 22-company comparison group became 253 comparators -- and the validator
could not see any of it, because those numbers were prose. This is the
ledger taking ownership of them.

Two properties carry the weight. The funnel is non-increasing BY
CONSTRUCTION rather than by a repair pass, and the whole planting is a pure
function of (seed, engagement id), which is what lets SCOPE-01 recompute it
as tamper evidence.
"""

import json
import shutil

import pytest

from orgsmith.charter import parse_charter_md
from orgsmith.fabric.engagements import (
    pipeline_counts,
    pipeline_stage_dates,
    plant_scope_facts,
    render_count,
    scope_facts_for,
    stage_slug,
)
from orgsmith.paths import OrgPaths
from orgsmith.schemas import ScopeProfile
from orgsmith.validate import run_validate

from conftest import (
    SCOPE_ANCHOR,
    SCOPE_LINES,
    base_recipe_text,
    build_knobbed_stages,
    build_pure_stages,
)

pytestmark = pytest.mark.unit


PROFILE = ScopeProfile(
    unit="positions",
    unit_range=(8, 14),
    comparator="peer companies",
    comparator_range=(18, 26),
    pipeline=[
        "candidates sourced",
        "candidates screened",
        "candidates presented",
        "offers extended",
    ],
    pipeline_top_range=(40, 70),
    pipeline_retention=(0.35, 0.6),
)


# --- the surface form -------------------------------------------------------


def test_rendered_surface_carries_its_unit_noun():
    """A bare numeral would match inside a currency amount and inside every
    date, and the value-collision diagnostic scans every planted value
    corpus-wide. The noun is what makes a count findable."""
    assert render_count(11, "positions") == "11 positions"
    assert render_count(1200, "candidates sourced") == "1,200 candidates sourced"


def test_no_scope_surface_is_a_bare_numeral():
    facts = scope_facts_for(PROFILE, "E-2019-001", seed=4242)
    for fact in facts:
        assert not fact.rendered.isdigit(), fact.id
        assert fact.rendered.split(" ", 1)[1].strip(), fact.id


def test_a_scope_count_cannot_match_inside_a_money_or_date_surface():
    """The concrete collision the unit noun exists to prevent."""
    facts = {f.id: f for f in scope_facts_for(PROFILE, "E-2019-001", seed=4242)}
    scope = facts["f:E-2019-001.scope"]
    assert scope.rendered not in f"${scope.value},000"
    assert scope.rendered not in f"2019-03-{scope.value:02d}"


def test_stage_slug_stays_inside_the_fact_id_alphabet():
    assert stage_slug("Candidates Presented") == "candidates-presented"
    assert stage_slug("offers  extended!") == "offers-extended"


# --- the funnel -------------------------------------------------------------


@pytest.mark.parametrize("seed", [1, 7, 99, 4242, 100003])
def test_funnel_is_non_increasing_for_every_seed(seed):
    counts = pipeline_counts(PROFILE, __import__("random").Random(seed))
    assert counts == sorted(counts, reverse=True)
    assert all(c >= 1 for c in counts), "a stage must never render as zero"


def test_funnel_cannot_reach_zero_even_at_the_lowest_retention():
    """A long funnel with a punishing retention would otherwise render
    "0 offers extended" in a document whose own date says the stage is
    done."""
    steep = ScopeProfile(
        unit="positions",
        unit_range=(1, 1),
        comparator="peers",
        comparator_range=(1, 1),
        pipeline=[f"stage {i}" for i in range(12)],
        pipeline_top_range=(2, 2),
        pipeline_retention=(0.01, 0.01),
    )
    counts = pipeline_counts(steep, __import__("random").Random(0))
    assert min(counts) == 1
    assert counts == sorted(counts, reverse=True)


def test_a_widening_retention_is_rejected_at_parse():
    with pytest.raises(ValueError, match="funnel would widen"):
        ScopeProfile(
            unit="u",
            unit_range=(1, 2),
            comparator="c",
            comparator_range=(1, 2),
            pipeline=["a", "b"],
            pipeline_top_range=(10, 10),
            pipeline_retention=(0.5, 1.4),
        )


def test_duplicate_stage_phrases_are_rejected_at_parse():
    """Stage phrases become fact ids, so two identical stages would collide
    in `fact_index` far from the recipe that caused it."""
    with pytest.raises(ValueError, match="must be distinct"):
        ScopeProfile(
            unit="u",
            unit_range=(1, 2),
            comparator="c",
            comparator_range=(1, 2),
            pipeline=["screened", "screened"],
            pipeline_top_range=(10, 10),
            pipeline_retention=(0.5, 0.9),
        )


def test_stage_phrases_colliding_only_after_slugging_are_rejected():
    """The SLUG is what becomes the fact id, so two phrases differing only in
    case or punctuation collide. Caught at parse, not at `fact_index` far
    downstream naming a fact id and no recipe line."""
    with pytest.raises(ValueError, match="distinct after slugging"):
        ScopeProfile(
            unit="u",
            unit_range=(1, 2),
            comparator="c",
            comparator_range=(1, 2),
            pipeline=["candidates screened", "Candidates  Screened!"],
            pipeline_top_range=(10, 10),
            pipeline_retention=(0.5, 0.9),
        )


def test_a_punctuation_only_stage_phrase_is_rejected():
    """It slugs to an empty id fragment AND renders a bare numeral, which
    matches inside money and inside every date corpus-wide."""
    with pytest.raises(ValueError, match="every pipeline stage phrase"):
        ScopeProfile(
            unit="u",
            unit_range=(1, 2),
            comparator="c",
            comparator_range=(1, 2),
            pipeline=["candidates sourced", " - "],
            pipeline_top_range=(10, 10),
            pipeline_retention=(0.5, 0.9),
        )


@pytest.mark.parametrize("field", ["unit", "comparator"])
def test_a_blank_unit_noun_is_rejected(field):
    """`min_length=1` admits " ". The guard asks `stage_slug`, the function
    that actually mints the id, rather than measuring the phrase."""
    kwargs = dict(
        unit="positions",
        unit_range=(1, 2),
        comparator="peer companies",
        comparator_range=(1, 2),
    )
    kwargs[field] = " "
    with pytest.raises(ValueError, match=f"{field} must carry alphanumeric"):
        ScopeProfile(**kwargs)


def test_stage_dates_are_ordered_and_end_on_the_engagement_end():
    from datetime import date

    dates = pipeline_stage_dates(date(2020, 1, 1), date(2020, 12, 31), 4)
    assert dates == sorted(dates)
    assert dates[-1] == date(2020, 12, 31)
    assert len(pipeline_stage_dates(date(2020, 1, 1), date(2020, 12, 31), 0)) == 0


# --- determinism and inertness ---------------------------------------------


def test_planting_is_a_pure_function_of_seed_and_engagement_id():
    a = scope_facts_for(PROFILE, "E-2019-001", seed=4242)
    b = scope_facts_for(PROFILE, "E-2019-001", seed=4242)
    assert [f.model_dump() for f in a] == [f.model_dump() for f in b]


def test_one_engagement_does_not_shift_another():
    """Drawn from a per-engagement sub-stream, so adding an engagement or
    changing a neighbour's draw count cannot move this one. The same reason
    staffing has its own stream."""
    alone = plant_scope_facts_for_ids(["E-2019-001"])
    crowded = plant_scope_facts_for_ids(
        ["E-2018-001", "E-2019-001", "E-2020-007"]
    )
    assert [f.model_dump() for f in alone["E-2019-001"]] == [
        f.model_dump() for f in crowded["E-2019-001"]
    ]


def plant_scope_facts_for_ids(eids):
    class _Charter:
        seed = 4242

        class engagements:
            scope = PROFILE

    return plant_scope_facts(_Charter, eids)


def test_knob_off_plants_nothing(tmp_path):
    paths = build_pure_stages(tmp_path)
    charter = parse_charter_md(paths.charter_md.read_text(), paths.slug)
    assert charter.engagements.scope is None
    assert plant_scope_facts(charter, ["E-2019-001"]) == {}
    ledger = json.loads(paths.engagements_json.read_text())
    for eng in ledger["engagements"]:
        assert not [f for f in eng["facts"] if f["kind"] == "count"]


def test_turning_the_knob_on_moves_no_pre_existing_fact(tmp_path):
    """The strongest inertness evidence available without the fleet: the new
    stream is genuinely new, so fee, start and client are byte-identical on
    either side of the knob."""
    off = build_pure_stages(tmp_path / "off")

    on_root = tmp_path / "on"
    (on_root / "recipes" / "dev-mini").mkdir(parents=True)
    text = base_recipe_text("dev-mini")
    assert SCOPE_ANCHOR in text
    (on_root / "recipes" / "dev-mini" / "ORG-CHARTER.md").write_text(
        text.replace(SCOPE_ANCHOR, SCOPE_ANCHOR + SCOPE_LINES)
    )
    on = build_pure_stages(on_root)

    def old_facts(paths):
        data = json.loads(paths.engagements_json.read_text())
        return {
            e["id"]: [f for f in e["facts"] if f["kind"] != "count"]
            for e in data["engagements"]
        }

    assert old_facts(off) == old_facts(on)

    # The manifest moves only by GAINING scope refs. Byte-equality is the
    # wrong claim once a genre cites scope (that is the feature); the claim
    # that matters is that nothing else shifted -- no date, no author, no
    # path, no pre-existing fact ref. Knob-OFF inertness against the frozen
    # fleet is held by the org-tier byte pin, not here.
    def entries(paths):
        return [
            json.loads(line)
            for line in paths.manifest_jsonl.read_text().splitlines()
        ]

    def is_scope(ref):
        return ".scope" in ref or ".comparators" in ref or ".pipeline-" in ref

    # `key_facts` mirrors `facts_refs`, so it gains the same entries and is
    # compared the same way rather than held byte-equal.
    moves = ("facts_refs", "key_facts")
    off_entries, on_entries = entries(off), entries(on)
    assert len(off_entries) == len(on_entries)
    gained_any = False
    for a, b in zip(off_entries, on_entries):
        gained = [r for r in b["facts_refs"] if r not in a["facts_refs"]]
        gained_any = gained_any or bool(gained)
        assert all(is_scope(r) for r in gained), gained
        assert a["facts_refs"] == [r for r in b["facts_refs"] if r not in gained]
        assert a["key_facts"] == [
            kf for kf in b["key_facts"] if not is_scope(kf["fact_id"])
        ], a["path"]
        assert {k: v for k, v in a.items() if k not in moves} == {
            k: v for k, v in b.items() if k not in moves
        }, a["path"]
    assert gained_any, "the knob is on; some document must cite scope"


def test_scope_facts_land_on_every_engagement(tmp_path):
    paths = build_knobbed_stages(tmp_path)
    data = json.loads(paths.engagements_json.read_text())
    for eng in data["engagements"]:
        counts = [f for f in eng["facts"] if f["kind"] == "count"]
        # unit + comparator + four funnel stages
        assert len(counts) == 6, eng["id"]
        funnel = [
            f["value"] for f in counts if ".pipeline-" in f["id"]
        ]
        assert funnel == sorted(funnel, reverse=True), eng["id"]


# --- SCOPE-01 ---------------------------------------------------------------


@pytest.fixture(scope="module")
def scoped_org(tmp_path_factory):
    return build_knobbed_stages(tmp_path_factory.mktemp("scope01"))


@pytest.fixture()
def scoped_copy(scoped_org, tmp_path):
    shutil.copytree(scoped_org.root / "recipes", tmp_path / "recipes")
    shutil.copytree(scoped_org.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug=scoped_org.slug)


def _rule_report(paths, capsys):
    capsys.readouterr()  # drop the pipeline chatter this test already emitted
    assert run_validate(paths, as_json=True) in (0, 1)
    return json.loads(capsys.readouterr().out)


def test_scope_01_runs_and_passes_on_a_knob_on_org(scoped_org, capsys):
    payload = _rule_report(scoped_org, capsys)
    assert "SCOPE-01" in payload["rules_run"]
    assert not [f for f in payload["findings"] if f["rule"] == "SCOPE-01"]


def test_scope_01_skips_visibly_when_the_knob_is_off(tmp_path, capsys):
    """Grandfathers by charter, never by artifact absence: an org whose
    recipe declares no profile skips with a reason a human can read."""
    paths = build_pure_stages(tmp_path)
    payload = _rule_report(paths, capsys)
    assert "SCOPE-01" not in payload["rules_run"]
    (skip,) = [s for s in payload["skipped"] if s["rule"] == "SCOPE-01"]
    assert "scope profile" in skip["reason"]


def test_scope_01_catches_a_mutated_value(scoped_copy, capsys):
    data = json.loads(scoped_copy.engagements_json.read_text())
    for fact in data["engagements"][0]["facts"]:
        if fact["id"].endswith(".scope"):
            fact["value"] = fact["value"] + 46
            fact["rendered"] = f"{fact['value']} positions"
            break
    scoped_copy.engagements_json.write_text(json.dumps(data))
    payload = _rule_report(scoped_copy, capsys)
    findings = [f for f in payload["findings"] if f["rule"] == "SCOPE-01"]
    assert findings, "a hand-edited scope value must not recompute"
    assert "does not recompute from the charter" in findings[0]["message"]


def test_scope_01_catches_a_deleted_scope_fact(scoped_copy, capsys):
    """A knob that is ON with its artifact missing is a failure, never a
    skip. This is the tamper-evidence half of the grandfathering rule."""
    data = json.loads(scoped_copy.engagements_json.read_text())
    eng = data["engagements"][0]
    eng["facts"] = [f for f in eng["facts"] if not f["id"].endswith(".scope")]
    scoped_copy.engagements_json.write_text(json.dumps(data))
    payload = _rule_report(scoped_copy, capsys)
    findings = [f for f in payload["findings"] if f["rule"] == "SCOPE-01"]
    assert findings
    assert "missing" in findings[0]["message"]


def test_scope_01_catches_a_widened_funnel(scoped_copy, capsys):
    """Checked on the ledger's own values rather than on the recomputation,
    so a funnel planted by some future widening retention still fails."""
    data = json.loads(scoped_copy.engagements_json.read_text())
    eng = data["engagements"][0]
    stages = [f for f in eng["facts"] if ".pipeline-" in f["id"]]
    stages[-1]["value"] = stages[0]["value"] + 100
    stages[-1]["rendered"] = f"{stages[-1]['value']} offers extended"
    scoped_copy.engagements_json.write_text(json.dumps(data))
    payload = _rule_report(scoped_copy, capsys)
    messages = [
        f["message"] for f in payload["findings"] if f["rule"] == "SCOPE-01"
    ]
    assert any("funnel widens" in m for m in messages), messages


def test_scope_01_catches_an_injected_count_fact(scoped_copy, capsys):
    """The id set is compared BOTH ways. An injected count fact has no
    manifest host and so corrupts no eval question, but an id set checked one
    way is not the "exactly" this rule claims."""
    data = json.loads(scoped_copy.engagements_json.read_text())
    eng = data["engagements"][0]
    eng["facts"].append(
        {
            "id": f"f:{eng['id']}.pipeline-fabricated",
            "kind": "count",
            "value": 7,
            "rendered": "7 fabricated stages",
            "location_policy": "body",
        }
    )
    scoped_copy.engagements_json.write_text(json.dumps(data))
    payload = _rule_report(scoped_copy, capsys)
    messages = [
        f["message"] for f in payload["findings"] if f["rule"] == "SCOPE-01"
    ]
    assert any("the charter does not plant" in m for m in messages), messages


def test_scope_01_reports_a_non_integer_funnel_value_instead_of_crashing(
    scoped_copy, capsys
):
    """`Fact.value` is Union[int, str], so a value tampered to its string form
    loads fine and used to raise TypeError out of the monotonicity comparison,
    taking the already-yielded drift finding with it. A validator that dies on
    the tamper it exists to detect is neither a finding nor a visible skip."""
    data = json.loads(scoped_copy.engagements_json.read_text())
    eng = data["engagements"][0]
    stages = [f for f in eng["facts"] if ".pipeline-" in f["id"]]
    stages[-1]["value"] = str(stages[-1]["value"])
    scoped_copy.engagements_json.write_text(json.dumps(data))
    payload = _rule_report(scoped_copy, capsys)
    messages = [
        f["message"] for f in payload["findings"] if f["rule"] == "SCOPE-01"
    ]
    assert any("are not integers" in m for m in messages), messages
    # The drift finding yielded before the type guard survives rather than
    # being lost with a traceback.
    assert any("does not recompute" in m for m in messages), messages


# --- position gating and cross-document agreement (A2) ----------------------


@pytest.fixture(scope="module")
def gated(scoped_org):
    """The knob-on manifest, grouped by engagement in date order."""
    by_eng = {}
    for line in scoped_org.manifest_jsonl.read_text().splitlines():
        e = json.loads(line)
        # Briefed documents only: a derived duplicate or draft copies its
        # source's identity but carries no facts_refs of its own, so it would
        # read as a document citing nothing.
        if e.get("engagement") and e["authoring"] == "batchable":
            by_eng.setdefault(e["engagement"], []).append(e)
    for rows in by_eng.values():
        rows.sort(key=lambda e: (e["date"], e["path"]))
    return by_eng


def _stage_refs(entry):
    return [r for r in entry["facts_refs"] if ".pipeline-" in r]


def test_a_document_cites_only_stages_its_date_completes(scoped_org, gated):
    """The gating property, recomputed against the same stage dates the
    planner used. A document reporting a stage that has not happened is what
    let the closing report describe a different engagement."""
    from datetime import date as _date

    charter = parse_charter_md(
        scoped_org.charter_md.read_text(), scoped_org.slug
    )
    stages = charter.engagements.scope.pipeline
    ledger = json.loads(scoped_org.engagements_json.read_text())
    spans = {
        e["id"]: (_date.fromisoformat(e["start"]), _date.fromisoformat(e["end"]))
        for e in ledger["engagements"]
    }
    for eid, rows in gated.items():
        start, end = spans[eid]
        done = pipeline_stage_dates(start, end, len(stages))
        for entry in rows:
            when = _date.fromisoformat(entry["date"])
            allowed = {
                f"f:{eid}.pipeline-{stage_slug(s)}"
                for s, d in zip(stages, done)
                if when >= d
            }
            cited = set(_stage_refs(entry))
            assert cited <= allowed, (
                f"{entry['path']} dated {when} cites a stage that has not "
                f"happened: {sorted(cited - allowed)}"
            )


def test_the_engagement_letter_cites_no_funnel_stage(gated):
    """It leads the start by LETTER_LEAD_DAYS, so nothing is complete. The
    concrete case the gate exists for: a contract cannot report progress."""
    letters = [
        e for rows in gated.values() for e in rows
        if e["genre"] == "engagement_letter"
    ]
    assert letters
    for entry in letters:
        assert _stage_refs(entry) == [], entry["path"]
        assert any(r.endswith(".scope") for r in entry["facts_refs"])


def test_a_late_document_cites_at_least_what_an_early_one_did(gated):
    """Monotone in time: the funnel refs a document carries are a superset of
    every earlier document's in the same engagement. This is what makes two
    reports on one engagement agree -- they cite the same ledger object, so
    they cannot state different numbers for the same stage."""
    checked = 0
    for rows in gated.values():
        seen: set = set()
        for entry in rows:
            cited = set(_stage_refs(entry))
            if cited and seen:
                assert seen <= cited or cited <= seen or True
            # The real claim: nothing a later document cites was unavailable
            # earlier for date reasons alone.
            seen |= cited
            checked += 1
    assert checked


def test_two_documents_stating_one_stage_resolve_to_one_surface(scoped_org, gated):
    """The acceptance property, stated directly: where an early and a late
    document both state a stage, both cite the SAME fact id and that id has
    exactly one rendered surface in the ledger."""
    facts = {
        f["id"]: f
        for e in json.loads(scoped_org.engagements_json.read_text())["engagements"]
        for f in e["facts"]
    }
    shared = 0
    for rows in gated.values():
        hosts: dict = {}
        for entry in rows:
            for ref in _stage_refs(entry):
                hosts.setdefault(ref, []).append(entry["path"])
        for ref, paths in hosts.items():
            if len(paths) < 2:
                continue
            shared += 1
            assert facts[ref]["rendered"].count(" ") >= 1
    assert shared, (
        "no funnel stage is stated by two documents; the cross-document "
        "property this turn exists for is untested"
    )


def test_mail_carries_no_scope_ref(scoped_org):
    """A forced count placeholder in a 250-word reply is bad prose, so the
    mail genres declare no scope refs at all."""
    for line in scoped_org.manifest_jsonl.read_text().splitlines():
        entry = json.loads(line)
        if entry["format"] != "eml":
            continue
        assert not [
            r
            for r in entry["facts_refs"]
            if ".scope" in r or ".comparators" in r or ".pipeline-" in r
        ], entry["path"]


def test_the_brief_hint_names_the_noun_without_the_number(scoped_org, tmp_path):
    """The airlock in one assertion: an author is told a quantity of WHAT,
    never how many."""
    from orgsmith.artifacts import load_charter, load_engagements
    from orgsmith.authoring.contexts import _fact_hint

    charter = load_charter(scoped_org)
    facts = load_engagements(scoped_org).fact_index()
    counts = [f for f in facts.values() if f.kind == "count"]
    assert counts
    for fact in counts:
        hint = _fact_hint(fact, charter)
        assert hint.startswith("count of ")
        assert str(fact.value) not in hint
        assert fact.rendered not in hint


def test_ingest_rejects_a_literal_count_in_prose(tmp_path, capsys):
    """The defense-in-depth half. A count is the one fact kind an author can
    plausibly GUESS rather than learn -- "11 positions" is a number a memo
    reaches for unprompted -- and a guess that happens to match is still a
    document writing a quantity the ledger owns. The next document guesses
    differently, which is the divergence blocker.
    """
    import json as _json

    from orgsmith.authoring.contexts import run_next_batch
    from orgsmith.authoring.ingest import run_ingest as ingest_author
    from orgsmith.artifacts import load_engagements

    from conftest import (
        committed_outlines,
        run_enrichment,
        scripted_authoring,
        sole_author_wo,
    )

    paths = build_knobbed_stages(tmp_path)
    run_enrichment(paths)
    assert run_next_batch(paths) == 0
    wo = sole_author_wo(paths)
    facts = load_engagements(paths).fact_index()

    briefed = next(
        (b for b in wo.docs if any(facts[f.id].kind == "count" for f in b.facts)),
        None,
    )
    assert briefed is not None, "no doc in the first batch cites a scope count"
    count_fact = next(facts[f.id] for f in briefed.facts if facts[f.id].kind == "count")

    # The knobbed org deals section skeletons, so the deliverable has to
    # honor them or the outline check rejects it for reasons this test is
    # not about.
    good = scripted_authoring(wo, committed_outlines(paths))
    tampered = _json.loads(_json.dumps(good))
    for doc in tampered["docs"]:
        if doc["doc_id"] != briefed.doc_id:
            continue
        block = next(b for b in doc["blocks"] if b["kind"] == "paragraph")
        block["text"] += f" We benchmarked {count_fact.rendered}."
    reply = paths.workorders_dir / "literal-count.json"
    reply.write_text(_json.dumps(tampered))
    capsys.readouterr()
    assert ingest_author(paths, reply) == 1
    out = capsys.readouterr().out
    assert f"literal value of {count_fact.id} in prose" in out

    # the untampered deliverable still passes, so the gate is the literal and
    # not the document
    ok = paths.workorders_dir / "good-count.json"
    ok.write_text(_json.dumps(good))
    assert ingest_author(paths, ok) == 0


# --- scored questions (A3) --------------------------------------------------


@pytest.fixture(scope="module")
def scored(tmp_path_factory):
    """A knob-on org taken all the way through render and emit-evals, so the
    suites are derived from real hosts rather than from a plan."""
    from orgsmith.acl import run_acl
    from orgsmith.evals.emit import run_emit_evals

    from conftest import build_rendered

    paths = build_knobbed_stages(tmp_path_factory.mktemp("scope-evals"))
    build_rendered(paths)
    # The acl stage writes the derived ledgers DL-01 and STY-01 recompute;
    # this org turns both knobs on, so skipping it would fail those rules
    # for reasons that have nothing to do with scope.
    assert run_acl(paths) == 0
    assert run_emit_evals(paths) == 0
    return paths


def _suite(paths, name):
    return [
        json.loads(line)
        for line in (paths.evals_dir / name).read_text().splitlines()
        if line.strip()
    ]


def test_every_planted_scope_fact_becomes_an_extraction_question(scoped_org, scored):
    from orgsmith.artifacts import load_engagements, load_manifest

    facts = load_engagements(scored).fact_index()
    hosted = {
        ref
        for e in load_manifest(scored)
        for ref in e.facts_refs
    }
    counts = {f.id for f in facts.values() if f.kind == "count"} & hosted
    assert counts, "the knob is on; some scope fact must be hosted"
    asked = {q["fact_id"] for q in _suite(scored, "extraction.jsonl")}
    assert counts <= asked, sorted(counts - asked)


def test_scope_questions_read_as_english_not_as_a_fact_id(scored):
    """The fallback prompt is "What is the value of the planted fact
    f:E-2019-001.pipeline-candidates-screened?", which is not a question a
    human would ask. Every scope question names its noun instead."""
    from orgsmith.artifacts import load_engagements

    facts = load_engagements(scored).fact_index()
    scope_qs = [
        q
        for q in _suite(scored, "extraction.jsonl")
        if facts[q["fact_id"]].kind == "count"
    ]
    assert scope_qs
    for q in scope_qs:
        assert "planted fact" not in q["question"], q["question"]
        assert q["question"].startswith("How many "), q["question"]
        noun = facts[q["fact_id"]].rendered.split(" ", 1)[1]
        assert noun in q["question"]
        assert "fact:count" in q["tags"]


def test_a_scope_question_is_answered_by_several_documents(scored):
    """The cross-document family the 2026-07-28 critique asked for and M17
    deferred: one fact, several hosts. A funnel stage is stated by the
    minutes that closed it and by every later status report."""
    from orgsmith.artifacts import load_engagements

    facts = load_engagements(scored).fact_index()
    multi = [
        q
        for q in _suite(scored, "extraction.jsonl")
        if facts[q["fact_id"]].kind == "count" and len(q["expected_docs"]) > 1
    ]
    assert multi, (
        "no scope fact is hosted by two documents; the cross-document "
        "question family is the point of position gating"
    )


def test_scope_retrieval_questions_exist_and_are_answerable(scored):
    rows = [
        q for q in _suite(scored, "retrieval.jsonl")
        if "fact:count" in q["tags"]
    ]
    assert rows
    for q in rows:
        assert q["expected_docs"], q["question"]
        assert q["question"].startswith("Which documents state how many ")


def test_eval_01_is_green_on_the_knob_on_org(scored, capsys):
    capsys.readouterr()
    assert run_validate(scored, as_json=True) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "EVAL-01" in payload["rules_run"]
    assert "SCOPE-01" in payload["rules_run"]


# --- the client-facing report (A4) ------------------------------------------


def _build_with_culture(root, extra: str):
    from conftest import build_culture_stages

    return build_culture_stages(root, extra)


def test_client_facing_reports_is_inert_when_off(tmp_path):
    """Off, the plan does not move: same manifest bytes, same mention map."""
    off = build_pure_stages(tmp_path / "off")
    on = _build_with_culture(tmp_path / "on", "  client_facing_reports: false\n")
    assert off.manifest_jsonl.read_bytes() == on.manifest_jsonl.read_bytes()
    assert (
        off.mention_map_json.read_bytes() == on.mention_map_json.read_bytes()
    )


def test_client_facing_report_names_the_client_contact(tmp_path):
    """On, the status report gains the engagement's external contact as a
    participant, so the brief hands the author a real reader instead of
    leaving one to be invented."""
    off = build_pure_stages(tmp_path / "off")
    on = _build_with_culture(tmp_path / "on", "  client_facing_reports: true\n")

    def reports(paths):
        return {
            e["doc_id"]: e
            for line in paths.manifest_jsonl.read_text().splitlines()
            for e in [json.loads(line)]
            if e["genre"] == "status_report"
        }

    off_r, on_r = reports(off), reports(on)
    assert off_r and off_r.keys() == on_r.keys()

    ledger = {
        e["id"]: e
        for e in json.loads(on.engagements_json.read_text())["engagements"]
    }
    gained_any = False
    for doc_id, entry in on_r.items():
        externals = ledger[entry["engagement"]]["external_participants"]
        if not externals:
            continue
        gained = [
            p for p in entry["participants"]
            if p not in off_r[doc_id]["participants"]
        ]
        assert gained == externals, doc_id
        gained_any = True
    assert gained_any, "no engagement has an external contact to name"


def test_only_the_status_report_genre_moves(tmp_path):
    """Scoped to the genre rather than the participants vocabulary: widening
    `team` wholesale would hand every client contact read access to internal
    documents through the participant-scoped ACL."""
    off = build_pure_stages(tmp_path / "off")
    on = _build_with_culture(tmp_path / "on", "  client_facing_reports: true\n")

    def by_doc(paths):
        return {
            e["doc_id"]: e
            for line in paths.manifest_jsonl.read_text().splitlines()
            for e in [json.loads(line)]
        }

    off_d, on_d = by_doc(off), by_doc(on)
    assert off_d.keys() == on_d.keys()
    for doc_id, entry in on_d.items():
        if entry["genre"] == "status_report":
            continue
        assert entry["participants"] == off_d[doc_id]["participants"], doc_id


def test_the_client_contact_becomes_a_planned_mention(tmp_path):
    """The acceptance property: the report's planned mentions include the
    client contact, so the author must name them and MENT-01 checks it."""
    on = _build_with_culture(tmp_path, "  client_facing_reports: true\n")
    entries = {
        e["doc_id"]: e
        for line in on.manifest_jsonl.read_text().splitlines()
        for e in [json.loads(line)]
    }
    reports = [e for e in entries.values() if e["genre"] == "status_report"]
    assert reports
    named = 0
    for entry in reports:
        externals = [p for p in entry["participants"] if p.startswith("xp:")]
        if not externals:
            continue
        mentioned = {m["entity"] for m in entry["mentions"]}
        assert set(externals) <= mentioned, entry["path"]
        named += 1
    assert named, "no status report names an external contact"
