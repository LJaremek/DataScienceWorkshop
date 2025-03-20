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

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

try:
    driver.get("https://www.google.pl/maps/@52.2195197,21.0102444,101m/data=!3m1!1e3?entry=ttu&g_ep=EgoyMDI1MDMwMi4wIKXMDSoASAFQAw%3D%3D")

    time.sleep(5)

    try:
        accept_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Zaakceptuj wszystko')]"))
        )
        accept_button.click()
        print("Kliknięto 'Zaakceptuj wszystko'.")
        time.sleep(3)
    except Exception as e:
        print("Nie znaleziono przycisku zgód lub już zaakceptowane.")

    screenshot_path = "google_maps_screenshot.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot zapisany jako: {screenshot_path}")

finally:
    driver.quit()
