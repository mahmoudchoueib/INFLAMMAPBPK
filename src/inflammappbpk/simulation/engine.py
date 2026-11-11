"""Piecewise stiff integration with right-continuous bolus events (nmol, h)."""

from dataclasses import dataclass
from typing import Protocol

import numpy as np
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class Dose:
    time: float
    amount: float
    route: str = "iv"

    def __post_init__(self):
        if not np.isfinite([self.time, self.amount]).all() or self.time < 0 or self.amount < 0:
            raise ValueError("Dose time and amount must be finite and nonnegative")
        if self.route not in {"iv", "sc"}:
            raise ValueError("Route must be iv or sc")


class Model(Protocol):
    names: list[str]
    iv_index: int
    sc_index: int

    def initial(self) -> np.ndarray: ...
    def rhs(self, time: float, state: np.ndarray) -> np.ndarray: ...


@dataclass
class Trajectory:
    time: np.ndarray
    amounts: np.ndarray
    names: list[str]
    nfev: int

    def state(self, name):
        return self.amounts[self.names.index(name)]


def simulate(model: Model, times, doses=(), *, method="BDF", rtol=1e-8, atol=1e-10):
    times = np.asarray(times, dtype=float)
    if times.ndim != 1 or len(times) < 2 or not np.isfinite(times).all():
        raise ValueError("At least two finite observation times required")
    if times[0] != 0 or np.any(np.diff(times) <= 0):
        raise ValueError("Times must start at zero and increase strictly")
    if rtol <= 0 or atol <= 0:
        raise ValueError("Tolerances must be positive")
    doses = tuple(doses)
    if any(d.time > times[-1] for d in doses):
        raise ValueError("Dose outside simulation horizon")
    events = sorted({0.0, float(times[-1]), *(float(d.time) for d in doses)})
    y = np.asarray(model.initial(), dtype=float)
    result = np.empty((len(y), len(times)))
    nfev = 0
    for i, left in enumerate(events):
        for dose in doses:
            if dose.time == left:
                y[model.iv_index if dose.route == "iv" else model.sc_index] += dose.amount
        result[:, times == left] = y[:, None]
        if i == len(events) - 1:
            break
        right = events[i + 1]
        mask = (times > left) & (times < right)
        requested = np.append(times[mask], right)
        sol = solve_ivp(
            model.rhs, (left, right), y, method=method, t_eval=requested, rtol=rtol, atol=atol
        )
        if not sol.success or not np.isfinite(sol.y).all():
            raise RuntimeError(sol.message)
        result[:, mask] = sol.y[:, :-1]
        y = sol.y[:, -1]
        nfev += sol.nfev
    return Trajectory(times, result, model.names, nfev)
