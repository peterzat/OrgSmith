"""orgsmith status: pipeline state for humans and orchestrating skills."""

from __future__ import annotations

import json

from .artifacts import load_manifest
from .paths import OrgPaths
from .state import STAGES, load_state


def collect_status(paths: OrgPaths) -> dict:
    state = load_state(paths)
    stages = {name: state.stage(name).status for name in STAGES}

    docs = {"planned": 0, "authored": 0, "rendered": 0, "static": 0}
    if paths.manifest_jsonl.exists():
        manifest = load_manifest(paths)
        docs["planned"] = len(manifest)
        for entry in manifest:
            doc = state.doc(entry.doc_id)
            if entry.authoring == "static":
                docs["static"] += 1
            elif doc.authored_hash:
                docs["authored"] += 1
            if doc.rendered_hash:
                docs["rendered"] += 1

    return {
        "slug": paths.slug,
        "stages": stages,
        "docs": docs,
        "outstanding": dict(state.outstanding),
        # Concurrent author batches dispatched but not yet ingested. A resumed
        # /forge re-dispatches these (path + doc count) before emitting fresh
        # ones, so no in-flight batch is stranded across a killed session.
        "author_batches": {
            wo_id: {
                "workorder": str(paths.workorders_dir / ref.workorder),
                "docs": len(ref.doc_ids),
            }
            for wo_id, ref in state.author_batches.items()
        },
        "probes": dict(state.probes),
    }


def run_status(paths: OrgPaths, as_json: bool = False) -> int:
    status = collect_status(paths)
    if as_json:
        print(json.dumps(status, indent=2))
        return 0
    print(f"org: {status['slug']}")
    for name, stage_status in status["stages"].items():
        print(f"  {name:<18} {stage_status}")
    d = status["docs"]
    print(
        f"  docs: {d['planned']} planned, {d['authored']} authored "
        f"(+{d['static']} static), {d['rendered']} rendered"
    )
    for stage, wo in status["outstanding"].items():
        print(f"  outstanding {stage}: {wo}")
    for wo_id, ref in status["author_batches"].items():
        print(f"  outstanding author batch {wo_id}: {ref['docs']} docs")
    return 0
