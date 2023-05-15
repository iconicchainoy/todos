from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumTest(StaticLiveServerTestCase):
    driver = None
    service = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = ChromeService(executable_path=ChromeDriverManager().install())
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--headless")
        cls.driver = webdriver.Chrome(service=cls.service, chrome_options=chrome_options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_page_available(self):
        self.driver.get("https://google.com")
        self.assertTrue("Google" in self.driver.title, self.driver.title)
