#!/usr/bin/env python3
"""Initialize a wiki project directory structure."""

import argparse
import json
import os
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Optional

SCRIPT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = SCRIPT_DIR.parent / "assets"

BASE_DIRS = [
    "raw/sources",
    "raw/assets",
    "wiki/entities",
    "wiki/concepts",
    "wiki/sources",
    "wiki/queries",
    "wiki/comparisons",
    "wiki/synthesis",
]

TEMPLATE_EXTRA_DIRS = {
    "research": ["wiki/methodology", "wiki/findings", "wiki/thesis"],
    "reading": ["wiki/characters", "wiki/themes", "wiki/plot-threads", "wiki/chapters"],
    "personal": ["wiki/goals", "wiki/habits", "wiki/reflections", "wiki/journal"],
    "business": ["wiki/meetings", "wiki/decisions", "wiki/projects", "wiki/stakeholders"],
}

ASSET_FILES = {
    "schema-template.md": "schema.md",
    "purpose-template.md": "purpose.md",
    "index-template.md": "wiki/index.md",
    "overview-template.md": "wiki/overview.md",
    "log-template.md": "wiki/log.md",
}

OBSIDIAN_FILES = {
    "obsidian-app.json": ".obsidian/app.json",
    "obsidian-appearance.json": ".obsidian/appearance.json",
    "obsidian-core-plugins.json": ".obsidian/core-plugins.json",
}


def default_wikis_dir() -> Path:
    """Resolve default wiki storage dir based on detected platform."""
    home = Path.home()
    for candidate in [home / ".openclaw" / "wikis", home / ".hermes" / "wikis"]:
        if candidate.parent.exists():
            return candidate
    return home / ".hermes" / "wikis"


def init_project(name: str, template: str = "general", path: Optional[str] = None) -> str:
    if path:
        project_dir = Path(path)
    else:
        project_dir = default_wikis_dir() / name

    if project_dir.exists():
        existing = [p.name for p in project_dir.iterdir()]
        if any(n not in (".obsidian",) for n in existing):
            print(f"Error: {project_dir} already exists and is not empty", file=sys.stderr)
            sys.exit(1)

    # Create directories
    all_dirs = list(BASE_DIRS)
    if template in TEMPLATE_EXTRA_DIRS:
        all_dirs.extend(TEMPLATE_EXTRA_DIRS[template])

    for d in all_dirs:
        (project_dir / d).mkdir(parents=True, exist_ok=True)

    # Copy asset files
    for src_name, dst_rel in ASSET_FILES.items():
        src = ASSETS_DIR / src_name
        dst = project_dir / dst_rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # Copy obsidian config
    for src_name, dst_rel in OBSIDIAN_FILES.items():
        src = ASSETS_DIR / src_name
        dst = project_dir / dst_rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # Write project config
    config_dir = project_dir / ".wiki"
    config_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "name": name,
        "template": template,
        "created": date.today().isoformat(),
    }
    (config_dir / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    # Update log with init date
    log_path = project_dir / "wiki" / "log.md"
    if log_path.exists():
        content = log_path.read_text(encoding="utf-8")
        content = content.replace("2026-05-04", date.today().isoformat())
        content = content.replace("Project Created", f"Project '{name}' Created")
        log_path.write_text(content, encoding="utf-8")

    print(json.dumps({
        "status": "ok",
        "path": str(project_dir),
        "name": name,
        "template": template,
    }, ensure_ascii=False))
    return str(project_dir)


def main():
    parser = argparse.ArgumentParser(description="Initialize a wiki project")
    parser.add_argument("name", help="Project name")
    parser.add_argument("--template", "-t", default="general",
                        choices=["general", "research", "reading", "personal", "business"],
                        help="Project template (default: general)")
    parser.add_argument("--path", "-p", default=None,
                        help="Custom project path (default: auto-detected wikis dir/<name>)")
    args = parser.parse_args()
    init_project(args.name, args.template, args.path)


if __name__ == "__main__":
    main()
