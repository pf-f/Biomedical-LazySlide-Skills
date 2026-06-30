#!/usr/bin/env python3
"""Print a LazySlide segmentation workflow checklist."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=["tissue", "cells", "semantic", "artifact"], required=True)
    parser.add_argument("--model", default="instanseg")
    parser.add_argument("--tile-key", default="tiles")
    parser.add_argument("--key-added", default=None)
    args = parser.parse_args()

    key = args.key_added or {"tissue": "tissues_model", "cells": "cells", "semantic": "anatomical_structures", "artifact": "artifacts"}[args.task]
    print("LazySlide segmentation plan")
    print(f"- Task: {args.task}")
    print(f"- Model: {args.model}")
    print(f"- Tile key: {args.tile_key}")
    print(f"- Output key: {key}")
    print("\nPre-run checks:")
    print("- Confirm WSI opens and MPP is valid.")
    print("- Confirm tile size/MPP matches model assumptions.")
    print("- Confirm model license/access and device memory.")
    print("- Inspect existing keys: wsi.shapes, wsi.tables, wsi.images.")
    print("\nSkeleton:")
    if args.task == "tissue":
        print(f'  zs.seg.tissue(wsi, model="{args.model}", key_added="{key}")')
        print(f'  zs.pl.tissue(wsi, tissue_key="{key}")')
    elif args.task == "cells":
        print(f'  zs.seg.cells(wsi, model="{args.model}", tile_key="{args.tile_key}", key_added="{key}", batch_size=1, num_workers=0)')
        print(f'  zs.pl.annotations(wsi, key="{key}")')
    elif args.task == "semantic":
        print(f'  zs.seg.semantic(wsi, model=model, tile_key="{args.tile_key}", class_names=[...], key_added="{key}")')
    else:
        print(f'  zs.seg.artifact(wsi, model="{args.model}", tile_key="{args.tile_key}", key_added="{key}")')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

