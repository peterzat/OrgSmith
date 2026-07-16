"""orgsmith doctor: capability probe.

Probes never fail the run for optional capabilities (LibreOffice arrives
with a later milestone); they record what this machine can do so stages
can choose fallbacks and skills can warn early. Required Python deps
missing IS a failure.
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


def probe() -> tuple[dict[str, str], bool]:
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
    # WeasyPrint needs system Pango; importing it proves the text stack.
    try:
        importlib.import_module("weasyprint")
        results["weasyprint"] = "ok"
    except (ImportError, OSError) as err:
        results["weasyprint"] = f"MISSING ({err})"
        ok = False
    for binary, purpose in _OPTIONAL_BINARIES.items():
        found = shutil.which(binary)
        results[binary] = "ok" if found else f"absent (optional: {purpose})"
    return results, ok


def run_doctor(paths: OrgPaths | None = None) -> int:
    results, ok = probe()
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
    if not effort_ok:
        # A warning, not a failure: the floor is advisory and authoring is
        # still the user's call. Exit code stays keyed to capabilities.
        print(
            "doctor: WARNING effort is below the authoring floor; "
            "generated prose will track it"
        )
    return 0 if ok else 1
