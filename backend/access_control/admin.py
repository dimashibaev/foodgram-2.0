from django.contrib import admin

from access_control.models import (
    AccessRoleRule,
    BusinessElement,
    ProtectedObject,
    Role,
    UserRole,
)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name')
    search_fields = ('code', 'name')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role')
    search_fields = ('user__email', 'user__username', 'role__name')
    list_filter = ('role__name',)


@admin.register(AccessRoleRule)
class AccessRoleRuleAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'role', 'element',
        'read_permission', 'read_all_permission',
        'create_permission',
        'update_permission', 'update_all_permission',
        'delete_permission', 'delete_all_permission',
    )
    list_filter = ('role__name', 'element__code')


@admin.register(ProtectedObject)
class ProtectedObjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'element', 'name', 'owner', 'created_at')
    list_filter = ('element',)
    search_fields = ('name', 'owner__email', 'owner__username')
