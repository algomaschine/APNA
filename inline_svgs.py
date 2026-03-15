#!/usr/bin/env python3
"""Inline SVG files into APNA-Whitepaper.html with unique ID prefixes so PDF renders all diagrams.
Run from repo root: python scripts/inline_svgs.py"""
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WHITEPAPER_DIR = REPO_ROOT / "whitepaper"
HTML_PATH = WHITEPAPER_DIR / "APNA-Whitepaper.html"


def prefix_svg(svg_content, prefix):
    ids = set(re.findall(r'\bid="([^"]+)"', svg_content))
    for i in ids:
        svg_content = svg_content.replace(f'id="{i}"', f'id="{prefix}-{i}"')
        svg_content = svg_content.replace(f'url(#{i})', f'url(#{prefix}-{i})')
    return svg_content.strip()


def main():
    files = [
        ("infographic-morphing-flow.svg", "flow"),
        ("infographic-transition-decision.svg", "dec"),
        ("infographic-topologies.svg", "topo"),
        ("infographic-morphing.svg", "morph"),
    ]
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    for filename, prefix in files:
        filepath = WHITEPAPER_DIR / filename
        with open(filepath, "r", encoding="utf-8") as f:
            svg = prefix_svg(f.read(), prefix)
        img_pattern = re.compile(
            r'<figure class="infographic">\s*<img\s+src="[^"]*"\s+alt="[^"]*"\s*/>',
            re.DOTALL
        )
        if img_pattern.search(html):
            replacement = f'<figure class="infographic">\n        <div class="infographic-svg">\n{svg}\n        </div>'
            html = img_pattern.sub(replacement, html, count=1)
        else:
            div_pattern = re.compile(
                r'(<div class="infographic-svg">)\s*\n(.*?)\n(\s*</div>)',
                re.DOTALL
            )
            replacement = f'\\1\n{svg}\n\\3'
            html = div_pattern.sub(replacement, html, count=1)

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("Inlined all 4 SVGs into HTML (whitepaper/APNA-Whitepaper.html).")


if __name__ == "__main__":
    main()
