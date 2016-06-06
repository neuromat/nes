# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0023_eeg_electrode_model_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eegelectrodepositionsetting',
            name='electrode_model',
            field=models.ForeignKey(to='experiment.EEGElectrodeModel'),
        ),
    ]
