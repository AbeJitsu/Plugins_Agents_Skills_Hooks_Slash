#!/usr/bin/env python3
"""
Detailed Page Diff Tool for Calypso Project

Shows exactly what text differences exist between extraction JSON and generated HTML.
Helps identify if 95-100% coverage is due to formatting (acceptable) or missing content (critical).

Usage:
    python3 detailed_page_diff.py <chapter_num> <page_num>
    python3 detailed_page_diff.py 1 6  # Show diff for Chapter 1, Page 6
"""

import json
import sys
import re
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Set, Dict


class TextExtractor(HTMLParser):
    """Extract all text from HTML, preserving word boundaries."""

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


def extract_text_from_json(json_path: str, page_num: int) -> str:
    """Extract text for specific page from JSON."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pages = data.get('pages', {})
    page_key = str(page_num)

    text_chunks = []
    if page_key in pages:
        page_data = pages[page_key]
        text_spans = page_data.get('text_spans', [])
        for span in text_spans:
            text = span.get('text', '').strip()
            if text:
                text_chunks.append(text)

    return ' '.join(text_chunks)


def tokenize_words(text: str) -> List[str]:
    """Split text into words, preserving hyphenated words."""
    # Split on whitespace
    words = text.split()
    return words


def normalize_word(word: str) -> str:
    """Normalize word for comparison."""
    # Remove trailing punctuation but preserve hyphens within words
    word = word.lower()
    # Keep only word characters and hyphens
    word = re.sub(r'[^\w\-]', '', word)
    return word


def find_word_sequences(words: List[str], context_size: int = 3) -> Dict:
    """Create a map of word sequences for finding missing content."""
    sequences = {}
    for i in range(len(words) - context_size):
        # Create a sequence key (normalized)
        seq = ' '.join(normalize_word(w) for w in words[i:i+context_size])
        if seq not in sequences:
            sequences[seq] = []
        sequences[seq].append({
            'index': i,
            'original': ' '.join(words[i:i+context_size]),
            'start': i,
            'end': i + context_size
        })
    return sequences


def find_missing_and_extra(json_words: List[str], html_words: List[str]) -> tuple:
    """Find missing and extra words with context."""
    json_normalized = [normalize_word(w) for w in json_words]
    html_normalized = [normalize_word(w) for w in html_words]

    json_set = set(json_normalized)
    html_set = set(html_normalized)

    # Find words in JSON but not in HTML
    missing_in_html = json_set - html_set

    # Find words in HTML but not in JSON
    extra_in_html = html_set - json_set

    return missing_in_html, extra_in_html


def find_missing_context(json_words: List[str], html_words: List[str], missing_words: Set[str], context_size: int = 5) -> List[Dict]:
    """Find missing words with their context in JSON."""
    json_normalized = [normalize_word(w) for w in json_words]
    missing_context = []

    for i, normalized in enumerate(json_normalized):
        if normalized in missing_words:
            start = max(0, i - context_size)
            end = min(len(json_words), i + context_size + 1)
            context = ' '.join(json_words[start:end])

            missing_context.append({
                'word': json_words[i],
                'original_word': json_words[i],
                'position': i,
                'context': context,
                'before': ' '.join(json_words[max(0, i-2):i]),
                'after': ' '.join(json_words[i+1:min(len(json_words), i+3)])
            })

    return missing_context


def main():
    """Main diff analysis."""

    if len(sys.argv) != 3:
        print("Usage: python3 detailed_page_diff.py <chapter_num> <page_num>")
        print("Example: python3 detailed_page_diff.py 1 6")
        sys.exit(1)

    try:
        chapter_num = int(sys.argv[1])
        page_num = int(sys.argv[2])
    except ValueError:
        print("Error: chapter_num and page_num must be integers")
        sys.exit(1)

    # Build paths
    base_dir = Path(__file__).parent.parent
    chapter_str = f"{chapter_num:02d}"

    json_path = base_dir / "analysis" / f"chapter_{chapter_str}" / "rich_extraction.json"
    html_path = base_dir / "output" / f"chapter_{chapter_str}" / "page_artifacts" / f"page_{page_num}" / f"04_page_{page_num}.html"

    # Verify files exist
    if not json_path.exists():
        print(f"Error: JSON not found: {json_path}")
        sys.exit(1)
    if not html_path.exists():
        print(f"Error: HTML not found: {html_path}")
        sys.exit(1)

    print("\n" + "=" * 90)
    print(f"DETAILED PAGE DIFF: Chapter {chapter_num}, Page {page_num}")
    print("=" * 90)

    # Extract texts
    print(f"\nExtracting from JSON... ", end="", flush=True)
    json_text = extract_text_from_json(str(json_path), page_num)
    print("✓")

    print(f"Extracting from HTML... ", end="", flush=True)
    html_text = extract_text_from_html(str(html_path))
    print("✓")

    # Tokenize
    json_words = tokenize_words(json_text)
    html_words = tokenize_words(html_text)

    json_word_count = len(json_words)
    html_word_count = len(html_words)
    coverage = (html_word_count / json_word_count * 100) if json_word_count > 0 else 0

    print("\n" + "-" * 90)
    print("SUMMARY")
    print("-" * 90)
    print(f"JSON words:    {json_word_count}")
    print(f"HTML words:    {html_word_count}")
    print(f"Difference:    {html_word_count - json_word_count:+d}")
    print(f"Coverage:      {coverage:.1f}%")
    print()

    # Status color
    if coverage > 100:
        status = f"❌ REJECTED: HTML contains extra content not in original page"
    elif coverage >= 100:
        status = f"✅ PERFECT: 100% match"
    elif coverage >= 99:
        status = f"✅ EXCELLENT: 1% or less missing (likely formatting)"
    elif coverage >= 95:
        status = f"✅ ACCEPTABLE: 5% or less missing (review recommended)"
    else:
        status = f"❌ FAILED: >5% missing content"

    print(f"Status: {status}")
    print()

    # Find differences
    missing_words, extra_words = find_missing_and_extra(json_words, html_words)

    # Analysis by coverage level
    if coverage > 105:
        print("🚨 CRITICAL ISSUE: HTML contains 5%+ MORE words than JSON")
        print("   This typically means WRONG PAGE CONTENT was generated")
        print("   → REGENERATE THIS PAGE IMMEDIATELY")
        print()
        print(f"Extra words ({len(extra_words)} unique):")
        for word in sorted(extra_words)[:20]:
            print(f"  + {word}")
        if len(extra_words) > 20:
            print(f"  ... and {len(extra_words) - 20} more")

    elif coverage < 100 and missing_words:
        print(f"MISSING CONTENT: {len(missing_words)} unique words not in HTML")
        print()

        # Categorize missing words
        critical_words = []
        formatting_words = []

        for word in sorted(missing_words):
            # Words that are likely formatting/punctuation
            if all(c in '-•–—.' for c in word) or len(word) <= 1:
                formatting_words.append(word)
            else:
                critical_words.append(word)

        if formatting_words:
            print(f"Formatting/Punctuation ({len(formatting_words)} items - probably OK):")
            for word in formatting_words[:15]:
                print(f"  - {word}")
            print()

        if critical_words:
            print(f"⚠️  Content Words ({len(critical_words)} items - need review):")
            for word in critical_words[:20]:
                print(f"  - {word}")
            if len(critical_words) > 20:
                print(f"  ... and {len(critical_words) - 20} more")
            print()

            # Show context for critical missing words
            print("-" * 90)
            print("CONTEXT FOR MISSING CONTENT WORDS")
            print("-" * 90)

            missing_context = find_missing_context(
                json_words, html_words, critical_words, context_size=3
            )

            for item in missing_context[:10]:
                print(f"\nMissing: {item['original_word']}")
                print(f"Context: ...{item['before']} [{item['original_word']}] {item['after']}...")
                if len(missing_context) > 10:
                    print(f"\n... showing first 10 of {len(missing_context)} missing items")

    elif extra_words and coverage < 100:
        print(f"UNUSUAL: HTML is missing words BUT has extra words")
        print(f"Extra words ({len(extra_words)} unique):")
        for word in sorted(extra_words)[:10]:
            print(f"  + {word}")

    print()
    print("=" * 90)
    print("RECOMMENDATION")
    print("=" * 90)

    if coverage > 100:
        print("\n❌ REJECT THIS PAGE - Extra content detected")
        print("   HTML has content not in original PDF")
        print("   REGENERATE IMMEDIATELY")
    elif coverage >= 100:
        print("\n✅ PERFECT - 100% match")
        print("   Ready for consolidation")
    elif coverage >= 99.5:
        print("\n✅ EXCELLENT - <0.5% missing (likely formatting)")
        print("   Safe for consolidation")
    elif coverage >= 98:
        print("\n✅ GOOD - <2% missing")
        print("   Acceptable if missing items are formatting only")
    elif coverage >= 95:
        print("\n✅ ACCEPTABLE - Up to 5% missing")
        print("   Check if missing words are critical content")
        print("   If only formatting: OK for consolidation")
        print("   If content words: REGENERATE PAGE")
    else:
        print("\n❌ FAIL - >5% missing")
        print("   Do not consolidate until fixed")
        print("   REGENERATE PAGE")

    print()


if __name__ == '__main__':
    main()
