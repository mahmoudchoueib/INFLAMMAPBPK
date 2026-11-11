"""Effective 1:1 drug-binding sites; distinct soluble clearance and membrane uptake."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Target:
    baseline: float = 0.0  # free target binding-site nmol per organ
    turnover: float = 0.1
    association: float = 0.1  # L/(nmol h)
    dissociation: float = 0.1
    complex_loss: float = 0.1  # soluble complex elimination OR membrane internalisation

    def __post_init__(self):
        import numpy as np

        if not np.isfinite(list(self.__dict__.values())).all() or min(self.__dict__.values()) < 0:
            raise ValueError("Nonnegative finite target parameters required")

    def rates(self, drug_concentration, target, complex_amount):
        binding = (
            self.association * drug_concentration * target - self.dissociation * complex_amount
        )
        return binding, self.turnover * (self.baseline - target), self.complex_loss * complex_amount
