# Apply "NeuroVault add-ons by Stel" onto the current NeuroVault checkout.
# Run from INSIDE a NeuroVault git checkout:  pwsh -File <path>\apply.ps1
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Test-Path ".git")) {
    Write-Error "Run this from inside a NeuroVault git checkout (no .git found here)."
    exit 1
}

$patches = Get-ChildItem "$here\patches\*.patch" | Sort-Object Name | ForEach-Object { $_.FullName }
Write-Host "Applying $($patches.Count) add-on commits (git am -3)..." -ForegroundColor Cyan
git am -3 @patches
if ($LASTEXITCODE -ne 0) {
    Write-Error "A patch conflicted. Resolve it, 'git add -A', then 'git am --continue' (or 'git am --abort')."
    exit 1
}

# No local-tweaks step any more: as of the v0.6.0 rebase every add-on is a
# real commit, so the patches above carry the launcher, the skills and the
# python helpers too.

Write-Host "`nDone. Build with:  npm install ; npm run tauri build" -ForegroundColor Green
