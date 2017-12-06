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
        ('experiment', '0055_stimulus_media_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalAdditionalData',
            fields=[
                ('id', models.IntegerField(db_index=True, blank=True, auto_created=True, verbose_name='ID')),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('description', models.TextField()),
                ('file', models.TextField(max_length=100)),
                ('file_format_description', models.TextField(default='', null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'),
                                                                         ('~', 'Changed'),
                                                                         ('-', 'Deleted')])),
                ('data_configuration_tree', models.ForeignKey(related_name='+',
                                                              to='experiment.DataConfigurationTree', blank=True,
                                                              on_delete=django.db.models.deletion.DO_NOTHING,
                                                              null=True, db_constraint=False)),
                ('file_format', models.ForeignKey(related_name='+', to='experiment.FileFormat', blank=True,
                                                  on_delete=django.db.models.deletion.DO_NOTHING,
                                                  null=True, db_constraint=False)),
                ('history_user', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL,
                                                   on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('subject_of_group', models.ForeignKey(related_name='+', to='experiment.SubjectOfGroup',
                                                       blank=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                       null=True, db_constraint=False)),
            ],
            options={
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical additional data',
            },
        ),
        migrations.CreateModel(
            name='HistoricalEEGData',
            fields=[
                ('id', models.IntegerField(db_index=True, blank=True, auto_created=True, verbose_name='ID')),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('description', models.TextField()),
                ('file', models.TextField(max_length=100)),
                ('file_format_description', models.TextField(default='', null=True, blank=True)),
                ('eeg_setting_reason_for_change', models.TextField(default='', null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1,
                                                  choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('data_configuration_tree', models.ForeignKey(related_name='+', to='experiment.DataConfigurationTree',
                                                              blank=True,
                                                              on_delete=django.db.models.deletion.DO_NOTHING,
                                                              null=True, db_constraint=False)),
                ('eeg_cap_size', models.ForeignKey(related_name='+', to='experiment.EEGCapSize',
                                                   blank=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                   null=True, db_constraint=False)),
                ('eeg_setting', models.ForeignKey(related_name='+', to='experiment.EEGSetting', blank=True,
                                                  on_delete=django.db.models.deletion.DO_NOTHING, null=True,
                                                  db_constraint=False)),
                ('file_format', models.ForeignKey(related_name='+', to='experiment.FileFormat', blank=True,
                                                  on_delete=django.db.models.deletion.DO_NOTHING, null=True,
                                                  db_constraint=False)),
                ('history_user', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL,
                                                   on_delete=django.db.models.deletion.SET_NULL,
                                                   null=True)),
                ('subject_of_group', models.ForeignKey(related_name='+', to='experiment.SubjectOfGroup',
                                                       blank=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                       null=True, db_constraint=False)),
            ],
            options={
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical eeg data',
            },
        ),
        migrations.CreateModel(
            name='HistoricalEMGData',
            fields=[
                ('id', models.IntegerField(db_index=True, blank=True, auto_created=True, verbose_name='ID')),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('description', models.TextField()),
                ('file', models.TextField(max_length=100)),
                ('file_format_description', models.TextField(default='', null=True, blank=True)),
                ('emg_setting_reason_for_change', models.TextField(default='', null=True, blank=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1,
                                                  choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('data_configuration_tree', models.ForeignKey(related_name='+', to='experiment.DataConfigurationTree',
                                                              blank=True,
                                                              on_delete=django.db.models.deletion.DO_NOTHING,
                                                              null=True, db_constraint=False)),
                ('emg_setting', models.ForeignKey(related_name='+', to='experiment.EMGSetting',
                                                  blank=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                  null=True, db_constraint=False)),
                ('file_format', models.ForeignKey(related_name='+', to='experiment.FileFormat', blank=True,
                                                  on_delete=django.db.models.deletion.DO_NOTHING, null=True,
                                                  db_constraint=False)),
                ('history_user', models.ForeignKey(related_name='+', to=settings.AUTH_USER_MODEL,
                                                   on_delete=django.db.models.deletion.SET_NULL, null=True)),
                ('subject_of_group', models.ForeignKey(related_name='+', to='experiment.SubjectOfGroup',
                                                       blank=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                       null=True, db_constraint=False)),
            ],
            options={
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
                'verbose_name': 'historical emg data',
            },
        ),
        migrations.AlterField(
            model_name='emgelectrodeplacement',
            name='standardization_system',
            field=models.ForeignKey(to='experiment.StandardizationSystem', related_name='electrode_placements'),
        ),
        migrations.AlterField(
            model_name='softwareversion',
            name='software',
            field=models.ForeignKey(to='experiment.Software', related_name='versions'),
        ),
    ]
