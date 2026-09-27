"""Bearer access-token authentication + the portal/role map it enforces.

Kept free of DRF view imports: DRF imports this module while it is still
initialising (DEFAULT_AUTHENTICATION_CLASSES), so importing views here would be
circular. Session issuing/refresh lives in core/tokens.py.
"""

from datetime import timedelta

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from .models import User

# roles: who may sign in.  refresh: idle timeout (each refresh restarts it).
# max_session: absolute cap from the original sign-in, rotation can't extend it.
PORTALS = {
    "admin": {"roles": {User.Role.ADMIN},
              "refresh": timedelta(hours=12), "max_session": timedelta(hours=12)},
    "dealer": {"roles": {User.Role.DEALER, User.Role.MANAGER},
               "refresh": timedelta(days=7), "max_session": timedelta(days=30)},
    "pilot": {"roles": {User.Role.PILOT},
              "refresh": timedelta(days=7), "max_session": timedelta(days=30)},
}



def role_allowed(user, portal):
    return user.role in PORTALS[portal]["roles"]


class SessionJWTAuthentication(JWTAuthentication):
    """Bearer access-token auth that also enforces session_version and portal,
    and keeps admin "view as" sessions strictly read-only."""

    def authenticate(self, request):
        result = super().authenticate(request)
        if result and result[1].get("view_only") and request.method not in SAFE_METHODS:
            raise PermissionDenied("View-only session: changes are disabled.")
        return result

    def get_user(self, validated_token):
        user = super().get_user(validated_token)  # also rejects inactive users
        portal = validated_token.get("portal")
        if validated_token.get("sv") != user.session_version:
            raise InvalidToken("Session has been revoked. Please sign in again.")
        if portal not in PORTALS or not role_allowed(user, portal):
            raise InvalidToken("Token is not valid for this account.")
        if validated_token.get("view_only"):
            # the admin who opened the view must still be an active admin
            if not User.objects.filter(pk=validated_token.get("view_admin"), is_active=True,
                                       role=User.Role.ADMIN).exists():
                raise InvalidToken("View session is no longer valid.")
        return user
