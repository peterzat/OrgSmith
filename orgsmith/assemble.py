"""assemble stage: wiki-style TOC over the rendered share."""

from __future__ import annotations

from urllib.parse import quote

from .artifacts import load_charter, load_manifest
from .paths import OrgPaths
from .state import load_state, require_stages, save_state


def run_assemble(paths: OrgPaths) -> int:
    state = load_state(paths)
    require_stages(state, "render")

    charter = load_charter(paths)
    manifest = load_manifest(paths)

    missing = [e.path for e in manifest if not (paths.share_dir / e.path).exists()]
    if missing:
        raise SystemExit(
            f"assemble: {len(missing)} manifest docs not rendered yet: "
            + ", ".join(missing[:3])
        )

    by_folder: dict[str, list] = {}
    for entry in manifest:
        folder = str(entry.path).rsplit("/", 1)[0] if "/" in entry.path else "."
        by_folder.setdefault(folder, []).append(entry)

    lines = [
        f"# {charter.name} — Document Index",
        "",
        f"{len(manifest)} documents. Everything in this share is synthetic;",
        "see the companion `-metadata` directory for ground truth.",
        "",
    ]
    for folder in sorted(by_folder):
        lines.append(f"## {folder}")
        lines.append("")
        for entry in sorted(by_folder[folder], key=lambda e: (e.date, e.path)):
            name = entry.path.rsplit("/", 1)[-1]
            link = quote(entry.path)
            lines.append(f"- [{name}]({link}) — {entry.date} ({entry.genre})")
        lines.append("")

    paths.share_dir.mkdir(parents=True, exist_ok=True)
    paths.toc_md.write_text("\n".join(lines), encoding="utf-8")

    state.mark_done("assemble")
    save_state(paths, state)
    print(f"assemble: TOC for {len(manifest)} docs -> {paths.toc_md}")
    return 0
