#!/usr/bin/env python3
"""
Calypso Orchestrator - Coordinates PDF-to-HTML conversion pipeline
Manages Python tools (extraction, validation) and prepares inputs for AI skills

NOTE: AI generation skills (Skills 2, 3, 4) and AI validation (Gate 3) are handled by Claude Code
This orchestrator handles:
- Skill 1: PDF extraction (Python)
- Gate 1: Structure validation (Python)
- Gate 2: Semantic validation (Python)
- Skill 5: Quality report generation (Python)

Claude Code (AI) handles:
- Skill 2: ASCII preview generation (AI - visual + text → ASCII layout)
- Skill 3: HTML generation (AI - PNG + JSON + ASCII → HTML)
- Skill 4: Chapter consolidation (AI - merge pages into chapter)
- Gate 3: Visual accuracy check (AI - compare rendered HTML to original PDF)
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CalypsoOrchestrator:
    """Orchestrates Calypso PDF-to-HTML conversion pipeline"""

    def __init__(self, chapter: int, pages_start: int, pages_end: int,
                 pdf_path: str, output_base: str = "output",
                 analysis_base: str = "analysis", tools_dir: str = "tools"):
        """Initialize orchestrator with chapter configuration"""
        self.chapter = chapter
        self.pages_start = pages_start
        self.pages_end = pages_end
        self.pdf_path = pdf_path
        self.output_base = Path(output_base)
        self.analysis_base = Path(analysis_base)
        self.tools_dir = Path(tools_dir)

        # Setup directories
        self.chapter_dir = self.output_base / f"chapter_{chapter:02d}"
        self.page_artifacts_dir = self.chapter_dir / "page_artifacts"
        self.chapter_artifacts_dir = self.chapter_dir / "chapter_artifacts"
        self.analysis_chapter_dir = self.analysis_base / f"chapter_{chapter:02d}"

        self._create_directories()
        self.start_time = datetime.now()

    def _create_directories(self):
        """Create necessary output directories"""
        self.page_artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.chapter_artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.analysis_chapter_dir.mkdir(parents=True, exist_ok=True)

        # Create per-page directories
        for page_idx in range(self.pages_start, self.pages_end + 1):
            page_dir = self.page_artifacts_dir / f"page_{page_idx:02d}"
            page_dir.mkdir(parents=True, exist_ok=True)

    def run(self) -> bool:
        """Run orchestrator workflow"""
        print("\n" + "=" * 80)
        print(f"CALYPSO ORCHESTRATOR - Chapter {self.chapter}")
        print("=" * 80 + "\n")

        try:
            # Step 1: Verify/Extract data
            print("📋 STEP 1: PDF Data Extraction (Skill 1 - Python)")
            print("-" * 80)
            if not self._step_1_extract_data():
                print("❌ Extraction failed\n")
                return False
            print("✅ Extraction complete\n")

            # Step 2: Render pages to PNG
            print("🖼️  STEP 2: Render PDF Pages to PNG")
            print("-" * 80)
            if not self._step_2_render_pages():
                print("❌ Rendering failed\n")
                return False
            print("✅ Pages rendered\n")

            # Step 3: Prepare for AI generation
            print("🤖 STEP 3: Prepare for AI Generation (Skills 2-4)")
            print("-" * 80)
            self._step_3_prepare_for_ai()
            print("✅ Ready for AI generation\n")

            # Step 4: Validate (assuming AI generation is done)
            print("✔️  STEP 4: Validate Generated HTML")
            print("-" * 80)
            if not self._step_4_validate():
                print("⚠️  Validation issues found (see above)\n")
            else:
                print("✅ Validation passed\n")

            # Summary
            self._print_summary()
            return True

        except Exception as e:
            logger.error(f"Orchestrator failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _step_1_extract_data(self) -> bool:
        """STEP 1: Extract PDF data using Python tools"""
        try:
            extraction_file = self.analysis_chapter_dir / "rich_extraction.json"

            # Check if already extracted
            if extraction_file.exists():
                with open(extraction_file) as f:
                    data = json.load(f)
                page_count = data['metadata']['total_pages_extracted']
                logger.info(f"✅ Already extracted: {page_count} pages")
                return True

            # Run extraction
            logger.info(f"Extracting pages {self.pages_start}-{self.pages_end}...")
            result = subprocess.run(
                [sys.executable, str(self.tools_dir / "rich_extractor.py"),
                 "--pdf", self.pdf_path,
                 "--start", str(self.pages_start),
                 "--end", str(self.pages_end),
                 "--output", str(extraction_file)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0 and extraction_file.exists():
                with open(extraction_file) as f:
                    data = json.load(f)
                page_count = data['metadata']['total_pages_extracted']
                logger.info(f"✅ Extracted {page_count} pages to {extraction_file}")
                return True
            else:
                logger.error(f"Extraction failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Step 1 failed: {e}")
            return False

    def _step_2_render_pages(self) -> bool:
        """STEP 2: Render PDF pages to PNG"""
        try:
            import fitz

            logger.info(f"Rendering pages {self.pages_start}-{self.pages_end} to PNG...")
            pdf = fitz.open(self.pdf_path)

            for page_idx in range(self.pages_start, self.pages_end + 1):
                page_dir = self.page_artifacts_dir / f"page_{page_idx:02d}"
                png_path = page_dir / f"02_page_{page_idx:02d}.png"

                if png_path.exists():
                    continue

                page = pdf[page_idx]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                pix.save(str(png_path))

            pdf.close()
            logger.info(f"✅ Rendered {self.pages_end - self.pages_start + 1} pages")
            return True

        except ImportError:
            logger.error("PyMuPDF not installed")
            return False
        except Exception as e:
            logger.error(f"Step 2 failed: {e}")
            return False

    def _step_3_prepare_for_ai(self):
        """STEP 3: Prepare inputs for AI generation"""
        print("\n⚠️  NEXT STEPS - AI GENERATION (requires Claude Code)")
        print("-" * 80)
        print("\nThe following steps require AI generation:")
        print("\n✋ SKILL 2: ascii-preview-generate (AI)")
        print("   Input files:")
        print(f"     - Rich extraction: {self.analysis_chapter_dir}/rich_extraction.json")
        print(f"     - PDF images: {self.page_artifacts_dir}/page_XX/02_page_XX.png")
        print("   Action: For each page, use Claude to generate ASCII text preview")
        print("   Output: Save to page_XX/03_page_XX_ascii.txt")

        print("\n✋ SKILL 3: ai-html-generate (AI)")
        print("   Input files (per page):")
        print("     - PDF image: 02_page_XX.png")
        print("     - Rich extraction: rich_extraction.json")
        print("     - ASCII preview: 03_page_XX_ascii.txt")
        print("   Action: Use Claude to generate semantic HTML from 3 inputs")
        print("   Output: Save to page_XX/04_page_XX.html")

        print("\n✋ SKILL 4: ai-chapter-consolidate (AI)")
        print("   Input: All page_XX.html files (pages %d-%d)" % (self.pages_start, self.pages_end))
        print("   Action: Use Claude to merge pages into single chapter document")
        print("   Output: Save to chapter_artifacts/chapter_%02d.html" % self.chapter)

        print("\n" + "-" * 80)
        print("After AI generation completes:")
        print(f"  1. Run validation: python3 tools/orchestrator.py {self.chapter} {self.pages_start} {self.pages_end} --validate-only")
        print(f"  2. Run AI visual accuracy check (Gate 3)")
        print(f"     Input: Original PDF pages + Rendered HTML")
        print(f"     Output: Save to chapter_artifacts/ai_visual_accuracy.json")

    def _step_4_validate(self) -> bool:
        """STEP 4: Validate generated HTML (Gates 1-2)

        Note: This runs Python validation gates:
        - Gate 1: HTML structure validation (DOCTYPE, tags, closure)
        - Gate 2: HTML semantic validation (CSS classes, hierarchy)

        Gate 3 (AI visual accuracy check) must be run separately by Claude Code
        """
        try:
            chapter_html = self.chapter_artifacts_dir / f"chapter_{self.chapter:02d}.html"

            if not chapter_html.exists():
                logger.warning(f"Chapter HTML not found: {chapter_html}")
                logger.info("Run AI generation first (Step 3)")
                return False

            logger.info(f"Running structural and semantic validation (Gates 1-2)...")
            print("\n📋 GATE 1: HTML Structure Validation")
            print("-" * 80)

            # Run structure validation
            result = subprocess.run(
                [sys.executable, str(self.tools_dir / "validate_html.py"), str(chapter_html)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("✅ Structural & semantic validation PASSED")
                print("✅ Gates 1-2 validation passed\n")
                print("⚠️  GATE 3: AI Visual Accuracy Check")
                print("-" * 80)
                print("Gate 3 requires AI comparison of rendered HTML to original PDF")
                print(f"Input: {chapter_html}")
                print(f"Input: Original PDF pages (from {self.page_artifacts_dir}/page_XX/02_page_XX.png)")
                print(f"Output: Save to chapter_artifacts/ai_visual_accuracy.json")
                print("\nAI must score visual accuracy on:")
                print("  • Layout match (40% weight)")
                print("  • Visual hierarchy (30% weight)")
                print("  • Content positioning (20% weight)")
                print("  • Typography & styling (10% weight)")
                print("\nPass threshold: ≥85% similarity")
                return True
            else:
                logger.warning("⚠️  Validation issues found (Gates 1-2)")
                print(result.stdout)
                return False

        except Exception as e:
            logger.error(f"Step 4 failed: {e}")
            return False

    def _print_summary(self):
        """Print execution summary"""
        elapsed = datetime.now() - self.start_time

        print("\n" + "=" * 80)
        print("ORCHESTRATOR SUMMARY")
        print("=" * 80)
        print(f"Chapter: {self.chapter}")
        print(f"Pages: {self.pages_start}-{self.pages_end}")
        print(f"Time: {elapsed.total_seconds():.1f}s")
        print(f"Output: {self.chapter_dir}")
        print("\n📁 Artifact Locations:")
        print(f"   Per-page: {self.page_artifacts_dir}/page_XX/")
        print(f"   Chapter: {self.chapter_artifacts_dir}/chapter_{self.chapter:02d}.html")
        print("\n🔄 Pipeline Status:")
        print("   ✅ Step 1: PDF extraction (Python)")
        print("   ✅ Step 2: Page rendering to PNG (Python)")
        print("   ⏳ Step 3: AI generation (Skills 2-4, Claude Code)")
        print("   ⏳ Gate 1-2: Validation (Python)")
        print("   ⏳ Gate 3: AI visual accuracy check (Claude Code)")
        print("=" * 80 + "\n")


def main():
    """Main entry point"""
    chapter = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    pages_start = int(sys.argv[2]) if len(sys.argv) > 2 else 15
    pages_end = int(sys.argv[3]) if len(sys.argv) > 3 else 28
    validate_only = "--validate-only" in sys.argv

    orchestrator = CalypsoOrchestrator(
        chapter=chapter,
        pages_start=pages_start,
        pages_end=pages_end,
        pdf_path="PREP-AL 4th Ed 9-26-25.pdf"
    )

    if validate_only:
        success = orchestrator._step_4_validate()
    else:
        success = orchestrator.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
