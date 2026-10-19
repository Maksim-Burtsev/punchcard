"""Write assets/demo.svg: the top of the review typed into a terminal, as an
animated SVG that loops, follows light and dark mode, and stays sharp at any
zoom. The text comes from assets/demo-screen.txt, up to finding #1's fix.

    python3 assets/demo/svg.py
"""

import re
from html import escape
from pathlib import Path

assets = Path(__file__).resolve().parents[1]
screen = (assets / "demo-screen.txt").read_text().splitlines()
review = screen[: next(i for i, l in enumerate(screen) if "Fix:" in l) + 1]

PROMPT = "/punchcard https://github.com/psf/requests/pull/7520"
LINE, CHAR, PAD, TOP = 20, 8.1, 22, 52  # px; CHAR is a 13px monospace column, rounded up for wide fallbacks
TYPE, CYCLE = 0.035, 16.0  # seconds per typed character, seconds per loop


def paint(line):
    """One screen line as tspans, coloured the way the old tape's awk did it."""
    text = escape(line)
    if "Ship after" in line:
        return f'<tspan class="orange b">{text}</tspan>'
    if re.match(r"  \d ", line):
        text = text.replace("● BLOCKER", '<tspan class="red">● BLOCKER</tspan>')
        return text.replace("● DESIGN", '<tspan class="yellow">● DESIGN</tspan>')
    if line.startswith("● 1"):
        return f'<tspan class="red b">{text}</tspan>'
    if "severity" in line or line.lstrip().startswith("# "):
        return f'<tspan class="dim">{text}</tspan>'
    if line.startswith("src/"):
        head, rest = text.split(" ", 1)
        return f'<tspan class="dim">{head}</tspan> {rest}'
    if "Fix:" in line:
        head, rest = text.split("Fix:", 1)
        return f'{head}<tspan class="b">Fix:{rest}</tspan>'
    return text


# (text, seconds it appears at); the prompt is typed, the rest streams in.
lines = [(f'<tspan class="dim">❯</tspan> {escape(PROMPT)}', 0.6)]
t = 0.6 + len(PROMPT) * TYPE + 0.6
lines.append(('<tspan class="green">✓</tspan> <tspan class="dim">three finder passes · every value to its last consumer · every removed guarantee</tspan>', t))
t += 0.9
lines.append(('<tspan class="green">✓</tspan> <tspan class="dim">judging 7 candidates against the constitution · running main and this PR</tspan>', t))
t += 0.8
lines.append(("", t))
for line in review:
    t += 0.9 if line.startswith("● 1") else 0.07
    lines.append((paint(line), t))

width = 2 * PAD + CHAR * max(len(l) for l in screen[:30])
height = TOP + LINE * len(lines) + PAD

pct = lambda s: f"{100 * s / CYCLE:.2f}%"
css, body = [], []
for i, (text, at) in enumerate(lines):
    css.append(f"@keyframes l{i} {{ 0%, {pct(at)} {{ opacity: 0 }} {pct(at + 0.01)}, 97% {{ opacity: 1 }} 100% {{ opacity: 0 }} }}"
               f" .l{i} {{ animation: l{i} {CYCLE}s infinite step-end; }}")
    body.append(f'<text class="l{i}" x="{PAD}" y="{TOP + LINE * (i + 1) - 6}">{text}</text>')

typed = len(PROMPT) + 2
css.append(f"@keyframes type {{ 0%, {pct(0.6)} {{ transform: scaleX({2 / typed:.4f}) }} {pct(0.6 + len(PROMPT) * TYPE)}, 100% {{ transform: none }} }}"
           f" .typing {{ transform-box: fill-box; transform-origin: left; animation: type {CYCLE}s infinite steps({len(PROMPT)}, end); }}")
# The prompt line is clipped by a rect that grows a column at a time.
body[0] = (f'<clipPath id="typed"><rect class="typing" x="{PAD}" y="{TOP}" width="{typed * CHAR + 2}" height="{LINE}"/></clipPath>'
           f'<g clip-path="url(#typed)">{body[0].replace("class=\"l0\" ", "")}</g>')

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="Punchcard reviewing psf/requests#7520: verdict Ship after #1, a summary table of three findings, and finding #1 run through main and the PR">
<style>
  svg {{ --bg: #ffffff; --bar: #f6f8fa; --line: #d1d9e0; --fg: #1f2328; --dim: #59636e; --red: #cf222e; --orange: #bc4c00; --yellow: #9a6700; --green: #1a7f37; }}
  @media (prefers-color-scheme: dark) {{
    svg {{ --bg: #0d1117; --bar: #151b23; --line: #3d444d; --fg: #e6edf3; --dim: #8b949e; --red: #ff7b72; --orange: #f0883e; --yellow: #e3b341; --green: #3fb950; }}
  }}
  text {{ font: 13px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: var(--fg); white-space: pre; font-variant-ligatures: none; }}
  .dim {{ fill: var(--dim); }} .red {{ fill: var(--red); }} .orange {{ fill: var(--orange); }}
  .yellow {{ fill: var(--yellow); }} .green {{ fill: var(--green); }} .b {{ font-weight: 700; }}
  {chr(10).join("  " + c for c in css)}
</style>
<rect x=".5" y=".5" width="{width - 1:.0f}" height="{height - 1:.0f}" rx="10" fill="var(--bg)" stroke="var(--line)"/>
<path d="M.5 34.5V10.5a10 10 0 0 1 10-10h{width - 21:.0f}a10 10 0 0 1 10 10v24z" fill="var(--bar)" stroke="var(--line)"/>
<circle cx="20" cy="17.5" r="6" fill="var(--line)"/><circle cx="40" cy="17.5" r="6" fill="var(--line)"/><circle cx="60" cy="17.5" r="6" fill="var(--line)"/>
<text x="{width / 2:.0f}" y="22" text-anchor="middle" class="dim" style="font-size: 12px">~/src/requests — claude</text>
{chr(10).join(body)}
</svg>
"""
(assets / "demo.svg").write_text(svg)
print(assets / "demo.svg")
