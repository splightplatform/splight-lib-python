# Generated by Django 3.2.8 on 2022-06-14 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djatabase', '0020_chart_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chart',
            name='position',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
