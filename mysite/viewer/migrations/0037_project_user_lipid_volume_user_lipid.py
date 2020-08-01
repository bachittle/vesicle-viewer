# Generated by Django 2.2.13 on 2020-07-20 19:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0036_auto_20200705_1237'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_Lipid',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_lipid_name', models.CharField(max_length=100, verbose_name='user lipid name')),
                ('hg_scattering', models.FloatField(default=0, verbose_name='user head group scattering length')),
                ('hg_electrons', models.FloatField(default=0, verbose_name='user head group electrons')),
                ('hg_volume', models.FloatField(default=0, verbose_name='user head group volume')),
                ('tg_scattering', models.FloatField(default=0, verbose_name='user tail group scattering length')),
                ('tg_electrons', models.FloatField(default=0, verbose_name='user tail group electrons')),
                ('tm_scattering', models.FloatField(default=0, verbose_name='user terminal methyl scattering length')),
                ('tm_electrons', models.FloatField(default=0, verbose_name='user terminal methyl electrons')),
                ('owner', models.ForeignKey(default='admin', on_delete=django.db.models.deletion.CASCADE, related_name='user_lipid_owner', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user lipid',
                'verbose_name_plural': 'user lipids',
            },
        ),
        migrations.CreateModel(
            name='Project_User_Lipid_Volume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_lipid_volume', models.FloatField(default=0, verbose_name='user lipid volume')),
                ('project_title', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_user_lipid', to='viewer.Project')),
                ('project_user_lipid_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_user_lipid_name', to='viewer.User_Lipid')),
            ],
            options={
                'verbose_name': 'user lipid volume',
                'verbose_name_plural': 'user lipid volumes',
            },
        ),
    ]