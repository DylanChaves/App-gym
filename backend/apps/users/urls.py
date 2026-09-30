from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConfigView, CsrfView, LoginView, LogoutView, MeView, RegisterView, UserViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
urlpatterns = [
    path("config/", ConfigView.as_view()),
    path("auth/csrf/", CsrfView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("auth/register/", RegisterView.as_view()),
    path("", include(router.urls)),
]
