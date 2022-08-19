from django.shortcuts import get_list_or_404, get_object_or_404

from recipes.models import Ingredient, Recipe, Tag

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet


from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer
from .permissions import RecipePermission
from ..paginator import CustomPageNumberPagination


class TagViewSet(ViewSet):

    def list(self, request):
        queryset = get_list_or_404(Tag)
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        tag = get_object_or_404(Tag, pk=pk)
        serializer = TagSerializer(tag, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(ViewSet):

    def list(self, request):
        queryset = get_list_or_404(Ingredient)
        serializer = IngredientSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        tag = get_object_or_404(Ingredient, pk=pk)
        serializer = IngredientSerializer(tag, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (RecipePermission,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        req_query_params = self.request.query_params
        current_user = self.request.user

        is_favorited = req_query_params.get('is_favorited')
        is_in_shopping_cart = req_query_params.get('is_in_shopping_cart')
        author_id = req_query_params.get('author')
        tags_slug = req_query_params.getlist('tags')

        all_recipes = Recipe.objects.all()

        if is_favorited:
            all_recipes = all_recipes & current_user.wish_list.all()
        if is_in_shopping_cart:
            all_recipes = all_recipes & current_user.shop_list.all()
        if author_id:
            all_recipes = all_recipes.filter(author__id=author_id)
        if tags_slug:
            for slug in tags_slug:
                all_recipes = all_recipes.filter(tag__slug=slug)

        return all_recipes
