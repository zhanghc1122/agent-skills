# Wiki Manager — AI Agent Knowledge Base Tool

Manage personal knowledge bases (wikis) with AI-powered ingestion, search, graph analysis, and quality checks.

## Scripts Location

All scripts are in `~/.claude/skills/wiki-manager/scripts/`
All prompt templates are in `~/.claude/skills/wiki-manager/reference.md`

## Available Commands

### Initialize a Wiki Project
```bash
python ~/.claude/skills/wiki-manager/scripts/wiki-init.py <name> [--template general|research|reading|personal|business]
```

### Search the Wiki
```bash
python ~/.claude/skills/wiki-manager/scripts/wiki-search.py <project> "<query>"
```

### Ingest a Document
1. Read source document + wiki context (schema.md, purpose.md, wiki/index.md, wiki/overview.md)
2. LLM Analysis → structured analysis of entities, concepts, connections (see reference.md Analysis Prompt)
3. LLM Generation → FILE blocks with wiki pages (see reference.md Generation Prompt)
4. Parse FILE blocks: `python scripts/wiki-parse.py --parse-files < output.txt`
5. Write files (merge if existing: `python scripts/wiki-merge.py existing.md new.md`)
6. Update wiki/index.md and wiki/log.md
7. Optionally vectorize: `python scripts/wiki-chunk.py <project> wiki/entities/page.md`

### Knowledge Graph
```bash
python ~/.claude/skills/wiki-manager/scripts/wiki-graph.py <project>
```

### Quality Check
```bash
python ~/.claude/skills/wiki-manager/scripts/wiki-lint.py <project>
```

### Deep Research
1. web_search for 2-3 queries
2. LLM synthesis with Deep Research Prompt (see reference.md)
3. Save to wiki/queries/research-{slug}-{date}.md

## Rules
- All wiki pages must have YAML frontmatter (type, title, created, updated)
- Use [[wikilink]] in body text for cross-references
- related field uses bare slugs: `related: [gpt-4, transformers]`
- Merge existing pages, don't overwrite
- Check wiki/index.md before creating new pages to avoid duplicates
