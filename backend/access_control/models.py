from django.conf import settings
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    code = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=128)

    class Meta:
        verbose_name = 'Бизнес-элемент'
        verbose_name_plural = 'Бизнес-элементы'

    def __str__(self):
        return f'{self.code} ({self.name})'


class UserRole(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='access_roles',
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')

    class Meta:
        unique_together = ('user', 'role')
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'

    def __str__(self):
        return f'{self.user_id}: {self.role.name}'


class AccessRoleRule(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='rules')
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name='rules')

    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'element')
        verbose_name = 'Правило доступа'
        verbose_name_plural = 'Правила доступа'

    def __str__(self):
        return f'{self.role.name} -> {self.element.code}'


class ProtectedObject(models.Model):
    """Макет защищаемого объекта (ID + имя) для демонстрации правил доступа."""

    element = models.ForeignKey(
        BusinessElement,
        on_delete=models.CASCADE,
        related_name='protected_objects',
        verbose_name='Бизнес-элемент',
    )
    name = models.CharField('Имя объекта', max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='protected_objects',
        verbose_name='Владелец',
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Защищаемый объект (макет)'
        verbose_name_plural = 'Защищаемые объекты (макет)'
        ordering = ('id',)

    def __str__(self) -> str:
        return f"{self.element.code}#{self.id}: {self.name}"
