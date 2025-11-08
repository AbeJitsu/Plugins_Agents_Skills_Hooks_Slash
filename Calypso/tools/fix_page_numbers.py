#!/usr/bin/env python3
"""
Fix page numbers across extracted images and metadata.
Adjusts all page indices by 1 to correct off-by-one errors.
"""

import json
import os
import shutil
from pathlib import Path


def fix_page_mapping(mapping_file, offset=1):
    """
    Adjust page numbers in mapping file by offset.

    Args:
        mapping_file: Path to page_mapping.json
        offset: Amount to adjust page numbers (default: 1)
    """
    print(f"\nFixing page mapping: {mapping_file}")
    print(f"Adjusting by offset: {offset}\n")

    with open(mapping_file, 'r') as f:
        mapping = json.load(f)

    new_mapping = {}
    for pdf_idx_str, data in mapping.items():
        pdf_idx = int(pdf_idx_str)
        new_pdf_idx = pdf_idx + offset

        new_mapping[str(new_pdf_idx)] = {
            "book_page": data["book_page"] + offset,
            "chapter": data["chapter"]
        }

        print(f"  PDF Index {pdf_idx} → {new_pdf_idx} | Book Page {data['book_page']} → {data['book_page'] + offset}")

    # Save updated mapping
    with open(mapping_file, 'w') as f:
        json.dump(new_mapping, f, indent=2)

    print(f"\n✓ Updated: {mapping_file}")
    return new_mapping


def fix_image_files(images_dir, offset=1):
    """
    Rename image files to reflect corrected page indices.

    Args:
        images_dir: Chapter images directory (e.g., output/chapter_XX/images)
        offset: Amount to adjust page numbers
    """
    print(f"\nFixing image files in: {images_dir}")
    print(f"Adjusting by offset: {offset}\n")

    images_path = Path(images_dir)
    if not images_path.exists():
        print(f"  ✗ Directory not found: {images_dir}")
        return

    for chapter_dir in sorted(images_path.glob("chapter_*")):
        print(f"\n  Processing: {chapter_dir.name}")

        for image_file in sorted(chapter_dir.glob("page_*_image_*.png")):
            # Extract page number from filename: page_17_image_1.png
            parts = image_file.stem.split("_")
            old_page_idx = int(parts[1])
            new_page_idx = old_page_idx + offset
            image_num = parts[3]

            # Create new filename
            new_name = f"page_{new_page_idx:02d}_image_{image_num}.png"
            new_path = chapter_dir / new_name

            # Rename file
            shutil.move(str(image_file), str(new_path))
            print(f"    ✓ Renamed: {image_file.name} → {new_name}")

        # Fix metadata JSON files
        for metadata_file in sorted(chapter_dir.glob("page_*_images.json")):
            parts = metadata_file.stem.split("_")
            old_page_idx = int(parts[1])
            new_page_idx = old_page_idx + offset

            # Read metadata
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            # Update page index
            metadata["page_index"] = new_page_idx
            metadata["book_page"] = metadata["book_page"] + offset

            # Update image file paths
            for img in metadata["images"]:
                old_path = img["file_path"]
                # Update page number in path: images/chapter_02/page_17_image_1.png
                new_path = old_path.replace(f"page_{old_page_idx:02d}_", f"page_{new_page_idx:02d}_")
                img["file_path"] = new_path

            # Write updated metadata
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Rename metadata file
            new_metadata_name = f"page_{new_page_idx:02d}_images.json"
            new_metadata_path = chapter_dir / new_metadata_name
            shutil.move(str(metadata_file), str(new_metadata_path))

            print(f"    ✓ Updated metadata: {metadata_file.name} → {new_metadata_name}")


def main():
    """Fix page numbers in both mapping and images."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description='Fix page numbers across mapping and extracted images'
    )
    parser.add_argument(
        '--offset',
        type=int,
        default=1,
        help='Amount to adjust page numbers (default: 1)'
    )
    parser.add_argument(
        '--mapping',
        default='../analysis/page_mapping.json',
        help='Path to page_mapping.json'
    )
    parser.add_argument(
        '--images',
        default='../output/chapter_02/images',
        help='Chapter images directory (e.g., ../output/chapter_XX/images)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("FIXING PAGE NUMBERS")
    print("=" * 60)

    try:
        # Fix mapping file
        if os.path.exists(args.mapping):
            fix_page_mapping(args.mapping, args.offset)
        else:
            print(f"✗ Mapping file not found: {args.mapping}")

        # Fix image files
        if os.path.exists(args.images):
            fix_image_files(args.images, args.offset)
        else:
            print(f"✗ Images directory not found: {args.images}")

        print("\n" + "=" * 60)
        print("✓ PAGE NUMBER CORRECTION COMPLETE")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
