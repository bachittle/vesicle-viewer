# Generated by Django 2.2.13 on 2020-08-20 01:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viewer', '0045_auto_20200819_2125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sample_lipid',
            name='sample_lipid_custom_augment',
        ),
    ]