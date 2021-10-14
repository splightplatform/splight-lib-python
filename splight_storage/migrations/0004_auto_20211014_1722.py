# Generated by Django 3.2.8 on 2021-10-14 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('splight_storage', '0003_auto_20211014_1710'),
    ]

    operations = [
        migrations.CreateModel(
            name='Line',
            fields=[
                ('asset_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='splight_storage.asset')),
                ('type', models.CharField(max_length=100)),
                ('base_voltage', models.FloatField(default=0)),
                ('current_limit', models.FloatField(default=0)),
                ('b0ch', models.FloatField(default=0)),
                ('bch', models.FloatField(default=0)),
                ('g0ch', models.FloatField(default=0)),
                ('gch', models.FloatField(default=0)),
                ('length', models.FloatField(default=0)),
                ('r', models.FloatField(default=0)),
                ('x', models.FloatField(default=0)),
                ('x0', models.FloatField(default=0)),
            ],
            bases=('splight_storage.asset',),
        ),
        migrations.AlterField(
            model_name='bus',
            name='base_voltage',
            field=models.FloatField(default=0),
        ),
    ]
