#!/usr/bin/env python3
"""
Detailed analysis: Compare PDF extraction JSON with generated HTML.
Shows exactly what words are extra/missing and where they appear.

Usage:
    python3 detailed_extraction_diff.py <chapter_num> <page_num>

Example:
    python3 detailed_extraction_diff.py 2 16
"""

import sys
import json
import re
from pathlib import Path
from html.parser import HTMLParser
from collections import defaultdict
from typing import List


class TextExtractor(HTMLParser):
    """Extract all text from HTML."""

    def __init__(self):
        super().__init__()
        self.text_chunks = []
        self.skip_content = False

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip_content = True

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip_content = False

    def handle_data(self, data):
        if not self.skip_content:
            text = data.strip()
            if text:
                self.text_chunks.append(text)

    def get_text(self) -> str:
        """Return all extracted text as single string."""
        return ' '.join(self.text_chunks)

    def get_text_with_context(self) -> List[str]:
        """Return text chunks with context."""
        return self.text_chunks


def extract_text_from_html(html_path: str) -> str:
    """Extract all text content from HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    parser = TextExtractor()
    parser.feed(html_content)
    return parser.get_text()


def normalize_word(word: str) -> str:
    """Normalize a word for comparison."""
    return word.lower().strip('.,;:!?\'"')


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 detailed_extraction_diff.py <chapter_num> <page_num>")
        print("Example: python3 detailed_extraction_diff.py 2 16")
        sys.exit(1)

    chapter_num = int(sys.argv[1])
    page_num = int(sys.argv[2])

    base_dir = Path(__file__).parent.parent
    chapter_str = f"{chapter_num:02d}"

    # Paths
    json_path = base_dir / "analysis" / f"chapter_{chapter_str}" / "rich_extraction.json"
    html_path = base_dir / "output" / f"chapter_{chapter_str}" / "page_artifacts" / f"page_{page_num}" / f"04_page_{page_num}.html"

    # Verify files exist
    if not json_path.exists():
        print(f"Error: JSON not found: {json_path}")
        sys.exit(1)
    if not html_path.exists():
        print(f"Error: HTML not found: {html_path}")
        sys.exit(1)

    print("=" * 100)
    print(f"DETAILED EXTRACTION COMPARISON: Chapter {chapter_num}, Page {page_num}")
    print("=" * 100)

    # Load JSON
    print("\n[1] Loading extraction JSON...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get page text from JSON
    page_key = str(page_num)
    if page_key not in data.get('pages', {}):
        print(f"Error: Page {page_num} not in JSON")
        sys.exit(1)

    page_data = data['pages'][page_key]
    json_text_chunks = []
    for span in page_data.get('text_spans', []):
        text = span.get('text', '').strip()
        if text:
            json_text_chunks.append(text)

    json_full_text = ' '.join(json_text_chunks)
    json_words = json_full_text.lower().split()
    print(f"   ✓ JSON has {len(json_words)} words in {len(json_text_chunks)} text spans")

    # Load HTML
    print("[2] Loading HTML file...")
    html_text = extract_text_from_html(str(html_path))
    html_words = html_text.lower().split()
    print(f"   ✓ HTML has {len(html_words)} words")

    # Calculate coverage
    coverage = (len(html_words) / len(json_words) * 100) if json_words else 0
    print(f"   ✓ Coverage: {coverage:.1f}%")

    # Find differences
    print("\n" + "=" * 100)
    print("WORD-LEVEL ANALYSIS")
    print("=" * 100)

    json_word_set = set(normalize_word(w) for w in json_words if w.strip())
    html_word_set = set(normalize_word(w) for w in html_words if w.strip())

    missing_in_html = json_word_set - html_word_set
    extra_in_html = html_word_set - json_word_set

    print(f"\nUnique words in JSON: {len(json_word_set)}")
    print(f"Unique words in HTML: {len(html_word_set)}")
    print(f"Missing in HTML: {len(missing_in_html)} unique words")
    print(f"Extra in HTML: {len(extra_in_html)} unique words")

    if missing_in_html:
        print(f"\n📋 Words from JSON not in HTML (first 30):")
        for word in sorted(missing_in_html)[:30]:
            # Find context in JSON
            for span in page_data.get('text_spans', []):
                if normalize_word(span.get('text', '')) == word or word in span.get('text', '').lower():
                    context = span.get('text', '')[:100]
                    print(f"   - '{word}' in context: \"{context}...\"")
                    break

    if extra_in_html:
        print(f"\n⚠️  Words in HTML not in JSON (first 30):")
        for word in sorted(extra_in_html)[:30]:
            # Find context in HTML
            if word in html_text.lower():
                start = html_text.lower().find(word)
                context = html_text[max(0, start-50):min(len(html_text), start+50)]
                print(f"   - '{word}' in context: \"...{context}...\"")

    # Show full texts for comparison
    print("\n" + "=" * 100)
    print("FULL TEXT COMPARISON")
    print("=" * 100)

    print("\n[JSON TEXT] (first 500 chars):")
    print(f"{json_full_text[:500]}...\n")

    print("[HTML TEXT] (first 500 chars):")
    print(f"{html_text[:500]}...\n")

    # Check for common issues
    print("=" * 100)
    print("DIAGNOSTIC CHECKS")
    print("=" * 100)

    # Check if HTML has content from different page
    if extra_in_html:
        print(f"\n⚠️  {len(extra_in_html)} extra words in HTML vs JSON")
        print("   Possible causes:")
        print("   1. HTML generation added words not in PDF (hallucination)")
        print("   2. HTML contains content from adjacent page")
        print("   3. JSON extraction missed content from PDF")
        print("   4. HTML has navigation/metadata not in JSON")

    if missing_in_html:
        print(f"\n⚠️  {len(missing_in_html)} words in JSON not in HTML")
        print("   Possible causes:")
        print("   1. HTML generation dropped content")
        print("   2. HTML truncated at page boundaries")
        print("   3. Content is in JSON footer/headers that were filtered")


if __name__ == '__main__':
    main()
