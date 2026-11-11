"""Reduced terminal-phase model. Hierarchy is explicit and requires independent study groups."""

import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist


def terminal_model(
    time,
    log_concentration=None,
    *,
    reference_time=168.0,
    rate_prior_width=2.0,
    sigma_prior_scale=0.5,
    study_index=None,
    n_studies=1,
):
    if n_studies < 1 or (n_studies > 1 and study_index is None):
        raise ValueError("Study groups required for a hierarchical model")
    alpha = numpyro.sample("log_Cref", dist.Normal(jnp.log(100.0), 3.0))
    logk = numpyro.sample("log_rate", dist.Normal(jnp.log(0.002), rate_prior_width))
    sigma = numpyro.sample("sigma_log", dist.HalfNormal(sigma_prior_scale))
    if n_studies > 1:
        tau_a = numpyro.sample("between_study_logC_sd", dist.HalfNormal(1.0))
        tau_k = numpyro.sample("between_study_lograte_sd", dist.HalfNormal(1.0))
        with numpyro.plate("study", n_studies):
            za = numpyro.sample("study_logC_z", dist.Normal(0.0, 1.0))
            zk = numpyro.sample("study_lograte_z", dist.Normal(0.0, 1.0))
        alpha = alpha + tau_a * za[study_index]
        logk = logk + tau_k * zk[study_index]
    mean = alpha - jnp.exp(logk) * (time - reference_time)
    numpyro.sample("observed_log_concentration", dist.Normal(mean, sigma), obs=log_concentration)
