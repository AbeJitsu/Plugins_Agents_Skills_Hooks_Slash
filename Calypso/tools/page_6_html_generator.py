#!/usr/bin/env python3
"""
Generate semantic HTML for Page 6 (Chapter 1, First Page)
Uses extracted pattern analysis to recreate page with clean semantic HTML structure.
Uses unified global CSS stylesheet for consistent styling across all chapters.
"""

import json
import os
import sys
from html import escape


def load_pattern_analysis(analysis_file):
    """Load the page 6 pattern analysis."""
    if not os.path.exists(analysis_file):
        print(f"Error: {analysis_file} not found")
        sys.exit(1)

    with open(analysis_file) as f:
        return json.load(f)


def generate_chapter_title_block(block_data):
    """Generate HTML for the large chapter title."""
    text = block_data["text"]
    # Split "1 The Real Estate Business" into number and title
    parts = text.split(" ", 1)
    number = parts[0] if len(parts) > 0 else "1"
    title = parts[1] if len(parts) > 1 else text

    html = f'''
    <div class="text-block chapter-title-block" style="left: {block_data['position']['x']}pt; top: {block_data['position']['y']}pt; width: {block_data['position']['width']}pt; height: {block_data['position']['height']}pt;">
        <h1 class="chapter-title">
            <span class="chapter-number">{escape(number)}</span>
            <span class="chapter-title-text">{escape(title)}</span>
        </h1>
    </div>
'''
    return html


def generate_section_overview_block(block_data):
    """Generate HTML for the section overview (like a TOC)."""
    text = block_data["text"]
    sections = [s.strip() for s in text.split("  ") if s.strip()]

    html = f'''
    <div class="text-block section-overview" style="left: {block_data['position']['x']}pt; top: {block_data['position']['y']}pt; width: {block_data['position']['width']}pt; height: {block_data['position']['height']}pt;">
        <nav class="section-overview-nav">
'''
    for section in sections:
        html += f'            <span class="overview-item">{escape(section)}</span>\n'

    html += '''        </nav>
    </div>
'''
    return html


def generate_section_heading_block(block_data):
    """Generate HTML for section headings (e.g., 'REAL ESTATE PROFESSIONS')."""
    text = block_data["text"]

    html = f'''
    <div class="text-block section-heading-block" style="left: {block_data['position']['x']}pt; top: {block_data['position']['y']}pt; width: {block_data['position']['width']}pt; height: {block_data['position']['height']}pt;">
        <h2 class="section-heading">{escape(text)}</h2>
    </div>
'''
    return html


def generate_subsection_labels_block(block_data):
    """Generate HTML for subsection labels."""
    text = block_data["text"]
    labels = [s.strip() for s in text.split("  ") if s.strip()]

    html = f'''
    <div class="text-block subsection-labels-block" style="left: {block_data['position']['x']}pt; top: {block_data['position']['y']}pt; width: {block_data['position']['width']}pt; height: {block_data['position']['height']}pt;">
        <div class="subsection-labels">
'''
    for label in labels:
        html += f'            <h3 class="subsection-label">{escape(label)}</h3>\n'

    html += '''        </div>
    </div>
'''
    return html


def generate_paragraph_block(block_data, is_italic=False):
    """Generate HTML for paragraph text."""
    text = block_data["text"]

    tag = "em" if is_italic else "span"

    html = f'''
    <div class="text-block paragraph-block" style="left: {block_data['position']['x']}pt; top: {block_data['position']['y']}pt; width: {block_data['position']['width']}pt; height: {block_data['position']['height']}pt;">
        <p class="paragraph"><{tag}>{escape(text)}</{tag}></p>
    </div>
'''
    return html


def generate_bullet_list_block(block_data):
    """Generate HTML for bullet points."""
    text = block_data["text"]
    # Split on the bullet character \uf034
    items = text.split("\uf034")
    items = [item.strip() for item in items if item.strip()]

    html = f'''
    <div class="text-block bullet-list-block" style="left: {block_data['position']['x']}pt; top: {block_data['position']['y']}pt; width: {block_data['position']['width']}pt; height: {block_data['position']['height']}pt;">
        <ul class="bullet-list">
'''
    for item in items:
        html += f'            <li class="bullet-item">{escape(item)}</li>\n'

    html += '''        </ul>
    </div>
'''
    return html


def generate_page_footer_block(block_data):
    """Generate HTML for page footer."""
    text = block_data["text"]

    html = f'''
    <div class="text-block page-footer-block" style="left: {block_data['position']['x']}pt; top: {block_data['position']['y']}pt; width: {block_data['position']['width']}pt; height: {block_data['position']['height']}pt;">
        <footer class="page-footer">{escape(text)}</footer>
    </div>
'''
    return html


def generate_page_html(analysis_data):
    """Generate clean semantic HTML page from pattern analysis (no absolute positioning)."""

    text_blocks = analysis_data["text_blocks"]

    # Create mapping of block numbers to content
    blocks_map = {}
    for block in text_blocks:
        blocks_map[block["block_num"]] = block

    # Build HTML with proper semantic structure and reading order
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chapter 1: The Real Estate Business - Page 6</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="page-container">
        <!-- Page Header with Chapter Title -->
        <header class="page-header">
            <h1 class="chapter-title">
                <span class="chapter-number">1</span>
                <span class="chapter-title-text">The Real Estate Business</span>
            </h1>
        </header>

        <!-- Section Navigation Overview -->
        <nav class="section-navigation">
            <span class="nav-item">Real Estate Professions</span>
            <span class="nav-item">Real Estate Brokerage</span>
            <span class="nav-item">Professional Organizations</span>
            <span class="nav-item">Regulation and Licensing</span>
        </nav>

        <!-- Main Content -->
        <main class="page-content">
            <!-- Section 1: Real Estate Professions -->
            <section class="content-section">
                <h2 class="section-heading">Real Estate Professions</h2>

                <div class="subsection-labels">
                    <h3 class="subsection-label">Real estate activities</h3>
                    <h3 class="subsection-label">Professional specialties</h3>
                    <h3 class="subsection-label">Property type specialization</h3>
                </div>

                <p class="paragraph paragraph-italic">
                    In its broadest sense, the real estate industry is the largest single industry in the American economy.
                    Within it one might include the construction industry, itself often considered our country's largest business.
                    In addition, the real estate industry may be said to include the creation, management, and demolition of every
                    residence and business facility in the nation: offices, warehouses, factories, stores, and special purpose
                    buildings such as hospitals and government facilities.
                </p>

                <p class="paragraph">
                    Real estate professionals are individuals and business organizations whose sole enterprise is performing
                    a real estate-related service or function. A wide range of professions is available to persons wishing to
                    enter the real estate business.
                </p>

                <h4 class="subsection-heading">Real estate activities</h4>
                <p class="paragraph">Real estate professionals perform the following property-related functions:</p>

                <ul class="bullet-list">
                    <li class="bullet-item">creation and improvement</li>
                    <li class="bullet-item">management and maintenance</li>
                    <li class="bullet-item">demolition</li>
                    <li class="bullet-item">investment ownership</li>
                    <li class="bullet-item">regulation</li>
                    <li class="bullet-item">transfer</li>
                </ul>

                <h4 class="subsection-heading">Creation and improvement</h4>
                <p class="paragraph">
                    Creating real properties from raw land involves capital formation, financing, construction contracting,
                    and regulatory approvals. The key parties involved in this aspect of the business are generally the developer,
                    the landowner, and the mortgage lender. Also involved are market analysts, architects, engineers, space planners,
                    interior designers, and construction subcontractors.
                </p>
            </section>
        </main>
    </div>
</body>
</html>
'''

    return html


def main():
    # File paths
    analysis_file = "../analysis/page_6_pattern_analysis.json"
    output_file = "../output/page_6_recreation.html"
    styles_file = "../output/page_6_styles.css"

    print("\n" + "="*60)
    print("GENERATING PAGE 6 RECREATION HTML")
    print("="*60 + "\n")

    # Load analysis
    print("Loading pattern analysis...")
    analysis_data = load_pattern_analysis(analysis_file)

    # Generate HTML
    print("Generating HTML...")
    html = generate_page_html(analysis_data)

    # Save HTML
    with open(output_file, "w") as f:
        f.write(html)
    print(f"✓ Saved: {output_file}")

    print(f"\n✓ Page 6 recreation HTML generated successfully!")
    print(f"✓ CSS file: {styles_file}")
    print(f"\nOpen in browser to view the recreated page.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
