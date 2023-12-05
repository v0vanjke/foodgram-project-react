from django.contrib import admin
from django.contrib.auth.models import Group

from recipes.models import (Cart, Favorites, Ingredient, Recipe,
                            RecipeIngredient, RecipeTag, Tag)
from users.models import User, Follow


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
        return obj.follow.count(author=obj)


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
    search_fields = ('author', 'name')
    list_filter = ('tags',)
    list_display_links = ('name',)
    ordering = ('pub_date',)
    inlines = (IngredientsInline, )
    filter_horizontal = ('tags',)

    @admin.display(description='Добавлений в Избранное')
    def count_favorites(self, obj):
        return obj.favorites.count()

    def get_tags(self, obj):
        return "\n".join([tag.recipe for tag in obj.tags.all()])

    def get_ingredients(self, obj):
        return "\n".join(
            [ingredient.recipe for ingredient in obj.ingredients.all()]
        )


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
    search_fields = ('user',)
    ordering = ('user',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(PaginatedAdminPanel):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
    )
    search_fields = ('recipe',)
    ordering = ('recipe',)


@admin.register(RecipeTag)
class RecipeTagAdmin(PaginatedAdminPanel):
    list_display = (
        'recipe',
        'tag',
    )
    search_fields = ('recipe',)
    ordering = ('recipe',)


@admin.register(Cart)
class CartAdmin(PaginatedAdminPanel):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user',)
    ordering = ('user',)


@admin.register(Follow)
class FollowAdmin(PaginatedAdminPanel):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user',)
    ordering = ('user',)


admin.site.unregister(Group)
