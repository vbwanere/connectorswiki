#!/usr/bin/env python3
"""
Download the images approved by harvest_commons.py --apply into images/,
and regenerate images/CREDITS.md.

CC-BY and CC-BY-SA REQUIRE attribution to be shown. The site renders it from
imageCredit in connectors.json; CREDITS.md is the repo-level record.
"""
import json, os, re, sys, urllib.request

UA = "connectorswiki/1.0 (https://github.com/YOURUSER/connectorswiki)"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "connectors.json")
IMGDIR = os.path.join(ROOT, "images")

data = json.load(open(DATA))
os.makedirs(IMGDIR, exist_ok=True)

got = skipped = 0
for x in data:
    cred = x.get("imageCredit") or {}
    remote = cred.get("remote")
    if not remote or not x.get("image"):
        continue
    dest = os.path.join(ROOT, x["image"])
    if os.path.exists(dest):
        skipped += 1
        continue
    try:
        req = urllib.request.Request(remote, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
            f.write(r.read())
        mb = os.path.getsize(dest) / 1e6
        print(f"  + {x['image']}  {mb:.1f} MB")
        if mb > 2:
            print(f"    ! large file — consider downscaling before committing")
        got += 1
    except Exception as e:
        print(f"  ! {x['name']}: {e}", file=sys.stderr)

# regenerate credits
lines = ["# Image credits", "",
         "Images below come from Wikimedia Commons under the licence shown.",
         "Attribution is required by those licences and is also displayed in the site UI.",
         ""]
for x in sorted(data, key=lambda d: d["name"]):
    c = x.get("imageCredit")
    if not c:
        continue
    lines.append(f"- **{x['name']}** — {c['author']}, {c['license']} — <{c['source']}>")
open(os.path.join(IMGDIR, "CREDITS.md"), "w").write("\n".join(lines) + "\n")

print(f"\nDownloaded {got}, already present {skipped}. Wrote images/CREDITS.md")
