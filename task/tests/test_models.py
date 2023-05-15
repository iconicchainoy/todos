from django.test import TestCase
from task.models import TaskCategory, Task
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import date


class TaskCategoryTest(TestCase):

    def test_task_category_creation(self):
        name = "TC_name"
        tc = TaskCategory.objects.create(name=name)

        self.assertEqual(str(tc), name)
        tc.full_clean()

    def test_task_category_creation_failure(self):
        tc = TaskCategory.objects.create()
        with self.assertRaises(ValidationError) as e:
            tc.full_clean()
        self.assertTrue("blank" in e.exception.messages[0], e.exception.messages)

    def test_task_category_name_length_limit(self):
        name = "A" * 1000
        tc = TaskCategory.objects.create(name=name)

        self.assertEqual(len(str(tc)), 1000)
        with self.assertRaises(ValidationError) as e:
            tc.full_clean()
        self.assertTrue("255" in e.exception.messages[0], e.exception.messages)


class TaskTest(TestCase):

    def test_task_creation(self):
        title = "do something"
        descr = "blah-blah"
        d = date(1900, 1, 1)

        tc = TaskCategory.objects.create(name="My TODOs")
        t = Task.objects.create(category=tc, title=title, description=descr, deadline=d)

        self.assertEqual(str(t), title)
        self.assertEqual(t.description, descr)
        self.assertEqual(t.deadline, d)
        self.assertIsInstance(t.deadline, date)
        t.full_clean()

    def test_task_creation_with_long_description(self):
        title = "do something"
        descr = "blah-blah" * 255
        d = date(1900, 1, 1)

        tc = TaskCategory.objects.create(name="My TODOs")
        t = Task.objects.create(category=tc, title=title, description=descr, deadline=d)

        self.assertEqual(str(t), title)
        self.assertEqual(t.description, descr)
        self.assertEqual(t.deadline, d)
        self.assertIsInstance(t.deadline, date)
        t.full_clean()

    def test_task_creation_with_blank_title(self):
        descr = "blah-blah" * 255
        d = date(1900, 1, 1)

        tc = TaskCategory.objects.create(name="My TODOs")
        t = Task.objects.create(category=tc, description=descr, deadline=d)

        self.assertEqual(t.description, descr)
        self.assertEqual(t.deadline, d)
        self.assertIsInstance(t.deadline, date)
        t.full_clean()

    def test_task_creation_failure_no_category(self):
        title = "do something"
        descr = "blah-blah" * 255
        d = date(1900, 1, 1)

        with self.assertRaises(IntegrityError) as e:
            t = Task.objects.create(title=title, description=descr, deadline=d)
            t.full_clean()
        self.assertTrue("category" in str(e.exception))

    def test_task_creation_failure_no_description(self):
        title = "do something"
        d = date(1900, 1, 1)

        tc = TaskCategory.objects.create(name="My TODOs")

        with self.assertRaises(ValidationError) as e:
            t = Task.objects.create(category=tc, title=title, deadline=d)
            t.full_clean()
        self.assertTrue("blank" in e.exception.messages[0], e.exception.messages)

    def test_task_creation_failure_no_date(self):
        title = "do something"
        descr = "blah-blah"

        tc = TaskCategory.objects.create(name="My TODOs")

        with self.assertRaises(IntegrityError) as e:
            t = Task.objects.create(category=tc, title=title, description=descr)
            t.full_clean()
        self.assertTrue("deadline" in str(e.exception))

    def test_task_creation_failure_malformed_date(self):
        title = "do something"
        descr = "blah-blah" * 255
        d = "1234-34-34"

        tc = TaskCategory.objects.create(name="My TODOs")
        with self.assertRaises(ValidationError) as e:
            t = Task.objects.create(category=tc, title=title, description=descr, deadline=d)
            t.full_clean()

        self.assertTrue("invalid date" in e.exception.messages[0], e.exception.messages)

    def test_task_creation_failure_title_length_limit(self):
        title = "do something" * 255
        descr = "blah-blah"
        d = date(1900, 1, 1)

        tc = TaskCategory.objects.create(name="My TODOs")
        t = Task.objects.create(category=tc, title=title, description=descr, deadline=d)

        self.assertEqual(str(t), title)
        self.assertEqual(t.description, descr)
        self.assertEqual(t.deadline, d)
        self.assertIsInstance(t.deadline, date)
        with self.assertRaises(ValidationError) as e:
            t.full_clean()
        self.assertTrue("255 characters" in e.exception.messages[0], e.exception.messages)

    def test_category_deletion(self):
        title1 = "do something"
        title2 = "do something else"
        descr = "blah-blah"
        d = date(1900, 1, 1)

        tc = TaskCategory.objects.create(name="My TODOs")

        t = Task.objects.create(category=tc, title=title1, description=descr, deadline=d)
        t.full_clean()
        t = Task.objects.create(category=tc, title=title2, description=descr, deadline=d)
        t.full_clean()

        number_of_deleted_object, numbers_by_type = tc.delete()
        self.assertEqual(number_of_deleted_object, 3)
        self.assertEqual(numbers_by_type['task.Task'], 2)
