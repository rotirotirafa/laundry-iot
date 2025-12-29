"""Migration to rename identificador -> apartamento, add password, and alter creditos default

This preserves existing data by renaming the column instead of dropping it.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("laundry", "0003_maquina_tempo_ciclo_minutos"),
    ]

    operations = [
        migrations.RenameField(
            model_name="inquilino",
            old_name="identificador",
            new_name="apartamento",
        ),
        migrations.AddField(
            model_name="inquilino",
            name="password",
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name="inquilino",
            name="creditos",
            field=models.IntegerField(default=10),
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: _set_default_creditos(apps),
            reverse_code=migrations.RunPython.noop,
        ),
    ]


def _set_default_creditos(apps):
    Inquilino = apps.get_model("laundry", "Inquilino")
    for i in Inquilino.objects.all():
        if not i.creditos or i.creditos < 10:
            i.creditos = 10
            i.save()
