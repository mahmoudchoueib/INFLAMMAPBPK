> Chunk 2 update (2026-11-10): published research-domain access now applies.
> PMC3836053 full HTML and EMA Humira product information were retrieved and
> inspected; see data/metadata/chunk2_sources.json. The remainder of this file
> records the earlier Chunk 1 audit. Other references/data have not been fully
> re-reviewed, and human tissue validation remains unresolved.

# Literature review: preliminary, access blocked

Audit date: 10 November 2026. This is an evidence-limited review and a reproducible
search protocol, not a completed systematic review. The eleven starting identifiers
are recorded in `literature_registry.csv`; their supplied descriptions remain
unverified. No assumption is made that an identifier resolves to the stated paper,
that a recent citation is published, or that a PMC identifier grants reuse rights.

## Executed retrievals

The managed proxy rejected Europe PMC, PMC, ClinicalTrials.gov, EMA, FDA, UniProt,
Human Protein Atlas, GEO, and the other research destinations during this run.
`data/metadata/retrieval_log.csv` records individual attempts. No primary full text,
supplement, TAURUS accession, or patient-level anti-TNF dataset was retrieved from
those hosts. Configuration additions are saved but do not establish live access.

Two complete OSP evaluation reports were retrieved from an immutable library
commit `07a71b3e025879db5cc46feca1d262cc786ed0f6`:

1. *Building and evaluation of a PBPK model for antibody 7E3 in wild-type and FcRn
   knockout mice*, version 1.0-OSP12.3, sections 2.1–2.3 and 5.
2. *Building and evaluation of a PBPK model for antibody MEDI-524 in cynomolgus
   monkeys*, version 1.0-OSP12.3, sections 2.1–2.3 and 5.

Both explicitly describe two-pore extravasation, lymph flow, endosomal clearance,
and FcRn protection/recycling in the generic whole-body large-molecule PK-Sim
platform. The reports cite Niederalt et al. (2018), *A generic whole body
physiologically based pharmacokinetic model for therapeutic proteins in PK-Sim*,
DOI `10.1007/s10928-017-9559-4`. This bibliographic information is verified only
against the downloaded report, not independently against the primary publication.

The 7E3 report describes plasma and tissue profiles after an 8 mg/kg IV bolus in
mice, with radiolabelled antibody measured from sacrificed animals. It notes
residual-blood correction for the brain dataset. Its discussion acknowledges
misfit in several organs, including early gut concentrations. These are existing
model-development data, so reuse cannot establish independent platform validation.
The MEDI-524 report describes 30 mg/kg IV data in cynomolgus monkeys; it provides a
FcRn comparator without an endogenous target. Neither is a human IBD anti-TNF
tissue dataset.

## Search protocol to execute after access is enabled

`configs/sources.json` contains exact Europe PMC queries S01–S12 covering whole-body
and minimal antibody PBPK, two-pore transport, FcRn/endosomal trafficking, anti-TNF
PK and tissue measurements, IBD vascular physiology, TNF turnover/binding, intestinal
single-cell data, Bayesian/hybrid PBPK, and newer literature through 2026-11-10.
The initial bounded retrieval collects up to 100 records per query. A full review
must paginate all results, deduplicate DOI/PMID, document title/abstract and
full-text exclusions, search reference lists, and cross-check Crossref/PubMed and
publisher correction/retraction status. The present search registry reports zero
screened records; an access failure is not a zero-hit search.

Include original mechanistic studies, evaluable PK/tissue cohorts, physiology
measurements, and identifiable datasets. Separate reviews from primary evidence.
Extract species, drug, disease/site/activity, route/regimen, assay and analyte,
sampling times, tissue processing, model states, parameter provenance, calibration
data, independent validation, code/data access, supplements, licences, uncertainty,
and conflicts. Do not infer free interstitial exposure from biopsy homogenates.

Priority full-text questions remain unresolved for all supplied references,
including ATLAS, TAURUS, both population-PK citations, and the platform comparison.
After metadata resolution, verify each label and article before interpreting it.
Use legitimate OA full-text/supplement endpoints; record restricted or missing
materials rather than substituting unsupported details.
