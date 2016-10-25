# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models
import django.core.validators
import datetime
import django.db.models.deletion
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BrainAreaSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BrainAreaSystemPerspective',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('brain_area_image', models.FileField(blank=True, upload_to=experiment.models.get_tms_brain_area_dir, null=True)),
                ('brain_area_system', models.ForeignKey(to='experiment.BrainAreaSystem')),
            ],
        ),
        migrations.CreateModel(
            name='CoilOrientation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='DirectionOfTheInducedCurrent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalHotSpot',
            fields=[
                ('coordinate_x', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('coordinate_y', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='+', null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical hot spot',
                'get_latest_by': 'history_date',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
        migrations.CreateModel(
            name='HistoricalTMSData',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, auto_created=True, db_index=True)),
                ('date', models.DateField(default=datetime.date.today, validators=[experiment.models.validate_date_questionnaire_response])),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file', models.TextField(max_length=100)),
                ('file_format_description', models.TextField(blank=True, default='', null=True)),
                ('resting_motor_threshold', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('test_pulse_intensity_of_simulation', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('interval_between_pulses', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('interval_between_pulses_unit', models.CharField(blank=True, null=True, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')], max_length=15)),
                ('time_between_mep_trials_low', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('time_between_mep_trials_high', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('time_between_mep_trials_unit', models.CharField(blank=True, null=True, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')], max_length=15)),
                ('repetitive_pulse_frequency', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('coil_position_angle', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('coil_orientation', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', null=True, db_constraint=False, blank=True, to='experiment.CoilOrientation')),
                ('data_configuration_tree', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', null=True, db_constraint=False, blank=True, to='experiment.DataConfigurationTree')),
                ('direction_of_induced_current', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', null=True, db_constraint=False, blank=True, to='experiment.DirectionOfTheInducedCurrent')),
                ('file_format', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', null=True, db_constraint=False, blank=True, to='experiment.FileFormat')),
                ('history_user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, related_name='+', null=True, to=settings.AUTH_USER_MODEL)),
                ('subject_of_group', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', null=True, db_constraint=False, blank=True, to='experiment.SubjectOfGroup')),
                ('tms_setting', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', null=True, db_constraint=False, blank=True, to='experiment.TMSSetting')),
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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('date', models.DateField(default=datetime.date.today, validators=[experiment.models.validate_date_questionnaire_response])),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('file_format_description', models.TextField(blank=True, default='', null=True)),
                ('resting_motor_threshold', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('test_pulse_intensity_of_simulation', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('interval_between_pulses', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('interval_between_pulses_unit', models.CharField(blank=True, null=True, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')], max_length=15)),
                ('time_between_mep_trials_low', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('time_between_mep_trials_high', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('time_between_mep_trials_unit', models.CharField(blank=True, null=True, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')], max_length=15)),
                ('repetitive_pulse_frequency', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('coil_position_angle', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TMSLocalizationSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('tms_localization_system_image', models.FileField(blank=True, upload_to=experiment.models.get_tms_localization_system_dir, null=True)),
                ('brain_area', models.ForeignKey(to='experiment.BrainArea')),
            ],
        ),
        migrations.CreateModel(
            name='TMSPosition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('tms_localization_system', models.ForeignKey(related_name='tms_positions', to='experiment.TMSLocalizationSystem')),
            ],
        ),
        migrations.CreateModel(
            name='HotSpot',
            fields=[
                ('coordinate_x', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('coordinate_y', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('tms_data', models.OneToOneField(primary_key=True, to='experiment.TMSData', serialize=False)),
                ('tms_position', models.ForeignKey(to='experiment.TMSPosition')),
            ],
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='coil_orientation',
            field=models.ForeignKey(null=True, blank=True, to='experiment.CoilOrientation'),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='data_configuration_tree',
            field=models.ForeignKey(null=True, blank=True, to='experiment.DataConfigurationTree'),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='direction_of_induced_current',
            field=models.ForeignKey(null=True, blank=True, to='experiment.DirectionOfTheInducedCurrent'),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat'),
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
            model_name='historicalhotspot',
            name='tms_data',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', null=True, db_constraint=False, blank=True, to='experiment.TMSData'),
        ),
        migrations.AddField(
            model_name='historicalhotspot',
            name='tms_position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', null=True, db_constraint=False, blank=True, to='experiment.TMSPosition'),
        ),
        migrations.AddField(
            model_name='brainarea',
            name='brain_area_system',
            field=models.ForeignKey(to='experiment.BrainAreaSystem'),
        ),
    ]
