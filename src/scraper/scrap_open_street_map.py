import time

from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver

chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1200,800")
        # Set language to Polish
chrome_options.add_argument("--lang=pl")
chrome_options.add_experimental_option(
    "prefs",
    {
        "intl.accept_languages": "pl,pl_PL",
        "profile.default_content_setting_values.geolocation": 2,  # Block geolocation
    },
)
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0 (pl-PL)"
)

chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
    )


def _remove_elements_by_class():
    def _remove(class_name):
        try:
            if " " in class_name:
                # Create an XPath that looks for elements with both classes
                class_parts = class_name.split(" ")
                xpath = f"//*[contains(@class, '{class_parts[0]}') and contains(@class, '{class_parts[1]}')]"
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
            else:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, class_name))
                )

            driver.execute_script("arguments[0].remove();", element)
            print(f"Element with class '{class_name}' removed.")
        except Exception as e:
            print(f"Couldn't remove element with class '{class_name}': {e}")

    elements_to_remove_by_class = [
        "leaflet-control-container",
        "search_forms",
        "d-flex bg-body text-nowrap closed z-3",
        "welcome position-relative p-3",
        "leaflet-control-attribution leaflet-control",
        "d-flex gap-2"
    ]

    for class_name in elements_to_remove_by_class:
        _remove(class_name)
    for _ in range(10):
        _remove("leaflet-control")
        
    
        

try:
    url = "https://www.openstreetmap.org/#map=19/52.219463/21.010304"
    driver.get(url)

    # Poczekaj na załadowanie strony
    time.sleep(2)

    try:
        # Jeśli pojawi się przycisk zgód, np. "Akceptuj wszystko", kliknij go
        accept_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Akceptuj wszystko')]")
            )
        )
        accept_button.click()
        print("Kliknięto 'Akceptuj wszystko'.")
        time.sleep(1)
    except Exception as e:
        print("Nie znaleziono przycisku zgód lub już zaakceptowane:", str(e))

    _remove_elements_by_class()
    time.sleep(0.1)

    screenshot_path = "openstreetmap_screenshot.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot zapisany jako: {screenshot_path}")

finally:
    driver.quit()
