"""Unit tier: the no-network guarantee at the PDF renderer."""

import io

import pytest

from orgsmith.render.pdf import no_remote_fetcher

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    "url",
    [
        "http://example.invalid/x.png",
        "https://example.invalid/style.css",
        "file:///etc/passwd",
        "ftp://example.invalid/a",
    ],
)
def test_fetcher_refuses_remote_and_local_urls(url):
    with pytest.raises(ValueError, match="remote resource blocked"):
        no_remote_fetcher(url)


def test_render_survives_blocked_resource_without_network():
    from weasyprint import HTML

    html = (
        '<html><body><p>text</p>'
        '<img src="http://127.0.0.1:1/never-fetched.png">'
        '<link rel="stylesheet" href="https://example.invalid/x.css">'
        "</body></html>"
    )
    buf = io.BytesIO()
    # The fetcher raises before any socket is opened; WeasyPrint logs the
    # failed resource and still produces a document.
    HTML(string=html, url_fetcher=no_remote_fetcher).write_pdf(buf)
    assert buf.getvalue().startswith(b"%PDF")
