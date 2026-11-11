# TNF target disposition and optional immunogenicity

Soluble TNF binding sites and membrane-associated binding sites have separate
Target parameter objects, free amounts T and complexes X per organ. Drug D is
free interstitial concentration. For either target form:

```
b = kon D T - koff X
T' = kturn (T0-T) - b
X' = b - kcomplex X
free drug amount' -= b; eliminated drug' += kcomplex X
```

Soluble kcomplex is clearance/degradation of soluble complex; membrane kcomplex
is internalisation and loss of bound drug/target. They are separate parameters,
not an assumed identity. Internalised drug enters the elimination accumulator;
endosomal rescue of target complexes is not currently modelled. Free target
turnover supplies kturn T0 and removes kturn T. Drug in complexes is counted once.
Without complex removal or turnover, T+X is conserved. With turnover, there is a
specified source/sink, so target conservation is not incorrectly demanded.

Units: site and complex amounts nmol, kon L/(nmol h), other rates h^-1. This is an
**effective 1:1 binding-site approximation**. It is not a molecular multivalent
model of bivalent antibody and trimeric TNF. Site scaling and TNF stoichiometry
need primary evidence; no unsupported TNF kinetic value is assigned a published
status. Defaults have T0=0 (mechanism inactive); example nonzero target levels
and kinetics are explicit hypotheses requiring calibration and identifiability
analysis. Use of the word TNF does not establish clinical predictive performance.

The separate Immunogenicity interface defines an optional additional free-plasma
clearance (L/h), accepted as WholeBody's ada_clearance. It is zero by default and
preserves drug balance by accumulating loss. This experimental lumped mechanism
has no explicit ADA titre, seroconversion or immune-complex states. It must not
be interpreted as established patient-specific immunogenicity kinetics.
