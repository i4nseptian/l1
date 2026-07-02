import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.page_load_strategy = "eager"

driver = webdriver.Chrome(options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

try:
    URL = "https://example.com/odds"
    driver.get(URL)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".odds-table"))
    )

    data = []
    for el in driver.find_elements(By.CSS_SELECTOR, ".odds-row"):
        try:
            data.append({
                "team": el.find_element(By.CSS_SELECTOR, ".team").text.strip(),
                "odds": el.find_element(By.CSS_SELECTOR, ".price").text.strip(),
            })
        except:
            continue

    with open("hasil.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"OK — {len(data)} data")

finally:
    driver.quit()
