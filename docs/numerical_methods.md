# Numerical methods and reproducibility

Run from the checkout:

```bash
source scripts/environment.sh
pytest -q
ruff check src tests scripts
mypy src
python scripts/run_reference_simulations.py
```

`simulate()` uses SciPy BDF by default (rtol=1e-8, atol=1e-10 nmol), with Radau
available. It integrates separately across every bolus event, applies simultaneous
doses together and reports right-continuous values exactly at the dose time.
An IV event enters venous plasma (central in the baseline); an SC event enters
the depot. Continuous infusion is not implemented. Doses outside the horizon,
negative/nonfinite inputs, duplicate or unsorted sample times and invalid model
parameters raise errors. Time starts at zero. No post-step clipping or unexplained
drug renormalisation is used.

Linear reference solutions use matrix exponentials plus event superposition.
One-compartment IV and coincident-rate Bateman solutions provide additional
closed-form checks. Tests cover repeated mixed routes, conservation including
presystemic losses, nonnegativity tolerances, tight/leaky steady partition,
constant-concentration fluid/portal/pulmonary balance, pore limits/back diffusion,
closed-system target stoichiometry, FcRn occupancy and limiting sensitivities.
BDF and Radau agree under tighter tolerances in the test scenario. This is
numerical verification, not experimental validation or proof for every parameter
combination. Negative amounts outside chosen tolerances or a failed solver require
investigation rather than clipping. Very fast rates may require scaling and
component-specific tolerances in future fitted models.

The reference script produces four uncalibrated SC scenarios and a linear
aggregate-PK reference. It saves amount/concentration CSVs, an annotated PNG,
exposure metrics, per-model mass residuals and performance diagnostics under
`results/chunk2/`. The same script benchmarks BDF/Radau on an identical 48-hour IV
scenario; summary.json records wall time and nfev for this machine. Timing is not
a portable performance guarantee. Cumulative recycled flux can exceed administered
dose because a molecule may recycle repeatedly; it is excluded from mass inventory.

Source regimen: EMA Humira product information section 4.2, adult Crohn's disease,
80 mg week 0, 40 mg week 2, then 40 mg every other week. This is a sourced example,
not a treatment recommendation. Section 5.2 reports mean absolute SC
bioavailability 64% after single 40 mg doses, IV CL 11–15 mL/h and Vss 5–6 L.
The linear example selects CL=.013 L/h and V=5.5 L within those aggregate ranges.
Constant F across regimens/disease and ka=.01 h^-1 are assumptions. WholeBody
examples set residual clearance to zero while explicitly modelling catabolism;
aggregate label CL is not added as an independent elimination pathway. The
150 kDa conversion is a generic IgG assumption, not a verified molecule-specific
adalimumab mass. The complete source URL, download size and hash are recorded in
`data/metadata/chunk2_sources.json`. Neither plausible curves nor these aggregate
label comparisons constitute calibration or independent validation.
