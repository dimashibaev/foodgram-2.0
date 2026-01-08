from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_api.authentication import create_jwt_for_user, decode_and_validate
from auth_api.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UserMeSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _session = create_jwt_for_user(user)
        return Response(
            {'token': token, 'user': UserMeSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'detail': 'User is inactive'}, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        token, _session = create_jwt_for_user(user)
        return Response({'token': token, 'user': UserMeSerializer(user).data})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        auth_header = request.headers.get('Authorization') or ''
        if not auth_header.lower().startswith('bearer '):
            return Response(status=status.HTTP_204_NO_CONTENT)

        token = auth_header.split(' ', 1)[1].strip()
        try:
            _user, session = decode_and_validate(token)
            session.revoke()
        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserMeSerializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserMeSerializer(request.user).data)

    def delete(self, request):
        # мягкое удаление: деактивация
        user = request.user
        user.is_active = False
        user.save(update_fields=['is_active'])
        # отзываем все активные сессии
        user.jwt_sessions.filter(revoked_at__isnull=True).update(revoked_at=timezone.now())
        return Response(status=status.HTTP_204_NO_CONTENT)
