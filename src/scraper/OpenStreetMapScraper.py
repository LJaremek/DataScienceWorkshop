import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from utils import create_driver


class OpenStreetMapScraper:

    def __init__(self, headless: bool = True) -> None:
        """
        TOOD

        Args:
            longitude (float): _description_
            latitude (float): _description_
            headless (bool, optional): _description_. Defaults to True.
        """
        self.driver = create_driver(headless=headless)


    def scrape(self, cords: tuple[float, float], path: str) -> None:
        latitude, longitude = cords
        self.driver.get(
            f"https://www.openstreetmap.org/#map=19/{latitude}/{longitude}"
        )
        self._click_accept()
        time.sleep(2)
        self._remove_elements_by_class()
        self.driver.save_screenshot(path)
        

    def _click_accept(self):
        try:
            accept_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Akceptuj wszystko')]")
                )
            )
            accept_button.click()
            print("Accepted cookies.")
            time.sleep(1)
        except Exception as e:
            print("Could not find the accept button:", e)
            
    
    def _remove_elements_by_class(self):
        def _remove(class_name):
            try:
                if " " in class_name:
                    # Create an XPath that looks for elements with both classes
                    class_parts = class_name.split(" ")
                    xpath = f"//*[contains(@class, '{class_parts[0]}') and contains(@class, '{class_parts[1]}')]"
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                else:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, class_name))
                    )

                self.driver.execute_script("arguments[0].remove();", element)
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
        for _ in range(8):
            _remove("leaflet-control")        
                
def main():
    longitude = 21.0103057
    latitude = 52.2203848
    scraper = OpenStreetMapScraper(headless=True)
    try:
        scraper.scrape(cords=(latitude, longitude), path="openstreetmap_screenshot.png")
    finally:
        scraper.driver.quit()


if __name__ == "__main__":
    main()
