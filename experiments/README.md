# Experiments: SAXS

Small-angle X-ray scattering on four variants of TLL at increasing protein concentration (paper Sec. 2.3,
Fig. 4). Notebook: `plot_experiments.ipynb` plots I(q)/c and normalised p(r) for every series.

| Series | Directory in `exp_data/` | Variant | Concentrations (g/L) |
|---|---|---|---|
| 1 | `1-nospirr_GLYC` | TLLm: glycosylated | 0.32, 0.7, 2.29, 3.8, 5.05, 6.44, 7.15, 7.85 |
| 2 | `2-nospirr_noglyc` | TLL: wildtype, deglycosylated | 0.34, 0.67, 1.24, 2.47, 3.07, 4.2, 5.6, 6.06 |
| 3 | `3-SPIRR_GLYC` | TLLm+: glycosylated, with SPIRR | 0.69, 1.51, 2.76, 3.81, 5.84, 6.81, 6.73 |
| 4 | `4-SPIRR_noglyc` | TLL+: with SPIRR | 0.44, 1.10, 1.62, 3.38, 4.19, 5.76, 7.22, 8.01 |

- **SPIRR:** the Ser-Pro-Ile-Arg-Arg propeptide at the N-terminus.
- **Deglycosylation:** Endoglycosidase H, which leaves one mannose unit on Asn33.
- **Buffer:** pH 8, 10 mM Tris + 100 mM NaCl.
- **Concentrations:** from amino acid analysis.
- **Setup:** BioXolver L (Xenocs) with a Ga MetalJet source (λ = 1.34 Å), 298 K, 20 × 30 s exposures,
  sample-detector distance 654 mm.
- **Reduction:** averaged with RAW and put on absolute scale with water.
- **Simulations:** series 2 is the one compared with them in `twobody/` and `manybody/`.

The file-to-concentration mapping is hard-coded in the notebook, in the order the files are loaded.

## Files

`exp_data/<series>/RBS_A_<run>_<well>-T<n>_lipase_s<series>_<nnn>_c.dat`
: Buffer-subtracted, rebinned intensity on absolute scale. Three `###` header lines, then
  whitespace-separated columns: q (Å⁻¹), I(q) (cm⁻¹), σ(I), and a fourth column that is always 0.
  I(q) is not divided by concentration; the notebook divides by c in g/L, i.e. mg/mL.

`Pr/series<n>/Result_<file>.dat/`
: Indirect Fourier transform of each curve with BayesApp.
  - `estimate.d`: p(r); columns r (Å), p(r), σ(p). The notebook plots this.
  - `fit.d`: fit to the data; columns q (Å⁻¹), I(q) fitted, I(q) smoothed.
  - `data.d`: the input data as used in the fit.
  - `parameters.d`: fit summary, incl. I(0), maximum diameter and radius of gyration (Å).
