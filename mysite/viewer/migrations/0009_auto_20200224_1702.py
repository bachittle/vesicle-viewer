# Generated by Django 2.2.7 on 2020-02-24 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0008_auto_20200224_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='symmetrical_parameters',
            name='average_vesicle_radius_lowerbound',
            field=models.FloatField(default=250, verbose_name='avr lower bound'),
        ),
        migrations.AlterField(
            model_name='symmetrical_parameters',
            name='average_vesicle_radius_upperbound',
            field=models.FloatField(default=1000, verbose_name='avr upper bound'),
        ),
        migrations.AlterField(
            model_name='symmetrical_parameters',
            name='relative_size_lowerbound',
            field=models.FloatField(default=0.1, verbose_name='rs lower bound'),
        ),
        migrations.AlterField(
            model_name='symmetrical_parameters',
            name='relative_size_upperbound',
            field=models.FloatField(default=0.7, verbose_name='rs upper bound'),
        ),
    ]