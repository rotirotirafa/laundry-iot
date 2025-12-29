"""Update Maquina fields to match current models:
- Rename ip_tomada -> ip_address
- Rename tempo_ciclo_minutos -> tempo_minutos
- Alter nome max_length to 50
- Alter ip_address to be unique
- Add custo_creditos
- Remove tipo, device_id, local_key
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("laundry", "0004_update_inquilino_fields"),
    ]

    operations = [
        migrations.RenameField(
            model_name='maquina',
            old_name='ip_tomada',
            new_name='ip_address',
        ),
        migrations.RenameField(
            model_name='maquina',
            old_name='tempo_ciclo_minutos',
            new_name='tempo_minutos',
        ),
        migrations.AlterField(
            model_name='maquina',
            name='nome',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='maquina',
            name='ip_address',
            field=models.GenericIPAddressField(unique=True),
        ),
        migrations.AddField(
            model_name='maquina',
            name='custo_creditos',
            field=models.IntegerField(default=1),
        ),
        migrations.RemoveField(
            model_name='maquina',
            name='tipo',
        ),
        migrations.RemoveField(
            model_name='maquina',
            name='device_id',
        ),
        migrations.RemoveField(
            model_name='maquina',
            name='local_key',
        ),
    ]
