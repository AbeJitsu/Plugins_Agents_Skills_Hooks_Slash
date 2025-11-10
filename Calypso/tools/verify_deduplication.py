#!/usr/bin/env python3
"""
Deduplication Validator - Detects duplicate content in HTML pages/chapters
Checks for:
- Duplicate chapter headers
- Duplicate section headings
- Duplicate paragraphs
- Repeated content blocks
"""

import sys
import re
from pathlib import Path
from collections import defaultdict
from html.parser import HTMLParser


class ContentExtractor(HTMLParser):
    """Extract semantic content from HTML"""

    def __init__(self):
        super().__init__()
        self.content_blocks = []
        self.current_block = None
        self.in_header = False
        self.in_footer = False
        self.in_content = False

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and any(k == 'class' and 'chapter-header' in v for k, v in attrs):
            self.in_header = True
        elif tag == 'footer' and any(k == 'class' for k, v in attrs):
            self.in_footer = True
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.current_block = {'type': f'heading_{tag}', 'content': '', 'tag': tag}
        elif tag == 'p' and any(k == 'class' and 'paragraph' in v for k, v in attrs):
            self.current_block = {'type': 'paragraph', 'content': '', 'tag': 'p'}
        elif tag in ['ul', 'ol'] and any(k == 'class' and 'bullet-list' in v for k, v in attrs):
            self.current_block = {'type': 'list', 'content': '', 'tag': tag}
        elif tag == 'table' and any(k == 'class' and 'exhibit-table' in v for k, v in attrs):
            self.current_block = {'type': 'table', 'content': '', 'tag': 'table'}

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_header:
            self.in_header = False
        elif tag == 'footer':
            self.in_footer = False
        elif self.current_block and self.current_block.get('tag') == tag:
            if self.current_block['content'].strip():
                self.content_blocks.append(self.current_block)
            self.current_block = None

    def handle_data(self, data):
        if self.current_block:
            self.current_block['content'] += data


def extract_html_content(html_path):
    """Extract semantic content from HTML file"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        parser = ContentExtractor()
        parser.feed(html)
        return parser.content_blocks
    except Exception as e:
        print(f"Error extracting HTML: {e}")
        return []


def find_duplicates(content_blocks):
    """Find duplicate content blocks"""
    seen_content = defaultdict(list)
    duplicates = []

    for i, block in enumerate(content_blocks):
        # Normalize content for comparison
        normalized = ' '.join(block['content'].split())

        if len(normalized) > 50:  # Only check significant blocks
            if normalized in seen_content:
                duplicates.append({
                    'content': normalized[:100],
                    'type': block['type'],
                    'positions': [block_idx for block_idx, cb in enumerate(content_blocks)
                                if ' '.join(cb['content'].split()) == normalized],
                    'count': len(seen_content[normalized]) + 1
                })
            seen_content[normalized].append(i)

    # Remove duplicates from the list
    unique_duplicates = {}
    for dup in duplicates:
        key = tuple(dup['positions'])
        if key not in unique_duplicates:
            unique_duplicates[key] = dup

    return list(unique_duplicates.values())


def check_duplicate_headers(html_path):
    """Specifically check for duplicate chapter headers"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Find all chapter-header divs
        chapter_headers = re.findall(
            r'<div class="chapter-header">.*?</div>',
            html,
            re.DOTALL
        )

        return len(chapter_headers)
    except Exception as e:
        print(f"Error checking headers: {e}")
        return 0


def verify_page(chapter, page):
    """Verify a single page for duplication"""
    page_dir = Path(f"Calypso/output/chapter_{chapter:02d}/page_artifacts/page_{page:02d}")
    html_file = page_dir / f"04_page_{page:02d}.html"

    if not html_file.exists():
        print(f"❌ HTML file not found: {html_file}")
        return False

    print("\n" + "=" * 80)
    print(f"DEDUPLICATION CHECK - Chapter {chapter}, Page {page}")
    print("=" * 80 + "\n")

    # Check for duplicate chapter headers
    header_count = check_duplicate_headers(str(html_file))
    if header_count > 1:
        print(f"⚠️  DUPLICATE HEADERS DETECTED: {header_count} chapter-header divs found")
        print(f"   (Expected: 1 at page opening, 0 on continuation pages)")
        return False
    elif header_count == 1:
        print(f"✓ Chapter header count OK: {header_count}")

    # Extract and check for duplicate content
    content_blocks = extract_html_content(str(html_file))
    if not content_blocks:
        print("✓ No content blocks to check")
        return True

    print(f"✓ Content blocks extracted: {len(content_blocks)}")

    duplicates = find_duplicates(content_blocks)
    if duplicates:
        print(f"\n⚠️  DUPLICATE CONTENT DETECTED: {len(duplicates)} duplicate blocks")
        for dup in duplicates:
            print(f"\n  Type: {dup['type']} (appears {dup['count']} times)")
            print(f"  Positions: {dup['positions']}")
            preview = dup['content'][:80].replace('\n', ' ')
            print(f"  Content: {preview}...")
        return False
    else:
        print("✓ No duplicate content blocks detected")

    print("\n" + "=" * 80)
    print("✅ DEDUPLICATION CHECK PASSED")
    print("=" * 80)
    return True


def verify_chapter(chapter):
    """Verify entire chapter for duplication"""
    chapter_dir = Path(f"Calypso/output/chapter_{chapter:02d}")
    html_file = chapter_dir / f"chapter_{chapter:02d}.html"

    if not html_file.exists():
        print(f"❌ Chapter HTML file not found: {html_file}")
        return False

    print("\n" + "=" * 80)
    print(f"DEDUPLICATION CHECK - Chapter {chapter} (Consolidated)")
    print("=" * 80 + "\n")

    # Check for duplicate chapter headers
    header_count = check_duplicate_headers(str(html_file))
    if header_count > 1:
        print(f"❌ DUPLICATE HEADERS DETECTED: {header_count} chapter-header divs found")
        print(f"   (Expected: 1 at chapter opening)")
        print(f"\n   This indicates the consolidation added extra headers.")
        print(f"   Remove duplicate chapter-header sections manually.")
        return False
    elif header_count == 1:
        print(f"✓ Chapter header count OK: {header_count}")
    else:
        print(f"⚠️  No chapter headers found (expected 1)")

    # Extract and check for duplicate content
    content_blocks = extract_html_content(str(html_file))
    if not content_blocks:
        print("⚠️  No content blocks extracted")
        return True

    print(f"✓ Content blocks extracted: {len(content_blocks)}")

    duplicates = find_duplicates(content_blocks)
    if duplicates:
        print(f"\n❌ DUPLICATE CONTENT DETECTED: {len(duplicates)} duplicate blocks")
        for dup in duplicates:
            print(f"\n  Type: {dup['type']} (appears {dup['count']} times)")
            print(f"  Positions: {dup['positions']}")
            preview = dup['content'][:80].replace('\n', ' ')
            print(f"  Content: {preview}...")
        return False
    else:
        print("✓ No duplicate content blocks detected")

    print("\n" + "=" * 80)
    print("✅ DEDUPLICATION CHECK PASSED")
    print("=" * 80)
    return True


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python3 verify_deduplication.py <chapter> [page]")
        print("  - Verify chapter consolidation: python3 verify_deduplication.py 1")
        print("  - Verify specific page: python3 verify_deduplication.py 1 6")
        sys.exit(1)

    chapter = int(sys.argv[1])

    if len(sys.argv) > 2:
        # Verify specific page
        page = int(sys.argv[2])
        success = verify_page(chapter, page)
    else:
        # Verify chapter
        success = verify_chapter(chapter)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
