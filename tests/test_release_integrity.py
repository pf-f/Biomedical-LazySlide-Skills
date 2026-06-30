#!/usr/bin/env python3
"""Release integrity checks for the LazySlide skill suite."""

from __future__ import annotations

import py_compile
import re
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = [
    "lazyslide-router",
    "lazyslide-core-workflow",
    "lazyslide-segmentation",
    "lazyslide-models-features",
    "lazyslide-spatial-omics",
    "lazyslide-visualization",
    "lazyslide-annotations-io",
]

FORBIDDEN_PATTERNS = [
    "TO" + "DO",
    "lazyslide-" + "local-knowledge",
    "original-site/" + "lazyslide.readthedocs.io",
    "lazyslide.readthedocs.io/en/latest/" + "_sources",
    "../" + "lazyslide-guide",
]

RELEASE_ROOTS = [
    ROOT / "skills",
    ROOT / ".github",
    ROOT / "tests",
    ROOT / "README.md",
    ROOT / ".gitignore",
]

ALLOWED_TRACKED_TOP_LEVELS = {
    ".github",
    ".gitignore",
    "README.md",
    "skills",
    "tests",
}

REQUIRED_TRACKED_FILES = {
    ".github/workflows/monthly-upstream-docs-update.yml",
    ".gitignore",
    "README.md",
    "skills/lazyslide-router/scripts/lazyslide_env.py",
    "skills/lazyslide-router/scripts/lazyslide_inspect_env.py",
    "tests/test_lazyslide_env.py",
    "tests/test_lazyslide_inspect_env.py",
    "tests/test_release_integrity.py",
}

FORBIDDEN_CACHE_DIRS = {
    "__pycache__",
    ".cache",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "cache",
    "caches",
}

FORBIDDEN_ARTIFACT_SUFFIXES = {
    ".bin",
    ".ckpt",
    ".h5",
    ".hdf5",
    ".joblib",
    ".keras",
    ".npy",
    ".npz",
    ".onnx",
    ".pb",
    ".pkl",
    ".pickle",
    ".pt",
    ".pth",
    ".pyc",
    ".pyo",
    ".safetensors",
    ".tflite",
    ".weights",
}

FORBIDDEN_SECRET_SUFFIXES = {
    ".asc",
    ".gpg",
    ".jks",
    ".key",
    ".kubeconfig",
    ".pem",
    ".pfx",
    ".p12",
}

FORBIDDEN_SECRET_NAME_PARTS = {
    ".env",
    "deploy_key",
    "id_ed25519",
    "id_rsa",
    "private_key",
    "secret",
}

FORBIDDEN_WSI_SUFFIXES = {
    ".bif",
    ".czi",
    ".dcm",
    ".dicom",
    ".isyntax",
    ".j2k",
    ".jp2",
    ".mrxs",
    ".ndpi",
    ".qptiff",
    ".scn",
    ".svs",
    ".svslide",
    ".tif",
    ".tiff",
    ".vsi",
    ".vms",
    ".vmu",
}

HEAVY_RUNTIME_PACKAGES = {
    "anndata",
    "bioformats",
    "cellpose",
    "cucim",
    "fastslide",
    "geopandas",
    "huggingface-hub",
    "instanseg",
    "lazyslide",
    "lazyslide-models",
    "monai",
    "openslide-bin",
    "openslide-python",
    "pyisyntax",
    "pylibczirw",
    "scanpy",
    "shapely",
    "tensorflow",
    "tiffslide",
    "timm",
    "torch",
    "torchvision",
    "wsidata",
}


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def release_files() -> list[Path]:
    files = []
    for root in RELEASE_ROOTS:
        if root.is_file():
            files.append(root)
        elif root.exists():
            files.extend(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts)
    return files


def tracked_release_paths() -> list[Path]:
    roots = [str(path.relative_to(ROOT)) for path in RELEASE_ROOTS if path.exists()]
    if not roots:
        return []
    result = subprocess.run(
        ["git", "ls-files", "--", *roots],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line]


def tracked_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line]


def untracked_release_paths() -> list[Path]:
    roots = [str(path.relative_to(ROOT)) for path in RELEASE_ROOTS if path.exists()]
    if not roots:
        return []
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", *roots],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line]


def tracked_path_set() -> set[Path]:
    return set(tracked_paths())


def lower_suffixes(path: Path) -> set[str]:
    name = path.name.lower()
    suffixes = {suffix.lower() for suffix in path.suffixes}
    if name.endswith(".ome.tif"):
        suffixes.add(".ome.tif")
    if name.endswith(".ome.tiff"):
        suffixes.add(".ome.tiff")
    return suffixes


def check_required_files() -> None:
    tracked = tracked_path_set()
    for rel in REQUIRED_TRACKED_FILES:
        path = ROOT / rel
        if not path.is_file():
            fail(f"missing required release file: {rel}")
        if path not in tracked:
            fail(f"required release file is not tracked: {rel}")
    for skill in SKILLS:
        base = ROOT / "skills" / skill
        for rel in ["SKILL.md", "agents/openai.yaml"]:
            path = base / rel
            if not path.is_file():
                fail(f"missing {path}")
            if path not in tracked:
                fail(f"required release file is not tracked: {path.relative_to(ROOT)}")
        if not (base / "references").is_dir():
            fail(f"missing references dir for {skill}")


def check_no_templates_or_local_leaks() -> None:
    for path in release_files():
        if path.suffix.lower() not in {".md", ".yaml", ".yml", ".py", ".json", ".txt"}:
            continue
        text = read(path)
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                fail(f"forbidden pattern {pattern!r} in {path.relative_to(ROOT)}")


def check_skill_scripts_compile() -> None:
    scripts = sorted(
        path
        for path in tracked_release_paths()
        if path.suffix == ".py" and "scripts" in path.relative_to(ROOT).parts
    )
    if not scripts:
        fail("no skill scripts found to compile")
    with tempfile.TemporaryDirectory() as tmp:
        bytecode_root = Path(tmp)
        for script in scripts:
            cfile = bytecode_root / script.relative_to(ROOT).with_suffix(".pyc")
            cfile.parent.mkdir(parents=True, exist_ok=True)
            try:
                py_compile.compile(str(script), cfile=str(cfile), doraise=True)
            except py_compile.PyCompileError as exc:
                fail(f"script does not compile: {script.relative_to(ROOT)}: {exc.msg}")


def check_no_tracked_release_artifacts() -> None:
    for path in tracked_release_paths():
        rel = path.relative_to(ROOT)
        parts = {part.lower() for part in rel.parts}
        forbidden_cache_parts = parts & FORBIDDEN_CACHE_DIRS
        if forbidden_cache_parts:
            fail(f"tracked cache artifact in release root: {rel}")
        if any(part.endswith(".zarr") for part in parts):
            fail(f"tracked zarr store in release root: {rel}")
        suffixes = lower_suffixes(path)
        forbidden_suffixes = suffixes & (FORBIDDEN_ARTIFACT_SUFFIXES | FORBIDDEN_WSI_SUFFIXES)
        if forbidden_suffixes:
            fail(f"tracked binary/data artifact in release root: {rel}")
        secret_suffixes = suffixes & FORBIDDEN_SECRET_SUFFIXES
        if secret_suffixes:
            fail(f"tracked secret-like file in release root: {rel}")
        name = path.name.lower()
        if any(part in name for part in FORBIDDEN_SECRET_NAME_PARTS):
            fail(f"tracked secret-like filename in release root: {rel}")


def check_tracked_release_scope() -> None:
    for path in tracked_paths():
        rel = path.relative_to(ROOT)
        top = rel.parts[0]
        if top not in ALLOWED_TRACKED_TOP_LEVELS:
            fail(f"tracked path outside release package: {rel}")


def check_no_untracked_release_files() -> None:
    paths = untracked_release_paths()
    if paths:
        rels = ", ".join(str(path.relative_to(ROOT)) for path in paths[:20])
        fail(f"untracked release files would not be pushed: {rels}")


def check_openai_yaml_prompts() -> None:
    for skill in SKILLS:
        text = read(ROOT / "skills" / skill / "agents" / "openai.yaml")
        expected = f"${skill}"
        if expected not in text:
            fail(f"agents/openai.yaml for {skill} must mention {expected}")


def check_frontmatter() -> None:
    for skill in SKILLS:
        text = read(ROOT / "skills" / skill / "SKILL.md")
        if not text.startswith("---\n"):
            fail(f"{skill}/SKILL.md missing YAML frontmatter")
        frontmatter = text.split("---", 2)[1]
        if f"name: {skill}" not in frontmatter:
            fail(f"{skill}/SKILL.md frontmatter name mismatch")
        match = re.search(r"description:\s*(.+)", frontmatter)
        if not match or len(match.group(1)) < 80:
            fail(f"{skill}/SKILL.md description is too short")


def check_router_environment_docs_are_wired() -> None:
    inspector = ROOT / "skills" / "lazyslide-router" / "scripts" / "lazyslide_inspect_env.py"
    planner = ROOT / "skills" / "lazyslide-router" / "scripts" / "lazyslide_env.py"
    environment_guide = ROOT / "skills" / "lazyslide-router" / "references" / "environment-guide.md"
    router_skill = ROOT / "skills" / "lazyslide-router" / "SKILL.md"
    if not inspector.is_file():
        fail("missing lazyslide router environment inspector script")
    if not planner.is_file():
        fail("missing lazyslide router environment planner script")
    tracked = tracked_path_set()
    for path in [inspector, planner]:
        if path not in tracked:
            fail(f"router environment helper is not tracked: {path.relative_to(ROOT)}")
    env_text = read(environment_guide)
    router_text = read(router_skill)
    if "references/environment-guide.md" not in router_text:
        fail("router skill does not point users to the environment guide")
    if "lazyslide_inspect_env.py" not in router_text or "--json" not in router_text:
        fail("router skill does not expose the environment inspector command")
    if "lazyslide_env.py" not in router_text or "plan" not in router_text:
        fail("router skill does not expose the environment planner command")
    if "lazyslide_inspect_env.py" not in env_text or "--json" not in env_text:
        fail("environment guide does not expose the JSON inspector command")
    if "lazyslide_env.py" not in env_text or "plan" not in env_text:
        fail("environment guide does not expose the environment planner command")
    workflow = read(ROOT / ".github" / "workflows" / "monthly-upstream-docs-update.yml")
    if "update-reports/**" in workflow:
        fail("monthly workflow must not add root-level update-reports")
    if "skills/lazyslide-router/references/upstream-reports/**" not in workflow:
        fail("monthly workflow does not add skill-scoped upstream reports")


def check_workflows_avoid_heavy_runtime_installs() -> None:
    workflow_dir = ROOT / ".github" / "workflows"
    for workflow in sorted(workflow_dir.glob("*.y*ml")):
        text = read(workflow)
        lowered = text.lower()
        for package in HEAVY_RUNTIME_PACKAGES:
            patterns = [
                rf"\bpip\s+install\b[^\n]*\b{re.escape(package)}\b",
                rf"\bpython\s+-m\s+pip\s+install\b[^\n]*\b{re.escape(package)}\b",
                rf"\buv\s+pip\s+install\b[^\n]*\b{re.escape(package)}\b",
                rf"\bconda\s+install\b[^\n]*\b{re.escape(package)}\b",
            ]
            if any(re.search(pattern, lowered) for pattern in patterns):
                fail(f"workflow installs heavyweight runtime package {package!r}: {workflow.relative_to(ROOT)}")


def main() -> int:
    check_required_files()
    check_skill_scripts_compile()
    check_no_templates_or_local_leaks()
    check_tracked_release_scope()
    check_no_untracked_release_files()
    check_no_tracked_release_artifacts()
    check_openai_yaml_prompts()
    check_frontmatter()
    check_router_environment_docs_are_wired()
    check_workflows_avoid_heavy_runtime_installs()
    print("release integrity checks passed")
    return 0


def test_release_integrity() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
