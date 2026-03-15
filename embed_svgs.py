#!/usr/bin/env python3
"""Embed SVG files as base64 data URIs in APNA-Whitepaper.html so they render in PDF."""
import base64
import re

HTML_PATH = "APNA-Whitepaper.html"
SVGS = [
    ("infographic-morphing-flow.svg", r'<img src="infographic-morphing-flow\.svg"[^>]*>'),
    ("infographic-transition-decision.svg", r'<img src="infographic-transition-decision\.svg"[^>]*>'),
    ("infographic-topologies.svg", r'<img src="infographic-topologies\.svg"[^>]*>'),
    ("infographic-morphing.svg", r'<img src="infographic-morphing\.svg"[^>]*>'),
]

def main():
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    for filename, _ in SVGS:
        with open(filename, "rb") as f:
            svg_bytes = f.read()
        b64 = base64.b64encode(svg_bytes).decode("ascii")
        data_uri = f"data:image/svg+xml;base64,{b64}"
        # Replace src="filename" with data URI (keep rest of tag)
        html = html.replace(f'src="{filename}"', f'src="{data_uri}"', 1)

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print("Embedded all 4 SVGs into HTML.")

if __name__ == "__main__":
    main()
