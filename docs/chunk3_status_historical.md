# Chunk 3 status — 10 November 2026

**Feasible analyses executed. Disease-informed PBPK superiority remains
inconclusive; independent human tissue validation is unavailable.** No Chunk 4,
publication or cloud configuration changes have been performed.

## Data and actual calibrations

- Reviewed model/research/provenance and ran all 62 existing tests before changes.
- Retained all 174 aggregate mouse 7E3 observations with missingness/analyte flags.
  One selected five-point terminal plasma profile supports an exploratory reduced
  likelihood/Bayesian fit; an eight-point same-profile window supports a separate
  one-/two-exponential complexity comparison. Other figures are not held-out studies.
- Retrieved and inspected two human reference-adalimumab source papers. NCT03917628
  supplies two observed healthy-arm GLSM endpoints for calibration; disjoint trial
  NCT02675023 supplies three correlated held-out GLSM endpoints. No raw human
  concentration-time records or individual clinical covariate records were acquired.
- Apparent CL/F=0.019766 L/h and V/F=9.744 L fit the two summaries conditional on
  literature ka=.0219 h^-1. Zero residual degrees of freedom preclude empirical
  human uncertainty estimation. Published arm weight/albumin summaries are retained
  as aggregate descriptors, not imputed individual covariates.
- Held-out summary predictions underestimate AUC_inf by 20.1%, Cmax by 15.5%, and
  AUC_0_336 by 12.4%. These are one-trial healthy exposure comparisons, not IBD,
  tissue or disease-versus-standard model effects. No clinical prediction bands
  or between-study improvement interval is fabricated.

## Estimation, identifiability and uncertainty

- Added bounded weighted least squares, normalized lognormal maximum likelihood,
  nuisance-reoptimised profiles, finite-difference sensitivities, SVD/rank diagnostics,
  AICc, positive-concentration metrics and study-cluster bootstrap eligibility.
- Structural symbolic analysis identifies SC absolute F/CL/V scaling ambiguity;
  apparent parameters are used. Full-model hypothetical log-sensitivity matrices
  have practical rank 4/5 at relative threshold 1e-3, with weak directions reported.
  This numerical threshold is not a structural proof for the nonlinear full model.
- A synthetic plasma-only colon-PS profile reoptimises uptake; all other parameters
  stay fixed. Bound hits and a weakly constrained scanned range are recorded.
  Twenty labelled synthetic datasets test reduced-model parameter recovery.
- Four sequential NUTS chains, 600 warmup + 1000 retained draws per chain, ran on
  five aggregate mouse terminal observations under two stated investigator priors.
  Both met unrounded R-hat<1.01, bulk/tail ESS>400 and zero-divergence requirements.
  Exact diagnostics, chains and working posterior predictive checks are saved.
  Terminal half-life median is about 434 h (working 95% credible interval about
  387–509 h). This is not a human whole-body posterior or population variability
  estimate. Hierarchical API support is tested, but not fitted to a single curve.

## Sensitivity and experiments

- Executed five-dimensional local log sensitivities, eight Morris trajectories and
  Sobol first/total effects at N=128 versus N=64, over three explicitly hypothetical
  priority ranges: 669 distinct global/Morris forward points plus local/profile runs.
  Largest ST change was 0.036. Confidence bands remain substantial; full sampling
  convergence and biological parameter importance are not asserted.
- Compared synthetic A–E candidates with identical one-gain calibration budgets
  and held-out synthetic study clusters, under both standard- and disease-generated
  truth. Synthetic free-colon predictions favour the generating transport model;
  plasma errors do not uniformly favour disease transport. A/B receive no invented
  regional tissue operator.
- Actual mouse full-window AICc: one exponential ~102.71, two exponentials ~98.68.
  This in-sample aggregate-mouse complexity example does not establish IBD novelty.
- All eight requested scientific experiments have explicit eligibility and evidence
  gates. F is excluded; independent disease transport, regionalisation, target
  superiority, transcript constraints and infliximab transfer are not demonstrated.

## Scientific limits and missing evidence

ATLAS and Yoshihara tissue-study identities/abstracts were verified. No individual
biopsy values with dosing histories, units/normalisation and assay recovery were
acquired: **usable independent human tissue observations = 0**. Empty tissue and
tissue:serum validation tables preserve this result. No unsupported comparison
of tissue homogenate with free interstitial concentration is made.

TAURUS primary article and processed-data deposit DOI 10.5281/zenodo.13768607 were
identified. The current proxy denies Zenodo metadata, so processed file sizes and
schema are unknown and no matrix was downloaded. No donor/cell-type differential
expression or quantitative RNA-to-protein assignment is claimed. The EMA Remicade
request returned HTTP 429. No independent infliximab dataset or validated
molecule-specific parameter set was established; cross-biologic transfer is untested.

Whole-body disease/FcRn/TNF geometry and rates remain hypothetical; no complete
human PBPK calibration is claimed. Population variation, assay recovery, tissue
normalisation, censored observations and between-study covariance need data before
credible mechanistic inference. Full prior-art review remains incomplete.

## Verification and artifacts

The expanded suite has **81 passed, 0 failed, 0 skipped**. Ruff passed and mypy
passed for 32 source files. Tests cover estimation recovery, likelihood normalization,
profile nuisance optimisation (including no-nuisance case), SC nonidentifiability,
unit-correct summary formulas, leakage gates, small-cluster uncertainty refusal,
assay-aware tissue/homogenate conversions, missing metadata and hierarchical prior
shapes, alongside all previous PK/PBPK numerical tests.

The seven-step analysis command completed with zero exits and source/script hashes
in `results/chunk3_run_manifest.json`. Outputs are in the six requested results
folders: calibration, validation, sensitivity, identifiability, bayesian, experiments.
Raw/processed third-party data and generated results remain ignored, retained locally.
Source hashes and missingness are versioned in metadata/configuration.

See `research/scientific_findings.md` for direct answers to all eight verdict
questions, `research/validation_summary.md` for evidence classes, and
`docs/inference_and_validation.md` for assumptions/objectives/constraints.
Historical Chunk 1 and Chunk 2 status reports are retained in docs.

## Reproduce

```bash
cd /workspace/INFLAMMAPBPK
source scripts/environment.sh
python scripts/run_chunk3.py
pytest -q
ruff check src tests scripts
mypy src
```

The pipeline stops on failed steps or failed posterior diagnostic gates. It verifies
pinned source content and validates numerical cache identity against semantic model
source and Python/NumPy/SciPy versions. It does not update dependency locks, change
network policy, send data requests to people, commit/push, or publish the environment.
