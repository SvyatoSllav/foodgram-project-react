from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredients, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "colored_name",
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "author",
    )
    list_filter = (
        "author",
        "name",
        "tag",
    )
    readonly_fields = ("wish_list_count",)


@admin.register(Ingredient)
class IngridientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    list_filter = ("name",)


@admin.register(RecipeIngredients)
class RecipeIngredients(admin.ModelAdmin):
    list_display = ("ingredient", "weight")
