#!/usr/bin/env python3
"""
Generate clean HTML for a chapter from extraction JSON.
Follows Chapter 1 template: no classes, no styles, semantic structure only.
"""

import json
import re
from collections import defaultdict

def load_extraction(json_path):
    """Load extraction JSON."""
    with open(json_path, 'r') as f:
        return json.load(f)

def extract_text_by_page(data):
    """Extract all text from each page in order."""
    pages_text = {}
    for page_id, page_data in sorted(data['pages'].items(), key=lambda x: int(x[0])):
        text_spans = page_data.get('text_spans', [])
        page_text = []
        for span in text_spans:
            text = span.get('text', '')
            font_size = span.get('size', 0)
            bold = span.get('bold', False)
            italic = span.get('italic', False)
            if text.strip():
                page_text.append({
                    'text': text,
                    'size': font_size,
                    'bold': bold,
                    'italic': italic
                })
        pages_text[page_id] = page_text
    return pages_text

def analyze_structure(pages_text):
    """Analyze font sizes to identify heading levels."""
    font_sizes = defaultdict(int)
    for page_id, texts in pages_text.items():
        for span in texts:
            size = round(span['size'], 1)
            font_sizes[size] += 1

    # Sort by frequency
    sorted_sizes = sorted(font_sizes.items(), key=lambda x: x[1], reverse=True)
    print("Font size distribution:")
    for size, count in sorted_sizes[:10]:
        print(f"  {size}pt: {count} occurrences")
    return sorted_sizes

def identify_heading_level(size, font_sizes):
    """Determine heading level based on font size."""
    # Get top sizes
    top_sizes = [s[0] for s in font_sizes[:5]]

    if size >= top_sizes[0] - 2:  # Largest = h1/h2
        return 'h2'
    elif size >= top_sizes[1] - 2 if len(top_sizes) > 1 else 0:  # Second largest = h3
        return 'h3'
    elif size >= 11 and size <= 12:  # Body text
        return 'p'
    else:
        return None

def format_text_spans(text, bold=False, italic=False):
    """Wrap text with appropriate tags."""
    if bold:
        text = f"<strong>{text}</strong>"
    if italic:
        text = f"<em>{text}</em>"
    return text

def generate_html_from_pages(pages_text):
    """Generate HTML from extracted text."""
    html_lines = []

    # Analyze structure first
    font_sizes = analyze_structure(pages_text)

    # Flatten all text and track context
    all_text = []
    for page_id in sorted(pages_text.keys(), key=lambda x: int(x)):
        all_text.extend(pages_text[page_id])

    # Group consecutive spans into logical blocks
    current_block = []
    current_size = None

    for span in all_text:
        text = span['text'].strip()
        if not text:
            continue

        # If size changes significantly, start new block
        if current_size is not None and abs(span['size'] - current_size) > 3:
            if current_block:
                # Process accumulated block
                html_lines.extend(process_text_block(current_block, current_size, font_sizes))
            current_block = [span]
            current_size = span['size']
        else:
            current_block.append(span)
            if current_size is None:
                current_size = span['size']

    # Process final block
    if current_block:
        html_lines.extend(process_text_block(current_block, current_size, font_sizes))

    return '\n'.join(html_lines)

def process_text_block(spans, font_size, font_sizes):
    """Process a block of text spans into HTML elements."""
    lines = []

    # Determine element type
    if font_size >= (font_sizes[0][0] - 2):  # Large text = heading
        text = ' '.join(s['text'].strip() for s in spans if s['text'].strip())
        lines.append(f"<h2>{text}</h2>")
    elif font_size >= (font_sizes[1][0] - 2 if len(font_sizes) > 1 else 12):  # Medium = heading
        text = ' '.join(s['text'].strip() for s in spans if s['text'].strip())
        lines.append(f"<h3>{text}</h3>")
    else:
        # Body text
        text_content = []
        for span in spans:
            text = span['text'].strip()
            if text:
                formatted = format_text_spans(text, span.get('bold', False), span.get('italic', False))
                text_content.append(formatted)

        if text_content:
            combined = ' '.join(text_content)
            # Clean up HTML
            combined = combined.replace('> <', '> <')
            lines.append(f"<p>{combined}</p>")

    return lines

def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 generate_chapter_html.py <chapter_num> <output_file>")
        sys.exit(1)

    chapter_num = sys.argv[1]
    output_file = sys.argv[2]
    json_path = f"Calypso/analysis/chapter_{chapter_num.zfill(2)}/rich_extraction.json"

    print(f"Loading extraction from {json_path}...")
    data = load_extraction(json_path)

    print(f"Extracting text from {data['metadata']['total_pages_extracted']} pages...")
    pages_text = extract_text_by_page(data)

    print(f"Generating HTML...")
    html = generate_html_from_pages(pages_text)

    print(f"Writing to {output_file}...")
    with open(output_file, 'w') as f:
        f.write(html)

    print("Done!")

if __name__ == '__main__':
    main()
