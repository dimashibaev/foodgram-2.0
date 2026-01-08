import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import IntegrityError, transaction

from access_control.models import (
    AccessRoleRule,
    BusinessElement,
    ProtectedObject,
    Role,
    UserRole,
)
from access_control.services import ensure_base_roles_and_elements

User = get_user_model()


class Command(BaseCommand):
    help = "Initialize base roles, business-elements and access rules (coursework task)."

    @transaction.atomic
    def handle(self, *args, **options):
        ensure_base_roles_and_elements()

        roles = {r.name: r for r in Role.objects.all()}
        elements = list(BusinessElement.objects.all())

        def upsert_rule(role, element, **perms):
            AccessRoleRule.objects.update_or_create(
                role=role,
                element=element,
                defaults=perms,
            )

        # admin: полный доступ
        for el in elements:
            upsert_rule(
                roles["admin"],
                el,
                read_permission=True,
                read_all_permission=True,
                create_permission=True,
                update_permission=True,
                update_all_permission=True,
                delete_permission=True,
                delete_all_permission=True,
            )

        # manager: полный доступ к orders, просмотр всего recipes, пользователей только просмотр
        for el in elements:
            if el.code == "orders":
                upsert_rule(
                    roles["manager"],
                    el,
                    read_permission=True,
                    read_all_permission=True,
                    create_permission=True,
                    update_permission=True,
                    update_all_permission=True,
                    delete_permission=True,
                    delete_all_permission=True,
                )
            elif el.code == "recipes":
                upsert_rule(
                    roles["manager"],
                    el,
                    read_permission=True,
                    read_all_permission=True,
                    create_permission=True,
                    update_permission=True,
                    update_all_permission=True,
                    delete_permission=True,
                    delete_all_permission=True,
                )
            elif el.code == "users":
                upsert_rule(
                    roles["manager"],
                    el,
                    read_permission=True,
                    read_all_permission=True,
                    create_permission=False,
                    update_permission=False,
                    update_all_permission=False,
                    delete_permission=False,
                    delete_all_permission=False,
                )
            else:
                upsert_rule(roles["manager"], el)

        # user: может создавать свои recipes и смотреть только свои
        for el in elements:
            if el.code == "recipes":
                upsert_rule(
                    roles["user"],
                    el,
                    read_permission=True,
                    read_all_permission=False,
                    create_permission=True,
                    update_permission=True,
                    update_all_permission=False,
                    delete_permission=True,
                    delete_all_permission=False,
                )
            else:
                upsert_rule(roles["user"], el)

        # guest: по умолчанию всё запрещено
        for el in elements:
            upsert_rule(roles["guest"], el)

        # optional: create admin user for demo (idempotent)
        admin_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        admin_email = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin12345")

        try:
            user, created = User.objects.get_or_create(
                username=admin_username,
                defaults={
                    "email": admin_email,
                    "is_staff": True,
                    "is_superuser": True,
                    "first_name": "Admin",
                    "last_name": "User",
                },
            )
        except IntegrityError:
            user = User.objects.get(username=admin_username)
            created = False

        updated_fields = []

        if user.first_name != "Admin":
            user.first_name = "Admin"
            updated_fields.append("first_name")
        if user.last_name != "User":
            user.last_name = "User"
            updated_fields.append("last_name")
        if not user.is_staff:
            user.is_staff = True
            updated_fields.append("is_staff")
        if not user.is_superuser:
            user.is_superuser = True
            updated_fields.append("is_superuser")

        if admin_email and user.email != admin_email:
            email_taken = User.objects.filter(email=admin_email).exclude(pk=user.pk).exists()
            if not email_taken:
                user.email = admin_email
                updated_fields.append("email")

        if updated_fields:
            user.save(update_fields=updated_fields)

        if admin_password and (created or not user.has_usable_password()):
            user.set_password(admin_password)
            user.save(update_fields=["password"])

        UserRole.objects.get_or_create(user=user, role=roles["admin"])

        # Создаем демонстрационные защищаемые объекты в БД (ID + имя),
        # чтобы можно было проверить права read/read_all и т.п.
        admin_user = (
            User.objects.filter(is_superuser=True).order_by("id").first()
            or User.objects.order_by("id").first()
        )
        if admin_user:
            for element in BusinessElement.objects.all():
                if not ProtectedObject.objects.filter(element=element).exists():
                    for i in range(1, 4):
                        ProtectedObject.objects.create(
                            element=element,
                            owner=admin_user,
                            name=f"{element.name} — объект {i}",
                        )

        self.stdout.write(self.style.SUCCESS("Access control data initialized."))
