from django.contrib import admin
from recipes.models import (Favorite, Ingredient, IngredientsRecipe, Recipe,
                            ShoppingCart, Tag)

EMPTY_VALUE = '-пусто-'


# class IngredientInline(admin.TabularInline):
#     model = IngredientsRecipe
#     extra = 2

class IngredientInline(admin.StackedInline):
    model = IngredientsRecipe
    autocomplete_fields = ('ingredients',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Представляет модель Tag в интерфейсе администратора."""
    list_display = ('id', 'name', 'color', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = EMPTY_VALUE


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Представляет модель Ingredient в интерфейсе администратора."""
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = EMPTY_VALUE


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Представляет модель Recipe в интерфейсе администратора."""
    list_display = ('id', 'name', 'author')
    fields = (
        ('name', 'cooking_time',),
        'ingredients',
        'author',
        'tags',
        'text',
        'image',
        'favorited_number',
    )
    readonly_fields = ('favorited_number',)
    search_fields = ('author', 'name', 'tags')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = EMPTY_VALUE
    inlines = (IngredientInline,)

    @admin.display(description='В избранном')
    def favorited_number(self, obj):
        # return Favorite.objects.filter(recipe=obj).count()
        return obj.favorites.count()

    # @admin.display(description='Ингредиенты')
    # def ingredients(self, obj):
    #     return '\n'.join(
    #         [str(ingredients) for ingredients in obj.ingredients.all()]
    #     )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Представляет модель Favorite в интерфейсе администратора."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = EMPTY_VALUE


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Представляет модель ShoppingCart в интерфейсе администратора."""
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = EMPTY_VALUE
