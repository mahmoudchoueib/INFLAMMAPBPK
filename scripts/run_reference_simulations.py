"""Reproducible uncalibrated examples. All outputs are exploratory, not clinical predictions."""

import csv
import json
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from inflammappbpk.compartments.baseline import LinearPK, exposure
from inflammappbpk.fcrn.mechanism import FcRn
from inflammappbpk.physiology.whole_body import disease_region, illustrative_organs
from inflammappbpk.simulation.engine import Dose, simulate
from inflammappbpk.simulation.whole_body import WholeBody
from inflammappbpk.tmdd.mechanism import Target
from inflammappbpk.units import Q_

root = Path(__file__).resolve().parents[1]
out = root / "results/chunk2"
out.mkdir(parents=True, exist_ok=True)


# EMA adult Crohn's schedule: 80 mg week 0, 40 mg week 2 then every other week.
# Molecular mass is a generic illustrative IgG value, NOT a sourced adalimumab property.
def nmol(mg):
    return (Q_(mg, "mg") / Q_(150000, "g/mol")).to("nmol").magnitude


doses = [Dose(t, nmol(mg), "sc") for t, mg in [(0, 80), (336, 40), (672, 40), (1008, 40)]]
times = np.unique(np.r_[np.linspace(0, 1344, 337), [d.time for d in doses]])
organs = illustrative_organs()
models = {
    "reference_exploratory": WholeBody(clearance=0.0),
    "colon_hypothesis": WholeBody(
        disease_region(organs, "colon", permeability=3, lymph=0.8, flow=1.2),
        clearance=0.0,
        soluble={"colon": Target(baseline=0.2)},
        membrane={"colon": Target(baseline=0.1, complex_loss=0.3)},
    ),
    "no_recycling": WholeBody(clearance=0.0, fcrn=FcRn(recycling=0)),
    "target_only_hypothesis": WholeBody(
        clearance=0.0,
        soluble={"colon": Target(baseline=0.2)},
        membrane={"colon": Target(baseline=0.1, complex_loss=0.3)},
    ),
}
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
summary = {"classification": "UNCALIBRATED EXPLORATORY; NOT VALIDATED", "models": {}}
for name, m in models.items():
    start = perf_counter()
    a = simulate(m, times, doses)
    elapsed = perf_counter() - start
    plasma = a.state("venous") / m.vv
    colon = a.state("colon.interstitial") / next(
        o.interstitial for o in m.organs if o.name == "colon"
    )
    small = a.state("small_intestine.interstitial") / next(
        o.interstitial for o in m.organs if o.name == "small_intestine"
    )
    administered = np.array([sum(d.amount for d in doses if d.time <= t) for t in times])
    residual = m.drug_total(a.amounts) + a.state("eliminated") - administered
    pd.DataFrame(a.amounts.T, columns=a.names, index=times).rename_axis("time_h").to_csv(
        out / f"{name}_amounts_nmol.csv"
    )
    pd.DataFrame(
        dict(
            time_h=times,
            plasma_free_nmol_L=plasma,
            colon_free_interstitial_nmol_L=colon,
            small_intestine_free_interstitial_nmol_L=small,
        )
    ).to_csv(out / f"{name}_concentrations.csv", index=False)
    summary["models"][name] = dict(
        **exposure(times, plasma),
        wall_seconds=elapsed,
        nfev=a.nfev,
        max_mass_residual_nmol=float(abs(residual).max()),
        minimum_state_nmol=float(a.amounts.min()),
        fcrn=asdict(m.fc),
        soluble={k: asdict(v) for k, v in m.soluble.items()},
        membrane={k: asdict(v) for k, v in m.membrane.items()},
    )
    axes[0, 0].plot(times / 24, plasma, label=name)
    axes[0, 1].plot(times / 24, colon, label=name)
    axes[1, 0].plot(times / 24, small, label=name)
    axes[1, 1].plot(times / 24, a.state("eliminated"), label=f"{name}: eliminated")
    axes[1, 1].plot(
        times / 24, a.state("recycled_total"), ls="--", label=f"{name}: recycled flux integral"
    )
for ax, title, unit in zip(
    axes.flat,
    [
        "Venous free plasma",
        "Colon free interstitial",
        "Small-intestine free interstitial",
        "Cumulative fluxes",
    ],
    ["nmol/L", "nmol/L", "nmol/L", "nmol"],
):
    ax.set(xlabel="Time (days)", ylabel=unit, title=title)
    ax.legend(fontsize=6)
fig.suptitle("Uncalibrated exploratory simulations; physiology/kinetics are hypotheses")
fig.tight_layout()
fig.savefig(out / "reference_simulations.png", dpi=160)
plt.close(fig)
linear = LinearPK(vc=5.5, clearance=0.013)
b = simulate(linear, times, doses)
summary["linear_reference"] = dict(
    **linear.descriptors(), **exposure(times, b.state("central") / linear.vc)
)
# Independent solver benchmark on the same model and events, not on plotted plausibility.
benchmark = {}
for method in ["BDF", "Radau"]:
    start = perf_counter()
    a = simulate(
        models["reference_exploratory"], np.linspace(0, 48, 49), [Dose(0, 100)], method=method
    )
    benchmark[method] = dict(seconds=perf_counter() - start, nfev=a.nfev)
summary["solver_benchmark"] = benchmark
(out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
config = {
    "classification": summary["classification"],
    "units": {"amount": "nmol", "volume": "L", "time": "h"},
    "organs": [asdict(o) for o in organs],
    "central_volumes_L": {"arterial": 0.3, "venous": 0.4, "lymph": 0.1},
    "molecular_mass_g_mol": 150000,
    "ka_per_h": 0.01,
    "bioavailability": 0.64,
    "baseline_reference_clearance_L_h": 0.013,
    "doses": [asdict(d) for d in doses],
    "sources": {
        "doses_and_F": "EMA Humira sections 4.2 and 5.2; F from single-dose studies",
        "geometry_and_kinetics": "Illustrative assumptions; uncalibrated",
    },
}
(root / "configs/chunk2_exploratory.json").write_text(json.dumps(config, indent=2) + "\n")
# Enumerate assumptions individually for provenance; preserve all existing registry rows.
p = root / "data/metadata/parameter_registry.csv"
with p.open() as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = [r for r in reader if not r["parameter_id"].startswith("C2_")]


def record(key, value, unit, status, source):
    row = dict.fromkeys(fields, "")
    row.update(
        parameter_id="C2_" + key,
        name=key,
        value=value,
        unit=unit,
        species="Illustrative human geometry",
        molecule="generic IgG exploratory adalimumab scenario",
        condition="uncalibrated",
        source=source,
        status=status,
        uncertainty="not quantified",
        intended_use="numerical exploration only",
        human_adalimumab_default="no",
    )
    rows.append(row)


for o in organs:
    for key, value in asdict(o).items():
        if key == "name":
            continue
        record(
            o.name + "_" + key,
            value,
            "L/h"
            if key in ["flow", "lymph", "ps"]
            else "dimensionless"
            if key in ["reflection", "large_fraction", "large_reflection"]
            else "L",
            "explicit_assumption",
            "configs/chunk2_exploratory.json",
        )
for key, value in asdict(models["reference_exploratory"].fc).items():
    unit = (
        "nmol"
        if key == "receptor"
        else "L/(nmol*h)"
        if key == "association"
        else "nmol/L"
        if key in ["endogenous_igg", "endogenous_kd"]
        else "1/h"
    )
    record("FcRn_" + key, value, unit, "explicit_assumption", "docs/fcrn_mechanism.md")
for key, value, unit in [("F", 0.64, "dimensionless"), ("CL", 0.013, "L/h")]:
    record(
        key,
        value,
        unit,
        "regulatory_aggregate_reference",
        "EMA Humira section 5.2; not a fitted whole-body value",
    )
record(
    "molecular_mass", 150000, "g/mol", "explicit_assumption", "Generic illustrative IgG conversion"
)
record("ka", 0.01, "1/h", "explicit_assumption", "Absorption rate not estimated")
for key, value in config["central_volumes_L"].items():
    record("central_" + key, value, "L", "explicit_assumption", "Illustrative geometry")
for name, model in models.items():
    for kind, targets in [("soluble", model.soluble), ("membrane", model.membrane)]:
        for organ, target in targets.items():
            for key, value in asdict(target).items():
                record(
                    name + "_" + organ + "_" + kind + "_" + key,
                    value,
                    "nmol"
                    if key == "baseline"
                    else "L/(nmol*h)"
                    if key == "association"
                    else "1/h",
                    "explicit_hypothesis",
                    "docs/tmdd_mechanism.md",
                )
for key, value in [
    ("colon_PS_multiplier", 3),
    ("colon_flow_multiplier", 1.2),
    ("colon_lymph_multiplier", 0.8),
]:
    record(key, value, "dimensionless", "explicit_hypothesis", "No clinical severity mapping")
with p.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print(
    json.dumps(
        {
            k: {
                s: v
                for s, v in value.items()
                if s in ["wall_seconds", "max_mass_residual_nmol", "minimum_state_nmol"]
            }
            for k, value in summary["models"].items()
        },
        indent=2,
    )
)
