from django.contrib.auth import get_user_model
from django.shortcuts import get_list_or_404, get_object_or_404

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from users.models import Follow

from .serializers import (
    FollowListSerializer,
    GetTokenSerializer,
    SafeUserSerializer,
    UserPasswordChangeSerializer,
    UserSerializer,
)
from ..paginator import CustomPageNumberPagination

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SafeUserSerializer
    pagination_class = CustomPageNumberPagination

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserSerializer
        elif self.action in ("subscriptions", "add_subscriptions"):
            return FollowListSerializer
        elif self.action == "set_password":
            return UserPasswordChangeSerializer
        return SafeUserSerializer

    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post"],
        url_path="set_password",
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.data.get("new_password", user.password)
        user.password = new_password
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["get"],
        url_path="subscriptions",
        permission_classes=[IsAuthenticated],
        pagination_class=CustomPageNumberPagination,
    )
    def subscriptions(self, request):
        current_user = request.user
        queryset = get_list_or_404(Follow, followers=current_user)
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=["post", "delete"],
        url_path="(?P<user_pk>[^/.])/subscribe",
        permission_classes=[IsAuthenticated],
    )
    def add_subscriptions(self, request, user_pk=None):
        if request.method == "POST":
            current_user = self.request.user
            following = get_object_or_404(User, id=int(user_pk))

            instance, created = Follow.objects.get_or_create(
                following=following, followers=current_user
            )
            if created:
                serializer = self.get_serializer(instance, many=False)
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(
                "Подписка уже существует", status=status.HTTP_400_BAD_REQUEST
            )

        elif request.method == "DELETE":
            current_user = self.request.user
            following = get_object_or_404(User, id=int(user_pk))

            instance = get_object_or_404(
                Follow, following=following, followers=current_user
            )
            instance.delete()

            return Response("Успешная отписка", status=status.HTTP_204_NO_CONTENT)


class CustomAuthToken(APIView):
    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.data
        email = validated_data.get("email")
        password = validated_data.get("password")

        user = get_object_or_404(User, email=email, password=password)
        token, is_exists = Token.objects.get_or_create(user=user)
        return Response({"auth_token": token.key}, status=status.HTTP_200_OK)


class DeleteToken(APIView):
    def post(self, request):
        if not request.user.is_anonymous:
            token = get_object_or_404(Token, user=request.user)
            token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            "User is not authenticated", status=status.HTTP_401_UNAUTHORIZED
        )
