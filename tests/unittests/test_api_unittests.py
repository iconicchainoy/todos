from django.test import TestCase
from django.test import Client
from django.utils import timezone

from rest_framework.test import APIRequestFactory, APIClient, RequestsClient

from task import views as task_views
from task.models import Task, TaskCategory

import json

class GetCategories(TestCase):

    def setUp(self):
        
        self.client = RequestsClient()

    def test_status_code(self):
        """Expecting a status code 200 from the test url"""

        response = self.client.get('http://testserver/api/categories/')
        self.assertEqual(response.status_code, 200)
    
    def test_content_type(self):
        """Testing the content type"""
        
        response = self.client.get('http://testserver/api/categories/')
        self.assertEqual(response.status_code, 200)
        
        content_type = response.headers['Content-Type']
        self.assertEqual(content_type, "application/json")

    def test_response_without_data(self):
        """Testing what we get from an empty database"""

        response = self.client.get('http://testserver/api/categories/')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        length_of_response_data = len(response_data)
        self.assertEqual(length_of_response_data, 0)

    def test_response_with_data(self):
        """Checking the response with available data in the database"""
        
        TaskCategory.objects.create(name='test_work')
        TaskCategory.objects.create(name='test_home')

        response = self.client.get('http://testserver/api/categories/')
        response_data = json.loads(response.content)
        length_of_response_data = len(response_data)
        self.assertGreater(length_of_response_data, 0)
        
        response_keys = list(response_data[0].keys())
        expected_keys = ['id', 'name']
        self.assertEqual(response_keys, expected_keys)

        self.assertEqual(response_data[0]['name'], 'test_work')
        self.assertEqual(response_data[1]['name'], 'test_home')

class CreateCategory(TestCase):

    def setUp(self):
        
        self.client = RequestsClient()
        self.MAX_NAME_LENGTH = 255

    def test_status_code(self):
        """Expecting a status code 201 after api call"""

        data = {'name': 'test_category'}
        response = self.client.post('http://testserver/api/categories/create/', json=data)
        self.assertEqual(response.status_code, 201)

    def test_category_creation(self):
        """Testing if category creation is done"""
        data = {'name': 'test_category'}
        response = self.client.post('http://testserver/api/categories/create/', json=data)
        self.assertEqual(response.status_code, 201)

        response_data = json.loads(response.content)
        self.assertEqual(response_data['name'], 'test_category')

        response = self.client.get('http://testserver/api/categories/')
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data[0]['name'], 'test_category')
        
    def test_bad_payload(self):
        """Testing category creation with bad payload (not existing key)"""
        data = {'random': 'test_category'}
        response = self.client.post('http://testserver/api/categories/create/', json=data)
        self.assertEqual(response.status_code, 400)

    def test_wrong_method(self):
        """Testing category creation with bad payload (not existing key)"""
        data = {'name': 'test_category'}
        response = self.client.put('http://testserver/api/categories/create/', json=data)
        self.assertEqual(response.status_code, 405)

    def test_max_length_name(self):
        """Testing category creation with max length key"""
        max_len_name = 'x' * self.MAX_NAME_LENGTH
        data = {'name': max_len_name}
        response = self.client.post('http://testserver/api/categories/create/', json=data)
        self.assertEqual(response.status_code, 201)

        response = self.client.get('http://testserver/api/categories/')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertEqual(response_data[0]['name'], max_len_name)

    def test_too_long_name(self):
        """Testing category creation with key name length above limit"""
        too_long_name = 'x' * (self.MAX_NAME_LENGTH + 1)
        data = {'name': too_long_name}
        response = self.client.post('http://testserver/api/categories/create/', json=data)
        self.assertEqual(response.status_code, 400)

class EditCategory(TestCase):

    def setUp(self):
        
        self.client = RequestsClient()

    def test_status_code(self):
        """Expecting a status code 200 after api call"""

        TaskCategory.objects.create(name='test_work')
        data = {'name': 'test_home'}
        response = self.client.put('http://testserver/api/categories/edit/1', json=data)
        self.assertEqual(response.status_code, 200)

    def test_edit(self):
        """Testing if we can edit a category"""

        TaskCategory.objects.create(name='test_work')
        data = {'name': 'test_home'}
        response = self.client.put('http://testserver/api/categories/edit/1', json=data)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('http://testserver/api/categories/')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        length_of_response_data = len(response_data)
        self.assertGreater(length_of_response_data, 0)
        self.assertEqual(response_data[0]['name'], 'test_home')

    def test_editing_not_existing_id(self):
        """Testing if we can edit a not existing id"""

        TaskCategory.objects.create(name='test_work')
        data = {'name': 'test_home'}
        response = self.client.put('http://testserver/api/categories/edit/5', json=data)
        self.assertEqual(response.status_code, 404)

    def test_editing_not_existing_field(self):
        """Testing if we can edit a not existing field"""

        TaskCategory.objects.create(name='test_work')
        data = {'bad_key': 'test_home'}
        response = self.client.put('http://testserver/api/categories/edit/1', json=data)
        self.assertEqual(response.status_code, 400)

    def test_wrong_method(self):
        """Testing if we can edit a category with wrong method"""

        TaskCategory.objects.create(name='test_work')
        data = {'name': 'test_home'}
        response = self.client.post('http://testserver/api/categories/edit/1', json=data)
        self.assertEqual(response.status_code, 405)

class DeleteCategory(TestCase):
    
    def setUp(self):
        
        self.client = RequestsClient()

    def test_status_code(self):
        """Expecting a status code 204 after api call"""
        
        TaskCategory.objects.create(name='test_work')
        response = self.client.delete('http://testserver/api/categories/delete/1')
        self.assertEqual(response.status_code, 204)

    def test_delete(self):
        """Testing if we can delete a category"""

        TaskCategory.objects.create(name='test_work')

        response = self.client.get('http://testserver/api/categories/')
        self.assertEqual(response.status_code, 200)
        
        num_of_categories = len(json.loads(response.content))
        self.assertEqual(num_of_categories, 1)

        response = self.client.delete('http://testserver/api/categories/delete/1')
        self.assertEqual(response.status_code, 204)

        response = self.client.get('http://testserver/api/categories/')
        self.assertEqual(response.status_code, 200)
        
        num_of_categories = len(json.loads(response.content))
        self.assertEqual(num_of_categories, 0)

    def test_deleting_not_existing_id(self):
        """Testing if we can delete a not existing id"""

        TaskCategory.objects.create(name='test_work')
        data = {'name': 'test_home'}
        response = self.client.delete('http://testserver/api/categories/delete/5')
        self.assertEqual(response.status_code, 404)

    def test_wrong_method(self):
        """Testing if we can delete a category with wrong method"""

        TaskCategory.objects.create(name='test_work')
        data = {'name': 'test_home'}
        response = self.client.post('http://testserver/api/categories/delete/1', json=data)
        self.assertEqual(response.status_code, 405)

        response = self.client.put('http://testserver/api/categories/delete/1', json=data)
        self.assertEqual(response.status_code, 405)

class GetTasks(TestCase):

    def setUp(self):
        
        self.client = RequestsClient()

    def test_status_code(self):
        """Expecting a status code 200 from the test url"""

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)
    
    def test_content_type(self):
        """Testing the content type"""
        
        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)
        
        content_type = response.headers['Content-Type']
        self.assertEqual(content_type, "application/json")

    def test_response_without_data(self):
        """Testing what we get from an empty database"""

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        length_of_response_data = len(response_data)
        self.assertEqual(length_of_response_data, 0)

    def test_response_with_data(self):
        """Checking the response with available data in the database"""
        
        category = TaskCategory.objects.create(name='test_work')
        Task.objects.create(
            category=category,
            title='Test Title',
            description='Test Description',
            deadline='2023-12-08'
        )

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        length_of_response_data = len(response_data)
        self.assertGreater(length_of_response_data, 0)

        response_keys = list(response_data[0].keys()).sort()
        expected_keys = ['id', 'category', 'title', 'description', 'deadline'].sort()
        self.assertEqual(response_keys, expected_keys)

        self.assertEqual(response_data[0]['title'], 'Test Title')
        self.assertEqual(response_data[0]['description'], 'Test Description')
        self.assertEqual(response_data[0]['deadline'], '2023-12-08')       
    
class CreateTask(TestCase):

    def setUp(self):
        
        self.client = RequestsClient()
        self.MAX_NAME_LENGTH = 255

    def test_status_code(self):
        """Expecting a status code 201 after api call"""

        TaskCategory.objects.create(name='test_work')
        data = {
            'category': 1,
            'title': 'Test Title',
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }
            
        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 201)

    def test_task_creation(self):
        """Testing if task creation is done"""
        
        TaskCategory.objects.create(name='test_work')
        test_category = {'id':1, 'name':'test_work'}
        data = {
            'category': 1,
            'title': 'Test Title',
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }

        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 201)

        response_data = json.loads(response.content)
        self.assertEqual(response_data['category'], 1)
        self.assertEqual(response_data['title'], 'Test Title')
        self.assertEqual(response_data['description'], 'Test Description')
        self.assertEqual(response_data['deadline'], '2023-12-08')

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data[0]['id'], 1)
        self.assertEqual(response_data[0]['category'], test_category)
        self.assertEqual(response_data[0]['title'], 'Test Title')
        self.assertEqual(response_data[0]['description'], 'Test Description')
        self.assertEqual(response_data[0]['deadline'], '2023-12-08')

    def test_task_creation_titleless(self):
        """Testing if task creation is done without a title or an empty title"""
        
        TaskCategory.objects.create(name='test_work')
        test_category = {'id':1, 'name':'test_work'}
        data = {
            'category': 1,
            'title': '',
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }

        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 201)

        response_data = json.loads(response.content)
        self.assertEqual(response_data['category'], 1)
        self.assertEqual(response_data['title'], '')
        self.assertEqual(response_data['description'], 'Test Description')
        self.assertEqual(response_data['deadline'], '2023-12-08')

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data[0]['id'], 1)
        self.assertEqual(response_data[0]['category'], test_category)
        self.assertEqual(response_data[0]['title'], '')
        self.assertEqual(response_data[0]['description'], 'Test Description')
        self.assertEqual(response_data[0]['deadline'], '2023-12-08')  

        test_category = {'id':1, 'name':'test_work'}
        data = {
            'category': 1,
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }

        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 201)

        response_data = json.loads(response.content)
        self.assertEqual(response_data['category'], 1)
        self.assertEqual(response_data['title'], '')
        self.assertEqual(response_data['description'], 'Test Description')
        self.assertEqual(response_data['deadline'], '2023-12-08')

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data[0]['id'], 1)
        self.assertEqual(response_data[0]['category'], test_category)
        self.assertEqual(response_data[0]['title'], '')
        self.assertEqual(response_data[0]['description'], 'Test Description')
        self.assertEqual(response_data[0]['deadline'], '2023-12-08')  

    def test_bad_payload_keys(self):
        """Testing task creation with bad payload (keys)"""
        
        TaskCategory.objects.create(name='test_work')

        data = {
            'xxx': 1,
            'title': 'Test Title',
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }

        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 400)

        data = {
            'category': 1,
            'title': 'Test Title',
            'xxx': 'Test Description',
            'deadline': '2023-12-08'
        }

        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 400)

        data = {
            'category': 1,
            'title': 'Test Title',
            'description': 'Test Description',
            'xxx': '2023-12-08'
        }

        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 400)

    def test_bad_payload_keys(self):
        """Testing task creation with bad payload (values)"""
        TaskCategory.objects.create(name='test_work')

        data = {
            'category': "5",
            'title': 'Test Title',
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }

        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 400)

        data = {
            'category': 1,
            'title': 'x' * (self.MAX_NAME_LENGTH + 1),
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }

        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 400)

        data = {
            'category': 1,
            'title': 'Test Title',
            'description': 'Test Description',
            'deadline': 'xxx'
        }

        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 400)

    def test_max_length_name(self):
        """Testing task creation with max length key"""

        TaskCategory.objects.create(name='test_work')
        max_len_name = 'x' * self.MAX_NAME_LENGTH
        data = {
            'category': 1,
            'title': max_len_name,
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }

        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 201)

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        self.assertEqual(response_data[0]['title'], max_len_name)

class EditTask(TestCase):

    def setUp(self):
        
        self.client = RequestsClient()

    def test_status_code(self):
        """Expecting a status code 200 after api call"""

        category = TaskCategory.objects.create(name='test_work')
        Task.objects.create(
            category=category,
            title='Test Title',
            description='Test Description',
            deadline='2023-12-08'
        )
        
        data = {
            'category':1,
            'id':1,
            'title': 'Updated Title',
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }
        response = self.client.put('http://testserver/api/tasks/edit/1', json=data)
        self.assertEqual(response.status_code, 200)

    def test_edit(self):
        """Testing if we can edit a task"""

        category = TaskCategory.objects.create(name='test_work')
        Task.objects.create(
            category=category,
            title='Test Title',
            description='Test Description',
            deadline='2023-12-08'
        )
        
        data = {
            'category':1,
            'id':1,
            'title': 'Updated Title',
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }

        response = self.client.put('http://testserver/api/tasks/edit/1', json=data)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        length_of_response_data = len(response_data)
        self.assertGreater(length_of_response_data, 0)
        self.assertEqual(response_data[0]['title'], 'Updated Title')

    def test_editing_not_existing_id(self):
        """Testing if we can edit a not existing id"""

        category = TaskCategory.objects.create(name='test_work')
        Task.objects.create(
            category=category,
            title='Test Title',
            description='Test Description',
            deadline='2023-12-08'
        )
        
        data = {
            'category':1,
            'id':1,
            'title': 'Updated Title',
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }

        response = self.client.put('http://testserver/api/tasks/edit/5', json=data)
        self.assertEqual(response.status_code, 404)

    def test_editing_not_existing_field(self):
        """Testing if we can edit a not existing field"""

        category = TaskCategory.objects.create(name='test_work')
        Task.objects.create(
            category=category,
            title='Test Title',
            description='Test Description',
            deadline='2023-12-08'
        )
        
        data = {
            'category':1,
            'id':1,
            'title': 'Test Title',
            'xxx': 'Test Description',
            'deadline': '2023-12-08'
        }

        response = self.client.put('http://testserver/api/tasks/edit/1', json=data)
        self.assertEqual(response.status_code, 400)

class DeleteTask(TestCase):
    
    def setUp(self):
        
        self.client = RequestsClient()

    def test_status_code(self):
        """Expecting a status code 204 after api call"""
        
        TaskCategory.objects.create(name='test_work')
        data = {
            'category': 1,
            'title': 'Test Title',
            'description': 'Test Description',
            'deadline': '2023-12-08'
        }
            
        response = self.client.post('http://testserver/api/tasks/create/', json=data)
        self.assertEqual(response.status_code, 201)

        response = self.client.delete('http://testserver/api/categories/delete/1')
        self.assertEqual(response.status_code, 204)

    def test_delete(self):
        """Testing if we can delete a task"""

        category = TaskCategory.objects.create(name='test_work')
        Task.objects.create(
            category=category,
            title='Test Title',
            description='Test Description',
            deadline='2023-12-08'
        )

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)
        
        num_of_tasks = len(json.loads(response.content))
        self.assertEqual(num_of_tasks, 1)

        response = self.client.delete('http://testserver/api/tasks/delete/1')
        self.assertEqual(response.status_code, 204)

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)
        
        num_of_tasks = len(json.loads(response.content))
        self.assertEqual(num_of_tasks, 0)

    def test_deleting_not_existing_id(self):
        """Testing if we can delete a not existing id"""

        category = TaskCategory.objects.create(name='test_work')
        Task.objects.create(
            category=category,
            title='Test Title',
            description='Test Description',
            deadline='2023-12-08'
        )

        response = self.client.delete('http://testserver/api/tasks/delete/5')
        self.assertEqual(response.status_code, 404)

    def test_wrong_method(self):
        """Testing if we can delete a category with wrong method"""

        category = TaskCategory.objects.create(name='test_work')
        Task.objects.create(
            category=category,
            title='Test Title',
            description='Test Description',
            deadline='2023-12-08'
        )
        
        response = self.client.post('http://testserver/api/tasks/delete/1')
        self.assertEqual(response.status_code, 405)

        response = self.client.put('http://testserver/api/tasks/delete/1')
        self.assertEqual(response.status_code, 405)

class GetCategoryTasks(TestCase):

    def setUp(self):
        
        self.client = RequestsClient()

    def test_status_code(self):
        
        category = TaskCategory.objects.create(name='test_work')
        Task.objects.create(
            category=category,
            title='Test Title',
            description='Test Description',
            deadline='2023-12-08'
        )

        response = self.client.get('http://testserver/api/category_tasks/1')
        self.assertEqual(response.status_code, 200)

    def test_content_type(self):
        
        category = TaskCategory.objects.create(name='test_work')
        Task.objects.create(
            category=category,
            title='Test Title',
            description='Test Description',
            deadline='2023-12-08'
        )

        response = self.client.get('http://testserver/api/category_tasks/1')
        self.assertEqual(response.status_code, 200)
        
        content_type = response.headers['Content-Type']
        self.assertEqual(content_type, "application/json")

    def test_respone_without_data(self):
        """Testing what we get from an empty database"""

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        length_of_response_data = len(response_data)
        self.assertEqual(length_of_response_data, 0)

    def test_respone_with_data(self):
        """Checking the response with available data in the database"""
        
        category = TaskCategory.objects.create(name='test_work')
        Task.objects.create(
            category=category,
            title='Test Title',
            description='Test Description',
            deadline='2023-12-08'
        )

        response = self.client.get('http://testserver/api/tasks/')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.content)
        length_of_response_data = len(response_data)
        self.assertGreater(length_of_response_data, 0)

        response_keys = list(response_data[0].keys()).sort()
        expected_keys = ['id', 'category', 'title', 'description', 'deadline'].sort()
        self.assertEqual(response_keys, expected_keys)

        self.assertEqual(response_data[0]['title'], 'Test Title')
        self.assertEqual(response_data[0]['description'], 'Test Description')
        self.assertEqual(response_data[0]['deadline'], '2023-12-08')     