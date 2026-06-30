#!/usr/bin/env python3
"""Print a LazySlide model/feature workflow checklist."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workflow", choices=["feature-extraction", "aggregation", "zero-shot", "prediction", "generation"], required=True)
    parser.add_argument("--model", default="uni")
    parser.add_argument("--tile-key", default="tiles")
    parser.add_argument("--feature-key", default=None)
    args = parser.parse_args()

    feature_key = args.feature_key or args.model
    print("LazySlide model workflow plan")
    print(f"- Workflow: {args.workflow}")
    print(f"- Model: {args.model}")
    print(f"- Tile key: {args.tile_key}")
    print("\nPre-run checks:")
    print("- Confirm tiles exist and match model MPP/tile assumptions.")
    print("- Confirm model is installed/listed, license is compatible, and gated access is granted.")
    print("- Confirm device, batch size, workers, precision, and storage.")
    print("- Record model name/revision and all preprocessing parameters.")
    print("- After extraction, run print(list(wsi.tables)) and use the actual table key associated with the selected tile_key.")
    print("\nSkeleton:")
    if args.workflow == "feature-extraction":
        print(f'  zs.tl.feature_extraction(wsi, model="{args.model}", tile_key="{args.tile_key}", device="cuda", batch_size=8)')
        print("  print(list(wsi.tables))")
    elif args.workflow == "aggregation":
        print(f'  # Replace "{feature_key}" with the actual table key from list(wsi.tables), e.g. "{args.model}_{args.tile_key}".')
        print(f'  zs.tl.feature_aggregation(wsi, feature_key="{feature_key}", by="tissue_id")')
    elif args.workflow == "zero-shot":
        print(f'  embeddings = zs.tl.text_embedding(["class A", "class B"], model="{args.model}")')
        print(f'  zs.tl.text_image_similarity(wsi, embeddings, model="{args.model}", softmax=True)')
    elif args.workflow == "prediction":
        print("  # Prediction outputs are model-derived estimates, not measured assays or clinical evidence.")
        print(f'  zs.tl.feature_prediction(wsi, model="{args.model}", tile_key="{args.tile_key}", batch_size=16)')
    else:
        print(f'  # Use zs.tl.virtual_stain or zs.tl.image_generation with model="{args.model}" after validating domain/license.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
