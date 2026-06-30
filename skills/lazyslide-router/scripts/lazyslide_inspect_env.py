#!/usr/bin/env python3
"""Inspect a Python environment for LazySlide workflow readiness."""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import shutil
import sys
from importlib import metadata


PROFILES = ("core", "analysis", "models-cpu", "models-gpu", "spatial-omics")

PROFILE_PACKAGES = {
    "core": ["lazyslide", "wsidata", "openslide", "tiffslide"],
    "analysis": ["lazyslide", "wsidata", "openslide", "tiffslide", "scanpy", "anndata", "geopandas", "shapely"],
    "models-cpu": [
        "lazyslide",
        "wsidata",
        "openslide",
        "tiffslide",
        "lazyslide_models",
        "torch",
        "torchvision",
        "timm",
        "huggingface_hub",
    ],
    "models-gpu": [
        "lazyslide",
        "wsidata",
        "openslide",
        "tiffslide",
        "lazyslide_models",
        "torch",
        "torchvision",
        "timm",
        "huggingface_hub",
    ],
    "spatial-omics": [
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
    ],
}


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


PACKAGES = unique([package for profile in PROFILE_PACKAGES.values() for package in profile])


COMMANDS = ["hf", "openslide-show-properties"]


DISTRIBUTION_NAMES = {
    "huggingface_hub": ["huggingface-hub"],
    "lazyslide_models": ["lazyslide-models"],
    "openslide": ["openslide-python"],
}


OPTIONAL_PACKAGES = {
    "scanpy",
}


def package_status(name: str, required: bool) -> dict[str, object]:
    candidates = DISTRIBUTION_NAMES.get(name, [name.replace("_", "-")])
    version = None
    distribution = None
    for candidate in candidates:
        try:
            version = metadata.version(candidate)
            distribution = candidate
            break
        except metadata.PackageNotFoundError:
            continue
    try:
        importlib.import_module(name)
        import_ok = True
    except Exception as exc:  # noqa: BLE001 - report import diagnostics
        import_ok = False
        error = f"{type(exc).__name__}: {exc}"
    else:
        error = None
    return {
        "installed": version is not None,
        "distribution": distribution,
        "version": version,
        "import_ok": import_ok,
        "required": required,
        "error": error,
    }


def torch_status() -> dict[str, object]:
    try:
        import torch
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    status: dict[str, object] = {
        "available": True,
        "version": getattr(torch, "__version__", None),
        "cuda_available": bool(torch.cuda.is_available()),
        "mps_available": bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()),
    }
    if torch.cuda.is_available():
        status["cuda_device_count"] = torch.cuda.device_count()
        status["cuda_devices"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
    return status


def model_names() -> dict[str, object]:
    try:
        from lazyslide_models import list_models
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
    out: dict[str, object] = {"available": True}
    for group in ["vision", "multimodal", "segmentation", "tile_prediction"]:
        try:
            out[group] = list_models(group)
        except Exception as exc:  # noqa: BLE001
            out[group] = f"{type(exc).__name__}: {exc}"
    return out


def redact_path(path: str | None) -> str | None:
    if not path:
        return path
    prefix = sys.prefix.rstrip("/")
    if path.startswith(prefix + "/"):
        return "<python-prefix>/" + path[len(prefix) + 1 :]
    return path


def redact_hardware(report: dict[str, object]) -> dict[str, object]:
    report["platform"] = "<platform-redacted>"
    torch = report.get("torch")
    if isinstance(torch, dict):
        if "cuda_device_count" in torch:
            torch["cuda_device_count"] = "<redacted>"
        if "cuda_devices" in torch:
            torch["cuda_devices"] = ["<redacted>"]
    return report


def packages_for_profile(profile: str | None) -> list[str]:
    if profile is None:
        return PACKAGES
    return PROFILE_PACKAGES[profile]


def build_summary(
    *,
    profile: str | None,
    packages: dict[str, dict[str, object]],
    torch: dict[str, object],
) -> dict[str, object]:
    blocking = [
        name
        for name, status in packages.items()
        if status.get("required", True) and not status.get("import_ok", False)
    ]
    optional_missing = [
        name
        for name, status in packages.items()
        if not status.get("required", True) and not status.get("import_ok", False)
    ]
    import_errors = {
        name: status["error"]
        for name, status in packages.items()
        if status.get("error") and status.get("import_ok") is False
    }
    next_steps = []
    if profile and blocking:
        profile_arg = f" --profile {profile}" if profile else ""
        next_steps.append(f"Run lazyslide_env.py plan{profile_arg} --manager auto --json before analysis.")
    if profile == "models-gpu" and not torch.get("cuda_available", False):
        blocking.append("torch.cuda")
        next_steps.append("For GPU work, create the environment with an explicit --torch-index-url and verify CUDA.")
    return {
        "profile": profile or "full",
        "ready": not blocking,
        "blocking_missing": blocking,
        "optional_missing": optional_missing,
        "import_errors": import_errors,
        "next_steps": next_steps,
    }


def collect(
    include_models: bool,
    redact_paths: bool,
    redact_hardware_info: bool,
    profile: str | None = None,
) -> dict[str, object]:
    executable = redact_path(sys.executable) if redact_paths else sys.executable
    commands = {cmd: shutil.which(cmd) for cmd in COMMANDS}
    if redact_paths:
        commands = {cmd: redact_path(path) for cmd, path in commands.items()}
    selected_packages = packages_for_profile(profile)
    required_packages = set(selected_packages) if profile else set()
    package_report = {pkg: package_status(pkg, required=pkg in required_packages) for pkg in selected_packages}
    torch = torch_status()
    report = {
        "python": sys.version,
        "executable": executable,
        "platform": platform.platform(),
        "profile": profile or "full",
        "packages": package_report,
        "commands": commands,
        "torch": torch,
        "summary": build_summary(profile=profile, packages=package_report, torch=torch),
    }
    if include_models:
        report["models"] = model_names()
    if redact_hardware_info:
        report = redact_hardware(report)
    return report


def print_text(report: dict[str, object]) -> None:
    print(f"Python: {report['python'].split()[0]} ({report['executable']})")
    print(f"Platform: {report['platform']}")
    summary = report.get("summary", {})
    if isinstance(summary, dict):
        state = "ready" if summary.get("ready") else "not-ready"
        print(f"Profile: {summary.get('profile', report.get('profile', 'full'))} ({state})")
        missing = summary.get("blocking_missing") or []
        if missing:
            print(f"Missing: {', '.join(str(item) for item in missing)}")
    print("\nPackages:")
    for name, status in report["packages"].items():
        if status["import_ok"]:
            marker = "ok"
        elif status.get("required", True):
            marker = "missing/error"
        else:
            marker = "optional-missing"
        version = status["version"] or "-"
        print(f"  {name:18} {marker:13} {version}")
        if status["error"]:
            print(f"    {status['error']}")
    print("\nCommands:")
    for cmd, path in report["commands"].items():
        print(f"  {cmd:28} {path or '-'}")
    print("\nTorch:")
    for key, value in report["torch"].items():
        print(f"  {key}: {value}")
    if "models" in report:
        print("\nModel groups:")
        models = report["models"]
        for key, value in models.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} models")
            else:
                print(f"  {key}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON.")
    parser.add_argument("--models", action="store_true", help="Try listing lazyslide_models groups.")
    parser.add_argument("--profile", choices=PROFILES, help="Limit checks to one LazySlide runtime profile.")
    parser.add_argument("--list-profiles", action="store_true", help="Print supported runtime profiles.")
    parser.add_argument("--fail-on-missing", action="store_true", help="Exit 2 when selected profile requirements are missing.")
    parser.add_argument("--redact-paths", action="store_true", help="Replace environment-local paths in output.")
    parser.add_argument("--redact-hardware", action="store_true", help="Replace platform and device names in output.")
    args = parser.parse_args()
    if args.list_profiles:
        print("\n".join(PROFILES))
        return 0
    report = collect(
        include_models=args.models,
        redact_paths=args.redact_paths,
        redact_hardware_info=args.redact_hardware,
        profile=args.profile,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    summary = report.get("summary", {})
    if args.fail_on_missing and isinstance(summary, dict) and not summary.get("ready", True):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
