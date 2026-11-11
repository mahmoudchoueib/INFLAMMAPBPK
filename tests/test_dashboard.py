"""Streamlit integration tests exercise all pages and meaningful scenario controls."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_all_dashboard_pages_and_default_simulation():
    app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=40).run()
    assert not app.exception
    app.button(key="run_simulation").click().run(timeout=40)
    assert not app.exception
    assert "simulation" in app.session_state
    assert app.session_state["simulation"]["summary"]["max_mass_error_nmol"] < 1e-6
    pages = app.selectbox(key="page").options
    assert len(pages) == 15
    for page in pages:
        app.selectbox(key="page").set_value(page).run(timeout=40)
        assert not app.exception, page


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
    next(
        b for b in app.button if b.label == "Compare transport hypothesis with reference transport"
    ).click().run(timeout=40)
    assert not app.exception
    assert len(app.get("plotly_chart")) >= 1
