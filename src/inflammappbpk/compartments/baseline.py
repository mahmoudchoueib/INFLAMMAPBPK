"""Linear IV and depot models, units nmol, L, h; all elimination is accumulated."""

from dataclasses import dataclass

import numpy as np
from scipy.linalg import expm

from inflammappbpk.simulation.engine import Trajectory


@dataclass(frozen=True)
class LinearPK:
    vc: float = 3.0
    clearance: float = 0.015
    vp: float = 0.0
    exchange: float = 0.0
    ka: float = 0.01
    bioavailability: float = 0.64

    names = ["central", "peripheral", "depot", "eliminated"]
    iv_index = 0
    sc_index = 2

    def __post_init__(self):
        if not np.isfinite(list(self.__dict__.values())).all():
            raise ValueError("Finite PK parameters required")
        if self.vc <= 0 or self.vp < 0 or min(self.clearance, self.exchange, self.ka) < 0:
            raise ValueError("Invalid PK parameters")
        if not 0 <= self.bioavailability <= 1 or (self.exchange > 0 and self.vp == 0):
            raise ValueError("Invalid bioavailability or peripheral volume")

    def initial(self):
        return np.zeros(4)

    def matrix(self):
        m = np.zeros((4, 4))
        m[0, 0] = -(self.clearance + self.exchange) / self.vc
        m[1, 0] = self.exchange / self.vc
        if self.vp:
            m[0, 1] = self.exchange / self.vp
            m[1, 1] = -self.exchange / self.vp
        m[0, 2] = self.ka * self.bioavailability
        m[2, 2] = -self.ka
        m[3, 0] = self.clearance / self.vc
        m[3, 2] = (1 - self.bioavailability) * self.ka
        return m

    def rhs(self, time, state):
        return self.matrix() @ state

    def analytical(self, times, doses):
        out = np.zeros((4, len(times)))
        for dose in doses:
            if dose.route not in {"iv", "sc"}:
                raise ValueError("Unknown route")
            v = self.initial()
            v[self.iv_index if dose.route == "iv" else self.sc_index] = dose.amount
            for i, t in enumerate(times):
                if t >= dose.time:
                    out[:, i] += expm(self.matrix() * (t - dose.time)) @ v
        return Trajectory(np.asarray(times), out, self.names, 0)

    def descriptors(self):
        if self.clearance == 0:
            terminal = 0.0
        elif self.exchange == 0:
            terminal = self.clearance / self.vc
        else:
            rates = np.linalg.eigvals(self.matrix()[:2, :2])
            terminal = float(min(-r.real for r in rates))
        accessible_volume = self.vc + (self.vp if self.exchange > 0 else 0.0)
        return {
            "clearance_L_h": self.clearance,
            "Vss_L": accessible_volume,
            "terminal_iv_half_life_h": np.log(2) / terminal if terminal > 0 else np.inf,
        }


def exposure(time, concentration):
    """Sampled Cmax/Tmax and finite-window AUC; no extrapolated CL from repeat doses."""
    t, c = np.asarray(time), np.asarray(concentration)
    if t.shape != c.shape or t.ndim != 1 or len(t) < 2 or np.any(np.diff(t) <= 0):
        raise ValueError("Aligned increasing times required")
    if not np.isfinite(c).all() or not np.isfinite(t).all():
        raise ValueError("Finite observations required")
    k = np.argmax(c)
    return {
        "Cmax_nmol_L": float(c[k]),
        "Tmax_h": float(t[k]),
        "AUC_nmol_h_L": float(np.trapezoid(c, t)),
    }
