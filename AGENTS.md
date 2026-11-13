# Agent instructions

Supporting information for Pasquier et al., J. Colloid Interface Sci. (2022),
doi:10.1016/j.jcis.2022.08.054, archived on Zenodo.
Everything here must let a stranger reproduce the published results.

## Layout

Directories mirror the parts of the paper; keep them, and don't invent new top-level directories.

```
experiments/  SAXS intensities I(q) and pair-distance distributions p(r)
onebody/      salt excess chemical potential (GCMC)
twobody/      two proteins: potentials of mean force and B2
  noswap/     rigid conformations (legacy Faunus, custom twobody.cpp)
  swap/       open/closed conformational swap
manybody/     many proteins: structure factors S(q)
  noswap/     rigid conformations
  swap/       open/closed conformational swap
```

Each part has a `README.md` describing data origin, file formats and units. Update it when files change.

## Notebooks

- `plot_*`, `analysis_*` and `Analysis_*` notebooks reproduce figures from tracked data and must run
  from a clean checkout: `uv run jupyter nbconvert --to notebook --execute --inplace <nb>`.
- `run_*` notebooks and the `*.sh` sbatch scripts are provenance for simulations made with legacy
  Faunus builds on SLURM clusters. Don't modify them; document issues in the part's README instead.
- Paths relative to the notebook's directory, never absolute or user-specific.

## Large files

- Commit inputs, code, and small extracted features (rdf, S(q), energies, averages) that figures use.
- Keep trajectories (`*.xtc`, `*.dcd`, `*.trr`) and generated figures out of git.
- Deposited via the GitHub-Zenodo integration: a GitHub release (SemVer) makes a new Zenodo version.

## Python

- Pythonic and idiomatic; target the `requires-python` in `pyproject.toml`.
- Prefer the standard library. Add a dependency only when it clearly pays for itself, and say why.
- Manage dependencies with uv only: `uv add <pkg>`, `uv add --dev <pkg>`. Never edit `uv.lock` by hand
  or use `pip`/conda. Commit `uv.lock`.
- OS-agnostic I/O: `pathlib.Path` for paths, explicit `encoding="utf-8"` on text I/O.
- Before finishing: `uv run ruff check --fix`, `uv run ruff format`, and re-execute changed notebooks.

## Comments and docs

- Comments explain *why*, not *what*. Brief and terse, minimal jargon.
- Cite equations or papers where a choice follows from them.

## FAIR

- Open, documented formats (plain-text columns, JSON, PDB/PQR); state units.
- Record provenance: every derived file and figure must be reproducible by a notebook.
- Keep `.zenodo.json` and `CITATION.cff` in sync when authors or metadata change.
