from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .access import effective_modules
from .serializers import UserSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UserSerializer(request.user).data
        data["modules"] = effective_modules(request.user)   # tabs this user may access
        if request.auth is not None and request.auth.get("view_only"):
            data.update({"may_write": False, "view_only": True})
        return Response(data)
