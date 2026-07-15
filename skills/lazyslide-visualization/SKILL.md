---
name: lazyslide-visualization
description: Use when a LazySlide task plots or debugs WSI tissue, tiles, annotations, feature/prediction maps, zoomed regions, WSIViewer output, blank or misaligned figures, tile/table coloring, Matplotlib export, DPI, palettes, or visual QC.
---

# LazySlide Visualization

Use this skill whenever the output is a figure or visual inspection step. Visualization is a validation gate, not just a pretty final step.

## Required References

- Read `references/input-contracts.md` for key/color/feature requirements.
- Read `references/reference-pack.md` for plotting patterns.
- Read `references/pitfalls.md` for blank/misaligned plots.
- If LazySlide, plotting/runtime imports, readers, or feature/model packages are missing/partial, route through `$lazyslide-router` environment checks before plot debugging.

## Plotting Skeletons

```python
zs.pl.tissue(wsi, tissue_key="tissues_otsu")
zs.pl.tiles(wsi, tile_key="tiles_20x", linewidth=0.5)
zs.pl.annotations(wsi, key="annotations", color="class")
```

Color by tile shape column:

```python
zs.pl.tiles(wsi, tile_key="tiles_20x", color="tissue_id", palette="tab10")
```

Color by feature table:

```python
print(list(wsi.tables))
zs.pl.tiles(wsi, tile_key="tiles_20x", feature_key="uni_tiles_20x", color="0", cmap="viridis")
```

For a "feature map", decide what the color means: a raw embedding dimension such as `color="0"` is an arbitrary model coordinate; a PCA/cluster/spatial-domain map is usually easier to interpret; a prediction map should name the predicted target and remain separate from measured assays.

## Debug Order

1. Inspect `wsi.shapes`, `wsi.tables`, `wsi.images`, `wsi.attrs`.
2. Plot underlying shapes without feature coloring.
3. Confirm `tile_key` and actual feature table/key association.
4. Confirm selected `tissue_id`, `zoom`, value range, and color variable contain data.
5. Add styling and export options only after geometry is correct.

## Stop Conditions

- Requested keys do not exist.
- Annotation coordinates are not verified level-0 pixels.
- Feature table was generated from a different tile key.
- User wants publication or quantitative interpretation from a plot that has not passed geometry/key checks.

## Script

```bash
LAZYSLIDE_VISUALIZATION_SKILL="${LAZYSLIDE_VISUALIZATION_SKILL:-$HOME/.codex/skills/lazyslide-visualization}"
python "$LAZYSLIDE_VISUALIZATION_SKILL/scripts/lazyslide_visualization_plan.py" --plot tiles --tile-key tiles_20x --feature-key uni_tiles_20x --color leiden
```

For a version-controlled plot manifest, copy `assets/visualization_config.example.json` and replace its keys/output with inspected values; the planner does not consume this file automatically.
