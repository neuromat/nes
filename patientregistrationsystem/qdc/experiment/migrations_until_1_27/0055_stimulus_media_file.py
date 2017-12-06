# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0054_initial_coil_shape_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='stimulus',
            name='media_file',
            field=models.FileField(blank=True, upload_to=experiment.models.get_stimulus_media_file_dir, null=True),
        ),
        migrations.AlterField(
            model_name='component',
            name='component_type',
            field=models.CharField(choices=[('block', 'Set of steps'), ('instruction', 'Instruction'),
                                            ('pause', 'Pause'), ('questionnaire', 'Questionnaire'),
                                            ('stimulus', 'Stimulus'), ('task', 'Task for participant'),
                                            ('task_experiment', 'Task for experimenter'), ('eeg', 'EEG'),
                                            ('emg', 'EMG'), ('tms', 'TMS')],
                                   max_length=15),
        ),
        migrations.AlterField(
            model_name='equipment',
            name='equipment_type',
            field=models.CharField(choices=[('eeg_machine', 'EEG Machine'), ('amplifier', 'Amplifier'),
                                            ('eeg_solution', 'EEG Solution'), ('filter', 'Filter'),
                                            ('eeg_electrode_net', 'EEG Electrode Net'),
                                            ('ad_converter', 'A/D Converter'), ('tms_device', 'TMS device')],
                                   max_length=50, blank=True, null=True),
        ),
    ]
