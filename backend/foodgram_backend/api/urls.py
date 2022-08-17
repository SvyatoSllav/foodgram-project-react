from django.urls import path, include

from rest_framework.routers import SimpleRouter

from .users_auth.views import UserViewSet, CustomAuthToken, DeleteToken


router = SimpleRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', CustomAuthToken.as_view()),
    path('auth/token/logout/', DeleteToken.as_view()),
]
