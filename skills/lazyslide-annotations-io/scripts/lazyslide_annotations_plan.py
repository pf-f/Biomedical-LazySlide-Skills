#!/usr/bin/env python3
"""Print a LazySlide annotation IO workflow checklist."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", choices=["load", "join", "roi-tiles", "export"], required=True)
    parser.add_argument("--file", default="annotations.geojson")
    parser.add_argument("--key", default="annotations")
    parser.add_argument("--tile-key", default="tiles")
    args = parser.parse_args()

    print("LazySlide annotation IO plan")
    print(f"- Action: {args.action}")
    print(f"- File/key: {args.file} / {args.key}")
    print("\nChecks:")
    print("- Confirm annotation belongs to the opened WSI.")
    print("- Confirm coordinate system and class field.")
    print("- Treat GeoJSON/QuPath no-CRS warnings as expected for level-0 pixel coordinates; verify origin/scale instead of assigning a map CRS.")
    print("- Plot imported geometry before joining/filtering.")
    print("- Preserve original key while testing transforms.")
    print("\nSkeleton:")
    if args.action == "load":
        print(f'  zs.io.load_annotations(wsi, "{args.file}", key_added="{args.key}")')
        print(f'  zs.pl.annotations(wsi, key="{args.key}")')
    elif args.action == "join":
        print(f'  zs.io.load_annotations(wsi, "{args.file}", join_with="{args.tile_key}", join_to="{args.tile_key}", key_added="{args.key}")')
        print(f'  print(wsi.shapes["{args.tile_key}"].columns)')
    elif args.action == "roi-tiles":
        print(f'  zs.pp.tile_tissues(wsi, 256, mpp=0.5, tissue_key="{args.key}", key_added="roi_tiles")')
    else:
        print(f'  zs.io.export_annotations(wsi, key="{args.key}", format="qupath", file="{args.file}")')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
