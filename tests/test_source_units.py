"""Guard against mixing concentration and error-column units during extraction."""

import importlib.util
from pathlib import Path

import pytest
from pint.errors import DimensionalityError

spec = importlib.util.spec_from_file_location(
    "extract_osp", Path(__file__).resolve().parents[1] / "scripts/extract_osp_7e3.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.fixture
def synthetic_snapshot():
    return {
        "ObservedData": [
            {
                "Name": "synthetic_not_biological_data",
                "ExtendedProperties": [],
                "BaseGrid": {"Values": [60, 120], "Unit": "minute"},
                "Columns": [
                    {
                        "DataInfo": {"Origin": "Observation"},
                        "Values": [1, 2],
                        "Unit": "micromole/liter",
                        "RelatedColumns": [
                            {
                                "DataInfo": {"AuxiliaryType": "ArithmeticStdDev"},
                                "Values": [2, 0],
                                "Unit": "nanomole/liter",
                            }
                        ],
                    }
                ],
            }
        ]
    }


def test_separate_concentration_sd_and_time_units(synthetic_snapshot):
    rows = module.extract(synthetic_snapshot)
    assert rows[0]["time_h"] == pytest.approx(1)
    assert rows[0]["concentration_nmol_l"] == pytest.approx(1000)
    assert rows[0]["reported_sd_nmol_l"] == pytest.approx(2)
    assert rows[1]["uncertainty_flag"] == "reported_zero_do_not_treat_as_exact"


def test_mismatched_lengths_rejected(synthetic_snapshot):
    synthetic_snapshot["ObservedData"][0]["Columns"][0]["Values"] = [1]
    with pytest.raises(ValueError, match="lengths differ"):
        module.extract(synthetic_snapshot)


def test_geometric_error_not_assumed_arithmetic(synthetic_snapshot):
    error = synthetic_snapshot["ObservedData"][0]["Columns"][0]["RelatedColumns"][0]
    error["DataInfo"]["AuxiliaryType"] = "GeometricStdDev"
    with pytest.raises(ValueError, match="uncertainty type"):
        module.extract(synthetic_snapshot)


def test_incompatible_dimensions_rejected(synthetic_snapshot):
    synthetic_snapshot["ObservedData"][0]["Columns"][0]["Unit"] = "gram"
    with pytest.raises(DimensionalityError):
        module.extract(synthetic_snapshot)
