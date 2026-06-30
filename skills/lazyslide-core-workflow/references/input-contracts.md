# LazySlide Core Input Contracts

## Slide Inputs

Accepted source files depend on installed readers. Common bright-field formats include SVS and TIFF variants; CZI, iSyntax, Bio-Formats, cuCIM, and other paths require optional backends.

Before analysis, confirm:

- Path exists and is readable.
- Reader opens the file in a minimal session.
- Dimensions and pyramid levels are plausible.
- MPP or physical pixel size is known when tile/model workflows depend on it.
- Source slide remains accessible if using a backed analysis store.

## Tissue Inputs

For `find_tissues`, confirm:

- Image is interpreted as intended, usually RGB bright-field for H&E-like workflows.
- Tissue detection level is fixed for reproducibility when needed.
- `min_tissue_area` and hole thresholds match the size of expected fragments.

## Tile Inputs

For `tile_tissues`, define:

- `tile_px`
- `mpp` or explicit `slide_mpp` override with provenance
- `tissue_key`
- `key_added`
- `overlap` or `stride_px`
- background filtering settings

Tile outputs must be visually checked before downstream feature extraction or segmentation.

## Output Contracts

Downstream functions depend on stable keys:

- If features were extracted from `tiles_20x`, do not replace `tiles_20x` without regenerating features.
- If a tile table is filtered, either create a new tile key or regenerate dependent feature tables.
- Store complete run parameters outside short human-readable keys.

