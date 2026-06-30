#!/usr/bin/env python3
"""Check whether a slide can be opened and optionally run a model-free LazySlide smoke test."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slide", type=Path, help="Path to WSI file. If omitted, use LazySlide sample data.")
    parser.add_argument("--store", type=Path, help="Optional analysis zarr store path or directory.")
    parser.add_argument(
        "--backed-file",
        type=Path,
        dest="store",
        help="Deprecated alias for --store.",
    )
    parser.add_argument("--smoke-tissue", action="store_true", help="Run pp.find_tissues(level=-1).")
    args = parser.parse_args()

    try:
        import lazyslide as zs
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"LazySlide import failed: {type(exc).__name__}: {exc}")

    if args.slide:
        if not args.slide.exists():
            raise SystemExit(f"Slide does not exist: {args.slide}")
        kwargs = {"store": str(args.store)} if args.store else {}
        wsi = zs.open_wsi(str(args.slide), **kwargs)
    else:
        wsi = zs.datasets.sample(with_data=False)

    print("WSIData opened")
    print(f"properties: {getattr(wsi, 'properties', '<unavailable>')}")
    try:
        print(f"pyramids: {wsi.fetch.pyramids()}")
    except Exception as exc:  # noqa: BLE001
        print(f"pyramids unavailable: {type(exc).__name__}: {exc}")

    if args.smoke_tissue:
        zs.pp.find_tissues(wsi, level=-1, key_added="tissues_smoke")
        print(f"tissues_smoke: {len(wsi.shapes['tissues_smoke'])}")

    print(f"shapes: {list(wsi.shapes)}")
    print(f"tables: {list(wsi.tables)}")
    print(f"images: {list(wsi.images)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
