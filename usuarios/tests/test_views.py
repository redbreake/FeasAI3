import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate


class UsuariosViewsTest(TestCase):
    """Test suite for usuarios app views"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!'
        }

    def test_register_view_get(self):
        """Test register view GET request"""
        response = self.client.get(reverse('usuarios:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/register.html')

    def test_register_view_post_valid(self):
        """Test register view POST request with valid data"""
        response = self.client.post(reverse('usuarios:register'), self.user_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration

        # Check that user was created
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('TestPass123!'))

    def test_register_view_post_invalid(self):
        """Test register view POST request with invalid data"""
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'DifferentPass123!'  # Passwords don't match

        response = self.client.post(reverse('usuarios:register'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Stay on form
        self.assertContains(response, 'error')  # Should show error

        # Check that user was not created
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username='testuser')

    def test_register_view_post_duplicate_username(self):
        """Test register view POST request with duplicate username"""
        # Create user first
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='ExistingPass123!'
        )

        response = self.client.post(reverse('usuarios:register'), self.user_data)
        self.assertEqual(response.status_code, 200)  # Stay on form
        self.assertContains(response, 'error')  # Should show error

    def test_login_view_get(self):
        """Test login view GET request"""
        response = self.client.get(reverse('usuarios:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'usuarios/login.html')

    def test_login_view_post_valid(self):
        """Test login view POST request with valid credentials"""
        # Create user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )

        login_data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }

        response = self.client.post(reverse('usuarios:login'), login_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_login_view_post_invalid_credentials(self):
        """Test login view POST request with invalid credentials"""
        # Create user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )

        invalid_login_data = {
            'username': 'testuser',
            'password': 'WrongPass123!'
        }

        response = self.client.post(reverse('usuarios:login'), invalid_login_data)
        self.assertEqual(response.status_code, 200)  # Stay on form
        self.assertContains(response, 'Credenciales inválidas')  # Should show error

    def test_login_view_post_nonexistent_user(self):
        """Test login view POST request with nonexistent user"""
        login_data = {
            'username': 'nonexistent',
            'password': 'SomePass123!'
        }

        response = self.client.post(reverse('usuarios:login'), login_data)
        self.assertEqual(response.status_code, 200)  # Stay on form
        self.assertContains(response, 'Credenciales inválidas')  # Should show error

    def test_logout_view(self):
        """Test logout view"""
        # Create and login user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.client.login(username='testuser', password='TestPass123!')

        # Verify user is logged in
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

        # Logout
        response = self.client.get(reverse('usuarios:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout

        # Verify user is logged out
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_register_redirect_authenticated_user(self):
        """Test that authenticated users are redirected from register page"""
        # Create and login user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.client.login(username='testuser', password='TestPass123!')

        response = self.client.get(reverse('usuarios:register'))
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_login_redirect_authenticated_user(self):
        """Test that authenticated users are redirected from login page"""
        # Create and login user
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.client.login(username='testuser', password='TestPass123!')

        response = self.client.get(reverse('usuarios:login'))
        self.assertEqual(response.status_code, 302)  # Should redirect

    def test_user_creation_edge_cases(self):
        """Test user creation with edge cases"""
        # Test with very long username
        long_username_data = self.user_data.copy()
        long_username_data['username'] = 'a' * 151  # One character over the limit

        response = self.client.post(reverse('usuarios:register'), long_username_data)
        self.assertEqual(response.status_code, 200)  # Should fail validation

        # Test with invalid email
        invalid_email_data = self.user_data.copy()
        invalid_email_data['email'] = 'invalid-email'

        response = self.client.post(reverse('usuarios:register'), invalid_email_data)
        self.assertEqual(response.status_code, 200)  # Should fail validation
        self.assertContains(response, 'error')

    def test_password_validation(self):
        """Test password validation during registration"""
        # Test with very short password
        short_pass_data = self.user_data.copy()
        short_pass_data['password1'] = '123'
        short_pass_data['password2'] = '123'

        response = self.client.post(reverse('usuarios:register'), short_pass_data)
        self.assertEqual(response.status_code, 200)  # Should fail validation

        # Test with common password
        common_pass_data = self.user_data.copy()
        common_pass_data['password1'] = 'password'
        common_pass_data['password2'] = 'password'

        response = self.client.post(reverse('usuarios:register'), common_pass_data)
        self.assertEqual(response.status_code, 200)  # Should fail validation