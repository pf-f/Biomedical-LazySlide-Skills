# LazySlide Spatial Omics Pitfalls

- Row order is not a join key. Use explicit sample, spot, slide, or patient IDs.
- Tiles are not independent biological replicates. Avoid tile-level p-values for patient/condition conclusions.
- Aggregating features changes the statistical unit; document whether each row is tissue, slide, or patient.
- Predicted expression is not measured expression. Keep color scales and units separate.
- Path2Space and survival tutorials are demonstrations, not clinical validation.
- Spatial smoothing can improve visual agreement while also changing signal interpretation.
- Small cohorts and single slides cannot support broad biological claims.
- Foundation model features can encode scanner/site/stain effects; consider batch/site confounding.

