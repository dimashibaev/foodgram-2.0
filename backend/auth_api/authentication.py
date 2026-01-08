from __future__ import annotations

import os
from datetime import timedelta
from typing import Optional, Tuple

import jwt
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from auth_api.models import UserSession

User = get_user_model()


def _jwt_secret() -> str:
    return os.getenv('JWT_SECRET_KEY') or os.getenv('SECRET_KEY') or 'changeme'


def _jwt_ttl_seconds() -> int:
    # 7 дней по умолчанию (можно переопределить переменной окружения)
    return int(os.getenv('JWT_TTL_SECONDS', str(7 * 24 * 60 * 60)))


def create_jwt_for_user(user: User) -> Tuple[str, UserSession]:
    """Создаёт серверную сессию и подписанный JWT."""
    now = timezone.now()
    expires_at = now + timedelta(seconds=_jwt_ttl_seconds())
    session = UserSession.objects.create(user=user, expires_at=expires_at)

    payload = {
        'sub': str(user.pk),
        'jti': str(session.jti),
        'iat': int(now.timestamp()),
        'exp': int(expires_at.timestamp()),
    }
    token = jwt.encode(payload, _jwt_secret(), algorithm='HS256')
    return token, session


def decode_and_validate(token: str) -> Tuple[User, UserSession]:
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=['HS256'])
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationFailed('Token expired') from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationFailed('Invalid token') from exc

    user_id = payload.get('sub')
    jti = payload.get('jti')
    if not user_id or not jti:
        raise AuthenticationFailed('Invalid token payload')

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist as exc:
        raise AuthenticationFailed('User not found') from exc

    if not user.is_active:
        raise AuthenticationFailed('User is inactive')

    try:
        session = UserSession.objects.get(jti=jti, user=user)
    except UserSession.DoesNotExist as exc:
        raise AuthenticationFailed('Session not found') from exc

    if not session.is_active:
        raise AuthenticationFailed('Session revoked or expired')

    return user, session


class JWTAuthentication(authentication.BaseAuthentication):
    """Bearer JWT auth (Authorization: Bearer <token>)."""

    keyword = 'Bearer'

    def authenticate(self, request) -> Optional[Tuple[User, str]]:
        auth_header = request.headers.get('Authorization') or ''
        auth_header = auth_header.strip()
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2:
            return None

        keyword, token = parts
        if keyword.lower() != self.keyword.lower():
            return None

        user, _session = decode_and_validate(token)
        return (user, token)
