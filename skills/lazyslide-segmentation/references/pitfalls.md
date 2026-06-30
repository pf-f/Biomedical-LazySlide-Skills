# LazySlide Segmentation Pitfalls

- Cell models are MPP-sensitive. Do not run blindly when slide MPP is missing or tile spec was inferred from bad metadata.
- Overlapping tiles can duplicate objects. Use overlap only when needed and enable ownership/NMS options where supported.
- `extract_features=True` increases memory and storage use.
- A segmentation plot that looks plausible is not validation; use labels and metrics for claims.
- Metrics are meaningless if prediction/reference masks have different resolution, extent, class mapping, or ignored-background definition.
- Gated or non-commercial models require explicit access and license compatibility.
- Store multiple model outputs under different keys; do not overwrite `cells` or `tissues` when comparing models.
- LazySlide API model names and lazyslide-models registry names can differ. Example: `zs.seg.tissue(..., model="grandqc")` loads the GrandQC tissue model; `grandqc-tissue` is not accepted by `zs.seg.tissue`.
- GrandQC artifact segmentation is strict about tile spec. Variant `7x` expects 512x512 tiles at 1.5 MPP; wrong MPP or 256 px tiles fail before inference.
