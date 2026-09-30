from django.db import migrations


def seed_roles(apps, schema_editor):
    role = apps.get_model("users", "Role")
    for slug in ["admin", "coach", "member"]:
        role.objects.using(schema_editor.connection.alias).get_or_create(slug=slug)


class Migration(migrations.Migration):
    dependencies = [("users", "0001_initial")]
    operations = [migrations.RunPython(seed_roles, migrations.RunPython.noop)]
