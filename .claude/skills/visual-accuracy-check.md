# Visual Accuracy Check Skill

Compare a generated HTML page against its source PDF PNG to verify visual accuracy.

## Input
- Chapter number
- Page number

## Process

1. **Load the source PNG image**
   - Read: `Calypso/output/chapter_{XX}/page_artifacts/page_{YY}/02_page_{YY}.png`
   - This is the ground truth - the original PDF page render

2. **Load the generated HTML**
   - Read: `Calypso/output/chapter_{XX}/page_artifacts/page_{YY}/04_page_{YY}.html`
   - This is what we generated

3. **Visually analyze the PNG** (using Claude Code's vision)
   - Identify: layout structure, heading hierarchy, visual elements
   - Note: tables, lists, exhibits, sidebars, formatting
   - Observe: spacing, alignment, typography

4. **Analyze the HTML semantically**
   - Check: Does HTML structure match visual layout?
   - Verify: Headings map correctly to visual hierarchy
   - Confirm: Lists, tables, exhibits are present and formatted
   - Validate: Spacing and grouping matches original

5. **Score visual similarity** (0-100%)

Evaluate these dimensions:
- **Layout Accuracy (0-100)**: Does HTML match PDF layout structure?
- **Content Presentation (0-100)**: Is content displayed appropriately?
- **Visual Hierarchy (0-100)**: Is visual emphasis correct (headings, sections)?
- **Formatting Details (0-100)**: Borders, spacing, alignment correct?
- **Completeness (0-100)**: All visible PDF content in HTML?

Calculate: `overall_similarity = average of 5 scores`

6. **Provide detailed feedback**

For each dimension with score <80%:
- List specific issues found
- Suggest improvements for regeneration

## Output

Create validation report:

```
VISUAL ACCURACY REPORT
Chapter: {X}, Page: {Y}

Layout Accuracy: {score}%
{issues if any}

Content Presentation: {score}%
{issues if any}

Visual Hierarchy: {score}%
{issues if any}

Formatting Details: {score}%
{issues if any}

Completeness: {score}%
{issues if any}

Overall Visual Similarity: {overall}%

VERDICT: {PASS ≥80% | WARNING 60-80% | FAIL <60%}

{Recommendations if <80%}
```

## Success Criteria

- Overall similarity ≥80% → PASS
- Overall similarity 60-80% → WARNING (recommend regeneration)
- Overall similarity <60% → FAIL (regeneration required)

## Integration

This skill is invoked by:
- Stage 4 validation hook as Part 3
- Manual validation during page regeneration
- Comprehensive chapter validation

## Example Usage

```
User: "Check visual accuracy for Chapter 2, Page 27"

Claude Code:
1. Reads PNG image (using vision)
2. Reads HTML file
3. Compares layout, structure, formatting
4. Scores each dimension
5. Provides detailed report with overall score
```

This leverages Claude Code's native vision capabilities without external API calls.
