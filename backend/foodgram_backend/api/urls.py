from django.urls import include, path

from rest_framework.routers import SimpleRouter

from .recipe.views import IngredientViewSet, RecipeViewSet, TagViewSet
from .users_auth.views import CustomAuthToken, DeleteToken, UserViewSet


router = SimpleRouter()
router.register("users", UserViewSet, basename="users")
router.register("tags", TagViewSet, basename="tags")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/login/", CustomAuthToken.as_view()),
    path("auth/token/logout/", DeleteToken.as_view()),
]
