# Agent Skills

A collection of AI agent skills for knowledge management, research, and productivity. Compatible with **Hermes**, **Claude Code**, and any agent framework that supports SKILL.md or CLAUDE.md.

## Skills

| Skill | Description | Status |
|-------|-------------|--------|
| [wiki-manager](skills/wiki-manager/) | Personal knowledge base (wiki) management — search, ingest, graph, lint, deep research | Ready |

## Installation

### For Hermes

```bash
git clone https://github.com/zhanghc1122/agent-skills.git
cp -r agent-skills/skills/wiki-manager ~/.hermes/skills/
hermes skills enable wiki-manager
```

### For Claude Code

```bash
git clone https://github.com/zhanghc1122/agent-skills.git
cp -r agent-skills/skills/wiki-manager ~/.claude/skills/
```

### For Other Agents

The Python scripts in `scripts/` are standalone and can be called from any agent:

```bash
python /path/to/agent-skills/skills/wiki-manager/scripts/wiki-init.py my-wiki
python /path/to/agent-skills/skills/wiki-manager/scripts/wiki-search.py my-wiki "query"
```

Prompt templates in `reference.md` work with any LLM (OpenAI, Anthropic, Gemini, etc.).

## Skill Structure

Each skill follows this layout:

```
skills/<skill-name>/
  SKILL.md          ← Hermes skill definition
  CLAUDE.md         ← Claude Code skill definition
  reference.md      ← Prompt templates and algorithm specs (universal)
  examples.md       ← Usage examples
  scripts/          ← Python helper scripts (universal)
  assets/           ← Templates and static files
```

- `SKILL.md` / `CLAUDE.md` — Agent-specific entry points and workflow instructions
- `reference.md` — Universal prompt templates and technical reference
- `scripts/` — Standalone Python scripts, callable from any environment
- `assets/` — Static templates used by scripts

## Compatibility

| Component | Hermes | Claude Code | Other Agents |
|-----------|--------|-------------|-------------|
| SKILL.md | Native | Supported | N/A |
| CLAUDE.md | N/A | Native | N/A |
| Python scripts | Via shell_exec | Via Bash tool | Direct execution |
| reference.md prompts | Via LLM calls | Via LLM calls | Via LLM calls |
| Wiki data format | Read/write | Read/write | Read/write |

## Contributing

Skills should:
1. Include both `SKILL.md` and `CLAUDE.md` for cross-platform support
2. Keep Python scripts standalone (no agent-specific imports)
3. Put all LLM prompts in `reference.md` for easy customization
4. Use standard data formats (markdown, YAML frontmatter, JSON)

## License

MIT
