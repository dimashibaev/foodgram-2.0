from django.urls import include, path
from rest_framework.routers import DefaultRouter

from access_control.views import (
    AccessRoleRuleViewSet,
    BusinessElementViewSet,
    RoleViewSet,
    UserRoleViewSet,
)

router = DefaultRouter()
router.register('roles', RoleViewSet, basename='roles')
router.register('elements', BusinessElementViewSet, basename='elements')
router.register('rules', AccessRoleRuleViewSet, basename='rules')
router.register('user-roles', UserRoleViewSet, basename='user-roles')

urlpatterns = [
    path('', include(router.urls)),
]
