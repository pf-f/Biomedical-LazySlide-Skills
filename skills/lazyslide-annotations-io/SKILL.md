---
name: lazyslide-annotations-io
description: LazySlide annotation import/export and coordinate alignment workflows for GeoJSON, QuPath, Hamamatsu NDPA, spatial joins, ROI tiling, class-field inspection, shifted annotations, in_bounds handling, and exporting cells or shapes back to QuPath-compatible GeoJSON. Use when users ask about zs.io.load_annotations, zs.io.export_annotations, joining annotations to tiles, analyzing annotated regions, fixing shifted/scaled/mirrored annotations, or preserving annotation classes in WSIData.
---

# LazySlide Annotations IO

Use this skill when external annotation files enter or leave LazySlide, or when annotations become ROI/tile labels.

## Required References

- Read `references/input-contracts.md` before loading external annotations.
- Read `references/reference-pack.md` for import/export and ROI patterns.
- Read `references/pitfalls.md` when annotations are shifted, scaled, mirrored, or class fields are missing.
- If LazySlide, geometry/annotation packages, or slide readers are missing/partial, route through `$lazyslide-router` environment checks before annotation debugging.

## Import Skeleton

```python
zs.io.load_annotations(wsi, "annotations.geojson", key_added="annotations")
ann = wsi.shapes["annotations"]
print(ann.columns)
print(ann.geom_type.value_counts())
zs.pl.annotations(wsi, key="annotations")
```

## ROI Tiling Skeleton

```python
zs.pp.tile_tissues(
    wsi,
    256,
    mpp=0.5,
    tissue_key="annotations",
    key_added="roi_tiles",
)
```

## Export Skeleton

```python
zs.io.export_annotations(
    wsi,
    key="cells",
    classes="class",
    format="qupath",
    file="cells.geojson",
)
```

## Stop Conditions

- Annotation coordinate system is unknown and the user wants quantitative analysis.
- Annotation classes are nested or missing and have not been inspected.
- Geometries are shifted/scaled/mirrored and no landmarks or metadata are available.
- Boundary tiles intersect multiple annotations and no labeling rule is defined.

## Script

```bash
python skills/lazyslide-annotations-io/scripts/lazyslide_annotations_plan.py --action load --file annotations.geojson --key annotations
```
