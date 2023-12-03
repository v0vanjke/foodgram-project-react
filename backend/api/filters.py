import django_filters
from django.db.models import Q
from django_filters import rest_framework
from rest_framework import exceptions

from recipes.models import Ingredient, Recipe

VALUE = [0, 1]


class RecipeFilter(rest_framework.FilterSet):
    """Фильтрация рецептов.

    По Тегам, Автору, Избранным рецептам и рецептам в Корзине покупок.
    """

    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = django_filters.NumberFilter(field_name='author__id')
    is_favorited = django_filters.NumberFilter(method='filter_is_favorited',
                                               label='В избранном')
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart',
    )

    def filter_is_favorited(self, queryset, name, value):
        if value not in VALUE:
            raise exceptions.ValidationError(
                {'is_favorited': [
                    'Значение фильтра может быть только 0 или 1'
                ]}
            )
        if value == 1 and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value not in VALUE:
            raise exceptions.ValidationError(
                {'is_in_shopping_cart': [
                    'Значение фильтра может быть только 0 или 1'
                ]}
            )
        if value == 1 and self.request.user.is_authenticated:
            return queryset.filter(cart__user=self.request.user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')


class IngredientNameFilter(django_filters.Filter):
    def filter(self, queryset, value):
        if value:
            return queryset.filter(Q(name__istartswith=value))
        return queryset


class IngredientFilter(rest_framework.FilterSet):
    name = IngredientNameFilter()

    class Meta:
        model = Ingredient
        fields = ('name',)
