"""Unit tier: the fabric's time dimension (M8).

Title history and its date resolver. Churn, rotation, and behavioral
finance join this module as they land.
"""

from datetime import date

import pytest
from pydantic import ValidationError

from orgsmith.schemas import EmploymentSpan, Person, TitleSpan

pytestmark = pytest.mark.unit


def _person(title: str = "Senior Associate", history=None) -> Person:
    return Person(
        id="p:rey.strong",
        name="Rey Strong",
        title=title,
        dept="Advisory",
        reports_to="p:boss",
        employment=EmploymentSpan(start=date(2019, 3, 1)),
        email="rey@example.com",
        phone="555-0100",
        title_history=history or [],
    )


def test_empty_history_resolves_to_title_for_every_date():
    """Most of a roster is never promoted and carries no history. The scalar
    stays the answer, which is what lets a hand-built Person and a synthetic
    charter work without inventing spans."""
    p = _person()
    assert p.title_history == []
    for when in (date(1990, 1, 1), date(2019, 3, 1), date(2050, 12, 31)):
        assert p.title_at(when) == "Senior Associate"


def test_promotion_resolves_the_title_held_on_the_date():
    p = _person(
        title="Director",
        history=[
            TitleSpan(title="Analyst", start=date(2019, 3, 1), end=date(2021, 6, 30)),
            TitleSpan(
                title="Senior Associate", start=date(2021, 7, 1), end=date(2024, 1, 31)
            ),
            TitleSpan(title="Director", start=date(2024, 2, 1)),
        ],
    )
    assert p.title_at(date(2020, 5, 1)) == "Analyst"
    assert p.title_at(date(2022, 9, 15)) == "Senior Associate"
    assert p.title_at(date(2025, 1, 1)) == "Director"
    # Person.title is the latest, and the last span mirrors it.
    assert p.title == p.title_history[-1].title == p.title_at(date(2025, 6, 1))


def test_span_boundaries_are_inclusive_on_both_ends():
    """Off-by-one here would brief the wrong title on exactly the day a
    promotion lands, which is the case a reviewer checks first."""
    p = _person(
        title="Director",
        history=[
            TitleSpan(title="Analyst", start=date(2019, 3, 1), end=date(2021, 6, 30)),
            TitleSpan(title="Director", start=date(2021, 7, 1)),
        ],
    )
    assert p.title_at(date(2019, 3, 1)) == "Analyst"
    assert p.title_at(date(2021, 6, 30)) == "Analyst"
    assert p.title_at(date(2021, 7, 1)) == "Director"


def test_date_outside_every_span_falls_back_to_title():
    """Mirrors employer_at: a resolver that raised on a gap or a pre-hire date
    would push a case the ledger cannot produce onto every caller."""
    p = _person(
        title="Director",
        history=[
            TitleSpan(title="Analyst", start=date(2019, 3, 1), end=date(2021, 6, 30)),
            # Deliberate gap: 2021-07-01 .. 2021-07-31 is covered by no span.
            TitleSpan(title="Director", start=date(2021, 8, 1)),
        ],
    )
    assert p.title_at(date(2015, 1, 1)) == "Director"  # before the first span
    assert p.title_at(date(2021, 7, 15)) == "Director"  # inside the gap


def test_first_matching_span_wins_when_spans_overlap():
    """Overlap is malformed and the ledger should never emit it, but the
    resolver must still be a function rather than order-dependent luck."""
    p = _person(
        title="Director",
        history=[
            TitleSpan(title="Analyst", start=date(2019, 3, 1), end=date(2022, 1, 1)),
            TitleSpan(title="Director", start=date(2021, 1, 1)),
        ],
    )
    assert p.title_at(date(2021, 6, 1)) == "Analyst"


def test_title_span_rejects_end_at_or_before_start():
    with pytest.raises(ValidationError, match="title span end must follow start"):
        TitleSpan(title="Analyst", start=date(2021, 1, 1), end=date(2021, 1, 1))
    with pytest.raises(ValidationError, match="title span end must follow start"):
        TitleSpan(title="Analyst", start=date(2021, 6, 1), end=date(2021, 1, 1))


def test_title_history_is_additive_on_the_existing_schema_id():
    """The six fixtures that stay committed until M11 carry no title_history.
    They must keep loading, and they must resolve every date to the scalar."""
    p = Person.model_validate(
        {
            "id": "p:old.hand",
            "name": "Old Hand",
            "title": "Managing Partner",
            "dept": "Leadership",
            "employment": {"start": "2018-01-01"},
            "email": "old@example.com",
            "phone": "555-0101",
        }
    )
    assert p.title_history == []
    assert p.title_at(date(2020, 1, 1)) == "Managing Partner"
