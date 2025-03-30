from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

REGISTER_USER_URL = reverse('split_it_app:register_users')
LOGIN_USER_URL = reverse('split_it_app:login_users')

class RegisterApiTest(TestCase):
    """ This testcase tests the RegisterApi. """
    
    def setUp(self):
        self.User = get_user_model()
        self.register_url = REGISTER_USER_URL
        
    def test_register_user_success(self):
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.User.objects.filter(username='testuser').exists())
        self.assertTrue(self.User.objects.filter(email='testuser@example.com').exists())
        
    def test_register_user_fail(self):
        self.User.objects.create_user(
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
        self.assertEqual(self.User.objects.filter(username='existinguser').count(), 1)
        
class LoginApiTest(TestCase):
    """ This testcase tests the LoginApi. """
    
    def setUp(self):
        self.User = get_user_model()
        self.register_url = REGISTER_USER_URL
        self.login_url = LOGIN_USER_URL
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_login_user_success(self):
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(self.User.objects.filter(username='testuser').exists())
        self.assertTrue(self.User.objects.filter(email='testuser@example.com').exists())
        
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