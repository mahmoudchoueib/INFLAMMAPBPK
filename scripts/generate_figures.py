"""Reproducible scientific figures, including explicit panels for missing evidence."""

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from inflammappbpk.inference.reduced import sc_concentration
from inflammappbpk.research_platform import Scenario, run_scenario

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/figures"
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "legend.fontsize": 8,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
        "svg.hashsalt": "inflammappbpk-v1",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)
COLORS = ["#176c80", "#cf6d34", "#5867a4", "#44947d"]


def read(path):
    return pd.read_csv(ROOT / path)


def load(path):
    return json.loads((ROOT / path).read_text())


def generate():
    OUT.mkdir(exist_ok=True)
    manifest = []

    def save(fig, name, scope, sources):
        fig.text(0.01, 0.005, scope, fontsize=7, color="#444444")
        fig.tight_layout(rect=(0, 0.035, 1, 0.98))
        files = []
        for suffix in ["png", "svg", "pdf"]:
            path = OUT / f"{name}.{suffix}"
            metadata = (
                {"Software": "InflammaPBPK"}
                if suffix == "png"
                else {"Date": None}
                if suffix == "svg"
                else {"CreationDate": None, "ModDate": None}
            )
            fig.savefig(path, dpi=240, metadata=metadata)
            files.append(
                dict(
                    path=str(path.relative_to(ROOT)),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                )
            )
        plt.close(fig)
        manifest.append(dict(id=name, classification=scope, data_sources=sources, exports=files))

    def diagram(title, nodes, edges, note):
        fig, ax = plt.subplots(figsize=(10, 5.5))
        ax.axis("off")
        ax.set(xlim=(-0.02, 1.18), ylim=(0, 1))
        patches = {}
        for name, (x, y, label) in nodes.items():
            patch = FancyBboxPatch(
                (x - 0.09, y - 0.055),
                0.18,
                0.11,
                boxstyle="round,pad=.015",
                facecolor="#eef4f7",
                edgecolor=COLORS[0],
            )
            patches[name] = patch
            ax.add_patch(patch)
            ax.text(x, y, label, ha="center", va="center", fontsize=9)
        for edge in edges:
            start, end, label = edge[:3]
            options = edge[3] if len(edge) > 3 else {}
            x, y, _ = nodes[start]
            u, v, _ = nodes[end]
            reversible = any(
                term in label
                for term in [
                    "kon / koff",
                    "kon,s / koff,s",
                    "kon,m / koff,m",
                    "two-pore exchange",
                    "convection + diffusion",
                ]
            )
            ax.add_patch(
                FancyArrowPatch(
                    (x, y),
                    (u, v),
                    arrowstyle="<->" if reversible else "->",
                    patchA=patches[start],
                    patchB=patches[end],
                    mutation_scale=13,
                    shrinkA=3,
                    shrinkB=3,
                    color="#4b5b69",
                    connectionstyle=f"arc3,rad={options.get('rad', 0.02)}",
                )
            )
            lx, ly = options.get("label_pos", ((x + u) / 2, (y + v) / 2 + 0.035))
            ax.text(
                lx,
                ly,
                label,
                ha="center",
                fontsize=7,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9},
            )
        ax.set_title(title, pad=10)
        ax.text(0.55, 0.025, note, ha="center", fontsize=8)
        return fig

    fig = diagram(
        "Whole-body circulation and exchange",
        {
            "v": (0.12, 0.85, "Venous plasma"),
            "l": (0.5, 0.85, "Lung vascular"),
            "a": (0.88, 0.85, "Arterial plasma"),
            "s": (0.85, 0.52, "Systemic beds"),
            "p": (0.8, 0.15, "Spleen / intestine"),
            "h": (0.4, 0.15, "Liver"),
            "i": (0.45, 0.5, "Interstitial drug"),
            "n": (0.12, 0.5, "Lymph node"),
        },
        [
            ("v", "l", "Qpul"),
            ("l", "a", "Qsys"),
            ("a", "s", "arterial flows"),
            ("s", "v", "venous return", {"label_pos": (0.45, 0.72)}),
            ("a", "p", "portal-bed inflow", {"rad": -0.42, "label_pos": (1.055, 0.36)}),
            ("a", "h", "hepatic arterial inflow", {"label_pos": (0.73, 0.34)}),
            ("p", "h", "portal return"),
            ("h", "v", "hepatic return", {"label_pos": (0.31, 0.35)}),
            ("s", "i", "two-pore exchange"),
            ("i", "n", "lymph drainage"),
            ("n", "v", "lymph return"),
        ],
        "Flows L/h; organ vascular plasma is counted once; systemic beds exclude portal beds.",
    )
    save(
        fig,
        "01_whole_body_architecture",
        "Implemented architecture schematic; numerical model, not anatomical validation",
        ["src/inflammappbpk/simulation/whole_body.py"],
    )
    fig = diagram(
        "Regional intestinal compartment",
        {
            "v": (0.15, 0.75, "Vascular drug"),
            "i": (0.55, 0.75, "Free interstitium"),
            "n": (0.88, 0.75, "Lymph outflow"),
            "e": (0.2, 0.3, "Endosomal drug"),
            "r": (0.55, 0.3, "FcRn-bound drug"),
            "t": (0.88, 0.3, "Local TNF sites"),
        },
        [
            ("v", "i", "convection + diffusion"),
            ("i", "n", "L Ci"),
            ("v", "e", "uptake"),
            ("e", "r", "acidic binding"),
            ("r", "v", "recycling / release"),
            ("i", "t", "binding / loss"),
        ],
        (
            "Small intestine and colon are separate aggregates; no "
            "unsupported ileum-specific parameterisation."
        ),
    )
    save(
        fig,
        "02_intestinal_submodel",
        "Hypothesis-generating regional model schematic",
        ["docs/intestinal_disease_model.md"],
    )
    fig = diagram(
        "FcRn salvage and competition",
        {
            "d": (0.15, 0.8, "Vascular / ISF drug"),
            "e": (0.5, 0.8, "Endosomal free E"),
            "b": (0.85, 0.8, "FcRn-bound B"),
            "z": (0.5, 0.25, "Lysosomal loss"),
            "g": (0.85, 0.25, "IgG competitor"),
        },
        [
            ("d", "e", "uptake u"),
            ("e", "b", "kon / koff"),
            ("b", "d", "krec; neutral release"),
            ("e", "z", "kdeg"),
            ("g", "b", "free-site competition"),
        ],
        (
            "Endosomal pH rates are assumed; surface release and "
            "IgG equilibrium are reduced approximations."
        ),
    )
    save(
        fig,
        "03_fcrn_recycling",
        "Implemented reduced mechanism; human rates are not calibrated",
        ["docs/fcrn_mechanism.md"],
    )
    fig = diagram(
        "Soluble and membrane effective target binding",
        {
            "s": (0.15, 0.8, "D + soluble TNF"),
            "xs": (0.5, 0.8, "Soluble complex"),
            "zs": (0.85, 0.8, "Complex clearance"),
            "m": (0.15, 0.25, "D + membrane TNF"),
            "xm": (0.5, 0.25, "Membrane complex"),
            "zm": (0.85, 0.25, "Internalisation"),
        },
        [
            ("s", "xs", "kon,s / koff,s"),
            ("xs", "zs", "ks"),
            ("m", "xm", "kon,m / koff,m"),
            ("xm", "zm", "km"),
        ],
        "Effective 1:1 sites; separate turnover terms; no multivalent TNF stoichiometry claim.",
    )
    save(
        fig,
        "04_tnf_tmdd",
        "Implemented effective-binding schematic, uncalibrated target kinetics",
        ["docs/tmdd_mechanism.md"],
    )
    fit = load("results/calibration/human_apparent_pk.json")
    t = np.linspace(0, 1680, 400)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(
        t / 24,
        sc_concentration(t, fit["CL_over_F_L_h"], fit["V_over_F_L"], fit["ka_fixed_h"]),
        color=COLORS[0],
    )
    ax.set(
        xlabel="Time (days)",
        ylabel="Plasma concentration (ng/mL)",
        title="Reduced apparent PK: 40 mg SC example",
    )
    save(
        fig,
        "05_adalimumab_plasma_pk",
        "Aggregate-parameter model curve; no observed time-course validation",
        ["results/calibration/human_apparent_pk.json"],
    )
    baseline = run_scenario(Scenario())
    from dataclasses import replace

    alternative = run_scenario(replace(Scenario(), disease="regional_hypothesis", permeability=3))
    fig, ax = plt.subplots(figsize=(7, 4))
    for c, label in [
        ("colon_free_interstitial_nmol_L", "Colon"),
        ("small_intestine_free_interstitial_nmol_L", "Small intestine"),
    ]:
        ax.plot(baseline["curves"].time_day, baseline["curves"][c], label=label)
    ax.set(
        xlabel="Time (days)",
        ylabel="Free interstitial drug (nmol/L)",
        title="Regional tissue exposure in the reference fixture",
    )
    ax.legend()
    save(
        fig,
        "06_intestinal_exposure",
        "Uncalibrated exploratory whole-body simulation",
        ["Scenario defaults, configs/dashboard_control_provenance.json"],
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    for r, label in [(baseline, "Reference transport"), (alternative, "Colon PS x3 hypothesis")]:
        ax.plot(r["curves"].time_day, r["curves"].colon_free_interstitial_nmol_L, label=label)
    ax.set(
        xlabel="Time (days)",
        ylabel="Colon free interstitial drug (nmol/L)",
        title="Reference versus transport hypothesis",
    )
    ax.legend()
    save(
        fig,
        "07_regional_transport_hypothesis",
        "Not observed inflamed/non-inflamed tissue; only PS differs",
        ["Scenario default; regional_hypothesis permeability=3"],
    )
    synthetic = read("results/experiments/synthetic_heldout_predictions.csv")
    selected = synthetic[(synthetic.truth == "D_disease") & synthetic.study_id.str.endswith("_0")]
    fig, ax = plt.subplots(figsize=(7, 4))
    for name in ["A_compartmental", "C_standard", "D_disease"]:
        df = selected[selected.model == name]
        ax.plot(df.time_h / 24, df.predicted_plasma, marker="o", label=name)
    ax.set(
        xlabel="Time (days)",
        ylabel="Simulated plasma (nmol/L)",
        title="Conventional and PBPK comparison on synthetic design",
    )
    ax.legend()
    save(
        fig,
        "08_conventional_and_disease_models",
        "Synthetic comparison; identical one-gain calibration budgets",
        ["results/experiments/synthetic_heldout_predictions.csv"],
    )
    mouse = read("results/calibration/mouse_terminal_fit.csv")
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(mouse.concentration, mouse.prediction_nmol_L, color=COLORS[0])
    lo = min(mouse.concentration.min(), mouse.prediction_nmol_L.min()) * 0.8
    hi = max(mouse.concentration.max(), mouse.prediction_nmol_L.max()) * 1.1
    ax.plot([lo, hi], [lo, hi], ls="--", color="gray")
    ax.set(
        xlabel="Observed aggregate (nmol/L)",
        ylabel="Fitted terminal prediction (nmol/L)",
        title="Mouse 7E3, five in-sample observations",
    )
    save(
        fig,
        "09_observed_vs_predicted",
        "In-sample aggregate mouse fit; not independent human validation",
        ["results/calibration/mouse_terminal_fit.csv"],
    )
    sobol = read("results/sensitivity/sobol_rankings.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, metric, title in zip(
        axes, ["plasma_AUC_0_336", "colon_free_AUC_0_336"], ["Plasma AUC", "Colon free AUC"]
    ):
        d = sobol[sobol.metric == metric]
        ax.bar(np.arange(len(d)), d.ST, yerr=d.ST_conf, color=COLORS[:3])
        ax.set_xticks(np.arange(len(d)), ["Uptake", "Colon PS", "Target"])
        ax.set(title=title, ylabel="Sobol total effect")
    save(
        fig,
        "10_parameter_sensitivity",
        "Hypothetical ranges, N=128; confidence bands and convergence caveats retained",
        ["results/sensitivity/sobol_rankings.csv"],
    )
    profile = load("results/identifiability/mouse_terminal_profile.json")
    rank = load("results/identifiability/whole_body_sensitivity_rank.json")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(
        [r["rate_h"] for r in profile], [r["twice_delta_nll"] for r in profile], color=COLORS[0]
    )
    axes[0].axhline(3.841, ls="--", color="gray")
    axes[0].set(
        xlabel="Mouse terminal rate (1/h)",
        ylabel="2 delta NLL",
        title="Nuisance-reoptimised profile, n=5",
    )
    for key, label in [
        ("plasma_only", "Plasma only"),
        ("plasma_plus_free_colon", "Plasma + free colon"),
    ]:
        axes[1].semilogy(range(1, 6), rank[key]["singular_values"], marker="o", label=label)
    axes[1].set(
        xlabel="Singular-value index",
        ylabel="Log-sensitivity singular value",
        title="Hypothetical whole-body design",
    )
    axes[1].legend()
    save(
        fig,
        "11_identifiability",
        "Asymptotic profile threshold qualified for n=5; SVD rank is tolerance-dependent",
        [
            "results/identifiability/mouse_terminal_profile.json",
            "results/identifiability/whole_body_sensitivity_rank.json",
        ],
    )
    with np.load(ROOT / "results/bayesian/primary_draws.npz") as samples:
        rate = np.exp(samples["log_rate"])
        half = np.log(2) / rate
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].hist(rate, bins=40, color=COLORS[0], density=True)
    axes[0].set(xlabel="Terminal rate (1/h)", ylabel="Density")
    axes[1].hist(half, bins=40, color=COLORS[1], density=True)
    axes[1].set(xlabel="Terminal half-life (h)", ylabel="Density")
    fig.suptitle("Reduced mouse working posterior")
    save(
        fig,
        "12_bayesian_posteriors",
        "Conditional on five aggregate mouse points and stated priors; not human PBPK",
        ["results/bayesian/primary_draws.npz"],
    )
    ppc = read("results/bayesian/posterior_predictive.csv")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.fill_between(
        ppc.time_h,
        ppc.predicted_lower,
        ppc.predicted_upper,
        color=COLORS[0],
        alpha=0.2,
        label="95% working PPC",
    )
    ax.plot(ppc.time_h, ppc.predicted_median, color=COLORS[0])
    ax.scatter(ppc.time_h, ppc.observed, color="black", label="Aggregate mouse observations")
    ax.set(
        xlabel="Time (h)",
        ylabel="Plasma concentration (nmol/L)",
        title="In-sample posterior predictive check",
    )
    ax.legend()
    save(
        fig,
        "13_predictive_uncertainty",
        "Training-data PPC; not clinical prediction interval or external coverage",
        ["results/bayesian/posterior_predictive.csv"],
    )
    cross = load("results/validation/cross_biologic_status.json")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    ax.text(
        0.5,
        0.8,
        "Infliximab external validation: not executed",
        ha="center",
        fontsize=15,
        color=COLORS[1],
    )
    ax.text(
        0.5,
        0.5,
        (
            f"Eligible independent plasma studies: "
            f"{cross['independent_plasma_validation_studies']}\n"
            f"Eligible independent tissue observations: {cross['independent_tissue_observations']}"
        ),
        ha="center",
        linespacing=1.8,
    )
    ax.text(
        0.5,
        0.16,
        (
            "Need IV histories, molecule-specific kinetics, "
            "population covariates\nand assay-interpretable "
            "observations."
        ),
        ha="center",
        fontsize=10,
    )
    save(
        fig,
        "14_infliximab_evidence_gap",
        "Evidence-gap panel, not a fabricated validation curve",
        ["results/validation/cross_biologic_status.json"],
    )
    table = read("results/experiments/synthetic_A_to_E_comparison.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, metric, title in zip(
        axes,
        ["heldout_free_colon_mae_log", "heldout_plasma_mae_log"],
        ["Free-colon error", "Plasma error"],
    ):
        for i, truth in enumerate(["C_standard", "D_disease"]):
            d = table[
                (table.truth == truth)
                & table.model.isin(["C_standard", "D_disease", "E_disease_target"])
            ]
            ax.bar(np.arange(3) + i * 0.36, d[metric], width=0.34, label=truth)
        ax.set_xticks(np.arange(3) + 0.18, ["Standard", "Disease", "Disease + target"])
        ax.set(title=title, ylabel="Mean absolute log error")
        ax.legend(fontsize=7)
    save(
        fig,
        "15_mechanism_ablation",
        "Synthetic generating-model dependence; all plasma and tissue endpoints retained",
        ["results/experiments/synthetic_A_to_E_comparison.csv"],
    )
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Exported {len(manifest)} figures as PNG, SVG and PDF")


if __name__ == "__main__":
    generate()
