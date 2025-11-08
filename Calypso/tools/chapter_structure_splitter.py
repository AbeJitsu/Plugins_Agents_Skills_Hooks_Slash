#!/usr/bin/env python3
"""
Split extracted PDF content into separate chapter folders based on detected structure.
Reorganizes from single 'chapter_01' folder into 31 folders: chapter_0 through chapter_29, plus chapter_Z.
"""

import json
import os
import sys
from pathlib import Path


# Define chapter boundaries (page numbers from pages.json)
CHAPTER_BOUNDARIES = {
    0: (0, 5, "Front Matter", "Title, Copyright, Table of Contents, Preface"),
    1: (6, 14, "The Real Estate Business", ""),
    2: (15, 27, "Rights in Real Estate", ""),
    3: (28, 37, "Interests and Estates", ""),
    4: (38, 53, "Ownership", ""),
    5: (54, 71, "Encumbrances and Liens", ""),
    6: (72, 88, "Transferring & Recording Title to Real Estate", ""),
    7: (89, 99, "Leasing Essentials", ""),
    8: (100, 118, "Land Use Planning and Control", ""),
    9: (119, 128, "Legal Descriptions", ""),
    10: (129, 140, "Fundamentals of Contract Law", ""),
    11: (141, 155, "National Agency", ""),
    12: (156, 171, "Listing Agreements: An Overview", ""),
    13: (173, 196, "General Brokerage Practices", ""),
    14: (197, 209, "Overview of Conveyance Contracts", ""),
    15: (210, 221, "Real Estate Market Economics", ""),
    16: (222, 247, "Appraising and Estimating Market Value", ""),
    17: (248, 279, "Real Estate Finance", ""),
    18: (280, 295, "Real Estate Investment", ""),
    19: (296, 303, "Real Estate Taxation", ""),
    20: (304, 327, "Professional Practices", ""),
    21: (328, 356, "Closings", ""),
    22: (357, 378, "Risk Management", ""),
    23: (379, 399, "Property Management", ""),
    24: (400, 426, "Real Estate Mathematics", ""),
    25: (427, 440, "The Alabama Regulatory Environment", ""),
    26: (441, 458, "Alabama Licensing Regulation", ""),
    27: (459, 479, "Alabama Brokerage Regulation", ""),
    28: (480, 494, "Alabama Agency", ""),
    29: (495, 515, "Alabama License Law Violations", ""),
    "Z": (516, 592, "Back Matter", "Chapter Tests, Answer Keys, Glossary, Index"),
}


def load_extracted_data():
    """Load the currently extracted chapter_01 data."""
    source_dir = "../chapters/chapter_01"

    pages_file = os.path.join(source_dir, "pages.json")
    if not os.path.exists(pages_file):
        print(f"Error: {pages_file} not found")
        sys.exit(1)

    with open(pages_file) as f:
        pages = json.load(f)

    return pages


def create_chapter_folder(chapter_id, start_page, end_page, title, description, pages):
    """Create a chapter folder and save chapter data."""
    chapters_dir = "../chapters"

    # Create chapter folder
    if isinstance(chapter_id, str):
        folder_name = f"chapter_{chapter_id}"
    else:
        folder_name = f"chapter_{chapter_id:02d}"

    chapter_folder = os.path.join(chapters_dir, folder_name)
    os.makedirs(chapter_folder, exist_ok=True)

    # Extract pages for this chapter
    chapter_pages = []
    chapter_text = []

    for i in range(start_page, end_page + 1):
        if i < len(pages):
            page_data = pages[i].copy()
            chapter_pages.append(page_data)
            chapter_text.append(page_data.get("text", ""))

    # Create metadata
    metadata = {
        "chapter": chapter_id,
        "title": title,
        "description": description,
        "start_page": start_page,
        "end_page": end_page,
        "total_pages": len(chapter_pages),
        "images": [],  # No images extracted yet
    }

    # Save metadata
    metadata_file = os.path.join(chapter_folder, "metadata.json")
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)

    # Save content as text
    content_text = "\n---PAGE_BREAK---\n".join(chapter_text)
    content_file = os.path.join(chapter_folder, "content.txt")
    with open(content_file, "w") as f:
        f.write(content_text)

    # Save pages as JSON
    pages_file = os.path.join(chapter_folder, "pages.json")
    with open(pages_file, "w") as f:
        json.dump(chapter_pages, f, indent=2)

    return chapter_folder, len(chapter_pages)


def main():
    print("Loading extracted PDF data...")
    pages = load_extracted_data()
    print(f"Total pages loaded: {len(pages)}")

    chapters_created = []

    print("\nCreating chapter folders...")
    for chapter_id, (start_page, end_page, title, description) in CHAPTER_BOUNDARIES.items():
        chapter_folder, page_count = create_chapter_folder(
            chapter_id, start_page, end_page, title, description, pages
        )
        chapters_created.append(chapter_id)
        print(f"✓ Chapter {chapter_id}: {title} ({page_count} pages) → {chapter_folder}")

    print(f"\n✓ Successfully created {len(chapters_created)} chapter folders")
    print("\nChapters created:")
    for i, chapter_id in enumerate(chapters_created):
        start, end, title, _ = CHAPTER_BOUNDARIES[chapter_id]
        print(f"  chapter_{chapter_id if isinstance(chapter_id, str) else f'{chapter_id:02d}'}: Pages {start}-{end}")


if __name__ == "__main__":
    main()
