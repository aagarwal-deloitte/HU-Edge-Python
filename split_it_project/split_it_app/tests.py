from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from .models import Occasion, Event

REGISTER_USER_URL = reverse('split_it_app:register_users')
LOGIN_USER_URL = reverse('split_it_app:login_users')
OCCASION_URL = reverse('split_it_app:occasion-view-create')
EVENT_URL = reverse('split_it_app:event-view-create')

class RegisterApiTest(TestCase):
    """ This testcase tests the RegisterApi. """
    
    def setUp(self):
        self.user = get_user_model()
        self.client = APIClient()
        self.register_url = REGISTER_USER_URL
    
    def tearDown(self):
        self.user.objects.all().delete()
        
    def test_register_user_success(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.user.objects.filter(username='testuser').exists())
        self.assertTrue(self.user.objects.filter(email='testuser@example.com').exists())
        
    def test_register_user_fail(self):
        self.user.objects.create_user(
            username='existinguser',
            email='testuser@example.com',
            password='testpassword'
        )
        data = {
            'username': 'existinguser', # using the same username for new user.
            'email': 'testuser1@example.com',
            'password': 'newpassword'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.user.objects.filter(username='existinguser').count(), 1)
        
class LoginApiTest(TestCase):
    """ This testcase tests the LoginApi. """
    
    def setUp(self):
        self.user = get_user_model()
        self.client = APIClient()
        self.register_url = REGISTER_USER_URL
        self.login_url = LOGIN_USER_URL
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        self.client.post(self.register_url, data, format='json')
        
    def tearDown(self):
        self.user.objects.all().delete()
        
    def test_login_user_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(self.user.objects.filter(username='testuser').exists())
        self.assertTrue(self.user.objects.filter(email='testuser@example.com').exists())
        
    def test_login_user_wrong_credentials_fail(self):
        data = {
            'username': 'testuser', 
            'password': 'tesstpassword' # giving wrong password for the registered user.
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Invalid Credentials')
        
    def test_login_user_unregistered_user_fail(self):
        data = {
            'username': 'testuser1', 
            'password': 'testpassword1'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['message'], 'Invalid Credentials')
        
    def test_login_user_no_password_fail(self):
        data = {
            'username': 'testuser2'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field is required.', response.data['password'][0])
        
class OccasionApiTest(TestCase):
    """ This testcase tests the OccasionApi. """
    
    def setUp(self):
        self.user = get_user_model()
        self.occasion = Occasion
        self.client = APIClient()
        
        self.register_url = REGISTER_USER_URL
        self.login_url = LOGIN_USER_URL
        self.occasion_url = OCCASION_URL
        
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        self.client.post(self.register_url, data, format='json') # registering the user
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data, format='json') # logging in the user
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        self.occasion_data = {
            'description': 'testing occasion',
            'participants' : ["test1", "test2", "ab11c"]
        }
        
    def tearDown(self):
        self.user.objects.all().delete()
        self.occasion.objects.all().delete()
        
    def test_create_occasion_success(self):
        response = self.client.post(self.occasion_url, self.occasion_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.occasion.objects.filter(description='testing occasion').exists())
        self.assertIn('participants', response.data)
    
    def test_get_occasion_success(self):
        self.client.post(self.occasion_url, self.occasion_data, format='json') # creating a occasion
        response = self.client.get(self.occasion_url, self.occasion_data, format='json') # viewing the occasion
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.occasion.objects.filter(description='testing occasion').exists())
        self.assertIn('id', response.data[0])
        
    def test_create_duplicate_occasion_fail(self):
        self.client.post(self.occasion_url, self.occasion_data, format='json')
        response = self.client.post(self.occasion_url, self.occasion_data, format='json') # creating a duplicate occasion
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('occasion with this description already exists.', response.data['description'][0])
        
class EventApiTest(TestCase):
    """ This testcase tests the EventApi. """
    
    def setUp(self):
        self.user = get_user_model()
        self.occasion = Occasion
        self.event = Event
        self.client = APIClient()
        
        self.register_url = REGISTER_USER_URL
        self.login_url = LOGIN_USER_URL
        self.occasion_url = OCCASION_URL
        self.event_url = EVENT_URL
        
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        self.client.post(self.register_url, data, format='json') # registering the user
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data, format='json') # logging in the user
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token) # setting jwt token
        self.occasion_data = {
            'description': 'test occasion',
            'participants' : ["test1", "test2", "ab11c"]
        }
        
    def tearDown(self):
        self.user.objects.all().delete()
        self.occasion.objects.all().delete()
        
    def test_create_event_only_with_equal_split_success(self):
        data = {
            "description": "test event",
            "amount": 30,
            "expender": "test1",
            "utiliser" : ["test1", "test2"],
            "split_type": "equal"
        }
        expected_split = {'test1': 15.0, 'test2': 15.0}
        response = self.client.post(self.event_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.event.objects.filter(description='test event').exists())
        self.assertEqual(response.data['expense_split'], expected_split)
        
    def test_create_event_only_with_unequal_split_success(self):
        data = {
            "description": "test event",
            "amount": 30,
            "expender": "test1",
            "utiliser" : ["test1", "test2"],
            "split_type": "unequal",
            "split": [10, 20]
        }
        expected_split = {'test1': 10.0, 'test2': 20.0}
        response = self.client.post(self.event_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.event.objects.filter(description='test event').exists())
        self.assertEqual(response.data['expense_split'], expected_split)
        
    def test_create_event_with_occasion_with_equal_split_success(self):
        self.client.post(self.occasion_url, self.occasion_data, format='json')  # creating an occasion
        data = {
            "description": "test event",
            "amount": 150,
            "expender": "test1",
            "utiliser" : ["test1","test2"],
            "split_type": "equal",
            "occasion": "test occasion" # tagging the event to the created occasion
        } 
        expected_split = {'test1': 75.0, 'test2': 75.0}
        response = self.client.post(self.event_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('occasion_name', response.data)
        self.assertEqual(response.data['occasion_name'], 'test occasion')
        self.assertEqual(response.data['expense_split'], expected_split)
        
    def test_create_event_with_occasion_with_unequal_split_success(self):
        self.client.post(self.occasion_url, self.occasion_data, format='json')  # creating an occasion
        data = {
            "description": "test event",
            "amount": 150,
            "expender": "test1",
            "utiliser" : ["test1","test2", "ab11c"],
            "split_type": "unequal",
            "split": [80, 40, 30],
            "occasion": "test occasion" # tagging the event to the created occasion
        } 
        expected_split = {'test1': 80.0, 'test2': 40.0, "ab11c": 30.0}
        response = self.client.post(self.event_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('occasion_name', response.data)
        self.assertEqual(response.data['occasion_name'], 'test occasion')
        self.assertEqual(response.data['expense_split'], expected_split)
     
    def test_create_event_only_fail(self):
        data = {
            "description": "test event",
            "amount": 30,
            "expender": "test1",
            "utiliser" : ["test1", "test2"],
            "split_type": "equal"
        }
        self.client.post(self.event_url, data, format='json')
        response = self.client.post(self.event_url, data, format='json') # creating the same event again
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('The fields description, amount must make a unique set.', response.data['non_field_errors'][0])
        
    def test_get_event_success(self):
        data = {
            "description": "test event",
            "amount": 30,
            "expender": "test1",
            "utiliser" : ["test1", "test2"],
            "split_type": "equal"
        }
        self.client.post(self.event_url, data, format='json') # creating an event
        response = self.client.get(self.event_url, data, format='json') # viewing the event
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.event.objects.filter(description='test event').exists())
        self.assertIn('id', response.data[0])
        
    def test_create_event_with_occasion_fail(self):
        self.client.post(self.occasion_url, self.occasion_data, format='json')  # creating an occasion
        data = {
            "description": "test event",
            "amount": 150,
            "expender": "test1",
            "utiliser" : ["test1","test2"],
            "split_type": "equal",
            "occasion": "test occasion" 
        } 
        self.client.post(self.event_url, data, format='json') # creating an event
        response = self.client.post(self.event_url, data, format='json') # creating the same event again for same occasion
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('The fields description, amount must make a unique set.', response.data['non_field_errors'][0])