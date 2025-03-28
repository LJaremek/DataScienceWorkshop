import time

from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1200,800")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
    )

try:
    url = "https://www.openstreetmap.org/export#map=19/52.219463/21.010304"
    driver.get(url)

    # Poczekaj na załadowanie strony
    time.sleep(5)

    try:
        # Jeśli pojawi się przycisk zgód, np. "Akceptuj wszystko", kliknij go
        accept_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Akceptuj wszystko')]")
            )
        )
        accept_button.click()
        print("Kliknięto 'Akceptuj wszystko'.")
        time.sleep(3)
    except Exception as e:
        print("Nie znaleziono przycisku zgód lub już zaakceptowane:", str(e))

    screenshot_path = "openstreetmap_screenshot.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot zapisany jako: {screenshot_path}")

finally:
    driver.quit()
