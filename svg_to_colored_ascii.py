#!/usr/bin/env python3
"""
SVG ASCII Art to Colored ASCII Converter
Converts SVG ASCII art with colors to multiple output formats:
- ANSI terminal colored text (.txt)
- GitHub README compatible markdown (.md)
- Plain text with color codes (.ansi)
"""

import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
import html

class SVGToColoredASCII:
    """Convert SVG ASCII art to colored ASCII formats"""
    
    # ANSI color codes
    ANSI_RESET = "\033[0m"
    ANSI_BOLD = "\033[1m"
    
    # Default color palette (GitHub dark theme)
    COLOR_MAP = {
        "#00ff00": ("2", "82"),      # Bright green (main accent)
        "#c9d1d9": ("7", "97"),      # Light gray (text)
        "#7d8590": ("8", "90"),      # Dark gray (dimmed)
        "#30363d": ("8", "234"),     # Very dark gray (frame)
        "#111722": ("0", "16"),      # Almost black
        "#0d1117": ("0", "234"),     # Black
        "#ff5f56": ("1", "91"),      # Red (close button)
        "#ffbd2e": ("3", "93"),      # Yellow (close button)
    }
    
    def __init__(self, svg_path: str):
        """Initialize converter with SVG file"""
        self.svg_path = Path(svg_path)
        self.text_elements = []
        self.colors_used = set()
        self.width = 0
        self.height = 0
        
    def parse_svg(self) -> bool:
        """Parse SVG and extract text elements with colors"""
        try:
            tree = ET.parse(self.svg_path)
            root = tree.getroot()
            
            # Get SVG dimensions
            self.width = int(root.get('width', '840'))
            self.height = int(root.get('height', '875'))
            
            # Register namespace
            ns = {'svg': 'http://www.w3.org/2000/svg'}
            
            # Extract all text elements
            for text_elem in root.findall('.//svg:text', ns):
                x = float(text_elem.get('x', '0'))
                y = float(text_elem.get('y', '0'))
                fill = text_elem.get('fill', '#c9d1d9')
                content = text_elem.text or ""
                
                if content.strip():  # Only process non-empty text
                    self.text_elements.append({
                        'x': x,
                        'y': y,
                        'fill': fill,
                        'content': content,
                        'text': content.rstrip()
                    })
                    self.colors_used.add(fill)
            
            return len(self.text_elements) > 0
            
        except Exception as e:
            print(f"Error parsing SVG: {e}", file=sys.stderr)
            return False
    
    @staticmethod
    def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_brightness(r: int, g: int, b: int) -> float:
        """Calculate brightness (0-1) for RGB color"""
        return (r * 0.299 + g * 0.587 + b * 0.114) / 255
    
    def get_ansi_color(self, hex_color: str) -> str:
        """Get ANSI color code for hex color"""
        if hex_color in self.COLOR_MAP:
            _, ansi_code = self.COLOR_MAP[hex_color]
            return f"\033[38;5;{ansi_code}m"
        
        # Convert hex to RGB and calculate closest ANSI color
        r, g, b = self.hex_to_rgb(hex_color)
        # For bright green accent
        if r == 0 and g == 255 and b == 0:
            return f"\033[38;5;82m"  # Bright green
        # For light colors
        elif r + g + b > 500:
            return f"\033[38;5;97m"  # Bright white
        # For dark colors
        else:
            return f"\033[38;5;90m"  # Dark gray
    
    def generate_ansi_output(self) -> str:
        """Generate ANSI colored terminal output"""
        lines = []
        
        # Add title
        lines.append(f"{self.get_ansi_color('#7d8590')}avi@github: ~$ ./portrait.sh{self.ANSI_RESET}\n")
        lines.append("")
        
        # Sort text elements by Y position
        sorted_elements = sorted(self.text_elements, key=lambda x: x['y'])
        
        current_y = 0
        for elem in sorted_elements:
            y = int(elem['y'])
            
            # Add empty lines if needed
            while current_y < y:
                lines.append("")
                current_y += 1
            
            # Add colored text
            color_code = self.get_ansi_color(elem['fill'])
            text = elem['content'].rstrip('\n')
            
            # Replace spaces with appropriate density
            colored_line = f"{color_code}{text}{self.ANSI_RESET}"
            lines.append(colored_line)
            current_y = y + 1
        
        return "\n".join(lines)
    
    def generate_html_output(self) -> str:
        """Generate HTML colored output (for GitHub README)"""
        html_lines = ['<pre><code class="language-ansi">']
        
        # Sort text elements by Y position
        sorted_elements = sorted(self.text_elements, key=lambda x: x['y'])
        
        current_y = 0
        for elem in sorted_elements:
            y = int(elem['y'])
            
            # Add empty lines if needed
            while current_y < y:
                html_lines.append("")
                current_y += 1
            
            # Add colored text with HTML span
            hex_color = elem['fill']
            text = elem['content'].rstrip('\n')
            
            # Escape HTML
            text = html.escape(text)
            
            # Create styled span
            if hex_color == '#00ff00':
                span = f'<span style="color: #00ff00; font-weight: bold;">{text}</span>'
            elif hex_color == '#c9d1d9':
                span = f'<span style="color: #c9d1d9;">{text}</span>'
            elif hex_color == '#7d8590':
                span = f'<span style="color: #7d8590;">{text}</span>'
            else:
                span = f'<span style="color: {hex_color};">{text}</span>'
            
            html_lines.append(span)
            current_y = y + 1
        
        html_lines.append('</code></pre>')
        return "\n".join(html_lines)
    
    def generate_markdown_output(self) -> str:
        """Generate GitHub README markdown version"""
        markdown = ['```ansi\n']
        
        # Sort text elements by Y position
        sorted_elements = sorted(self.text_elements, key=lambda x: x['y'])
        
        current_y = 0
        for elem in sorted_elements:
            y = int(elem['y'])
            
            # Add empty lines if needed
            while current_y < y:
                markdown.append("")
                current_y += 1
            
            # Add colored text using ANSI codes (works in GitHub markdown)
            color_code = self.get_ansi_color(elem['fill'])
            text = elem['content'].rstrip('\n')
            
            colored_line = f"{color_code}{text}{self.ANSI_RESET}"
            markdown.append(colored_line)
            current_y = y + 1
        
        markdown.append('```\n')
        return "\n".join(markdown)
    
    def generate_plain_ascii(self) -> str:
        """Generate plain ASCII without colors"""
        lines = []
        
        # Add title
        lines.append("avi@github: ~$ ./portrait.sh\n")
        lines.append("")
        
        # Sort text elements by Y position
        sorted_elements = sorted(self.text_elements, key=lambda x: x['y'])
        
        current_y = 0
        for elem in sorted_elements:
            y = int(elem['y'])
            
            # Add empty lines if needed
            while current_y < y:
                lines.append("")
                current_y += 1
            
            # Add plain text
            text = elem['content'].rstrip('\n')
            lines.append(text)
            current_y = y + 1
        
        return "\n".join(lines)
    
    def convert_to_brightness_chars(self, text: str) -> str:
        """Convert text to brightness-based characters (optional)"""
        # Character density palette: light to dark
        chars = [' ', '.', ':', '-', '=', '+', '*', '#', '@']
        
        result = []
        for char in text:
            if char == ' ':
                result.append(' ')
            elif char == '\t':
                result.append('    ')
            else:
                # Use density-based character representation
                result.append(char)
        
        return ''.join(result)
    
    def save_outputs(self, output_dir: str = None) -> Dict[str, str]:
        """Generate and save all output formats"""
        if output_dir is None:
            output_dir = self.svg_path.parent
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        # Generate outputs
        ansi_output = self.generate_ansi_output()
        html_output = self.generate_html_output()
        markdown_output = self.generate_markdown_output()
        plain_output = self.generate_plain_ascii()
        
        # Save ANSI colored text file
        ansi_file = output_path / "portrait-colored.txt"
        with open(ansi_file, 'w', encoding='utf-8') as f:
            f.write(ansi_output)
        results['ansi_txt'] = str(ansi_file)
        
        # Save HTML version
        html_file = output_path / "portrait-colored.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ASCII Portrait</title>
    <style>
        body {{
            background-color: #0d1117;
            color: #c9d1d9;
            font-family: 'SFMono-Regular', Menlo, Consolas, monospace;
            padding: 20px;
        }}
        pre {{
            background-color: #161b22;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #30363d;
            overflow-x: auto;
        }}
        code {{
            font-size: 12px;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    {html_output}
</body>
</html>
""")
        results['html'] = str(html_file)
        
        # Save markdown version
        md_file = output_path / "portrait-colored.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"""# ASCII Portrait

## Terminal Display

{markdown_output}

## Info

- **Format**: Colored ASCII Art
- **Colors**: Green accent (#00ff00), GitHub dark theme
- **Terminal Compatible**: ANSI color codes
- **Markdown Compatible**: Works in GitHub README

### Display in GitHub README

Copy the code block below to your README.md:

```markdown
{markdown_output}
```
""")
        results['markdown'] = str(md_file)
        
        # Save plain ASCII
        plain_file = output_path / "portrait-plain.txt"
        with open(plain_file, 'w', encoding='utf-8') as f:
            f.write(plain_output)
        results['plain'] = str(plain_file)
        
        return results


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        svg_file = r"c:\Users\Admin\Music\scripts\avi-ascii.svg"
    else:
        svg_file = sys.argv[1]
    
    print(f"Converting SVG: {svg_file}")
    print("=" * 60)
    
    converter = SVGToColoredASCII(svg_file)
    
    if not converter.parse_svg():
        print("Error: Failed to parse SVG file")
        sys.exit(1)
    
    print(f"✓ Found {len(converter.text_elements)} text elements")
    print(f"✓ Colors used: {', '.join(converter.colors_used)}")
    print()
    
    # Generate and save outputs
    results = converter.save_outputs()
    
    print("Generated Output Files:")
    print("-" * 60)
    for format_name, filepath in results.items():
        file_size = Path(filepath).stat().st_size
        print(f"✓ {format_name.upper():15} → {Path(filepath).name:25} ({file_size:,} bytes)")
    
    print()
    print("=" * 60)
    print("Conversion complete!")
    print()
    print("To use in GitHub README:")
    print("1. Copy the colored ASCII from portrait-colored.md")
    print("2. Paste into your README.md file")
    print("3. The colors will display in terminal")
    

if __name__ == "__main__":
    main()
