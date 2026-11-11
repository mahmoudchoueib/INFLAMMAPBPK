"""Evidence-aware Streamlit research application. Launch from the repository root."""

import json
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from inflammappbpk.research_platform import (
    PARAMETERS,
    Scenario,
    parameter_table,
    physiology_table,
    run_scenario,
)

ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    "Project overview",
    "Whole-body physiology",
    "Biologic selection",
    "Plasma pharmacokinetics",
    "Tissue distribution",
    "Intestinal inflammation model",
    "FcRn recycling",
    "Target-mediated disposition",
    "Dose and schedule simulator",
    "Population variability",
    "Parameter sensitivity",
    "Bayesian uncertainty",
    "Model comparison",
    "Experimental validation",
    "Literature and parameter provenance",
]
st.set_page_config(page_title="InflammaPBPK Research", layout="wide")
st.title("InflammaPBPK")
st.caption("Mechanistic research workspace · numerical verification is not biological validation")
st.warning(
    (
        "Exploratory whole-body simulations. Human intestinal "
        "exposure and infliximab transfer are unvalidated."
    )
)
page = st.sidebar.selectbox("Research page", PAGES, key="page")


def number(key):
    spec = PARAMETERS[key]
    help_text = (
        f"Units: {spec.unit}. Default: {spec.default}; exploration bounds: "
        f"{spec.minimum}–{spec.maximum}. Source: {spec.source}. Evidence: {spec.evidence}."
    )
    if key == "dose_count":
        return st.number_input(
            f"{spec.label} ({spec.unit})",
            min_value=int(spec.minimum),
            max_value=int(spec.maximum),
            value=int(spec.default),
            step=1,
            key="p_" + key,
            help=help_text,
        )
    return st.number_input(
        f"{spec.label} ({spec.unit})",
        min_value=float(spec.minimum),
        max_value=float(spec.maximum),
        value=float(spec.default),
        format="%.4f" if spec.default < 1 else "%.1f",
        key="p_" + key,
        help=help_text,
    )


@st.cache_data(max_entries=12, show_spinner=False)
def cached_simulation(payload):
    return run_scenario(Scenario(**payload))


biologic = st.sidebar.selectbox(
    "Biologic",
    ["adalimumab", "infliximab"],
    key="biologic",
    help="Adalimumab: uncalibrated whole-body fixture. Infliximab: generic IV scaffold only.",
)

with st.sidebar.form("simulation_form"):
    st.subheader("Exploratory configuration")
    route = st.selectbox(
        "Route",
        ["iv"] if biologic == "infliximab" else ["sc", "iv"],
        key="route",
        help="Piecewise IV bolus or SC depot; infusions are not implemented.",
    )
    ack = st.checkbox("I acknowledge that infliximab kinetics are hypothetical", key="ifx_ack")
    disease = st.selectbox(
        "Disease scenario",
        ["reference", "regional_hypothesis"],
        key="disease",
        help="No clinical score is mapped to transport. Regional changes are explicit hypotheses.",
    )
    region = st.selectbox(
        "Intestinal region",
        ["colon", "small_intestine"],
        key="region",
        help="Regional aggregate; small intestine does not mean a separately parameterised ileum.",
    )
    unit = st.selectbox(
        "Dose unit",
        ["mg", "mg/kg"],
        key="dose_unit",
        help="Weight-normalised dose uses the entered body weight. This is not dose advice.",
    )
    fields = {}
    with st.expander("Dose, weight and horizon", expanded=True):
        for name in [
            "weight_kg",
            "dose_mg",
            "dose_mg_kg",
            "interval_days",
            "dose_count",
            "horizon_days",
            "molecular_mass",
        ]:
            fields[name] = number(name)
    with st.expander("SC absorption"):
        for name in ["ka", "bioavailability"]:
            fields[name] = number(name)
        st.caption(
            (
                "Absorption parameters are inactive for IV dosing. "
                "F=.64 is an adalimumab single-dose average."
            )
        )
    with st.expander("Regional transport hypotheses"):
        for name in ["permeability", "flow", "lymph"]:
            fields[name] = number(name)
        st.caption("Reference scenario requires all three modifiers to equal 1.")
    with st.expander("FcRn and target hypotheses"):
        for name in [
            "uptake",
            "recycling",
            "degradation",
            "receptor",
            "endogenous_igg",
            "soluble_target",
            "membrane_target",
        ]:
            fields[name] = number(name)
    submitted = st.form_submit_button("Run exploratory simulation", key="run_simulation")
if submitted:
    try:
        config = Scenario(
            biologic=biologic,
            route=route,
            dose_unit=unit,
            region=region,
            disease=disease,
            acknowledge_infliximab=ack,
            **fields,
        )
        with st.spinner("Solving conservative ODEs…"):
            st.session_state["simulation"] = cached_simulation(config.payload())
        st.session_state["simulation_error"] = None
    except (ValueError, RuntimeError) as exc:
        st.session_state["simulation_error"] = str(exc)
if st.session_state.get("simulation_error"):
    st.error(st.session_state["simulation_error"])
result = st.session_state.get("simulation")
st.header(page)
if result is not None:
    st.caption(
        (
            "Displayed results use the last successful run. Apply "
            "edited inputs with Run exploratory simulation."
        )
    )
    st.caption("Configuration fingerprint: " + result["summary"]["configuration_sha256"][:16])
    with st.expander("Displayed configuration and numerical audit"):
        st.json(result["configuration"])
        st.json(result["summary"])
        st.download_button(
            "Download displayed configuration",
            json.dumps(result["configuration"], indent=2),
            "inflammappbpk_configuration.json",
            "application/json",
        )
        st.download_button(
            "Download simulated concentrations and mass audit",
            result["curves"].to_csv(index=False),
            "inflammappbpk_exploratory.csv",
            "text/csv",
        )


def csv(path):
    target = ROOT / path
    if target.exists():
        return pd.read_csv(target)
    st.info("Stored analysis artifact unavailable. Generate it with: make analysis")
    return None


def json_artifact(path):
    target = ROOT / path
    if target.exists():
        return json.loads(target.read_text())
    st.info("Stored analysis artifact unavailable. Generate it with: make analysis")
    return None


def plot(frame, columns, title, ylabel="Concentration (nmol/L)"):
    fig = px.line(
        frame,
        x="time_day",
        y=columns,
        title=title,
        labels={"time_day": "Time (days)", "value": ylabel, "variable": "Quantity"},
    )
    st.plotly_chart(fig, width="stretch")


def live_required():
    if result is None:
        st.info("Configure a scenario in the sidebar and run the exploratory simulation.")
        return False
    return True


if page == "Project overview":
    st.write(
        (
            "Explore implemented mechanisms, inspect their "
            "provenance, and review actual calibration and "
            "validation evidence."
        )
    )
    gates = json_artifact("results/validation/evidence_gates.json")
    if gates:
        a, b, c = st.columns(3)
        a.metric("Independent tissue observations", gates["independent_tissue_observations"])
        b.metric("Held-out healthy trial", gates["human_aggregate_validation_trials"])
        c.metric("Central hypothesis", gates["central_hypothesis_status"])
    st.markdown(
        "**Evidence levels:** implemented ODEs; tested numerical balances; "
        "limited aggregate plasma calibration; one held-out summary comparison; "
        "hypothesis-generating intestinal simulations."
    )
    st.info(
        (
            "No clinical treatment recommendations. Extra "
            "mechanisms and visually plausible curves do not "
            "establish superiority."
        )
    )
elif page == "Whole-body physiology":
    config = Scenario(**result["configuration"]) if result else Scenario()
    table = physiology_table(config)
    st.dataframe(table, width="stretch", hide_index=True)
    st.plotly_chart(
        px.bar(
            table,
            x="organ",
            y="arterial_or_pulmonary_inflow_L_h",
            labels={"arterial_or_pulmonary_inflow_L_h": "Plasma inflow (L/h)"},
            title="Illustrative plasma flows; lung is in series",
        ),
        width="stretch",
    )
    st.caption(
        (
            "Portal inflow is separate from hepatic arterial flow. "
            "Volumes/sites scale with weight; flows/PS with "
            "weight^0.75. These laws are assumptions."
        )
    )
elif page == "Biologic selection":
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "biologic": "adalimumab",
                    "implemented": "generic whole-body IV/SC; reduced healthy-summary PK",
                    "calibration": "two aggregate endpoints, ka fixed",
                    "tissue_validation": "none",
                },
                {
                    "biologic": "infliximab",
                    "implemented": "explicitly acknowledged generic IV scaffold",
                    "calibration": "no drug-specific calibration",
                    "tissue_validation": "none",
                },
            ]
        ),
        hide_index=True,
    )
    st.write(
        (
            "Infliximab SC, IV infusion, drug-specific FcRn/TNF "
            "kinetics and validated tissue transfer are not "
            "implemented."
        )
    )
    st.write(
        (
            "The molecular-mass default is a generic IgG "
            "assumption; it is not a verified drug-specific "
            "measurement."
        )
    )
elif page == "Plasma pharmacokinetics":
    if live_required():
        plot(result["curves"], ["plasma_nmol_L"], "Exploratory free venous plasma")
        st.dataframe(pd.DataFrame([result["summary"]]), hide_index=True)
        st.caption(
            (
                "AUC is finite-window, Cmax/Tmax are sampled. No "
                "nonlinear clinical clearance or half-life is inferred."
            )
        )
elif page == "Tissue distribution":
    if live_required():
        columns = [c for c in result["curves"] if c.endswith("_free_interstitial_nmol_L")]
        chosen = st.multiselect(
            "Free interstitial regions",
            columns,
            default=[c for c in columns if c.startswith(("colon_", "small_intestine_"))],
        )
        if chosen:
            plot(
                result["curves"], chosen, "Free interstitial exposure; not homogenate concentration"
            )
        st.info(
            (
                "Biopsy comparison requires residual vascular content, "
                "tissue mass, recovery and homogenisation metadata."
            )
        )
elif page == "Intestinal inflammation model":
    st.write(
        (
            "Regional PS, blood-flow and lymph multipliers are "
            "explicit hypotheses. Disease labels or severity scores "
            "do not set them."
        )
    )
    if live_required() and st.button("Compare transport hypothesis with reference transport"):
        config = Scenario(**result["configuration"])
        ref = replace(config, disease="reference", permeability=1.0, flow=1.0, lymph=1.0)
        other = cached_simulation(ref.payload())
        column = config.region + "_free_interstitial_nmol_L"
        paired = result["curves"][["time_day", column]].rename(
            columns={column: "configured transport"}
        )
        paired["reference transport"] = other["curves"][column].to_numpy()
        plot(
            paired,
            ["configured transport", "reference transport"],
            "Paired hypothetical transport scenarios",
        )
        st.caption(
            (
                "Target, dose, weight and FcRn settings are held fixed. "
                "Curves are not inflamed/non-inflamed patient "
                "observations."
            )
        )
elif page == "FcRn recycling":
    if live_required():
        plot(
            result["curves"],
            ["endosomal_unbound_nmol", "fcrn_bound_nmol"],
            "Whole-body endosomal drug inventory",
            "Amount (nmol)",
        )
        plot(
            result["curves"],
            ["recycled_flux_integral_nmol", "eliminated_nmol"],
            "Cumulative flux diagnostics",
            "Integrated amount (nmol)",
        )
        st.info(
            (
                "Recycled drug can be counted repeatedly in the flux "
                "integral. It is excluded from remaining-drug mass."
            )
        )
        st.caption(
            (
                "Acidic binding rates and neutral instantaneous release "
                "are hypothetical reduced mechanisms."
            )
        )
elif page == "Target-mediated disposition":
    if live_required():
        cols = ["soluble_target_occupancy", "membrane_target_occupancy"]
        if result["curves"][cols].notna().any().any():
            plot(
                result["curves"],
                cols,
                "Regional effective binding-site occupancy",
                "Occupied fraction",
            )
        else:
            st.info(
                (
                    "No target sites enabled; occupancy is undefined rather "
                    "than zero evidence of engagement."
                )
            )
        st.caption(
            (
                "Effective 1:1 binding sites; soluble complex clearance "
                "and membrane internalisation remain separate "
                "assumptions."
            )
        )
elif page == "Dose and schedule simulator":
    if live_required():
        config = Scenario(**result["configuration"])
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "time_day": i * config.interval_days,
                        "route": config.route,
                        "dose_mg": config.dose_amount_mg(),
                    }
                    for i in range(config.dose_count)
                ]
            ),
            hide_index=True,
        )
        plot(
            result["curves"],
            ["administered_nmol", "drug_remaining_nmol", "eliminated_nmol"],
            "Administered = remaining + eliminated",
            "Amount (nmol)",
        )
        st.metric(
            "Maximum balance residual (nmol)", f"{result['summary']['max_mass_error_nmol']:.3g}"
        )
        st.caption(
            (
                "IV is an instantaneous venous bolus. Infusion and "
                "individual dose histories require further "
                "implementation."
            )
        )
elif page == "Population variability":
    st.write(
        (
            "A three-weight sensitivity grid, not a fitted "
            "population distribution or predictive interval."
        )
    )
    spread = number("population_spread_kg")
    if live_required() and st.button("Run hypothetical weight grid"):
        config = Scenario(**result["configuration"])
        weights = [config.weight_kg - spread, config.weight_kg, config.weight_kg + spread]
        if min(weights) < 40 or max(weights) > 150:
            st.error("Weight grid must stay within 40–150 kg exploration bounds.")
        else:
            comparison = None
            for weight in sorted(set(weights)):
                run = cached_simulation(replace(config, weight_kg=weight).payload())
                if comparison is None:
                    comparison = run["curves"][["time_day"]].copy()
                comparison[f"{weight:g} kg"] = run["curves"].plasma_nmol_L.to_numpy()
            plot(
                comparison,
                [c for c in comparison if c != "time_day"],
                "Hypothetical weight scaling",
            )
            st.caption(
                (
                    "Absolute mg dosing is unchanged; mg/kg dosing changes "
                    "total dose with weight. No empirical covariate law is "
                    "estimated."
                )
            )
elif page == "Parameter sensitivity":
    st.info(
        (
            "Stored reference analysis over hypothetical ranges; "
            "these results are not recalculated by live controls."
        )
    )
    table = csv("results/sensitivity/sobol_rankings.csv")
    if table is not None:
        metric = st.selectbox("Sensitivity endpoint", table.metric.unique())
        selected = table[table.metric == metric]
        st.plotly_chart(
            px.bar(
                selected,
                x="parameter",
                y="ST",
                error_y="ST_conf",
                title="Sobol total effects, N=128; conditional screening",
            ),
            width="stretch",
        )
        st.dataframe(selected, hide_index=True)
    st.caption(
        (
            "Sensitivity is not identifiability. Ranges are "
            "uncalibrated; confidence widths and N64/N128 "
            "differences are retained."
        )
    )
elif page == "Bayesian uncertainty":
    st.info("Stored reduced mouse 7E3 terminal-phase inference; not a human whole-body posterior.")
    summary = json_artifact("results/bayesian/summary.json")
    if summary:
        st.json(summary["primary"])
        if summary["primary"]["diagnostics_thresholds_met"]:
            path = ROOT / "results/bayesian/primary_draws.npz"
            if path.exists():
                with np.load(path) as draws:
                    half = np.log(2) / np.exp(draws["log_rate"])
                st.plotly_chart(
                    px.histogram(
                        x=half,
                        labels={"x": "Mouse working terminal half-life (h)"},
                        title="Conditional posterior draws",
                    ),
                    width="stretch",
                )
            ppc = csv("results/bayesian/posterior_predictive.csv")
            if ppc is not None:
                st.plotly_chart(
                    px.scatter(
                        ppc,
                        x="time_h",
                        y="observed",
                        title="Five aggregate mouse observations; PPC is in-sample",
                    ),
                    width="stretch",
                )
        else:
            st.error(
                (
                    "Posterior diagnostics failed; uncertainty summaries "
                    "are not eligible for interpretation."
                )
            )
elif page == "Model comparison":
    st.info(
        (
            "A–E comparison is synthetic. A/B have no regional "
            "tissue operator. Transcriptomic model F is excluded."
        )
    )
    table = csv("results/experiments/synthetic_A_to_E_comparison.csv")
    if table is not None:
        truth = st.selectbox("Synthetic generating model", table.truth.unique())
        st.dataframe(table[table.truth == truth], hide_index=True, width="stretch")
        st.plotly_chart(
            px.bar(
                table[table.truth == truth],
                x="model",
                y="heldout_plasma_mae_log",
                title="All candidates, identical one-gain calibration budget",
            ),
            width="stretch",
        )
elif page == "Experimental validation":
    st.warning(
        "Usable independent human tissue observations: 0. Infliximab transfer is not validated."
    )
    table = csv("results/validation/human_summary_validation.csv")
    if table is not None:
        st.dataframe(table, hide_index=True, width="stretch")
        st.plotly_chart(
            px.bar(
                table,
                x="endpoint",
                y="predicted_over_observed",
                title="One held-out healthy Humira trial; aggregate summaries",
            ),
            width="stretch",
        )
    st.caption(
        (
            "Different endpoint denominators overlap. Three "
            "summaries are not three independent studies or "
            "individual concentration records."
        )
    )
    st.json(json_artifact("results/validation/cross_biologic_status.json") or {})
elif page == "Literature and parameter provenance":
    tabs = st.tabs(["Controls", "Model parameters", "Datasets", "Literature"])
    with tabs[0]:
        st.dataframe(parameter_table(), hide_index=True, width="stretch")
    for tab, path in zip(
        tabs[1:],
        [
            "data/metadata/parameter_registry.csv",
            "data/metadata/dataset_registry.csv",
            "research/literature_registry.csv",
        ],
    ):
        with tab:
            table = csv(path)
            if table is not None:
                st.dataframe(table, hide_index=True, width="stretch")

with st.expander("Control provenance and exploration bounds"):
    st.dataframe(parameter_table(), hide_index=True, width="stretch")
    st.caption(
        (
            "Exploration bounds are computational guardrails. "
            "Unestablished kinetics, geometry and disease modifiers "
            "require independent evidence before predictive use."
        )
    )
