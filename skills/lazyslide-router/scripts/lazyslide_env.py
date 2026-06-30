#!/usr/bin/env python3
"""Inspect, plan, emit, and create LazySlide Python environments."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence


PROFILES = ("core", "analysis", "models-cpu", "models-gpu", "spatial-omics")
MANAGERS = ("auto", "micromamba", "mamba", "conda", "venv")
CONDA_MANAGERS = ("micromamba", "mamba", "conda")
TORCH_PACKAGES = ("torch", "torchvision")

DEFAULT_ENV_NAME = "lazyslide"
DEFAULT_PYTHON = "3.11"

CORE_PACKAGES = ("lazyslide", "wsidata", "openslide-python", "openslide-bin", "tiffslide")
ANALYSIS_PACKAGES = CORE_PACKAGES + ("scanpy", "anndata", "geopandas", "shapely")
MODELS_PACKAGES = CORE_PACKAGES + (
    "lazyslide-models",
    "torch",
    "torchvision",
    "timm",
    "huggingface-hub",
)
SPATIAL_OMICS_PACKAGES = ANALYSIS_PACKAGES + (
    "lazyslide-models",
    "torch",
    "torchvision",
    "timm",
    "huggingface-hub",
    "muon",
    "mofapy2",
    "lifelines",
)

PROFILE_PACKAGES = {
    "core": CORE_PACKAGES,
    "analysis": ANALYSIS_PACKAGES,
    "models-cpu": MODELS_PACKAGES,
    "models-gpu": MODELS_PACKAGES,
    "spatial-omics": SPATIAL_OMICS_PACKAGES,
}

PROFILE_IMPORTS = {
    "core": ("lazyslide", "wsidata", "openslide", "tiffslide"),
    "analysis": ("lazyslide", "wsidata", "openslide", "tiffslide", "scanpy", "anndata", "geopandas", "shapely"),
    "models-cpu": (
        "lazyslide",
        "wsidata",
        "openslide",
        "tiffslide",
        "lazyslide_models",
        "torch",
        "torchvision",
        "timm",
        "huggingface_hub",
    ),
    "models-gpu": (
        "lazyslide",
        "wsidata",
        "openslide",
        "tiffslide",
        "lazyslide_models",
        "torch",
        "torchvision",
        "timm",
        "huggingface_hub",
    ),
    "spatial-omics": (
        "lazyslide",
        "wsidata",
        "openslide",
        "tiffslide",
        "scanpy",
        "anndata",
        "geopandas",
        "shapely",
        "lazyslide_models",
        "torch",
        "torchvision",
        "timm",
        "huggingface_hub",
        "muon",
        "mofapy2",
        "lifelines",
    ),
}


@dataclass
class EnvPlan:
    profile: str
    manager: str
    env_name: str
    commands: list[str]
    warnings: list[str]
    refusal: str | None
    success_checks: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "profile": self.profile,
            "manager": self.manager,
            "env_name": self.env_name,
            "commands": self.commands,
            "warnings": self.warnings,
            "refusal": self.refusal,
            "success_checks": self.success_checks,
        }


Which = Callable[[str], str | None]
Runner = Callable[[Sequence[str]], subprocess.CompletedProcess[object]]


def command(args: Sequence[str]) -> str:
    return " ".join(shlex.quote(str(arg)) for arg in args)


def unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def packages_for(profile: str) -> list[str]:
    return unique(PROFILE_PACKAGES[profile])


def imports_for(profile: str) -> list[str]:
    return list(PROFILE_IMPORTS[profile])


def resolve_manager(requested: str, which: Which) -> str:
    if requested != "auto":
        return requested
    for candidate in CONDA_MANAGERS:
        if which(candidate):
            return candidate
    return "venv"


def python_executable_for_venv(python: str) -> str:
    if "/" in python or "\\" in python or python.startswith("python"):
        return python
    return f"python{python}"


def venv_python(env_name: str) -> str:
    if os.name == "nt":
        return str(Path(env_name) / "Scripts" / "python.exe")
    return str(Path(env_name) / "bin" / "python")


def active_conda_env(environ: dict[str, str]) -> str | None:
    return environ.get("CONDA_DEFAULT_ENV") or None


def conda_base_active(environ: dict[str, str]) -> bool:
    return active_conda_env(environ) == "base" and not environ.get("VIRTUAL_ENV")


def split_for_gpu(packages: Sequence[str]) -> tuple[list[str], list[str]]:
    torch = [pkg for pkg in packages if pkg in TORCH_PACKAGES]
    other = [pkg for pkg in packages if pkg not in TORCH_PACKAGES]
    return other, torch


def install_commands_for(
    manager: str,
    env_name: str,
    packages: Sequence[str],
    torch_index_url: str | None,
) -> list[str]:
    if manager == "venv":
        pip = [venv_python(env_name), "-m", "pip"]
    else:
        pip = [manager, "run", "-n", env_name, "python", "-m", "pip"]

    commands = [command([*pip, "install", "--upgrade", "pip"])]
    if torch_index_url:
        non_torch, torch_packages = split_for_gpu(packages)
        if torch_packages:
            commands.append(command([*pip, "install", "--index-url", torch_index_url, *torch_packages]))
        if non_torch:
            commands.append(command([*pip, "install", *non_torch]))
    else:
        commands.append(command([*pip, "install", *packages]))
    return commands


def success_checks_for(manager: str, env_name: str, profile: str) -> list[str]:
    code = "import " + ", ".join(imports_for(profile))
    if profile == "models-gpu":
        code += "; import torch; raise SystemExit(0 if torch.cuda.is_available() else 1)"
    if manager == "venv":
        base = [venv_python(env_name), "-c", code]
    else:
        base = [manager, "run", "-n", env_name, "python", "-c", code]
    return [command(base)]


def build_plan(
    *,
    profile: str,
    manager: str,
    env_name: str,
    python: str,
    torch_index_url: str | None,
    hpc: bool,
    environ: dict[str, str] | None = None,
    which: Which = shutil.which,
) -> EnvPlan:
    env = dict(os.environ if environ is None else environ)
    resolved_manager = resolve_manager(manager, which)
    warnings: list[str] = []
    refusal: str | None = None

    if profile == "models-gpu" and not torch_index_url:
        refusal = "models-gpu requires --torch-index-url so GPU torch wheels are selected deliberately."

    if hpc:
        warnings.append("HPC mode is non-mutating; use plan or emit output in a scheduler/provisioning workflow.")

    if resolved_manager in CONDA_MANAGERS:
        if env_name == "base":
            refusal = "Refusing to mutate the conda base environment; choose a non-base --env-name."
        elif conda_base_active(env):
            warnings.append(
                f"Active conda env is base; planning a named {resolved_manager} environment ({env_name}) instead."
            )
        if manager != "auto" and which(resolved_manager) is None:
            warnings.append(f"{resolved_manager!r} was requested but was not found on PATH.")
    elif resolved_manager == "venv":
        py = python_executable_for_venv(python)
        if which(py) is None:
            warnings.append(f"{py!r} was not found on PATH; create may fail unless it is available.")

    packages = packages_for(profile)
    commands: list[str] = []
    if refusal is None:
        if resolved_manager == "venv":
            py = python_executable_for_venv(python)
            commands.append(command([py, "-m", "venv", env_name]))
        else:
            commands.append(command([resolved_manager, "create", "-y", "-n", env_name, f"python={python}", "pip"]))
        commands.extend(install_commands_for(resolved_manager, env_name, packages, torch_index_url))

    return EnvPlan(
        profile=profile,
        manager=resolved_manager,
        env_name=env_name,
        commands=commands,
        warnings=warnings,
        refusal=refusal,
        success_checks=success_checks_for(resolved_manager, env_name, profile),
    )


def plan_to_json(plan: EnvPlan) -> str:
    return json.dumps(plan.as_dict(), indent=2, sort_keys=True)


def format_requirements(plan: EnvPlan, torch_index_url: str | None) -> str:
    lines: list[str] = []
    if torch_index_url:
        lines.append(f"--extra-index-url {torch_index_url}")
    lines.extend(packages_for(plan.profile))
    return "\n".join(lines) + "\n"


def format_environment_yml(plan: EnvPlan, python: str, torch_index_url: str | None) -> str:
    pip_packages: list[str] = []
    if torch_index_url:
        pip_packages.append(f"--extra-index-url {torch_index_url}")
    pip_packages.extend(packages_for(plan.profile))
    lines = [
        f"name: {plan.env_name}",
        "channels:",
        "  - conda-forge",
        "dependencies:",
        f"  - python={python}",
        "  - pip",
        "  - pip:",
    ]
    lines.extend(f"      - {pkg}" for pkg in pip_packages)
    return "\n".join(lines) + "\n"


def format_emit(plan: EnvPlan, fmt: str, python: str, torch_index_url: str | None) -> str:
    if fmt == "commands":
        return "\n".join(plan.commands) + ("\n" if plan.commands else "")
    if fmt == "requirements":
        return format_requirements(plan, torch_index_url)
    if fmt == "environment-yml":
        return format_environment_yml(plan, python, torch_index_url)
    raise ValueError(f"unknown emit format: {fmt}")


def write_or_print(text: str, output: str | None, overwrite: bool) -> int:
    if not output:
        print(text, end="")
        return 0
    path = Path(output)
    if path.exists() and not overwrite:
        print(f"{path} already exists; pass --overwrite to replace it.", file=sys.stderr)
        return 1
    path.write_text(text, encoding="utf-8")
    return 0


def _load_inspector():
    script_dir = Path(__file__).resolve().parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    return importlib.import_module("lazyslide_inspect_env")


def run_inspect(args: argparse.Namespace) -> int:
    if args.list_profiles:
        print("\n".join(PROFILES))
        return 0
    try:
        inspector = _load_inspector()
    except Exception as exc:  # noqa: BLE001 - keep this helper useful as a standalone script
        print(f"Unable to load lazyslide_inspect_env.py: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    report = inspector.collect(
        include_models=args.models,
        redact_paths=args.redact_paths,
        redact_hardware_info=args.redact_hardware,
        profile=args.profile,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        inspector.print_text(report)
    summary = report.get("summary", {}) if isinstance(report, dict) else {}
    if args.fail_on_missing and isinstance(summary, dict) and not summary.get("ready", True):
        return 2
    return 0


def add_plan_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--profile", choices=PROFILES, default="core", help="LazySlide environment profile.")
    parser.add_argument("--manager", choices=MANAGERS, default="auto", help="Environment manager to plan for.")
    parser.add_argument("--env-name", default=DEFAULT_ENV_NAME, help="Conda env name or venv directory.")
    parser.add_argument("--python", default=DEFAULT_PYTHON, help="Python version, or executable for venv.")
    parser.add_argument("--torch-index-url", help="Required for the models-gpu profile.")
    parser.add_argument("--hpc", action="store_true", help="Refuse local mutation; emit plans/artifacts only.")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)

    inspect_parser = subparsers.add_parser("inspect", help="Inspect the current Python environment.")
    inspect_parser.add_argument("--json", action="store_true", help="Print JSON.")
    inspect_parser.add_argument("--models", action="store_true", help="Try listing lazyslide_models groups.")
    inspect_parser.add_argument("--profile", choices=PROFILES, help="Check readiness for one LazySlide profile.")
    inspect_parser.add_argument("--list-profiles", action="store_true", help="Print supported runtime profiles.")
    inspect_parser.add_argument("--fail-on-missing", action="store_true", help="Exit non-zero when profile requirements are missing.")
    inspect_parser.add_argument("--redact-paths", action="store_true", help="Replace environment-local paths.")
    inspect_parser.add_argument("--redact-hardware", action="store_true", help="Replace platform and device names.")

    plan_parser = subparsers.add_parser("plan", help="Print a non-mutating JSON environment plan.")
    add_plan_options(plan_parser)
    plan_parser.add_argument("--json", action="store_true", help="Print JSON plan output (default).")

    emit_parser = subparsers.add_parser("emit", help="Emit commands, requirements, or an environment.yml.")
    add_plan_options(emit_parser)
    emit_parser.add_argument(
        "--format",
        choices=("commands", "requirements", "environment-yml"),
        default="commands",
        help="Artifact format to emit.",
    )
    emit_parser.add_argument("--output", help="Write output to a file instead of stdout.")
    emit_parser.add_argument("--overwrite", action="store_true", help="Replace an existing --output file.")

    create_parser = subparsers.add_parser("create", help="Create the planned LazySlide environment.")
    add_plan_options(create_parser)

    return root


def run_command(args: Sequence[str]) -> subprocess.CompletedProcess[object]:
    return subprocess.run(args, check=False)


def build_plan_from_args(
    args: argparse.Namespace,
    *,
    environ: dict[str, str] | None,
    which: Which,
) -> EnvPlan:
    return build_plan(
        profile=args.profile,
        manager=args.manager,
        env_name=args.env_name,
        python=args.python,
        torch_index_url=args.torch_index_url,
        hpc=args.hpc,
        environ=environ,
        which=which,
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    environ: dict[str, str] | None = None,
    which: Which = shutil.which,
    runner: Runner = run_command,
) -> int:
    args = parser().parse_args(argv)

    if args.command == "inspect":
        return run_inspect(args)

    plan = build_plan_from_args(args, environ=environ, which=which)

    if args.command == "plan":
        print(plan_to_json(plan))
        if plan.refusal:
            print(plan.refusal, file=sys.stderr)
            return 2
        return 0

    if args.command == "emit":
        if plan.refusal:
            print(plan.refusal, file=sys.stderr)
            return 2
        if plan.profile == "models-gpu" and args.format in {"requirements", "environment-yml"}:
            print(
                "Refusing GPU requirements/environment-yml output; use emit --format commands so torch "
                "is installed from the explicit --torch-index-url before model dependencies.",
                file=sys.stderr,
            )
            return 2
        text = format_emit(plan, args.format, args.python, args.torch_index_url)
        return write_or_print(text, args.output, args.overwrite)

    if args.command == "create":
        print(plan_to_json(plan))
        if plan.refusal:
            print(plan.refusal, file=sys.stderr)
            return 2
        if args.hpc:
            print("Refusing to execute create in --hpc mode; use plan or emit instead.", file=sys.stderr)
            return 2
        for planned in plan.commands:
            completed = runner(shlex.split(planned))
            if completed.returncode != 0:
                return int(completed.returncode)
        return 0

    raise AssertionError(f"unhandled command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
