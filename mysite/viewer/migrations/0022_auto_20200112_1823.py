# Generated by Django 2.2.7 on 2020-01-12 23:23

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0021_auto_20200112_1819'),
    ]

    operations = [
        migrations.AlterField(
            model_name='symmetrical_parameters',
            name='fit_report',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=500), blank=True, size=None, verbose_name='fitted parameter report'),
        ),
    ]
