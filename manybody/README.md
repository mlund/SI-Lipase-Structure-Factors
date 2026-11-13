# Many body: structure factors

Many TLL proteins in a cubic periodic box at 0.105 M 1:1 salt (implicit; Yukawa screening, Debye length
3.04/√c_s Å, cut off at 5 Debye lengths) and 298.15 K. There are 8 protein concentrations, 0.34–6.06 g/L.
The box length follows from L = (N_p M_w / (N_A c_p))^(1/3), with M_w = 29609.61 g/mol.
Each parameter set is run three times (`dp0`–`dp2`); `dp` offsets the MC displacement parameters, giving
independent replicas.

The structure factor S(q) is computed from protein mass centres. It is averaged over the q-vectors
commensurate with the periodic box (Faunus `scatter` analysis, `scheme: explicit`, `pmax: 200`).
I(q)/c is compared with experiment as P(q)·S(q), where P(q) is the series-2 form factor
`formf_s2_closed.dat` (see below).

## `noswap/`: rigid conformations

Notebook: `plot_manybody_noswap.ipynb`.

- Plots S(q) and I(q) for the four parameter sets and the LJ potentials, writing `lj.pdf`,
  `mc/data/simulated_sofq.pdf` and `mc/data/simulated_iofq.pdf`.
- Plots g(r).
- Fits S(q → 0) and writes `mc/data/<series>-<structure>-e<ε_LJ>_s0.dat` with columns c_p (g/L),
  mean 1/S(0) and its standard deviation over replicas.
- Plots 1/S(0) vs. c_p against experiment, and prints B2/B2_HS from the slope.

`mc/data/<series>-<structure>-h<ε_HH>-e<ε_LJ>-C<c_p>-dp<m>/`
: ε in kT, c_p in g/L.
  - `tll.json`, `tll.out`: Faunus input and output (JSON).
  - `debye_n2.dat`: S(q); columns q (Å⁻¹), S(q).
  - `rdf.dat`: mass-centre g(r); columns r (Å), g(r).
  - `energy.dat`: system energy (kT) vs. MC step.
  - The four parameter sets are `closed-h0.61-e0.05`, `closed-h0.825-e0.005`, `open-h0.355-e0.05` and
    `open-h0.485-e0.005`. `series2-closed-h0.61-e0.05-C6.06-dp2` has no `rdf.dat`.

`mc/data/s0_exp_series2.dat`
: Experimental S(0) for series 2. Columns c_p (g/L), 1/S(0), S(0).

`mc/1du4_closed.aam`, `mc/1ein_open.aam`
: Rigid structures (see `twobody/README.md`).

## `swap/`: conformational swap

Each protein switches between the closed (PDB 1DU4) and open (PDB 1EIN) conformations during the
simulation (`tll-close_open.pqr`). Notebooks: `analysis_epsilon1.ipynb` (ε_HH = 0.404, ε_LJ = 0.05 kT) and
`analysis_epsilon2.ipynb` (ε_HH = 0.537, ε_LJ = 0.005 kT). They plot energies, S(q), g(r), S(0) from a
linear fit for q < 0.046 Å⁻¹, I(q) vs. experiment, and the open/closed population ratio
(`analysis_epsilon1` only).

`series2-close_open-h<ε_HH>-e<ε_LJ>-C<c_p>-dp<m>/`
: Same layout as `noswap/`, but S(q) is in `debye.dat`, equilibration output is in `*_eq.dat`, and
  `tll.out` holds the open/closed histogram.

`series2-close_open-h<ε_HH>-e<ε_LJ>-C<c_p>_moy.dat`
: Replica-averaged S(q); columns q (Å⁻¹), S(q). Written by the notebooks.

`series2-close_open-h<ε_HH>-e<ε_LJ>-dp<m>_intercepts.dat`
: S(0) per replica; columns c_p (g/L), S(0). Written by the notebooks.

## Form factor `formf_s2_closed.dat`

P(q) for I(q)/c; columns q (Å⁻¹), P(q), same units as the series-2 I(q)/c. Both many-body parts use it.

- **Origin:** recovered from the original cluster workspace in 2026. It was most likely computed with CRYSOL
  from the closed crystal structure (chain A of PDB 1DU4), fitted to the dilute series-2 SAXS data.
- **Check:** a Pepsi-SAXS calculation on 1DU4 chain A, fitted to the most dilute series-2 curve (H2), agrees to
  within 0.5% for q ≤ 0.15 Å⁻¹. Above 0.2 Å⁻¹ the archived P(q) is about half of Pepsi's, presumably from
  different hydration-shell or excluded-volume settings.
- **Open vs. closed:** at infinite dilution the protein is believed to be open, and closed only in dimeric
  contact. The open structure (PDB 1EIN) differs from the closed P(q) by less than 4% for q ≤ 0.15 Å⁻¹,
  where S(q) deviates from 1, so the choice barely affects I(q) there.
- **q range:** the file covers 0–0.483 Å⁻¹ and S(q) extends to 0.60 Å⁻¹. `np.interp` holds P(q) constant
  above 0.483 Å⁻¹.
- **Missing original:** `noswap/` originally read `mc/formf_s2.txt`, which is lost. It now uses the same
  `formf_s2_closed.dat`.

## Re-running the simulations

The `run_*` notebooks and `swap/*.sh` scripts generated the inputs and submitted jobs. They are kept
unchanged and need:

- `noswap/`: Faunus git revision `db5c364` (Nov 2019), as recorded in `tll.out`.
- `swap/`: a parallel Faunus development build, git revision `b86d549` (Sep 2020), built with GCC 8.2,
  CMake 3.13 and OpenMPI 3.1.
- SLURM (`sbatch`) with environment modules. Cluster accounts and paths are hard-coded.
  - `eq_*.sh`: equilibration from scratch.
  - `eq_state_*.sh`, `run_*.sh`: continue from `state.json`. The suffix `_3`/`_8` is the number of tasks.
  - Known bugs in the scripts: `cd SLURM_SUBMIT_DIR` is missing the `$`, and `OMP_NUM_THREADS=N;faunus`
    does not export the variable.
