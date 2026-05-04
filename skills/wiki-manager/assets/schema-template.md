# Wiki Page Types & Schema

This document defines the wiki structure, page types, naming conventions, and frontmatter fields.

## Directory Layout

```
{project}/
  raw/sources/          -- Original source documents (PDF, DOCX, MD, etc.)
  wiki/
    entities/           -- Named things: people, organizations, products, models
    concepts/           -- Ideas, techniques, phenomena, theories
    sources/            -- Source summary pages (one per ingested document)
    queries/            -- Open questions and research results
    comparisons/        -- Side-by-side analyses
    synthesis/          -- Cross-cutting summaries
    index.md            -- Master index of all wiki pages
    overview.md         -- Project overview and scope
    log.md              -- Activity log
  schema.md             -- This file
  purpose.md            -- Project purpose and goals
```

## Page Types

### entity
Named things with distinct identity: people, organizations, products, datasets, tools, models.
- Directory: `wiki/entities/`
- Filename: match the official/common name in kebab-case (e.g., `gpt-4.md`, `openai.md`)

### concept
Ideas, techniques, methods, phenomena, theories.
- Directory: `wiki/concepts/`
- Filename: descriptive noun phrase in kebab-case (e.g., `chain-of-thought.md`, `retrieval-augmented-generation.md`)

### source
Summary of an ingested source document.
- Directory: `wiki/sources/`
- Filename: derived from source file (e.g., `attention-is-all-you-need.md`)

### query
Open questions, research topics, investigation results.
- Directory: `wiki/queries/`
- Filename: `research-{slug}-{date}.md` for deep research, or `{question-slug}.md`

### comparison
Side-by-side analysis of two or more entities/concepts.
- Directory: `wiki/comparisons/`
- Filename: `{a}-vs-{b}.md`

### synthesis
Cross-cutting summaries that integrate multiple pages.
- Directory: `wiki/synthesis/`
- Filename: descriptive kebab-case

### overview
Project-level overview page.
- File: `wiki/overview.md`
- Single page per project

## Frontmatter Fields

### Required (all types)

| Field | Type | Description |
|-------|------|-------------|
| type | string | Page type: entity, concept, source, query, comparison, synthesis, overview |
| title | string | Human-readable page title |
| created | date | Creation date (YYYY-MM-DD) |
| updated | date | Last update date (YYYY-MM-DD) |

### Optional (all types)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| tags | string[] | [] | Categorization tags |
| related | string[] | [] | Related page slugs (bare slug, no [[...]]) |
| sources | string[] | [] | Source filenames this page derives from |

### Type-specific fields

| Type | Field | Description |
|------|-------|-------------|
| source | origin | Where the source came from (web-clip, file-import, deep-research) |
| source | url | Original URL (for web clips) |
| query | status | open, answered, partially-answered |

## Naming Conventions

1. **File names**: kebab-case, `.md` extension
2. **Wikilinks**: `[[page-slug]]` or `[[page-slug|Display Text]]`
3. **Related field**: bare slugs without `[[]]`, e.g., `related: [gpt-4, transformers]`
4. **Sources field**: original filename with extension, e.g., `sources: ["attention-is-all-you-need.pdf"]`

## Cross-Referencing Rules

- Use `[[wikilink]]` in body text to link to other wiki pages
- Case-insensitive matching: `[[GPT-4]]` matches `gpt-4.md`
- Hyphen/space normalization: `[[chain of thought]]` matches `chain-of-thought.md`
- The `related` frontmatter field supplements wikilinks for important connections
