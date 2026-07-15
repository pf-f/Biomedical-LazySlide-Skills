---
name: lazyslide-segmentation
description: Use when a LazySlide task runs or debugs tissue, cell/nucleus, semantic, or artifact segmentation; uses zs.seg APIs or models such as HistoPLUS, Instanseg, NuLite, Cellpose, SAM, or GrandQC; or evaluates aligned masks with Dice, IoU, or PQ.
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

## Completion Gate

- Confirm the requested output key exists, is nonempty, and retains the intended class/geometry fields.
- Treat overlays as geometry/QC checks only: a plausible plot is not validation. Quantitative or biological claims require aligned references, declared class/background rules, and task-appropriate metrics or expert labels.

## Stop Conditions

- MPP or tile specification is unknown for a model with resolution assumptions.
- The selected model license/access is incompatible with the user's intended use.
- Cell segmentation OOM persists after reducing batch size/workers and enabling low-memory options where applicable.
- User wants clinical/pathology conclusions from segmentation without validation.
- Metrics are requested but reference/predicted masks are not aligned.

## Script

```bash
LAZYSLIDE_SEGMENTATION_SKILL="${LAZYSLIDE_SEGMENTATION_SKILL:-$HOME/.codex/skills/lazyslide-segmentation}"
python "$LAZYSLIDE_SEGMENTATION_SKILL/scripts/lazyslide_segmentation_plan.py" --task cells --model instanseg --tile-key tiles_cells_20x
```

For a version-controlled run manifest, copy `assets/segmentation_config.example.json` and replace its runtime/model values with inspected values; the planner does not consume this file automatically.
