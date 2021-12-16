# Generated by Django 3.2.8 on 2021-12-16 09:27

from django.db import migrations, models
import splight_storage.models.network.vpns


class Migration(migrations.Migration):

    dependencies = [
        ('splight_storage', '0040_auto_20211210_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openvpnnetwork',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=splight_storage.models.network.vpns.upload_to),
        ),
    ]
