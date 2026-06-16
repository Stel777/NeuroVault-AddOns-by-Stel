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

Write-Host "Applying local tweaks..." -ForegroundColor Cyan
git apply --3way "$here\local-tweaks\local-tweaks.diff"

$dst = "scripts"
if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Path $dst | Out-Null }
Copy-Item "$here\local-tweaks\scripts\_nv_staleness_check.py" "$dst\_nv_staleness_check.py" -Force

Write-Host "`nDone. Build with:  npm install ; npm run tauri dev" -ForegroundColor Green
