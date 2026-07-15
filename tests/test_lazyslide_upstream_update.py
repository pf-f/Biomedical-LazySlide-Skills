#!/usr/bin/env python3
"""Tests for safe, low-noise LazySlide upstream snapshot updates."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "lazyslide-router" / "scripts" / "lazyslide_upstream_update.py"


def load_module():
    name = "lazyslide_upstream_update_under_test"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def snapshot(generated_at: str, *, status: str = "ok", digest: str = "stable") -> dict[str, object]:
    entry: dict[str, object] = {
        "name": "source-a",
        "url": "https://example.invalid/source-a",
        "status": status,
    }
    if status == "ok":
        entry["sha256"] = digest
    else:
        entry["error"] = "HTTPError: HTTP Error 429: Too Many Requests"
    return {"generated_at": generated_at, "entries": [entry]}


class LazySlideUpstreamUpdateTests(unittest.TestCase):
    def run_main(self, updater, root: Path, current: dict[str, object], *extra: str):
        stdout = io.StringIO()
        stderr = io.StringIO()
        argv = [str(SCRIPT), "--project-root", str(root), *extra]
        with (
            mock.patch.object(updater, "collect", return_value=current),
            mock.patch.object(sys, "argv", argv),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            code = updater.main()
        return code, stdout.getvalue(), stderr.getvalue()

    def write_previous(self, root: Path, previous: dict[str, object]) -> Path:
        path = root / "skills" / "lazyslide-router" / "references" / "upstream-snapshot.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(previous, indent=2) + "\n", encoding="utf-8")
        return path

    def test_failed_collection_never_replaces_previous_snapshot(self):
        updater = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            previous = snapshot("2026-01-01T00:00:00+00:00")
            path = self.write_previous(root, previous)
            before = path.read_bytes()

            code, _stdout, stderr = self.run_main(
                updater,
                root,
                snapshot("2026-02-01T00:00:00+00:00", status="error"),
                "--update-snapshot",
            )

            self.assertEqual(code, 2)
            self.assertEqual(path.read_bytes(), before)
            self.assertIn("source-a", stderr)

    def test_no_semantic_change_writes_neither_snapshot_nor_report(self):
        updater = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            previous = snapshot("2026-01-01T00:00:00+00:00")
            path = self.write_previous(root, previous)
            before = path.read_bytes()
            report_dir = root / "reports"

            code, stdout, _stderr = self.run_main(
                updater,
                root,
                snapshot("2026-02-01T00:00:00+00:00"),
                "--write-report",
                "--report-dir",
                "reports",
                "--update-snapshot",
            )

            self.assertEqual(code, 0)
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse(report_dir.exists())
            self.assertIn("no upstream changes", stdout.lower())

    def test_snapshot_only_prints_full_collection_without_writing(self):
        updater = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            current = snapshot("2026-02-01T00:00:00+00:00")

            code, stdout, _stderr = self.run_main(updater, root, current, "--snapshot-only")

            self.assertEqual(code, 0)
            self.assertEqual(json.loads(stdout), current)
            self.assertFalse((root / "skills").exists())

    def test_report_directory_must_remain_inside_project(self):
        updater = load_module()
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp)
            self.write_previous(root, snapshot("2026-01-01T00:00:00+00:00", digest="old"))
            target = Path(outside) / "reports"

            code, _stdout, stderr = self.run_main(
                updater,
                root,
                snapshot("2026-02-01T00:00:00+00:00", digest="new"),
                "--write-report",
                "--report-dir",
                str(target),
            )

            self.assertEqual(code, 2)
            self.assertFalse(target.exists())
            self.assertIn("project root", stderr)

    def test_tree_digest_is_independent_of_api_item_order(self):
        updater = load_module()
        first = {
            "sha": "tree",
            "truncated": False,
            "tree": [
                {"path": "src/b.py", "sha": "b", "size": 2, "type": "blob"},
                {"path": "src/a.py", "sha": "a", "size": 1, "type": "blob"},
            ],
        }
        second = {**first, "tree": list(reversed(first["tree"]))}

        one = updater.tree_metadata("tree", "https://example.invalid", json.dumps(first).encode(), {})
        two = updater.tree_metadata("tree", "https://example.invalid", json.dumps(second).encode(), {})

        self.assertEqual(one["sha256"], two["sha256"])


if __name__ == "__main__":
    unittest.main()
