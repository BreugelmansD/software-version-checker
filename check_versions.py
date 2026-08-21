#!/usr/bin/env python3
"""Fetch the latest available version + download links for the shared app catalog.

Writes latest.json (public, committed to the repo, served by GitHub Pages
alongside index.html). This script runs on a schedule via GitHub Actions
(--ci flag), so nobody needs to install or run anything to see the shared
dashboard at the Pages URL.

Optional/advanced: if you want a desktop notification on your own machine
when an update appears, keep a local_versions.json (gitignored) with your
installed versions and run this script locally (see setup_macos.sh /
setup_windows.ps1).

Usage:
  python3 check_versions.py            # fetch + write latest.json, notify locally if configured
  python3 check_versions.py --ci       # fetch + write latest.json only, no local notification
  python3 check_versions.py --setup    # (optional) enter your installed version per app, for local notifications
  python3 check_versions.py --set "Shure Wireless Workbench (WWB)" 7.8.3
"""
import json
import platform
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
APPS_PATH = BASE_DIR / "apps.json"
LOCAL_VERSIONS_PATH = BASE_DIR / "local_versions.json"
LATEST_PATH = BASE_DIR / "latest.json"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def load_apps():
    return json.loads(APPS_PATH.read_text())["apps"]


def load_local_versions():
    if not LOCAL_VERSIONS_PATH.exists():
        return {}
    return json.loads(LOCAL_VERSIONS_PATH.read_text())


def save_local_versions(versions):
    LOCAL_VERSIONS_PATH.write_text(json.dumps(versions, indent=2, sort_keys=True) + "\n")


def version_tuple(version_str):
    return tuple(int(part) if part.isdigit() else part for part in version_str.split("."))


def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract(html, pattern):
    if not pattern:
        return None
    match = re.search(pattern, html)
    if not match:
        return None
    return match.group(1) if match.groups() else match.group(0)


def check_app(app):
    result = {
        "name": app["name"],
        "check_url": app["check_url"],
        "latest_version": None,
        "download_mac": None,
        "download_win": None,
        "error": None,
    }
    try:
        html = fetch_html(app["check_url"])
        result["latest_version"] = extract(html, app["version_regex"])
        if result["latest_version"] is None:
            raise ValueError("version pattern not found on page")
        result["download_mac"] = app.get("mac_download_static") or extract(html, app.get("mac_download_regex"))
        result["download_win"] = app.get("win_download_static") or extract(html, app.get("win_download_regex"))
    except Exception as exc:  # noqa: BLE001 - surface any fetch/parse failure on the page
        result["error"] = str(exc)
    return result


def notify_desktop(title, message):
    system = platform.system()
    try:
        if system == "Darwin":
            script = f'display notification "{message}" with title "{title}" sound name "Glass"'
            subprocess.run(["osascript", "-e", script], check=False, timeout=10)
        elif system == "Windows":
            ps = f"""
$xml = [Windows.Data.Xml.Dom.XmlDocument]::new()
$xml.LoadXml('<toast><visual><binding template="ToastGeneric"><text>{title}</text><text>{message}</text></binding></visual></toast>')
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Software Version Checker").Show($toast)
"""
            subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=False, timeout=10)
    except Exception:
        pass  # best-effort only


def run_setup():
    apps = load_apps()
    local = load_local_versions()
    print("Vul voor elke applicatie de versie in die je nu hebt geïnstalleerd.")
    print("Laat leeg om de huidige waarde te behouden.\n")
    for app in apps:
        name = app["name"]
        current = local.get(name) or "niet ingesteld"
        try:
            value = input(f"{name} (huidig: {current}): ").strip()
        except EOFError:
            value = ""
        if value:
            local[name] = value
    save_local_versions(local)
    print("\nOpgeslagen.")


def run_set(name, version):
    apps = load_apps()
    if not any(a["name"] == name for a in apps):
        print(f"App niet gevonden: {name}")
        print("Beschikbare namen: " + ", ".join(a["name"] for a in apps))
        return 1
    local = load_local_versions()
    local[name] = version
    save_local_versions(local)
    print(f"Ingesteld: {name} -> {version}")
    return 0


def main():
    args = sys.argv[1:]
    ci_mode = "--ci" in args
    notify = "--no-notify" not in args and not ci_mode

    if "--setup" in args:
        run_setup()
        return 0

    if "--set" in args:
        idx = args.index("--set")
        try:
            name, version = args[idx + 1], args[idx + 2]
        except IndexError:
            print('Gebruik: --set "app naam" versienummer')
            return 1
        return run_set(name, version)

    apps = load_apps()
    results = [check_app(app) for app in apps]
    checked_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    LATEST_PATH.write_text(json.dumps({"checked_at": checked_at, "apps": results}, indent=2) + "\n")
    for r in results:
        print(f"{r['name']}: latest={r['latest_version']}" + (f" (error: {r['error']})" if r["error"] else ""))

    if notify:
        local = load_local_versions()
        updates = []
        for r in results:
            installed = local.get(r["name"])
            if installed and r["latest_version"] and version_tuple(installed) < version_tuple(r["latest_version"]):
                updates.append(r["name"])
        if updates:
            notify_desktop("Software update beschikbaar", ", ".join(updates))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
