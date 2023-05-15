import json
from datetime import date

from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.forms.models import model_to_dict
from rest_framework import status
from task.models import TaskCategory, Task
from task import views


class CategoriesTest(TestCase):
    client = Client()

    def test_get_categories_when_none_is_defined(self):
        response = self.client.get(reverse(views.get_categories))

        self.assertEqual(response.status_code, 200)
        # couldn't find a better way to assert that no records should be returned
        self.assertEqual(response.content, b'[]')

    def test_get_categories_when_some_exists(self):
        category_1 = TaskCategory.objects.create(name="TC1")
        category_2 = TaskCategory.objects.create(name="TC2")
        category_3 = TaskCategory.objects.create(name="TC3")
        category_1.save()
        category_2.save()
        category_3.save()

        response = self.client.get(reverse(views.get_categories))

        self.assertContains(response, category_1, status_code=200)
        self.assertContains(response, category_2, status_code=200)
        self.assertContains(response, category_3, status_code=200)


class CategoriesCreateTest(TestCase):
    client = Client()

    def test_create_category_success(self):
        name = "TC1"
        response = self.client.post(reverse(views.create_category), {"name": name})

        # I don't think it matters what kind of 2xx is returned, thus the convoluted assertion
        self.assertTrue(status.is_success(response.status_code), response)
        self.assertTrue(name in response.content.decode("utf-8"), response.content)
        self.assertEqual(TaskCategory.objects.all()[0].name, name)

    def test_create_category_failure_incorrect_data(self):
        name = "TC1"
        response = self.client.post(reverse(views.create_category), {"tag": name})
        self.assertEqual(response.status_code, 400)
        self.assertTrue("name" in response.content.decode("utf-8"), response.content)
        self.assertQuerysetEqual(TaskCategory.objects.all(), [])


class CategoriesEditTest(TestCase):
    client = Client()
    default_tc_name = "TC1"

    def setUp(self):
        category = TaskCategory.objects.create(name=self.default_tc_name)
        category.save()

    def test_edit_category_successful(self):
        existing_tc = TaskCategory.objects.filter(name=self.default_tc_name).values()[0]
        category_id = existing_tc["id"]
        new_category_name = "I'm a new category"
        new_category = TaskCategory.objects.create(name=new_category_name)

        response = self.client.put(reverse(views.edit_category, kwargs={"category_id": category_id}),
                                   data=model_to_dict(new_category), content_type='application/json')

        self.assertContains(response, new_category_name)
        self.assertEqual(TaskCategory.objects.all()[0].name, new_category_name)

    def test_edit_category_nonexistent(self):
        expected_categories = list(TaskCategory.objects.all())
        new_category_name = "I'm a new category"

        response = self.client.put(reverse(views.edit_category, kwargs={"category_id": 9999999}),
                                   data={"name": new_category_name}, content_type='application/json')

        actual_categories = list(TaskCategory.objects.all())
        self.assertTrue(status.is_client_error(response.status_code), response)
        self.assertTrue("Not found" in response.content.decode("utf-8"), response.content)
        self.assertListEqual(actual_categories, expected_categories)

    def test_edit_category_failure_incorrect_fields(self):
        expected_categories = list(TaskCategory.objects.all())
        existing_tc = TaskCategory.objects.filter(name=self.default_tc_name).values()[0]
        category_id = existing_tc["id"]

        response = self.client.put(reverse(views.edit_category, kwargs={"category_id": category_id}),
                                   data={"this": "is", "something": "bad"}, content_type='application/json')

        actual_categories = list(TaskCategory.objects.all())
        self.assertTrue(status.is_client_error(response.status_code), response)
        self.assertTrue("name" in response.content.decode("utf-8"), response.content)
        self.assertListEqual(actual_categories, expected_categories)


class CategoriesDeleteTest(TestCase):
    client = Client()
    default_tc_name = "TC1"

    def setUp(self):
        category = TaskCategory.objects.create(name=self.default_tc_name)
        category.save()

    def test_delete_category_successful(self):
        existing_tc = TaskCategory.objects.filter(name=self.default_tc_name).values()[0]
        category_id = existing_tc["id"]

        response = self.client.delete(reverse(views.delete_category, kwargs={"category_id": category_id}),
                                      data={})

        self.assertTrue(status.is_success(response.status_code), response)
        self.assertQuerysetEqual(TaskCategory.objects.all(), [])

    def test_delete_category_delete_only_selected(self):
        existing_tc = TaskCategory.objects.filter(name=self.default_tc_name).values()[0]
        category_id = existing_tc["id"]
        second_category_name = "2nd cat"
        category2 = TaskCategory.objects.create(name=second_category_name)
        category2.save()

        response = self.client.delete(reverse(views.delete_category, kwargs={"category_id": category_id}),
                                      data={})

        remaining_tc = TaskCategory.objects.all().values()
        self.assertEqual(len(remaining_tc), 1)
        self.assertTrue(status.is_success(response.status_code), response)
        self.assertEqual(remaining_tc[0]["name"], second_category_name)

    def test_delete_category_non_existent(self):
        expected_categories = list(TaskCategory.objects.all())

        response = self.client.delete(reverse(views.delete_category, kwargs={"category_id": 99999}),
                                      data={})

        actual_categories = list(TaskCategory.objects.all())
        self.assertTrue(status.is_client_error(response.status_code), response)
        self.assertListEqual(actual_categories, expected_categories)


class CategoryTasksTest(TestCase):
    client = Client()
    default_tc_name = "TC1"
    task_name_1 = "title1"
    task_name_2 = "title2"
    default_task_1 = None
    default_task_2 = None

    def setUp(self):
        category = TaskCategory.objects.create(name=self.default_tc_name)
        category.save()
        self.default_task_1 = Task.objects.create(category=category, title=self.task_name_1, description="descr1",
                                                  deadline=date(1990, 1, 1))
        self.default_task_2 = Task.objects.create(category=category, title=self.task_name_2, description="descr2",
                                                  deadline=date(1990, 1, 1))
        self.default_task_1.save()
        self.default_task_2.save()

    def test_category_has_tasks(self):
        existing_tc = TaskCategory.objects.filter(name=self.default_tc_name).values()[0]
        category_id = existing_tc["id"]

        response = self.client.get(reverse(views.get_category_tasks, kwargs={"category_id": category_id}))
        tasks = json.loads(response.content)
        expected_tasks = [model_to_dict(self.default_task_1), model_to_dict(self.default_task_2)]

        self.assertEqual(response.status_code, 200, response)
        self.assertEqual(len(tasks), len(expected_tasks))

        for t, e_t in zip(tasks, expected_tasks):
            # returned object has a category instance, not just an id, getting rid of it
            t["category"] = category_id
            e_t["deadline"] = str(e_t["deadline"])
            self.assertDictEqual(t, e_t)

    def test_category_is_empty(self):
        category = TaskCategory.objects.create(name="empty")
        category.save()
        existing_tc = TaskCategory.objects.filter(name="empty").values()[0]
        category_id = existing_tc["id"]

        response = self.client.get(reverse(views.get_category_tasks, kwargs={"category_id": category_id}))

        self.assertEqual(response.status_code, 200, response)
        tasks = json.loads(response.content)
        self.assertEqual(len(tasks), 0)

    def test_category_not_exists(self):
        response = self.client.get(reverse(views.get_category_tasks, kwargs={"category_id": 99999}))

        self.assertTrue(status.is_client_error(response.status_code), response)

    def test_category_is_large(self):
        # might want to convert this a proper performance test and run it separately
        large_category_name = "Large category"
        large_category = TaskCategory.objects.create(name=large_category_name)
        large_category.save()
        existing_tc = TaskCategory.objects.filter(name=large_category_name).values()[0]
        category_id = existing_tc["id"]
        num_of_tasks = 10000
        for _ in range(num_of_tasks):
            Task.objects.create(category=large_category, title="My name is Legion", description="for we are many",
                                deadline=date(1990, 1, 1)).save()

        response = self.client.get(reverse(views.get_category_tasks, kwargs={"category_id": category_id}))
        tasks = json.loads(response.content)

        self.assertEqual(response.status_code, 200, response)
        self.assertEqual(len(tasks), num_of_tasks)


class TasksTest(TestCase):
    client = Client()

    def test_get_tasks_when_exists(self):
        tc1 = "TC1"
        tc2 = "TC2"
        category1 = TaskCategory.objects.create(name=tc1)
        category1.save()
        category2 = TaskCategory.objects.create(name=tc2)
        category2.save()

        title1 = "title1"
        self.task1 = Task.objects.create(category=category1, title=title1, description="descr1",
                                         deadline=date(1990, 1, 1))
        title2 = "title2"
        self.task2 = Task.objects.create(category=category1, title=title2, description="descr2",
                                         deadline=date(1990, 1, 1))
        self.task1.save()
        self.task2.save()

        title3 = "title3"
        self.task3 = Task.objects.create(category=category2, title=title3, description="descr3",
                                         deadline=date(1990, 1, 1))
        self.task3.save()

        response = self.client.get(reverse(views.get_tasks))
        tasks = json.loads(response.content)

        self.assertContains(response, tc1)
        self.assertContains(response, tc2)
        self.assertContains(response, title1)
        self.assertContains(response, title2)
        self.assertContains(response, title2)
        self.assertEqual(len(tasks), 3)

    def test_no_tasks_only_categories(self):
        tc1 = "TC1"
        tc2 = "TC2"
        category1 = TaskCategory.objects.create(name=tc1)
        category1.save()
        category2 = TaskCategory.objects.create(name=tc2)
        category2.save()

        response = self.client.get(reverse(views.get_tasks))

        self.assertEqual(json.loads(response.content), [])


class TasksCreateTest(TestCase):
    client = Client()
    default_tc_name = "TC1"
    category_id = None

    def setUp(self):
        category = TaskCategory.objects.create(name=self.default_tc_name)
        category.save()
        existing_tc = TaskCategory.objects.filter(name=self.default_tc_name).values()[0]
        self.category_id = existing_tc["id"]

    def test_task_creation_successful(self):
        task = {"category": self.category_id, "title": "title1", "description": "description", "deadline": "1900-01-01"}

        response = self.client.post(reverse(views.create_task), task)

        self.assertDictEqual(json.loads(response.content), task)
        self.assertTrue(status.is_success(response.status_code), response.status_code)
        self.assertEqual(Task.objects.filter(id=1).values()[0]["title"], task["title"])

    def test_creation_successful_wo_title(self):
        task = {"category": self.category_id, "description": "description", "deadline": "1900-01-01"}

        response = self.client.post(reverse(views.create_task), task)

        expected_task = task
        expected_task["title"] = ''
        self.assertDictEqual(json.loads(response.content), expected_task)
        self.assertTrue(status.is_success(response.status_code), response.status_code)
        self.assertEqual(Task.objects.filter(id=1).values()[0]["title"], expected_task["title"])

    def test_task_creation_failed_bad_title(self):
        expected_tasks = list(Task.objects.all())
        task = {"category": self.category_id, "title": "aa" * 255, "description": "description" * 255,
                "deadline": "1900-01-01"}

        response = self.client.post(reverse(views.create_task), task)

        self.assertTrue(status.is_client_error(response.status_code), response.status_code)
        self.assertTrue("title" in response.content.decode("utf-8"))
        actual_tasks = list(Task.objects.all())
        self.assertListEqual(actual_tasks, expected_tasks)

    def test_task_creation_failed_bad_category(self):
        expected_tasks = list(Task.objects.all())
        fake_id = 9999999999
        task = {"category": fake_id, "title": "title1", "description": "description", "deadline": "1900-01-01"}

        response = self.client.post(reverse(views.create_task), task)

        self.assertTrue(status.is_client_error(response.status_code), response.status_code)
        self.assertTrue("does not exist" in response.content.decode("utf-8"))
        self.assertTrue(str(fake_id) in response.content.decode("utf-8"))
        actual_tasks = list(Task.objects.all())
        self.assertListEqual(actual_tasks, expected_tasks)

    def test_task_creation_failed_bad_date(self):
        expected_tasks = list(Task.objects.all())
        task = {"category": self.category_id, "title": "aa", "description": "description",
                "deadline": "kitten"}

        response = self.client.post(reverse(views.create_task), task)

        self.assertTrue(status.is_client_error(response.status_code), response.status_code)
        self.assertTrue("deadline" in response.content.decode("utf-8"))
        actual_tasks = list(Task.objects.all())
        self.assertListEqual(actual_tasks, expected_tasks)


class TasksEditTest(TestCase):
    client = Client()
    default_tc_name = "TC1"
    category_id = None
    task_definition = None
    existing_task_id = None

    def setUp(self):
        category = TaskCategory.objects.create(name=self.default_tc_name)
        category.save()
        existing_tc = TaskCategory.objects.filter(name=self.default_tc_name).values()[0]
        self.category_id = existing_tc["id"]
        self.task_definition = {"category": self.category_id, "title": "title1", "description": "description",
                                "deadline": "1900-01-01"}

        _t = Task.objects.create(category=category, title=self.task_definition["title"],
                                 description=self.task_definition["description"],
                                 deadline=date(1990, 1, 1))
        _t.save()

        self.existing_task_id = _t.id

    def test_edit_task_no_change_successful(self):
        task_before_change = list(Task.objects.filter(id=self.existing_task_id))

        response = self.client.put(reverse(views.edit_task, kwargs={"task_id": self.existing_task_id}),
                                   self.task_definition,
                                   content_type="application/json")

        self.assertTrue(status.is_success(response.status_code), response.content)
        self.assertContains(response, self.task_definition["category"])
        self.assertContains(response, self.task_definition["title"])
        self.assertContains(response, self.task_definition["description"])
        self.assertContains(response, self.task_definition["deadline"])

        task_after_change = list(Task.objects.filter(id=self.existing_task_id))
        self.assertListEqual(task_before_change, task_after_change)

    def test_edit_task_change_successful(self):
        self.task_definition["title"] = "new_title"

        response = self.client.put(reverse(views.edit_task, kwargs={"task_id": self.existing_task_id}),
                                   self.task_definition,
                                   content_type="application/json")

        self.assertTrue(status.is_success(response.status_code), response.content)
        self.assertContains(response, self.task_definition["category"])
        self.assertContains(response, self.task_definition["title"])
        self.assertContains(response, self.task_definition["description"])
        self.assertContains(response, self.task_definition["deadline"])

        task_after_change = Task.objects.filter(id=self.existing_task_id).values()[0]
        self.assertEqual(task_after_change["title"], "new_title")

    def test_task_edit_successful_blank_title(self):
        self.task_definition["title"] = ""

        response = self.client.put(reverse(views.edit_task, kwargs={"task_id": self.existing_task_id}),
                                   self.task_definition,
                                   content_type="application/json")

        self.assertTrue(status.is_success(response.status_code), response.content)
        self.assertNotContains(response, "title1")
        self.assertContains(response, self.task_definition["category"])
        self.assertContains(response, self.task_definition["description"])
        self.assertContains(response, self.task_definition["deadline"])

        task_after_change = Task.objects.filter(id=self.existing_task_id).values()[0]
        self.assertEqual(task_after_change["title"], "")

    def test_edit_task_category_successful(self):
        # not sure if bug or feature, the UI doesn't expose this functionality
        tasks_before_change = list(Task.objects.all())
        new_category = TaskCategory.objects.create(name="other category")
        new_category.save()
        self.task_definition["category"] = 2

        response = self.client.put(reverse(views.edit_task, kwargs={"task_id": self.existing_task_id}),
                                   self.task_definition,
                                   content_type="application/json")

        self.assertTrue(status.is_success(response.status_code), response.content)
        self.assertContains(response, self.task_definition["category"])
        self.assertContains(response, self.task_definition["title"])
        self.assertContains(response, self.task_definition["description"])
        self.assertContains(response, self.task_definition["deadline"])

        tasks_after_change = list(Task.objects.all())
        task_after_change = Task.objects.filter(id=self.existing_task_id).values()[0]
        self.assertEqual(task_after_change["category_id"], self.task_definition["category"])
        # assert that the task was moved from one category to another and not duplicated with the new category
        self.assertEqual(len(tasks_before_change), len(tasks_after_change))

    def test_edit_task_failed_nonexistent_task(self):
        tasks_before_change = list(Task.objects.all())

        response = self.client.put(reverse(views.edit_task, kwargs={"task_id": 999999999}), self.task_definition,
                                   content_type="application/json")

        self.assertTrue(status.is_client_error(response.status_code), response.content)
        tasks_after_change = list(Task.objects.all())
        self.assertListEqual(tasks_before_change, tasks_after_change)

    def test_edit_task_failed_bad_category(self):
        tasks_before_change = list(Task.objects.all())
        self.task_definition["category"] = 2

        response = self.client.put(reverse(views.edit_task, kwargs={"task_id": self.existing_task_id}),
                                   self.task_definition,
                                   content_type="application/json")

        self.assertTrue(status.is_client_error(response.status_code), response.content)
        tasks_after_change = list(Task.objects.all())
        self.assertListEqual(tasks_before_change, tasks_after_change)

    def test_edit_task_failed_bad_title(self):
        tasks_before_change = list(Task.objects.all())
        self.task_definition["title"] = "new_title" * 255

        response = self.client.put(reverse(views.edit_task, kwargs={"task_id": self.existing_task_id}),
                                   self.task_definition,
                                   content_type="application/json")

        self.assertTrue(status.is_client_error(response.status_code), response.content)
        tasks_after_change = list(Task.objects.all())
        self.assertListEqual(tasks_before_change, tasks_after_change)

    def test_edit_task_failed_bad_date(self):
        tasks_before_change = list(Task.objects.all())
        self.task_definition["deadline"] = "kitten"

        response = self.client.put(reverse(views.edit_task, kwargs={"task_id": self.existing_task_id}),
                                   self.task_definition,
                                   content_type="application/json")

        self.assertTrue(status.is_client_error(response.status_code), response.content)
        tasks_after_change = list(Task.objects.all())
        self.assertListEqual(tasks_before_change, tasks_after_change)


class TasksDeleteTest(TestCase):
    client = Client()
    default_tc_name = "TC1"
    category_id = None
    task = None
    existing_task_id = None
    default_category = None

    def setUp(self):
        self.default_category = TaskCategory.objects.create(name=self.default_tc_name)
        self.default_category.save()
        existing_tc = TaskCategory.objects.filter(name=self.default_tc_name).values()[0]
        self.category_id = existing_tc["id"]
        self.task = {"category": self.category_id, "title": "title1", "description": "description",
                     "deadline": "1900-01-01"}

        _t = Task.objects.create(category=self.default_category, title=self.task["title"],
                                 description=self.task["description"],
                                 deadline=date(1990, 1, 1))
        _t.save()

        self.existing_task_id = _t.id

    def test_delete_existing_task(self):
        response = self.client.delete(reverse(views.delete_task, kwargs={"task_id": self.existing_task_id}), {})

        self.assertTrue(status.is_success(response.status_code), response.status_code)
        remaining_tasks = Task.objects.all()
        self.assertQuerysetEqual(remaining_tasks, [])

    def test_delete_task_delete_only_selected(self):
        Task.objects.create(category=self.default_category, title="other task",
                            description="other description",
                            deadline=date(1990, 1, 1)).save()

        response = self.client.delete(reverse(views.delete_task, kwargs={"task_id": self.existing_task_id}), {})

        self.assertTrue(status.is_success(response.status_code), response.status_code)
        remaining_task = Task.objects.all().values()[0]
        self.assertEqual(remaining_task["title"], "other task")

    def test_delete_nonexistent_task(self):
        tasks_before_delete = list(Task.objects.all())
        response = self.client.delete(reverse(views.delete_task, kwargs={"task_id": 99999999}), {})

        self.assertTrue(status.is_client_error(response.status_code), response.status_code)
        remaining_tasks = list(Task.objects.all())
        self.assertListEqual(remaining_tasks, tasks_before_delete)
