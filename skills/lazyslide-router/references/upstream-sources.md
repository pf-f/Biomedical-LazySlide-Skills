# Upstream Sources and Monthly Alignment

Track upstream changes without bundling downloaded tutorials.

## Sources

| Source | Why track it | Pattern |
| --- | --- | --- |
| ReadTheDocs | Human-facing official docs and rendered API/tutorial pages | `https://lazyslide.readthedocs.io/en/latest/` |
| LazySlide repository | Package source, API implementation, docs config, releases | `https://github.com/rendeirolab/LazySlide` |
| LazySlide tutorials repository | Notebook/tutorial source used to build tutorial pages | `https://github.com/rendeirolab/lazyslide-tutorials` |
| LazySlide models repository | Model registry, model API pages, model zoo metadata, references | `https://github.com/rendeirolab/lazyslide-models` |

## Monthly Workflow

Run:

```bash
LAZYSLIDE_ROUTER_SKILL="${LAZYSLIDE_ROUTER_SKILL:-$HOME/.codex/skills/lazyslide-router}"
python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_upstream_update.py" --write-report --update-snapshot
```

The script records checksums, sizes, URLs, and repository paths. It writes concise reports under `skills/lazyslide-router/references/upstream-reports/`. It does not rewrite skill references.

Review the report and update skills manually when changes affect:

- API names or signatures.
- Model names, licenses, gated access, or package namespace.
- Key defaults such as `tile_key`, `feature_key`, `key_added`, output locations.
- MPP/resolution requirements.
- WSI storage/persistence semantics.
- Tutorial disclaimers, especially gene prediction, survival, and clinical-use language.

## Targeted Lookup

Use:

```bash
LAZYSLIDE_ROUTER_SKILL="${LAZYSLIDE_ROUTER_SKILL:-$HOME/.codex/skills/lazyslide-router}"
python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_upstream_check.py" --query "feature_extraction" --limit 10
```

This searches official URLs and GitHub tree entries for likely source pages. Prefer upstream pages over stale bundled references when resolving conflicts.
