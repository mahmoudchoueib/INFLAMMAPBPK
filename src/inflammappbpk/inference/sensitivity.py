"""Hypothetical whole-body sensitivities, never calibrated biological importance."""

from dataclasses import replace

import numpy as np

from inflammappbpk.fcrn.mechanism import FcRn
from inflammappbpk.physiology.whole_body import disease_region, illustrative_organs
from inflammappbpk.simulation import Dose, WholeBody, simulate
from inflammappbpk.tmdd.mechanism import Target

PARAMETERS = [
    "log_uptake_multiplier",
    "log_colon_PS_multiplier",
    "log_target_multiplier",
    "log_recycling_multiplier",
    "log_degradation_multiplier",
]
METRICS = [
    "plasma_AUC_0_336",
    "colon_free_AUC_0_336",
    "small_intestine_free_AUC_0_336",
    "colon_to_plasma_AUC_ratio",
    "soluble_target_occupancy_336h",
    "apparent_terminal_half_life_h",
    "instantaneous_elimination_over_plasma_L_h_336h",
]


def whole_forward(theta):
    multipliers = np.exp(theta)
    if len(multipliers) != 5 or not np.isfinite(multipliers).all():
        raise ValueError("Five finite log multipliers required")
    u, ps, target, rec, deg = multipliers
    fc = replace(FcRn(), uptake=0.001 * u, recycling=0.2 * rec, degradation=0.5 * deg)
    m = WholeBody(
        disease_region(illustrative_organs(), "colon", permeability=ps),
        fcrn=fc,
        soluble={"colon": Target(baseline=0.2 * target)},
    )
    time = np.unique(np.r_[np.linspace(0, 336, 57), [24, 48, 72, 96, 168, 240, 336]])
    a = simulate(m, time, [Dose(0, 100)], rtol=2e-7, atol=1e-9)
    plasma = a.state("venous") / m.vv
    colon = a.state("colon.interstitial") / next(
        o.interstitial for o in m.organs if o.name == "colon"
    )
    intestine = a.state("small_intestine.interstitial") / next(
        o.interstitial for o in m.organs if o.name == "small_intestine"
    )
    auc = np.trapezoid(plasma, time)
    auc_c = np.trapezoid(colon, time)
    occupancy = a.state("colon.soluble_complex")[-1] / (
        a.state("colon.soluble_complex")[-1] + a.state("colon.soluble_target")[-1]
    )
    tail = time >= 240
    slope = np.polyfit(time[tail], np.log(plasma[tail]), 1)[0]
    half = -np.log(2) / slope if slope < 0 else np.nan
    flux = m.rhs(time[-1], a.amounts[:, -1])[4] / plasma[-1]
    outputs = np.array(
        [auc, auc_c, np.trapezoid(intestine, time), auc_c / auc, occupancy, half, flux]
    )
    if not np.isfinite(outputs).all():
        raise RuntimeError("Undefined sensitivity endpoint")
    indices = [int(np.where(time == t)[0][0]) for t in [24, 48, 72, 96, 168, 240, 336]]
    return {
        "theta": list(theta),
        "metrics": outputs.tolist(),
        "plasma": plasma[indices].tolist(),
        "colon": colon[indices].tolist(),
    }


def priority_worker(theta):
    return whole_forward([*theta, 0.0, 0.0])
