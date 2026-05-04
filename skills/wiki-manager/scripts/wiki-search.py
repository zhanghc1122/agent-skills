#!/usr/bin/env python3
"""Search wiki pages using BM25 keyword scoring with optional vector search + RRF fusion."""

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

# --- Frontmatter parsing ---

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


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


# --- CJK tokenization ---

CJK_RE = re.compile(r"[一-鿿぀-ゟ゠-ヿ가-힯]")
CJK_LONG_RE = re.compile(r"[一-鿿぀-ゟ゠-ヿ가-힯]{2,}")

EN_STOP = frozenset(
    "the is a an what how are who when where which why this that it its of for in on at to "
    "from by with and or not but if then than so no all any can will would could should "
    "may might do does did has have had been be am was were being".split()
)
ZH_STOP = frozenset("的 是 了 什么 在 有 和 与 对 从 把 被 让 给 也 都 就 而 但 又 很 还".split())


def tokenize(text: str) -> List[str]:
    tokens = []
    for word in re.findall(r"\w+", text.lower()):
        if CJK_RE.search(word):
            if len(word) > 2:
                tokens.append(word)
                for i in range(len(word) - 1):
                    tokens.append(word[i:i + 2])
                for ch in word:
                    tokens.append(ch)
            elif len(word) == 2:
                tokens.append(word)
                for ch in word:
                    tokens.append(ch)
            else:
                tokens.append(word)
        else:
            if word not in EN_STOP and len(word) > 1:
                tokens.append(word)
    return [t for t in tokens if t not in ZH_STOP]


# --- BM25 scoring ---

def score_page(query_tokens: List[str], query_str: str, rel_path: str,
               title: str, content: str) -> float:
    score = 0.0
    stem = Path(rel_path).stem.lower()

    # Filename exact match
    if stem == query_str.lower().replace(" ", "-"):
        score += 200

    # Title phrase match
    if query_str.lower() in title.lower():
        score += 50

    # Content phrase occurrences (cap at 10)
    phrase_count = content.lower().count(query_str.lower())
    score += min(phrase_count, 10) * 20

    # Token matching
    title_tokens = set(tokenize(title))
    content_counter = Counter(tokenize(content))

    for qt in query_tokens:
        if qt in title_tokens:
            score += 5
        if qt in content_counter:
            score += min(content_counter[qt], 5)

    return score


# --- Snippet extraction ---

def extract_snippet(content: str, query_str: str, max_len: int = 200) -> str:
    body = FM_RE.sub("", content).strip()
    idx = body.lower().find(query_str.lower())
    if idx < 0:
        for qt in tokenize(query_str):
            idx = body.lower().find(qt)
            if idx >= 0:
                break
    if idx < 0:
        return body[:max_len] + ("..." if len(body) > max_len else "")

    start = max(0, idx - 80)
    end = min(len(body), idx + len(query_str) + 80)
    snippet = body[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(body):
        snippet = snippet + "..."
    return snippet[:max_len + 20]


# --- Main search ---

def get_project_path(name: str, path: Optional[str] = None) -> Path:
    if path:
        return Path(path)
    return Path.home() / ".hermes" / "wikis" / name


def search_wiki(project_path: Path, query: str, top_k: int = 20) -> List[dict]:
    wiki_dir = project_path / "wiki"
    if not wiki_dir.exists():
        print(json.dumps({"error": f"wiki/ directory not found in {project_path}"}), file=sys.stderr)
        return []

    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    results = []
    for md_file in wiki_dir.rglob("*.md"):
        rel = md_file.relative_to(project_path)
        try:
            text = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        fm = parse_frontmatter(text)
        title = fm.get("title", md_file.stem)
        body = FM_RE.sub("", text)

        score = score_page(query_tokens, query, str(rel), title, body)
        if score > 0:
            snippet = extract_snippet(text, query)
            results.append({
                "path": str(rel).replace("\\", "/"),
                "title": title,
                "snippet": snippet,
                "score": round(score, 2),
            })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:top_k]


def main():
    parser = argparse.ArgumentParser(description="Search wiki pages")
    parser.add_argument("project", help="Project name")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--path", "-p", default=None, help="Custom project path")
    parser.add_argument("--top", "-k", type=int, default=20, help="Max results (default: 20)")
    args = parser.parse_args()

    project_path = get_project_path(args.project, args.path)
    results = search_wiki(project_path, args.query, args.top)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
