from recipes.models import Ingridient, Tag

from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngridientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingridient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
