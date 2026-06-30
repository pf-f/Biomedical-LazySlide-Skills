# LazySlide Annotation IO Input Contracts

## Before Import

Require:

- Annotation file path and format.
- Matching WSI object opened from the corresponding slide.
- Known exporter/tool: QuPath, GeoJSON, NDPA, or other.
- Coordinate system expectation: level-0 pixels, bounded-image origin, or vendor metadata.
- Class/label field location.

## Before Joining to Tiles

Require:

- Destination `join_to` key exists.
- Source `join_with` key exists when used.
- Labeling rule for overlapping annotations: any overlap, largest overlap, centroid inside, or custom.
- Plan for tiles intersecting multiple classes.

## Before Export

Require:

- Shape key exists.
- Class field exists if exporting classes.
- Parent output directory exists.
- Receiving tool coordinate expectation is known.

