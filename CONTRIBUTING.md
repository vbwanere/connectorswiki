# Contributing to Connectors Wiki

Everything lives in one file: [`data/connectors.json`](data/connectors.json).
You can contribute entirely from the GitHub web UI — no local setup needed.

## 1. Fix or add a connector

Click the pencil on `data/connectors.json`, edit, then **Propose changes → Create
pull request**. Every field is a plain string.

```json
{
  "name": "JST XH",
  "family": "JST XH",
  "application": "Low voltage DC power",
  "useCases": "LED strips, small batteries, Arduino shields",
  "voltage": "250V",
  "current": "3A",
  "pins": "2–20",
  "pitch": "2.50",
  "maxLength": "< 1m typical",
  "tempRange": "-25 to +85",
  "standard": "—",
  "locking": "Friction lock with header latch",
  "legacy": "No",
  "notes": "Top-entry latch on header; do not confuse with VH (3.96mm pitch).",
  "category": "Power",
  "subcategory": "1A — LOW VOLTAGE DC (≤48V)",
  "datasheet": "https://www.jst-mfg.com/product/pdf/eng/eXH.pdf",
  "image": ""
}
```

`category` must be one of: `Power`, `Signal - Low Speed`, `Signal - High Speed`,
`RF / Fiber / Specialty`, `Specialty - Extreme`, `PCB`.
CI validates every PR, so a malformed entry gets caught before merge.

**The highest-value contribution right now is `datasheet` links.** Link the
manufacturer's own PDF or product page — that's where the authoritative
dimensions live, and it's what makes a row usable instead of merely informative.

## 2. Drawings

154 connectors get a **generated, to-scale drawing** automatically: if a
connector has a numeric `pitch` and a `pins` count, the site computes the
footprint, pin-1 marker, pitch dimension, and overall span live in the browser.
Nothing to draw — just make sure `pitch` and `pins` are accurate.

The other 258 are circular, RF, or moulded parts whose geometry can't be derived
from pitch. Those need a real drawing, contributed as SVG:

1. Draw the **mating face** (the view you see looking into the connector).
2. Save as `images/<slug>.svg` — e.g. `images/anderson-sb50.svg`.
3. Set `"image": "images/anderson-sb50.svg"` on that connector.
4. Use `stroke="#1857a4"`, `fill="#eef2f7"` for the body and `fill="#fff"` for
   contacts, so it matches the generated drawings.

### Image licensing — read this before uploading anything

**Do not upload manufacturer photos or datasheet drawings.** They're copyrighted,
and they are the fastest way to get this project taken down. Only contribute:

- SVGs **you drew yourself** (preferred), or
- images you took yourself, or
- media explicitly licensed CC0 / CC-BY / public domain, with the source and
  licence recorded in the PR description.

A link to the manufacturer's datasheet is always safe and often more useful than
a picture.

## 3. Rebuilding from spreadsheets

```bash
python scripts/build_json.py   # regenerate data/connectors.json from source_xlsx/
python scripts/validate.py     # must pass before you open a PR
```
