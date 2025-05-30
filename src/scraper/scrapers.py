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
        # wait 120 seconds for the map to load
        # time.sleep(120)
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
            print("Looking for Więcej button...")
            found_wiecej_button = False

            # try:
            #     button = WebDriverWait(self.driver, 5).until(
            #         EC.element_to_be_clickable(
            #             (By.XPATH, "//button[contains(., 'Więcej')]")
            #         )
            #     )
            #     button.click()
            #     found_wiecej_button = True
            #     print("Clicked on layer switcher button.")
            # except Exception as e:
            #     print(f"Could not find the Więcej button: {e} using XPath. Will try class name.")

            # time.sleep(0.2)

            # if not found_wiecej_button:
            #     print("Trying to find Więcej button by class name...")
            #     try:
            #         print(
            #             "Layer switcher (wiecej button) not found by XPath, trying by class name."
            #         )
            #         button = WebDriverWait(self.driver, 5).until(
            #             EC.element_to_be_clickable(
            #                 (By.CLASS_NAME, "hYkU8c")
            #             )
            #         )
            #         button.click()
            #         print("Clicked on layer switcher button by class name.")
            #         found_wiecej_button = True
            #     except Exception as e:
            #         print(f"Could not find the Więcej button by class name: {e}")

            # if not found_wiecej_button:
            #     # try moving mouse by 500 pixels to teh right from target_x and target_y
            #     print("Layer switcher (wiecej button) not found by class name, trying to move mouse.")
            #     OFFSET_X = 520
            #     self.driver.execute_script(
            #         f"""
            #         var event = new MouseEvent('mousemove', {{
            #             'view': window,
            #             'bubbles': true,
            #             'cancelable': true,
            #             'clientX': {target_x + OFFSET_X},
            #             'clientY': {target_y}
            #         }});
            #         document.elementFromPoint({target_x + OFFSET_X}, {target_y}).dispatchEvent(event);
            #     """
            #     )
            #     print(
            #         f"Moved cursor to position (x: {target_x + OFFSET_X}, y: {target_y})"
            #     )
            #     # press left mouse button down and instantly release it

            #     self.driver.execute_script(
            #         f"""
            #         var event = new MouseEvent('mousedown', {{
            #             'view': window,
            #             'bubbles': true,
            #             'cancelable': true,
            #             'clientX': {target_x + OFFSET_X},
            #             'clientY': {target_y}
            #         }});
            #         document.elementFromPoint({target_x + OFFSET_X}, {target_y}).dispatchEvent(event);
            #     """
            #     )
            #     self.driver.execute_script(
            #         f"""
            #         var event = new MouseEvent('mouseup', {{
            #             'view': window,
            #             'bubbles': true,
            #             'cancelable': true,
            #             'clientX': {target_x + OFFSET_X},
            #             'clientY': {target_y}
            #         }});
            #         document.elementFromPoint({target_x + OFFSET_X}, {target_y}).dispatchEvent(event);
            #     """
            #     )
            #     print(
            #         f"Clicked on layer switcher button by moving mouse to position (x: {target_x + OFFSET_X}, y: {target_y})"
            #     )

            # the layer switer executes jsaction layerswitcher.quick.more
            # so we can just execute it directly

            if not found_wiecej_button:
                try:
                    print("Layer switcher (wiecej button) not found, executing jsaction directly.")
                    self.driver.execute_script(
                        "document.querySelector('button[jsaction=\"layerswitcher.quick.more\"]').click();"
                    )
                    print("Clicked on layer switcher button by executing jsaction.")
                    found_wiecej_button = True
                except Exception as e:
                    print(f"Could not click on layer switcher button by executing jsaction: {e}")

            try:
                checkbox = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button[@role='checkbox' and .//label[contains(text(), 'Etykiety')]]",
                        )
                    )
                )
            except Exception as e:
                print(f"Could not find checkbox.")

            if checkbox:
                print("Checkbox found, checking its state...")
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
            "gb_Re",  # login button
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
        # self._click_accept()
        time.sleep(2)
        self._remove_elements_by_class()
        # time.sleep(1200)
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
            "d-flex gap-2",
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
