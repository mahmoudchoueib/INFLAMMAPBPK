"""Render scientific verdict from executed results, with explicit evidence gates."""

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]


def report():
    cal = json.loads((ROOT / "results/calibration/human_apparent_pk.json").read_text())
    bayes = json.loads((ROOT / "results/bayesian/summary.json").read_text())
    sensitivity = json.loads((ROOT / "results/sensitivity/design.json").read_text())
    validation = pd.read_csv(ROOT / "results/validation/human_summary_validation.csv")
    if not all(
        bayes[key]["diagnostics_thresholds_met"] for key in ["primary", "alternative_prior"]
    ):
        raise RuntimeError("Cannot issue posterior convergence claims when diagnostics failed")
    bp = bayes["primary"]
    half = bp["terminal_half_life_h_median_CI95"]
    source = json.loads((ROOT / "data/metadata/chunk3_sources.json").read_text())
    # Tables distinguish human aggregate comparisons from mouse or synthetic analyses.
    tissue_cols = [
        "study_id",
        "patient_id",
        "region",
        "measured_quantity",
        "observed",
        "predicted",
        "unit",
        "assay_definition",
    ]
    pd.DataFrame(columns=tissue_cols).to_csv(
        ROOT / "results/validation/independent_tissue_validation.csv", index=False
    )
    pd.DataFrame(
        columns=["study_id", "time_h", "tissue_to_serum_observed", "tissue_to_serum_predicted"]
    ).to_csv(ROOT / "results/validation/independent_tissue_to_serum.csv", index=False)
    cross = {
        "biologic": "infliximab",
        "independent_plasma_validation_studies": 0,
        "independent_tissue_observations": 0,
        "status": "not validated",
        "required": [
            "matched dosing/sample histories",
            "drug-specific binding/FcRn parameters or uncertainty",
            "immunogenicity and population covariates",
            "IV dose and body-weight records",
            "assay-consistent independent observations",
        ],
        "source_attempt": (
            "EMA Remicade product-information request returned HTTP 429; no retry loop"
        ),
        "shared_physiology": "can be retained only after external physiological parameterisation",
        "prohibition": (
            "No transfer of adalimumab SC absorption parameters or "
            "generic IgG rates as validated infliximab kinetics"
        ),
    }
    (ROOT / "results/validation/cross_biologic_status.json").write_text(
        json.dumps(cross, indent=2) + "\n"
    )
    eligibility = []
    for name, reason in [
        ("A", "two apparent parameters fitted to two aggregate calibration endpoints; ka fixed"),
        ("B", "insufficient data for a unique physiological calibration"),
        ("C", "illustrative geometry/kinetics lack independent parameterisation"),
        ("D", "no model-ready independent tissue data or measured disease transport law"),
        ("E", "target binding/turnover not identifiable from available summaries"),
        ("F", "no donor matrix acquired or validated transcript-to-protein mapping"),
    ]:
        eligibility.append(
            dict(
                model=name,
                clinical_calibration_status="limited aggregate calibration"
                if name == "A"
                else "not established",
                independent_human_plasma_summary_studies=1 if name == "A" else 0,
                independent_tissue_observations=0,
                reason=reason,
            )
        )
    pd.DataFrame(eligibility).to_csv(ROOT / "results/validation/model_eligibility.csv", index=False)
    # Predefined ratio metrics: units cancel within each endpoint, not across patient records.
    validation["relative_error_percent"] = 100 * (validation.predicted_over_observed - 1)
    validation["prediction_interval_lower"] = None
    validation["prediction_interval_upper"] = None
    validation["prediction_interval_reason"] = (
        "No population/heterogeneity estimate from two calibration summaries"
    )
    validation.to_csv(ROOT / "results/validation/human_summary_validation.csv", index=False)
    errors = {r.endpoint: float(r.relative_error_percent) for r in validation.itertuples()}
    clinical = {
        "scope": "healthy-arm aggregate summaries; one held-out trial",
        "fitted_CL_over_F_L_h": cal["CL_over_F_L_h"],
        "fitted_V_over_F_L": cal["V_over_F_L"],
        "endpoint_relative_errors_percent": errors,
        "independent_trial_count": 1,
        "raw_concentration_time_records": 0,
        "independent_tissue_observations": 0,
        "clinical_predictive_intervals": None,
        "derived_holdout_CL_over_F_L_h": 40000
        / float(validation[validation.endpoint == "AUC_inf"].value.iloc[0]),
        "derived_CL_note": (
            "Dose/AUC_inf repeats the AUC endpoint; not an extra independent observation"
        ),
    }
    (ROOT / "results/validation/summary.json").write_text(json.dumps(clinical, indent=2) + "\n")
    # An observed-versus-predicted plot of real published summaries, not invented time points.
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.5))
    for axis, row in zip(ax, validation.itertuples()):
        scale = 1e6 if "AUC" in row.endpoint else 1000
        axis.errorbar(
            [0],
            [row.value / scale],
            yerr=[
                [(row.value - row.reported_lower95) / scale],
                [(row.reported_upper95 - row.value) / scale],
            ],
            fmt="o",
            label="published GLSM, 95% CI",
        )
        axis.scatter([1], [row.predicted / scale], marker="x", label="model point prediction")
        axis.set_xticks([0, 1], ["observed", "predicted"])
        axis.set(
            title=row.endpoint,
            ylabel=("million " + row.unit if "AUC" in row.endpoint else "thousand " + row.unit),
        )
        axis.legend(fontsize=6)
    fig.suptitle("One independent healthy trial; observed-mean CI is not a prediction interval")
    fig.tight_layout()
    fig.savefig(ROOT / "results/validation/observed_vs_predicted.png", dpi=150)
    plt.close(fig)
    verdict = f"""# Scientific findings — Chunk 3

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
   model underpredicts held-out healthy-trial AUC_inf by {abs(errors["AUC_inf"]):.1f}%,
   Cmax by {abs(errors["Cmax"]):.1f}%, and AUC_0_336 by {abs(errors["AUC_0_336"]):.1f}%.
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

The healthy-Humira aggregate fit gives **CL/F = {cal["CL_over_F_L_h"]:.5f} L/h** and
**V/F = {cal["V_over_F_L"]:.3f} L**, conditional on ka=0.0219 h^-1 from the same
source PopPK article. They are apparent parameters, not absolute CL/V. Two fitted
parameters and two correlated aggregate calibration endpoints cannot establish an
uncertainty distribution. No human parameter CIs or population prediction bands
are reported. Published validation CIs describe arm GLSMs, not patient prediction.

A separate mouse 7E3 terminal-window likelihood uses **five aggregate time points**
from one selected profile (>=168 h), avoiding duplicate figure/cohort pooling.
The reduced Bayesian terminal half-life median is
**{half[0]:.1f} h**, with a working 95% credible
interval **{half[1]:.1f}–{half[2]:.1f} h**.
Four sequential chains had {bp["divergences"]} divergences, max R-hat
{bp["max_rhat"]:.2f}, minimum bulk ESS {bp["min_bulk_ess"]:.0f} and minimum tail ESS
{bp["min_tail_ess"]:.0f}. Both stated priors met thresholds; median rate changed by
{100 * bayes["prior_sensitivity"]["relative_median_rate_change"]:.3f}% between them.
This is a proper reduced-model posterior under a working independent-log-error
likelihood, **not a human PBPK posterior** or a population variability estimate.
Unknown animal-level correlation and radiolabel/assay limitations remain. In-sample
PPC coverage is not external predictive calibration. Priors are explicitly broad
investigator regularisation, not fabricated literature-informed human kinetics.

## Sensitivity and complexity

Local sensitivities, 8 Morris trajectories and first/total-order Sobol estimates
(N=128 versus N=64) were executed on a hypothetical three-parameter subspace,
using {sensitivity["forward_evaluations"]} distinct global/Morris forward points.
Largest N64-to-N128 total-index change was
{sensitivity["max_N64_N128_ST_change"]:.3f}; uncertainty bands remain substantial,
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
"""
    (ROOT / "research/scientific_findings.md").write_text(verdict)
    summary = """# Validation summary

| Evidence class | Executed result | Interpretation |
|---|---|---|
| Human calibration | 2 GLSMs; NCT03917628 | Apparent PK; ka fixed; zero residual df |
| Human plasma holdout | 3 summaries; NCT02675023 | One healthy trial; no raw profile |
| Human tissue holdout | 0 usable observations | Unvalidated; no biopsy/free-ISF substitution |
| Infliximab | 0 independent validation studies | No cross-biologic claim |
| Mouse 7E3 | Terminal n=5; complexity n=8 | Aggregate; no independent holdout |
| Synthetic A–E | Standard and disease generators | Conditional software comparison |
| Bayesian | Mouse model; 4 chains; 2 priors | Diagnostics met; no human PBPK posterior |
| Sensitivity | Morris; Sobol N128/N64 | Hypothetical ranges; convergence qualified |
| Transcriptomics | TAURUS deposit identified; no matrix | Context only; F excluded |

Endpoint choices are retrospective exploratory analysis choices encoded in scripts,
not a prospectively registered protocol. Calibration and validation trial IDs and
cohort IDs are disjoint. Individual identifiers were not published/acquired, so
participant-level overlap cannot be checked directly. US/EU arms from a single
trial are not counted as distinct studies. The remaining mouse figure profiles
are not independent validation cohorts. Source hashes and missingness are retained.

The observation operator separates free interstitial nmol/L, total recovered tissue
nmol/g and extract/homogenate nmol/L. It requires residual vascular content,
accessible interstitial volume per wet gram, representative organ wet mass,
intracellular/complex assay recovery and overall recovery. Homogenate additionally
requires biopsy wet mass and extraction volume. Protein-normalised or ambiguous
radiolabel signals require further assay definitions and are not mapped by default.
No such conversion was invented for ATLAS or the retained mouse tissue observations.

Predefined positive-concentration metrics are log MAE, log RMSE, geometric bias,
absolute fold error, and paired equal-study-weight error differences with cluster
bootstrap only when >=2 independent clusters exist. BLQ data require a censored
likelihood and are rejected by the uncensored log-normal tools. Published summary
confidence intervals are not substituted for individual predictive distributions.
See scientific_findings.md for the eight-part verdict and exact numerical results.
"""
    (ROOT / "research/validation_summary.md").write_text(summary)
    # Update parameter provenance without rewriting earlier decisions.
    path = ROOT / "data/metadata/parameter_registry.csv"
    with path.open() as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = [r for r in reader if not r["parameter_id"].startswith("C3_")]
    for key, value, unit, condition, source_path, uncertainty in [
        (
            "CL_over_F",
            cal["CL_over_F_L_h"],
            "L/h",
            "healthy Humira aggregate; ka fixed",
            "results/calibration/human_apparent_pk.json",
            "not estimated; zero residual degrees of freedom",
        ),
        (
            "V_over_F",
            cal["V_over_F_L"],
            "L",
            "healthy Humira aggregate; ka fixed",
            "results/calibration/human_apparent_pk.json",
            "not estimated; zero residual degrees of freedom",
        ),
        (
            "mouse_terminal_rate_posterior_median",
            bp["rate_h_median_CI95"][0],
            "1/h",
            "aggregate mouse 7E3 working posterior",
            "results/bayesian/summary.json",
            str(bp["rate_h_median_CI95"][1:]) + " conditional credible interval",
        ),
    ]:
        row = dict.fromkeys(fields, "")
        row.update(
            parameter_id="C3_" + key,
            name=key,
            value=value,
            unit=unit,
            species="Mouse" if "mouse" in key else "Human",
            molecule="7E3" if "mouse" in key else "adalimumab_reference_Humira",
            condition=condition,
            source=source_path,
            status="limited_reduced_model_estimate",
            uncertainty=uncertainty,
            intended_use="not a disease-informed whole-body mechanism estimate",
            human_adalimumab_default="no",
        )
        rows.append(row)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    verified = json.loads((ROOT / "data/metadata/verified_references.json").read_text())
    # Promote verified reference metadata while preserving unrelated registry entries.
    path = ROOT / "research/literature_registry.csv"
    with path.open() as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    for r in rows:
        if r["reference_id"] in ["R07", "R08"]:
            name = (
                "atlas_metadata.json" if r["reference_id"] == "R07" else "yoshihara_metadata.json"
            )
            raw_path = ROOT / "data/raw/chunk3" / name
            if not raw_path.exists():
                r.update(verified[r["reference_id"]])
                continue
            x = json.loads(raw_path.read_text())["resultList"]["result"][0]
            r.update(
                title=x["title"],
                authors=x["authorString"],
                year=x["pubYear"],
                doi=x["doi"],
                verification_status="metadata_and_abstract_verified",
                retrieval_status="metadata_retrieved",
                available_measurements=(
                    "reported tissue study; individual numeric records not acquired"
                ),
                limitations=(
                    "abstract does not establish model-ready data; no "
                    "assay-normalised individual histories"
                ),
            )
    rows = [r for r in rows if not r["reference_id"].startswith("C3_")]
    for identifier, file in [
        ("C3_HUM_CAL", "calibration_population_article.html"),
        ("C3_HUM_VAL", "validation_M923_article.html"),
        ("C3_TAURUS", "taurus_article.html"),
    ]:
        if not (ROOT / "data/raw/chunk3" / file).exists():
            rows.append(dict(verified[identifier]))
            continue
        soup = BeautifulSoup((ROOT / "data/raw/chunk3" / file).read_text(), "html.parser")
        row = dict.fromkeys(fields, "")
        title = soup.find("meta", attrs={"name": "citation_title"})
        doi = soup.find("meta", attrs={"name": "citation_doi"})
        row.update(
            reference_id=identifier,
            title=title.get("content", "") if title else soup.title.get_text().strip(),
            doi=doi.get("content", "") if doi else "",
            verification_status="primary_article_inspected",
            retrieval_status="retrieved",
            source_url=next(s["url"] for s in source if s["path"].endswith(file)),
            limitations="aggregate or contextual evidence; not patient-level tissue validation",
        )
        rows.append(row)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    # Machine-readable eligibility and blocked-source facts, without changing network configuration.
    evidence = {
        "central_hypothesis_status": "inconclusive",
        "independent_tissue_observations": 0,
        "human_aggregate_validation_trials": 1,
        "infliximab_validated": False,
        "TAURUS_matrix_acquired": False,
        "published_environment_changed": False,
        "blocked_probes": [
            {"url": "https://zenodo.org/api/records/13768607", "observed": "proxy tunnel 403"},
            {
                "url": "https://www.nature.com/articles/s41590-024-01994-8",
                "observed": "proxy tunnel 403; OA PMC article subsequently acquired",
            },
            {
                "url": (
                    "https://www.ema.europa.eu/en/documents/product-information/r"
                    "emicade-epar-product-information_en.pdf"
                ),
                "observed": "HTTP 429; not retried in a loop",
            },
        ],
    }
    (ROOT / "results/validation/evidence_gates.json").write_text(
        json.dumps(evidence, indent=2) + "\n"
    )
    print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    report()
