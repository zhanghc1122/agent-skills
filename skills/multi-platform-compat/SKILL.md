---
name: multi-platform-compat
description: "Make agent skills compatible with OpenClaw, Hermes, and Claude Code simultaneously. Use this skill whenever you are creating a new skill, updating an existing skill, or need to add multi-platform compatibility to a skill. Triggers: create skill, new skill, skill compatibility, multi-platform skill, OpenClaw skill, Hermes skill, Claude Code skill, skill format, SKILL.md, CLAUDE.md, 跨平台技能, 兼容技能, 技能格式"
metadata:
  openclaw:
    emoji: "🔌"
    requires:
      bins: ["python3"]
---

## Goal

Ensure any agent skill works across OpenClaw, Hermes, and Claude Code with a single codebase. This skill provides the format specifications, compatibility patterns, and a scaffold script to generate platform-specific entry files from a universal skill definition.

## Platform Format Reference

### OpenClaw

**Install path:** `~/.openclaw/skills/<skill-name>/`
**Entry file:** `SKILL.md` (native)
**Data path:** `~/.openclaw/wikis/` or `~/.openclaw/data/`

SKILL.md frontmatter format:
```yaml
---
name: skill-name
description: "What the skill does and when to trigger it. Be pushy about triggering."
metadata:
  openclaw:
    emoji: "🎯"
    requires:
      bins: ["python3", "node"]
      pip: ["lancedb", "networkx"]
---
```

Key points:
- `name` and `description` are the only required frontmatter fields
- `metadata.openclaw` is optional, used for emoji and dependency declarations
- `requires.bins` lists required CLI tools, `requires.pip` lists Python packages
- Description is the primary triggering mechanism — include both what the skill does AND specific trigger contexts
- Scripts are referenced with absolute or skill-relative paths

### Hermes

**Install path:** `~/.hermes/skills/<skill-name>/`
**Entry file:** `SKILL.md` (native)
**Data path:** `~/.hermes/wikis/` or `~/.hermes/data/`

SKILL.md frontmatter format:
```yaml
---
name: skill-name
description: "What the skill does"
version: 1
triggers: ["keyword1", "keyword2"]
tools_required: [file_read, file_write, file_edit, shell_exec, web_search]
tags: [tag1, tag2]
---
```

Key points:
- `name`, `description`, `version`, `triggers`, `tools_required`, `tags` are recognized fields
- `triggers` is an array of keywords/phrases that activate the skill
- `tools_required` lists Hermes tool names the skill needs
- Hermes reads SKILL.md natively — same file format as OpenClaw with extra fields

### Claude Code

**Install path:** `~/.claude/skills/<skill-name>/`
**Entry file:** `CLAUDE.md` (native)
**Data path:** Uses `--path` flag or inherits from other platforms

CLAUDE.md format:
```markdown
# Skill Name — Short Description

One-line description of what this skill enables.

## Scripts Location
All scripts are in `~/.claude/skills/<skill-name>/scripts/`
All prompt templates are in `~/.claude/skills/<skill-name>/reference.md`

## Available Commands
### Command 1
\`\`\`bash
python ~/.claude/skills/<skill-name>/scripts/script.py <args>
\`\`\`

## Rules
- Rule 1
- Rule 2
```

Key points:
- No YAML frontmatter — pure Markdown
- Must include explicit script paths (Claude Code doesn't auto-resolve)
- Commands reference `~/.claude/skills/<skill-name>/` paths
- CLAUDE.md should NOT be committed to public repos (user preference)

## Compatibility Strategy

### Unified SKILL.md Frontmatter

Use a frontmatter that satisfies both OpenClaw and Hermes. OpenClaw ignores unknown fields, and Hermes does the same:

```yaml
---
name: skill-name
description: "Pushy description with trigger contexts. Use when: (1) scenario A, (2) scenario B. Triggers: keyword1, keyword2, 关键词3"
version: 1
triggers: ["keyword1", "keyword2", "关键词3"]
tools_required: [file_read, file_write, shell_exec]
tags: [tag1, tag2]
metadata:
  openclaw:
    emoji: "🎯"
    requires:
      bins: ["python3"]
---
```

This works because:
- OpenClaw reads `name`, `description`, `metadata.openclaw` — ignores `version`, `triggers`, `tools_required`, `tags`
- Hermes reads `name`, `description`, `version`, `triggers`, `tools_required`, `tags` — ignores `metadata.openclaw`

### Script Path Resolution

Never hardcode a single platform path in SKILL.md. Use one of these patterns:

**Pattern A — Platform variable (recommended for SKILL.md):**
```markdown
Scripts are in the `scripts/` directory within this skill folder.
Resolve the path based on your platform:

| Platform | Skill install path |
|----------|-------------------|
| OpenClaw | `~/.openclaw/skills/<skill-name>/scripts/` |
| Hermes | `~/.hermes/skills/<skill-name>/scripts/` |

In examples below, replace `<SKILL_DIR>` with your platform's path.
```

**Pattern B — Auto-detection in Python scripts:**
```python
def default_data_dir() -> Path:
    """Resolve default data dir based on detected platform."""
    home = Path.home()
    for candidate in [home / ".openclaw" / "data", home / ".hermes" / "data"]:
        if candidate.parent.exists():
            return candidate
    return home / ".hermes" / "data"
```

Detection priority: OpenClaw → Hermes → fallback to Hermes path.

**Pattern C — CLAUDE.md uses fixed path:**
CLAUDE.md always uses `~/.claude/skills/<skill-name>/` since Claude Code has its own install location.

### Directory Structure

```
skills/<skill-name>/
  SKILL.md          ← OpenClaw + Hermes entry (committed to git)
  CLAUDE.md         ← Claude Code entry (NOT committed, .gitignore'd)
  reference.md      ← Universal prompt templates (committed)
  examples.md       ← Usage examples (committed)
  scripts/          ← Standalone Python scripts (committed)
  assets/           ← Templates and static files (committed)
```

### .gitignore Rule

Always add to the skill repo's `.gitignore`:
```
# Claude Code specific files (not for public repo)
**/CLAUDE.md
```

## Skill Scaffold Script

Use the scaffold script to generate a new multi-platform skill:

```bash
python <SKILL_DIR>/scripts/scaffold-skill.py <skill-name> --description "What it does" --triggers "trigger1,trigger2"
```

This generates:
1. `SKILL.md` with unified frontmatter
2. `CLAUDE.md` with Claude Code format
3. `scripts/` directory with a placeholder
4. `.gitignore` excluding CLAUDE.md

## Checklist for Multi-Platform Compatibility

When creating or updating a skill, verify:

- [ ] SKILL.md has unified frontmatter (name, description, version, triggers, tools_required, tags, metadata.openclaw)
- [ ] Description is pushy — includes trigger contexts and keywords
- [ ] CLAUDE.md exists with Claude Code format and `~/.claude/skills/` paths
- [ ] CLAUDE.md is in .gitignore
- [ ] Python scripts use `default_data_dir()` auto-detection pattern
- [ ] SKILL.md uses `<SKILL_DIR>` variable instead of hardcoded paths
- [ ] No platform-specific imports or dependencies in scripts
- [ ] `reference.md` contains all LLM prompts (agent-agnostic)
- [ ] Scripts are standalone — no agent-specific imports
- [ ] Data format uses standard formats (markdown, YAML frontmatter, JSON)

## Common Pitfalls

1. **Hardcoded paths** — Always use platform detection or `<SKILL_DIR>` variable
2. **Missing CLAUDE.md** — Claude Code won't find the skill without it
3. **CLAUDE.md in git** — Add to .gitignore immediately
4. **Python 3.9 compatibility** — Use `from typing import Optional, List, Dict` instead of `str | None`, `list[str]`, `dict[`
5. **Agent-specific imports** — Scripts must work standalone, no `import hermes` or `import openclaw`
6. **LLM logic in scripts** — Scripts should be deterministic helpers. LLM calls are the agent's responsibility, using prompts from reference.md
7. **Overlapping trigger words** — Make description specific enough to avoid false triggers
8. **Missing metadata.openclaw** — Even an empty `metadata: {}` helps OpenClaw parse correctly

## Platform Quick Reference

| Aspect | OpenClaw | Hermes | Claude Code |
|--------|----------|--------|-------------|
| Entry file | SKILL.md | SKILL.md | CLAUDE.md |
| Frontmatter | YAML (name, description, metadata) | YAML (name, description, version, triggers, tools_required, tags) | None (pure Markdown) |
| Install path | ~/.openclaw/skills/ | ~/.hermes/skills/ | ~/.claude/skills/ |
| Script exec | shell_exec | shell_exec | Bash tool |
| LLM calls | Agent handles | Agent handles | Agent handles |
| Data path | ~/.openclaw/ | ~/.hermes/ | --path flag |
| Emoji support | metadata.openclaw.emoji | N/A | N/A |
| Dependencies | metadata.openclaw.requires | tools_required | N/A |
