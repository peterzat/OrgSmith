"""Unit tier: concurrent writers cannot lose a state.json update (M17d).

`/forge` keeps the merge race-free by running every `--ingest` itself, one at
a time, and telling its parallel workers never to ingest. That held as a rule
in a prompt. These tests pin the code half: every state-writing CLI verb runs
under `state_lock`, so concurrent ingests into one org all land.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

from orgsmith.artifacts import load_work_order
from orgsmith.authoring.contexts import run_next_batch
from orgsmith.state import load_state, state_lock

from conftest import build_pure_stages, committed_outlines, run_enrichment, scripted_authoring

pytestmark = pytest.mark.unit

REPO = Path(__file__).resolve().parent.parent


def _emit_all(paths):
    prev = -1
    while True:
        assert run_next_batch(paths) == 0
        n = len(load_state(paths).author_batches)
        if n == prev:
            return load_state(paths).author_batches
        prev = n


def test_concurrent_ingests_all_land(tmp_path):
    paths = build_pure_stages(tmp_path)
    run_enrichment(paths)
    batches = _emit_all(paths)
    assert len(batches) >= 3, "the race needs several outstanding batches"

    replies = []
    outlines = committed_outlines(paths)
    for wo_id, ref in batches.items():
        wo = load_work_order(paths.workorders_dir / ref.workorder)
        reply = paths.workorders_dir / f"reply-{wo_id.replace(':', '-')}.json"
        reply.write_text(json.dumps(scripted_authoring(wo, outlines)))
        replies.append(reply)

    procs = [
        subprocess.Popen(
            [sys.executable, "-m", "orgsmith", "author", paths.slug,
             "--ingest", str(r), "--root", str(tmp_path)],
            cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        for r in replies
    ]
    outputs = [p.communicate(timeout=300)[0] for p in procs]
    assert all(p.returncode == 0 for p in procs), outputs

    state = load_state(paths)
    assert state.author_batches == {}, "an ingested batch was lost from state"
    claimed = [d for ref in batches.values() for d in ref.doc_ids]
    assert all(state.doc(d).authored_hash for d in claimed), (
        "a concurrent ingest saved over a sibling's authored hashes"
    )
    assert state.stage_done("author")


def test_a_held_lock_makes_a_second_writer_wait(tmp_path):
    paths = build_pure_stages(tmp_path)
    holder = subprocess.Popen(
        [sys.executable, "-c",
         "import sys, time\n"
         "from pathlib import Path\n"
         "from orgsmith.paths import org_paths\n"
         "from orgsmith.state import state_lock\n"
         f"p = org_paths({paths.slug!r}, Path({str(tmp_path)!r}))\n"
         "with state_lock(p):\n"
         "    print('held', flush=True)\n"
         "    time.sleep(1.5)\n"],
        cwd=REPO, stdout=subprocess.PIPE, text=True,
    )
    assert holder.stdout.readline().strip() == "held"
    started = time.monotonic()
    with state_lock(paths):
        waited = time.monotonic() - started
    holder.wait(timeout=30)
    assert waited > 0.5, f"the second writer did not wait ({waited:.2f}s)"


def test_the_lock_is_reentrant_within_one_process(tmp_path):
    paths = build_pure_stages(tmp_path)
    with state_lock(paths):
        with state_lock(paths):
            pass
    # And released afterwards: a fresh acquire returns at once.
    with state_lock(paths):
        pass


def test_no_lock_file_lands_in_the_org(tmp_path):
    paths = build_pure_stages(tmp_path)
    before = sorted(p.name for p in paths.meta_dir.iterdir())
    with state_lock(paths):
        pass
    assert sorted(p.name for p in paths.meta_dir.iterdir()) == before
