# StandardsRepository Interface

A centralized interface for all standards access throughout the High-Quality Builder system.

## Purpose

Instead of scattered file I/O across agents and skills, everything goes through this repository. It provides a clean, validated interface for:
- Loading standards from `standards/standards.json`
- Saving standards with validation
- Checking if standards exist
- Providing default templates
- Consistent error handling

## Available Methods

### getStandards(projectType)

Load standards for a specific project type.

**Parameters**:
- `projectType` (string): Project type ID (e.g., "code-features")

**Returns**:
- Standards object if custom standards exist
- null if not found (no error, just null)

**Throws**:
- Error if file is corrupted or invalid JSON
- Error if standards fail schema validation

**Example**:
```javascript
const standards = standardsRepository.getStandards('code-features')
if (!standards) {
  // No custom standards found, use default template instead
  const template = standardsRepository.getDefaultTemplate('code-features')
}
```

### setStandards(projectType, standards)

Save standards for a project type.

**Parameters**:
- `projectType` (string): Project type ID
- `standards` (object): Standards object to save

**Returns**:
- Success confirmation

**Throws**:
- Error if standards fail schema validation
- Error if file write fails

**Example**:
```javascript
standardsRepository.setStandards('code-features', {
  projectType: 'code-features',
  description: 'Standards for implementing code features',
  principles: ['DRY', 'SOLID', 'Test-driven development'],
  qualityCriteria: { /* ... */ }
})
```

### exists(projectType)

Check if custom standards exist for a project type.

**Parameters**:
- `projectType` (string): Project type ID

**Returns**:
- true if custom standards exist
- false otherwise

**Example**:
```javascript
if (standardsRepository.exists('code-features')) {
  // Use custom standards
  const standards = standardsRepository.getStandards('code-features')
} else {
  // Use default template
  const template = standardsRepository.getDefaultTemplate('code-features')
}
```

### listProjectTypes()

Get all project types that have custom standards.

**Returns**:
- Array of project type IDs with custom standards

**Example**:
```javascript
const customTypes = standardsRepository.listProjectTypes()
// Returns: ['code-features', 'documentation', ...]
```

### getDefaultTemplate(projectType)

Get the default template for a project type.

**Parameters**:
- `projectType` (string): Project type ID

**Returns**:
- Default template object if available
- null if no default template exists

**Example**:
```javascript
const template = standardsRepository.getDefaultTemplate('code-features')
if (template) {
  // Use template as starting point for new standards
}
```

## Usage Patterns

### In Agents

Agents that need to access standards should use the repository pattern:

```javascript
// Check if custom standards exist
if (standardsRepository.exists(projectType)) {
  const standards = standardsRepository.getStandards(projectType)
  // Use custom standards
} else {
  const template = standardsRepository.getDefaultTemplate(projectType)
  // Use default template as fallback
}

// When saving standards
standardsRepository.setStandards(projectType, standardsObject)
```

This replaces direct file references like `standards/standards.json`.

### In Skills

Skills receive standards through the pipeline context. They can access the repository if they need to:

```javascript
const standards = standardsRepository.getStandards(context.projectType)
if (standards) {
  // Adapt approach based on custom standards
}
```

## Schema Validation

All standards are validated against `.claude/lib/schemas/standards-schema.json` when loaded or saved. This ensures:
- Required fields are present (projectType, description, qualityCriteria)
- Project types follow naming conventions (kebab-case)
- All quality criteria are properly defined

See `standards-schema.json` for complete validation rules.

## Error Handling

All repository methods handle errors gracefully:

```javascript
try {
  const standards = standardsRepository.getStandards(projectType)
} catch (error) {
  // Handle corrupted file, invalid JSON, schema validation errors
  logger.error(`Failed to load standards for ${projectType}: ${error.message}`)

  // Fallback to default template
  const template = standardsRepository.getDefaultTemplate(projectType)
}
```

## Implementation Details

- **File location**: `standards/standards.json`
- **Schema validation**: `.claude/lib/schemas/standards-schema.json`
- **Default templates**: `standards/templates/{projectType}.json`
- **Caching**: No caching in this version (can be optimized later)
- **Concurrency**: Not thread-safe (file-based implementation)

## Future Improvements

This interface is designed to support future enhancements without breaking existing code:
- Caching for performance optimization
- Database storage instead of JSON files
- Remote standards repository
- Version control for standards changes
