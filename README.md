# Connectors Wiki

An open, community-maintained reference of electrical connectors — ratings, pin
counts, pitch, standards, temperature range, locking, and application notes.
**412 connectors** across 6 categories, **154 with generated to-scale drawings**: Power, Signal (Low & High Speed),
RF/Fiber/Specialty, Specialty-Extreme, and PCB.

The site is a single static page. No server, no build step, no database. It
loads `data/connectors.json` in the browser and does all search, filtering, and
sorting client-side. That's why it can be hosted free on GitHub Pages and why
anyone can contribute by editing one JSON file.

---

## Publish it (GitHub Pages) — one time

1. Create a new **public** repo on GitHub, e.g. `connectorswiki`.
2. Put these files at the repo root: `index.html`, `data/connectors.json`,
   `README.md`, `LICENSE`, `scripts/`.
3. In `index.html`, set the `REPO` constant (near the bottom `<script>`) to
   `"YOURUSER/connectorswiki"` so the Star/Contribute links point at your repo.
4. Push:
   ```bash
   git init
   git add .
   git commit -m "Initial connectorswiki"
   git branch -M main
   git remote add origin https://github.com/YOURUSER/connectorswiki.git
   git push -u origin main
   ```
5. Repo → **Settings → Pages** → Source: **Deploy from a branch** → Branch:
   `main`, folder `/ (root)` → Save.
6. Wait ~1 minute. Your site is live at
   `https://YOURUSER.github.io/connectorswiki/`.

Every push to `main` after that redeploys automatically.

---

## Drawings

Connectors with a numeric pitch and pin count get a **to-scale footprint drawn
live in the browser** — pin-1 marker, pitch dimension, overall span, and a pin-count
slider so a 4-way and a 20-way of the same family show their real dimensions.
No image files, no licensing problem: the drawing is computed from the data.

Circular, RF, and moulded connectors need hand-drawn SVGs — see
[CONTRIBUTING.md](CONTRIBUTING.md). **Do not upload manufacturer photos or
datasheet scans**; they're copyrighted. Original SVGs, your own photos, or
explicitly free-licensed media only.

## How to contribute

The data is one file: [`data/connectors.json`](data/connectors.json). Each
connector is one object. To add or fix a connector you edit that file and open a
pull request — you can do the whole thing in the GitHub web UI, no tools needed.

1. Open `data/connectors.json` on GitHub → click the pencil (**Edit**).
2. Add a new object (copy the template below) or correct an existing one.
3. Scroll down → **Propose changes** → **Create pull request**.

### Connector object template

```json
{
  "name": "JST XH",
  "family": "JST XH",
  "application": "Low voltage DC power",
  "useCases": "LED strips, small batteries, Arduino shields, hobby electronics",
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
  "subcategory": "1A — LOW VOLTAGE DC (≤48V)"
}
```

### Field rules
- **All 16 keys must be present.** Use `""` or `"—"` if a value is unknown.
- `category` must be exactly one of: `Power`, `Signal - Low Speed`,
  `Signal - High Speed`, `RF / Fiber / Specialty`, `Specialty - Extreme`, `PCB`.
- `legacy` is a short status string: `"No"` for current, `"Yes — Legacy"` for
  obsolete, or a note like `"Declining (USB-C replacing)"`. Anything starting
  with "No" shows as CURRENT; "Declining"/"Partial"/"Becoming" show as DECLINING;
  everything else shows as LEGACY.
- Keep `pitch` numeric-ish (`"2.50"`) so column sorting works.
- Cite a datasheet or standard in `notes` where you can.

A GitHub Action validates every PR (see below), so a malformed entry is caught
before merge.

---

## Regenerating from the spreadsheets

The JSON was generated from the six phase spreadsheets. If you prefer to keep
editing in Excel, drop the `.xlsx` files in `source_xlsx/` and run:

```bash
python scripts/build_json.py
```

That rewrites `data/connectors.json`. Then validate:

```bash
python scripts/validate.py
```

---

## License

Data and code released under the MIT License. See [LICENSE](LICENSE).
