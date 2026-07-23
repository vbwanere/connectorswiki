#!/usr/bin/env python3
"""Merge verified datasheet URLs from data/datasheets.json into connectors.json.
Never overwrites a URL you've already set by hand."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "data", "connectors.json")))
ds = {k: v for k, v in json.load(open(os.path.join(ROOT, "data", "datasheets.json"))).items()
      if not k.startswith("_")}
by = {x["name"]: x for x in data}
new = kept = missing = 0
for name, url in ds.items():
    x = by.get(name)
    if not x:
        print(f"  ? no connector named {name!r}"); missing += 1; continue
    if x.get("datasheet"):
        kept += 1; continue
    x["datasheet"] = url; new += 1
    print(f"  + {name}")
json.dump(data, open(os.path.join(ROOT, "data", "connectors.json"), "w"), indent=1, ensure_ascii=False)
print(f"\nAdded {new}, left {kept} existing untouched, {missing} name mismatch(es).")
