#!/usr/bin/env python3
"""
Extract first pages of PDF for TOC analysis using multiple libraries.
Saves outputs from pdfplumber, PyMuPDF, and OCR for comparison.
"""

import json
import os
import sys
from pathlib import Path

try:
    import pdfplumber
    import fitz  # PyMuPDF
    from pdf2image import convert_from_path
    from PIL import Image
    import pytesseract
except ImportError as e:
    print(f"Error: Missing required library. Install with: pip install -r requirements.txt")
    print(f"Missing: {e}")
    sys.exit(1)


def extract_with_pdfplumber(pdf_path, page_nums):
    """Extract text and layout data using pdfplumber."""
    results = {}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in page_nums:
                if page_num >= len(pdf.pages):
                    continue

                page = pdf.pages[page_num]
                results[page_num] = {
                    "text": page.extract_text(),
                    "layout": {
                        "width": page.width,
                        "height": page.height,
                        "tables": len(page.find_tables()) if hasattr(page, 'find_tables') else 0,
                    },
                    "lines": [
                        {
                            "x0": obj.get("x0"),
                            "y0": obj.get("y0"),
                            "x1": obj.get("x1"),
                            "y1": obj.get("y1"),
                            "type": obj.get("object_type"),
                        }
                        for obj in page.objects.get("line", [])[:10]  # First 10 lines
                    ] if page.objects else []
                }
    except Exception as e:
        print(f"Error in pdfplumber extraction: {e}")

    return results


def extract_with_fitz(pdf_path, page_nums):
    """Extract fonts, images, and metadata using PyMuPDF."""
    results = {}
    try:
        pdf = fitz.open(pdf_path)

        for page_num in page_nums:
            if page_num >= len(pdf):
                continue

            page = pdf[page_num]

            # Get fonts
            fonts = {}
            text_dict = page.get_text("dict")
            if "blocks" in text_dict:
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                font_name = span.get("font", "unknown")
                                size = span.get("size", 0)
                                if font_name not in fonts:
                                    fonts[font_name] = {"size": size, "count": 0}
                                fonts[font_name]["count"] += 1

            # Get images count
            images = page.get_images()

            results[page_num] = {
                "metadata": {
                    "rotation": page.rotation,
                    "width": page.rect.width,
                    "height": page.rect.height,
                },
                "fonts": fonts,
                "image_count": len(images),
                "text_preview": page.get_text()[:200],
            }

        pdf.close()
    except Exception as e:
        print(f"Error in PyMuPDF extraction: {e}")

    return results


def extract_with_ocr(pdf_path, page_nums):
    """Extract text using OCR as fallback."""
    results = {}
    try:
        images = convert_from_path(pdf_path, first_page=page_nums[0]+1, last_page=page_nums[-1]+1 if page_nums else 1)

        for idx, image in enumerate(images):
            page_num = page_nums[idx] if idx < len(page_nums) else page_nums[0] + idx
            text = pytesseract.image_to_string(image)
            results[page_num] = {
                "ocr_text": text[:500],  # First 500 chars
                "image_size": image.size,
            }
    except Exception as e:
        print(f"Error in OCR extraction: {e}")

    return results


def save_page_images(pdf_path, page_nums, output_dir):
    """Save page images for visual reference."""
    try:
        images = convert_from_path(pdf_path, first_page=page_nums[0]+1, last_page=page_nums[-1]+1 if page_nums else 1)

        for idx, image in enumerate(images):
            page_num = page_nums[idx] if idx < len(page_nums) else page_nums[0] + idx
            image_path = os.path.join(output_dir, f"page_{page_num:03d}.png")
            image.save(image_path, "PNG")
            print(f"Saved: {image_path}")
    except Exception as e:
        print(f"Error saving page images: {e}")


def main():
    # Get PDF path from parent directory
    pdf_path = "../../PREP-AL 4th Ed 9-26-25.pdf"
    output_dir = "../analysis"

    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        sys.exit(1)

    print(f"Analyzing PDF: {pdf_path}")
    print(f"Output directory: {output_dir}")

    # Extract first 20 pages (0-19)
    page_nums = list(range(20))

    print("\n1. Extracting with pdfplumber...")
    pdfplumber_data = extract_with_pdfplumber(pdf_path, page_nums)
    with open(os.path.join(output_dir, "pdfplumber_output.json"), "w") as f:
        json.dump(pdfplumber_data, f, indent=2, default=str)
    print(f"Saved: pdfplumber_output.json")

    print("\n2. Extracting with PyMuPDF...")
    fitz_data = extract_with_fitz(pdf_path, page_nums)
    with open(os.path.join(output_dir, "fitz_output.json"), "w") as f:
        json.dump(fitz_data, f, indent=2, default=str)
    print(f"Saved: fitz_output.json")

    print("\n3. Saving page images...")
    save_page_images(pdf_path, page_nums, output_dir)

    print("\n4. Extracting with OCR (this may take a while)...")
    ocr_data = extract_with_ocr(pdf_path, page_nums)
    with open(os.path.join(output_dir, "ocr_output.json"), "w") as f:
        json.dump(ocr_data, f, indent=2, default=str)
    print(f"Saved: ocr_output.json")

    print("\nAnalysis complete! Check the analysis/ folder for results.")


if __name__ == "__main__":
    main()
