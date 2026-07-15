# LazySlide Skills

Codex skills for [LazySlide](https://github.com/rendeirolab/LazySlide) workflows.

## Skills

- `lazyslide-router`
- `lazyslide-core-workflow`
- `lazyslide-segmentation`
- `lazyslide-models-features`
- `lazyslide-spatial-omics`
- `lazyslide-visualization`
- `lazyslide-annotations-io`

## Install

Recommended: install the skills into Codex's local skills directory.

```bash
git clone https://github.com/pf-f/Biomedical-LazySlide-Skills.git lazyslide-skills
mkdir -p ~/.codex/skills
rsync -a --exclude '__pycache__/' --exclude '*.pyc' --exclude '.pytest_cache/' lazyslide-skills/skills/lazyslide-* ~/.codex/skills/
```

To update an existing install:

```bash
cd lazyslide-skills
git pull
rsync -a --delete --exclude '__pycache__/' --exclude '*.pyc' --exclude '.pytest_cache/' skills/lazyslide-* ~/.codex/skills/
```

## First Run

Check the active LazySlide runtime before analysis, especially for readers, models, GPU, or HPC jobs:

```bash
python ~/.codex/skills/lazyslide-router/scripts/lazyslide_env.py inspect --profile core --json
python ~/.codex/skills/lazyslide-router/scripts/lazyslide_env.py plan --profile core --manager auto --json
```

Use `create` only after reviewing the plan. Available profiles are `core`, `analysis`, `models-cpu`, `models-gpu`, and `spatial-omics`; GPU plans require an explicit torch index URL and should use emitted commands rather than requirements files.

## Validate

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
python tests/test_release_integrity.py
```

## Upstream Sync

The monthly GitHub workflow checks LazySlide documentation and source metadata against:

- https://lazyslide.readthedocs.io/en/latest/
- https://github.com/rendeirolab/LazySlide
- https://github.com/rendeirolab/lazyslide-tutorials
- https://github.com/rendeirolab/lazyslide-models

It opens a PR with snapshot/report updates under `skills/lazyslide-router/references/` when upstream changes are detected.
