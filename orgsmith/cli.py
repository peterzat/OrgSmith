"""Command-line entry point: the stage verbs of python -m orgsmith.

Every verb is offline and deterministic. Verbs that pair with a model pass
(`foundation --emit-context/--ingest`, `author --next-batch/--ingest`)
never call a model themselves; they exchange JSON files with the skills
that do (the airlock).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from . import PRODUCT_NAME, __version__
from .paths import org_paths


def _add_slug(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("slug", help="recipe/org slug, e.g. dev-mini")
    sub.add_argument(
        "--root",
        type=Path,
        default=None,
        help="repo root (default: current directory)",
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="orgsmith",
        description=f"{PRODUCT_NAME}: generate synthetic organizations.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="verb", required=True)

    _add_slug(sub.add_parser("charter", help="parse recipe -> charter.json"))

    p_fnd = sub.add_parser("foundation", help="roster scaffold + enrichment airlock")
    _add_slug(p_fnd)
    g = p_fnd.add_mutually_exclusive_group(required=True)
    g.add_argument("--scaffold", action="store_true", help="deterministic roster")
    g.add_argument(
        "--emit-context", action="store_true", help="write enrichment work order"
    )
    g.add_argument("--ingest", metavar="FILE", help="merge enrichment deliverable")

    _add_slug(sub.add_parser("fabric", help="finance/engagements/graph ledgers"))
    _add_slug(sub.add_parser("docplan", help="immutable document manifest"))

    p_auth = sub.add_parser("author", help="authoring airlock (work orders/DocIR)")
    _add_slug(p_auth)
    g = p_auth.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--next-batch", action="store_true", help="write next authoring work order"
    )
    g.add_argument("--ingest", metavar="FILE", help="merge authoring deliverable")

    _add_slug(sub.add_parser("render", help="render DocIR + static docs to files"))
    _add_slug(sub.add_parser("assemble", help="TOC over the rendered share"))

    p_val = sub.add_parser("validate", help="deterministic org lint")
    p_val.add_argument("target", help="slug or companies/<slug> path")
    p_val.add_argument("--root", type=Path, default=None)
    p_val.add_argument("--json", action="store_true", dest="as_json")
    p_val.add_argument("--only", help="comma-separated rule ids")

    _add_slug(sub.add_parser("emit-evals", help="golden eval suites from ground truth"))

    p_score = sub.add_parser("score", help="grade external answers against evals")
    p_score.add_argument("slug", nargs="?", help="org slug (or use --evals-dir)")
    p_score.add_argument("--root", type=Path, default=None)
    p_score.add_argument("--suite", required=True, choices=["retrieval", "graph"])
    p_score.add_argument("--answers", required=True, metavar="FILE")
    p_score.add_argument(
        "--evals-dir",
        type=Path,
        default=None,
        help="score from a bare evals directory (no org needed)",
    )
    p_score.add_argument("--json", action="store_true", dest="as_json")

    p_status = sub.add_parser("status", help="pipeline status from state.json")
    _add_slug(p_status)
    p_status.add_argument("--json", action="store_true", dest="as_json")

    p_doc = sub.add_parser("doctor", help="capability probe")
    p_doc.add_argument("slug", nargs="?", help="record results into this org's state")
    p_doc.add_argument("--root", type=Path, default=None)

    args = parser.parse_args(argv)

    if args.verb == "validate":
        target = args.target
        if "/" in target:
            slug = Path(target).name
            if slug.endswith("-metadata"):
                slug = slug[: -len("-metadata")]
        else:
            slug = target
        paths = org_paths(slug, args.root)
        from .validate import run_validate

        only = args.only.split(",") if args.only else None
        return run_validate(paths, as_json=args.as_json, only=only)

    if args.verb == "doctor":
        from .doctor import run_doctor

        paths = org_paths(args.slug, args.root) if args.slug else None
        return run_doctor(paths)

    if args.verb == "score":
        from .evals import run_score

        if args.evals_dir is not None:
            evals_dir = args.evals_dir
        elif args.slug:
            evals_dir = org_paths(args.slug, args.root).evals_dir
        else:
            parser.error("score needs a slug or --evals-dir")
        return run_score(
            evals_dir, args.suite, Path(args.answers), as_json=args.as_json
        )

    paths = org_paths(args.slug, args.root)

    if args.verb == "charter":
        from .charter import run_charter

        return run_charter(paths)
    if args.verb == "foundation":
        if args.scaffold:
            from .foundation import run_scaffold

            return run_scaffold(paths)
        if args.emit_context:
            from .foundation.contexts import run_emit_context

            return run_emit_context(paths)
        from .foundation.ingest import run_ingest

        return run_ingest(paths, Path(args.ingest))
    if args.verb == "fabric":
        from .fabric import run_fabric

        return run_fabric(paths)
    if args.verb == "docplan":
        from .docplan import run_docplan

        return run_docplan(paths)
    if args.verb == "author":
        if args.next_batch:
            from .authoring.contexts import run_next_batch

            return run_next_batch(paths)
        from .authoring.ingest import run_ingest

        return run_ingest(paths, Path(args.ingest))
    if args.verb == "render":
        from .render import run_render

        return run_render(paths)
    if args.verb == "assemble":
        from .assemble import run_assemble

        return run_assemble(paths)
    if args.verb == "emit-evals":
        from .evals import run_emit_evals

        return run_emit_evals(paths)
    if args.verb == "status":
        from .status import run_status

        return run_status(paths, as_json=args.as_json)

    parser.error(f"unhandled verb {args.verb}")
    return 2
