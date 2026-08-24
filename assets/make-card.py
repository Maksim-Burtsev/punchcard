"""The banner as a sheet of paper, from the light original — one file, both themes.

    uv run --with pillow --with numpy python assets/make-card.py

A drawing on white paper cannot be made dark without either redrawing it or
cutting the paper away, and a cut-out silhouette reads as exactly that: a torn
piece of paper floating on the page. So the paper stays and becomes deliberate
instead — warm off-white rather than blown-out white, rounded corners, a soft
shadow under it. A sheet laid on the page is a thing readers recognise on a
white background and on a black one alike.

# ponytail: constants tuned by eye against assets/banner.png at width=720,
# the size the README actually renders.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SRC, OUT = "assets/banner.png", "assets/banner-card.png"
PAPER = 244        # white of the original maps to this: paper, not glare
RADIUS = 28
MARGIN = 30        # room around the sheet for the shadow
SHADOW_SIGMA, SHADOW_ALPHA, SHADOW_DY = 16, 0.40, 8

src = Image.open(SRC).convert("L")
w, h = src.size
cw, ch = w + 2 * MARGIN, h + 2 * MARGIN

sheet = Image.new("L", (cw, ch), 0)
ImageDraw.Draw(sheet).rounded_rectangle(
    [MARGIN, MARGIN, MARGIN + w - 1, MARGIN + h - 1], radius=RADIUS, fill=255)
shadow = np.roll(np.asarray(sheet.filter(ImageFilter.GaussianBlur(SHADOW_SIGMA))),
                 SHADOW_DY, axis=0)

tone = np.zeros((ch, cw), np.float32)
tone[MARGIN:MARGIN + h, MARGIN:MARGIN + w] = np.asarray(src, np.float32) * (PAPER / 255.0)

a_sheet = np.asarray(sheet, np.float32) / 255.0
a_shadow = (shadow.astype(np.float32) / 255.0) * SHADOW_ALPHA
alpha = a_sheet + a_shadow * (1 - a_sheet)
premul = tone * a_sheet                      # the shadow is black, so it adds nothing here
out = np.where(alpha > 1e-4, premul / np.maximum(alpha, 1e-4), 0.0)

Image.fromarray(np.stack([out, alpha * 255], -1).clip(0, 255).astype(np.uint8), "LA") \
     .save(OUT, optimize=True)
print(f"{OUT}: {cw}x{ch}")
