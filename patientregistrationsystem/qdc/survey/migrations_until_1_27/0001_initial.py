# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('lime_survey_id', models.IntegerField(unique=True)),
                ('is_initial_evaluation', models.BooleanField(default=True)),
            ],
            options={
                'permissions': (('view_survey', 'Can view survey'),),
            },
        ),
    ]
