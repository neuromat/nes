# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0067_componentconfiguration_requires_start_and_end_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='eegelectrodeposition',
            name='channel_default_index',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='eegelectrodepositioncollectionstatus',
            name='channel_index',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='eegelectrodepositionsetting',
            name='channel_index',
            field=models.IntegerField(null=True),
        ),
    ]
