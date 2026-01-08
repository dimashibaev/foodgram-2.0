from rest_framework.permissions import BasePermission

from access_control.services import user_has_role


class IsAdminRole(BasePermission):
    message = 'Admin role required'

    def has_permission(self, request, view):
        user = request.user
        return bool(getattr(user, 'is_authenticated', False) and (user.is_superuser or user_has_role(user, 'admin')))
