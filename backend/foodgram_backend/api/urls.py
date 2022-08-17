from django.urls import include, path

from rest_framework.routers import SimpleRouter

from .users_auth.views import CustomAuthToken, DeleteToken, UserViewSet

from .recipe.views import TagViewSet, IngridientViewSet


router = SimpleRouter()
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingridient', IngridientViewSet, basename='ingridient')

urlpatterns = [
    path('', include(router.urls)),

    # Auth urls
    path('auth/token/login/', CustomAuthToken.as_view()),
    path('auth/token/logout/', DeleteToken.as_view()),
]
