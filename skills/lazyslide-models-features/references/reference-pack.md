# LazySlide Models and Features Reference Pack

## Model Discovery

```python
from lazyslide_models import list_models

list_models()
list_models("vision")
list_models("multimodal")
list_models("segmentation")
list_models("tile_prediction")
```

LazySlide models are maintained in `lazyslide-models`. Use `lazyslide_models`, not the deprecated `lazyslide.models` namespace.

## Feature Extraction

```python
zs.tl.feature_extraction(wsi, model="resnet50", tile_key="tiles")
features = wsi.tables["resnet50_tiles"]
```

After every extraction, inspect actual table keys and use the one associated with the selected tile layer:

```python
print(list(wsi.tables))
feature_key = "resnet50_tiles"  # replace with the actual key
```

Memory tuning:

```python
zs.tl.feature_extraction(
    wsi,
    "uni",
    device="cuda",
    batch_size=8,
    num_workers=2,
    amp=True,
)
```

On Apple MPS, validate mixed precision results before trusting them.

## Dense Features and Pooling

Dense extraction is for compatible ViT models and can require much more storage:

```python
zs.tl.feature_extraction(wsi, model="uni", dense=True, pool_mode="cls_patch_mean")
```

Record `dense` and `pool_mode` because they change feature shape and semantics.

## Feature Aggregation

```python
zs.tl.feature_aggregation(wsi, feature_key="uni_tiles_20x", by="tissue_id")
zs.tl.feature_aggregation(wsi, feature_key="uni_tiles_20x", encoder="mean")
```

Aggregation metadata/results live inside the feature AnnData rather than a new shape layer.

## Spatial Domains

```python
zs.pp.tile_graph(wsi, tile_key="tiles")
zs.tl.spatial_features(wsi, "plip_tiles")
zs.tl.spatial_domain(wsi, feature_key="plip_tiles", layer="spatial_features", resolution=0.2)
zs.pl.tiles(wsi, color="domain", alpha=0.5)
```

## Text/Image and Zero-Shot

```python
terms = ["tumor", "stroma", "necrosis"]
embeddings = zs.tl.text_embedding(terms, model="plip")
zs.tl.text_image_similarity(wsi, embeddings, model="plip", softmax=True)
zs.tl.zero_shot_score(wsi, prompts=terms, model="plip")
```

Treat zero-shot scores as exploratory unless independently validated.

## Prediction and Generation

- `zs.tl.tile_prediction`: tile-level quality/classification models.
- `zs.tl.feature_prediction`: model-derived values from feature matrices, including Path2Space workflows. Treat these as predictions, not measured assays or clinical evidence.
- `zs.tl.virtual_stain`: H&E to multiplex-like output.
- `zs.tl.image_generation`: unconditional or conditional tile image generation.
- `zs.tl.slide_caption`: caption generation.

Prediction, generative, and caption outputs require explicit validation before scientific interpretation. For Path2Space-like expression prediction, keep predicted values separate from measured expression and avoid clinical reporting claims.

## Upstream Pages

- Model zoo: https://lazyslide.readthedocs.io/en/latest/avail_models.html
- Models/features how-to: https://lazyslide.readthedocs.io/en/latest/how-to/models-and-features.html
- Tools API: https://lazyslide.readthedocs.io/en/latest/api/tools.html
- Models repo: https://github.com/rendeirolab/lazyslide-models
