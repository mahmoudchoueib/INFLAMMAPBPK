# Chunk 2 implementation status — 10 November 2026

**Executable mechanisms implemented and numerically verified; biological
parameterisation and independent validation remain incomplete.** No inference or
later chunk has started. The historical Chunk 1 report is retained at
`docs/chunk1_status_historical.md`.

## Implemented

- One-/two-compartment IV and SC baseline models; single/repeated mixed-route
  dosing, exact matrix-exponential references, sampled Cmax/Tmax/AUC, CL, Vss
  and meaningful linear IV terminal half-life.
- Tight/leaky minimal PBPK with explicit lymph and conserved elimination.
  Model A equations checked against the retrieved primary PMC3836053 article.
- Ten-organ whole-body ODEs, serial pulmonary circulation, hepatic portal inputs,
  nonduplicated plasma volumes, interstitial and endosomal states, lymph drainage.
- Stable two-pore convection/diffusion flux and reflection-model comparator.
- FcRn uptake, reversible acidic binding, receptor availability/competition,
  recycling with immediate neutral release, and lysosomal loss.
- Separate soluble and membrane effective TNF binding-site systems with target
  turnover, complex clearance/internalisation and drug stoichiometric accounting.
- SC interstitial depot-to-lymph transit with explicit presystemic loss.
- Regional small-intestine/colon parameter hypotheses, optional experimental
  immunogenicity clearance, conservative validation of parameters and event inputs.
- Six requested mathematical/mechanistic/numerical documents, expanded parameter
  registry, source hashes, reproducible examples and benchmark artifacts.

## Verification

Full suite: **62 passed, 0 failed, 0 skipped**, 6.15 seconds in the recorded final
run. Ruff passed; mypy passed for 25 source files. Tests include analytical
single/repeated IV/SC solutions (including coincident rates), mass conservation,
nonnegativity, pore limits, portal flow direction, fluid balance including lung
filtration, target stoichiometry/turnover, FcRn limiting cases/competition,
repeated events, presystemic-loss and ADA limits, and BDF/Radau tolerance agreement.

Four 56-day exploratory SC scenarios produced amount/concentration CSVs, exposure
metrics and a PNG under `results/chunk2/`. Maximum drug balance residual was
8.57e-10 nmol; sampled states were nonnegative. Recycled flux is excluded from
mass. The independent identical-scenario 48-hour benchmark recorded BDF ~0.43 s
(1015 RHS calls), Radau ~0.99 s (2927 calls); these are machine-specific timings.
See `results/chunk2/summary.json` for actual diagnostics and all scenario inputs.

## Evidence and limitations

Research access in the published configuration now works for the checked sources.
PMC full HTML succeeded after Europe PMC XML returned HTTP 500. Source downloads
and hashes are recorded in `data/metadata/chunk2_sources.json`. Minimal PBPK
structure and selected physiological assignments are source-backed. EMA Humira
sections 4.2/5.2 supply the adult Crohn's dosing example and aggregate PK reference
values. Registry entries distinguish source assignments, regulatory averages,
unfitted choices and hypotheses.

**The whole-body organ values and FcRn/TNF/disease rates remain illustrative
assumptions, not an adequate human parameter database.** No clinical calibration,
patient-level tissue validation or novel improvement in IBD prediction is claimed.
The full prior-art review and other starting references remain unresolved.
Effective target stoichiometry does not capture molecular multivalent TNF binding.
FcRn competition/release are reduced approximations; immunogenicity is a lumped
experimental clearance. Intestinal tissue is regional aggregate, without an
unsupported separate ileal or microscopic inflamed-tissue subregion. No clinical
severity, albumin or transcript-to-permeability function is assigned.

Outputs are free compartment concentrations, not biopsy homogenate observations.
Further work requires externally supported human physiology/molecule parameters,
assay-specific observation models, calibration/validation datasets, a completed
novelty audit and identifiability analysis before elaborate inference.

The pre-existing Kaleido static-export limitation is unchanged; examples use
Matplotlib. No package installation, environment-draft edits, reapplication of
previous settings or publication occurred in Chunk 2. Earlier uncommitted project
files were preserved; no commits or pushes were made.

## Reproduce

```bash
cd /workspace/INFLAMMAPBPK
source scripts/environment.sh
pytest -q
ruff check src tests scripts
mypy src
python scripts/run_reference_simulations.py
```

The final command regenerates ignored numerical artifacts, the explicit example
configuration and C2 parameter-registry entries. Source downloads are retained
locally; snapshot/licence and independent-validation limits from Chunk 1 still
apply to the mouse 7E3 comparator.
