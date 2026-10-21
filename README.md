# Software Version Checker

**English** · [Nederlands](#nederlands)

Pro-audio and show-production software rarely updates itself. This page tells you
at a glance whether the version you run is still the latest one, and starts the
download for your system when it isn't.

Currently tracked: L-Acoustics Soundvision, L-Acoustics Network Manager,
Shure Wireless Workbench, Green-GO Control.

## Use it

**https://breugelmansd.github.io/software-version-checker/**

No install, no account, no terminal. Type the version you have installed next to
each application. It is remembered in your own browser only. When a newer version
exists, the **Update** button opens the vendor page and starts the download for
macOS or Windows (detected automatically). Phones get the vendor page only.

The "latest version" column is refreshed automatically every Monday by a GitHub
Action, so nobody has to maintain anything. If a vendor page can't be read one
week, the last known version stays visible with a note.

> **Soundvision:** the app's own About screen shows an internal build number
> (for example `3.19.1.2`), not the release number on the website (for example
> `2026.4`). Compare against the website's number.
>
> **Network Manager:** L-Acoustics only hands out this download after a form, so
> the button opens the download page instead of starting the file.

## Add or fix software

Open an [issue](https://github.com/BreugelmansD/software-version-checker/issues/new/choose)
with the vendor's download page, or send a pull request that adds an entry to
`apps.json`:

| field | meaning |
| --- | --- |
| `name`, `check_url` | what to show and which page to read |
| `version_regex` | matches the version number on that page (first capture group wins) |
| `mac_download_regex`, `win_download_regex` | optional: find a direct file link on the same page |
| `mac_download_static`, `win_download_static` | optional: a vendor link that always points to the latest file |

Test locally with `python3 check_versions.py --ci` (Python 3.9+, no packages needed);
it rewrites `latest.json`.

## Optional: desktop notification

If you also want a notification on your own computer, run the script locally:

```bash
git clone https://github.com/BreugelmansD/software-version-checker.git
cd software-version-checker
python3 check_versions.py --setup   # enter your installed versions once
./setup_macos.sh                    # macOS: weekly check, Monday 09:00
# Windows (PowerShell): ./setup_windows.ps1
```

## How it works

- `apps.json`: the shared catalogue of tracked software.
- `.github/workflows/update-latest.yml`: weekly job that runs `check_versions.py --ci` and commits `latest.json`.
- `index.html`: static page on GitHub Pages. It reads `latest.json` and compares it with the version you typed (stored in `localStorage`).
- `local_versions.json`: only for the optional local notification; git-ignored.

Not affiliated with L-Acoustics, Shure or Green-GO. Licensed under MIT.

---

## Nederlands

Software voor geluid en show heeft zelden een ingebouwde updater. Deze pagina toont
in één oogopslag of jouw versie nog de laatste is, en start de download voor jouw
systeem als dat niet zo is.

**Gebruik:** open **https://breugelmansd.github.io/software-version-checker/**, vul
naast elke applicatie de versie in die je hebt (enkel in jouw browser bewaard) en
klik op **Updaten** als er een nieuwere versie is. De pagina opent de leverancier
en start de download voor macOS of Windows. Geen installatie of account nodig.

De laatste versies worden elke maandag automatisch vernieuwd. Ontbreekt er software
of klopt iets niet? Maak een [issue](https://github.com/BreugelmansD/software-version-checker/issues/new/choose)
aan of stuur een pull request die `apps.json` uitbreidt.

Let op bij Soundvision: het About-scherm toont een intern buildnummer (bv. `3.19.1.2`),
niet het versienummer van de website (bv. `2026.4`). Bij Network Manager vraagt
L-Acoustics eerst een formulier, dus daar opent de knop enkel de downloadpagina.
