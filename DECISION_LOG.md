# Decision log

- 2026-11-10: User's Chunk 1 brief authorises project initialisation and tests in
  the previously README-only checkout. Preserve this checkout and its history;
  do not create a worktree for a cloud task already isolated by the platform.
- Use a standard `src/inflammappbpk` layout, with mechanism namespaces explicitly
  marked unimplemented. Keep biological modelling in later chunks.
- Reference Python 3.12, isolated `.venv`, uv frozen lock and CPU. Resolve all
  groups together, install core then extras. NumPyro is the sole Bayesian stack;
  SciPy optimisation is included with SciPy. No duplicate PyMC installation.
- JAX 0.6.2/JAXlib 0.6.2 with x64 passed generic numerical/gradient tests; SciPy
  remains the reference stiff solver until actual model-level verification.
- Use writable cache configuration via `scripts/environment.sh` without changing
  HOME, proxy settings, trust stores or TLS verification.
- Research-domain additions are draft configuration only until user review/save.
  HTTP proxy 403 errors are access failures, not evidence of missing publications.
- Fetch only bounded public source files, pin OSP Git commits, log hashes, preserve
  units, and distinguish model-development observations from independent data.
- The 7E3 source model states GPLv2; verify underlying observation/report rights
  separately. Keep raw and processed third-party artifacts outside tracked changes.
- Do not transfer mouse/cynomolgus FcRn values to adalimumab in humans or equate
  RNA abundance with receptor kinetics. Leave unsupported parameters unassigned.
- Whole-body/two-pore/FcRn combinations are established by the retrieved OSP
  reports. Novelty remains unresolved; independent IBD physiology transfer is a
  conditional hypothesis requiring a completed prior-art and data review.

- 2026-11-10, Chunk 2: User requested executable mechanistic development in the
  restored checkout. Preserve published environment configuration; no draft
  reapplication, new publication, commits or pushes performed.
- The configured research access now applies. Retrieved PMC3836053 full HTML and
  EMA Humira product information; checked minimal-model equations 1–7 and label
  dosing/PK sections 4.2/5.2. Chunk 1's full prior-art and tissue-data audit remains
  incomplete; this does not prevent numerical mechanism development, but prevents
  scientific validation and novelty claims.
- Implement amount-based conservative fluxes and a piecewise stiff dose driver.
  Pulmonary circulation is serial; spleen/intestines feed portal liver; plasma
  vascular volumes sum to 3 L in the illustrative fixture. Lymph returns once.
- Whole-body organ geometry and kinetics are explicit assumptions. Adopt published
  minimal-model structure and physiological volume/flow partitions, documenting
  deviations (accessibility fraction and lymph volume). Do not claim reproduction
  of a fitted published parameter set.
- Endogenous-IgG competition uses a rapid-equilibrium reservoir; neutral-pH drug
  release is instantaneous. TNF is represented as effective 1:1 binding sites,
  with separate soluble-complex loss and membrane internalisation. These reductions
  require evidence/identifiability testing before biological inference.
- Whole-body residual clearance defaults to zero to avoid adding aggregate clinical
  clearance on top of mechanistic lysosomal loss. Baseline aggregate CL remains
  separately reportable. No empirical clinical-severity or albumin relationship
  is invented. Immunogenicity is optional, zero by default, and experimental.
- All example curves are uncalibrated sensitivity scenarios with an EMA-sourced
  regimen. Recycled flux is a diagnostic integral, excluded from drug mass.

- 2026-11-10, Chunk 3: Confirmed 62 existing tests pass before changes. No published
  configuration edits, previous-change reapplication or publication performed.
- Curate aggregate animal data separately from human aggregate NCA summaries.
  Keep individual fields missing and arm medians/means explicitly typed. Retain
  source hashes and zero-SD flags; never use a reported zero as infinite weight.
- Fit human apparent CL/F and V/F to two healthy-trial summaries with fixed ka,
  then compare a disjoint registered trial. Do not claim residual uncertainty,
  individual profile accuracy, IBD transfer or independent tissue validation.
- Infer only the reduced terminal phase of one mouse aggregate profile. Broad
  investigator priors are labelled as such. Do not reuse same-source PopPK estimates
  as independent literature priors on the same clinical data. Do not estimate
  population/study variability from one curve; test the hierarchical interface only.
- Require unrounded convergence diagnostics and preserve all chain/sample diagnostics.
  A failed diagnostic gate prevents issuing successful convergence claims.
- Use theoretical SC scaling invariance and practical log-sensitivity/profile
  diagnostics to withhold precise absolute or poorly identifiable mechanism estimates.
- Extend global screening to Sobol N128/N64 after the smaller initial screen changed
  materially. Retain confidence bands and report incomplete convergence rather than
  treating point rankings as empirical biology.
- Include both standard- and disease-generated synthetic truth. Use the same
  calibration budget, do not invent colon outputs for A/B, and do not count fixed
  unverified assumptions as clinically established because they are not AIC parameters.
- ATLAS/Yoshihara metadata verified but no assay-normalised individual observations
  acquired. Their sample enrolments do not create a usable validation dataset.
  TAURUS OA article/deposit verified; Zenodo metadata blocked; no expression matrix
  or validated transcript-to-protein mapping. Infliximab validation remains untested.
- Central scientific verdict: inconclusive. Preserve zero independent tissue counts
  and all unfavourable held-out plasma-summary errors. No novelty or superiority
  claim follows from calibration fit, synthetic wins, or visually plausible curves.

- 2026-11-11, Chunk 4: Read prior findings/specifications and ran the 81-test suite
  before changes. Preserve numerical functionality and distinguish software QA
  from biological validation throughout the dashboard and manuscript.
- Implement 15 Streamlit/Plotly research pages with atomic configuration submission,
  explicit control provenance, exact result fingerprints and unsupported-route
  gates. Infliximab is an acknowledged generic IV scaffold, never validated transfer.
- Body-weight/target-capacity/flow scaling and population grids remain explicit
  hypotheses. The UI does not create clinical severity or transcript-to-protein laws.
- Correct zero-clearance half-life and inaccessible peripheral Vss descriptors;
  retain all existing tests and add limiting-case regressions.
- Generate own Matplotlib PNG/SVG/PDF figures to avoid the managed Kaleido file-URL
  limitation. Represent missing infliximab validation as an evidence-gap panel.
- Make setup portable and preserve TLS/proxy trust. Numerical reproduction uses
  immutable OSP input and audited attributed public summary facts; optional raw
  HTML verification remains strict. Do not disable or silently change source pins.
- The full main and fresh source-export workflows each passed 100 tests, Ruff and
  configured mypy. Clean installation verified 211 compatible packages and reproduced
  clinical, global-sensitivity and posterior outputs within recorded tolerances.
  Shared package caches were permitted; no source/data/result cache or private data
  was copied. No remote GitHub publication or clone is claimed.
- All 15 dashboard pages passed integration checks; actual Chromium submitted a
  simulation and rendered Plotly without frontend errors. The QA-only server was
  stopped after verification. No persistent service or environment publication is
  assumed by future runs.
- Write the manuscript and same-agent reviewer-style assessment candidly: independent
  human tissue data are absent, model superiority/novelty and infliximab transfer
  are unproven, and the work is not publication-ready as an IBD validation study.
- No environment draft/settings changes, deployment, publication, commits or pushes.
  Source/licensing decisions and clinical validation require the authors' further work.
