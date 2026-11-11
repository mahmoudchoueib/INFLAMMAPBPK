"""Actual aggregate mouse-data posterior under a working reduced likelihood; no human PBPK claim."""

import json
from pathlib import Path

import arviz as az
import jax
import jax.numpy as jnp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpyro.infer import MCMC, NUTS

from inflammappbpk.inference.bayesian import terminal_model

ROOT = Path(__file__).resolve().parents[1]


def bayesian():
    jax.config.update("jax_enable_x64", True)
    out = ROOT / "results/bayesian"
    out.mkdir(exist_ok=True)
    x = pd.read_csv(ROOT / "results/calibration/mouse_terminal_fit.csv")
    t = x.sampling_time_h.to_numpy()
    y = x.concentration.to_numpy()
    records = {}
    estimates = {}
    for name, width, scale in [("primary", 2.0, 0.5), ("alternative_prior", 1.0, 1.0)]:
        sampler = None
        for warmup, draws, accept in [(600, 1000, 0.9), (1200, 2000, 0.98)]:
            sampler = MCMC(
                NUTS(terminal_model, target_accept_prob=accept),
                num_warmup=warmup,
                num_samples=draws,
                num_chains=4,
                chain_method="sequential",
                progress_bar=False,
            )
            sampler.run(
                jax.random.PRNGKey(813),
                jnp.asarray(t),
                jnp.log(jnp.asarray(y)),
                rate_prior_width=width,
                sigma_prior_scale=scale,
            )
            inference = az.from_numpyro(sampler)
            stats = az.summary(
                inference, var_names=["log_Cref", "log_rate", "sigma_log"], round_to="none"
            )
            divergences = int(np.asarray(sampler.get_extra_fields()["diverging"]).sum())
            passed = (
                divergences == 0
                and stats.r_hat.max() < 1.01
                and stats.ess_bulk.min() > 400
                and stats.ess_tail.min() > 400
            )
            if passed:
                break
        stats.to_csv(out / f"{name}_diagnostics.csv")
        inference.to_netcdf(out / f"{name}_posterior.nc")
        samples = {k: np.asarray(v) for k, v in sampler.get_samples().items()}
        np.savez_compressed(out / f"{name}_draws.npz", **samples)
        rate = np.exp(samples["log_rate"])
        half = np.log(2) / rate
        estimates[name] = float(np.median(rate))
        record = {
            "classification": "aggregate mouse terminal-phase working posterior",
            "independent_human_validation": False,
            "study_count": 1,
            "observations": len(y),
            "chains": 4,
            "warmup": warmup,
            "draws_per_chain": draws,
            "diagnostics_thresholds_met": bool(passed),
            "divergences": divergences,
            "max_rhat": float(stats.r_hat.max()),
            "min_bulk_ess": float(stats.ess_bulk.min()),
            "min_tail_ess": float(stats.ess_tail.min()),
            "rate_h_median_CI95": np.quantile(rate, [0.5, 0.025, 0.975]).tolist(),
            "terminal_half_life_h_median_CI95": np.quantile(half, [0.5, 0.025, 0.975]).tolist(),
            "priors": {
                "log_Cref": "Normal(log(100 nmol/L),3)",
                "log_rate": f"Normal(log(.002 /h),{width})",
                "sigma_log": f"HalfNormal({scale})",
                "justification": "investigator regularisation; not literature-derived",
            },
            "hierarchy": (
                "not fitted: one aggregate curve cannot estimate population/study variability"
            ),
        }
        if name == "primary":
            rng = np.random.default_rng(91)
            latent = np.exp(samples["log_Cref"][:, None] - rate[:, None] * (t - 168))
            predicted = latent * np.exp(
                rng.normal(size=latent.shape) * samples["sigma_log"][:, None]
            )
            q = np.quantile(predicted, [0.025, 0.5, 0.975], axis=0)
            pd.DataFrame(
                dict(
                    time_h=t,
                    observed=y,
                    predicted_lower=q[0],
                    predicted_median=q[1],
                    predicted_upper=q[2],
                    scope="in_sample_working_posterior_predictive",
                )
            ).to_csv(out / "posterior_predictive.csv", index=False)
            record["in_sample_PPC_coverage"] = float(np.mean((y >= q[0]) & (y <= q[2])))
            record["posterior_correlation"] = np.corrcoef(
                [samples["log_Cref"], samples["log_rate"], samples["sigma_log"]]
            ).tolist()
            fig, ax = plt.subplots(1, 2, figsize=(10, 4))
            ax[0].fill_between(t, q[0], q[2], alpha=0.2, label="95% working PPC, in sample")
            ax[0].plot(t, q[1])
            ax[0].scatter(t, y, label="aggregate mouse data")
            ax[0].set(xlabel="Time (h)", ylabel="nmol/L")
            ax[0].legend(fontsize=7)
            ax[1].scatter(samples["log_rate"][::5], samples["log_Cref"][::5], s=3, alpha=0.2)
            ax[1].set(xlabel="log rate", ylabel="log concentration at 168 h")
            fig.suptitle("Reduced mouse model; no human PBPK validation")
            fig.tight_layout()
            fig.savefig(out / "posterior_predictive_and_geometry.png", dpi=150)
            plt.close(fig)
            # Prior predictive concentrations, separate from posterior fit.
            prior_rng = np.random.default_rng(711)
            prior_alpha = prior_rng.normal(np.log(100), 3, 2000)
            prior_rate = np.exp(prior_rng.normal(np.log(0.002), width, 2000))
            log_prior = prior_alpha[:, None] - prior_rate[:, None] * (t - 168)
            pd.DataFrame(
                dict(
                    time_h=t,
                    logC_prior_lower=np.quantile(log_prior, 0.025, axis=0),
                    logC_prior_upper=np.quantile(log_prior, 0.975, axis=0),
                )
            ).to_csv(out / "prior_predictive_logscale.csv", index=False)
        records[name] = record
    records["prior_sensitivity"] = {
        "relative_median_rate_change": estimates["alternative_prior"] / estimates["primary"] - 1,
        "scope": "two stated prior choices, not an exhaustive robustness proof",
    }
    (out / "summary.json").write_text(json.dumps(records, indent=2) + "\n")
    if not all(
        records[key]["diagnostics_thresholds_met"] for key in ["primary", "alternative_prior"]
    ):
        raise RuntimeError(
            "Bayesian diagnostics failed; inspect saved diagnostics before interpretation"
        )
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    bayesian()
