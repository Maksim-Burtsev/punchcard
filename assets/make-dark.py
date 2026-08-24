"""Dark-theme variant of doyen.png: flood the white background to transparency,
keep the drawing untouched. Regenerate with:  uv run --with pillow python assets/make-dark.py

# ponytail: per-pixel Python loops, ~2s on a 700x586 png — fine for a one-off asset.
"""
from PIL import Image, ImageDraw, ImageFilter
from collections import deque

def cut(src, out_rgba, out_prev, bg=(13,17,23), close=9, white=232):
    im = Image.open(src).convert("L")
    w, h = im.size
    sealed = im.filter(ImageFilter.MinFilter(close))
    work = sealed.copy()
    for pt in [(0,0),(w-1,0),(0,h-1),(w-1,h-1),(w//2,0),(w//2,h-1),(0,h//2),(w-1,h//2)]:
        ImageDraw.floodfill(work, pt, 128, thresh=40)
    flood = work.point(lambda v: 255 if v == 128 else 0)
    # флуд не доливает до линий (линии утолщены) -> расширяем и режем по реально светлым пикселям
    grown = flood.filter(ImageFilter.MaxFilter(close + 4))
    g, o = grown.load(), im.load()
    alpha = Image.new("L", (w, h), 255)
    a = alpha.load()
    for y in range(h):
        for x in range(w):
            if g[x, y] > 127 and o[x, y] >= white:
                a[x, y] = 0

    # выбросить всё, что не связано с главным силуэтом (чернильные брызги в фоне)
    seen = bytearray(w * h)
    kept = []
    minpx = int(w * h * 0.0015)   # мельче — это чернильные брызги в фоне
    for sy in range(0, h, 7):
        for sx in range(0, w, 7):
            i = sy * w + sx
            if seen[i] or a[sx, sy] == 0:
                continue
            q, comp = deque([(sx, sy)]), []
            seen[i] = 1
            while q:
                x, y = q.popleft()
                comp.append((x, y))
                for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
                    if 0 <= nx < w and 0 <= ny < h:
                        j = ny * w + nx
                        if not seen[j] and a[nx, ny]:
                            seen[j] = 1
                            q.append((nx, ny))
            if len(comp) >= minpx:
                kept.extend(comp)
    keep = Image.new("L", (w, h), 0)
    k = keep.load()
    for x, y in kept:
        k[x, y] = 255

    rgba = Image.merge("RGBA", (im, im, im, keep))
    rgba.save(out_rgba)
    flat = Image.new("RGBA", (w, h), bg + (255,))
    flat.alpha_composite(rgba)
    flat.convert("RGB").save(out_prev)
    print(out_rgba, "kept", len(kept), "px of", w*h)

cut("assets/doyen.png", "assets/doyen-dark.png", "/tmp/doyen-dark-preview.png")

