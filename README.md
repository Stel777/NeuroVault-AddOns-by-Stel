# NeuroVault add-ons by Stel

Local add-ons layered on top of upstream **[NeuroVault](https://github.com/sirdath/NeuroVault)**.
Delivered as a **patch set** (not a fork): `git format-patch` files plus a small
install script that replays them onto a clean checkout.

> Base: these patches apply on top of upstream **`v0.6.0`**.
> The install script uses 3-way apply so they still land on nearby revisions.

---

## What's included

| # | Add-on | What it does |
|---|--------|--------------|
| 0001 | **SSD brain workflow** | Finds the brain store on an external SSD by its `NEURO-VAULT-STORAGE\.neurovault\brains.json` marker instead of a hardcoded drive letter, so the app, `neurovault-server` and the MCP forwarder all follow the drive wherever it mounts. Adds the **Eject SSD Brain** button + `nv_eject_ssd_brain` (flush WAL, drop the mmap, hand off to an elevated eject task). Makes **closing the window quit the app** so the drive is actually released. Ships the launcher, auto-open watcher, loading splash, eject/registration scripts, the `update-brain` + `update-neurovault-app` Claude skills, and the python vault helpers. |
| 0002 | **"Full import (code)" button** | Runs the `/update-brain` importer over every configured source folder, so **all** file types come into the vault (code/html/binary become `.neurovault.md` sidecars) rather than markdown only. Needs Python on PATH. Complements upstream's "Index code", which reads code *structure* into the graph without importing the files. |
| 0003 | **Readable vault dropdown** | Pins `color-scheme` on the sidebar's native vault `<select>` so its OS-drawn option list stops rendering near-white text on a white background under light appearances. (Superseded in practice by 0005, which removes that `<select>` entirely; kept so the set applies in order.) |
| 0004 | **Grid view for the vault manager** | Re-adds the list/grid toggle upstream dropped. Grid widens the panel and tiles the vaults in auto-fill columns, which is the difference between browsing and scrolling once you have 30+. Persisted next to the sort key. |
| 0005 | **Real vault picker in the sidebar** | Replaces the native `<select>` with the app's own picker, so the list is drawn by the app (always legible) and brings sort + list/grid into the sidebar. Adds `tone`, `onSwitch` and `disabled` props so the sidebar keeps its own guarded switch flow: leave vault-scoped views first, respect a note that will not save, lock while activating. |

### Why this set is so much smaller than the v0.5.2 one

Upstream **absorbed most of the old add-ons** in v0.6.0, so they are no longer
carried here:

| previously a local patch | status in v0.6.0 |
|---|---|
| per-brain source folders, ignore build dirs, `_source_files` layout, dry-run preview | shipped upstream (`446847f`) |
| sortable brain list / grid | shipped upstream |
| static graph mode | absorbed — upstream's `2d`/`3d` are pinned-coordinate snapshots with no physics loop |
| theme vars mirrored to `:root` | fixed upstream in `applyThemeToDocument` |
| WAL checkpoint + close DBs on exit | implemented upstream, explicitly for unmounting an external drive |
| window-rebuild fix (closed window could not be reopened) | unnecessary — upstream prevents the close that destroyed the window |

There is no longer a `local-tweaks/` directory: everything is a real commit.

## Requirements

- A NeuroVault source checkout (git).
- **Node + Rust** to build the app (same as upstream).
- **Python 3** — only for the "Full import (code)" button and the `update-brain`
  skill (same dependency they have always had).

## How to apply

```bash
# 1. Clone upstream NeuroVault (or use your existing checkout)
git clone https://github.com/sirdath/NeuroVault.git
cd NeuroVault

# 2. (recommended) start from the base these patches target
git checkout v0.6.0        # or stay on your branch; the scripts use 3-way apply

# 3. From inside the NeuroVault checkout, run the installer from this repo:
#    Windows:
pwsh -File /path/to/neurovault-addons-by-stel/apply.ps1
#    macOS/Linux:
bash   /path/to/neurovault-addons-by-stel/apply.sh
```

The installer replays the add-on commits with `git am -3`.

Then build as usual: `npm install && npm run tauri build`.

If a patch conflicts (because upstream moved), resolve it, `git add -A`, and
`git am --continue`.

> **Do not use the in-app "Update to vX" button.** It installs the stock
> upstream binary over your build, which silently removes every add-on above —
> the first symptom is an empty brain, because SSD detection is one of them.
> Update the source checkout and rebuild instead.

---

*Generated from Stel's `custom/v060-with-local-tweaks` branch. Not affiliated
with the upstream project; provided as-is.*
