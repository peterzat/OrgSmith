"""Unit tier: the engagement-book-is-sample coherence knob (M12,
engagement-ledger-reads-as-whole-book). The board found the firm overview
presenting the sampled engagement ledger as the whole book while the financial
summary posts 20-60x the fee total. When a recipe declares the book a sample,
firm_digest tells the author so, and report records the fee/revenue ratio."""

from datetime import date

import pytest

from orgsmith.authoring.contexts import _firm_digest
from orgsmith.review.report import _fee_coverage_lines

from conftest import REPO, build_pure_stages
from orgsmith.charter import run_charter
from orgsmith.fabric import run_fabric
from orgsmith.foundation.scaffold import run_scaffold
from orgsmith.docplan import run_docplan
from orgsmith.paths import OrgPaths

pytestmark = pytest.mark.unit


class _Eng:
    def __init__(self, eid, start):
        self.id = eid
        self.start = start


def test_firm_digest_off_is_unchanged_and_claims_completeness():
    """Default off keeps the pre-M12 digest byte-identical, including the
    completeness instruction that let the overview claim the whole book."""
    engs = [_Eng("E-2019-001", date(2019, 3, 1))]
    digest = _firm_digest(engs, date(2021, 1, 1), book_is_sample=False)
    assert "claim no engagement not listed here" in digest
    assert "sample" not in digest.lower()


def test_firm_digest_on_frames_the_book_as_a_sample():
    """On, the digest forbids completeness claims and frames the engagements
    as a representative sample of a larger book."""
    engs = [_Eng("E-2019-001", date(2019, 3, 1))]
    digest = _firm_digest(engs, date(2021, 1, 1), book_is_sample=True)
    assert "sample" in digest.lower()
    assert "not its complete book" in digest
    assert "whole business" in digest  # instructs NOT to call it that
    assert "{{fact:f:E-2019-001.client}}" in digest  # clients still by fact id


def test_firm_digest_empty_book_is_shared_by_both_modes():
    """An overview dated before any engagement gets the same no-client digest
    either way; there is nothing to frame as a sample yet."""
    off = _firm_digest([], date(2019, 1, 1), book_is_sample=False)
    on = _firm_digest([], date(2019, 1, 1), book_is_sample=True)
    assert off == on
    assert "no completed client" in off


def _build_sample_org(root) -> OrgPaths:
    dest = root / "recipes" / "dev-mini"
    dest.mkdir(parents=True, exist_ok=True)
    text = (REPO / "recipes" / "dev-mini" / "ORG-CHARTER.md").read_text()
    anchor = "engagements:\n"
    assert anchor in text
    text = text.replace(anchor, anchor + "  book_is_sample: true\n", 1)
    (dest / "ORG-CHARTER.md").write_text(text)
    paths = OrgPaths(root=root, slug="dev-mini")
    assert run_charter(paths) == 0
    assert run_scaffold(paths) == 0
    assert run_fabric(paths) == 0
    assert run_docplan(paths) == 0
    return paths


def test_report_records_the_fee_revenue_ratio(tmp_path):
    """The fee-coverage measurement is deterministic and present whether or not
    the knob is declared; it names the ratio and the recipe's stance."""
    off = build_pure_stages(tmp_path / "off")
    lines = "\n".join(_fee_coverage_lines(off))
    assert "of lifetime revenue" in lines
    assert "does not declare the engagement book a sample" in lines

    on = _build_sample_org(tmp_path / "on")
    lines_on = "\n".join(_fee_coverage_lines(on))
    assert "declares the engagement book a sample" in lines_on
    assert "expected and coherent" in lines_on
