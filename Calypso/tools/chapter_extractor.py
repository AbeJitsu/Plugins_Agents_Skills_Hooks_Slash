#!/usr/bin/env python3
"""
Extract chapters from PDF based on detected TOC patterns.
Saves chapter data organized in chapter folders.
"""

import json
import os
import sys

try:
    import pdfplumber
    import fitz  # PyMuPDF
except ImportError:
    print("Error: Missing required libraries. Install with: pip install -r requirements.txt")
    sys.exit(1)


def extract_chapter_content(pdf_path, start_page, end_page):
    """Extract content from a range of pages."""
    chapter_data = {
        "pages": [],
        "images": [],
        "text": "",
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in range(start_page, end_page + 1):
                if page_num >= len(pdf.pages):
                    break

                page = pdf.pages[page_num]
                page_data = {
                    "page_number": page_num,
                    "text": page.extract_text(),
                    "width": page.width,
                    "height": page.height,
                }
                chapter_data["pages"].append(page_data)
                chapter_data["text"] += page.extract_text() + "\n---PAGE_BREAK---\n"

    except Exception as e:
        print(f"Error extracting with pdfplumber: {e}")

    # Extract images with PyMuPDF
    try:
        pdf = fitz.open(pdf_path)
        image_counter = 0

        for page_num in range(start_page, end_page + 1):
            if page_num >= len(pdf):
                break

            page = pdf[page_num]
            image_list = page.get_images()

            for img_index in image_list:
                xref = img_index
                pix = fitz.Pixmap(pdf, xref)

                if pix.n - pix.alpha < 4:  # GRAY or RGB
                    pix_rgb = pix
                else:  # CMYK
                    pix_rgb = fitz.Pixmap(fitz.csRGB, pix)

                image_filename = f"image_{page_num}_{image_counter}.png"
                chapter_data["images"].append(image_filename)
                image_counter += 1

        pdf.close()
    except Exception as e:
        print(f"Error extracting images: {e}")

    return chapter_data


def load_chapter_map(analysis_dir):
    """Load the chapter map from TOC analysis."""
    chapter_map_file = os.path.join(analysis_dir, "chapter_map.json")

    if not os.path.exists(chapter_map_file):
        print(f"Warning: chapter_map.json not found. Creating default single chapter.")
        return {
            "chapters": [
                {"chapter": 1, "title": "Full Document", "start_page": 0, "end_page": None}
            ]
        }

    with open(chapter_map_file) as f:
        return json.load(f)


def main():
    pdf_path = "../../PREP-AL 4th Ed 9-26-25.pdf"
    analysis_dir = "../analysis"
    chapters_dir = "../chapters"

    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)

    # Load chapter map
    print("Loading chapter map...")
    chapter_map = load_chapter_map(analysis_dir)

    # For now, extract all pages as one "full document" chapter
    # This will be refined once we have proper TOC analysis
    print(f"Extracting chapters...")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

        print(f"PDF has {total_pages} pages")

        # Create a simple chapter structure for now
        # In production, this would use the chapter map
        chapter_start = 0
        chapter_end = total_pages - 1

        chapter_folder = os.path.join(chapters_dir, "chapter_01")
        os.makedirs(chapter_folder, exist_ok=True)

        print(f"Extracting Chapter 1 (pages {chapter_start}-{chapter_end})...")
        chapter_content = extract_chapter_content(pdf_path, chapter_start, chapter_end)

        # Save chapter data
        chapter_meta_file = os.path.join(chapter_folder, "metadata.json")
        with open(chapter_meta_file, "w") as f:
            json.dump(
                {
                    "chapter": 1,
                    "title": "Full Document",
                    "start_page": chapter_start,
                    "end_page": chapter_end,
                    "total_pages": len(chapter_content["pages"]),
                    "images": chapter_content["images"],
                },
                f,
                indent=2,
            )

        chapter_text_file = os.path.join(chapter_folder, "content.txt")
        with open(chapter_text_file, "w") as f:
            f.write(chapter_content["text"])

        chapter_json_file = os.path.join(chapter_folder, "pages.json")
        with open(chapter_json_file, "w") as f:
            json.dump(chapter_content["pages"], f, indent=2)

        print(f"Chapter 1 saved to: {chapter_folder}")
        print(f"  - metadata.json")
        print(f"  - content.txt")
        print(f"  - pages.json")
        print(f"  - {len(chapter_content['images'])} images")

    except Exception as e:
        print(f"Error during extraction: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
