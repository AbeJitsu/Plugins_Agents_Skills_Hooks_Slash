# Task: Implement ProjectTypeRegistry

## 🎯 Overview

We're creating a **ProjectTypeRegistry** — a single, authoritative source for all project type definitions. Right now, project types are hardcoded in 7+ files (agents, templates, commands), creating the most severe DRY violation in the system. This task consolidates them into one place.

**Why it matters**:
- Fixes the worst DRY violation (project types duplicated everywhere)
- Makes it trivial to add/remove project types (one file, not seven)
- Enables future features (project type detection, validation)
- Creates a data contract that all components can rely on

**What it solves**:
- DRY violation #1 (Critical severity)
- Orthogonality issue #5 (missing abstraction)

---

## 🎯 Goals

- [x] Create project type registry JSON file
- [x] Document the registry structure and how to use it
- [ ] Update project-analyzer to read from registry
- [ ] Remove hardcoded project types from all other files
- [ ] Verify system detects and uses all project types

---

## 📖 Current State

### How Project Types Are Defined Now

**Problem**: Project types duplicated in 7+ locations

**Example 1 - Hardcoded in agent** (agents/project-analyzer.md lines 18-34):
```markdown
1. **Code Features** - Writing new functions, components, modules
2. **Documentation** - Writing docs, guides, tutorials, specs
3. **Refactoring** - Improving existing code structure
4. **Test Suite** - Writing automated tests
5. **Content Creation** - Writing articles, tutorials, blog posts
```

**Example 2 - In command help** (commands/hqb.md):
```markdown
## Available Project Types
...lists project types again...
```

**Example 3 - In template filenames** (standards/templates/):
```
code-features.json
documentation.json
refactoring.json
test-suite.json
content-creation.json
```

**Example 4 - In standards-definer** (agents/standards-definer.md):
```markdown
What type of project are you working on?
...lists types again...
```

**Example 5 - In template content** (standards/templates/code-features.json line 2):
```json
"projectType": "code-features"
```

### Problems with Current Approach

1. **Duplication**: Same information in 7+ locations
2. **Inconsistency**: Slight variations in naming/description
3. **No Validation**: System can't validate if a project type is valid
4. **Hard to Extend**: Adding a new type requires 7+ file edits
5. **No Single Source of Truth**: Can't tell which is authoritative
6. **Tight Coupling**: Agents depend on hardcoded lists

---

## 🏗️ New Design: ProjectTypeRegistry

### Concept

One JSON file that defines:
- All available project types
- Metadata for each type
- Which templates/standards are available
- How to detect each type

### Registry Structure

```json
{
  "projectTypes": [
    {
      "id": "code-features",
      "name": "Code Features",
      "description": "Writing new functions, components, modules",
      "keywords": ["component", "function", "module", "api"],
      "defaultTemplate": "standards/templates/code-features.json",
      "isActive": true
    },
    {
      "id": "documentation",
      "name": "Documentation",
      "description": "Writing docs, guides, tutorials, specs",
      "keywords": ["docs", "guide", "tutorial", "specification"],
      "defaultTemplate": "standards/templates/documentation.json",
      "isActive": true
    },
    ...
  ]
}
```

### Benefits

- **Consistent Data**: One source for all project types
- **Extensible**: Add new types by adding one object
- **Structured**: Enables type validation and detection
- **Discoverable**: Can query available types programmatically
- **Maintainable**: Change description in one place

---

## 📋 Implementation Steps

### Step 1: Create Project Type Registry

**What**: Define all project types in one JSON file

**Why**: Creates single source of truth

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/lib/schemas/project-type-registry.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Project Type Registry",
  "description": "Authoritative list of all project types supported by HQB",
  "type": "object",
  "required": ["projectTypes"],
  "properties": {
    "projectTypes": {
      "type": "array",
      "description": "Array of available project types",
      "items": {
        "type": "object",
        "required": ["id", "name", "description", "keywords", "defaultTemplate", "isActive"],
        "properties": {
          "id": {
            "type": "string",
            "description": "Unique project type identifier (kebab-case)",
            "pattern": "^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"
          },
          "name": {
            "type": "string",
            "description": "Human-readable project type name (Title Case)"
          },
          "description": {
            "type": "string",
            "description": "Clear description of what this project type covers"
          },
          "keywords": {
            "type": "array",
            "description": "Keywords to help detect this project type",
            "items": { "type": "string" },
            "minItems": 1
          },
          "defaultTemplate": {
            "type": "string",
            "description": "Path to default standards template for this type"
          },
          "isActive": {
            "type": "boolean",
            "description": "Whether this project type is currently available"
          }
        }
      },
      "minItems": 1
    }
  }
}
```

**Registry content**:

```json
{
  "projectTypes": [
    {
      "id": "code-features",
      "name": "Code Features",
      "description": "Writing new functions, components, modules, and APIs",
      "keywords": ["component", "function", "module", "api", "feature", "class", "method"],
      "defaultTemplate": "standards/templates/code-features.json",
      "isActive": true
    },
    {
      "id": "documentation",
      "name": "Documentation",
      "description": "Writing docs, guides, tutorials, specifications, and README files",
      "keywords": ["docs", "documentation", "guide", "tutorial", "specification", "readme", "manual"],
      "defaultTemplate": "standards/templates/documentation.json",
      "isActive": true
    },
    {
      "id": "refactoring",
      "name": "Refactoring",
      "description": "Improving existing code structure, readability, and performance",
      "keywords": ["refactor", "refactoring", "improve", "clean", "optimize", "restructure"],
      "defaultTemplate": "standards/templates/refactoring.json",
      "isActive": true
    },
    {
      "id": "test-suite",
      "name": "Test Suite",
      "description": "Writing automated tests, test frameworks, and testing infrastructure",
      "keywords": ["test", "testing", "unit test", "integration test", "spec", "jest", "pytest", "mocha"],
      "defaultTemplate": "standards/templates/test-suite.json",
      "isActive": true
    },
    {
      "id": "content-creation",
      "name": "Content Creation",
      "description": "Writing articles, tutorials, blog posts, guides, and educational content",
      "keywords": ["article", "blog", "tutorial", "content", "post", "guide", "educational"],
      "defaultTemplate": "standards/templates/content-creation.json",
      "isActive": true
    }
  ]
}
```

**Validation**: ✅ Registry file created and valid

---

### Step 2: Create Registry Usage Documentation

**What**: Document how to use the registry

**Why**: Makes it clear to agents how to access project type information

**How**:

Create `/Users/abereyes/Projects/Templates/HQB/.claude/lib/project-type-registry.md`:

```markdown
# ProjectTypeRegistry

A centralized registry of all available project types in HQB.

## Purpose

The registry is the single source of truth for project type information. Instead of hardcoding project types in agents, all components read from this registry.

## Registry Structure

The registry is stored in `lib/schemas/project-type-registry.json` and contains:

```json
{
  "projectTypes": [
    {
      "id": "code-features",           // Unique identifier
      "name": "Code Features",          // Human-readable name
      "description": "...",             // What this type is for
      "keywords": [...],                // Keywords for detection
      "defaultTemplate": "...",         // Path to default standards
      "isActive": true                  // Whether this type is available
    },
    ...
  ]
}
```

## Using the Registry

### In Project Analyzer

When asking the user about their project type:

```markdown
The registry provides the authoritative list of project types.

Get all active project types:
```
const registry = projectTypeRegistry.getActiveTypes()
// Returns: [
//   { id: 'code-features', name: 'Code Features', description: '...' },
//   { id: 'documentation', name: 'Documentation', description: '...' },
//   ...
// ]
```

Present these options to the user clearly and invitingly.
```

---

### In Standards Definer

When interviewing for project type:

```markdown
Use the registry to:
1. Get all project type options
2. Validate user's selection
3. Retrieve default template

```
const types = projectTypeRegistry.getActiveTypes()
// Let user choose from validated list
const template = projectTypeRegistry.getTemplate(selectedType)
```
```

---

### In Other Agents

When you need to validate or access project type information:

```markdown
// Validate a project type
if (projectTypeRegistry.exists(projectType)) {
  // Valid type
} else {
  // Invalid type, ask user again
}

// Get type metadata
const typeInfo = projectTypeRegistry.getType(projectType)
// Returns: { id, name, description, keywords, defaultTemplate, isActive }
```
```

---

## API Methods

### getActiveTypes()
Returns all active (enabled) project types.

**Returns**:
- Array of project type objects

**Example**:
```
const types = projectTypeRegistry.getActiveTypes()
types.forEach(type => console.log(type.name))
// Output: Code Features, Documentation, Refactoring, Test Suite, Content Creation
```

---

### getAllTypes()
Returns all project types (including inactive).

**Returns**:
- Array of all project type objects

---

### getType(id)
Get metadata for a specific project type.

**Parameters**:
- `id` (string): Project type ID

**Returns**:
- Project type object, or null if not found

**Example**:
```
const typeInfo = projectTypeRegistry.getType('code-features')
// Returns:
// {
//   id: 'code-features',
//   name: 'Code Features',
//   description: '...',
//   keywords: [...],
//   defaultTemplate: '...',
//   isActive: true
// }
```

---

### exists(id)
Check if a project type exists.

**Parameters**:
- `id` (string): Project type ID

**Returns**:
- true if exists, false otherwise

---

### getTemplate(id)
Get the default standards template for a project type.

**Parameters**:
- `id` (string): Project type ID

**Returns**:
- Path to template file

**Example**:
```
const templatePath = projectTypeRegistry.getTemplate('code-features')
// Returns: 'standards/templates/code-features.json'
```

---

### detectType(userDescription)
(Future feature) Suggest a project type based on user's description.

**Parameters**:
- `userDescription` (string): User's project description

**Returns**:
- Suggested project type ID, or null if unclear

---

## Adding New Project Types

To add a new project type:

1. Add entry to `project-type-registry.json` with:
   - Unique `id`
   - Clear `name` and `description`
   - Relevant `keywords`
   - Path to `defaultTemplate`
   - `isActive: true`

2. Create corresponding template file: `standards/templates/{id}.json`

3. That's it! The new type is immediately available throughout the system.

**No other files need to change.**

---

## Implementation Notes

- Registry location: `lib/schemas/project-type-registry.json`
- Schema validation: Registry validates against JSON schema
- Active status: Set `isActive: false` to temporarily disable a type
- Keywords: Used for future type detection feature

---
```

**Validation**: ✅ Usage documentation created

---

### Step 3: Update Project Analyzer Agent

**What**: Modify project-analyzer.md to read from registry

**Why**: Eliminates hardcoded project type list from agent

**Current problematic code** (agents/project-analyzer.md lines 18-34):
```markdown
## Detecting Project Type

Ask the user to identify their project type:

1. **Code Features** - Writing new functions, components, modules
2. **Documentation** - Writing docs, guides, tutorials, specs
3. **Refactoring** - Improving existing code structure
4. **Test Suite** - Writing automated tests
5. **Content Creation** - Writing articles, tutorials, blog posts
```

**Replacement**:
```markdown
## Detecting Project Type

Ask the user to identify their project type from the registry:

Use `projectTypeRegistry.getActiveTypes()` to get the current list of project types.

Present each type with its name and description in a clear, inviting way:
- Clear labels
- Helpful descriptions
- Easy selection

The registry is the single source of truth, so you don't need to maintain a hardcoded list here.

See `.claude/lib/project-type-registry.md` for registry API details.
```

**Validation**: ✅ Agent references registry

---

### Step 4: Update Standards Definer Agent

**Current problematic code** (agents/standards-definer.md - interview section):
```markdown
What type of project are you working on?

1. Code Features
2. Documentation
3. Refactoring
4. Test Suite
5. Content Creation
```

**Replacement**:
```markdown
What type of project are you working on?

Use `projectTypeRegistry.getActiveTypes()` to get the current list.

For each option, show:
- The friendly name
- The description
- Clear selection method

Reference `.claude/lib/project-type-registry.md` for API details.
```

**Validation**: ✅ Agent uses registry for interview

---

### Step 5: Remove Hardcoded References from Other Files

**Check commands/define-standards.md**:
- If it mentions project types, update to reference registry

**Check commands/show-standards.md**:
- If it lists project types, update to reference registry

**Check agents/quality-orchestrator.md**:
- If it hardcodes project types, update to reference registry

**Validation**: ✅ No hardcoded project type lists remain

---

## 📁 Files to Create

```
.claude/lib/
├── schemas/
│   └── project-type-registry.json    [NEW]
└── project-type-registry.md          [NEW]
```

---

## ✏️ Files to Modify

```
.claude/agents/
├── project-analyzer.md               [MODIFY - Step 3]
├── standards-definer.md              [MODIFY - Step 4]
└── quality-orchestrator.md           [MODIFY if needed - Step 5]

.claude/commands/
├── define-standards.md               [MODIFY if needed - Step 5]
└── show-standards.md                 [MODIFY if needed - Step 5]
```

---

## 🧪 Testing & Validation

### Verify Registry is Valid

```bash
# Check registry JSON is valid
cat .claude/lib/schemas/project-type-registry.json | jq .
# Expected: No errors, valid JSON

# Count project types
cat .claude/lib/schemas/project-type-registry.json | jq '.projectTypes | length'
# Expected: 5
```

### Verify All Types Have Required Fields

```bash
# Check that all types have required properties
cat .claude/lib/schemas/project-type-registry.json | jq '.projectTypes[] | {id, name, description, keywords, defaultTemplate, isActive}' | head -20
# Expected: Clear, complete project type definitions
```

### Verify No Hardcoded Project Types Remain

```bash
# Search for hardcoded project type lists
grep -r "Code Features\|Documentation\|Refactoring" .claude/agents/ .claude/commands/
# Expected: Results only in project-analyzer.md (legacy)
#           and registry-related files, not scattered
```

### Verify Registry References

```bash
# Check agents reference the registry
grep -r "projectTypeRegistry" .claude/agents/
# Expected: References in project-analyzer, standards-definer
```

---

## 🔄 What's Next

After ProjectTypeRegistry is implemented:

1. **StandardsRepository** (already done) + **ProjectTypeRegistry** work together
2. **Structured Pipeline State** task improves hook validation
3. Together they create clean abstractions eliminating DRY violations

---

**Status**: Ready for implementation
**Estimated Time**: 30-40 minutes
**Complexity**: Medium (data centralization)

Created: 2025-11-07
Branch: dev
