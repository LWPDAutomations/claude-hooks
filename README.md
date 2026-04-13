# Claude Code Hooks

Mijn persoonlijke Claude Code hooks collectie.

## Installeren

```bash
git clone https://github.com/LWPDAutomations/claude-hooks.git
cd claude-hooks
python install.py
```

Het install-script kopieert de `.py` hook-scripts naar `~/.claude/hooks/` en merged de hook-configuratie uit `settings-fragment.json` automatisch in `~/.claude/settings.json`. Werkt op Windows, macOS en Linux.

## Hooks

- **notify.py** - Desktop notificatie als Claude klaar is, cross-platform: Windows/macOS/Linux (Stop event)
- **secret_scanner.py** - Blokkeert writes die API keys, tokens of andere secrets bevatten (PreToolUse event)
- **syntax_checker.py** - Checkt syntax van geschreven bestanden: .py, .json, .js/.jsx, .yaml/.yml (PostToolUse event)

De `.ps1` versies van notify en secret-scanner zijn nog aanwezig als backup.
