# LazySlide Core Pitfalls

## Missing or Wrong MPP

Do not infer MPP from filename or nominal magnification. Retrieve it from scanner metadata or acquisition records. If using `slide_mpp`, record the override.

Do not request a tile `mpp` smaller than the slide MPP unless you intentionally want an unsupported up-sampling error. Converted or generic tiled TIFF files may expose surprising MPP values such as `1000.0`; for format smoke tests use `max(requested_mpp, wsi.properties.mpp)` or set a justified `slide_mpp` override.

## No Tissue Found

Check:

- Slide opens correctly and color interpretation is right.
- `level` is fixed.
- Otsu vs entropy methods.
- `min_tissue_area` and artifact filtering thresholds.
- Learned tissue segmentation if thresholding fails.

## No Tiles Found

Common causes:

- Tile footprint is larger than tissue fragments.
- Tissue detection produced no valid contours.
- `background_fraction` rejected border tiles.
- Requested MPP plus slide metadata implies a huge level-0 footprint.

Temporarily disable background filtering only to diagnose:

```python
zs.pp.tile_tissues(wsi, 256, mpp=0.5, background_filter=False)
```

## Key Mismatches

Feature rows correspond to the tile table used during extraction. If counts differ, regenerate from matching tiles; do not trim arrays to force alignment.

## Persistence Surprise

`store` stores LazySlide outputs, not pixels. Reopening still requires the source WSI. Use `store="analysis.zarr"` for an explicit file path, `store="analysis-dir/"` to collect stores in a directory, `store="auto"` for a sibling `.zarr` next to the slide, or `store=None` for no persistence.
