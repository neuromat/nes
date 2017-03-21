# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0091_initial_information_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoalkeeperGameLog',
            fields=[
                ('file_content', models.TextField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': '"public"."goalgame"',
                'managed': False,
            },
        ),
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Group'},
        ),
        migrations.AddField(
            model_name='dataconfigurationtree',
            name='code',
            field=models.CharField(null=True, blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='group',
            name='code',
            field=models.CharField(null=True, blank=True, max_length=150, unique=True, verbose_name='Code'),
        ),
    ]
