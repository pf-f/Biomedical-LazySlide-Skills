---
name: lazyslide-segmentation
description: LazySlide segmentation workflows for tissue segmentation, cell/nucleus segmentation, semantic segmentation, artifact segmentation, and segmentation metrics. Use when the user asks to run or debug zs.seg.tissue, zs.seg.cells, zs.seg.semantic, zs.seg.artifact, learned tissue masks, HistoPLUS, Instanseg, NuLite, Cellpose, SAM, GrandQC, segmentation memory issues, overlapping segmentation tiles, class maps, or Dice/IoU/PQ evaluation.
---

# LazySlide Segmentation

Use this skill after a `WSIData` object and suitable tile/tissue keys exist, or when deciding how to create them for segmentation.

## Required References

- Read `references/input-contracts.md` before running segmentation.
- Read `references/reference-pack.md` for tissue/cell/semantic workflows.
- Read `references/pitfalls.md` for MPP, duplicate objects, memory, and metrics risks.
- If LazySlide, torch/device, or segmentation model packages are missing/partial, route through `$lazyslide-router` environment checks before inference.

## Workflow Choices

- Fast tissue baseline: use `$lazyslide-core-workflow` and `zs.pp.find_tissues`.
- Learned tissue segmentation: use `zs.seg.tissue` when thresholds fail and a model matches stain/domain.
- Cell segmentation: prepare model-compatible tiles first, then use `zs.seg.cells`.
- Semantic segmentation: pass a compatible segmentation model object and `class_names`.
- Evaluation: use segmentation metrics only after confirming prediction/reference masks share resolution, extent, classes, and background rules.

## Cell Segmentation Skeleton

```python
import lazyslide as zs

zs.pp.tile_tissues(wsi, 512, mpp=0.5, key_added="tiles_cells_20x")
zs.seg.cells(
    wsi,
    model="instanseg",
    tile_key="tiles_cells_20x",
    key_added="cells_instanseg",
    batch_size=1,
    num_workers=0,
)
zs.pl.annotations(wsi, key="cells_instanseg")
```

## Stop Conditions

- MPP or tile specification is unknown for a model with resolution assumptions.
- The selected model license/access is incompatible with the user's intended use.
- Cell segmentation OOM persists after reducing batch size/workers and enabling low-memory options where applicable.
- User wants clinical/pathology conclusions from segmentation without validation.
- Metrics are requested but reference/predicted masks are not aligned.

## Script

```bash
python skills/lazyslide-segmentation/scripts/lazyslide_segmentation_plan.py --task cells --model instanseg --tile-key tiles_cells_20x
```
