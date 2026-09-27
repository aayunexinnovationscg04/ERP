"""Access/refresh token sessions for the three portals (admin, dealer, pilot).

Model:
  * Access token  - 10 min JWT, returned in the response body, kept only in the
    SPA's memory and sent as `Authorization: Bearer ...`. Never persisted.
  * Refresh token - JWT stored in an HttpOnly, Secure, SameSite=Strict cookie
    scoped to /api/auth/ and named per portal, so JS can never read it and the
    three portals keep independent sessions on the same origin.
  * Rotation      - every refresh blacklists the presented refresh token and
    issues a new pair. A replayed (already rotated) token is rejected.
  * Portal lock   - each token carries a `portal` claim; a login/refresh only
    succeeds when the user's role is allowed on that portal.
  * Revocation    - every token carries `sv` (User.session_version). Changing a
    user's password/role/company/active flag, or "sign out everywhere", bumps
    it, which kills all their access AND refresh tokens immediately.
  * Absolute cap  - `auth_time` is carried across rotations; once a portal's
    max session age is reached the user must sign in again.

Every cookie-authenticated endpoint also requires the `X-FGX-Portal` header.
A cross-site page cannot set a custom header without a CORS preflight (which
we never grant with credentials), so that header plus SameSite=Strict blocks CSRF.
"""

import logging
import time

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.db import transaction
from django.db.models import F
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.token_blacklist.models import (BlacklistedToken,
                                                             OutstandingToken)
from rest_framework_simplejwt.tokens import RefreshToken

from .access import effective_modules
from .authentication import PORTALS, role_allowed
from .models import User
from .serializers import UserSerializer

log = logging.getLogger("fuelguardx.auth")

PORTAL_HEADER = "HTTP_X_FGX_PORTAL"
COOKIE_PATH = "/api/auth/"


def cookie_name(portal):
    return f"fgx_rt_{portal}"


def portal_from(request):
    portal = request.META.get(PORTAL_HEADER, "").strip().lower()
    if portal not in PORTALS:
        raise PermissionDenied("Missing or unknown X-FGX-Portal header.")
    return portal


# --- issuing / cookies -----------------------------------------------------

def issue_pair(user, portal, auth_time=None):
    """New refresh (recorded as OutstandingToken) + its access token."""
    refresh = RefreshToken.for_user(user)
    refresh.set_exp(lifetime=PORTALS[portal]["refresh"])
    refresh["portal"] = portal
    refresh["sv"] = user.session_version
    refresh["auth_time"] = auth_time or int(time.time())
    refresh["role"] = user.role
    refresh["company_id"] = user.company_id
    # Re-record the outstanding row's expiry, since set_exp ran after for_user().
    OutstandingToken.objects.filter(jti=refresh["jti"]).update(
        token=str(refresh), expires_at=refresh.current_time + PORTALS[portal]["refresh"])
    access = refresh.access_token  # copies portal/sv/auth_time/role/company_id
    return refresh, access


def set_refresh_cookie(response, portal, refresh):
    response.set_cookie(
        cookie_name(portal), str(refresh),
        max_age=int(PORTALS[portal]["refresh"].total_seconds()),
        path=COOKIE_PATH, secure=settings.AUTH_COOKIE_SECURE,
        httponly=True, samesite="Strict",
    )


def clear_refresh_cookie(response, portal):
    response.delete_cookie(cookie_name(portal), path=COOKIE_PATH, samesite="Strict")


def session_payload(user, access):
    data = UserSerializer(user).data
    data["modules"] = effective_modules(user)
    return {
        "access": str(access),
        "access_expires_in": int(jwt_settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
        "user": data,
    }


def revoke_all_sessions(user):
    """Invalidate every access + refresh token this user holds, on all portals."""
    User.objects.filter(pk=user.pk).update(session_version=F("session_version") + 1)
    user.refresh_from_db(fields=["session_version"])
    for tok in OutstandingToken.objects.filter(user=user, blacklistedtoken__isnull=True):
        BlacklistedToken.objects.get_or_create(token=tok)


# --- views -------------------------------------------------------------------

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(trim_whitespace=False)


class LoginView(APIView):
    """POST {username, password} + X-FGX-Portal -> access token + user; sets refresh cookie."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"  # tight per-IP bucket against credential stuffing

    def post(self, request):
        portal = portal_from(request)
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = authenticate(request, username=s.validated_data["username"],
                            password=s.validated_data["password"])
        if user is None or not user.is_active:
            # Explicit 401: with no authentication_classes DRF would turn
            # AuthenticationFailed into a 403.
            return Response({"detail": "Invalid username or password."},
                            status=status.HTTP_401_UNAUTHORIZED)
        if not role_allowed(user, portal):
            log.warning("login refused: user=%s role=%s portal=%s", user.pk, user.role, portal)
            raise PermissionDenied(f"This account cannot sign in to the {portal} portal.")
        refresh, access = issue_pair(user, portal)
        update_last_login(None, user)
        resp = Response(session_payload(user, access))
        set_refresh_cookie(resp, portal, refresh)
        return resp


class RefreshView(APIView):
    """POST + X-FGX-Portal (refresh cookie) -> new access token + user; rotates the cookie."""

    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "refresh"

    def post(self, request):
        portal = portal_from(request)
        raw = request.COOKIES.get(cookie_name(portal))
        try:
            if not raw:
                raise TokenError("No session.")
            user, auth_time = self._consume(raw, portal)
        except TokenError as e:
            resp = Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            clear_refresh_cookie(resp, portal)
            return resp
        refresh, access = issue_pair(user, portal, auth_time=auth_time)
        resp = Response(session_payload(user, access))
        set_refresh_cookie(resp, portal, refresh)
        return resp

    @staticmethod
    def _consume(raw, portal):
        """Validate the refresh token and blacklist it (single use). Returns (user, auth_time)."""
        token = RefreshToken(raw)  # signature, expiry, type, and blacklist check
        if token.get("portal") != portal:
            raise TokenError("Session belongs to a different portal.")
        user = User.objects.filter(pk=token.get(jwt_settings.USER_ID_CLAIM), is_active=True).first()
        if user is None or token.get("sv") != user.session_version or not role_allowed(user, portal):
            raise TokenError("Session has been revoked. Please sign in again.")
        auth_time = int(token.get("auth_time", 0))
        if time.time() - auth_time > PORTALS[portal]["max_session"].total_seconds():
            raise TokenError("Session expired. Please sign in again.")
        with transaction.atomic():
            outstanding = OutstandingToken.objects.select_for_update().filter(jti=token["jti"]).first()
            if outstanding is None:
                raise TokenError("Unknown session.")
            _, created = BlacklistedToken.objects.get_or_create(token=outstanding)
        if not created:  # lost a race with a concurrent refresh of the same token
            log.warning("refresh token replay: user=%s portal=%s", user.pk, portal)
            raise TokenError("Session already used. Please sign in again.")
        return user, auth_time


class LogoutView(APIView):
    """POST + X-FGX-Portal: revoke this portal's refresh token and clear its cookie."""

    permission_classes = [AllowAny]  # must work even once the access token has expired
    authentication_classes = []

    def post(self, request):
        portal = portal_from(request)
        raw = request.COOKIES.get(cookie_name(portal))
        if raw:
            try:
                RefreshToken(raw).blacklist()
            except TokenError:
                pass  # already expired/revoked - nothing left to kill
        resp = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(resp, portal)
        return resp


class LogoutAllView(APIView):
    """POST (authenticated): sign this user out of every device and portal."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        portal = portal_from(request)
        revoke_all_sessions(request.user)
        resp = Response(status=status.HTTP_204_NO_CONTENT)
        clear_refresh_cookie(resp, portal)
        return resp
