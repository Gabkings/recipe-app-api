from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    '''Test the publicly available tags API'''

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        '''test that login is required for retrieving tags'''
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApiTests(TestCase):
    '''Test Api when user is already logined'''

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="londondappdev@gmail.com", password='testpass123')
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_list_tags(self):
        '''Test listing tags for authenticated user'''
        Tag.objects.create(
            user=self.user,
            name="Desert"
        )
        Tag.objects.create(
            user=self.user,
            name="Fruity"
        )
        res = self.client.get(TAGS_URL)
        '''Fetch tags from the Tags model to compare'''
        tags = Tag.objects.all().order_by('-name')
        seriliazer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,  seriliazer .data)

    def test_tags_limited_to_authenticated_user(self):
        '''Test tags retrieved belong too authenticated user'''
        new_user = get_user_model().objects.create_user(
            email='test@gmail.com', password='testpass123'
        )
        tag1 = Tag.objects.create(
            user=new_user,
            name="vegetables"
        )
        tag2 = Tag.objects.create(
            user=self.user,
            name="Deserts"
        )

        res = self.client.get(TAGS_URL)
        '''Fetch tags from the Tags model to compare'''
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], tag2.name)
        self.assertNotEqual(res.data[0]['name'], tag1.name)
        self.assertEqual(len(res.data), 1)
