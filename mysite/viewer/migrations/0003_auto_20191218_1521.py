# Generated by Django 2.2.7 on 2019-12-18 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0002_auto_20191218_1309'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project_lipid',
            name='lipid_percentage',
        ),
        migrations.AddField(
            model_name='project_lipid',
            name='lipid_mol_fraction',
            field=models.FloatField(default=0, verbose_name='project_lipid_mol_fraction'),
        ),
    ]
