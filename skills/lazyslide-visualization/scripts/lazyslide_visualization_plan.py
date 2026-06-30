#!/usr/bin/env python3
"""Print a LazySlide visualization workflow checklist."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plot", choices=["tissue", "tiles", "annotations"], required=True)
    parser.add_argument("--tissue-key", default="tissues")
    parser.add_argument("--tile-key", default="tiles")
    parser.add_argument("--annotation-key", default="annotations")
    parser.add_argument("--feature-key", default=None)
    parser.add_argument("--color", default=None)
    args = parser.parse_args()

    print("LazySlide visualization plan")
    print("\nPre-plot checks:")
    print("- Inspect list(wsi.shapes), list(wsi.tables), list(wsi.images), list(wsi.attrs).")
    print("- Plot geometry first, then add color/feature layers.")
    print("- If using feature_key, confirm it is the actual table key generated from the same tile_key.")
    print("- Decide whether the color is a raw embedding dimension, cluster/domain, or prediction target.")
    print("- Confirm coordinate system is level-0 pixels for annotations and zoom.")
    print("\nSkeleton:")
    if args.plot == "tissue":
        print(f'  zs.pl.tissue(wsi, tissue_key="{args.tissue_key}")')
    elif args.plot == "tiles":
        options = [f'tile_key="{args.tile_key}"']
        if args.feature_key:
            options.append(f'feature_key="{args.feature_key}"')
        if args.color:
            options.append(f'color="{args.color}"')
        print(f"  zs.pl.tiles(wsi, {', '.join(options)})")
    else:
        color = f', color="{args.color}"' if args.color else ""
        print(f'  zs.pl.annotations(wsi, key="{args.annotation_key}"{color})')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
