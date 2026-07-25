#!/usr/bin/env bash
# Apply "NeuroVault add-ons by Stel" onto the current NeuroVault checkout.
# Run from INSIDE a NeuroVault git checkout:  bash <path>/apply.sh
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# -e, not -d: in a git worktree `.git` is a file pointing at the real
# gitdir, and a -d test would reject a perfectly valid checkout.
if [ ! -e .git ]; then
  echo "Run this from inside a NeuroVault git checkout (no .git found here)." >&2
  exit 1
fi

echo "Applying add-on commits (git am -3)..."
if ! git am -3 "$here"/patches/*.patch; then
  echo "A patch conflicted. Resolve it, 'git add -A', then 'git am --continue' (or 'git am --abort')." >&2
  exit 1
fi

# No local-tweaks step any more: as of the v0.6.0 rebase every add-on is a
# real commit, so the patches above carry the launcher, the skills and the
# python helpers too.

echo
echo "Done. Build with:  npm install && npm run tauri build"
