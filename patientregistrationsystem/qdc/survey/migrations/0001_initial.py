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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lime_survey_id', models.IntegerField(unique=True)),
                ('is_initial_evaluation', models.BooleanField(default=True)),
            ],
            options={
                'permissions': (('view_survey', 'Can view survey'),),
            },
        ),
    ]
