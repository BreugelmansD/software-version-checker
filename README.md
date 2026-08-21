# Software Version Checker

Checkt of er een nieuwe versie is van software die geen in-app updater heeft
(L-Acoustics Soundvision, L-Acoustics Network Manager, Shure Wireless Workbench,
Green-GO Control) en toont dat in een lokaal dashboard.

Iedereen in het bedrijf gebruikt dezelfde app-catalogus (`apps.json`), maar houdt
zijn eigen geïnstalleerde versies lokaal bij (`local_versions.json`) — dat bestand
wordt niet gedeeld via git, want elke laptop heeft mogelijk een andere versie
geïnstalleerd.

## Vereisten

- Python 3.9 of hoger (macOS heeft dit standaard; Windows: installeer via
  [python.org](https://www.python.org/downloads/) — vink "Add python.exe to PATH" aan).
- Geen extra packages nodig.

## Installatie

```bash
git clone https://github.com/BreugelmansD/software-version-checker.git
cd software-version-checker
```

Of: download de repo als zip via de groene "Code" knop op GitHub en pak uit.

## Eerste gebruik

Vul één keer in welke versie je nu van elke applicatie hebt geïnstalleerd:

```bash
python3 check_versions.py --setup
```

Daarna controleren:

```bash
python3 check_versions.py
```

Dit genereert `dashboard.html` — open dat bestand in je browser voor het overzicht.
Op macOS/Windows kan je ook gewoon dubbelklikken op **"Check Updates.command"**
(macOS) of **"Check Updates.bat"** (Windows) in de projectmap — dat controleert
en opent meteen het dashboard.

In het dashboard klik je bij een update op **"Updaten →"**: dat opent de
productpagina van de leverancier én start, waar mogelijk, meteen de download
voor jouw besturingssysteem (macOS/Windows wordt automatisch herkend).

> **Let op — Soundvision:** de app zelf toont in het "About"-scherm een intern
> buildnummer (bv. `3.19.1.2`) dat losstaat van het marketingversienummer op de
> website (bv. `2026.3.1`). Gebruik dus de website of `--setup` als referentie,
> niet het "About"-scherm.

## Automatisch elke week controleren

**macOS:**
```bash
./setup_macos.sh
```
Installeert een launchd-taak die elke maandag 09:00 controleert en (bij een
update) een macOS-melding stuurt.

**Windows** (PowerShell, als gewone gebruiker):
```powershell
./setup_windows.ps1
```
Installeert een Taakplanner-taak die elke maandag 09:00 controleert.

## Je eigen geïnstalleerde versie aanpassen

```bash
python3 check_versions.py --set "Shure Wireless Workbench (WWB)" 7.8.3
```
of opnieuw `--setup` draaien.

## Een applicatie toevoegen aan de catalogus

Voeg een item toe aan `apps.json` met `name`, `check_url` en een `version_regex`
die het versienummer op die pagina matcht (optioneel `mac_download_regex` /
`win_download_regex` voor rechtstreekse downloads). Maak hiervoor een pull
request zodat iedereen de nieuwe app ziet.
