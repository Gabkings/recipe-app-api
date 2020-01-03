from django.urls import path, include
from .views import TagViewSet, IngredientViewSet
from rest_framework.routers import DefaultRouter


app_name = 'recipe'
router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
