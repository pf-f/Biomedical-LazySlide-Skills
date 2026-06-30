# LazySlide Spatial Omics Input Contracts

## WSI Feature Inputs

Require:

- Feature table generated from stable tile/spot/tissue keys.
- Aggregation level declared: tile, spot, tissue, slide, patient.
- Metadata IDs preserved in `.obs` or an external metadata table.
- No post-feature tile filtering unless features are regenerated.

## Transcriptomics Inputs

Require:

- AnnData or table with sample/spot IDs.
- Expression unit documented: raw counts, log-normalized counts, TPM, or model-derived predicted values that are not measured expression.
- Gene identifiers and symbols mapped consistently.
- Spatial coordinates in `obsm["spatial"]` for spot-level workflows.

## Survival Inputs

Require:

- One row per patient/slide/sample as appropriate.
- Time-to-event column.
- Event/censoring column with explicit coding.
- Train/test or validation split at patient level.
- Covariates if making adjusted claims.

## Path2Space Inputs

Require:

- Paired WSI and ST spots from the same sample.
- Spot coordinates in slide coordinate system or a verified transform.
- Spot tile size and feature extraction model matching Path2Space assumptions.
- Gated dataset/model access where needed.
