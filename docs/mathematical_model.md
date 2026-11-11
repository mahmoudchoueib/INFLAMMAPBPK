# Executable model specification

Canonical units: amounts nmol, time h, volumes L, concentrations nmol/L, plasma
flows and permeability–surface products L/h. Rates are h^-1, association constants
L/(nmol h). Public float APIs require these units; dose conversion in the example
uses Pint. No clinical use, calibrated prediction or independent validation is claimed.

## Baselines (`compartments/baseline.py`)

For central X, peripheral Y, SC depot S, elimination accumulator Z:

```
X' = -(CL+Q) X/Vc + Q Y/Vp + F ka S
Y' = Q X/Vc - Q Y/Vp
S' = -ka S
Z' = CL X/Vc + (1-F) ka S
```

Q=0,Vp=0 gives the one-compartment model. Single/repeated IV or SC events add
amounts to X or S. Matrix exponentials with superposition are exact reference
solutions, including coincident rates and doses. For one-compartment IV,
C=D/Vc exp(-CL t/Vc), AUC_inf=D/CL. `descriptors()` reports input CL, Vss=Vc+Vp
(for an exchanging peripheral space), and ln(2)/the slow IV disposition rate.
SC flip-flop absorption can change an observed terminal slope. Exposure metrics
are sampled Cmax/Tmax and trapezoidal finite-window AUC, not extrapolated NCA.
No single nonlinear whole-body half-life is asserted.

## Minimal PBPK (`compartments/minimal.py`)

The four amounts P,T,G,N are plasma, tight interstitium, leaky interstitium and
lymph. Write Cp=P/Vp, Ct=T/Vt, Cg=G/Vg, Cn=N/Vn.

```
Jt=L1(1-sigma1)Cp; Jg=L2(1-sigma2)Cp
Rt=L1(1-sigmaL)Ct; Rg=L2(1-sigmaL)Cg
P'=-Jt-Jg+(L1+L2)Cn-CL Cp
T'=Jt-Rt; G'=Jg-Rg
N'=Rt+Rg-(L1+L2)Cn+F ka S
S'=-ka S; Z'=CL Cp+(1-F)ka S
```

These are amount-form Model A equations (1)–(4) of Cao, Balthasar and Jusko,
*Second-generation minimal physiologically-based pharmacokinetic model for
monoclonal antibodies*, 2013, DOI 10.1007/s10928-013-9332-2, PMC3836053.
The PMC full text was retrieved and equations read directly in Chunk 2. SC depot
input is an extension. Default ISF 15.6 L, 65/35 volume split, total lymph
2.9 L/day and 33/67 flow split follow the article's physiological assignments,
using accessibility fraction 1 as an explicit assumption. The default small lymph
volume (0.1 L) is a numerical exploration choice departing from the article's
blood-volume assumption; reflection coefficients and CL remain unfitted choices.
This is a structural implementation, not reproduction of its fitted datasets.

## Whole-body circulation (`simulation/whole_body.py`)

State vector: arterial, venous, lymph-node and depot drug; eliminated amount Z;
cumulative recycled diagnostic R; and eight states per organ: vascular V,
interstitial I, unbound endosomal E, FcRn-bound B, soluble free target Ts,
soluble complex Xs, membrane free target Tm and membrane complex Xm.
Only V,I,E,B,Xs,Xm contain drug. Target sites do not enter drug inventory.
R is a flux integral and must not be added to drug mass.

Qsys=sum systemic arterial organ flows; Qpul=Qsys+Llung. Venous blood enters lung,
lung effluent enters arterial plasma. Spleen, small-intestine and colon venous
flows enter liver; hepatic arterial flow is separate. Other organs return to veins.
For a nonhepatic systemic organ, Qout=Qin-Li. Hepatic outflow additionally includes
all portal inflows (Qportal-Lportal). Lung outflow is Qsys. Thus arterial, portal,
pulmonary and lymph volume fluxes balance without a second circulating pool.

For each organ with incoming and outgoing advective drug flux Fin,Fout:

```
V' = Fin-Fout-J - u V + krec B
I' = J-Li Ci - u I - bs-bm
E' = u(V+I)-bFc-kdeg E
B' = bFc-krec B
Tj' = kturn(T0j-Tj)-bj
Xj' = bj-kcomplex,j Xj                    (j=soluble, membrane)
Z' += kdeg E + sum_j kcomplex,j Xj
R' += krec B
```

Arterial derivative is Qsys(Clung-Carterial); venous derivative is total systemic
return plus lymph-node return minus Qpul Cvenous minus residual CL Cvenous.
Node'=sum Li Ci - sum Li Cnode + F ka S. SC depot'= -ka S; Z also accumulates
presystemic loss (1-F)ka S and optional residual/ADA clearance. The pulmonary
vascular equation uses Qpul Cvenous-Qsys Clung plus its local exchange terms.
No state clipping is used. Every transport, uptake or binding loss has an equal
gain, or an explicit elimination entry. Consequently Mdrug+Z equals administered
drug for zero initial drug, including all repeated events.

Residual clearance defaults to zero in WholeBody: aggregate clinical CL must not
be added on top of FcRn-mediated catabolism as if it were an independent pathway.
A user-supplied residual CL needs separate evidence or joint calibration.

## Final-platform interfaces and reporting limits

The exploratory body-weight transformation uses s=weight/70 kg: volumes and site
amounts scale by s; flows/PS scale by s^0.75. Central and organ vascular volumes
scale together. This is a user-visible hypothesis, not a fitted biological law.
It is independent of clinical diagnosis/severity and is constrained by the same
flow and mass checks as the base model.

Baseline descriptor QA now handles zero clearance explicitly: terminal elimination
half-life is infinite, even if intercompartmental redistribution continues. A
peripheral volume disconnected by Q=0 is excluded from accessible Vss. This changes
reporting of limiting cases, not the underlying baseline ODE or prior positive-CL
fit results. Regression tests cover both cases.
