from pathlib import Path

from django.http.response import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404

from recipes.models import Ingredient, Recipe, Tag

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet


from .permissions import RecipePermission
from .serializers import (
    CreateUpdateRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer
)
from .services import create_file
from ..paginator import CustomPageNumberPagination


BASE_DIR = Path(__file__).resolve().parent.parent.parent


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
    permission_classes = (RecipePermission,)
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return CreateUpdateRecipeSerializer
        return RecipeSerializer

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

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path='(?P<recipe_pk>[^/.]+)/favorite',
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, recipe_pk=None):
        if request.method == 'POST':
            current_user = request.user
            recipe = get_object_or_404(Recipe, id=recipe_pk)

            current_user.wish_list.add(recipe)
            return Response(
                'Рецепт успешно добавлен в избранное',
                status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            current_user = request.user
            recipe = get_object_or_404(Recipe, id=recipe_pk)

            if recipe in current_user.wish_list.all():
                current_user.wish_list.remove(recipe)
                return Response(
                    'Рецепт успешно удалён из избранного',
                    status=status.HTTP_204_NO_CONTENT
                )

            return Response(
                'Рецепта нет в избранном',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        current_user = request.user
        user_username = current_user.username
        current_user_shop_list = current_user.shop_list
        try:
            create_file(current_user_shop_list, request.user.username)

            path_to_file = Path(
                f'{BASE_DIR}/media/recipe/users/'
                f'shop_list/{user_username}/output.pdf'
            )
            wish_list_pdf = open(path_to_file, mode='rb')

            return HttpResponse(wish_list_pdf, content_type='application/pdf')

        except Exception:
            return Response(
                'Something went wrong',
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['post', 'delete'],
        url_path='(?P<recipe_pk>[^/.]+)/shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, recipe_pk=None):
        if request.method == 'POST':
            current_user = request.user
            recipe = get_object_or_404(Recipe, id=recipe_pk)

            current_user.shop_list.add(recipe)
            return Response(
                'Рецепт успешно добавлен в список покупок',
                status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            current_user = request.user
            recipe = get_object_or_404(Recipe, id=recipe_pk)

            if recipe in current_user.shop_list.all():
                current_user.shop_list.remove(recipe)
                return Response(
                    'Рецепт успешно удалён из список покупок',
                    status=status.HTTP_204_NO_CONTENT
                )

            return Response(
                'Рецепта нет в список покупок',
                status=status.HTTP_400_BAD_REQUEST
            )
