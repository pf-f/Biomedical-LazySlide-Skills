#!/usr/bin/env python3
"""Tests for the LazySlide environment inspector.

These tests intentionally use only the Python standard library and do not
require LazySlide, model packages, slide readers, network access, or downloads.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSPECTOR = ROOT / "skills" / "lazyslide-router" / "scripts" / "lazyslide_inspect_env.py"


class LazySlideInspectEnvTests(unittest.TestCase):
    def run_inspector(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONNOUSERSITE"] = "1"
        return subprocess.run(
            [sys.executable, str(INSPECTOR), *args],
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
        )

    def run_json(self, *args: str) -> dict[str, object]:
        result = self.run_inspector("--json", *args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_json_runs_without_lazyslide_installed(self) -> None:
        report = self.run_json()
        self.assertIn("python", report)
        self.assertIn("executable", report)
        self.assertIn("platform", report)
        self.assertIn("packages", report)
        self.assertIn("commands", report)
        self.assertIn("torch", report)

        packages = report["packages"]
        self.assertIsInstance(packages, dict)
        for package in ["lazyslide", "wsidata", "lazyslide_models"]:
            self.assertIn(package, packages)
            status = packages[package]
            self.assertIsInstance(status, dict)
            self.assertIn("installed", status)
            self.assertIn("import_ok", status)
            self.assertIn("version", status)

        summary = report["summary"]
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary["profile"], "full")
        self.assertEqual(summary["blocking_missing"], [])

    def test_redact_paths_hides_python_prefix_for_executable(self) -> None:
        report = self.run_json("--redact-paths")
        executable = report["executable"]
        self.assertIsInstance(executable, str)

        prefix = sys.prefix.rstrip("/")
        if sys.executable.startswith(prefix + "/"):
            self.assertTrue(executable.startswith("<python-prefix>/"), executable)
            self.assertNotIn(prefix, executable)

    def test_redact_hardware_masks_platform_and_cuda_names(self) -> None:
        report = self.run_json("--redact-hardware")
        self.assertEqual(report["platform"], "<platform-redacted>")

        torch = report["torch"]
        self.assertIsInstance(torch, dict)
        if "cuda_device_count" in torch:
            self.assertEqual(torch["cuda_device_count"], "<redacted>")
        if "cuda_devices" in torch:
            self.assertEqual(torch["cuda_devices"], ["<redacted>"])

    def test_models_listing_is_optional_and_json_safe(self) -> None:
        report = self.run_json("--models")
        self.assertIn("models", report)
        models = report["models"]
        self.assertIsInstance(models, dict)
        self.assertIn("available", models)

    def test_profiles_are_listed_and_core_limits_package_scope(self) -> None:
        list_result = self.run_inspector("--list-profiles")
        self.assertEqual(list_result.returncode, 0, list_result.stderr)
        profiles = set(list_result.stdout.split())
        self.assertTrue({"core", "analysis", "models-cpu", "models-gpu", "spatial-omics"} <= profiles)

        report = self.run_json("--profile", "core")
        self.assertEqual(report["profile"], "core")
        packages = report["packages"]
        self.assertIsInstance(packages, dict)
        self.assertIn("lazyslide", packages)
        self.assertIn("openslide", packages)
        self.assertNotIn("scanpy", packages)

        summary = report["summary"]
        self.assertIsInstance(summary, dict)
        self.assertEqual(summary["profile"], "core")
        self.assertIn("ready", summary)

    def test_fail_on_missing_uses_readiness_summary(self) -> None:
        result = self.run_inspector("--profile", "core", "--fail-on-missing", "--json")
        self.assertIn(result.returncode, {0, 2}, result.stderr)
        report = json.loads(result.stdout)
        ready = report["summary"]["ready"]
        self.assertEqual(result.returncode, 0 if ready else 2)

    def test_legacy_fail_on_missing_is_report_only_without_profile(self) -> None:
        result = self.run_inspector("--fail-on-missing", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["summary"]["profile"], "full")
        self.assertEqual(report["summary"]["blocking_missing"], [])


if __name__ == "__main__":
    unittest.main()
