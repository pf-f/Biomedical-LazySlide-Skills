# LazySlide Spatial Omics Reference Pack

## RNALinker

Use `RNALinker` to associate slide-level WSI features with RNA features across matched samples:

```python
import lazyslide as zs

linker = zs.tl.RNALinker(wsi_features, rna)
linker.associate(method="spearman", score_key="calcification")
linker.plot_rank(gene_name="Description")
genes = linker.associated_genes(100, gene_name="Description")
```

Input rows must represent matched samples. Do not rely on row order unless explicitly verified.

`RNALinker` imports `scanpy`; install and record `scanpy` before treating RNALinker failures as data or API problems.

## Path2Space Pattern

Path2Space predicts spatial gene expression from histology features. A typical workflow:

1. Load paired H&E WSI and measured spatial transcriptomics AnnData.
2. Create spot-centered tiles.
3. Extract CTransPath features from spot tiles.
4. Run `zs.tl.feature_prediction(wsi, "path2space", tile_key="spots")`.
5. Align predictions to measured spot IDs through the tile table.
6. Compare spatial patterns with per-gene correlations; do not treat predictions as calibrated molecular counts.

Important language: Path2Space estimates expression from morphology; it does not replace molecular assays and is not for clinical decisions.

Operational note: the public Path2Space exported model is non-gated but large (about 7 GB). For small CI/release checks, validate `zs.tl.feature_prediction` table alignment with a local `FeaturePredictionModelProtocol` fixture that consumes CTransPath-shaped `[n_tiles, 768]` features, then run the real model only in a heavyweight environment.

## Slide-Level Survival Demo Pattern

1. Extract slide/tile features.
2. Aggregate to slide-level representations.
3. Join to patient-level survival metadata.
4. Use patient-level train/test splits.
5. Evaluate with concordance index, Kaplan-Meier, or log-rank only as appropriate.

Tutorial subsets are demonstrations. They do not validate prognostic performance.

Use explicit patient/sample IDs for the join. TCGA-like feature matrices may keep integer observation names while patient IDs live in `obs["PATIENT_ID"]`; joining on row names will silently produce too few matches.

## Multi-Modal Integration

MOFA-style analysis can combine WSI feature AnnData and RNA AnnData in MuData:

```python
import muon as mu

mdata = mu.MuData({"wsi": wsi_features, "rna": rna})
mu.tl.mofa(mdata, verbose=False)
```

Check sample ordering and shared observations before creating `MuData`.

MOFA-style runs require `muon` and `mofapy2`. Tiny smoke-test cohorts can verify execution, but warnings about low sample count mean the factors are not scientifically meaningful.

## Upstream Pages

- Genomics integration: https://lazyslide.readthedocs.io/en/latest/tutorials/genomics_integration.html
- Gene expression prediction: https://lazyslide.readthedocs.io/en/latest/tutorials/gene_expression_prediction.html
- Survival prediction: https://lazyslide.readthedocs.io/en/latest/tutorials/survival_prediction.html
- Multiple slides: https://lazyslide.readthedocs.io/en/latest/tutorials/multiple_slides.html
- `RNALinker`: https://lazyslide.readthedocs.io/en/latest/api/_autogen/lazyslide.tl.RNALinker.html
- `feature_prediction`: https://lazyslide.readthedocs.io/en/latest/api/_autogen/lazyslide.tl.feature_prediction.html
