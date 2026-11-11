"""Experimental optional ADA-associated additional free-drug clearance, not ADA kinetics."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Immunogenicity:
    clearance: float = 0.0  # L/h; zero is the default, no assumed immunogenicity

    def __post_init__(self):
        import math

        if not math.isfinite(self.clearance) or self.clearance < 0:
            raise ValueError("Finite nonnegative experimental clearance required")
