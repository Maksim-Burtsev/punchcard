"""Render the README demo GIF from its page.

    uv run --with playwright python assets/demo/render.py assets/demo/claude-code.html assets/demo.gif

The page is stepped frame by frame through window.demo (timeline.js) and the
frames are packed by ffmpeg. It is served over HTTP from the repository root,
so it loads its fonts and timeline.js the way a browser would.
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

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_port}/{page_path.relative_to(root)}"

with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
    browser = p.chromium.launch()
    page = browser.new_page(device_scale_factor=SCALE, viewport={"width": 1200, "height": 900})
    page.goto(url, wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    page.evaluate("window.demo.paused = true")
    stage = page.locator("#stage")
    duration = page.evaluate("window.demo.duration")
    for i in range(int(duration * FPS) + 1):
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
