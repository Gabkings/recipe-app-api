from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from unittest.mock import patch


def sample_user(email="test@gmail.com", password='testpass123'):
    '''create a sample user '''
    return get_user_model().objects.create_user(email, password)


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

    def test_tag_str(self):
        '''Test the tag string representation '''
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name='Cucumber'
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        '''Test the recipe's string representation'''
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Mushroom Recipe 001',
            price=300.00,
            time_minutes=5
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
