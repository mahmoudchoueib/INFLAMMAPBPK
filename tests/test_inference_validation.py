from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from inflammappbpk.compartments import LinearPK
from inflammappbpk.inference.estimation import (
    aicc,
    lognormal_nll,
    profile_likelihood,
    rank_diagnostics,
    sensitivity_matrix,
    weighted_fit,
)
from inflammappbpk.inference.reduced import sc_concentration, sc_summaries
from inflammappbpk.simulation import Dose
from inflammappbpk.validation.data import assert_disjoint, check_data
from inflammappbpk.validation.metrics import paired_improvement, performance
from inflammappbpk.validation.observations import TissueAssay, observe_tissue


def test_wls_known_parameter_recovery():
    t = np.arange(6.0)
    r = weighted_fit(lambda th: th[0] + th[1] * t, 2 + 3 * t, 0.5, [0, 0], ([-5, -5], [5, 5]))
    assert r.success
    assert_allclose(r.parameters, [2, 3], atol=1e-7)
    assert r.objective < 1e-10


def test_wls_uncertainty_zero_and_log_blq_rejected():
    with pytest.raises(ValueError, match="uncertainties"):
        weighted_fit(lambda th: np.ones(2), [1, 2], 0, [1], ([0], [2]))
    with pytest.raises(ValueError, match="Positive concentrations"):
        weighted_fit(lambda th: np.ones(2), [0, 2], 1, [1], ([0], [2]), log_error=True)


def test_lognormal_jacobian_and_normalization():
    y = np.array([2.0, 4.0])
    sigma = 0.2
    expected = np.sum(np.log(y) + np.log(sigma) + 0.5 * np.log(2 * np.pi))
    assert lognormal_nll(y, y, sigma) == pytest.approx(expected)


def test_profile_reoptimises_correlated_nuisance():
    def objective(p):
        return (p[0] + p[1] - 1) ** 2 + 0.1 * p[1] ** 2

    rows = profile_likelihood(objective, [1.0, 0.0], [(-5, 5), (-5, 5)], 0, [-1.0, 0.0, 1.0, 2.0])
    for row in rows:
        assert row["success"]
        assert row["nll"] == pytest.approx(0.1 / 1.1 * (1 - row["fixed"]) ** 2, abs=1e-8)
        assert row["parameters"][1] == pytest.approx((1 - row["fixed"]) / 1.1, abs=1e-6)


def test_rank_does_not_invent_covariance_for_ridge():
    r = rank_diagnostics([[1, 2], [2, 4], [3, 6]])
    assert r["rank"] == 1 and r["local_parameter_correlation"] is None


def test_finite_difference_linear_jacobian():
    m = np.array([[1, 2], [3, 4.0]])
    assert_allclose(sensitivity_matrix(lambda t: m @ t, [1, 1]), m, atol=1e-11)


def test_unidentifiable_SC_absolute_scale():
    first = LinearPK(vc=4, clearance=0.02, bioavailability=0.4)
    second = LinearPK(vc=8, clearance=0.04, bioavailability=0.8)
    t = np.linspace(0, 1000, 100)
    d = [Dose(0, 100, "sc")]
    assert_allclose(
        first.analytical(t, d).state("central") / 4,
        second.analytical(t, d).state("central") / 8,
        atol=1e-10,
    )


def test_sc_summary_mass_units_and_equal_rates():
    s = sc_summaries(0.02, 10, 0.002)
    assert s["AUC_inf_ng_h_mL"] == pytest.approx(2e6)
    assert s["Tmax_h"] == pytest.approx(500)
    assert sc_concentration(500, 0.02, 10, 0.002) == pytest.approx(4000 / np.e)


def test_study_and_shared_cohort_leakage_rejected():
    a = pd.DataFrame({"study_id": ["s1"], "cohort_id": ["shared"]})
    b = pd.DataFrame({"study_id": ["s2"], "cohort_id": ["shared"]})
    with pytest.raises(ValueError, match="cohort"):
        assert_disjoint(a, b)
    with pytest.raises(ValueError, match="study"):
        assert_disjoint(a, a)
    assert_disjoint(a, pd.DataFrame({"study_id": ["s3"], "cohort_id": ["other"]}))


def test_one_study_no_bootstrap_confidence_interval():
    r = paired_improvement([1, 2], [2, 4], [1, 2], ["s1", "s1"])
    assert r["mean_log_error_improvement"] == pytest.approx(np.log(2))
    assert r["ci95"] is None
    assert performance([1, 2], [1, 2])["mae_log"] == 0


def test_aicc_refuses_insufficient_degrees_of_freedom():
    assert aicc(2, 3, 4) is None
    assert aicc(2, 1, 5) == pytest.approx(4 + 2 + 4 / 3)


@pytest.fixture
def tissue_example():
    model = SimpleNamespace(organs=[SimpleNamespace(name="colon", vascular=0.1, interstitial=0.4)])
    states = {
        f"colon.{key}": np.array([value])
        for key, value in {
            "vascular": 10.0,
            "interstitial": 40.0,
            "endosomal": 1.0,
            "fcrn_bound": 2.0,
            "soluble_complex": 0.5,
            "membrane_complex": 0.5,
        }.items()
    }
    trajectory = SimpleNamespace(state=lambda name: states[name])
    assay = TissueAssay(100, 0.0001, 0.0004, 1.0, 1.0, 1.0, 0.01, 0.001)
    return model, trajectory, assay


def test_homogenate_differs_from_free_interstitial(tissue_example):
    model, trajectory, assay = tissue_example
    assert observe_tissue(model, trajectory, "colon", "free_interstitial_nmol_L")[0] == 100
    assert observe_tissue(model, trajectory, "colon", "total_tissue_nmol_g", assay)[
        0
    ] == pytest.approx(0.09)
    assert observe_tissue(model, trajectory, "colon", "homogenate_nmol_L", assay)[
        0
    ] == pytest.approx(0.9)


def test_homogenate_metadata_required(tissue_example):
    model, trajectory, assay = tissue_example
    with pytest.raises(ValueError, match="metadata"):
        observe_tissue(model, trajectory, "colon", "homogenate_nmol_L")
    incomplete = TissueAssay(100, 0.0001, 0.0004, 1.0, 1.0, 1.0)
    with pytest.raises(ValueError, match="sample mass"):
        observe_tissue(model, trajectory, "colon", "homogenate_nmol_L", incomplete)


def test_tissue_invalid_recovery_fraction_rejected():
    with pytest.raises(ValueError, match="Recovery"):
        TissueAssay(100, 0.0001, 0.0004, 2.0, 1.0, 1.0)


def test_data_schema_does_not_accept_unknown_required_data():
    with pytest.raises(ValueError, match="Missing columns"):
        check_data(pd.DataFrame({"drug": ["adalimumab"]}))


def test_split_requires_known_study_ids():
    with pytest.raises(ValueError, match="Study IDs"):
        assert_disjoint(pd.DataFrame({"study_id": [None]}), pd.DataFrame({"study_id": ["valid"]}))


def test_profile_without_nuisance_parameter():
    rows = profile_likelihood(lambda p: (p[0] - 1) ** 2, [1.0], [(-2, 3)], 0, [-1.0, 0.0, 1.0])
    assert [r["nll"] for r in rows] == [4.0, 1.0, 0.0]
    assert all(r["success"] for r in rows)


def test_hierarchical_prior_api_has_study_specific_latents():
    import jax.numpy as jnp
    from numpyro import handlers

    from inflammappbpk.inference.bayesian import terminal_model

    trace = handlers.trace(handlers.seed(terminal_model, rng_seed=18)).get_trace(
        jnp.array([168.0, 200.0]), n_studies=2, study_index=jnp.array([0, 1])
    )
    assert trace["study_logC_z"]["value"].shape == (2,)
    assert trace["study_lograte_z"]["value"].shape == (2,)
    assert trace["observed_log_concentration"]["value"].shape == (2,)


def test_point_schema_rejects_sample_before_dose():
    frame = pd.DataFrame(
        [
            dict(
                drug="adalimumab",
                study_id="study1",
                dose=40.0,
                dose_unit="mg",
                route="sc",
                administration_time_h=10.0,
                sampling_time_h=5.0,
                concentration=3.0,
                concentration_unit="ng/mL",
                measured_quantity="plasma_drug",
            )
        ]
    )
    with pytest.raises(ValueError, match="precedes"):
        check_data(frame)
    frame["sampling_time_h"] = 15.0
    check_data(frame)
