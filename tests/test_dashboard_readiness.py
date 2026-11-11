import hashlib
import json

import numpy as np
import pandas as pd
import plotly.express as px
import pytest

from inflammappbpk.validation.readiness import artifact_inventory, source_inventory
from inflammappbpk.visualisation.static import chart_png


def test_source_check_detects_missing_and_tampered_files(tmp_path):
    (tmp_path / "configs").mkdir()
    (tmp_path / "source.csv").write_bytes(b"reference data")
    manifest = [
        {
            "id": "example",
            "local_path": "source.csv",
            "sha256": hashlib.sha256(b"reference data").hexdigest(),
        }
    ]
    (tmp_path / "configs/public_benchmark_manifest.json").write_text(json.dumps(manifest))
    assert source_inventory(tmp_path).status.tolist() == ["Verified"]
    (tmp_path / "source.csv").write_bytes(b"changed data")
    assert source_inventory(tmp_path).status.tolist() == ["Checksum mismatch"]
    (tmp_path / "source.csv").unlink()
    assert source_inventory(tmp_path).status.tolist() == ["Missing"]


def test_readiness_rejects_unusable_chart_values(tmp_path):
    path = tmp_path / "results/sensitivity/sobol_rankings.csv"
    path.parent.mkdir(parents=True)
    pd.DataFrame(
        {"metric": ["auc"], "parameter": ["flow"], "ST": [np.inf], "ST_conf": [0.1]}
    ).to_csv(path, index=False)
    table = artifact_inventory(tmp_path)
    row = table[table.path == "results/sensitivity/sobol_rankings.csv"].iloc[0]
    assert row.status == "Invalid"
    assert "Non-finite" in row.detail
    assert (table.status == "Missing").any()


@pytest.mark.parametrize("kind", ["line", "scatter", "bar", "histogram"])
def test_static_chart_is_a_nonempty_png(kind):
    from io import BytesIO

    from PIL import Image

    frame = pd.DataFrame({"time": [0, 1, 2, 3], "concentration": [0, 2, 1, 0.5]})
    if kind == "histogram":
        chart = px.histogram(frame, x="concentration")
    else:
        chart = getattr(px, kind)(frame, x="time", y="concentration")
    payload = chart_png(chart)
    assert payload.startswith(b"\x89PNG\r\n\x1a\n")
    image = Image.open(BytesIO(payload)).convert("RGB")
    assert image.width >= 1000 and image.height >= 600
    assert np.asarray(image).std() > 10  # Catch blank renderings, not just valid file headers.
