# Generated manually for the coursework task.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.utils import timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('jti', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('created_at', models.DateTimeField(default=timezone.now)),
                ('expires_at', models.DateTimeField()),
                ('revoked_at', models.DateTimeField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jwt_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Сессия JWT',
                'verbose_name_plural': 'Сессии JWT',
            },
        ),
        migrations.AddIndex(
            model_name='usersession',
            index=models.Index(fields=['user'], name='auth_api_us_user_id_2f72f1_idx'),
        ),
        migrations.AddIndex(
            model_name='usersession',
            index=models.Index(fields=['expires_at'], name='auth_api_us_expires_7b7b21_idx'),
        ),
    ]
