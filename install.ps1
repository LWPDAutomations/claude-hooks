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

Get-ChildItem $HooksSource -File | Copy-Item -Destination $HooksTarget -Force

Write-Host "Hooks geinstalleerd in $HooksTarget" -ForegroundColor Green
Get-ChildItem $HooksTarget -File | ForEach-Object {
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

    $added = @()
    $skipped = @()

    # Merge elk event type (PreToolUse, Stop, etc.) uit het fragment
    foreach ($prop in $fragment.hooks.PSObject.Properties) {
        $eventName = $prop.Name
        $fragmentEntries = @($prop.Value)

        # Haal bestaande entries op voor dit event type
        $existingEntries = @()
        if ($settings.hooks.PSObject.Properties[$eventName]) {
            $existingEntries = @($settings.hooks.$eventName)
        }

        foreach ($entry in $fragmentEntries) {
            $entryJson = $entry | ConvertTo-Json -Depth 10 -Compress

            # Check of deze hook al bestaat (zelfde matcher + hooks combo)
            $duplicate = $false
            foreach ($existing in $existingEntries) {
                $existingJson = $existing | ConvertTo-Json -Depth 10 -Compress
                if ($entryJson -eq $existingJson) {
                    $duplicate = $true
                    break
                }
            }

            if ($duplicate) {
                $skipped += "$eventName (matcher: $($entry.matcher))"
            } else {
                $existingEntries += $entry
                $added += "$eventName (matcher: $($entry.matcher))"
            }
        }

        $settings.hooks | Add-Member -NotePropertyName $eventName -NotePropertyValue $existingEntries -Force
    }

    $settings | ConvertTo-Json -Depth 10 | Set-Content $SettingsFile -Encoding UTF8

    if ($added.Count -gt 0) {
        Write-Host "Settings bijgewerkt in $SettingsFile" -ForegroundColor Green
        foreach ($item in $added) {
            Write-Host "  + Toegevoegd: $item" -ForegroundColor Cyan
        }
    }
    if ($skipped.Count -gt 0) {
        foreach ($item in $skipped) {
            Write-Host "  = Overgeslagen (bestaat al): $item" -ForegroundColor DarkGray
        }
    }
    if ($added.Count -eq 0 -and $skipped.Count -eq 0) {
        Write-Host "Geen hook-configuratie om te mergen." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Installatie compleet!" -ForegroundColor Green
