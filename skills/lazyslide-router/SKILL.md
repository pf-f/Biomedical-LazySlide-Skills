---
name: lazyslide-router
description: Use when a LazySlide task is ambiguous across workflow domains, the runtime/imports/readers/devices are missing or uncertain, bundled LazySlide guidance must be searched, or official documentation and rendeirolab source drift must be checked.
---

# LazySlide Router

Use this skill first when the task is about LazySlide but the exact domain is unclear. Route to a domain skill, load only the needed references, and use scripts for deterministic checks.

## First Moves

1. Identify the user's task: environment/runtime check, open/tile, segment, extract features, integrate omics, visualize, import/export annotations, or update docs.
2. Read `references/domain-map.md` for routing if the domain is not obvious.
3. Read `references/environment-guide.md` before running code, models, readers, GPU/MPS/CUDA, or Hugging Face downloads.
4. Use `scripts/lazyslide_docs_search.py --query "<terms>"` to search bundled concise references.
5. For upstream drift, use `references/upstream-sources.md` and the upstream scripts.

## Domain Routing

- Stay in `$lazyslide-router` for missing or partial runtimes: failed `lazyslide`/`wsidata`/`lazyslide_models` imports, absent slide readers, unresolved Hugging Face/model packages, or uncertain CUDA/MPS/HPC setup.
- Use `$lazyslide-core-workflow` for `open_wsi`, `WSIData`, slide metadata, MPP/magnification, tissue detection, tiling, tile graph setup, keys, zarr/store persistence, and first-slide workflows.
- Use `$lazyslide-segmentation` for `zs.seg.tissue`, `zs.seg.cells`, semantic segmentation, artifacts, segmentation metrics, model resolution requirements, overlapping tiles, and segmentation memory issues.
- Use `$lazyslide-models-features` for `lazyslide_models`, model zoo selection, feature extraction, feature aggregation, tile prediction, feature prediction, text/image similarity, zero-shot, slide captions, virtual staining, and image generation.
- Use `$lazyslide-spatial-omics` for RNALinker, Path2Space, WSI morphology with RNA/spatial transcriptomics, MOFA-style multimodal analysis, slide-level labels, survival demos, and sample-level inference risks.
- Use `$lazyslide-visualization` for `zs.pl.tissue`, `zs.pl.tiles`, `zs.pl.annotations`, `WSIViewer`, publication plots, blank plots, and feature/tile coloring.
- Use `$lazyslide-annotations-io` for `zs.io.load_annotations`, `zs.io.export_annotations`, GeoJSON, QuPath, NDPA, class fields, spatial joins, coordinate shifts, and annotation-to-tile workflows.

## Environment Routing

- Resolve this skill directory before running helper scripts. In a standard install, use `LAZYSLIDE_ROUTER_SKILL="$HOME/.codex/skills/lazyslide-router"`.
- When runtime readiness is uncertain, inspect before analysis: `python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_env.py" inspect --profile core --json`.
- Plan before creating or repairing environments: `python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_env.py" plan --profile core --manager auto --json`.
- Use the smallest profile that fits: `core`, `analysis`, `models-cpu`, `models-gpu`, or `spatial-omics`.
- Do not mutate `base`; use `create` only after the plan is reviewed. For GPU work, require an explicit torch index URL. For HPC, use `--hpc` with `plan` or `emit`, not local mutation.
- Fix missing imports, readers, model packages, device availability, and offline cache/token issues before choosing scientific workflow parameters.
- After the runtime is adequate for the requested profile, route to the narrowest domain skill.

## Safety Defaults

- Treat LazySlide workflows as research workflows, not diagnostic or clinical decision systems.
- Inspect `wsi.shapes`, `wsi.tables`, `wsi.images`, and `wsi.attrs` before guessing result keys.
- Keep `tile_key`, `feature_key`, and `key_added` explicit in reusable pipelines.
- Do not infer MPP from filenames or nominal magnification when model behavior depends on physical resolution.
- Do not truncate or reorder tables to hide tile/feature mismatches; regenerate from matched inputs.
- Confirm model license, gated Hugging Face access, device, batch size, and storage budget before long inference jobs.

## Scripts

Run scripts through the installed skill directory:

```bash
LAZYSLIDE_ROUTER_SKILL="${LAZYSLIDE_ROUTER_SKILL:-$HOME/.codex/skills/lazyslide-router}"
python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_docs_search.py" --query "tile graph feature_key"
python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_inspect_env.py" --json
python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_env.py" plan --profile core --manager auto --json
python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_env.py" emit --profile core --format requirements
python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_upstream_check.py" --query "Path2Space" --limit 10
python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_upstream_update.py" --write-report --update-snapshot
```

The upstream update script writes reports but does not rewrite scientific guidance automatically.
