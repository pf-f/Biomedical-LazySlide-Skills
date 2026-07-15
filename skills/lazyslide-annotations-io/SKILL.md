---
name: lazyslide-annotations-io
description: Use when a LazySlide task imports, inspects, aligns, joins, labels from, or exports WSI annotations such as GeoJSON, QuPath, or Hamamatsu NDPA, especially when coordinate origins, class fields, ROI tiling, in_bounds handling, or shifted/scaled/mirrored geometries matter.
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
LAZYSLIDE_ANNOTATIONS_IO_SKILL="${LAZYSLIDE_ANNOTATIONS_IO_SKILL:-$HOME/.codex/skills/lazyslide-annotations-io}"
python "$LAZYSLIDE_ANNOTATIONS_IO_SKILL/scripts/lazyslide_annotations_plan.py" --action load --file annotations.geojson --key annotations
```

For a version-controlled IO manifest, copy `assets/annotations_config.example.json` and replace its keys, coordinate options, and export path with verified values; the planner does not consume this file automatically.
