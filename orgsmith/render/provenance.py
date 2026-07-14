"""Machine-readable synthetic-provenance markers.

Every rendered file declares itself synthetic in its native metadata:
- .docx: a custom document property (docProps/custom.xml)
- .pdf: a DocumentInfo key (plus Creator), stamped via pikepdf
- .xlsx: a custom workbook property (set by the xlsx renderer directly)

The docx marker is injected by rewriting the OPC zip; the same pass
normalizes zip timestamps so rendered bytes are deterministic.
"""

from __future__ import annotations

import io
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path

from .. import PRODUCT_NAME

MARKER_NAME = f"{PRODUCT_NAME}Synthetic"

_CUSTOM_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    "<Properties "
    'xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties" '
    'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
    '<property fmtid="{D5CDD505-2E9C-101B-9397-08002B2CF9AE}" pid="2" '
    f'name="{MARKER_NAME}"><vt:lpwstr>true</vt:lpwstr></property>'
    "</Properties>"
)

_CONTENT_TYPE = (
    '<Override PartName="/docProps/custom.xml" ContentType="application/'
    'vnd.openxmlformats-officedocument.custom-properties+xml"/>'
)

_RELATIONSHIP = (
    f'<Relationship Id="rId{PRODUCT_NAME}" Type="http://schemas.openxmlformats.org/'
    'officeDocument/2006/relationships/custom-properties" '
    'Target="docProps/custom.xml"/>'
)


def add_docx_marker(docx_bytes: bytes) -> bytes:
    """Add the custom-property marker and normalize zip metadata."""
    src = zipfile.ZipFile(io.BytesIO(docx_bytes))
    out_buf = io.BytesIO()
    with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as out:
        for name in src.namelist():
            data = src.read(name)
            if name == "[Content_Types].xml":
                text = data.decode("utf-8")
                if "/docProps/custom.xml" not in text:
                    text = text.replace("</Types>", _CONTENT_TYPE + "</Types>")
                data = text.encode("utf-8")
            elif name == "_rels/.rels":
                text = data.decode("utf-8")
                if "custom-properties" not in text:
                    text = text.replace(
                        "</Relationships>", _RELATIONSHIP + "</Relationships>"
                    )
                data = text.encode("utf-8")
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            out.writestr(info, data)
        info = zipfile.ZipInfo("docProps/custom.xml", date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        out.writestr(info, _CUSTOM_XML)
    return out_buf.getvalue()


def docx_has_marker(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path) as zf:
            if "docProps/custom.xml" not in zf.namelist():
                return False
            xml = zf.read("docProps/custom.xml").decode("utf-8")
            return MARKER_NAME in xml
    except (zipfile.BadZipFile, KeyError, UnicodeDecodeError):
        return False


def stamp_pdf(path: Path, *, title: str, author: str, doc_date: date) -> None:
    import pikepdf

    when = datetime(doc_date.year, doc_date.month, doc_date.day, 9, 0, 0,
                    tzinfo=timezone.utc)
    stamp = when.strftime("D:%Y%m%d%H%M%S+00'00'")
    with pikepdf.open(path, allow_overwriting_input=True) as pdf:
        pdf.docinfo["/Title"] = title
        pdf.docinfo["/Author"] = author
        pdf.docinfo["/Creator"] = PRODUCT_NAME
        pdf.docinfo["/CreationDate"] = stamp
        pdf.docinfo["/ModDate"] = stamp
        pdf.docinfo[f"/{MARKER_NAME}"] = "true"
        pdf.save(path, deterministic_id=True)


def pdf_has_marker(path: Path) -> bool:
    import pikepdf

    try:
        with pikepdf.open(path) as pdf:
            return str(pdf.docinfo.get(f"/{MARKER_NAME}", "")) == "true"
    except pikepdf.PdfError:
        return False


def xlsx_has_marker(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path) as zf:
            if "docProps/custom.xml" not in zf.namelist():
                return False
            xml = zf.read("docProps/custom.xml").decode("utf-8")
            return MARKER_NAME in xml
    except (zipfile.BadZipFile, KeyError, UnicodeDecodeError):
        return False
