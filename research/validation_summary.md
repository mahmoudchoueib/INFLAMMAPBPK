# Validation summary

| Evidence class | Executed result | Interpretation |
|---|---|---|
| Human calibration | 2 GLSMs; NCT03917628 | Apparent PK; ka fixed; zero residual df |
| Human plasma holdout | 3 summaries; NCT02675023 | One healthy trial; no raw profile |
| Human tissue holdout | 0 usable observations | Unvalidated; no biopsy/free-ISF substitution |
| Infliximab | 0 independent validation studies | No cross-biologic claim |
| Mouse 7E3 | Terminal n=5; complexity n=8 | Aggregate; no independent holdout |
| Synthetic A–E | Standard and disease generators | Conditional software comparison |
| Bayesian | Mouse model; 4 chains; 2 priors | Diagnostics met; no human PBPK posterior |
| Sensitivity | Morris; Sobol N128/N64 | Hypothetical ranges; convergence qualified |
| Transcriptomics | TAURUS deposit identified; no matrix | Context only; F excluded |

Endpoint choices are retrospective exploratory analysis choices encoded in scripts,
not a prospectively registered protocol. Calibration and validation trial IDs and
cohort IDs are disjoint. Individual identifiers were not published/acquired, so
participant-level overlap cannot be checked directly. US/EU arms from a single
trial are not counted as distinct studies. The remaining mouse figure profiles
are not independent validation cohorts. Source hashes and missingness are retained.

The observation operator separates free interstitial nmol/L, total recovered tissue
nmol/g and extract/homogenate nmol/L. It requires residual vascular content,
accessible interstitial volume per wet gram, representative organ wet mass,
intracellular/complex assay recovery and overall recovery. Homogenate additionally
requires biopsy wet mass and extraction volume. Protein-normalised or ambiguous
radiolabel signals require further assay definitions and are not mapped by default.
No such conversion was invented for ATLAS or the retained mouse tissue observations.

Predefined positive-concentration metrics are log MAE, log RMSE, geometric bias,
absolute fold error, and paired equal-study-weight error differences with cluster
bootstrap only when >=2 independent clusters exist. BLQ data require a censored
likelihood and are rejected by the uncensored log-normal tools. Published summary
confidence intervals are not substituted for individual predictive distributions.
See scientific_findings.md for the eight-part verdict and exact numerical results.
