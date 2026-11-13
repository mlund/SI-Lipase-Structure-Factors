[![DOI](https://zenodo.org/badge/296540544.svg)](https://zenodo.org/badge/latestdoi/296540544)
[![Code: MIT](https://img.shields.io/badge/Code-MIT-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/Data-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA)

# Electronic notebooks: Anisotropic protein-protein interactions in dilute and concentrated solutions

Supporting information for

> C. Pasquier, S. Midtgaard, M. Polimeni, C. I. Jørgensen, L. Arleth, T. Callisen, M. Lund,
> *Anisotropic protein-protein interactions in dilute and concentrated solutions*,
> J. Colloid Interface Sci. **629**, 794–804 (2023). [doi:10.1016/j.jcis.2022.08.054](https://doi.org/10.1016/j.jcis.2022.08.054)

It contains experimental SAXS data for *Thermomyces lanuginosus* lipase (TLL), simulation input and output
from Metropolis Monte Carlo simulations with [Faunus](https://github.com/mlund/faunus), and Jupyter notebooks
that turn them into the figures of the paper.

## Layout

Directories follow the parts of the paper; each has a `README.md` with data origin, file formats and units.

| Directory | Content |
|---|---|
| [`experiments/`](experiments/) | SAXS intensities I(q) and pair-distance distributions p(r), four sample series |
| [`onebody/`](onebody/) | Salt excess chemical potential in concentrated protein solutions |
| [`twobody/`](twobody/) | Two proteins: potentials of mean force and second virial coefficients, B2 |
| [`manybody/`](manybody/) | Many proteins: structure factors S(q), S(0) and I(q) |

In each part, `noswap/` uses rigid open or closed lipase conformations, and `swap/` lets each protein switch
between them during the simulation.

## Reproducing the figures

Install [uv](https://docs.astral.sh/uv/), then

``` bash
uv sync
uv run jupyter lab
```

`uv` installs the Python version in `.python-version` and the exact package versions in `uv.lock`.

The analysis notebooks below run from a clean checkout and regenerate the figures and derived data from the
archived simulation output. CI executes all of them on every push.

| Notebook | Produces | Paper |
|---|---|---|
| `experiments/plot_experiments.ipynb` | Experimental I(q)/c and p(r) | Fig. 4 |
| `onebody/excess_chemical_potential.ipynb` | Salt excess chemical potential, γ_s | Fig. 12 |
| `twobody/noswap/plot_2body_noswap.ipynb` | B2 vs. hydrophobic interaction strength; B2 deviation heatmap | Figs. 5, 7 |
| `twobody/swap/Analysis_eps_*.ipynb` | PMFs and B2 with conformational swap; fits ε_HH | Sec. 3.2.3 |
| `manybody/noswap/plot_manybody_noswap.ipynb` | S(q), I(q), 1/S(0) vs. concentration | Figs. 8, 9 |
| `manybody/swap/analysis_epsilon*.ipynb` | S(q), I(q), 1/S(0) and open fraction with conformational swap | Figs. 10, 11 |

Not reproduced here: the all-atom MD that produced the SPIRR structures (Sec. 2.4) and the contact maps (Fig. 6).

The `run_*` notebooks and `*.sh` scripts generated the simulation input and launched the runs on SLURM
clusters with Faunus builds from 2019–2020. They are kept unchanged as a record of how the data was made;
re-running them needs those builds (see each part's README) and is not required to reproduce the figures.

## Development

``` bash
uv add <package>            # add a dependency (updates pyproject.toml and uv.lock)
uv run ruff check --fix     # lint notebooks
uv run ruff format          # format notebooks
```

## License

Code (notebooks, scripts) is licensed under [MIT](LICENSE); data under [CC BY 4.0](LICENSE-DATA).
