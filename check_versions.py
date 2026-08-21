#!/usr/bin/env python3
"""Check for new versions of entertainment-industry software without in-app updaters.

Shared app catalog lives in apps.json (checked into git). Each person's own
installed versions live in local_versions.json (gitignored, machine-local).

Usage:
  python3 check_versions.py                  # check all apps, update dashboard, notify on updates
  python3 check_versions.py --setup          # interactive: enter your installed version per app
  python3 check_versions.py --set "Shure Wireless Workbench (WWB)" 7.8.3
                                               # record the version you currently have installed
  python3 check_versions.py --no-notify       # check + dashboard, skip desktop notification
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
DASHBOARD_PATH = BASE_DIR / "dashboard.html"
LOG_PATH = BASE_DIR / "last_check.log"

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


def check_app(app, installed_version):
    result = {
        "name": app["name"],
        "check_url": app["check_url"],
        "installed_version": installed_version,
        "latest_version": None,
        "download_mac": None,
        "download_win": None,
        "status": "unknown",
        "error": None,
    }
    try:
        html = fetch_html(app["check_url"])
        result["latest_version"] = extract(html, app["version_regex"])
        if result["latest_version"] is None:
            raise ValueError("version pattern not found on page")
        result["download_mac"] = extract(html, app.get("mac_download_regex"))
        result["download_win"] = extract(html, app.get("win_download_regex"))
    except Exception as exc:  # noqa: BLE001 - surface any fetch/parse failure in the dashboard
        result["status"] = "error"
        result["error"] = str(exc)
        return result

    if not installed_version:
        result["status"] = "no_baseline"
    elif version_tuple(installed_version) < version_tuple(result["latest_version"]):
        result["status"] = "update_available"
    else:
        result["status"] = "up_to_date"
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
        pass  # notification is best-effort; the dashboard remains the source of truth


STATUS_LABEL = {
    "update_available": ("Update beschikbaar", "filled", "#c2680d"),
    "up_to_date": ("Up-to-date", "filled", "#0f6f6b"),
    "no_baseline": ("Geen versie ingesteld", "outline", None),
    "error": ("Check mislukt", "filled", "#dc2626"),
}


def render_dashboard(results, checked_at):
    rows = []
    n_updates = sum(1 for r in results if r["status"] == "update_available")

    for r in results:
        label, variant, color = STATUS_LABEL[r["status"]]
        installed = r["installed_version"] or "—"
        latest = r["latest_version"] or "—"
        detail = f'<div class="error">{r["error"]}</div>' if r["error"] else ""
        badge_style = f'background:{color};color:#fff;' if variant == "filled" else ""
        badge = f'<span class="badge {variant}" style="{badge_style}">{label}</span>'
        action = ""
        if r["status"] == "update_available":
            args = ", ".join(json.dumps(v or "") for v in (r["check_url"], r["download_mac"], r["download_win"]))
            action = f'<button class="update-btn" onclick=\'handleUpdate({args})\'>Updaten →</button>'

        rows.append(f"""
        <tr>
          <td class="name"><a href="{r['check_url']}" target="_blank" rel="noopener">{r['name']}</a></td>
          <td>{installed}</td>
          <td>{latest}</td>
          <td>{badge}{detail}</td>
          <td>{action}</td>
        </tr>""")

    html = f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<title>Software Version Checker</title>
<style>
  :root {{
    --brand:#0f6f6b; --brand-dark:#0b5b58;
    --bg:#eef3f4; --card:#ffffff; --text:#152224; --muted:#5f7679; --border:#dfe7e8;
    --thead-bg:#eaf3f3;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#0b1516; --card:#101c1d; --text:#e6f1f1; --muted:#89a3a5; --border:#203435; --thead-bg:#132322; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--text);
          font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; }}
  .topbar {{ background:var(--brand); color:#fff; padding:16px 32px; display:flex;
             align-items:baseline; justify-content:space-between; }}
  .topbar h1 {{ font-size:18px; margin:0; font-weight:600; }}
  .topbar .subtitle {{ font-size:12px; opacity:.85; }}
  .content {{ max-width:1000px; margin:0 auto; padding:28px 24px 40px; }}
  table {{ width:100%; border-collapse:collapse; background:var(--card); border:1px solid var(--border);
           border-radius:12px; overflow:hidden; }}
  th, td {{ text-align:left; padding:12px 16px; font-size:14px; border-bottom:1px solid var(--border); }}
  th {{ background:var(--thead-bg); color:var(--muted); font-weight:600; font-size:12px;
        text-transform:uppercase; letter-spacing:.04em; }}
  tr:last-child td {{ border-bottom:none; }}
  .name a {{ color:var(--text); text-decoration:none; font-weight:600; }}
  .name a:hover {{ text-decoration:underline; }}
  .badge {{ display:inline-block; padding:4px 12px; border-radius:999px; font-size:11px; font-weight:700;
            text-transform:uppercase; letter-spacing:.03em; }}
  .badge.outline {{ background:transparent; color:var(--muted); border:1px solid var(--border); }}
  .error {{ color:#dc2626; font-size:11px; margin-top:4px; }}
  .update-btn {{ display:inline-block; padding:6px 14px; border-radius:999px; background:var(--brand);
                  color:#fff; font-size:13px; font-weight:600; border:none; cursor:pointer; white-space:nowrap;
                  font-family:inherit; }}
  .update-btn:hover {{ background:var(--brand-dark); }}
  footer {{ margin-top:20px; color:var(--muted); font-size:12px; }}
</style>
</head>
<body>
  <div class="topbar">
    <h1>Software Version Checker</h1>
    <div class="subtitle">Laatst gecontroleerd: {checked_at} · {n_updates} update(s) beschikbaar</div>
  </div>
  <div class="content">
    <table>
      <thead><tr><th>Applicatie</th><th>Geïnstalleerd</th><th>Laatste versie</th><th>Status</th><th></th></tr></thead>
      <tbody>{"".join(rows)}</tbody>
    </table>
    <footer>Genereer opnieuw met <code>python3 check_versions.py</code>. Versie instellen met <code>python3 check_versions.py --setup</code>.</footer>
  </div>
  <script>
    function handleUpdate(pageUrl, macUrl, winUrl) {{
      window.open(pageUrl, "_blank", "noopener");
      var isMac = /Macintosh/.test(navigator.userAgent);
      var fileUrl = isMac ? macUrl : winUrl;
      if (fileUrl) {{
        var a = document.createElement("a");
        a.href = fileUrl;
        a.rel = "noopener";
        document.body.appendChild(a);
        a.click();
        a.remove();
      }}
    }}
  </script>
</body>
</html>
"""
    DASHBOARD_PATH.write_text(html)


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
    print("\nOpgeslagen. Draai nu 'python3 check_versions.py' om te controleren op updates.")


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
    notify = "--no-notify" not in args

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
    local = load_local_versions()
    results = [check_app(app, local.get(app["name"])) for app in apps]
    checked_at = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")

    render_dashboard(results, checked_at)

    updates = [r for r in results if r["status"] == "update_available"]
    log_lines = [
        f"[{checked_at}] {r['name']}: {r['status']} (installed={r['installed_version']}, latest={r['latest_version']})"
        for r in results
    ]
    LOG_PATH.write_text("\n".join(log_lines) + "\n")

    for line in log_lines:
        print(line)

    if updates and notify:
        names = ", ".join(u["name"] for u in updates)
        notify_desktop("Software update beschikbaar", names)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
