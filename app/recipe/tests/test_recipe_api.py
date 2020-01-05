from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Tag, Ingredient
from django.contrib.auth import get_user_model
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer
from django.urls import reverse
import os
from PIL import Image
import tempfile


RECIPE_URL = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def sample_tag(user, name='Sample tag'):
    '''create and return sample tag'''
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="sample ingredients"):
    '''create and return ingredient'''
    return Ingredient.objects.create(user=user, name=name)


def recipe_detail_url(id):
    '''Url for recrecipe_idipes details'''
    return reverse('recipe:recipe-detail', args=[id])


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

    def test_recipe_detail(self):
        '''Get and return single recipe details'''
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        url = recipe_detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), len(serializer.data))

    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'Test recipe',
            'time_minutes': 30,
            'price': 10.00,
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        '''Test creating a recipe attaching tags'''
        tag1 = sample_tag(user=self.user, name='tag1')
        tag2 = sample_tag(user=self.user, name='tag2')
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 40,
            'price': 40.00,
            'tags': [tag1.id, tag2.id]
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag2, tags)
        self.assertIn(tag1, tags)

    def test_create_recipe_with_ingridents(self):
        '''Test creating tags with ingridents'''
        ingredient1 = sample_ingredient(user=self.user, name="Sample 1")
        ingredient2 = sample_ingredient(user=self.user, name='Sample 2')
        payload = {
            'title': 'sample recipe',
            'ingredients': [ingredient1.id, ingredient2.id],
            'price': 78.00,
            'time_minutes': 20
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient2, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_create_recipe_with_tag_ingredient(self):
        '''Test creating a recipe with tags and ingredients'''
        ingredient1 = sample_ingredient(user=self.user, name="Sample 1")
        ingredient2 = sample_ingredient(user=self.user, name='Sample 2')
        tag1 = sample_tag(user=self.user, name='tag1')
        tag2 = sample_tag(user=self.user, name='tag2')
        payload = {
            'title': 'sample recipe',
            'ingredients': [ingredient1.id, ingredient2.id],
            'tags': [tag2.id, tag1.id],
            'price': 78.00,
            'time_minutes': 20
        }
        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        ingredients = recipe.ingredients.all()
        self.assertEqual(tags.count(), 2)
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(tag2, tags)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {'title': 'Chicken tikka', 'tags': [new_tag.id]}
        url = recipe_detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            'title': 'Spaghetti carbonara',
            'time_minutes': 25,
            'price': 5.00
        }
        url = recipe_detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):
    '''test uploaing image endpoint '''

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user', 'testpass')
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
