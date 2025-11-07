# Task: Implement StandardsRepository Abstraction

## 🎯 Overview

We're creating a centralized **StandardsRepository** — a single pattern for all standards access throughout the system. Right now, 7+ files directly access the filesystem for standards, creating duplication and making the system fragile. This task establishes one reliable interface that everything will use.

**Why it matters**:
- Eliminates DRY violations in standards access
- Makes the system easier to test
- Enables future improvements (caching, database migration, validation)
- Reduces coupling between components and file storage

**What it solves**:
- DRY violations #2 and #3 (standards access scattered everywhere)
- Lack of validation when loading standards
- No caching or performance optimization opportunity

---

## 🎯 Goals

- [x] Create standards access interface documentation
- [x] Create standards JSON schema for validation
- [ ] Update all components to use the repository pattern
- [ ] Test that all components work with new pattern
- [ ] Verify standards are properly validated on load

---

## 📖 Current State

### How Standards Are Accessed Now

**Problem**: Each component re-implements standards loading

**Examples from codebase**:

**Project Analyzer** (agents/project-analyzer.md):
```markdown
## Standards Matching
1. Check if standards exist in `standards/standards.json`
2. If YES: Load and display their saved standards
3. If NO: Offer the default template
```
→ Direct file path reference, no validation

**Standards Definer** (agents/standards-definer.md):
```markdown
## Saving Standards
Save the structured standards to the standards file:
- Location: `standards/standards.json`
- Format: JSON with project type as key
```
→ Direct file I/O, no schema validation

**Quality Orchestrator** (agents/quality-orchestrator.md):
```markdown
Load their saved standards for that project type from the standards file
```
→ Vague, no detail on how or where

**All Skills**: Reference standards indirectly through context

### Problems with Current Approach

1. **No Validation**: Standards could be malformed JSON or missing required fields
2. **No Error Handling**: If file doesn't exist or is corrupt, behavior is undefined
3. **Tight Coupling**: Components know file paths and JSON structure
4. **No Caching**: Every access reads from disk
5. **Inconsistent Patterns**: Each component does it differently
6. **Hard to Test**: Can't mock standards access easily

---

## 🏗️ New Design: StandardsRepository Pattern

### Concept

A single interface that all components use to:
- ✅ Load standards with validation
- ✅ Save standards with validation
- ✅ Check if standards exist
- ✅ List available standards
- ✅ Access defaults
- ✅ Handle errors gracefully

### Interface

Components will call methods like:

```javascript
// Load standards for a project type
const standards = standardsRepository.getStandards('code-features')

// Check if standards exist
if (standardsRepository.exists('code-features')) { ... }

// Get all available project types
const types = standardsRepository.listProjectTypes()

// Save new standards
standardsRepository.setStandards('code-features', standardsObject)

// Get default template
const template = standardsRepository.getDefaultTemplate('code-features')
```

### Architecture

```
Components (Agents, Skills, Commands)
         ↓
StandardsRepository (interface)
         ↓
File I/O (standards/standards.json)
```

The repository handles all the details. Components never touch the file system directly.

### Benefits

- **Single Source of Truth**: One place that knows about standards storage
- **Validation**: Standards are validated on load and save
- **Error Handling**: Consistent error messages
- **Testability**: Can mock the repository
- **Future-Proof**: Can change storage (e.g., to database) without affecting components

---

## 📋 Implementation Steps

### Step 1: Create Standards Schema

**What**: Define the JSON schema that standards must follow

**Why**: Enables validation when loading/saving standards

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/lib/schemas/standards-schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Project Standards Schema",
  "type": "object",
  "additionalProperties": {
    "type": "object",
    "required": ["projectType", "description", "qualityCriteria"],
    "properties": {
      "projectType": {
        "type": "string",
        "description": "Unique identifier for project type (kebab-case)",
        "pattern": "^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"
      },
      "description": {
        "type": "string",
        "description": "Human-readable description of this project type"
      },
      "principles": {
        "type": "array",
        "description": "Core development principles for this type",
        "items": { "type": "string" }
      },
      "validationRules": {
        "type": "object",
        "properties": {
          "input": {
            "type": "array",
            "description": "Validation rules for input requirements",
            "items": { "type": "string" }
          }
        }
      },
      "qualityCriteria": {
        "type": "object",
        "description": "Quality dimensions and their definitions",
        "properties": {
          "completeness": { "type": "string" },
          "correctness": { "type": "string" },
          "consistency": { "type": "string" },
          "performance": { "type": "string" },
          "security": { "type": "string" },
          "maintainability": { "type": "string" }
        }
      },
      "commonPatterns": {
        "type": "array",
        "description": "Patterns commonly used in this project type",
        "items": { "type": "string" }
      },
      "antiPatterns": {
        "type": "array",
        "description": "Patterns to avoid in this project type",
        "items": { "type": "string" }
      }
    }
  }
}
```

**Validation**: ✅ Schema file created and valid JSON

---

### Step 2: Create StandardsRepository Interface Documentation

**What**: Document how the repository works and how to use it

**Why**: Makes it clear to agents/skills what methods are available

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/lib/standards-repository.md`:

```markdown
# StandardsRepository Interface

A centralized interface for all standards access throughout HQB.

## Purpose

Instead of scattered file I/O across agents and skills, everything goes through this repository. It handles:
- Loading standards from `standards/standards.json`
- Saving standards with validation
- Checking existence
- Providing defaults
- Error handling

## Available Methods

### getStandards(projectType)

Load standards for a specific project type.

**Parameters**:
- `projectType` (string): Project type ID (e.g., "code-features")

**Returns**:
- Standards object if found
- null if not found (no error, just null)

**Throws**:
- Error if file is corrupted or invalid JSON
- Error if standards fail schema validation

**Example**:
```
const standards = standardsRepository.getStandards('code-features')
if (!standards) {
  // No custom standards found, use default template instead
}
```

---

### setStandards(projectType, standards)

Save standards for a project type.

**Parameters**:
- `projectType` (string): Project type ID
- `standards` (object): Standards object to save

**Returns**:
- Success message

**Throws**:
- Error if standards fail schema validation
- Error if file write fails

**Example**:
```
standardsRepository.setStandards('code-features', {
  projectType: 'code-features',
  description: '...',
  qualityCriteria: { ... }
})
```

---

### exists(projectType)

Check if standards exist for a project type.

**Parameters**:
- `projectType` (string): Project type ID

**Returns**:
- true if custom standards exist
- false otherwise

**Example**:
```
if (standardsRepository.exists('code-features')) {
  // Use custom standards
} else {
  // Use default template
}
```

---

### listProjectTypes()

Get all project types that have custom standards.

**Returns**:
- Array of project type IDs

**Example**:
```
const types = standardsRepository.listProjectTypes()
// Returns: ['code-features', 'documentation', ...]
```

---

### getDefaultTemplate(projectType)

Get the default template for a project type.

**Parameters**:
- `projectType` (string): Project type ID

**Returns**:
- Default template object
- null if no default exists

**Example**:
```
const template = standardsRepository.getDefaultTemplate('code-features')
// Use template as starting point for new standards
```

---

## Usage in Components

### In Agents

```markdown
## How to Use

The StandardsRepository provides a clean interface for standards access:

```
const standards = standardsRepository.getStandards(projectType)
if (!standards) {
  // No custom standards, offer default template
  const template = standardsRepository.getDefaultTemplate(projectType)
}
```

This replaces direct file references like `standards/standards.json`.

---

### In Skills

Skills receive standards through the pipeline context, so they don't call the repository directly. However, they can access it if needed:

```
if (standardsRepository.exists(context.projectType)) {
  // Adapt approach based on custom standards
}
```

---

## Error Handling

All repository methods handle errors gracefully:

```
try {
  const standards = standardsRepository.getStandards(projectType)
} catch (error) {
  // Handle corrupted file, invalid JSON, etc.
  logger.error(`Failed to load standards: ${error.message}`)
}
```

---

## Implementation Notes

- File location: `standards/standards.json`
- Schema validation: All standards validated against `standards-schema.json`
- Default templates: Located in `standards/templates/`
- No caching in this version (can be added later)

---
```

**Validation**: ✅ Interface documentation created

---

### Step 3: Update Project Analyzer Agent

**What**: Modify project-analyzer.md to use StandardsRepository

**Why**: Eliminates direct file access from agents

**Current problematic code** (agents/project-analyzer.md lines 48-54):
```markdown
## Standards Matching
Once you identify the project type:
1. Check if standards exist in `standards/standards.json`
2. If YES: Load and display their saved standards
3. If NO: Offer the default template
```

**Replacement**:
```markdown
## Standards Matching
Once you identify the project type:
1. Use StandardsRepository.exists(projectType) to check if custom standards exist
2. If YES: Load via StandardsRepository.getStandards(projectType) and display
3. If NO: Use StandardsRepository.getDefaultTemplate(projectType)

See `.claude/lib/standards-repository.md` for interface details.
```

**Validation**: ✅ Agent references repository pattern

---

### Step 4: Update Standards Definer Agent

**Current problematic code** (agents/standards-definer.md lines 99-103):
```markdown
## Saving Standards
Save the structured standards to the standards file:
- Location: `standards/standards.json`
```

**Replacement**:
```markdown
## Saving Standards
Use StandardsRepository.setStandards(projectType, standards) to save.

The repository automatically:
- Validates against the standards schema
- Creates `standards/standards.json` if needed
- Saves with proper JSON formatting

See `.claude/lib/standards-repository.md` for interface details.
```

**Validation**: ✅ Agent uses repository for saves

---

### Step 5: Update Quality Orchestrator Agent

**Current vague reference** (agents/quality-orchestrator.md):
```markdown
Load their saved standards for that project type from the standards file
```

**Replacement**:
```markdown
Load standards using StandardsRepository.getStandards(projectType).
If none exist, use StandardsRepository.getDefaultTemplate(projectType).

See `.claude/lib/standards-repository.md` for available methods.
```

**Validation**: ✅ Agent explicitly references repository

---

### Step 6: Add Repository Reference to Skills

**What**: Update all 4 skills to reference the repository

**Why**: Makes it clear how standards are accessed if needed

**Current state**: Skills reference standards indirectly

**Update in each skill** (validate-requirements, generate-output, format-standardize, quality-verify):

Add this section under "Using Standards":

```markdown
## Using Standards

Standards are provided through the pipeline context. If you need to access standards directly:

```
const standards = standardsRepository.getStandards(context.projectType)
```

See `.claude/lib/standards-repository.md` for available methods.
```

**Validation**: ✅ All skills reference repository docs

---

## 📁 Files to Create

```
.claude/lib/
├── schemas/
│   └── standards-schema.json          [NEW]
└── standards-repository.md            [NEW]
```

**Contents**: See Steps 1-2 above

---

## ✏️ Files to Modify

```
.claude/agents/
├── project-analyzer.md                [MODIFY - Step 3]
├── standards-definer.md               [MODIFY - Step 4]
└── quality-orchestrator.md            [MODIFY - Step 5]

.claude/skills/
├── validate-requirements/SKILL.md     [MODIFY - Step 6]
├── generate-output/SKILL.md           [MODIFY - Step 6]
├── format-standardize/SKILL.md        [MODIFY - Step 6]
└── quality-verify/SKILL.md            [MODIFY - Step 6]
```

---

## 🧪 Testing & Validation

### Verify Schema is Valid

```bash
# Schema should be valid JSON
cat .claude/lib/schemas/standards-schema.json | jq .
# Expected: No errors, valid JSON output
```

### Verify Interface Documentation

```bash
# Check that interface doc exists and is readable
cat .claude/lib/standards-repository.md | head -20
# Expected: Clear interface documentation
```

### Verify All References Updated

```bash
# Check that agents reference the repository
grep -r "StandardsRepository" .claude/agents/
# Expected: References in all 3 agent files

# Check that skills reference the repository
grep -r "StandardsRepository" .claude/skills/
# Expected: References in all 4 skill files
```

### Verify Old File References Are Removed

```bash
# Check for direct file references (should be minimal)
grep -r "standards/standards.json" .claude/
# Expected: Only in StandardsRepository docs, not in agents/skills
```

---

## 🔄 What's Next

After StandardsRepository is implemented:

1. **ProjectTypeRegistry** task implements the registry pattern
2. **Structured Pipeline State** task improves hook validation
3. All three abstractions work together to create a clean, DRY system

---

**Status**: Ready for implementation
**Estimated Time**: 30-45 minutes
**Complexity**: Medium (mostly documentation and pattern establishment)

Created: 2025-11-07
Branch: dev
