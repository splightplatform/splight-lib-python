# Generated by Django 3.2.8 on 2022-04-11 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djatabase', '0015_auto_20220406_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientmapping',
            name='period',
            field=models.IntegerField(default=5000),
        ),
    ]
