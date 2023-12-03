from django.urls import include, path
from rest_framework import routers

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import CustomUserViewSet

routerv1 = routers.DefaultRouter()
routerv1.register(r'users', CustomUserViewSet, basename='users')
routerv1.register(r'ingredients', IngredientViewSet, basename='ingredients')
routerv1.register(r'tags', TagViewSet, basename='tags')
routerv1.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(routerv1.urls)),
    # path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
