> Chunk 2 update (2026-11-10): published research-domain access now applies.
> PMC3836053 full HTML and EMA Humira product information were retrieved and
> inspected; see data/metadata/chunk2_sources.json. The remainder of this file
> records the earlier Chunk 1 audit. Other references/data have not been fully
> re-reviewed, and human tissue validation remains unresolved.

# Data availability and feasibility

## Retrieved and inspected

The OSP library commit and the 7E3 source snapshot are pinned in `configs/sources.json`.
The source snapshot at `12f886989585472e26d5857364047ff2d68abbcd` contains **24 aggregate
profiles and 174 concentration observations** across plasma and nine tissue organs
(including gut), in wild-type and FcRn-knockout mice. The extraction summary records
the actual gut count and output checksum. The raw snapshot retains all source
metadata; the CSV preserves original values/units and adds hours and nmol/L.
Reported zero standard deviations are flagged and retained; they are not treated
as exact measurements or replaced by invented uncertainties.

The report identifies radiolabelled 7E3, an 8 mg/kg IV bolus and three sacrificed
mice per tissue time point for the cited tissue experiment. These statements come
from the OSP report, not an independent inspection of the original Garg papers.
The snapshot encodes aggregate observed-data profiles, not patient-level or
animal-level records. The reported tissue signal is not established to be free
interstitial intact antibody; blood correction is explicitly described for brain,
not universally for every tissue. Original assay and conversion methods require
primary-source verification. Reusing data already used for OSP model development
does not validate that platform independently.

Two PK-Sim project containers and two evaluation reports were also downloaded
(about 3.3 MB combined before the small source snapshot/plan). SQLite inspection
confirmed the project containers include observed-data repositories; the portable
source JSON is used for extraction. PK-Sim itself has not been installed or run.
The 7E3 source README states GPLv2 for model code. This does not settle licences
for third-party measurements or reports; confirm rights before redistribution.
Raw and processed artifacts are ignored by Git and retained locally for review.

## Priority human data: not yet established

| Requirement | Present state | Scientific implication |
|---|---|---|
| Adalimumab serum profiles, IV PK and SC bioavailability | Research endpoints blocked | No numerical adalimumab calibration dataset verified |
| ATLAS/other matched serum-biopsy data | Supplied identifiers unverified | Primary tissue outcome is not presently evaluable |
| Disease activity, dose and sample timing | Not retrieved for human tissue candidates | Cannot identify disease-physiology effects |
| Infliximab external cohort | Endpoint access blocked | Cross-drug validation cannot yet be specified numerically |
| TNF on/off kinetics and turnover; human FcRn | Primary evidence unverified | No molecule-specific numbers assigned |
| TAURUS processed expression and metadata | Article/data statement blocked | Accession, processed file sizes and licence unknown; no raw reads downloaded |
| ClinicalTrials.gov / regulatory labels | Requests blocked | Registry records and aggregate label values are not individual-level data |
| UniProt / ChEMBL / PDB / HPA / Atlas / GEO | Requests logged; blocked | An annotation, structure or search page is not a PK calibration dataset |

## Decision gates

For a human tissue study, obtain concentrations and units, intact/free/total assay
definition, biopsy handling/dilution and wet/dry mass, sample time relative to a
fully known regimen, paired serum timing, segment, disease activity and covariates,
and inclusion/selection criteria. Record subject IDs only if legitimately provided;
never reconstruct individual data from aggregate means. Missingness, below-LLOQ
values and anti-drug-antibody interference need explicit handling. Use censored
likelihoods where supported and separate assay heterogeneity from biological noise.

Human tissue validation is a conditional goal. If usable observations cannot be
obtained, a defensible alternative is a numerical reproduction/benchmark using
public nonhuman tissue data, serum-only external evaluation when available, and
uncertainty/identifiability analysis of hypothetical IBD physiology. Such a study
cannot establish improved human intestinal exposure prediction. Do not tune
permeability or TNF turnover against the same tissue observations used to evaluate
that claim. Plan falsification and information-content analysis before adding
weakly identified mechanisms.

## Resume

Review/save research-domain additions in cloud environment settings. Refresh
runtime status and retry a fresh Europe PMC request. Then run acquisition with
`--scope research`, verify identities/rights, paginate searches, review full texts
and supplements, inspect file sizes, acquire only justified processed data, and
update the registries. The acquisition script exiting successfully means its
attempt log was written; inspect individual statuses before claiming retrieval.
