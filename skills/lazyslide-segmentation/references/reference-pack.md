# LazySlide Segmentation Reference Pack

## Tissue Segmentation

Use threshold-based tissue detection first when appropriate:

```python
zs.pp.find_tissues(wsi, method="otsu", key_added="tissues_otsu")
```

Use learned tissue segmentation when image thresholds are unreliable:

```python
zs.seg.tissue(wsi, model="pathprofiler", key_added="tissues_pathprofiler")
zs.pl.tissue(wsi, tissue_key="tissues_pathprofiler")
```

Compare alternatives visually and keep different keys.

## Cell Segmentation

Prepare tiles at the expected model resolution:

```python
zs.pp.tile_tissues(wsi, 512, mpp=0.5, key_added="tiles_cells")
zs.seg.cells(wsi, model="instanseg", tile_key="tiles_cells", key_added="cells")
```

Compatible models can add classes and per-cell features:

```python
zs.seg.cells(wsi, model="histoplus", extract_features=True, key_added="cells")
```

Expected outputs:

- `wsi.shapes["cells"]`
- optional `wsi.tables["cells_features"]`

## Memory Controls

```python
zs.seg.cells(
    wsi,
    model="histoplus",
    batch_size=1,
    num_workers=0,
    extract_features=True,
    low_memory=True,
)
```

Reduce `batch_size` first. Then reduce `num_workers`. Restart after framework OOMs when allocations may be retained.

## Semantic Segmentation

```python
zs.seg.semantic(
    wsi,
    model=model,
    tile_key="tiles",
    class_names=["background", "tumor", "stroma"],
    key_added="anatomical_structures",
)
```

The result is stored in `wsi.shapes[key_added]`.

## Upstream Pages

- Segmentation how-to: https://lazyslide.readthedocs.io/en/latest/how-to/segmentation.html
- Segmentation API: https://lazyslide.readthedocs.io/en/latest/api/segmentation.html
- Metrics API: https://lazyslide.readthedocs.io/en/latest/api/metrics.html
- Model zoo: https://lazyslide.readthedocs.io/en/latest/avail_models.html

