#!/usr/bin/env python3
"""
Compare PDF text extraction across multiple libraries.

Purpose: Determine if PyMuPDF extraction is complete or if alternative
libraries capture more content (e.g., words marked as "extra" in HTML validation).

Libraries tested:
1. PyMuPDF (fitz) - current method using get_text("dict")
2. pdfplumber - alternative with direct text access
3. pypdfium2 - modern alternative (if available)
4. pdfminer.six - thorough extraction (if available)

Usage:
    python3 compare_extractors.py <pdf_path> <page_num> [--target-words word1 word2 ...]

Example:
    python3 compare_extractors.py "PREP-AL 4th Ed 9-26-25.pdf" 15 --target-words "also" "includes" "heterogeneity"
"""

import sys
import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Tuple

# Try to import all extraction libraries
libraries_available = {}

try:
    import fitz  # PyMuPDF
    libraries_available['PyMuPDF'] = True
except ImportError:
    libraries_available['PyMuPDF'] = False
    print("⚠️  PyMuPDF not installed")

try:
    import pdfplumber
    libraries_available['pdfplumber'] = True
except ImportError:
    libraries_available['pdfplumber'] = False
    print("⚠️  pdfplumber not installed")

try:
    import pypdfium2
    libraries_available['pypdfium2'] = True
except ImportError:
    libraries_available['pypdfium2'] = False
    print("⚠️  pypdfium2 not installed (optional)")

try:
    from pdfminer.high_level import extract_text
    libraries_available['pdfminer.six'] = True
except ImportError:
    libraries_available['pdfminer.six'] = False
    print("⚠️  pdfminer.six not installed (optional)")


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('\"', '\"').replace('\"', '\"').replace(''', "'").replace(''', "'")
    return text.strip()


def extract_with_pymupdf(pdf_path: str, page_num: int) -> Tuple[str, int]:
    """Extract text using PyMuPDF with get_text('dict')."""
    if not libraries_available['PyMuPDF']:
        return "", 0

    pdf = fitz.open(pdf_path)
    page = pdf[page_num]
    text_dict = page.get_text("dict")

    text_chunks = []
    for block in text_dict.get('blocks', []):
        if block['type'] == 0:  # Text block
            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    text = span.get('text', '').strip()
                    if text:
                        text_chunks.append(text)

    full_text = ' '.join(text_chunks)
    word_count = len(full_text.split())
    pdf.close()

    return full_text, word_count


def extract_with_pdfplumber(pdf_path: str, page_num: int) -> Tuple[str, int]:
    """Extract text using pdfplumber."""
    if not libraries_available['pdfplumber']:
        return "", 0

    pdf = pdfplumber.open(pdf_path)
    page = pdf.pages[page_num]
    text = page.extract_text()
    pdf.close()

    word_count = len(text.split()) if text else 0
    return text or "", word_count


def extract_with_pypdfium2(pdf_path: str, page_num: int) -> Tuple[str, int]:
    """Extract text using pypdfium2."""
    if not libraries_available['pypdfium2']:
        return "", 0

    try:
        pdf = pypdfium2.open(pdf_path)
        page = pdf[page_num]
        text_page = page.get_textpage()
        text = text_page.get_text()

        word_count = len(text.split()) if text else 0
        return text, word_count
    except Exception as e:
        return "", 0


def extract_with_pdfminer(pdf_path: str, page_num: int) -> Tuple[str, int]:
    """Extract text using pdfminer.six - extracts entire PDF, we'll parse by page."""
    if not libraries_available['pdfminer.six']:
        return "", 0

    try:
        from pdfminer.converter import PDFPageInterpreter, PDFResourceManager, PDFPageAggregator
        from pdfminer.layout import LAParams, LTTextBox
        from pdfminer.pdfpage import PDFPage

        text_chunks = []
        with open(pdf_path, 'rb') as fp:
            rsrcmgr = PDFResourceManager()
            laparams = LAParams()
            device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)

            current_page = 0
            for page in PDFPage.get_pages(fp):
                if current_page == page_num:
                    interpreter.process_page(page)
                    layout = device.get_result()

                    for element in layout:
                        if isinstance(element, LTTextBox):
                            text = element.get_text().strip()
                            if text:
                                text_chunks.append(text)
                    break
                current_page += 1

            device.close()

        full_text = ' '.join(text_chunks)
        word_count = len(full_text.split())
        return full_text, word_count
    except Exception as e:
        print(f"Error with pdfminer: {e}")
        return "", 0


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 compare_extractors.py <pdf_path> <page_num> [--target-words word1 word2 ...]")
        print("Example: python3 compare_extractors.py 'PREP-AL 4th Ed 9-26-25.pdf' 15 --target-words 'also' 'includes'")
        sys.exit(1)

    pdf_path = sys.argv[1]
    try:
        page_num = int(sys.argv[2])
    except ValueError:
        print(f"Error: page_num must be an integer, got '{sys.argv[2]}'")
        sys.exit(1)

    # Parse target words if provided
    target_words = set()
    if '--target-words' in sys.argv:
        idx = sys.argv.index('--target-words')
        target_words = set(word.lower() for word in sys.argv[idx+1:])

    # Verify PDF exists
    if not Path(pdf_path).exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)

    print("=" * 100)
    print(f"PDF TEXT EXTRACTION COMPARISON")
    print("=" * 100)
    print(f"\nPDF File: {pdf_path}")
    print(f"Page Number: {page_num} (0-based PDF index)")
    if target_words:
        print(f"Target words to search: {', '.join(sorted(target_words))}")

    # Extract with each method
    results = {}

    print("\n" + "=" * 100)
    print("EXTRACTION RESULTS")
    print("=" * 100)

    # PyMuPDF
    if libraries_available['PyMuPDF']:
        print("\n1. PyMuPDF (fitz) - Current method using get_text('dict')...")
        text, word_count = extract_with_pymupdf(pdf_path, page_num)
        results['PyMuPDF'] = {'text': text, 'word_count': word_count, 'available': True}
        print(f"   ✓ Extracted {word_count} words")
        if target_words:
            found = set(w.lower() for w in text.lower().split() if w.lower() in target_words)
            print(f"   ✓ Found {len(found)}/{len(target_words)} target words: {', '.join(sorted(found)) if found else 'none'}")
    else:
        print("\n1. PyMuPDF (fitz) - NOT INSTALLED")
        results['PyMuPDF'] = {'text': '', 'word_count': 0, 'available': False}

    # pdfplumber
    if libraries_available['pdfplumber']:
        print("\n2. pdfplumber - Direct text extraction...")
        text, word_count = extract_with_pdfplumber(pdf_path, page_num)
        results['pdfplumber'] = {'text': text, 'word_count': word_count, 'available': True}
        print(f"   ✓ Extracted {word_count} words")
        if target_words:
            found = set(w.lower() for w in text.lower().split() if w.lower() in target_words)
            print(f"   ✓ Found {len(found)}/{len(target_words)} target words: {', '.join(sorted(found)) if found else 'none'}")
    else:
        print("\n2. pdfplumber - NOT INSTALLED")
        results['pdfplumber'] = {'text': '', 'word_count': 0, 'available': False}

    # pypdfium2
    if libraries_available['pypdfium2']:
        print("\n3. pypdfium2 - Modern PDF library...")
        text, word_count = extract_with_pypdfium2(pdf_path, page_num)
        results['pypdfium2'] = {'text': text, 'word_count': word_count, 'available': True}
        print(f"   ✓ Extracted {word_count} words")
        if target_words:
            found = set(w.lower() for w in text.lower().split() if w.lower() in target_words)
            print(f"   ✓ Found {len(found)}/{len(target_words)} target words: {', '.join(sorted(found)) if found else 'none'}")
    else:
        print("\n3. pypdfium2 - NOT INSTALLED (install with: pip3 install pypdfium2)")
        results['pypdfium2'] = {'text': '', 'word_count': 0, 'available': False}

    # pdfminer.six
    if libraries_available['pdfminer.six']:
        print("\n4. pdfminer.six - Thorough extraction...")
        text, word_count = extract_with_pdfminer(pdf_path, page_num)
        results['pdfminer.six'] = {'text': text, 'word_count': word_count, 'available': True}
        print(f"   ✓ Extracted {word_count} words")
        if target_words:
            found = set(w.lower() for w in text.lower().split() if w.lower() in target_words)
            print(f"   ✓ Found {len(found)}/{len(target_words)} target words: {', '.join(sorted(found)) if found else 'none'}")
    else:
        print("\n4. pdfminer.six - NOT INSTALLED (install with: pip3 install pdfminer.six)")
        results['pdfminer.six'] = {'text': '', 'word_count': 0, 'available': False}

    # Comparison Analysis
    print("\n" + "=" * 100)
    print("COMPARISON ANALYSIS")
    print("=" * 100)

    available_results = {k: v for k, v in results.items() if v['available']}

    if not available_results:
        print("\n❌ No extraction libraries available!")
        sys.exit(1)

    # Word count comparison
    print("\nWord Count by Library:")
    for lib, data in sorted(available_results.items(), key=lambda x: x[1]['word_count'], reverse=True):
        print(f"  {lib:20s}: {data['word_count']:5d} words")

    max_words = max(d['word_count'] for d in available_results.values())
    min_words = min(d['word_count'] for d in available_results.values())
    word_diff = max_words - min_words

    print(f"\n  Difference (max-min): {word_diff} words")
    if word_diff > 0:
        print(f"  ⚠️  Libraries extracted different amounts of text!")
    else:
        print(f"  ✓ All libraries extracted same word count")

    # Detailed word difference analysis for target words
    if target_words:
        print("\n" + "-" * 100)
        print("TARGET WORD ANALYSIS")
        print("-" * 100)

        word_found_in = defaultdict(list)
        for lib, data in available_results.items():
            text_words = set(w.lower() for w in data['text'].lower().split())
            for target in target_words:
                if target in text_words:
                    word_found_in[target].append(lib)

        print("\nTarget word presence:")
        for word in sorted(target_words):
            libs = word_found_in.get(word, [])
            status = "✓ FOUND" if libs else "✗ NOT FOUND"
            lib_list = ", ".join(libs) if libs else "none"
            print(f"  '{word}': {status:12s} in {lib_list}")

        # Check if any library found words that PyMuPDF missed
        if libraries_available['PyMuPDF'] and available_results.get('PyMuPDF'):
            pymupdf_words = set(w.lower() for w in results['PyMuPDF']['text'].lower().split())
            print("\n" + "-" * 100)
            print("WORDS FOUND BY OTHER LIBRARIES BUT NOT PYMUPDF")
            print("-" * 100)

            found_elsewhere = defaultdict(set)
            for lib, data in available_results.items():
                if lib != 'PyMuPDF':
                    other_words = set(w.lower() for w in data['text'].lower().split())
                    missing_in_pymupdf = other_words - pymupdf_words

                    # Filter to target words or interesting additions
                    if target_words:
                        missing_in_pymupdf = missing_in_pymupdf & target_words

                    if missing_in_pymupdf:
                        found_elsewhere[lib] = missing_in_pymupdf

            if found_elsewhere:
                print("\n⚠️  Alternative libraries captured text that PyMuPDF missed:\n")
                for lib, words in found_elsewhere.items():
                    print(f"  {lib}: {', '.join(sorted(words))}")
                print("\n⚠️  This suggests PyMuPDF extraction may be incomplete!")
            else:
                print("\n✓ No additional target words found by other libraries")

    # Show sample text from PyMuPDF
    if results['PyMuPDF']['available']:
        print("\n" + "-" * 100)
        print("PYMUPDF EXTRACTION SAMPLE (first 300 chars)")
        print("-" * 100)
        sample = results['PyMuPDF']['text'][:300]
        print(f"\n{sample}...\n")

    print("=" * 100)


if __name__ == '__main__':
    main()
