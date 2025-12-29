"""Sync remaining model changes:
- Remove Inquilino.nome_responsavel
- Alter Inquilino.apartamento max_length -> 10
- Add HistoricoUso.custo_creditos with default 1
- Remove related_name attributes on HistoricUso foreign keys (represented as AlterField)
- Alter Maquina.status and tempo_minutos to match models
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("laundry", "0005_update_maquina_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inquilino',
            name='nome_responsavel',
        ),
        migrations.AlterField(
            model_name='inquilino',
            name='apartamento',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AddField(
            model_name='historicouso',
            name='custo_creditos',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='historicouso',
            name='inquilino',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='laundry.inquilino'),
        ),
        migrations.AlterField(
            model_name='historicouso',
            name='maquina',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='laundry.maquina'),
        ),
        migrations.AlterField(
            model_name='maquina',
            name='status',
            field=models.CharField(choices=[('Disponível', 'Disponível'), ('Em Uso', 'Em Uso'), ('Manutenção', 'Manutenção')], default='Disponível', max_length=20),
        ),
        migrations.AlterField(
            model_name='maquina',
            name='tempo_minutos',
            field=models.IntegerField(default=30, help_text='Tempo do ciclo em minutos'),
        ),
    ]
