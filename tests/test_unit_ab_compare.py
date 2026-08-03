"""M17c: the control check never certifies a comparison it did not run.

`tools/ab_compare.py` exists to say whether the two arms are the same corpus.
Its first printed line reports the identity fields, and on the paths where the
manifests are too far apart to compare entry by entry that line has nothing to
report: the fields were never looked at. Printing them as identical there
would be the one output this tool must never produce, because a human reads
the report top-down and the exit code is the only other signal.

Nothing here is a threshold and nothing here reads authored prose.
"""

import json

import pytest

from orgsmith.paths import OrgPaths

from tools.ab_compare import IDENTITY_FIELDS, compare, main

pytestmark = pytest.mark.unit

SLUG = "quillon-harbor"


def _entry(n: int) -> dict:
    return {
        "schema_id": "orgsmith/manifest-entry@1",
        "doc_id": f"d:{n:04d}",
        "path": f"Engagements/doc-{n}.docx",
        "title": f"Document {n}",
        "genre": "status_report",
        "format": "docx",
        "date": "2024-03-01",
        "authors": ["p:someone"],
        "engagement": None,
        "rev": 0,
        "authoring": "batchable",
    }


def _arm(root, entries: list[dict]) -> OrgPaths:
    """The deterministic artifacts `compare` reads, and nothing else."""
    paths = OrgPaths(root=root, slug=SLUG)
    paths.ledger_dir.mkdir(parents=True)
    paths.docplan_dir.mkdir(parents=True)
    paths.foundation_json.write_text('{"schema_id": "orgsmith/foundation@1"}')
    paths.manifest_jsonl.write_text(
        "".join(json.dumps(e, sort_keys=True) + "\n" for e in entries)
    )
    return paths


def _run(tmp_path, control_entries, treatment_entries, capsys):
    _arm(tmp_path / "control", control_entries)
    _arm(tmp_path / "treatment", treatment_entries)
    code = main(
        [
            SLUG,
            "--control",
            str(tmp_path / "control"),
            "--treatment",
            str(tmp_path / "treatment"),
        ]
    )
    return code, capsys.readouterr().out


@pytest.mark.parametrize(
    "treatment,why",
    [
        ([_entry(1), _entry(2)], "manifest length differs"),
        ([_entry(1), _entry(9), _entry(3)], "manifest order diverged"),
    ],
    ids=["length", "order"],
)
def test_early_return_reports_the_identity_check_as_not_run(
    tmp_path, capsys, treatment, why
):
    """The finding, as a test.

    On both bail-out paths `compare` returns before a single identity field
    is compared, so the report must say so rather than derive "identical"
    from the absence of a complaint it had no chance to raise.
    """
    control = [_entry(1), _entry(2), _entry(3)]
    code, out = _run(tmp_path, control, treatment, capsys)

    assert code == 1
    assert "identity fields: NOT CHECKED" in out
    assert "identity fields identical" not in out, (
        f"the arms bailed on {why} and the report certified the identity "
        "fields anyway; a human reading top-down is told the arms match"
    )


def test_compare_reports_whether_the_identity_check_ran(tmp_path):
    """The third return value is what `main` keys the headline off."""
    control = _arm(tmp_path / "control", [_entry(1), _entry(2)])
    short = _arm(tmp_path / "short", [_entry(1)])
    same = _arm(tmp_path / "same", [_entry(1), _entry(2)])

    assert compare(control, short)[2] is False
    assert compare(control, same)[2] is True


def test_identical_arms_still_report_every_identity_field(tmp_path, capsys):
    """The fix must not cost the headline on the path that earned it."""
    entries = [_entry(1), _entry(2), _entry(3)]
    code, out = _run(tmp_path, entries, list(entries), capsys)

    assert code == 0
    assert "identity fields identical: " in out
    for field in IDENTITY_FIELDS:
        assert field in out
