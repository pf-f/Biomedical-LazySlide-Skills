---
name: lazyslide-models-features
description: Use when a LazySlide task selects or runs lazyslide_models, pathology foundation models, feature extraction or aggregation, tile/feature prediction, zero-shot or text-image workflows, captions, virtual staining, or image generation, including device, memory, license, and gated-access decisions.
---

# LazySlide Models and Features

Use this skill when LazySlide touches model choice, embedding tables, predictions, multimodal text/image workflows, or generative models.

## Required References

- Read `references/input-contracts.md` before model inference.
- Read `references/reference-pack.md` for common workflow skeletons.
- Read `references/pitfalls.md` for licensing, device, feature/tile alignment, and interpretation risks.
- If `lazyslide_models`, torch/device, Hugging Face access, or model packages are missing/partial, route through `$lazyslide-router` environment checks before model selection.

## Model Selection Rules

1. Start from the downstream question, tissue/stain domain, required MPP, and compute budget.
2. Prefer a small/public model for pipeline validation before gated foundation models.
3. Use `from lazyslide_models import list_models` to inspect installed model names.
4. Confirm license and Hugging Face access before batch jobs.
5. Record model name, revision if available, device, precision, batch size, and tile key.

## Feature Extraction Skeleton

```python
from lazyslide_models import list_models
import lazyslide as zs

print(list_models("vision"))
device = "cpu"  # replace only after runtime inspection confirms cuda or mps
zs.tl.feature_extraction(
    wsi,
    model="uni",
    tile_key="tiles_20x",
    key_added="uni_experiment_a",
    device=device,
    batch_size=8,
    num_workers=2,
)
print(list(wsi.tables))
feature_key = "uni_experiment_a"  # matches key_added above; verify it was created
if wsi.tables[feature_key].n_obs != len(wsi.shapes["tiles_20x"]):
    raise RuntimeError("Feature rows do not match tiles; regenerate from the matching tile layer.")
```

Feature tables normally use `{model}_{tile_key}`. Always run `print(list(wsi.tables))` after extraction and use the actual matching table/key in downstream calls.

## Analysis Skeleton

```python
print(list(wsi.tables))
feature_key = "uni_tiles_20x"  # replace with the actual key printed above
adata = wsi.tables[feature_key]
zs.tl.feature_aggregation(wsi, feature_key=feature_key, by="tissue_id")
zs.pp.tile_graph(wsi, tile_key="tiles_20x")
zs.tl.spatial_features(wsi, feature_key=feature_key)
zs.tl.spatial_domain(wsi, feature_key=feature_key, layer="spatial_features")
```

## Stop Conditions

- Tile key is missing or was modified after feature extraction.
- Feature rows do not match the current tile table.
- User wants clinical conclusions from zero-shot, caption, virtual stain, or predicted expression/image outputs.
- Model license, gated access, or offline cache is unresolved.
- MPP/tile size does not match model assumptions or the model documentation has not been checked.

## Script

```bash
LAZYSLIDE_MODELS_FEATURES_SKILL="${LAZYSLIDE_MODELS_FEATURES_SKILL:-$HOME/.codex/skills/lazyslide-models-features}"
DEVICE="${DEVICE:-cpu}"
python "$LAZYSLIDE_MODELS_FEATURES_SKILL/scripts/lazyslide_model_plan.py" --workflow feature-extraction --model uni --tile-key tiles_20x --device "$DEVICE"
```

For a version-controlled run manifest, copy `assets/model_feature_config.example.json` and replace every placeholder with inspected values; the planner does not consume this file automatically.
