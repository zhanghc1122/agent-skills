#!/usr/bin/env python3
"""Merge two versions of a wiki page's frontmatter."""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

UNION_FIELDS = {"sources", "tags", "related"}
LOCKED_FIELDS = {"type", "title", "created"}


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


def get_body(text: str) -> str:
    m = FM_RE.match(text)
    if m:
        return text[m.end():]
    return text


def merge_frontmatter(existing: dict, new: dict) -> dict:
    merged = {}

    # Start with existing
    for key, val in existing.items():
        merged[key] = val

    # Merge union fields (take union of arrays)
    for field in UNION_FIELDS:
        existing_vals = set(existing.get(field, []))
        new_vals = set(new.get(field, []))
        combined = existing_vals | new_vals
        if combined:
            merged[field] = sorted(combined)

    # Locked fields: keep existing values
    for field in LOCKED_FIELDS:
        if field in existing:
            merged[field] = existing[field]
        elif field in new:
            merged[field] = new[field]

    # Always update the date
    merged["updated"] = date.today().isoformat()

    # Copy any new fields not in existing and not locked
    for key, val in new.items():
        if key not in merged and key not in LOCKED_FIELDS:
            merged[key] = val

    return merged


def format_frontmatter(fm: dict) -> str:
    lines = ["---"]
    for key, val in fm.items():
        if isinstance(val, list):
            items = ", ".join(f'"{v}"' for v in val)
            lines.append(f"{key}: [{items}]")
        else:
            lines.append(f'{key}: "{val}"' if isinstance(val, str) and not val.isdigit() else f"{key}: {val}")
    lines.append("---")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Merge two wiki page versions")
    parser.add_argument("existing", help="Path to existing wiki page")
    parser.add_argument("new", help="New page content (or path to file)")
    parser.add_argument("--output", "-o", default=None, help="Output file path (default: stdout)")
    args = parser.parse_args()

    existing_path = Path(args.existing)
    if not existing_path.exists():
        print(json.dumps({"error": f"File not found: {existing_path}"}), file=sys.stderr)
        sys.exit(1)

    existing_text = existing_path.read_text(encoding="utf-8")

    # New content can be a file path or inline text
    new_path = Path(args.new)
    if new_path.exists():
        new_text = new_path.read_text(encoding="utf-8")
    else:
        new_text = args.new

    existing_fm = parse_frontmatter(existing_text)
    new_fm = parse_frontmatter(new_text)
    merged_fm = merge_frontmatter(existing_fm, new_fm)

    existing_body = get_body(existing_text)
    new_body = get_body(new_text)

    result = {
        "frontmatter": format_frontmatter(merged_fm),
        "frontmatter_dict": merged_fm,
        "existing_body": existing_body.strip(),
        "new_body": new_body.strip(),
        "needs_llm_merge": existing_body.strip() != new_body.strip() and bool(existing_body.strip()),
    }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
