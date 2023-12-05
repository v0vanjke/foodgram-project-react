from django.core.validators import (MaxValueValidator, MinValueValidator)
from django.db import models

from colorfield.fields import ColorField
from foodgram_backend import constants
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=constants.MAX_TAG_NAME_LENGHT,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет',
        blank=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        max_length=constants.MAX_TAG_SLUG_LENGHT,
        blank=True,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент',
        max_length=constants.MAX_INGREDIENT_NAME_LENGHT,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=constants.MAX_INGREDIENT_MEASUREMENT_UNIT_LENGHT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_measurement_unit',
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=constants.MAX_RECIPE_NAME_LENGHT,
    )
    text = models.TextField(
        verbose_name='Описание',
        max_length=constants.MAX_RECIPE_TEXT_LENGHT,
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/images/',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(constants.MIN_COOKING_TIME_VALUE),
            MaxValueValidator(constants.MAX_COOKING_TIME_VALUE),
        ],
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты блюда',
        related_name='recipes',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='recipeingredient',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(constants.MIN_INGREDIENT_AMOUNT_VALUE),
            MaxValueValidator(constants.MAX_INGREDIENT_AMOUNT_VALUE),
        ],
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='recipeingredient',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipetag',
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тег',
        on_delete=models.CASCADE,
        related_name='recipetag',
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'


class Favorites(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Избранное',
        related_name='favorites',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='favorites',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'


class Cart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='cart',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='cart',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
