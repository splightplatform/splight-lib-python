# Generated by Django 3.2.8 on 2022-04-27 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djatabase', '0007_auto_20220421_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='chartitem',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
