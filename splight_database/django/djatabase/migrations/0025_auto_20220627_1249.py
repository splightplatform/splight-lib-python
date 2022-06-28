# Generated by Django 3.2.8 on 2022-06-27 17:49

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('djatabase', '0024_merge_20220616_1213'),
    ]

    operations = [
        migrations.CreateModel(
            name='Billing',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=1000)),
                ('items_type', models.CharField(max_length=255)),
                ('detailed_pricing', models.JSONField()),
                ('total_price', models.FloatField()),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BillingItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=1000)),
                ('total_price', models.FloatField()),
                ('billing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='djatabase.billing')),
                ('namespace', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='djatabase.namespace')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='algorithm',
            name='privacy_policy',
        ),
        migrations.RemoveField(
            model_name='algorithm',
            name='tenant',
        ),
        migrations.RemoveField(
            model_name='connector',
            name='privacy_policy',
        ),
        migrations.RemoveField(
            model_name='connector',
            name='tenant',
        ),
        migrations.RemoveField(
            model_name='network',
            name='privacy_policy',
        ),
        migrations.RemoveField(
            model_name='network',
            name='tenant',
        ),
        migrations.CreateModel(
            name='DeploymentBillingItem',
            fields=[
                ('billingitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='djatabase.billingitem')),
                ('computing_price', models.FloatField()),
                ('storage_price', models.FloatField()),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
            bases=('djatabase.billingitem',),
        ),
        migrations.CreateModel(
            name='MonthBilling',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('month', models.DateTimeField()),
                ('discount_detail', models.CharField(max_length=255)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=1000)),
                ('total_price_without_discount', models.DecimalField(decimal_places=2, max_digits=1000)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=1000)),
                ('paid', models.BooleanField()),
                ('namespace', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='djatabase.namespace')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BillingSettings',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField()),
                ('pricing', models.JSONField()),
                ('discounts', models.JSONField()),
                ('computing_time_measurement_per_hour', models.BooleanField()),
                ('namespace', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='djatabase.namespace')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='billing',
            name='month_billing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billings', to='djatabase.monthbilling'),
        ),
        migrations.AddField(
            model_name='billing',
            name='namespace',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='djatabase.namespace'),
        ),
    ]
