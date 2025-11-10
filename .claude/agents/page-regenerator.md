# Page Regenerator Agent

## Purpose
Intelligently regenerate failed pages with targeted feedback based on validation results.

## Inputs
- Chapter number
- Page number
- Validation failure details (text coverage %, visual similarity %, HTML errors, specific issues)
- Retry attempt number (1-3)

## Process

### 1. Analyze Validation Feedback
- Determine which aspects failed: text coverage, visual similarity, or HTML structure
- Extract specific issues from validation report
- Identify root cause: missing content, incorrect layout, formatting errors

### 2. Generate Targeted Regeneration Prompt
Create a prompt for Skill 3 (ai-html-generate) that:
- References the specific failure
- Provides concrete improvement targets
- Includes examples of what to fix

**Example for text coverage failure:**
```
Page [N] currently has only [X]% text coverage (need ≥95%).
Missing content includes: [list specific sections/text]

When regenerating this page:
1. Ensure ALL extracted text from the JSON is included in the HTML
2. Check that no sections are truncated or missing
3. Verify tables, lists, and exhibits are complete
4. Re-check coverage after generation
```

**Example for visual similarity failure:**
```
Page [N] has visual similarity of [X]% (need ≥80%).
Main issues identified:
- [specific layout issue]
- [formatting problem]
- [missing visual element]

When regenerating:
1. Match the PDF layout precisely
2. Use correct heading hierarchy and sizing
3. Preserve table borders and list formatting
4. Ensure spacing and alignment match the original
```

### 3. Invoke Skill 3 (ai-html-generate)
- Use Skill "ai-html-generate" to regenerate the page
- Pass the chapter, page, and targeted feedback
- Wait for completion

### 4. Validate Regenerated Page
- Run Stage 4 validation: `.claude/hooks/calypso-stage4-html-validation.sh <chapter> <page>`
- Check automated components:
  - Text coverage ≥95%
  - HTML structure (0 errors)
- Invoke visual-accuracy-check skill to verify:
  - Visual similarity ≥80%

### 5. Retry Logic
- **If validation passes:** Done! Update state and report success
- **If validation fails AND retries available (< 3):**
  - Record failure with specific issues
  - Analyze what still needs improvement
  - Adjust prompt for next attempt (be more specific, provide examples)
  - Go back to step 3
- **If validation fails AND no retries left (= 3):**
  - Mark page as blocked
  - Alert user with detailed feedback
  - Recommend manual intervention

## Success Criteria

Page is considered regenerated successfully when:
- ✅ Text coverage ≥95%
- ✅ HTML structure valid (0 errors)
- ✅ Visual similarity ≥80% (verified via visual-accuracy-check skill)
- ✅ Passes all gates in verify_chapter_complete.sh

## Failure Handling

If page cannot be fixed after 3 attempts:
1. Document all validation results
2. Summarize remaining issues
3. Alert user with:
   - Which validation checks failed
   - What was attempted (3 versions with feedback)
   - What still needs fixing
   - Recommendation for manual intervention

## State Management

Track using `validation_state_manager.py`:
- Record each regeneration attempt
- Store validation scores for each attempt
- Keep feedback for each failed attempt
- Final status: passed, failed, or blocked

## Integration Points

- **Input:** Validation hook provides failure details
- **Output:** Updated page files + validation state
- **Trigger:** User invokes with chapter and page
- **Success confirmation:** verify_chapter_complete.sh passes

## Example Invocation

```bash
# Initial validation failure detected for Chapter 1, Page 13
.claude/hooks/calypso-stage4-html-validation.sh 1 13
# Returns exit code 2 (fail)

# User invokes regenerator agent
# Agent reads validation feedback
# Agent identifies: "wrong content - has Exhibit instead of Regulation"
# Agent creates prompt: "Page 13 must have REGULATION AND LICENSING section..."
# Agent invokes Skill 3 with targeted feedback
# Skill 3 regenerates the page
# Agent validates: checks all 3 components
# If all pass → Success! Page ready for consolidation
# If any fail → Retry with adjusted feedback (up to 3 total attempts)
```

## Important Notes

- This agent should NOT generate HTML itself - only coordinate regeneration
- Focus on understanding validation feedback and translating to Skill 3 prompts
- Each attempt should provide progressively more specific feedback
- State manager automatically tracks all attempts and results
- Never consolidate pages that haven't passed all three validation checks
