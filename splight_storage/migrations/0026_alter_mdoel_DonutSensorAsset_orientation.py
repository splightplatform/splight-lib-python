# Generated by Django 3.2.8 on 2021-11-17 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('splight_storage', '0025_create_model_DonutSensorAsset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donutsensorasset',
            name='angle',
            field=models.DecimalField(decimal_places=2, max_digits=4),
        ),
    ]
