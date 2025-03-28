import time
import os

from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver

to_check = [
    None,
    (52.207490, 21.002115),
    (52.206627, 21.001152),
    (52.162737, 21.027527),
    (52.164514, 20.990903),
    (52.170382, 20.994074),
    (52.190805, 20.957609),
    (52.192980, 20.953028),
    (52.194452, 20.952341),
    (52.196366, 20.951335),
    (52.197370, 20.950818),
    (52.198332, 20.952261),
    (52.201217, 20.945625)
]


def scrap_google_map(
        cords: tuple[float, float],
        driver: ChromiumDriver = None,
        path: str = "google_map.png",
        printing: bool = False
        ) -> None:

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    url = f"https://www.google.pl/maps/@{cords[0]},{cords[1]},101m"
    url += "/data=!3m1!1e3?entry=ttu&g_ep=EgoyMDI1MDMwMi4wIKXMDSoASAFQAw%3D%3D"
    driver.get(url)

    time.sleep(5)

    try:
        accept_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Zaakceptuj wszystko')]")
            )
        )
        accept_button.click()

        if printing:
            print("Kliknięto 'Zaakceptuj wszystko'.")

        time.sleep(3)
    except Exception as e:
        if printing:
            msg = "Nie znaleziono przycisku zgód lub już zaakceptowane: "
            msg += str(e)
            print(msg)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    driver.save_screenshot(path)

    if printing:
        print("Path:", path)


def scrap_open_street_map(
        cords: tuple[float, float],
        driver: ChromiumDriver = None,
        path: str = "open_street_map.png",
        printing: bool = False
        ) -> None:

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    url = f"https://www.openstreetmap.org/export#map=19/{cords[0]}/{cords[1]}"
    driver.get(url)

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
        if printing:
            msg = "Nie znaleziono przycisku zgód lub już zaakceptowane: "
            msg += str(e)
            print(msg)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    driver.save_screenshot(path)

    if printing:
        print("Path:", path)


if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1200,800")

    for index, cords in enumerate(to_check):
        if cords is None:
            continue

        scrap_google_map(cords=cords, path=f"data/{index}/gm.png")
        scrap_open_street_map(cords=cords, path=f"data/{index}/osm.png")
