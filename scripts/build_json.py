#!/usr/bin/env python3
"""Rebuild data/connectors.json from the phase spreadsheets in source_xlsx/."""
import openpyxl, json, re, glob, os, sys

MAP = {
    "phase1": "Power", "phase2": "Signal - Low Speed", "phase3": "Signal - High Speed",
    "phase4": "RF / Fiber / Specialty", "phase5": "Specialty - Extreme", "phase6": "PCB",
}
KEYS = ['name','family','application','useCases','voltage','current','pins','pitch',
        'maxLength','tempRange','standard','locking','legacy','notes']

def classify(x):
    """Derive drawing geometry from published dimensional data (pitch, pins, rows)."""
    pitch = re.search(r'\d+\.?\d*', x['pitch'] or '')
    pins  = re.findall(r'\d+', x['pins'] or '')
    name  = x['name'].lower()
    if pitch and pins:
        rows = 2 if re.search(r'2x|dual.?row|2 row|idc|ribbon', name + x['notes'].lower()) else 1
        return {"draw":"header","pitch":float(pitch.group()),
                "pinMin":int(pins[0]),"pinMax":int(pins[-1]),"rows":rows}
    if re.search(r'm8|m12|m16|m23|circular|mil-dtl|xlr|din|aviation|gx|bulgin|amphenol c16|ip67 circ', name):
        n = int(pins[0]) if pins else 4
        return {"draw":"circular","pinMin":n,"pinMax":int(pins[-1]) if pins else n}
    if re.search(r'\bd[a-e]-?\d|d-sub|db-?\d|de-?9|dc-37|dd-50', name):
        return {"draw":"dsub","pins":int(pins[0]) if pins else 9}
    if re.search(r'xt30|xt60|xt90|bullet|banana|powerpole|deans|ec[35]', name):
        return {"draw":"blade","pins":int(pins[0]) if pins else 2}
    return None

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
        g = classify(d)
        if g: d["geom"] = g
        d["datasheet"] = ""
        d["image"] = ""
        out.append(d)
os.makedirs(os.path.join(root, "data"), exist_ok=True)
with open(os.path.join(root, "data", "connectors.json"), "w") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
print(f"Wrote {len(out)} connectors to data/connectors.json")
