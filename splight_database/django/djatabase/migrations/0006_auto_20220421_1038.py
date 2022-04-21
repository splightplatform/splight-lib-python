# Generated by Django 3.2.8 on 2022-04-21 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djatabase', '0005_alter_rule_variables'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rule',
            name='variables',
        ),
        migrations.AddField(
            model_name='rule',
            name='variables',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='RuleVariable',
        ),
    ]
