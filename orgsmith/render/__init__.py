"""render stage: DocIR + ledgers -> real files in the share.

Incremental and resumable: each doc records the content basis it was
rendered from (authored hash, or the finance ledger hash for static docs);
unchanged docs are skipped, unauthored docs are left pending so the org is
browsable after every batch.
"""

from __future__ import annotations

from datetime import date

from ..artifacts import (
    load_charter,
    load_engagements,
    load_finance,
    load_foundation,
    load_manifest,
)
from ..fabric.engagements import employer_at
from ..paths import OrgPaths
from ..schemas import DocIR
from ..state import load_state, require_stages, save_state, sha256_file
from .resolve import resolve_docir
from .styles import style_pack


def people_index(foundation, at: date | None = None) -> dict[str, dict]:
    """name/title/email per person id; shared with the EML-01 validator so
    header recomputation reads the ledger exactly the way render did.

    `at` resolves each external person's employer line via the affiliation
    covering that date (era-appropriate sigblocks for affiliations_in_docs
    orgs); None keeps the current employer. Only the title line varies:
    name and email are single ledger-owned fields, so a prior-era doc
    keeps the current-domain email (known, documented residual)."""
    people = {
        p.id: {"name": p.name, "title": p.title, "email": p.email}
        for p in foundation.people
    }
    for xp in foundation.external_people:
        org_id = employer_at(xp, at) if at is not None else xp.org
        org = next(o for o in foundation.external_orgs if o.id == org_id)
        people[xp.id] = {
            "name": xp.name,
            "title": f"{xp.title}, {org.name}",
            "email": xp.email,
        }
    return people


def _full_mail_body(entry, paths, manifest, facts, foundation, people) -> str:
    """A mail-block message's rendered body (M14): the author's resolved words,
    a deterministic signature block (name / title-as-of-send-date / phone from
    foundation, never authored), then a derived quoted-history tail carrying
    the predecessor's full body. Recurses up the thread, so the chain nests the
    way a real reply does. Pure text, zero tokens, byte-stable on re-render."""
    from ..authoring.ingest import docir_path
    from .eml import _body_text, mail_signature, quote_history, thread_members

    docir = DocIR.model_validate_json(
        docir_path(paths, entry.doc_id).read_text("utf-8")
    )
    resolved = resolve_docir(docir, facts)
    author = foundation.person(entry.authors[0])
    parts = [_body_text(resolved, entry), mail_signature(author, entry.date)]
    thread = thread_members(entry, manifest)
    pos = int(entry.render_params.get("thread_pos", 0))
    if thread is not None and pos > 0:
        pred = thread[pos - 1]
        parts.append(
            quote_history(
                pred,
                _full_mail_body(pred, paths, manifest, facts, foundation, people),
                people,
            )
        )
    return "\n\n".join(parts)


def _render_derived(entry, resolved, style, people, charter, target) -> None:
    """Render a derived noise draft. Noise is planned only in modern,
    non-scan, non-sig formats, so this is the plain DocIR path with none of
    the hard-case machinery (no legacy conversion, scan, or signature fact)."""
    author_name = people[entry.authors[0]]["name"]
    if entry.format == "docx":
        from .docx import render_docx

        target.write_bytes(render_docx(resolved, entry, style, author_name, people))
    elif entry.format == "pptx":
        from .pptx import render_pptx

        target.write_bytes(render_pptx(resolved, entry, style, author_name))
    elif entry.format == "eml":
        from .eml import render_eml

        target.write_bytes(
            render_eml(resolved, entry, people, charter.slug, charter.domain)
        )
    elif entry.format == "pdf":
        from .pdf import render_pdf

        render_pdf(
            resolved, entry, style, author_name, people, target, sig_fact_text=None
        )
    else:
        raise SystemExit(
            f"render: derived noise doc {entry.doc_id} has unrenderable "
            f"format {entry.format!r}"
        )


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
    todo = []
    for entry in manifest:
        if entry.authoring == "derived":
            continue  # noise docs render in a second pass, after their sources
        if entry.render_params.get("attach_path") is not None:
            continue  # transmittal mail renders after its attachment exists
        doc_state = state.doc(entry.doc_id)
        if entry.authoring == "static":
            basis = f"static:{finance_hash}"
        else:
            if doc_state.authored_hash is None:
                pending += 1
                continue
            basis = doc_state.authored_hash

        # A mail-block reply's body quotes every predecessor, reading each
        # predecessor's DocIR (_full_mail_body recurses up the thread). Defer
        # the reply to pending when any predecessor is still unauthored (threads
        # split across batches), so a partial thread stays browsable instead of
        # crashing render on a missing DocIR.
        if entry.render_params.get("send_minute") is not None:
            pos = int(entry.render_params.get("thread_pos", 0))
            if pos > 0:
                from .eml import thread_members

                thread = thread_members(entry, manifest)
                if thread is not None and any(
                    state.doc(pred.doc_id).authored_hash is None
                    for pred in thread[:pos]
                ):
                    pending += 1
                    continue

        target = paths.share_dir / entry.path
        if doc_state.rendered_from == basis and target.exists():
            skipped += 1
            continue
        todo.append((entry, basis, target))

    from ..schemas import BASE_FORMAT

    if any(entry.format in BASE_FORMAT for entry, _, _ in todo):
        # Fail before rendering anything: a run that needs LibreOffice and
        # lacks it should not leave a half-rendered share behind.
        from .legacy import require_soffice

        require_soffice()

    aff_docs = charter.graph_targets.affiliations_in_docs
    for entry, basis, target in todo:
        doc_state = state.doc(entry.doc_id)
        if aff_docs:
            # Era-appropriate surfaces: each doc resolves external
            # employer lines as of its own date.
            people = people_index(foundation, at=entry.date)
        author_name = people[entry.authors[0]]["name"]
        if entry.authoring == "static":
            from .xlsx import render_financial_summary

            if entry.format == "xls":
                import tempfile
                from pathlib import Path

                from .legacy import render_legacy

                with tempfile.TemporaryDirectory() as tmp:
                    modern = Path(tmp) / "intermediate.xlsx"
                    render_financial_summary(
                        entry, charter, finance, style, author_name, modern
                    )
                    render_legacy(entry, modern.read_bytes(), target, facts)
            else:
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
            elif entry.format in ("doc", "ppt"):
                from .legacy import render_legacy

                if entry.format == "doc":
                    from .docx import render_docx

                    modern = render_docx(
                        resolved, entry, style, author_name, people
                    )
                else:
                    from .pptx import render_pptx

                    modern = render_pptx(resolved, entry, style, author_name)
                render_legacy(entry, modern, target, facts)
            elif entry.format == "pptx":
                from .pptx import render_pptx

                target.write_bytes(
                    render_pptx(resolved, entry, style, author_name)
                )
            elif entry.format == "eml":
                from .eml import render_eml, thread_members

                mail_body = (
                    _full_mail_body(
                        entry, paths, manifest, facts, foundation, people
                    )
                    if entry.render_params.get("send_minute") is not None
                    else None
                )
                target.write_bytes(
                    render_eml(
                        resolved, entry, people, charter.slug, charter.domain,
                        thread_members(entry, manifest), mail_body,
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

    # --- derived noise pass (M12): sources are now rendered ---
    by_id = {e.doc_id: e for e in manifest}
    for entry in manifest:
        if entry.authoring != "derived":
            continue
        doc_state = state.doc(entry.doc_id)
        src_state = state.doc(entry.noise_of)
        if src_state.authored_hash is None:
            pending += 1
            continue
        if entry.noise_kind == "exact_duplicate":
            basis = f"exact:{src_state.rendered_hash}"
        else:
            basis = f"draft:{src_state.authored_hash}"
        target = paths.share_dir / entry.path
        if doc_state.rendered_from == basis and target.exists():
            skipped += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if entry.noise_kind == "exact_duplicate":
            import shutil

            src_target = paths.share_dir / by_id[entry.noise_of].path
            shutil.copyfile(src_target, target)
        else:
            from ..authoring.ingest import docir_path
            from .noise import derive_draft_docir

            src_docir = DocIR.model_validate_json(
                docir_path(paths, entry.noise_of).read_text("utf-8")
            )
            draft = resolve_docir(
                derive_draft_docir(src_docir, entry.doc_id), facts
            )
            _render_derived(entry, draft, style, people, charter, target)
        doc_state.rendered_hash = sha256_file(target)
        doc_state.rendered_from = basis
        state.docs[entry.doc_id] = doc_state
        rendered += 1

    # --- transmittal attachment pass (M14): attachments now rendered ---
    for entry in manifest:
        ap = entry.render_params.get("attach_path")
        if ap is None or entry.authoring == "derived":
            continue
        doc_state = state.doc(entry.doc_id)
        if doc_state.authored_hash is None:
            pending += 1
            continue
        attach_file = paths.share_dir / str(ap)
        if not attach_file.exists():
            pending += 1  # the attached document is not rendered yet
            continue
        import hashlib

        from .eml import render_eml, thread_members

        attach_bytes = attach_file.read_bytes()
        basis = (
            f"attach:{doc_state.authored_hash}:"
            f"{hashlib.sha256(attach_bytes).hexdigest()}"
        )
        target = paths.share_dir / entry.path
        if doc_state.rendered_from == basis and target.exists():
            skipped += 1
            continue
        from ..authoring.ingest import docir_path

        who = people_index(foundation, at=entry.date) if aff_docs else people
        docir = DocIR.model_validate_json(
            docir_path(paths, entry.doc_id).read_text("utf-8")
        )
        resolved = resolve_docir(docir, facts)
        mail_body = _full_mail_body(entry, paths, manifest, facts, foundation, who)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(
            render_eml(
                resolved, entry, who, charter.slug, charter.domain,
                thread_members(entry, manifest), mail_body,
                (attach_bytes, str(ap).rsplit("/", 1)[-1]),
            )
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
