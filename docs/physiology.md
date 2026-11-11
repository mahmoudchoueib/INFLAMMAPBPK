# Physiology and transport

`illustrative_organs()` enumerates lung, liver, kidney, spleen, muscle, skin,
adipose, small intestine, colon and remaining tissue. **All organ geometry,
flow, PS, endosomal volumes and pore allocations are explicit illustrative
assumptions**, recorded individually in the parameter registry and
`configs/chunk2_exploratory.json`. No verified human organ parameter set or IBD
population physiology was available in Chunk 1. These defaults are executable
numerical fixtures, not a defensible calibrated human physiology database.

Flows are plasma flows (L/h), not whole-blood flows. A whole-blood source must be
converted with its measured hematocrit before use; no red-cell drug pool is
modelled. Arterial 0.3 L + venous 0.4 L + organ vascular 2.3 L = 3 L plasma.
Systemic arterial flows sum to 210 L/h. Portal flows are not additional arterial
flows. Interstitial volumes exclude vascular plasma and endosomal spaces. The
lymph node is a separate 0.1 L fluid space, not additional circulating plasma.
`WholeBody.plasma_volume()` reports the vascular total.

## Two-pore transport

For each of small/large pores:

```
v=Jv(1-sigma), Pe=v/PS
Js=v (Cv-Ci exp(-Pe))/(1-exp(-Pe))
```

PS and Jv have units L/h; concentrations are nmol/L, so Js is nmol/h. At zero
filtration this tends to PS(Cv-Ci); at PS=0 it gives upstream convection v Cv;
at equal concentrations it gives v C. `expm1` and a small-Pe expansion avoid
cancellation and handle impermeable limits. Negative flux permits back diffusion.
Only nonnegative filtration is currently supported. Each organ partitions total
PS and filtration by its large-pore fraction; both pore fractions sum to one.
The reflection comparator is PS(Cv-Ci)+Jv(1-sigma)Cv, an upstream approximation.

This is a constant-flow convection/diffusion implementation. It does not implement
Starling pressure laws or reproduce all pore hindrance/radius equations of an OSP
platform. Pressure values are not silently treated as flows. Measured organ PS,
reflection and filtration (or an independently validated pressure model) must be
supplied for biological prediction. The retrieved OSP 7E3 report section 2.1
establishes existing whole-body two-pore/FcRn architecture; exact equivalence to
Niederalt et al. is not claimed. Primary source for the minimal model is
PMC3836053, equations 1–7 (see mathematical_model.md).
