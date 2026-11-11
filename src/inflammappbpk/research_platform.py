"""Validated configuration and shared exploratory simulation service for UI, CLI and QA."""

import hashlib
import json
from dataclasses import asdict, dataclass, replace

import numpy as np
import pandas as pd

from inflammappbpk.compartments import exposure
from inflammappbpk.fcrn import FcRn
from inflammappbpk.physiology import disease_region, illustrative_organs
from inflammappbpk.simulation import Dose, WholeBody, simulate
from inflammappbpk.tmdd import Target
from inflammappbpk.units import Q_


@dataclass(frozen=True)
class ParameterSpec:
    label: str
    unit: str
    default: float
    minimum: float
    maximum: float
    source: str
    evidence: str


PARAMETERS = {
    "weight_kg": ParameterSpec(
        "Body weight", "kg", 70, 40, 150, "docs/physiology.md", "hypothetical adult scaling range"
    ),
    "dose_mg": ParameterSpec(
        "Absolute dose",
        "mg",
        40,
        0,
        500,
        "EMA Humira 5.2 single-dose studies",
        "40 mg source-backed; exploration range assumed",
    ),
    "dose_mg_kg": ParameterSpec(
        "Weight-normalised dose",
        "mg/kg",
        5,
        0.1,
        10,
        "User-defined research scenario",
        "assumed; not a prescribed regimen",
    ),
    "interval_days": ParameterSpec(
        "Dose interval",
        "day",
        14,
        1,
        56,
        "EMA Humira 4.2 maintenance interval",
        "14-day example; range not validated",
    ),
    "dose_count": ParameterSpec(
        "Number of administrations",
        "count",
        1,
        1,
        8,
        "Piecewise bolus implementation",
        "computational limit; integer",
    ),
    "horizon_days": ParameterSpec(
        "Observation horizon", "day", 28, 1, 112, "Research scenario", "computational range"
    ),
    "molecular_mass": ParameterSpec(
        "Molecular mass for dose conversion",
        "g/mol",
        150000,
        100000,
        200000,
        "Generic IgG assumption",
        "not a verified drug-specific mass",
    ),
    "ka": ParameterSpec(
        "SC absorption rate",
        "1/h",
        0.01,
        0.001,
        0.05,
        "Chunk 2 exploratory fixture",
        "assumed; not fitted",
    ),
    "bioavailability": ParameterSpec(
        "SC bioavailability",
        "fraction",
        0.64,
        0,
        1,
        "EMA Humira 5.2, single 40 mg doses",
        "regulatory average; population transfer uncertain",
    ),
    "permeability": ParameterSpec(
        "Regional PS multiplier",
        "fold",
        1,
        0.5,
        4,
        "docs/intestinal_disease_model.md",
        "hypothesis; no clinical-score mapping",
    ),
    "flow": ParameterSpec(
        "Regional arterial-flow multiplier",
        "fold",
        1,
        0.5,
        1.5,
        "docs/intestinal_disease_model.md",
        "hypothesis; total cardiac flow changes",
    ),
    "lymph": ParameterSpec(
        "Regional lymph-flow multiplier",
        "fold",
        1,
        0,
        2,
        "docs/intestinal_disease_model.md",
        "hypothesis; not measured IBD physiology",
    ),
    "uptake": ParameterSpec(
        "Endosomal uptake rate", "1/h", 0.001, 0.0001, 0.01, "docs/fcrn_mechanism.md", "assumed"
    ),
    "recycling": ParameterSpec(
        "FcRn-bound recycling rate", "1/h", 0.2, 0, 1, "docs/fcrn_mechanism.md", "assumed"
    ),
    "degradation": ParameterSpec(
        "Unprotected endosomal degradation", "1/h", 0.5, 0.1, 2, "docs/fcrn_mechanism.md", "assumed"
    ),
    "receptor": ParameterSpec(
        "FcRn sites per organ at 70 kg",
        "nmol",
        1,
        0,
        10,
        "docs/fcrn_mechanism.md",
        "assumed shared capacity; not human receptor data",
    ),
    "endogenous_igg": ParameterSpec(
        "Endosomal endogenous IgG reservoir",
        "nmol/L",
        0,
        0,
        50000,
        "docs/fcrn_mechanism.md",
        "assumed; zero disables competition",
    ),
    "soluble_target": ParameterSpec(
        "Regional soluble target sites at 70 kg",
        "nmol",
        0,
        0,
        2,
        "docs/tmdd_mechanism.md",
        "assumed; zero disables target",
    ),
    "membrane_target": ParameterSpec(
        "Regional membrane target sites at 70 kg",
        "nmol",
        0,
        0,
        2,
        "docs/tmdd_mechanism.md",
        "assumed; zero disables target",
    ),
    "population_spread_kg": ParameterSpec(
        "Hypothetical weight spread",
        "kg",
        10,
        0,
        30,
        "User-defined three-scenario grid",
        "not a population distribution or confidence interval",
    ),
}


@dataclass(frozen=True)
class Scenario:
    biologic: str = "adalimumab"
    route: str = "sc"
    dose_unit: str = "mg"
    region: str = "colon"
    disease: str = "reference"
    acknowledge_infliximab: bool = False
    weight_kg: float = 70.0
    dose_mg: float = 40.0
    dose_mg_kg: float = 5.0
    interval_days: float = 14.0
    dose_count: int = 1
    horizon_days: float = 28.0
    molecular_mass: float = 150000.0
    ka: float = 0.01
    bioavailability: float = 0.64
    permeability: float = 1.0
    flow: float = 1.0
    lymph: float = 1.0
    uptake: float = 0.001
    recycling: float = 0.2
    degradation: float = 0.5
    receptor: float = 1.0
    endogenous_igg: float = 0.0
    soluble_target: float = 0.0
    membrane_target: float = 0.0

    def __post_init__(self):
        for key, value in asdict(self).items():
            if key in PARAMETERS:
                spec = PARAMETERS[key]
                if not np.isfinite(value) or not spec.minimum <= value <= spec.maximum:
                    raise ValueError(
                        f"{spec.label} outside exploration bounds "
                        f"[{spec.minimum}, {spec.maximum}] {spec.unit}"
                    )
        if isinstance(self.dose_count, bool) or int(self.dose_count) != self.dose_count:
            raise ValueError("Number of administrations must be an integer")
        if self.biologic not in {"adalimumab", "infliximab"} or self.route not in {"iv", "sc"}:
            raise ValueError("Unknown biologic or route")
        if self.dose_unit not in {"mg", "mg/kg"} or self.region not in {"colon", "small_intestine"}:
            raise ValueError("Unknown unit or region")
        if self.disease not in {"reference", "regional_hypothesis"}:
            raise ValueError("Unknown disease scenario")
        if self.biologic == "infliximab" and (
            self.route != "iv" or not self.acknowledge_infliximab
        ):
            raise ValueError(
                "Infliximab is only an acknowledged hypothetical IV scaffold; no validated kinetics"
            )
        if (self.dose_count - 1) * self.interval_days > self.horizon_days:
            raise ValueError("Last administration is outside observation horizon")
        if self.disease == "reference" and (self.permeability, self.flow, self.lymph) != (
            1.0,
            1.0,
            1.0,
        ):
            raise ValueError("Regional modifiers require an explicit hypothesis scenario")

    def payload(self):
        return asdict(self)

    def fingerprint(self):
        return hashlib.sha256(json.dumps(self.payload(), sort_keys=True).encode()).hexdigest()

    def dose_amount_mg(self):
        return self.dose_mg if self.dose_unit == "mg" else self.dose_mg_kg * self.weight_kg


def build_model(config: Scenario):
    scale = config.weight_kg / 70.0
    organs = tuple(
        replace(
            o,
            vascular=o.vascular * scale,
            interstitial=o.interstitial * scale,
            endosomal=o.endosomal * scale,
            flow=o.flow * scale**0.75,
            lymph=o.lymph * scale**0.75,
            ps=o.ps * scale**0.75,
        )
        for o in illustrative_organs()
    )
    organs = disease_region(
        organs,
        config.region,
        permeability=config.permeability,
        flow=config.flow,
        lymph=config.lymph,
    )
    fc = FcRn(
        uptake=config.uptake,
        recycling=config.recycling,
        degradation=config.degradation,
        receptor=config.receptor * scale,
        endogenous_igg=config.endogenous_igg,
    )
    model = WholeBody(
        organs,
        fcrn=fc,
        ka=config.ka,
        bioavailability=config.bioavailability,
        soluble={config.region: Target(baseline=config.soluble_target * scale)},
        membrane={config.region: Target(baseline=config.membrane_target * scale, complex_loss=0.3)},
    )
    model.va *= scale
    model.vv *= scale
    model.vl *= scale
    return model


def physiology_table(config: Scenario):
    model = build_model(config)
    systemic = sum(o.flow for o in model.organs if o.name != "lung")
    rows = []
    portal = {"spleen", "small_intestine", "colon"}
    for o in model.organs:
        arterial = systemic + o.lymph if o.name == "lung" else o.flow
        portal_in = (
            sum(p.flow - p.lymph for p in model.organs if p.name in portal)
            if o.name == "liver"
            else 0.0
        )
        rows.append(
            dict(
                organ=o.name,
                arterial_or_pulmonary_inflow_L_h=arterial,
                portal_inflow_L_h=portal_in,
                vascular_L=o.vascular,
                interstitial_L=o.interstitial,
                lymph_L_h=o.lymph,
                PS_L_h=o.ps,
                provenance="hypothetical 70-kg fixture and allometric scaling",
            )
        )
    return pd.DataFrame(rows)


def run_scenario(config: Scenario):
    model = build_model(config)
    amount: float = (
        (Q_(config.dose_amount_mg(), "mg") / Q_(config.molecular_mass, "g/mol"))
        .to("nmol")
        .magnitude
    )
    doses = [
        Dose(i * config.interval_days * 24, amount, config.route) for i in range(config.dose_count)
    ]
    time = np.unique(np.r_[np.linspace(0, config.horizon_days * 24, 241), [d.time for d in doses]])
    result = simulate(model, time, doses)
    administered = np.array([sum(d.amount for d in doses if d.time <= t) for t in time])
    total = model.drug_total(result.amounts)
    mass_error = total + result.state("eliminated") - administered
    if result.amounts.min() < -1e-7 or abs(mass_error).max() > 1e-6 * max(1.0, administered.max()):
        raise RuntimeError("Numerical nonnegativity or mass-balance criterion failed")
    curves = pd.DataFrame(
        {
            "time_h": time,
            "time_day": time / 24,
            "plasma_nmol_L": result.state("venous") / model.vv,
            "drug_remaining_nmol": total,
            "eliminated_nmol": result.state("eliminated"),
            "recycled_flux_integral_nmol": result.state("recycled_total"),
            "administered_nmol": administered,
            "mass_error_nmol": mass_error,
        }
    )
    for organ in model.organs:
        name = organ.name
        curves[name + "_free_interstitial_nmol_L"] = (
            result.state(name + ".interstitial") / organ.interstitial
        )
    for species in ["soluble", "membrane"]:
        bound = result.state(config.region + "." + species + "_complex")
        denominator = bound + result.state(config.region + "." + species + "_target")
        curves[species + "_target_occupancy"] = np.divide(
            bound, denominator, out=np.full_like(bound, np.nan), where=denominator > 0
        )
    curves["endosomal_unbound_nmol"] = sum(
        result.state(o.name + ".endosomal") for o in model.organs
    )
    curves["fcrn_bound_nmol"] = sum(result.state(o.name + ".fcrn_bound") for o in model.organs)
    states = pd.DataFrame(result.amounts.T, columns=result.names)
    states.insert(0, "time_h", time)
    summary = exposure(time, curves.plasma_nmol_L)
    summary.update(
        classification="UNCALIBRATED EXPLORATORY",
        configuration_sha256=config.fingerprint(),
        max_mass_error_nmol=float(abs(mass_error).max()),
        min_state_nmol=float(result.amounts.min()),
        plasma_volume_L=model.plasma_volume(),
        effective_dose_mg=config.dose_amount_mg(),
        nfev=result.nfev,
        scaling=(
            "Hypothesis: volumes/sites proportional to weight; flows/PS proportional to weight^0.75"
        ),
        intracellular_defaults=(
            "association/dissociation, IgG Kd and target turnover remain Chunk 2 assumptions"
        ),
    )
    return {
        "curves": curves,
        "states": states,
        "summary": summary,
        "configuration": config.payload(),
    }


def parameter_table():
    return pd.DataFrame(
        [
            dict(
                key=k, **asdict(v), range_meaning="exploration guardrails, not validated physiology"
            )
            for k, v in PARAMETERS.items()
        ]
    )
