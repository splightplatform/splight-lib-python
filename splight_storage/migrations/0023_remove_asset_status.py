# Generated by Django 3.2.8 on 2021-11-12 14:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('splight_storage', '0022_alter_Asset_create_status_field'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='status',
        ),
    ]
