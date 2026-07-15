---
name: lazyslide-core-workflow
description: Use when a LazySlide task must open a WSI, validate dimensions/MPP/magnification/readers, create or debug tissue and tile layers, preserve result-key variants, build tile graphs, or persist and reopen WSIData analysis stores.
---

# LazySlide Core Workflow

Use this skill for the part of LazySlide that creates reliable `WSIData` objects and tile sets. Most later LazySlide work depends on these keys being correct.

## Required References

- Read `references/input-contracts.md` before running user data.
- Read `references/reference-pack.md` for workflow skeletons and output keys.
- Read `references/pitfalls.md` when MPP, readers, no tiles, or persistence issues appear.
- If `lazyslide`, `wsidata`, or slide reader imports are missing/partial, route through `$lazyslide-router` environment checks before workflow debugging.

## Workflow Skeleton

```python
from pathlib import Path
import lazyslide as zs

store_path = Path("slide-analysis.zarr")
if store_path.exists():
    raise FileExistsError("Choose a new store, or explicitly approve resuming/replacing this one.")

wsi = zs.open_wsi("slide.svs", store=str(store_path))
print(wsi.properties)
print(wsi.fetch.pyramids())

zs.pp.find_tissues(wsi, level=-1, method="otsu", key_added="tissues_otsu")
zs.pl.tissue(wsi, tissue_key="tissues_otsu")

zs.pp.tile_tissues(
    wsi,
    256,
    mpp=0.5,
    tissue_key="tissues_otsu",
    key_added="tiles_20x",
)
print(wsi.shapes["tiles_20x"].head())
if wsi.shapes["tiles_20x"].empty:
    raise RuntimeError("No tiles were created; resolve tissue/MPP/filter settings before saving.")
wsi.write(overwrite=True)
```

## Operating Rules

- Inspect `wsi.properties` and `wsi.fetch.pyramids()` before choosing MPP-sensitive models.
- Keep `tissue_key` and `tile_key` explicit. Do not overwrite `tissues` or `tiles` after downstream features exist unless regenerating dependents.
- Record tile size, MPP, overlap/stride, background filter, and tissue source in a run manifest.
- Treat an existing analysis store as mutable shared state. Inspect its keys first; use a new path by default, and replace it only when the user has explicitly approved that side effect.
- For reproducible tissue detection, set a fixed `level`; `level="auto"` can vary by memory and slide pyramid.
- Use `store="analysis.zarr"` or `store="analysis-dir/"` when results must survive the session. `store="auto"` creates a sibling `.zarr` next to the source slide, and `store=None` disables persistence. The source WSI remains the pixel source and must stay available.

## Stop Conditions

- Slide path is missing, unreadable, encrypted, truncated, or unsupported by installed readers.
- MPP is missing, zero, implausible, or overridden without source provenance.
- User asks for model inference before confirming tile size/MPP matches the model's assumptions.
- No tissue or no tiles are produced and the user asks to continue to feature extraction.
- The target analysis store already exists and the user has not chosen resume, a new store, or replacement.

## Script

```bash
LAZYSLIDE_CORE_WORKFLOW_SKILL="${LAZYSLIDE_CORE_WORKFLOW_SKILL:-$HOME/.codex/skills/lazyslide-core-workflow}"
python "$LAZYSLIDE_CORE_WORKFLOW_SKILL/scripts/lazyslide_core_check.py" --slide path/to/slide.svs --store analysis.zarr
```

For a version-controlled run manifest, copy `assets/core_config.example.json` and replace its paths/parameters with inspected values; the checker does not consume this file automatically.
