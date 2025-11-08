#!/usr/bin/env python3
"""
Generate semantic HTML for Page 7 (Chapter 1, Second Page)
Uses extracted pattern analysis to recreate page with clean semantic HTML structure.
Uses unified global CSS stylesheet for consistent styling across all chapters.
"""

import json
import os
import sys
from html import escape


def load_pattern_analysis(analysis_file):
    """Load the page 7 pattern analysis."""
    if not os.path.exists(analysis_file):
        print(f"Error: {analysis_file} not found")
        sys.exit(1)

    with open(analysis_file) as f:
        return json.load(f)


def generate_page_html(analysis_data):
    """Generate clean semantic HTML page from pattern analysis (no absolute positioning)."""

    # Build HTML with proper semantic structure and reading order
    # Page 7 continues the real estate professions section from page 6
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chapter 1: The Real Estate Business - Page 7</title>
    <link rel="stylesheet" href="styles/main.css">
</head>
<body>
    <div class="page-container">
        <!-- Main Content -->
        <main class="page-content">
            <!-- Section 1: Real Estate Professions (continued) -->
            <section class="content-section">
                <h4 class="subsection-heading">Experts who support the development</h4>
                <p class="paragraph">
                    Experts who manage the legal aspects of the development project include real estate attorneys, title companies, surveyors, property insurance companies, and government regulatory officials. The brokerage community, with the assistance of professional appraisers, usually handles the ownership and leasing transactions that occur over the many phases of development.
                </p>

                <h4 class="subsection-heading">Management and maintenance</h4>
                <p class="paragraph">
                    All real estate, whether raw land or improved property, must be managed and maintained. The two principal types of managers are property managers and asset managers. Property managers and their staff oversee specific properties on behalf of the owners, making sure the condition of the property and its financial performance meet specific standards.
                </p>

                <p class="paragraph">
                    Asset managers oversee groups of properties, or portfolios. Their role is to achieve the investment objectives of the owners as opposed to managing day-to-day operations.
                </p>

                <p class="paragraph">
                    Maintenance personnel include engineers, systems technicians, janitorial staff, and other employees needed to maintain the property's condition.
                </p>

                <h4 class="subsection-heading">Demolition</h4>
                <p class="paragraph">
                    Demolition experts in conjunction with excavation and debris removal experts serve to remove properties that are no longer economically viable from the market.
                </p>

                <h4 class="subsection-heading">Investment ownership</h4>
                <p class="paragraph">
                    A specialized niche in the real estate business is the real estate investor who risks capital in order to buy, hold, and sell real properties. In contrast to property owners whose primary interest is in some other business, the real estate investor focuses on identifying and exploiting real estate investment opportunities for profit. The real estate investor provides capital and liquidity to the real estate market.
                </p>

                <h4 class="subsection-heading">Regulation</h4>
                <p class="paragraph">
                    All real estate is to some degree regulated by government. The principal areas of regulation are usage, taxation, and housing administration. Professional regulatory functions include public planners, zoning administrators, building inspectors, assessors, and administrators of specific federal statutes such as Federal Fair Housing Laws.
                </p>

                <h4 class="subsection-heading">Transfer</h4>
                <p class="paragraph">
                    Rights and interests in real estate can be bought, sold, assigned, leased, exchanged, inherited, or otherwise transferred from one owner to another. Real estate brokers and the brokers' salespeople are generally centrally involved in such transfers. Other professional participants are mortgage brokers, mortgage bankers, appraisers, insurers, and title companies.
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
    analysis_file = "../analysis/page_7_pattern_analysis.json"
    output_file = "../output/page_7_recreation.html"

    print("\n" + "="*60)
    print("GENERATING PAGE 7 RECREATION HTML")
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

    print(f"\n✓ Page 7 recreation HTML generated successfully!")
    print(f"✓ CSS file: styles/main.css")
    print(f"\nOpen in browser to view the recreated page.")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
