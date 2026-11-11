# InflammaPBPK: an exploratory anti-TNF PBPK research platform with explicit evidence gates

## Abstract

**Background.** Intestinal inflammation may alter antibody tissue exposure, but a
mechanistic implementation alone cannot establish improved prediction. **Methods.**
We implemented linear, minimal and ten-organ antibody PK/PBPK models with two-pore
transport, lymph return, endosomal/FcRn salvage, separate soluble/membrane effective
target disposition and SC input. Numerical verification preceded reduced-model
estimation. Audited public data comprised 174 aggregate mouse 7E3 records and five
human study-arm NCA summary facts from two trials. **Results.** Two apparent human
PK parameters matched two calibration summaries conditional on fixed absorption.
One held-out healthy Humira trial was underpredicted by 20.1% for AUC_inf, 15.5%
for Cmax and 12.4% for AUC_0_336. A five-point mouse terminal working posterior had
half-life median about 434 h (95% credible interval approximately 387–509 h), with
four chains meeting diagnostic thresholds. Whole-body design sensitivities had
practical rank 4/5 at the stated numerical threshold. Synthetic tissue comparisons
favoured the generating transport assumption; plasma differences did not uniformly
favour added disease transport. **Conclusion.** The software provides a reproducible
exploratory platform, not a validated human tissue predictor. Zero usable independent
human tissue observations were available. Disease-informed superiority, infliximab
transfer and novelty remain unproven.

## Introduction

Monoclonal-antibody tissue exposure depends on vascular exchange, interstitial
transport, lymphatic return, endosomal processing and binding. For anti-TNF
therapies in inflammatory bowel disease, plasma exposure alone may not determine
local pharmacology. Tissue sampling, however, often measures a mixture of vascular,
extracellular, cellular and bound material. A model of free interstitial drug must
not be compared directly with an unspecified biopsy signal.

This project asks whether independently parameterised intestinal disease physiology
can improve prediction of anti-TNF tissue concentrations over a matched reference
model. It does not assume that additional compartments or mechanisms improve
out-of-sample performance.

## Literature background

Cao, Balthasar and Jusko's second-generation minimal PBPK model [1] provides a
plasma/tight-tissue/leaky-tissue/lymph structure. OSP's 7E3 and MEDI-524 reports
explicitly describe established whole-body two-pore, lymph, endosomal and FcRn
mechanisms, citing the generic protein platform of Niederalt et al. [2,3]. Those
mechanisms cannot be claimed as novel here.

ATLAS [4] and Yoshihara et al. [5] report human anti-TNF intestinal tissue studies;
identities and abstracts were verified, but individual model-ready observations
were not acquired. The TAURUS article [6] establishes a longitudinal single-cell
resource and links raw/processed data to Zenodo. A matrix was not obtained or
quantitatively integrated. A complete systematic prior-art review remains pending.

## Research gap

The candidate gap is a rigorously controlled, independent transfer test of externally
measured IBD transport physiology. Combining established mechanisms is insufficient
as novelty. The current acquired data cannot establish that this gap is unfilled
or that the proposed model closes it.

## Hypotheses

The primary candidate hypothesis is lower held-out tissue log-concentration error
under independently sourced disease physiology than under standard physiology.
Secondary hypotheses concern regionalisation, transport versus local target
binding, uncertainty calibration and cross-biologic transfer. All require assay
compatibility, independent study-level evaluation and prespecified exclusions.
Current choices are retrospective exploratory analysis choices, not a prospective
registration. No human tissue effect size is estimated.

## Methods

The Python 3.12 CPU implementation uses canonical nmol/L/h units, event-aware
SciPy BDF integration, Radau comparisons, analytical baseline references and
conserved elimination accounting. Code, source/parameter hashes, random seeds,
locked dependencies, numerical tests, command-line workflow and a Streamlit
interface support reproducibility. The interface exposes scientific evidence
classifications and exact configurations rather than only plots.

## PBPK model development

Baseline one-/two-compartment and SC models use mass-transfer matrices with
matrix-exponential reference solutions. The minimal model implements amount-form
Model A equations of [1]. The whole-body model distinguishes lung, liver, kidney,
spleen, muscle, skin, adipose, small intestine, colon and remaining tissue.
Pulmonary circulation is serial; spleen and intestinal venous flows enter liver.
Lymph returns once. Endosomal unbound and FcRn-bound drug, target complexes and
an elimination accumulator maintain drug mass. Cumulative recycled flux is a
repeat-passage diagnostic and is excluded from inventory.

A constant-flow convection/diffusion pore solution is implemented with stable
small-Peclet limits. This is not a full Starling pressure/hindrance implementation
or a demonstrated numerical reproduction of every OSP platform equation. FcRn
uses acidic reversible binding, a constant endogenous-IgG competition reservoir
and instantaneous neutral release. TMDD uses effective 1:1 binding sites, not
molecular bivalent-IgG/trimeric-TNF stoichiometry. Soluble complex loss and membrane
internalisation are distinct. Optional ADA-associated clearance is experimental.
Full equations and units are in docs/mathematical_model.md and mechanism documents.

## Data sources

The immutable OSP 7E3 source snapshot contains 24 aggregate profiles and 174 records,
including 13 gut values. Its source report describes mouse IV dosing and
radiolabel-associated tissue measurements. Ninety-six zero reported SD values are
retained as flags, not infinite weights. One eight-point wild-type plasma profile
is used for a complexity comparison; its five points at or after 168 h form the
terminal analysis. These windows overlap and are not separate validation cohorts.

Li et al. [7], trial NCT03917628, provide two observed healthy-reference-Humira
single-dose GLSMs: AUC_inf=2,023,643 ng h/mL and Cmax=3,220 ng/mL after 40 mg SC.
Hillson et al. [8], trial NCT02675023, provide held-out US-Humira GLSMs:
AUC_inf=2,534,000 ng h/mL (n=91), Cmax=3,809 ng/mL (n=105) and
AUC_0_336=1,023,000 ng h/mL (n=101). Their overlapping denominators are not
independent datasets. Trial/cohort identifiers are disjoint; individual identifiers
were unavailable for direct participant-overlap checking. Arm-level weight and
albumin summaries are descriptive, not imputed patient records.

## Physiological parameterisation

Minimal-model structural partitions and selected assignments derive from [1],
with accessibility and lymph-volume departures documented. Whole-body organ
geometry, flows/PS, endosomal volumes and disease modifiers are explicitly
illustrative. They are not a validated human physiology database. Body-weight
scaling in the interface assumes volumes/sites proportional to weight and flows/PS
to weight^0.75; no empirical IBD covariate relationship is estimated. Clinical
severity, albumin and RNA counts are not silently mapped to permeability or rates.

## Drug-specific parameterisation

The EMA Humira product information [9] supplies SC/regimen and aggregate PK
references. A generic 150 kDa IgG value is used only as an explicit exploratory
dose-conversion assumption. No drug-specific whole-body FcRn/TNF parameter set is
validated. Infliximab is restricted to an acknowledged generic IV scaffold in the
interface; SC transfer, infusion and external validation are unsupported.

## Calibration

The human reduced model fits CL/F and V/F with ka=.0219 h^-1 fixed from [7].
SC scaling invariance prevents separate identification of absolute F, CL and V.
The fit yields CL/F=0.019766 L/h and V/F=9.744 L. With two fitted parameters and
two correlated aggregate endpoints, residual degrees of freedom are zero. Exact
matching is not goodness-of-fit evidence, and no empirical human parameter CI is
reported. Source-population ka is not reused as an independent prior on the same data.

The mouse terminal model uses bounded lognormal maximum likelihood, weighted
fitting, nuisance-reoptimised profiles and a reduced NumPyro posterior. Priors
are broad investigator regularisation, not asserted literature human kinetics.
Four sequential chains and an alternative prior choice are checked for R-hat,
ESS and divergences. Animal-level covariance and radiolabel assay recovery are
unknown; inference is explicitly conditional on a working aggregate likelihood.

## Validation

Log error, geometric bias, absolute fold error and matched endpoint ratios are
used without turning study-arm GLSMs into individual profiles. Published GLSM
confidence intervals are not individual prediction intervals. One held-out trial
cannot estimate a between-study improvement distribution.

Usable independent human tissue observations are zero. ATLAS/Yoshihara enrolment
counts of 30 and 25 do not create numeric validation records. Homogenate operators
require residual plasma, accessible ISF per wet mass, representative organ mass,
recovery and extraction metadata; no conversion is invented for those studies.
Tissue/serum validation tables remain empty. Infliximab validation is unexecuted.

## Sensitivity analysis

Five local log dimensions, eight Morris trajectories and Sobol first/total effects
(N=128 versus N=64) screen hypothetical ranges for uptake, colon PS and target
abundance. Six hundred sixty-nine distinct global/Morris points were evaluated.
The largest total-index change was about .036; confidence bands remain substantial.
Rankings depend on the chosen assumptions. The full-body sensitivity design has
practical rank 4/5 at relative threshold 1e-3, not a full structural identifiability
proof. A synthetic plasma-only profile leaves colon PS weakly constrained and
uptake at a bound. Twenty labelled synthetic datasets test parameter recovery.

## Results

The reduced human model underpredicts the held-out healthy study's AUC_inf by
20.1%, Cmax by 15.5% and AUC_0_336 by 12.4%. These are limited aggregate plasma
comparisons, not effects of disease-informed physiology. Predicted Tmax/half-life
are not validated without corresponding independent observations.

The mouse terminal posterior median half-life is approximately 434 h, with a
working 95% credible interval approximately 387–509 h. Both prior choices met
R-hat<1.01, bulk/tail ESS>400 and zero-divergence criteria; the median rate changed
by about -.056% between those choices. In-sample posterior predictive checks do
not establish external predictive calibration.

AICc for the eight-point mouse full-window fit was approximately 102.71 for one
exponential and 98.68 for two exponentials, including residual sigma in parameter
counts. This is an in-sample nonhuman complexity illustration.

Synthetic A–E candidates use identical one-gain calibration budgets and both
standard- and disease-generated truth. Free-colon errors favour the generating
transport structure. Plasma errors do not uniformly favour D. A/B have no regional
tissue operator; missing tissue cells are preserved. F is excluded. Thus the
synthetic experiment demonstrates conditional implementation behaviour, not
clinical superiority. Numerical tests and exported artifacts provide software
verification; current QA counts are reported separately in PROJECT_STATUS.md.

## Discussion

The platform makes assumptions, assay definitions, missingness and unsupported
claims reviewable. Its principal current contribution is a tested implementation
and reproducibility/evidence workflow. It does not establish new transport or
salvage biology. A positive synthetic comparison is expected when the generating
structure is included; it cannot substitute for independent tissue observations.

The healthy-trial underprediction cautions against assuming transfer even for a
reduced model. Differences in weight, immunogenicity, statistical adjustment and
study population may matter, but two aggregate datasets cannot identify their
causal contributions. More detailed PBPK could add uncertainty rather than improve
prediction when physiological parameters are weakly supported.

## Limitations

There is no complete human whole-body calibration, independent tissue validation,
validated infliximab transfer, fitted population model or quantitative transcriptomic
extension. Parameter bounds are research guardrails rather than measured uncertainty
intervals. The selected terminal window and small aggregate dataset constrain
uncertainty interpretation. The full prior-art review remains incomplete. Effective
TMDD, equilibrium IgG competition and instantaneous release are reductions requiring
validation. Software/numerical correctness cannot establish physiological validity.
Article/source reuse terms and a project software licence require author review
before a public release; no licence is silently imposed on the user's code.

## Future work

Highest value is an independent anti-TNF biopsy/serum cohort with exact dose/sample
histories, bowel segment, activity, tissue mass/extraction, residual blood correction,
analyte definition, assay recovery and covariates. Independently measured disease
vascular/lymph physiology and molecule-specific FcRn/TNF kinetics should constrain
priors before tissue fitting. Multiple disjoint cohorts are needed for transport
and uncertainty calibration. Donor-aware TAURUS analysis can provide context after
processed access, but quantitative protein scaling needs separate calibration.
The prior-art audit and reference-model reproduction should precede novelty claims.

## Conclusion

InflammaPBPK is an executable, tested exploratory research platform. The hypothesis
that disease-informed intestinal PBPK improves independent tissue prediction remains
inconclusive. It is not ready for publication as a validated IBD exposure or clinical
dosing study. A software/methods manuscript would also require completed novelty
positioning, reference reproduction, release/licensing decisions and broader review.

## References

1. Cao Y, Balthasar JP, Jusko WJ. Second-generation minimal physiologically-based
   pharmacokinetic model for monoclonal antibodies. 2013.
   DOI: 10.1007/s10928-013-9332-2. PMC3836053. Primary equations inspected.
2. Open Systems Pharmacology. 7E3 and MEDI-524 evaluation reports, 1.0-OSP12.3.
   Immutable library commit 07a71b3e025879db5cc46feca1d262cc786ed0f6.
3. Niederalt C et al. A generic whole body physiologically based pharmacokinetic
   model for therapeutic proteins in PK-Sim. 2018.
   DOI: 10.1007/s10928-017-9559-4. Cited via retrieved OSP reports; independent
   primary-publication verification remains a limitation.
4. Yarur AJ et al. The association of tissue anti-TNF drug levels with serological
   and endoscopic disease activity in inflammatory bowel disease: the ATLAS study.
   DOI: 10.1136/gutjnl-2014-308099. PMID25670812. Metadata/abstract inspected.
5. Yoshihara T et al. Tissue Drug Concentrations of Anti-tumor Necrosis Factor
   Agents Are Associated with the Long-term Outcome of Patients with Crohn's Disease.
   DOI: 10.1097/MIB.0000000000001260. PMID28945638. Metadata/abstract inspected.
6. Thomas T et al. A longitudinal single-cell atlas of anti-tumour necrosis factor
   treatment in inflammatory bowel disease. 2024. DOI: 10.1038/s41590-024-01994-8.
   PMC11519010. Article inspected; expression matrix not acquired.
7. Li D et al. Population pharmacokinetic modeling of adalimumab biosimilar SCT630
   and Humira in healthy participants and patients with moderate to severe plaque
   psoriasis to establish PK similarity. 2026. DOI: 10.1016/j.curtheres.2026.100848.
   PMC13675741, Tables 1, 3 and 4. Primary aggregate data inspected.
8. Hillson J et al. Pharmacokinetic equivalence, comparable safety, and immunogenicity
   of an adalimumab biosimilar product (M923) to Humira in healthy subjects. 2018.
   DOI: 10.1002/prp2.380. PMC5817835, Tables 1 and 2. Primary summaries inspected.
9. EMA. Humira EPAR product information, sections 4.2 and 5.2. Retrieved
   10 November 2026; source hash and URL in data/metadata/chunk2_sources.json.
