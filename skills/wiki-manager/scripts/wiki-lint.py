#!/usr/bin/env python3
"""Structural lint: check for orphan pages, broken wikilinks, and missing frontmatter."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]")

REQUIRED_FM_FIELDS = {"type", "title", "created", "updated"}
EXEMPT_IDS = frozenset(["index", "log"])


def parse_frontmatter(text: str) -> dict:
    m = FM_RE.match(text)
    if not m:
        return {}
    fm_text = m.group(1)
    result = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            items = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",")]
            result[key] = [i for i in items if i]
        else:
            result[key] = val.strip('"').strip("'")
    return result


def normalize_slug(s: str) -> str:
    return re.sub(r"[\s\-_]+", "", s.lower())


def lint_wiki(project_path: Path) -> List[dict]:
    wiki_dir = project_path / "wiki"
    if not wiki_dir.exists():
        return [{"type": "error", "page": "", "detail": f"wiki/ not found in {project_path}"}]

    issues = []

    # Scan all pages
    pages = {}
    slug_map = {}
    for md_file in wiki_dir.rglob("*.md"):
        rel = md_file.relative_to(project_path)
        slug = md_file.stem
        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception:
            issues.append({"type": "read-error", "page": str(rel), "detail": "Cannot read file"})
            continue

        fm = parse_frontmatter(text)
        links = [m.group(1).strip() for m in WIKILINK_RE.finditer(text)]

        pages[slug] = {
            "path": str(rel).replace("\\", "/"),
            "frontmatter": fm,
            "links": links,
            "has_wikilinks": len(links) > 0,
        }
        slug_map[normalize_slug(slug)] = slug

    # Check: missing frontmatter fields
    for slug, page in pages.items():
        fm = page["frontmatter"]
        missing = REQUIRED_FM_FIELDS - set(fm.keys())
        if missing and slug not in EXEMPT_IDS:
            issues.append({
                "type": "missing-frontmatter",
                "page": page["path"],
                "detail": f"Missing required fields: {', '.join(sorted(missing))}",
            })

    # Check: broken wikilinks
    for slug, page in pages.items():
        for target in page["links"]:
            norm = normalize_slug(target)
            if norm not in slug_map:
                issues.append({
                    "type": "broken-link",
                    "page": page["path"],
                    "detail": f"[[{target}]] -> page not found",
                })

    # Check: orphan pages (no inbound links)
    inbound = set()
    for slug, page in pages.items():
        for target in page["links"]:
            norm = normalize_slug(target)
            if norm in slug_map:
                inbound.add(slug_map[norm])

    for slug, page in pages.items():
        if slug not in inbound and slug not in EXEMPT_IDS:
            fm = page["frontmatter"]
            if fm.get("type") != "overview":
                issues.append({
                    "type": "orphan-page",
                    "page": page["path"],
                    "detail": "No inbound wikilinks from other pages",
                })

    # Check: no outbound links
    for slug, page in pages.items():
        if not page["has_wikilinks"] and slug not in EXEMPT_IDS:
            fm = page["frontmatter"]
            if fm.get("type") != "overview":
                issues.append({
                    "type": "no-outlinks",
                    "page": page["path"],
                    "detail": "Page has no [[wikilinks]] to other pages",
                })

    return issues


def main():
    parser = argparse.ArgumentParser(description="Structural lint for wiki")
    parser.add_argument("project", help="Project name")
    parser.add_argument("--path", "-p", default=None, help="Custom project path")
    args = parser.parse_args()

    project_path = Path(args.path) if args.path else Path.home() / ".hermes" / "wikis" / args.project
    issues = lint_wiki(project_path)
    print(json.dumps(issues, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()