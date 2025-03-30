from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from .models import Occasion

REGISTER_USER_URL = reverse('split_it_app:register_users')
LOGIN_USER_URL = reverse('split_it_app:login_users')
OCCASION_URL = reverse('split_it_app:occasion-view-create')

class RegisterApiTest(TestCase):
    """ This testcase tests the RegisterApi. """
    
    def setUp(self):
        self.user = get_user_model()
        self.client = APIClient()
        self.register_url = REGISTER_USER_URL
        
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
            'username': 'existinguser', #using the same username for new user.
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
            'password': 'tesstpassword' #giving wrong password for the registered user.
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
        
    def tearDown(self):
        self.user.objects.all().delete()
        self.occasion.objects.all().delete()
        
    def test_create_occasion_success(self):
        data = {
            'description': 'testing occasion',
            'participants' : ["test1", "test2", "ab11c"]
        }
        response = self.client.post(self.occasion_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.occasion.objects.filter(description='testing occasion').exists())
        self.assertIn('participants', response.data)
    
    def test_get_occasion_success(self):
        data = {
            'description': 'testing occasion',
            'participants' : ["test1", "test2", "ab11c"]
        }
        self.client.post(self.occasion_url, data, format='json') # creating a occasion
        response = self.client.get(self.occasion_url, data, format='json') # viewing the occasion
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.occasion.objects.filter(description='testing occasion').exists())
        self.assertIn('id', response.data[0])
        
    def test_create_duplicate_occasion_fail(self):
        data = {
            'description': 'testing occasion',
            'participants' : ["test1", "test2", "ab11c"]
        }
        response = self.client.post(self.occasion_url, data, format='json')
        data = {
            'description': 'testing occasion',
            'participants' : 'test'
        }
        response = self.client.post(self.occasion_url, data, format='json') # creating a duplicate occasion
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('occasion with this description already exists.', response.data['description'][0])