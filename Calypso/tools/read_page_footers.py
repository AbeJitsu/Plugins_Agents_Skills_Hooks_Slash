#!/usr/bin/env python3
"""
Read footer text from PDF pages to establish correct page number mapping.
Footers contain the actual book page numbers.
"""

import fitz  # PyMuPDF
import re
import json
from pathlib import Path


def extract_footer_text(pdf_path, page_index):
    """
    Extract footer text from a PDF page.
    Footers are typically in the bottom margin of the page.

    Args:
        pdf_path: Path to PDF file
        page_index: 0-based PDF page index

    Returns:
        Footer text string or None
    """
    pdf = fitz.open(pdf_path)
    page = pdf[page_index]

    # Footer is typically in the bottom portion
    # Standard PDF page height is 792 points (11 inches)
    # Footer usually in last 50-80 points
    page_height = page.rect.height
    footer_region = fitz.Rect(0, page_height - 80, page.rect.width, page_height)

    # Extract text from footer region
    footer_text = page.get_text("text", clip=footer_region).strip()

    pdf.close()

    return footer_text if footer_text else None


def extract_page_number_from_footer(footer_text):
    """
    Parse page number from footer text.
    Footers typically contain: "Chapter X: Title YY" or "YY Chapter X: Title"
    where YY is the book page number.

    Args:
        footer_text: Footer text string

    Returns:
        Book page number (int) or None
    """
    if not footer_text:
        return None

    # Common patterns:
    # "Chapter 1: The Real Estate Business 7"
    # "8 Principles of Real Estate..."
    # "Chapter 2: Rights in Real Estate 15"

    # Try to find number at end of footer (most common)
    match = re.search(r'(\d+)\s*$', footer_text)
    if match:
        return int(match.group(1))

    # Try to find "Chapter X: Title YY" pattern
    match = re.search(r'Chapter\s+\d+:[^0-9]*(\d+)\s*$', footer_text)
    if match:
        return int(match.group(1))

    # Try to find number at start
    match = re.search(r'^(\d+)\s+', footer_text)
    if match:
        return int(match.group(1))

    return None


def scan_page_footers(pdf_path, start_page, end_page):
    """
    Scan footers across a range of PDF pages to establish page mapping.

    Args:
        pdf_path: Path to PDF file
        start_page: Starting PDF page index (0-based)
        end_page: Ending PDF page index (inclusive, 0-based)

    Returns:
        List of dicts with page mapping data
    """
    results = []

    print(f"\nScanning PDF page footers: {start_page} to {end_page}\n")
    print(f"{'PDF Index':<12} {'Footer Text':<50} {'Book Page':<12}")
    print("=" * 75)

    for pdf_idx in range(start_page, end_page + 1):
        try:
            footer_text = extract_footer_text(pdf_path, pdf_idx)
            book_page = extract_page_number_from_footer(footer_text)

            # Determine chapter from book page number
            # Rough estimate: every ~13-14 pages per chapter
            if book_page:
                if book_page <= 6:
                    chapter = 0  # Front matter
                elif book_page <= 14:
                    chapter = 1
                elif book_page <= 27:
                    chapter = 2
                elif book_page <= 40:
                    chapter = 3
                else:
                    chapter = book_page // 13

            footer_display = footer_text[:45] if footer_text else "[no footer]"

            print(f"{pdf_idx:<12} {footer_display:<50} {book_page or 'N/A':<12}")

            results.append({
                "pdf_index": pdf_idx,
                "footer_text": footer_text,
                "book_page": book_page,
                "chapter": chapter if book_page else None
            })

        except Exception as e:
            print(f"{pdf_idx:<12} [ERROR: {str(e)[:40]}]")
            results.append({
                "pdf_index": pdf_idx,
                "error": str(e)
            })

    print("=" * 75)
    return results


def create_page_mapping(scan_results, output_file="page_mapping.json"):
    """
    Create a mapping file from scan results.
    Maps PDF indices to book pages and chapters.

    Args:
        scan_results: List of scan result dicts
        output_file: Path to save mapping JSON

    Returns:
        Mapping dict
    """
    mapping = {}

    for result in scan_results:
        if "book_page" in result and result["book_page"]:
            pdf_idx = str(result["pdf_index"])
            mapping[pdf_idx] = {
                "book_page": result["book_page"],
                "chapter": result["chapter"]
            }

    # Save to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(mapping, f, indent=2)

    print(f"\n✓ Saved mapping to: {output_path}\n")

    return mapping


def main():
    """Command-line interface."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description='Read page footers to establish PDF page mapping'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=0,
        help='Starting PDF page index (0-based)'
    )
    parser.add_argument(
        '--end',
        type=int,
        default=20,
        help='Ending PDF page index (0-based, inclusive)'
    )
    parser.add_argument(
        '--pdf',
        default='/Users/abiezerreyes/Projects/Calypso_Acadio/Calypso/PREP-AL 4th Ed 9-26-25.pdf',
        help='Path to PDF file'
    )
    parser.add_argument(
        '--output',
        default='../analysis/page_mapping.json',
        help='Output file for page mapping'
    )

    args = parser.parse_args()

    # Scan footers
    try:
        results = scan_page_footers(args.pdf, args.start, args.end)

        # Create mapping
        mapping = create_page_mapping(results, args.output)

        print(f"✓ Successfully scanned {len(results)} pages")
        print(f"✓ Found {len(mapping)} valid page mappings\n")

    except FileNotFoundError:
        print(f"Error: PDF file not found: {args.pdf}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
