from dataclasses import replace

import numpy as np
import pytest
from numpy.testing import assert_allclose

from inflammappbpk.research_platform import Scenario, build_model, parameter_table, run_scenario


def test_platform_conserves_repeated_mass_and_units():
    config = Scenario(dose_count=2, horizon_days=14, interval_days=7, route="iv")
    r = run_scenario(config)
    assert r["summary"]["effective_dose_mg"] == 40
    assert r["summary"]["max_mass_error_nmol"] < 1e-6
    assert_allclose(r["curves"].administered_nmol.iloc[-1], 2 * 40 / 150000 * 1e6)
    assert r["curves"].soluble_target_occupancy.isna().all()


def test_weight_scaling_balances_volumes_and_flows():
    c = Scenario(weight_kg=140)
    m = build_model(c)
    assert m.plasma_volume() == pytest.approx(6.0)
    base = build_model(Scenario())
    assert m.organs[2].flow / base.organs[2].flow == pytest.approx(2**0.75)
    r = run_scenario(replace(c, horizon_days=1))
    assert r["summary"]["min_state_nmol"] >= -1e-7


@pytest.mark.parametrize(
    "change",
    [
        {"dose_count": 1.5},
        {"weight_kg": np.nan},
        {"dose_count": 8, "horizon_days": 1},
        {"disease": "reference", "permeability": 2},
        {"biologic": "infliximab"},
        {"biologic": "infliximab", "route": "sc", "acknowledge_infliximab": True},
    ],
)
def test_invalid_or_unsupported_scenarios_rejected(change):
    with pytest.raises(ValueError):
        Scenario(**change)


def test_infliximab_is_explicit_generic_iv_only():
    config = Scenario(
        biologic="infliximab", route="iv", acknowledge_infliximab=True, horizon_days=1
    )
    r = run_scenario(config)
    assert r["summary"]["classification"] == "UNCALIBRATED EXPLORATORY"


def test_reproducible_simulation_and_provenance():
    config = Scenario(horizon_days=1)
    a, b = run_scenario(config), run_scenario(config)
    assert_allclose(a["curves"].plasma_nmol_L, b["curves"].plasma_nmol_L, rtol=0, atol=0)
    assert a["summary"]["configuration_sha256"] == config.fingerprint()
    assert not parameter_table()[["unit", "source", "evidence"]].isna().any().any()
