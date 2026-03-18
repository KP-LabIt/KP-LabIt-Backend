# Ensures student / teacher / admin roles exist (required for User.default role & CI).

from django.db import migrations


def seed_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    defaults = [
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("admin", "Administrator"),
    ]
    for name, description in defaults:
        Role.objects.get_or_create(
            name=name,
            defaults={"description": description},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_must_change_password_alter_user_role"),
    ]

    operations = [
        migrations.RunPython(seed_roles, migrations.RunPython.noop),
    ]
