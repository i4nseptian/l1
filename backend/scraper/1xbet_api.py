"""
Pendekatan: INTERCEPT API RESPONSE via CDP (Chrome DevTools Protocol)
Lebih cepat & akurat daripada OCR.
"""
import json
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ------------------------------------------------
# 1. SETUP dengan CDP Network interception
# ------------------------------------------------
options = uc.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# Aktifkan Network tracking via CDP
driver.execute_cdp_cmd("Network.enable", {})

captured = []

def on_response(request_id, response_dump):
    """Callback tiap kali ada response dari server."""
    url = response_dump.get("response", {}).get("url", "")
    # Filter URL yang mengandung kata kunci odds / event / market
    if any(kw in url for kw in ["/odds/", "/events/", "/market/", "LineFeed", "GetEvents"]):
        try:
            body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
            text = body.get("body", "")
            # Coba parse sebagai JSON
            data = json.loads(text)
            captured.append({
                "url": url,
                "data": data
            })
            print(f"[API] {url[:80]}...")
        except:
            pass

# Register listener
driver.execute_cdp_cmd("Network.setResponseCallback", {
    "callback": f"({on_response.__code__.co_varnames}) => {{}}"
})

# ------------------------------------------------
# 2. BUKA 1XBET
# ------------------------------------------------
driver.get("https://1xbet.com/en")
time.sleep(5)

# Tutup popup
try:
    driver.find_element(By.CSS_SELECTOR, ".cookie__btn, .modal__close, [class*='close']").click()
except:
    pass

# ------------------------------------------------
# 3. PILIH OLAHRAGA
# ------------------------------------------------
try:
    fb = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "[data-name='football'], a[href*='football'], .sport-item__football")
    ))
    fb.click()
    time.sleep(3)
except:
    pass

# ------------------------------------------------
# 4. AMBIL DATA DARI API YANG TERTANGKAP
# ------------------------------------------------
print(f"\nTotal response API tertangkap: {len(captured)}")

# Gabung & simpan semua data API yang relevant
all_odds = []
for c in captured:
    data = c["data"]
    if isinstance(data, dict):
        # Coba ekstrak event / market / odds
        if "events" in data:
            all_odds.extend(data["events"] if isinstance(data["events"], list) else [data["events"]])
        elif "markets" in data:
            all_odds.append(data)
        elif "Value" in data:
            all_odds.append(data)

output = {
    "source": "1xBet (via API intercept)",
    "total_events": len(all_odds),
    "data": all_odds
}

with open("1xbet_api.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Tersimpan {len(all_odds)} event di 1xbet_api.json")

driver.quit()
