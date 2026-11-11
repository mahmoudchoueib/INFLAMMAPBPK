# Final platform status — 11 November 2026

**Completed executable exploratory platform and reproducibility workflow.
Disease-informed PBPK superiority is not demonstrated. The work is not ready for
publication as a validated IBD tissue-exposure or clinical dosing study.**

## Implemented and tested

- Preserved the existing baseline, minimal and whole-body models, transport, FcRn,
  effective soluble/membrane TMDD, SC, observation, estimation and validation tools.
- Added a pure scenario service and IV/SC CLI, bounded configuration, unit-correct
  mg/mg/kg conversion, explicit hypothetical weight scaling, numerical mass audits
  and exact configuration fingerprints. Unsupported combinations are rejected.
- Implemented all 15 requested Streamlit/Plotly research pages. Controls expose
  names, units, defaults, ranges, source and evidence status. Infliximab requires
  explicit acknowledgement and IV route; no drug-specific validation is implied.
  Population and disease comparisons are labelled hypotheses, not clinical bands.
- Exported 15 scientific figure sets as PNG, SVG and PDF. Each is reproducible and
  classified in its manifest. Infliximab figure 14 is an evidence-gap panel.
- Added Markdown/HTML/JSON reports with configuration, dataset identities,
  parameter/software version hashes, actual fits/metrics, figures and caveats.
- Completed installation/architecture/estimation/validation/dashboard documentation,
  manuscript, same-agent reviewer-style critical assessment and 12-question verdict.
- Removed hardcoded cloud cache paths and scratch-data dependencies. The public
  benchmark uses immutable OSP downloads plus audited, attributed summary facts.
  Optional raw-source verification still enforces its hashes and never silently
  repins content. No private data or browser is needed for numerical reproduction.

## Executed final QA

**Main checkout: 100 passed, 0 failed, 0 skipped. Clean source: 100 passed,
0 failed, 0 skipped.** Ruff passed and mypy passed for 34 source files.
Unit/integration/numerical/mass/solver, leakage, assay, uncertainty and artifact
checks remain active. Fifteen-page Streamlit AppTest coverage and actual Chromium
health/simulation/Plotly smoke tests passed without frontend errors.

A fresh source-export virtual environment installed all 211 compatible packages
and completed `make reproduce` with empty raw/result directories. It obtained
only permitted small public inputs, imported its own installed source, regenerated
all analyses, 45 figure files and three report formats, and passed all checks.
Clinical/Sobol/posterior outputs matched the recorded numerical/Monte Carlo
tolerances. Verified dependency artifact caches were shared; source/data/result
caches and private data were not copied. This is not a claim that GitHub main was
updated or that a remote clone was tested. See docs/quality_assurance.md and the
machine-readable results/quality/clean_reproduction.json.

QA corrected a baseline descriptor bug: zero clearance now means infinite terminal
elimination half-life, and disconnected peripheral volume does not inflate Vss.
No prior positive-clearance numerical fit or whole-body flux equation was changed.

## Scientific evidence remains limited

Two human reference-adalimumab aggregate calibration summaries identify apparent
CL/F and V/F conditional on ka. Three correlated held-out summaries come from
**one healthy trial**; underprediction is 20.1% AUC_inf, 15.5% Cmax and 12.4%
AUC_0_336. There are no raw individual human concentration-time records or clinical
prediction intervals. Arm-level covariates are not imputed as individual records.

The 174 retained aggregate mouse records are not 174 independent validation cases.
The five-point terminal posterior is nested in the eight-point fitting profile;
its inference concerns mouse 7E3 under a working likelihood, not human PBPK.
Full-model practical rank, weak profiles, global sensitivity and synthetic A–E
experiments retain their assumptions and uncertainty. Synthetic plasma results do
not uniformly favour the disease extension. No clinical superiority is inferred.

**Usable independent human tissue observations: 0. Infliximab validation: none.
Quantitative transcriptomics: not performed. Novelty: unproven.** ATLAS/Yoshihara
metadata and TAURUS's article/deposit were identified, but required biopsy histories,
assay normalization, processed expression and molecule-specific parameters were
not established. Whole-body geometry/kinetics/disease modifiers remain largely
assumed. A full prior-art review, independent assay-compatible tissue datasets,
external physiology/kinetics and identifiability-aware validation are still required.

See research/manuscript.md, research/independent_review.md and
research/final_report.md. Hypothetical defaults themselves are not validated human
parameter sets. Software presentation does not change this assessment.

## Exact commands

From this completed source tree, with Python 3.12, Bash and Make:

```bash
bash scripts/install.sh
make reproduce
make dashboard
```

Separate workflows: `make data`, `make baseline`, `make whole`, `make analysis`,
`make examples`, `make figures`, `make report`, `make check`, `make dashboard-smoke`.
CLI examples and optional real-browser QA are in README.md and installation.md.

Generated report: results/report/research_report.html (adjacent Markdown/JSON).
Figures: results/figures. Source bundle: results/release/InflammaPBPK-source.zip.
Historical status reports for Chunks 1–3 are retained in docs.

No environment configuration update, deployment, publication, commit or push was
performed. The source archive and working-tree changes are ready for review;
remote reproducibility requires the completed files to be committed/made available.
Source rights and a project software licence require author release decisions.
