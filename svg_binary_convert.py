"""
Convert avi-ascii-updated.svg to binary format:
  0 = white  (space characters)
  1 = green  (non-space characters)

Produces a new SVG where every character is rendered individually:
  - spaces  → white  (#ffffff)
  - others  → green  (#00ff41 / matrix green)
"""

import re
import xml.etree.ElementTree as ET

INPUT_SVG  = r"C:\Users\Admin\Music\scripts\avi-ascii-updated.svg"
OUTPUT_SVG = r"C:\Users\Admin\Music\scripts\avi-ascii-binary.svg"

# ── colours ─────────────────────────────────────────────────────────────────
BG_COLOR    = "#0d1117"   # dark background
WHITE_COLOR = "#ffffff"   # 0  → white (space)
GREEN_COLOR = "#00ff41"   # 1  → bright matrix green (non-space)
GLOW_COLOR  = "#00ff41"

# ── parse the source SVG ────────────────────────────────────────────────────
tree = ET.parse(INPUT_SVG)
root = tree.getroot()
NS   = "http://www.w3.org/2000/svg"

SVG_W  = int(root.get("width",  840))
SVG_H  = int(root.get("height", 875))

# collect every <text> row that carries ASCII art
# they all share: x="20", textLength="800", font-size="12.9"
rows = []   # list of (y_baseline, text_content)

for text_el in root.iter(f"{{{NS}}}text"):
    tl = text_el.get("textLength")
    fs = text_el.get("font-size")
    if tl == "800" and fs == "12.9":
        y    = float(text_el.get("y", 0))
        content = (text_el.text or "")
        rows.append((y, content))

rows.sort(key=lambda r: r[0])
print(f"Found {len(rows)} ASCII rows")

# ── build the output SVG ────────────────────────────────────────────────────
# We keep the same canvas, same font, same row positions.
# Each row's text is split into individual characters rendered with tspan or
# rendered as two tspan groups: spaces in white, non-spaces in green.
# For simplicity we render each character as a separate <text> element
# positioned at the correct x offset.

# monospace char width in SVG user units
CHAR_WIDTH = 800 / 100   # textLength=800 over 100 columns → 8 px per char
X_ORIGIN   = 20
FONT_SIZE  = 12.9
FONT_FAMILY = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
ROW_HEIGHT = 15

def build_svg():
    lines = []
    lines.append(f"""<?xml version='1.0' encoding='utf-8'?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{SVG_W}" height="{SVG_H}"
     viewBox="0 0 {SVG_W} {SVG_H}"
     font-family="{FONT_FAMILY}">
  <defs>
    <filter id="greenGlow">
      <feGaussianBlur stdDeviation="1.5" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>

  <!-- background -->
  <rect width="{SVG_W}" height="{SVG_H}" rx="12" fill="{BG_COLOR}"/>

  <!-- title bar -->
  <rect x="0.5" y="0.5" width="{SVG_W-1}" height="{SVG_H-1}" rx="12"
        fill="none" stroke="#808080" stroke-width="2" opacity="0.6"/>
  <line x1="0" y1="30" x2="{SVG_W}" y2="30" stroke="#30363d"/>
  <circle cx="20" cy="15" r="5" fill="#ff5f56"/>
  <circle cx="36" cy="15" r="5" fill="#ffbd2e"/>
  <circle cx="52" cy="15" r="5" fill="#808080" opacity="0.8"/>
  <text x="{SVG_W/2}" y="19" fill="#7d8590" font-size="12"
        text-anchor="middle">avi@github: ~$ ./portrait.sh</text>
""")

    # ── ASCII rows ───────────────────────────────────────────────────────────
    for y_base, content in rows:
        # Pad / trim to exactly 100 chars so spacing is predictable
        content = content.ljust(100)[:100]

        # Build run-length spans: group consecutive same-type chars
        segments = []   # (start_idx, text, is_space)
        i = 0
        while i < len(content):
            ch = content[i]
            is_sp = (ch == ' ')
            j = i
            while j < len(content) and (content[j] == ' ') == is_sp:
                j += 1
            segments.append((i, content[i:j], is_sp))
            i = j

        # open a <text> group for this row
        lines.append(f'  <text xml:space="preserve" y="{y_base}" '
                      f'font-size="{FONT_SIZE}" '
                      f'textLength="800" lengthAdjust="spacing">')

        for seg_i, (col, seg_text, is_sp) in enumerate(segments):
            x_pos = X_ORIGIN + col * CHAR_WIDTH
            color = WHITE_COLOR if is_sp else GREEN_COLOR
            filt  = '' if is_sp else ' filter="url(#greenGlow)"'
            esc   = seg_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            lines.append(
                f'    <tspan x="{x_pos:.2f}"{filt} fill="{color}">{esc}</tspan>'
            )

        lines.append('  </text>')

    # ── footer ───────────────────────────────────────────────────────────────
    footer_y = SVG_H - 43
    lines.append(f"""
  <line x1="0" y1="{footer_y}" x2="{SVG_W}" y2="{footer_y}" stroke="#30363d"/>
  <text x="20" y="{footer_y+19}" fill="#7d8590" font-size="13">
    avi@github:~$ whoami <tspan fill="{GREEN_COLOR}">Avi Vashishta</tspan>
  </text>
  <!-- blinking cursor -->
  <rect x="216" y="{footer_y+7}" width="8" height="14" fill="{GREEN_COLOR}">
    <animate attributeName="opacity" values="1;1;0;0"
             keyTimes="0;0.5;0.51;1" dur="1s" repeatCount="indefinite"/>
  </rect>
</svg>""")

    return "\n".join(lines)

svg_content = build_svg()

with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
    f.write(svg_content)

print(f"✓ Written: {OUTPUT_SVG}")

# ── also produce a pretty HTML viewer ───────────────────────────────────────
HTML_OUT = r"C:\Users\Admin\Music\scripts\avi-ascii-binary.html"

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Binary ASCII Portrait — Avi Vashishta</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background: #000;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      font-family: 'Segoe UI', sans-serif;
    }}
    h1 {{
      color: #00ff41;
      font-size: 1rem;
      letter-spacing: .25em;
      text-transform: uppercase;
      margin-bottom: 1rem;
      opacity: .6;
    }}
    .legend {{
      display: flex;
      gap: 2rem;
      margin-bottom: 1.2rem;
      font-size: .85rem;
    }}
    .legend span {{
      display: flex;
      align-items: center;
      gap: .5rem;
    }}
    .swatch {{
      width: 16px;
      height: 16px;
      border: 1px solid #333;
      border-radius: 3px;
    }}
    .zero  {{ background: #ffffff; }}
    .one   {{ background: #00ff41; box-shadow: 0 0 6px #00ff41; }}
    .label {{ color: #888; }}
    img {{
      max-width: 90vw;
      border-radius: 12px;
      box-shadow: 0 0 60px rgba(0,255,65,.25);
    }}
  </style>
</head>
<body>
  <h1>Binary Portrait — 0 = White · 1 = Green</h1>
  <div class="legend">
    <span><div class="swatch zero"></div><span class="label">0 = space (white)</span></span>
    <span><div class="swatch one"></div><span class="label">1 = character (green)</span></span>
  </div>
  <img src="avi-ascii-binary.svg" alt="Binary ASCII Portrait">
</body>
</html>"""

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✓ HTML viewer: {HTML_OUT}")
