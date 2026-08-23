#!/usr/bin/env python3
"""Build assets/corpus.png — the thirty covers on the shelf, in CORPUS.md order.

    pip install pillow && python3 scripts/covers.py

Covers are fetched by ISBN from Open Library, then Google Books, and cached in
assets/covers/ (gitignored), so re-running is offline and idempotent. A book
neither service has gets a drawn title plate instead of a hole in the grid.
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "assets" / "covers"
OUT = ROOT / "assets" / "corpus.png"

COLUMNS = 10
HEIGHT = 150          # every cover is scaled to this height
GAP = 6
BG = (255, 255, 255)
UA = {"User-Agent": "punchcard-corpus/1.0"}

ROW = re.compile(r"^\| (\d+) \| \*\*(.+?)\*\* — (.+?) \|.*\| (\d{13}) \|$")


def books():
    for line in (ROOT / "CORPUS.md").read_text().splitlines():
        m = ROW.match(line)
        if m:
            yield int(m.group(1)), m.group(2), m.group(3), m.group(4)


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            return r.read()
    except Exception as e:                      # noqa: BLE001 — any failure is a miss
        print(f"    {type(e).__name__}: {url}", file=sys.stderr)
        return None


def download(isbn):
    """Open Library first, Google Books second. None when neither has a cover."""
    data = get(f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false")
    if data and len(data) > 1000:
        return data
    meta = get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}")
    if meta:
        items = json.loads(meta).get("items") or []
        for item in items:
            thumb = item["volumeInfo"].get("imageLinks", {}).get("thumbnail")
            if thumb:
                data = get(thumb.replace("http://", "https://").replace("&edge=curl", ""))
                if data and len(data) > 1000:
                    return data
    return None


def plate(title, author):
    """Last resort: a drawn cover in the same proportions as the real ones."""
    img = Image.new("RGB", (int(HEIGHT * 0.66), HEIGHT), (28, 30, 38))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    y = 14
    for word in (title.split() + ["", author]):
        draw.text((8, y), word[:16], font=font, fill=(226, 228, 233))
        y += 12
    return img


def cover(num, title, author, isbn):
    path = CACHE / f"{isbn}.jpg"
    if not path.exists():
        print(f"[{num:2}] fetching {title}")
        data = download(isbn)
        if data is None:
            print(f"[{num:2}] no cover found, drawing a plate")
            return plate(title, author)
        path.write_bytes(data)
    img = Image.open(path).convert("RGB")
    return img.resize((max(1, round(img.width * HEIGHT / img.height)), HEIGHT), Image.LANCZOS)


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    covers = [cover(*b) for b in books()]
    if len(covers) != 30:
        sys.exit(f"expected 30 books in CORPUS.md, parsed {len(covers)}")

    rows = [covers[i:i + COLUMNS] for i in range(0, len(covers), COLUMNS)]
    width = max(sum(c.width for c in row) + GAP * (len(row) - 1) for row in rows)
    height = len(rows) * HEIGHT + GAP * (len(rows) - 1)

    sheet = Image.new("RGB", (width, height), BG)
    for r, row in enumerate(rows):
        x = (width - (sum(c.width for c in row) + GAP * (len(row) - 1))) // 2
        for c in row:
            sheet.paste(c, (x, r * (HEIGHT + GAP)))
            x += c.width + GAP
    sheet.convert("P", palette=Image.Palette.ADAPTIVE, colors=192).save(OUT, optimize=True)
    print(f"{OUT.relative_to(ROOT)}: {sheet.width}x{sheet.height}, {OUT.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
