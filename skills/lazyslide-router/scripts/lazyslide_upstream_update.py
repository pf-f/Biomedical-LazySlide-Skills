#!/usr/bin/env python3
"""Create a monthly LazySlide upstream metadata diff report."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import urllib.error
import urllib.request


UPSTREAMS = {
    "readthedocs-index": "https://lazyslide.readthedocs.io/en/latest/",
    "readthedocs-searchindex": "https://lazyslide.readthedocs.io/en/latest/searchindex.js",
    "readthedocs-objects": "https://lazyslide.readthedocs.io/en/latest/objects.inv",
    "lazyslide-main-tree": "https://api.github.com/repos/rendeirolab/LazySlide/git/trees/main?recursive=1",
    "lazyslide-main-releases": "https://api.github.com/repos/rendeirolab/LazySlide/releases/latest",
    "tutorials-main-tree": "https://api.github.com/repos/rendeirolab/lazyslide-tutorials/git/trees/main?recursive=1",
    "models-main-tree": "https://api.github.com/repos/rendeirolab/lazyslide-models/git/trees/main?recursive=1",
    "models-main-releases": "https://api.github.com/repos/rendeirolab/lazyslide-models/releases/latest",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str, timeout: int = 45) -> tuple[bytes, dict[str, str]]:
    request = urllib.request.Request(url, headers={"User-Agent": "lazyslide-skill-updater"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        headers = {key.lower(): value for key, value in response.headers.items()}
        return response.read(), headers


def text_metadata(name: str, url: str, data: bytes, headers: dict[str, str]) -> dict[str, object]:
    text = data.decode("utf-8", errors="replace")
    headings = re.findall(r"<h[12][^>]*>(.*?)</h[12]>", text, flags=re.I | re.S)
    headings = [re.sub(r"<[^>]+>", "", item).strip() for item in headings[:30]]
    api_like = sorted(set(re.findall(r"lazyslide(?:_models)?\.[A-Za-z0-9_.$]+", text)))[:300]
    return {
        "name": name,
        "url": url,
        "status": "ok",
        "bytes": len(data),
        "sha256": sha256_bytes(data),
        "etag": headers.get("etag"),
        "last_modified": headers.get("last-modified"),
        "heading_sample": headings,
        "api_symbol_sample": api_like,
    }


def tree_metadata(name: str, url: str, data: bytes, headers: dict[str, str]) -> dict[str, object]:
    parsed = json.loads(data.decode("utf-8"))
    tree = sorted(parsed.get("tree", []), key=lambda item: item.get("path", ""))
    paths = [item.get("path", "") for item in tree if item.get("type") == "blob"]
    interesting = [
        path
        for path in paths
        if path.endswith((".py", ".md", ".rst", ".ipynb", ".toml", ".yaml", ".yml", ".bib"))
        and (
            path.startswith(("docs/", "src/", "tutorials/", ".github/"))
            or path in {"README.md", "pyproject.toml", ".readthedocs.yaml", "uv.lock", "references.bib"}
        )
    ]
    digest_input = "\n".join(f"{item.get('path')} {item.get('sha')} {item.get('size', '')}" for item in tree).encode()
    return {
        "name": name,
        "url": url,
        "status": "ok",
        "tree_sha": parsed.get("sha"),
        "truncated": parsed.get("truncated"),
        "blob_count": len(paths),
        "interesting_count": len(interesting),
        "interesting_path_sample": interesting[:300],
        "sha256": sha256_bytes(digest_input),
        "etag": headers.get("etag"),
        "last_modified": headers.get("last-modified"),
    }


def release_metadata(name: str, url: str, data: bytes, headers: dict[str, str]) -> dict[str, object]:
    parsed = json.loads(data.decode("utf-8"))
    return {
        "name": name,
        "url": url,
        "status": "ok",
        "tag_name": parsed.get("tag_name"),
        "name_field": parsed.get("name"),
        "published_at": parsed.get("published_at"),
        "html_url": parsed.get("html_url"),
        "sha256": sha256_bytes(data),
        "etag": headers.get("etag"),
        "last_modified": headers.get("last-modified"),
    }


def collect(max_sources: int | None = None) -> dict[str, object]:
    entries = []
    for idx, (name, url) in enumerate(UPSTREAMS.items()):
        if max_sources is not None and idx >= max_sources:
            break
        try:
            data, headers = fetch(url)
            if "git/trees" in url:
                entry = tree_metadata(name, url, data, headers)
            elif "releases/latest" in url:
                entry = release_metadata(name, url, data, headers)
            else:
                entry = text_metadata(name, url, data, headers)
        except Exception as exc:  # noqa: BLE001
            entry = {"name": name, "url": url, "status": "error", "error": f"{type(exc).__name__}: {exc}"}
        entries.append(entry)
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "entries": entries}


def load_snapshot(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def compare(old: dict[str, object] | None, new: dict[str, object]) -> dict[str, list[str]]:
    old_entries = {entry["name"]: entry for entry in old.get("entries", [])} if old else {}
    new_entries = {entry["name"]: entry for entry in new.get("entries", [])}
    added = sorted(set(new_entries) - set(old_entries))
    removed = sorted(set(old_entries) - set(new_entries))
    changed = []
    unchanged = []
    for name in sorted(set(new_entries) & set(old_entries)):
        if new_entries[name].get("sha256") != old_entries[name].get("sha256") or new_entries[name].get("status") != old_entries[name].get("status"):
            changed.append(name)
        else:
            unchanged.append(name)
    return {"added": added, "removed": removed, "changed": changed, "unchanged": unchanged}


def collection_errors(snapshot: dict[str, object]) -> list[dict[str, object]]:
    return [entry for entry in snapshot.get("entries", []) if entry.get("status") != "ok"]


def has_semantic_changes(diff: dict[str, list[str]]) -> bool:
    return any(diff[key] for key in ("added", "removed", "changed"))


def project_report_dir(root: Path, report_dir: Path) -> Path:
    candidate = report_dir if report_dir.is_absolute() else root / report_dir
    candidate = candidate.resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"report directory must remain inside project root: {candidate}")
    return candidate


DEFAULT_REPORT_DIR = Path("skills/lazyslide-router/references/upstream-reports")


def write_report(root: Path, snapshot: dict[str, object], diff: dict[str, list[str]], report_dir: Path) -> Path:
    report_dir = report_dir if report_dir.is_absolute() else root / report_dir
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    report_path = report_dir / f"upstream-docs-update-{stamp}.md"
    lines = [
        f"# LazySlide Upstream Update Report: {stamp}",
        "",
        f"Generated at: `{snapshot['generated_at']}`",
        "",
        "## Summary",
        "",
        f"- Added sources: {len(diff['added'])}",
        f"- Removed sources: {len(diff['removed'])}",
        f"- Changed sources: {len(diff['changed'])}",
        f"- Unchanged sources: {len(diff['unchanged'])}",
        "",
        "## Changed",
        "",
    ]
    lines.extend([f"- {name}" for name in diff["changed"]] or ["- none"])
    lines.extend(["", "## Source Snapshot", ""])
    for entry in snapshot["entries"]:
        lines.append(f"### {entry['name']}")
        lines.append("")
        lines.append(f"- Status: `{entry.get('status')}`")
        lines.append(f"- URL: {entry.get('url')}")
        if entry.get("tag_name"):
            lines.append(f"- Latest tag: `{entry.get('tag_name')}`")
        if entry.get("interesting_count") is not None:
            lines.append(f"- Interesting tracked paths: {entry.get('interesting_count')}")
        if entry.get("api_symbol_sample"):
            lines.append(f"- API symbol sample count: {len(entry.get('api_symbol_sample', []))}")
        if entry.get("error"):
            lines.append(f"- Error: `{entry.get('error')}`")
        lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    latest = report_dir / "latest-upstream-docs-update.md"
    latest.write_text(report_path.read_text(encoding="utf-8"), encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=repo_root())
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--update-snapshot", action="store_true")
    parser.add_argument("--snapshot-only", action="store_true", help="Print the collected snapshot without writing files.")
    parser.add_argument("--max-sources", type=int, default=None, help="Debug limit for fast smoke tests.")
    args = parser.parse_args()

    root = args.project_root.resolve()
    snapshot_path = root / "skills" / "lazyslide-router" / "references" / "upstream-snapshot.json"
    previous = load_snapshot(snapshot_path)
    current = collect(max_sources=args.max_sources)

    if args.snapshot_only:
        print(json.dumps(current, indent=2, sort_keys=True))
        return 2 if collection_errors(current) else 0

    errors = collection_errors(current)
    if errors:
        names = ", ".join(str(entry.get("name", "<unknown>")) for entry in errors)
        print(f"Incomplete upstream collection; preserving previous snapshot. Failed: {names}", file=sys.stderr)
        return 2

    diff = compare(previous, current)

    if not has_semantic_changes(diff):
        print("No upstream changes; no files written.")
        print(json.dumps({"diff": diff, "generated_at": current["generated_at"]}, indent=2, sort_keys=True))
        return 0

    if args.write_report:
        try:
            report_dir = project_report_dir(root, args.report_dir)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        report_path = write_report(root, current, diff, report_dir)
        print(f"Wrote {report_path.relative_to(root)}")

    if args.update_snapshot:
        snapshot_path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Updated {snapshot_path.relative_to(root)}")

    print(json.dumps({"diff": diff, "generated_at": current["generated_at"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
