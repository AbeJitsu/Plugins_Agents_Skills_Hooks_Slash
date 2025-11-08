#!/usr/bin/env python3
"""
Semantic HTML generator using rich formatting data.
Combines font information, sizes, and styles to generate high-quality HTML.

PDF Page Mapping:
  - PDF indices are 0-based (0, 1, 2, ...)
  - Book pages are 1-based
  - PDF index 0-5 = Front matter (no book page number)
  - PDF index 6+ = Book page = PDF index + 1
  - Example: PDF index 6 = Book page 7 (footer shows "7")
"""

import json
import os
import sys
import argparse
from html import escape

# Chapter boundaries (all values are PDF indices, 0-based)
# Format: chapter_num: (pdf_start_index, pdf_end_index, title, description)
CHAPTER_BOUNDARIES = {
    0: (0, 5, "Front Matter", ""),
    1: (6, 14, "The Real Estate Business", ""),  # PDF 6-14 = Book pages 7-15
    2: (15, 28, "Rights in Real Estate", ""),
    3: (29, 42, "Interests and Estates", ""),
    4: (43, 54, "Ownership", ""),
    5: (55, 72, "Encumbrances and Liens", ""),
    6: (73, 89, "Transferring & Recording Title to Real Estate", ""),
    7: (90, 100, "Leasing Essentials", ""),
    8: (101, 119, "Land Use Planning and Control", ""),
}


def pdf_index_to_book_page(pdf_index):
    """
    Convert PDF index (0-based) to book page number (1-based).

    PDF index 0-5 have no book page (front matter).
    PDF index 6+ maps to book page = PDF index + 1.

    Args:
        pdf_index: 0-based PDF page index

    Returns:
        Book page number for indices >= 6, None otherwise

    Example:
        pdf_index_to_book_page(6) -> 7 (footer shows "Page 7")
        pdf_index_to_book_page(14) -> 15 (footer shows "Page 15")
    """
    if pdf_index < 6:
        return None
    return pdf_index + 1


def load_rich_extraction(json_file):
    """Load rich extraction data from JSON."""
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        sys.exit(1)

    with open(json_file) as f:
        return json.load(f)


def group_text_spans_into_elements(text_spans):
    """Group text spans into logical elements (headings, paragraphs)."""
    if not text_spans:
        return []

    elements = []
    current_group = []
    current_heading_parts = []
    current_heading_level = None

    for span in text_spans:
        text = span["text"].strip()
        if not text:
            continue

        font_size = span["size"]
        is_bold = span["bold"]
        is_italic = span["italic"]

        # Is this text all-caps? (must be > 2 chars, all uppercase letters/spaces/hyphens)
        is_all_caps = text.isupper() and len(text) > 2

        # Filter out page numbers and noise
        # Skip: single characters, or just spaces/bullets
        if len(text) < 2 or text in ['●', '○', '*']:
            continue

        # Determine if this span should be part of a heading
        is_heading_candidate = (
            (font_size > 50 and len(text) > 1) or  # Very large titles
            (font_size > 20 and is_bold) or  # Large bold
            (is_bold and (is_all_caps or font_size > 11.5))  # Bold heading
        )

        if is_heading_candidate:
            # Determine heading level
            if font_size > 50 and len(text) > 1:
                heading_level = 1
            elif font_size > 20 and is_bold:
                heading_level = 2
            else:
                heading_level = 3 if is_all_caps else 4

            # If this is a different heading level than what we're accumulating, flush previous
            if current_heading_level is not None and heading_level != current_heading_level:
                if current_heading_parts:
                    heading_text = " ".join(current_heading_parts)
                    elements.append({
                        "type": "heading",
                        "level": current_heading_level,
                        "text": heading_text,
                    })
                current_heading_parts = []
            elif current_group:
                # If we were accumulating paragraph text, flush it first
                elements.append(flush_group(current_group))
                current_group = []

            # Only accumulate adjacent headings if they're h3+ (all-caps or very large)
            # Don't accumulate h4 - they should be separate items
            if heading_level <= 3:
                current_heading_parts.append(text)
                current_heading_level = heading_level
            else:
                # For h4, treat each span as a separate heading
                if current_heading_parts:
                    heading_text = " ".join(current_heading_parts)
                    elements.append({
                        "type": "heading",
                        "level": current_heading_level,
                        "text": heading_text,
                    })
                    current_heading_parts = []
                    current_heading_level = None

                elements.append({
                    "type": "heading",
                    "level": heading_level,
                    "text": text,
                })

        else:
            # Regular text
            # If we were accumulating heading parts, flush them first
            if current_heading_parts:
                heading_text = " ".join(current_heading_parts)
                elements.append({
                    "type": "heading",
                    "level": current_heading_level,
                    "text": heading_text,
                })
                current_heading_parts = []
                current_heading_level = None

            # Add to paragraph group
            current_group.append({
                "text": text,
                "italic": is_italic,
                "bold": is_bold,
            })

    # Flush remaining heading parts
    if current_heading_parts:
        heading_text = " ".join(current_heading_parts)
        elements.append({
            "type": "heading",
            "level": current_heading_level,
            "text": heading_text,
        })

    # Flush remaining group
    if current_group:
        elements.append(flush_group(current_group))

    return elements


def flush_group(group):
    """Convert grouped spans into a single element."""
    if not group:
        return None

    combined_text = " ".join(s["text"] for s in group)
    has_italic = any(s["italic"] for s in group)

    return {
        "type": "paragraph",
        "text": combined_text,
        "italic": has_italic,
    }


def build_html_from_elements(elements):
    """Build HTML from grouped elements."""
    html_parts = []

    # Mapping of heading levels to semantic CSS classes
    heading_classes = {
        1: "chapter-title",
        2: "section-heading",
        3: "subsection-title",
        4: "subsection-heading",
    }

    for elem in elements:
        if elem["type"] == "heading":
            level = elem["level"]
            tag = f"h{level}"
            css_class = heading_classes.get(level, "subsection-heading")
            html_parts.append(
                f'            <{tag} class="{css_class}">{escape(elem["text"])}</{tag}>'
            )

        elif elem["type"] == "paragraph":
            classes = ["paragraph"]
            if elem.get("italic"):
                classes.append("paragraph-italic")
            class_str = " ".join(classes)
            html_parts.append(
                f'            <p class="{class_str}">{escape(elem["text"])}</p>'
            )

    return "\n".join(html_parts)


def generate_html(pages_data, title="Content"):
    """
    Generate complete HTML document from pages data.

    Args:
        pages_data: Dict of {pdf_index_str: page_data} pairs
        title: Title for the HTML document

    Returns:
        Complete HTML document as string
    """
    # pages_data keys are PDF indices (strings)
    page_nums = sorted([int(k) for k in pages_data.keys()])

    if page_nums:
        # Convert PDF indices to book page numbers
        # PDF index 0-5 = no book page (front matter)
        # PDF index 6+ = book page = PDF index + 1
        start_pdf_idx = page_nums[0]
        end_pdf_idx = page_nums[-1]
        start_book_page = pdf_index_to_book_page(start_pdf_idx) or start_pdf_idx
        end_book_page = pdf_index_to_book_page(end_pdf_idx) or end_pdf_idx
        page_range = f"Pages {start_book_page}-{end_book_page}"
    else:
        page_range = ""

    content_parts = []
    for page_num_str in sorted(pages_data.keys(), key=lambda x: int(x)):
        page_data = pages_data[page_num_str]
        elements = group_text_spans_into_elements(page_data.get("text_spans", []))
        page_content = build_html_from_elements(elements)
        content_parts.append(page_content)

    full_content = "\n".join(content_parts)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} - {page_range}</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="page-container">
        <main class="page-content">
{full_content}
        </main>
    </div>
</body>
</html>
'''

    return html


def main():
    parser = argparse.ArgumentParser(description='Generate semantic HTML from rich PDF data')
    parser.add_argument('--chapter', type=int, help='Chapter number (generates all pages in that chapter)')
    parser.add_argument('--pages', type=str, help='PDF page range by index (e.g., 6-14). Note: PDF indices are 0-based, so index 6 = book page 7')
    parser.add_argument('--page', type=int, help='Single PDF page index (0-based). Note: index 6 = book page 7')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--rich-data', default='../analysis/rich_extraction.json', help='Rich extraction JSON file path')

    args = parser.parse_args()

    pdf_indices = []
    title = "Content"

    if args.chapter:
        if args.chapter not in CHAPTER_BOUNDARIES:
            print(f"Error: Chapter {args.chapter} not found")
            sys.exit(1)
        start, end, chapter_title, _ = CHAPTER_BOUNDARIES[args.chapter]
        pdf_indices = list(range(start, end + 1))
        title = f"Chapter {args.chapter}: {chapter_title}"
        if not args.output:
            args.output = f"../output/chapter_{args.chapter:02d}.html"

    elif args.pages:
        try:
            start_idx, end_idx = map(int, args.pages.split('-'))
            pdf_indices = list(range(start_idx, end_idx + 1))
            # Convert PDF indices to book pages for title
            start_book = pdf_index_to_book_page(start_idx) or start_idx
            end_book = pdf_index_to_book_page(end_idx) or end_idx
            title = f"Pages {start_book}-{end_book}"
        except ValueError:
            print("Error: --pages format should be 'start-end' (PDF indices, 0-based)")
            sys.exit(1)
        if not args.output:
            args.output = f"../output/pages_{start_idx}_{end_idx}.html"

    elif args.page is not None:
        pdf_indices = [args.page]
        book_page = pdf_index_to_book_page(args.page)
        # Display both PDF index and book page in title for clarity
        title = f"Page {book_page or args.page}"
        if not args.output:
            args.output = f"../output/page_{args.page}.html"

    else:
        parser.print_help()
        sys.exit(1)

    if not pdf_indices:
        print("Error: No pages specified")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"GENERATING: {title}")
    print(f"PDF indices: {pdf_indices}")
    print(f"{'='*60}\n")

    print("Loading rich extraction data...")
    rich_data = load_rich_extraction(args.rich_data)

    pages_data = {}
    for idx in pdf_indices:
        idx_str = str(idx)
        if idx_str in rich_data.get("pages", {}):
            pages_data[idx_str] = rich_data["pages"][idx_str]

    if not pages_data:
        print("Error: No pages found in rich extraction")
        sys.exit(1)

    print(f"✓ Loaded {len(pages_data)} pages")
    print("Generating semantic HTML...")
    html = generate_html(pages_data, title)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        f.write(html)
    print(f"✓ Saved: {args.output}")
    print(f"\n✓ Complete! CSS: styles/main.css")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
