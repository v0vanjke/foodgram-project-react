import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.paginations import CustomPagination
from api.serializers import (IngredientSerializer, RecipeGetSerializer,
                             RecipePostSerializer, TagSerializer)
from recipes.models import (Cart, Favorites, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from recipes.serializers import ShortRecipeSerializer
from users.permissions import IsAuthorOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет с реализацией добавления/удаления.

    В Избраное и Корзину покупок,
    а также возможностью выгрузить Список покупок.
    """

    queryset = (Recipe.objects.all().order_by("id"))
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PATCH']:
            return RecipePostSerializer
        return RecipeGetSerializer

    def add_to(self, model, user, pk):
        if Recipe.objects.filter(id=pk).exists():
            obj, created = model.objects.get_or_create(
                user=user, recipe=Recipe.objects.get(id=pk),
            )
            if created:
                serializer = ShortRecipeSerializer(Recipe.objects.get(id=pk))
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def remove_from(self, model, user, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if model.objects.filter(user=user, recipe=recipe).exists():
            model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='favorite',
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favorites, request.user, pk)
        elif request.method == 'DELETE':
            return self.remove_from(Favorites, request.user, pk)

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Cart, request.user, pk)
        elif request.method == 'DELETE':
            return self.remove_from(Cart, request.user, pk)

    @action(
        detail=False,
        methods=('GET',),
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shopping_cart = (
            RecipeIngredient.objects.filter(recipe__cart__user=request.user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(amount=Sum('amount'))
            .order_by('ingredient__name')
        )
        output = io.StringIO()
        for item in shopping_cart:
            output.write(f"{item['ingredient__name']}\t")
            output.write(f"{item['amount']}\t")
            output.write(f"{item['ingredient__measurement_unit']} \n")
        response = FileResponse(output.getvalue(), content_type='text/plain')
        response['Content-Disposition'] = ('attachment;'
                                           ' filename="shopping_cart.txt"')
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (Tag.objects.all().order_by('id'))
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (Ingredient.objects.all().order_by('id'))
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    search_fields = ('^name',)
