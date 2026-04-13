# install.ps1 - Installeert Claude Code hooks globaal
$ErrorActionPreference = "Stop"

$HooksSource = Join-Path $PSScriptRoot "hooks"
$HooksTarget = Join-Path $env:USERPROFILE ".claude\hooks"
$SettingsFragment = Join-Path $PSScriptRoot "settings-fragment.json"
$SettingsFile = Join-Path $env:USERPROFILE ".claude\settings.json"

# --- Stap 1: Kopieer hook-scripts ---

if (!(Test-Path $HooksTarget)) {
    New-Item -ItemType Directory -Path $HooksTarget -Force | Out-Null
}

Copy-Item "$HooksSource\*" -Destination $HooksTarget -Force -Recurse

Write-Host "Hooks geinstalleerd in $HooksTarget" -ForegroundColor Green
Get-ChildItem $HooksTarget | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor Cyan
}

# --- Stap 2: Merge hook-config in settings.json ---

Write-Host ""

if (!(Test-Path $SettingsFragment)) {
    Write-Host "Geen settings-fragment.json gevonden, settings overgeslagen." -ForegroundColor Yellow
    exit 0
}

$fragment = Get-Content $SettingsFragment -Raw | ConvertFrom-Json

if (!(Test-Path $SettingsFile)) {
    # Geen bestaande settings: schrijf fragment als basis
    $result = @{ hooks = $fragment.hooks }
    $result | ConvertTo-Json -Depth 10 | Set-Content $SettingsFile -Encoding UTF8
    Write-Host "Nieuw settings.json aangemaakt met hook-configuratie." -ForegroundColor Green
} else {
    $settings = Get-Content $SettingsFile -Raw | ConvertFrom-Json

    if (-not $settings.hooks) {
        $settings | Add-Member -NotePropertyName "hooks" -NotePropertyValue @{} -Force
    }

    $changed = @()

    # Merge elk event type (PreToolUse, Stop, etc.) uit het fragment
    foreach ($prop in $fragment.hooks.PSObject.Properties) {
        $eventName = $prop.Name
        $fragmentHooks = $prop.Value

        $settings.hooks | Add-Member -NotePropertyName $eventName -NotePropertyValue $fragmentHooks -Force
        $changed += $eventName
    }

    $settings | ConvertTo-Json -Depth 10 | Set-Content $SettingsFile -Encoding UTF8

    if ($changed.Count -gt 0) {
        Write-Host "Settings bijgewerkt in $SettingsFile" -ForegroundColor Green
        foreach ($evt in $changed) {
            Write-Host "  - Hook event gemerged: $evt" -ForegroundColor Cyan
        }
    } else {
        Write-Host "Geen hook-configuratie om te mergen." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Installatie compleet!" -ForegroundColor Green
