from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q

from access_control.models import AccessRoleRule, BusinessElement, Role, UserRole


DEFAULT_ROLE = 'user'
ADMIN_ROLE = 'admin'


@dataclass(frozen=True)
class EffectivePermissions:
    read_permission: bool = False
    read_all_permission: bool = False
    create_permission: bool = False
    update_permission: bool = False
    update_all_permission: bool = False
    delete_permission: bool = False
    delete_all_permission: bool = False


def ensure_base_roles_and_elements():
    """Создаёт базовые роли/элементы, если их ещё нет."""
    Role.objects.get_or_create(name='admin', defaults={'description': 'Администратор'})
    Role.objects.get_or_create(name='manager', defaults={'description': 'Менеджер'})
    Role.objects.get_or_create(name='user', defaults={'description': 'Пользователь'})
    Role.objects.get_or_create(name='guest', defaults={'description': 'Гость'})

    # Набор бизнес-элементов для мок-ресурсов и демонстрации
    for code, name in [
        ('users', 'Пользователи'),
        ('recipes', 'Рецепты'),
        ('orders', 'Заказы'),
        ('shops', 'Магазины'),
    ]:
        BusinessElement.objects.get_or_create(code=code, defaults={'name': name})


def ensure_default_role_for_user(user):
    role, _ = Role.objects.get_or_create(name=DEFAULT_ROLE, defaults={'description': 'Пользователь'})
    UserRole.objects.get_or_create(user=user, role=role)


def user_has_role(user, role_name: str) -> bool:
    if not user or isinstance(user, AnonymousUser) or not getattr(user, 'is_authenticated', False):
        return False
    return UserRole.objects.filter(user=user, role__name=role_name).exists()


def get_effective_permissions(user, element_code: str) -> EffectivePermissions:
    if not user or isinstance(user, AnonymousUser) or not getattr(user, 'is_authenticated', False):
        return EffectivePermissions()

    role_ids = list(UserRole.objects.filter(user=user).values_list('role_id', flat=True))
    if not role_ids:
        # если ролей нет — считаем user
        role = Role.objects.filter(name=DEFAULT_ROLE).first()
        if role:
            role_ids = [role.id]

    try:
        element = BusinessElement.objects.get(code=element_code)
    except BusinessElement.DoesNotExist:
        return EffectivePermissions()

    rules = AccessRoleRule.objects.filter(role_id__in=role_ids, element=element)
    # union: разрешено если разрешено хотя бы одной ролью
    def any_true(field: str) -> bool:
        return rules.filter(**{field: True}).exists()

    return EffectivePermissions(
        read_permission=any_true('read_permission'),
        read_all_permission=any_true('read_all_permission'),
        create_permission=any_true('create_permission'),
        update_permission=any_true('update_permission'),
        update_all_permission=any_true('update_all_permission'),
        delete_permission=any_true('delete_permission'),
        delete_all_permission=any_true('delete_all_permission'),
    )
