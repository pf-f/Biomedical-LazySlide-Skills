# LazySlide Annotation IO Pitfalls

- LazySlide shapes use level-0 pixel coordinates. Thumbnail or bounded-image coordinates will be wrong unless transformed.
- `in_bounds=True` is not a magic fix. Test on a new key and verify multiple landmarks.
- NDPA depends on Hamamatsu offsets and MPP metadata.
- QuPath class labels may be nested; inspect columns before filtering.
- GeoJSON/QuPath exports may warn that no CRS was provided. For WSI annotations this is common because geometries are usually level-0 pixel coordinates, not map coordinates. Treat the warning as a reminder to verify coordinate origin and scale; do not invent a geographic CRS.
- Boundary tiles may intersect multiple annotations. Define the label assignment rule before training or quantification.
- Do not overwrite original imported annotations while experimenting with coordinate transforms.
- Parent output directories for exports must already exist.
