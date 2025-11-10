#!/usr/bin/env python3
"""
Remove footer and header elements from HTML files.

Targets:
- <footer class="page-footer"> elements
- <header class="page-header"> elements with page-number class spans
- <p class="paragraph"><small>FOOTER_TEXT</small></p> patterns

Footer text patterns to remove:
- "[number] Principles of Real Estate Practice in Alabama"
- "Chapter [number]: The Real Estate Business [number]"

Usage:
    python3 remove_footers.py <file_path>
    python3 remove_footers.py <directory_path>  # Recursively processes all HTML files
"""

import sys
import os
import re
from pathlib import Path
from bs4 import BeautifulSoup


def is_footer_text(text):
    """
    Check if text matches footer patterns.

    Patterns:
    - "[number] Principles of Real Estate Practice in Alabama"
    - "Chapter [number]: The Real Estate Business [number]"
    """
    # Strip whitespace
    text = text.strip()

    # Pattern 1: "X Principles of Real Estate Practice in Alabama"
    if re.match(r'^\d+\s+Principles of Real Estate Practice in Alabama$', text):
        return True

    # Pattern 2: "Chapter X: The Real Estate Business Y"
    if re.match(r'^Chapter\s+\d+:\s+The Real Estate Business\s+\d+$', text):
        return True

    return False


def remove_footers_from_html(file_path):
    """
    Remove footer and header elements from a single HTML file.

    Args:
        file_path: Path to HTML file

    Returns:
        tuple: (success: bool, message: str, removed_count: int)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')
        removed_count = 0

        # Remove footer elements with class "page-footer"
        for footer in soup.find_all('footer', class_='page-footer'):
            footer.decompose()
            removed_count += 1

        # Remove header elements with class "page-header"
        for header in soup.find_all('header', class_='page-header'):
            header.decompose()
            removed_count += 1

        # Remove embedded footer text in paragraphs
        # Target: <p class="paragraph"><small>FOOTER_TEXT</small></p>
        for para in soup.find_all('p', class_='paragraph'):
            # Check if paragraph contains only a small tag with footer text
            small_tag = para.find('small')
            if small_tag:
                small_text = small_tag.get_text()
                if is_footer_text(small_text):
                    para.decompose()
                    removed_count += 1

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify()))

        return True, f"Removed {removed_count} footer/header elements", removed_count

    except Exception as e:
        return False, f"Error processing {file_path}: {str(e)}", 0


def process_files(target_path):
    """
    Process either a single file or directory of HTML files.

    Args:
        target_path: Path to file or directory
    """
    target = Path(target_path)
    total_removed = 0
    files_processed = 0

    if target.is_file():
        # Single file
        if target.suffix.lower() == '.html':
            success, message, count = remove_footers_from_html(str(target))
            print(f"{'✓' if success else '✗'} {target.name}: {message}")
            if success:
                files_processed += 1
                total_removed += count
        else:
            print(f"✗ Not an HTML file: {target}")

    elif target.is_dir():
        # Directory - process all HTML files recursively
        html_files = list(target.rglob('*.html'))
        if not html_files:
            print(f"No HTML files found in {target}")
            return

        print(f"Processing {len(html_files)} HTML file(s)...\n")

        for html_file in sorted(html_files):
            success, message, count = remove_footers_from_html(str(html_file))
            status = '✓' if success else '✗'
            rel_path = html_file.relative_to(target)
            print(f"{status} {rel_path}: {message}")

            if success:
                files_processed += 1
                total_removed += count

        print(f"\n{'='*60}")
        print(f"Total: {files_processed} file(s) processed, {total_removed} element(s) removed")

    else:
        print(f"✗ Path not found: {target}")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file_or_directory>")
        sys.exit(1)

    process_files(sys.argv[1])
