#!/usr/bin/env python3
"""Parse FILE, REVIEW, and LINT blocks from LLM output."""

import argparse
import json
import re
import sys
from pathlib import Path

FILE_RE = re.compile(r"---FILE:\s*(.+?)---\s*\n(.*?)---END FILE---", re.DOTALL)
REVIEW_RE = re.compile(r"---REVIEW:\s*(\w+)\s*\|\s*(.+?)---\s*\n(.*?)---END REVIEW---", re.DOTALL)
LINT_RE = re.compile(r"---LINT:\s*(\w+)\s*\|\s*(\w+)\s*\|\s*(.+?)---\s*\n(.*?)---END LINT---", re.DOTALL)

SAFE_PATH_RE = re.compile(r"^\w[\w/\-]*$")


def validate_path(p: str) -> bool:
    if not p.startswith("wiki/"):
        return False
    if ".." in p:
        return False
    if not SAFE_PATH_RE.match(p.replace("wiki/", "")):
        return False
    return True


def parse_files(text: str) -> list[dict]:
    results = []
    for m in FILE_RE.finditer(text):
        path = m.group(1).strip()
        content = m.group(2).strip()
        if not validate_path(path):
            continue
        if not content.startswith("---"):
            content = "---\n" + content
        results.append({"path": path, "content": content})
    return results


def parse_reviews(text: str) -> list[dict]:
    results = []
    for m in REVIEW_RE.finditer(text):
        review_type = m.group(1).strip()
        title = m.group(2).strip()
        body = m.group(3).strip()

        pages = []
        search_queries = []
        options = []

        for line in body.split("\n"):
            line = line.strip()
            if line.startswith("PAGES:"):
                pages = [p.strip() for p in line[6:].split(",") if p.strip()]
            elif line.startswith("SEARCH:"):
                search_queries = [q.strip() for q in line[7:].split("|") if q.strip()]
            elif line.startswith("OPTIONS:"):
                options = [o.strip() for o in line[8:].split("|") if o.strip()]

        description = "\n".join(
            line for line in body.split("\n")
            if not line.strip().startswith(("PAGES:", "SEARCH:", "OPTIONS:"))
        ).strip()

        results.append({
            "type": review_type,
            "title": title,
            "description": description,
            "pages": pages,
            "search_queries": search_queries,
            "options": options,
        })
    return results


def parse_lints(text: str) -> list[dict]:
    results = []
    for m in LINT_RE.finditer(text):
        results.append({
            "type": m.group(1).strip(),
            "severity": m.group(2).strip(),
            "title": m.group(3).strip(),
            "description": m.group(4).strip(),
        })
    return results


def parse_all(text: str) -> dict:
    return {
        "files": parse_files(text),
        "reviews": parse_reviews(text),
        "lints": parse_lints(text),
    }


def main():
    parser = argparse.ArgumentParser(description="Parse FILE/REVIEW/LINT blocks from LLM output")
    parser.add_argument("--parse-files", action="store_true", help="Parse FILE blocks only")
    parser.add_argument("--parse-reviews", action="store_true", help="Parse REVIEW blocks only")
    parser.add_argument("--parse-lints", action="store_true", help="Parse LINT blocks only")
    parser.add_argument("input", nargs="?", help="Input file path (default: stdin)")
    args = parser.parse_args()

    if args.input:
        text = Path(args.input).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    if args.parse_files:
        result = parse_files(text)
    elif args.parse_reviews:
        result = parse_reviews(text)
    elif args.parse_lints:
        result = parse_lints(text)
    else:
        result = parse_all(text)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
