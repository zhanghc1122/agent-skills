# Wiki Manager — Usage Examples

## Initialize a Research Wiki

```bash
python ~/.hermes/skills/wiki-manager/scripts/wiki-init.py my-research --template research
```

Creates `~/.hermes/wikis/my-research/` with research-specific directories (methodology, findings, thesis).

## Initialize a Business Wiki at Custom Path

```bash
python ~/.hermes/skills/wiki-manager/scripts/wiki-init.py team-knowledge --template business --path /home/user/projects/team-wiki
```

## Search the Wiki

```bash
python ~/.hermes/skills/wiki-manager/scripts/wiki-search.py my-research "transformer architecture"
```

Returns:
```json
[
  {
    "path": "wiki/concepts/transformer-architecture.md",
    "title": "Transformer Architecture",
    "snippet": "...the transformer architecture introduced self-attention mechanisms...",
    "score": 270.5
  },
  {
    "path": "wiki/entities/gpt-4.md",
    "title": "GPT-4",
    "snippet": "...based on the transformer architecture...",
    "score": 25.0
  }
]
```

## Ingest a Document (Full Workflow)

1. Read source document and wiki context:
   - Read `raw/sources/paper.pdf` (or `.md`, `.txt`)
   - Read `schema.md`, `purpose.md`, `wiki/index.md`, `wiki/overview.md`

2. LLM Analysis call (use Analysis Prompt from reference.md):
   - Input: source content + wiki context
   - Output: structured analysis of entities, concepts, connections

3. LLM Generation call (use Generation Prompt from reference.md):
   - Input: analysis + source content
   - Output: FILE blocks like:
   ```
   ---FILE: wiki/sources/attention-is-all-you-need.md---
   ---
   type: source
   title: "Attention Is All You Need"
   created: 2026-05-04
   updated: 2026-05-04
   tags: [deep-learning, nlp, transformers]
   related: [transformer-architecture, self-attention]
   sources: ["attention-is-all-you-need.pdf"]
   ---
   
   # Attention Is All You Need
   
   This paper introduced the [[transformer-architecture]]...
   ---END FILE---
   ```

4. Parse and write:
   ```bash
   python ~/.hermes/skills/wiki-manager/scripts/wiki-parse.py --parse-files < generation_output.txt
   ```

5. For existing pages, merge:
   ```bash
   python ~/.hermes/skills/wiki-manager/scripts/wiki-merge.py wiki/entities/transformer-architecture.md new_content.md
   ```

6. Vectorize (optional):
   ```bash
   python ~/.hermes/skills/wiki-manager/scripts/wiki-chunk.py my-research wiki/entities/transformer-architecture.md
   ```

## Knowledge Graph Analysis

```bash
python ~/.hermes/skills/wiki-manager/scripts/wiki-graph.py my-research
```

Returns communities, surprising connections, and knowledge gaps.

## Quality Check

```bash
python ~/.hermes/skills/wiki-manager/scripts/wiki-lint.py my-research
```

Returns orphan pages, broken links, missing frontmatter fields.

## Deep Research

1. Use web_search for 2-3 queries related to the topic.
2. Send search results + wiki/index.md to LLM with Deep Research Prompt.
3. Save synthesis to `wiki/queries/research-{slug}-{date}.md`.
4. Optionally ingest the research page.

## Wikilink Enrichment

1. Read `wiki/index.md` and the target page content.
2. Send to LLM with Wikilink Enrichment Prompt.
3. LLM returns JSON: `{"links": [{"term": "Transformer", "target": "transformer-architecture"}]}`
4. Replace first unlinked occurrence of "Transformer" with `[[transformer-architecture|Transformer]]`.