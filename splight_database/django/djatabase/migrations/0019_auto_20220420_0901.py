# Generated by Django 3.2.8 on 2022-04-20 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djatabase', '0018_merge_20220412_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='chart',
            name='timestamp_gte',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='chart',
            name='timestamp_lte',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
