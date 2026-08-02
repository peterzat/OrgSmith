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
    # And the manifest, which the docplan derives downstream, is untouched
    # until a genre actually cites a scope fact.
    assert (
        off.manifest_jsonl.read_bytes() == on.manifest_jsonl.read_bytes()
    )


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
