from django import forms

import django_filters
from django_filters import rest_framework
from recipes.models import Ingredient, Recipe
from rest_framework import exceptions

VALUE = [0, 1]


class NonValidatingTagChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        pass


class NonValidatingTagFilter(django_filters.AllValuesMultipleFilter):
    field_class = NonValidatingTagChoiceField


class RecipeFilter(rest_framework.FilterSet):
    """Фильтрация рецептов.

    По Тегам, Автору, Избранным рецептам и рецептам в Корзине покупок.
    """

    tags = NonValidatingTagFilter(field_name='tags__slug')
    is_favorited = django_filters.NumberFilter(
        method='filter_is_favorited',
        label='В избранном',
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        method='filter_is_in_shopping_cart',
        label='В корзине покупок',
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

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


class IngredientFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
