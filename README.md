# Claude Code Hooks

Mijn persoonlijke Claude Code hooks collectie.

## Installeren

```powershell
git clone git@github.com:JOUW-USERNAME/claude-hooks.git
cd claude-hooks
powershell -ExecutionPolicy Bypass -File install.ps1
```

Kopieer daarna de inhoud van `settings-fragment.json` naar je `~/.claude/settings.json`.

## Hooks

- **notify.ps1** - Windows notificatie als Claude klaar is (Stop event)
