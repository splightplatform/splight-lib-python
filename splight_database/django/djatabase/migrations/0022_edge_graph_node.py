# Generated by Django 3.2.8 on 2022-06-14 10:14

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('djatabase', '0021_alter_chart_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='Graph',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('modifiable', models.BooleanField(default=True)),
                ('namespace', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='djatabase.namespace')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=100)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='djatabase.asset')),
                ('graph', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nodes', to='djatabase.graph')),
                ('namespace', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='djatabase.namespace')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('directed', models.BooleanField(default=False)),
                ('graph', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='edges', to='djatabase.graph')),
                ('namespace', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='djatabase.namespace')),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_edges', to='djatabase.node')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='incoming_edges', to='djatabase.node')),
            ],
            options={
                'ordering': ['-id'],
                'abstract': False,
            },
        ),
    ]
