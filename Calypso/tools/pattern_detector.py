#!/usr/bin/env python3
"""
Detect visual and structural patterns in PDF.
Identifies heading styles, layouts, and structures for HTML conversion.
"""

import json
import os
import re
import sys
from collections import defaultdict


def analyze_text_patterns(pdfplumber_data):
    """Analyze text patterns for heading detection."""
    patterns = {
        "headings": defaultdict(list),
        "text_blocks": defaultdict(int),
        "list_patterns": defaultdict(int),
        "code_blocks": defaultdict(int),
    }

    for page_num, page_data in sorted(pdfplumber_data.items()):
        if not isinstance(page_num, int):
            page_num = int(page_num)

        text = page_data.get("text", "")
        lines = text.split("\n")

        for line_num, line in enumerate(lines):
            stripped = line.strip()

            # Detect headings (single words or short lines in caps, numbers, etc.)
            if stripped and len(stripped) < 80:
                # H1-like: All caps, short
                if stripped.isupper() and len(stripped) > 3:
                    patterns["headings"]["h1_caps"].append(
                        {"page": page_num, "text": stripped}
                    )

                # H2-like: Numbered (Chapter, Section)
                if re.match(r"^(chapter|section|part|module)\s+\d+", stripped, re.IGNORECASE):
                    patterns["headings"]["h2_numbered"].append(
                        {"page": page_num, "text": stripped}
                    )

                # H3-like: Starts with number and dot
                if re.match(r"^\d+\.\s+", stripped):
                    patterns["headings"]["h3_dotted"].append(
                        {"page": page_num, "text": stripped}
                    )

            # Detect lists
            if re.match(r"^[-•*]\s+", stripped) or re.match(r"^\d+\)\s+", stripped):
                patterns["list_patterns"]["list_items"] += 1

            # Detect code blocks or monospace content
            if stripped.startswith("```") or re.match(r"^\s{4,}", stripped):
                patterns["code_blocks"]["indented_blocks"] += 1

            # Count text blocks
            if len(stripped) > 50:
                patterns["text_blocks"]["paragraphs"] += 1

    return dict(patterns)


def analyze_font_patterns(fitz_data):
    """Analyze font patterns to identify heading hierarchy."""
    font_hierarchy = defaultdict(lambda: {"sizes": [], "usage": 0, "pages": []})

    for page_num, page_data in fitz_data.items():
        fonts = page_data.get("fonts", {})

        for font_name, font_info in fonts.items():
            size = font_info.get("size", 0)
            count = font_info.get("count", 0)

            font_hierarchy[font_name]["sizes"].append(size)
            font_hierarchy[font_name]["usage"] += count
            if page_num not in font_hierarchy[font_name]["pages"]:
                font_hierarchy[font_name]["pages"].append(page_num)

    # Create hierarchy
    hierarchy = {
        "primary": None,  # Likely body text
        "heading_1": None,  # Largest font
        "heading_2": None,  # Second largest
        "heading_3": None,  # Third largest
    }

    # Sort by average size
    sorted_fonts = sorted(
        font_hierarchy.items(),
        key=lambda x: max(x[1]["sizes"]) if x[1]["sizes"] else 0,
        reverse=True,
    )

    for idx, (font_name, info) in enumerate(sorted_fonts[:4]):
        if idx == 0:
            hierarchy["heading_1"] = {
                "font": font_name,
                "avg_size": sum(info["sizes"]) / len(info["sizes"]),
                "usage": info["usage"],
            }
        elif idx == 1:
            hierarchy["heading_2"] = {
                "font": font_name,
                "avg_size": sum(info["sizes"]) / len(info["sizes"]),
                "usage": info["usage"],
            }
        elif idx == 2:
            hierarchy["heading_3"] = {
                "font": font_name,
                "avg_size": sum(info["sizes"]) / len(info["sizes"]),
                "usage": info["usage"],
            }
        elif idx == 3:
            hierarchy["primary"] = {
                "font": font_name,
                "avg_size": sum(info["sizes"]) / len(info["sizes"]),
                "usage": info["usage"],
            }

    return hierarchy


def detect_layout_patterns(pdfplumber_data, fitz_data):
    """Detect page layout patterns."""
    layouts = defaultdict(int)
    page_widths = []
    page_heights = []

    for page_num, page_data in pdfplumber_data.items():
        layout = page_data.get("layout", {})
        page_widths.append(layout.get("width", 0))
        page_heights.append(layout.get("height", 0))

        # Detect if it's a single or multi-column layout
        lines = page_data.get("layout", {}).get("lines", [])
        if lines:
            layouts["has_lines"] += 1

    # Calculate average dimensions
    avg_width = sum(page_widths) / len(page_widths) if page_widths else 0
    avg_height = sum(page_heights) / len(page_heights) if page_heights else 0

    return {
        "average_page_width": avg_width,
        "average_page_height": avg_height,
        "layout_elements": dict(layouts),
    }


def create_pattern_rules(text_patterns, font_hierarchy, layout_patterns):
    """Create conversion rules based on detected patterns."""
    rules = {
        "heading_rules": {},
        "text_rules": {},
        "layout_rules": {},
    }

    # Heading rules based on font hierarchy
    if font_hierarchy["heading_1"]:
        rules["heading_rules"]["h1"] = {
            "font": font_hierarchy["heading_1"]["font"],
            "size": font_hierarchy["heading_1"]["avg_size"],
            "also_match": "h1_caps",  # from text patterns
        }
    if font_hierarchy["heading_2"]:
        rules["heading_rules"]["h2"] = {
            "font": font_hierarchy["heading_2"]["font"],
            "size": font_hierarchy["heading_2"]["avg_size"],
            "also_match": "h2_numbered",
        }
    if font_hierarchy["heading_3"]:
        rules["heading_rules"]["h3"] = {
            "font": font_hierarchy["heading_3"]["font"],
            "size": font_hierarchy["heading_3"]["avg_size"],
            "also_match": "h3_dotted",
        }

    # Text rules
    rules["text_rules"]["paragraph"] = {
        "font": font_hierarchy["primary"]["font"] if font_hierarchy["primary"] else "default",
    }
    rules["text_rules"]["list"] = {
        "pattern": "^[-•*]\\s+|^\\d+\\)\\s+",
    }
    rules["text_rules"]["code"] = {
        "pattern": "^```|^\\s{4,}",
    }

    # Layout rules
    rules["layout_rules"]["page_size"] = layout_patterns
    rules["layout_rules"]["margins"] = {"default": 36}  # points

    return rules


def main():
    analysis_dir = "../analysis"

    # Load extracted data
    pdfplumber_file = os.path.join(analysis_dir, "pdfplumber_output.json")
    fitz_file = os.path.join(analysis_dir, "fitz_output.json")

    if not os.path.exists(pdfplumber_file):
        print(f"Error: pdfplumber_output.json not found. Run analysis_extractor.py first.")
        sys.exit(1)

    print("Loading analysis data...")
    with open(pdfplumber_file) as f:
        pdfplumber_data = json.load(f)

    fitz_data = {}
    if os.path.exists(fitz_file):
        with open(fitz_file) as f:
            fitz_data = json.load(f)

    print("Detecting text patterns...")
    text_patterns = analyze_text_patterns(pdfplumber_data)

    print("Analyzing font hierarchy...")
    font_hierarchy = analyze_font_patterns(fitz_data)

    print("Detecting layout patterns...")
    layout_patterns = detect_layout_patterns(pdfplumber_data, fitz_data)

    print("Creating conversion rules...")
    rules = create_pattern_rules(text_patterns, font_hierarchy, layout_patterns)

    # Save patterns and rules
    patterns_file = os.path.join(analysis_dir, "patterns.json")
    rules_file = os.path.join(analysis_dir, "conversion_rules.json")

    with open(patterns_file, "w") as f:
        json.dump(
            {
                "text_patterns": {k: v for k, v in text_patterns.items() if not isinstance(v, defaultdict)},
                "font_hierarchy": font_hierarchy,
                "layout_patterns": layout_patterns,
            },
            f,
            indent=2,
            default=str,
        )

    with open(rules_file, "w") as f:
        json.dump(rules, f, indent=2)

    print("\nPattern Detection Summary:")
    print(f"Text patterns detected: {len(text_patterns)}")
    print(f"Font hierarchy: {len([x for x in font_hierarchy.values() if x])}")
    print(f"Page dimensions: {layout_patterns['average_page_width']}x{layout_patterns['average_page_height']}")

    print(f"\nFiles saved:")
    print(f"  - {patterns_file}")
    print(f"  - {rules_file}")


if __name__ == "__main__":
    main()
