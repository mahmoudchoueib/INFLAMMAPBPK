# Regional intestinal hypotheses

Small intestine and colon have separate vascular, interstitial, endosomal and
optional soluble/membrane target states. Small intestine is an aggregate; no
ileum-specific compartment is claimed without separate physiological evidence.
The region modifier accepts explicit permeability/PS, arterial-flow and lymph
multipliers, validating the resulting organ. Other organ parameters are retained;
cardiac/portal flows are recomputed from the modified network.

Example colon multipliers PS=3, flow=1.2, lymph=0.8 and added target amounts are
**uncalibrated hypotheses**, recorded in the parameter registry and example
summary. They are not inferred from disease severity, CRP or albumin. No clinical
score-to-permeability formula exists. Likewise no quantitative albumin or RNA
expression relationship is implemented without supporting evidence. The API can
represent an inflamed region by supplied parameters, or keep both regions at the
reference fixture; it does not simulate disease progression or within-region
inflamed/noninflamed tissue mixtures.

Outputs are free vascular and free interstitial drug concentrations, with bound
complex/endosomal amounts available separately. They are not automatically biopsy
homogenate concentrations. A future observation operator needs residual vascular
blood, interstitial accessibility, intracellular/complex fractions, tissue mass,
assay recovery and sample timing. Human tissue calibration and external validation
remain absent. Therefore changes in simulated exposure test implementation
sensitivity only, not the primary IBD research hypothesis.

Flow multipliers change total systemic flow; they do not redistribute a fixed
cardiac output from other organs. This is an explicit modelling choice requiring
physiological constraints before calibration.
