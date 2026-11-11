"""Explicit plasma circulation; illustrative geometry is not calibrated human physiology."""

from dataclasses import dataclass, replace

import numpy as np


@dataclass(frozen=True)
class Organ:
    name: str
    flow: float
    vascular: float
    interstitial: float
    lymph: float
    ps: float
    reflection: float = 0.95
    large_fraction: float = 0.1
    large_reflection: float = 0.2
    endosomal: float = 0.002

    def __post_init__(self):
        values = [v for k, v in self.__dict__.items() if k != "name"]
        if not np.isfinite(values).all() or min(values) < 0:
            raise ValueError("Finite nonnegative organ parameters required")
        if min(self.vascular, self.interstitial, self.endosomal) <= 0:
            raise ValueError("Positive organ volumes required")
        if self.name != "lung" and self.flow <= self.lymph:
            raise ValueError("Organ inflow must exceed lymph filtration")
        if max(self.reflection, self.large_fraction, self.large_reflection) > 1:
            raise ValueError("Invalid pore fraction")


def illustrative_organs():
    # ALL values are explicit assumptions for numerical examples, not a physiology fit.
    names = [
        "lung",
        "liver",
        "kidney",
        "spleen",
        "muscle",
        "skin",
        "adipose",
        "small_intestine",
        "colon",
        "remaining",
    ]
    flows = [0, 12, 36, 6, 42, 12, 10, 20, 8, 64]  # systemic sum = 210 L/h
    vascular = [0.25, 0.25, 0.15, 0.08, 0.5, 0.2, 0.12, 0.18, 0.08, 0.49]
    interstitial = [0.3, 0.4, 0.2, 0.1, 4, 2, 1.5, 0.6, 0.4, 2.5]
    return tuple(
        Organ(n, q, v, i, 0.001 * q, 0.003 * i)
        for n, q, v, i in zip(names, flows, vascular, interstitial)
    )


def disease_region(organs, region, *, permeability=1.0, flow=1.0, lymph=1.0):
    """Explicit hypothetical multipliers; no conversion from clinical severity/albumin."""
    if region not in {"small_intestine", "colon"}:
        raise ValueError("Region must be small_intestine or colon")
    if not np.isfinite([permeability, flow, lymph]).all() or min(permeability, flow, lymph) < 0:
        raise ValueError("Nonnegative finite modifiers required")
    if not any(o.name == region for o in organs):
        raise ValueError("Region not in physiology")
    return tuple(
        replace(o, ps=o.ps * permeability, flow=o.flow * flow, lymph=o.lymph * lymph)
        if o.name == region
        else o
        for o in organs
    )
