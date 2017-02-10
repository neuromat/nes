# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0086_digital_game_phase_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='data_acquisition_is_concluded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='experiment',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalexperiment',
            name='data_acquisition_is_concluded',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='historicalexperiment',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]
