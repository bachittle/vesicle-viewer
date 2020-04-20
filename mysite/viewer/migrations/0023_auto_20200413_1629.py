# Generated by Django 2.2.7 on 2020-04-13 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0022_auto_20200413_1626'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lipid_augmentation',
            name='tmv_scattering_net_change',
        ),
        migrations.RemoveField(
            model_name='sample_lipid_augmentation',
            name='tmv_scattering_net_change',
        ),
        migrations.AddField(
            model_name='lipid_augmentation',
            name='tmg_scattering_net_change',
            field=models.FloatField(default=0, verbose_name='terminal methyl scattering length net change'),
        ),
        migrations.AddField(
            model_name='sample_lipid_augmentation',
            name='tmg_scattering_net_change',
            field=models.FloatField(default=0, verbose_name='terminal methyl scattering length net change'),
        ),
    ]
