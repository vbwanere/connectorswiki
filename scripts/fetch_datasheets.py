#!/usr/bin/env python3
"""
LOCAL REFERENCE ONLY — output goes to images/local/, which is gitignored.
Never commit or publish what this produces. Datasheet figures are the
manufacturer's copyrighted work; keeping a personal copy for reference is a
different thing from redistributing it, and this script only does the former.

Pulls whatever is named in each connector's `datasheet` field and extracts
figures from it:

  * PDF  -> extracts embedded raster images, and rasterizes pages as a fallback
  * HTML -> extracts product images referenced by the page

Usage:
    python scripts/fetch_datasheets.py                # every entry with a datasheet URL
    python scripts/fetch_datasheets.py --only "JST"   # names containing JST
    python scripts/fetch_datasheets.py --pages        # also rasterize full PDF pages
    python scripts/fetch_datasheets.py --list         # just show what has a datasheet URL

After it runs, point a connector at the best figure by hand:
    "localImage": "images/local/jst-xh/p3-fig2.png"
"""
import argparse, json, os, re, subprocess, sys, urllib.parse, urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) connectorswiki-local-reference/1.0"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "connectors.json")
OUT = os.path.join(ROOT, "images", "local")
MIN_PX = 120          # ignore icons, bullets, spacer gifs
MIN_BYTES = 1200        # cheap pre-filter only; pixel size is the real gate


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def get(url, timeout=45):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "").lower(), r.geturl()

def big_enough(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.width >= MIN_PX and im.height >= MIN_PX
    except Exception:
        return os.path.getsize(path) >= MIN_BYTES


def from_pdf(pdf_path, dest, rasterize):
    """pdfimages pulls the embedded figures; pdftoppm renders whole pages."""
    n = 0
    try:
        subprocess.run(["pdfimages", "-png", "-p", pdf_path, os.path.join(dest, "fig")],
                       check=True, capture_output=True, timeout=180)
    except Exception as e:
        print(f"    ! pdfimages: {e}")
    for f in sorted(os.listdir(dest)):
        p = os.path.join(dest, f)
        if f.startswith("fig") and f.endswith(".png"):
            if big_enough(p):
                n += 1
            else:
                os.remove(p)      # drop logos and rules

    if rasterize or n == 0:
        try:
            subprocess.run(["pdftoppm", "-png", "-r", "110", "-f", "1", "-l", "6",
                            pdf_path, os.path.join(dest, "page")],
                           check=True, capture_output=True, timeout=180)
            n += len([f for f in os.listdir(dest) if f.startswith("page")])
        except Exception as e:
            print(f"    ! pdftoppm: {e}")
    return n


def from_html(html, base_url, dest):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    urls, seen = [], set()
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-original")
        if not src:
            continue
        u = urllib.parse.urljoin(base_url, src)
        if u in seen or re.search(r"logo|icon|sprite|avatar|pixel|badge|banner", u, re.I):
            continue
        seen.add(u)
        urls.append(u)

    n = 0
    for i, u in enumerate(urls[:25]):
        ext = os.path.splitext(urllib.parse.urlparse(u).path)[1][:5] or ".jpg"
        if ext.lower() not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            continue
        p = os.path.join(dest, f"img{i:02d}{ext}")
        try:
            data, _, _ = get(u, timeout=25)
            if len(data) < MIN_BYTES:
                continue          # 1x1 trackers and spacers
            open(p, "wb").write(data)
            if big_enough(p):
                n += 1
            else:
                os.remove(p)
        except Exception:
            continue
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="only connectors whose name contains this")
    ap.add_argument("--pages", action="store_true", help="also rasterize PDF pages")
    ap.add_argument("--list", action="store_true", help="list entries with datasheet URLs")
    a = ap.parse_args()

    data = json.load(open(DATA))
    todo = [x for x in data if (x.get("datasheet") or "").startswith("http")]
    if a.only:
        todo = [x for x in todo if a.only.lower() in x["name"].lower()]

    if a.list or not todo:
        print(f"{len(todo)} connector(s) have a datasheet URL:")
        for x in todo:
            print(f"  {x['name'][:40]:42} {x['datasheet']}")
        if not todo:
            print("\nNothing to fetch. Populate the `datasheet` field first —")
            print("that's the bottleneck, not this script.")
        return

    os.makedirs(OUT, exist_ok=True)
    total = 0
    for i, x in enumerate(todo, 1):
        s = slug(x["name"])
        dest = os.path.join(OUT, s)
        os.makedirs(dest, exist_ok=True)
        print(f"[{i}/{len(todo)}] {x['name']}")
        try:
            body, ctype, final = get(x["datasheet"])
        except Exception as e:
            print(f"    ! fetch failed: {e}")
            continue

        if "pdf" in ctype or final.lower().endswith(".pdf") or body[:4] == b"%PDF":
            pdf = os.path.join(dest, "datasheet.pdf")
            open(pdf, "wb").write(body)
            n = from_pdf(pdf, dest, a.pages)
            print(f"    pdf -> {n} figure(s) in images/local/{s}/")
        elif "html" in ctype:
            n = from_html(body.decode("utf-8", "ignore"), final, dest)
            print(f"    html -> {n} image(s) in images/local/{s}/")
        else:
            print(f"    ? unhandled content-type: {ctype}")
            n = 0
        total += n

    print(f"\n{total} file(s) into images/local/ — gitignored, local reference only.")
    print('Point a connector at one with:  "localImage": "images/local/<slug>/<file>"')


if __name__ == "__main__":
    main()
