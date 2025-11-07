#!/bin/bash

# High-Quality Builder Pipeline Validation Hook
# Runs at the end of each agent turn to ensure quality pipeline steps completed

set -e

echo "🔍 Validating quality pipeline..."
echo ""

# Track which steps were completed based on keywords in the output
validation_passed=false
generation_passed=false
formatting_passed=false
quality_check_passed=false

# Check for validation step completion
if grep -iq "validation.*passed\|valid\|requirement.*check\|✓.*validation" <<< "$@" 2>/dev/null; then
  echo "✓ Validation step confirmed"
  validation_passed=true
else
  echo "⚠️  Validation step not confirmed yet"
fi

# Check for generation step completion
if grep -iq "generation.*complete\|generated\|output.*created\|✓.*generate" <<< "$@" 2>/dev/null; then
  echo "✓ Generation step confirmed"
  generation_passed=true
else
  echo "⚠️  Generation step not confirmed yet"
fi

# Check for formatting step completion
if grep -iq "format.*applied\|formatted\|standardize.*complete\|✓.*format" <<< "$@" 2>/dev/null; then
  echo "✓ Formatting step confirmed"
  formatting_passed=true
else
  echo "⚠️  Formatting step not confirmed yet"
fi

# Check for quality check step completion
if grep -iq "quality.*passed\|quality.*verified\|ready.*deliver\|✓.*quality" <<< "$@" 2>/dev/null; then
  echo "✓ Quality check step confirmed"
  quality_check_passed=true
else
  echo "⚠️  Quality check step not confirmed yet"
fi

echo ""

# Determine pipeline state
completed_steps=0
[ "$validation_passed" = true ] && ((completed_steps++))
[ "$generation_passed" = true ] && ((completed_steps++))
[ "$formatting_passed" = true ] && ((completed_steps++))
[ "$quality_check_passed" = true ] && ((completed_steps++))

# Provide feedback based on completion status
if [ $completed_steps -eq 4 ]; then
  echo "✅ All pipeline steps completed successfully!"
  echo "🎉 Quality pipeline is ready to deliver"
elif [ $completed_steps -eq 0 ]; then
  echo "⏳ Pipeline just started - continue with the quality process"
elif [ $completed_steps -lt 4 ]; then
  echo "⏳ Pipeline in progress: $completed_steps/4 steps completed"
  echo "   Continue with the next step when ready"
fi

echo ""
