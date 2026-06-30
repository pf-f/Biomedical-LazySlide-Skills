---
name: lazyslide-core-workflow
description: Core LazySlide whole-slide image workflow guidance for opening slides, validating WSI metadata, managing WSIData, tissue detection, tiling, tile graphs, result keys, persistence, backed zarr stores, and first analysis pipelines. Use when the user needs to open SVS/TIFF/CZI/iSyntax or other WSI files, inspect dimensions/MPP/magnification/readers, create tissue or tile layers, debug no tissue/no tiles, preserve multiple tissue/tile variants, or save/reopen LazySlide analyses.
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
import lazyslide as zs

wsi = zs.open_wsi("slide.svs", store="slide-analysis.zarr")
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
wsi.write(overwrite=True)
```

## Operating Rules

- Inspect `wsi.properties` and `wsi.fetch.pyramids()` before choosing MPP-sensitive models.
- Keep `tissue_key` and `tile_key` explicit. Do not overwrite `tissues` or `tiles` after downstream features exist unless regenerating dependents.
- Record tile size, MPP, overlap/stride, background filter, and tissue source in a run manifest.
- For reproducible tissue detection, set a fixed `level`; `level="auto"` can vary by memory and slide pyramid.
- Use `store="analysis.zarr"` or `store="analysis-dir/"` when results must survive the session. `store="auto"` creates a sibling `.zarr` next to the source slide, and `store=None` disables persistence. The source WSI remains the pixel source and must stay available.

## Stop Conditions

- Slide path is missing, unreadable, encrypted, truncated, or unsupported by installed readers.
- MPP is missing, zero, implausible, or overridden without source provenance.
- User asks for model inference before confirming tile size/MPP matches the model's assumptions.
- No tissue or no tiles are produced and the user asks to continue to feature extraction.

## Script

```bash
python skills/lazyslide-core-workflow/scripts/lazyslide_core_check.py --slide path/to/slide.svs --store analysis.zarr
```
