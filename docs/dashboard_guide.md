# Dashboard guide

Launch with `make dashboard` or `bash scripts/run_dashboard.sh --server.port 8501`.
The service binds to loopback by default. Use the platform's authorised browser or
your local browser after launch; this repository does not deploy or publish it.

Select one of 15 research pages. Enter a configuration in the sidebar, then select
**Run exploratory simulation**. Pending form edits do not change displayed results
until submitted successfully. Inspect the displayed fingerprint, full configuration
and mass audit, and download the exact CSV/configuration snapshot. A rejected input
preserves the previous successful snapshot with its identity clearly displayed.

Every numerical control has units, bounds, default, source and evidence status in
its help and the control-provenance table. Bounds are exploration guardrails,
not validated physiological intervals. Mechanistic defaults outside established
human evidence are labelled as assumptions. The reference disease scenario
requires PS/flow/lymph multipliers of 1. To study other values, select the explicit
regional hypothesis. Clinical severity and albumin are not converted to coefficients.

IV is a bolus. SC uses a depot and lymph transit; absorption controls are irrelevant
for IV. Absolute mg and mg/kg doses are distinct; the latter changes administered
mass when body weight changes. All administrations must lie within the horizon.
Body weight is restricted to the adult exploratory range 40–150 kg. Weight-scaled
physiology and receptor amounts are assumptions, with conserved circulation.

Adalimumab whole-body results are exploratory. Infliximab enables a generic IV
scaffold only after acknowledgement; it has no molecule-specific calibration or
external validation. Do not use the name selection as evidence of drug transfer.

Tissue plots show **free interstitial** concentrations. They are not biopsy
homogenates. Occupancy requires nonzero target sites; otherwise it is undefined.
Recycled flux is a repeated-passage integral, excluded from remaining-drug mass.
The population page is a deterministic three-weight grid, not a prediction band.
The inflammation comparison changes transport while keeping dose/target/FcRn fixed.

Sensitivity, Bayesian, comparison and validation pages read the stored reference
analyses created by `make analysis`. They do not refit those analyses when live
controls change. Bayesian curves concern five aggregate mouse observations, not
human whole-body uncertainty. A/B have no colon operator. F is excluded. The
validation page retains one held-out healthy trial and zero independent human
tissue observations. Missing result files give an explicit generation command.

This is a research tool, not a clinical decision-support or dosing recommendation
system. No appearance or successful ODE run changes the evidence classification.
