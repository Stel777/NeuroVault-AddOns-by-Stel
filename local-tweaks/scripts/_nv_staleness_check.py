"""Read-only staleness check: how far behind is a brain's clone vs the working folder?
Reuses the same skip rules + needs_copy logic as thesis_incremental_refresh.py.
Usage: python _nv_staleness_check.py "<SOURCE_ROOT>" "<DEST_ROOT>"
"""
from __future__ import annotations
import hashlib, os, sys
from pathlib import Path

SKIP_DIRS = {".git", ".claude", "__pycache__", "node_modules", ".venv", "venv", "dist", "build", "target"}
SKIP_SUFFIXES = (".neurovault.md", ".neurovault.html", ".mammoth.html")

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def iter_source_files(root: Path):
    files = []
    for d, dirs, names in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for n in names:
            if n.startswith("~$") or n.endswith(SKIP_SUFFIXES):
                continue
            files.append(Path(d) / n)
    return files

def needs_copy(src: Path, dst: Path) -> bool:
    if not dst.exists():
        return True
    s, d = src.stat(), dst.stat()
    if s.st_size == d.st_size and abs(s.st_mtime - d.st_mtime) <= 2:
        return False
    return sha256_file(src) != sha256_file(dst)

def main():
    source = Path(sys.argv[1]); dest = Path(sys.argv[2])
    new, changed, total = [], [], 0
    for src in iter_source_files(source):
        total += 1
        dst = dest / src.relative_to(source)
        if not dst.exists():
            new.append(src.relative_to(source).as_posix())
        elif needs_copy(src, dst):
            changed.append(src.relative_to(source).as_posix())
    print(f"Working-folder files scanned: {total}")
    print(f"NEW (never synced): {len(new)}")
    print(f"CHANGED since last sync: {len(changed)}")
    print(f"=> Brain is {'OUTDATED' if (new or changed) else 'UP TO DATE'} ({len(new)+len(changed)} files behind)")
    def show(label, items):
        if items:
            print(f"\n--- {label} ({len(items)}) ---")
            for x in sorted(items)[:40]:
                print("  " + x)
            if len(items) > 40:
                print(f"  ... +{len(items)-40} more")
    show("NEW", new); show("CHANGED", changed)

if __name__ == "__main__":
    main()
