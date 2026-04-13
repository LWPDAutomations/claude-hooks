# Claude Code Hooks

Mijn persoonlijke Claude Code hooks collectie.

## Installeren

```powershell
git clone https://github.com/LWPDAutomations/claude-hooks.git
cd claude-hooks
powershell -ExecutionPolicy Bypass -File install.ps1
```

Het install-script kopieert de hook-scripts naar `~/.claude/hooks/` en merged de hook-configuratie uit `settings-fragment.json` automatisch in `~/.claude/settings.json`.

## Hooks

- **notify.ps1** - Windows notificatie als Claude klaar is (Stop event)
- **secret-scanner.ps1** - Blokkeert writes die API keys, tokens of andere secrets bevatten (PreToolUse event)
- **syntax_checker.py** - Checkt syntax van geschreven bestanden: .py, .json, .js/.jsx, .yaml/.yml (PostToolUse event)
