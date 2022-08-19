from recipes.models import Ingredient, Recipe, Tag, RecipeIngredients

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField

from api.users_auth.serializers import SafeUserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeingredientsSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(read_only=False, many=False)

    class Meta:
        model = RecipeIngredients
        fields = (
            'ingredient',
        )

    def to_representation(self, instance):
        representation = super(RecipeingredientsSerializer, self).to_representation(instance)
        representation['ingredient']['amount'] = instance.weight
        return representation


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        source='tag',
        many=True
    )
    author = SafeUserSerializer(
        read_only=True,
        many=False
    )
    ingredients = RecipeingredientsSerializer(many=True,)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
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
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        return bool(
            self.context.get('request').query_params.get('is_favorited')
            )

    def get_is_in_shopping_cart(self, obj):
        return bool(
            self.context.get('request').query_params.get('is_in_shopping_cart')
            )

    def to_representation(self, instance):
        representation = super(RecipeSerializer, self).to_representation(instance)
        # Converts {ingredients: [ingredient:{some_values}]}
        # to {ingredients: [{some_values}]}
        for ingredient_index in range(len(representation['ingredients'])):
            ingredient = representation.get('ingredients')[ingredient_index]
            ingredient_value = ingredient.get('ingredient')
            representation['ingredients'][ingredient] = ingredient_value
        return representation

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        print(ingredients)
        recipe = super().create(validated_data)

        return recipe
