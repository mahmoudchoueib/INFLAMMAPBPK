"""Endosomal pH-6 kinetics and fast neutral-pH release. Rates h^-1, amounts nmol."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FcRn:
    uptake: float = 0.001
    association: float = 1.0  # L/(nmol h), illustrative
    dissociation: float = 1.0
    receptor: float = 1.0  # total nmol per organ
    recycling: float = 0.2
    degradation: float = 0.5
    endogenous_igg: float = 0.0  # nmol/L in endosome
    endogenous_kd: float = 1000.0

    def __post_init__(self):
        import numpy as np

        if not np.isfinite(list(self.__dict__.values())).all():
            raise ValueError("Finite FcRn parameters required")
        if min(self.__dict__.values()) < 0 or self.endogenous_kd == 0:
            raise ValueError("Nonnegative rates and positive endogenous Kd required")

    def rates(self, free, bound, volume):
        receptor_free = (self.receptor - bound) / (1 + self.endogenous_igg / self.endogenous_kd)
        binding = self.association * free / volume * receptor_free - self.dissociation * bound
        return binding, self.recycling * bound, self.degradation * free
