# ProjectTypeRegistry

A centralized registry of all available project types in the High-Quality Builder system.

## Purpose

The registry is the single source of truth for project type information. Instead of hardcoding project types in agents and commands, all components read from this registry. This eliminates duplication and makes it trivial to add, remove, or modify project types.

## Registry Structure

The registry is stored in `.claude/lib/schemas/project-type-registry.json` and contains:

```json
{
  "projectTypes": [
    {
      "id": "code-features",           // Unique identifier (kebab-case)
      "name": "Code Features",         // Human-readable name
      "description": "...",            // What this type is for
      "keywords": [...],               // Keywords for detection
      "defaultTemplate": "...",        // Path to default standards
      "isActive": true                 // Whether this type is available
    },
    // ... more project types
  ]
}
```

## Available Project Types

The system currently supports 5 core project types:

1. **Code Features** (`code-features`)
   - Writing new functions, components, modules, and APIs
   - Examples: React component, API endpoint, utility function, class

2. **Documentation** (`documentation`)
   - Writing docs, guides, tutorials, specifications, and README files
   - Examples: API docs, user guide, implementation guide, architecture docs

3. **Refactoring** (`refactoring`)
   - Improving existing code structure, readability, and performance
   - Examples: Simplify complex function, rename variables, extract methods

4. **Test Suite** (`test-suite`)
   - Writing automated tests, test frameworks, and testing infrastructure
   - Examples: Unit tests, integration tests, E2E tests, test coverage

5. **Content Creation** (`content-creation`)
   - Writing articles, tutorials, blog posts, guides, and educational content
   - Examples: Blog post, tutorial, technical article, educational material

## Using the Registry

### In Agents

When asking the user about their project type:

```markdown
Load all active project types from the registry and present them clearly to the user.

Get all active project types:
const registry = projectTypeRegistry.getActiveTypes()
// Returns: [
//   { id: 'code-features', name: 'Code Features', description: '...', ... },
//   { id: 'documentation', name: 'Documentation', description: '...', ... },
//   ...
// ]

Present these options to the user in a clear, inviting format.
```

### In Standards Definer

When interviewing for project type selection:

```markdown
Use the registry to:
1. Get all project type options
2. Validate user's selection
3. Retrieve default template for the chosen type

const types = projectTypeRegistry.getActiveTypes()
// Let user choose from validated list
const typeInfo = projectTypeRegistry.getType(selectedType)
const template = standardsRepository.getDefaultTemplate(typeInfo.id)
```

### In Other Components

When you need to validate or access project type information:

```javascript
// Validate a project type
if (projectTypeRegistry.exists(projectType)) {
  // Valid type - proceed
} else {
  // Invalid type - ask user to choose again
}

// Get detailed type metadata
const typeInfo = projectTypeRegistry.getType(projectType)
// Returns: { id, name, description, keywords, defaultTemplate, isActive }

// Use the metadata
const defaultTemplate = typeInfo.defaultTemplate
```

## API Methods

### getActiveTypes()

Returns all active (enabled) project types.

**Returns**:
- Array of project type objects with `id`, `name`, `description`, `keywords`, `defaultTemplate`, `isActive`

**Example**:
```javascript
const types = projectTypeRegistry.getActiveTypes()
types.forEach(type => {
  console.log(`${type.id}: ${type.name}`)
})
// Output:
// code-features: Code Features
// documentation: Documentation
// refactoring: Refactoring
// test-suite: Test Suite
// content-creation: Content Creation
```

### getAllTypes()

Returns all project types (including inactive ones).

**Returns**:
- Array of all project type objects

**Example**:
```javascript
const allTypes = projectTypeRegistry.getAllTypes()
// Useful for admin/diagnostic purposes
```

### getType(id)

Get complete metadata for a specific project type.

**Parameters**:
- `id` (string): Project type ID (e.g., "code-features")

**Returns**:
- Project type object if found, or null if not found

**Example**:
```javascript
const typeInfo = projectTypeRegistry.getType('code-features')
// Returns:
// {
//   id: 'code-features',
//   name: 'Code Features',
//   description: 'Writing new functions, components, modules, and APIs...',
//   keywords: ['component', 'function', 'module', 'api', ...],
//   defaultTemplate: 'standards/templates/code-features.json',
//   isActive: true
// }
```

### exists(id)

Check if a project type exists and is active.

**Parameters**:
- `id` (string): Project type ID

**Returns**:
- true if the project type exists and is active
- false otherwise

**Example**:
```javascript
if (projectTypeRegistry.exists('code-features')) {
  // Project type is valid
  const typeInfo = projectTypeRegistry.getType('code-features')
} else {
  // Project type doesn't exist - ask user again
  const validTypes = projectTypeRegistry.getActiveTypes()
}
```

## Keywords for Detection

Each project type has keywords that help detect the user's intent. For example:

- User says "Create a React component" → matches `code-features` (keyword: "component")
- User says "Write API documentation" → matches `documentation` (keyword: "api-docs")
- User says "Improve this function" → matches `refactoring` (keyword: "improve")
- User says "Write unit tests" → matches `test-suite` (keyword: "test")
- User says "Write a blog post" → matches `content-creation` (keyword: "blog")

## Adding New Project Types

To add a new project type:

1. Edit `.claude/lib/schemas/project-type-registry.json`
2. Add a new object to the `projectTypes` array with all required fields
3. Create corresponding template in `standards/templates/{id}.json` if needed
4. All agents and commands automatically see the new type

Example: Adding a "Database Migration" project type:

```json
{
  "id": "database-migration",
  "name": "Database Migration",
  "description": "Writing database schema changes, migrations, and DDL scripts",
  "keywords": ["database", "migration", "schema", "ddl", "sql"],
  "defaultTemplate": "standards/templates/database-migration.json",
  "isActive": true
}
```

## Implementation Notes

- **Single Source of Truth**: All project type information comes from this registry
- **Extensible**: Easy to add new project types without modifying agents or commands
- **Validated**: Project type IDs follow kebab-case naming convention
- **Structured**: Each type has consistent metadata (id, name, description, keywords, etc.)
- **Discoverable**: Components can query available types programmatically

## Future Improvements

- Type detection based on keywords and user input
- Type categorization (frontend, backend, documentation, etc.)
- Type-specific configurations and settings
- Disabled types (isActive=false) for deprecation
