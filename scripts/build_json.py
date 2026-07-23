#!/usr/bin/env python3
"""Rebuild data/connectors.json from the phase spreadsheets in source_xlsx/."""
import openpyxl, json, re, glob, os, sys

MAP = {
    "phase1": "Power", "phase2": "Signal - Low Speed", "phase3": "Signal - High Speed",
    "phase4": "RF / Fiber / Specialty", "phase5": "Specialty - Extreme", "phase6": "PCB",
}
KEYS = ['name','family','application','useCases','voltage','current','pins','pitch',
        'maxLength','tempRange','standard','locking','legacy','notes']
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = []
for f in sorted(glob.glob(os.path.join(root, "source_xlsx", "*.xlsx"))):
    base = os.path.basename(f).lower()
    cat = next((v for k, v in MAP.items() if base.startswith(k)), "Uncategorized")
    ws = openpyxl.load_workbook(f, read_only=True).active
    sub = ""
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[0]:
            continue
        name = str(r[0]).strip()
        others = [str(v).strip() for v in r[1:] if v is not None and str(v).strip()]
        m = re.match(r'^CATEGORY:\s*(.+)$', name, re.I)
        if m and not others:
            sub = re.sub(r'\s+', ' ', m.group(1)).strip()
            continue
        d = {k: (str(v).strip() if v is not None else "") for k, v in zip(KEYS, r)}
        d["category"] = cat
        d["subcategory"] = sub
        out.append(d)
os.makedirs(os.path.join(root, "data"), exist_ok=True)
with open(os.path.join(root, "data", "connectors.json"), "w") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
print(f"Wrote {len(out)} connectors to data/connectors.json")
