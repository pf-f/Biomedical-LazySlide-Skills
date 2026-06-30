---
name: lazyslide-spatial-omics
description: LazySlide spatial omics and slide-level integration workflows linking WSI morphology features with RNA-seq, spatial transcriptomics, AnnData/MuData, RNALinker, Path2Space gene expression prediction, MOFA-style multimodal analysis, slide-level labels, multiple slides, and survival prediction demos. Use when users ask to connect LazySlide features to transcriptomics/genomics/spatial gene expression, predict genes from H&E, aggregate slide features for cohorts, or analyze survival/clinical metadata from WSI features.
---

# LazySlide Spatial Omics

Use this skill when LazySlide morphology features leave a single-slide visualization context and become molecular, sample-level, or patient-level analysis inputs.

## Required References

- Read `references/input-contracts.md` before integrating datasets.
- Read `references/reference-pack.md` for RNALinker, Path2Space, and survival skeletons.
- Read `references/pitfalls.md` before interpreting results.
- If AnnData/Scanpy, LazySlide, model packages, or readers are missing/partial, route through `$lazyslide-router` environment checks before integration.

## Routing Rules

- Need tile/feature extraction first: use `$lazyslide-core-workflow` and `$lazyslide-models-features`.
- Need Path2Space or feature prediction: use this skill plus `$lazyslide-models-features`.
- Need plots: use `$lazyslide-visualization`.
- Need formal condition/statistical conclusions: stop until sample/patient units, design, and validation are clear.

## Integration Checklist

1. Define the statistical unit: spot, tile, tissue, slide, patient, or sample.
2. Confirm WSI features and omics rows are paired by stable IDs, not by row order.
3. Confirm expression units and preprocessing: raw counts, log-normalized, TPM, spatial counts, or predicted values.
4. Keep measured and predicted expression units separate.
5. Split train/test or validate at slide/patient level, not tile level.
6. Use tutorial outputs as demonstrations unless the user's data and design support stronger claims.

## Stop Conditions

- No shared sample/spot/patient ID between WSI and omics inputs.
- User asks to treat Path2Space predictions as measured expression or clinical evidence.
- Survival or clinical metadata lacks censoring/event/time definitions.
- Slide-level labels are joined to tile-level rows and then interpreted as independent tile statistics.
- A single slide or tiny cohort is used for broad biological or clinical conclusions.

## Script

```bash
python skills/lazyslide-spatial-omics/scripts/lazyslide_spatial_omics_plan.py --workflow path2space --sample-id NCBI776
```
