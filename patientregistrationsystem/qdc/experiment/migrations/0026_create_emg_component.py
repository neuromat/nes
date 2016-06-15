# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0025_auto_20160614_1615'),
    ]

    operations = [
        migrations.CreateModel(
            name='EMG',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component',
                                                       primary_key=True, serialize=False, parent_link=True)),
            ],
            bases=('experiment.component',),
        ),
        migrations.AlterField(
            model_name='component',
            name='component_type',
            field=models.CharField(
                choices=[('block', 'Set of steps'), ('instruction', 'Instruction'), ('pause', 'Pause'),
                         ('questionnaire', 'Questionnaire'), ('stimulus', 'Stimulus'),
                         ('task', 'Task for participant'), ('task_experiment', 'Task for experimenter'),
                         ('eeg', 'EEG'), ('emg', 'EMG')],
                max_length=15),
        ),
    ]
