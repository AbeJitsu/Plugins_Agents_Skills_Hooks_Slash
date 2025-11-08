#!/usr/bin/env python3
"""
Analyze visual patterns in a PDF page.
Extracts positioning, fonts, layout, and visual elements for pattern learning.
Focus: Chapter 1, Page 6 (first page of first numbered chapter)
"""

import json
import os
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError as e:
    print(f"Error: Missing required library: {e}")
    sys.exit(1)


def extract_page_image(pdf_path, page_num, output_dir):
    """Convert PDF page to high-res PNG image."""
    try:
        images = convert_from_path(pdf_path, first_page=page_num + 1, last_page=page_num + 1, dpi=300)
        if images:
            image_path = os.path.join(output_dir, f"page_{page_num:03d}_hires.png")
            images[0].save(image_path, "PNG")
            print(f"✓ Saved high-res image: {image_path}")
            return image_path
    except Exception as e:
        print(f"✗ Error converting page to image: {e}")
    return None


def extract_text_blocks_with_positions(pdf_path, page_num):
    """Extract text blocks with font, size, and position information."""
    text_blocks = []

    try:
        pdf = fitz.open(pdf_path)
        page = pdf[page_num]

        # Get detailed text with positions
        text_dict = page.get_text("dict")

        page_height = page.rect.height
        page_width = page.rect.width

        if "blocks" in text_dict:
            block_num = 0
            for block in text_dict["blocks"]:
                if block.get("type") == 0:  # Text block
                    block_num += 1
                    block_text = ""
                    block_bbox = block.get("bbox", (0, 0, page_width, page_height))

                    fonts_in_block = set()
                    sizes_in_block = set()

                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                block_text += span.get("text", "")
                                fonts_in_block.add(span.get("font", "unknown"))
                                sizes_in_block.add(span.get("size", 0))

                    if block_text.strip():
                        text_blocks.append({
                            "block_num": block_num,
                            "text": block_text.strip()[:200],  # First 200 chars
                            "position": {
                                "x": round(block_bbox[0], 2),
                                "y": round(block_bbox[1], 2),
                                "width": round(block_bbox[2] - block_bbox[0], 2),
                                "height": round(block_bbox[3] - block_bbox[1], 2),
                            },
                            "fonts": sorted(list(fonts_in_block)),
                            "sizes": sorted(list(sizes_in_block)),
                        })

        pdf.close()
    except Exception as e:
        print(f"✗ Error extracting text blocks: {e}")

    return text_blocks


def extract_page_layout_metrics(pdf_path, page_num):
    """Extract page layout metrics: margins, dimensions, columns."""
    metrics = {}

    try:
        pdf = fitz.open(pdf_path)
        page = pdf[page_num]

        page_width = page.rect.width
        page_height = page.rect.height

        # Get text blocks to estimate margins
        text_dict = page.get_text("dict")
        min_x, min_y, max_x, max_y = page_width, page_height, 0, 0

        if "blocks" in text_dict:
            for block in text_dict["blocks"]:
                if block.get("type") == 0:  # Text block
                    bbox = block.get("bbox")
                    if bbox:
                        min_x = min(min_x, bbox[0])
                        min_y = min(min_y, bbox[1])
                        max_x = max(max_x, bbox[2])
                        max_y = max(max_y, bbox[3])

        metrics = {
            "page_dimensions": {
                "width": round(page_width, 2),
                "height": round(page_height, 2),
            },
            "estimated_margins": {
                "left": round(min_x, 2),
                "top": round(min_y, 2),
                "right": round(page_width - max_x, 2),
                "bottom": round(page_height - max_y, 2),
            },
            "content_area": {
                "width": round(max_x - min_x, 2),
                "height": round(max_y - min_y, 2),
            },
        }

        pdf.close()
    except Exception as e:
        print(f"✗ Error extracting layout metrics: {e}")

    return metrics


def analyze_heading_hierarchy(text_blocks):
    """Analyze text blocks to identify heading hierarchy by font size."""
    if not text_blocks:
        return {}

    # Group blocks by font sizes
    size_groups = {}
    for block in text_blocks:
        for size in block.get("sizes", []):
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(block)

    # Sort sizes (largest fonts are likely headings)
    sorted_sizes = sorted(size_groups.keys(), reverse=True)

    hierarchy = {}
    for i, size in enumerate(sorted_sizes[:4]):  # Top 4 font sizes
        blocks = size_groups[size]
        hierarchy[f"level_{i}"] = {
            "font_size": size,
            "count": len(blocks),
            "examples": [b["text"][:50] for b in blocks[:2]],
        }

    return hierarchy


def detect_visual_elements(pdf_path, page_num):
    """Detect visual elements: lines, rectangles, images."""
    elements = {
        "lines": [],
        "rectangles": [],
        "images": [],
    }

    try:
        pdf = fitz.open(pdf_path)
        page = pdf[page_num]

        # Get all drawing objects
        for item in page.get_drawings():
            if item.type == "l":  # Line
                elements["lines"].append({
                    "start": (round(item.p1.x, 2), round(item.p1.y, 2)),
                    "end": (round(item.p2.x, 2), round(item.p2.y, 2)),
                })
            elif item.type == "c":  # Rectangle
                elements["rectangles"].append({
                    "bbox": (round(item.x0, 2), round(item.y0, 2), round(item.x1, 2), round(item.y1, 2)),
                })

        # Check for images
        image_list = page.get_images()
        elements["images"] = [{"count": len(image_list), "note": f"Found {len(image_list)} images"}]

        pdf.close()
    except Exception as e:
        print(f"✗ Error detecting visual elements: {e}")

    return elements


def main():
    pdf_path = "../../PREP-AL 4th Ed 9-26-25.pdf"
    output_dir = "../analysis"
    page_num = 6  # First page of Chapter 1

    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"PAGE PATTERN ANALYSIS - Chapter 1, Page {page_num}")
    print(f"{'='*60}\n")

    # 1. Extract page as image
    print("1. Extracting page as high-resolution image...")
    image_path = extract_page_image(pdf_path, page_num, output_dir)

    # 2. Extract text blocks with positions
    print("\n2. Extracting text blocks with positioning...")
    text_blocks = extract_text_blocks_with_positions(pdf_path, page_num)
    print(f"✓ Found {len(text_blocks)} text blocks")

    # 3. Extract layout metrics
    print("\n3. Analyzing page layout metrics...")
    layout_metrics = extract_page_layout_metrics(pdf_path, page_num)

    # 4. Analyze heading hierarchy
    print("\n4. Analyzing heading hierarchy by font size...")
    heading_hierarchy = analyze_heading_hierarchy(text_blocks)

    # 5. Detect visual elements
    print("\n5. Detecting visual elements (lines, boxes, images)...")
    visual_elements = detect_visual_elements(pdf_path, page_num)

    # Compile analysis
    analysis = {
        "page_number": page_num,
        "chapter": 1,
        "text_blocks": text_blocks,
        "layout_metrics": layout_metrics,
        "heading_hierarchy": heading_hierarchy,
        "visual_elements": visual_elements,
        "analysis_summary": {
            "total_text_blocks": len(text_blocks),
            "page_lines": len(visual_elements.get("lines", [])),
            "page_rectangles": len(visual_elements.get("rectangles", [])),
            "page_images": visual_elements.get("images", []),
        },
    }

    # Save analysis
    analysis_file = os.path.join(output_dir, "page_6_pattern_analysis.json")
    with open(analysis_file, "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\n✓ Saved detailed analysis to: {analysis_file}")

    # Print summary
    print(f"\n{'='*60}")
    print("ANALYSIS SUMMARY")
    print(f"{'='*60}")
    print(f"Text blocks: {analysis['analysis_summary']['total_text_blocks']}")
    print(f"Visual lines: {analysis['analysis_summary']['page_lines']}")
    print(f"Visual rectangles: {analysis['analysis_summary']['page_rectangles']}")

    print(f"\nPage dimensions: {layout_metrics['page_dimensions']['width']}x{layout_metrics['page_dimensions']['height']}")
    print(f"Estimated margins: L={layout_metrics['estimated_margins']['left']}, "
          f"T={layout_metrics['estimated_margins']['top']}, "
          f"R={layout_metrics['estimated_margins']['right']}, "
          f"B={layout_metrics['estimated_margins']['bottom']}")

    print("\nHeading hierarchy (by font size):")
    for level, info in sorted(heading_hierarchy.items()):
        print(f"  {level}: size {info['font_size']}pt ({info['count']} blocks)")
        for example in info.get("examples", []):
            print(f"    - {example}...")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
