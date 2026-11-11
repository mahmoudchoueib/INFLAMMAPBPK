# State of the art and evidence boundaries

## Established by retrieved source documents

The downloaded OSP 7E3 and MEDI-524 reports establish that a generic whole-body
protein PBPK platform already combines two-pore transport, lymphatic return,
endosomal degradation, and FcRn salvage. Murine plasma and multiple tissue
profiles, including gut and FcRn-knockout observations, already support this
research area. Source: OSP reports, sections 2.1, 2.2, 3, and 5; hashes in the
retrieval log. Reimplementing these mechanisms is an engineering contribution
until a scientific comparison shows something additional.

## Questions requiring primary-source review

Minimal PBPK is a comparator candidate; its precise state definitions and tissue
groupings must be checked against R02. The scope and validation of the other
platforms (R01, R03–R06) remain unverified. The provided DOI/PMID labels cannot yet
support claims about which platform outperforms another.

Adalimumab/infliximab population PK, subcutaneous absorption/bioavailability,
albumin/inflammation covariates, immunogenicity, fecal loss, target interactions,
intestinal biopsy exposure, and single-cell disease atlases are planned evidence
domains. They are not quantitatively characterised in the retrieved anti-TNF
evidence because no such primary source was accessible in this run.

An RNA expression value cannot directly determine receptor density, receptor
trafficking, TNF turnover, or vascular permeability. A cross-layer mapping needs
protein measurements, cell abundance, explicit scaling uncertainty, and an
out-of-sample test. Bayesian inference quantifies a specified model's uncertainty;
it does not make unidentifiable parameters or a new mechanistic claim identifiable.

## Comparison to build

Compare a literature-derived reference PBPK, an independently constrained IBD
physiology extension, and optional identifiable target/recycling extensions under
the same dosing, calibration data, observation model, and evaluation split. Keep
simple serum-PK and minimal-PBPK baselines when their data requirements permit.
Require reproducible published equations and numerical comparisons before calling
any implementation a reproduction of an existing platform.
