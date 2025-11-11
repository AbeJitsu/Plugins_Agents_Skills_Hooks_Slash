#!/usr/bin/env python3
"""
Generate clean HTML for a chapter from extraction JSON - Version 2.
Better handling of structure, lists, and sections.
"""

import json
import re

def load_extraction(json_path):
    """Load extraction JSON."""
    with open(json_path, 'r') as f:
        return json.load(f)

def extract_all_spans(data):
    """Extract all text spans in page order."""
    all_spans = []
    for page_id in sorted(data['pages'].keys(), key=lambda x: int(x)):
        page_data = data['pages'][page_id]
        text_spans = page_data.get('text_spans', [])
        for span in text_spans:
            text = span.get('text', '')
            if text.strip():  # Only include non-empty spans
                all_spans.append({
                    'text': text.strip(),
                    'size': round(span.get('size', 0), 1),
                    'bold': span.get('bold', False),
                    'italic': span.get('italic', False),
                    'page': page_id
                })
    return all_spans

def identify_structure(spans):
    """Identify heading levels and structure from spans."""
    # Analyze font sizes
    sizes = {}
    for span in spans:
        size = span['size']
        sizes[size] = sizes.get(size, 0) + 1

    # Sort by frequency
    sorted_sizes = sorted(sizes.items(), key=lambda x: x[1], reverse=True)

    print("Text analysis:")
    print(f"  Total spans: {len(spans)}")
    print(f"  Font size distribution (top 5):")
    for size, count in sorted_sizes[:5]:
        print(f"    {size}pt: {count} occurrences")

    # Identify size thresholds
    sizes_by_freq = [s[0] for s in sorted_sizes]
    h2_threshold = sizes_by_freq[0] if len(sizes_by_freq) > 0 else 27
    h3_threshold = sizes_by_freq[1] if len(sizes_by_freq) > 1 else 12

    return {
        'h2': h2_threshold,
        'h3': h3_threshold,
        'all_sizes': sorted_sizes
    }

def classify_span(span, thresholds):
    """Classify a span as heading, subheading, or body text."""
    size = span['size']

    # Check if it's a heading
    if size >= (thresholds['h2'] * 0.8):  # Within 80% of largest size
        return 'h2'
    elif size >= (thresholds['h3'] * 0.9):  # Within 90% of second size
        return 'h3'
    else:
        return 'p'

def is_potential_list_item(text):
    """Check if text looks like a list item."""
    # Items that start with bullet, dash, or number
    return bool(re.match(r'^[•\-\*]?\s*[a-z]', text, re.IGNORECASE) or
                re.match(r'^[0-9]+\.\s+', text))

def format_span(span):
    """Format span text with bold/italic tags if needed."""
    text = span['text']
    if span['bold']:
        text = f"<strong>{text}</strong>"
    if span['italic']:
        text = f"<em>{text}</em>"
    return text

def group_and_generate_html(spans, thresholds):
    """Group spans into logical blocks and generate HTML."""
    html_lines = []
    i = 0

    while i < len(spans):
        span = spans[i]
        span_type = classify_span(span, thresholds)

        if span_type == 'h2':
            # Heading 2 - collect until next heading
            heading_text = span['text']
            i += 1

            # Skip page numbers and empty spans after heading
            while i < len(spans) and classify_span(spans[i], thresholds) == 'p':
                next_text = spans[i]['text'].strip()
                # Stop if we hit what looks like a new major section
                if re.match(r'^[A-Z\s]+$', next_text) or len(next_text) > 100:
                    break
                heading_text += ' ' + next_text
                i += 1

            html_lines.append(f"<h2>{heading_text.strip()}</h2>")

        elif span_type == 'h3':
            # Heading 3
            heading_text = span['text']
            i += 1

            # Only collect next span if it's also h3-sized
            if i < len(spans) and classify_span(spans[i], thresholds) == 'h3':
                heading_text += ' ' + spans[i]['text']
                i += 1

            html_lines.append(f"<h3>{heading_text.strip()}</h3>")

        else:
            # Body text - group consecutive paragraphs
            para_lines = [format_span(span)]
            i += 1

            # Collect following body text spans
            while i < len(spans) and classify_span(spans[i], thresholds) not in ['h2', 'h3']:
                next_span = spans[i]
                text = format_span(next_span)

                # Start new paragraph if we see a clear break (e.g., exhibit, snapshot)
                if any(marker in next_span['text'].upper() for marker in
                       ['EXHIBIT', 'SNAPSHOT', 'REVIEW', '●']):
                    break

                para_lines.append(text)
                i += 1

            combined = ' '.join(para_lines)

            # Check for bullet lists
            if '●' in combined:
                # Extract and format as list
                html_lines.extend(format_bullet_list(combined))
            else:
                # Regular paragraph
                combined = combined.replace('  ', ' ').replace('> <', '> <')
                if combined.strip():
                    html_lines.append(f"<p>{combined.strip()}</p>")

    return html_lines

def format_bullet_list(text):
    """Convert bullet text into proper HTML list."""
    lines = []

    # Split on bullet markers
    items = re.split(r'●\s*', text)

    if len(items) > 1:
        # We have bullets
        list_items = []
        for item in items:
            item = item.strip()
            if item:
                list_items.append(f"<li>{item}</li>")

        if list_items:
            lines.append("<ul>")
            lines.extend(list_items)
            lines.append("</ul>")
        return lines
    else:
        # No bullets, return as paragraph
        return [f"<p>{text.strip()}</p>"] if text.strip() else []

def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python3 generate_chapter_html_v2.py <chapter_num> <output_file>")
        sys.exit(1)

    chapter_num = sys.argv[1]
    output_file = sys.argv[2]
    json_path = f"Calypso/analysis/chapter_{chapter_num.zfill(2)}/rich_extraction.json"

    print(f"Loading extraction from {json_path}...")
    data = load_extraction(json_path)

    print(f"Extracting text from {data['metadata']['total_pages_extracted']} pages...")
    spans = extract_all_spans(data)

    print(f"\nAnalyzing structure...")
    thresholds = identify_structure(spans)

    print(f"\nGenerating HTML ({len(spans)} text spans)...")
    html_lines = group_and_generate_html(spans, thresholds)

    print(f"Writing {len(html_lines)} elements to {output_file}...")
    with open(output_file, 'w') as f:
        f.write('\n'.join(html_lines))

    print("Done!")

if __name__ == '__main__':
    main()
