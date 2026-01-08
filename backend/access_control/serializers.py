from rest_framework import serializers

from access_control.models import AccessRoleRule, BusinessElement, Role, UserRole


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name', 'description')


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = ('id', 'code', 'name')


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ('id', 'user', 'role')


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessRoleRule
        fields = (
            'id',
            'role',
            'element',
            'read_permission',
            'read_all_permission',
            'create_permission',
            'update_permission',
            'update_all_permission',
            'delete_permission',
            'delete_all_permission',
        )
