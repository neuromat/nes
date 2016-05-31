# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0019_data_configuration_tree_cannot_be_null'),
    ]

    operations = [
        migrations.CreateModel(
            name='EEGAmplifier',
            fields=[
                ('equipment_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='experiment.Equipment', serialize=False)),
                ('gain', models.FloatField(blank=True, null=True)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='EEGAmplifierSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(primary_key=True, to='experiment.EEGSetting', serialize=False)),
                ('gain', models.FloatField(blank=True, null=True)),
                ('eeg_amplifier', models.ForeignKey(to='experiment.EEGAmplifier')),
            ],
        ),
        migrations.CreateModel(
            name='EEGCapSize',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=30)),
                ('electrode_adjacent_distance', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodeLayoutSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(primary_key=True, to='experiment.EEGSetting', serialize=False)),
                ('number_of_electrodes', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodeLocalizationSystem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('number_of_electrodes', models.IntegerField(blank=True, null=True)),
                ('map_image_file', models.FileField(blank=True, upload_to=experiment.models.get_eeg_electrode_system_dir, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodeModel',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('usability', models.CharField(choices=[('disposable', 'Disposable'), ('reusable', 'Reusable')], blank=True, null=True, max_length=50)),
                ('impedance', models.FloatField(blank=True, null=True)),
                ('impedance_unit', models.CharField(choices=[('ohm', 'Ohm(s)'), ('kilohm', 'Kilohm(s)'), ('megaohm', 'Megaohm(s)'), ('gigaohm', 'Gigaohm(s)')], blank=True, null=True, max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodeNet',
            fields=[
                ('equipment_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='experiment.Equipment', serialize=False)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='EEGElectrodeNetSystem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('eeg_electrode_localization_system', models.ForeignKey(to='experiment.EEGElectrodeLocalizationSystem')),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodePosition',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('coordinate_x', models.IntegerField(blank=True, null=True)),
                ('coordinate_y', models.IntegerField(blank=True, null=True)),
                ('eeg_electrode_localization_system', models.ForeignKey(to='experiment.EEGElectrodeLocalizationSystem')),
                ('position_reference', models.ForeignKey(related_name='children', to='experiment.EEGElectrodePosition', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodePositionCollectionStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('worked', models.BooleanField()),
                ('eeg_data', models.ForeignKey(to='experiment.EEGData')),
            ],
        ),
        migrations.CreateModel(
            name='EEGElectrodePositionSetting',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('used', models.BooleanField()),
                ('eeg_electrode_layout_setting', models.ForeignKey(to='experiment.EEGElectrodeLayoutSetting')),
                ('eeg_electrode_position', models.ForeignKey(to='experiment.EEGElectrodePosition')),
            ],
        ),
        migrations.CreateModel(
            name='EEGFilterSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(primary_key=True, to='experiment.EEGSetting', serialize=False)),
                ('high_pass', models.FloatField(blank=True, null=True)),
                ('low_pass', models.FloatField(blank=True, null=True)),
                ('order', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGFilterType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGMachine',
            fields=[
                ('equipment_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='experiment.Equipment', serialize=False)),
                ('number_of_channels', models.IntegerField(blank=True, null=True)),
                ('software_version', models.CharField(blank=True, null=True, max_length=150)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='EEGMachineSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(primary_key=True, to='experiment.EEGSetting', serialize=False)),
                ('number_of_channels_used', models.IntegerField()),
                ('eeg_machine', models.ForeignKey(to='experiment.EEGMachine')),
            ],
        ),
        migrations.CreateModel(
            name='EEGSolution',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('components', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EEGSolutionSetting',
            fields=[
                ('eeg_setting', models.OneToOneField(primary_key=True, to='experiment.EEGSetting', serialize=False)),
                ('eeg_solution', models.ForeignKey(to='experiment.EEGSolution')),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='eegsetting',
            name='set_of_equipment',
        ),
        migrations.AddField(
            model_name='eegsetting',
            name='copied_from',
            field=models.ForeignKey(related_name='children', to='experiment.EEGSetting', null=True),
        ),
        migrations.CreateModel(
            name='EEGElectrodeCap',
            fields=[
                ('eegelectrodenet_ptr', models.OneToOneField(primary_key=True, auto_created=True, parent_link=True, to='experiment.EEGElectrodeNet', serialize=False)),
                ('material', models.ForeignKey(to='experiment.Material', blank=True, null=True)),
            ],
            bases=('experiment.eegelectrodenet',),
        ),
        migrations.AddField(
            model_name='eegfiltersetting',
            name='eeg_filter_type',
            field=models.ForeignKey(to='experiment.EEGFilterType'),
        ),
        migrations.AddField(
            model_name='eegelectrodepositioncollectionstatus',
            name='eeg_electrode_position_setting',
            field=models.ForeignKey(to='experiment.EEGElectrodePositionSetting'),
        ),
        migrations.AddField(
            model_name='eegelectrodenetsystem',
            name='eeg_electrode_net',
            field=models.ForeignKey(to='experiment.EEGElectrodeNet'),
        ),
        migrations.AddField(
            model_name='eegelectrodenet',
            name='electrode_model_default',
            field=models.ForeignKey(to='experiment.EEGElectrodeModel'),
        ),
        migrations.AddField(
            model_name='eegelectrodemodel',
            name='material',
            field=models.ForeignKey(to='experiment.Material', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='eegelectrodelayoutsetting',
            name='eeg_electrode_net_system',
            field=models.ForeignKey(to='experiment.EEGElectrodeNetSystem'),
        ),
        migrations.AddField(
            model_name='eegdata',
            name='eeg_cap_size',
            field=models.ForeignKey(null=True, to='experiment.EEGCapSize'),
        ),
        migrations.AddField(
            model_name='eegcapsize',
            name='eeg_electrode_cap',
            field=models.ForeignKey(to='experiment.EEGElectrodeCap'),
        ),
    ]
