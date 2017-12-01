# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators
from django.conf import settings
import django.db.models.deletion
import datetime
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
        ('patient', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GoalkeeperGameConfig',
            fields=[
                ('idconfig', models.IntegerField(serialize=False, primary_key=True)),
                ('experimentgroup', models.CharField(max_length=50)),
                ('phase', models.IntegerField()),
                ('playeralias', models.CharField(max_length=20)),
                ('sequexecuted', models.TextField()),
                ('gamedata', models.CharField(max_length=6)),
                ('gametime', models.CharField(max_length=6)),
                ('idresult', models.IntegerField()),
            ],
            options={
                'managed': False,
                'db_table': '"public"."gameconfig"',
            },
        ),
        migrations.CreateModel(
            name='GoalkeeperGameLog',
            fields=[
                ('filecontent', models.TextField(serialize=False, primary_key=True)),
            ],
            options={
                'managed': False,
                'db_table': '"public"."results"',
            },
        ),
        migrations.CreateModel(
            name='GoalkeeperGameResults',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('filecontent', models.TextField()),
            ],
            options={
                'managed': False,
                'db_table': '"public"."results"',
            },
        ),
        migrations.CreateModel(
            name='AdditionalData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(default='', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AdditionalDataFile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('additional_data', models.ForeignKey(to='experiment.AdditionalData', related_name='additional_data_files')),
            ],
        ),
        migrations.CreateModel(
            name='AmplifierDetectionType',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(max_length=150, null=True)),
                ('name_en', models.CharField(max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BrainArea',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BrainAreaSystem',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BrainAreaSystemPerspective',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('brain_area_image', models.FileField(upload_to=experiment.models.get_tms_brain_area_dir, blank=True, null=True)),
                ('brain_area_system', models.ForeignKey(to='experiment.BrainAreaSystem')),
            ],
        ),
        migrations.CreateModel(
            name='CoilModel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('coil_design', models.CharField(max_length=50, choices=[('air_core_coil', 'Air core coil'), ('solid_core_coil', 'Solid core coil')], blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CoilOrientation',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='CoilShape',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(max_length=150, null=True)),
                ('name_en', models.CharField(max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('identification', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('duration_value', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], blank=True, null=True)),
                ('duration_unit', models.CharField(max_length=15, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')], blank=True, null=True)),
                ('component_type', models.CharField(max_length=30, choices=[('block', 'Set of steps'), ('instruction', 'Instruction'), ('pause', 'Pause'), ('questionnaire', 'Questionnaire'), ('stimulus', 'Stimulus'), ('task', 'Task for participant'), ('task_experiment', 'Task for experimenter'), ('eeg', 'EEG'), ('emg', 'EMG'), ('tms', 'TMS'), ('digital_game_phase', 'Goalkeeper game phase'), ('generic_data_collection', 'Generic data collection')])),
            ],
        ),
        migrations.CreateModel(
            name='ComponentConfiguration',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50, blank=True, null=True)),
                ('number_of_repetitions', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], default=1, blank=True, null=True)),
                ('interval_between_repetitions_value', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], blank=True, null=True)),
                ('interval_between_repetitions_unit', models.CharField(max_length=15, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')], blank=True, null=True)),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('random_position', models.NullBooleanField()),
                ('requires_start_and_end_datetime', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ContextTree',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('setting_text', models.TextField(blank=True, null=True)),
                ('setting_file', models.FileField(upload_to=experiment.models.get_context_tree_dir, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DataConfigurationTree',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('code', models.IntegerField(blank=True, null=True)),
                ('component_configuration', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='experiment.ComponentConfiguration')),
                ('parent', models.ForeignKey(to='experiment.DataConfigurationTree', related_name='children', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='DigitalGamePhaseData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(default='', blank=True, null=True)),
                ('sequence_used_in_context_tree', models.TextField(blank=True, null=True)),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DigitalGamePhaseFile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('digital_game_phase_data', models.ForeignKey(to='experiment.DigitalGamePhaseData', related_name='digital_game_phase_files')),
            ],
        ),
        migrations.CreateModel(
            name='DirectionOfTheInducedCurrent',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='EEGCapSize',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('size', models.CharField(max_length=30)),
                ('electrode_adjacent_distance', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(default='', blank=True, null=True)),
                ('eeg_setting_reason_for_change', models.TextField(default='', blank=True, null=True)),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', blank=True, null=True)),
                ('eeg_cap_size', models.ForeignKey(to='experiment.EEGCapSize', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EEGElectrodeLocalizationSystem',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('map_image_file', models.FileField(upload_to=experiment.models.get_eeg_electrode_system_dir, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodeNetSystem',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('eeg_electrode_localization_system', models.ForeignKey(to='experiment.EEGElectrodeLocalizationSystem', related_name='set_of_electrode_net_system')),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodePosition',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('coordinate_x', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('coordinate_y', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('channel_default_index', models.IntegerField()),
                ('eeg_electrode_localization_system', models.ForeignKey(to='experiment.EEGElectrodeLocalizationSystem', related_name='electrode_positions')),
                ('position_reference', models.ForeignKey(to='experiment.EEGElectrodePosition', related_name='children', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodePositionCollectionStatus',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('worked', models.BooleanField()),
                ('channel_index', models.IntegerField()),
                ('eeg_data', models.ForeignKey(to='experiment.EEGData', related_name='electrode_positions')),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodePositionSetting',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('used', models.BooleanField()),
                ('channel_index', models.IntegerField()),
                ('eeg_electrode_position', models.ForeignKey(to='experiment.EEGElectrodePosition')),
            ],
        ),
        migrations.CreateModel(
            name='EEGFile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('eeg_data', models.ForeignKey(to='experiment.EEGData', related_name='eeg_files')),
            ],
        ),
        migrations.CreateModel(
            name='EEGSetting',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EEGSolution',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('components', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ElectrodeConfiguration',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(max_length=150, null=True)),
                ('name_en', models.CharField(max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ElectrodeModel',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('usability', models.CharField(max_length=50, choices=[('disposable', 'Disposable'), ('reusable', 'Reusable')], blank=True, null=True)),
                ('impedance', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('impedance_unit', models.CharField(max_length=15, choices=[('ohm', 'Ohm(s)'), ('kilohm', 'Kilohm(s)'), ('megaohm', 'Megaohm(s)'), ('gigaohm', 'Gigaohm(s)')], blank=True, null=True)),
                ('inter_electrode_distance', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('inter_electrode_distance_unit', models.CharField(max_length=10, choices=[('mm', 'millimeter(s)'), ('cm', 'centimeter(s)')], blank=True, null=True)),
                ('electrode_type', models.CharField(max_length=50, choices=[('surface', 'Surface'), ('intramuscular', 'Intramuscular'), ('needle', 'Needle')])),
            ],
        ),
        migrations.CreateModel(
            name='ElectrodeShape',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(max_length=150, null=True)),
                ('name_en', models.CharField(max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ElectrodeSurfaceMeasure',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('value', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='EMGData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(default='', blank=True, null=True)),
                ('emg_setting_reason_for_change', models.TextField(default='', blank=True, null=True)),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EMGElectrodePlacement',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('photo', models.FileField(upload_to=experiment.models.get_emg_placement_dir, blank=True, null=True)),
                ('location', models.TextField(blank=True, null=True)),
                ('placement_type', models.CharField(max_length=50, choices=[('surface', 'Surface'), ('intramuscular', 'Intramuscular'), ('needle', 'Needle')])),
            ],
        ),
        migrations.CreateModel(
            name='EMGElectrodeSetting',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGFile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('emg_data', models.ForeignKey(to='experiment.EMGData', related_name='emg_files')),
            ],
        ),
        migrations.CreateModel(
            name='EMGSetting',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('equipment_type', models.CharField(max_length=50, choices=[('eeg_machine', 'EEG Machine'), ('amplifier', 'Amplifier'), ('eeg_solution', 'EEG Solution'), ('filter', 'Filter'), ('eeg_electrode_net', 'EEG Electrode Net'), ('ad_converter', 'A/D Converter'), ('tms_device', 'TMS device')], blank=True, null=True)),
                ('identification', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('serial_number', models.CharField(max_length=50, blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Equipment',
                'verbose_name': 'Equipment',
                'permissions': (('register_equipment', 'Can register equipment'),),
            },
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('is_public', models.BooleanField(default=False)),
                ('data_acquisition_is_concluded', models.BooleanField(default=False)),
                ('source_code_url', models.URLField(blank=True, null=True)),
                ('ethics_committee_project_url', models.URLField(verbose_name='URL of the project approved by the ethics committee', blank=True, null=True)),
                ('ethics_committee_project_file', models.FileField(verbose_name='Project file approved by the ethics committee', upload_to=experiment.models.get_experiment_dir, blank=True, null=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('last_sending', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FileFormat',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('nes_code', models.CharField(unique=True, max_length=50, blank=True, null=True)),
                ('name', models.CharField(max_length=50)),
                ('name_pt_br', models.CharField(max_length=50, null=True)),
                ('name_en', models.CharField(max_length=50, null=True)),
                ('extension', models.CharField(max_length=20)),
                ('description', models.TextField(blank=True, null=True)),
                ('description_pt_br', models.TextField(blank=True, null=True)),
                ('description_en', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='FilterType',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GenericDataCollectionData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(default='', blank=True, null=True)),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', blank=True, null=True)),
                ('file_format', models.ForeignKey(to='experiment.FileFormat')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GenericDataCollectionFile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('generic_data_collection_data', models.ForeignKey(to='experiment.GenericDataCollectionData', related_name='generic_data_collection_files')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('code', models.CharField(verbose_name='Code', unique=True, max_length=150, blank=True, null=True)),
                ('classification_of_diseases', models.ManyToManyField(to='patient.ClassificationOfDiseases')),
                ('experiment', models.ForeignKey(to='experiment.Experiment')),
            ],
            options={
                'verbose_name': 'Group',
            },
        ),
        migrations.CreateModel(
            name='HistoricalAdditionalData',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', blank=True, db_index=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(default='', blank=True, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
                ('file_format', models.ForeignKey(to='experiment.FileFormat', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, related_name='+', null=True)),
            ],
            options={
                'verbose_name': 'historical additional data',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalDigitalGamePhaseData',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', blank=True, db_index=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(default='', blank=True, null=True)),
                ('sequence_used_in_context_tree', models.TextField(blank=True, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
                ('file_format', models.ForeignKey(to='experiment.FileFormat', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, related_name='+', null=True)),
            ],
            options={
                'verbose_name': 'historical digital game phase data',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalEEGData',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', blank=True, db_index=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(default='', blank=True, null=True)),
                ('eeg_setting_reason_for_change', models.TextField(default='', blank=True, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
                ('eeg_cap_size', models.ForeignKey(to='experiment.EEGCapSize', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'historical eeg data',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalEMGData',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', blank=True, db_index=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(default='', blank=True, null=True)),
                ('emg_setting_reason_for_change', models.TextField(default='', blank=True, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'historical emg data',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalExperiment',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', blank=True, db_index=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('is_public', models.BooleanField(default=False)),
                ('data_acquisition_is_concluded', models.BooleanField(default=False)),
                ('source_code_url', models.URLField(blank=True, null=True)),
                ('ethics_committee_project_url', models.URLField(verbose_name='URL of the project approved by the ethics committee', blank=True, null=True)),
                ('ethics_committee_project_file', models.TextField(verbose_name='Project file approved by the ethics committee', max_length=100, blank=True, null=True)),
                ('last_update', models.DateTimeField(editable=False, blank=True)),
                ('last_sending', models.DateTimeField(null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, related_name='+', null=True)),
            ],
            options={
                'verbose_name': 'historical experiment',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalGenericDataCollectionData',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', blank=True, db_index=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(default='', blank=True, null=True)),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
                ('file_format', models.ForeignKey(to='experiment.FileFormat', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, related_name='+', null=True)),
            ],
            options={
                'verbose_name': 'historical generic data collection data',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalQuestionnaireResponse',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', blank=True, db_index=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('token_id', models.IntegerField()),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, related_name='+', null=True)),
                ('questionnaire_responsible', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'historical questionnaire response',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='HistoricalTMSData',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', blank=True, db_index=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('resting_motor_threshold', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('test_pulse_intensity_of_simulation', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('second_test_pulse_intensity', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('interval_between_pulses', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('interval_between_pulses_unit', models.CharField(max_length=15, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')], blank=True, null=True)),
                ('time_between_mep_trials', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('time_between_mep_trials_unit', models.CharField(max_length=15, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')], blank=True, null=True)),
                ('repetitive_pulse_frequency', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('coil_orientation_angle', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('description', models.TextField()),
                ('history_id', models.AutoField(serialize=False, primary_key=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('coil_orientation', models.ForeignKey(to='experiment.CoilOrientation', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
                ('direction_of_induced_current', models.ForeignKey(to='experiment.DirectionOfTheInducedCurrent', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True)),
                ('history_user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, related_name='+', null=True)),
            ],
            options={
                'verbose_name': 'historical tms data',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
        ),
        migrations.CreateModel(
            name='InformationType',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(max_length=150, null=True)),
                ('name_en', models.CharField(max_length=150, null=True)),
                ('description', models.TextField()),
                ('description_pt_br', models.TextField(null=True)),
                ('description_en', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MeasureSystem',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(max_length=150, null=True)),
                ('name_en', models.CharField(max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MeasureUnit',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('measure_system', models.ForeignKey(to='experiment.MeasureSystem')),
            ],
        ),
        migrations.CreateModel(
            name='Muscle',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='MuscleSide',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('muscle', models.ForeignKey(to='experiment.Muscle')),
            ],
        ),
        migrations.CreateModel(
            name='MuscleSubdivision',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('anatomy_origin', models.TextField(blank=True, null=True)),
                ('anatomy_insertion', models.TextField(blank=True, null=True)),
                ('anatomy_function', models.TextField(blank=True, null=True)),
                ('muscle', models.ForeignKey(to='experiment.Muscle')),
            ],
        ),
        migrations.CreateModel(
            name='PortalSelectedQuestion',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('question_code', models.CharField(max_length=150)),
                ('experiment', models.ForeignKey(to='experiment.Experiment', related_name='portal_selected_questions')),
                ('survey', models.ForeignKey(to='survey.Survey')),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('citation', models.TextField()),
                ('url', models.URLField(blank=True, null=True)),
                ('experiments', models.ManyToManyField(to='experiment.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionnaireResponse',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('token_id', models.IntegerField()),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', blank=True, null=True)),
                ('questionnaire_responsible', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
            options={
                'permissions': (('view_questionnaireresponse', 'Can view questionnaire response'),),
            },
        ),
        migrations.CreateModel(
            name='ResearchProject',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('keywords', models.ManyToManyField(to='experiment.Keyword')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
            options={
                'permissions': (('view_researchproject', 'Can view research project'), ('change_researchproject_from_others', 'Can change research project created by others'), ('change_researchproject_owner', 'Can change research project owner')),
            },
        ),
        migrations.CreateModel(
            name='ResearchProjectCollaboration',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('is_coordinator', models.BooleanField()),
                ('research_project', models.ForeignKey(to='experiment.ResearchProject', related_name='collaborators')),
                ('team_person', models.ForeignKey(to='team.TeamPerson', related_name='collaborators')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduleOfSending',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('schedule_datetime', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=50, choices=[('scheduled', 'scheduled'), ('canceled', 'canceled'), ('sending', 'sending'), ('sent', 'sent'), ('error_sending', 'error sending')])),
                ('sending_datetime', models.DateTimeField(null=True)),
                ('reason_for_resending', models.CharField(max_length=500, null=True)),
                ('experiment', models.ForeignKey(to='experiment.Experiment', related_name='schedule_of_sending')),
                ('responsible', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Software',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('manufacturer', models.ForeignKey(to='experiment.Manufacturer')),
            ],
        ),
        migrations.CreateModel(
            name='SoftwareVersion',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('software', models.ForeignKey(to='experiment.Software', related_name='versions')),
            ],
        ),
        migrations.CreateModel(
            name='StandardizationSystem',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StimulusType',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('name_pt_br', models.CharField(max_length=30, null=True)),
                ('name_en', models.CharField(max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('patient', models.ForeignKey(to='patient.Patient')),
            ],
        ),
        migrations.CreateModel(
            name='SubjectOfGroup',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('consent_form', models.FileField(upload_to=experiment.models.get_dir, null=True)),
                ('group', models.ForeignKey(to='experiment.Group')),
                ('subject', models.ForeignKey(to='experiment.Subject')),
            ],
        ),
        migrations.CreateModel(
            name='SubjectStepData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('start_date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today, blank=True, null=True)),
                ('start_time', models.TimeField(blank=True, null=True)),
                ('end_date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today, blank=True, null=True)),
                ('end_time', models.TimeField(blank=True, null=True)),
                ('data_configuration_tree', models.ForeignKey(to='experiment.DataConfigurationTree', blank=True, null=True)),
                ('subject_of_group', models.ForeignKey(to='experiment.SubjectOfGroup')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TetheringSystem',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(max_length=150, null=True)),
                ('name_en', models.CharField(max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TMSData',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response], default=datetime.date.today)),
                ('time', models.TimeField(blank=True, null=True)),
                ('resting_motor_threshold', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('test_pulse_intensity_of_simulation', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('second_test_pulse_intensity', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('interval_between_pulses', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('interval_between_pulses_unit', models.CharField(max_length=15, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')], blank=True, null=True)),
                ('time_between_mep_trials', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('time_between_mep_trials_unit', models.CharField(max_length=15, choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'), ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')], blank=True, null=True)),
                ('repetitive_pulse_frequency', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('coil_orientation_angle', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TMSLocalizationSystem',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('tms_localization_system_image', models.FileField(upload_to=experiment.models.get_tms_localization_system_dir, blank=True, null=True)),
                ('brain_area', models.ForeignKey(to='experiment.BrainArea')),
            ],
        ),
        migrations.CreateModel(
            name='TMSSetting',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ADConverter',
            fields=[
                ('equipment_ptr', models.OneToOneField(auto_created=True, to='experiment.Equipment', primary_key=True, parent_link=True, serialize=False)),
                ('signal_to_noise_rate', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('sampling_rate', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('resolution', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='Amplifier',
            fields=[
                ('equipment_ptr', models.OneToOneField(auto_created=True, to='experiment.Equipment', primary_key=True, parent_link=True, serialize=False)),
                ('gain', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('number_of_channels', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('common_mode_rejection_ratio', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('input_impedance', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('input_impedance_unit', models.CharField(max_length=15, choices=[('ohm', 'Ohm(s)'), ('kilohm', 'Kilohm(s)'), ('megaohm', 'Megaohm(s)'), ('gigaohm', 'Gigaohm(s)')], blank=True, null=True)),
                ('amplifier_detection_type', models.ForeignKey(to='experiment.AmplifierDetectionType', blank=True, null=True)),
                ('tethering_system', models.ForeignKey(to='experiment.TetheringSystem', blank=True, null=True)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
                ('number_of_mandatory_components', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('type', models.CharField(max_length=20, choices=[('sequence', 'Sequence'), ('parallel_block', 'Parallel')])),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='DigitalGamePhase',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='EEG',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='EEGAmplifierSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(to='experiment.EEGSetting', primary_key=True, related_name='eeg_amplifier_setting', serialize=False)),
                ('gain', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('sampling_rate', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('number_of_channels_used', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('eeg_amplifier', models.ForeignKey(to='experiment.Amplifier')),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodeLayoutSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(to='experiment.EEGSetting', primary_key=True, related_name='eeg_electrode_layout_setting', serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodeNet',
            fields=[
                ('equipment_ptr', models.OneToOneField(auto_created=True, to='experiment.Equipment', primary_key=True, parent_link=True, serialize=False)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='EEGFilterSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(to='experiment.EEGSetting', primary_key=True, related_name='eeg_filter_setting', serialize=False)),
                ('high_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('low_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('high_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('low_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('high_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('low_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGSolutionSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(to='experiment.EEGSetting', primary_key=True, related_name='eeg_solution_setting', serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='EMG',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='EMGADConverterSetting',
            fields=[
                ('emg_setting', models.OneToOneField(to='experiment.EMGSetting', primary_key=True, related_name='emg_ad_converter_setting', serialize=False)),
                ('sampling_rate', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('ad_converter', models.ForeignKey(to='experiment.ADConverter')),
            ],
        ),
        migrations.CreateModel(
            name='EMGAmplifierSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(to='experiment.EMGElectrodeSetting', primary_key=True, related_name='emg_amplifier_setting', serialize=False)),
                ('gain', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGDigitalFilterSetting',
            fields=[
                ('emg_setting', models.OneToOneField(to='experiment.EMGSetting', primary_key=True, related_name='emg_digital_filter_setting', serialize=False)),
                ('low_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('high_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('low_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('high_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('low_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('high_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGElectrodePlacementSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(to='experiment.EMGElectrodeSetting', primary_key=True, related_name='emg_electrode_placement_setting', serialize=False)),
                ('remarks', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGIntramuscularPlacement',
            fields=[
                ('emgelectrodeplacement_ptr', models.OneToOneField(auto_created=True, to='experiment.EMGElectrodePlacement', primary_key=True, parent_link=True, serialize=False)),
                ('method_of_insertion', models.TextField(blank=True, null=True)),
                ('depth_of_insertion', models.TextField(blank=True, null=True)),
            ],
            bases=('experiment.emgelectrodeplacement',),
        ),
        migrations.CreateModel(
            name='EMGNeedlePlacement',
            fields=[
                ('emgelectrodeplacement_ptr', models.OneToOneField(auto_created=True, to='experiment.EMGElectrodePlacement', primary_key=True, parent_link=True, serialize=False)),
                ('depth_of_insertion', models.TextField(blank=True, null=True)),
            ],
            bases=('experiment.emgelectrodeplacement',),
        ),
        migrations.CreateModel(
            name='EMGPreamplifierSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(to='experiment.EMGElectrodeSetting', primary_key=True, related_name='emg_preamplifier_setting', serialize=False)),
                ('gain', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGSurfacePlacement',
            fields=[
                ('emgelectrodeplacement_ptr', models.OneToOneField(auto_created=True, to='experiment.EMGElectrodePlacement', primary_key=True, parent_link=True, serialize=False)),
                ('start_posture', models.TextField(blank=True, null=True)),
                ('orientation', models.TextField(blank=True, null=True)),
                ('fixation_on_the_skin', models.TextField(blank=True, null=True)),
                ('reference_electrode', models.TextField(blank=True, null=True)),
                ('clinical_test', models.TextField(blank=True, null=True)),
            ],
            bases=('experiment.emgelectrodeplacement',),
        ),
        migrations.CreateModel(
            name='GenericDataCollection',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
                ('information_type', models.ForeignKey(to='experiment.InformationType')),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='HotSpot',
            fields=[
                ('name', models.CharField(max_length=50)),
                ('coordinate_x', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('coordinate_y', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('hot_spot_map', models.FileField(upload_to=experiment.models.get_data_file_dir, blank=True, null=True)),
                ('tms_data', models.OneToOneField(to='experiment.TMSData', primary_key=True, serialize=False)),
                ('tms_localization_system', models.ForeignKey(to='experiment.TMSLocalizationSystem', related_name='hotspots')),
            ],
        ),
        migrations.CreateModel(
            name='Instruction',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
                ('text', models.TextField()),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='IntramuscularElectrode',
            fields=[
                ('electrodemodel_ptr', models.OneToOneField(auto_created=True, to='experiment.ElectrodeModel', primary_key=True, parent_link=True, serialize=False)),
                ('strand', models.CharField(max_length=20, choices=[('single', 'Single'), ('multi', 'Multi')])),
                ('length_of_exposed_tip', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('insulation_material', models.ForeignKey(to='experiment.Material', blank=True, null=True)),
            ],
            bases=('experiment.electrodemodel',),
        ),
        migrations.CreateModel(
            name='NeedleElectrode',
            fields=[
                ('electrodemodel_ptr', models.OneToOneField(auto_created=True, to='experiment.ElectrodeModel', primary_key=True, parent_link=True, serialize=False)),
                ('size', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('size_unit', models.CharField(max_length=10, choices=[('mm', 'millimeter(s)'), ('cm', 'centimeter(s)')], blank=True, null=True)),
                ('number_of_conductive_contact_points_at_the_tip', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('size_of_conductive_contact_points_at_the_tip', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
            ],
            bases=('experiment.electrodemodel',),
        ),
        migrations.CreateModel(
            name='Pause',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Survey')),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Stimulus',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
                ('media_file', models.FileField(upload_to=experiment.models.get_stimulus_media_file_dir, blank=True, null=True)),
                ('stimulus_type', models.ForeignKey(to='experiment.StimulusType')),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='SurfaceElectrode',
            fields=[
                ('electrodemodel_ptr', models.OneToOneField(auto_created=True, to='experiment.ElectrodeModel', primary_key=True, parent_link=True, serialize=False)),
                ('conduction_type', models.CharField(max_length=20, choices=[('gelled', 'Gelled'), ('dry', 'Dry')])),
                ('electrode_mode', models.CharField(max_length=20, choices=[('active', 'Active'), ('passive', 'Passive')])),
            ],
            bases=('experiment.electrodemodel',),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='TaskForTheExperimenter',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='TMS',
            fields=[
                ('component_ptr', models.OneToOneField(auto_created=True, to='experiment.Component', primary_key=True, parent_link=True, serialize=False)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='TMSDevice',
            fields=[
                ('equipment_ptr', models.OneToOneField(auto_created=True, to='experiment.Equipment', primary_key=True, parent_link=True, serialize=False)),
                ('pulse_type', models.CharField(max_length=50, choices=[('monophase', 'Monophase'), ('biphase', 'Biphase')], blank=True, null=True)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='TMSDeviceSetting',
            fields=[
                ('tms_setting', models.OneToOneField(to='experiment.TMSSetting', primary_key=True, related_name='tms_device_setting', serialize=False)),
                ('pulse_stimulus_type', models.CharField(max_length=50, choices=[('single_pulse', 'Single pulse'), ('paired_pulse', 'Paired pulse'), ('repetitive_pulse', 'Repetitive pulse')], blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='tmssetting',
            name='copied_from',
            field=models.ForeignKey(to='experiment.TMSSetting', related_name='children', null=True),
        ),
        migrations.AddField(
            model_name='tmssetting',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment'),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='coil_orientation',
            field=models.ForeignKey(to='experiment.CoilOrientation', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='data_configuration_tree',
            field=models.ForeignKey(to='experiment.DataConfigurationTree', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='direction_of_induced_current',
            field=models.ForeignKey(to='experiment.DirectionOfTheInducedCurrent', blank=True, null=True),
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
            model_name='questionnaireresponse',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='historicaltmsdata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaltmsdata',
            name='tms_setting',
            field=models.ForeignKey(to='experiment.TMSSetting', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalquestionnaireresponse',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalgenericdatacollectiondata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalexperiment',
            name='research_project',
            field=models.ForeignKey(to='experiment.ResearchProject', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalemgdata',
            name='emg_setting',
            field=models.ForeignKey(to='experiment.EMGSetting', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalemgdata',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicalemgdata',
            name='history_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='historicalemgdata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaleegdata',
            name='eeg_setting',
            field=models.ForeignKey(to='experiment.EEGSetting', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaleegdata',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaleegdata',
            name='history_user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.SET_NULL, related_name='+', null=True),
        ),
        migrations.AddField(
            model_name='historicaleegdata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaldigitalgamephasedata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='historicaladditionaldata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', db_constraint=False, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='experimental_protocol',
            field=models.ForeignKey(to='experiment.Component', on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AddField(
            model_name='genericdatacollectiondata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='filtertype',
            name='tags',
            field=models.ManyToManyField(to='experiment.Tag'),
        ),
        migrations.AddField(
            model_name='fileformat',
            name='tags',
            field=models.ManyToManyField(to='experiment.Tag'),
        ),
        migrations.AddField(
            model_name='experiment',
            name='research_project',
            field=models.ForeignKey(to='experiment.ResearchProject'),
        ),
        migrations.AddField(
            model_name='equipment',
            name='manufacturer',
            field=models.ForeignKey(to='experiment.Manufacturer', related_name='set_of_equipment'),
        ),
        migrations.AddField(
            model_name='equipment',
            name='tags',
            field=models.ManyToManyField(to='experiment.Tag'),
        ),
        migrations.AddField(
            model_name='emgsetting',
            name='acquisition_software_version',
            field=models.ForeignKey(to='experiment.SoftwareVersion'),
        ),
        migrations.AddField(
            model_name='emgsetting',
            name='copied_from',
            field=models.ForeignKey(to='experiment.EMGSetting', related_name='children', null=True),
        ),
        migrations.AddField(
            model_name='emgsetting',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment'),
        ),
        migrations.AddField(
            model_name='emgelectrodesetting',
            name='electrode',
            field=models.ForeignKey(to='experiment.ElectrodeModel'),
        ),
        migrations.AddField(
            model_name='emgelectrodesetting',
            name='emg_setting',
            field=models.ForeignKey(to='experiment.EMGSetting', related_name='emg_electrode_settings'),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacement',
            name='muscle_subdivision',
            field=models.ForeignKey(to='experiment.MuscleSubdivision'),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacement',
            name='placement_reference',
            field=models.ForeignKey(to='experiment.EMGElectrodePlacement', related_name='children', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacement',
            name='standardization_system',
            field=models.ForeignKey(to='experiment.StandardizationSystem', related_name='electrode_placements'),
        ),
        migrations.AddField(
            model_name='emgdata',
            name='emg_setting',
            field=models.ForeignKey(to='experiment.EMGSetting'),
        ),
        migrations.AddField(
            model_name='emgdata',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat'),
        ),
        migrations.AddField(
            model_name='emgdata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='electrodesurfacemeasure',
            name='measure_unit',
            field=models.ForeignKey(to='experiment.MeasureUnit'),
        ),
        migrations.AddField(
            model_name='electrodeshape',
            name='measure_systems',
            field=models.ManyToManyField(to='experiment.MeasureSystem'),
        ),
        migrations.AddField(
            model_name='electrodemodel',
            name='electrode_configuration',
            field=models.ForeignKey(to='experiment.ElectrodeConfiguration', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='electrodemodel',
            name='material',
            field=models.ForeignKey(to='experiment.Material', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='electrodemodel',
            name='tags',
            field=models.ManyToManyField(to='experiment.Tag'),
        ),
        migrations.AddField(
            model_name='eegsolution',
            name='manufacturer',
            field=models.ForeignKey(to='experiment.Manufacturer', related_name='set_of_solution'),
        ),
        migrations.AddField(
            model_name='eegsetting',
            name='copied_from',
            field=models.ForeignKey(to='experiment.EEGSetting', related_name='children', null=True),
        ),
        migrations.AddField(
            model_name='eegsetting',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment'),
        ),
        migrations.AddField(
            model_name='eegelectrodepositionsetting',
            name='electrode_model',
            field=models.ForeignKey(to='experiment.ElectrodeModel'),
        ),
        migrations.AddField(
            model_name='eegelectrodepositioncollectionstatus',
            name='eeg_electrode_position_setting',
            field=models.ForeignKey(to='experiment.EEGElectrodePositionSetting'),
        ),
        migrations.AddField(
            model_name='eegdata',
            name='eeg_setting',
            field=models.ForeignKey(to='experiment.EEGSetting'),
        ),
        migrations.AddField(
            model_name='eegdata',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat'),
        ),
        migrations.AddField(
            model_name='eegdata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='digitalgamephasedata',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat'),
        ),
        migrations.AddField(
            model_name='digitalgamephasedata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='contexttree',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment'),
        ),
        migrations.AddField(
            model_name='componentconfiguration',
            name='component',
            field=models.ForeignKey(to='experiment.Component', related_name='configuration'),
        ),
        migrations.AddField(
            model_name='component',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment'),
        ),
        migrations.AddField(
            model_name='coilmodel',
            name='coil_shape',
            field=models.ForeignKey(to='experiment.CoilShape'),
        ),
        migrations.AddField(
            model_name='coilmodel',
            name='material',
            field=models.ForeignKey(to='experiment.Material', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='brainarea',
            name='brain_area_system',
            field=models.ForeignKey(to='experiment.BrainAreaSystem'),
        ),
        migrations.AddField(
            model_name='additionaldata',
            name='data_configuration_tree',
            field=models.ForeignKey(to='experiment.DataConfigurationTree', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='additionaldata',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat'),
        ),
        migrations.AddField(
            model_name='additionaldata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup'),
        ),
        migrations.CreateModel(
            name='EEGElectrodeCap',
            fields=[
                ('eegelectrodenet_ptr', models.OneToOneField(auto_created=True, to='experiment.EEGElectrodeNet', primary_key=True, parent_link=True, serialize=False)),
                ('material', models.ForeignKey(to='experiment.Material', blank=True, null=True)),
            ],
            bases=('experiment.eegelectrodenet',),
        ),
        migrations.CreateModel(
            name='EMGAnalogFilterSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(to='experiment.EMGAmplifierSetting', primary_key=True, related_name='emg_analog_filter_setting', serialize=False)),
                ('low_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('high_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('low_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('low_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('high_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('high_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGPreamplifierFilterSetting',
            fields=[
                ('emg_preamplifier_filter_setting', models.OneToOneField(to='experiment.EMGPreamplifierSetting', primary_key=True, related_name='emg_preamplifier_filter_setting', serialize=False)),
                ('low_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('high_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('low_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('low_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('high_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('high_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='tmsdevicesetting',
            name='coil_model',
            field=models.ForeignKey(to='experiment.CoilModel'),
        ),
        migrations.AddField(
            model_name='tmsdevicesetting',
            name='tms_device',
            field=models.ForeignKey(to='experiment.TMSDevice'),
        ),
        migrations.AddField(
            model_name='tms',
            name='tms_setting',
            field=models.ForeignKey(to='experiment.TMSSetting'),
        ),
        migrations.AddField(
            model_name='surfaceelectrode',
            name='electrode_shape',
            field=models.ForeignKey(to='experiment.ElectrodeShape'),
        ),
        migrations.AlterUniqueTogether(
            name='subjectofgroup',
            unique_together=set([('subject', 'group')]),
        ),
        migrations.AlterUniqueTogether(
            name='portalselectedquestion',
            unique_together=set([('experiment', 'survey', 'question_code')]),
        ),
        migrations.AddField(
            model_name='emgpreamplifiersetting',
            name='amplifier',
            field=models.ForeignKey(to='experiment.Amplifier'),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacementsetting',
            name='emg_electrode_placement',
            field=models.ForeignKey(to='experiment.EMGElectrodePlacement'),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacementsetting',
            name='muscle_side',
            field=models.ForeignKey(to='experiment.MuscleSide', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='emgdigitalfiltersetting',
            name='filter_type',
            field=models.ForeignKey(to='experiment.FilterType'),
        ),
        migrations.AddField(
            model_name='emgamplifiersetting',
            name='amplifier',
            field=models.ForeignKey(to='experiment.Amplifier'),
        ),
        migrations.AddField(
            model_name='emg',
            name='emg_setting',
            field=models.ForeignKey(to='experiment.EMGSetting'),
        ),
        migrations.AddField(
            model_name='electrodesurfacemeasure',
            name='electrode_surface',
            field=models.ForeignKey(to='experiment.SurfaceElectrode'),
        ),
        migrations.AddField(
            model_name='eegsolutionsetting',
            name='eeg_solution',
            field=models.ForeignKey(to='experiment.EEGSolution'),
        ),
        migrations.AddField(
            model_name='eegfiltersetting',
            name='eeg_filter_type',
            field=models.ForeignKey(to='experiment.FilterType'),
        ),
        migrations.AddField(
            model_name='eegelectrodepositionsetting',
            name='eeg_electrode_layout_setting',
            field=models.ForeignKey(to='experiment.EEGElectrodeLayoutSetting', related_name='positions_setting'),
        ),
        migrations.AlterUniqueTogether(
            name='eegelectrodepositioncollectionstatus',
            unique_together=set([('eeg_data', 'channel_index')]),
        ),
        migrations.AlterUniqueTogether(
            name='eegelectrodeposition',
            unique_together=set([('eeg_electrode_localization_system', 'channel_default_index')]),
        ),
        migrations.AddField(
            model_name='eegelectrodenetsystem',
            name='eeg_electrode_net',
            field=models.ForeignKey(to='experiment.EEGElectrodeNet', related_name='set_of_electrode_net_system'),
        ),
        migrations.AddField(
            model_name='eegelectrodenet',
            name='electrode_model_default',
            field=models.ForeignKey(to='experiment.ElectrodeModel'),
        ),
        migrations.AddField(
            model_name='eegelectrodelayoutsetting',
            name='eeg_electrode_net_system',
            field=models.ForeignKey(to='experiment.EEGElectrodeNetSystem'),
        ),
        migrations.AddField(
            model_name='eeg',
            name='eeg_setting',
            field=models.ForeignKey(to='experiment.EEGSetting'),
        ),
        migrations.AddField(
            model_name='digitalgamephase',
            name='context_tree',
            field=models.ForeignKey(to='experiment.ContextTree'),
        ),
        migrations.AddField(
            model_name='digitalgamephase',
            name='software_version',
            field=models.ForeignKey(to='experiment.SoftwareVersion'),
        ),
        migrations.AddField(
            model_name='componentconfiguration',
            name='parent',
            field=models.ForeignKey(to='experiment.Block', related_name='children', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='eegelectrodepositionsetting',
            unique_together=set([('eeg_electrode_layout_setting', 'channel_index')]),
        ),
        migrations.AddField(
            model_name='eegcapsize',
            name='eeg_electrode_cap',
            field=models.ForeignKey(to='experiment.EEGElectrodeCap'),
        ),
        migrations.AlterUniqueTogether(
            name='componentconfiguration',
            unique_together=set([('parent', 'order')]),
        ),
    ]
