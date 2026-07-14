"""charter stage: parse and validate recipes/<slug>/ORG-CHARTER.md.

Pure. Extracts the fenced yaml block as structured fields and the
surrounding prose as the narrative brief, validates the Charter contract,
and writes companies/<slug>-metadata/charter.json.
"""

from __future__ import annotations

import re

import yaml

from .paths import OrgPaths
from .schemas import Charter, write_model
from .state import load_state, save_state, sha256_file

_YAML_BLOCK = re.compile(r"^```yaml\s*$(.*?)^```\s*$", re.MULTILINE | re.DOTALL)


def parse_charter_md(text: str, slug: str) -> Charter:
    match = _YAML_BLOCK.search(text)
    if not match:
        raise SystemExit("ORG-CHARTER.md has no fenced ```yaml block")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise SystemExit("charter yaml block must be a mapping")
    if "narrative" in data:
        raise SystemExit("narrative belongs in prose, not the yaml block")

    prose = (text[: match.start()] + text[match.end() :]).strip()
    prose = re.sub(r"^#\s+.*$", "", prose, count=1, flags=re.MULTILINE).strip()
    if not prose:
        raise SystemExit("ORG-CHARTER.md needs a narrative brief around the yaml block")
    data["narrative"] = prose

    charter = Charter(**data)
    if charter.slug != slug:
        raise SystemExit(
            f"charter slug {charter.slug!r} does not match recipe directory {slug!r}"
        )
    return charter


def run_charter(paths: OrgPaths) -> int:
    if not paths.charter_md.exists():
        raise SystemExit(f"no recipe at {paths.charter_md}")
    charter = parse_charter_md(paths.charter_md.read_text("utf-8"), paths.slug)
    write_model(paths.charter_json, charter)

    state = load_state(paths)
    state.mark_done("charter", inputs_hash=sha256_file(paths.charter_md))
    save_state(paths, state)
    print(f"charter: wrote {paths.charter_json}")
    return 0
