from __future__ import annotations

"""Clean an existing brain's INDEX without touching the SSD backup.

A brain's vault holds two things side by side:
  * `_source_files/<project>/...`        — the raw backup (everything copied)
  * `*.neurovault.md` sidecars + `.md`   — what NeuroVault actually INDEXES

Over time a brain can get bloated with sidecars for files that are not real
knowledge — per-post screenshots, thumbnails, bulk machine-data JSON — which
blow up the note/chunk count and make the graph view unusable. This tool finds
those sidecars (using the SAME rules the importer now uses to decide what to
back-up-but-not-index: `INDEX_EXCLUDE_DIRS` + the project's `.neurovaultignore`)
and DELETES ONLY THE SIDECARS. The raw files stay on the SSD, fully backed up.

After running this, trigger `/api/update` for the brain so the app soft-deletes
the now-missing sidecar notes; the brain shrinks to just its real knowledge.

Usage:
  python scripts/clean_brain_index.py --brain-id competitor-insights-pwc --dry-run
  python scripts/clean_brain_index.py --brain-id competitor-insights-pwc
"""

import argparse
import json
from pathlib import Path

from import_project_vault import (
    INDEX_EXCLUDE_DIRS,
    NO_INDEX_FILE,
    is_index_excluded,
    load_no_index_patterns,
)

SIDECAR_SUFFIXES = (".neurovault.md", ".neurovault.html")


def _is_sidecar(path: Path) -> bool:
    return path.name.lower().endswith(SIDECAR_SUFFIXES)


def scan_brain(vault: Path, extra_patterns: list[str] | None = None) -> dict:
    """Find sidecars that index backup-only files (screenshots/thumbs/.neurovaultignore).
    Returns the list of sidecars to remove + the raw bytes that stay backed up.
    `extra_patterns` are merged on top of each project's own .neurovaultignore — use it
    to apply the LIVE source's ignore rules before they've been re-imported."""
    extra_patterns = extra_patterns or []
    source_root = vault / "_source_files"
    targets: list[dict] = []
    if not source_root.is_dir():
        return {"targets": targets, "projects": []}

    projects = [p for p in source_root.iterdir() if p.is_dir()]
    for project in projects:
        patterns = load_no_index_patterns(project) + extra_patterns
        for raw in project.rglob("*"):
            if not raw.is_file() or _is_sidecar(raw):
                continue
            rel = raw.relative_to(project).as_posix()
            if not is_index_excluded(rel, patterns):
                continue
            # The importer names the sidecar "<original name>.neurovault.md".
            sidecar = raw.with_name(raw.name + ".neurovault.md")
            if sidecar.is_file():
                targets.append(
                    {
                        "project": project.name,
                        "raw": rel,
                        "sidecar": sidecar.relative_to(vault).as_posix(),
                        "raw_bytes": raw.stat().st_size,
                    }
                )
            elif raw.suffix.lower() == ".md":
                # A .md original is indexed directly (no sidecar). Removing it would
                # also remove the backup, so we never delete it — just flag it.
                targets.append(
                    {
                        "project": project.name,
                        "raw": rel,
                        "sidecar": "",
                        "raw_bytes": raw.stat().st_size,
                        "note": "indexed .md original — left in place (would lose backup)",
                    }
                )
    return {"targets": targets, "projects": [p.name for p in projects]}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="De-index backup-only junk (screenshots/thumbs/.neurovaultignore) from a brain, keeping the SSD backup."
    )
    parser.add_argument("--brain-id", required=True)
    parser.add_argument("--nv-home", default=r"D:\NEURO-VAULT-STORAGE\.neurovault")
    parser.add_argument("--dry-run", action="store_true", help="Report what would be removed; change nothing.")
    parser.add_argument("--source", help="Live project folder: read its .neurovaultignore and apply those rules now (before any re-import).")
    parser.add_argument("--pattern", action="append", default=[], help="Extra backup-only path/glob to de-index (repeatable).")
    args = parser.parse_args()

    nv_home = Path(args.nv_home)
    vault = nv_home / "brains" / args.brain_id / "vault"
    if not vault.is_dir():
        raise SystemExit(f"brain vault not found: {vault}")

    extra_patterns = list(args.pattern)
    if args.source:
        extra_patterns += load_no_index_patterns(Path(args.source))

    result = scan_brain(vault, extra_patterns)
    removable = [t for t in result["targets"] if t["sidecar"]]
    skipped_md = [t for t in result["targets"] if not t["sidecar"]]
    freed = sum(t["raw_bytes"] for t in removable)

    removed = 0
    if not args.dry_run:
        for t in removable:
            sidecar = vault / t["sidecar"]
            try:
                sidecar.unlink()
                removed += 1
            except FileNotFoundError:
                pass

    summary = {
        "brain_id": args.brain_id,
        "vault": str(vault),
        "projects": result["projects"],
        "index_exclude_dirs": sorted(INDEX_EXCLUDE_DIRS),
        "no_index_file": NO_INDEX_FILE,
        "sidecars_found": len(removable),
        "sidecars_removed": removed,
        "indexed_md_left_in_place": len(skipped_md),
        "raw_bytes_still_backed_up": freed,
        "dry_run": args.dry_run,
        "next_step": f'curl -s -X POST http://127.0.0.1:8765/api/update -H "Content-Type: application/json" -d \'{{"brain":"{args.brain_id}"}}\'  then poll /api/brains/{args.brain_id}/stats',
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
