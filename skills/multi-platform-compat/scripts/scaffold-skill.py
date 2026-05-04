#!/usr/bin/env python3
"""Scaffold a new multi-platform agent skill (OpenClaw + Hermes + Claude Code)."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


SKILL_MD_TEMPLATE = """---
name: {name}
description: "{description}. Use when: (1) {trigger_contexts}. Triggers: {triggers}"
version: 1
triggers: [{triggers_yaml}]
tools_required: [file_read, file_write, file_edit, shell_exec]
tags: [{tags}]
metadata:
  openclaw:
    emoji: "{emoji}"
    requires:
      bins: ["python3"]
---

## Goal

{description}.

## Scripts Location

Scripts are in the `scripts/` directory within this skill folder.
Resolve the path based on your platform:

| Platform | Skill install path |
|----------|-------------------|
| OpenClaw | `~/.openclaw/skills/{name}/scripts/` |
| Hermes | `~/.hermes/skills/{name}/scripts/` |

In examples below, replace `<SKILL_DIR>` with your platform's path.

## Core Operations

### 1. Operation Name

When the user wants to ...:

```bash
python <SKILL_DIR>/scripts/{name}-main.py <args>
```

## Rules

- All data files must use YAML frontmatter
- Merge existing data, don't overwrite
- Scripts are standalone — no agent-specific imports

## Project Path Resolution

- OpenClaw default: `~/.openclaw/data/{name}/`
- Hermes default: `~/.hermes/data/{name}/`
- Custom: pass `--path` to any script
- All scripts accept `<project-name>` as first argument (resolves to default path)
"""

CLAUDE_MD_TEMPLATE = """# {title} — AI Agent Tool

{description}.

## Scripts Location
All scripts are in `~/.claude/skills/{name}/scripts/`
All prompt templates are in `~/.claude/skills/{name}/reference.md`

## Available Commands

### Main Command
```bash
python ~/.claude/skills/{name}/scripts/{name}-main.py <args>
```

## Rules
- All data files must use YAML frontmatter
- Merge existing data, don't overwrite
- Check existing data before creating new entries to avoid duplicates
"""

GITIGNORE_TEMPLATE = """# Claude Code specific files (not for public repo)
**/CLAUDE.md
"""

SCRIPT_TEMPLATE = '''#!/usr/bin/env python3
"""Main script for {name} skill."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


def default_data_dir() -> Path:
    """Resolve default data dir based on detected platform."""
    home = Path.home()
    for candidate in [home / ".openclaw" / "data" / "{name}", home / ".hermes" / "data" / "{name}"]:
        if candidate.parent.parent.exists():
            return candidate
    return home / ".hermes" / "data" / "{name}"


def main():
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("project", help="Project name")
    parser.add_argument("--path", "-p", default=None, help="Custom project path")
    args = parser.parse_args()

    project_path = Path(args.path) if args.path else default_data_dir() / args.project
    print(json.dumps({{"project": str(project_path)}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
'''

REFERENCE_TEMPLATE = """# {title} — Prompt Templates and Algorithm Specs

## Analysis Prompt

Use this prompt when analyzing input data for ingestion:

```
You are analyzing [input] for a knowledge base. Extract:
1. Key entities and their types
2. Core concepts and definitions
3. Relationships between entities
4. Connections to existing knowledge

Output as structured JSON.
```

## Generation Prompt

Use this prompt when generating wiki pages from analysis:

```
Based on the analysis, generate wiki pages in this format:

---FILE: wiki/type/page-slug.md---
---
type: entity
title: Page Title
created: DATE_TODAY
updated: DATE_TODAY
related: [other-slug]
---

Page content with [[wikilinks]] here.

---END FILE---
```
"""


def scaffold_skill(name: str, description: str, triggers: str, output_dir: Optional[str] = None,
                   emoji: str = "🎯", tags: Optional[str] = None) -> str:
    if output_dir:
        skill_dir = Path(output_dir) / name
    else:
        skill_dir = Path.cwd() / name

    if skill_dir.exists():
        return f"Error: directory {skill_dir} already exists"

    trigger_list = [t.strip() for t in triggers.split(",") if t.strip()]
    triggers_yaml = ", ".join(f'"{t}"' for t in trigger_list)
    trigger_contexts = ", (2) ".join(trigger_list[:3])
    title = name.replace("-", " ").title()

    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    else:
        tag_list = trigger_list[:3]
    tags_yaml = ", ".join(f'"{t}"' for t in tag_list)

    # Create directories
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(parents=True)

    # Write SKILL.md
    skill_md = SKILL_MD_TEMPLATE.format(
        name=name, description=description, triggers=triggers,
        triggers_yaml=triggers_yaml, trigger_contexts=trigger_contexts,
        tags=tags_yaml, emoji=emoji, title=title,
    )
    (skill_dir / "SKILL.md").write_text(skill_md, encoding="utf-8")

    # Write CLAUDE.md
    claude_md = CLAUDE_MD_TEMPLATE.format(
        name=name, description=description, title=title,
    )
    (skill_dir / "CLAUDE.md").write_text(claude_md, encoding="utf-8")

    # Write .gitignore
    (skill_dir / ".gitignore").write_text(GITIGNORE_TEMPLATE, encoding="utf-8")

    # Write main script
    script_content = SCRIPT_TEMPLATE.format(
        name=name, description=description,
    )
    (scripts_dir / f"{name}-main.py").write_text(script_content, encoding="utf-8")

    # Write reference.md
    ref_content = REFERENCE_TEMPLATE.format(title=title)
    (skill_dir / "reference.md").write_text(ref_content, encoding="utf-8")

    # Write examples.md
    examples = f"# {title} — Usage Examples\n\n## Example 1: Basic Usage\n\n```bash\npython <SKILL_DIR>/scripts/{name}-main.py my-project\n```\n"
    (skill_dir / "examples.md").write_text(examples, encoding="utf-8")

    files_created = list(skill_dir.rglob("*"))
    file_list = "\n".join(f"  {f.relative_to(skill_dir)}" for f in files_created if f.is_file())

    return f"Created skill at {skill_dir}:\n{file_list}"


def main():
    parser = argparse.ArgumentParser(description="Scaffold a multi-platform agent skill")
    parser.add_argument("name", help="Skill name (kebab-case)")
    parser.add_argument("--description", "-d", required=True, help="Skill description")
    parser.add_argument("--triggers", "-t", required=True, help="Comma-separated trigger keywords")
    parser.add_argument("--tags", default=None, help="Comma-separated tags (defaults to triggers)")
    parser.add_argument("--emoji", default="🎯", help="OpenClaw emoji (default: 🎯)")
    parser.add_argument("--output", "-o", default=None, help="Output directory (default: current dir)")
    args = parser.parse_args()

    result = scaffold_skill(args.name, args.description, args.triggers,
                            output_dir=args.output, emoji=args.emoji, tags=args.tags)
    print(result)


if __name__ == "__main__":
    main()
