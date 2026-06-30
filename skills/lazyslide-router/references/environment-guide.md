# LazySlide Environment Guide

Use this when the LazySlide runtime is unknown, newly installed, or only partly working.

## First-Run Flow

Set the installed router skill path first:

```bash
LAZYSLIDE_ROUTER_SKILL="${LAZYSLIDE_ROUTER_SKILL:-$HOME/.codex/skills/lazyslide-router}"
```

1. Inspect the active Python before analysis:

   ```bash
   python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_env.py" inspect --profile core --json
   ```

   The legacy-compatible inspector remains available:

   ```bash
   python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_inspect_env.py" --json --models
   ```

2. Choose the smallest profile that fits the task:

   - `core`: LazySlide, `wsidata`, OpenSlide/TiffSlide readers.
   - `analysis`: `core` plus AnnData/Scanpy and geometry packages.
   - `models-cpu`: `core` plus `lazyslide_models`, torch, timm, and Hugging Face tooling.
   - `models-gpu`: GPU model work; requires an explicit torch index URL.
   - `spatial-omics`: `analysis` plus model and MOFA-style omics packages.

3. Review a non-mutating environment plan:

   ```bash
   python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_env.py" plan --profile core --manager auto --json
   ```

4. Create or repair only after the plan is reviewed and the user agrees:

   ```bash
   python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_env.py" create --profile core --manager auto --env-name lazyslide
   ```

   The helper refuses `base` for conda managers and does not guess CUDA. For GPU:

   ```bash
   python "$LAZYSLIDE_ROUTER_SKILL/scripts/lazyslide_env.py" plan --profile models-gpu --torch-index-url <torch-index-url> --json
   ```

   For HPC, use `--hpc` with `plan` or `emit`; do not run local `create` on login nodes.

The import name `openslide` is provided by the `openslide-python` distribution.

## Reader Selection

LazySlide relies on WSI reader backends through `wsidata`. TiffSlide and OpenSlide cover many bright-field formats; fastslide, Bio-Formats, cuCIM, pyisyntax, and pylibCZIrw cover specialized performance or vendor needs. Test representative files from the scanner before committing to a pipeline.

Stop when a slide will not open cleanly. Do not assume extension support implies scanner-variant support.

## GPU and HPC Cautions

- Match torch/CUDA builds to the node driver and scheduler image. Do not assume `device="cuda"` works because a login node has NVIDIA tools installed.
- Run imports and small smoke tests on an interactive compute node before submitting long jobs.
- Avoid model downloads and heavy inference on login nodes. Set `HF_HOME`, torch cache, and temporary directories to project/scratch storage.
- For offline compute nodes, pre-download weights on a networked node and set `HF_HUB_OFFLINE=1`.
- Never commit Hugging Face tokens or cluster paths to notebooks, manifests, or skill files.

Pass device explicitly when reproducibility matters:

```python
zs.tl.feature_extraction(wsi, "uni", device="cuda")
zs.tl.feature_extraction(wsi, "resnet50", device="cpu")
zs.tl.feature_extraction(wsi, "uni", device="mps")
```

Reduce model memory pressure in this order:

1. Lower `batch_size`.
2. Lower `num_workers`.
3. Enable mixed precision only where supported and verified.
4. Use a smaller model or fewer/coarser tiles if scientifically acceptable.

On Apple MPS, validate `amp=True` outputs because mixed precision may produce invalid values for some workflows.

## Hugging Face Access

Many models and datasets are gated or license-restricted. Never commit tokens. Authenticate outside notebooks:

```bash
hf auth login
```

For offline compute nodes, pre-download weights on a networked node and set:

```bash
export HF_HUB_OFFLINE=1
```

Use a consistent `HF_HOME` when sharing caches across machines.

## Smoke Tests

Minimal imports:

```bash
python -c "import lazyslide as zs, wsidata; print('lazyslide', zs.__version__)"
python -c "import tiffslide, openslide; print('readers ok')"
```

Model-free LazySlide path:

```python
import lazyslide as zs

wsi = zs.datasets.sample(with_data=False)
zs.pp.find_tissues(wsi, level=-1)
print(len(wsi.shapes["tissues"]))
```

Model package check:

```bash
python -c "from lazyslide_models import list_models; print(len(list_models('vision')))"
```

Reader check: open one representative scanner file, inspect `wsi.properties` and `wsi.fetch.pyramids()`, then stop if metadata or geometry look wrong.

## Reproducibility Fields to Record

- LazySlide, wsidata, lazyslide-models, torch, timm, scanpy versions.
- Slide reader and source WSI path.
- MPP/magnification metadata and any override.
- Tissue/tile keys and parameters.
- Model name, revision if known, device, precision, batch size, workers.
- Feature key, tile key, and aggregation configuration.
- Random seeds and clustering parameters when using scanpy-style analysis.
