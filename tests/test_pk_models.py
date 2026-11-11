from dataclasses import replace

import numpy as np
import pytest
from numpy.testing import assert_allclose

from inflammappbpk.compartments.baseline import LinearPK, exposure
from inflammappbpk.compartments.minimal import MinimalPBPK
from inflammappbpk.fcrn.mechanism import FcRn
from inflammappbpk.physiology.whole_body import disease_region, illustrative_organs
from inflammappbpk.simulation.engine import Dose, simulate
from inflammappbpk.simulation.whole_body import WholeBody
from inflammappbpk.tmdd.mechanism import Target
from inflammappbpk.transport.pores import pore_flux


@pytest.mark.parametrize("vp,q,ka", [(0, 0, 0.01), (4, 0.1, 0.01), (0, 0, 0.005)])
@pytest.mark.parametrize("route", ["iv", "sc"])
def test_linear_repeated_analytical(vp, q, ka, route):
    m = LinearPK(vp=vp, exchange=q, ka=ka)
    doses = [Dose(0, 100, route), Dose(24, 50, route), Dose(24, 20, route), Dose(100, 5, route)]
    t = np.unique(np.r_[np.linspace(0, 100, 121), 24])
    a = simulate(m, t, doses)
    assert_allclose(a.amounts, m.analytical(t, doses).amounts, atol=2e-5, rtol=1e-6)
    expected = np.array([sum(d.amount for d in doses if d.time <= time) for time in t])
    assert_allclose(a.amounts.sum(axis=0), expected, atol=2e-8)


def test_one_compartment_closed_form_auc():
    m = LinearPK()
    t = np.linspace(0, 4000, 10001)
    out = m.analytical(t, [Dose(0, 100)])
    assert_allclose(out.state("central"), 100 * np.exp(-m.clearance / m.vc * t), atol=1e-10)
    e = exposure(t, out.state("central") / m.vc)
    assert e["AUC_nmol_h_L"] == pytest.approx(100 / m.clearance, rel=1e-5)
    assert e["Tmax_h"] == 0
    assert m.descriptors()["terminal_iv_half_life_h"] == pytest.approx(np.log(2) * 3 / 0.015)


def test_sc_bateman_equal_rates():
    m = LinearPK(ka=0.005)
    t = np.linspace(0, 1000, 100)
    a = m.analytical(t, [Dose(0, 100, "sc")])
    assert_allclose(a.state("central"), 0.64 * 100 * 0.005 * t * np.exp(-0.005 * t), atol=1e-10)


def test_pore_limits():
    assert pore_flux(2, 1, 0.1, 0, 0.8) == pytest.approx(0.1)
    assert pore_flux(2, 1, 0, 0.2, 0.5) == pytest.approx(0.2)
    assert pore_flux(2, 2, 0.1, 0.2, 0.5) == pytest.approx(0.2)
    assert pore_flux(2, 1, 0.1, 0.2, 1) == pytest.approx(0.1)
    assert np.isfinite(pore_flux(2, 1, 1e-12, 1, 0))
    assert pore_flux(0, 1, 0.1, 0, 0) < 0  # back diffusion, not artificially clipped


def test_minimal_mass_and_steady_partition():
    m = MinimalPBPK(clearance=0)
    a = simulate(m, np.linspace(0, 200, 80), [Dose(0, 100, "sc")])
    assert_allclose(a.amounts.sum(axis=0), 100, atol=1e-8)
    assert a.amounts.min() > -1e-8
    y = m.initial()
    y[0] = m.plasma_volume
    y[1] = m.tight_volume * (1 - m.tight_reflection) / (1 - m.lymph_reflection)
    y[2] = m.leaky_volume * (1 - m.leaky_reflection) / (1 - m.lymph_reflection)
    y[3] = (
        m.lymph_volume
        * (m.tight_lymph * (1 - m.tight_reflection) + m.leaky_lymph * (1 - m.leaky_reflection))
        / (m.tight_lymph + m.leaky_lymph)
    )
    assert_allclose(m.rhs(0, y), 0, atol=1e-14)


def test_whole_body_fluid_and_portal_conservation():
    organs = tuple(replace(o, reflection=0, large_reflection=0) for o in illustrative_organs())
    organs = tuple(replace(o, lymph=0.03) if o.name == "lung" else o for o in organs)
    m = WholeBody(organs, fcrn=FcRn(uptake=0), clearance=0)
    assert m.plasma_volume() == pytest.approx(3)
    y = m.initial()
    y[:3] = [m.va, m.vv, m.vl]
    for o in m.organs:
        j = m.index[o.name]
        y[j] = o.vascular
        y[j + 1] = o.interstitial
    assert_allclose(m.rhs(0, y), 0, atol=5e-14)


@pytest.mark.parametrize("transport", ["two_pore", "reflection"])
def test_whole_body_balance_nonnegative_and_receptor(transport):
    m = WholeBody(
        transport=transport,
        soluble={"colon": Target(baseline=0.2)},
        membrane={"colon": Target(baseline=0.4, complex_loss=0.3)},
    )
    doses = [Dose(0, 10), Dose(12, 20, "sc"), Dose(24, 5)]
    t = np.linspace(0, 48, 49)
    a = simulate(m, t, doses)
    expected = [sum(d.amount for d in doses if d.time <= x) for x in t]
    assert_allclose(m.drug_total(a.amounts) + a.state("eliminated"), expected, atol=2e-7)
    assert a.amounts.min() > -1e-8
    for j in m.index.values():
        assert a.amounts[j + 3].max() <= m.fc.receptor + 1e-8
    assert a.state("recycled_total")[-1] > 0


def test_target_closed_binding_stoichiometry():
    m = WholeBody(
        clearance=0,
        fcrn=FcRn(uptake=0),
        soluble={"colon": Target(0.3, 0, 0.2, 0.1, 0)},
        membrane={"colon": Target(0.4, 0, 0.3, 0.1, 0)},
    )
    a = simulate(m, np.linspace(0, 30, 25), [Dose(0, 20)])
    assert_allclose(
        a.state("colon.soluble_target") + a.state("colon.soluble_complex"), 0.3, atol=1e-9
    )
    assert_allclose(
        a.state("colon.membrane_target") + a.state("colon.membrane_complex"), 0.4, atol=1e-9
    )
    assert_allclose(m.drug_total(a.amounts), 20, atol=1e-8)


def test_target_turnover_equilibrium():
    m = WholeBody(soluble={"colon": Target(0.2)}, membrane={"colon": Target(0.4)})
    assert_allclose(m.rhs(0, m.initial()), 0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"recycling": 0},
        {"recycling": 2},
        {"degradation": 2},
        {"receptor": 0},
        {"endogenous_igg": 10000},
    ],
)
def test_fcrn_mechanism_limits(kwargs):
    fc = replace(FcRn(), **kwargs)
    binding, recycle, degrade = fc.rates(0.02, 0, 0.002)
    assert binding >= 0 and recycle == 0 and degrade >= 0
    if fc.receptor == 0:
        assert binding == 0
    if fc.endogenous_igg:
        assert binding < FcRn().rates(0.02, 0, 0.002)[0]


def test_recycling_availability_and_degradation_direction():
    # Isolated endosomal subsystem: a controlled sensitivity test, not experimental validation.
    from scipy.integrate import solve_ivp

    def recover(fc):
        def rhs(t, y):
            b, r, d = fc.rates(y[0], y[1], 0.1)
            return [-b - d, b - r, r, d]

        a = solve_ivp(rhs, [0, 50], [1, 0, 0, 0], method="BDF", rtol=1e-9, atol=1e-11)
        assert a.success
        assert_allclose(a.y.sum(axis=0), 1, atol=1e-9)
        return a.y[2, -1]

    base = recover(FcRn())
    assert recover(FcRn(recycling=0)) == 0
    assert recover(FcRn(receptor=0)) == 0
    assert recover(FcRn(recycling=1)) > base
    assert recover(FcRn(degradation=2)) < base
    assert recover(FcRn(receptor=2)) > base


def test_disease_locality_and_validation():
    o = illustrative_organs()
    changed = disease_region(o, "colon", permeability=2)
    for a, b in zip(o, changed):
        assert b.ps == a.ps * (2 if a.name == "colon" else 1)
    with pytest.raises(ValueError):
        disease_region(o, "colon", flow=0)
    with pytest.raises(ValueError):
        disease_region(o, "ileum")


def test_radau_bdf_tolerance_convergence():
    m = WholeBody()
    t = np.linspace(0, 12, 20)
    d = [Dose(0, 10)]
    a = simulate(m, t, d, rtol=1e-6, atol=1e-8)
    b = simulate(m, t, d, rtol=1e-9, atol=1e-11)
    c = simulate(m, t, d, method="Radau", rtol=1e-9, atol=1e-11)
    assert_allclose(b.amounts, c.amounts, rtol=2e-5, atol=2e-7)
    assert_allclose(a.amounts, b.amounts, rtol=2e-4, atol=2e-6)


@pytest.mark.parametrize("times", [[1, 2], [0, 1, 1], [0, np.nan]])
def test_bad_times(times):
    with pytest.raises(ValueError):
        simulate(LinearPK(), times)


def test_portal_direction_is_spleen_to_liver_not_vein():
    organs = tuple(replace(o, lymph=0, ps=0) for o in illustrative_organs())
    m = WholeBody(organs, fcrn=FcRn(uptake=0), clearance=0)
    y = m.initial()
    y[m.index["spleen"]] = 1
    derivative = m.rhs(0, y)
    spleen = next(o for o in organs if o.name == "spleen")
    assert derivative[m.index["liver"]] == pytest.approx(spleen.flow / spleen.vascular)
    assert derivative[1] == 0


def test_optional_ada_mass_balance_and_effect():
    from inflammappbpk.immunogenicity import Immunogenicity

    ada = Immunogenicity(clearance=0.02)
    m = WholeBody(ada_clearance=ada.clearance)
    t = np.linspace(0, 24, 25)
    a = simulate(m, t, [Dose(0, 10)])
    b = simulate(WholeBody(), t, [Dose(0, 10)])
    assert_allclose(m.drug_total(a.amounts) + a.state("eliminated"), 10, atol=1e-8)
    assert a.state("eliminated")[-1] > b.state("eliminated")[-1]


def test_depot_no_bioavailability_limiting_case():
    m = LinearPK(bioavailability=0)
    a = simulate(m, np.linspace(0, 1000, 25), [Dose(0, 100, "sc")])
    assert_allclose(a.state("central"), 0)
    assert_allclose(a.state("depot") + a.state("eliminated"), 100, atol=1e-8)


def test_no_clearance_has_no_finite_elimination_half_life():
    assert np.isinf(
        LinearPK(clearance=0, vp=4, exchange=0.1).descriptors()["terminal_iv_half_life_h"]
    )


def test_inaccessible_peripheral_volume_does_not_inflate_vss():
    assert LinearPK(vc=3, vp=4, exchange=0).descriptors()["Vss_L"] == 3
