# Generated by Django 3.2.8 on 2021-11-19 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('splight_storage', '0027_alter_donutsensorasset_angle'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineasset',
            name='line_type',
            field=models.CharField(choices=[('DRA', 'drake'), ('DOV', 'dove')], max_length=3, null=True),
        ),
    ]
