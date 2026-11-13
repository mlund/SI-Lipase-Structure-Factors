# Two body: potentials of mean force and B2

Two TLL proteins in a cylindrical cell (L = 500 Å, R = 80 Å) at pH 8 and 0.105 M 1:1 salt (implicit;
Debye–Hückel screening), with Lennard-Jones interactions between residues. All residues have strength ε_LJ.
Hydrophobic residues (SASA > 30 Å²) have ε_HH, which is fitted to the experimental B2 of wildtype TLL
(paper Sec. 2.5.1, 3.2.1).
The second virial coefficient is B2 = −2π ∫ (e^(−w(r)) − 1) r² dr, reported as B2/B2_HS with
hard-sphere diameter σ = 2 × 27.8 Å.

## `noswap/`: rigid conformations

Notebook: `plot_2body_noswap.ipynb`.

- Computes B2/B2_HS vs. ε_HH from each `rdf.dat` and writes `mc/b2-<series>-<structure>-e<ε_LJ>.dat`
  with columns ε_HH (kT) and B2/B2_HS.
- Plots B2/B2_HS against the experimental value (dashed line).
- Writes `mc/data/b2-heatmap.pdf`.
- B2/B2_HS vs. ε_HH is paper Fig. 5; the heatmap is Fig. 7. The best-fit ε_HH values are in Table 3.
- The heatmap shows |B2_sim − B2_exp| per protein variant and model. The numbers are typed into the notebook.
  They were presumably computed from the `series1_R20`, `series3_R20mix` and `series4mix` runs at the
  Table 3 ε_HH values, against the experimental B2 in paper Table 2. The script that computed them is not
  archived.

`mc/`
: Inputs:
  - Structures (`.aam`, Faunus format: name, index, x, y, z (Å), charge, mass, radius (Å)):
    - `1du4_closed.aam`: chain A of PDB 1DU4, closed lid.
    - `1ein_open.aam`: chain A of PDB 1EIN, open lid.
    - `SPIRR-*-frame*.aam`: TLL+ (with the SPIRR propeptide). These are snapshots from all-atom MD
      (Amber ff14SB), paper Sec. 2.4.
    - `*_R20.aam`: glycosylated variants (TLLm). They carry a neutral 20 Å bead on the mannose unit at Asn33.
  - `twobody.cpp` and `CMakeLists.txt`: the simulation program, built by `run_2body_noswap.ipynb`.

`mc/data/<series>-<structure>-h<ε_HH>-e<ε_LJ>[-mod<m>]/`
: One run per directory. ε values are in kT. `structure` is `open`, `closed` or `both` (one of each).
  `mod` offsets the MC displacement parameters, giving independent replicas.
  - Series: `series1_R20` = TLLm, `series2` = TLL, `series3_R20mix` = TLLm+, `series4mix` = TLL+.
    In the `mix` series, one protein has SPIRR and one does not, which approximates the 63 % SPIRR content
    measured by mass spectrometry.
  - `hsa.json`: Faunus input.
  - `rdf.dat`, `rdf_eq.dat`: histogram of mass-centre separation; columns r (Å), counts. Production and
    equilibration. The notebook normalises by the mean of the last 20 bins to get g(r), and then
    w(r) = −ln g(r).
  - `eq`, `out`, `stderr`: program output.

## `swap/`: conformational swap

Notebooks: `Analysis_eps_0.05.ipynb` and `Analysis_eps_0.005.ipynb`. They fit ε_HH for the swap model
(0.404 kT at ε_LJ = 0.05 kT; 0.537 kT at ε_LJ = 0.005 kT; paper Sec. 3.2.3), which is then used in
`manybody/swap/`.

- Integrate the mean force to a PMF, w(r) = −∫ F dr.
- Compute B2/B2_HS per replica and from the replica-averaged force.
- Compare with experiment (dashed lines).

`TLL_wildtype/<ε_LJ>/<ε_HH>/<replica>/`
: ε values in kJ/mol (ε/kT × 2.476, so e.g. `0.12380000000000001` is 0.05 kT); replicas 0–4.
  - `Av_force_vs_r.dat`: mean force between the proteins along r, from virtual translation; columns r (Å),
    F (kT/Å). The notebooks start from this file.
  - `input.json`, `out.json`, `state.json`: Faunus input, output and final state.
  - `energy.dat`, `Q_total.dat`, `rho-protein*.dat`, `confout.pqr`: energies, net charge,
    density profiles and final configuration.
  - The raw per-step `R.dat` and `vt.dat` that `Av_force_vs_r.dat` was reduced from are not archived. The
    first analysis cell skips them.

`tll-close_open.pqr`, `tll-close.pqr`, `tll-closed_coralie.pqr`
: Structures with charges (Å, e).

## Re-running the simulations

The `run_*` notebooks generated the inputs and submitted jobs. They are kept unchanged and need:

- `noswap/`: the legacy C++ Faunus at
  [`cpasquier/faunus@a0f0b469`](https://github.com/cpasquier/faunus/tree/a0f0b469d57c45e9d0345f9dc8356b57551beb4b),
  built with CMake together with `mc/twobody.cpp`.
- `swap/`: a Faunus development build, git revision `b86d549` (Sep 2020), as recorded in `out.json`.
- SLURM (`sbatch`) via `submit.sh` and `submit_state.sh`. Cluster accounts and paths are hard-coded.
  `OMP_NUM_THREADS=N;faunus ...` does not export the variable to Faunus.
