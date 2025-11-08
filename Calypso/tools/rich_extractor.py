#!/usr/bin/env python3
"""
Rich data extractor combining PyMuPDF, pdfplumber, and pattern analysis.
Extracts complete formatting information: fonts, sizes, styles, positioning, tables.
Output: rich_extraction.json with full semantic markup information.

PDF Index Mapping:
  - PDF pages are indexed 0-based (0, 1, 2, ...)
  - Book pages are numbered 1-based
  - PDF index 0-5 = Front matter (no book page number)
  - PDF index 6+ = Book page = PDF index + 1
  - Example: PDF index 6 extracts to book_page: 7 (footer shows "7")
"""

import json
import os
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
    import pdfplumber
except ImportError as e:
    print(f"Error: Missing required library: {e}")
    sys.exit(1)


def extract_rich_page_data(pdf_path, page_num):
    """
    Extract rich formatting data from a single page.
    Combines PyMuPDF dict (fonts/styles) with pdfplumber (text/tables).

    Args:
        pdf_path: Path to PDF file
        page_num: 0-based PDF page index (not book page number)
                  Example: page_num=6 extracts PDF index 6, which is book page 7

    Returns:
        Dict with page_number (PDF index), book_page (book number if applicable),
        text_spans with font metadata, tables, images, and structure analysis
    """

    # Open PDF with PyMuPDF (page_num is 0-based index)
    pdf_fitz = fitz.open(pdf_path)
    page_fitz = pdf_fitz[page_num]
    text_dict = page_fitz.get_text("dict")

    # Open PDF with pdfplumber for table detection
    pdf_plumber = pdfplumber.open(pdf_path)
    page_plumber = pdf_plumber.pages[page_num]

    # Initialize output
    # page_number = PDF index (0-based)
    # book_page = Book page number (1-based), only for PDF indices >= 6
    page_data = {
        "page_number": page_num,
        "book_page": page_num + 1 if page_num >= 6 else None,  # Book page = PDF index + 1
        "dimensions": {
            "width": page_fitz.rect.width,
            "height": page_fitz.rect.height,
        },
        "text_spans": [],
        "tables": [],
        "images": [],
    }

    # Extract text spans with detailed formatting
    if "blocks" in text_dict:
        for block in text_dict["blocks"]:
            if block.get("type") == 0:  # Text block
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            # Determine font style
                            font_name = span.get("font", "unknown")
                            is_bold = "Bold" in font_name
                            is_italic = "Italic" in font_name

                            # Extract span data
                            span_data = {
                                "text": span.get("text", ""),
                                "font": font_name,
                                "size": span.get("size", 0),
                                "bold": is_bold,
                                "italic": is_italic,
                                "color": span.get("color", 0),
                                "bbox": {
                                    "x0": round(span.get("x0", 0), 2),
                                    "y0": round(span.get("y0", 0), 2),
                                    "x1": round(span.get("x1", 0), 2),
                                    "y1": round(span.get("y1", 0), 2),
                                },
                                "flags": span.get("flags", 0),
                            }
                            page_data["text_spans"].append(span_data)

            elif block.get("type") == 1:  # Image block
                image_data = {
                    "bbox": {
                        "x0": round(block.get("bbox", [0,0,0,0])[0], 2),
                        "y0": round(block.get("bbox", [0,0,0,0])[1], 2),
                        "x1": round(block.get("bbox", [0,0,0,0])[2], 2),
                        "y1": round(block.get("bbox", [0,0,0,0])[3], 2),
                    }
                }
                page_data["images"].append(image_data)

    # Extract tables using pdfplumber
    try:
        tables = page_plumber.extract_tables()
        if tables:
            for table in tables:
                table_data = {
                    "rows": len(table),
                    "cols": len(table[0]) if table else 0,
                    "content": table,
                }
                page_data["tables"].append(table_data)
    except Exception as e:
        pass  # Table extraction failed, continue

    # Analyze text spans for structure
    page_data["analysis"] = analyze_page_structure(page_data["text_spans"])

    pdf_fitz.close()
    pdf_plumber.close()

    return page_data


def analyze_page_structure(text_spans):
    """Analyze text spans to identify document structure."""
    analysis = {
        "font_sizes": {},
        "font_styles": {},
        "likely_headings": [],
        "likely_paragraphs": [],
    }

    if not text_spans:
        return analysis

    # Group by font size
    for span in text_spans:
        size = span["size"]
        if size not in analysis["font_sizes"]:
            analysis["font_sizes"][size] = 0
        analysis["font_sizes"][size] += 1

    # Group by style
    for span in text_spans:
        if span["bold"]:
            style = f"bold_{span['size']}"
        elif span["italic"]:
            style = f"italic_{span['size']}"
        else:
            style = f"regular_{span['size']}"

        if style not in analysis["font_styles"]:
            analysis["font_styles"][style] = 0
        analysis["font_styles"][style] += 1

    # Identify likely headings (bold text, large sizes)
    for span in text_spans:
        text = span["text"].strip()
        if len(text) > 3:
            # Heuristics for headings
            if (span["bold"] or span["size"] > 14) and span["size"] > 11:
                analysis["likely_headings"].append({
                    "text": text,
                    "size": span["size"],
                    "bold": span["bold"],
                })
            elif span["size"] > 10 and not span["bold"]:
                analysis["likely_paragraphs"].append(text[:100])

    return analysis


def extract_chapters(pdf_path, output_file, start_page=None, end_page=None):
    """Extract rich data for specified page range."""

    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)

    # Determine page range
    pdf = fitz.open(pdf_path)
    total_pages = pdf.page_count
    pdf.close()

    if start_page is None:
        start_page = 0
    if end_page is None:
        end_page = total_pages - 1

    if start_page < 0 or end_page >= total_pages or start_page > end_page:
        print(f"Error: Invalid page range {start_page}-{end_page} (total: {total_pages})")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"RICH DATA EXTRACTION")
    print(f"Pages: {start_page}-{end_page} ({end_page - start_page + 1} pages)")
    print(f"{'='*60}\n")

    # Extract all pages
    all_pages = {}
    for page_num in range(start_page, end_page + 1):
        print(f"Extracting page {page_num}...", end=" ")
        page_data = extract_rich_page_data(pdf_path, page_num)
        all_pages[str(page_num)] = page_data
        print(f"✓ ({len(page_data['text_spans'])} spans, {len(page_data['tables'])} tables)")

    # Save to JSON
    output_dir = os.path.dirname(output_file)
    os.makedirs(output_dir, exist_ok=True)

    output_data = {
        "metadata": {
            "source": pdf_path,
            "total_pages_extracted": end_page - start_page + 1,
            "page_range": f"{start_page}-{end_page}",
        },
        "pages": all_pages,
    }

    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✓ Saved: {output_file}")
    print(f"\nExtraction Summary:")
    print(f"  Total pages: {len(all_pages)}")
    total_spans = sum(len(p.get("text_spans", [])) for p in all_pages.values())
    total_tables = sum(len(p.get("tables", [])) for p in all_pages.values())
    print(f"  Total text spans: {total_spans}")
    print(f"  Total tables: {total_tables}")
    print("="*60 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract rich formatting data from PDF'
    )
    parser.add_argument('--pdf', default='../../PREP-AL 4th Ed 9-26-25.pdf', help='PDF file path')
    parser.add_argument('--start', type=int, default=6, help='Start page (0-based)')
    parser.add_argument('--end', type=int, default=14, help='End page (0-based)')
    parser.add_argument('--output', default='../analysis/rich_extraction.json', help='Output file')

    args = parser.parse_args()

    extract_chapters(args.pdf, args.output, args.start, args.end)


if __name__ == "__main__":
    main()
