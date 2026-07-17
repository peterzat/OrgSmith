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
from orgsmith.schemas import Block, DocIR
from orgsmith.validate.rules import Context, _needs_noise, noise_01

from conftest import REPO, run_authoring, run_enrichment

pytestmark = pytest.mark.unit


def _write_noise_recipe(root, duplicates=2, drafts=3, slug="dev-mini") -> OrgPaths:
    dest = root / "recipes" / slug
    dest.mkdir(parents=True, exist_ok=True)
    text = (REPO / "recipes" / slug / "ORG-CHARTER.md").read_text()
    anchor = "  format_mix: {docx: 14, pdf: 3, xlsx: 5}\n"
    assert anchor in text
    block = f"  noise:\n    duplicates: {duplicates}\n    drafts: {drafts}\n"
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
