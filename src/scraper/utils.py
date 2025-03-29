from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

def create_driver(headless: bool = True) -> webdriver.Chrome:
        """TODO"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
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
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        return driver
