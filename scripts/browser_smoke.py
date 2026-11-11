"""Optional real-browser QA; requires Playwright and a running loopback Streamlit server."""
import argparse
import importlib.metadata
import json
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', default='http://127.0.0.1:8765')
    args = parser.parse_args()
    out = ROOT / 'results/quality'
    out.mkdir(exist_ok=True)
    with urllib.request.urlopen(args.url + '/_stcore/health', timeout=20) as response:
        assert response.status == 200
    with sync_playwright() as tool:
        browser = tool.chromium.launch(executable_path='/usr/bin/chromium', headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1080})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(args.url, wait_until='networkidle', timeout=45000)
        page.get_by_role('button', name='Run exploratory simulation', exact=True).click()
        page.get_by_text('Configuration fingerprint:', exact=False).wait_for(timeout=45000)
        page.get_by_role('combobox').first.click()
        page.get_by_role('option', name='Plasma pharmacokinetics', exact=True).click()
        page.get_by_role('heading', name='Plasma pharmacokinetics', exact=True).wait_for()
        page.get_by_test_id('stPlotlyChart').first.wait_for(timeout=30000)
        assert page.get_by_test_id('stPlotlyChart').count() > 0
        assert not errors, errors
        page.screenshot(path=str(out / 'dashboard_browser.png'), full_page=True)
        record = {
            'status': 'passed', 'health_status': 200,
            'playwright_version': importlib.metadata.version('playwright'),
            'chromium_version': browser.version, 'page_errors': errors,
            'functional_check': 'submitted ODE simulation and navigated to a rendered Plotly chart',
        }
        browser.close()
    (out / 'browser_smoke.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))


if __name__ == '__main__':
    main()
