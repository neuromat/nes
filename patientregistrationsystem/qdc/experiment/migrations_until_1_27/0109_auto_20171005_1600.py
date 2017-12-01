# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0108_remove_file_from_data_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionaldatafile',
            name='additional_data',
            field=models.ForeignKey(to='experiment.AdditionalData', related_name='additional_data_files'),
        ),
        migrations.AlterField(
            model_name='digitalgamephasefile',
            name='digital_game_phase_data',
            field=models.ForeignKey(to='experiment.DigitalGamePhaseData', related_name='digital_game_phase_files'),
        ),
        migrations.AlterField(
            model_name='eegfile',
            name='eeg_data',
            field=models.ForeignKey(to='experiment.EEGData', related_name='eeg_files'),
        ),
        migrations.AlterField(
            model_name='emgfile',
            name='emg_data',
            field=models.ForeignKey(to='experiment.EMGData', related_name='emg_files'),
        ),
        migrations.AlterField(
            model_name='genericdatacollectionfile',
            name='generic_data_collection_data',
            field=models.ForeignKey(to='experiment.GenericDataCollectionData', related_name='generic_data_collection_files'),
        ),
    ]
