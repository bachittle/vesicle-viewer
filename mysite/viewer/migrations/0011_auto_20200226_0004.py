# Generated by Django 2.2.7 on 2020-02-26 05:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0010_auto_20200225_2346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='model_type',
            field=models.CharField(choices=[('SM', 'Symmetrical'), ('AS', 'Asymmetrical')], max_length=3, verbose_name='model'),
        ),
    ]
