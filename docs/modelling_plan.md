# Mathematical modelling and validation plan

Status: design for later chunks; no whole-body PBPK model is implemented here.
Numerical environment checks use synthetic systems and are not biological evidence.

## 1. States and mass accounting

Use amounts (nmol), time (h), volumes (L), flows and permeability-surface products
(L/h); calculate concentrations from explicit compartment volumes. Organ vascular,
interstitial and endosomal states connect to arterial/venous blood and lymph.
Represent intestinal segments separately only when physiology and outcome data
support the resolution. Account for blood/plasma partition and hematocrit without
mixing whole-blood and plasma flow conventions. Specify systemic/extracellular IgG
competition and receptor units before deriving FcRn equations.

For organ i, schematic vascular and interstitial balances are

```
dA_v,i/dt  = Q_i (C_art - C_v,i) - J_transport,i - J_uptake,v,i + J_recycle,v,i
dA_is,i/dt = J_transport,i - L_i C_is,i - J_uptake,is,i + J_recycle,is,i - J_target,i
```

Complete these with explicit endosomal bound/free states, lymph return, dosing,
degradation, target-complex disposition and all matching gain/loss terms. Integrate
an eliminated-amount accumulator so total administered drug equals drug remaining
plus eliminated drug, including drug in complexes with the correct stoichiometry.
Document which volumes/flows are fixed and which vary with disease.

## 2. Mechanism hierarchy

M0: reproducible reference whole-body antibody PBPK and serum/minimal comparator.
M1: add externally constrained intestinal permeability, interstitial volume and
lymph/vascular changes. M2: add target binding/disposition only when supported.
M3: disease-dependent recycling only when separate evidence justifies it. Ablate
each extension and keep calibration and measurement assumptions identical.

For each pore p, a candidate constant-flow convection/diffusion expression is

```
Pe_p = Jv_p (1 - sigma_p) / PS_p
Js_p = Jv_p (1 - sigma_p) (Cv - Cis exp(-Pe_p)) / (1 - exp(-Pe_p))
```

Verify the exact pore model, partition and hindrance definitions against a chosen
primary source before implementation. Recover the small-Pe limit PS_p(Cv-Cis),
use stable expm1/series forms, and handle signed flow consistently. Sum the two
pore fluxes; enforce fluid balance between transvascular filtration and lymph.
Avoid independently changing pore parameters, PS and lymph in ways that count
one disease effect multiple times.

FcRn states require pH-dependent drug binding, protected recycling/transcytosis,
surface release and degradation of unprotected drug. A fast-equilibrium reduction
needs timescale verification. Track drug and receptor balances and endogenous IgG
competition if saturability is claimed. Exclude artificial drug creation through
receptor recycling.

For target binding, start from D + T <-> DT with kon, koff and complex elimination,
with explicit TNF synthesis/turnover. Document effective stoichiometry, soluble
versus membrane TNF, avidity and accessibility; a reduced 1:1 approximation is a
testable assumption for bivalent IgG/trimeric TNF, not an established molecular
description. Check whether a target-mediated model is identifiable at the available
concentrations before adding it. Add immunogenicity/fecal loss only when data can
support separate mechanisms; represent unexplained clearance uncertainty honestly.

## 3. Parameter and observation provenance

Every physiological/molecular parameter needs source locator, species/disease,
temperature/pH/assay when relevant, units, uncertainty, transformation and whether
measured, literature-derived, calibrated or assumed. The current registry's mouse
and cynomolgus examples are not human adalimumab defaults. Independently measure
or source disease-physiology priors; prohibit using held-out biopsy values to
select their ranges. Single-cell expression can inform a hierarchical prior only
after gene/cell/protein mapping, donor-level processing and sensitivity analysis.
Transcript counts cannot be substituted for functional receptor turnover rates.

Define a separate observation operator for plasma, wet-mass biopsy homogenate,
free interstitial drug, radiolabel, target-bound drug and assay recovery. A biopsy
may combine vascular, interstitial, intracellular and bound fractions. Model
residual blood, homogenate dilution and reporting units from actual assay methods.
Avoid fitting a free-interstitial prediction directly to total homogenate values.

## 4. Numerical verification and inference

Use SciPy BDF/Radau as the reference; nondimensionalise/scaling and tolerances must
resolve all relevant species. Test zero-dose, no-clearance conservation, no-FcRn,
zero-target, permeability limits, receptor saturation, nonnegative states, repeated
dose events and steady-state consistency. Conduct tolerance/step convergence and
cross-solver comparisons on model outputs. JAX/Diffrax are CPU/x64 eligible after
generic checks; verify stiff-model results and gradients against finite differences
before differentiating a PBPK likelihood. Preserve discontinuous dose-event logic.

Begin with structural/practical identifiability and sensitivity (local derivatives
and global screening where meaningful). Fit only identifiable parameter blocks.
Use NumPyro with explicit priors and likelihood, prior/posterior predictive checks,
multiple-chain diagnostics, effective sample sizes and divergences. The current
40-draw synthetic sampler check asserts execution, not inference quality. Validate
estimation with simulated-data recovery before fitting biological observations.

## 5. Outcomes and independent validation

Conditional primary outcome: improvement in held-out log tissue concentration
error for adalimumab under externally determined IBD physiology versus M0. Report
paired per-observation differences in absolute log error, cohort/subject-clustered
uncertainty, geometric mean bias, fold error and prediction-interval coverage.
Use matched tissue:serum ratios as a secondary outcome only when times and assays
are compatible. Prespecify censoring, missingness, tissue definitions and exclusions
after determining data availability and before examining model errors.

Use study/subject splits, never random time-point leakage. Hold human tissue data
out from serum calibration and physiology selection. Use infliximab as a separate
transfer test with independently sourced molecule-specific properties; do not
refit the disease model on its evaluation data. Report all attempted cohorts and
assay differences. Without independent, interpretable tissue data, restrict claims
to implementation benchmarking, serum prediction and uncertainty analysis.

## 6. Gates before Chunk 2

Resolve bibliographic identities and licences; complete the prior-art screen;
confirm calibration and validation data with interpretable assays; select a
reproducible reference model; and write the final state/flux/observation specification.
If access/data remain insufficient, explicitly revise the scientific objective
before presenting a disease-exposure model as validated.
