---
description: Run the quality pipeline for your project
---

# High-Quality Builder - Main Pipeline

Launch the adaptive quality pipeline for your project. This will detect your project type, apply your saved standards, and guide you through validation → generation → formatting → quality verification.

## Usage

`/hqb` - Starts the quality orchestrator agent

## What It Does

1. Asks what type of project you're working on
2. Loads your saved standards (or defaults if new)
3. Validates your requirements
4. Generates your deliverable
5. Formats it to your standards
6. Verifies quality against all criteria
7. Delivers the result

## Examples

- `/hqb` - Interactive mode: "What are you building?"
- Create new code features and ensure they follow your standards
- Refactor existing code with consistent approach
- Generate test suites that match your quality criteria
- Write documentation that meets your specifications
- Create content that aligns with your principles

The pipeline adapts based on your chosen project type and remembers your preferences.
