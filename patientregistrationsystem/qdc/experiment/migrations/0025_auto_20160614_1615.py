# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0024_eeg_electrode_model_null_for_position_setting'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='eegelectrodelayoutsetting',
            name='number_of_electrodes',
        ),
        migrations.RemoveField(
            model_name='eegelectrodelocalizationsystem',
            name='number_of_electrodes',
        ),
        migrations.AlterField(
            model_name='eegdata',
            name='eeg_cap_size',
            field=models.ForeignKey(to='experiment.EEGCapSize', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='eegelectrodeposition',
            name='eeg_electrode_localization_system',
            field=models.ForeignKey(related_name='electrode_positions', to='experiment.EEGElectrodeLocalizationSystem'),
        ),
        migrations.AlterField(
            model_name='eegelectrodeposition',
            name='position_reference',
            field=models.ForeignKey(related_name='children',
                                    to='experiment.EEGElectrodePosition', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='eegelectrodepositioncollectionstatus',
            name='eeg_data',
            field=models.ForeignKey(related_name='electrode_positions', to='experiment.EEGData'),
        ),
    ]
