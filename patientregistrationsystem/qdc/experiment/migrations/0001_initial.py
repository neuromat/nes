# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
import datetime
import experiment.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0001_initial'),
        ('survey', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GoalkeeperGameConfig',
            fields=[
                ('idconfig', models.IntegerField(primary_key=True, serialize=False)),
                ('institution', models.CharField(max_length=150)),
                ('groupcode', models.CharField(max_length=150)),
                ('soccerteam', models.CharField(max_length=150)),
                ('game', models.CharField(max_length=2)),
                ('phase', models.IntegerField()),
                ('playeralias', models.CharField(max_length=20)),
                ('sequexecuted', models.TextField()),
                ('gamedata', models.CharField(max_length=6)),
                ('gametime', models.CharField(max_length=6)),
                ('idresult', models.IntegerField()),
                ('playid', models.TextField(default="")),
                ('sessiontime', models.FloatField(default="")),
                ('relaxtime', models.FloatField(default="")),
                ('playermachine', models.TextField(default="")),
                ('gamerandom', models.TextField(default="")),
                ('limitplays', models.SmallIntegerField(default="")),
                ('totalcorrect', models.SmallIntegerField(default="")),
                ('successrate', models.FloatField(default="")),
                ('gamemode', models.TextField(default="")),
                ('status', models.SmallIntegerField(default="")),
                ('playstorelax', models.SmallIntegerField(default="")),
                ('scoreboard', models.BooleanField(default="")),
                ('finalscoreboard', models.SmallIntegerField(default="")),
                ('animationtype', models.SmallIntegerField(default="")),
                ('minhits', models.SmallIntegerField(default="")),
            ],
            options={
                'managed': settings.IS_TESTING,
                'db_table': '"public"."gameconfig"',
            },
        ),
        migrations.CreateModel(
            name='GoalkeeperGameLog',
            fields=[
                ('filecontent', models.TextField(primary_key=True, serialize=False)),
            ],
            options={
                'managed': False,
                'db_table': '"public"."results"',
            },
        ),
        migrations.CreateModel(
            name='GoalkeeperGameResults',
            fields=[
                ('idgameresult', models.IntegerField(primary_key=True, serialize=False, default='')),
                ('idconfig', models.IntegerField(default="")),
                ('move', models.SmallIntegerField(default="")),
                ('timeuntilanykey', models.FloatField(default="")),
                ('timeuntilshowagain', models.FloatField(default="")),
                ('waitedresult', models.SmallIntegerField(default="")),
                ('ehrandom', models.CharField(max_length=3, default="")),
                ('optionchoosen', models.SmallIntegerField(default="")),
                ('movementtime', models.FloatField(default="")),
                ('decisiontime', models.FloatField(default="")),
            ],
            options={
                'managed': settings.IS_TESTING,
                'db_table': '"public"."gameresults"',
            },
        ),
        migrations.CreateModel(
            name='AdditionalData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(null=True, blank=True, default='')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AdditionalDataFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('additional_data', models.ForeignKey(to='experiment.AdditionalData',
                                                      related_name='additional_data_files', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='AmplifierDetectionType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(null=True, max_length=150)),
                ('name_en', models.CharField(null=True, max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='BrainArea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BrainAreaSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BrainAreaSystemPerspective',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('brain_area_image', models.FileField(null=True, blank=True,
                                                      upload_to=experiment.models.get_tms_brain_area_dir)),
                ('brain_area_system', models.ForeignKey(to='experiment.BrainAreaSystem', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='CoilModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(null=True, blank=True)),
                ('coil_design', models.CharField(choices=[('air_core_coil', 'Air core coil'),
                                                          ('solid_core_coil', 'Solid core coil')],
                                                 blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CoilOrientation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='CoilShape',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(null=True, max_length=150)),
                ('name_en', models.CharField(null=True, max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='Component',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('identification', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
                ('duration_value', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)],
                                                       blank=True, null=True)),
                ('duration_unit', models.CharField(choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'),
                                                            ('min', 'minute(s)'), ('h', 'hour(s)'), ('d', 'day(s)'),
                                                            ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')],
                                                   blank=True, max_length=15, null=True)),
                ('component_type', models.CharField(choices=[('block', 'Set of steps'), ('instruction', 'Instruction'),
                                                             ('pause', 'Pause'), ('questionnaire', 'Questionnaire'),
                                                             ('stimulus', 'Stimulus'), ('task', 'Task for participant'),
                                                             ('task_experiment', 'Task for experimenter'),
                                                             ('eeg', 'EEG'), ('emg', 'EMG'), ('tms', 'TMS'),
                                                             ('digital_game_phase', 'Goalkeeper game phase'),
                                                             ('generic_data_collection', 'Generic data collection')],
                                                    max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='ComponentAdditionalFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('file', models.FileField(upload_to=experiment.models.get_step_file_dir)),
            ],
        ),
        migrations.CreateModel(
            name='ComponentConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(null=True, blank=True, max_length=50)),
                ('number_of_repetitions', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)],
                                                              blank=True, default=1, null=True)),
                ('interval_between_repetitions_value', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(1)], blank=True, null=True)
                 ),
                ('interval_between_repetitions_unit', models.CharField(
                    choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'),
                             ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')],
                    blank=True, max_length=15, null=True)
                 ),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('random_position', models.NullBooleanField()),
                ('requires_start_and_end_datetime', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ContextTree',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('setting_text', models.TextField(null=True, blank=True)),
                ('setting_file', models.FileField(null=True, blank=True,
                                                  upload_to=experiment.models.get_context_tree_dir)),
            ],
        ),
        migrations.CreateModel(
            name='DataConfigurationTree',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('code', models.IntegerField(null=True, blank=True)),
                ('component_configuration', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                                                              to='experiment.ComponentConfiguration')),
                ('parent', models.ForeignKey(related_name='children', null=True,
                                             to='experiment.DataConfigurationTree', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='DigitalGamePhaseData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(null=True, blank=True, default='')),
                ('sequence_used_in_context_tree', models.TextField(null=True, blank=True)),
                ('data_configuration_tree', models.ForeignKey(blank=True, null=True,
                                                              to='experiment.DataConfigurationTree', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DigitalGamePhaseFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('digital_game_phase_data', models.ForeignKey(to='experiment.DigitalGamePhaseData',
                                                              related_name='digital_game_phase_files', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='DirectionOfTheInducedCurrent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='EEGCapSize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('size', models.CharField(max_length=30)),
                ('electrode_adjacent_distance', models.FloatField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(null=True, blank=True, default='')),
                ('eeg_setting_reason_for_change', models.TextField(null=True, blank=True, default='')),
                ('data_configuration_tree', models.ForeignKey(blank=True, null=True,
                                                              to='experiment.DataConfigurationTree', on_delete=models.CASCADE)),
                ('eeg_cap_size', models.ForeignKey(blank=True, null=True, to='experiment.EEGCapSize', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EEGElectrodeLocalizationSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(null=True, blank=True)),
                ('map_image_file', models.FileField(null=True, blank=True,
                                                    upload_to=experiment.models.get_eeg_electrode_system_dir)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodeNetSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('eeg_electrode_localization_system', models.ForeignKey(to='experiment.EEGElectrodeLocalizationSystem',
                                                                        related_name='set_of_electrode_net_system', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodePosition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('coordinate_x', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)],
                                                     blank=True, null=True)),
                ('coordinate_y', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)],
                                                     blank=True, null=True)),
                ('channel_default_index', models.IntegerField()),
                ('eeg_electrode_localization_system', models.ForeignKey(to='experiment.EEGElectrodeLocalizationSystem',
                                                                        related_name='electrode_positions', on_delete=models.CASCADE)),
                ('position_reference', models.ForeignKey(blank=True, related_name='children', null=True,
                                                         to='experiment.EEGElectrodePosition', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodePositionCollectionStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('worked', models.BooleanField()),
                ('channel_index', models.IntegerField()),
                ('eeg_data', models.ForeignKey(to='experiment.EEGData', related_name='electrode_positions', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodePositionSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('used', models.BooleanField()),
                ('channel_index', models.IntegerField()),
                ('eeg_electrode_position', models.ForeignKey(to='experiment.EEGElectrodePosition', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='EEGFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('eeg_data', models.ForeignKey(to='experiment.EEGData', related_name='eeg_files', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='EEGSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EEGSolution',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('components', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ElectrodeConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(null=True, max_length=150)),
                ('name_en', models.CharField(null=True, max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='ElectrodeModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(null=True, blank=True)),
                ('usability', models.CharField(choices=[('disposable', 'Disposable'), ('reusable', 'Reusable')],
                                               blank=True, max_length=50, null=True)),
                ('impedance', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                                null=True)),
                ('impedance_unit', models.CharField(
                    choices=[('ohm', 'Ohm(s)'), ('kilohm', 'Kilohm(s)'), ('megaohm', 'Megaohm(s)'),
                             ('gigaohm', 'Gigaohm(s)')],
                    blank=True, max_length=15, null=True)
                 ),
                ('inter_electrode_distance', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                               blank=True, null=True)),
                ('inter_electrode_distance_unit', models.CharField(choices=[('mm', 'millimeter(s)'),
                                                                            ('cm', 'centimeter(s)')],
                                                                   blank=True, max_length=10, null=True)),
                ('electrode_type', models.CharField(choices=[('surface', 'Surface'), ('intramuscular', 'Intramuscular'),
                                                             ('needle', 'Needle')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ElectrodeShape',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(null=True, max_length=150)),
                ('name_en', models.CharField(null=True, max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='ElectrodeSurfaceMeasure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('value', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
            ],
        ),
        migrations.CreateModel(
            name='EMGData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(null=True, blank=True, default='')),
                ('emg_setting_reason_for_change', models.TextField(null=True, blank=True, default='')),
                ('data_configuration_tree', models.ForeignKey(blank=True, null=True,
                                                              to='experiment.DataConfigurationTree', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EMGElectrodePlacement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('photo', models.FileField(null=True, blank=True, upload_to=experiment.models.get_emg_placement_dir)),
                ('location', models.TextField(null=True, blank=True)),
                ('placement_type', models.CharField(choices=[('surface', 'Surface'), ('intramuscular', 'Intramuscular'),
                                                             ('needle', 'Needle')], max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='EMGElectrodeSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('emg_data', models.ForeignKey(to='experiment.EMGData', related_name='emg_files', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='EMGSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('equipment_type', models.CharField(choices=[('eeg_machine', 'EEG Machine'), ('amplifier', 'Amplifier'),
                                                             ('eeg_solution', 'EEG Solution'), ('filter', 'Filter'),
                                                             ('eeg_electrode_net', 'EEG Electrode Net'),
                                                             ('ad_converter', 'A/D Converter'),
                                                             ('tms_device', 'TMS device')],
                                                    blank=True, max_length=50, null=True)),
                ('identification', models.CharField(max_length=150)),
                ('description', models.TextField(null=True, blank=True)),
                ('serial_number', models.CharField(null=True, blank=True, max_length=50)),
            ],
            options={
                'verbose_name': 'Equipment',
                'verbose_name_plural': 'Equipment',
                'permissions': (('register_equipment', 'Can register equipment'),),
            },
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('is_public', models.BooleanField(default=False)),
                ('data_acquisition_is_concluded', models.BooleanField(default=False)),
                ('source_code_url', models.URLField(null=True, blank=True)),
                ('ethics_committee_project_url', models.URLField(
                    verbose_name='URL of the project approved by the ethics committee', blank=True, null=True)),
                ('ethics_committee_project_file', models.FileField(
                    verbose_name='Project file approved by the ethics committee', blank=True, null=True,
                    upload_to=experiment.models.get_experiment_dir)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('last_sending', models.DateTimeField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ExperimentResearcher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('experiment', models.ForeignKey(to='experiment.Experiment', on_delete=models.CASCADE)),
                ('researcher', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='FileFormat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('nes_code', models.CharField(unique=True, blank=True, max_length=50, null=True)),
                ('name', models.CharField(max_length=50)),
                ('name_pt_br', models.CharField(null=True, max_length=50)),
                ('name_en', models.CharField(null=True, max_length=50)),
                ('extension', models.CharField(max_length=20)),
                ('description', models.TextField(null=True, blank=True)),
                ('description_pt_br', models.TextField(null=True, blank=True)),
                ('description_en', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FilterType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='GenericDataCollectionData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(null=True, blank=True, default='')),
                ('data_configuration_tree', models.ForeignKey(blank=True, null=True,
                                                              to='experiment.DataConfigurationTree', on_delete=models.CASCADE)),
                ('file_format', models.ForeignKey(to='experiment.FileFormat', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GenericDataCollectionFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('generic_data_collection_data', models.ForeignKey(to='experiment.GenericDataCollectionData',
                                                                   related_name='generic_data_collection_files', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='GoalkeeperGame',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('code', models.CharField(verbose_name='Code', unique=True, max_length=2)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='GoalkeeperPhase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('phase', models.IntegerField(null=True, blank=True)),
                ('game', models.ForeignKey(to='experiment.GoalkeeperGame', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('code', models.CharField(verbose_name='Code', unique=True, max_length=150, null=True, blank=True)),
                ('classification_of_diseases', models.ManyToManyField(to='patient.ClassificationOfDiseases')),
                ('experiment', models.ForeignKey(to='experiment.Experiment', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'Group',
            },
        ),
        migrations.CreateModel(
            name='HistoricalAdditionalData',
            fields=[
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(null=True, blank=True, default='')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                                                  max_length=1)),
                ('data_configuration_tree', models.ForeignKey(blank=True, db_constraint=False, related_name='+',
                                                              null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                              to='experiment.DataConfigurationTree')),
                ('file_format', models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                                  on_delete=django.db.models.deletion.DO_NOTHING,
                                                  to='experiment.FileFormat')),
                ('history_user', models.ForeignKey(related_name='+', null=True,
                                                   on_delete=django.db.models.deletion.SET_NULL,
                                                   to=settings.AUTH_USER_MODEL)),
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
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(null=True, blank=True, default='')),
                ('sequence_used_in_context_tree', models.TextField(null=True, blank=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                                                  max_length=1)),
                ('data_configuration_tree', models.ForeignKey(blank=True, db_constraint=False, related_name='+',
                                                              null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                              to='experiment.DataConfigurationTree')),
                ('file_format', models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                                  on_delete=django.db.models.deletion.DO_NOTHING,
                                                  to='experiment.FileFormat')),
                ('history_user', models.ForeignKey(related_name='+', null=True,
                                                   on_delete=django.db.models.deletion.SET_NULL,
                                                   to=settings.AUTH_USER_MODEL)),
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
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(null=True, blank=True, default='')),
                ('eeg_setting_reason_for_change', models.TextField(null=True, blank=True, default='')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                                                  max_length=1)),
                ('data_configuration_tree', models.ForeignKey(blank=True, db_constraint=False, related_name='+',
                                                              null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                              to='experiment.DataConfigurationTree')),
                ('eeg_cap_size', models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                                   on_delete=django.db.models.deletion.DO_NOTHING,
                                                   to='experiment.EEGCapSize')),
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
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(null=True, blank=True, default='')),
                ('emg_setting_reason_for_change', models.TextField(null=True, blank=True, default='')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                                                  max_length=1)),
                ('data_configuration_tree', models.ForeignKey(blank=True, db_constraint=False, related_name='+',
                                                              null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                              to='experiment.DataConfigurationTree')),
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
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('is_public', models.BooleanField(default=False)),
                ('data_acquisition_is_concluded', models.BooleanField(default=False)),
                ('source_code_url', models.URLField(null=True, blank=True)),
                ('ethics_committee_project_url', models.URLField(
                    verbose_name='URL of the project approved by the ethics committee', blank=True, null=True)),
                ('ethics_committee_project_file', models.TextField(
                    verbose_name='Project file approved by the ethics committee', blank=True, max_length=100,
                    null=True)),
                ('last_update', models.DateTimeField(blank=True, editable=False)),
                ('last_sending', models.DateTimeField(null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                                                  max_length=1)),
                ('history_user', models.ForeignKey(related_name='+', null=True,
                                                   on_delete=django.db.models.deletion.SET_NULL,
                                                   to=settings.AUTH_USER_MODEL)),
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
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('description', models.TextField()),
                ('file_format_description', models.TextField(null=True, blank=True, default='')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                                                  max_length=1)),
                ('data_configuration_tree', models.ForeignKey(blank=True, db_constraint=False, related_name='+',
                                                              null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                              to='experiment.DataConfigurationTree')),
                ('file_format', models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                                  on_delete=django.db.models.deletion.DO_NOTHING,
                                                  to='experiment.FileFormat')),
                ('history_user', models.ForeignKey(related_name='+', null=True,
                                                   on_delete=django.db.models.deletion.SET_NULL,
                                                   to=settings.AUTH_USER_MODEL)),
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
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('token_id', models.IntegerField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                                                  max_length=1)),
                ('data_configuration_tree', models.ForeignKey(blank=True, db_constraint=False, related_name='+',
                                                              null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                              to='experiment.DataConfigurationTree')),
                ('history_user', models.ForeignKey(related_name='+', null=True,
                                                   on_delete=django.db.models.deletion.SET_NULL,
                                                   to=settings.AUTH_USER_MODEL)),
                ('questionnaire_responsible', models.ForeignKey(blank=True, db_constraint=False, related_name='+',
                                                                null=True,
                                                                on_delete=django.db.models.deletion.DO_NOTHING,
                                                                to=settings.AUTH_USER_MODEL)),
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
                ('id', models.IntegerField(verbose_name='ID', blank=True, db_index=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('resting_motor_threshold', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                              blank=True, null=True)),
                ('test_pulse_intensity_of_simulation', models.FloatField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('second_test_pulse_intensity', models.FloatField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('interval_between_pulses', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('interval_between_pulses_unit', models.CharField(
                    choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'),
                             ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')],
                    blank=True, max_length=15, null=True)),
                ('time_between_mep_trials', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('time_between_mep_trials_unit', models.CharField(
                    choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'),
                             ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')],
                    blank=True, max_length=15, null=True)),
                ('repetitive_pulse_frequency', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('coil_orientation_angle', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('description', models.TextField()),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')],
                                                  max_length=1)),
                ('coil_orientation', models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                                       on_delete=django.db.models.deletion.DO_NOTHING,
                                                       to='experiment.CoilOrientation')),
                ('data_configuration_tree', models.ForeignKey(blank=True, db_constraint=False, related_name='+',
                                                              null=True, on_delete=django.db.models.deletion.DO_NOTHING,
                                                              to='experiment.DataConfigurationTree')),
                ('direction_of_induced_current', models.ForeignKey(blank=True, db_constraint=False, related_name='+',
                                                                   null=True,
                                                                   on_delete=django.db.models.deletion.DO_NOTHING,
                                                                   to='experiment.DirectionOfTheInducedCurrent')),
                ('history_user', models.ForeignKey(related_name='+', null=True,
                                                   on_delete=django.db.models.deletion.SET_NULL,
                                                   to=settings.AUTH_USER_MODEL)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(null=True, max_length=150)),
                ('name_en', models.CharField(null=True, max_length=150)),
                ('description', models.TextField()),
                ('description_pt_br', models.TextField(null=True)),
                ('description_en', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Manufacturer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MeasureSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(null=True, max_length=150)),
                ('name_en', models.CharField(null=True, max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='MeasureUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('measure_system', models.ForeignKey(to='experiment.MeasureSystem', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Muscle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='MuscleSide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('muscle', models.ForeignKey(to='experiment.Muscle', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='MuscleSubdivision',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('anatomy_origin', models.TextField(null=True, blank=True)),
                ('anatomy_insertion', models.TextField(null=True, blank=True)),
                ('anatomy_function', models.TextField(null=True, blank=True)),
                ('muscle', models.ForeignKey(to='experiment.Muscle', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='PortalSelectedQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('question_code', models.CharField(max_length=150)),
                ('experiment', models.ForeignKey(to='experiment.Experiment', related_name='portal_selected_questions', on_delete=models.CASCADE)),
                ('survey', models.ForeignKey(to='survey.Survey', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('citation', models.TextField()),
                ('url', models.URLField(null=True, blank=True)),
                ('experiments', models.ManyToManyField(to='experiment.Experiment')),
            ],
        ),
        migrations.CreateModel(
            name='QuestionnaireResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('token_id', models.IntegerField()),
                ('data_configuration_tree', models.ForeignKey(blank=True, null=True,
                                                              to='experiment.DataConfigurationTree', on_delete=models.CASCADE)),
                ('questionnaire_responsible', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+', on_delete=models.CASCADE)),
            ],
            options={
                'permissions': (('view_questionnaireresponse', 'Can view questionnaire response'),),
            },
        ),
        migrations.CreateModel(
            name='ResearchProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(null=True, blank=True)),
                ('keywords', models.ManyToManyField(to='experiment.Keyword')),
                ('owner', models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'permissions': (('view_researchproject', 'Can view research project'),
                                ('change_researchproject_from_others', 'Can change research project created by others'),
                                ('change_researchproject_owner', 'Can change research project owner')),
            },
        ),
        migrations.CreateModel(
            name='ScheduleOfSending',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('schedule_datetime', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(
                    choices=[('scheduled', 'scheduled'), ('canceled', 'canceled'), ('sending', 'sending'),
                             ('sent', 'sent'), ('error_sending', 'error sending')],
                    max_length=50)),
                ('sending_datetime', models.DateTimeField(null=True)),
                ('reason_for_resending', models.CharField(null=True, max_length=500)),
                ('send_participant_age', models.BooleanField()),
                ('experiment', models.ForeignKey(to='experiment.Experiment', related_name='schedule_of_sending', on_delete=models.CASCADE)),
                ('responsible', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Software',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(null=True, blank=True)),
                ('manufacturer', models.ForeignKey(to='experiment.Manufacturer', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='SoftwareVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('software', models.ForeignKey(to='experiment.Software', related_name='versions', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='StandardizationSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='StimulusType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=30)),
                ('name_pt_br', models.CharField(null=True, max_length=30)),
                ('name_en', models.CharField(null=True, max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('patient', models.ForeignKey(to='patient.Patient', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='SubjectOfGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('consent_form', models.FileField(null=True, upload_to=experiment.models.get_dir)),
                ('group', models.ForeignKey(to='experiment.Group', on_delete=models.CASCADE)),
                ('subject', models.ForeignKey(to='experiment.Subject', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='SubjectStepData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('start_date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                                blank=True, default=datetime.date.today, null=True)),
                ('start_time', models.TimeField(null=True, blank=True)),
                ('end_date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                              blank=True, default=datetime.date.today, null=True)),
                ('end_time', models.TimeField(null=True, blank=True)),
                ('data_configuration_tree', models.ForeignKey(blank=True, null=True,
                                                              to='experiment.DataConfigurationTree', on_delete=models.CASCADE)),
                ('subject_of_group', models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='TetheringSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(null=True, max_length=150)),
                ('name_en', models.CharField(null=True, max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='TMSData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('date', models.DateField(validators=[experiment.models.validate_date_questionnaire_response],
                                          default=datetime.date.today)),
                ('time', models.TimeField(null=True, blank=True)),
                ('resting_motor_threshold', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                              blank=True, null=True)),
                ('test_pulse_intensity_of_simulation', models.FloatField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('second_test_pulse_intensity', models.FloatField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('interval_between_pulses', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('interval_between_pulses_unit', models.CharField(
                    choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'),
                             ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')],
                    blank=True, max_length=15, null=True)),
                ('time_between_mep_trials', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('time_between_mep_trials_unit', models.CharField(
                    choices=[('ms', 'milisecond(s)'), ('s', 'second(s)'), ('min', 'minute(s)'), ('h', 'hour(s)'),
                             ('d', 'day(s)'), ('w', 'week(s)'), ('mon', 'month(s)'), ('y', 'year(s)')],
                    blank=True, max_length=15, null=True)),
                ('repetitive_pulse_frequency', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('coil_orientation_angle', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)],
                                                               blank=True, null=True)),
                ('description', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TMSLocalizationSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(null=True, blank=True)),
                ('tms_localization_system_image',
                 models.FileField(null=True, blank=True, upload_to=experiment.models.get_tms_localization_system_dir)),
                ('brain_area', models.ForeignKey(to='experiment.BrainArea', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='TMSSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ADConverter',
            fields=[
                ('equipment_ptr', models.OneToOneField(parent_link=True, to='experiment.Equipment', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('signal_to_noise_rate', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                           blank=True, null=True)),
                ('sampling_rate', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                    blank=True, null=True)),
                ('resolution', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                 blank=True, null=True)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='Amplifier',
            fields=[
                ('equipment_ptr', models.OneToOneField(parent_link=True, to='experiment.Equipment', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('gain', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                           null=True)),
                ('number_of_channels', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)],
                                                           blank=True, null=True)),
                ('common_mode_rejection_ratio', models.FloatField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('input_impedance', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                      blank=True, null=True)),
                ('input_impedance_unit', models.CharField(
                    choices=[('ohm', 'Ohm(s)'), ('kilohm', 'Kilohm(s)'), ('megaohm', 'Megaohm(s)'),
                             ('gigaohm', 'Gigaohm(s)')],
                    blank=True, max_length=15, null=True)),
                ('amplifier_detection_type', models.ForeignKey(blank=True, null=True,
                                                               to='experiment.AmplifierDetectionType', on_delete=models.CASCADE)),
                ('tethering_system', models.ForeignKey(blank=True, null=True, to='experiment.TetheringSystem', on_delete=models.CASCADE)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('number_of_mandatory_components', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('type', models.CharField(choices=[('sequence', 'Sequence'), ('parallel_block', 'Parallel')],
                                          max_length=20)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='DigitalGamePhase',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='EEG',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='EEGAmplifierSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(related_name='eeg_amplifier_setting', primary_key=True,
                                                     serialize=False, to='experiment.EEGSetting', on_delete=models.CASCADE)),
                ('gain', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                           null=True)),
                ('sampling_rate', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                    blank=True, null=True)),
                ('number_of_channels_used', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(0)], null=True)),
                ('eeg_amplifier', models.ForeignKey(to='experiment.Amplifier', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodeLayoutSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(related_name='eeg_electrode_layout_setting', primary_key=True,
                                                     serialize=False, to='experiment.EEGSetting', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodeNet',
            fields=[
                ('equipment_ptr', models.OneToOneField(parent_link=True, to='experiment.Equipment', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='EEGFilterSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(related_name='eeg_filter_setting', primary_key=True,
                                                     serialize=False, to='experiment.EEGSetting', on_delete=models.CASCADE)),
                ('high_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                                null=True)),
                ('low_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                               null=True)),
                ('high_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                     blank=True, null=True)),
                ('low_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                    blank=True, null=True)),
                ('high_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                                 null=True)),
                ('low_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                                null=True)),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                              null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGSolutionSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(related_name='eeg_solution_setting', primary_key=True,
                                                     serialize=False, to='experiment.EEGSetting', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='EMG',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='EMGADConverterSetting',
            fields=[
                ('emg_setting', models.OneToOneField(related_name='emg_ad_converter_setting', primary_key=True,
                                                     serialize=False, to='experiment.EMGSetting', on_delete=models.CASCADE)),
                ('sampling_rate', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                    blank=True, null=True)),
                ('ad_converter', models.ForeignKey(to='experiment.ADConverter', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='EMGAmplifierSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(related_name='emg_amplifier_setting', primary_key=True,
                                                               serialize=False, to='experiment.EMGElectrodeSetting', on_delete=models.CASCADE)),
                ('gain', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                           null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGDigitalFilterSetting',
            fields=[
                ('emg_setting', models.OneToOneField(related_name='emg_digital_filter_setting', primary_key=True,
                                                     serialize=False, to='experiment.EMGSetting', on_delete=models.CASCADE)),
                ('low_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                               null=True)),
                ('high_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                                null=True)),
                ('low_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                    blank=True, null=True)),
                ('high_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                     blank=True, null=True)),
                ('low_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                blank=True, null=True)),
                ('high_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                 blank=True, null=True)),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                              null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGElectrodePlacementSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(related_name='emg_electrode_placement_setting',
                                                               primary_key=True, serialize=False,
                                                               to='experiment.EMGElectrodeSetting', on_delete=models.CASCADE)),
                ('remarks', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGIntramuscularPlacement',
            fields=[
                ('emgelectrodeplacement_ptr', models.OneToOneField(
                    parent_link=True, to='experiment.EMGElectrodePlacement', primary_key=True, serialize=False,
                    auto_created=True, on_delete=models.CASCADE)),
                ('method_of_insertion', models.TextField(null=True, blank=True)),
                ('depth_of_insertion', models.TextField(null=True, blank=True)),
            ],
            bases=('experiment.emgelectrodeplacement',),
        ),
        migrations.CreateModel(
            name='EMGNeedlePlacement',
            fields=[
                ('emgelectrodeplacement_ptr', models.OneToOneField(
                    parent_link=True, to='experiment.EMGElectrodePlacement', primary_key=True, serialize=False,
                    auto_created=True, on_delete=models.CASCADE)),
                ('depth_of_insertion', models.TextField(null=True, blank=True)),
            ],
            bases=('experiment.emgelectrodeplacement',),
        ),
        migrations.CreateModel(
            name='EMGPreamplifierSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(related_name='emg_preamplifier_setting',
                                                               primary_key=True, serialize=False,
                                                               to='experiment.EMGElectrodeSetting', on_delete=models.CASCADE)),
                ('gain', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                           null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGSurfacePlacement',
            fields=[
                ('emgelectrodeplacement_ptr', models.OneToOneField(parent_link=True,
                                                                   to='experiment.EMGElectrodePlacement',
                                                                   primary_key=True, serialize=False,
                                                                   auto_created=True, on_delete=models.CASCADE)),
                ('start_posture', models.TextField(null=True, blank=True)),
                ('orientation', models.TextField(null=True, blank=True)),
                ('fixation_on_the_skin', models.TextField(null=True, blank=True)),
                ('reference_electrode', models.TextField(null=True, blank=True)),
                ('clinical_test', models.TextField(null=True, blank=True)),
            ],
            bases=('experiment.emgelectrodeplacement',),
        ),
        migrations.CreateModel(
            name='GenericDataCollection',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('information_type', models.ForeignKey(to='experiment.InformationType', on_delete=models.CASCADE)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='HotSpot',
            fields=[
                ('name', models.CharField(max_length=50)),
                ('coordinate_x', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)],
                                                     blank=True, null=True)),
                ('coordinate_y', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)],
                                                     blank=True, null=True)),
                ('hot_spot_map', models.FileField(null=True, blank=True,
                                                  upload_to=experiment.models.get_data_file_dir)),
                ('tms_data', models.OneToOneField(primary_key=True, serialize=False, to='experiment.TMSData', on_delete=models.CASCADE)),
                ('tms_localization_system', models.ForeignKey(to='experiment.TMSLocalizationSystem',
                                                              related_name='hotspots', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Instruction',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('text', models.TextField()),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='IntramuscularElectrode',
            fields=[
                ('electrodemodel_ptr', models.OneToOneField(parent_link=True, to='experiment.ElectrodeModel',
                                                            primary_key=True, serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('strand', models.CharField(choices=[('single', 'Single'), ('multi', 'Multi')], max_length=20)),
                ('length_of_exposed_tip', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                            blank=True, null=True)),
                ('insulation_material', models.ForeignKey(blank=True, null=True, to='experiment.Material')),
            ],
            bases=('experiment.electrodemodel',),
        ),
        migrations.CreateModel(
            name='NeedleElectrode',
            fields=[
                ('electrodemodel_ptr', models.OneToOneField(parent_link=True, to='experiment.ElectrodeModel',
                                                            primary_key=True, serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('size', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                           null=True)),
                ('size_unit', models.CharField(choices=[('mm', 'millimeter(s)'), ('cm', 'centimeter(s)')], blank=True,
                                               max_length=10, null=True)),
                ('number_of_conductive_contact_points_at_the_tip', models.IntegerField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
                ('size_of_conductive_contact_points_at_the_tip', models.FloatField(
                    validators=[django.core.validators.MinValueValidator(0)], blank=True, null=True)),
            ],
            bases=('experiment.electrodemodel',),
        ),
        migrations.CreateModel(
            name='Pause',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('survey', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='survey.Survey')),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='Stimulus',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('media_file', models.FileField(null=True, blank=True,
                                                upload_to=experiment.models.get_stimulus_media_file_dir)),
                ('stimulus_type', models.ForeignKey(to='experiment.StimulusType', on_delete=models.CASCADE)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='SurfaceElectrode',
            fields=[
                ('electrodemodel_ptr', models.OneToOneField(parent_link=True, to='experiment.ElectrodeModel',
                                                            primary_key=True, serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('conduction_type', models.CharField(choices=[('gelled', 'Gelled'), ('dry', 'Dry')], max_length=20)),
                ('electrode_mode', models.CharField(choices=[('active', 'Active'), ('passive', 'Passive')],
                                                    max_length=20)),
            ],
            bases=('experiment.electrodemodel',),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='TaskForTheExperimenter',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='TMS',
            fields=[
                ('component_ptr', models.OneToOneField(parent_link=True, to='experiment.Component', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
            ],
            bases=('experiment.component',),
        ),
        migrations.CreateModel(
            name='TMSDevice',
            fields=[
                ('equipment_ptr', models.OneToOneField(parent_link=True, to='experiment.Equipment', primary_key=True,
                                                       serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('pulse_type', models.CharField(choices=[('monophase', 'Monophase'), ('biphase', 'Biphase')],
                                                blank=True, max_length=50, null=True)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='TMSDeviceSetting',
            fields=[
                ('tms_setting', models.OneToOneField(related_name='tms_device_setting', primary_key=True,
                                                     serialize=False, to='experiment.TMSSetting', on_delete=models.CASCADE)),
                ('pulse_stimulus_type', models.CharField(
                    choices=[('single_pulse', 'Single pulse'), ('paired_pulse', 'Paired pulse'),
                             ('repetitive_pulse', 'Repetitive pulse')],
                    blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='tmssetting',
            name='copied_from',
            field=models.ForeignKey(related_name='children', null=True, to='experiment.TMSSetting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='tmssetting',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='coil_orientation',
            field=models.ForeignKey(blank=True, null=True, to='experiment.CoilOrientationForeignKey', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='data_configuration_tree',
            field=models.ForeignKey(blank=True, null=True, to='experiment.DataConfigurationTree', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='direction_of_induced_current',
            field=models.ForeignKey(blank=True, null=True, to='experiment.DirectionOfTheInducedCurrent', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='tmsdata',
            name='tms_setting',
            field=models.ForeignKey(to='experiment.TMSSetting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='questionnaireresponse',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='historicaltmsdata',
            name='subject_of_group',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='historicaltmsdata',
            name='tms_setting',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.TMSSetting'),
        ),
        migrations.AddField(
            model_name='historicalquestionnaireresponse',
            name='subject_of_group',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='historicalgenericdatacollectiondata',
            name='subject_of_group',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='historicalexperiment',
            name='research_project',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.ResearchProject'),
        ),
        migrations.AddField(
            model_name='historicalemgdata',
            name='emg_setting',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.EMGSetting'),
        ),
        migrations.AddField(
            model_name='historicalemgdata',
            name='file_format',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.FileFormat'),
        ),
        migrations.AddField(
            model_name='historicalemgdata',
            name='history_user',
            field=models.ForeignKey(related_name='+', null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicalemgdata',
            name='subject_of_group',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='historicaleegdata',
            name='eeg_setting',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.EEGSetting'),
        ),
        migrations.AddField(
            model_name='historicaleegdata',
            name='file_format',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.FileFormat'),
        ),
        migrations.AddField(
            model_name='historicaleegdata',
            name='history_user',
            field=models.ForeignKey(related_name='+', null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='historicaleegdata',
            name='subject_of_group',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='historicaldigitalgamephasedata',
            name='subject_of_group',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='historicaladditionaldata',
            name='subject_of_group',
            field=models.ForeignKey(blank=True, db_constraint=False, related_name='+', null=True,
                                    on_delete=django.db.models.deletion.DO_NOTHING, to='experiment.SubjectOfGroup'),
        ),
        migrations.AddField(
            model_name='group',
            name='experimental_protocol',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='experiment.Component'),
        ),
        migrations.AddField(
            model_name='genericdatacollectiondata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=models.CASCADE),
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
            field=models.ForeignKey(to='experiment.ResearchProject', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='equipment',
            name='manufacturer',
            field=models.ForeignKey(to='experiment.Manufacturer', related_name='set_of_equipment', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='equipment',
            name='tags',
            field=models.ManyToManyField(to='experiment.Tag'),
        ),
        migrations.AddField(
            model_name='emgsetting',
            name='acquisition_software_version',
            field=models.ForeignKey(to='experiment.SoftwareVersion', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgsetting',
            name='copied_from',
            field=models.ForeignKey(related_name='children', null=True, to='experiment.EMGSetting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgsetting',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgelectrodesetting',
            name='electrode',
            field=models.ForeignKey(to='experiment.ElectrodeModel', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgelectrodesetting',
            name='emg_setting',
            field=models.ForeignKey(to='experiment.EMGSetting', related_name='emg_electrode_settings', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacement',
            name='muscle_subdivision',
            field=models.ForeignKey(to='experiment.MuscleSubdivision', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacement',
            name='placement_reference',
            field=models.ForeignKey(blank=True, related_name='children', null=True,
                                    to='experiment.EMGElectrodePlacement', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacement',
            name='standardization_system',
            field=models.ForeignKey(to='experiment.StandardizationSystem', related_name='electrode_placements', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgdata',
            name='emg_setting',
            field=models.ForeignKey(to='experiment.EMGSetting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgdata',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgdata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='electrodesurfacemeasure',
            name='measure_unit',
            field=models.ForeignKey(to='experiment.MeasureUnit', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='electrodeshape',
            name='measure_systems',
            field=models.ManyToManyField(to='experiment.MeasureSystem'),
        ),
        migrations.AddField(
            model_name='electrodemodel',
            name='electrode_configuration',
            field=models.ForeignKey(blank=True, null=True, to='experiment.ElectrodeConfiguration', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='electrodemodel',
            name='material',
            field=models.ForeignKey(blank=True, null=True, to='experiment.Material', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='electrodemodel',
            name='tags',
            field=models.ManyToManyField(to='experiment.Tag'),
        ),
        migrations.AddField(
            model_name='eegsolution',
            name='manufacturer',
            field=models.ForeignKey(to='experiment.Manufacturer', related_name='set_of_solution', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegsetting',
            name='copied_from',
            field=models.ForeignKey(related_name='children', null=True, to='experiment.EEGSetting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegsetting',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegelectrodepositionsetting',
            name='electrode_model',
            field=models.ForeignKey(to='experiment.ElectrodeModel', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegelectrodepositioncollectionstatus',
            name='eeg_electrode_position_setting',
            field=models.ForeignKey(to='experiment.EEGElectrodePositionSetting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegdata',
            name='eeg_setting',
            field=models.ForeignKey(to='experiment.EEGSetting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegdata',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegdata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='digitalgamephasedata',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='digitalgamephasedata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='contexttree',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='componentconfiguration',
            name='component',
            field=models.ForeignKey(to='experiment.Component', related_name='configuration', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='componentadditionalfile',
            name='component',
            field=models.ForeignKey(to='experiment.Component', related_name='component_additional_files', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='component',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='coilmodel',
            name='coil_shape',
            field=models.ForeignKey(to='experiment.CoilShape', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='coilmodel',
            name='material',
            field=models.ForeignKey(blank=True, null=True, to='experiment.Material', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='brainarea',
            name='brain_area_system',
            field=models.ForeignKey(to='experiment.BrainAreaSystem', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='additionaldata',
            name='data_configuration_tree',
            field=models.ForeignKey(blank=True, null=True, to='experiment.DataConfigurationTree', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='additionaldata',
            name='file_format',
            field=models.ForeignKey(to='experiment.FileFormat', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='additionaldata',
            name='subject_of_group',
            field=models.ForeignKey(to='experiment.SubjectOfGroup', on_delete=models.CASCADE),
        ),
        migrations.CreateModel(
            name='EEGElectrodeCap',
            fields=[
                ('eegelectrodenet_ptr', models.OneToOneField(parent_link=True, to='experiment.EEGElectrodeNet',
                                                             primary_key=True, serialize=False, auto_created=True, on_delete=models.CASCADE)),
                ('material', models.ForeignKey(blank=True, null=True, to='experiment.Material', on_delete=models.CASCADE)),
            ],
            bases=('experiment.eegelectrodenet',),
        ),
        migrations.CreateModel(
            name='EMGAnalogFilterSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(related_name='emg_analog_filter_setting',
                                                               primary_key=True, serialize=False,
                                                               to='experiment.EMGAmplifierSetting', on_delete=models.CASCADE)),
                ('low_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                               null=True)),
                ('high_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                                null=True)),
                ('low_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                    blank=True, null=True)),
                ('low_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                                null=True)),
                ('high_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                     blank=True, null=True)),
                ('high_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                                 null=True)),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                              null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGPreamplifierFilterSetting',
            fields=[
                ('emg_preamplifier_filter_setting', models.OneToOneField(related_name='emg_preamplifier_filter_setting',
                                                                         primary_key=True, serialize=False,
                                                                         to='experiment.EMGPreamplifierSetting', on_delete=models.CASCADE)),
                ('low_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                               null=True)),
                ('high_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                                null=True)),
                ('low_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                    blank=True, null=True)),
                ('low_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                                null=True)),
                ('high_band_pass', models.FloatField(validators=[django.core.validators.MinValueValidator(0)],
                                                     blank=True, null=True)),
                ('high_notch', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                                 null=True)),
                ('order', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], blank=True,
                                              null=True)),
            ],
        ),
        migrations.AddField(
            model_name='tmsdevicesetting',
            name='coil_model',
            field=models.ForeignKey(to='experiment.CoilModel', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='tmsdevicesetting',
            name='tms_device',
            field=models.ForeignKey(to='experiment.TMSDevice', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='tms',
            name='tms_setting',
            field=models.ForeignKey(to='experiment.TMSSetting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='surfaceelectrode',
            name='electrode_shape',
            field=models.ForeignKey(to='experiment.ElectrodeShape', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='subjectofgroup',
            unique_together=set([('subject', 'group')]),
        ),
        migrations.AlterUniqueTogether(
            name='portalselectedquestion',
            unique_together=set([('experiment', 'survey', 'question_code')]),
        ),
        migrations.AlterUniqueTogether(
            name='goalkeeperphase',
            unique_together=set([('game', 'phase')]),
        ),
        migrations.AddField(
            model_name='emgpreamplifiersetting',
            name='amplifier',
            field=models.ForeignKey(to='experiment.Amplifier', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacementsetting',
            name='emg_electrode_placement',
            field=models.ForeignKey(to='experiment.EMGElectrodePlacement', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacementsetting',
            name='muscle_side',
            field=models.ForeignKey(blank=True, null=True, to='experiment.MuscleSide', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgdigitalfiltersetting',
            name='filter_type',
            field=models.ForeignKey(to='experiment.FilterType', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emgamplifiersetting',
            name='amplifier',
            field=models.ForeignKey(to='experiment.Amplifier', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='emg',
            name='emg_setting',
            field=models.ForeignKey(to='experiment.EMGSetting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='electrodesurfacemeasure',
            name='electrode_surface',
            field=models.ForeignKey(to='experiment.SurfaceElectrode', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegsolutionsetting',
            name='eeg_solution',
            field=models.ForeignKey(to='experiment.EEGSolution', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegfiltersetting',
            name='eeg_filter_type',
            field=models.ForeignKey(to='experiment.FilterType', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegelectrodepositionsetting',
            name='eeg_electrode_layout_setting',
            field=models.ForeignKey(to='experiment.EEGElectrodeLayoutSetting', related_name='positions_setting', on_delete=models.CASCADE),
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
            field=models.ForeignKey(to='experiment.EEGElectrodeNet', related_name='set_of_electrode_net_system', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegelectrodenet',
            name='electrode_model_default',
            field=models.ForeignKey(to='experiment.ElectrodeModel', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eegelectrodelayoutsetting',
            name='eeg_electrode_net_system',
            field=models.ForeignKey(to='experiment.EEGElectrodeNetSystem', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='eeg',
            name='eeg_setting',
            field=models.ForeignKey(to='experiment.EEGSetting', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='digitalgamephase',
            name='context_tree',
            field=models.ForeignKey(to='experiment.ContextTree', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='digitalgamephase',
            name='software_version',
            field=models.ForeignKey(to='experiment.SoftwareVersion', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='componentconfiguration',
            name='parent',
            field=models.ForeignKey(related_name='children', null=True, to='experiment.Block', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='eegelectrodepositionsetting',
            unique_together=set([('eeg_electrode_layout_setting', 'channel_index')]),
        ),
        migrations.AddField(
            model_name='eegcapsize',
            name='eeg_electrode_cap',
            field=models.ForeignKey(to='experiment.EEGElectrodeCap', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='componentconfiguration',
            unique_together=set([('parent', 'order')]),
        ),
    ]
