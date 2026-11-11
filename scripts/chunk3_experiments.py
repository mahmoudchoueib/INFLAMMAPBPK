"""Conditional synthetic model comparisons and actual mouse likelihood complexity benchmark."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from inflammappbpk.compartments import LinearPK, MinimalPBPK
from inflammappbpk.inference.estimation import aicc, lognormal_nll, maximum_likelihood
from inflammappbpk.physiology import disease_region, illustrative_organs
from inflammappbpk.simulation import Dose, WholeBody, simulate
from inflammappbpk.tmdd import Target
from inflammappbpk.validation.metrics import paired_improvement, performance

ROOT = Path(__file__).resolve().parents[1]


def experiments():
    out = ROOT / "results/experiments"
    out.mkdir(exist_ok=True)
    time = np.array([0, 24, 48, 72, 96, 168, 240, 336.0])
    models = {
        "A_compartmental": LinearPK(),
        "B_minimal": MinimalPBPK(),
        "C_standard": WholeBody(),
        "D_disease": WholeBody(disease_region(illustrative_organs(), "colon", permeability=3)),
        "E_disease_target": WholeBody(
            disease_region(illustrative_organs(), "colon", permeability=3),
            soluble={"colon": Target(baseline=0.2)},
        ),
    }
    preds = {}
    for name, m in models.items():
        a = simulate(m, time, [Dose(0, 100)])
        if name.startswith("A"):
            plasma = a.state("central") / m.vc
        elif name.startswith("B"):
            plasma = a.state("plasma") / m.plasma_volume
        else:
            plasma = a.state("venous") / m.vv
        tissue = None if name[0] in "AB" else a.state("colon.interstitial") / 0.4
        preds[name] = {"plasma": plasma[1:], "colon": None if tissue is None else tissue[1:]}
    rng = np.random.default_rng(7114)
    rows = []
    records = []
    # Include both standard-generated and disease-generated truth to expose conditional results.
    for truth in ["C_standard", "D_disease"]:
        training = preds[truth]["plasma"] * np.exp(rng.normal(0, 0.1, 7))
        heldout_plasma = np.array(
            [preds[truth]["plasma"] * np.exp(rng.normal(0, 0.1, 7)) for _ in range(4)]
        )
        heldout_tissue = np.array(
            [preds[truth]["colon"] * np.exp(rng.normal(0, 0.1, 7)) for _ in range(4)]
        )
        tissue_predictions = {}
        for name, pred in preds.items():
            # Same one-parameter calibration budget: a multiplicative common observation gain.
            gain = float(np.exp(np.mean(np.log(training / pred["plasma"]))))
            pl = pred["plasma"] * gain
            nll = lognormal_nll(pl, training, 0.1)
            for study in range(4):
                for k, t in enumerate(time[1:]):
                    records.append(
                        dict(
                            classification="SYNTHETIC_NOT_CLINICAL",
                            truth=truth,
                            model=name,
                            study_id=f"synthetic_{truth}_{study}",
                            time_h=t,
                            observed_plasma=heldout_plasma[study, k],
                            predicted_plasma=pl[k],
                            observed_free_colon=heldout_tissue[study, k],
                            predicted_free_colon=None
                            if pred["colon"] is None
                            else pred["colon"][k] * gain,
                        )
                    )
            pm = performance(heldout_plasma.ravel(), np.tile(pl, 4))
            tm = (
                None
                if pred["colon"] is None
                else performance(heldout_tissue.ravel(), np.tile(pred["colon"] * gain, 4))
            )
            if tm is not None:
                tissue_predictions[name] = np.tile(pred["colon"] * gain, 4)
            rows.append(
                dict(
                    classification="SYNTHETIC_NOT_CLINICAL",
                    truth=truth,
                    model=name,
                    fitted_parameter_count=1,
                    gain=gain,
                    calibration_AICc=aicc(nll, 1, 7),
                    heldout_plasma_mae_log=pm["mae_log"],
                    heldout_free_colon_mae_log=None if tm is None else tm["mae_log"],
                    observation_note="A/B have no colon-specific measurement operator",
                )
            )
        differences = paired_improvement(
            heldout_tissue.ravel(),
            tissue_predictions["C_standard"],
            tissue_predictions["D_disease"],
            np.repeat(np.arange(4), 7),
        )
        (out / f"{truth}_synthetic_paired_difference.json").write_text(
            json.dumps(differences, indent=2) + "\n"
        )
    pd.DataFrame(rows).to_csv(out / "synthetic_A_to_E_comparison.csv", index=False)
    pd.DataFrame(records).to_csv(out / "synthetic_heldout_predictions.csv", index=False)
    # Actual 8-point mouse profile, all observations same fit window for both candidates.
    x = pd.read_csv(ROOT / "data/processed/chunk3_7e3_ready.csv")
    x = x[(x.profile.str.endswith("Plasma.Garg2007Fig3")) & (x.source_sheet == "Data_WildType")]
    t = x.sampling_time_h.to_numpy()
    y = x.concentration.to_numpy()

    def one(th):
        return np.exp(th[0] - np.exp(th[1]) * t)

    def two(th):
        a, b, beta, delta = np.exp(th[:4])
        return a * np.exp(-(beta + delta) * t) + b * np.exp(-beta * t)

    fit_rows = []
    for name, forward, starts, bounds in [
        (
            "one_exponential",
            one,
            [[np.log(500), np.log(k), np.log(0.2)] for k in [0.001, 0.002]],
            [(-10, 15), (np.log(1e-6), np.log(1)), (np.log(0.005), np.log(3))],
        ),
        (
            "two_exponential",
            two,
            [
                [np.log(amp), np.log(300), np.log(0.0015), np.log(rate), np.log(0.1)]
                for amp in [500, 1500]
                for rate in [0.03, 0.2]
            ],
            [
                (-10, 15),
                (-10, 15),
                (np.log(1e-6), np.log(0.1)),
                (np.log(1e-5), np.log(2)),
                (np.log(0.005), np.log(3)),
            ],
        ),
    ]:

        def objective(th):
            sigma = np.exp(th[-1])
            if name == "one_exponential":
                logp = th[0] - np.exp(th[1]) * t
            else:
                beta, delta = np.exp(th[2:4])
                logp = np.logaddexp(th[0] - (beta + delta) * t, th[1] - beta * t)
            r = (np.log(y) - logp) / sigma
            return float(np.sum(0.5 * r * r + np.log(sigma) + np.log(y) + 0.5 * np.log(2 * np.pi)))

        fits = [maximum_likelihood(objective, s, bounds) for s in starts]
        good = [r for r in fits if r.success and np.isfinite(r.fun)]
        if not good:
            raise RuntimeError("Mouse comparison failed convergence")
        fit = min(good, key=lambda r: r.fun)
        fit_rows.append(
            dict(
                model=name,
                n=len(y),
                fitted_parameter_count=len(fit.x),
                nll=fit.fun,
                AICc=aicc(fit.fun, len(fit.x), len(y)),
                success=bool(fit.success),
                parameters=fit.x.tolist(),
                scope="in_sample_mouse_working_likelihood; not novelty evidence",
            )
        )
    (out / "mouse_complexity_benchmark.json").write_text(json.dumps(fit_rows, indent=2) + "\n")
    # Gate scientific claims separately from synthetic demonstrations.
    gates = []
    names = [
        "independent tissue improvement",
        "regional compartment prediction improvement",
        "inflammation-dependent transport",
        "local TNF beyond transport",
        "single-cell constraints",
        "Bayesian predictive calibration",
        "infliximab transfer",
        "penalised complexity benefit",
    ]
    for i, name in enumerate(names, 1):
        gates.append(
            dict(
                experiment=i,
                hypothesis=name,
                status="not_demonstrated_on_independent_tissue_data",
                primary_endpoint="paired held-out study-level log concentration error",
                independent_tissue_observations=0,
                software_experiment="synthetic A-E ablations and/or mouse benchmark"
                if i in [1, 3, 4, 6, 8]
                else "not executed: adequate data/mapping unavailable",
                missing_evidence="donor-aware matrix and functional calibration"
                if i == 5
                else "independent molecule-specific infliximab calibration/validation data"
                if i == 7
                else (
                    "assay-interpretable independent human tissue concentrations and full histories"
                ),
            )
        )
    pd.DataFrame(gates).to_csv(out / "scientific_experiment_gates.csv", index=False)
    val = pd.read_csv(ROOT / "results/validation/human_summary_validation.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].bar(np.arange(len(val)), val.predicted_over_observed)
    axes[0].axhline(1, color="k", ls="--")
    axes[0].set_xticks(np.arange(len(val)), val.endpoint)
    axes[0].set(ylabel="Predicted / published aggregate", title="One held-out healthy Humira trial")
    tab = pd.DataFrame(rows)
    for name in models:
        select = tab[tab.model == name]
        if select.heldout_free_colon_mae_log.notna().all():
            axes[1].plot([0, 1], select.heldout_free_colon_mae_log, marker="o", label=name)
    axes[1].set_xticks([0, 1], ["standard-generated", "disease-generated"])
    axes[1].set(title="Synthetic conditional ablations", ylabel="Free-colon log MAE")
    axes[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "summary_comparison.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    experiments()
