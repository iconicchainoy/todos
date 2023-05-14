from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class SanityTest(StaticLiveServerTestCase):
    port = 8000
    driver = None
    service = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.service = ChromeService(executable_path=ChromeDriverManager().install())
        cls.driver = webdriver.Chrome(service=cls.service)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_page_available(self):
        self.driver.get(self.live_server_url)
        self.assertTrue("TODOs" in self.driver.title, self.driver.title)
        dropdown = self.driver.find_element(By.CLASS_NAME, "dropdown")
        self.assertIsNotNone(dropdown)
        default_text = dropdown.find_element(By.CLASS_NAME, "default").get_attribute('innerHTML')
        self.assertTrue("category" in default_text, default_text)
