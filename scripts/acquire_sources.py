"""Bounded, logged retrieval. Public visibility does not establish a reuse licence."""

import argparse
import csv
import hashlib
import json
import urllib.error
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "data/metadata/retrieval_log.csv"
FIELDS = [
    "source_id",
    "attempted_at_utc",
    "url",
    "final_url",
    "status",
    "http_status",
    "bytes",
    "sha256",
    "local_path",
    "content_type",
    "error",
]


def retrieve(source, refresh=False):
    path = ROOT / source["local_path"]
    row = dict.fromkeys(FIELDS, "")
    row.update(
        source_id=source["id"],
        attempted_at_utc=datetime.now(UTC).isoformat(),
        url=source["url"],
        local_path=source["local_path"],
    )
    if path.is_file() and not refresh:
        row.update(
            status="cached_not_refetched",
            bytes=path.stat().st_size,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        return row
    limit = source.get("max_bytes", 5_000_000)
    try:
        request = urllib.request.Request(
            source["url"],
            headers={
                "User-Agent": "InflammaPBPK-research-scaffold/0.1 (public-source feasibility audit)"
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            row.update(
                http_status=response.status,
                final_url=response.url,
                content_type=response.headers.get("Content-Type", ""),
            )
            if int(response.headers.get("Content-Length", 0)) > limit:
                raise ValueError(f"Content-Length exceeds {limit}-byte retrieval budget")
            payload = response.read(limit + 1)
            if len(payload) > limit:
                raise ValueError(f"Stream exceeds {limit}-byte retrieval budget")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_bytes(payload)
        temporary.replace(path)
        row.update(
            status="retrieved", bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest()
        )
    except urllib.error.HTTPError as error:
        row.update(status="http_error", http_status=error.code, error=str(error))
    except urllib.error.URLError as error:
        row.update(status="connection_error", error=str(error))
    except (OSError, ValueError, TimeoutError) as error:
        row.update(status="retrieval_error", error=str(error))
    return row


def write_csv(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build_registries(sources):
    latest = {}
    if LOG.exists():
        for row in csv.DictReader(LOG.open()):
            latest[row["source_id"]] = row
    literature, searches = [], []
    for source in sources:
        if source["kind"] not in {"literature", "search"}:
            continue
        path = ROOT / source["local_path"]
        response = json.loads(path.read_text()) if path.is_file() else {}
        results = response.get("resultList", {}).get("result", [])
        if source["kind"] == "search":
            searches.append(
                {
                    "search_id": source["id"],
                    "query": source["query"],
                    "status": latest.get(source["id"], {}).get("status", "unrun"),
                    "total_hits": response.get("hitCount", ""),
                    "returned_records": len(results),
                    "screened": "no",
                    "result_path": source["local_path"],
                }
            )
            continue
        record = results[0] if len(results) == 1 else {}
        literature.append(
            {
                "reference_id": source["id"],
                "user_supplied_description": source["description"],
                "requested_identifier": source["identifier"],
                "title": record.get("title", ""),
                "authors": record.get("authorString", ""),
                "year": record.get("pubYear", ""),
                "doi": record.get("doi", ""),
                "pmid": record.get("id", ""),
                "pmcid": record.get("pmcid", ""),
                "publication_type": json.dumps(record.get("pubTypeList", {})),
                "verification_status": "metadata_retrieved_needs_relevance_review"
                if record
                else "unverified",
                "relevance": "not_assessed",
                "model_mechanisms": "not_assessed",
                "available_measurements": "not_assessed",
                "supplementary_files": "not_assessed",
                "limitations": "Bibliographic labels supplied by user are not validated titles",
                "open_access": record.get("isOpenAccess", "unknown"),
                "licence": "not_verified",
                "retrieval_status": latest.get(source["id"], {}).get("status", "unrun"),
                "source_url": source["url"],
            }
        )
    for source in sources:
        if source["kind"] != "github" or not source["id"].endswith("evaluation_report_md"):
            continue
        path = ROOT / source["local_path"]
        if not path.is_file():
            continue
        row = dict.fromkeys(literature[0], "")
        row.update(
            reference_id=source["id"],
            title=path.read_text().splitlines()[0].removeprefix("# "),
            verification_status="source_report_retrieved_primary_references_not_verified",
            relevance="nonhuman mechanistic comparator",
            model_mechanisms="whole body; two pore; lymph; endosomal clearance; FcRn recycling",
            available_measurements="aggregate mouse plasma/tissue"
            if "7E3" in source["id"]
            else "cynomolgus plasma; not extracted",
            supplementary_files="pinned PK-Sim project; 7E3 snapshot acquired separately",
            limitations="model-development data; not independent human anti-TNF validation",
            open_access="publicly accessible source report",
            licence="report and underlying data rights require verification",
            retrieval_status=latest[source["id"]]["status"],
            source_url=source["url"],
        )
        literature.append(row)
    write_csv(ROOT / "research/literature_registry.csv", literature)
    write_csv(ROOT / "research/search_registry.csv", searches)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=["all", "github", "research"], default="all")
    parser.add_argument("--refresh", action="store_true", help="Refetch successful local artifacts")
    args = parser.parse_args()
    sources = json.loads((ROOT / "configs/sources.json").read_text())
    selected = [
        s
        for s in sources
        if args.scope == "all" or (args.scope == "github") == (s["kind"] == "github")
    ]
    LOG.parent.mkdir(parents=True, exist_ok=True)
    header = not LOG.exists()
    with LOG.open("a", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        if header:
            writer.writeheader()
        for source in selected:
            row = retrieve(source, args.refresh)
            writer.writerow(row)
            stream.flush()
            print(f"{source['id']}: {row['status']} ({row['bytes']} bytes)", flush=True)
    build_registries(sources)


if __name__ == "__main__":
    main()
