# LazySlide Models and Features Pitfalls

- `lazyslide.models` is deprecated; use `lazyslide_models`.
- Public, gated, non-commercial, GPL/AGPL, and custom-license models are mixed in the model zoo. Check license before use.
- Hugging Face access can fail during long jobs; instantiate/download models before dispatching a batch run.
- Small non-gated smoke tests are feasible with models such as `focuslitenn` and GrandQC weights. Full Path2Space is non-gated but the exported model is about 7 GB; treat it as a heavyweight workflow, not a small release smoke test.
- Feature table names usually include tile keys. Inspect actual `wsi.tables` before plotting or analysis.
- Dense ViT features can multiply storage and memory requirements.
- Mixed precision can vary by device; validate outputs for NaNs, especially on MPS.
- Scanpy clustering of image features is exploratory. Do not treat cluster labels as pathology truth without validation.
- Slide-level aggregation changes the statistical unit from tiles to tissue/slide/patient. Avoid tile-level pseudoreplication in downstream statistics.
- Virtual stains, generated images, captions, and zero-shot labels are model outputs, not assays or diagnoses.
