import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ============================================================
# 1. SETUP: Konfigurasi Chrome agar tidak mudah terdeteksi
# ============================================================
def create_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    # Sembunyikan properti navigator.webdriver agar bot tidak terdeteksi
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

# ============================================================
# 2. NAVIGASI: Buka URL & tunggu elemen loading selesai
# ============================================================
def navigate_and_wait(driver, url, wait_selector, timeout=15):
    try:
        driver.get(url)
        # Tunggu hingga elemen yang ditunjuk benar-benar muncul di DOM
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector))
        )
        print(f"Halaman berhasil dimuat: {url}")
        return True
    except TimeoutException:
        print(f"ERROR: Timeout menunggu selector '{wait_selector}' di {url}")
        return False

# ============================================================
# 3. EKSTRAKSI DATA: Contoh ambil teks via XPath / CSS
# ============================================================
def extract_odds_data(driver):
    data = []

    try:
        # --- Contoh 1: ambil teks dari elemen dengan CSS Selector ---
        # Ganti '.odds-table .team-name' dengan selector sesuai target
        team_elements = driver.find_elements(By.CSS_SELECTOR, ".odds-table .team-name")
        team_names = [el.text.strip() for el in team_elements]

        # --- Contoh 2: ambil teks dari elemen dengan XPath ---
        # Ganti '//table[@id="odds"]//tr[@class="row"]/td[2]' sesuai target
        price_elements = driver.find_elements(By.XPATH, '//table[@id="odds"]//tr[@class="row"]/td[2]')
        prices = [el.text.strip() for el in price_elements]

        # --- Contoh 3: ambil atribut (misal href / data-odds) ---
        link_elements = driver.find_elements(By.CSS_SELECTOR, "a.match-link")
        links = [el.get_attribute("href") for el in link_elements]

        # Gabungkan ke list of dictionaries (sesuaikan struktur dengan kebutuhan)
        for i in range(max(len(team_names), len(prices), len(links))):
            entry = {}
            if i < len(team_names):
                entry["team"] = team_names[i]
            if i < len(prices):
                entry["odds"] = prices[i]
            if i < len(links):
                entry["link"] = links[i]
            if entry:
                data.append(entry)

    except NoSuchElementException as e:
        print(f"ERROR: Elemen tidak ditemukan saat ekstraksi - {e}")

    return data

# ============================================================
# 4. SIMPAN KE JSON
# ============================================================
def save_to_json(data, filename="hasil_odds.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data tersimpan di {filename} ({len(data)} entri)")

# ============================================================
# 5. MAIN: Jalankan scraper dengan penanganan error penuh
# ============================================================
def main():
    # >>> SESUAIKAN URL DAN SELECTOR DI SINI <<<
    TARGET_URL = "https://example-sportsbook.com/odds"
    WAIT_SELECTOR = ".odds-table"  # ganti dengan selector elemen utama

    driver = None
    try:
        driver = create_driver()
        if navigate_and_wait(driver, TARGET_URL, WAIT_SELECTOR):
            data = extract_odds_data(driver)
            save_to_json(data)
        else:
            print("Scraping gagal: halaman tidak termuat dengan benar.")
    except Exception as e:
        print(f"ERROR umum: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()
