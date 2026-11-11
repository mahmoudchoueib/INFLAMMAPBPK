# Reviewer-style critical assessment

This review adopts a sceptical peer-review perspective. It was prepared by the
same implementation assistant, not an external independent reviewer or a clinical
regulatory assessment. Independent domain review is still needed.

**Recommendation: not publication-ready as a disease-informed tissue prediction
or clinical decision study.** The software is a useful exploratory prototype;
its scientific claim remains unsupported by adequate independent data.

| Domain | Evidence and assessment | Rejection risk / required remedy |
|---|---|---|
| Mathematical correctness | Conservative ODEs, analytical baselines, receptor/target limits, event and cross-solver tests. Zero-clearance half-life reporting bug identified and fixed in final QA. | Tests establish selected numerical properties, not exhaustive correctness; independent equation/code audit needed. |
| Physiological plausibility | Consistent plasma/portal/lymph bookkeeping; many geometry/flow/PS/endosomal rates are assumed. Weight scaling is hypothetical. | A dashboard can make arbitrary assumptions look authoritative. Supply externally constrained human physiology and uncertainty. |
| Data quality | Public facts and source hashes retained; mouse radioactivity and biopsy analytes are not assumed free drug. | Individual dose/sample histories and assay recovery are absent; cannot validate tissue exposure. |
| Provenance | Evidence levels and numerical control metadata are explicit. | Source rights and project licensing still need release decisions; complete primary-reference verification. |
| Identifiability | Analytic SC scaling ambiguity; practical rank 4/5 and weak profiles reported. | Precise human mechanistic rates would be unjustified. Reduce/externally constrain parameter blocks. |
| Calibration validity | Apparent PK fits two summaries; five mouse terminal points support a working reduced likelihood. | Zero human residual df; no individual/population likelihood or covariance. Exact fit is not validation. |
| Leakage | Trials/cohorts kept separate; duplicate mouse figures not called holdouts. | Individual identifiers unavailable; only one held-out human study. Do not bootstrap endpoints as studies. |
| Independent validation | One healthy-trial aggregate comparison retains unfavourable errors. | No independent human tissue validation; no clinical IBD extrapolation claim is supportable. |
| Tissue observation model | Explicit vascular/ISF/cellular/complex recovery operators with required metadata. | Operators cannot repair unavailable assay definitions; do not compare homogenate to ISF by default. |
| Complexity | Synthetic null and disease truth both retained; AICc counts fitted parameters. | Fixed unverified assumptions are not penalised away by AICc. Demonstrate external benefit under comparable budgets. |
| Bayesian inference | Chains, priors, exact diagnostics and PPC stored. | Diagnostics do not validate an aggregate independence likelihood or a selected window. No human PBPK posterior. |
| Reproducibility | Locked setup, public benchmark facts, pinned OSP source, CLI/Make and report manifests. | Clean-source QA is necessary; remote main is not updated merely by uncommitted files. Raw mutable HTML is optional. |
| Novelty | Established mechanisms acknowledged; candidate independent transfer test framed explicitly. | Full prior-art differentiation incomplete; do not claim that a new combination is a new scientific result. |
| Clinical interpretation | Unsupported predictions and missing evidence explicitly visible. | No dosing, efficacy, benefit or clinical safety claims; generic infliximab scaffold is not drug transfer validation. |

Major scientific revisions are independent tissue/serum data, defensible physiological
parameterisation, molecule-specific kinetics, a prespecified assay/validation design,
multiple unseen cohorts and identifiability-aware calibration. Completing the
systematic literature audit and reproducing a published reference platform would
make the technical contribution assessable.

The most valuable experiments measure paired drug and TNF in tissue/serum with
exact dosing, time, segment and inflammation; quantify residual vascular drug and
homogenisation recovery; and independently constrain permeability, interstitial
volume, lymph drainage and functional FcRn. Cross-biologic testing needs independent
infliximab IV records and molecule-specific binding/ADA information. Transcriptomics
can contextualise heterogeneity but requires protein/functional calibration for
quantitative priors. More attractive plots cannot substitute for these experiments.

Final software QA passed in the main checkout and a clean source export (100 tests
each), with real-browser rendering and 45 scientific export files. This strengthens
reproducibility, not the biological claim. The default exploratory whole-body curve
can itself have slow elimination/delayed peaks; defaults must not be interpreted
as established adalimumab pharmacokinetics. Publication-quality typography does
not make unvalidated physiology publication-ready science.
