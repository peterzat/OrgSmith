"""Filesystem layout for one org: recipe in, share + metadata out.

Every stage resolves locations through OrgPaths; nothing else may build
paths under recipes/ or companies/ by hand.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OrgPaths:
    root: Path
    slug: str

    # --- input recipe ---
    @property
    def recipe_dir(self) -> Path:
        return self.root / "recipes" / self.slug

    @property
    def charter_md(self) -> Path:
        return self.recipe_dir / "ORG-CHARTER.md"

    # --- output: the browsable file share ---
    @property
    def share_dir(self) -> Path:
        return self.root / "companies" / self.slug

    @property
    def toc_md(self) -> Path:
        return self.share_dir / "TOC.md"

    @property
    def permissions_md(self) -> Path:
        return self.share_dir / "PERMISSIONS.md"

    # --- output: ground truth ---
    @property
    def meta_dir(self) -> Path:
        return self.root / "companies" / f"{self.slug}-metadata"

    @property
    def charter_json(self) -> Path:
        return self.meta_dir / "charter.json"

    @property
    def foundation_json(self) -> Path:
        return self.meta_dir / "foundation.json"

    @property
    def ledger_dir(self) -> Path:
        return self.meta_dir / "ledger"

    @property
    def finance_json(self) -> Path:
        return self.ledger_dir / "finance.json"

    @property
    def engagements_json(self) -> Path:
        return self.ledger_dir / "engagements.json"

    @property
    def graph_json(self) -> Path:
        return self.ledger_dir / "graph.json"

    @property
    def mention_map_json(self) -> Path:
        return self.ledger_dir / "mention_map.json"

    @property
    def acl_json(self) -> Path:
        return self.ledger_dir / "acl.json"

    @property
    def evals_dir(self) -> Path:
        return self.meta_dir / "evals"

    @property
    def docplan_dir(self) -> Path:
        return self.meta_dir / "docplan"

    @property
    def manifest_jsonl(self) -> Path:
        return self.docplan_dir / "manifest.jsonl"

    @property
    def docir_dir(self) -> Path:
        return self.meta_dir / "docir"

    @property
    def workorders_dir(self) -> Path:
        return self.meta_dir / "workorders"

    @property
    def state_json(self) -> Path:
        return self.meta_dir / "state.json"


def org_paths(slug: str, root: Path | None = None) -> OrgPaths:
    return OrgPaths(root=root or Path.cwd(), slug=slug)
