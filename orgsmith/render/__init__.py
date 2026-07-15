"""render stage: DocIR + ledgers -> real files in the share.

Incremental and resumable: each doc records the content basis it was
rendered from (authored hash, or the finance ledger hash for static docs);
unchanged docs are skipped, unauthored docs are left pending so the org is
browsable after every batch.
"""

from __future__ import annotations

from ..artifacts import (
    load_charter,
    load_engagements,
    load_finance,
    load_foundation,
    load_manifest,
)
from ..paths import OrgPaths
from ..schemas import DocIR
from ..state import load_state, require_stages, save_state, sha256_file
from .resolve import resolve_docir
from .styles import style_pack


def people_index(foundation) -> dict[str, dict]:
    """name/title/email per person id; shared with the EML-01 validator so
    header recomputation reads the ledger exactly the way render did."""
    people = {
        p.id: {"name": p.name, "title": p.title, "email": p.email}
        for p in foundation.people
    }
    for xp in foundation.external_people:
        org = next(o for o in foundation.external_orgs if o.id == xp.org)
        people[xp.id] = {
            "name": xp.name,
            "title": f"{xp.title}, {org.name}",
            "email": xp.email,
        }
    return people


def run_render(paths: OrgPaths) -> int:
    state = load_state(paths)
    require_stages(state, "docplan", "fabric")

    charter = load_charter(paths)
    foundation = load_foundation(paths)
    finance = load_finance(paths)
    facts = load_engagements(paths).fact_index()
    manifest = load_manifest(paths)
    style = style_pack(charter)
    people = people_index(foundation)

    finance_hash = sha256_file(paths.finance_json)
    rendered = skipped = pending = 0
    for entry in manifest:
        doc_state = state.doc(entry.doc_id)
        if entry.authoring == "static":
            basis = f"static:{finance_hash}"
        else:
            if doc_state.authored_hash is None:
                pending += 1
                continue
            basis = doc_state.authored_hash

        target = paths.share_dir / entry.path
        if doc_state.rendered_from == basis and target.exists():
            skipped += 1
            continue

        author_name = people[entry.authors[0]]["name"]
        if entry.authoring == "static":
            from .xlsx import render_financial_summary

            render_financial_summary(
                entry, charter, finance, style, author_name, target
            )
        else:
            from ..authoring.ingest import docir_path

            docir = DocIR.model_validate_json(
                docir_path(paths, entry.doc_id).read_text("utf-8")
            )
            resolved = resolve_docir(docir, facts)
            target.parent.mkdir(parents=True, exist_ok=True)
            if entry.format == "docx":
                from .docx import render_docx

                target.write_bytes(
                    render_docx(resolved, entry, style, author_name, people)
                )
            elif entry.format == "pptx":
                from .pptx import render_pptx

                target.write_bytes(
                    render_pptx(resolved, entry, style, author_name)
                )
            elif entry.format == "eml":
                from .eml import render_eml

                target.write_bytes(
                    render_eml(
                        resolved, entry, people, charter.slug, charter.domain
                    )
                )
            elif entry.format == "pdf":
                from .pdf import render_pdf

                sig_fid = entry.render_params.get("sig_fact")
                if sig_fid is not None and str(sig_fid) not in facts:
                    raise SystemExit(
                        f"render: sig_fact {sig_fid!r} not in engagement ledger"
                    )
                render_pdf(
                    resolved,
                    entry,
                    style,
                    author_name,
                    people,
                    target,
                    sig_fact_text=facts[str(sig_fid)].rendered if sig_fid else None,
                )
                if entry.render_params.get("scan"):
                    from .scan import apply_scan

                    apply_scan(
                        paths, entry, target, charter.seed, facts, author_name
                    )
            else:
                raise SystemExit(
                    f"render: no renderer for format {entry.format!r}"
                )

        doc_state.rendered_hash = sha256_file(target)
        doc_state.rendered_from = basis
        state.docs[entry.doc_id] = doc_state
        rendered += 1

    if pending == 0:
        state.mark_done("render", inputs_hash=finance_hash)
    save_state(paths, state)
    print(
        f"render: {rendered} rendered, {skipped} up to date, "
        f"{pending} awaiting authoring"
    )
    return 0
