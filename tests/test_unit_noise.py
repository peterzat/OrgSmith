"""Unit tier: the deterministic noise model (M12). A recipe may declare
duplicates and drafts; docplan plants them as derived documents from authored
sources with no model pass, each labeled with its source, and re-derives them
byte-identically. Default off: a recipe without the block plans the same
manifest (covered by the org tier)."""

import json
import shutil

import pytest

from orgsmith.artifacts import load_manifest
from orgsmith.charter import run_charter
from orgsmith.docplan import run_docplan
from orgsmith.evals.emit import run_emit_evals
from orgsmith.fabric import run_fabric
from orgsmith.foundation.scaffold import run_scaffold
from orgsmith.paths import OrgPaths
from orgsmith.render import run_render
from orgsmith.render.noise import derive_draft_docir
from orgsmith.schemas import Block, DocCulture, DocIR, MailCulture, NoiseModel
from orgsmith.validate.rules import Context, _needs_noise, noise_01

from conftest import REPO, run_authoring, run_enrichment

pytestmark = pytest.mark.unit


def _write_noise_recipe(root, slug="dev-mini", **counts) -> OrgPaths:
    dest = root / "recipes" / slug
    dest.mkdir(parents=True, exist_ok=True)
    text = (REPO / "recipes" / slug / "ORG-CHARTER.md").read_text()
    anchor = "  format_mix: {docx: 14, pdf: 3, xlsx: 5}\n"
    assert anchor in text
    counts = counts or {"duplicates": 2, "drafts": 3}
    lines = "".join(
        f"    {k}: {str(v).lower() if isinstance(v, bool) else v}\n"
        for k, v in counts.items()
    )
    block = f"  noise:\n{lines}"
    dest.joinpath("ORG-CHARTER.md").write_text(text.replace(anchor, anchor + block))
    return OrgPaths(root=root, slug=slug)


def _pure(root, **kw) -> OrgPaths:
    p = _write_noise_recipe(root, **kw)
    for stage in (run_charter, run_scaffold, run_fabric, run_docplan):
        assert stage(p) == 0
    return p


@pytest.fixture(scope="module")
def rendered_noise_org(tmp_path_factory):
    """A dev-mini org with noise on, authored (scripted) and rendered once."""
    root = tmp_path_factory.mktemp("noise-org")
    p = _pure(root)
    run_enrichment(p)
    run_authoring(p)
    assert run_render(p) == 0
    return p


def test_docplan_plants_labeled_derived_docs(tmp_path):
    p = _pure(tmp_path, duplicates=2, drafts=3)
    derived = [e for e in load_manifest(p) if e.authoring == "derived"]
    assert len(derived) == 5
    kinds = sorted(e.noise_kind for e in derived)
    assert kinds == ["draft", "draft", "draft", "exact_duplicate", "exact_duplicate"]
    by_id = {e.doc_id: e for e in load_manifest(p)}
    for e in derived:
        assert e.noise_of in by_id
        assert by_id[e.noise_of].authoring == "batchable"  # a real source
        assert not e.facts_refs and not e.key_facts and not e.mentions


def test_manifest_re_derives_byte_identically(tmp_path):
    p = _pure(tmp_path / "a")
    dest = tmp_path / "b" / "recipes" / "dev-mini"
    dest.parent.mkdir(parents=True)
    shutil.copytree(p.root / "recipes" / "dev-mini", dest)
    q = OrgPaths(root=tmp_path / "b", slug="dev-mini")
    for stage in (run_charter, run_scaffold, run_fabric, run_docplan):
        assert stage(q) == 0
    assert p.manifest_jsonl.read_bytes() == q.manifest_jsonl.read_bytes()


def test_over_demand_fails_actionably(tmp_path):
    with pytest.raises(SystemExit, match="only .* eligible source"):
        _pure(tmp_path, duplicates=500, drafts=0)


def test_exact_duplicate_is_byte_identical_and_draft_is_a_near_copy(
    rendered_noise_org,
):
    p = rendered_noise_org
    manifest = load_manifest(p)
    by_id = {e.doc_id: e for e in manifest}
    for e in manifest:
        if e.authoring != "derived":
            continue
        target = p.share_dir / e.path
        assert target.exists()
        src = by_id[e.noise_of]
        src_bytes = (p.share_dir / src.path).read_bytes()
        if e.noise_kind == "exact_duplicate":
            assert target.read_bytes() == src_bytes  # collapses on a hash
        else:
            # a near-copy: different bytes, but not a fresh document
            assert target.read_bytes() != src_bytes


def test_noise_01_skips_off_passes_clean_and_fires_when_stripped(
    rendered_noise_org, tmp_path
):
    p = rendered_noise_org
    ctx = Context.load(p)
    assert _needs_noise(ctx) is None  # knob on: the rule runs
    assert list(noise_01(ctx)) == []  # clean org

    # strip the derived docs: the noise ground truth is now missing
    ctx.manifest = [e for e in ctx.manifest if e.authoring != "derived"]
    findings = list(noise_01(ctx))
    assert findings and "no derived documents" in findings[0][0]

    # a knob-off org skips visibly rather than running
    off = OrgPaths(root=tmp_path, slug="dev-mini")
    shutil.copytree(REPO / "recipes" / "dev-mini", tmp_path / "recipes" / "dev-mini")
    for stage in (run_charter, run_scaffold, run_fabric, run_docplan):
        assert stage(off) == 0
    assert _needs_noise(Context.load(off)) is not None


def test_derived_docs_are_never_eval_answers(rendered_noise_org):
    p = rendered_noise_org
    assert run_emit_evals(p) == 0
    derived_paths = {
        e.path for e in load_manifest(p) if e.authoring == "derived"
    }
    for suite in ("retrieval.jsonl", "extraction.jsonl"):
        text = (p.evals_dir / suite).read_text()
        for path in derived_paths:
            assert path not in text, f"{path} leaked into {suite}"


def test_eml_01_excludes_derived_noise_emails(tmp_path):
    """A noise .eml is a copy or draft whose headers mirror its source, not a
    fresh ledger recompute (an exact duplicate carries the source's To/Subject/
    Message-ID verbatim). EML-01 must exclude derived docs, exactly as
    SCAN-01/LEG-01 do, or a duplicated email fails header recomputation."""
    import shutil as _shutil

    from conftest import build_knobbed_stages, run_authoring, run_enrichment
    from orgsmith.render import run_render
    from orgsmith.validate.rules import Context, eml_01

    p = build_knobbed_stages(tmp_path)  # has format_mix.eml > 0
    run_enrichment(p)
    run_authoring(p)
    assert run_render(p) == 0
    ctx = Context.load(p)
    assert list(eml_01(ctx)) == []  # baseline clean

    src = next(e for e in ctx.manifest if e.format == "eml")
    copy_path = src.path.rsplit(".", 1)[0] + " (copy).eml"
    _shutil.copyfile(p.share_dir / src.path, p.share_dir / copy_path)
    derived = src.model_copy(
        update={
            "doc_id": "d:0199",
            "path": copy_path,
            "title": src.title + " (copy)",
            "authoring": "derived",
            "participants": [],
            "facts_refs": [],
            "mentions": [],
            "key_facts": [],
            "render_params": {
                "noise_of": src.doc_id,
                "noise_kind": "exact_duplicate",
            },
        }
    )
    ctx.manifest.append(derived)
    # excluded because authoring == derived: no header-recompute finding
    assert list(eml_01(ctx)) == []
    # prove the exclusion is what saves it: as a normal doc it would fail,
    # because the copied file carries the source's Message-ID, not d:0199's
    as_batchable = derived.model_copy(
        update={"authoring": "batchable", "render_params": {}}
    )
    ctx.manifest[-1] = as_batchable
    assert any("Message-ID" in m for m, _ in eml_01(ctx))


def test_derive_draft_introduces_no_new_facts():
    source = DocIR(
        doc_id="d:0001",
        blocks=[
            Block(kind="heading", text="Title", level=1),
            Block(kind="paragraph", text="Body with {{fact:f:E-1.fee}}."),
            Block(kind="paragraph", text="A closing paragraph, dropped in draft."),
        ],
    )
    draft = derive_draft_docir(source, "d:0099")
    texts = [b.text for b in draft.blocks]
    assert "DRAFT" in texts[0]  # banner prepended
    assert "A closing paragraph" not in " ".join(texts)  # last block dropped
    # every placeholder in the draft was already the source's (no new fact)
    src_ph = {"f:E-1.fee"}
    import re

    draft_ph = set(re.findall(r"\{\{fact:([^}]*)\}\}", " ".join(texts)))
    assert draft_ph <= src_ph


# --- M15 noise v2: schema layer -------------------------------------------


def _culture(**kw) -> DocCulture:
    from datetime import date

    return DocCulture(
        target_docs=20,
        date_range=(date(2020, 1, 1), date(2024, 12, 31)),
        format_mix={"docx": 10, "eml": 5},
        **kw,
    )


def test_noise_v2_fields_default_zero_and_off():
    """calderwood's committed {duplicates: 15, drafts: 20} shape gains the
    new fields at zero/off, so its declared noise plans unchanged."""
    m = NoiseModel(duplicates=15, drafts=20)
    assert m.version_chains == 0
    assert m.misfiled == 0
    assert m.stale_templates == 0
    assert m.empty_dirs == 0
    assert m.attachment_mismatch == 0
    assert m.filename_variety is False


def test_a_v2_kind_alone_declares_a_valid_model():
    assert NoiseModel(version_chains=1).version_chains == 1
    assert NoiseModel(empty_dirs=2).empty_dirs == 2


def test_all_zero_noise_model_still_rejected():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        NoiseModel()
    with pytest.raises(ValidationError):
        # the variety switch alone plans nothing
        NoiseModel(filename_variety=True)


def test_attachment_mismatch_requires_mail_with_attachments():
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="mail block"):
        _culture(noise=NoiseModel(version_chains=1, attachment_mismatch=1))
    with pytest.raises(ValidationError, match="mail block"):
        _culture(
            noise=NoiseModel(version_chains=1, attachment_mismatch=1),
            mail=MailCulture(),  # attachments defaults 0
        )


def test_attachment_mismatch_requires_version_chains():
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="version_chains"):
        _culture(
            noise=NoiseModel(duplicates=1, attachment_mismatch=1),
            mail=MailCulture(attachments=2),
        )
    ok = _culture(
        noise=NoiseModel(version_chains=1, attachment_mismatch=1),
        mail=MailCulture(attachments=2),
    )
    assert ok.noise.attachment_mismatch == 1


def test_style_specs_defaults_off_on_doc_culture():
    assert _culture().style_specs is False
    assert _culture(style_specs=True).style_specs is True


# --- M15 noise v2: version chains -----------------------------------------


@pytest.fixture(scope="module")
def rendered_chain_org(tmp_path_factory):
    """A dev-mini org with two version chains on, authored (scripted) and
    rendered once."""
    root = tmp_path_factory.mktemp("chain-org")
    p = _pure(root, version_chains=2)
    run_enrichment(p)
    run_authoring(p)
    assert run_render(p) == 0
    return p


def _chains(manifest):
    grouped = {}
    for e in manifest:
        if e.noise_kind == "version":
            grouped.setdefault(e.noise_of, []).append(e)
    return grouped


def test_version_chains_plan_coherent_labeled_members(tmp_path):
    from orgsmith.artifacts import load_charter

    p = _pure(tmp_path, version_chains=2)
    manifest = load_manifest(p)
    by_id = {e.doc_id: e for e in manifest}
    grouped = _chains(manifest)
    assert len(grouped) == 2
    start, end = load_charter(p).doc_culture.date_range
    for src_id, members in grouped.items():
        src = by_id[src_id]
        assert src.authoring == "batchable"
        assert src.format != "eml"  # a versioned email is not a thing
        length = int(members[0].render_params["noise_len"])
        assert length >= 3
        poss = sorted(int(m.render_params["noise_pos"]) for m in members)
        assert poss == list(range(1, length))
        for m in members:
            assert m.authoring == "derived"
            assert start <= m.date < src.date  # earlier, inside the range
            assert not m.facts_refs and not m.key_facts and not m.mentions


def test_chain_manifest_re_derives_byte_identically(tmp_path):
    p = _pure(tmp_path / "a", version_chains=2, duplicates=1, drafts=1)
    dest = tmp_path / "b" / "recipes" / "dev-mini"
    dest.parent.mkdir(parents=True)
    shutil.copytree(p.root / "recipes" / "dev-mini", dest)
    q = OrgPaths(root=tmp_path / "b", slug="dev-mini")
    for stage in (run_charter, run_scaffold, run_fabric, run_docplan):
        assert stage(q) == 0
    assert p.manifest_jsonl.read_bytes() == q.manifest_jsonl.read_bytes()


def test_chains_land_after_the_m12_kinds(tmp_path):
    """Chains append after duplicates/drafts, so turning them on cannot
    renumber or rename the M12 noise a committed recipe already plans."""
    base = _pure(tmp_path / "a", duplicates=2, drafts=3)
    plus = _pure(tmp_path / "b", duplicates=2, drafts=3, version_chains=1)
    old = [e for e in load_manifest(base) if e.authoring == "derived"]
    new = {e.doc_id: e for e in load_manifest(plus)}
    for e in old:
        assert new[e.doc_id].path == e.path
        assert new[e.doc_id].noise_kind == e.noise_kind


def test_chain_over_demand_fails_actionably(tmp_path):
    with pytest.raises(SystemExit, match="chainable source"):
        _pure(tmp_path, version_chains=500)


def test_rendered_chain_members_pairwise_diverge(rendered_chain_org):
    p = rendered_chain_org
    manifest = load_manifest(p)
    by_id = {e.doc_id: e for e in manifest}
    for src_id, members in _chains(manifest).items():
        blobs = {}
        for m in [*members, by_id[src_id]]:
            blobs[m.doc_id] = (p.share_dir / m.path).read_bytes()
        digests = {v for v in blobs.values()}
        assert len(digests) == len(blobs)  # no two byte-identical


def test_chain_org_validates_clean_and_splits_exclude_chains(
    rendered_chain_org,
):
    import json

    p = rendered_chain_org
    ctx = Context.load(p)
    assert list(noise_01(ctx)) == []
    assert run_emit_evals(p) == 0
    splits = json.loads((p.evals_dir / "splits.json").read_text())["splits"]
    chain_paths = {
        e.path for e in load_manifest(p) if e.noise_kind == "version"
    }
    assert chain_paths  # the fixture planned some
    assert not chain_paths & set(splits["core"])
    assert not chain_paths & set(splits["distractors"])
    assert chain_paths <= set(splits["noise"])
    assert chain_paths <= set(splits["full"])


def test_noise01_fires_on_a_hash_collapsed_chain(rendered_chain_org, tmp_path):
    """Overwriting a chain member with its final's bytes is tamper (the
    divergence is the chain's point); NOISE-01 must fail, not skip."""
    p = rendered_chain_org
    root = tmp_path / "tampered"
    shutil.copytree(p.root, root)
    q = OrgPaths(root=root, slug="dev-mini")
    manifest = load_manifest(q)
    by_id = {e.doc_id: e for e in manifest}
    member = next(e for e in manifest if e.noise_kind == "version")
    final = by_id[member.noise_of]
    shutil.copyfile(q.share_dir / final.path, q.share_dir / member.path)
    findings = list(noise_01(Context.load(q)))
    assert any("byte-identical" in msg for msg, _ in findings)


def test_noise01_fires_on_a_backdated_final(rendered_chain_org):
    """A member dated on or after its final breaks the chain's timeline."""
    p = rendered_chain_org
    ctx = Context.load(p)
    member = next(e for e in ctx.manifest if e.noise_kind == "version")
    by_id = {e.doc_id: e for e in ctx.manifest}
    tampered = member.model_copy(update={"date": by_id[member.noise_of].date})
    ctx.manifest = [
        tampered if e.doc_id == member.doc_id else e for e in ctx.manifest
    ]
    findings = list(noise_01(ctx))
    assert any("not earlier than its final" in msg for msg, _ in findings)


# --- M15 noise v2: misfiled copies ----------------------------------------


def test_misfiles_plan_into_a_foreign_folder(tmp_path):
    p = _pure(tmp_path, misfiled=2)
    manifest = load_manifest(p)
    by_id = {e.doc_id: e for e in manifest}
    misfiles = [e for e in manifest if e.noise_kind == "misfile"]
    assert len(misfiles) == 2
    for m in misfiles:
        src = by_id[m.noise_of]
        assert m.path.rsplit("/", 1)[0] != src.path.rsplit("/", 1)[0]
        assert m.path.rsplit("/", 1)[-1] == src.path.rsplit("/", 1)[-1]
        assert not m.facts_refs and not m.key_facts and not m.mentions


def test_misfile_renders_as_a_byte_copy(tmp_path):
    p = _pure(tmp_path, misfiled=1)
    run_enrichment(p)
    run_authoring(p)
    assert run_render(p) == 0
    manifest = load_manifest(p)
    by_id = {e.doc_id: e for e in manifest}
    m = next(e for e in manifest if e.noise_kind == "misfile")
    src = by_id[m.noise_of]
    assert (p.share_dir / m.path).read_bytes() == (
        p.share_dir / src.path
    ).read_bytes()
    assert list(noise_01(Context.load(p))) == []


def test_noise01_fires_on_a_misfile_filed_at_home(tmp_path):
    p = _pure(tmp_path, misfiled=1)
    ctx = Context.load(p)
    m = next(e for e in ctx.manifest if e.noise_kind == "misfile")
    by_id = {e.doc_id: e for e in ctx.manifest}
    src = by_id[m.noise_of]
    home = src.path.rsplit("/", 1)[0] + "/" + m.path.rsplit("/", 1)[-1]
    moved = m.model_copy(update={"path": home})
    ctx.manifest = [
        moved if e.doc_id == m.doc_id else e for e in ctx.manifest
    ]
    findings = list(noise_01(ctx))
    assert any("source's own folder" in msg for msg, _ in findings)


def test_acl_and_visibility_follow_the_misfiled_location(tmp_path):
    """A misfile readable by the wrong team is ground truth: grants derive
    from the manifest path, so the misfile carries its destination folder's
    grant set, not its source's."""
    from orgsmith.acl import run_acl
    from orgsmith.artifacts import load_acl
    from orgsmith.validate.rules import acl_01, acl_02, acl_03

    dest = tmp_path / "recipes" / "dev-mini"
    dest.mkdir(parents=True)
    text = (REPO / "recipes" / "dev-mini" / "ORG-CHARTER.md").read_text()
    anchor = "  external_people: 3\n"
    assert anchor in text
    text = text.replace(anchor, anchor + "\nacl_posture: departmental\n")
    mix = "  format_mix: {docx: 14, pdf: 3, xlsx: 5}\n"
    assert mix in text
    text = text.replace(mix, mix + "  noise:\n    misfiled: 2\n")
    (dest / "ORG-CHARTER.md").write_text(text)
    p = OrgPaths(root=tmp_path, slug="dev-mini")
    for stage in (run_charter, run_scaffold, run_fabric, run_docplan):
        assert stage(p) == 0
    assert run_acl(p) == 0

    manifest = load_manifest(p)
    by_id = {e.doc_id: e for e in manifest}
    acl = load_acl(p)
    holders = {}
    for g in acl.grants:
        for doc in g.docs:
            holders.setdefault(doc, set()).add(g.person)
    checked = 0
    for m in (e for e in manifest if e.noise_kind == "misfile"):
        folder = m.path.rsplit("/", 1)[0]
        siblings = [
            e
            for e in manifest
            if e.doc_id != m.doc_id
            and e.authoring != "derived"
            and e.path.rsplit("/", 1)[0] == folder
        ]
        assert siblings  # destination folders come from the authored plan
        expected: set = set()
        for s in siblings:
            expected |= holders.get(s.path, set())
        # the misfile reads as its destination folder does (the union of the
        # folder's authored readers), not as its source's content would
        assert holders.get(m.path, set()) == expected
        checked += 1
    assert checked

    # the recompute rules pass: the misfiled location is never a failure
    run_enrichment(p)
    run_authoring(p)
    assert run_render(p) == 0
    ctx = Context.load(p)
    for rule in (acl_01, acl_02, acl_03):
        assert list(rule(ctx)) == []
