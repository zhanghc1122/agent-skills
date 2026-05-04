# Agent Skills

A collection of AI agent skills for knowledge management, research, and productivity. Compatible with **OpenClaw**, **Hermes**, **Claude Code**, and any agent framework that supports SKILL.md or CLAUDE.md.

## Skills

| Skill | Description | Status |
|-------|-------------|--------|
| [wiki-manager](skills/wiki-manager/) | Personal knowledge base (wiki) management — search, ingest, graph, lint, deep research | Ready |

## Installation

### For OpenClaw

```bash
git clone https://github.com/zhanghc1122/agent-skills.git
cp -r agent-skills/skills/wiki-manager ~/.openclaw/skills/
```

Or install via OpenClaw CLI:
```bash
openclaw skills install wiki-manager
```

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
  SKILL.md          ← OpenClaw / Hermes skill definition
  CLAUDE.md         ← Claude Code skill definition
  reference.md      ← Prompt templates and algorithm specs (universal)
  examples.md       ← Usage examples
  scripts/          ← Python helper scripts (universal)
  assets/           ← Templates and static files
```

- `SKILL.md` — Agent entry point for OpenClaw and Hermes (YAML frontmatter + Markdown instructions)
- `CLAUDE.md` — Claude Code entry point
- `reference.md` — Universal prompt templates and technical reference
- `scripts/` — Standalone Python scripts, callable from any environment
- `assets/` — Static templates used by scripts

## Compatibility

| Component | OpenClaw | Hermes | Claude Code | Other Agents |
|-----------|----------|--------|-------------|-------------|
| SKILL.md | Native | Native | Supported | N/A |
| CLAUDE.md | N/A | N/A | Native | N/A |
| Python scripts | Via shell_exec | Via shell_exec | Via Bash tool | Direct execution |
| reference.md prompts | Via LLM calls | Via LLM calls | Via LLM calls | Via LLM calls |
| Wiki data format | Read/write | Read/write | Read/write | Read/write |

### Platform-Specific Paths

| Platform | Skill install path | Wiki storage path |
|----------|-------------------|-------------------|
| OpenClaw | `~/.openclaw/skills/wiki-manager/` | `~/.openclaw/wikis/<name>/` |
| Hermes | `~/.hermes/skills/wiki-manager/` | `~/.hermes/wikis/<name>/` |
| Claude Code | `~/.claude/skills/wiki-manager/` | `~/.hermes/wikis/<name>/` |

Scripts auto-detect the platform and use the appropriate default path. You can override with `--path` on any command.

## Contributing

Skills should:
1. Include both `SKILL.md` and `CLAUDE.md` for cross-platform support
2. Keep Python scripts standalone (no agent-specific imports)
3. Put all LLM prompts in `reference.md` for easy customization
4. Use standard data formats (markdown, YAML frontmatter, JSON)
5. Auto-detect platform for default paths (OpenClaw → Hermes → fallback)

## License

MIT
