from django.urls import path, include
from .views import TagViewSet, IngredientViewSet, RecipeViewSet
from rest_framework.routers import DefaultRouter


app_name = 'recipe'
router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
