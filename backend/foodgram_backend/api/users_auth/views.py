from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .serializers import (
    GetTokenSerializer,
    SafeUserSerializer,
    UserPasswordChangeSerializer,
    UserSerializer)
from ..paginator import CustomPageNumberPagination


User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SafeUserSerializer
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserSerializer
        return SafeUserSerializer

    def create(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        self.check_permissions(request)
        user = get_object_or_404(User, pk=pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get', ],
        url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = SafeUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post', ],
        url_path='set_password',
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserPasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)

        validated_data = serializer.data
        new_password = validated_data.get('new_password', user.password)
        user.password = new_password
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CustomAuthToken(APIView):

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.data
        email = validated_data.get('email')
        password = validated_data.get('password')

        user = get_object_or_404(User, email=email, password=password)
        token = Token.objects.create(user=user)
        return Response({'Token': token.key}, status=status.HTTP_200_OK)


class DeleteToken(APIView):

    def post(self, request):
        user = request.user
        if not user.is_anonymous:
            token = Token.objects.get(user=user)
            token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            'User is not authenticated',
            status=status.HTTP_401_UNAUTHORIZED
        )
