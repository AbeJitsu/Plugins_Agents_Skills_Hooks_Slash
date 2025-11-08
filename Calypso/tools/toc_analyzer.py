#!/usr/bin/env python3
"""
Analyze Table of Contents from extracted pages.
Identifies chapter boundaries and creates a chapter map.
"""

import json
import os
import re
import sys
from pathlib import Path


def analyze_pdfplumber_data(data):
    """Analyze pdfplumber output to find TOC patterns."""
    chapters = []
    toc_section = False

    for page_num, page_data in sorted(data.items()):
        if not isinstance(page_num, int):
            page_num = int(page_num)

        text = page_data.get("text", "")

        # Look for common TOC indicators
        if any(
            keyword in text.upper() for keyword in ["TABLE OF CONTENTS", "CONTENTS", "CHAPTERS"]
        ):
            toc_section = True
            print(f"Found TOC section at page {page_num}")

        if toc_section:
            # Look for chapter patterns (usually "Chapter X" or numbered entries)
            lines = text.split("\n")
            for line in lines:
                # Pattern: "Chapter 1" or "1." or similar
                chapter_match = re.search(
                    r"(?:chapter|ch\.?)\s*(\d+)[:\s]*([^0-9]*?)(?:\d+)?$",
                    line.strip(),
                    re.IGNORECASE,
                )
                if chapter_match:
                    chapter_num = int(chapter_match.group(1))
                    title = chapter_match.group(2).strip()
                    chapters.append(
                        {
                            "chapter": chapter_num,
                            "title": title,
                            "start_page": None,  # Will be determined later
                            "found_in_toc": page_num,
                        }
                    )

    return {
        "toc_section_found": toc_section,
        "chapters_found": chapters,
    }


def analyze_fonts(fitz_data):
    """Identify heading fonts by frequency and size."""
    font_stats = {}

    for page_num, page_data in fitz_data.items():
        fonts = page_data.get("fonts", {})
        for font_name, font_info in fonts.items():
            if font_name not in font_stats:
                font_stats[font_name] = {"sizes": set(), "total_count": 0}
            font_stats[font_name]["sizes"].add(font_info.get("size", 0))
            font_stats[font_name]["total_count"] += font_info.get("count", 0)

    # Sort by frequency
    sorted_fonts = sorted(font_stats.items(), key=lambda x: x[1]["total_count"], reverse=True)

    return {
        "font_analysis": [
            {
                "font": name,
                "sizes": list(info["sizes"]),
                "total_count": info["total_count"],
            }
            for name, info in sorted_fonts[:10]
        ]
    }


def create_chapter_map(pdfplumber_data, fitz_data):
    """Create a comprehensive chapter map from all analysis data."""
    toc_analysis = analyze_pdfplumber_data(pdfplumber_data)
    font_analysis = analyze_fonts(fitz_data)

    return {
        "toc_analysis": toc_analysis,
        "font_analysis": font_analysis,
        "analysis_summary": {
            "total_pages_analyzed": len(pdfplumber_data),
            "chapters_identified": len(toc_analysis.get("chapters_found", [])),
        },
    }


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

    print("Analyzing TOC structure...")
    chapter_map = create_chapter_map(pdfplumber_data, fitz_data)

    # Save chapter map
    output_file = os.path.join(analysis_dir, "chapter_map.json")
    with open(output_file, "w") as f:
        json.dump(chapter_map, f, indent=2)

    print(f"\nChapter Map Analysis:")
    print(f"Total pages analyzed: {chapter_map['analysis_summary']['total_pages_analyzed']}")
    print(f"Chapters identified: {chapter_map['analysis_summary']['chapters_identified']}")

    if chapter_map["toc_analysis"]["chapters_found"]:
        print("\nChapters found:")
        for chapter in chapter_map["toc_analysis"]["chapters_found"]:
            print(f"  - Chapter {chapter['chapter']}: {chapter['title']}")

    print(f"\nTop fonts (likely for headings):")
    for font_info in chapter_map["font_analysis"]["font_analysis"][:5]:
        print(f"  - {font_info['font']} (sizes: {font_info['sizes']}, count: {font_info['total_count']})")

    print(f"\nChapter map saved to: {output_file}")


if __name__ == "__main__":
    main()
