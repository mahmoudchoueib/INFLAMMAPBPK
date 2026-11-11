"""Infrastructure checks, not evidence that the future PBPK model is correct."""

import importlib

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from inflammappbpk.paths import data_root, project_root
from inflammappbpk.units import Q_


def test_numpy_and_scipy_stiff_robertson():
    def rhs(t, y):
        a, b, c = y
        return [-0.04 * a + 1e4 * b * c, 0.04 * a - 1e4 * b * c - 3e7 * b * b, 3e7 * b * b]

    out = solve_ivp(rhs, (0, 100), [1, 0, 0], method="BDF", rtol=1e-8, atol=1e-11)
    assert out.success, out.message
    np.testing.assert_allclose(out.y.sum(axis=0), 1, atol=1e-8)
    np.testing.assert_allclose(
        out.y[:, -1], [0.61723488, 6.153591e-6, 0.38275897], rtol=2e-5, atol=2e-8
    )
    assert out.y.min() >= -1e-10


def test_units_and_explicit_molecular_mass():
    concentration = Q_(1, "microgram / milliliter")
    assert concentration.to("milligram / liter").magnitude == pytest.approx(1)
    # Illustrative 150 kDa IgG, not an assigned adalimumab parameter.
    assert (concentration / Q_(150_000, "gram / mole")).to(
        "nanomole / liter"
    ).magnitude == pytest.approx(6.6666667)


@pytest.mark.parametrize(
    "name",
    [
        "physiology",
        "molecules",
        "compartments",
        "transport",
        "fcrn",
        "tmdd",
        "inflammation",
        "immunogenicity",
        "population",
        "inference",
        "validation",
        "simulation",
        "visualisation",
    ],
)
def test_module_imports(name):
    assert importlib.import_module(f"inflammappbpk.{name}")


def test_paths_independent_of_cwd(tmp_path, monkeypatch):
    expected = data_root()
    monkeypatch.chdir(tmp_path)
    assert data_root() == expected
    assert (data_root() / "metadata").is_dir()


def test_explicit_data_override(tmp_path, monkeypatch):
    monkeypatch.setenv("INFLAMMAPBPK_DATA_DIR", str(tmp_path))
    assert data_root() == tmp_path
    monkeypatch.setenv("INFLAMMAPBPK_DATA_DIR", "relative")
    with pytest.raises(ValueError, match="absolute"):
        data_root()


@pytest.mark.parametrize(
    "name",
    [
        "configs",
        "data/raw",
        "data/processed",
        "data/external_validation",
        "data/metadata",
        "docs",
        "notebooks",
        "research",
        "tests",
        "scripts",
        "results",
        "dashboard",
    ],
)
def test_required_directories(name):
    assert (project_root() / name).is_dir()
