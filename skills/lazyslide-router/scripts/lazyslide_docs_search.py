#!/usr/bin/env python3
"""Search bundled LazySlide skill references."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9_.$-]+", text.lower())


def score_text(query_terms: list[str], text: str) -> tuple[int, list[str]]:
    lower = text.lower()
    hits = [term for term in query_terms if term in lower]
    return sum(lower.count(term) for term in hits), hits


def iter_markdown(root: Path) -> list[Path]:
    return sorted(p for p in (root / "skills").glob("lazyslide-*/**/*.md") if p.is_file())


def make_snippet(text: str, terms: list[str], width: int = 220) -> str:
    lower = text.lower()
    positions = [lower.find(term) for term in terms if lower.find(term) >= 0]
    start = max(min(positions) - width // 4, 0) if positions else 0
    snippet = " ".join(text[start : start + width].split())
    return snippet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", "-q", required=True, help="Search terms.")
    parser.add_argument("--limit", "-n", type=int, default=8, help="Maximum results.")
    parser.add_argument(
        "--root",
        type=Path,
        default=repo_root(),
        help="Repository root containing skills/. Defaults to this script's repository.",
    )
    args = parser.parse_args()

    query_terms = tokenize(args.query)
    if not query_terms:
        raise SystemExit("Query did not contain searchable terms.")

    results = []
    for path in iter_markdown(args.root):
        text = path.read_text(encoding="utf-8")
        score, hits = score_text(query_terms, text)
        if score:
            results.append((score, path, hits, make_snippet(text, hits)))

    results.sort(key=lambda item: (-item[0], str(item[1])))
    if not results:
        print("No bundled LazySlide reference matches found.")
        return 1

    for score, path, hits, snippet in results[: args.limit]:
        rel = path.relative_to(args.root)
        print(f"{rel}  score={score}  hits={','.join(sorted(set(hits)))}")
        print(f"  {snippet}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

