# LazySlide Domain Map

Use this map to route user requests to the smallest useful skill.

| User intent | Primary skill | Key LazySlide concepts |
| --- | --- | --- |
| Open a slide, inspect metadata, save analysis | `$lazyslide-core-workflow` | `zs.open_wsi`, `WSIData`, `store`, `wsi.write`, readers |
| Find tissue and create tiles | `$lazyslide-core-workflow` | `zs.pp.find_tissues`, `zs.pp.tile_tissues`, MPP, `tile_key`, `tissue_key` |
| Build spatial context between tiles | `$lazyslide-core-workflow` then `$lazyslide-models-features` | `zs.pp.tile_graph`, `zs.tl.spatial_features`, `zs.tl.spatial_domain` |
| Segment tissue/cells/semantic regions | `$lazyslide-segmentation` | `zs.seg.tissue`, `zs.seg.cells`, `zs.seg.semantic`, `key_added` |
| Evaluate segmentation | `$lazyslide-segmentation` | Dice, mean IoU, PQ, class maps, shared resolution |
| Extract pathology image features | `$lazyslide-models-features` | `zs.tl.feature_extraction`, `lazyslide_models.list_models`, devices, `feature_key` |
| Aggregate to slide-level features | `$lazyslide-models-features` | `zs.tl.feature_aggregation`, slide encoders, `agg_slide`, group aggregation |
| Predict tile values or spatial genes | `$lazyslide-models-features` or `$lazyslide-spatial-omics` | `zs.tl.feature_prediction`, Path2Space, calibrated vs relative predictions |
| Use multimodal text prompts | `$lazyslide-models-features` | `zs.tl.text_embedding`, `zs.tl.text_image_similarity`, zero-shot |
| Generate virtual stains or images | `$lazyslide-models-features` | `zs.tl.virtual_stain`, `zs.tl.image_generation`, model license and validation |
| Integrate WSI with RNA or metadata | `$lazyslide-spatial-omics` | `RNALinker`, paired samples, AnnData, sample alignment |
| Survival or slide-level label analysis | `$lazyslide-spatial-omics` | slide aggregation, patient/sample split, censoring, non-clinical demo |
| Visualize tissue/tiles/features | `$lazyslide-visualization` | `zs.pl.tissue`, `zs.pl.tiles`, `zs.pl.annotations`, feature table colors |
| Import/export annotations | `$lazyslide-annotations-io` | GeoJSON, QuPath, NDPA, `in_bounds`, level-0 coordinates, spatial joins |
| Search bundled guidance | `$lazyslide-router` | `lazyslide_docs_search.py` |
| Check upstream docs drift | `$lazyslide-router` | ReadTheDocs, `rendeirolab/LazySlide`, `rendeirolab/lazyslide-tutorials` |

Common entry points:

- Official docs: https://lazyslide.readthedocs.io/en/latest/
- API reference: https://lazyslide.readthedocs.io/en/latest/api/
- Model zoo: https://lazyslide.readthedocs.io/en/latest/avail_models.html
- Package source: https://github.com/rendeirolab/LazySlide
- Tutorial source: https://github.com/rendeirolab/lazyslide-tutorials
