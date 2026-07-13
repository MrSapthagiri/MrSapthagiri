#!/usr/bin/env python3
"""Create white/green binary version"""

import xml.etree.ElementTree as ET

# Update original SVG - remove green accents
svg_file = 'avi-ascii.svg'
tree = ET.parse(svg_file)
root = tree.getroot()

# Remove green accents (#00ff00 -> #808080)
for elem in root.iter():
    for attr in ['stroke', 'fill', 'flood-color']:
        if elem.get(attr) == '#00ff00':
            elem.set(attr, '#808080')

tree.write('avi-ascii-updated.svg', encoding='utf-8', xml_declaration=True)
print('✓ Updated SVG with green accents removed')

# Read binary portrait
with open('binary-portrait.txt', 'r') as f:
    binary_text = f.read()

# Create white/green HTML
html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Binary Portrait - White (0) & Green (1)</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            background: #0d1117;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Courier New', monospace;
            padding: 20px;
        }
        .container {
            background: #0d1117;
            border: 2px solid #808080;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.1);
            max-width: 900px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #808080;
            padding-bottom: 15px;
        }
        .header h1 {
            color: #ffffff;
            margin-bottom: 5px;
        }
        .color-legend {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            border-radius: 3px;
        }
        .white {
            background: #ffffff;
        }
        .green {
            background: #00ff00;
        }
        .portrait {
            font-size: 11px;
            line-height: 1.2;
            letter-spacing: 0.5px;
            overflow-x: auto;
            white-space: pre;
            color: #ffffff;
            background: #0a0e27;
            padding: 20px;
            border-radius: 6px;
            margin: 20px 0;
        }
        .zero {
            color: #ffffff;
        }
        .one {
            color: #00ff00;
            font-weight: bold;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 20px;
            text-align: center;
        }
        .stat {
            padding: 15px;
            background: #161b22;
            border-radius: 6px;
            border-left: 3px solid #808080;
        }
        .stat-value {
            font-size: 20px;
            font-weight: bold;
            color: #00ff00;
        }
        .stat-label {
            font-size: 12px;
            color: #8b949e;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔢 Binary Portrait</h1>
            <p style="color: #8b949e; margin-top: 5px;">Encoded in 0s and 1s | White & Green</p>
        </div>

        <div class="color-legend">
            <div class="legend-item">
                <div class="legend-color white"></div>
                <span style="color: #ffffff;"><code>0</code> = Sparse (White)</span>
            </div>
            <div class="legend-item">
                <div class="legend-color green"></div>
                <span style="color: #00ff00;"><code>1</code> = Dense (Green)</span>
            </div>
        </div>

        <div class="portrait" id="portrait">'''

# Add colored binary
for line in binary_text.split('\n'):
    for char in line:
        if char == '0':
            html_content += f'<span class="zero">{char}</span>'
        elif char == '1':
            html_content += f'<span class="one">{char}</span>'
        else:
            html_content += char
    html_content += '\n'

ones = binary_text.count('1')
zeros = binary_text.count('0')
total = ones + zeros

html_content += f'''</div>

        <div class="stats">
            <div class="stat">
                <div class="stat-value">{total:,}</div>
                <div class="stat-label">Total Pixels</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #00ff00;">{ones}</div>
                <div class="stat-label">Ones (1) - {(ones/total*100):.1f}%</div>
            </div>
            <div class="stat">
                <div class="stat-value" style="color: #ffffff;">{zeros}</div>
                <div class="stat-label">Zeros (0) - {(zeros/total*100):.1f}%</div>
            </div>
        </div>
    </div>
</body>
</html>'''

with open('binary-portrait-white-green.html', 'w') as f:
    f.write(html_content)

print('✓ Created binary-portrait-white-green.html with white/green colors')
print(f'\n✨ Binary Portrait Stats:')
print(f'   Total: {total:,} pixels')
print(f'   Ones (1):  {ones:3d} ({ones/total*100:5.1f}%)')
print(f'   Zeros (0): {zeros:3d} ({zeros/total*100:5.1f}%)')
