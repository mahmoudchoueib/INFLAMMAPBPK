"""Identifiable reduced-order functions; apparent SC parameters avoid pretending F is known."""

import numpy as np


def terminal_curve(time, alpha, log_rate, reference_time=168.0):
    return np.exp(alpha - np.exp(log_rate) * (np.asarray(time) - reference_time))


def sc_concentration(time, clearance_over_F, volume_over_F, ka, dose_mg=40.0):
    """Returns ng/mL using mass units. CL/F L/h, V/F L; ka h^-1."""
    if min(clearance_over_F, volume_over_F, ka, dose_mg) <= 0:
        raise ValueError("Positive finite dose and PK parameters required")
    if not np.isfinite([clearance_over_F, volume_over_F, ka, dose_mg]).all():
        raise ValueError("Finite parameters required")
    t = np.asarray(time, dtype=float)
    if not np.isfinite(t).all() or (t < 0).any():
        raise ValueError("Nonnegative finite times required")
    k = clearance_over_F / volume_over_F
    if abs(ka - k) < 1e-8 * max(ka, k):
        return 1000 * dose_mg / volume_over_F * ka * t * np.exp(-k * t)
    return 1000 * dose_mg / volume_over_F * ka / (ka - k) * (np.exp(-k * t) - np.exp(-ka * t))


def sc_summaries(clearance_over_F, volume_over_F, ka, dose_mg=40.0):
    sc_concentration(0.0, clearance_over_F, volume_over_F, ka, dose_mg)
    k = clearance_over_F / volume_over_F
    tmax = 1 / k if abs(ka - k) < 1e-8 * max(ka, k) else np.log(ka / k) / (ka - k)
    return {
        "AUC_inf_ng_h_mL": 1000 * dose_mg / clearance_over_F,
        "Cmax_ng_mL": float(sc_concentration(tmax, clearance_over_F, volume_over_F, ka, dose_mg)),
        "Tmax_h": float(tmax),
        "terminal_half_life_h": float(np.log(2) / min(ka, k)),
    }
