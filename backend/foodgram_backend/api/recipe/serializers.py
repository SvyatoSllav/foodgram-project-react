from api.users_auth.serializers import SafeUserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredients,
    Tag
)
from rest_framework import serializers
from users.models import Follow


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
        representation = super(
            RecipeingredientsSerializer, self).to_representation(instance)

        representation['ingredient']['amount'] = instance.weight
        return representation


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        source='tag',
        many=True,
        read_only=True
    )
    author = SafeUserSerializer(
        read_only=True,
        many=False
    )
    ingredients = RecipeingredientsSerializer(
        many=True,
        read_only=True
    )
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
        representation = super(
            RecipeSerializer, self).to_representation(instance)

        representation['image'] = (
            representation['image'][:7] +
            '51.250.102.77' + representation['image'][15:]
        )
        for ingredient_index in range(len(representation['ingredients'])):
            ingredient = representation.get('ingredients')[ingredient_index]
            ingredient_value = ingredient.get('ingredient')
            representation['ingredients'][ingredient_index] = ingredient_value
        return representation


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField(min_value=0))
    )
    tags = serializers.ListField(
        child=serializers.IntegerField(min_value=0)
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tag_ids = validated_data.pop('tags')

        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context['request'].user,
        )

        for value in ingredients:
            recipe_ingredient = RecipeIngredients.objects.create(
                ingredient=Ingredient.objects.get(id=value.get('id')),
                weight=value.get('amount')
            )
            recipe.ingredients.add(recipe_ingredient)

        for id in tag_ids:
            recipe.tag.add(Tag.objects.get(id=id))

        return recipe

    def to_representation(self, instance):
        current_user = self.context['request'].user

        tags = instance.tag.all()
        tags_fields_to_representation = [
            {
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'slug': tag.slug
            } for tag in tags]

        author = instance.author
        is_subscribed = Follow.objects.filter(
            followers=current_user,
            following=author
        ).exists()
        author_to_representation = {
            'email': author.email,
            'id': author.id,
            'username': author.username,
            'first_name': author.first_name,
            'last_name': author.last_name,
            'is_subscribed': is_subscribed
        }

        ingredients = instance.ingredients.all()
        ingredients_fields_to_representation = [
            {
                'id': ingredient.ingredient.id,
                'name': ingredient.ingredient.name,
                'measurement_unit': ingredient.ingredient.measurement_unit,
                'amount': ingredient.weight
            } for ingredient in ingredients
        ]

        is_favorited = current_user.wish_list.through.objects.filter(
            recipe__id=instance.id
            ).exists()

        is_in_shopping_cart = current_user.shop_list.through.objects.filter(
            recipe__id=instance.id
            ).exists()

        image = 'http://51.250.102.77/instance.image/' + instance.image.url
        representation = {
            'id': instance.id,
            'tags': tags_fields_to_representation,
            'author': author_to_representation,
            'ingredients': ingredients_fields_to_representation,
            'is_favorited': is_favorited,
            'is_in_shopping_cart': is_in_shopping_cart,
            'name': instance.name,
            'image': image,
            'test': instance.text,
            'cooking_time': instance.cooking_time
        }
        return representation

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tag_ids = validated_data.pop('tags')

        instance.name = validated_data.pop('name')
        instance.text = validated_data.pop('text')
        instance.image = validated_data.pop('image')
        instance.cooking_time = validated_data.pop('cooking_time')

        instance.ingredients.all().delete()
        for value in ingredients:
            recipe_ingredient, created = (
                RecipeIngredients.objects.get_or_create(
                    ingredient=Ingredient.objects.get(id=value.get('id')),
                    weight=value.get('amount')
                ))
            instance.ingredients.add(recipe_ingredient)

        instance.tag.clear()
        for id in tag_ids:
            instance.tag.add(Tag.objects.get(id=id))

        instance.save()

        return instance
