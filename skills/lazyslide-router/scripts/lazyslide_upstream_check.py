#!/usr/bin/env python3
"""Search LazySlide upstream source indexes for likely documentation/API matches."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request


SOURCES = {
    "readthedocs": "https://lazyslide.readthedocs.io/en/latest/searchindex.js",
    "lazyslide-tree": "https://api.github.com/repos/rendeirolab/LazySlide/git/trees/main?recursive=1",
    "tutorials-tree": "https://api.github.com/repos/rendeirolab/lazyslide-tutorials/git/trees/main?recursive=1",
    "models-tree": "https://api.github.com/repos/rendeirolab/lazyslide-models/git/trees/main?recursive=1",
}


def fetch_text(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "lazyslide-skill-updater"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def readthedocs_matches(text: str, query: str, limit: int) -> list[dict[str, str]]:
    lower = text.lower()
    query_l = query.lower()
    matches = []
    for marker in ["docnames:", "titles:"]:
        idx = lower.find(query_l)
        if idx >= 0:
            start = max(idx - 140, 0)
            stop = min(idx + 240, len(text))
            matches.append({"source": "readthedocs-searchindex", "url": SOURCES["readthedocs"], "snippet": text[start:stop]})
            break
    return matches[:limit]


def github_tree_matches(source_name: str, text: str, query: str, limit: int) -> list[dict[str, str]]:
    data = json.loads(text)
    query_l = query.lower()
    repo_url = {
        "lazyslide-tree": "https://github.com/rendeirolab/LazySlide/blob/main/",
        "tutorials-tree": "https://github.com/rendeirolab/lazyslide-tutorials/blob/main/",
        "models-tree": "https://github.com/rendeirolab/lazyslide-models/blob/main/",
    }[source_name]
    out = []
    for item in data.get("tree", []):
        path = item.get("path", "")
        if query_l in path.lower():
            out.append({"source": source_name, "path": path, "url": repo_url + path})
        if len(out) >= limit:
            break
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", "-q", required=True, help="Search term.")
    parser.add_argument("--limit", "-n", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    all_matches = []
    errors = []
    for name, url in SOURCES.items():
        try:
            text = fetch_text(url)
            if name == "readthedocs":
                matches = readthedocs_matches(text, args.query, args.limit)
            else:
                matches = github_tree_matches(name, text, args.query, args.limit)
            all_matches.extend(matches)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            errors.append({"source": name, "url": url, "error": f"{type(exc).__name__}: {exc}"})

    payload = {"query": args.query, "matches": all_matches[: args.limit], "errors": errors}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for match in payload["matches"]:
            print(match.get("url", ""))
            if match.get("path"):
                print(f"  path: {match['path']}")
            if match.get("snippet"):
                print(f"  snippet: {' '.join(match['snippet'].split())[:260]}")
        if errors:
            print("\nErrors:")
            for error in errors:
                print(f"  {error['source']}: {error['error']}")
    return 0 if all_matches else 1


if __name__ == "__main__":
    raise SystemExit(main())

