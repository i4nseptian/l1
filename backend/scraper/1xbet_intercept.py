import json, sys
from playwright.sync_api import sync_playwright

"""
Cara pakai:
  1. pip install playwright
  2. python -m playwright install chromium
  3. python 1xbet_intercept.py
"""

ALL_DATA = []

def handle_response(response):
    url = response.url
    if any(kw in url for kw in ["/odds/", "/events/", "LineFeed", "GetEvents"]):
        try:
            data = response.json()
            ALL_DATA.append({"url": url, "data": data})
            print(f"[+] {url[:90]}")
        except:
            pass

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = ctx.new_page()
    page.on("response", handle_response)

    page.goto("https://1xbet.com/en")
    page.wait_for_timeout(5000)

    try:
        page.click(".sport-item__football, [data-name='football']", timeout=10000)
        page.wait_for_timeout(3000)
    except:
        pass

    # Scroll biar semua event ke-load
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(2000)

    browser.close()

with open("1xbet_playwright.json", "w", encoding="utf-8") as f:
    json.dump(ALL_DATA, f, ensure_ascii=False, indent=2)

print(f"\nSelesai! {len(ALL_DATA)} API response tersimpan.")
