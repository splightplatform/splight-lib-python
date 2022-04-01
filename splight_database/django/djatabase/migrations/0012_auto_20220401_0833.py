# Generated by Django 3.2.8 on 2022-04-01 08:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djatabase', '0011_chart_dashboard_filter_tab'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chart',
            name='filters',
        ),
        migrations.AddField(
            model_name='filter',
            name='chart_item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='filters', to='djatabase.chart'),
        ),
        migrations.AlterField(
            model_name='chart',
            name='refresh_interval',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='chart',
            name='relative_window_time',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='chart',
            name='type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='dashboard',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='filter',
            name='key',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='filter',
            name='operator',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='filter',
            name='value',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='tab',
            name='dashboard',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_tabs', to='djatabase.dashboard'),
        ),
        migrations.AlterField(
            model_name='tab',
            name='name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='ChartItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('chart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chart_items', to='djatabase.chart')),
                ('namespace', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='djatabase.namespace')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
    ]
