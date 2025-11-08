#!/usr/bin/env python3
"""
Convert extracted chapter content to clean HTML with external CSS.
Uses detected patterns to apply semantic classes.
"""

import json
import os
import re
import sys
from html import escape


def load_conversion_rules(analysis_dir):
    """Load conversion rules from analysis."""
    rules_file = os.path.join(analysis_dir, "conversion_rules.json")

    if os.path.exists(rules_file):
        with open(rules_file) as f:
            return json.load(f)

    # Default rules if analysis hasn't run
    return {
        "heading_rules": {
            "h1": {"pattern": "^[A-Z\\s]{10,}$"},
            "h2": {"pattern": "^(chapter|section|part)\\s+\\d+"},
            "h3": {"pattern": "^\\d+\\.\\s+"},
        },
        "text_rules": {
            "list": {"pattern": "^[-•*]\\s+|^\\d+\\)\\s+"},
            "code": {"pattern": "^```|^\\s{4,}"},
        },
    }


def classify_line(line, rules):
    """Classify a line of text based on rules."""
    stripped = line.strip()

    if not stripped:
        return "empty", stripped

    # Check heading rules
    for heading_level, heading_rule in rules.get("heading_rules", {}).items():
        pattern = heading_rule.get("pattern", "")
        if pattern and re.match(pattern, stripped, re.IGNORECASE):
            return heading_level, stripped

    # Check text rules
    if re.match(rules.get("text_rules", {}).get("list", {}).get("pattern", "^$"), stripped):
        return "list", stripped

    if re.match(rules.get("text_rules", {}).get("code", {}).get("pattern", "^$"), stripped):
        return "code", stripped

    # Default to paragraph
    return "paragraph", stripped


def text_to_html(text_content, rules, chapter_num):
    """Convert text content to HTML."""
    html_parts = []
    in_code_block = False
    in_list = False
    in_paragraph = False
    paragraph_lines = []

    lines = text_content.split("\n")

    for line in lines:
        # Handle page breaks
        if "---PAGE_BREAK---" in line:
            # Flush current elements
            if paragraph_lines:
                html_parts.append(
                    f"<p class='paragraph'>{escape(' '.join(paragraph_lines))}</p>\n"
                )
                paragraph_lines = []
            if in_list:
                html_parts.append("</ul>\n")
                in_list = False

            html_parts.append("<div class='page-break'></div>\n")
            continue

        line_class, stripped = classify_line(line, rules)

        # Handle different line types
        if line_class == "empty":
            if paragraph_lines:
                html_parts.append(
                    f"<p class='paragraph'>{escape(' '.join(paragraph_lines))}</p>\n"
                )
                paragraph_lines = []
            if in_list:
                html_parts.append("</ul>\n")
                in_list = False

        elif line_class == "h1":
            if paragraph_lines:
                html_parts.append(
                    f"<p class='paragraph'>{escape(' '.join(paragraph_lines))}</p>\n"
                )
                paragraph_lines = []
            if in_list:
                html_parts.append("</ul>\n")
                in_list = False
            html_parts.append(f"<h1 class='chapter-title'>{escape(stripped)}</h1>\n")

        elif line_class == "h2":
            if paragraph_lines:
                html_parts.append(
                    f"<p class='paragraph'>{escape(' '.join(paragraph_lines))}</p>\n"
                )
                paragraph_lines = []
            if in_list:
                html_parts.append("</ul>\n")
                in_list = False
            html_parts.append(f"<h2 class='section-title'>{escape(stripped)}</h2>\n")

        elif line_class == "h3":
            if paragraph_lines:
                html_parts.append(
                    f"<p class='paragraph'>{escape(' '.join(paragraph_lines))}</p>\n"
                )
                paragraph_lines = []
            if in_list:
                html_parts.append("</ul>\n")
                in_list = False
            html_parts.append(f"<h3 class='subsection-title'>{escape(stripped)}</h3>\n")

        elif line_class == "list":
            if paragraph_lines:
                html_parts.append(
                    f"<p class='paragraph'>{escape(' '.join(paragraph_lines))}</p>\n"
                )
                paragraph_lines = []

            if not in_list:
                html_parts.append("<ul class='content-list'>\n")
                in_list = True

            # Remove list markers
            item_text = re.sub(r"^[-•*]\s+|^\\d+\\)\\s+", "", stripped)
            html_parts.append(f"<li class='list-item'>{escape(item_text)}</li>\n")

        elif line_class == "code":
            if paragraph_lines:
                html_parts.append(
                    f"<p class='paragraph'>{escape(' '.join(paragraph_lines))}</p>\n"
                )
                paragraph_lines = []
            if in_list:
                html_parts.append("</ul>\n")
                in_list = False

            if stripped.startswith("```"):
                if not in_code_block:
                    html_parts.append("<pre class='code-block'><code>\n")
                    in_code_block = True
                else:
                    html_parts.append("</code></pre>\n")
                    in_code_block = False
            elif in_code_block:
                html_parts.append(escape(stripped) + "\n")

        elif line_class == "paragraph":
            if in_list:
                html_parts.append("</ul>\n")
                in_list = False
            if in_code_block:
                html_parts.append("</code></pre>\n")
                in_code_block = False

            if stripped:
                paragraph_lines.append(stripped)

    # Flush remaining content
    if paragraph_lines:
        html_parts.append(f"<p class='paragraph'>{escape(' '.join(paragraph_lines))}</p>\n")
    if in_list:
        html_parts.append("</ul>\n")
    if in_code_block:
        html_parts.append("</code></pre>\n")

    return "".join(html_parts)


def create_html_document(chapter_num, chapter_title, content_html):
    """Create a complete HTML document."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chapter {chapter_num}: {escape(chapter_title)}</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="container">
        <header class="chapter-header">
            <h1>Chapter {chapter_num}: {escape(chapter_title)}</h1>
        </header>

        <main class="chapter-content">
{content_html}
        </main>

        <footer class="chapter-footer">
            <p>Chapter {chapter_num}: {escape(chapter_title)}</p>
        </footer>
    </div>
</body>
</html>
"""
    return html


def convert_chapter_to_html(chapter_dir, output_dir, analysis_dir):
    """Convert a single chapter to HTML."""
    # Load metadata
    metadata_file = os.path.join(chapter_dir, "metadata.json")
    content_file = os.path.join(chapter_dir, "content.txt")

    if not os.path.exists(metadata_file) or not os.path.exists(content_file):
        print(f"Warning: Missing files in {chapter_dir}")
        return

    with open(metadata_file) as f:
        metadata = json.load(f)

    with open(content_file) as f:
        content_text = f.read()

    # Load rules
    rules = load_conversion_rules(analysis_dir)

    # Convert to HTML
    print(f"Converting Chapter {metadata['chapter']}: {metadata['title']}...")
    content_html = text_to_html(content_text, rules, metadata["chapter"])
    full_html = create_html_document(metadata["chapter"], metadata["title"], content_html)

    # Save HTML
    output_file = os.path.join(
        output_dir, f"chapter_{metadata['chapter']:02d}.html"
    )
    with open(output_file, "w") as f:
        f.write(full_html)

    print(f"Saved: {output_file}")


def main():
    chapters_dir = "../chapters"
    output_dir = "../output"
    analysis_dir = "../analysis"

    if not os.path.exists(chapters_dir):
        print(f"Error: chapters directory not found. Run chapter_extractor.py first.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Convert all chapters
    chapter_dirs = sorted(
        [
            d
            for d in os.listdir(chapters_dir)
            if os.path.isdir(os.path.join(chapters_dir, d))
        ]
    )

    if not chapter_dirs:
        print("No chapters found. Run chapter_extractor.py first.")
        sys.exit(1)

    for chapter_folder in chapter_dirs:
        chapter_path = os.path.join(chapters_dir, chapter_folder)
        convert_chapter_to_html(chapter_path, output_dir, analysis_dir)

    print(f"\nAll chapters converted. HTML files saved to: {output_dir}")


if __name__ == "__main__":
    main()
