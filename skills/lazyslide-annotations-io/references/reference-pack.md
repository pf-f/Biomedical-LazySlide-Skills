# LazySlide Annotations IO Reference Pack

## Import

```python
zs.io.load_annotations(wsi, "annotations.geojson", key_added="annotations")
zs.io.load_annotations(wsi, "slide.ndpa", key_added="annotations")
```

GeoJSON exported by QuPath is read through GeoPandas. Hamamatsu NDPA requires matching slide metadata for offsets and MPP.

## Inspect

```python
annotations = wsi.shapes["annotations"]
print(annotations.columns)
print(annotations.geom_type.value_counts())
print(annotations.head())
zs.pl.annotations(wsi, key="annotations")
```

External class labels may be nested. For common QuPath classification fields, use options such as `json_flatten="classification"` when needed.

## Join to Tiles

```python
zs.io.load_annotations(
    wsi,
    "annotations.geojson",
    join_with="tiles",
    join_to="tiles",
    key_added="annotations",
)
```

Inspect destination columns. Boundary tiles can intersect more than one annotation.

## Analyze Annotated Regions

Filter annotations first if needed, store as a new key, then tile:

```python
zs.pp.tile_tissues(wsi, 256, mpp=0.5, tissue_key="annotations", key_added="roi_tiles")
```

## Shifted Annotations

LazySlide shape coordinates are level-0 pixels. If source coordinates are relative to bounded image origin, test a new key:

```python
zs.io.load_annotations(wsi, "annotations.geojson", in_bounds=True, key_added="annotations_in_bounds")
```

Verify against landmarks, not just approximate visual alignment.

## Export

```python
zs.io.export_annotations(
    wsi,
    key="cells",
    classes="class",
    format="qupath",
    file="cells.geojson",
)
```

The parent directory must exist.

## Upstream Pages

- Annotations how-to: https://lazyslide.readthedocs.io/en/latest/how-to/annotations.html
- IO API: https://lazyslide.readthedocs.io/en/latest/api/io.html

