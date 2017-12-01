# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0003_translate_data_into_english'),
    ]

    operations = [
        migrations.CreateModel(
            name='EEG',
            fields=[
                ('component_ptr', models.OneToOneField(to='experiment.Component', auto_created=True, serialize=False,
                                                       parent_link=True, primary_key=True)),
            ],
            bases=('experiment.component',),
        ),
        migrations.AlterField(
            model_name='component',
            name='component_type',
            field=models.CharField(max_length=15, choices=[('block', 'Set of steps'), ('instruction', 'Instruction'),
                                                           ('pause', 'Pause'), ('questionnaire', 'Questionnaire'),
                                                           ('stimulus', 'Stimulus'), ('task', 'Task for participant'),
                                                           ('task_experiment', 'Task for experimenter'),
                                                           ('eeg', 'EEG')]),
        ),
        migrations.AlterField(
            model_name='component',
            name='duration_unit',
            field=models.CharField(blank=True, max_length=15, null=True,
                                   choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'),
                                            ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'),
                                            ('y', 'year(s)')]),
        ),
        migrations.AlterField(
            model_name='componentconfiguration',
            name='interval_between_repetitions_unit',
            field=models.CharField(blank=True, max_length=15, null=True,
                                   choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'),
                                            ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'),
                                            ('y', 'year(s)')]),
        ),
        migrations.AlterField(
            model_name='group',
            name='classification_of_diseases',
            field=models.ManyToManyField(to='patient.ClassificationOfDiseases'),
        ),
    ]
