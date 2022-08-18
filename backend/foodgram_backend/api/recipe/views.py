from django.shortcuts import get_list_or_404, get_object_or_404

from recipes.models import Ingridient, Tag

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


from .serializers import IngridientSerializer, TagSerializer


class TagViewSet(ViewSet):

    def list(self, request):
        queryset = get_list_or_404(Tag)
        serializer = TagSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        tag = get_object_or_404(Tag, pk=pk)
        serializer = TagSerializer(tag, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngridientViewSet(ViewSet):

    def list(self, request):
        queryset = get_list_or_404(Ingridient)
        serializer = IngridientSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        tag = get_object_or_404(Ingridient, pk=pk)
        serializer = IngridientSerializer(tag, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
