from django.contrib import admin
from django.contrib.auth.models import Group

from recipes.models import (Cart, Favorites, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Follow, User


class PaginatedAdminPanel(admin.ModelAdmin):
    list_per_page = 20


class IngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(User)
class UserAdmin(PaginatedAdminPanel):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'count_recipes',
        'count_followers',
        'role',
    )
    list_editable = ('role',)
    search_fields = ('username', 'email')
    list_display_links = ('username',)
    ordering = ('username',)

    @admin.display(description='Количество рецептов')
    def count_recipes(self, obj):
        return obj.recipes.count()

    @admin.display(description='Количество подписчиков')
    def count_followers(self, obj):
        return obj.subscribe.count()


@admin.register(Recipe)
class RecipeAdmin(PaginatedAdminPanel):
    list_display = (
        'name',
        'author',
        'get_ingredients',
        'get_tags',
        'count_favorites',
        'pub_date',
    )
    fields = ('name', 'text', 'image', 'cooking_time', 'author', 'tags')
    search_fields = ('author__username', 'name')
    list_filter = ('tags',)
    list_display_links = ('name',)
    ordering = ('pub_date',)
    inlines = (IngredientsInline,)
    filter_horizontal = ('tags',)

    @admin.display(description='Добавлений в Избранное')
    def count_favorites(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='Теги')
    def get_tags(self, recipe):
        return list(recipe.tags.only('name'))

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, recipe):
        return list(recipe.recipeingredient.only('ingredient'))


@admin.register(Ingredient)
class IngredientAdmin(PaginatedAdminPanel):
    list_display = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Tag)
class TagAdmin(PaginatedAdminPanel):
    list_display = (
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Favorites)
class FavoritesAdmin(PaginatedAdminPanel):
    list_display = (
        'recipe',
        'user',
    )
    search_fields = ('user__username', 'recipe__name')
    ordering = ('user__username',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(PaginatedAdminPanel):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = ('recipe__name',)
    ordering = ('recipe__pub_date',)


@admin.register(Cart)
class CartAdmin(PaginatedAdminPanel):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user__username',)
    ordering = ('user__username',)


@admin.register(Follow)
class FollowAdmin(PaginatedAdminPanel):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user__username',)
    ordering = ('user__username',)


admin.site.unregister(Group)
