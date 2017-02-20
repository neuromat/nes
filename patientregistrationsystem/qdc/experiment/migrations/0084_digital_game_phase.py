# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0083_tmsdata_fields_update'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContextTree',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('setting_text', models.TextField(blank=True, null=True)),
                ('setting_file', models.FileField(upload_to=experiment.models.get_context_tree_dir, null=True)),
                ('experiment', models.ForeignKey(to='experiment.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='DigitalGamePhase',
            fields=[
                ('component_ptr', models.OneToOneField(to='experiment.Component',
                                                       parent_link=True, auto_created=True,
                                                       serialize=False, primary_key=True)),
                ('context_tree', models.ForeignKey(to='experiment.ContextTree')),
                ('software_version', models.ForeignKey(to='experiment.SoftwareVersion')),
            ],
            bases=('experiment.component',),
        ),
        migrations.AlterField(
            model_name='component',
            name='component_type',
            field=models.CharField(choices=[('block', 'Set of steps'), ('instruction', 'Instruction'),
                                            ('pause', 'Pause'), ('questionnaire', 'Questionnaire'),
                                            ('stimulus', 'Stimulus'), ('task', 'Task for participant'),
                                            ('task_experiment', 'Task for experimenter'), ('eeg', 'EEG'),
                                            ('emg', 'EMG'), ('tms', 'TMS'),
                                            ('digital_game_phase', 'Digital game phase')],
                                   max_length=15),
        ),
    ]
