# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0065_populate_number_of_channels_used_eegamplifiersettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eegmachine',
            name='equipment_ptr',
        ),
        migrations.RemoveField(
            model_name='eegmachinesetting',
            name='eeg_machine',
        ),
        migrations.RemoveField(
            model_name='eegmachinesetting',
            name='eeg_setting',
        ),
        migrations.DeleteModel(
            name='EEGMachine',
        ),
        migrations.DeleteModel(
            name='EEGMachineSetting',
        ),
    ]
