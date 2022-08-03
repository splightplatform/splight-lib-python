# Generated by Django 3.2.8 on 2022-07-29 16:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djatabase', '0037_auto_20220726_1531'),
    ]

    operations = [
        migrations.AddField(
            model_name='algorithm',
            name='asset',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asset_algorithms', to='djatabase.asset'),
        ),
        migrations.AddField(
            model_name='algorithm',
            name='sub_algorithms',
            field=models.ManyToManyField(blank=True, to='djatabase.Algorithm'),
        ),
        migrations.AlterField(
            model_name='mappingrule',
            name='operator',
            field=models.CharField(choices=[('gt', 'Greater than'), ('ge', 'Greater than or equal'), ('lt', 'Lower than'), ('le', 'Lower than or equal'), ('eq', 'Equal')], default='eq', max_length=20),
        ),
    ]
