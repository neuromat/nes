# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0066_delete_models_EEGMachine_EEGMachineSetting'),
    ]

    operations = [
        migrations.AddField(
            model_name='componentconfiguration',
            name='requires_start_and_end_datetime',
            field=models.BooleanField(default=False),
        ),
    ]
