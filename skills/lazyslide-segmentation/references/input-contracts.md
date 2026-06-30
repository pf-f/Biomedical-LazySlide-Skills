# LazySlide Segmentation Input Contracts

## Required Before Any Segmentation

- Open `WSIData` object.
- Valid slide dimensions and reader.
- Known or explicitly overridden MPP when the model expects physical resolution.
- A tissue/tile key appropriate for the segmentation target.
- Confirmed model availability, license, and access.

## Tissue Segmentation

Inputs:

- WSI suitable for bright-field or model-supported stain.
- Optional existing tissue key for comparison.
- For learned GrandQC tissue segmentation, call LazySlide as `zs.seg.tissue(wsi, model="grandqc", ...)`; `grandqc-tissue` is the lazyslide-models registry name, not the `zs.seg.tissue` API option.

Outputs:

- Tissue polygons in `wsi.shapes[key_added]`.

## Cell Segmentation

Inputs:

- Tile layer with model-compatible tile size and MPP.
- Device, batch size, and workers chosen for available memory.

Outputs:

- Cell polygons in `wsi.shapes[key_added]`.
- Optional features in `wsi.tables["cells_features"]` or model-specific table.

## Semantic Segmentation

Inputs:

- Compatible segmentation model object or registry name where supported.
- Tile key.
- Stable class mapping through `class_names`.

Outputs:

- Class polygons/shapes in `wsi.shapes[key_added]`.

## Artifact Segmentation

Inputs:

- Tile layer with the model-required tile size and MPP. For `grandqc-artifact` variant `7x`, use 512 px tiles at 1.5 MPP.
- Small tissue fragments may need `edge=True` and relaxed background filtering to create a smoke-test tile; record that this is a test convenience, not a production recommendation.

Outputs:

- Artifact polygons in `wsi.shapes[key_added]`.

## Evaluation

Inputs:

- Predicted mask/map and reference mask/map at the same resolution and extent.
- Identical class labels and ignored-background rule.

Outputs:

- Metric values with explicit class/background interpretation.
