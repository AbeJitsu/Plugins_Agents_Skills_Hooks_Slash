# CLAUDE.md: Calypso Project Infrastructure & Process

## Core Principles
- **Follow the process. No shortcuts.** - Every chapter must complete all steps: extract → render → ASCII → HTML → consolidate → validate
- **Use existing agents and skills.** - Don't duplicate functionality; leverage what's built
- **Data is our source of truth.** - Reference extraction data, ASCII previews, and progress.md
- **No auto-commits.** - Always explain what was done in an inviting, focused, considerate, and supportive manner

---

## Directory Structure & Key Resources

### Source Data
```
Calypso/analysis/
├── chapter_01/rich_extraction.json    # PDF text extraction, fonts, styling
├── chapter_02/rich_extraction.json    # VALIDATED: pages 15-27
├── chapter_03/rich_extraction.json    # VALIDATED: pages 28-37
└── chapter_0X/rich_extraction.json    # (remaining chapters)

Key fields in extraction JSON:
- metadata.page_range: Expected chapter page boundaries
- pages.{page}.page_number: PDF page index
- pages.{page}.book_page: Book page number (shown in footer)
- pages.{page}.text_spans: All text with font, size, position data
```

### Generated Assets
```
Calypso/output/chapter_XX/
├── chapter_XX.html                    # CONSOLIDATED: all pages merged
├── page_artifacts/
│   └── page_YY/
│       ├── 02_page_YY.png             # PNG render (2x resolution)
│       ├── 03_page_YY_ascii.txt       # ASCII structural preview (FROM SKILL 2)
│       └── 04_page_YY.html            # Individual page HTML (FROM SKILL 3)
├── metadata/
│   ├── metadata.json                  # Chapter metadata
│   └── content.txt                    # Content summary
└── styles/
    └── main.css                       # Global semantic CSS classes
```

### Progress & Standards
```
Calypso/progress.md                    # SINGLE SOURCE OF TRUTH
                                      # - Chapter completion status
                                      # - Boundary validation results
                                      # - Quality metrics
                                      # - Current phase/blockers
```

### Validation & Tools
```
Calypso/tools/
├── orchestrator.py                    # Python: Extract + Render + Prepare for AI
├── rich_extractor.py                  # Python: Text extraction from PDF
├── validate_html.py                   # Python: Gates 1-2 validation (0-error target)
└── render_pages.py                    # Python: PNG rendering

Usage:
  python3 orchestrator.py <chapter> <start_page> <end_page>
  python3 validate_html.py <consolidated_file.html>
```

---

## Agents & Skills Location

### Agents (`.claude/agents/`)
```
.claude/agents/
├── project-analyzer/          # Analyze project structure & requirements
├── quality-orchestrator/       # Coordinate validation & quality checks
└── standards-definer/          # Define and enforce quality standards
```

**When to use:**
- Use `project-analyzer` for understanding codebase structure
- Use `quality-orchestrator` for multi-step validation workflows
- Use `standards-definer` for creating reusable standards

### Skills (`.claude/skills/`)
```
.claude/skills/
├── generate/                  # Skill 3: Generate HTML from PNG+JSON+ASCII
├── verify/                    # Validate deliverables against criteria
├── format-standardize/        # Standardize formatting & styling
└── validate-requirements/     # Check prerequisites before work

Integrated in workflow:
- Skill 2 (ASCII): AI analysis of PNG + JSON → ASCII structural preview
- Skill 3 (HTML): AI generation using PNG + JSON + ASCII → semantic HTML5
- Skill 4 (Consolidate): AI merging pages → single chapter file
```

---

## Process Flow: Extract → Render → Generate → Validate

### Phase 1: Data Preparation (Python - Deterministic)
```
INPUT: PDF file + chapter range (e.g., chapter 2, pages 15-27)
  ↓
orchestrator.py
  ├─ Extract PDF → JSON (rich_extraction.json)
  │  └─ Contains: text spans, fonts, sizes, positions, footer info
  ├─ Render PNG (02_page_XX.png)
  │  └─ 2x resolution visual reference
  └─ Prepare directory structure
OUTPUT: Ready for AI generation (Skill 2)
```

**Validation:**
- Check extraction has all pages
- Verify PNG renders exist
- Confirm JSON metadata matches page range

---

### Phase 2a: ASCII Preview Generation (AI Skill 2)
```
INPUT: PNG image + rich_extraction.json + understanding of structure
  ↓
SKILL 2: AI Analysis
  ├─ Analyze visual layout from PNG
  ├─ Read text structure from JSON
  ├─ Identify sections (h1, h2, h4, h5, bullets, tables, exhibits)
  ├─ Mark emphasis (bold, italic)
  └─ Generate 03_page_XX_ascii.txt
OUTPUT: ASCII preview showing:
  - Section hierarchy
  - FOOTER markers (start/end indicators)
  - OPENING markers (chapter header, title, nav)
  - CLOSING markers (Snapshot Review, summary)
  - Element counts & structure
  - Confidence scores
```

**Use ASCII files as boundary validators:**
- First page ASCII should show chapter number, title, navigation
- Last page ASCII should show "Snapshot Review" marker
- No ASCII should show next chapter's opening content

---

### Phase 2b: HTML Generation (AI Skill 3)
```
INPUT: PNG + JSON + ASCII preview (all three)
  ↓
SKILL 3: AI Generation
  ├─ Use PNG for visual context
  ├─ Use JSON for exact text & styling
  ├─ Use ASCII for structural guidance
  └─ Generate 04_page_XX.html
OUTPUT: Semantic HTML5
  - Proper heading hierarchy (h1 → h2 → h4, intentional skip)
  - Semantic CSS classes (from main.css)
  - Text styling preserved (<em>, <strong>)
  - Exhibits as <figure> elements
  - Tables as semantic <table> with <thead>/<tbody>
```

**Quality check:**
- Each page must validate with 0 errors
- Must use semantic classes from main.css
- Must preserve exact text from JSON

---

### Phase 3: Chapter Consolidation (AI Skill 4)
```
INPUT: All individual page HTMLs (04_page_15.html through 04_page_27.html)
  ↓
SKILL 4: Consolidation
  ├─ Merge all <main> content into single file
  ├─ Preserve chapter opening (from first page)
  ├─ Preserve chapter closing (last page = Snapshot Review)
  └─ Generate chapter_02.html
OUTPUT: Complete chapter file
  - Single <div class="page-container">
  - Single <main class="page-content chapter-content">
  - Seamless content flow
```

---

### Phase 4: Validation (Python - Deterministic)
```
INPUT: chapter_XX.html (consolidated)
  ↓
validate_html.py (Gates 1-2)
  ├─ Gate 1: Structural validation
  │  └─ DOCTYPE, meta tags, proper nesting
  ├─ Gate 2: Semantic validation
  │  └─ Heading hierarchy, CSS classes, list integrity
  └─ TARGET: 0 errors
OUTPUT: Validation report
  - Error count
  - Heading hierarchy
  - Semantic class coverage
  - List structure integrity
```

**Success criteria:**
- ✓ VALID with 0 errors
- All semantic classes properly applied
- Expected h2→h4 hierarchy jumps (intentional)

**Detailed validation guide:** See [VALIDATION_CHECKLIST.md](./.claude/VALIDATION_CHECKLIST.md) for step-by-step validation procedures

---

## ASCII Preview Files: The Boundary Validators

### What ASCII files contain:
```
03_page_XX_ascii.txt structure:
├─ PAGE HEADER (metadata)
├─ PAGE CONTENT (visual layout)
├─ STRUCTURE SUMMARY (element counts)
├─ KEY TERMS (emphasized content)
└─ CONFIDENCE ASSESSMENT
```

### How to read boundaries from ASCII:

**Chapter OPENING (First Page):**
```
Look for:
- Large chapter number (e.g., "3" in ASCII representation)
- Chapter title in large text
- Navigation menu with 3+ section items
- First major h2 section heading (ALL CAPS)
→ If these present: page is valid chapter opening
```

**Chapter CLOSING (Last Page):**
```
Look for:
- "Snapshot Review" text/marker
- Summary section headers (ALL CAPS, smaller size)
- Multiple bullet lists with condensed topics
- NO large chapter number (would indicate next chapter)
→ If these present: page is valid chapter ending
```

**Page BOUNDARIES:**
```
Look for footer information:
- Book page numbers in sequence (27 → 28 = chapter break)
- Chapter indicators if present
- No overlap between chapters
→ If continuous: chapter is properly bounded
```

---

## Chapter Standards (Based on Chapters 2-3)

### Required Chapter Structure:

#### Opening Page (First page of chapter):
- [ ] Large chapter number (70-80pt)
- [ ] Chapter title (26-28pt)
- [ ] Navigation menu (3+ items, 12pt)
- [ ] First major section heading (h2, ALL CAPS)
- [ ] ASCII shows all these elements
- [ ] HTML has chapter-header div with class="chapter-number" and "chapter-title"

#### Content Pages (Middle pages):
- [ ] Continuation of sections/subsections
- [ ] ASCII identifies h2, h4, h5 hierarchy
- [ ] Tables/figures properly marked in ASCII
- [ ] Bullet lists/paragraphs counted in ASCII

#### Closing Page (Last page of chapter):
- [ ] "Snapshot Review" marker visible
- [ ] Summary sections (h2 ALL CAPS)
- [ ] Bullet lists with condensed topics
- [ ] NO next chapter opening content
- [ ] ASCII explicitly shows "Snapshot Review" text

#### Validation:
- [ ] chapter_XX.html validates with 0 errors
- [ ] No page overlap with adjacent chapters
- [ ] Book page numbers sequential and continuous
- [ ] All pages present (no gaps)

---

## Chapters Status

| Chapter | Pages | Status | Validation | Notes |
|---------|-------|--------|------------|-------|
| 1 | 6-14 | ⭕ AUDIT | Needs standard check | Old format, needs review |
| 2 | 15-27 | ✅ FIXED | ✓ VALID (0 errors) | Extraction JSON needs update |
| 3 | 28-37 | ✅ FIXED | ✓ VALID (0 errors) | Extraction JSON needs update |
| 4 | 38-53 | ⭕ PENDING | Not started | Partial (pages 38-42 only) |
| 5-29 | ... | ⭕ PENDING | Not started | Awaiting automation setup |

---

## Data Flow Diagram

```
PDF File (593 pages)
    ↓
[Python] orchestrator.py
    ├─→ rich_extraction.json (text + fonts + positions)
    ├─→ 02_page_XX.png (visual renders)
    └─→ Directory structure ready
    ↓
[AI Skill 2] ASCII Preview Generation
    INPUT: PNG + JSON
    ↓
    03_page_XX_ascii.txt (structure + boundaries)
    ↓
[AI Skill 3] HTML Generation
    INPUT: PNG + JSON + ASCII
    ↓
    04_page_XX.html (individual pages, 0 errors each)
    ↓
[AI Skill 4] Consolidation
    INPUT: All 04_page_*.html files
    ↓
    chapter_XX.html (merged, maintains structure)
    ↓
[Python] validate_html.py (Gates 1-2)
    ↓
    ✓ VALID (0 errors)
    ↓
[HOOK] Pre-commit validation
    ├─ ASCII shows proper opening/closing?
    ├─ HTML validates with 0 errors?
    ├─ Progress.md updated?
    └─ → Approve or block operation
```

---

## Execution Checklist

Before processing any chapter:
- [ ] Verify extraction JSON has correct page_range in metadata
- [ ] Confirm orchestrator generated PNG renders for all pages
- [ ] Check ASCII files exist for all pages
- [ ] Verify ASCII shows proper opening on first page
- [ ] Verify ASCII shows "Snapshot Review" on last page
- [ ] Generate individual page HTMLs using Skill 3
- [ ] Validate each page with 0 errors
- [ ] Consolidate using Skill 4
- [ ] Final validation of consolidated chapter
- [ ] Update progress.md with status and metrics
- [ ] Run pre-commit hooks to verify standards met

**For detailed validation procedures:** See [VALIDATION_CHECKLIST.md](./.claude/VALIDATION_CHECKLIST.md)
- Quick validation (30 seconds): Run automated hook
- Complete manual validation (5-10 minutes): Follow detailed checklist
- Troubleshooting: Common issues and solutions

---

## Next Steps

1. ✓ Fix extraction JSONs (chapters 2-3 metadata)
2. ✓ Update progress.md as single source of truth
3. ✓ Create validation hooks referencing ASCII files (.claude/hooks/calypso-chapter-boundary-validation.sh)
4. ✓ Audit chapter 1 against standard (findings documented in progress.md)
5. ✓ Document reusable validation checklist (.claude/VALIDATION_CHECKLIST.md)
6. ⭕ Enable bash auto-approve for orchestrator operations
7. ⭕ Generate missing Chapter 3 page 28 artifacts (ASCII + HTML)
8. ⭕ Process remaining chapters using proven automation

---

## Documentation Reference

| Document | Purpose | Key Content |
|----------|---------|-------------|
| **CLAUDE.md** (this file) | Infrastructure & process | Directory structure, agents, skills, process flow, standards |
| **[VALIDATION_CHECKLIST.md](./.claude/VALIDATION_CHECKLIST.md)** | Validation procedures | Quick validation, manual checklist, troubleshooting |
| **[Calypso/progress.md](./Calypso/progress.md)** | Project status (SSoT) | Chapter status, boundary validation, known issues, metrics |
| **[.claude/hooks/calypso-chapter-boundary-validation.sh](./.claude/hooks/calypso-chapter-boundary-validation.sh)** | Automated validation | 5-step validation hook (extraction, opening, closing, HTML, progress) |

### Quick Reference

- **For overview:** Start with CLAUDE.md (this file)
- **For validation:** See VALIDATION_CHECKLIST.md
- **For status:** Check Calypso/progress.md (single source of truth)
- **For automation:** Run `./.claude/hooks/calypso-chapter-boundary-validation.sh <chapter_number>`