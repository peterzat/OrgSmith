"""orgsmith doctor: capability probe, scoped by intent.

Two intents share one install, and they need different things:

- **Validating and scoring** a committed org needs only pure-python
  readers. That is what a consumer who cloned the repo for the data does,
  and it must report healthy.
- **Generating** an org additionally needs the rendering stack: WeasyPrint
  (which needs system Pango) for pdfs, and LibreOffice for legacy binaries
  when a recipe asks for them.

So a missing rendering stack reports "generation not available" and exits
0, rather than failing a machine that was never going to generate anything.
Missing pure-python dependencies remain a hard failure, because nothing
works without them.
"""

from __future__ import annotations

import importlib
import shutil
import sys

from .effort import effort_report
from .paths import OrgPaths
from .state import load_state, save_state

_REQUIRED = [
    "pydantic",
    "yaml",
    "jinja2",
    "faker",
    "docx",
    "xlsxwriter",
    "pypdf",
    "pikepdf",
    "openpyxl",
    "pptx",
    "pypdfium2",
    "PIL",
    "numpy",
    "olefile",
    "xlrd",
]

_OPTIONAL_BINARIES = {"soffice": "legacy .doc/.xls/.ppt conversion at render time"}


def probe() -> tuple[dict[str, str], bool, bool]:
    """(results, ok, can_generate). `ok` covers validating and scoring, the
    intent every install has to serve; `can_generate` additionally covers
    the rendering stack."""
    results: dict[str, str] = {
        "python": ".".join(str(v) for v in sys.version_info[:3])
    }
    ok = True
    for module in _REQUIRED:
        try:
            importlib.import_module(module)
            results[module] = "ok"
        except ImportError as err:
            results[module] = f"MISSING ({err})"
            ok = False
    # WeasyPrint needs system Pango, and only the render stage calls it.
    # Absent, this box can still validate and score every committed org.
    try:
        importlib.import_module("weasyprint")
        results["weasyprint"] = "ok"
        can_generate = True
    except (ImportError, OSError) as err:
        results["weasyprint"] = f"absent (generation only: {err})"
        can_generate = False
    for binary, purpose in _OPTIONAL_BINARIES.items():
        found = shutil.which(binary)
        results[binary] = "ok" if found else f"absent (optional: {purpose})"
    return results, ok, can_generate


def run_doctor(paths: OrgPaths | None = None) -> int:
    results, ok, can_generate = probe()
    for name, value in results.items():
        print(f"  {name:<12} {value}")

    # Effort is reported but never recorded in `probes`: probes describe
    # what this machine can do, and re-probing a frozen fixture must not
    # rewrite its state.json with the effort of whoever ran doctor. The
    # authoritative record is the per-batch generator, written at ingest.
    effort_line, effort_ok = effort_report()
    print(f"  {'effort':<12} {effort_line}")

    if paths is not None and paths.meta_dir.exists():
        state = load_state(paths)
        state.probes = results
        save_state(paths, state)
        print(f"doctor: probes recorded in {paths.state_json}")
    print(f"doctor: {'ok' if ok else 'REQUIRED CAPABILITIES MISSING'}")
    if ok and not can_generate:
        # A scope report, not a failure. Validating and scoring the
        # committed fleet is a first-class use of this install and needs no
        # rendering stack; say what is unavailable and why.
        print(
            "doctor: generation not available (WeasyPrint/Pango missing). "
            "Validating and scoring committed orgs works; rendering a new "
            "one does not."
        )
    if not effort_ok:
        # A warning, not a failure: the floor is advisory and authoring is
        # still the user's call. Exit code stays keyed to capabilities.
        print(
            "doctor: WARNING effort is below the authoring floor; "
            "generated prose will track it"
        )
    return 0 if ok else 1
