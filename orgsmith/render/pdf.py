""".pdf renderer: Jinja2 HTML through WeasyPrint, with paged-media
letterhead and page numbers, then pikepdf metadata stamping."""

from __future__ import annotations

import html
from pathlib import Path

from jinja2 import Environment

from .. import PRODUCT_NAME
from ..fabric.engagements import render_date
from ..schemas import DocIR, ManifestEntry
from .provenance import stamp_pdf
from .styles import StylePack


def no_remote_fetcher(url: str, timeout=None, ssl_context=None):
    """URL fetcher that upholds the no-network guarantee: only inline data:
    URIs are served; anything remote is refused before a socket exists.
    Block content is HTML-escaped upstream, so this is defense in depth."""
    if url.startswith("data:"):
        from weasyprint import default_url_fetcher

        return default_url_fetcher(url)
    raise ValueError(f"{PRODUCT_NAME}: remote resource blocked: {url}")

_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {
  size: Letter;
  margin: 2.6cm 2.2cm 2.4cm 2.2cm;
  @top-left { content: "{{ letterhead0 }}"; font-family: {{ font }}, {{ generic }};
              font-size: 8.5pt; color: #{{ accent }}; }
  @bottom-center { content: "Page " counter(page) " of " counter(pages);
                   font-size: 8.5pt; color: #555; }
}
body { font-family: {{ font }}, {{ generic }}; font-size: 11pt;
       line-height: 1.45; color: #1a1a1a; }
.letterhead { border-bottom: 2px solid #{{ accent }}; margin-bottom: 1.6em;
              padding-bottom: 0.5em; }
.letterhead .name { font-size: 15pt; font-weight: bold; color: #{{ accent }}; }
.letterhead .sub { font-size: 9pt; color: #444; }
h1 { font-size: 13pt; color: #{{ accent }}; }
h2, h3 { font-size: 11.5pt; }
.dateline { margin: 1.2em 0; }
table { border-collapse: collapse; margin: 0.8em 0; width: 100%; }
td, th { border: 1px solid #999; padding: 4px 8px; font-size: 10pt;
         text-align: left; }
.sig { margin-top: 2.2em; }
.sig .line { margin-top: 2.4em; border-top: 1px solid #333; width: 45%;
             padding-top: 2px; }
.sig .name { font-weight: bold; }
.sig .meta { font-size: 10pt; color: #333; }
</style>
</head>
<body>
<div class="letterhead">
  <div class="name">{{ letterhead0 }}</div>
  {% for line in letterhead_rest %}<div class="sub">{{ line }}</div>{% endfor %}
</div>
<div class="dateline">{{ dateline }}</div>
{{ body }}
</body>
</html>
"""

_ENV = Environment(autoescape=False)


def _blocks_to_html(docir: DocIR, people: dict[str, dict], when_text: str) -> str:
    parts: list[str] = []
    esc = html.escape
    for block in docir.blocks:
        if block.kind == "heading":
            level = min(max(block.level, 1), 3)
            parts.append(f"<h{level}>{esc(block.text)}</h{level}>")
        elif block.kind == "paragraph":
            parts.append(f"<p>{esc(block.text)}</p>")
        elif block.kind == "list":
            items = "".join(f"<li>{esc(i)}</li>" for i in block.items)
            parts.append(f"<ul>{items}</ul>")
        elif block.kind == "table":
            head = ""
            if block.header:
                cells = "".join(f"<th>{esc(c)}</th>" for c in block.header)
                head = f"<tr>{cells}</tr>"
            rows = "".join(
                "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in row) + "</tr>"
                for row in block.rows
            )
            parts.append(f"<table>{head}{rows}</table>")
        elif block.kind == "sigblock":
            for signer in block.signers:
                person = people[signer]
                parts.append(
                    '<div class="sig"><div class="line"></div>'
                    f'<div class="name">{esc(person["name"])}</div>'
                    f'<div class="meta">{esc(person["title"])}</div>'
                    f'<div class="meta">Date: {esc(when_text)}</div></div>'
                )
    return "\n".join(parts)


def render_pdf(
    docir: DocIR,
    entry: ManifestEntry,
    style: StylePack,
    author_name: str,
    people: dict[str, dict],
    target: Path,
) -> None:
    from weasyprint import HTML

    when_text = render_date(entry.date)
    doc_html = _ENV.from_string(_TEMPLATE).render(
        font=f'"{style.font_family}"',
        generic=style.font_generic,
        accent=style.accent_hex,
        letterhead0=style.letterhead_lines[0],
        letterhead_rest=list(style.letterhead_lines[1:]),
        dateline=when_text,
        body=_blocks_to_html(docir, people, when_text),
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=doc_html, url_fetcher=no_remote_fetcher).write_pdf(str(target))
    stamp_pdf(target, title=entry.title, author=author_name, doc_date=entry.date)
