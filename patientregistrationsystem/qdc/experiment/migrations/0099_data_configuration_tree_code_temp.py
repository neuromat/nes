# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0098_increased_field_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoalkeeperGameConfig',
            fields=[
                ('idconfig', models.IntegerField(serialize=False, primary_key=True)),
                ('experimentgroup', models.CharField(max_length=50)),
                ('phase', models.IntegerField()),
                ('playeralias', models.CharField(max_length=20)),
                ('sequexecuted', models.TextField()),
                ('gamedata', models.CharField(max_length=6)),
                ('gametime', models.CharField(max_length=6)),
                ('idresult', models.IntegerField()),
            ],
            options={
                'managed': False,
                'db_table': '"public"."gameconfig"',
            },
        ),
        migrations.CreateModel(
            name='GoalkeeperGameResults',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('filecontent', models.TextField()),
            ],
            options={
                'managed': False,
                'db_table': '"public"."results"',
            },
        ),
        migrations.AddField(
            model_name='dataconfigurationtree',
            name='code_number',
            field=models.IntegerField(null=True, blank=True),
        ),
        # migrations.AddField(
        #     model_name='hotspot',
        #     name='hot_spot_map',
        #     field=models.FileField(null=True, blank=True, upload_to=experiment.models.get_data_file_dir),
        # ),
    ]
