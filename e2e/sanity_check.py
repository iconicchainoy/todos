import unittest

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class SanityTest(unittest.TestCase):
    service = None
    driver = None

    @classmethod
    def setUpClass(cls):
        cls.service = ChromeService(executable_path=ChromeDriverManager().install())

    def setUp(self):
        self.driver = webdriver.Chrome(service=SanityTest.service)

    def tearDown(self):
        if self.driver:
            self.driver.close()

    def test_page_available(self):
        self.driver.get("http://localhost:8000")
        self.assertTrue("TODOs" in self.driver.title, self.driver.title)
        dropdown = self.driver.find_element(By.CLASS_NAME, "dropdown")
        self.assertIsNotNone(dropdown)
        default_text = dropdown.find_element(By.CLASS_NAME, "default").get_attribute('innerHTML')
        self.assertTrue("category" in default_text, default_text)

