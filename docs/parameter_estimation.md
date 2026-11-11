# Parameter estimation

See inference_and_validation.md for full objectives, bounds, priors and diagnostics.
Run `make analysis` to regenerate supported fits and `configs/chunk3_analysis.json`
for recorded choices and seeds.

Human calibration estimates only CL/F and V/F from two aggregate reference-Humira
NCA endpoints, conditional on ka=.0219 h^-1. Their apparent scale reflects the
SC F/CL/V invariance. Two fitted parameters leave no residual degrees of freedom;
no empirical human parameter covariance, population variability or clinical
prediction band is inferred. Hypothetical physiology and target rates are not
freely tuned to make the tissue model appear superior.

Mouse terminal fitting uses a five-point window of one aggregate 7E3 profile with
a working lognormal likelihood and estimated residual log error. Profiles
reoptimise nuisance parameters, and a four-chain reduced NumPyro posterior is
reported only after diagnostic thresholds pass under both stated priors. This
posterior is conditional on a small aggregate dataset and selection assumptions.
It is not a human mechanistic posterior. Additional cohort/animal-level data,
assay definitions and identifiability work are prerequisites for richer inference.

Diagnostic reports distinguish local numerical rank, analytic structural scaling
invariance, synthetic recovery and empirical fit. Sensitivity rankings cannot be
used as identifiability proofs. AICc counts fitted parameters and does not establish
that the many fixed biological assumptions are valid.
