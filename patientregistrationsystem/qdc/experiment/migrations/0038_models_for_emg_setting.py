# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0037_initial_data_fileformat_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='ADConverter',
            fields=[
                ('equipment_ptr', models.OneToOneField(primary_key=True, parent_link=True, auto_created=True,
                                                       serialize=False, to='experiment.Equipment')),
                ('signal_to_noise_rate', models.FloatField(blank=True, null=True)),
                ('sampling_rate', models.FloatField(blank=True, null=True)),
                ('resolution', models.FloatField(blank=True, null=True)),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='EMGElectrodePlacement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.FileField(blank=True, null=True, upload_to=experiment.models.get_emg_placement_dir)),
                ('location', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGElectrodeSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='EMGSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Muscle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('anatomy_orign', models.TextField(blank=True, null=True)),
                ('anatomy_insertion', models.TextField(blank=True, null=True)),
                ('anatomy_function', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MuscleSide',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('muscle', models.ForeignKey(to='experiment.Muscle')),
            ],
        ),
        migrations.CreateModel(
            name='MuscleSubdivision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('muscle', models.ForeignKey(to='experiment.Muscle')),
            ],
        ),
        migrations.CreateModel(
            name='Software',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
                ('manufacturer', models.ForeignKey(to='experiment.Manufacturer')),
            ],
        ),
        migrations.CreateModel(
            name='SoftwareVersion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('software', models.ForeignKey(to='experiment.Software')),
            ],
        ),
        migrations.CreateModel(
            name='StandardizationSystem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGADConverterSetting',
            fields=[
                ('emg_setting', models.OneToOneField(primary_key=True, related_name='emg_ad_converter_setting',
                                                     serialize=False, to='experiment.EMGSetting')),
                ('sampling_rate', models.FloatField(blank=True, null=True)),
                ('ad_converter', models.ForeignKey(to='experiment.ADConverter')),
            ],
        ),
        migrations.CreateModel(
            name='EMGAmplifierSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(primary_key=True, related_name='emg_amplifier_setting',
                                                               serialize=False, to='experiment.EMGElectrodeSetting')),
                ('gain', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EMGDigitalFilterSetting',
            fields=[
                ('emg_setting', models.OneToOneField(primary_key=True, related_name='emg_digital_filter_setting',
                                                     serialize=False, to='experiment.EMGSetting')),
                ('low_pass', models.FloatField(blank=True, null=True)),
                ('high_pass', models.FloatField(blank=True, null=True)),
                ('band_pass', models.FloatField(blank=True, null=True)),
                ('notch', models.FloatField(blank=True, null=True)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('filter_type', models.ForeignKey(to='experiment.FilterType')),
            ],
        ),
        migrations.CreateModel(
            name='EMGElectrodePlacementSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(primary_key=True,
                                                               related_name='emg_electrode_placement_setting',
                                                               serialize=False, to='experiment.EMGElectrodeSetting')),
                ('remarks', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EMGIntramuscularPlacement',
            fields=[
                ('emgelectrodeplacement_ptr', models.OneToOneField(primary_key=True, parent_link=True,
                                                                   auto_created=True, serialize=False,
                                                                   to='experiment.EMGElectrodePlacement')),
                ('method_of_insertion', models.TextField(blank=True, null=True)),
                ('depth_of_insertion', models.TextField(blank=True, null=True)),
            ],
            bases=('experiment.emgelectrodeplacement',),
        ),
        migrations.CreateModel(
            name='EMGNeedlePlacement',
            fields=[
                ('emgelectrodeplacement_ptr', models.OneToOneField(primary_key=True, parent_link=True,
                                                                   auto_created=True, serialize=False,
                                                                   to='experiment.EMGElectrodePlacement')),
                ('depth_of_insertion', models.TextField(blank=True, null=True)),
            ],
            bases=('experiment.emgelectrodeplacement',),
        ),
        migrations.CreateModel(
            name='EMGPreamplifierSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(primary_key=True,
                                                               related_name='emg_preamplifier_setting',
                                                               serialize=False, to='experiment.EMGElectrodeSetting')),
                ('gain', models.FloatField(blank=True, null=True)),
                ('amplifier', models.ForeignKey(to='experiment.Amplifier')),
            ],
        ),
        migrations.CreateModel(
            name='EMGSurfacePlacement',
            fields=[
                ('emgelectrodeplacement_ptr', models.OneToOneField(primary_key=True, parent_link=True,
                                                                   auto_created=True, serialize=False,
                                                                   to='experiment.EMGElectrodePlacement')),
                ('start_posture', models.TextField(blank=True, null=True)),
                ('orientation', models.TextField(blank=True, null=True)),
                ('fixation_on_the_skin', models.TextField(blank=True, null=True)),
                ('reference_electrode', models.TextField(blank=True, null=True)),
                ('clinical_test', models.TextField(blank=True, null=True)),
            ],
            bases=('experiment.emgelectrodeplacement',),
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
            field=models.ForeignKey(related_name='emg_electrode_settings', to='experiment.EMGSetting'),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacement',
            name='muscle_subdivision',
            field=models.ForeignKey(to='experiment.MuscleSubdivision'),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacement',
            name='placement_reference',
            field=models.ForeignKey(to='experiment.EMGElectrodePlacement', related_name='children', null=True),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacement',
            name='standardization_system',
            field=models.ForeignKey(to='experiment.StandardizationSystem'),
        ),
        migrations.CreateModel(
            name='EMGAnalogFilterSetting',
            fields=[
                ('emg_electrode_setting', models.OneToOneField(primary_key=True,
                                                               related_name='emg_analog_filter_setting',
                                                               serialize=False, to='experiment.EMGAmplifierSetting')),
                ('low_pass', models.FloatField(blank=True, null=True)),
                ('high_pass', models.FloatField(blank=True, null=True)),
                ('band_pass', models.FloatField(blank=True, null=True)),
                ('notch', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='emgelectrodeplacementsetting',
            name='emg_electrode_placement',
            field=models.ForeignKey(to='experiment.EMGElectrodePlacement'),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacementsetting',
            name='muscle_side',
            field=models.ForeignKey(blank=True, to='experiment.MuscleSide', null=True),
        ),
        migrations.AddField(
            model_name='emgamplifiersetting',
            name='amplifier',
            field=models.ForeignKey(to='experiment.Amplifier'),
        ),
    ]
