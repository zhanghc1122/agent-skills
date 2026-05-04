# Wiki Manager Reference

This document contains all prompt templates, algorithms, and technical details for the wiki-manager skill.

## Prompt Templates

### 1. Analysis Prompt (Ingest Step 1)

**System prompt:**

```
You are an expert research analyst. Read the source document and produce a structured analysis.

## ⚠️ MANDATORY OUTPUT LANGUAGE: {lang}

You MUST write your entire response (including wiki page titles, content, descriptions, summaries, and any generated text) in **{lang}**.
The source material or wiki content may be in a different language, but this is IRRELEVANT to your output language.
Ignore the language of any source content. Generate everything in {lang} only.
Proper nouns should use standard {lang} transliteration when appropriate.
DO NOT use any other language. This overrides all other instructions.

Your analysis should cover:

## Key Entities
List people, organizations, products, datasets, tools mentioned. For each:
- Name and type
- Role in the source (central vs. peripheral)
- Whether it likely already exists in the wiki (check the index)

## Key Concepts
List theories, methods, techniques, phenomena. For each:
- Name and brief definition
- Why it matters in this source
- Whether it likely already exists in the wiki

## Main Arguments & Findings
- What are the core claims or results?
- What evidence supports them?
- How strong is the evidence?

## Connections to Existing Wiki
- What existing pages does this source relate to?
- Does it strengthen, challenge, or extend existing knowledge?

## Contradictions & Tensions
- Does anything in this source conflict with existing wiki content?
- Are there internal tensions or caveats?

## Recommendations
- What wiki pages should be created or updated?
- What should be emphasized vs. de-emphasized?
- Any open questions worth flagging for the user?

Be thorough but concise. Focus on what's genuinely important.

If a folder context is provided, use it as a hint for categorization — the folder structure often reflects the user's organizational intent (e.g., 'papers/energy' suggests the file is an energy-related paper).

## Wiki Purpose (for context)
{purpose}

## Current Wiki Index (for checking existing content)
{index}
```

**User message:**

```
Analyze this source document:

**File:** {fileName}
**Folder context:** {folderContext}

---

{truncatedContent}
```

**Parameters:** Temperature 0.1. Truncate source content at 50000 chars with `[...truncated...]`.

---

### 2. Generation Prompt (Ingest Step 2)

**System prompt:**

```
You are a wiki maintainer. Based on the analysis provided, generate wiki files.

## ⚠️ MANDATORY OUTPUT LANGUAGE: {lang}

## IMPORTANT: Source File
The original source file is: **{sourceFileName}**
All wiki pages generated from this source MUST include this filename in their frontmatter `sources` field.

## What to generate

1. A source summary page at **wiki/sources/{sourceBaseName}.md** (MUST use this exact path)
2. Entity pages in wiki/entities/ for key entities identified in the analysis
3. Concept pages in wiki/concepts/ for key concepts identified in the analysis
4. An updated wiki/index.md — add new entries to existing categories, preserve all existing entries
5. A log entry for wiki/log.md (just the new entry to append, format: ## [YYYY-MM-DD] ingest | Title)
6. An updated wiki/overview.md — a high-level summary of what the entire wiki covers, updated to reflect the newly ingested source. This should be a comprehensive 2-5 paragraph overview of ALL topics in the wiki, not just the new source.

## Frontmatter Rules (CRITICAL — parser is strict)

1. The VERY FIRST line of the file MUST be exactly `---` (three hyphens, nothing else).
   Do NOT wrap the file in a ```yaml ... ``` code fence.
   Do NOT prefix it with a `frontmatter:` key or any other line.
2. Each frontmatter line is a `key: value` pair on its own line.
3. The frontmatter ends with another `---` line on its own.
4. The next line after the closing `---` is the start of the page body.
5. Arrays use the standard YAML inline form `[a, b, c]`.
   Wikilinks belong in the BODY only — never write `related: [[a]], [[b]]` (invalid YAML);
   write `related: [a, b]` with bare slugs.

Required fields:
  • type     — one of: source | entity | concept | comparison | query | synthesis
  • title    — string (quote it if it contains a colon)
  • created  — date in YYYY-MM-DD (no quotes)
  • updated  — same as created
  • tags     — array of bare strings: `tags: [microbiology, ai]`
  • related  — array of bare wiki page slugs: `related: [foo, bar-baz]`
  • sources  — array of source filenames; MUST include "{sourceFileName}"

Concrete example:
    ---
    type: entity
    title: Example Entity
    created: 2026-05-04
    updated: 2026-05-04
    tags: [example, demo]
    related: [related-slug-1, related-slug-2]
    sources: ["{sourceFileName}"]
    ---
    
    # Example Entity
    
    Body content goes here. Use [[wikilink]] syntax in the body for cross-references.

Other rules:
- Use [[wikilink]] syntax in the BODY for cross-references between pages
- Use kebab-case filenames
- Follow the analysis recommendations on what to emphasize
- If the analysis found connections to existing pages, add cross-references

## Review block types

After all FILE blocks, optionally emit REVIEW blocks:
- contradiction: conflicts with existing wiki content
- duplicate: entity/concept might already exist under different name
- missing-page: important concept referenced but no dedicated page
- suggestion: ideas for further research

OPTIONS: Create Page | Skip (only these labels)
SEARCH: 2-3 web search queries (for suggestion/missing-page types)

## Output Format (MUST FOLLOW EXACTLY)

FILE block:
---FILE: wiki/path/to/page.md---
(complete file content with YAML frontmatter)
---END FILE---

REVIEW block:
---REVIEW: type | Title---
Description
OPTIONS: Create Page | Skip
PAGES: wiki/page1.md, wiki/page2.md
SEARCH: query1 | query2 | query3
---END REVIEW---

## Output Requirements (STRICT)
1. First character MUST be `-` (opening of ---FILE:)
2. No preamble
3. No analysis echo
4. No markdown outside FILE/REVIEW blocks
5. No trailing commentary
6. Every FILE block content MUST be in the mandatory output language

---

## ⚠️ MANDATORY OUTPUT LANGUAGE: {lang}
```

**User message:**

```
Source document to process: **{fileName}**

The Stage 1 analysis below is CONTEXT to inform your output. Do NOT echo
its tables, bullet points, or prose. Your output must be FILE/REVIEW
blocks as specified in the system prompt — nothing else.

## Stage 1 Analysis (context only — do not repeat)

{analysis}

## Original Source Content

{truncatedContent}

---

Now emit the FILE blocks for the wiki files derived from **{fileName}**.
Your response MUST begin with `---FILE:` as the very first characters.
No preamble. No analysis prose. Start immediately.
```

**Parameters:** Temperature 0.1.

---

### 3. Page Merger Prompt

**System prompt:**

```
You are merging two versions of the same wiki page into one coherent document.
Both versions describe the same entity/concept; one is on disk, the other from a different source.

Output ONE merged version that:
- Preserves every factual claim from both versions (do not drop content)
- Eliminates redundancy when both versions state the same fact
- Reorganizes sections so the structure is logical for the merged topic
- Uses consistent markdown structure (headings, tables, lists, callouts)
- Keeps [[wikilink]] references intact

Output requirements:
- First character MUST be `-` (opening of ---)
- Output COMPLETE file: YAML frontmatter + body
- No preamble
- Caller will overwrite sources/tags/related/updated with deterministic values
```

**User message:**

```
## Existing version on disk

{existingContent}

---

## Newly generated version (from {sourceFileName})

{incomingContent}

---

Now output the merged file. Start with `---` on the first line.
```

**Parameters:** Temperature 0.1. Reject merge if body < 70% of longer version.

---

### 4. Wikilink Enrichment Prompt

**System prompt:**

```
You identify which terms in a wiki page should become [[wikilinks]] pointing to existing wiki pages.

You will receive:
  - a wiki index listing existing pages
  - the content of ONE wiki page

Return a JSON object listing which terms should be linked to which index entries.

Response format (EXACTLY this JSON shape, nothing else):
{
  "links": [
    { "term": "exact text appearing in the content", "target": "index page name" }
  ]
}

Rules:
- Each "term" MUST be a literal substring present in the page content (case-sensitive).
- Each "target" MUST be a page listed in the wiki index.
- Include at most one entry per target (first mention).
- Only include clearly-matching terms.
- If no terms should be linked, return {"links": []}.
- Do NOT output preamble, explanations, or markdown fences — ONLY the JSON object.

## Wiki Index
{indexContent}
```

**User message:**

```
Page content:

{content}
```

---

### 5. Deep Research Prompt

**System prompt:**

```
You are a research assistant. Synthesize the web search results into a comprehensive wiki page.

## ⚠️ MANDATORY OUTPUT LANGUAGE: {lang}

## Cross-referencing (IMPORTANT)
- The wiki already has existing pages listed in the Wiki Index below.
- When your synthesis mentions an entity or concept that exists in the wiki, ALWAYS use [[wikilink]] syntax to link to it.
- For example, if the wiki has an entity 'anthropic', write [[anthropic]] when mentioning it.

## Writing Rules
- Organize into clear sections with headings
- Cite web sources using [N] notation
- Note contradictions or gaps
- Suggest additional sources worth finding
- Neutral, encyclopedic tone

## Existing Wiki Index (link to these pages with [[wikilink]])
{wikiIndex}
```

**User message:**

```
Research topic: **{topic}**

## Web Search Results

[1] **{title}** ({source})
{snippet}

[2] ...

Synthesize into a wiki page.
```

**Save format:**

```yaml
---
type: query
title: "Research: {topic}"
created: {date}
updated: {date}
origin: deep-research
tags: [research]
related: [existing-slug-1, existing-slug-2]
sources: []
---
```

---

### 6. Semantic Lint Prompt

**System prompt:**

```
You are a wiki quality analyst. Review the following wiki page summaries and identify issues.

For each issue, output exactly this format:

---LINT: type | severity | Short title---
Description of the issue.
PAGES: page1.md, page2.md
---END LINT---

Types:
- contradiction: two or more pages make conflicting claims
- stale: information that appears outdated or superseded
- missing-page: an important concept is heavily referenced but has no dedicated page
- suggestion: a question or source worth adding to the wiki

Severities:
- warning: should be addressed
- info: nice to have

Only report genuine issues. Do not invent problems. Output ONLY the ---LINT--- blocks, no other text.

## Wiki Pages

{summaries}
```

Where each summary is: `### {relativePath}\n{first 500 chars}...`

---

## Algorithms

### BM25 Search Scoring

```
score = (filenameExact ? 200 : 0)
      + (titleHasPhrase ? 50 : 0)
      + contentPhraseOcc * 20    (capped at 10)
      + titleTokenScore * 5
      + contentTokenScore * 1
```

**CJK tokenization:** For tokens containing CJK characters and length > 2:
- Keep original token for exact phrase matching
- Generate overlapping bigrams: `"默会知识"` → `"默会"`, `"会知"`, `"知识"`
- Add individual characters (excluding stop words)

**Stop words:**
- Chinese: 的, 是, 了, 什么, 在, 有, 和, 与, 对, 从
- English: the, is, a, an, what, how, are, was, were, do, does, did, be, been, being, have, has, had, it, its, in, on, at, to, for, of, with, by, this, that

### RRF Fusion (BM25 + Vector Search)

```
fused_score(p) = 1/(K + token_rank(p)) + 1/(K + vector_rank(p))
```

Where K = 60 (Cormack et al. SIGIR 2009). Pages absent from either list contribute 0 for that term.

### Knowledge Graph Relevance

```
relevance(A,B) = directLink * 3.0 + sourceOverlap * 4.0 + adamicAdar * 1.5 + typeAffinity * 1.0
```

**Type affinity matrix:**
- entity↔concept: 1.2, concept↔synthesis: 1.2 (highest)
- Same-type pairs: 0.5-0.8 (penalized)
- source↔source: 0.5, query↔query: 0.5 (lowest)

### Surprising Connection Detection

Per edge scoring:
- Cross-community: +3
- Cross-type distant (source↔concept, source↔synthesis, query↔entity): +2
- Cross-type other: +1
- Peripheral-to-hub (min_deg≤2 AND max_deg≥maxDegree*0.5): +2
- Weak connection (0<weight<2): +1

Threshold: score ≥ 3. Limit: 5 results.

### Knowledge Gap Detection

- **Isolated nodes**: linkCount ≤ 1 (excluding overview, index, log)
- **Sparse communities**: cohesion < 0.15 AND nodeCount ≥ 3
- **Bridge nodes**: neighbors span ≥ 3 communities (top 3)

### Markdown Chunking

Parameters: targetChars=1000, maxChars=1500, minChars=200, overlapChars=200

Pipeline:
1. Strip frontmatter
2. Split by headings (track heading path breadcrumb)
3. Split atoms: fenced code blocks and tables are indivisible, paragraphs are splittable
4. Recursive split: paragraph → line → sentence → space → hard slice
5. Greedy pack pieces into chunks
6. Merge small chunks (< minChars) with neighbors
7. Apply overlap from previous chunk tail (snap to sentence boundary)

### Page Merge Rules

- **Union fields** (take set union): sources, tags, related
- **Locked fields** (keep existing): type, title, created
- **updated**: always set to today
- **Body**: LLM merge; reject if merged body < 70% of longer version

### LanceDB v2 Schema

Table: `wiki_chunks_v2`
Path: `{project}/.wiki/lancedb/`

| Column | Type | Description |
|--------|------|-------------|
| chunk_id | string | `{page_id}#{chunk_index}` |
| page_id | string | Wiki page slug (kebab-case, no .md) |
| chunk_index | uint32 | 0-based position |
| chunk_text | string | Raw chunk content |
| heading_path | string | Breadcrumb like `## Intro > ### Usage` |
| vector | float32[] | Embedding vector |

Upsert: DELETE all rows with target page_id, then ADD new chunks.

### Wikilink Resolution

Three matching strategies (in order):
1. Exact match against node IDs
2. Lowercase + hyphen-normalized match (spaces → hyphens)
3. Case-insensitive direct match

### Frontmatter Parsing

Two-pass approach:
1. Strict regex: `^---\n...\n---\n` (anchored to file start)
2. Fallback regex: search for `---\n...\n---` block within first 6 lines

Wikilink list repair: `related: [[a]], [[b]]` → `related: ["[[a]]", "[[b]]"]`

### Language Detection

Auto-detect from source content. Override with user preference.
Directive format:
```
## ⚠️ MANDATORY OUTPUT LANGUAGE: {lang}
You MUST write your entire response in **{lang}**.
DO NOT use any other language. This overrides all other instructions.
```