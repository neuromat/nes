# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0083_tmsdata_fields_update'),
    ]

    operations = [
        migrations.CreateModel(
            name='Goolkeeper_game',
            fields=[
                ('component_ptr', models.OneToOneField(serialize=False, auto_created=True, parent_link=True, primary_key=True, to='experiment.Component')),
                ('text', models.TextField()),
            ],
            bases=('experiment.component',),
        ),
        migrations.AlterField(
            model_name='component',
            name='component_type',
            field=models.CharField(max_length=15, choices=[('block', 'Set of steps'), ('instruction', 'Instruction'), ('pause', 'Pause'), ('questionnaire', 'Questionnaire'), ('stimulus', 'Stimulus'), ('task', 'Task for participant'), ('task_experiment', 'Task for experimenter'), ('eeg', 'EEG'), ('emg', 'EMG'), ('tms', 'TMS'), ('goolkeeper_game', 'Goolkeeper game')]),
        ),
    ]
