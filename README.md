# Software Version Checker

Toont of er een nieuwe versie is van software die geen in-app updater heeft
(L-Acoustics Soundvision, L-Acoustics Network Manager, Shure Wireless Workbench,
Green-GO Control).

## Voor collega's: gewoon de link openen

**https://breugelmansd.github.io/software-version-checker/**

Geen installatie, geen terminal, geen git nodig. Vul bij "Jouw versie" eenmalig
in welke versie je nu hebt geïnstalleerd — dat wordt in je eigen browser
onthouden (niet gedeeld met anderen). Zodra er een update beschikbaar is,
klik je op **"Updaten →"**: dat opent de productpagina van de leverancier én
start, waar mogelijk, meteen de download voor jouw besturingssysteem
(macOS/Windows wordt automatisch herkend).

De "laatste versie"-kolom wordt wekelijks automatisch vernieuwd door GitHub
zelf — daarvoor moet niemand iets doen.

> **Let op — Soundvision:** de app zelf toont in het "About"-scherm een intern
> buildnummer (bv. `3.19.1.2`) dat losstaat van het marketingversienummer op de
> website (bv. `2026.3.1`). Gebruik de website als referentie voor "jouw versie",
> niet het "About"-scherm.

## Optioneel/geavanceerd: lokale desktop-melding

Wil je zelf ook automatisch een melding op je bureaublad krijgen (macOS/Windows)
zodra er een update is, naast de gedeelde webpagina? Dat kan met hetzelfde
script, lokaal:

```bash
git clone https://github.com/BreugelmansD/software-version-checker.git
cd software-version-checker
python3 check_versions.py --setup     # eenmalig: jouw geïnstalleerde versies
```

**macOS** — installeert een wekelijkse achtergrondcontrole (elke maandag 09:00):
```bash
./setup_macos.sh
```

**Windows** (PowerShell):
```powershell
./setup_windows.ps1
```

## Een applicatie toevoegen aan de catalogus

Voeg een item toe aan `apps.json` met `name`, `check_url` en een `version_regex`
die het versienummer op die pagina matcht (optioneel `mac_download_regex` /
`win_download_regex` voor rechtstreekse downloads). Maak hiervoor een pull
request zodat iedereen de nieuwe app op de gedeelde pagina ziet.

## Hoe het werkt

- `apps.json` — gedeelde catalogus van te checken software (in git).
- `.github/workflows/update-latest.yml` — GitHub Action die wekelijks
  `check_versions.py --ci` draait en het resultaat opslaat in `latest.json`.
- `index.html` — statische pagina (gehost via GitHub Pages) die `latest.json`
  ophaalt en, samen met jouw versie uit `localStorage`, de status per app
  berekent en toont.
- `local_versions.json` — enkel voor de optionele lokale desktop-melding;
  wordt niet gedeeld (staat in `.gitignore`).
