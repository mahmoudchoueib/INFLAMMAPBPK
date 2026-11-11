# Scientific findings — Chunk 3

**The central hypothesis remains inconclusive. Disease-informed PBPK superiority
has not been demonstrated.** There are zero usable independent human tissue
observations in the acquired modelling dataset. No patient-level tissue values,
doses, inflammation grades or ratios were fabricated from study abstracts.

## Answers to the eight scientific questions

1. **Does disease physiology improve independent tissue predictions?** Unknown;
   not evaluable with the acquired data. ATLAS (PMID 25670812) and Yoshihara
   (PMID 28945638) are verified tissue-study identities/abstracts, but individual
   assay-normalised observations and full treatment histories were not retrieved.
   Reported study enrolment (30 and 25) is not the count of usable independent
   validation observations; that count is **0**.
2. **Magnitude of improvement?** Not estimable. No human tissue effect estimate,
   interval or favourable endpoint is selected. A limited conventional plasma
   model underpredicts held-out healthy-trial AUC_inf by 20.1%,
   Cmax by 15.5%, and AUC_0_336 by 12.4%.
   These are summary-endpoint discrepancies, not disease-versus-standard effects.
3. **Does improvement persist on unseen studies?** Tissue transfer is unknown.
   Only one disjoint registered human trial supplies held-out aggregate plasma
   endpoints. These correlated summaries cannot estimate between-study heterogeneity
   or patient-level prediction intervals. Calibration and validation have different
   arm-level weight descriptors (65 kg median versus 78.5 kg mean) and immunogenicity
   contexts; no causal adjustment is inferred from two studies.
4. **Which mechanisms contribute?** Within hypothetical ranges, transport and
   target assumptions alter colon exposure, while uptake/recycling/degradation
   also affect outputs. These are model sensitivities, not experimental causal
   contributions. On the synthetic free-colon endpoint, standard-generated data
   favour standard transport and disease-generated data favour disease transport.
   Plasma differences between C and D are small and do not uniformly favour D.
   These conditional results cannot demonstrate clinical improvement.
5. **Which mechanisms are poorly identifiable?** SC plasma cannot separately
   identify absolute F, CL and V: simultaneous scaling leaves the curve unchanged.
   Fixing ka permits apparent CL/F and V/F to match two aggregate endpoints, but
   leaves zero residual degrees of freedom. In the illustrative whole-body design,
   five log sensitivities have practical rank 4 at relative threshold 1e-3 for
   serum only and also for serum plus free-colon outputs. This threshold-based
   numerical result is not a structural proof. A synthetic plasma profile leaves
   colon PS weakly constrained and uptake at the specified bound; no precise
   human mechanism estimates are reported.
6. **Sufficient data to demonstrate novelty?** No. Whole-body transport, lymph and
   FcRn are established mechanisms. The current observations do not test independent
   IBD physiology transfer. The full prior-art audit remains incomplete.
7. **Generalisation to infliximab?** Not demonstrated. No independent infliximab
   validation dataset was model-ready, and drug-specific binding, FcRn, ADA and
   IV dosing/covariate records were not established. A shared physiological layout
   or a generic IV simulation is not cross-biologic tissue validation.
8. **Missing evidence?** Independent study/subject-identified adalimumab and
   infliximab serum/tissue time histories; dose/regimen and timing; inflammation
   severity and bowel segment; biopsy recovery/dilution/normalisation and analyte;
   molecule-specific kinetics; externally measured disease physiology; and
   donor-aware expression/protein calibration before quantitative integration.

## Actual reduced-model results

The healthy-Humira aggregate fit gives **CL/F = 0.01977 L/h** and
**V/F = 9.744 L**, conditional on ka=0.0219 h^-1 from the same
source PopPK article. They are apparent parameters, not absolute CL/V. Two fitted
parameters and two correlated aggregate calibration endpoints cannot establish an
uncertainty distribution. No human parameter CIs or population prediction bands
are reported. Published validation CIs describe arm GLSMs, not patient prediction.

A separate mouse 7E3 terminal-window likelihood uses **five aggregate time points**
from one selected profile (>=168 h), avoiding duplicate figure/cohort pooling.
The reduced Bayesian terminal half-life median is
**434.1 h**, with a working 95% credible
interval **386.6–509.3 h**.
Four sequential chains had 0 divergences, max R-hat
1.00, minimum bulk ESS 1308 and minimum tail ESS
1255. Both stated priors met thresholds; median rate changed by
-0.056% between them.
This is a proper reduced-model posterior under a working independent-log-error
likelihood, **not a human PBPK posterior** or a population variability estimate.
Unknown animal-level correlation and radiolabel/assay limitations remain. In-sample
PPC coverage is not external predictive calibration. Priors are explicitly broad
investigator regularisation, not fabricated literature-informed human kinetics.

## Sensitivity and complexity

Local sensitivities, 8 Morris trajectories and first/total-order Sobol estimates
(N=128 versus N=64) were executed on a hypothetical three-parameter subspace,
using 669 distinct global/Morris forward points.
Largest N64-to-N128 total-index change was
0.036; uncertainty bands remain substantial,
so full convergence is not asserted. Other physiology is fixed; rankings are
range- and model-dependent. Terminal half-life and instantaneous elimination/serum
ratio in this analysis are dynamic descriptors, not clinical NCA clearance.

AICc penalises **estimated** parameters. The real mouse 8-point one-/two-exponential
benchmark uses identical fit windows and includes residual sigma in k. It is an
in-sample complexity example, not IBD validation. Synthetic A–E candidates have
identical one-gain calibration budgets; fixed unverified mechanisms do not become
validated merely because AICc does not count them as estimated parameters. A/B
have no colon-specific operator and receive no fabricated tissue predictions.
F is excluded from quantitative comparisons.

## Transcriptomic context

TAURUS was verified as *A longitudinal single-cell atlas of anti-tumour necrosis
factor treatment in inflammatory bowel disease* (DOI 10.1038/s41590-024-01994-8;
PMC11519010). Its data statement links raw and processed data to Zenodo
10.5281/zenodo.13768607. Zenodo metadata retrieval was denied by the current proxy;
file sizes and donor matrix schema were not verified, and no large raw download
was attempted. No expression analysis, differential-expression claim or numeric
RNA-to-protein conversion is reported. TNF, TNFRSF1A/B, FCGRT, B2M, endothelial
markers and pathways remain candidate donor-aware contextual analyses after
processed data access and annotation review.
