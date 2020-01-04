from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe
from django.contrib.auth import get_user_model
from recipe.serializers import RecipeSerializer
from django.urls import reverse


RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    '''create and return  sample recipe'''
    defaults = {
        'title': 'Sample recipe',
        'price': 30.00,
        'time_minutes': 30

    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicApiTests(TestCase):
    '''Test authentication is required'''
    def setUp(self):
        '''Set up for the tests'''
        self.client = APIClient()

    def test_auth_required(self):
        '''Test authetication is required to view recipes'''
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAPITests(TestCase):
    '''Test access of recipes for authenticated users'''

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='londondevapp@gmail.com',
            password='testpass1234'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_recipes(self):
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_limited_auth_user(self):
        '''Test recipe returned belongs to authenticated user'''
        user2 = get_user_model().objects.create_user(
            email="testemail@gmail.com",
            password='testspass123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        seriliezer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, seriliezer.data)
        self.assertEqual(len(res.data), len(seriliezer.data))
