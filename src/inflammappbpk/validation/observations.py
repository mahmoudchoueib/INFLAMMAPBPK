"""Assay-aware operators; canonical nmol/L or nmol/g, never implicit homogenate=ISF."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class TissueAssay:
    organ_wet_mass_g: float
    residual_plasma_L_g: float
    accessible_isf_L_g: float
    intracellular_recovery: float
    complex_recovery: float
    assay_recovery: float
    sample_wet_mass_g: float | None = None
    extract_volume_L: float | None = None

    def __post_init__(self):
        required = [
            self.organ_wet_mass_g,
            self.residual_plasma_L_g,
            self.accessible_isf_L_g,
            self.intracellular_recovery,
            self.complex_recovery,
            self.assay_recovery,
        ]
        if not np.isfinite(required).all() or min(required) < 0 or self.organ_wet_mass_g == 0:
            raise ValueError("Finite nonnegative tissue metadata and positive organ mass required")
        if max(self.intracellular_recovery, self.complex_recovery, self.assay_recovery) > 1:
            raise ValueError("Recovery fractions must lie in [0,1]")
        for value in [self.sample_wet_mass_g, self.extract_volume_L]:
            if value is not None and (not np.isfinite(value) or value <= 0):
                raise ValueError("Positive finite sample mass and extraction volume required")


def observe_tissue(model, trajectory, organ, quantity, assay=None):
    tissue = next(o for o in model.organs if o.name == organ)
    ci = trajectory.state(organ + ".interstitial") / tissue.interstitial
    if quantity == "free_interstitial_nmol_L":
        return ci
    if quantity not in {"total_tissue_nmol_g", "homogenate_nmol_L"}:
        raise ValueError("Unknown or ambiguous measured quantity")
    if assay is None:
        raise ValueError("Tissue/homogenate observations need explicit assay metadata")
    cv = trajectory.state(organ + ".vascular") / tissue.vascular
    intracellular = trajectory.state(organ + ".endosomal") + trajectory.state(organ + ".fcrn_bound")
    complexes = trajectory.state(organ + ".soluble_complex") + trajectory.state(
        organ + ".membrane_complex"
    )
    nmol_g = (
        assay.residual_plasma_L_g * cv
        + assay.accessible_isf_L_g * ci
        + (assay.intracellular_recovery * intracellular + assay.complex_recovery * complexes)
        / assay.organ_wet_mass_g
    ) * assay.assay_recovery
    if quantity == "total_tissue_nmol_g":
        return nmol_g
    if assay.sample_wet_mass_g is None or assay.extract_volume_L is None:
        raise ValueError("Homogenate requires measured sample mass and extraction volume")
    return nmol_g * assay.sample_wet_mass_g / assay.extract_volume_L
