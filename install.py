"""install.py - Cross-platform installer for Claude Code hooks.
Copies .py hook scripts to ~/.claude/hooks/ and merges hook config
from settings-fragment.json into ~/.claude/settings.json.
"""

import json
import os
import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
HOOKS_SOURCE = SCRIPT_DIR / "hooks"
SETTINGS_FRAGMENT = SCRIPT_DIR / "settings-fragment.json"

CLAUDE_DIR = Path.home() / ".claude"
HOOKS_TARGET = CLAUDE_DIR / "hooks"
SETTINGS_FILE = CLAUDE_DIR / "settings.json"

GREEN = "\033[92m"
CYAN = "\033[96m"
GRAY = "\033[90m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def install_hooks():
    """Copy .py hook scripts to ~/.claude/hooks/."""
    HOOKS_TARGET.mkdir(parents=True, exist_ok=True)

    installed = []
    for f in sorted(HOOKS_SOURCE.iterdir()):
        if f.is_file() and f.suffix == ".py":
            shutil.copy2(f, HOOKS_TARGET / f.name)
            installed.append(f.name)

    print(f"{GREEN}Hooks geinstalleerd in {HOOKS_TARGET}{RESET}")
    for name in installed:
        print(f"  {CYAN}- {name}{RESET}")

    return installed


def merge_settings():
    """Merge hook config from settings-fragment.json into ~/.claude/settings.json."""
    print()

    if not SETTINGS_FRAGMENT.exists():
        print(f"{YELLOW}Geen settings-fragment.json gevonden, settings overgeslagen.{RESET}")
        return

    fragment = json.loads(SETTINGS_FRAGMENT.read_text(encoding="utf-8-sig"))
    fragment_hooks = fragment.get("hooks", {})

    if not fragment_hooks:
        print(f"{YELLOW}Geen hook-configuratie in settings-fragment.json.{RESET}")
        return

    if not SETTINGS_FILE.exists():
        settings = {"hooks": fragment_hooks}
        SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        print(f"{GREEN}Nieuw settings.json aangemaakt met hook-configuratie.{RESET}")
        return

    settings = json.loads(SETTINGS_FILE.read_text(encoding="utf-8-sig"))

    if "hooks" not in settings:
        settings["hooks"] = {}

    added = []
    skipped = []

    for event_name, fragment_entries in fragment_hooks.items():
        existing_entries = settings["hooks"].get(event_name, [])

        # Serialize existing entries for comparison
        existing_json = {json.dumps(e, sort_keys=True) for e in existing_entries}

        for entry in fragment_entries:
            entry_json = json.dumps(entry, sort_keys=True)
            matcher = entry.get("matcher", "")

            if entry_json in existing_json:
                skipped.append(f"{event_name} (matcher: {matcher})")
            else:
                existing_entries.append(entry)
                existing_json.add(entry_json)
                added.append(f"{event_name} (matcher: {matcher})")

        settings["hooks"][event_name] = existing_entries

    SETTINGS_FILE.write_text(json.dumps(settings, indent=2), encoding="utf-8")

    if added:
        print(f"{GREEN}Settings bijgewerkt in {SETTINGS_FILE}{RESET}")
        for item in added:
            print(f"  {CYAN}+ Toegevoegd: {item}{RESET}")
    if skipped:
        for item in skipped:
            print(f"  {GRAY}= Overgeslagen (bestaat al): {item}{RESET}")
    if not added and not skipped:
        print(f"{YELLOW}Geen hook-configuratie om te mergen.{RESET}")


def main():
    install_hooks()
    merge_settings()
    print(f"\n{GREEN}Installatie compleet!{RESET}")


if __name__ == "__main__":
    main()
