from django.urls import path
from rest_framework.routers import DefaultRouter

from .admin_views import (AdminUserViewSet, CompanyViewSet, ModulesView,
                          PlatformHealthView, RoleMatrixView)
from .tokens import LoginView, LogoutAllView, LogoutView, RefreshView, ViewAsRedeemView
from .views import MeView

router = DefaultRouter()
router.register("admin/users", AdminUserViewSet, basename="admin-user")
router.register("admin/companies", CompanyViewSet, basename="admin-company")

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/refresh", RefreshView.as_view(), name="token-refresh"),
    path("auth/logout", LogoutView.as_view(), name="logout"),
    path("auth/logout-all", LogoutAllView.as_view(), name="logout-all"),
    path("auth/view-as", ViewAsRedeemView.as_view(), name="view-as"),
    path("auth/me", MeView.as_view(), name="me"),
    path("admin/modules", ModulesView.as_view(), name="admin-modules"),
    path("admin/roles", RoleMatrixView.as_view(), name="admin-roles"),
    path("admin/health", PlatformHealthView.as_view(), name="admin-health"),
] + router.urls
