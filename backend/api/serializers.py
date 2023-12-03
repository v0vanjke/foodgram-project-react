import webcolors
from django.core.validators import MinValueValidator
from rest_framework import exceptions, serializers
from django.core.files.base import ContentFile
from recipes.models import (
    Ingredient, Recipe, RecipeIngredient, Tag,
)
from users.serializers import UserSerializer
import base64


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class Hex2NameColor(serializers.Field):
    """Класс для нового типа поля в HEX-формате.

    Используется в поле Color сериализатора Recipe.
    """

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


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
                limit_value=0,
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
        current_amounts = [
            ingredient.get('amount') for ingredient in ingredients
        ]
        for amount in current_amounts:
            if amount <= 0:
                raise exceptions.ValidationError(
                    'Количество игредиентов должно быть больше 0'
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

    def create(self, validated_data):
        author = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredient')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            base_ingredient = ingredient.get('id')
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=base_ingredient, amount=amount,
            )
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
        ingredients = validated_data.pop('recipeingredient')
        RecipeIngredient.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        for ingredient in ingredients:
            amount = ingredient.get('amount')
            base_ingredient = ingredient.get('id')
            if (RecipeIngredient.objects.filter(
                    recipe=instance, ingredient=base_ingredient).exists()):
                raise serializers.ValidationError(
                    {'errors': 'нельзя добавить два одинаковых ингредиента'}
                )
            RecipeIngredient.objects.create(
                recipe=instance, ingredient=base_ingredient, amount=amount,
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = [
            TagSerializer(tag).data for tag in instance.tags.all()
        ]
        representation['ingredients'] = [
            RecipeIngredientGetSerializer(
                recipeingredient
            ).data for recipeingredient in instance.recipeingredient.all()
        ]
        return representation
