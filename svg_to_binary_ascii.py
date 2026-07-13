#!/usr/bin/env python3
"""
Convert SVG ASCII art to binary representation (0s and 1s)
with customizable colors
"""

import xml.etree.ElementTree as ET
from pathlib import Path


class SVGToBinaryASCII:
    def __init__(self, svg_file):
        self.svg_file = svg_file
        self.tree = ET.parse(svg_file)
        self.root = self.tree.getroot()
        self.ns = {'svg': 'http://www.w3.org/2000/svg'}
        
        # Character brightness mapping (sparse = 0, dense = 1)
        self.char_brightness = {
            ' ': 0,  # space
            '.': 0.1, ',': 0.1, ':': 0.2,
            ';': 0.2, '!': 0.3, '?': 0.3,
            '-': 0.3, '_': 0.3, '+': 0.4,
            '*': 0.5, '#': 0.7, '@': 0.9,
            '█': 1, '▓': 0.8, '▒': 0.6, '░': 0.3,
        }
        
        # Color configurations
        self.color_schemes = {
            'blue_red': {
                'bg': '#0d1117',          # Dark background
                'border': '#0066ff',      # Blue border
                'glow': '#0066ff',        # Blue glow
                'color0': '#ff1744',      # Red for 0s
                'color1': '#0066ff',      # Blue for 1s
            },
            'purple_cyan': {
                'bg': '#0d1117',
                'border': '#9c27b0',
                'glow': '#9c27b0',
                'color0': '#ff1744',
                'color1': '#00e5ff',
            },
            'orange_purple': {
                'bg': '#0d1117',
                'border': '#ff6f00',
                'glow': '#ff6f00',
                'color0': '#9c27b0',
                'color1': '#ff6f00',
            },
            'green_pink': {
                'bg': '#0d1117',
                'border': '#00ff00',
                'glow': '#00ff00',
                'color0': '#ff1744',
                'color1': '#00ff00',
            }
        }
    
    def get_brightness(self, char):
        """Get brightness value for a character (0-1)"""
        if char in self.char_brightness:
            return self.char_brightness[char]
        elif char.isdigit():
            return 0.4
        elif char.isalpha():
            return 0.5
        elif char in '()[]{}':
            return 0.4
        else:
            return 0.3
    
    def char_to_binary(self, char):
        """Convert character to 0 or 1 based on brightness"""
        brightness = self.get_brightness(char)
        return '1' if brightness > 0.4 else '0'
    
    def extract_text_elements(self):
        """Extract all text elements from SVG"""
        texts = []
        for text_elem in self.root.findall('.//svg:text', self.ns):
            content = text_elem.text if text_elem.text else ''
            y = text_elem.get('y', '0')
            x = text_elem.get('x', '0')
            fill = text_elem.get('fill', '#c9d1d9')
            texts.append({
                'content': content,
                'x': float(x),
                'y': float(y),
                'fill': fill,
                'element': text_elem
            })
        return sorted(texts, key=lambda t: t['y'])
    
    def convert_to_binary(self):
        """Convert text content to binary (0s and 1s)"""
        text_elements = self.extract_text_elements()
        
        for item in text_elements:
            original = item['content']
            binary = ''.join(self.char_to_binary(c) for c in original)
            item['element'].text = binary
    
    def update_colors(self, scheme='blue_red'):
        """Update SVG colors to new scheme"""
        colors = self.color_schemes.get(scheme, self.color_schemes['blue_red'])
        
        # Update background gradient
        for stop in self.root.findall('.//svg:stop', self.ns):
            stop_color = stop.get('stop-color')
            if stop_color in ['#111722', '#0d1117']:
                stop.set('stop-color', colors['bg'])
        
        # Update borders and accents
        for rect in self.root.findall('.//svg:rect', self.ns):
            stroke = rect.get('stroke')
            if stroke == '#00ff00':
                rect.set('stroke', colors['border'])
        
        for line in self.root.findall('.//svg:line', self.ns):
            stroke = line.get('stroke')
            if stroke == '#00ff00':
                line.set('stroke', colors['border'])
        
        # Update glow filter
        for flood in self.root.findall('.//svg:feFlood', self.ns):
            current_color = flood.get('flood-color')
            if current_color == '#00ff00':
                flood.set('flood-color', colors['glow'])
        
        # Update text colors (0s vs 1s)
        text_elements = self.extract_text_elements()
        for item in text_elements:
            binary_content = item['element'].text
            if binary_content:
                # Create tspan elements for alternating colors
                item['element'].clear()
                for i, char in enumerate(binary_content):
                    tspan = ET.Element('tspan')
                    tspan.text = char
                    if char == '0':
                        tspan.set('fill', colors['color0'])
                    else:
                        tspan.set('fill', colors['color1'])
                    item['element'].append(tspan)
    
    def save_binary_svg(self, output_file, scheme='blue_red'):
        """Save binary SVG with new colors"""
        self.convert_to_binary()
        self.update_colors(scheme)
        self.tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    def generate_binary_text(self):
        """Generate binary text version"""
        text_elements = self.extract_text_elements()
        binary_lines = []
        for item in text_elements:
            original = item['content']
            binary = ''.join(self.char_to_binary(c) for c in original)
            binary_lines.append(binary)
        return '\n'.join(binary_lines)
    
    def generate_binary_markdown(self):
        """Generate binary in markdown code block"""
        binary_text = self.generate_binary_text()
        return f'```\n{binary_text}\n```'
    
    def generate_binary_html(self, color0='#ff1744', color1='#0066ff'):
        """Generate standalone HTML with binary and colors"""
        binary_text = self.generate_binary_text()
        lines = binary_text.split('\n')
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Binary ASCII Portrait</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background: linear-gradient(180deg, #111722 0%, #0d1117 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Courier New', monospace;
            padding: 20px;
        }}
        .container {{
            background: #0d1117;
            border: 2px solid #0066ff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 102, 255, 0.3);
            max-width: 900px;
        }}
        .header {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #0066ff;
        }}
        .controls {{
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }}
        .controls button {{
            padding: 8px 16px;
            background: #0066ff;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-family: monospace;
            font-weight: bold;
        }}
        .controls button:hover {{
            background: #0052cc;
        }}
        .portrait {{
            font-size: 11px;
            line-height: 1.2;
            letter-spacing: 0.5px;
            overflow-x: auto;
            white-space: pre;
            color: #c9d1d9;
        }}
        .zero {{
            color: {color0};
        }}
        .one {{
            color: {color1};
        }}
        .controls-info {{
            color: #8b949e;
            font-size: 12px;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="color: #0066ff; margin-right: 20px;">Binary Portrait</h1>
            <span style="color: #8b949e;">Press 'C' to toggle colors | 'M' for monochrome</span>
        </div>
        <div class="controls">
            <button onclick="toggleColors()">Toggle Colors</button>
            <button onclick="downloadSVG()">Download SVG</button>
        </div>
        <div class="portrait" id="portrait">"""
        
        for line in lines:
            for char in line:
                if char == '0':
                    html += f'<span class="zero">{char}</span>'
                elif char == '1':
                    html += f'<span class="one">{char}</span>'
                else:
                    html += char
            html += '\n'
        
        html += """</div>
        <div class="controls-info">
            Total Characters: """ + str(len(binary_text)) + """<br>
            Ones (1): """ + str(binary_text.count('1')) + """ | Zeros (0): """ + str(binary_text.count('0')) + """
        </div>
    </div>
    
    <script>
        let colorMode = true;
        
        function toggleColors() {
            const portrait = document.getElementById('portrait');
            if (colorMode) {
                portrait.style.color = '#c9d1d9';
                document.querySelectorAll('.zero, .one').forEach(el => {
                    el.style.color = '#c9d1d9';
                });
                colorMode = false;
            } else {
                document.querySelectorAll('.zero').forEach(el => {
                    el.style.color = '{color0}';
                });
                document.querySelectorAll('.one').forEach(el => {
                    el.style.color = '{color1}';
                });
                colorMode = true;
            }
        }
        
        function downloadSVG() {{
            alert('Download SVG from binary-portrait-*.svg files');
        }}
        
        document.addEventListener('keydown', (e) => {{
            if (e.key.toLowerCase() === 'c') toggleColors();
        }});
    </script>
</body>
</html>"""
        return html


def main():
    """Main execution"""
    svg_file = 'avi-ascii.svg'
    
    if not Path(svg_file).exists():
        print(f"Error: {svg_file} not found")
        return
    
    print(f"Processing {svg_file}...")
    converter = SVGToBinaryASCII(svg_file)
    
    # Color schemes to generate
    schemes = ['blue_red', 'purple_cyan', 'orange_purple', 'green_pink']
    
    # Generate outputs for each scheme
    for scheme in schemes:
        # Binary SVG
        output_svg = f'binary-portrait-{scheme}.svg'
        converter.save_binary_svg(output_svg, scheme)
        print(f"✓ Created {output_svg}")
        
        # Reinitialize for next iteration
        converter = SVGToBinaryASCII(svg_file)
    
    # Generate text version (colorless)
    binary_text = converter.generate_binary_text()
    with open('binary-portrait.txt', 'w', encoding='utf-8') as f:
        f.write(binary_text)
    print(f"✓ Created binary-portrait.txt")
    
    # Generate markdown version
    binary_md = converter.generate_binary_markdown()
    with open('binary-portrait.md', 'w', encoding='utf-8') as f:
        f.write(f"# Binary ASCII Portrait\n\n{binary_md}")
    print(f"✓ Created binary-portrait.md")
    
    # Generate HTML version
    html = converter.generate_binary_html()
    with open('binary-portrait.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ Created binary-portrait.html")
    
    # Print statistics
    stats = f"""
╔═══════════════════════════════════╗
║   Binary ASCII Conversion Stats   ║
╚═══════════════════════════════════╝

Total Characters: {len(binary_text)}
Binary Ones (1): {binary_text.count('1')}
Binary Zeros (0): {binary_text.count('0')}
Ratio: {(binary_text.count('1') / len(binary_text) * 100):.1f}% ones

Generated Files:
├── binary-portrait.txt           (plain text)
├── binary-portrait.md            (markdown)
├── binary-portrait.html          (interactive web)
└── binary-portrait-[scheme].svg  (4 color schemes)
    ├── blue_red
    ├── purple_cyan
    ├── orange_purple
    └── green_pink
"""
    print(stats)


if __name__ == '__main__':
    main()
