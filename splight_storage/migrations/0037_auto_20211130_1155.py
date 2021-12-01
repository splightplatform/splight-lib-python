# Generated by Django 3.2.8 on 2021-11-30 11:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('splight_storage', '0036_clientmapping_servermapping'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientmapping',
            name='connector',
        ),
        migrations.RemoveField(
            model_name='clientmapping',
            name='id',
        ),
        migrations.RemoveField(
            model_name='clientmapping',
            name='path',
        ),
        migrations.RemoveField(
            model_name='clientmapping',
            name='tenant',
        ),
        migrations.RemoveField(
            model_name='servermapping',
            name='connector',
        ),
        migrations.RemoveField(
            model_name='servermapping',
            name='id',
        ),
        migrations.RemoveField(
            model_name='servermapping',
            name='path',
        ),
        migrations.RemoveField(
            model_name='servermapping',
            name='tenant',
        ),
        migrations.AlterField(
            model_name='clientmapping',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client_mappings', to='splight_storage.asset'),
        ),
        migrations.CreateModel(
            name='Mapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=300)),
                ('connector', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='splight_storage.connector')),
                ('tenant', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='splight_storage.tenant')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='clientmapping',
            name='mapping_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='splight_storage.mapping'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='servermapping',
            name='mapping_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='splight_storage.mapping'),
            preserve_default=False,
        ),
    ]
