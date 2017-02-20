# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models
import django.db.models.deletion
import datetime
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('experiment', '0080_auto_20161013_1810'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrainArea',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BrainAreaSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BrainAreaSystemPerspective',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('brain_area_image', models.FileField(blank=True, upload_to=experiment.models.get_tms_brain_area_dir,
                                                      null=True)),
                ('brain_area_system', models.ForeignKey(to='experiment.BrainAreaSystem')),
            ],
        ),
        migrations.CreateModel(
            name='CoilOrientation',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='DirectionOfTheInducedCurrent',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalTMSData',
            fields=[
                ('id', models.IntegerField(blank=True, db_index=True, verbose_name='ID', auto_created=True)),
                ('date', models.DateField(
                    validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('resting_motor_threshold', models.FloatField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('test_pulse_intensity_of_simulation', models.FloatField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('interval_between_pulses', models.IntegerField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('interval_between_pulses_unit', models.CharField(
                    blank=True, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'),
                                         ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'),
                                         ('y', 'year(s)')], max_length=15, null=True)),
                ('time_between_mep_trials_low', models.IntegerField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('time_between_mep_trials_high', models.IntegerField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('time_between_mep_trials_unit', models.CharField(
                    blank=True, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'),
                                         ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'),
                                         ('y', 'year(s)')], max_length=15, null=True)),
                ('repetitive_pulse_frequency', models.IntegerField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('description', models.TextField()),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1,
                                                  choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('coil_orientation', models.ForeignKey(blank=True,
                                                       on_delete=django.db.models.deletion.DO_NOTHING,
                                                       to='experiment.CoilOrientation',
                                                       related_name='+', null=True, db_constraint=False)),
                ('data_configuration_tree', models.ForeignKey(blank=True,
                                                              on_delete=django.db.models.deletion.DO_NOTHING,
                                                              to='experiment.DataConfigurationTree',
                                                              related_name='+',
                                                              null=True, db_constraint=False)),
                ('direction_of_induced_current', models.ForeignKey(blank=True,
                                                                   on_delete=django.db.models.deletion.DO_NOTHING,
                                                                   to='experiment.DirectionOfTheInducedCurrent',
                                                                   related_name='+', null=True, db_constraint=False)),
                ('history_user', models.ForeignKey(null=True,
                                                   on_delete=django.db.models.deletion.SET_NULL,
                                                   to=settings.AUTH_USER_MODEL, related_name='+')),
                ('subject_of_group', models.ForeignKey(blank=True,
                                                       on_delete=django.db.models.deletion.DO_NOTHING,
                                                       to='experiment.SubjectOfGroup',
                                                       related_name='+', null=True, db_constraint=False)),
                ('tms_setting', models.ForeignKey(blank=True,
                                                  on_delete=django.db.models.deletion.DO_NOTHING,
                                                  to='experiment.TMSSetting',
                                                  related_name='+', null=True, db_constraint=False)),
            ],
            options={
                'verbose_name': 'historical tms data',
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
        migrations.CreateModel(
            name='TMSData',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('resting_motor_threshold', models.FloatField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('test_pulse_intensity_of_simulation', models.FloatField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('interval_between_pulses', models.IntegerField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('interval_between_pulses_unit', models.CharField(
                    blank=True, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'),
                                         ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'),
                                         ('y', 'year(s)')], max_length=15, null=True)),
                ('time_between_mep_trials_low', models.IntegerField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('time_between_mep_trials_high', models.IntegerField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('time_between_mep_trials_unit', models.CharField(
                    blank=True, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'),
                                         ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'),
                                         ('y', 'year(s)')], max_length=15, null=True)),
                ('repetitive_pulse_frequency', models.IntegerField(
                    blank=True, validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TMSLocalizationSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('tms_localization_system_image', models.FileField(
                    blank=True, upload_to=experiment.models.get_tms_localization_system_dir, null=True)),
                ('brain_area', models.ForeignKey(to='experiment.BrainArea')),
            ],
        ),
        migrations.AlterField(
            model_name='block',
            name='type',
            field=models.CharField(max_length=20, choices=[('sequence', 'Sequence'), ('parallel_block', 'Parallel')]),
        ),
        migrations.CreateModel(
            name='HotSpot',
            fields=[
                ('name', models.CharField(max_length=50)),
                ('coordinate_x', models.IntegerField(blank=True,
                                                     validators=[django.core.validators.MinValueValidator(0)],
                                                     null=True)),
                ('coordinate_y', models.IntegerField(blank=True,
                                                     validators=[django.core.validators.MinValueValidator(0)],
                                                     null=True)),
                ('tms_data', models.OneToOneField(serialize=False, primary_key=True,
                                                  to='experiment.TMSData')),
                ('tms_localization_system', models.ForeignKey(related_name='hotspots',
                                                              to='experiment.TMSLocalizationSystem')),
            ],
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='coil_orientation',
            field=models.ForeignKey(blank=True, to='experiment.CoilOrientation', null=True),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='data_configuration_tree',
            field=models.ForeignKey(blank=True, to='experiment.DataConfigurationTree', null=True),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='direction_of_induced_current',
            field=models.ForeignKey(blank=True, to='experiment.DirectionOfTheInducedCurrent', null=True),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='tms_setting',
            field=models.ForeignKey(to='experiment.TMSSetting'),
        ),
        migrations.AddField(
            model_name='brainarea',
            name='brain_area_system',
            field=models.ForeignKey(to='experiment.BrainAreaSystem'),
        ),
    ]
