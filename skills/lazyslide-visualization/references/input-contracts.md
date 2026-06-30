# LazySlide Visualization Input Contracts

## Required for Any Plot

- Open `WSIData`.
- Existing shape/table/image keys.
- Known coordinate system for shapes, especially imported annotations.
- Appropriate tile/feature association when coloring by feature table.

## Tissue Plot

Inputs:

- `tissue_key` in `wsi.shapes`.

## Tile Plot

Inputs:

- `tile_key` in `wsi.shapes`.
- Optional `color` column in tile shapes, or `feature_key` pointing to the actual matched table printed from `list(wsi.tables)`.

## Annotation Plot

Inputs:

- Annotation key in `wsi.shapes`.
- Optional class/color column.
- Verified coordinate alignment with WSI.

## Publication Export

Inputs:

- Matplotlib axis or controlled figure size.
- Export DPI and `target_dpi`.
- Checked data range and palette/cmap.
- Clear meaning for the color layer: raw embedding coordinate, cluster/domain, or prediction.
