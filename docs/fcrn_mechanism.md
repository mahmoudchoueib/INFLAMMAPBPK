# FcRn mechanism

Each organ has endosomal unbound E and bound B (nmol). Uptake u (h^-1) transfers
vascular/interstitial drug to E. Total FcRn binding sites Rtot are fixed nmol;
free sites in the presence of a constant endogenous-IgG reservoir G are
Rfree=(Rtot-B)/(1+G/KdG). Association b=kon E/Ve Rfree-koff B. E loses b and
lysosomal degradation kdeg E; B gains b and loses recycling krec B. Recycled drug
returns to the same organ's vascular plasma. Receptor sites become available
again. Bounds B in [0,Rtot] follow from the ODE; they are not imposed by clipping.

Association/dissociation constants describe acidic endosomal conditions. Release
at neutral plasma pH is represented by an instantaneous-release limit, not an
explicit pH trajectory or fitted dual-pH affinity model. Endogenous competition is
a rapid-equilibrium reservoir approximation, not a dynamic IgG turnover model;
G=0 disables it. No arbitrary RNA-to-recycling conversion is used.

All default rates, receptor amounts and endosomal volumes are **hypothetical**;
mouse/cynomolgus values from Chunk 1 are not used as human adalimumab defaults.
The 7E3/ MEDI-524 OSP reports support FcRn salvage as established architecture,
not these numerical human parameters. Units: kon L/(nmol h), koff/krec/kdeg/u
h^-1, E/B/Rtot nmol, G/KdG nmol/L. A generic observation of FcRn sensitivity is
not experimental validation. Tests cover zero receptors, zero recycling, higher
recycling, higher degradation, receptor availability, endogenous competition,
drug conservation and occupancy bounds.
