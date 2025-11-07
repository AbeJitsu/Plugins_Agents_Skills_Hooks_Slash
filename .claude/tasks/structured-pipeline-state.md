# Task: Implement Structured Pipeline State

## 🎯 Overview

We're replacing the fragile **text-parsing hook** with a robust **structured pipeline state** system. Right now, the hook searches for keywords like "validation.*passed" in natural language output — it's incredibly fragile and error-prone. This task establishes a clean state file that skills explicitly write to, eliminating guesswork.

**Why it matters**:
- Current approach breaks if you rephrase output
- Can't distinguish "validation failed" from "validation passed"
- No way to debug pipeline state between runs
- No metadata about what actually happened
- Skills must "perform for the hook" using magic keywords

**What it solves**:
- Orthogonality issue #4 (hook validation coupling) — the worst orthogonality problem
- Enables proper error handling and debugging
- Creates clear communication between pipeline steps

---

## 🎯 Goals

- [x] Define pipeline state structure
- [x] Create schema for state validation
- [ ] Update hook to read structured state instead of parsing text
- [ ] Update all 4 skills to write structured status
- [ ] Verify pipeline correctly tracks progress

---

## 📖 Current State

### How Hook Validation Works Now

**Location**: `.claude/hooks/validate-quality.sh`

**Current approach** (lines 12-46):
```bash
validation_passed=false
generation_passed=false
formatting_passed=false
quality_check_passed=false

# Check for validation completion with regex
if grep -iq "validation.*passed\|valid\|requirement.*check\|✓.*validation" <<< "$@"
then
  validation_passed=true
fi

# Check for generation completion
if grep -iq "generation.*complete\|generated\|output.*created\|✓.*generate" <<< "$@"
then
  generation_passed=true
fi

# Similar for formatting and quality...

# Then judge pipeline completion
if [ "$validation_passed" = true ] && [ "$generation_passed" = true ] && \
   [ "$formatting_passed" = true ] && [ "$quality_check_passed" = true ]
then
  echo "✓ Pipeline complete and ready for delivery"
fi
```

### Problems with Current Approach

1. **Fragile Text Matching**: Depends on keywords appearing in output
2. **False Positives**: "Validation failed" might match "validation"
3. **False Negatives**: Rephrased output breaks pattern matching
4. **No Metadata**: Can't see duration, errors, timestamps
5. **Coupling**: Skills must write specific keywords
6. **No History**: Can't see what happened in previous runs
7. **No Error Tracking**: Can't distinguish "step skipped" from "step failed"

### Skill Output Problem

**Skills currently output free-form text**:
```
"I've validated your requirements and found 3 sections:
1. Feature description
2. Acceptance criteria
3. Edge cases

All requirements are clear and complete. ✓ validation"
```

The hook searches this output for keywords like "validation" and "✓".

**Issues**:
- Hook success depends on specific wording
- Skills can't communicate structured information
- No way to pass data between steps reliably
- Debugging is impossible

---

## 🏗️ New Design: Structured Pipeline State

### Concept

A JSON state file that explicitly tracks what happened:

```json
{
  "currentRun": {
    "startTime": "2025-11-07T10:30:00Z",
    "projectType": "code-features",
    "steps": {
      "validation": {
        "status": "completed",
        "startTime": "2025-11-07T10:30:00Z",
        "endTime": "2025-11-07T10:30:15Z",
        "durationMs": 15000,
        "errors": [],
        "metadata": {
          "inputSource": "user",
          "requirementsCount": 3
        }
      },
      "generation": {
        "status": "in_progress",
        "startTime": "2025-11-07T10:30:15Z"
      },
      "formatting": {
        "status": "pending"
      },
      "verification": {
        "status": "pending"
      }
    }
  }
}
```

### Benefits

- **Explicit**: No ambiguity about what happened
- **Structured**: Can parse reliably
- **Observable**: Can see progress and timing
- **Debuggable**: Full history of each step
- **Flexible**: Skills can add metadata
- **Error-Aware**: Can track failures and reasons
- **Auditable**: Complete record of execution

---

## 📋 Implementation Steps

### Step 1: Create Pipeline State Schema

**What**: Define the JSON schema for pipeline state

**Why**: Ensures state file is always valid

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/lib/schemas/pipeline-state.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Pipeline State Schema",
  "description": "Tracks the state of HQB pipeline execution across all steps",
  "type": "object",
  "required": ["currentRun"],
  "properties": {
    "currentRun": {
      "type": "object",
      "description": "Current pipeline execution state",
      "required": ["startTime", "steps"],
      "properties": {
        "startTime": {
          "type": "string",
          "format": "date-time",
          "description": "When the pipeline started"
        },
        "projectType": {
          "type": "string",
          "description": "Project type being worked on"
        },
        "steps": {
          "type": "object",
          "description": "State of each pipeline step",
          "required": ["validation", "generation", "formatting", "verification"],
          "properties": {
            "validation": {
              "$ref": "#/definitions/stepState"
            },
            "generation": {
              "$ref": "#/definitions/stepState"
            },
            "formatting": {
              "$ref": "#/definitions/stepState"
            },
            "verification": {
              "$ref": "#/definitions/stepState"
            }
          }
        }
      }
    }
  },
  "definitions": {
    "stepState": {
      "type": "object",
      "description": "State of a single pipeline step",
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["pending", "in_progress", "completed", "failed", "skipped"],
          "description": "Current status of the step"
        },
        "startTime": {
          "type": "string",
          "format": "date-time",
          "description": "When step started (ISO 8601)"
        },
        "endTime": {
          "type": "string",
          "format": "date-time",
          "description": "When step completed"
        },
        "durationMs": {
          "type": "integer",
          "description": "Duration in milliseconds"
        },
        "errors": {
          "type": "array",
          "description": "Any errors that occurred",
          "items": {
            "type": "object",
            "required": ["message"],
            "properties": {
              "message": { "type": "string" },
              "code": { "type": "string" },
              "severity": { "enum": ["warning", "error", "critical"] }
            }
          }
        },
        "metadata": {
          "type": "object",
          "description": "Step-specific metadata",
          "additionalProperties": true
        }
      }
    }
  }
}
```

**Validation**: ✅ Schema file created and valid

---

### Step 2: Create Pipeline State Utilities Documentation

**What**: Document how to write and read pipeline state

**Why**: Makes it easy for skills to update state correctly

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/lib/pipeline-state-utilities.md`:

```markdown
# Pipeline State Utilities

Helpers for reading and writing the structured pipeline state file.

## Location

Pipeline state is stored at: `.claude/pipeline-state.json`

## State Structure

See `lib/schemas/pipeline-state.json` for complete schema.

Current state structure:
```json
{
  "currentRun": {
    "startTime": "ISO-8601 timestamp",
    "projectType": "code-features",
    "steps": {
      "validation": { "status": "...", ... },
      "generation": { "status": "...", ... },
      "formatting": { "status": "...", ... },
      "verification": { "status": "...", ... }
    }
  }
}
```

## Step Statuses

- **pending**: Not yet started
- **in_progress**: Currently executing
- **completed**: Finished successfully
- **failed**: Encountered an error
- **skipped**: Was not executed (by design)

## How Skills Use Pipeline State

### Starting a Step

When a skill begins:

```markdown
Update the pipeline state to mark the step as in_progress:

```
status: in_progress
startTime: current ISO-8601 timestamp
```

Example for validation step:
```json
{
  "currentRun": {
    "steps": {
      "validation": {
        "status": "in_progress",
        "startTime": "2025-11-07T10:30:15Z"
      }
    }
  }
}
```
```

---

### Completing a Step Successfully

When a skill finishes successfully:

```markdown
```
status: completed
endTime: current ISO-8601 timestamp
durationMs: calculated duration
errors: [] (empty array)
metadata: { ... any relevant data ... }
```

Example:
```json
{
  "currentRun": {
    "steps": {
      "validation": {
        "status": "completed",
        "startTime": "2025-11-07T10:30:15Z",
        "endTime": "2025-11-07T10:30:30Z",
        "durationMs": 15000,
        "errors": [],
        "metadata": {
          "requirementsCount": 3,
          "validationErrors": 0
        }
      }
    }
  }
}
```
```

---

### Completing a Step with Errors

If a step encounters recoverable errors:

```markdown
```
status: completed  (or "failed" if unrecoverable)
endTime: current ISO-8601 timestamp
durationMs: calculated duration
errors: [
  {
    "message": "Description of what went wrong",
    "code": "ERROR_CODE",
    "severity": "warning" | "error" | "critical"
  }
]
```

Example:
```json
{
  "currentRun": {
    "steps": {
      "validation": {
        "status": "completed",
        "errors": [
          {
            "message": "Missing acceptance criteria in requirement 2",
            "code": "MISSING_CRITERIA",
            "severity": "warning"
          }
        ]
      }
    }
  }
}
```
```

---

### Recording Step Metadata

Skills can add custom metadata for debugging/auditing:

```markdown
Add any relevant information to the metadata object:

```
metadata: {
  "inputSource": "user",
  "requirementsCount": 3,
  "standardsLoaded": true,
  "customFields": { ... }
}
```
```

---

## How the Hook Uses Pipeline State

The validation hook (`hooks/validate-quality.sh`) now:

1. Reads `.claude/pipeline-state.json`
2. Checks `currentRun.steps.validation.status`
3. Checks `currentRun.steps.generation.status`
4. Checks `currentRun.steps.formatting.status`
5. Checks `currentRun.steps.verification.status`

No text parsing. No keyword matching. Just explicit state checking.

---

## Example: Full Pipeline Execution

```json
{
  "currentRun": {
    "startTime": "2025-11-07T10:30:00Z",
    "projectType": "code-features",
    "steps": {
      "validation": {
        "status": "completed",
        "startTime": "2025-11-07T10:30:00Z",
        "endTime": "2025-11-07T10:30:15Z",
        "durationMs": 15000,
        "errors": [],
        "metadata": { "requirementsCount": 3 }
      },
      "generation": {
        "status": "completed",
        "startTime": "2025-11-07T10:30:15Z",
        "endTime": "2025-11-07T10:31:00Z",
        "durationMs": 45000,
        "errors": [],
        "metadata": { "outputLines": 250, "timeoutMs": 60000 }
      },
      "formatting": {
        "status": "completed",
        "startTime": "2025-11-07T10:31:00Z",
        "endTime": "2025-11-07T10:31:15Z",
        "durationMs": 15000,
        "errors": [],
        "metadata": { "linesFormatted": 250 }
      },
      "verification": {
        "status": "completed",
        "startTime": "2025-11-07T10:31:15Z",
        "endTime": "2025-11-07T10:31:45Z",
        "durationMs": 30000,
        "errors": [],
        "metadata": { "dimensionsChecked": 6, "allPassed": true }
      }
    }
  }
}
```

---

## Initialization

At the start of a pipeline run, initialize the state file:

```bash
# Initialize with pending steps
echo '{
  "currentRun": {
    "startTime": "ISO-8601 now",
    "steps": {
      "validation": { "status": "pending" },
      "generation": { "status": "pending" },
      "formatting": { "status": "pending" },
      "verification": { "status": "pending" }
    }
  }
}' > .claude/pipeline-state.json
```

---

## Important Notes

- State file is JSON, never text
- Always write complete step state, not partial updates
- Use ISO-8601 format for all timestamps
- Include metadata for debugging/auditing
- State file is created fresh for each pipeline run
- Hook can safely assume state file is valid JSON

---
```

**Validation**: ✅ Utilities documentation created

---

### Step 3: Rewrite Validation Hook

**What**: Replace text-parsing hook with state file reader

**Why**: Creates reliable, unambiguous pipeline validation

**Current problematic hook** (lines 1-46 of `.claude/hooks/validate-quality.sh`):
```bash
#!/bin/bash

# Parse text output for completion keywords
validation_passed=false
generation_passed=false
formatting_passed=false
quality_check_passed=false

if grep -iq "validation.*passed\|valid\|requirement.*check\|✓.*validation" <<< "$@"
then
  validation_passed=true
fi

# ... more regex matching ...

if [ "$validation_passed" = true ] && [ "$generation_passed" = true ] && \
   [ "$formatting_passed" = true ] && [ "$quality_check_passed" = true ]
then
  echo "✓ Pipeline complete and ready for delivery"
fi
```

**Replacement**:

Create new version of `.claude/hooks/validate-quality.sh`:

```bash
#!/bin/bash

# Structured Pipeline State Validation Hook
# Reads pipeline state from .claude/pipeline-state.json
# No text parsing, explicit state checking

STATE_FILE=".claude/pipeline-state.json"

# Check if state file exists
if [ ! -f "$STATE_FILE" ]; then
  exit 0  # State file not created yet, allow pipeline to continue
fi

# Read state file and check step statuses
validation_status=$(jq -r '.currentRun.steps.validation.status' "$STATE_FILE" 2>/dev/null)
generation_status=$(jq -r '.currentRun.steps.generation.status' "$STATE_FILE" 2>/dev/null)
formatting_status=$(jq -r '.currentRun.steps.formatting.status' "$STATE_FILE" 2>/dev/null)
verification_status=$(jq -r '.currentRun.steps.verification.status' "$STATE_FILE" 2>/dev/null)

# All steps must be completed for pipeline to be ready
if [ "$validation_status" = "completed" ] && \
   [ "$generation_status" = "completed" ] && \
   [ "$formatting_status" = "completed" ] && \
   [ "$verification_status" = "completed" ]; then
  echo "✓ Pipeline complete: All steps passed validation"
  echo "✓ Ready for delivery"
  exit 0
else
  # Report current status
  echo "Pipeline status:"
  echo "  Validation:    $validation_status"
  echo "  Generation:    $generation_status"
  echo "  Formatting:    $formatting_status"
  echo "  Verification:  $verification_status"
  exit 0  # Don't block, allow pipeline to continue
fi
```

**Validation**: ✅ Hook reads structured state instead of parsing text

---

### Step 4: Update All 4 Skills to Write State

**What**: Modify each skill to write pipeline state

**Why**: Skills explicitly track their progress

**Location**: Each skill file

**Pattern**: At the end of each skill, before returning output

**Example for validate-requirements/SKILL.md**:

Add this section:

```markdown
## Recording Pipeline State

After validation completes, record the state:

```json
Update .claude/pipeline-state.json:
{
  "currentRun": {
    "steps": {
      "validation": {
        "status": "completed",
        "endTime": "<current ISO-8601 timestamp>",
        "durationMs": <calculated duration>,
        "errors": [],
        "metadata": {
          "requirementsValidated": true,
          "requirementsCount": <number>,
          "validationErrors": <count>
        }
      }
    }
  }
}
```

This allows the hook to track pipeline progress reliably.
```

**Apply to all 4 skills**:
1. `validate-requirements/SKILL.md` — Records validation step
2. `generate-output/SKILL.md` — Records generation step
3. `format-standardize/SKILL.md` — Records formatting step
4. `quality-verify/SKILL.md` — Records verification step

**Validation**: ✅ All skills can write state

---

### Step 5: Initialize State at Pipeline Start

**What**: Ensure state file exists before pipeline runs

**Why**: Hook expects file to exist

**How**: Add to quality-orchestrator.md

```markdown
## Pipeline Initialization

Before starting the quality pipeline:

1. Initialize pipeline state file (`.claude/pipeline-state.json`)
2. Set all steps to "pending" status
3. Record pipeline start time

This ensures the validation hook can track progress.

Reference `.claude/lib/pipeline-state-utilities.md` for state file format.
```

**Validation**: ✅ State file initialized properly

---

## 📁 Files to Create

```
.claude/lib/
├── schemas/
│   └── pipeline-state.json           [NEW]
└── pipeline-state-utilities.md       [NEW]
```

---

## ✏️ Files to Modify

```
.claude/hooks/
└── validate-quality.sh               [REPLACE - Step 3]

.claude/skills/
├── validate-requirements/SKILL.md    [MODIFY - Step 4]
├── generate-output/SKILL.md          [MODIFY - Step 4]
├── format-standardize/SKILL.md       [MODIFY - Step 4]
└── quality-verify/SKILL.md           [MODIFY - Step 4]

.claude/agents/
└── quality-orchestrator.md           [MODIFY - Step 5]
```

---

## 🧪 Testing & Validation

### Verify Schema is Valid

```bash
# Check schema JSON is valid
cat .claude/lib/schemas/pipeline-state.json | jq .
# Expected: No errors, valid JSON
```

### Verify Hook Can Read State

```bash
# Test hook with sample state file
./.claude/hooks/validate-quality.sh
# Expected: No errors, reports current status
```

### Verify Hook Correctly Validates States

Create a test state file:
```json
{
  "currentRun": {
    "steps": {
      "validation": { "status": "completed" },
      "generation": { "status": "completed" },
      "formatting": { "status": "completed" },
      "verification": { "status": "completed" }
    }
  }
}
```

Run hook:
```bash
./.claude/hooks/validate-quality.sh
# Expected: "✓ Pipeline complete: All steps passed validation"
```

---

## 🔄 What's Next

After Structured Pipeline State is implemented:

1. **StandardsRepository** ✓
2. **ProjectTypeRegistry** ✓
3. **StructuredPipelineState** ✓
4. **Communication Style** (next)

The three abstractions work together to create a clean, maintainable system.

---

**Status**: Ready for implementation
**Estimated Time**: 45-60 minutes
**Complexity**: Medium (hook replacement, skill updates)

Created: 2025-11-07
Branch: dev
