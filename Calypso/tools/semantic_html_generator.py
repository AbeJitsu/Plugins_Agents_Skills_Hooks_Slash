#!/usr/bin/env python3
"""
Flexible semantic HTML generator for PDF to HTML conversion.
Supports generating single pages, page ranges, or complete chapters.
Intelligently parses text into semantic HTML structure.
"""

import json
import os
import sys
import argparse
from html import escape

# Chapter boundaries (PDF indices are 0-based)
CHAPTER_BOUNDARIES = {
    0: (0, 5, "Front Matter", ""),
    1: (6, 14, "The Real Estate Business", ""),
    2: (15, 28, "Rights in Real Estate", ""),
    3: (29, 42, "Interests and Estates", ""),
    4: (43, 54, "Ownership", ""),
    5: (55, 72, "Encumbrances and Liens", ""),
    6: (73, 89, "Transferring & Recording Title to Real Estate", ""),
    7: (90, 100, "Leasing Essentials", ""),
    8: (101, 119, "Land Use Planning and Control", ""),
}


def pdf_index_to_book_page(pdf_index):
    """Convert PDF index (0-based) to book page number."""
    if pdf_index < 6:
        return None  # Front matter has no book page numbers
    return pdf_index + 1


def load_pdf_text(pdf_indices):
    """Load text from pdfplumber_output.json for given PDF indices."""
    json_file = "../analysis/pdfplumber_output.json"

    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        sys.exit(1)

    with open(json_file) as f:
        all_pages = json.load(f)

    # Extract text for requested pages
    pages = []
    for idx in pdf_indices:
        page_key = str(idx)
        if page_key in all_pages:
            pages.append({
                "pdf_index": idx,
                "book_page": pdf_index_to_book_page(idx),
                "text": all_pages[page_key].get("text", "")
            })

    return pages


def parse_text_into_sections(text):
    """
    Parse raw text into semantic sections.
    Returns list of dicts: {type: 'heading'|'paragraph'|'list', content: str, level: int}
    """
    sections = []
    lines = text.strip().split('\n')

    current_paragraph = []

    for line in lines:
        stripped = line.strip()

        if not stripped:
            # Empty line - end current paragraph
            if current_paragraph:
                sections.append({
                    'type': 'paragraph',
                    'content': ' '.join(current_paragraph)
                })
                current_paragraph = []
            continue

        # Detect heading patterns
        if stripped.isupper() and len(stripped) > 3 and stripped.count(' ') > 0:
            # All caps = section heading (h2)
            if current_paragraph:
                sections.append({
                    'type': 'paragraph',
                    'content': ' '.join(current_paragraph)
                })
                current_paragraph = []

            sections.append({
                'type': 'heading',
                'level': 2,
                'content': stripped
            })

        # Detect bullet points (check for bullet character or common patterns)
        elif stripped.startswith('•') or stripped.startswith('- ') or stripped.startswith('* '):
            if current_paragraph:
                sections.append({
                    'type': 'paragraph',
                    'content': ' '.join(current_paragraph)
                })
                current_paragraph = []

            # Remove bullet character
            item_text = stripped.lstrip('•- *').strip()
            sections.append({
                'type': 'list_item',
                'content': item_text
            })

        # Regular paragraph text
        else:
            current_paragraph.append(stripped)

    # Add remaining paragraph
    if current_paragraph:
        sections.append({
            'type': 'paragraph',
            'content': ' '.join(current_paragraph)
        })

    return sections


def build_html_content(pages):
    """Build semantic HTML content from parsed pages."""
    html_sections = []

    for page_num, page in enumerate(pages):
        book_page = page['book_page']
        text = page['text']

        # Parse text into sections
        sections = parse_text_into_sections(text)

        for section in sections:
            if section['type'] == 'heading' and section['level'] == 2:
                html_sections.append(f'''            <section class="content-section">
                <h2 class="section-heading">{escape(section['content'])}</h2>''')

            elif section['type'] == 'paragraph':
                html_sections.append(f'''                <p class="paragraph">{escape(section['content'])}</p>''')

            elif section['type'] == 'list_item':
                # Group consecutive list items
                if not html_sections or '</ul>' in html_sections[-1]:
                    html_sections.append(f'''                <ul class="bullet-list">
                    <li class="bullet-item">{escape(section['content'])}</li>''')
                else:
                    html_sections.append(f'''                    <li class="bullet-item">{escape(section['content'])}</li>''')

        # Close last section
        if html_sections and '</section>' not in html_sections[-1]:
            html_sections.append('''            </section>''')

    # Close any open lists
    html_content = '\n'.join(html_sections)
    html_content = html_content.replace('</ul>', '').replace('</li>', '')
    html_content += '''
                </ul>
            </section>'''

    return html_content


def generate_html(pages, title="Content"):
    """Generate complete HTML document."""

    # Get page range for document title
    if pages:
        start_book_page = pages[0].get('book_page') or pages[0]['pdf_index'] + 1
        end_book_page = pages[-1].get('book_page') or pages[-1]['pdf_index'] + 1
        page_range = f"Pages {start_book_page}-{end_book_page}"
    else:
        page_range = ""

    # Build content
    html_content = build_html_content(pages)

    # Generate complete HTML
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
        <!-- Content -->
        <main class="page-content">
{html_content}
        </main>
    </div>
</body>
</html>
'''

    return html


def main():
    parser = argparse.ArgumentParser(
        description='Generate semantic HTML from PDF pages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  python3 semantic_html_generator.py --chapter 1
  python3 semantic_html_generator.py --pages 6-14 --output chapter_1.html
  python3 semantic_html_generator.py --page 7
        '''
    )

    parser.add_argument('--chapter', type=int, help='Chapter number (1-29)')
    parser.add_argument('--pages', type=str, help='Page range (e.g., 6-14)')
    parser.add_argument('--page', type=int, help='Single page (PDF index)')
    parser.add_argument('--output', type=str, help='Output file path')

    args = parser.parse_args()

    # Determine PDF indices to process
    pdf_indices = []
    title = "Generated Content"

    if args.chapter:
        if args.chapter not in CHAPTER_BOUNDARIES:
            print(f"Error: Chapter {args.chapter} not found in CHAPTER_BOUNDARIES")
            sys.exit(1)

        start, end, chapter_title, _ = CHAPTER_BOUNDARIES[args.chapter]
        pdf_indices = list(range(start, end + 1))
        title = f"Chapter {args.chapter}: {chapter_title}"

        if not args.output:
            args.output = f"../output/chapter_{args.chapter:02d}.html"

    elif args.pages:
        try:
            start, end = map(int, args.pages.split('-'))
            pdf_indices = list(range(start, end + 1))
            title = f"Pages {start}-{end}"
        except ValueError:
            print("Error: --pages format should be 'start-end' (e.g., 6-14)")
            sys.exit(1)

        if not args.output:
            args.output = f"../output/pages_{start}_{end}.html"

    elif args.page is not None:
        pdf_indices = [args.page]
        book_page = pdf_index_to_book_page(args.page)
        title = f"Page {book_page or args.page}"

        if not args.output:
            args.output = f"../output/page_{args.page}.html"

    else:
        parser.print_help()
        sys.exit(1)

    if not pdf_indices:
        print("Error: No pages specified")
        sys.exit(1)

    # Load and process pages
    print(f"\n{'='*60}")
    print(f"GENERATING: {title}")
    print(f"PDF indices: {pdf_indices}")
    print(f"{'='*60}\n")

    print("Loading text from pdfplumber_output.json...")
    pages = load_pdf_text(pdf_indices)
    print(f"✓ Loaded {len(pages)} pages")

    print("Parsing text into semantic HTML...")
    html = generate_html(pages, title)

    print(f"Writing to {args.output}...")
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, 'w') as f:
        f.write(html)
    print(f"✓ Saved: {args.output}")

    print(f"\n✓ HTML generation complete!")
    print(f"✓ CSS file: styles/main.css")
    print(f"\nOpen in browser to view the generated content.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
