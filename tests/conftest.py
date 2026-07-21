import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# The M12 pilot/flagship org is large enough (218 files) that validating it
# alone is ~2.8s, which pushes the org tier past its ~5s budget. It gets its
# own `flagship` marker, excluded from the default org tier and run on its own
# (TESTING.md). Any future flagship-scale org joins this set.
FLAGSHIP_SLUGS = {"calderwood-partners"}


def flagship_params(slugs):
    """Wrap flagship slugs so their parametrized cases carry the `flagship`
    marker in addition to the module's `org` marker, so `-m "org and not
    flagship"` (the default org tier) skips them and `-m flagship` runs them."""
    return [
        pytest.param(s, marks=pytest.mark.flagship) if s in FLAGSHIP_SLUGS else s
        for s in slugs
    ]
sys.path.insert(0, str(REPO))

from orgsmith.charter import run_charter  # noqa: E402
from orgsmith.docplan import run_docplan  # noqa: E402
from orgsmith.fabric import run_fabric  # noqa: E402
from orgsmith.foundation import run_scaffold  # noqa: E402
from orgsmith.paths import OrgPaths


def build_pure_stages(root: Path, slug: str = "dev-mini") -> OrgPaths:
    """Copy the tracer recipe into `root` and run every pure stage up to
    docplan. No model pass, no network."""
    (root / "recipes").mkdir(parents=True, exist_ok=True)
    dest = root / "recipes" / slug
    if not dest.exists():
        shutil.copytree(REPO / "recipes" / slug, dest)
    paths = OrgPaths(root=root, slug=slug)
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    assert run_docplan(paths) == 0
    return paths


@pytest.fixture(scope="module")
def pure_org(tmp_path_factory) -> OrgPaths:
    """One dev-mini org built through docplan, shared read-only per module."""
    return build_pure_stages(tmp_path_factory.mktemp("pure-org"))


# Knobs appended after the `external_people` anchor. `min_mentions_per_person`
# is NOT here: the recipe already carries it, so appending would emit a
# duplicate YAML key that PyYAML resolves silently. It is raised in place
# by MENTIONS_FROM -> MENTIONS_TO instead.
KNOB_LINES = (
    "  surname_collisions: 1\n"
    "  nickname_aliases: 1\n"
    "  multi_affiliations: 1\n"
    "  affiliations_in_docs: true\n"
)

MENTIONS_FROM = "  min_mentions_per_person: 1\n"
MENTIONS_TO = "  min_mentions_per_person: 2\n"


def write_hardcase_recipe(
    root: Path, slug: str = "dev-mini", sig: int = 1, fn: int = 1
) -> OrgPaths:
    """dev-mini recipe with hard_cases knobs set; stages not run."""
    dest = root / "recipes" / slug
    dest.mkdir(parents=True, exist_ok=True)
    text = (REPO / "recipes" / slug / "ORG-CHARTER.md").read_text()
    anchor = "  external_people: 3\n"
    assert anchor in text
    block = (
        f"\nhard_cases:\n  signature_page_facts: {sig}\n  filename_dates: {fn}\n"
    )
    (dest / "ORG-CHARTER.md").write_text(text.replace(anchor, anchor + block))
    return OrgPaths(root=root, slug=slug)


def build_hardcase_stages(
    root: Path, slug: str = "dev-mini", sig: int = 1, fn: int = 1
) -> OrgPaths:
    """dev-mini recipe with hard_cases knobs on, through docplan."""
    paths = write_hardcase_recipe(root, slug, sig, fn)
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    assert run_docplan(paths) == 0
    return paths


def build_acl_stages(
    root: Path, slug: str = "dev-mini", posture: str = "departmental"
) -> OrgPaths:
    """dev-mini recipe with an acl_posture, through docplan plus the ACL
    overlay."""
    from orgsmith.acl import run_acl

    dest = root / "recipes" / slug
    dest.mkdir(parents=True, exist_ok=True)
    text = (REPO / "recipes" / slug / "ORG-CHARTER.md").read_text()
    anchor = "  external_people: 3\n"
    assert anchor in text
    (dest / "ORG-CHARTER.md").write_text(
        text.replace(anchor, anchor + f"\nacl_posture: {posture}\n")
    )
    paths = OrgPaths(root=root, slug=slug)
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    assert run_docplan(paths) == 0
    assert run_acl(paths) == 0
    return paths


def write_mix_recipe(root: Path, mix: dict, slug: str = "dev-mini") -> OrgPaths:
    """dev-mini recipe with a replaced format_mix (target_docs follows the
    mix sum); stages not run."""
    dest = root / "recipes" / slug
    dest.mkdir(parents=True, exist_ok=True)
    text = (REPO / "recipes" / slug / "ORG-CHARTER.md").read_text()
    old_mix = "  format_mix: {docx: 14, pdf: 3, xlsx: 5}\n"
    assert old_mix in text and "target_docs: 22" in text
    new_mix = (
        "  format_mix: {"
        + ", ".join(f"{k}: {v}" for k, v in mix.items())
        + "}\n"
    )
    text = text.replace(old_mix, new_mix)
    text = text.replace("target_docs: 22", f"target_docs: {sum(mix.values())}")
    (dest / "ORG-CHARTER.md").write_text(text)
    return OrgPaths(root=root, slug=slug)


def build_mix_stages(root: Path, mix: dict, slug: str = "dev-mini") -> OrgPaths:
    """dev-mini recipe with a replaced format_mix, through docplan."""
    paths = write_mix_recipe(root, mix, slug)
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    assert run_docplan(paths) == 0
    return paths


def write_culture_recipe(
    root: Path,
    culture_lines: str,
    slug: str = "dev-mini",
    extra_blocks: str = "",
) -> OrgPaths:
    """dev-mini recipe with lines appended inside doc_culture (indented two
    spaces, e.g. scan knobs) and optional top-level blocks appended after
    graph_targets; stages not run."""
    dest = root / "recipes" / slug
    dest.mkdir(parents=True, exist_ok=True)
    text = (REPO / "recipes" / slug / "ORG-CHARTER.md").read_text()
    mix_anchor = "  format_mix: {docx: 14, pdf: 3, xlsx: 5}\n"
    assert mix_anchor in text
    text = text.replace(mix_anchor, mix_anchor + culture_lines)
    if extra_blocks:
        anchor = "  external_people: 3\n"
        assert anchor in text
        text = text.replace(anchor, anchor + extra_blocks)
    (dest / "ORG-CHARTER.md").write_text(text)
    return OrgPaths(root=root, slug=slug)


def build_culture_stages(
    root: Path,
    culture_lines: str,
    slug: str = "dev-mini",
    extra_blocks: str = "",
) -> OrgPaths:
    """dev-mini recipe with doc_culture knobs on, through docplan."""
    paths = write_culture_recipe(root, culture_lines, slug, extra_blocks)
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    assert run_docplan(paths) == 0
    return paths


def build_knobbed_stages(root: Path, slug: str = "dev-mini") -> OrgPaths:
    """dev-mini recipe with every ambiguity knob on and every format in the
    mix, through docplan. The zero-skip validator test keys off this org:
    charter-gated rules must all find their knob on here (except legacy,
    which CI cannot render: no LibreOffice)."""
    dest = root / "recipes" / slug
    dest.mkdir(parents=True, exist_ok=True)
    text = (REPO / "recipes" / slug / "ORG-CHARTER.md").read_text()
    anchor = "  external_people: 3\n"
    assert anchor in text
    text = text.replace(anchor, anchor + KNOB_LINES)
    assert MENTIONS_FROM in text
    text = text.replace(MENTIONS_FROM, MENTIONS_TO)
    # Widen the date range by two years. M8's staffing rotation shifted
    # dev-mini's engagement dates, and its 2019-2023 window with 3
    # engagements can no longer place the multi-affiliation person on both
    # sides of the employer boundary (affiliations_in_docs). Two more years
    # give the placement room without touching engagements.count, so the
    # format_mix quota below is unchanged. This is a test copy, not the
    # committed recipe.
    old_range = "  date_range: [2019-01-01, 2023-12-31]\n"
    assert old_range in text
    text = text.replace(old_range, "  date_range: [2019-01-01, 2025-12-31]\n")
    old_mix = "  format_mix: {docx: 14, pdf: 3, xlsx: 5}\n"
    assert old_mix in text
    text = text.replace(
        old_mix,
        "  format_mix: {docx: 14, pdf: 3, xlsx: 5, pptx: 1, eml: 2}\n"
        "  scanned_ratio: 0.4\n"
        "  ocr_layer_rate: 1.0\n"
        # M12: turn the business-day calendar and the noise model on so CAL-01
        # and NOISE-01 find their knobs here too (the zero-skip test keys off
        # this org). Weekends only, no declared holidays; one duplicate and one
        # draft, which is enough to run both rules.
        "  business_calendar:\n    holidays: []\n"
        "  noise:\n    duplicates: 1\n    drafts: 1\n"
        # M14: mail on so EML-02 (signatures) finds its knob here too; the
        # zero-skip test keys off this org. eml: 2 gives single-message
        # threads, enough to run EML-01/EML-02 (the reply path is exercised
        # by test_unit_mail).
        "  mail:\n    business_hours: [9, 17]\n    max_thread_depth: 3\n",
    )
    text = text.replace("target_docs: 22", "target_docs: 16")
    (dest / "ORG-CHARTER.md").write_text(text)
    paths = OrgPaths(root=root, slug=slug)
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    assert run_docplan(paths) == 0
    return paths


# --- scripted airlock counterparts (tests only) ----------------------------
# Deterministic template text standing in for the model so the airlock
# contract and resume machinery can be exercised offline. Never used for
# committed orgs; realism comes from the real skills.


def scripted_enrichment(order) -> dict:
    return {
        "schema_id": "orgsmith/enrichment-deliverable@1",
        "work_order_id": order.id,
        "personas": [
            {
                "person_id": p.id,
                "persona": (
                    f"{p.name} is the firm's {p.title}. Writes brief, direct "
                    f"prose and keeps meetings short. Test-double persona."
                ),
            }
            for p in order.people
        ],
    }


def scripted_authoring(order) -> dict:
    docs = []
    for brief in order.docs:
        placeholders = " ".join("{{fact:%s}}" % f.id for f in brief.facts)
        surfaces = "; ".join(m.surface for m in brief.mentions)
        # Honor the hard-case guidance the way the real model must: a
        # filename-only dated doc carries no date in its text.
        dated = (
            ""
            if "filename only" in brief.guidance
            else f" dated {brief.date}"
        )
        blocks = [
            {"kind": "heading", "text": brief.title, "level": 1},
            {
                "kind": "paragraph",
                "text": (
                    f"Scripted body for {brief.genre}{dated}. "
                    f"{placeholders} Present: {surfaces}. End of scripted prose."
                ),
            },
        ]
        if brief.genre == "briefing_deck":
            blocks = [
                {"kind": "heading", "text": brief.title, "level": 1},
                {
                    "kind": "list",
                    "items": [
                        f"Scripted slide bullet{dated}. {placeholders}",
                        f"Present: {surfaces}.",
                    ],
                },
                {"kind": "heading", "text": "Next Steps", "level": 1},
                {"kind": "list", "items": ["Scripted follow-up item."]},
            ]
        if brief.genre == "meeting_minutes":
            blocks.append(
                {"kind": "list", "items": [p.name for p in brief.participants]}
            )
        if brief.genre == "engagement_letter":
            signers = [brief.authors[0].id]
            if brief.participants:
                ext = [p.id for p in brief.participants if p.id.startswith("xp:")]
                signers += ext[:1]
            blocks.append({"kind": "sigblock", "signers": signers})
        docs.append(
            {"schema_id": "orgsmith/docir@1", "doc_id": brief.doc_id, "blocks": blocks}
        )
    return {
        "schema_id": "orgsmith/authoring-deliverable@1",
        "work_order_id": order.id,
        "docs": docs,
    }


def run_enrichment(paths: OrgPaths) -> None:
    import json

    from orgsmith.artifacts import load_work_order
    from orgsmith.foundation.contexts import run_emit_context
    from orgsmith.foundation.ingest import run_ingest as ingest_enrichment
    from orgsmith.state import load_state

    assert run_emit_context(paths) == 0
    state = load_state(paths)
    wo = load_work_order(paths.workorders_dir / state.outstanding["foundation"])
    reply = paths.workorders_dir / "reply-foundation.json"
    reply.write_text(json.dumps(scripted_enrichment(wo)))
    assert ingest_enrichment(paths, reply) == 0


def sole_author_wo(paths: OrgPaths):
    """The single outstanding author work order, for tests that drive one
    batch. Asserts exactly one batch is outstanding."""
    from orgsmith.artifacts import load_work_order
    from orgsmith.state import load_state

    (_wo_id, ref), = load_state(paths).author_batches.items()
    return load_work_order(paths.workorders_dir / ref.workorder)


def ingest_author_batch(paths: OrgPaths, wo_id: str) -> None:
    """Author and ingest one outstanding batch by work_order_id (scripted)."""
    import json

    from orgsmith.artifacts import load_work_order
    from orgsmith.authoring.ingest import run_ingest as ingest_author
    from orgsmith.state import load_state

    ref = load_state(paths).author_batches[wo_id]
    wo = load_work_order(paths.workorders_dir / ref.workorder)
    reply = paths.workorders_dir / f"reply-{wo.id.replace(':', '-')}.json"
    reply.write_text(json.dumps(scripted_authoring(wo)))
    assert ingest_author(paths, reply) == 0


def run_authoring(paths: OrgPaths, max_batches: int = 20) -> int:
    """Drive next-batch/ingest with the scripted author until done, ingesting
    every outstanding batch each round (including any left over from a killed
    session). Returns the number of batches ingested."""
    from orgsmith.authoring.contexts import run_next_batch
    from orgsmith.state import load_state

    batches = 0
    for _ in range(max_batches):
        assert run_next_batch(paths) == 0
        outstanding = list(load_state(paths).author_batches)
        if not outstanding:
            return batches
        for wo_id in outstanding:
            ingest_author_batch(paths, wo_id)
            batches += 1
    raise AssertionError("authoring did not converge")
