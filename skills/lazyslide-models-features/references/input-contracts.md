# LazySlide Models and Features Input Contracts

## Before Feature Extraction

Require:

- Open `WSIData`.
- Existing `tile_key` with visually checked tiles.
- Valid MPP/tile size for the selected model.
- Model name available in installed `lazyslide_models` or `timm`.
- Device plan: `cpu`, `cuda`, or `mps`.
- Storage plan for feature tables, especially dense ViT features.

## Feature Table Contract

Feature table rows correspond to the image regions from `tile_key` at extraction time.

Before downstream analysis:

```python
print(list(wsi.shapes))
print(list(wsi.tables))
features = wsi.tables["uni_tiles"]
tiles = wsi.shapes["tiles"]
print(features.n_obs, len(tiles))
```

Do not repair mismatches by truncation. Regenerate matched features.

## Aggregation Contract

For slide- or group-level aggregation, define:

- Feature table.
- Grouping variable (`tissue_id`, slide id, patient id, or none for slide-level).
- Encoder (`mean` or learned slide encoder).
- Biological/statistical unit represented by each output row.

## Text/Image Contract

For text embedding and zero-shot:

- Prompts/classes must be explicit.
- Prompt wording should be recorded.
- Model must support image-text co-embedding.
- Output scores are not calibrated diagnoses.

## Generative Contract

For virtual staining or generated images:

- Confirm input stain/domain matches model.
- Confirm output is for exploration or visualization unless validated.
- Record model, checkpoint, seed, device, and preprocessing.

