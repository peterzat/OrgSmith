"""The quality instrument: sample, measure, and record what the board said.

This package is the only part of OrgSmith that looks at whether the prose
is any good. It stays on the reporting side of the line:

- `review --sample` and `report` are pure Python over committed files. They
  call no model and touch no network, like every other verb.
- `review --ingest` is a validate-and-merge airlock verb of the same shape
  as `author --ingest`. The board itself is a skill (`/forge-review`);
  Python never invokes it, and no test tier may reach it.
- Nothing here gates. No validator rule references a metric, a finding, or
  a generator record.
"""

from .ingest import run_ingest as run_review_ingest
from .report import run_report
from .sample import run_sample

__all__ = ["run_review_ingest", "run_report", "run_sample"]
