from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .admin_views import (AdminUserViewSet, CompanyViewSet, ModulesView,
                          RoleMatrixView)
from .views import LoginView, MeView

router = DefaultRouter()
router.register("admin/users", AdminUserViewSet, basename="admin-user")
router.register("admin/companies", CompanyViewSet, basename="admin-company")

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me", MeView.as_view(), name="me"),
    path("admin/modules", ModulesView.as_view(), name="admin-modules"),
    path("admin/roles", RoleMatrixView.as_view(), name="admin-roles"),
] + router.urls
