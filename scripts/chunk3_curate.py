"""Deterministic curation; missing fields stay missing and animal data never become human data."""

import hashlib
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from inflammappbpk.validation.data import assert_disjoint, missingness

ROOT = Path(__file__).resolve().parents[1]


def curate(verify_sources=False):
    raw = ROOT / "data/raw/chunk3"
    raw.mkdir(exist_ok=True)
    source_map = {
        "atlas_metadata.json": (
            "c3_25670812",
            (
                "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT"
                "_ID:25670812%20AND%20SRC:MED&format=json&resultType=core"
            ),
        ),
        "yoshihara_metadata.json": (
            "c3_28945638",
            (
                "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT"
                "_ID:28945638%20AND%20SRC:MED&format=json&resultType=core"
            ),
        ),
        "calibration_population_article.html": (
            "c3_pop.html",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC13675741/",
        ),
        "validation_M923_article.html": (
            "c3_PMC5817835.html",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5817835/",
        ),
        "candidate_ABP501_article.html": (
            "c3_abp.html",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC13140478/",
        ),
        "candidate_early_ABP501_article.html": (
            "c3_PMC5445997.html",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5445997/",
        ),
    }
    source_map["taurus_metadata.json"] = (
        "c3_taurus_metadata.json",
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41590-024-01994-8&format=json&resultType=core",
    )
    source_map["taurus_article.html"] = (
        "c3_taurus_pmc.html",
        "https://pmc.ncbi.nlm.nih.gov/articles/PMC11519010/",
    )
    pin_path = ROOT / "configs/chunk3_source_manifest.json"
    pins = json.loads(pin_path.read_text()) if pin_path.exists() else {}
    log = []
    for target, (cached, url) in source_map.items():
        p = raw / target
        if not p.exists() and verify_sources:
            with urllib.request.urlopen(url, timeout=30) as response:
                payload = response.read(3_000_001)
            if len(payload) > 3_000_000:
                raise ValueError("Source exceeds curation download budget")
            p.write_bytes(payload)
        if not p.exists():
            if target not in pins:
                raise FileNotFoundError(f"No archived source provenance for {target}")
            archived = dict(pins[target])
            archived["raw_retained_in_this_checkout"] = False
            archived["verification"] = "archived manual curation, not newly retrieved"
            log.append(archived)
            continue
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        if target in pins and digest != pins[target]["sha256"]:
            raise ValueError(f"Source changed; review evidence before repinning {target}")
        log.append(
            dict(
                path=str(p.relative_to(ROOT)),
                url=url,
                sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                bytes=p.stat().st_size,
                checked_date_utc="2026-11-10",
                rights="consult source licence; public access is not an individual-data grant",
            )
        )
    (ROOT / "data/metadata/chunk3_sources.json").write_text(json.dumps(log, indent=2) + "\n")
    x = pd.read_csv(ROOT / "data/processed/osp_7e3_observations.csv")
    ready = pd.DataFrame(
        dict(
            drug=x.molecule,
            study_id=x.study_id,
            cohort_id="Garg2007_2009_shared_OSP_source",
            patient_id=np.nan,
            observation_level="aggregate_animal_profile",
            species="Mouse",
            dose=8.0,
            dose_unit="mg/kg",
            route="iv",
            administration_time_h=0.0,
            sampling_time_h=x.time_h,
            concentration=x.concentration_nmol_l,
            concentration_unit="nmol/L",
            disease="non_IBD_control",
            body_weight_kg=np.nan,
            albumin_g_L=np.nan,
            inflammation_marker=np.nan,
            tissue_region=x.organ,
            tissue_sample_type=x.compartment,
            immunogenicity=np.nan,
            profile=x.profile,
            source_sheet=x.source_sheet,
            reported_sd=x.reported_sd_nmol_l,
        )
    )
    ready["measured_quantity"] = np.where(
        x.compartment == "Plasma",
        "plasma_drug",
        "radiolabelled_tissue_signal_intact_free_bound_fractions_unresolved",
    )
    ready["role"] = "animal_benchmark_only_no_independent_human_validation"
    ready.to_csv(ROOT / "data/processed/chunk3_7e3_ready.csv", index=False)
    # Audited published aggregate facts are versioned; dynamic publisher HTML is optional.
    summaries = pd.read_csv(ROOT / "data/benchmarks/human_summary_endpoints.csv")
    public = json.loads((ROOT / "configs/public_benchmark_manifest.json").read_text())
    expected = next(x["sha256"] for x in public if x["id"] == "human_aggregate_facts")
    actual = hashlib.sha256(
        (ROOT / "data/benchmarks/human_summary_endpoints.csv").read_bytes()
    ).hexdigest()
    if actual != expected:
        raise ValueError("Curated public benchmark changed; review before repinning")
    assert_disjoint(
        summaries[summaries.role == "calibration"], summaries[summaries.role == "validation"]
    )
    summaries.to_csv(ROOT / "data/processed/chunk3_human_summary_endpoints.csv", index=False)
    audit = {
        "animal_rows": len(ready),
        "animal_independent_human_validation_rows": 0,
        "human_summary_rows": len(summaries),
        "human_concentration_time_rows": 0,
        "usable_independent_tissue_rows": 0,
        "independent_heldout_human_studies": 1,
        "calibration_missingness": missingness(summaries),
        "animal_missingness": missingness(ready),
        "split_rule": (
            "Entire trials separated; US/EU arms of same trial not separate "
            "studies; participant IDs unavailable"
        ),
        "tissue_exclusions": {
            "ATLAS_PMID25670812": (
                "30 participants reported; abstract/metadata only; no individual "
                "dosing/assay-normalised observations retrieved"
            ),
            "Yoshihara_PMID28945638": (
                "25 participants reported; abstract/metadata only; no individual data retrieved"
            ),
            "7E3": (
                "Mouse radiolabelled tissue/model-development data; not free "
                "interstitium or independent human IBD validation"
            ),
        },
        "zero_sd_policy": (
            "96 zeros retained as flags; not used as infinite weights; "
            "terminal fit uses estimated working log error"
        ),
        "TAURUS": "No matrix acquired; no transcript-to-protein mapping attempted",
    }
    (ROOT / "data/metadata/chunk3_curation.json").write_text(json.dumps(audit, indent=2) + "\n")
    return ready, summaries


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-sources", action="store_true")
    curate(verify_sources=parser.parse_args().verify_sources)
