# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import experiment.models
import django.db.models.deletion
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('experiment', '0089_publication'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericDataCollection',
            fields=[
                ('component_ptr', models.OneToOneField(serialize=False,
                                                       parent_link=True,
                                                       to='experiment.Component',
                                                       primary_key=True,
                                                       auto_created=True)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='GenericDataCollectionData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('file_format_description', models.TextField(blank=True, null=True, default='')),
                ('data_configuration_tree', models.ForeignKey(null=True, blank=True,
                                                              to='experiment.DataConfigurationTree')),
                ('file_format', models.ForeignKey(to='experiment.FileFormat')),
                ('subject_of_group', models.ForeignKey(to='experiment.SubjectOfGroup')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalGenericDataCollectionData',
            fields=[
                ('id', models.IntegerField(blank=True, auto_created=True, verbose_name='ID', db_index=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file', models.TextField(max_length=100)),
                ('file_format_description', models.TextField(blank=True, null=True, default='')),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1,
                                                  choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('data_configuration_tree', models.ForeignKey(related_name='+',
                                                              on_delete=django.db.models.deletion.DO_NOTHING,
                                                              db_constraint=False, null=True, blank=True,
                                                              to='experiment.DataConfigurationTree')),
                ('file_format', models.ForeignKey(related_name='+', on_delete=django.db.models.deletion.DO_NOTHING,
                                                  db_constraint=False, null=True, blank=True,
                                                  to='experiment.FileFormat')),
                ('history_user', models.ForeignKey(related_name='+',
                                                   on_delete=django.db.models.deletion.SET_NULL, null=True,
                                                   to=settings.AUTH_USER_MODEL)),
                ('subject_of_group', models.ForeignKey(related_name='+',
                                                       on_delete=django.db.models.deletion.DO_NOTHING,
                                                       db_constraint=False, null=True, blank=True,
                                                       to='experiment.SubjectOfGroup')),
            ],
            options={
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical generic data collection data',
            },
        ),
        migrations.CreateModel(
            name='InformationType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(max_length=150, null=True)),
                ('name_en', models.CharField(max_length=150, null=True)),
                ('description', models.TextField()),
                ('description_pt_br', models.TextField(null=True)),
                ('description_en', models.TextField(null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='component',
            name='component_type',
            field=models.CharField(max_length=30,
                                   choices=[('block', 'Set of steps'), ('instruction', 'Instruction'),
                                            ('pause', 'Pause'), ('questionnaire', 'Questionnaire'),
                                            ('stimulus', 'Stimulus'), ('task', 'Task for participant'),
                                            ('task_experiment', 'Task for experimenter'), ('eeg', 'EEG'),
                                            ('emg', 'EMG'), ('tms', 'TMS'),
                                            ('digital_game_phase', 'Goalkeeper game phase'),
                                            ('generic_data_collection', 'Generic data collection')]),
        ),
        migrations.AddField(
            model_name='genericdatacollection',
            name='information_type',
            field=models.ForeignKey(to='experiment.InformationType'),
        ),
    ]
