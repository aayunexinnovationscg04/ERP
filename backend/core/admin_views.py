"""Super-Admin API: user management, role management, per-member overrides."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .access import effective_modules, role_defaults, role_matrix
from .models import RolePermission, User, UserModuleOverride
from .modules import MODULES, MODULE_KEYS
from .permissions import IsSuperAdmin
from .serializers import AdminUserSerializer, CompanySerializer
from .models import Company


class ModulesView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        return Response(MODULES)


class CompanyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdmin]
    serializer_class = CompanySerializer
    queryset = Company.objects.all().order_by("name")


class AdminUserViewSet(viewsets.ModelViewSet):
    """CRUD users, assign roles/companies, plus per-user module overrides."""

    permission_classes = [IsSuperAdmin]
    serializer_class = AdminUserSerializer

    def get_queryset(self):
        qs = User.objects.all().order_by("username")
        role = self.request.query_params.get("role")
        company = self.request.query_params.get("company")
        if role:
            qs = qs.filter(role=role)
        if company:
            qs = qs.filter(company_id=company)
        return qs

    @action(detail=True, methods=["get", "put"])
    def permissions(self, request, pk=None):
        user = self.get_object()
        if request.method == "GET":
            overrides = {o.module: o.allowed for o in user.module_overrides.all()}
            return Response({
                "user_id": user.id,
                "role": user.role,
                "role_defaults": role_defaults(user.role) if user.role != User.Role.SUPERADMIN
                                 else {m: True for m in MODULE_KEYS},
                "overrides": overrides,
                "effective": effective_modules(user),
            })
        # PUT: body {overrides: {module: bool|null}}  (null clears the override)
        payload = (request.data or {}).get("overrides", {})
        for module, val in payload.items():
            if module not in MODULE_KEYS:
                continue
            if val is None:
                UserModuleOverride.objects.filter(user=user, module=module).delete()
            else:
                UserModuleOverride.objects.update_or_create(
                    user=user, module=module, defaults={"allowed": bool(val)})
        return Response({"ok": True, "effective": effective_modules(user)})


class RoleMatrixView(APIView):
    """GET the full role x module matrix; PUT to update role defaults."""

    permission_classes = [IsSuperAdmin]

    def get(self, request):
        return Response({"modules": MODULES, "matrix": role_matrix()})

    def put(self, request):
        # body: {role: {module: bool}}  — super admin role is ignored (always all-access)
        data = request.data or {}
        valid_roles = {r for r, _ in User.Role.choices if r != User.Role.SUPERADMIN}
        for role, mods in data.items():
            if role not in valid_roles or not isinstance(mods, dict):
                continue
            for module, allowed in mods.items():
                if module not in MODULE_KEYS:
                    continue
                RolePermission.objects.update_or_create(
                    role=role, module=module, defaults={"allowed": bool(allowed)})
        return Response({"ok": True, "matrix": role_matrix()}, status=status.HTTP_200_OK)
