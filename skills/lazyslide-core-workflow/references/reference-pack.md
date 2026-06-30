# LazySlide Core Workflow Reference Pack

## Core Object Model

LazySlide analyzes slides through `WSIData`. The source slide remains the pixel source; LazySlide stores analysis outputs in named collections:

- `wsi.shapes`: tissue polygons, tiles, cells, imported annotations.
- `wsi.tables`: feature matrices and prediction tables, usually AnnData-like.
- `wsi.images`: generated rasters or segmentation images.
- `wsi.attrs`: result specifications and metadata.

Most functions mutate `wsi` in place and return `None`. Always inspect keys:

```python
print(list(wsi.shapes))
print(list(wsi.tables))
print(list(wsi.images))
print(list(wsi.attrs))
```

## Output Key Defaults

| Operation | Default result | Location |
| --- | --- | --- |
| `zs.pp.find_tissues` | `tissues` | `wsi.shapes` |
| `zs.pp.tile_tissues` | `tiles` | `wsi.shapes` |
| `zs.seg.tissue` | `tissues` | `wsi.shapes` |
| `zs.seg.cells` | `cells` | `wsi.shapes` |
| `zs.io.load_annotations` | `annotations` | `wsi.shapes` |
| `zs.tl.feature_extraction` | `{model}_{tile_key}` | `wsi.tables` |

Use `key_added` for variants:

```python
zs.pp.find_tissues(wsi, method="entropy", key_added="tissues_entropy")
zs.pp.tile_tissues(wsi, 256, mpp=1.0, tissue_key="tissues_entropy", key_added="tiles_10x")
```

## Tissue and Tile Decisions

- Start with `zs.pp.find_tissues(wsi, method="otsu")`.
- Compare `method="entropy"` for faint/textural tissue.
- Use `zs.seg.tissue` when thresholding is unreliable and a model matches the slide domain.
- Tile field of view is `tile_px * mpp` in microns.
- Use either `overlap` or `stride_px`, not both.
- Set `tissue_key=None` to tile the whole slide.

## Persistence

```python
wsi = zs.open_wsi("slide.svs", store="slide-analysis.zarr")
# run analysis
wsi.write(overwrite=True)
wsi = zs.open_wsi("slide.svs", store="slide-analysis.zarr")
```

The `.zarr` store does not replace the slide; keep the source WSI path valid.

## Upstream Pages

- Workflow: https://lazyslide.readthedocs.io/en/latest/concepts/workflow.html
- Data model: https://lazyslide.readthedocs.io/en/latest/concepts/data-model.html
- Slides and storage: https://lazyslide.readthedocs.io/en/latest/how-to/slides-and-storage.html
- Tissue and tiling: https://lazyslide.readthedocs.io/en/latest/how-to/tissue-and-tiles.html
- Outputs and keys: https://lazyslide.readthedocs.io/en/latest/reference/outputs.html
