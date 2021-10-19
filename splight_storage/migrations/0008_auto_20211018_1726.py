# Generated by Django 3.2.8 on 2021-10-18 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('splight_storage', '0007_alter_powertransformerasset_windings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='asset',
            name='name',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='b',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='b0',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='base_voltage',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='code_connect',
            field=models.CharField(default='NA', max_length=10),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='current_limit',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='g',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='g0',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='r',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='r0',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='ratedS',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='ratedU',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='rground',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='x',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='x0',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='powertransformerwinding',
            name='xground',
            field=models.FloatField(default=0),
        ),
    ]
