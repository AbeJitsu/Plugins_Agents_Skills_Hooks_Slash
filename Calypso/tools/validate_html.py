#!/usr/bin/env python3
"""
HTML validation script for Calypso generated chapters.

Validates continuous document format (single page, flowing content):
- Valid HTML5 structure
- Single page-container with page-content wrapper
- Required CSS classes for semantic styling
- Proper heading hierarchy (h1-h6)
- Structural requirements (chapter header, navigation, sections, exhibits)
- List integrity and paragraph validation

Document Format (v2):
- Single <div class="page-container"> wrapping <main class="page-content">
- Continuous flowing content (no page breaks/footers)
- Multiple sections with semantic classes
- Support for exhibits/tables with proper styling
"""

import sys
import re
import json
from pathlib import Path
from datetime import datetime

try:
    from html.parser import HTMLParser
except ImportError:
    print("Error: Could not import html.parser")
    sys.exit(1)


class HTMLValidator:
    """Validates Calypso HTML pages for structure and semantics."""

    def __init__(self, html_content):
        """Initialize with HTML content to validate."""
        self.html = html_content
        self.errors = []
        self.warnings = []
        self.info = []

        # Track state during parsing
        self.tags = []
        self.has_charset = False
        self.has_viewport = False
        self.has_title = False
        self.has_css_link = False
        self.has_page_container = False
        self.has_page_content = False
        self.has_chapter_header = False
        self.has_section_navigation = False
        self.has_section_heading = False
        self.has_footer = False
        self.heading_levels = []
        self.open_tags_stack = []
        self.classes_found = set()
        self.ids_found = set()
        self.p_count = 0
        self.ul_stack = []
        self.current_li_parent = None

    def validate(self):
        """Run all validations and return results."""
        self._check_html_structure()
        self._check_head_section()
        self._check_required_elements()
        self._check_heading_hierarchy()
        self._check_semantic_classes()
        self._check_lists()
        self._check_paragraphs()

        return {
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
        }

    def _check_html_structure(self):
        """Check basic HTML structure."""
        if not self.html.strip().startswith('<!DOCTYPE html>'):
            self.warnings.append("Missing or incorrect DOCTYPE declaration")

        if '<html' not in self.html.lower():
            self.errors.append("Missing <html> tag")

        if '</html>' not in self.html.lower():
            self.errors.append("Missing closing </html> tag")

        # Check for basic tag closure
        required_tags = [
            ('<body', '</body>'),
            ('<head', '</head>'),
            ('<main', '</main>')
        ]

        for open_tag, close_tag in required_tags:
            if open_tag in self.html.lower():
                if close_tag not in self.html.lower():
                    self.errors.append(f"Missing closing {close_tag} tag")

    def _check_head_section(self):
        """Check for required <head> elements."""
        # Check charset
        if 'charset' in self.html:
            self.has_charset = True
        else:
            self.warnings.append("Missing charset declaration in <meta>")

        # Check viewport
        if 'viewport' in self.html:
            self.has_viewport = True
        else:
            self.warnings.append("Missing viewport meta tag (mobile responsiveness)")

        # Check title
        if '<title>' in self.html and '</title>' in self.html:
            self.has_title = True
            title_match = re.search(r'<title>(.+?)</title>', self.html)
            if title_match:
                self.info.append(f"Page title: '{title_match.group(1)}'")
        else:
            self.errors.append("Missing <title> tag")

        # Check CSS link
        if 'href=' in self.html and ('.css' in self.html or 'styles' in self.html):
            self.has_css_link = True
        else:
            self.errors.append("Missing CSS stylesheet link")

    def _check_required_elements(self):
        """Check for required page structure elements."""
        # Single page-container (continuous document format)
        # Check for page-container class (exact or as part of class list)
        if re.search(r'class="[^"]*page-container[^"]*"', self.html):
            self.has_page_container = True
        else:
            self.errors.append("Missing .page-container element")

        # Check for page-content class (exact or as part of class list)
        if re.search(r'class="[^"]*page-content[^"]*"', self.html):
            self.has_page_content = True
        else:
            self.errors.append("Missing .page-content element")

        if re.search(r'class="[^"]*chapter-header[^"]*"', self.html):
            self.has_chapter_header = True
        else:
            self.warnings.append("Missing .chapter-header element")

        if re.search(r'class="[^"]*section-navigation[^"]*"', self.html):
            self.has_section_navigation = True
        else:
            self.warnings.append("Missing .section-navigation element (chapter navigation)")

        if re.search(r'class="[^"]*section-heading[^"]*"', self.html):
            self.has_section_heading = True
        else:
            self.warnings.append("Missing .section-heading element (main section heading)")

        # Footer is optional in continuous document format
        if '<footer' in self.html or 'class="page-footer"' in self.html:
            self.has_footer = True
            self.info.append("Document format: Paginated (contains footers)")
        else:
            self.info.append("Document format: Continuous (no page footers)")

    def _check_heading_hierarchy(self):
        """Check heading tags and hierarchy."""
        h_pattern = r'<h([1-6])[^>]*>(.+?)</h\1>'
        headings = re.findall(h_pattern, self.html, re.IGNORECASE)

        if not headings:
            self.warnings.append("No headings found on page")

        for level, text in headings:
            self.heading_levels.append(int(level))
            self.info.append(f"  h{level}: {text[:50]}...")

        # Check heading hierarchy (shouldn't jump levels drastically)
        if self.heading_levels:
            # First heading should ideally be h1
            if self.heading_levels[0] != 1:
                self.warnings.append(f"First heading is h{self.heading_levels[0]}, expected h1")

            # Check for large jumps (e.g., h1 directly to h4)
            for i in range(len(self.heading_levels) - 1):
                jump = self.heading_levels[i + 1] - self.heading_levels[i]
                if jump > 1:
                    self.warnings.append(f"Heading hierarchy jump: h{self.heading_levels[i]} → h{self.heading_levels[i+1]}")

    def _check_semantic_classes(self):
        """Check for proper semantic CSS classes."""
        found_classes = set()
        class_pattern = r'class="([^"]*)"'
        for match in re.finditer(class_pattern, self.html):
            classes = match.group(1).split()
            found_classes.update(classes)

        self.classes_found = found_classes

        # Check for key semantic classes (required for document structure)
        # Continuous document format: single chapter with flowing content
        key_classes = ['page-container', 'page-content', 'section-heading', 'paragraph', 'bullet-list']
        missing = [c for c in key_classes if c not in found_classes]
        if missing:
            self.warnings.append(f"Missing key semantic classes: {', '.join(missing)}")

        # Info about found classes
        self.info.append(f"Semantic classes used: {', '.join(sorted(found_classes))}")

    def _check_lists(self):
        """Check for proper list structure."""
        # Check for ul/ol without proper li children
        ul_pattern = r'<ul[^>]*>(.+?)</ul>'
        ol_pattern = r'<ol[^>]*>(.+?)</ol>'

        ul_matches = re.findall(ul_pattern, self.html, re.IGNORECASE | re.DOTALL)
        if ul_matches:
            for i, content in enumerate(ul_matches):
                # Match <li followed by whitespace or > to avoid catching <link> tags
                li_count = len(re.findall(r'<li[\s>]', content, re.IGNORECASE))
                self.info.append(f"Unordered list {i+1}: {li_count} items")

                if li_count == 0:
                    self.errors.append(f"<ul> element {i+1} has no <li> items")

        # Check for unclosed <li> tags using proper regex patterns
        # <li must be followed by whitespace or > to avoid matching <link>
        li_open = len(re.findall(r'<li[\s>]', self.html, re.IGNORECASE))
        li_close = len(re.findall(r'</li>', self.html, re.IGNORECASE))
        if li_open != li_close:
            self.warnings.append(f"Unmatched <li> tags: {li_open} opened, {li_close} closed")

    def _check_paragraphs(self):
        """Check paragraph elements."""
        p_count = len(re.findall(r'<p[^>]*>', self.html, re.IGNORECASE))
        self.info.append(f"Total paragraphs: {p_count}")

        # Check for empty paragraphs
        empty_p_pattern = r'<p[^>]*>\s*</p>'
        empty_p = re.findall(empty_p_pattern, self.html, re.IGNORECASE)
        if empty_p:
            self.warnings.append(f"Found {len(empty_p)} empty paragraph tags")

    def report(self):
        """Print validation report."""
        results = self.validate()

        print("\n" + "=" * 70)
        print("HTML VALIDATION REPORT")
        print("=" * 70)

        # Status
        status = "✓ VALID" if results['valid'] else "✗ INVALID"
        print(f"\nStatus: {status}")

        # Errors
        if results['errors']:
            print(f"\n❌ ERRORS ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"   • {error}")

        # Warnings
        if results['warnings']:
            print(f"\n⚠️  WARNINGS ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"   • {warning}")

        # Info
        if results['info']:
            print(f"\nℹ️  INFO:")
            for info in results['info']:
                print(f"   • {info}")

        print("\n" + "=" * 70)
        return results['valid']

    def save_json_report(self, output_path):
        """Save validation report as JSON file.

        Args:
            output_path (str): Path where JSON report should be saved

        Returns:
            bool: True if saved successfully, False otherwise
        """
        results = self.validate()

        # Prepare JSON report
        report_data = {
            "validation_type": "html_structure_and_semantic",
            "validation_timestamp": datetime.now().isoformat(),
            "status": "VALID" if results['valid'] else "INVALID",
            "valid": results['valid'],
            "error_count": len(results['errors']),
            "warning_count": len(results['warnings']),
            "info_count": len(results['info']),
            "errors": results['errors'],
            "warnings": results['warnings'],
            "info": results['info'],
            "semantic_classes_found": sorted(list(self.classes_found)),
        }

        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(report_data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving JSON report: {e}")
            return False


def main():
    """Main entry point.

    Usage:
        python3 validate_html.py <html_file>
            - Prints validation report to screen

        python3 validate_html.py <html_file> --json <output_path>
            - Saves validation report as JSON to output_path
            - Also prints report to screen

        python3 validate_html.py <html_file> --json-only <output_path>
            - Saves validation report as JSON only (no screen output)
    """
    if len(sys.argv) < 2:
        print("Usage: python3 validate_html.py <html_file> [--json <output_path>] [--json-only <output_path>]")
        sys.exit(1)

    html_file = sys.argv[1]
    json_output = None
    json_only = False

    # Parse command line arguments
    if '--json' in sys.argv:
        idx = sys.argv.index('--json')
        if idx + 1 < len(sys.argv):
            json_output = sys.argv[idx + 1]

    if '--json-only' in sys.argv:
        idx = sys.argv.index('--json-only')
        if idx + 1 < len(sys.argv):
            json_output = sys.argv[idx + 1]
            json_only = True

    try:
        with open(html_file, 'r') as f:
            html_content = f.read()
    except FileNotFoundError:
        print(f"Error: File '{html_file}' not found")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    validator = HTMLValidator(html_content)

    # Generate JSON report if requested
    if json_output:
        json_success = validator.save_json_report(json_output)
        if not json_success:
            sys.exit(1)

    # Print screen report unless json-only requested
    if not json_only:
        is_valid = validator.report()
    else:
        # Still validate, but don't print
        results = validator.validate()
        is_valid = results['valid']
        if json_output:
            print(f"✓ Validation report saved to {json_output}")

    sys.exit(0 if is_valid else 1)


if __name__ == '__main__':
    main()
