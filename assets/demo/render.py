"""Render a demo page into the image the README shows.

    uv run --with playwright python assets/demo/render.py assets/demo/claude-code.html assets/demo.gif
    uv run --with playwright python assets/demo/render.py assets/demo/pr-comment.html assets/demo-dark.png
    uv run --with playwright python assets/demo/render.py assets/demo/pr-comment.html assets/demo-light.png light

A .gif is stepped frame by frame through window.demo (timeline.js) and packed
by ffmpeg; a .png is one screenshot. The optional third argument becomes the
page's ?theme. The page is served over HTTP from the repository root so it
can fetch files next to it, like ../demo-review.md.
"""

import functools
import http.server
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

FPS = 15
SCALE = 2  # captured at 2x, packed at OUT_SCALE: sharp text on retina, sane GIF size
OUT_SCALE = 1.5

root = Path(__file__).resolve().parents[2]
page_path, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
theme = sys.argv[3] if len(sys.argv) > 3 else "dark"

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/{page_path.relative_to(root)}?theme={theme}"

with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
    browser = p.chromium.launch()
    page = browser.new_page(device_scale_factor=SCALE, viewport={"width": 1200, "height": 900})
    page.goto(url, wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    stage = page.locator("#stage")

    if out.suffix == ".png":
        page.wait_for_function("window.ready !== false")
        stage.screenshot(path=out)
    else:
        page.evaluate("window.demo.paused = true")
        duration = page.evaluate("window.demo.duration")
        frames = int(duration * FPS) + 1
        for i in range(frames):
            page.evaluate(f"window.demo.seek({i / FPS})")
            stage.screenshot(path=f"{tmp}/{i:05d}.png")
        width = int(stage.bounding_box()["width"] * OUT_SCALE)
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{tmp}/%05d.png",
             "-vf", f"scale={width}:-1:flags=lanczos,split[a][b];"
                    "[a]palettegen=max_colors=128:stats_mode=full[p];"
                    "[b][p]paletteuse=dither=none:diff_mode=rectangle",
             str(out)],
            check=True,
        )
    browser.close()
server.shutdown()
print(out)
