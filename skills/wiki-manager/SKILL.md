---
name: wiki-manager
description: "Personal knowledge base (wiki) management — search, ingest, knowledge graph, quality check, deep research. Use when: (1) creating or managing a wiki/knowledge base, (2) searching wiki pages, (3) ingesting documents into wiki, (4) analyzing knowledge graph, (5) checking wiki quality, (6) deep research on a topic. Triggers: wiki, 知识库, 搜索wiki, 摄入文档, 知识图谱, 深度研究, wiki search, wiki ingest"
metadata:
  openclaw:
    emoji: "📚"
    requires:
      bins: ["python3"]
---

## Goal

Manage a personal knowledge base (wiki) with structured pages, cross-references, and AI-powered ingestion. All wiki projects are stored in `~/.hermes/wikis/` by default (Hermes) or `~/.openclaw/wikis/` (OpenClaw), with a format compatible with the llm_wiki desktop app.

## Scripts Location

Scripts are in the `scripts/` directory within this skill folder. Resolve the path based on your platform:

| Platform | Skill install path |
|----------|-------------------|
| Hermes | `~/.hermes/skills/wiki-manager/scripts/` |
| OpenClaw | `~/.openclaw/skills/wiki-manager/scripts/` |
| Claude Code | `~/.claude/skills/wiki-manager/scripts/` |

In examples below, replace `<SKILL_DIR>` with your platform's path.

## Core Operations

### 1. Initialize a Wiki Project

When the user wants to create a new knowledge base:

```bash
python <SKILL_DIR>/scripts/wiki-init.py <project-name> --template <general|research|reading|personal|business>
```

This creates the directory structure at the default wiki storage path with:
- `raw/sources/` — for original documents
- `wiki/entities/`, `wiki/concepts/`, `wiki/sources/`, etc. — for wiki pages
- `schema.md`, `purpose.md` — project metadata
- `.wiki/config.json` — project configuration

Templates add extra directories:
- **research**: methodology, findings, thesis
- **reading**: characters, themes, plot-threads, chapters
- **personal**: goals, habits, reflections, journal
- **business**: meetings, decisions, projects, stakeholders

### 2. Search the Wiki

When the user asks to find information in the wiki:

```bash
python <SKILL_DIR>/scripts/wiki-search.py <project-name> "<query>"
```

Returns JSON array of matching pages with title, path, snippet, and score.
Uses BM25 keyword scoring with CJK tokenization support.

### 3. Ingest a Document (Core Workflow)

When the user wants to add a document to the wiki, follow these steps:

**Step 1 — Read context**: Read the source document content, `schema.md`, `purpose.md`, `wiki/index.md`, and `wiki/overview.md` from the project.

**Step 2 — Analysis LLM call**: Send the source document to the LLM with the **Analysis Prompt** from `reference.md`. Temperature 0.1. The LLM analyzes key entities, concepts, arguments, connections to existing wiki, and contradictions.

**Step 3 — Generation LLM call**: Send the analysis + source content to the LLM with the **Generation Prompt** from `reference.md`. Temperature 0.1. The LLM outputs FILE blocks in this exact format:
```
---FILE: wiki/entities/page-slug.md---
(complete file with YAML frontmatter)
---END FILE---
```

**Step 4 — Parse and write**: Parse the FILE blocks using:
```bash
python <SKILL_DIR>/scripts/wiki-parse.py --parse-files < <generation-output>
```
For each parsed file:
- If the page already exists, use `wiki-merge.py` to merge frontmatter, then call LLM with the **Merger Prompt** from `reference.md` to merge the body.
- If the page is new, write directly.
- Special handling: `wiki/log.md` is appended (not overwritten). `wiki/index.md` and `wiki/overview.md` are overwritten.

**Step 5 — Update index**: Add new entries to `wiki/index.md` under the appropriate type category.

**Step 6 — Vectorize** (optional): If embedding is configured:
```bash
python <SKILL_DIR>/scripts/wiki-chunk.py <project-name> wiki/entities/page-slug.md
```

### 4. Enrich Wikilinks

When the user wants to add cross-references to a page:

1. Read `wiki/index.md` and the page content.
2. Send both to the LLM with the **Wikilink Enrichment Prompt** from `reference.md`.
3. The LLM returns JSON: `{"links": [{"term": "exact text", "target": "page-slug"}]}`
4. For each link, replace the first unlinked occurrence of `term` with `[[target]]` (or `[[target|term]]` if term != target).

### 5. Knowledge Graph Analysis

When the user wants to understand the wiki structure:

```bash
python <SKILL_DIR>/scripts/wiki-graph.py <project-name>
```

Returns: nodes, edges, communities (Louvain), surprising connections, and knowledge gaps.

### 6. Quality Check

When the user wants to audit the wiki:

```bash
python <SKILL_DIR>/scripts/wiki-lint.py <project-name>
```

Returns: orphan pages, broken wikilinks, pages with no outlinks, missing frontmatter fields.

For semantic quality (contradictions, stale info), send page summaries to the LLM with the **Semantic Lint Prompt** from `reference.md`.

### 7. Deep Research

When the user wants to research a topic and add it to the wiki:

1. Use `web_search` to search for 2-3 relevant queries.
2. Send the search results + `wiki/index.md` to the LLM with the **Deep Research Prompt** from `reference.md`.
3. The LLM synthesizes a wiki page with citations.
4. Save to `wiki/queries/research-{slug}-{date}.md` with frontmatter `type: query, origin: deep-research`.
5. Optionally ingest the research page to extract entities and concepts.

## Important Rules

- All wiki pages **must** have YAML frontmatter with: `type`, `title`, `created`, `updated`
- Use `[[wikilink]]` syntax in body text for cross-references
- The `related` frontmatter field uses **bare slugs** (no `[[...]]`), e.g., `related: [gpt-4, transformers]`
- The `sources` field uses original filenames, e.g., `sources: ["paper.pdf"]`
- When ingesting, check `wiki/index.md` first to avoid creating duplicate pages
- **Merge, don't overwrite** existing pages
- Ingest cache: skip files already processed (SHA-256 hash check in `.wiki/ingest-cache.json`)
- Output language: auto-detect from source content, or follow user preference
- File names: kebab-case.md
- Wikilink resolution is case-insensitive and normalizes spaces to hyphens

## Project Path Resolution

- Hermes default: `~/.hermes/wikis/<project-name>/`
- OpenClaw default: `~/.openclaw/wikis/<project-name>/`
- Custom: pass `--path` to any script
- All scripts accept `<project-name>` as first argument (resolves to default path)

## Compatibility with llm_wiki

Wiki projects created by this skill are fully compatible with the [llm_wiki](https://github.com/zhanghc1122/llm_wiki) desktop app. To open in llm_wiki:
1. Open llm_wiki
2. Click "Open Project"
3. Navigate to the wiki project directory

The directory structure, frontmatter format, wikilink syntax, and LanceDB vector schema are identical.