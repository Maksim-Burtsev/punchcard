"""Dark-theme banner, derived from the light original — same drawing, not a negative.

    uv run --with pillow --with numpy --with scipy python assets/make-dark.py

The original is black ink on white paper, so a plain inversion turns the
hatched face into a photographic negative. What actually has to change is the
paper, and only where the paper is empty:

    ink        = 255 - gray                      how much ink a pixel carries
    silhouette = fill_holes(blur(ink > 8) > l)   the body of the drawing
    inside     -> the drawing untouched: white paper, black lines
    outside    -> white ink on transparent: the stray hairs, the table specks,
                  the splatters and the hand lettering, which are black on bare
                  paper and would otherwise vanish on a dark page

The two layers are blended in premultiplied alpha so the boundary carries no
seam. The boundary is kept sharp on purpose: a soft one makes the empty paper
semi-transparent white, which reads as a haze around the figure.

# ponytail: constants tuned by eye against assets/banner.png, not a general
# background remover — a second drawing would need its own pass.
"""
import numpy as np
from PIL import Image
from scipy import ndimage as nd

SRC, OUT = "assets/banner.png", "assets/banner-dark.png"
INK_FLOOR = 8     # below this a pixel is paper, not ink
SIGMA, LEVEL = 14, 0.10   # how far apart strokes may sit and still count as one body
CLOSE, SHRINK = 25, 12    # close the gaps in sparse hatching, then pull the edge
EDGE = 0.8                # antialiasing only — see the note about haze above

gray = np.asarray(Image.open(SRC).convert("L"), np.float32)
ink = 255.0 - gray

body = nd.gaussian_filter((ink > INK_FLOOR).astype(np.float32), SIGMA) > LEVEL
body = nd.binary_fill_holes(nd.binary_closing(body, np.ones((CLOSE, CLOSE), bool)))
labels, n = nd.label(body)
body = labels == 1 + int(np.argmax(nd.sum(body, labels, range(1, n + 1))))
body = nd.binary_erosion(body, iterations=SHRINK)

w = nd.gaussian_filter(body.astype(np.float32), EDGE)
alpha = w + (1 - w) * (ink / 255.0)
premul = w * gray + (1 - w) * ink
tone = np.where(alpha > 1e-4, premul / np.maximum(alpha, 1e-4), 255.0)

rgba = np.stack([tone, alpha * 255], -1).clip(0, 255).astype(np.uint8)
Image.fromarray(rgba, "LA").save(OUT, optimize=True)
print(f"{OUT}: silhouette covers {body.mean():.1%} of the frame")
