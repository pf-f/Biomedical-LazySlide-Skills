#!/usr/bin/env python3
"""Tests for the LazySlide environment planner."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "lazyslide-router" / "scripts" / "lazyslide_env.py"


def load_module():
    name = "lazyslide_env_under_test"
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def found(cmd: str) -> str:
    return f"/usr/bin/{cmd}"


def missing(cmd: str) -> None:
    return None


def run_with_output(func):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        code = func()
    return code, stdout.getvalue(), stderr.getvalue()


class LazySlideEnvTests(unittest.TestCase):
    def test_plan_models_gpu_requires_torch_index_url(self):
        env = load_module()

        code, stdout, stderr = run_with_output(
            lambda: env.main(["plan", "--profile", "models-gpu", "--json"], environ={}, which=missing)
        )

        payload = json.loads(stdout)
        self.assertEqual(code, 2)
        self.assertEqual(payload["profile"], "models-gpu")
        self.assertEqual(payload["commands"], [])
        self.assertIn("--torch-index-url", payload["refusal"])
        self.assertIn("--torch-index-url", stderr)

    def test_conda_plan_uses_named_env_when_base_is_active(self):
        env = load_module()

        plan = env.build_plan(
            profile="core",
            manager="conda",
            env_name="lazyslide-ci",
            python="3.11",
            torch_index_url=None,
            hpc=False,
            environ={"CONDA_DEFAULT_ENV": "base"},
            which=found,
        )

        self.assertIsNone(plan.refusal)
        self.assertEqual(plan.manager, "conda")
        self.assertEqual(plan.commands[0], "conda create -y -n lazyslide-ci python=3.11 pip")
        self.assertIn("openslide-bin", " ".join(plan.commands))
        self.assertTrue(all(" -n base " not in command for command in plan.commands))
        self.assertTrue(any("base" in warning and "lazyslide-ci" in warning for warning in plan.warnings))

    def test_refuses_base_env_name_for_conda(self):
        env = load_module()

        plan = env.build_plan(
            profile="core",
            manager="conda",
            env_name="base",
            python="3.11",
            torch_index_url=None,
            hpc=False,
            environ={"CONDA_DEFAULT_ENV": "base"},
            which=found,
        )

        self.assertEqual(plan.commands, [])
        self.assertIsNotNone(plan.refusal)
        self.assertIn("base environment", plan.refusal)

    def test_gpu_plan_installs_torch_before_model_dependencies(self):
        env = load_module()

        plan = env.build_plan(
            profile="models-gpu",
            manager="conda",
            env_name="lazyslide-gpu",
            python="3.11",
            torch_index_url="https://download.pytorch.org/whl/cu124",
            hpc=False,
            environ={},
            which=found,
        )

        self.assertIsNone(plan.refusal)
        torch_command_index = next(i for i, command in enumerate(plan.commands) if "--index-url" in command)
        model_command_index = next(i for i, command in enumerate(plan.commands) if "lazyslide-models" in command)
        self.assertLess(torch_command_index, model_command_index)

    def test_gpu_requirements_emit_is_refused(self):
        env = load_module()

        code, _stdout, stderr = run_with_output(
            lambda: env.main(
                [
                    "emit",
                    "--profile",
                    "models-gpu",
                    "--torch-index-url",
                    "https://download.pytorch.org/whl/cu124",
                    "--format",
                    "requirements",
                ],
                environ={},
                which=found,
            )
        )

        self.assertEqual(code, 2)
        self.assertIn("GPU requirements", stderr)

    def test_create_hpc_never_runs_commands(self):
        env = load_module()
        calls = []

        def runner(args):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0)

        code, stdout, stderr = run_with_output(
            lambda: env.main(["create", "--hpc", "--manager", "venv"], environ={}, which=found, runner=runner)
        )

        payload = json.loads(stdout)
        self.assertEqual(code, 2)
        self.assertTrue(payload["commands"])
        self.assertEqual(calls, [])
        self.assertIn("--hpc mode", stderr)

    def test_emit_requirements_output_requires_overwrite(self):
        env = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "requirements.txt"

            code = env.main(
                ["emit", "--profile", "analysis", "--format", "requirements", "--output", str(output)],
                environ={},
                which=missing,
            )

            self.assertEqual(code, 0)
            text = output.read_text(encoding="utf-8")
            self.assertIn("lazyslide\n", text)
            self.assertIn("scanpy\n", text)

            code, _stdout, stderr = run_with_output(
                lambda: env.main(
                    ["emit", "--profile", "analysis", "--format", "requirements", "--output", str(output)],
                    environ={},
                    which=missing,
                )
            )

            self.assertEqual(code, 1)
            self.assertIn("already exists", stderr)

            code = env.main(
                [
                    "emit",
                    "--profile",
                    "analysis",
                    "--format",
                    "requirements",
                    "--output",
                    str(output),
                    "--overwrite",
                ],
                environ={},
                which=missing,
            )

            self.assertEqual(code, 0)

    def test_inspect_reuses_existing_collector(self):
        env = load_module()
        calls = []

        class DummyInspector:
            @staticmethod
            def collect(include_models, redact_paths, redact_hardware_info, profile=None):
                calls.append((include_models, redact_paths, redact_hardware_info, profile))
                return {"ok": True, "summary": {"ready": True}}

            @staticmethod
            def print_text(report):
                raise AssertionError(f"unexpected text output: {report}")

        original = env._load_inspector
        env._load_inspector = lambda: DummyInspector
        try:
            code, stdout, _stderr = run_with_output(
                lambda: env.main(
                    ["inspect", "--json", "--models", "--profile", "core", "--redact-paths", "--redact-hardware"]
                )
            )
        finally:
            env._load_inspector = original

        self.assertEqual(code, 0)
        self.assertEqual(calls, [(True, True, True, "core")])
        self.assertEqual(json.loads(stdout), {"ok": True, "summary": {"ready": True}})

    def test_spatial_omics_profile_includes_model_and_mofa_stack(self):
        env = load_module()

        packages = env.packages_for("spatial-omics")
        imports = env.imports_for("spatial-omics")

        for package in ["lazyslide-models", "torch", "timm", "muon", "mofapy2", "lifelines"]:
            self.assertIn(package, packages)
        for module in ["lazyslide_models", "torchvision", "huggingface_hub", "shapely"]:
            self.assertIn(module, imports)


if __name__ == "__main__":
    unittest.main()
