# Validation and evidence classification

The code has mathematical/numerical verification: analytical baseline checks,
conservation, nonnegativity tolerances, flow directions, receptor/target limits,
repeated dosing, cross-solver and tolerance agreement. This is not biological
validation of the whole-body parameterisation.

A limited **external aggregate comparison** uses three correlated endpoints from
one held-out healthy Humira trial. AUC_inf, Cmax and AUC_0_336 are underpredicted by
20.1%, 15.5% and 12.4%. No individual concentration-time profiles, study heterogeneity
or prediction-interval coverage were validated. Published arm GLSM confidence
intervals are not patient prediction intervals.

Usable independent human tissue observations: **0**. ATLAS and Yoshihara identities
and abstracts are verified, but dosing/sample histories and assay-interpretable
raw observations were not acquired. Enrolled patient counts are not evaluable
biopsy counts. Tissue and tissue:serum result tables are intentionally empty.

Infliximab external validation is unexecuted. Figure 14 is an evidence-gap panel,
not a validation curve. TAURUS is contextual; no processed matrix or quantitative
transcript-to-protein mapping has been analysed. Synthetic comparisons and mouse
benchmarks retain explicit nonclinical labels.

See research/scientific_findings.md and research/validation_summary.md for the
critical verdict, and research/independent_review.md for rejection risks. No claim
of novelty, disease-model superiority, clinical accuracy or publication readiness
follows from the current evidence.
