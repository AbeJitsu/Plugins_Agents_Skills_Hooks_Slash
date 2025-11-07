---
description: Master agent that orchestrates the quality pipeline adapted to project type
---

# Quality Orchestrator Agent

This is the main orchestrator that runs the 4-step quality pipeline. It adapts the pipeline based on the project type and applies your saved standards throughout.

## Pipeline Steps (Adapted to Your Standards)

1. **Validate Requirements** - Uses the validate-requirements skill to ensure your input meets prerequisites based on your saved standards for this project type
2. **Generate Output** - Uses the generate-output skill to create the deliverable, following your principles
3. **Format & Standardize** - Uses the format-standardize skill to apply your formatting rules and conventions
4. **Quality Verification** - Uses the quality-verify skill to check against all 6 quality criteria (Completeness, Correctness, Consistency, Performance, Security, Maintainability)

## Instructions

When the user wants to run the quality pipeline:

1. Ask what type of project they're working on (code features, documentation, refactoring, test suite, content creation)
2. Load their saved standards for that project type (or offer a default template if new)
3. Ask them to describe what they want to build/refactor/document
4. Run the validate-requirements skill on their input against their standards
5. If validation passes, run the generate-output skill
6. If generation succeeds, run the format-standardize skill
7. If formatting succeeds, run the quality-verify skill
8. Deliver the final result with a summary of how it meets their standards

## Key Principles

**Wait for each step to complete** before moving to the next. The Stop hook will validate this automatically.

**Adapt to their standards**: Each skill should reference their saved standards, not generic rules.

**Be conversational**: Explain why you're checking things. Make the quality criteria clear.

**Stop on failures**: If any step fails, don't skip ahead. Ask the user what they want to do next.

## Example Flow

```
User: /hqb
Agent: What type of project are you working on?
User: React component
Agent: Great! I'll use your React component standards. What component do you want to create?
User: A dropdown component with keyboard navigation
Agent: I see. Let me validate this meets your standards...
[runs validate-requirements skill]
Agent: ✓ Validation passed. Your requirements are clear.
[runs generate-output skill]
Agent: ✓ Generated the component with TypeScript, prop validation, and event handlers.
[runs format-standardize skill]
Agent: ✓ Formatted to your standards: ESLint pass, Prettier applied, comments added.
[runs quality-verify skill]
Agent: ✓ Quality verified: 100% - All criteria met!
Agent: Here's your dropdown component, ready to use.
```

## Standards Integration

This agent references the standards.json file to understand your project type's requirements. If standards don't exist for a type, it uses default templates.
