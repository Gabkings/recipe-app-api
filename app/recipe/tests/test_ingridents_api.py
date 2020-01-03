from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicAPITests(TestCase):
    def setUp(self):
        '''Set up client'''
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access this endpoint"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITests(TestCase):
    '''Test Authenicated users can view/modify ingredients'''

    def setUp(self):
        '''set required for the tests'''
        self.user = get_user_model().objects.create_user(
            email="testuser@gmail.com",
            password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_listing_ingredient_success(self):
        '''Test listing ingrident success for auth user'''
        Ingredient.objects.create(name="Sample 1", user=self.user)
        Ingredient.objects.create(name="smple 2", user=self.user)
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        seriliazer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, seriliazer.data)
        self.assertEqual(len(res.data), len(seriliazer.data))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_ingredients_limited_to_user(self):
        '''Test tags are limited to authenticated user'''
        self.user2 = get_user_model().objects.create_user(
            email='test133@gmail.com', password='testpass123'
        )
        Ingredient.objects.create(user=self.user2, name='Vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='tumeric')
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
