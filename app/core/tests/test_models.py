from django.test import TestCase
from django.contrib.auth import get_user_model


class MeodelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """ create a new user """
        email = "gabriel@gmail.com"
        password = "Testpassword123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        '''Test the email for a new user is normalized'''
        email = 'test@LONGDG.COM'
        user = get_user_model().objects.create_user(
            email=email, password='testpass123'
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        '''Test creating user with no email raises error'''

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None,
                                                 password='testpass123')

    def test_create_new_superuser(self):
        '''Test creating a new superuser '''
        user = get_user_model().objects.create_superuser(
            email='test@gmail.com', password="testpassword123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_new_staff(self):
        '''Test creatting a staff user'''
        user = get_user_model().objects.create_staff(
            email="test@gmail.com", password="testpass123"
        )
        self.assertTrue(user.is_staff)
        self.assertFalse(user.is_superuser)
