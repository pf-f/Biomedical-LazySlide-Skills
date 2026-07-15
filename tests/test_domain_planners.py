#!/usr/bin/env python3
"""Behavior checks for lightweight LazySlide domain planning helpers."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODEL_PLANNER = ROOT / "skills" / "lazyslide-models-features" / "scripts" / "lazyslide_model_plan.py"


class DomainPlannerTests(unittest.TestCase):
    def run_model(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MODEL_PLANNER), *args],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )

    def test_feature_extraction_renders_explicit_runtime_choices(self):
        result = self.run_model(
            "--workflow",
            "feature-extraction",
            "--model",
            "uni",
            "--tile-key",
            "tiles_20x",
            "--device",
            "cpu",
            "--batch-size",
            "4",
            "--num-workers",
            "1",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('device="cpu"', result.stdout)
        self.assertIn("batch_size=4", result.stdout)
        self.assertIn("num_workers=1", result.stdout)

    def test_aggregation_refuses_to_guess_feature_key(self):
        result = self.run_model("--workflow", "aggregation", "--model", "uni", "--tile-key", "tiles_20x")

        self.assertEqual(result.returncode, 2)
        self.assertIn("--feature-key", result.stderr)

    def test_prediction_uses_only_supported_runtime_parameters(self):
        result = self.run_model(
            "--workflow",
            "prediction",
            "--model",
            "path2space",
            "--tile-key",
            "spots",
            "--device",
            "cpu",
            "--batch-size",
            "16",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        skeleton = result.stdout.split("Skeleton:", 1)[1]
        self.assertIn('device="cpu"', skeleton)
        self.assertIn("batch_size=16", skeleton)
        self.assertNotIn("num_workers", skeleton)


if __name__ == "__main__":
    unittest.main()
