"""Conservative tight/leaky plasma–interstitium model with finite lymph transit."""

from dataclasses import dataclass

import numpy as np


@dataclass
class MinimalPBPK:
    plasma_volume: float = 3.0
    tight_volume: float = 15.6 * 0.65
    leaky_volume: float = 15.6 * 0.35
    tight_lymph: float = 2.9 / 24 * 0.33
    leaky_lymph: float = 2.9 / 24 * 0.67
    tight_reflection: float = 0.95
    leaky_reflection: float = 0.85
    lymph_reflection: float = 0.2
    lymph_volume: float = 0.1
    clearance: float = 0.015
    ka: float = 0.01
    bioavailability: float = 0.64
    names = ["plasma", "tight", "leaky", "lymph", "depot", "eliminated"]
    iv_index = 0
    sc_index = 4

    def __post_init__(self):
        v = np.array(list(self.__dict__.values()))
        if not np.isfinite(v).all() or np.any(v < 0):
            raise ValueError("Nonnegative finite parameters required")
        if min(self.plasma_volume, self.tight_volume, self.leaky_volume, self.lymph_volume) <= 0:
            raise ValueError("Positive volumes required")
        if any(
            not 0 <= x <= 1
            for x in [
                self.tight_reflection,
                self.leaky_reflection,
                self.lymph_reflection,
                self.bioavailability,
            ]
        ):
            raise ValueError("Invalid fraction")

    def initial(self):
        return np.zeros(6)

    def rhs(self, time, state):
        p, tight, leaky, lymph, depot, _ = state
        a = self.tight_lymph * (1 - self.tight_reflection) * p / self.plasma_volume
        b = self.leaky_lymph * (1 - self.leaky_reflection) * p / self.plasma_volume
        c = self.tight_lymph * (1 - self.lymph_reflection) * tight / self.tight_volume
        d = self.leaky_lymph * (1 - self.lymph_reflection) * leaky / self.leaky_volume
        ret = (self.tight_lymph + self.leaky_lymph) * lymph / self.lymph_volume
        loss = self.clearance * p / self.plasma_volume
        absorption = self.ka * depot
        return np.array(
            [
                -a - b + ret - loss,
                a - c,
                b - d,
                c + d - ret + self.bioavailability * absorption,
                -absorption,
                loss + (1 - self.bioavailability) * absorption,
            ]
        )
