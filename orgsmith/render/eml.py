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


def _message_id(doc_id: str, slug: str, domain: str) -> str:
    return f"<{doc_id.replace(':', '')}.{slug}@{domain}>"


def _addr(pid: str, people: dict[str, dict]) -> str:
    return formataddr((people[pid]["name"], people[pid]["email"]))


def thread_members(entry: ManifestEntry, manifest) -> list | None:
    """The ordered messages of a mail-block engagement thread, or None for a
    non-threaded message (knob-off mail, derived noise). Shared by the renderer
    and the EML-01 validator so In-Reply-To / References can never drift: both
    reconstruct the thread from (engagement, thread_pos), never from doc-id
    order (doc ids are assigned after the manifest sort and carry no thread
    meaning)."""
    if "thread_pos" not in entry.render_params or entry.engagement is None:
        return None
    members = [
        e
        for e in manifest
        if e.format == "eml"
        and e.engagement == entry.engagement
        and e.authoring != "derived"
        and "thread_pos" in e.render_params
    ]
    members.sort(key=lambda e: int(e.render_params["thread_pos"]))
    return members


def expected_headers(
    entry: ManifestEntry,
    people: dict[str, dict],
    slug: str,
    domain: str,
    thread: list | None = None,
) -> dict[str, str]:
    """The exact transport headers this entry must carry, shared by the
    renderer and EML-01 so the checker cannot drift from what was written.

    Knob-off mail (no `send_minute` render param): From, To (every other
    participant), Subject, Date at 09:00 UTC, Message-ID from the doc id --
    the pre-M14 behavior, byte-for-byte.

    Mail-block mail (M14): the send minute lands the Date at a real time of
    day; recipients split into To (the client side) and Cc (the internal
    team); a reply (thread_pos > 0) carries In-Reply-To naming its predecessor
    and an ordered References chain, and its Subject reads "RE: {subject}".
    Openers carry neither threading header. `thread` is the ordered thread
    (thread_members); it is required to resolve a reply's predecessor id."""
    author = entry.authors[0]
    mail_on = "send_minute" in entry.render_params
    recipients = [p for p in entry.participants if p != author] or [author]
    if mail_on:
        to = [p for p in recipients if p.startswith("xp:")]
        cc = [p for p in recipients if not p.startswith("xp:")]
        if not to:  # an internal-only message: everyone in To, no Cc
            to, cc = cc, []
    else:
        to, cc = recipients, []

    pos = int(entry.render_params.get("thread_pos", 0))
    minute = int(entry.render_params.get("send_minute", 9 * 60))
    when = datetime(
        entry.date.year, entry.date.month, entry.date.day,
        minute // 60, minute % 60, 0, tzinfo=timezone.utc,
    )
    subject = f"RE: {entry.title}" if (mail_on and pos > 0) else entry.title

    headers = {
        "From": _addr(author, people),
        "To": ", ".join(_addr(p, people) for p in to),
    }
    if cc:
        headers["Cc"] = ", ".join(_addr(p, people) for p in cc)
    headers["Subject"] = subject
    headers["Date"] = format_datetime(when)
    headers["Message-ID"] = _message_id(entry.doc_id, slug, domain)
    if mail_on and pos > 0 and thread is not None:
        pred = thread[pos - 1]
        headers["In-Reply-To"] = _message_id(pred.doc_id, slug, domain)
        headers["References"] = " ".join(
            _message_id(a.doc_id, slug, domain) for a in thread[:pos]
        )
    return headers


def mail_signature(person, when) -> str:
    """The deterministic signature block a mail-block message ends its own
    words with (M14): name, title AS OF the send date, phone -- all from
    foundation, never authored, so a promotion changes the block mid-corpus.
    Shared by the renderer and EML-02 so the two cannot drift."""
    return f"-- \n{person.name}\n{person.title_at(when)}\n{person.phone}"


def quote_history(pred_entry: ManifestEntry, pred_body: str, people) -> str:
    """A derived quoted-history tail: an attribution line plus the
    predecessor's full body (which already nests its own quoted history),
    quote-prefixed. Pure text, zero tokens, byte-stable on re-render."""
    author = pred_entry.authors[0]
    header = f"On {pred_entry.date:%Y-%m-%d}, {people[author]['name']} wrote:"
    quoted = "\n".join(
        ("> " + line).rstrip() for line in pred_body.splitlines()
    )
    return f"{header}\n{quoted}"


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
    thread: list | None = None,
    body: str | None = None,
) -> bytes:
    """`body` overrides the flattened DocIR text: mail-block messages pass a
    full body (authored words + signature + quoted history), built by the
    render stage which holds the thread and the foundation. Knob-off mail
    passes None and keeps the pre-M14 flattened body, byte-for-byte."""
    msg = EmailMessage(policy=policy.SMTP)
    for name, value in expected_headers(
        entry, people, slug, domain, thread
    ).items():
        msg[name] = value
    msg[MARKER_HEADER] = "true"
    msg.set_content(_body_text(docir, entry) if body is None else body)
    return msg.as_bytes()
