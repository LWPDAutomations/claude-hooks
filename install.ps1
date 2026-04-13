# install.ps1 - Installeert Claude Code hooks globaal
$HooksSource = Join-Path $PSScriptRoot "hooks"
$HooksTarget = Join-Path $env:USERPROFILE ".claude\hooks"

# Maak doelmap aan als die niet bestaat
if (!(Test-Path $HooksTarget)) {
    New-Item -ItemType Directory -Path $HooksTarget -Force | Out-Null
}

# Kopieer alle hook-scripts
Copy-Item "$HooksSource\*" -Destination $HooksTarget -Force -Recurse

Write-Host "Hooks geinstalleerd in $HooksTarget" -ForegroundColor Green

# Toon wat er geinstalleerd is
Get-ChildItem $HooksTarget | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Let op: check of je ~/.claude/settings.json naar deze scripts verwijst." -ForegroundColor Yellow
