import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from src.scraper.utils import create_driver


class GoogleMapsScraper:

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
            f"https://www.google.pl/maps/@{latitude},{longitude},101m/data=!3m1!1e3?entry=ttu&g_ep=EgoyMDI1MDMwMi4wIKXMDSoASAFQAw%3D%3D"
        )
        self._click_accept()
        time.sleep(3)
        self._disable_labels()
        self._remove_elements_by_class()
        self._remove_minimap()
        self.driver.save_screenshot(path)

    def _click_accept(self):
        try:
            accept_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Zaakceptuj wszystko')]")
                )
            )
            accept_button.click()
            print("Accepted cookies.")
            time.sleep(1)
        except Exception as e:
            print("Could not find the accept button:", e)

    def _disable_labels(self):
        try:
            target_x = 150
            target_y = self.driver.execute_script("return window.innerHeight;") - 80

            # Execute JavaScript to move cursor directly to that position
            self.driver.execute_script(
                f"""
                var event = new MouseEvent('mousemove', {{
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': {target_x},
                    'clientY': {target_y}
                }});
                document.elementFromPoint({target_x}, {target_y}).dispatchEvent(event);
            """
            )

            print(f"Moved cursor to position (x: {target_x}, y: {target_y})")
            time.sleep(
                0.5
            )  # Increased wait time to make sure hover effect is triggered

            # Now look for the button
            button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Więcej')]")
                )
            )
            button.click()
            print("Clicked on layer switcher button.")
            time.sleep(0.2)

            # find and click the checkbox
            checkbox = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[@role='checkbox' and .//label[contains(text(), 'Etykiety')]]",
                    )
                )
            )

            if checkbox.get_attribute("aria-checked") == "true":
                checkbox.click()
                print("Unchecked labels.")
            else:
                print("Labels checkbox is already unchecked.")

            time.sleep(0.2)
        except Exception as e:
            print(f"Could not uncheck labels button {e}")

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
            "JLm1tf-bEDTcc-GWbSKc",  # search box
            "bJzME tTVLSc",  # likely a UI panel or widget
            "app-vertical-widget-holder Hk4XGb",  # vertical widget holder
            "app-bottom-content-anchor HdXONd",  # bottom content anchor
            "gb_Qe",  # login button
            "scene-footer",  # footer
            "hUbt4d-watermark",  # google logo at the bottom
            "ZhtFke",  # another UI element
        ]

        for class_name in elements_to_remove_by_class:
            _remove(class_name)

    def _remove_minimap(self):
        try:
            xpath = "//*[contains(@class, 'hdeJwf')]"
            element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            self.driver.execute_script("arguments[0].remove();", element)
            print("Element z klasą 'hdeJwf pzaG1c' usunięty przed zrzutem ekranu.")
        except Exception as e:
            print(f"Element z klasą 'hdeJwf pzaG1c' nie został znaleziony: {e}")


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
    scraper = OpenStreetMapScraper(headless=False)
    try:
        scraper.scrape(cords=(latitude, longitude), path="openstreetmap_screenshot.png")
    finally:
        scraper.driver.quit()

    scraper = GoogleMapsScraper(headless=False)
    try:
        scraper.scrape(cords=(latitude, longitude), path="googlemaps_screenshot.png")
    finally:
        scraper.driver.quit()

if __name__ == "__main__":
    main()
