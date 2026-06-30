#!/usr/bin/env python3
"""Print a LazySlide spatial-omics workflow checklist."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", choices=["rnalinker", "path2space", "survival", "mofa"], required=True)
    parser.add_argument("--sample-id", default="sample")
    args = parser.parse_args()

    print("LazySlide spatial-omics plan")
    print(f"- Workflow: {args.workflow}")
    print(f"- Sample/cohort: {args.sample_id}")
    print("\nPre-run checks:")
    print("- Define statistical unit: spot, tile, tissue, slide, patient, or sample.")
    print("- Verify explicit IDs for joins; never rely on row order.")
    print("- Document expression units and feature preprocessing.")
    print("- Keep predictions distinct from measured assays.")
    print("- Avoid clinical or strong biological conclusions without validation.")
    print("\nSkeleton:")
    if args.workflow == "rnalinker":
        print("  linker = zs.tl.RNALinker(wsi_features, rna)")
        print('  linker.associate(method="spearman", score_key="score_column")')
        print("  genes = linker.associated_genes(100)")
    elif args.workflow == "path2space":
        print('  # create spot-centered tiles under tile_key="spots"')
        print('  zs.tl.feature_extraction(wsi, "ctranspath", tile_key="spots", amp=False)')
        print('  zs.tl.feature_prediction(wsi, "path2space", tile_key="spots", batch_size=16, amp=False)')
        print("  # align predictions to measured ST by spot IDs and compare correlations")
    elif args.workflow == "survival":
        print("  # aggregate WSI features to slide/patient level")
        print("  # join survival metadata by patient/slide ID")
        print("  # split/evaluate at patient level")
    else:
        print('  mdata = mu.MuData({"wsi": wsi_features, "rna": rna})')
        print("  mu.tl.mofa(mdata, verbose=False)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

