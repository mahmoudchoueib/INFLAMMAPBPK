"""Synthetic plasma-only conditional profile; all unprofiled physiology is fixed hypothetical."""

import json
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar

from inflammappbpk.inference.sensitivity import whole_forward

ROOT = Path(__file__).resolve().parents[1]


def point(args):
    logps, observed = args

    def objective(logu):
        prediction = np.array(whole_forward([logu, logps, 0.0, 0.0, 0.0])["plasma"])
        r = (np.log(prediction) - np.log(observed)) / 0.1
        return float(0.5 * np.dot(r, r))

    result = minimize_scalar(
        objective,
        bounds=(np.log(0.5), np.log(2.0)),
        method="bounded",
        options={"xatol": 0.005, "maxiter": 40},
    )
    return {
        "colon_PS_multiplier": float(np.exp(logps)),
        "optimal_uptake_multiplier": float(np.exp(result.x)),
        "nll_up_to_constant": float(result.fun),
        "success": bool(result.success),
        "nfev": int(result.nfev),
        "message": result.message,
    }


def run():
    truth = np.array(whole_forward(np.zeros(5))["plasma"])
    observed = truth * np.exp(np.random.default_rng(819).normal(0, 0.1, len(truth)))
    grid = np.linspace(np.log(0.5), np.log(4.0), 7)
    with ProcessPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(point, [(p, observed) for p in grid]))
    best = min(r["nll_up_to_constant"] for r in rows if r["success"])
    for r in rows:
        r["two_delta_nll_relative_best_grid"] = 2 * (r["nll_up_to_constant"] - best)
    result = {
        "classification": "SYNTHETIC_HYPOTHETICAL_PLASMA_DESIGN_ONLY",
        "noise_log_sd_assumed": 0.1,
        "n": len(observed),
        "profiled": "colon PS multiplier",
        "nuisance_reoptimised": "endosomal uptake multiplier",
        "nuisance_bounds": [0.5, 2.0],
        "fixed_parameters": "all remaining illustrative parameters; no human mechanistic inference",
        "profile_grid": rows,
        "global_reference": "best grid NLL, not claimed exact joint optimum",
        "sampling_times_h": [24, 48, 72, 96, 168, 240, 336],
        "observed_synthetic": observed.tolist(),
    }
    (ROOT / "results/identifiability/synthetic_whole_body_profile.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )


if __name__ == "__main__":
    run()
