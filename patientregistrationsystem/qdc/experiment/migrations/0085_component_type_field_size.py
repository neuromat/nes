# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0084_digital_game_phase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='component',
            name='component_type',
            field=models.CharField(choices=[('block', 'Set of steps'), ('instruction', 'Instruction'),
                                            ('pause', 'Pause'), ('questionnaire', 'Questionnaire'),
                                            ('stimulus', 'Stimulus'), ('task', 'Task for participant'),
                                            ('task_experiment', 'Task for experimenter'),
                                            ('eeg', 'EEG'), ('emg', 'EMG'), ('tms', 'TMS'),
                                            ('digital_game_phase', 'Goalkeeper game phase')], max_length=30),
        ),
    ]
