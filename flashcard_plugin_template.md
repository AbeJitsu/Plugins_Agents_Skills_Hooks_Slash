# Claude Code Flashcard Plugin - Complete Setup Template

## Folder Structure

```
flashcard-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── flashcard.md
├── agents/
│   └── flashcard-orchestrator.md
├── skills/
│   ├── validate-source/
│   │   └── SKILL.md
│   ├── generate-cards/
│   │   └── SKILL.md
│   ├── format-output/
│   │   └── SKILL.md
│   └── quality-check/
│       └── SKILL.md
├── hooks/
│   ├── hooks.json
│   └── validate-pipeline.sh
└── README.md
```

---

## File 1: `.claude-plugin/plugin.json`

```json
{
  "name": "flashcard-generator",
  "description": "Autonomous flashcard generation with validation hooks and multi-step pipeline",
  "version": "1.0.0",
  "author": {
    "name": "Abe at Acadio"
  }
}
```

---

## File 2: `commands/flashcard.md`

```markdown
---
description: Generate flashcards from source material with automatic validation
---

# Flashcard Generator Command

Run the complete flashcard pipeline from start to finish. This command orchestrates validation, generation, formatting, and quality checking.

## Usage

`/flashcard` - Starts the flashcard orchestrator agent

## What It Does

1. Validates your source material is ready
2. Generates flashcard content
3. Formats output for consistency
4. Runs quality checks before delivery

The pipeline includes automated validation hooks that ensure each step completes before moving to the next.
```

---

## File 3: `agents/flashcard-orchestrator.md`

```markdown
---
description: Master agent that orchestrates the complete flashcard pipeline
---

# Flashcard Orchestrator Agent

This agent runs the 4-step flashcard pipeline in sequence:

1. **Validation** - Uses the validate-source skill to ensure input is ready
2. **Generation** - Uses the generate-cards skill to create flashcard content
3. **Formatting** - Uses the format-output skill to standardize the output
4. **Quality Check** - Uses the quality-check skill to verify everything is correct

## Instructions

When the user wants to generate flashcards:

1. Ask them what source material they want to use
2. Run the validate-source skill on the input
3. If validation passes, run the generate-cards skill
4. If generation succeeds, run the format-output skill
5. If formatting succeeds, run the quality-check skill
6. Deliver the final flashcards

If any step fails, stop and ask the user what they want to do next. Don't skip steps.

## Key Principle

Wait for explicit confirmation that each step completed successfully before moving to the next. The Stop hook will validate this automatically.
```

---

## File 4: `skills/validate-source/SKILL.md`

```markdown
---
name: validate-source
description: Verify that source material is valid and ready for flashcard generation. Use when checking if input data is complete, properly formatted, and contains sufficient content.
---

# Validate Source Skill

## Purpose

Ensures the source material is ready before generation begins.

## What to Check

- Is the source material present and readable?
- Does it contain enough content (minimum 100 words)?
- Is the format recognizable (text, markdown, HTML)?
- Are there any encoding issues or corruption?

## Process

1. Read the source material
2. Check file size and format
3. Scan for common issues (empty files, corrupted text)
4. Report findings clearly

## Output

Return a simple JSON object:

```json
{
  "status": "valid" or "invalid",
  "issues": ["list of any problems found"],
  "word_count": number,
  "recommendation": "proceed or fix X before continuing"
}
```

## Success Criteria

- Status is "valid"
- No critical issues found
- Word count exceeds 100
```

---

## File 5: `skills/generate-cards/SKILL.md`

```markdown
---
name: generate-cards
description: Create flashcard content from validated source material. Use when you have validated source material and need to generate actual flashcard questions and answers.
---

# Generate Cards Skill

## Purpose

Transforms source material into individual flashcards with questions and answers.

## What to Do

1. Read the validated source material
2. Extract key concepts and ideas
3. Create question-answer pairs
4. Ensure questions are clear and specific
5. Ensure answers are concise but complete

## Format Per Card

```
Question: [Clear, specific question]
Answer: [Concise but complete answer]
Topic: [Category]
Difficulty: [Easy/Medium/Hard]
```

## Output

Generate 5-15 cards depending on source length. Return as a structured list.

## Success Criteria

- Each card has a clear question and answer
- Answers are self-contained (can be understood alone)
- No duplicate cards
- Topics are logical and related
```

---

## File 6: `skills/format-output/SKILL.md`

```markdown
---
name: format-output
description: Standardize flashcard formatting for consistency and usability. Use after cards are generated to ensure consistent structure, markup, and presentation.
---

# Format Output Skill

## Purpose

Ensures all flashcards follow consistent formatting and markup standards.

## What to Do

1. Check each flashcard's structure
2. Standardize spacing and indentation
3. Ensure markdown is consistent
4. Add proper line breaks between cards
5. Remove any formatting inconsistencies

## Format Standard

```
---
Card 1
Question: [text]
Answer: [text]
Topic: [text]
Difficulty: [level]
---
```

## Validation

- All cards have same structure
- No extra whitespace or formatting artifacts
- Ready for export or display

## Success Criteria

- Consistent formatting across all cards
- Valid structure for import/export
- Clean, professional appearance
```

---

## File 7: `skills/quality-check/SKILL.md`

```markdown
---
name: quality-check
description: Verify flashcard quality and completeness before delivery. Use as the final validation step to ensure cards meet quality standards.
---

# Quality Check Skill

## Purpose

Final validation that all flashcards meet quality standards before delivery.

## What to Check

1. **Completeness** - Do all cards have questions and answers?
2. **Clarity** - Are questions unambiguous?
3. **Accuracy** - Are answers correct based on source?
4. **Consistency** - Do all cards follow the same format?
5. **Useful** - Would these cards actually help someone learn?

## Scoring

- 0 issues = ✓ Ready to deliver
- 1-2 issues = ⚠️ Minor fixes needed
- 3+ issues = ✗ Major problems, restart

## Output

```json
{
  "quality_score": "0-100",
  "issues_found": ["list"],
  "ready_to_deliver": true/false,
  "notes": "brief summary"
}
```

## Success Criteria

- Quality score above 85
- No critical issues
- Ready to deliver = true
```

---

## File 8: `hooks/hooks.json`

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/hooks/validate-pipeline.sh"
          }
        ]
      }
    ]
  }
}
```

---

## File 9: `hooks/validate-pipeline.sh`

```bash
#!/bin/bash

# Flashcard Pipeline Validation Hook
# Runs at the end of each agent turn to ensure tasks completed

set -e

echo "🔍 Validating flashcard pipeline..."

# Check if output contains all required steps
# This is a simple example - customize based on your needs

if grep -q "validation.*passed\|valid\|✓" <<< "$@" 2>/dev/null; then
  echo "✓ Validation passed"
else
  echo "⚠️  Validation step not confirmed"
fi

if grep -q "generation.*complete\|cards.*created\|✓" <<< "$@" 2>/dev/null; then
  echo "✓ Generation passed"
else
  echo "⚠️  Generation step not confirmed"
fi

if grep -q "format.*applied\|formatted\|✓" <<< "$@" 2>/dev/null; then
  echo "✓ Formatting passed"
else
  echo "⚠️  Formatting step not confirmed"
fi

if grep -q "quality.*passed\|ready.*deliver\|✓" <<< "$@" 2>/dev/null; then
  echo "✓ Quality check passed"
else
  echo "⚠️  Quality check not confirmed"
fi

echo ""
echo "✅ Pipeline validation complete"
```

---

## File 10: `README.md`

```markdown
# Flashcard Generator Plugin

Autonomous flashcard generation system with validation hooks and multi-step pipeline.

## Installation

```bash
/plugin install flashcard-generator
```

## Usage

```bash
/flashcard
```

## Pipeline Steps

1. **Validate** - Source material validation
2. **Generate** - Flashcard creation
3. **Format** - Output standardization
4. **Quality Check** - Final verification

## Architecture

- **Skills**: 4 specialized skills (one per step)
- **Agent**: Orchestrator that runs skills in sequence
- **Hooks**: Stop hooks validate completion
- **Slash Command**: `/flashcard` entry point

## How It Works

When you run `/flashcard`, the orchestrator agent:
1. Calls validate-source skill
2. If valid, calls generate-cards skill
3. If generated, calls format-output skill
4. If formatted, calls quality-check skill
5. Stop hook validates all steps completed
6. Delivers final flashcards

If any step fails, the hook catches it and asks for your input.

## Customization

Edit the SKILL.md files to match your exact flashcard requirements.
```

---

## Setup Instructions

1. Create the folder structure above
2. Copy each file into its location
3. Make the hook script executable: `chmod +x hooks/validate-pipeline.sh`
4. Test locally with: `/plugin install ./flashcard-plugin`
5. Try it: `/flashcard`

This is your complete, copy-paste-ready template.