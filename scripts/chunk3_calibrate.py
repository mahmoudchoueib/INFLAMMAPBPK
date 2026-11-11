"""Real but limited aggregate calibrations, with explicit inferential boundaries."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.integrate import quad

from inflammappbpk.inference.estimation import (
    aicc,
    lognormal_nll,
    maximum_likelihood,
    profile_likelihood,
    rank_diagnostics,
    sensitivity_matrix,
    weighted_fit,
)
from inflammappbpk.inference.reduced import sc_concentration, sc_summaries, terminal_curve
from inflammappbpk.validation.metrics import performance

ROOT = Path(__file__).resolve().parents[1]


def calibrate():
    out = ROOT / "results/calibration"
    out.mkdir(exist_ok=True)
    ident = ROOT / "results/identifiability"
    ident.mkdir(exist_ok=True)
    val = ROOT / "results/validation"
    val.mkdir(exist_ok=True)
    data = pd.read_csv(ROOT / "data/processed/chunk3_human_summary_endpoints.csv")
    train = data[data.role == "calibration"]
    test = data[data.role == "validation"].copy()
    y = train.value.to_numpy()
    ka = 0.0219

    def predict(theta):
        values = sc_summaries(*np.exp(theta), ka)
        return np.array([values["AUC_inf_ng_h_mL"], values["Cmax_ng_mL"]])

    estimate = weighted_fit(
        predict,
        y,
        0.15,
        np.log([0.02, 8.0]),
        (np.log([0.001, 0.5]), np.log([0.2, 40.0])),
        log_error=True,
    )
    if not estimate.success:
        raise RuntimeError(estimate.message)
    cl, v = np.exp(estimate.parameters)
    summaries = sc_summaries(cl, v, ka)
    auc336 = quad(lambda t: float(sc_concentration(t, cl, v, ka)), 0, 336, epsabs=1e-4)[0]
    p = {
        "AUC_inf": summaries["AUC_inf_ng_h_mL"],
        "Cmax": summaries["Cmax_ng_mL"],
        "AUC_0_336": auc336,
    }
    test["predicted"] = test.endpoint.map(p)
    test["predicted_over_observed"] = test.predicted / test.value
    test["log_error"] = np.log(test.predicted / test.value)
    test["comparison_scope"] = (
        "one held-out healthy trial, aggregate endpoints; not IBD or tissue validation"
    )
    test.to_csv(val / "human_summary_validation.csv", index=False)
    human = dict(
        classification="aggregate apparent-PK calibration, not individual or disease-informed PBPK",
        CL_over_F_L_h=cl,
        V_over_F_L=v,
        ka_fixed_h=ka,
        ka_source="PMC13675741 final PopPK model; same source as calibration",
        fitted_parameter_count=2,
        calibration_summary_count=2,
        residual_degrees_of_freedom=0,
        log_error_scale=0.15,
        error_scale_status="working weights, not measured standard errors",
        success=estimate.success,
        objective=estimate.objective,
        message=estimate.message,
        residuals=estimate.residuals.tolist(),
        **summaries,
        parameter_CI=None,
        reason=(
            "Two aggregate endpoints, two fitted parameters; covariance "
            "unavailable; ka and F not separately identified"
        ),
    )
    (out / "human_apparent_pk.json").write_text(json.dumps(human, indent=2) + "\n")
    # One selected aggregate terminal profile; no pooling of overlapping figure series.
    x = pd.read_csv(ROOT / "data/processed/chunk3_7e3_ready.csv")
    subset = x[
        (x.profile.str.endswith("Plasma.Garg2007Fig3"))
        & (x.source_sheet == "Data_WildType")
        & (x.sampling_time_h >= 168)
    ].copy()
    t = subset.sampling_time_h.to_numpy()
    obs = subset.concentration.to_numpy()
    bounds = [(-10, 15), (np.log(1e-6), np.log(0.1)), (np.log(0.01), np.log(3.0))]

    def predict_mouse(theta):
        return terminal_curve(t, *theta[:2])

    def objective(theta):
        return lognormal_nll(predict_mouse(theta), obs, np.exp(theta[2]))

    starts = [np.array([np.log(obs[0]), np.log(k), np.log(0.2)]) for k in [0.0003, 0.001, 0.003]]
    fits = [maximum_likelihood(objective, start, bounds) for start in starts]
    good = [r for r in fits if r.success and np.isfinite(r.fun)]
    if not good:
        raise RuntimeError("Mouse terminal MLE did not converge")
    fit = min(good, key=lambda r: r.fun)
    subset["prediction_nmol_L"] = predict_mouse(fit.x)
    subset["log_residual"] = np.log(obs / subset.prediction_nmol_L)
    subset.to_csv(out / "mouse_terminal_fit.csv", index=False)
    wls = weighted_fit(
        lambda theta: terminal_curve(t, *theta),
        obs,
        0.2,
        fit.x[:2],
        ([bounds[0][0], bounds[1][0]], [bounds[0][1], bounds[1][1]]),
        log_error=True,
    )
    profile = profile_likelihood(
        objective, fit.x, bounds, 1, np.linspace(fit.x[1] - 1.3, fit.x[1] + 1.3, 31)
    )
    for row in profile:
        row["rate_h"] = float(np.exp(row["fixed"]))
        row["twice_delta_nll"] = 2 * (row["nll"] - fit.fun) if row["nll"] is not None else None
    pd.DataFrame(profile).to_json(ident / "mouse_terminal_profile.json", orient="records", indent=2)
    jac = sensitivity_matrix(lambda theta: np.log(terminal_curve(t, *theta)), fit.x[:2])
    diagnostics = rank_diagnostics(jac)
    result = dict(
        classification="exploratory aggregate mouse terminal-phase working likelihood",
        n=len(t),
        selected_profile=str(subset.profile.iloc[0]),
        time_threshold_h=168,
        selection_status="exploratory terminal window, not preregistered",
        reference_time_h=168,
        log_Cref=float(fit.x[0]),
        rate_h=float(np.exp(fit.x[1])),
        half_life_h=float(np.log(2) / np.exp(fit.x[1])),
        sigma_log=float(np.exp(fit.x[2])),
        nll=float(fit.fun),
        AICc=aicc(fit.fun, 3, len(t)),
        success=bool(fit.success),
        message=fit.message,
        wls_rate_h=float(np.exp(wls.parameters[1])),
        metrics=performance(obs, predict_mouse(fit.x)),
        identifiability=diagnostics,
        uncertainty_warning=(
            "Five aggregate points; likelihood/error scale are assumptions, "
            "no patient-level interpretation"
        ),
    )
    (out / "mouse_terminal_mle.json").write_text(json.dumps(result, indent=2) + "\n")
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    ax[0].scatter(t, obs, label="observed aggregate mouse 7E3")
    ax[0].plot(t, predict_mouse(fit.x), label="terminal fit")
    ax[0].set_yscale("log")
    ax[0].set(xlabel="Time (h)", ylabel="Concentration (nmol/L)")
    ax[0].legend(fontsize=8)
    ax[1].plot([r["rate_h"] for r in profile], [r["twice_delta_nll"] for r in profile])
    ax[1].axhline(3.841, ls="--", color="gray", label="asymptotic threshold; n=5 caveat")
    ax[1].set(xlabel="Terminal rate (1/h)", ylabel="2 delta NLL")
    ax[1].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(ident / "terminal_fit_and_profile.png", dpi=150)
    plt.close(fig)
    # Simulated-data recovery with a known mechanism, explicit synthetic label.
    rng = np.random.default_rng(721)
    recovery = []
    true = np.array([np.log(300.0), np.log(0.0015)])
    tr = np.linspace(168, 1440, 25)
    for seed in range(20):
        simulated = terminal_curve(tr, *true) * np.exp(rng.normal(0, 0.1, len(tr)))
        r = weighted_fit(
            lambda th: terminal_curve(tr, *th),
            simulated,
            0.1,
            true + 0.1,
            ([-10, np.log(1e-6)], [15, np.log(0.1)]),
            log_error=True,
        )
        recovery.append(
            dict(
                replicate=seed,
                classification="SYNTHETIC",
                true_rate=0.0015,
                estimated_rate=float(np.exp(r.parameters[1])),
                success=r.success,
            )
        )
    pd.DataFrame(recovery).to_csv(ident / "synthetic_parameter_recovery.csv", index=False)
    return result, human


if __name__ == "__main__":
    calibrate()
