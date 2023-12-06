from django.core.validators import MinValueValidator

from api.fields import Base64ImageField, Hex2NameColor
from foodgram_backend.constants import MIN_COOKING_TIME_VALUE
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import exceptions, serializers
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientGetSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(
        source='ingredient.name',
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit',
    )
    id = serializers.ReadOnlyField(
        source='ingredient.id',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        validators=(
            MinValueValidator(
                limit_value=MIN_COOKING_TIME_VALUE,
                message='Количество ингредиента не может быть меньше 0',
            ),
        )
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientGetSerializer(
        many=True,
        source='recipeingredient',
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserSerializer()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, object):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.favorites.filter(recipe=object).exists()

    def get_is_in_shopping_cart(self, object):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.cart.filter(recipe=object).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientPostSerializer(
        many=True,
        source='recipeingredient',
        )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        validators=(
            MinValueValidator(
                limit_value=1,
                message='Время приготовления не может быть меньше 0 минут',
            ),
        )
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise exceptions.ValidationError(
                'Нельзя создать рецепт без Ингредиентов'
            )
        current_ingredients = [
            ingredient.get('id') for ingredient in ingredients
        ]
        if len(current_ingredients) != len(set(current_ingredients)):
            raise exceptions.ValidationError(
                'Вы указали один и тот же Ингредиент несколько раз'
            )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                {'tags': ['Отсутствует в переданных данных']}
            )
        if len(tags) != len(set(tags)):
            raise exceptions.ValidationError(
                'Вы указали один и тот же Ингредиент несколько раз'
            )
        return tags

    def get_is_favorited(self, recipe):
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context.get('view').request.user
        if user.is_anonymous:
            return False
        return user.cart.filter(recipe=recipe).exists()

    def add_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ])

    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        if 'recipeingredient' not in validated_data:
            raise serializers.ValidationError(
                {'ingredients': ['Отсутствует в переданных данных']}
            )
        if 'tags' not in validated_data:
            raise serializers.ValidationError(
                {'tags': ['Отсутствует в переданных данных']}
            )
        recipe = instance
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        instance.tags.clear()
        instance.ingredients.clear()
        tags = validated_data.get('tags')
        instance.tags.set(tags)
        ingredients = validated_data.get('recipeingredient')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time,
        )
        self.add_ingredients(ingredients, recipe)
        instance.save()
        return instance

    def to_representation(self, recipe):
        serializer = RecipeGetSerializer(recipe)
        return serializer.data
