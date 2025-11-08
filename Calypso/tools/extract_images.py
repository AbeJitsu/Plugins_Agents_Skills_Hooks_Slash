#!/usr/bin/env python3
"""
Extract embedded images from PDF pages.
Saves images to organized directory structure with metadata.
"""

import fitz  # PyMuPDF
import json
import os
import sys
from pathlib import Path


def extract_images_from_page(pdf_path, page_index, output_base_dir="../output", mapping_file=None):
    """
    Extract all embedded images from a PDF page.

    Args:
        pdf_path: Path to PDF file
        page_index: 0-based PDF page index (e.g., 16 for book page 17)
        output_base_dir: Base output directory
        mapping_file: Path to page_mapping.json for accurate book page lookup

    Returns:
        List of extracted image metadata dicts
    """
    pdf = fitz.open(pdf_path)
    page = pdf[page_index]

    # Determine chapter based on page index
    # Chapter boundaries: 1: 0-12, 2: 14-26, 3: 27-40, etc.
    if 0 <= page_index <= 12:
        chapter = 1
    elif 14 <= page_index <= 26:
        chapter = 2
    elif 27 <= page_index <= 40:
        chapter = 3
    else:
        chapter = 0

    # Create output directory (following chapter-based structure)
    output_dir = os.path.join(output_base_dir, f"chapter_{chapter:02d}", "images")
    os.makedirs(output_dir, exist_ok=True)

    # Get all images on page
    image_list = page.get_images(full=True)

    extracted_images = []
    # Look up accurate book page from mapping file, fall back to formula
    book_page = None
    if mapping_file and os.path.exists(mapping_file):
        try:
            with open(mapping_file, 'r') as f:
                mapping = json.load(f)
            if str(page_index) in mapping:
                book_page = mapping[str(page_index)]["book_page"]
        except:
            pass

    # Fallback to formula if not in mapping
    if book_page is None:
        book_page = page_index + 1 if page_index >= 6 else None

    if not image_list:
        print(f"No images found on PDF page {page_index}" +
              (f" (book page {book_page})" if book_page else ""))
        pdf.close()
        return extracted_images

    print(f"\nExtracting {len(image_list)} image(s) from PDF page {page_index}" +
          (f" (book page {book_page})" if book_page else ""))
    print(f"Output directory: {output_dir}\n")

    for img_index, img_info in enumerate(image_list, start=1):
        try:
            xref = img_info[0]

            # Extract image data
            base_image = pdf.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            width = base_image["width"]
            height = base_image["height"]

            # Save image
            image_filename = f"page_{page_index:02d}_image_{img_index}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)

            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)

            # Store metadata
            metadata = {
                "file_path": f"images/chapter_{chapter:02d}/{image_filename}",
                "width": width,
                "height": height,
                "image_index": img_index,
                "image_xref": xref
            }

            extracted_images.append(metadata)
            print(f"  ✓ Image {img_index}: {image_filename} ({width}x{height}px)")

        except Exception as e:
            print(f"  ✗ Error extracting image {img_index}: {e}")

    pdf.close()

    # Save metadata
    metadata_file = os.path.join(output_dir, f"page_{page_index:02d}_images.json")
    with open(metadata_file, 'w') as f:
        json.dump({
            "page_index": page_index,
            "book_page": book_page,
            "chapter": chapter,
            "image_count": len(extracted_images),
            "images": extracted_images
        }, f, indent=2)

    print(f"✓ Metadata saved: {metadata_file}")

    return extracted_images


def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract embedded images from a PDF page'
    )
    parser.add_argument(
        '--page',
        type=int,
        required=True,
        help='PDF page index (0-based). Example: 16 for book page 17'
    )
    parser.add_argument(
        '--pdf',
        default='../../PREP-AL 4th Ed 9-26-25.pdf',
        help='Path to PDF file'
    )
    parser.add_argument(
        '--output',
        default='../output',
        help='Base output directory for images'
    )
    parser.add_argument(
        '--mapping',
        default='../analysis/page_mapping.json',
        help='Path to page_mapping.json for accurate book page lookup'
    )

    args = parser.parse_args()

    # Validate page index
    if args.page < 0:
        print("Error: Page index must be >= 0")
        sys.exit(1)

    # Extract images
    try:
        images = extract_images_from_page(args.pdf, args.page, args.output, args.mapping)

        if images:
            print(f"\n{'='*60}")
            print(f"✓ Successfully extracted {len(images)} image(s)")
            print(f"{'='*60}\n")
        else:
            print(f"\n{'='*60}")
            print(f"No images to extract")
            print(f"{'='*60}\n")

    except FileNotFoundError:
        print(f"Error: PDF file not found: {args.pdf}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
