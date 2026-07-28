"""Out-of-airlock authoring drivers for OrgSmith.

This package lives OUTSIDE `orgsmith/` on purpose. The airlock rule
(CLAUDE.md) forbids code in `orgsmith/` from calling a model or touching the
network; that rule is what keeps the deterministic core pure and every
committed fixture reproducible. A provider-neutral authoring driver is the
exact opposite job: it reads a `WorkOrder` JSON, calls a model over the
network with a user-supplied token, and writes back a `Deliverable` JSON for
`orgsmith ... --ingest` to validate and merge. So it belongs here, in the
same structural position `bin/review-external.sh` occupies in zat.env
relative to that project's core.

The dependency is strictly one-way: this package imports the pure
`orgsmith.schemas` for validation; nothing in `orgsmith/` imports `drivers`.
Bring-your-own-token mode is off by default: with no provider selected the
driver is inert and `/forge` runs its normal forked-worker path.
"""
