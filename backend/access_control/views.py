from rest_framework import viewsets

from access_control.models import AccessRoleRule, BusinessElement, Role, UserRole
from access_control.permissions import IsAdminRole
from access_control.serializers import (
    AccessRoleRuleSerializer,
    BusinessElementSerializer,
    RoleSerializer,
    UserRoleSerializer,
)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    permission_classes = [IsAdminRole]


class BusinessElementViewSet(viewsets.ModelViewSet):
    queryset = BusinessElement.objects.all().order_by('id')
    serializer_class = BusinessElementSerializer
    permission_classes = [IsAdminRole]


class AccessRoleRuleViewSet(viewsets.ModelViewSet):
    queryset = AccessRoleRule.objects.all().select_related('role', 'element').order_by('id')
    serializer_class = AccessRoleRuleSerializer
    permission_classes = [IsAdminRole]


class UserRoleViewSet(viewsets.ModelViewSet):
    queryset = UserRole.objects.all().select_related('user', 'role').order_by('id')
    serializer_class = UserRoleSerializer
    permission_classes = [IsAdminRole]
