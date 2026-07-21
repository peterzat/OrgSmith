"""Unit tier: the M14 email-culture knob (`doc_culture.mail`, MailCulture).

Presence turns on thread mechanics for engagement mail; absence leaves every
committed artifact byte-identical (the byte pin is the load-bearing proof of
that, in the org/flagship tiers). This file grows with the mechanics; it opens
with the schema-level inertness and validation checks.
"""

import shutil
from email import policy
from email.parser import BytesParser

import pytest
from pydantic import ValidationError

from orgsmith.artifacts import load_charter, load_foundation, load_manifest
from orgsmith.docplan import run_docplan
from orgsmith.fabric import run_fabric
from orgsmith.foundation.scaffold import run_scaffold
from orgsmith.charter import run_charter
from orgsmith.paths import OrgPaths
from orgsmith.render import people_index, run_render
from orgsmith.render.eml import expected_headers, thread_members
from orgsmith.schemas import DocCulture, MailCulture
from orgsmith.validate import run_validate

from conftest import REPO, run_authoring, run_enrichment

pytestmark = pytest.mark.unit


def _build_mail_org(root, eml=8, max_depth=5, extra_culture="", stages=True):
    """A dev-mini copy with engagement mail and a MailCulture block."""
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True, exist_ok=True)
    text = (REPO / "recipes" / "dev-mini" / "ORG-CHARTER.md").read_text()
    old_mix = "  format_mix: {docx: 14, pdf: 3, xlsx: 5}\n"
    assert old_mix in text
    text = text.replace(
        old_mix,
        f"  format_mix: {{docx: 14, pdf: 3, xlsx: 5, eml: {eml}}}\n"
        "  mail:\n"
        "    business_hours: [9, 17]\n"
        f"    max_thread_depth: {max_depth}\n"
        f"{extra_culture}",
    )
    text = text.replace("target_docs: 22", f"target_docs: {22 + eml}")
    (dest / "ORG-CHARTER.md").write_text(text)
    paths = OrgPaths(root=root, slug="dev-mini")
    if stages:
        assert run_charter(paths) == 0
        assert run_scaffold(paths) == 0
        assert run_fabric(paths) == 0
        assert run_docplan(paths) == 0
    return paths


def _mails(paths):
    return [e for e in load_manifest(paths) if e.format == "eml"]


def _parse(path):
    with open(path, "rb") as fh:
        return BytesParser(policy=policy.default).parse(fh)


def test_mail_defaults_off_on_doc_culture():
    """A DocCulture built without a mail block carries None: the whole knob is
    absent, so the planner takes the pre-M14 single-message path."""
    culture = DocCulture(
        target_docs=20,
        date_range=(__import__("datetime").date(2020, 1, 1),
                    __import__("datetime").date(2024, 12, 31)),
        format_mix={"docx": 10, "eml": 5},
    )
    assert culture.mail is None


def test_mail_culture_sensible_defaults():
    mc = MailCulture()
    assert mc.business_hours == (9, 17)
    assert mc.max_thread_depth == 6
    assert mc.mundane_emails == 0
    assert mc.attachments == 0


@pytest.mark.parametrize("hours", [(17, 9), (9, 9), (-1, 8), (8, 25)])
def test_business_hours_must_be_a_valid_window(hours):
    with pytest.raises(ValidationError):
        MailCulture(business_hours=hours)


def test_max_thread_depth_must_be_positive():
    with pytest.raises(ValidationError):
        MailCulture(max_thread_depth=0)


def test_mail_culture_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        MailCulture(cc=True)  # extra="forbid" on every contract


# --- threaded planning (docplan) ------------------------------------------


@pytest.fixture(scope="module")
def mail_manifest(tmp_path_factory):
    return _build_mail_org(tmp_path_factory.mktemp("mail-plan"), eml=8, max_depth=5)


def test_threads_vary_in_depth(mail_manifest):
    mails = _mails(mail_manifest)
    assert len(mails) == 8
    by_eng = {}
    for m in mails:
        assert "thread_pos" in m.render_params
        assert "send_minute" in m.render_params
        by_eng.setdefault(m.engagement, []).append(m)
    depths = sorted(len(v) for v in by_eng.values())
    assert len(set(depths)) > 1, f"threads not varied: {depths}"
    assert max(depths) >= 4, f"no deep thread: {depths}"


def test_thread_positions_and_minutes_strictly_increase(mail_manifest):
    by_eng = {}
    for m in _mails(mail_manifest):
        by_eng.setdefault(m.engagement, []).append(m)
    for eng, msgs in by_eng.items():
        msgs.sort(key=lambda e: int(e.render_params["thread_pos"]))
        assert [int(m.render_params["thread_pos"]) for m in msgs] == list(
            range(len(msgs))
        )
        keys = [(m.date, int(m.render_params["send_minute"])) for m in msgs]
        assert keys == sorted(keys)
        assert len(set(keys)) == len(keys), f"non-strict datetimes in {eng}"


def test_same_day_replies_occur_without_colliding(mail_manifest):
    by_eng = {}
    for m in _mails(mail_manifest):
        by_eng.setdefault(m.engagement, []).append(m)
    same_day = any(
        len({m.date for m in msgs}) < len(msgs) for msgs in by_eng.values()
    )
    assert same_day, "no same-day reply in any thread"
    paths = [m.path for m in _mails(mail_manifest)]
    assert len(paths) == len(set(paths)), "same-day replies collided on path"


def test_send_minutes_land_in_business_hours(mail_manifest):
    for m in _mails(mail_manifest):
        minute = int(m.render_params["send_minute"])
        assert 9 * 60 <= minute < 17 * 60


# --- rendered headers (the twin) ------------------------------------------


@pytest.fixture(scope="module")
def mail_rendered(tmp_path_factory):
    paths = _build_mail_org(tmp_path_factory.mktemp("mail-render"), eml=8, max_depth=5)
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    return paths


def test_openers_have_no_threading_headers_replies_do(mail_rendered):
    charter = load_charter(mail_rendered)
    people = people_index(load_foundation(mail_rendered))
    manifest = load_manifest(mail_rendered)
    saw_reply = False
    for entry in _mails(mail_rendered):
        msg = _parse(mail_rendered.share_dir / entry.path)
        pos = int(entry.render_params["thread_pos"])
        if pos == 0:
            assert msg["In-Reply-To"] is None
            assert msg["References"] is None
            assert not str(msg["Subject"]).startswith("RE: ")
        else:
            saw_reply = True
            thread = thread_members(entry, manifest)
            pred = thread[pos - 1]
            assert str(msg["In-Reply-To"]) == (
                f"<{pred.doc_id.replace(':', '')}.{charter.slug}@{charter.domain}>"
            )
            refs = str(msg["References"]).split()
            assert len(refs) == pos
            assert str(msg["Subject"]).startswith("RE: ")
    assert saw_reply


def test_rendered_headers_recompute_via_the_twin(mail_rendered):
    import re

    def norm(v):  # the whitespace normalization EML-01 applies (folded headers)
        return re.sub(r"\s+", " ", str(v or "")).strip()

    charter = load_charter(mail_rendered)
    people = people_index(load_foundation(mail_rendered))
    manifest = load_manifest(mail_rendered)
    for entry in _mails(mail_rendered):
        msg = _parse(mail_rendered.share_dir / entry.path)
        thread = thread_members(entry, manifest)
        for name, want in expected_headers(
            entry, people, charter.slug, charter.domain, thread
        ).items():
            assert norm(msg[name]) == norm(want), f"{entry.path}: {name}"


def test_cc_appears_disjoint_from_to(mail_rendered):
    seen_cc = False
    for entry in _mails(mail_rendered):
        msg = _parse(mail_rendered.share_dir / entry.path)
        if msg["Cc"] is None:
            continue
        seen_cc = True
        to = {a.strip() for a in str(msg["To"]).split(",")}
        cc = {a.strip() for a in str(msg["Cc"]).split(",")}
        assert to and cc and not (to & cc)
    assert seen_cc, "no thread produced a Cc"


def test_date_header_carries_a_real_time_of_day(mail_rendered):
    off_nine = False
    for entry in _mails(mail_rendered):
        msg = _parse(mail_rendered.share_dir / entry.path)
        if " 09:00:00 " not in str(msg["Date"]):
            off_nine = True
    assert off_nine, "every mail landed at 09:00; minute granularity unused"


def test_mail_validates_clean(mail_rendered):
    assert run_validate(mail_rendered) == 0


def test_mail_renders_byte_identically(mail_rendered):
    from orgsmith.authoring.ingest import docir_path
    from orgsmith.render.eml import render_eml
    from orgsmith.render.resolve import resolve_docir
    from orgsmith.schemas import DocIR
    from orgsmith.artifacts import load_engagements

    from orgsmith.render import _full_mail_body

    charter = load_charter(mail_rendered)
    foundation = load_foundation(mail_rendered)
    people = people_index(foundation)
    facts = load_engagements(mail_rendered).fact_index()
    manifest = load_manifest(mail_rendered)
    reply = next(m for m in _mails(mail_rendered) if int(m.render_params["thread_pos"]) > 0)
    docir = DocIR.model_validate_json(
        docir_path(mail_rendered, reply.doc_id).read_text("utf-8")
    )
    resolved = resolve_docir(docir, facts)
    thread = thread_members(reply, manifest)
    body = _full_mail_body(reply, mail_rendered, manifest, facts, foundation, people)
    a = render_eml(resolved, reply, people, charter.slug, charter.domain, thread, body)
    b = render_eml(resolved, reply, people, charter.slug, charter.domain, thread, body)
    assert a == b == (mail_rendered.share_dir / reply.path).read_bytes()


@pytest.fixture()
def mail_copy(mail_rendered, tmp_path):
    shutil.copytree(mail_rendered.root / "recipes", tmp_path / "recipes")
    shutil.copytree(mail_rendered.root / "companies", tmp_path / "companies")
    return OrgPaths(root=tmp_path, slug="dev-mini")


def test_tampered_inreplyto_fails_eml01(mail_copy, capsys):
    manifest = load_manifest(mail_copy)
    reply = next(m for m in _mails(mail_copy) if int(m.render_params["thread_pos"]) > 0)
    target = mail_copy.share_dir / reply.path
    text = target.read_bytes().decode("utf-8")
    assert "In-Reply-To: " in text
    tampered = text.replace("In-Reply-To: <", "In-Reply-To: <tampered.", 1)
    target.write_bytes(tampered.encode("utf-8"))
    assert run_validate(mail_copy, only=["EML-01"]) == 1
    assert "does not recompute" in capsys.readouterr().out


def test_spurious_inreplyto_on_opener_fails_eml01(mail_copy, capsys):
    opener = next(m for m in _mails(mail_copy) if int(m.render_params["thread_pos"]) == 0)
    target = mail_copy.share_dir / opener.path
    text = target.read_bytes().decode("utf-8")
    tampered = text.replace("Subject: ", "In-Reply-To: <forged@x>\nSubject: ", 1)
    target.write_bytes(tampered.encode("utf-8"))
    assert run_validate(mail_copy, only=["EML-01"]) == 1
    assert "no thread predecessor" in capsys.readouterr().out


# --- quoted history and signatures (M14 body render) ----------------------


def test_replies_carry_quoted_history(mail_rendered):
    manifest = load_manifest(mail_rendered)
    for entry in _mails(mail_rendered):
        if int(entry.render_params["thread_pos"]) == 0:
            continue
        body = _parse(mail_rendered.share_dir / entry.path).get_body(
            preferencelist=("plain",)
        ).get_content()
        thread = thread_members(entry, manifest)
        pred = thread[int(entry.render_params["thread_pos"]) - 1]
        assert f"On {pred.date:%Y-%m-%d}," in body
        assert "wrote:" in body
        assert "\n> " in body  # quote-prefixed predecessor body


def test_mail_body_carries_recomputed_signature(mail_rendered):
    from orgsmith.render.eml import mail_signature

    foundation = load_foundation(mail_rendered)
    for entry in _mails(mail_rendered):
        body = _parse(mail_rendered.share_dir / entry.path).get_body(
            preferencelist=("plain",)
        ).get_content()
        person = foundation.person(entry.authors[0])
        assert mail_signature(person, entry.date) in body


def test_signature_is_promotion_aware():
    from datetime import date

    from orgsmith.render.eml import mail_signature
    from orgsmith.schemas import EmploymentSpan, Person, TitleSpan

    person = Person(
        id="p:jane.doe",
        name="Jane Doe",
        title="Principal",
        dept="Advisory",
        employment=EmploymentSpan(start=date(2018, 1, 1)),
        email="jane@x.com",
        phone="+1 555 0100",
        title_history=[
            TitleSpan(title="Manager", start=date(2018, 1, 1), end=date(2020, 6, 30)),
            TitleSpan(title="Principal", start=date(2020, 7, 1)),
        ],
    )
    early = mail_signature(person, date(2019, 1, 1))
    late = mail_signature(person, date(2021, 1, 1))
    assert "Manager" in early and "Principal" not in early
    assert "Principal" in late and "Manager" not in late
    assert "+1 555 0100" in early and "Jane Doe" in early


def test_tampered_signature_fails_eml02(mail_copy, capsys):
    entry = _mails(mail_copy)[0]
    target = mail_copy.share_dir / entry.path
    text = target.read_bytes().decode("utf-8")
    foundation = load_foundation(mail_copy)
    title = foundation.person(entry.authors[0]).title_at(entry.date)
    assert title in text
    target.write_bytes(text.replace(title, "Grand Poobah", 1).encode("utf-8"))
    assert run_validate(mail_copy, only=["EML-02"]) == 1
    assert "does not recompute" in capsys.readouterr().out


def test_eml02_skips_visibly_when_mail_off(capsys):
    committed = OrgPaths(root=REPO, slug="dev-mini")
    assert run_validate(committed, only=["EML-02"]) == 0
    out = capsys.readouterr().out
    assert "SKIP EML-02" in out and "doc_culture.mail is not declared" in out


# --- mundane internal mail (M14 mailbox ecology) --------------------------


@pytest.fixture(scope="module")
def ecology_org(tmp_path_factory):
    from orgsmith.acl import run_acl

    paths = _build_mail_org(
        tmp_path_factory.mktemp("mail-ecology"),
        eml=8,
        max_depth=5,
        extra_culture=(
            "    mundane_emails: 6\n    attachments: 1\n"
            "    distribution_lists: 2\n"
        ),
    )
    run_enrichment(paths)
    run_authoring(paths)
    assert run_render(paths) == 0
    assert run_acl(paths) == 0  # writes the DL ledger DL-01 checks
    return paths


def _mundane(paths):
    return [e for e in load_manifest(paths) if e.genre == "internal_email"]


def test_mundane_mail_planned_off_engagement(ecology_org):
    mundane = _mundane(ecology_org)
    assert len(mundane) == 6
    for m in mundane:
        assert m.format == "eml"
        assert m.engagement is None
        assert m.facts_refs == []
        assert "send_minute" in m.render_params
        assert "thread_pos" not in m.render_params  # standalone, not a thread
        assert m.path.startswith("Firm/Mail/")


def test_mundane_mail_carries_colleague_mentions(ecology_org):
    for m in _mundane(ecology_org):
        assert m.mentions, f"{m.path} names no one"
        body = _parse(ecology_org.share_dir / m.path).get_body(
            preferencelist=("plain",)
        ).get_content()
        for mention in m.mentions:
            assert mention.surface in body


def test_mundane_mail_has_no_thread_headers(ecology_org):
    for m in _mundane(ecology_org):
        msg = _parse(ecology_org.share_dir / m.path)
        assert msg["In-Reply-To"] is None
        assert msg["References"] is None
        assert not str(msg["Subject"]).startswith("RE: ")


def test_ecology_validates_clean(ecology_org):
    assert run_validate(ecology_org) == 0


def test_mundane_mail_is_a_retrieval_distractor(ecology_org):
    import json

    from orgsmith.acl import run_acl
    from orgsmith.assemble import run_assemble
    from orgsmith.evals.emit import run_emit_evals

    assert run_assemble(ecology_org) == 0
    assert run_acl(ecology_org) == 0
    assert run_emit_evals(ecology_org) == 0
    mundane_paths = {m.path for m in _mundane(ecology_org)}

    def answers(name):
        return {
            p
            for line in (ecology_org.evals_dir / name).read_text().splitlines()
            for p in json.loads(line)["expected_docs"]
        }

    # Mundane mail is a retrieval/extraction DISTRACTOR: never an answer to
    # those suites. (Visibility still counts it -- a readable doc is a
    # visibility answer, exactly -- so it does appear in `core` via that suite,
    # which is correct, not a leak.)
    assert not (mundane_paths & answers("retrieval.jsonl"))
    assert not (mundane_paths & answers("extraction.jsonl"))

    splits = json.loads(
        (ecology_org.evals_dir / "splits.json").read_text()
    )["splits"]
    assert mundane_paths <= set(splits["distractors"])
    assert mundane_paths <= set(splits["full"])


# --- transmittal attachments (M14 mailbox ecology) ------------------------


def _transmittals(paths):
    return [
        e for e in load_manifest(paths)
        if e.render_params.get("attach_path")
    ]


def test_transmittal_carries_byte_identical_attachment(ecology_org):
    from orgsmith.render.eml import eml_attachment_bytes

    trans = _transmittals(ecology_org)
    assert trans, "no transmittal planned"
    for t in trans:
        src = ecology_org.share_dir / str(t.render_params["attach_path"])
        assert src.exists()
        got = eml_attachment_bytes(ecology_org.share_dir / t.path)
        assert got == src.read_bytes()
        # the opener of its thread, so no quoted history precedes it
        assert int(t.render_params["thread_pos"]) == 0


def test_transmittal_attributed_in_extraction_evals(ecology_org):
    import json

    from orgsmith.acl import run_acl
    from orgsmith.assemble import run_assemble
    from orgsmith.evals.emit import run_emit_evals

    assert run_assemble(ecology_org) == 0
    assert run_acl(ecology_org) == 0
    assert run_emit_evals(ecology_org) == 0
    trans = _transmittals(ecology_org)[0]
    attached = str(trans.render_params["attach_path"])
    extraction = [
        json.loads(line)
        for line in (ecology_org.evals_dir / "extraction.jsonl")
        .read_text()
        .splitlines()
    ]
    # every extraction question that names the attached doc also credits the
    # transmittal email that carries it byte-identically.
    for q in extraction:
        if attached in q["expected_docs"]:
            assert trans.path in q["expected_docs"], q["fact_id"]
    assert any(
        trans.path in q["expected_docs"] for q in extraction
    ), "transmittal never attributed a fact"


def test_eml03_detects_a_mismatched_attachment(ecology_org, tmp_path, capsys):
    dst = tmp_path / "companies"
    shutil.copytree(ecology_org.root / "companies", dst)
    shutil.copytree(ecology_org.root / "recipes", tmp_path / "recipes")
    copy = OrgPaths(root=tmp_path, slug="dev-mini")
    trans = _transmittals(copy)[0]
    src = copy.share_dir / str(trans.render_params["attach_path"])
    src.write_bytes(src.read_bytes() + b"tampered")
    assert run_validate(copy, only=["EML-03"]) == 1
    assert "byte-identical" in capsys.readouterr().out


def test_eml03_skips_visibly_when_mail_off(capsys):
    committed = OrgPaths(root=REPO, slug="dev-mini")
    assert run_validate(committed, only=["EML-03"]) == 0
    out = capsys.readouterr().out
    assert "SKIP EML-03" in out


# --- distribution lists (M14, derived ledger) -----------------------------


def test_dl_ledger_derived_beside_acl(ecology_org):
    from orgsmith.artifacts import load_distribution_lists

    dls = load_distribution_lists(ecology_org)
    assert dls is not None and len(dls.lists) == 2
    # All Staff first, then a department team; addresses at the org domain.
    assert dls.lists[0].name == "All Staff"
    for dl in dls.lists:
        assert dl.address.endswith("@pinebrookadvisory.com")
        assert dl.members, f"{dl.address} has no members"
    # committed foundation.json never gains a distribution_lists field
    import json

    foundation = json.loads(ecology_org.foundation_json.read_text())
    assert "distribution_lists" not in foundation


def test_some_mundane_mail_is_dl_addressed(ecology_org):
    dl_addressed = [m for m in _mundane(ecology_org) if m.render_params.get("dl")]
    assert dl_addressed, "no mundane mail addressed to a distribution list"
    from orgsmith.artifacts import load_distribution_lists

    addrs = {dl.address for dl in load_distribution_lists(ecology_org).lists}
    for m in dl_addressed:
        msg = _parse(ecology_org.share_dir / m.path)
        assert str(msg["To"]) == m.render_params["dl"]
        assert m.render_params["dl"] in addrs
        assert msg["Cc"] is None


def test_dl_members_can_read_the_message(ecology_org):
    from orgsmith.artifacts import load_acl, load_distribution_lists

    acl = load_acl(ecology_org)
    reader_of = {}
    for grant in acl.grants:
        for doc in grant.docs:
            reader_of.setdefault(doc, set()).add(grant.person)
    by_addr = {dl.address: dl for dl in load_distribution_lists(ecology_org).lists}
    for m in _mundane(ecology_org):
        addr = m.render_params.get("dl")
        if not addr:
            continue
        members = set(by_addr[addr].members)
        assert members <= reader_of.get(m.path, set())


def test_dl01_detects_a_tampered_ledger(ecology_org, tmp_path, capsys):
    shutil.copytree(ecology_org.root / "companies", tmp_path / "companies")
    shutil.copytree(ecology_org.root / "recipes", tmp_path / "recipes")
    copy = OrgPaths(root=tmp_path, slug="dev-mini")
    import json

    led = json.loads(copy.distribution_lists_json.read_text())
    led["lists"][0]["members"] = led["lists"][0]["members"][:-1]  # drop a member
    copy.distribution_lists_json.write_text(json.dumps(led, indent=2) + "\n")
    assert run_validate(copy, only=["DL-01"]) == 1
    assert "does not recompute" in capsys.readouterr().out


def test_dl01_skips_visibly_when_no_lists(capsys):
    committed = OrgPaths(root=REPO, slug="dev-mini")
    assert run_validate(committed, only=["DL-01"]) == 0
    out = capsys.readouterr().out
    assert "SKIP DL-01" in out and "no distribution lists" in out
