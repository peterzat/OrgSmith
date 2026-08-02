"""Unit tier: the mail recipient-mention exemption (M17).

The fleet-wide realism artifact the M13-M16 wave introduced: the ingest
mention check required an email author to spell the recipient's full legal
name in the body, because a first-name greeting alone did not satisfy it.
So the mail demonstrators address colleagues in the third person, in notes
sent directly to them.

`mail.exempt_recipient_mentions` stops the planner forcing it. MENT-01
still finds the recipient, because since v2.1.1 an .eml's extractable text
folds in the To/Cc display names, which is where a recipient's name
legitimately lives.
"""

import pytest

from orgsmith.artifacts import load_manifest
from orgsmith.paths import OrgPaths
from orgsmith.render.eml import eml_recipients
from orgsmith.schemas import MailCulture

from conftest import REPO, build_culture_stages

pytestmark = pytest.mark.unit

_MAIL = (
    "  mail:\n"
    "    business_hours: [9, 17]\n"
    "    max_thread_depth: 3\n"
    "    mundane_emails: 2\n"
)


def _mail_docs(paths):
    return [e for e in load_manifest(paths) if e.format == "eml"]


def test_the_knob_is_adopted_only_where_a_recipe_asks_for_it():
    """The knob defaults off, so an org that predates it is untouched. The
    exemplar adopted it at its M17 regeneration, and at least one mail org
    has not, which is what keeps the default-off half honest."""
    from orgsmith.artifacts import load_charter

    adopted, untouched = [], []
    for slug in sorted(
        p.name
        for p in (REPO / "companies").iterdir()
        if p.is_dir() and not p.name.endswith("-metadata")
    ):
        mail = load_charter(OrgPaths(root=REPO, slug=slug)).doc_culture.mail
        if mail is None:
            continue
        (adopted if mail.exempt_recipient_mentions else untouched).append(slug)
    assert MailCulture().exempt_recipient_mentions is False
    assert untouched, "no committed mail org still carries the pre-M17 default"


def test_off_the_planner_still_forces_recipient_mentions(tmp_path):
    paths = build_culture_stages(tmp_path, "  format_mix: {docx: 12, pdf: 3, xlsx: 5, eml: 4}\n" + _MAIL)
    docs = _mail_docs(paths)
    assert docs, "fixture planned no mail"
    forced = [
        e
        for e in docs
        if any(
            m.entity in set(e.participants) - set(e.authors)
            for m in e.mentions
        )
    ]
    assert forced, "no mail document forces a recipient mention with the knob off"


def test_on_no_mail_document_forces_a_recipient_mention(tmp_path):
    paths = build_culture_stages(
        tmp_path,
        "  format_mix: {docx: 12, pdf: 3, xlsx: 5, eml: 4}\n"
        + _MAIL
        + "    exempt_recipient_mentions: true\n",
    )
    docs = _mail_docs(paths)
    assert docs, "fixture planned no mail"
    for entry in docs:
        recipients = set(entry.participants) - set(entry.authors)
        planned = {m.entity for m in entry.mentions}
        assert not (planned & recipients), entry.path


def test_coverage_is_relocated_rather_than_lost(tmp_path):
    """The exemption removes mentions, so the question is whether the
    people-graph loses coverage. It does not: `min_mentions_per_person` is
    still satisfied for everyone, because the top-up moves the shortfall
    into genres that name people for a reason (memos, minutes, status
    reports) instead of into a note addressed to them.

    So the knob does touch non-mail documents, indirectly. That is the
    point of it: the mention lands where a full name belongs."""
    from orgsmith.artifacts import load_charter

    lines = "  format_mix: {docx: 12, pdf: 3, xlsx: 5, eml: 4}\n" + _MAIL
    off = build_culture_stages(tmp_path / "off", lines)
    on = build_culture_stages(
        tmp_path / "on", lines + "    exempt_recipient_mentions: true\n"
    )
    minimum = load_charter(on).graph_targets.min_mentions_per_person
    assert minimum, "fixture sets no coverage floor, so this proves nothing"

    def coverage(paths):
        counts: dict = {}
        for entry in load_manifest(paths):
            for mention in entry.mentions:
                counts[mention.entity] = counts.get(mention.entity, 0) + 1
        return counts

    from orgsmith.artifacts import load_foundation

    on_counts = coverage(on)
    for person in load_foundation(on).people:
        assert on_counts.get(person.id, 0) >= minimum, person.id

    # And the total really did fall: mail stopped carrying names it should
    # never have carried.
    assert sum(coverage(on).values()) < sum(coverage(off).values())


def test_the_recipient_partition_matches_the_renderers(tmp_path):
    """The planner exempts exactly who the renderer addresses. If these two
    ever disagreed, the exemption would drop a mention MENT-01 still
    demands, or keep one it does not."""
    paths = build_culture_stages(
        tmp_path,
        "  format_mix: {docx: 12, pdf: 3, xlsx: 5, eml: 4}\n"
        + _MAIL
        + "    exempt_recipient_mentions: true\n",
    )
    for entry in _mail_docs(paths):
        if entry.render_params.get("dl"):
            continue  # a DL address names the list, not its members
        planner_view = set(entry.participants) - set(entry.authors)
        renderer_view = set(
            eml_recipients(entry.authors, entry.participants)
        ) - set(entry.authors)
        assert planner_view == renderer_view, entry.path
