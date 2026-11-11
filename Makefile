.NOTPARALLEL:
RUN = bash scripts/run_python.sh
.PHONY: install data baseline whole analysis examples figures report check dashboard dashboard-smoke audit-dashboard reproduce
install:
	bash scripts/install.sh
data:
	$(RUN) scripts/fetch_public_data.py
	$(RUN) scripts/extract_osp_7e3.py
baseline:
	$(RUN) -m inflammappbpk baseline --route iv --dose-nmol 100 --hours 48
whole:
	$(RUN) -m inflammappbpk whole
analysis: data
	$(RUN) scripts/run_chunk3.py
examples:
	$(RUN) scripts/run_reference_simulations.py
figures: analysis examples
	$(RUN) scripts/generate_figures.py
report: figures
	$(RUN) scripts/build_report.py
check:
	$(RUN) -m ruff check src tests scripts dashboard
	$(RUN) -m mypy src
	$(RUN) -m pytest -q
dashboard:
	bash scripts/run_dashboard.sh
dashboard-smoke:
	$(RUN) -m pytest -q tests/test_dashboard.py
audit-dashboard:
	$(RUN) scripts/audit_dashboard.py
reproduce: data baseline whole report check
