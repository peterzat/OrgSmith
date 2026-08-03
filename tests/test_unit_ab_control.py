"""M17c: the two arms differ in the M17b knobs and in nothing else.

SPEC.md 2026-08-03 criterion one asks for one recipe generated twice "with
the M17b knobs as the only variable", and criterion three asks that the
control be exact where it must be. Neither is checkable by reading two
recipe files side by side, which is why `tools/ab_control.py` derives one
from the other and this module diffs the resulting *charters*.

Charters rather than recipe text, deliberately: the control's yaml block is
re-emitted by `yaml.safe_dump`, so the files differ in whitespace, key order
and comments no matter what. What has to hold is that the two parsed
contracts agree field for field, because the charter is what every
downstream stage reads.
"""

import pytest
import yaml

from orgsmith.charter import parse_charter_md
from orgsmith.schemas import dump_json

from conftest import REPO
from tools.ab_control import ARM_KNOBS, main, strip_arm_knobs

pytestmark = pytest.mark.unit

SLUG = "quillon-harbor"


def _recipe_text():
    return (REPO / "recipes" / SLUG / "ORG-CHARTER.md").read_text()


def _arms():
    treatment = _recipe_text()
    control, removed = strip_arm_knobs(treatment)
    return (
        parse_charter_md(treatment, SLUG),
        parse_charter_md(control, SLUG),
        removed,
    )


def test_treatment_recipe_declares_every_arm_knob():
    """The experiment is only as good as its treatment arm.

    A recipe that quietly lost a knob would still generate, still validate,
    and still produce a comparison -- of nothing. Fail here instead.
    """
    _, _, removed = _arms()
    assert removed == [f"{s}.{k}" for s, k in ARM_KNOBS], (
        f"{SLUG} does not declare every arm knob: stripped {removed}. "
        "The treatment arm must turn on all of them, or the control arm is "
        "not a control for the ones it is missing."
    )


def test_arms_differ_in_exactly_the_arm_knobs():
    """The whole experiment in one assertion.

    Walks both charters as plain dicts and collects every path whose value
    differs. That set must equal ARM_KNOBS. A new recipe knob that lands in
    the treatment arm without being declared an arm variable shows up here as
    an extra path, which is the confound this test exists to catch.
    """
    treatment, control, _ = _arms()
    t = yaml.safe_load(dump_json(treatment))
    c = yaml.safe_load(dump_json(control))

    differing = set()

    def walk(a, b, path):
        if isinstance(a, dict) and isinstance(b, dict):
            for key in set(a) | set(b):
                walk(a.get(key), b.get(key), path + (key,))
        elif a != b:
            differing.add(path)

    walk(t, c, ())
    expected = {(s, k) for s, k in ARM_KNOBS}
    assert differing == expected, (
        f"arms differ at {sorted(differing)}; expected exactly "
        f"{sorted(expected)}. An unexpected path means the two arms are not "
        "a controlled comparison: something other than the M17b knobs "
        "changed, and any difference the structural axis reports could be "
        "that instead."
    )


def test_control_arm_leaves_every_knob_inert():
    """Absence, not `false`. The control has to exercise the same knob-off
    path the frozen fleet runs, so that the comparison's baseline is the
    generator as every committed org already uses it."""
    _, control, _ = _arms()
    assert control.doc_culture.outline_variety is False
    assert control.doc_culture.client_facing_reports is False
    assert control.engagements.scope is None


def test_narrative_brief_is_byte_identical_across_arms():
    """The brief is handed to the model on every authoring batch.

    If the derivation reflowed a single line of prose, the two arms would be
    authoring against different instructions and the experiment would measure
    that difference alongside the knobs. This is the one part of the recipe
    the tool must copy rather than re-emit.
    """
    treatment, control, _ = _arms()
    assert treatment.narrative == control.narrative
    assert treatment.narrative.strip(), "a charter with no brief proves nothing"


def test_deriving_from_a_control_arm_is_an_error(tmp_path):
    """Running the tool twice must not silently yield two identical arms.

    The failure mode is quiet and expensive: two knob-off corpora authored at
    full cost that differ only by sampling noise, reported as a null result.
    The guard lives in `main()`, so this drives `main()`: asserting only that
    a second strip removes nothing would cover the precondition the guard
    keys on and leave the guard itself untested.
    """
    control_text, _ = strip_arm_knobs(_recipe_text())
    src = tmp_path / "src" / "recipes" / SLUG
    src.mkdir(parents=True)
    (src / "ORG-CHARTER.md").write_text(control_text)
    out = tmp_path / "out"

    with pytest.raises(SystemExit) as exc:
        main([SLUG, "--root", str(out), "--source-root", str(tmp_path / "src")])
    assert exc.value.code != 0
    assert not out.exists(), (
        "the guard must fire before the derived recipe is written; a second "
        "control arm on disk is what would get authored at full cost"
    )


def test_deriving_in_place_is_an_error(tmp_path):
    """`--root` equal to `--source-root` must not overwrite the treatment arm.

    Stripping in place destroys the only copy of the knobs-on recipe while the
    run prints its normal success line, and the double-derive guard above
    cannot catch it: `removed` is non-empty on the run that does the damage.
    Both arms then become controls and the experiment reports a null result
    that is an artifact of the tooling.
    """
    treatment = _recipe_text()
    root = tmp_path / "repo"
    recipe = root / "recipes" / SLUG / "ORG-CHARTER.md"
    recipe.parent.mkdir(parents=True)
    recipe.write_text(treatment)

    with pytest.raises(SystemExit) as exc:
        main([SLUG, "--root", str(root), "--source-root", str(root)])
    assert exc.value.code != 0
    assert recipe.read_text() == treatment, (
        "the treatment recipe must survive byte-for-byte; a stripped one on "
        "disk is a silently destroyed arm"
    )
