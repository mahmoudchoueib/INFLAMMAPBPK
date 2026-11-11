"""Leakage gates and modelling-ready evidence checks."""

import numpy as np

REQUIRED = [
    "drug",
    "study_id",
    "dose",
    "dose_unit",
    "route",
    "administration_time_h",
    "sampling_time_h",
    "concentration",
    "concentration_unit",
    "measured_quantity",
]


def check_data(frame):
    missing = set(REQUIRED) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    if frame[REQUIRED].isna().any().any():
        raise ValueError("Required evidence fields contain missing values")
    numeric = frame[["dose", "administration_time_h", "sampling_time_h", "concentration"]].to_numpy(
        float
    )
    if not np.isfinite(numeric).all() or (numeric < 0).any():
        raise ValueError("Invalid dose, time or concentration")
    if not frame.route.isin(["iv", "sc"]).all():
        raise ValueError("Unknown route")
    if (frame.sampling_time_h < frame.administration_time_h).any():
        raise ValueError("Sampling precedes administration")


def assert_disjoint(calibration, validation):
    """Study exclusion is mandatory; patient IDs are only globally unique with study IDs."""
    if any(
        "study_id" not in frame or frame.study_id.isna().any()
        for frame in [calibration, validation]
    ):
        raise ValueError("Study IDs required to establish independence")
    for column in ["study_id", "cohort_id"]:
        if column in calibration and column in validation:
            common = set(calibration[column].dropna()) & set(validation[column].dropna())
            if common:
                raise ValueError(f"Leakage in {column}: {sorted(common)}")
    if "global_patient_id" in calibration and "global_patient_id" in validation:
        common = set(calibration.global_patient_id.dropna()) & set(
            validation.global_patient_id.dropna()
        )
        if common:
            raise ValueError("Patient leakage")


def missingness(frame):
    return {key: {"missing": int(frame[key].isna().sum()), "total": len(frame)} for key in frame}
