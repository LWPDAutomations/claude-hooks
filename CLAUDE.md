# Claude Code Hooks Repository

Dit is mijn persoonlijke verzameling Claude Code hooks.

## Projectstructuur

claude-hooks/
  hooks/          <- Alle hook-scripts komen HIER in
    *.py          <- Python scripts (cross-platform)
  install.py      <- Installeert hooks naar ~/.claude/hooks/
  settings-fragment.json  <- Hook-registraties voor settings.json
  README.md

## Regels

- ALLE hook-scripts MOETEN in de hooks/ map geschreven worden, NOOIT ergens anders
- Schrijf hooks als Python (.py) scripts (cross-platform)
- Hook-scripts lezen JSON van stdin via sys.stdin.read() en communiceren via exit codes (0 = ok, 2 = blokkeer)
- Gebruik print(..., file=sys.stderr) voor stderr output
- Bij het registreren van hooks in settings-fragment.json, gebruik dit pad-formaat: python "C:\Users\larsd\.claude\hooks\SCRIPTNAAM.py"
- Na het aanmaken of fixen van een hook: toon een test-commando zodat ik het handmatig kan testen
- Update ALTIJD settings-fragment.json als je een nieuwe hook toevoegt

## Na een succesvolle hook-wijziging

Als een hook is aangemaakt, gefixt, of gewijzigd en getest:

1. Draai `python install.py` om hooks te kopiëren naar ~/.claude/hooks/ en settings te mergen
2. Vraag mij of ik wil committen en pushen naar GitHub