# Using InflammaPBPK

## Start and see your first graph

Open **http://localhost:8501** while the local server is running. In Windows
PowerShell, start it from the repository folder with:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m streamlit run dashboard/app.py
```

Keep that terminal open. Ctrl+C stops a server started in that terminal. See
`docs/installation.md` for installation; in WSL2 Ubuntu use `make dashboard`.

**Project overview** opens with an exploratory reference simulation and plasma
graph: 70 kg, one 40 mg SC administration, 28 days. This is a research example,
not a treatment recommendation.

1. Use **Research page** at the top of the sidebar to open a page.
2. Keep **Chart display → Static images** for PNG graphs. Select **Interactive**
   for hover values, legend selection and zoom.
3. Expand the relevant sidebar controls, edit them, and press the blue
   **Run exploratory simulation** button near the top of the form.
4. Open **Plasma pharmacokinetics**, **Tissue distribution** or **FcRn recycling**.
   Changing pages preserves the successful simulation.
5. Expand **Displayed configuration and numerical audit** to inspect the exact
   inputs, fingerprint and mass balance, or download the configuration and CSV.

The caption identifies the reference preview or last successful run. Form edits
only take effect after Run. Invalid inputs show an error and preserve the previous
successful result, which is not a run of the invalid inputs.

## Pages and what to expect

| Page | Contents and usage |
| --- | --- |
| Project overview | Immediate plasma preview, evidence counts and starting instructions. |
| Whole-body physiology | Organ volumes, flows and an illustrative flow graph. |
| Biologic selection | Implementation and evidence table; no simulation graph. |
| Plasma pharmacokinetics | Free venous plasma curve and exposure summaries. |
| Tissue distribution | Free interstitial curves; select at least one region. |
| Intestinal inflammation model | Automatic configured/reference transport comparison. Curves overlap at reference settings. |
| FcRn recycling | Endosomal inventories and cumulative recycling/elimination curves. |
| Target-mediated disposition | Occupancy curves with nonzero target sites. With both targets at zero, occupancy is undefined and no occupancy graph is drawn. |
| Dose and schedule simulator | Administration times and the administered/remaining/eliminated balance graph. |
| Population variability | Automatic three-weight comparison; change the spread. All weights must be within 40–150 kg. |
| Parameter sensitivity | Stored Sobol analysis; select an endpoint. Live controls do not refit it. |
| Bayesian uncertainty | Stored mouse 7E3 posterior and in-sample predictive data; not a human PBPK posterior. |
| Model comparison | Stored synthetic A–E comparison; select the generating model. |
| Experimental validation | One held-out healthy-trial aggregate comparison and evidence gaps. |
| Literature and parameter provenance | Controls, Model parameters, Datasets and Literature tabs. |
| Data and system status | Current file presence, source checksums, readable chart data and optional-source availability. |
| User guide | This guide and its downloadable copy. |

## Try a transport experiment

Choose **regional_hypothesis** as Disease scenario. Expand **Regional transport
hypotheses**, change the regional PS multiplier from 1 to 2, and press Run. Open
**Intestinal inflammation model** to compare against reference transport at the
same dose, weight, target and FcRn settings. These are hypotheses, not observed
inflamed/non-inflamed patient tissue curves.

For an occupancy experiment, set positive soluble or membrane target sites in
**FcRn and target hypotheses**, press Run, and open **Target-mediated disposition**.
The target amounts and kinetics are assumptions; occupancy does not validate them.

## Data readiness and stored analyses

The required benchmark consists of the pinned public OSP 7E3 source and README,
and the versioned human summary CSV. Extraction yields **174 aggregate mouse
observations across 24 profiles**. The human CSV has **five aggregate endpoints
from two trials**, with calibration and validation separated. There are no
patient-level records or independent human tissue observations.

**Data and system status** checks the current checkout. Historical retrieval
notes are kept separate from current optional-source presence. TAURUS matrices,
candidate papers and other optional sources are not required for the supported
benchmark. A dataset-registry entry does not mean its raw file is present.

Sensitivity, Bayesian, comparison and validation pages use stored analyses,
which do not change with the live scenario. In WSL2 Ubuntu, regenerate missing
sources, analyses, 15 PNG/SVG/PDF figure sets and reports with:

```bash
bash scripts/install.sh
make reproduce
```

The report is `results/report/research_report.html`. Results and virtual
environments are excluded from Git and must be generated in a new checkout.

To repeat the dataset and dashboard audit on Windows:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/audit_dashboard.py
```

It checks all 17 pages in both chart modes and writes
`results/quality/dashboard_audit.json`. It reports missing required files and
runtime/chart errors. Browser appearance still requires a visual check.

## If a graph is missing

- Refresh after an update. If the sidebar is collapsed, use its upper-left arrow.
- Select **Chart display → Static images**. PNGs do not need Plotly's browser
  renderer; each has a **Download chart PNG** button.
- Biologic selection, provenance, guide and status are information pages.
- Select at least one tissue region. Enable target sites before expecting an
  occupancy graph.
- If Run shows an error, fix the inputs and run again. Check the displayed
  configuration and fingerprint to identify the successful snapshot.
- For stored-analysis graphs, check **Data and system status** and regenerate
  missing or invalid files using the commands above.
- If the page cannot connect, start the server and open its printed URL in a
  normal browser such as Brave. Use the exact port shown by Streamlit.

## Interpretation and limits

Every control documents units, bounds, defaults, source and evidence in its help
and the provenance table. Bounds are computational guardrails, not validated
physiological intervals. Reference disease settings require PS/flow/lymph factors
of 1. Clinical severity and albumin are not converted to transport coefficients.

IV is an instantaneous bolus; infusion is not implemented. SC uses a depot and
lymph transit. Absorption controls are inactive for IV. Absolute mg and mg/kg
differ: weight-normalised dosing changes total dose when weight changes. All
administrations must fit within the simulation horizon. Weight scaling is assumed.

Infliximab requires explicit acknowledgement and IV route. It uses a generic
scaffold without drug-specific calibration or external validation. Tissue curves
are free interstitial concentrations, not biopsy homogenates. Recycled flux counts
repeated passages and is excluded from remaining-drug mass. The three-weight grid
is a sensitivity experiment, not a fitted population interval.

The tissue-prediction hypothesis remains **inconclusive**. Zero usable independent
human tissue observations and no validated infliximab transfer are available.
Numerical tests and plausible curves do not establish clinical accuracy. This
application provides no clinical dosing advice.
