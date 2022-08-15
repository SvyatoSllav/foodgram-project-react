from django.contrib import admin

from .models import Ingridient, Recipe, RecipeIngridients, Tag


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'colored_name')


admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe)
admin.site.register(Ingridient)
admin.site.register(RecipeIngridients)
