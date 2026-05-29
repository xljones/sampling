import datetime
import json
import os
import re
import subprocess

ver = re.search(r'version\s*=\s*"([^"]+)"', open("pyproject.toml").read())
ver = ver.group(1) if ver else "unknown"

sha = subprocess.check_output(["git", "log", "-1", "--format=%h"]).decode().strip()
msg = subprocess.check_output(["git", "log", "-1", "--format=%s"]).decode().strip()
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

bi = json.load(open("dist/build-info.json")) if os.path.exists("dist/build-info.json") else {}

print("")
print("════ Deployment complete ════════════════════════════")
print(f"  Version:     {ver}")
if bi:
    print(f"  dist SHA:    {bi.get('sha', '?')}  (built {bi.get('built_at', '?')})")
print(f"  Commit:      {sha} — {msg}")
print(f"  Deployed at: {now}")
print("════════════════════════════════════════════════════")
print("Reload the web app in the PythonAnywhere Web tab.")
print("")
