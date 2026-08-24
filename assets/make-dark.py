"""Dark-theme variants of the ink drawings: flood the white background to
transparency and leave the drawing itself untouched, so the light and dark
versions are the same picture rather than a negative of each other.

Regenerate with:  uv run --with pillow python assets/make-dark.py

Anything not connected to the drawing — ink splatters, and on the banner the
hand-lettered title — is black on white and would vanish on a dark page, so
those parts are inverted to white instead of dropped.

# ponytail: per-pixel Python loops, seconds per asset — fine for a one-off.
"""
from PIL import Image, ImageDraw, ImageFilter
from collections import deque


def components(alpha, w, h):
    """Every connected run of opaque pixels, largest first."""
    a = alpha.load()
    seen = bytearray(w * h)
    out = []
    for sy in range(h):
        for sx in range(w):
            if seen[sy * w + sx] or not a[sx, sy]:
                continue
            seen[sy * w + sx] = 1
            q, comp = deque([(sx, sy)]), []
            while q:
                x, y = q.popleft()
                comp.append((x, y))
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        j = ny * w + nx
                        if not seen[j] and a[nx, ny]:
                            seen[j] = 1
                            q.append((nx, ny))
            out.append(comp)
    out.sort(key=len, reverse=True)
    return out


def cut(src, out_rgba, out_prev, bg=(13, 17, 23), close=9, white=232):
    im = Image.open(src).convert("L")
    w, h = im.size

    # Thicken the lines first: the contour has gaps the flood would leak through.
    sealed = im.filter(ImageFilter.MinFilter(close))
    work = sealed.copy()
    edges = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
             (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for pt in edges:
        ImageDraw.floodfill(work, pt, 128, thresh=40)
    flood = work.point(lambda v: 255 if v == 128 else 0)

    # The flood stops short of the real lines (they were thickened), so grow it
    # back and clip to pixels that are actually white in the original.
    grown = flood.filter(ImageFilter.MaxFilter(close + 4))
    g, o = grown.load(), im.load()
    alpha = Image.new("L", (w, h), 255)
    a = alpha.load()
    for y in range(h):
        for x in range(w):
            if g[x, y] > 127 and o[x, y] >= white:
                a[x, y] = 0

    comps = components(alpha, w, h)
    drawing, rest = comps[0], comps[1:]
    minpx = 12  # below this it is antialiasing fringe, not ink

    tone = im.copy()
    t = tone.load()
    keep = Image.new("L", (w, h), 0)
    k = keep.load()
    for x, y in drawing:
        k[x, y] = 255
    for comp in rest:
        if len(comp) < minpx:
            continue
        for x, y in comp:
            k[x, y] = 255
            t[x, y] = 255 - t[x, y]

    rgba = Image.merge("RGBA", (tone, tone, tone, keep))
    rgba.save(out_rgba)
    flat = Image.new("RGBA", (w, h), bg + (255,))
    flat.alpha_composite(rgba)
    flat.convert("RGB").save(out_prev)
    print(f"{out_rgba}: drawing {len(drawing)}px, {len(rest)} other parts, of {w * h}")


cut("assets/doyen.png", "assets/doyen-dark.png", "/tmp/doyen-dark-preview.png")
cut("assets/banner.png", "assets/banner-dark.png", "/tmp/banner-dark-preview.png")
