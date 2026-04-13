# Claude Code Hooks Repository

Dit is mijn persoonlijke verzameling Claude Code hooks.

## Projectstructuur

claude-hooks/
  hooks/          <- Alle hook-scripts komen HIER in
    *.ps1         <- PowerShell scripts (Windows)
  install.ps1     <- Installeert hooks naar ~/.claude/hooks/
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

1. Draai install.ps1 om hooks te kopiëren naar ~/.claude/hooks/
2. Merge de hook-config uit settings-fragment.json naar ~/.claude/settings.json
3. Vraag mij of ik wil committen en pushen naar GitHub