from django.contrib import admin

from auth_api.models import UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('jti', 'user', 'created_at', 'expires_at', 'revoked_at')
    list_filter = ('revoked_at',)
    search_fields = ('user__email', 'user__username', 'jti')
