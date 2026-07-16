"""The authoring effort floor: stated here, referenced everywhere else.

Content quality tracks the model and the effort it runs at, and an
authoring pass that silently ran at low effort produces a corpus that
looks fine and reads wrong. Nothing downstream can detect that from the
artifacts, so the only defense is to surface the setting BEFORE tokens are
spent and to record what actually ran.

This module is the single source of the floor. `doctor` prints it, the
skills reference it, and the README points at it; none of them restate the
value. A short-tier test pins that.

What the harness exposes, verified rather than assumed:

- **Effort** arrives as `CLAUDE_EFFORT` in the environment, so Python can
  read it and warn. It is a hint, not a guarantee: the variable describes
  the session that launched the process, and a worker could in principle
  run elsewhere.
- **Model** is NOT in the environment. Only the agent knows which model it
  is, so the model half is self-reported by the skill into the deliverable's
  `generator` field. That is exactly why provenance is a record and never
  an oracle: nothing here is verifiable from artifacts.
"""

from __future__ import annotations

import os

# The lowest effort at which an authoring pass should be dispatched.
AUTHORING_EFFORT_FLOOR = "high"

# Ascending. Anything the harness reports that is not in this tuple is
# treated as unknown rather than guessed at.
EFFORT_ORDER = ("low", "medium", "high", "xhigh", "max")

_ENV_VAR = "CLAUDE_EFFORT"


def session_effort() -> str | None:
    """The effort this process was launched under, or None if unreported."""
    value = os.environ.get(_ENV_VAR, "").strip().lower()
    return value or None


def meets_floor(effort: str | None) -> bool | None:
    """True/False against the floor; None when the effort is unknown.

    Unknown is deliberately not False: an unreported effort is a gap in
    what we can see, not evidence of a low setting, and treating it as a
    failure would train users to ignore the warning.
    """
    if effort is None or effort not in EFFORT_ORDER:
        return None
    return EFFORT_ORDER.index(effort) >= EFFORT_ORDER.index(AUTHORING_EFFORT_FLOOR)


def effort_report() -> tuple[str, bool]:
    """(human line, ok) for the capability probe.

    `ok` is False only for a *known* effort below the floor, so an
    unreported effort never fails a run.
    """
    effort = session_effort()
    verdict = meets_floor(effort)
    if verdict is None:
        shown = effort or "unreported"
        return (
            f"{shown} (authoring floor: {AUTHORING_EFFORT_FLOOR}; "
            f"set by the session, not by {_ENV_VAR} alone)",
            True,
        )
    if verdict:
        return f"{effort} (authoring floor: {AUTHORING_EFFORT_FLOOR}) ok", True
    return (
        f"{effort} BELOW the authoring floor ({AUTHORING_EFFORT_FLOOR}): "
        f"prose quality tracks effort; raise it with /effort before authoring",
        False,
    )
