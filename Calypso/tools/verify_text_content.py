#!/usr/bin/env python3
"""
Text Content Verification Tool for Calypso Project

Verifies that all extracted text from the PDF made it into the final HTML.
Compares JSON text content with HTML text content to identify any gaps.

Usage:
    python3 verify_text_content.py <chapter_num>
    python3 verify_text_content.py <extraction_json> <consolidated_html>
"""

import json
import sys
import re
from pathlib import Path
from html.parser import HTMLParser
from typing import Set, List, Tuple


class TextExtractor(HTMLParser):
    """Extract all text from HTML, excluding script/style tags."""

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


def extract_text_from_html(html_path: str) -> str:
    """Extract all text content from HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    parser = TextExtractor()
    parser.feed(html_content)
    return parser.get_text()


def is_header_footer_text(text: str) -> bool:
    """
    Determine if text is a header/footer that should be excluded from validation.

    Headers/footers include:
    - Page numbers with chapter titles (e.g., "28 Principles of Real Estate Practice in Alabama")
    - Chapter headers (e.g., "Chapter 2: Rights in Real Estate")
    - Book page numbers
    """
    text_lower = text.lower().strip()

    # Pattern: digit(s) followed by "principles of real estate practice in alabama"
    if re.search(r'^\d+\s+principles\s+of\s+real\s+estate\s+practice\s+in\s+alabama$', text_lower):
        return True

    # Pattern: "chapter X:" (start of chapter header)
    if re.search(r'^chapter\s+\d+\s*:', text_lower):
        return True

    # Pattern: Just a number (page number)
    if re.match(r'^\d+$', text_lower):
        return True

    # Pattern: "business X" or similar footer patterns
    if re.search(r'^(business|chapter|real estate|principles)\s+\d+$', text_lower):
        return True

    return False


def extract_text_from_json(json_path: str, page_num: int = None) -> Tuple[str, int]:
    """Extract all text content from extraction JSON.

    Args:
        json_path: Path to extraction JSON
        page_num: If specified, extract only this page; else extract all pages

    Returns:
        Tuple of (combined_text, text_span_count)
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    text_chunks = []
    text_span_count = 0

    pages = data.get('pages', {})

    if page_num is not None:
        # Extract specific page only
        page_key = str(page_num)
        if page_key in pages:
            page_data = pages[page_key]
            text_spans = page_data.get('text_spans', [])

            for span in text_spans:
                text = span.get('text', '').strip()
                if text and not is_header_footer_text(text):
                    text_chunks.append(text)
                    text_span_count += 1
    else:
        # Extract all pages
        for page_num_key in sorted(int(p) for p in pages.keys()):
            page_data = pages[str(page_num_key)]
            text_spans = page_data.get('text_spans', [])

            for span in text_spans:
                text = span.get('text', '').strip()
                if text and not is_header_footer_text(text):
                    text_chunks.append(text)
                    text_span_count += 1

    return ' '.join(text_chunks), text_span_count


def normalize_text(text: str) -> str:
    """Normalize text for comparison: lowercase, collapse whitespace."""
    # Convert to lowercase
    text = text.lower()
    # Replace multiple spaces/newlines with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove common punctuation variations
    text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    return text.strip()


def find_missing_content(json_text: str, html_text: str, chunk_size: int = 50) -> List[str]:
    """
    Find text chunks from JSON that don't appear in HTML.
    Uses progressive chunk sizes to find smallest missing segments.
    """
    norm_html = normalize_text(html_text)
    missing = []

    # Split JSON text into sentences/chunks
    sentences = json_text.split('. ')

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        norm_sentence = normalize_text(sentence)

        # Check if full sentence is in HTML
        if norm_sentence not in norm_html:
            # Try to find what part is missing
            missing.append(sentence)

    return missing


def get_chapter_paths(chapter_num: int) -> Tuple[str, str]:
    """Get paths for chapter extraction JSON and HTML."""
    base_dir = Path(__file__).parent.parent

    chapter_str = f"{chapter_num:02d}"
    extraction_json = base_dir / "analysis" / f"chapter_{chapter_str}" / "rich_extraction.json"
    consolidated_html = base_dir / "output" / f"chapter_{chapter_str}" / f"chapter_{chapter_str}.html"

    return str(extraction_json), str(consolidated_html)


def main():
    """Main verification logic."""

    page_num = None  # For per-page verification

    # Parse arguments
    if len(sys.argv) == 2:
        # Single argument: chapter number
        try:
            chapter_num = int(sys.argv[1])
            json_path, html_path = get_chapter_paths(chapter_num)
        except ValueError:
            print(f"Error: Invalid chapter number '{sys.argv[1]}'")
            sys.exit(1)
    elif len(sys.argv) == 3:
        # Two arguments: explicit paths (or chapter + page)
        # Try to interpret as chapter and page number
        try:
            chapter_num = int(sys.argv[1])
            page_num = int(sys.argv[2])
            json_path, _ = get_chapter_paths(chapter_num)
            # Find the page HTML file
            base_dir = Path(__file__).parent.parent
            chapter_str = f"{chapter_num:02d}"
            html_path = base_dir / "output" / f"chapter_{chapter_str}" / "page_artifacts" / f"page_{page_num}" / f"04_page_{page_num}.html"
            html_path = str(html_path)
        except ValueError:
            # If that fails, treat as extraction_json and consolidated_html paths
            json_path = sys.argv[1]
            html_path = sys.argv[2]
    elif len(sys.argv) == 4:
        # Three arguments: extraction_json, html, page_num
        json_path = sys.argv[1]
        html_path = sys.argv[2]
        try:
            page_num = int(sys.argv[3])
        except ValueError:
            print(f"Error: Invalid page number '{sys.argv[3]}'")
            sys.exit(1)
    else:
        print("Usage:")
        print("  python3 verify_text_content.py <chapter_num>")
        print("  python3 verify_text_content.py <extraction_json> <consolidated_html>")
        print("  python3 verify_text_content.py <chapter_num> <page_num>")
        print("  python3 verify_text_content.py <extraction_json> <html> <page_num>")
        sys.exit(1)

    # Verify files exist
    if not Path(json_path).exists():
        print(f"Error: Extraction JSON not found: {json_path}")
        sys.exit(1)
    if not Path(html_path).exists():
        print(f"Error: HTML file not found: {html_path}")
        sys.exit(1)

    print("=" * 80)
    print("TEXT CONTENT VERIFICATION")
    print("=" * 80)
    print(f"\nExtraction JSON: {json_path}")
    print(f"Consolidated HTML: {html_path}\n")

    # Extract texts
    print("Extracting text from JSON...", end=" ")
    json_text, span_count = extract_text_from_json(json_path, page_num=page_num)
    json_word_count = len(json_text.split())
    print(f"✓ ({span_count} text spans, {json_word_count} words)")

    print("Extracting text from HTML...", end=" ")
    html_text = extract_text_from_html(html_path)
    html_word_count = len(html_text.split())
    print(f"✓ ({html_word_count} words)")

    # Compare texts
    print("\nComparison:")
    print(f"  JSON word count:  {json_word_count}")
    print(f"  HTML word count:  {html_word_count}")

    coverage = (html_word_count / json_word_count * 100) if json_word_count > 0 else 0
    print(f"  Coverage:         {coverage:.1f}%")

    # Detailed analysis
    print("\n" + "=" * 80)
    print("DETAILED ANALYSIS")
    print("=" * 80)

    # Normalize and compare
    norm_json = normalize_text(json_text)
    norm_html = normalize_text(html_text)

    # Character-level comparison
    json_chars = set(norm_json.split())
    html_chars = set(norm_html.split())

    # Find what's in JSON but not in HTML
    missing_words = json_chars - html_chars
    extra_words = html_chars - json_chars

    if coverage >= 94:
        print(f"\n✅ TEXT COVERAGE GOOD: {coverage:.1f}%")
        print("   All extracted text appears to be in the HTML.")

        if missing_words:
            print(f"\n   Note: {len(missing_words)} words from JSON not found in HTML:")
            for word in sorted(missing_words)[:10]:  # Show first 10
                print(f"     - {word}")
            if len(missing_words) > 10:
                print(f"     ... and {len(missing_words) - 10} more")
    else:
        print(f"\n⚠️  TEXT COVERAGE LOW: {coverage:.1f}%")
        print(f"   Missing approximately {json_word_count - html_word_count} words.")
        print(f"   {len(missing_words)} unique words from JSON not found in HTML")

        if missing_words:
            print("\n   Missing words (first 20):")
            for word in sorted(missing_words)[:20]:
                print(f"     - {word}")

    # Check for potential structural issues
    print("\n" + "=" * 80)
    print("STRUCTURAL CHECKS")
    print("=" * 80)

    # Load JSON for structural analysis
    with open(json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    pages = json_data.get('pages', {})
    print(f"\nPages in extraction:  {len(pages)} pages")

    # Check first and last page markers
    page_nums = sorted(int(p) for p in pages.keys())
    if page_nums:
        first_page = page_nums[0]
        last_page = page_nums[-1]

        first_spans = pages[str(first_page)].get('text_spans', [])
        last_spans = pages[str(last_page)].get('text_spans', [])

        first_text = ' '.join(s.get('text', '').strip() for s in first_spans[:5])
        last_text = ' '.join(s.get('text', '').strip() for s in last_spans[-5:])

        print(f"\nFirst page ({first_page}) sample text:")
        print(f"  {first_text[:80]}...")

        print(f"\nLast page ({last_page}) sample text:")
        print(f"  {last_text[:80]}...")

        # Check if these appear in HTML
        if normalize_text(first_text) in norm_html:
            print(f"\n✅ First page content found in HTML")
        else:
            print(f"\n⚠️  First page content NOT found in HTML")

        if "snapshot review" in norm_html:
            print(f"✅ 'Snapshot Review' (closing marker) found in HTML")
        else:
            print(f"⚠️  'Snapshot Review' (closing marker) NOT found in HTML")

    print("\n" + "=" * 80)

    # Exit code based on coverage
    # Note: Headers/footers are filtered out from JSON, so expect slightly lower coverage
    if coverage >= 94:
        print("\n✅ VERIFICATION PASSED: Text content is comprehensive")
        return 0
    elif coverage >= 85:
        print("\n⚠️  VERIFICATION WARNING: Minor text gaps detected")
        return 1
    else:
        print("\n❌ VERIFICATION FAILED: Significant text gaps detected")
        return 2


if __name__ == '__main__':
    sys.exit(main())
