"""fabric stage runner: finance + engagements + graph ledgers."""

from __future__ import annotations

from ..artifacts import load_charter, load_foundation
from ..paths import OrgPaths
from ..schemas import write_model
from ..state import load_state, require_stages, save_state, sha256_file
from .engagements import build_engagements
from .finance import build_finance
from .graph import build_graph


def run_fabric(paths: OrgPaths) -> int:
    state = load_state(paths)
    require_stages(state, "charter", "foundation")
    if paths.finance_json.exists() and paths.engagements_json.exists():
        print("fabric: ledgers exist, nothing to do")
        return 0

    charter = load_charter(paths)
    foundation = load_foundation(paths)

    finance = build_finance(charter)
    bad = [c for c in finance.checks if not c.ok]
    if bad:
        raise SystemExit(f"fabric: finance tie-out failed: {bad}")
    engagements = build_engagements(charter, foundation)
    graph = build_graph(charter, foundation, engagements)

    write_model(paths.finance_json, finance)
    write_model(paths.engagements_json, engagements)
    write_model(paths.graph_json, graph)

    state.mark_done("fabric", inputs_hash=sha256_file(paths.foundation_json))
    save_state(paths, state)
    print(
        f"fabric: {len(finance.years)} fiscal years, "
        f"{len(engagements.engagements)} engagements -> {paths.ledger_dir}"
    )
    return 0
