"""Streamlit integration tests exercise all pages and meaningful scenario controls."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("display", ["Static images", "Interactive"])
def test_all_dashboard_pages_and_default_simulation(display):
    app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=40).run()
    assert not app.exception
    assert "simulation" in app.session_state
    assert len(app.get("image")) == 1  # A graph must be visible before the first form submission.
    app.radio(key="chart_display").set_value(display).run()
    assert app.session_state["simulation"]["summary"]["max_mass_error_nmol"] < 1e-6
    pages = app.selectbox(key="page").options
    assert len(pages) == 17
    live_graphs = {
        "Project overview",
        "Whole-body physiology",
        "Plasma pharmacokinetics",
        "Tissue distribution",
        "Intestinal inflammation model",
        "FcRn recycling",
        "Dose and schedule simulator",
        "Population variability",
    }
    stored_graphs = {
        "Parameter sensitivity": "results/sensitivity/sobol_rankings.csv",
        "Bayesian uncertainty": "results/bayesian/summary.json",
        "Model comparison": "results/experiments/synthetic_A_to_E_comparison.csv",
        "Experimental validation": "results/validation/human_summary_validation.csv",
    }
    for page in pages:
        app.selectbox(key="page").set_value(page).run(timeout=40)
        assert not app.exception, page
        if page in live_graphs or (page in stored_graphs and (ROOT / stored_graphs[page]).exists()):
            chart_type = "image" if display == "Static images" else "plotly_chart"
            assert len(app.get(chart_type)) > 0, page
        if page == "Literature and parameter provenance":
            assert [tab.label for tab in app.tabs] == [
                "Controls",
                "Model parameters",
                "Datasets",
                "Literature",
            ]
            assert len(app.dataframe) >= 4
        if page == "User guide":
            assert any("If a graph is missing" in block.value for block in app.markdown)


def test_dashboard_rejects_unsupported_ifx_without_acknowledgment():
    app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=40).run()
    app.selectbox(key="biologic").set_value("infliximab").run()
    app.button(key="run_simulation").click().run(timeout=40)
    assert not app.exception
    assert app.error
    assert "acknowledged hypothetical IV scaffold" in app.error[0].value
    app.checkbox(key="ifx_ack").check()
    app.button(key="run_simulation").click().run(timeout=40)
    assert not app.exception
    assert app.session_state["simulation"]["configuration"]["route"] == "iv"


def test_dashboard_transport_comparison():
    app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=40).run()
    app.selectbox(key="disease").set_value("regional_hypothesis")
    app.number_input(key="p_permeability").set_value(3.0)
    app.button(key="run_simulation").click().run(timeout=40)
    app.selectbox(key="page").set_value("Intestinal inflammation model").run()
    assert not app.exception
    assert len(app.get("image")) >= 1


def test_target_occupancy_and_failed_run_preserves_snapshot():
    app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=40).run()
    app.number_input(key="p_soluble_target").set_value(0.5)
    app.button(key="run_simulation").click().run(timeout=40)
    app.selectbox(key="page").set_value("Target-mediated disposition").run()
    assert not app.exception
    assert app.get("image")
    fingerprint = app.session_state["simulation"]["summary"]["configuration_sha256"]
    app.number_input(key="p_permeability").set_value(3)
    app.button(key="run_simulation").click().run(timeout=40)
    assert app.error
    assert app.session_state["simulation"]["summary"]["configuration_sha256"] == fingerprint


def test_guide_shortcut_is_accessible():
    app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=40).run()
    next(b for b in app.button if b.label == "How to use this dashboard").click().run()
    assert not app.exception
    assert app.selectbox(key="page").value == "User guide"
