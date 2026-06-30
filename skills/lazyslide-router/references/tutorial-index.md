# LazySlide Tutorial and Reference Index

This is a concise index for choosing what to read upstream. It is not a copy of the tutorials.

## Getting Started

- Digital pathology primer: terminology for WSI, pixels, magnification, MPP, tiles, annotations.
- First analysis: model-free first slide workflow using sample data, tissue detection, tiling, feature extraction, plotting.
- Installation: package install, reader backends, optional model/runtime dependencies.

## Concepts

- Workflow: `zs.pp` prepares spatial regions, `zs.seg` runs learned segmentation, `zs.tl` analyzes tiles/features, `zs.pl` visualizes, `zs.io` exchanges annotations.
- Data model: `WSIData` stores results in `wsi.shapes`, `wsi.tables`, `wsi.images`, `wsi.attrs`; most functions mutate the object in place.
- Resolution: MPP and tile size determine biological field of view; missing or wrong MPP is a data-quality problem.
- Choosing models: decide from task, tissue domain, input MPP, compute budget, license, and gated access.

## Tutorials

- Preprocessing: raw WSI to analysis-ready object, tissue detection and tiling.
- Visualization: tissue, tiles, annotations, feature-colored plots.
- Feature extraction and spatial analysis: tile embeddings, scanpy-style feature analysis, `spatial_domain`, `tile_graph`, spatial feature smoothing, text-image similarity.
- Cell segmentation: prepare model-compatible tiles, run cells segmentation, inspect cell features/classes.
- Zero-shot learning: prompt/text-image similarity and model assumptions.
- Image generation and virtual staining: generative model use, validation and license risk.
- Build tile model: approximate segmentation through tile prediction.
- Multiple slides: slide-level labels and dataset-level processing.
- Genomics integration: WSI aggregated features with RNA-seq, MOFA-style integration, `RNALinker`.
- Gene expression prediction: Path2Space, spot-centered tiling, CTransPath features, spatial smoothing, comparison to measured ST.
- Survival prediction: slide-level features, survival metadata, c-index/KM demo; not clinical evidence.

## How-To Guides

- Installation and environments: import checks, smoke test, readers, Hugging Face auth/offline cache.
- Slides and storage: `open_wsi`, `store`, `wsi.write`, source WSI remains required.
- Tissue and tiles: `find_tissues`, learned tissue models, tile size/MPP, overlap, no-tile debugging.
- Models and features: `list_models`, devices, memory tuning, dense features, cells features, aggregation.
- Segmentation: tissue vs learned tissue segmentation, cells, semantic segmentation, metrics.
- Annotations: GeoJSON, QuPath, NDPA, class inspection, joins, coordinate shifts, export.
- Visualization: tissue/tile/annotation plots, feature coloring, zoom, blank plot debugging.
- Troubleshooting: reader failures, MPP issues, model download, OOM, key errors, feature/tile mismatches.

## API Groups

- `lazyslide.pp`: `find_tissues`, `tile_tissues`, `tile_graph`
- `lazyslide.seg`: `tissue`, `cells`, `semantic`, `artifact`
- `lazyslide.tl`: `feature_extraction`, `feature_aggregation`, `feature_prediction`, `spatial_features`, `spatial_domain`, `tile_prediction`, `text_embedding`, `text_image_similarity`, `RNALinker`, `zero_shot_score`, `slide_caption`, `virtual_stain`, `image_generation`
- `lazyslide.pl`: `tissue`, `tiles`, `annotations`, `WSIViewer`
- `lazyslide.io`: `load_annotations`, `export_annotations`
- `lazyslide.metrics.segmentation`: semantic and instance segmentation metrics
- `lazyslide_models`: `list_models`, model registry and model classes
