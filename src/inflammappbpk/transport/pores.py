"""Constant-flow convection/diffusion pore flux; amount/time, not concentration/time."""

import numpy as np


def pore_flux(cv, ci, ps, flow, reflection):
    if not np.isfinite([cv, ci, ps, flow, reflection]).all():
        raise ValueError("Finite transport parameters required")
    if ps < 0 or not 0 <= reflection <= 1 or flow < 0:
        raise ValueError("Require PS >= 0, filtration >= 0 and 0 <= reflection <= 1")
    convection = flow * (1 - reflection)
    if ps == 0:
        return convection * cv
    pe = convection / ps
    if abs(pe) < 1e-7:
        return ps * (cv - ci) + 0.5 * convection * (cv + ci)
    return convection * (cv - ci * np.exp(-pe)) / (-np.expm1(-pe))


def reflection_flux(cv, ci, ps, flow, reflection):
    """Simpler upstream convection approximation for comparison."""
    if ps < 0 or flow < 0 or not 0 <= reflection <= 1:
        raise ValueError("Invalid transport parameters")
    return ps * (cv - ci) + flow * (1 - reflection) * cv
