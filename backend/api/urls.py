from django.urls import include, path

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from rest_framework import routers
from users.views import CustomUserViewSet

routerv1 = routers.DefaultRouter()
routerv1.register('users', CustomUserViewSet, basename='users')
routerv1.register('ingredients', IngredientViewSet, basename='ingredients')
routerv1.register('tags', TagViewSet, basename='tags')
routerv1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(routerv1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
