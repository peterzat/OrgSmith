"""Unit tier: the M14 email-culture knob (`doc_culture.mail`, MailCulture).

Presence turns on thread mechanics for engagement mail; absence leaves every
committed artifact byte-identical (the byte pin is the load-bearing proof of
that, in the org/flagship tiers). This file grows with the mechanics; it opens
with the schema-level inertness and validation checks.
"""

import pytest
from pydantic import ValidationError

from orgsmith.schemas import DocCulture, MailCulture

pytestmark = pytest.mark.unit


def test_mail_defaults_off_on_doc_culture():
    """A DocCulture built without a mail block carries None: the whole knob is
    absent, so the planner takes the pre-M14 single-message path."""
    culture = DocCulture(
        target_docs=20,
        date_range=(__import__("datetime").date(2020, 1, 1),
                    __import__("datetime").date(2024, 12, 31)),
        format_mix={"docx": 10, "eml": 5},
    )
    assert culture.mail is None


def test_mail_culture_sensible_defaults():
    mc = MailCulture()
    assert mc.business_hours == (9, 17)
    assert mc.max_thread_depth == 6
    assert mc.mundane_emails == 0
    assert mc.attachments == 0


@pytest.mark.parametrize("hours", [(17, 9), (9, 9), (-1, 8), (8, 25)])
def test_business_hours_must_be_a_valid_window(hours):
    with pytest.raises(ValidationError):
        MailCulture(business_hours=hours)


def test_max_thread_depth_must_be_positive():
    with pytest.raises(ValidationError):
        MailCulture(max_thread_depth=0)


def test_mail_culture_rejects_unknown_fields():
    with pytest.raises(ValidationError):
        MailCulture(cc=True)  # extra="forbid" on every contract
