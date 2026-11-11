# Chunk 3 estimation and validation methods

## Evidence and splits

`chunk3_curate.py` preserves all 174 aggregate mouse observations, source identities,
reported zero-SD flags, missing individual covariates and unresolved tissue-analyte
labels. Only one wild-type plasma figure is used for mouse fitting. No remaining
mouse figure is called independent validation. The terminal window >=168 h is an
exploratory selection, not a preregistered biological model.

Human observations are a **separate aggregate-summary schema**. The calibration
article PMC13675741 reports observed reference-Humira healthy single-dose GLSMs:
AUC_inf=2,023,643 ng h/mL and Cmax=3,220 ng/mL, 40 mg SC, trial NCT03917628.
Its final PopPK ka=.0219 h^-1 is fixed, not fitted twice as a separate prior.
The held-out trial NCT02675023, PMC5817835 Table 2, US Humira arm, supplies
AUC_inf=2,534,000 ng h/mL (n=91), Cmax=3,809 ng/mL (n=105), and
AUC_0_336=1,023,000 ng h/mL (n=101). Endpoint samples overlap and are not
independent studies. Study IDs and cohort IDs are excluded across splits. Patient
identifiers were not acquired; participant-level overlap cannot be directly checked.
Arm weights and albumin are marked as aggregate descriptors, not patient covariates.
The two populations and immunogenicity assays differ; no body-weight/ADA adjustment
is inferred from these summaries. The multiple endpoints have unknown covariance.

The point-observation validator deliberately rejects missing dose/time/analyte
fields. Aggregate NCA endpoints are not passed off as point concentration data.
Summary source tables, URLs, hashes, missingness and exclusions are retained in
`data/metadata/chunk3_*` and `configs/chunk3_source_manifest.json`. Source hashes
must match before curation. No paper's curve was digitised or treated as raw data.

## Objectives, constraints and uncertainty

Weighted least squares minimises sum((prediction-y)/sigma)^2, or on the log scale
sum((log prediction-log y)/sigma_log)^2. The library requires positive finite
uncertainties; reported zero SD never becomes infinite weight. Bounded trust-region
least squares reports convergence, evaluations, residuals and its Jacobian.
Uncensored log tools reject zero/BLQ observations rather than inserting arbitrary
pseudo-concentrations. A censored likelihood would be required for those records.

The lognormal maximum likelihood includes the normalization and log(y) Jacobian:
NLL=sum(0.5*((log y-log prediction)/sigma)^2+log sigma+log y+log(2 pi)/2).
Mouse terminal fitting estimates concentration at 168 h, terminal rate and log
error, with multiple initial rates and explicit bounds. The complete bounds and
initializations are in the analysis configuration. A full-window mouse
one-/two-exponential comparison uses identical eight-point data and counts residual
sigma in the AICc parameter count. Its log-domain objective avoids underflow during
optimisation. It is an in-sample nonhuman benchmark, not mechanistic novelty.

The healthy SC reduced model fits only apparent CL/F and V/F; ka is held fixed.
Two endpoints and two fitted parameters leave zero residual degrees of freedom.
A log-error scale .15 supplies numerical relative weights, not a measured SEM or
population residual estimate. No covariance-derived human parameter CI is reported.
Dose/AUC_inf is CL/F here; absolute CL requires independently known F. Clinical
AUC/Cmax GLSMs are compared with model summaries as an exploratory transport check,
not as individual or population mean predictions with a validated random-effects
observation model. Their exact fit does not demonstrate goodness of fit.

## Identifiability

For a known IV dose, observables D/V and CL/V have a full-rank Jacobian in V and CL.
For SC with unknown F, scaling (V,CL,F) together leaves the curve invariant. The
symbolic Jacobian has rank 3 in four coordinates (V,CL,F,ka); absorption/elimination
pole assignment may require IV information or other constraints as well. This
supports fitting apparent parameters, not absolute physiology.

Profile likelihood fixes a parameter and reoptimises all nuisance coordinates at
each value with multiple starts. Mouse rate profiles estimate residual sigma as a
nuisance; the asymptotic chi-square reference is qualified for n=5. A separate
synthetic whole-body plasma-only profile reoptimises uptake at seven colon-PS
values. All other physiology is fixed and the global reference is the best scanned
grid point. It is a conditional design demonstration, not a human tissue profile.
Bound hits and failure statuses are preserved.

Local log sensitivities use central differences (h=.01), with singular values,
weak directions, threshold and correlations reported. Rank 4/5 at relative threshold
1e-3 prevents reporting an inverse-Hessian correlation matrix as precise full-model
uncertainty. These are practical numerical design diagnostics, not a structural
proof of all nonlinear PBPK states. Twenty separately generated synthetic terminal
profiles test parameter recovery; they are explicitly marked synthetic.

## Bayesian scope and diagnostics

NumPyro NUTS runs four sequential CPU/x64 chains on the five aggregate mouse terminal
points. Priors are Normal(log(100 nmol/L),3) for log C168, Normal(log(.002 /h),2)
for log rate, and HalfNormal(.5) for log residual SD. They are broad investigator
regularisation, **not literature-derived human kinetic priors**. An alternative
rate width 1 and residual scale 1 tests two stated prior choices. Literature
PopPK estimates from the human calibration paper are not reused as independent
priors on the same observations.

Diagnostics require zero divergences, R-hat<1.01 and bulk/tail ESS>400. A higher
warmup/draw/acceptance configuration is attempted if those fail. Save full chains,
diagnostics, geometry, prior predictive summaries and in-sample posterior predictive
checks. Diagnostic thresholds do not prove validity of the independent-log-error
working likelihood. Animal-level covariance, assay recovery and terminal-window
selection uncertainty are unknown. The hierarchical noncentered API is available,
but population/study variability is not estimated from one aggregate curve.
No human whole-body posterior or clinical prediction interval is manufactured.

## Sensitivity and experiments

Five local dimensions cover uptake, colon PS, target abundance, recycling and
degradation. Morris (8 trajectories) and Sobol (N=128, compared with N=64) screen
three priority log-multiplier dimensions over hypothetical ranges: uptake .5–2,
colon PS .5–4, target .25–4. They are not measured uncertainty intervals. Report all
seven endpoints: plasma, colon and small-intestinal finite-window AUC, colon/serum
AUC ratio, terminal-time target occupancy, late-window apparent half-life, and
instantaneous eliminated flux/free-plasma concentration. The last is not NCA CL.
Sobol S1/ST, confidence widths and convergence differences remain untruncated;
full convergence or a biological causal ranking is not asserted. Cached forward
outputs require semantic source and Python/NumPy/SciPy identity checks.

Synthetic A–E candidates receive an identical one-gain observation calibration
budget. Both standard-generated and disease-generated data are evaluated, with
four independent synthetic study clusters held out. The paired bootstrap is only
for these synthetic clusters; one real held-out trial cannot give a between-study
interval. A/B have no regional colon operator, so their tissue cells are missing.
AICc counts fitted parameters, not the many unverified fixed assumptions. F is
excluded without donor data and a validated quantitative expression mapping.
All eight requested scientific experiments have explicit eligibility/gate rows;
synthetic successes never change their independent-tissue evidence count of zero.

## Observation model and transfer gates

Free interstitial concentration is I/Visf. An explicit TissueAssay operator maps
residual vascular plasma, accessible ISF, intracellular and target-complex drug to
recovered nmol per wet gram. Homogenate concentration additionally needs biopsy
wet mass and extraction volume. Recovery fractions and representative organ mass
must be supplied. Protein-normalised or unspecified radiolabel measurements require
further definitions and are not automatically equated to intact/free drug.
No usable independent ATLAS/Yoshihara raw tissue data were retrieved. Their
abstract enrolment sizes are not independent evaluable biopsy counts.

Infliximab IV dosing, molecular/target/FcRn kinetics, ADA and populations require
separate evidence before sharing calibrated physiology. No such independent
validation is executed. TAURUS's article and Zenodo deposit are identified, but
Zenodo metadata is denied by the proxy; file sizes/processed matrices are not
verified. No raw reads, donor-level analysis or RNA-to-protein conversion is done.

## Reproduce

```bash
source scripts/environment.sh
python scripts/run_chunk3.py
pytest -q
```

The pipeline writes per-step logs and a run manifest with exit statuses, source
hashes and script hashes. A failed analysis stops the pipeline. Success means the
feasible analyses executed; evidence gates still prohibit unsupported conclusions.
Nothing updates or publishes the cloud environment configuration.
