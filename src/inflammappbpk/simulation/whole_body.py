"""Conservative antibody PBPK with pulmonary series and explicit hepatic portal return."""

import numpy as np

from inflammappbpk.fcrn.mechanism import FcRn
from inflammappbpk.physiology.whole_body import illustrative_organs
from inflammappbpk.tmdd.mechanism import Target
from inflammappbpk.transport.pores import pore_flux, reflection_flux


class WholeBody:
    def __init__(
        self,
        organs=None,
        *,
        fcrn=None,
        soluble=None,
        membrane=None,
        clearance=0.0,
        ka=0.01,
        bioavailability=0.64,
        ada_clearance=0.0,
        transport="two_pore",
    ):
        self.organs = tuple(illustrative_organs() if organs is None else organs)
        names = [o.name for o in self.organs]
        if len(set(names)) != len(names) or "lung" not in names or "liver" not in names:
            raise ValueError("Unique organs including lung and liver required")
        if transport not in {"two_pore", "reflection"}:
            raise ValueError("Unknown transport model")
        if not np.isfinite([clearance, ka, bioavailability, ada_clearance]).all():
            raise ValueError("Finite rates required")
        if min(clearance, ka, ada_clearance) < 0 or not 0 <= bioavailability <= 1:
            raise ValueError("Invalid elimination or absorption")
        self.clearance, self.ka, self.F = clearance, ka, bioavailability
        self.ada_clearance = ada_clearance
        self.transport = transport
        self.fc = FcRn() if fcrn is None else fcrn
        self.soluble = dict(soluble or {})
        self.membrane = dict(membrane or {})
        if (set(self.soluble) | set(self.membrane)) - set(names):
            raise ValueError("Target assigned to unknown organ")
        self.va, self.vv, self.vl = 0.3, 0.4, 0.1
        self.names = ["arterial", "venous", "lymph", "depot", "eliminated", "recycled_total"]
        self.index = {}
        for o in self.organs:
            self.index[o.name] = len(self.names)
            self.names += [
                f"{o.name}.{s}"
                for s in [
                    "vascular",
                    "interstitial",
                    "endosomal",
                    "fcrn_bound",
                    "soluble_target",
                    "soluble_complex",
                    "membrane_target",
                    "membrane_complex",
                ]
            ]
        self.iv_index, self.sc_index = 1, 3
        self.drug_indices = [0, 1, 2, 3]
        for j in self.index.values():
            self.drug_indices += [j, j + 1, j + 2, j + 3, j + 5, j + 7]

    def initial(self):
        y = np.zeros(len(self.names))
        for name, j in self.index.items():
            y[j + 4] = self.soluble.get(name, Target()).baseline
            y[j + 6] = self.membrane.get(name, Target()).baseline
        return y

    def drug_total(self, state):
        return np.asarray(state)[self.drug_indices].sum(axis=0)

    def plasma_volume(self):
        return self.va + self.vv + sum(o.vascular for o in self.organs)

    def rhs(self, time, y):
        d = np.zeros_like(y)
        ca, cv = y[0] / self.va, y[1] / self.vv
        systemic = sum(o.flow for o in self.organs if o.name != "lung")
        lung = next(o for o in self.organs if o.name == "lung")
        pulmonary = systemic + lung.lymph
        jlung = self.index["lung"]
        # Venous -> lung -> arterial; pulmonary lymph returns via venous node.
        d[1] -= pulmonary * cv
        d[jlung] += pulmonary * cv - systemic * y[jlung] / lung.vascular
        d[0] += systemic * y[jlung] / lung.vascular - systemic * ca
        portal = {"spleen", "small_intestine", "colon"}
        for o in self.organs:
            j = self.index[o.name]
            if o.name != "lung":
                inflow = o.flow * ca
                qout = o.flow - o.lymph
                if o.name == "liver":
                    qout += sum(p.flow - p.lymph for p in self.organs if p.name in portal)
                outflow = qout * y[j] / o.vascular
                d[j] += inflow - outflow
                d[self.index["liver"] if o.name in portal else 1] += outflow
            cv_i, ci = y[j] / o.vascular, y[j + 1] / o.interstitial
            if self.transport == "two_pore":
                flux = sum(
                    pore_flux(cv_i, ci, o.ps * w, o.lymph * w, sigma)
                    for w, sigma in [
                        (1 - o.large_fraction, o.reflection),
                        (o.large_fraction, o.large_reflection),
                    ]
                )
            else:
                flux = reflection_flux(cv_i, ci, o.ps, o.lymph, o.reflection)
            d[j] -= flux
            d[j + 1] += flux - o.lymph * ci
            d[2] += o.lymph * ci
            uptake_v, uptake_i = self.fc.uptake * y[j], self.fc.uptake * y[j + 1]
            bind, recycle, degrade = self.fc.rates(y[j + 2], y[j + 3], o.endosomal)
            d[j] += -uptake_v + recycle
            d[j + 1] -= uptake_i
            d[j + 2] += uptake_v + uptake_i - bind - degrade
            d[j + 3] += bind - recycle
            d[4] += degrade
            d[5] += recycle  # cumulative flux diagnostic; exclude from drug inventory
            for offset, parameters in [(4, self.soluble), (6, self.membrane)]:
                target = parameters.get(o.name, Target())
                binding, turnover, removal = target.rates(ci, y[j + offset], y[j + offset + 1])
                d[j + 1] -= binding
                d[j + offset] += turnover - binding
                d[j + offset + 1] += binding - removal
                d[4] += removal
        lymph_flow = sum(o.lymph for o in self.organs)
        returning = lymph_flow * y[2] / self.vl
        d[2] -= returning
        d[1] += returning
        absorption = self.ka * y[3]
        d[3] -= absorption
        d[2] += self.F * absorption
        loss = (self.clearance + self.ada_clearance) * cv
        d[1] -= loss
        d[4] += loss + (1 - self.F) * absorption
        return d
