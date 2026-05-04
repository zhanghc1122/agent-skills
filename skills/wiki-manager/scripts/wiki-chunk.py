#!/usr/bin/env python3
"""Chunk wiki pages and store embeddings in LanceDB for semantic search."""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

DEFAULT_TARGET = 1000
DEFAULT_MAX = 1500
DEFAULT_MIN = 200
DEFAULT_OVERLAP = 200


def strip_frontmatter(text: str) -> str:
    m = FM_RE.match(text)
    if m:
        return text[m.end():]
    return text


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


def chunk_markdown(text: str, target: int = DEFAULT_TARGET, max_chars: int = DEFAULT_MAX,
                    min_chars: int = DEFAULT_MIN, overlap: int = DEFAULT_OVERLAP) -> List[dict]:
    body = strip_frontmatter(text)
    lines = body.split("\n")

    sections = []
    current = []
    heading_path = []
    in_fence = False
    fence_char = None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            if not in_fence:
                in_fence = True
                fence_char = stripped[0]
            elif stripped[0] == fence_char:
                in_fence = False
                fence_char = None
            current.append(line)
            continue

        if not in_fence and re.match(r"^#{1,6}\s", stripped):
            if current:
                sections.append({
                    "text": "\n".join(current),
                    "heading_path": " > ".join(heading_path),
                })
                current = []
            level = len(stripped) - len(stripped.lstrip("#"))
            title = stripped.lstrip("#").strip()
            heading_path = heading_path[:level - 1] + [title]

        current.append(line)

    if current:
        sections.append({
            "text": "\n".join(current),
            "heading_path": " > ".join(heading_path),
        })

    chunks = []
    for section in sections:
        text = section["text"].strip()
        if not text:
            continue
        if len(text) <= target:
            chunks.append({
                "text": text,
                "heading_path": section["heading_path"],
            })
        else:
            pieces = split_long_text(text, target, max_chars)
            for piece in pieces:
                chunks.append({
                    "text": piece,
                    "heading_path": section["heading_path"],
                })

    # Merge small chunks
    merged = []
    for chunk in chunks:
        if merged and len(chunk["text"]) < min_chars:
            prev = merged[-1]
            combined = prev["text"] + "\n\n" + chunk["text"]
            if len(combined) <= max_chars:
                merged[-1] = {
                    "text": combined,
                    "heading_path": prev["heading_path"],
                }
                continue
        merged.append(chunk)

    # Apply overlap
    result = []
    for i, chunk in enumerate(merged):
        text = chunk["text"]
        if i > 0 and overlap > 0:
            prev_text = merged[i - 1]["text"]
            tail = prev_text[-overlap:]
            # Snap to sentence boundary
            sentence_end = re.search(r"[。！？!?.;；]\s*", tail)
            if sentence_end:
                tail = tail[sentence_end.end():]
            text = tail + text if tail else text
        result.append({
            "index": i,
            "text": text.strip(),
            "heading_path": chunk["heading_path"],
        })

    return result


def split_long_text(text: str, target: int, max_chars: int) -> List[str]:
    if len(text) <= target:
        return [text]

    # Try paragraph boundaries
    paras = re.split(r"\n\n+", text)
    pieces = []
    current = ""
    for para in paras:
        if len(current) + len(para) + 2 <= target:
            current = current + "\n\n" + para if current else para
        else:
            if current:
                pieces.append(current)
            current = para
    if current:
        pieces.append(current)

    # Split any still-too-long pieces
    result = []
    for piece in pieces:
        if len(piece) <= max_chars:
            result.append(piece)
        else:
            # Hard split at target intervals
            for i in range(0, len(piece), target):
                result.append(piece[i:i + target])

    return result


def fetch_embedding(text: str, config: Dict) -> List[float]:
    import urllib.request
    import urllib.error

    endpoint = config.get("embedding_endpoint", "http://127.0.0.1:1234/v1/embeddings")
    api_key = config.get("embedding_api_key", "")
    model = config.get("embedding_model", "text-embedding-nomic-embed-text-v1.5")

    payload = json.dumps({
        "input": text,
        "model": model,
    }).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(endpoint, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["data"][0]["embedding"]
    except Exception as e:
        print(f"Embedding error: {e}", file=sys.stderr)
        return []


def store_in_lancedb(project_path: Path, page_id: str, chunks: List[dict],
                      embeddings: List[List[float]], config: Dict):
    try:
        import lancedb
    except ImportError:
        print("lancedb not installed. Skipping vector storage.", file=sys.stderr)
        return

    db_path = str(project_path / ".wiki" / "lancedb")
    db = lancedb.connect(db_path)
    table_name = "wiki_chunks_v2"

    dim = len(embeddings[0]) if embeddings else 0
    if dim == 0:
        return

    records = []
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        records.append({
            "chunk_id": f"{page_id}#{i}",
            "page_id": page_id,
            "chunk_index": i,
            "chunk_text": chunk["text"],
            "heading_path": chunk["heading_path"],
            "vector": emb,
        })

    try:
        table = db.open_table(table_name)
        table.delete(f"page_id = '{page_id}'")
        table.add(records)
    except Exception:
        db.create_table(table_name, records)


def default_wikis_dir() -> Path:
    """Resolve default wiki storage dir based on detected platform."""
    home = Path.home()
    for candidate in [home / ".openclaw" / "wikis", home / ".hermes" / "wikis"]:
        if candidate.parent.exists():
            return candidate
    return home / ".hermes" / "wikis"


def main():
    parser = argparse.ArgumentParser(description="Chunk and embed a wiki page")
    parser.add_argument("project", help="Project name")
    parser.add_argument("page", help="Page path relative to project (e.g., wiki/entities/gpt-4.md)")
    parser.add_argument("--path", "-p", default=None, help="Custom project path")
    parser.add_argument("--target", type=int, default=DEFAULT_TARGET)
    parser.add_argument("--max", type=int, default=DEFAULT_MAX)
    parser.add_argument("--min", type=int, default=DEFAULT_MIN)
    parser.add_argument("--overlap", type=int, default=DEFAULT_OVERLAP)
    parser.add_argument("--no-embed", action="store_true", help="Only chunk, skip embedding")
    args = parser.parse_args()

    project_path = Path(args.path) if args.path else default_wikis_dir() / args.project
    page_path = project_path / args.page

    if not page_path.exists():
        print(json.dumps({"error": f"Page not found: {page_path}"}), file=sys.stderr)
        sys.exit(1)

    text = page_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    page_id = page_path.stem

    chunks = chunk_markdown(text, args.target, args.max, args.min, args.overlap)

    result = {
        "page_id": page_id,
        "chunk_count": len(chunks),
        "chunks": chunks,
    }

    if not args.no_embed:
        config_path = project_path / ".wiki" / "config.json"
        config = {}
        if config_path.exists():
            config = json.loads(config_path.read_text(encoding="utf-8"))

        embeddings = []
        for chunk in chunks:
            embed_text = f"{fm.get('title', page_id)}\n\n{chunk['heading_path']}\n\n{chunk['text']}"
            emb = fetch_embedding(embed_text, config)
            embeddings.append(emb)

        if any(emb for emb in embeddings):
            store_in_lancedb(project_path, page_id, chunks, embeddings, config)
            result["embedded"] = True
        else:
            result["embedded"] = False

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()