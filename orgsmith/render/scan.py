"""Scan transform: a rendered pdf becomes a degraded raster scan.

Applied after render_pdf when docplan flagged the doc. The true per-page
text is archived first (the oracle for image-only docs), then pages are
rasterized, degraded deterministically per doc seed, and rebuilt as an
image pdf. OCR-layer docs additionally carry an invisible (render mode 3)
text layer: the archived text with synthetic OCR corruptions (l/1, O/0,
rn/m) that may only touch prose OUTSIDE planted fact and mention
surfaces, so the fact/mention/location rules keep holding by
construction. Provenance is re-stamped after the rebuild.
"""

from __future__ import annotations

import io
import re
from pathlib import Path

from ..naming import doc_id_filename
from ..paths import OrgPaths
from ..schemas import Fact, ManifestEntry, ScanPages, write_model
from ..seeds import derive_seed, rng
from .provenance import stamp_pdf

_PAGE_W, _PAGE_H = 612, 792  # Letter, points
_DPI = 150
_SWAPS = {"rn": "m", "l": "1", "O": "0"}
_CANDIDATE = re.compile("|".join(_SWAPS))


def scan_pages_path(paths: OrgPaths, doc_id: str) -> Path:
    return paths.scans_dir / doc_id_filename(doc_id, ".pages.json")


def _protected_surfaces(entry: ManifestEntry, facts: dict[str, Fact]) -> list[str]:
    refs = set(entry.facts_refs) | {k.fact_id for k in entry.key_facts}
    surfaces = [facts[r].rendered for r in sorted(refs) if r in facts]
    surfaces += [m.surface for m in entry.mentions]
    return surfaces


def _protected_mask(line: str, surfaces: list[str]) -> list[bool]:
    mask = [False] * len(line)
    for surface in surfaces:
        start = line.find(surface)
        while start != -1:
            for i in range(start, start + len(surface)):
                mask[i] = True
            start = line.find(surface, start + 1)
    return mask


def corrupt_pages(
    pages: list[str], surfaces: list[str], rand
) -> tuple[list[str], int]:
    """The archived text with seeded OCR corruptions outside protected
    spans. Guarantees at least one corruption (the first candidate is
    forced if the dice never fired); returns (pages, corruption count)."""
    out_pages: list[str] = []
    applied = 0
    first: tuple[int, int, str] | None = None  # (page, line, corrupted line)
    for p, page in enumerate(pages):
        out_lines: list[str] = []
        for li, line in enumerate(page.splitlines()):
            mask = _protected_mask(line, surfaces)
            pieces: list[str] = []
            cursor = 0
            for m in _CANDIDATE.finditer(line):
                if any(mask[m.start() : m.end()]):
                    continue
                swapped = (
                    line[cursor : m.start()] + _SWAPS[m.group(0)]
                )
                if first is None:
                    first = (p, li, m.start())
                if rand.random() < 0.12:
                    pieces.append(swapped)
                    cursor = m.end()
                    applied += 1
            pieces.append(line[cursor:])
            out_lines.append("".join(pieces))
        out_pages.append("\n".join(out_lines))
    if applied == 0 and first is not None:
        p, li, start = first
        lines = out_pages[p].splitlines()
        line = lines[li]
        for pat, repl in _SWAPS.items():
            if line.startswith(pat, start):
                lines[li] = line[:start] + repl + line[start + len(pat) :]
                break
        out_pages[p] = "\n".join(lines)
        applied = 1
    return out_pages, applied


def _pdf_escape(text: str) -> bytes:
    raw = text.encode("cp1252", errors="replace")
    return raw.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def _degraded_images(target: Path, seed: int, doc_id: str) -> list:
    import numpy as np
    import pypdfium2 as pdfium
    from PIL import Image, ImageEnhance

    rand = rng(seed, "render.scan", doc_id)
    angle = rand.uniform(-0.8, 0.8)
    sigma = rand.uniform(4.0, 8.0)
    contrast = rand.uniform(0.85, 0.97)
    noise_rng = np.random.default_rng(
        derive_seed(seed, "render.scan.noise", doc_id)
    )

    images = []
    doc = pdfium.PdfDocument(str(target))
    try:
        for page in doc:
            img = page.render(scale=_DPI / 72).to_pil().convert("L")
            arr = np.asarray(img).astype(np.int16)
            arr = arr + noise_rng.normal(0, sigma, arr.shape)
            img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
            img = ImageEnhance.Contrast(img).enhance(contrast)
            img = img.rotate(angle, expand=False, fillcolor=255)
            images.append(img)
    finally:
        doc.close()
    return images


def _rebuild_pdf(target: Path, images: list, ocr_pages: list[str] | None) -> None:
    import pikepdf

    pdf = pikepdf.new()
    for i, img in enumerate(images):
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=70)
        image_obj = pikepdf.Stream(pdf, buf.getvalue())
        image_obj.stream_dict = pikepdf.Dictionary(
            Type=pikepdf.Name.XObject,
            Subtype=pikepdf.Name.Image,
            Width=img.size[0],
            Height=img.size[1],
            ColorSpace=pikepdf.Name.DeviceGray,
            BitsPerComponent=8,
            Filter=pikepdf.Name.DCTDecode,
        )
        ops = [
            b"q",
            b"%d 0 0 %d 0 0 cm" % (_PAGE_W, _PAGE_H),
            b"/Im0 Do",
            b"Q",
        ]
        resources = pikepdf.Dictionary(
            XObject=pikepdf.Dictionary(Im0=image_obj)
        )
        if ocr_pages is not None:
            # Invisible text layer (render mode 3): extractable, unseen.
            ops.append(b"BT 3 Tr /F1 8 Tf")
            y = _PAGE_H - 32
            for line in ocr_pages[i].splitlines():
                if line.strip():
                    ops.append(
                        b"1 0 0 1 36 %d Tm (%s) Tj" % (y, _pdf_escape(line))
                    )
                y -= 12
            ops.append(b"ET")
            resources.Font = pikepdf.Dictionary(
                F1=pikepdf.Dictionary(
                    Type=pikepdf.Name.Font,
                    Subtype=pikepdf.Name.Type1,
                    BaseFont=pikepdf.Name.Helvetica,
                    Encoding=pikepdf.Name.WinAnsiEncoding,
                )
            )
        page = pikepdf.Dictionary(
            Type=pikepdf.Name.Page,
            MediaBox=[0, 0, _PAGE_W, _PAGE_H],
            Resources=resources,
            Contents=pikepdf.Stream(pdf, b"\n".join(ops)),
        )
        pdf.pages.append(pikepdf.Page(pdf.make_indirect(page)))
    pdf.save(str(target), deterministic_id=True)


def apply_scan(
    paths: OrgPaths,
    entry: ManifestEntry,
    target: Path,
    seed: int,
    facts: dict[str, Fact],
    author_name: str,
) -> None:
    from pypdf import PdfReader

    true_pages = [
        page.extract_text() or "" for page in PdfReader(str(target)).pages
    ]
    write_model(
        scan_pages_path(paths, entry.doc_id),
        ScanPages(doc_id=entry.doc_id, pages=true_pages),
    )

    ocr_pages = None
    if entry.render_params.get("ocr_layer"):
        surfaces = _protected_surfaces(entry, facts)
        rand = rng(seed, "render.scan.ocr", entry.doc_id)
        ocr_pages, applied = corrupt_pages(true_pages, surfaces, rand)
        if applied == 0:
            raise SystemExit(
                f"render: {entry.doc_id} has no corruptible prose outside "
                "protected fact/mention spans; the OCR-corruption contract "
                "cannot hold for this document"
            )
        joined_true = "\n".join(true_pages)
        joined_ocr = "\n".join(ocr_pages)
        for surface in surfaces:
            if joined_true.count(surface) != joined_ocr.count(surface):
                raise SystemExit(
                    f"render: OCR corruption touched protected surface "
                    f"{surface!r} in {entry.doc_id}"
                )

    _rebuild_pdf(target, _degraded_images(target, seed, entry.doc_id), ocr_pages)
    stamp_pdf(
        target, title=entry.title, author=author_name, doc_date=entry.date
    )
