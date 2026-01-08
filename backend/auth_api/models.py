import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class UserSession(models.Model):
    """Серверная сессия для JWT (logout реализуется через отзыв сессии)."""

    jti = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jwt_sessions',
    )
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user'], name='auth_api_us_user_id_2f72f1_idx'),
            models.Index(fields=['expires_at'], name='auth_api_us_expires_7b7b21_idx'),
        ]
        verbose_name = 'Сессия JWT'
        verbose_name_plural = 'Сессии JWT'

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None and self.expires_at > timezone.now()

    def revoke(self):
        if self.revoked_at is None:
            self.revoked_at = timezone.now()
            self.save(update_fields=['revoked_at'])
