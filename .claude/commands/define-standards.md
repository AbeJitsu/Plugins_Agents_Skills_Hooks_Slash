---
description: Define quality standards for a new project type
---

# Define Standards - Setup New Quality Criteria

Create custom quality standards for a specific project type. This is a conversational setup where you tell me what matters for that type of work, and I'll structure it into your personal quality framework.

## Usage

`/define-standards <project-type>` - Define standards for a project type

Examples:
- `/define-standards react-components`
- `/define-standards api-endpoints`
- `/define-standards technical-writing`
- `/define-standards test-suites`

## What It Does

The standards-definer agent will:

1. Ask what's important for this project type
2. Listen to your quality criteria (what makes good work)
3. Explore high-level principles you care about
4. Ask about common pitfalls to avoid
5. Structure your answers into a reusable standard
6. Save it for future projects

## Examples of Standards You Might Define

**For Code Features:**
- "Must be testable with 80%+ coverage"
- "Must follow DRY principle"
- "Must include error handling"
- "Must be documented with JSDoc"

**For Documentation:**
- "Must have clear examples"
- "Must explain the why, not just the how"
- "Must be scannable with headers"
- "Must include troubleshooting section"

**For Test Suites:**
- "Should test happy path and edge cases"
- "Should have descriptive test names"
- "Should not be flaky or timing-dependent"

## Your Standards Are Learned

Each time you define standards, they're saved. The system learns your preferences and applies them automatically in the quality pipeline.
