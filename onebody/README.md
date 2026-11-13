# One body: salt excess chemical potential

Notebook: `excess_chemical_potential.ipynb` plots γ_s = c_s / c_s^p, the ratio of salt concentration with and
without protein, vs. protein concentration (mM), for salt activities a = 0.06, 0.08 and 0.1 M, with
polynomial fits. It writes `salt_final.png`.

The input numbers are typed into the notebook as arrays `a` (with protein) and `b` (reference): 6 protein
concentrations × 3 salt activities each. They come from grand canonical Monte Carlo (GCMC) simulations of a
single protein centred in a spherical cell with explicit 1:1 salt at constant salt chemical potential.
In those simulations the cell radius gives the protein concentration, and NaCl is modelled as beads with
σ = 4.6 Å and ε = 0.01 kT (paper Sec. 2.5.3, 3.2.4, Fig. 12).

The GCMC input and output behind these numbers are not archived.
