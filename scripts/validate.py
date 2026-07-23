#!/usr/bin/env python3
"""Validate data/connectors.json. Exit non-zero on any problem (used by CI)."""
import json, os, sys

REQUIRED = {'name','family','application','useCases','voltage','current','pins','pitch',
            'maxLength','tempRange','standard','locking','legacy','notes','category','subcategory'}
CATS = {"Power","Signal - Low Speed","Signal - High Speed",
        "RF / Fiber / Specialty","Specialty - Extreme","PCB"}
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(root, "data", "connectors.json")))
errs = []
for i, x in enumerate(data):
    if not isinstance(x, dict):
        errs.append(f"[{i}] not an object"); continue
    missing = REQUIRED - x.keys()
    if missing:
        errs.append(f"[{i}] {x.get('name','?')}: missing keys {sorted(missing)}")
    if x.get("category") not in CATS:
        errs.append(f"[{i}] {x.get('name','?')}: bad category {x.get('category')!r}")
    if not str(x.get("name","")).strip():
        errs.append(f"[{i}] empty name")
if errs:
    print("VALIDATION FAILED:"); [print(" -", e) for e in errs]; sys.exit(1)
print(f"OK — {len(data)} connectors valid.")
