#!/usr/bin/env python3
"""
Propose Wikimedia Commons image candidates for connectors that have no image yet.

This NEVER edits data/connectors.json. It writes data/image_candidates.json for you
to review by hand, because Commons search matches a lot of unrelated hardware
("M12" hits bolts, lenses and cable glands as well as the connector).

Usage:
    python scripts/harvest_commons.py                 # all connectors lacking an image
    python scripts/harvest_commons.py --only "M12"    # just names containing M12
    python scripts/harvest_commons.py --limit 40      # cap how many connectors to query
    python scripts/harvest_commons.py --apply         # apply entries you marked "approved": true

Review loop:
    1. run it            -> data/image_candidates.json
    2. open that file, look at each `thumb` URL in a browser
    3. set "approved": true on the one good candidate per connector (delete the rest)
    4. python scripts/harvest_commons.py --apply
    5. python scripts/download_images.py     (fetches approved files into images/)
"""
import json, os, re, sys, time, argparse, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA  = "connectorswiki-harvester/1.0 (https://github.com/YOURUSER/connectorswiki)"

# Only these licences may be redistributed. Anything else is rejected outright.
FREE = re.compile(r'\b(cc0|cc[- ]by([- ]sa)?|public domain|pd[- ]|gfdl)\b', re.I)
NONFREE = re.compile(r'fair use|non[- ]?free|copyright|all rights reserved|nc\b|nd\b', re.I)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "connectors.json")
CAND = os.path.join(ROOT, "data", "image_candidates.json")


def api(params):
    params = dict(params, format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def parse_page(pg):
    """Turn one API page result into a candidate dict, or None if not usable/free."""
    ii = (pg.get("imageinfo") or [{}])[0]
    if not ii:
        return None
    meta = ii.get("extmetadata") or {}
    def m(k):
        return strip_html((meta.get(k) or {}).get("value", ""))

    lic = m("LicenseShortName") or m("License")
    if not lic or NONFREE.search(lic) or not FREE.search(lic):
        return None
    if ii.get("width", 0) < 300:          # too small to identify a part
        return None

    return {
        "title":   pg.get("title", ""),
        "thumb":   ii.get("thumburl") or ii.get("url"),
        "full":    ii.get("url"),
        "descUrl": ii.get("descriptionurl"),
        "author":  m("Artist") or "Unknown",
        "license": lic,
        "size":    f'{ii.get("width")}x{ii.get("height")}',
        "bytes":   ii.get("size"),
        "approved": False,
    }


def search(term, n=6):
    """Search Commons file namespace and return free-licensed candidates."""
    try:
        r = api({
            "action": "query", "generator": "search",
            "gsrsearch": term, "gsrnamespace": 6, "gsrlimit": n,
            "prop": "imageinfo",
            "iiprop": "url|size|extmetadata",
            "iiurlwidth": 480,            # thumbnail, so we never pull a 13 MB original
        })
    except Exception as e:
        print(f"    ! query failed: {e}", file=sys.stderr)
        return []
    pages = (r.get("query") or {}).get("pages") or []
    out = []
    for pg in pages:
        c = parse_page(pg)
        if c:
            out.append(c)
    return out


def query_term(x):
    """Build a search string biased toward the connector, not the generic word."""
    name = re.sub(r"\s*\(.*?\)", "", x["name"]).strip()
    return f'{name} connector'


def harvest(args):
    data = json.load(open(DATA))
    todo = [x for x in data if not x.get("image")]
    if args.only:
        todo = [x for x in todo if args.only.lower() in x["name"].lower()]
    if args.limit:
        todo = todo[: args.limit]

    print(f"Querying Commons for {len(todo)} connectors without an image…\n")
    results = {}
    for i, x in enumerate(todo, 1):
        term = query_term(x)
        cands = search(term)
        if cands:
            results[x["name"]] = {"query": term, "candidates": cands}
        print(f"  [{i}/{len(todo)}] {x['name'][:38]:40} {len(cands)} free candidate(s)")
        time.sleep(0.4)                   # be polite to the API

    json.dump(results, open(CAND, "w"), indent=1, ensure_ascii=False)
    hit = sum(1 for v in results.values() if v["candidates"])
    print(f"\nWrote {CAND}")
    print(f"{hit}/{len(todo)} connectors got at least one free-licensed candidate.")
    print("Review the `thumb` URLs, set \"approved\": true on the good ones, then run --apply.")


def apply(args):
    if not os.path.exists(CAND):
        sys.exit("No candidates file — run the harvester first.")
    cands = json.load(open(CAND))
    data = json.load(open(DATA))
    by_name = {x["name"]: x for x in data}

    n = 0
    for name, blob in cands.items():
        chosen = [c for c in blob["candidates"] if c.get("approved")]
        if not chosen:
            continue
        if len(chosen) > 1:
            print(f"  ! {name}: {len(chosen)} approved, using the first")
        c = chosen[0]
        x = by_name.get(name)
        if not x:
            print(f"  ! {name}: no longer in connectors.json, skipped")
            continue
        ext = os.path.splitext(c["full"])[1].lower() or ".jpg"
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        x["image"] = f"images/{slug}{ext}"
        x["imageCredit"] = {
            "author":  c["author"],
            "license": c["license"],
            "source":  c["descUrl"],
            "remote":  c["full"],          # download_images.py reads this
        }
        n += 1
        print(f"  + {name} -> {x['image']}  ({c['license']})")

    json.dump(data, open(DATA, "w"), indent=1, ensure_ascii=False)
    print(f"\nApplied {n} image(s). Now run: python scripts/download_images.py")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--only", help="only connectors whose name contains this")
    p.add_argument("--limit", type=int, help="max connectors to query")
    p.add_argument("--apply", action="store_true", help="apply approved candidates")
    a = p.parse_args()
    apply(a) if a.apply else harvest(a)
