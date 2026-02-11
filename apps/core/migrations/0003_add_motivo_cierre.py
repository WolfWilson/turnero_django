# Generated manually by Copilot - 2026-02-11
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_llamadaturno'),
    ]

    operations = [
        migrations.CreateModel(
            name='MotivoCierre',
            fields=[
                ('id', models.AutoField(db_column='IdMotivoCierre', primary_key=True, serialize=False)),
                ('nombre', models.CharField(db_column='Nombre', max_length=100, unique=True)),
                ('descripcion', models.CharField(blank=True, db_column='Descripcion', max_length=255)),
                ('activo', models.BooleanField(db_column='Activo', default=True)),
                ('orden', models.SmallIntegerField(db_column='Orden', default=0)),
            ],
            options={
                'db_table': 'MotivoCierre',
                'ordering': ['orden', 'nombre'],
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='turno',
            name='motivo_cierre',
            field=models.ForeignKey(blank=True, db_column='FkIdMotivoCierre', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='turnos', to='core.motivocierre'),
        ),
        migrations.AddField(
            model_name='turno',
            name='prioridad_consulta',
            field=models.SmallIntegerField(db_column='PrioridadConsulta', default=0),
        ),
        migrations.AddField(
            model_name='turno',
            name='observaciones',
            field=models.TextField(blank=True, db_column='Observaciones', null=True),
        ),
    ]
