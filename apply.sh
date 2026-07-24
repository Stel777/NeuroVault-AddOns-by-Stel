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

echo "Applying local tweaks..."
git apply --3way "$here/local-tweaks/local-tweaks.diff"

mkdir -p scripts
# Copy every helper in local-tweaks/scripts/, so dropping a new one in
# there is enough to ship it — this script never needs editing again.
cp "$here"/local-tweaks/scripts/*.py scripts/

echo
echo "Done. Build with:  npm install && npm run tauri dev"
