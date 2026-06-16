# NeuroVault add-ons by Stel

Extra features layered on top of upstream **[NeuroVault](https://github.com/sirdath/NeuroVault)**.
If you already run stock NeuroVault, apply these patches to get everything in
Stel's build — SSD workflow, a static graph mode, per‑brain source folders with
full `/update-brain` parity, and more.

These are delivered as a **patch set** (not a fork): a series of
`git format-patch` files plus a small diff for a couple of uncommitted local
tweaks, and an install script that applies them onto a clean checkout.

> Base: the patches apply on top of upstream commit **`a9d5628`** (the v0.5.2
> line — "delete retired Python MCP proxy"). The install script uses 3‑way
> apply so they still land cleanly on nearby revisions.

---

## What's included

| # | Add‑on | What it does |
|---|--------|--------------|
| 0001 | **Preserve local customizations** | Baseline local tweaks (launcher, build settings, etc.). |
| 0002 | **SSD: auto‑open + loading splash** | When the external SSD with your brains is plugged in, NeuroVault auto‑opens with a loading splash. |
| 0003 | **SSD: reliable eject + loading ring** | A dependable eject button and an asymptotic loading ring. |
| 0004 | **Skills: `update-brain` + `update-neurovault-app`** | Two Claude‑Code skills: refresh project content into a brain on the SSD; and update the app to a new upstream release without losing these add‑ons. |
| 0005 | **Sortable brain list/grid** | Sort your vaults by name / date / note count. |
| 0006 | **Static graph mode + per‑brain source folders** | A third **Static** graph view (frozen layout, no physics — low CPU); and per‑brain configurable source folders that the brain mirrors. |
| 0007 | **Source folders: ignore build dirs + race fix** | Skips `node_modules`/`.git`/`dist`/build/cache dirs; tolerates the watcher ingest race. |
| 0008 | **Source folders: dry‑run preview + dedup** | "Sync" previews exactly what it will add/update/remove/skip before applying, and skips content already in the brain. |
| 0009 | **Source folders: shared `_source_files/` layout** | The in‑app Sync writes the **same** vault layout as `/update-brain`, so the two reconcile instead of duplicating. |
| 0010 | **Source folders: "Full import (code)" button** | Runs `/update-brain`'s own importer so the in‑app Sync imports **all** file types (code/binary → `.neurovault.md` sidecars), not just markdown. Needs Python. |
| 0011 | **UI: theme vars on `:root`** | Fixes portaled modals (the Source Folders panel) rendering transparent. |
| — | **`local-tweaks/`** | Uncommitted local edits: `src-tauri/src/lib.rs` tweaks, refinements to the `update-brain` skill, and the `_nv_staleness_check.py` helper. |

---

## Requirements

- A NeuroVault source checkout (git).
- **Node + Rust** to build the app (same as upstream).
- **Python 3** — only for the "Full import (code)" button and the `update-brain` skill (same dependency they've always had).

## How to apply

```bash
# 1. Clone upstream NeuroVault (or use your existing checkout)
git clone https://github.com/sirdath/NeuroVault.git
cd NeuroVault

# 2. (recommended) start from the base these patches target
git checkout a9d5628    # or stay on your branch; the scripts use 3-way apply

# 3. From inside the NeuroVault checkout, run the installer from this repo:
#    Windows:
pwsh -File /path/to/neurovault-addons-by-stel/apply.ps1
#    macOS/Linux:
bash   /path/to/neurovault-addons-by-stel/apply.sh
```

The installer:
1. `git am -3 patches/*.patch` — replays the 11 add‑on commits.
2. `git apply --3way local-tweaks/local-tweaks.diff` — applies the local tweaks.
3. Copies `local-tweaks/scripts/_nv_staleness_check.py` into `scripts/`.

Then build as usual: `npm install && npm run tauri dev` (or `tauri build`).

If a patch conflicts (because upstream moved), resolve it, `git add -A`, and
`git am --continue`.

---

*Generated from Stel's `custom/v052-with-local-tweaks` branch. Not affiliated
with the upstream project; provided as‑is.*
