# LazySlide Visualization Pitfalls

- A blank plot usually means missing key, empty geometry, zoom outside data, filtered tissue ID, or feature/color mismatch.
- Plot shapes without feature coloring before debugging colors.
- Feature tables usually include tile-key suffixes. Inspect `list(wsi.tables)` before assuming `feature_key`.
- Raw embedding dimensions such as `color="0"` are arbitrary coordinates, not named biology.
- Imported annotations may need `in_bounds=True` or may use a different origin.
- Coordinates are level-0 pixels; do not mix thumbnail coordinates with full-resolution coordinates.
- A nice feature map is not biological validation; keep interpretation tied to the upstream workflow and validation evidence.
