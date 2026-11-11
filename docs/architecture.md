# Software architecture

The src/inflammappbpk package contains unit-aware infrastructure, analytical and
numerical baselines, minimal PBPK, whole-body circulation, transport, FcRn, TMDD,
optional immunogenicity, inference and assay-aware observation/validation utilities.
Amounts are canonical nmol, volumes L, time h and flow/PS L/h. Mechanism ODEs do
not import Streamlit or depend on a browser.

`research_platform.py` is the pure service shared by the UI and CLI. Scenario
validates every supported control, route, hypothesis opt-in and dose schedule.
`build_model` applies an explicit hypothetical weight scaling law: compartment
volumes and binding-site amounts proportional to weight, plasma flows/PS to
weight^0.75. Central plasma scales consistently. This is not an inferred population
covariate law. `run_scenario` performs dosing conversion with Pint, solves the ODE,
checks nonnegativity/mass balance, and returns concentrations, raw states, numerical
metrics and a configuration fingerprint. Undefined occupancy remains missing.

The Streamlit app exposes 15 research sections through a page selector. Form edits
are submitted atomically; only successful results replace the displayed snapshot.
Downloads identify the exact saved configuration. Stored reference analyses are
labelled independently of live controls. Expensive simulation caching is bounded
by configuration content. Infliximab requires an explicit acknowledgement and IV
route because drug-specific calibration, SC transfer and infusion are unsupported.

Scripts curate public inputs, run statistical analyses, generate three-format
scientific figures and build Markdown/HTML/JSON reports. Makefile orchestrates
these serially. Source and parameter digests distinguish the current working tree
from an old Git revision. Study/cohort leakage gates and observation-type gates
are independent of plotting and cannot be bypassed by changing dashboard labels.

The analysis uses two distinct schemas: individual/aggregate concentration-time
records and correlated study-arm NCA summaries. The latter cannot be treated as
patient-level observations. Whole-body tissue outputs are free interstitial drug;
homogenate comparisons require an explicitly specified TissueAssay operator.

The package does not implement a validated human physiology database, molecular
multivalent TNF binding, dynamic IgG turnover, clinical severity-to-permeability,
RNA-to-protein calibration, IV infusion, a fitted population model, or validated
infliximab disposition. Dashboard controls do not manufacture those capabilities.
