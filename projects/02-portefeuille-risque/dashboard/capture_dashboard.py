from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page=browser.new_page(viewport={"width":1440,"height":900},device_scale_factor=1)
    page.goto('http://127.0.0.1:8765/dashboard/web/',wait_until='domcontentloaded')
    page.wait_for_timeout(1500)
    page.screenshot(path=str(ROOT/'preview/dashboard_web.png'),full_page=True)
    page.select_option('#sector','Finance')
    page.wait_for_timeout(500)
    page.screenshot(path=str(ROOT/'preview/dashboard_web_finance.png'),full_page=True)
    browser.close()
print('captures créées')
