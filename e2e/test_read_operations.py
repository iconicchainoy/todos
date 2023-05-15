from datetime import date
from time import sleep

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import visibility_of_element_located, element_to_be_clickable
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from task.models import TaskCategory, Task


class TestReadOperations(StaticLiveServerTestCase):
    port = 8000
    driver = None
    service = None
    expected_category_names = ["School", "Work", "Other", "Christmas"]
    expected_task_titles = {"School": ["Math HW", "Literature HW"], "Other": ["Get milk"]}

    @staticmethod
    def _create_test_task(tcs, c, title):
        c = next(filter(lambda category: category.name == c, tcs))
        return Task.objects.create(category=c, title=title, description="", deadline=date.today().strftime('%Y-%m-%d'))

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
        cls.wait = WebDriverWait(cls.driver, 20)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        task_categories_created = [TaskCategory.objects.create(name=ct_name) for ct_name in
                                   self.expected_category_names]
        [TestReadOperations._create_test_task(task_categories_created, tc, title) for (tc, titles) in
         self.expected_task_titles.items() for title in titles]

    def _select_nth_from_dropdown(self, n):
        sleep(.1)
        self.driver.get(self.live_server_url)
        sleep(1)
        dropdown = self.driver.find_element(By.CLASS_NAME, "dropdown")
        self.assertIsNotNone(dropdown)
        dropdown.click()
        sleep(1)
        elements = self.driver.find_elements(By.CSS_SELECTOR, "div[role=option]")
        self.wait.until(element_to_be_clickable(elements[n]))
        elements[n].click()
        sleep(.1)

    def test_dropdown_has_default_values(self):
        self.driver.get(self.live_server_url)
        dropdown = self.driver.find_element(By.CLASS_NAME, "dropdown")
        self.assertIsNotNone(dropdown)

        actual_categories = list(
            map(lambda element: element.get_attribute('innerHTML'),
                self.driver.find_elements(By.CSS_SELECTOR, ".item span.text")))

        self.assertCountEqual(actual_categories, self.expected_category_names, actual_categories)

    def test_dropdown_entry_is_selectable(self):
        first_category_idx = 0
        actual_selected_category, category_title_selector = self._selected_category_name(first_category_idx)
        expected_selected_category = self.expected_category_names[first_category_idx]

        self.assertEqual(actual_selected_category, expected_selected_category,
                         self.driver.find_element(By.CSS_SELECTOR, category_title_selector))

    def _selected_category_name(self, category_idx):
        self._select_nth_from_dropdown(category_idx)
        category_title_selector = "div.ui.divided.padded.grid > div > h2"
        self.wait.until(visibility_of_element_located((By.CSS_SELECTOR, category_title_selector)))
        actual_selected_entry = self.driver.find_element(By.CSS_SELECTOR, category_title_selector).get_attribute(
            'innerHTML')
        return actual_selected_entry, category_title_selector

    def test_tasks_show_up_under_category(self):
        self._select_nth_from_dropdown(0)

        category_title_selector = "#todos-wrapper > div > div > table"
        self.wait.until(visibility_of_element_located((By.CSS_SELECTOR, category_title_selector)))
        first_row_selector = "#todos-wrapper > div > div > table > tbody > tr:nth-child(1)"
        second_row_selector = "#todos-wrapper > div > div > table > tbody > tr:nth-child(2)"
        first_row = self.driver.find_element(By.CSS_SELECTOR, first_row_selector)
        second_row = self.driver.find_element(By.CSS_SELECTOR, second_row_selector)
        first_row_content = list(map(lambda element: element.text, first_row.find_elements(By.CSS_SELECTOR, "td")))
        second_row_content = list(map(lambda element: element.text, second_row.find_elements(By.CSS_SELECTOR, "td")))

        first_category = self.expected_category_names[0]
        expected_first_row = self.expected_task_titles[first_category][0]
        expected_second_row = self.expected_task_titles[first_category][1]

        self.assertTrue(expected_first_row in first_row_content, first_row_content)
        self.assertTrue(expected_second_row in second_row_content, second_row_content)

    def test_switching_categories(self):
        first_category_idx = 0
        actual_selected_category, category_title_selector = self._selected_category_name(first_category_idx)
        expected_selected_category = self.expected_category_names[first_category_idx]

        self.assertEqual(actual_selected_category, expected_selected_category,
                         self.driver.find_element(By.CSS_SELECTOR, category_title_selector))

        second_category_idx = 1
        actual_selected_category, category_title_selector = self._selected_category_name(second_category_idx)
        expected_selected_category = self.expected_category_names[second_category_idx]

        self.assertEqual(actual_selected_category, expected_selected_category,
                         self.driver.find_element(By.CSS_SELECTOR, category_title_selector))
