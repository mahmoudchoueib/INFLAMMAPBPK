"""Audit local datasets and every dashboard page in PNG and interactive modes."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from streamlit.testing.v1 import AppTest

from inflammappbpk.validation.readiness import (
    artifact_inventory,
    optional_inventory,
    source_inventory,
)

ROOT = Path(__file__).resolve().parents[1]
INFORMATION_PAGES = {
    "Biologic selection",
    "Target-mediated disposition",
    "Literature and parameter provenance",
    "Data and system status",
    "User guide",
}


def main():
    sources = source_inventory(ROOT)
    artifacts = artifact_inventory(ROOT)
    failures = []
    pages = []
    for display in ["Static images", "Interactive"]:
        app = AppTest.from_file(str(ROOT / "dashboard/app.py"), default_timeout=60).run()
        if app.exception:
            failures.extend(str(item.message) for item in app.exception)
            continue
        app.radio(key="chart_display").set_value(display).run()
        for page in app.selectbox(key="page").options:
            app.selectbox(key="page").set_value(page).run(timeout=60)
            charts = len(app.get("image")) + len(app.get("plotly_chart"))
            errors = [str(item.message) for item in app.exception]
            if page not in INFORMATION_PAGES and charts == 0:
                errors.append("Expected chart was not produced")
            failures.extend(f"{display}/{page}: {error}" for error in errors)
            pages.append({"page": page, "display": display, "charts": charts, "errors": errors})
    report = {
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "status": "passed"
        if not failures
        and sources.status.eq("Verified").all()
        and artifacts.status.eq("Ready").all()
        else "needs_attention",
        "required_sources": sources.to_dict("records"),
        "chart_inputs": artifacts.to_dict("records"),
        "optional_sources": optional_inventory(ROOT).to_dict("records"),
        "page_checks": pages,
        "failures": failures,
        "scope": "Streamlit runtime and chart production; not a browser visual inspection",
        "dashboard_source_sha256": hashlib.sha256(
            (ROOT / "dashboard/app.py").read_bytes()
        ).hexdigest(),
    }
    path = ROOT / "results/quality/dashboard_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Dashboard audit: {report['status']}; {len(pages)} page/mode checks; report: {path}")
    if report["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
