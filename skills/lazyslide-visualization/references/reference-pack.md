# LazySlide Visualization Reference Pack

## Basic Plots

```python
zs.pl.tissue(wsi)
zs.pl.tiles(wsi, linewidth=0.5)
zs.pl.annotations(wsi, key="annotations", color="class")
```

Always pass explicit keys in reusable pipelines:

```python
zs.pl.tissue(wsi, tissue_key="tissues_entropy")
zs.pl.tiles(wsi, tile_key="tiles_20x")
```

## Feature Coloring

Tile shape column:

```python
zs.pl.tiles(wsi, color="tissue_id", palette="tab10")
```

Feature or prediction table:

```python
print(list(wsi.tables))
zs.pl.tiles(wsi, tile_key="tiles_20x", feature_key="uni_tiles_20x", color="0", cmap="viridis")
```

Inspect feature variables:

```python
adata = wsi.fetch.features_anndata("uni")
print(adata.var_names[:20])
```

Before making a "feature map", choose the semantic target:

- Raw embedding dimension: useful for debugging, but `color="0"` has no direct biological meaning.
- PCA/cluster/domain map: use scanpy or `zs.tl.spatial_domain` outputs for interpretable grouping.
- Prediction map: name the predicted class/gene/score and do not present it as a measured assay.

## Focused Views

```python
zs.pl.tissue(wsi, tissue_id=0)
zs.pl.tiles(wsi, tissue_id=0)
zs.pl.tiles(wsi, zoom=(10000, 20000, 5000, 15000))
```

Zoom coordinates are level-0 pixel coordinates.

## Publication Export

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6, 6))
zs.pl.tiles(wsi, tile_key="tiles_20x", feature_key="uni_tiles_20x", color="0", target_dpi=300, ax=ax)
fig.savefig("feature-map.png", dpi=300, bbox_inches="tight")
```

## Upstream Pages

- Visualization how-to: https://lazyslide.readthedocs.io/en/latest/how-to/visualization.html
- Visualization tutorial: https://lazyslide.readthedocs.io/en/latest/tutorials/visualization.html
- Plotting API: https://lazyslide.readthedocs.io/en/latest/api/plotting.html
