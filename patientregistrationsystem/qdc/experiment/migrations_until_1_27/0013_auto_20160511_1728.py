# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0012_create_eeg_setting_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eeg',
            name='eeg_setting',
            field=models.ForeignKey(to='experiment.EEGSetting'),
        ),
        migrations.AlterField(
            model_name='eegdata',
            name='eeg_setting',
            field=models.ForeignKey(to='experiment.EEGSetting'),
        ),
    ]
