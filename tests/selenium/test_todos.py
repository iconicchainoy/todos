import time
import unittest
from unittest import skip

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

# Notes:
# - To execute these tests you have to run the server already

URL = "http://localhost:8000/"

class HomePage:

    def __init__(self, webDriver):
        
        self.wd = webDriver
        
        self.category_dropdown_closed = (By.CLASS_NAME, "ui.selection.dropdown")
        self.category_dropdown_opened = (By.CLASS_NAME, "ui.active.visible.selection.dropdown")
        
        self.new_category_field = (By.CSS_SELECTOR, '[placeholder="New category"]')
        self.new_category_button = (By.CLASS_NAME, "ui.icon.button")

        # Currently there's no better option
        self.selected_category_container = (By.XPATH, "//div[@class='ui divided padded grid']/div/h2")
        self.delete_icon = (By.CLASS_NAME, "trash.alternate.icon")

        self.title_field = (By.XPATH, '//input[@name="title"]')
        self.description_field = (By.XPATH, '//input[@name="description"]')
        self.date_field = (By.XPATH, '//input[@placeholder="YYYY-M-D"]')
        self.add_task_button = (By.XPATH, '//button[text()="Add task"]')

        self.task_list = (By.XPATH, '//table[@class="ui violet table"]/tbody')

        self.save_changes_button = (By.XPATH, '//button[text()="Save changes"]')
        self.close_icon = (By.XPATH, '//button[@class="ui icon button"]/i[@class="close icon"]')

    def add_new_category(self, categoryName):
        """Writing new category name into the proper field and presses the add button"""
        
        new_category_field_we = self.wd.find_element(*self.new_category_field)
        WebDriverWait(self.wd, 5).until(EC.element_to_be_clickable(new_category_field_we))
        new_category_field_we.send_keys(categoryName)

        new_category_button_we = self.wd.find_element(*self.new_category_button)
        new_category_button_we.click()  

        time.sleep(1)

    def get_category_list(self):
        """Returns the list of the available categories"""

        category_list = []

        category_dropdown_we = self.wd.find_element(*self.category_dropdown_closed)
        WebDriverWait(self.wd, 5).until(EC.element_to_be_clickable(category_dropdown_we))
        category_dropdown_we.click()

        category_container_we = self.wd.find_element(By.CLASS_NAME, "menu.transition")
        we_list = category_container_we.find_elements(By.TAG_NAME, "div")
        for item in we_list:
            category_list.append(item.text)

        category_dropdown_we_opened = self.wd.find_element(*self.category_dropdown_opened)
        WebDriverWait(self.wd, 5).until(EC.element_to_be_clickable(category_dropdown_we_opened))
        category_dropdown_we_opened.click()

        return category_list

    def get_selected_category(self):
        """Returns the currently selected category's name"""

        selected_category_container_we = self.wd.find_element(*self.selected_category_container)
        WebDriverWait(self.wd, 5).until(EC.visibility_of(selected_category_container_we))
        return selected_category_container_we.text

    def get_tasks(self, category):
        """Returns available task objects for the given category"""
        
        tasks = []

        task_list_we = self.wd.find_element(*self.task_list)
        task_rows = task_list_we.find_elements(By.TAG_NAME, 'tr')

        if len(task_rows) > 1:
            # Last element is the new task form
            for row in task_rows[:-1]:
                task = row.find_elements(By.TAG_NAME, 'td')
                tasks.append({
                    "title":task[0].text, 
                    "desc":task[1].text, 
                    "date":task[2].text
                })

        return tasks

    def select_last_category(self):
        """Selects the last category in the dropdown menu"""

        category_dropdown_we = self.wd.find_element(*self.category_dropdown_closed)
        WebDriverWait(self.wd, 5).until(EC.element_to_be_clickable(category_dropdown_we))
        category_dropdown_we.click()

        category_container_we = self.wd.find_element(By.CLASS_NAME, "menu.transition")
        we_list = category_container_we.find_elements(By.TAG_NAME, "div")
        we_list[-1].click()

    def select_category(self, selectedCategory):
        """Selects the required category from the dropdown menu"""

        category_dropdown_we = self.wd.find_element(*self.category_dropdown_closed)
        WebDriverWait(self.wd, 5).until(EC.element_to_be_clickable(category_dropdown_we))
        category_dropdown_we.click()

        category_container_we = self.wd.find_element(By.CLASS_NAME, "menu.transition")
        we_list = category_container_we.find_elements(By.TAG_NAME, "div")
        for item in we_list:
            if item.text == selectedCategory:
                item.click()
                break

    def delete_selected_category(self):
        """Deletes the currently selected category by clicking on the trash icon"""
        
        delete_icon_we = self.wd.find_element(*self.delete_icon)
        delete_icon_we.click()
        time.sleep(1)

    def fill_task(self, title, description, date):
        """Filling the new task form"""

        title_field_we = self.wd.find_element(*self.title_field)
        desc_field_we = self.wd.find_element(*self.description_field)
        date_field_we = self.wd.find_element(*self.date_field)
        add_button_we = self.wd.find_element(*self.add_task_button)

        title_field_we.send_keys(title)
        desc_field_we.send_keys(description)
        if len(date):
            date_field_we.send_keys(date)
        add_button_we.click()

        time.sleep(1)

    def edit_task(self, identifier, update):
        """Editing a task in the edit form"""
        
        category = identifier[0]
        title = identifier[1]
        descr = identifier[2]

        new_title = update[0]
        new_desc = update[1]

        task_list_we = self.wd.find_element(*self.task_list)
        task_rows = task_list_we.find_elements(By.TAG_NAME, 'tr')

        if len(task_rows) > 1:
            for row in task_rows[:-1]:
                task = row.find_elements(By.TAG_NAME, 'td')
                if task[0].text == title:
                    buttons = task[3].find_elements(By.TAG_NAME, 'button')
                    # 0 - finish task
                    # 1 - edit task
                    buttons[1].click()
                    time.sleep(1)
                    break
        
        # Using 'dynamic' locators
        title_field_we = self.wd.find_element(*(By.XPATH, f"//input[@value='{title}']"))
        desc_field_we = self.wd.find_element(*(By.XPATH, f"//input[@value='{descr}']"))
        

        # TODO: Getting StaleElementReferenceException and behaves weird in the app as well
        title_field_we.clear()
        title_field_we.send_keys(new_title)
        
        desc_field_we.clear()
        desc_field_we.send_keys(new_desc)        

        save_changes_button_we = self.wd.find_element(*self.save_changes_button)
        save_changes_button_we.click()

        time.sleep(1)

    def finish_task(self, title):
        """Finishing a given task"""

        task_list_we = self.wd.find_element(*self.task_list)
        task_rows = task_list_we.find_elements(By.TAG_NAME, 'tr')

        if len(task_rows) > 1:
            for row in task_rows[:-1]:
                task = row.find_elements(By.TAG_NAME, 'td')
                if task[0].text == title:
                    buttons = task[3].find_elements(By.TAG_NAME, 'button')
                    # 0 - finish task
                    # 1 - edit task
                    buttons[0].click()
                    time.sleep(1)
                    break

class TestSuite(unittest.TestCase):

    def setUp(self):
        """Creating a Chrome webdriver for the test"""
        self.driver = webdriver.Chrome()
        self.driver.get(URL)
        self.page = HomePage(self.driver)

    def tearDown(self):
        """Closing the created webdriver"""
        self.driver.close()

    def test_check_title(self):
        """Checking if we have the right title on the site"""

        title = self.driver.title
        assert title == "TODOs"

    def test_select_category(self):
        """Test if we can select a category in the app with the dropdown menu"""

        test_category = "Work"
        
        self.page.select_category(test_category)
        selected_category = self.page.get_selected_category()
        assert selected_category == test_category

    def test_add_category(self):
        """Checking if we can add categories in the app"""
        
        category_name = "Test category"

        old_category_list = self.page.get_category_list()
        self.page.add_new_category(category_name)
        new_category_list = self.page.get_category_list()

        assert len(old_category_list) < len(new_category_list)
        assert category_name in new_category_list

    def test_delete_category(self):
        """Checking if we can delete categories in the app"""
        
        old_category_list = self.page.get_category_list()
        
        self.page.select_last_category()
        selected_category = self.page.get_selected_category()
        self.page.delete_selected_category()

        new_category_list = self.page.get_category_list()

        assert len(old_category_list) > len(new_category_list)

        diff = list(set(old_category_list) ^ set(new_category_list))
        assert diff[0] == selected_category

    def test_add_task(self):
        """Tests if we can add a task"""

        category = "Work"
        task_title = "Title"
        task_desc = "Desc"
        task_date = ""
        
        self.page.select_category(category)
        old_tasks = self.page.get_tasks(category)
        
        self.page.fill_task(
            title=task_title, 
            description=task_desc, 
            date=""
        )
        new_tasks = self.page.get_tasks(category)

        assert len(old_tasks) < len(new_tasks)

    @skip("Has problems with the edit fields")
    def test_edit_task(self):
        """Test if we can edit a task"""
        
        category = "Work"
        task_title = "Title"
        description = "Desc"
        identifier = (category, task_title, description)

        new_title = "Title2"
        new_desc = "Desc2"
        update = (new_title, new_desc)

        self.page.select_category(category)
        old_tasks = self.page.get_tasks(category)
        self.page.edit_task(identifier, update)
        new_tasks = self.page.get_tasks(category)

        old_titles = [x for x in old_tasks if task_title in x['title']]
        new_titles = [x for x in new_tasks if task_title in x['title']]

        assert len(old_titles) == 1
        assert len(new_titles) == 1

    def test_finish_task(self):
        """Test if we can remove a task from the app by 'finishing' it"""
        
        category = "Work"
        task_title = "Title"

        self.page.select_category(category)
        old_tasks = self.page.get_tasks(category)
        self.page.finish_task(task_title)
        new_tasks = self.page.get_tasks(category)
        
        assert len(old_tasks) > len(new_tasks)