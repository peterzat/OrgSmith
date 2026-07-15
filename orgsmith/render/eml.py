""".eml renderer: stdlib email, fully deterministic.

Every header is a pure function of the manifest entry plus the ledgers
(`expected_headers`), shared with the EML-01 validator rule so the
renderer and the checker can never drift apart. The body is the DocIR
flattened to text/plain. Re-rendering writes identical bytes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from email import policy
from email.message import EmailMessage
from email.utils import format_datetime, formataddr

from .. import PRODUCT_NAME
from ..schemas import DocIR, ManifestEntry

MARKER_HEADER = f"X-{PRODUCT_NAME}-Synthetic"


def expected_headers(
    entry: ManifestEntry, people: dict[str, dict], slug: str, domain: str
) -> dict[str, str]:
    """The exact transport headers this entry must carry: From is the
    author, To is every other participant in manifest order, Date is
    09:00 UTC on the doc date, Message-ID derives from the doc id."""
    author = entry.authors[0]
    recipients = [p for p in entry.participants if p != author] or [author]
    when = datetime(
        entry.date.year, entry.date.month, entry.date.day, 9, 0, 0,
        tzinfo=timezone.utc,
    )
    return {
        "From": formataddr((people[author]["name"], people[author]["email"])),
        "To": ", ".join(
            formataddr((people[p]["name"], people[p]["email"]))
            for p in recipients
        ),
        "Subject": entry.title,
        "Date": format_datetime(when),
        "Message-ID": f"<{entry.doc_id.replace(':', '')}.{slug}@{domain}>",
    }


def _body_text(docir: DocIR, entry: ManifestEntry) -> str:
    lines: list[str] = []
    for block in docir.blocks:
        if block.kind == "heading":
            lines += [block.text, ""]
        elif block.kind == "paragraph":
            lines += [block.text, ""]
        elif block.kind == "list":
            lines += [f"  - {item}" for item in block.items] + [""]
        elif block.kind == "table":
            if block.header:
                lines.append(" | ".join(block.header))
            lines += [" | ".join(row) for row in block.rows] + [""]
        elif block.kind == "sigblock":
            raise SystemExit(
                f"render: sigblock in {entry.doc_id} ({entry.format}); mail "
                "carries no signature blocks"
            )
    return "\n".join(lines).strip() + "\n"


def render_eml(
    docir: DocIR,
    entry: ManifestEntry,
    people: dict[str, dict],
    slug: str,
    domain: str,
) -> bytes:
    msg = EmailMessage(policy=policy.SMTP)
    for name, value in expected_headers(entry, people, slug, domain).items():
        msg[name] = value
    msg[MARKER_HEADER] = "true"
    msg.set_content(_body_text(docir, entry))
    return msg.as_bytes()
