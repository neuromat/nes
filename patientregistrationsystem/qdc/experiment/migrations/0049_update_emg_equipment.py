# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0048_emg_setting_not_null_for_emg_data'),
    ]

    operations = [
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
            name='ElectrodeConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(null=True, max_length=150)),
                ('name_en', models.CharField(null=True, max_length=150)),
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
                ('value', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='EMGPreamplifierFilterSetting',
            fields=[
                ('emg_preamplifier_filter_setting', models.OneToOneField(related_name='emg_preamplifier_filter_setting', serialize=False, primary_key=True, to='experiment.EMGPreamplifierSetting')),
                ('low_pass', models.FloatField(blank=True, null=True)),
                ('high_pass', models.FloatField(blank=True, null=True)),
                ('band_pass', models.FloatField(blank=True, null=True)),
                ('notch', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IntramuscularElectrode',
            fields=[
                ('electrodemodel_ptr', models.OneToOneField(serialize=False, to='experiment.ElectrodeModel', parent_link=True, auto_created=True, primary_key=True)),
                ('strand', models.CharField(choices=[('single', 'Single'), ('multi', 'Multi')], max_length=20)),
                ('length_of_exposed_tip', models.FloatField(blank=True, null=True)),
                ('insulation_material', models.ForeignKey(blank=True, null=True, to='experiment.Material')),
            ],
            bases=('experiment.electrodemodel',),
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
                ('measure_system', models.ForeignKey(to='experiment.MeasureSystem')),
            ],
        ),
        migrations.CreateModel(
            name='NeedleElectrode',
            fields=[
                ('electrodemodel_ptr', models.OneToOneField(serialize=False, to='experiment.ElectrodeModel', parent_link=True, auto_created=True, primary_key=True)),
                ('size', models.FloatField(blank=True, null=True)),
                ('size_unit', models.CharField(choices=[('mm', 'millimeter(s)'), ('cm', 'centimeter(s)')], max_length=10)),
                ('number_of_conductive_contact_points_at_the_tip', models.IntegerField(blank=True, null=True)),
                ('size_of_conductive_contact_points_at_the_tip', models.FloatField(blank=True, null=True)),
            ],
            bases=('experiment.electrodemodel',),
        ),
        migrations.CreateModel(
            name='SurfaceElectrode',
            fields=[
                ('electrodemodel_ptr', models.OneToOneField(serialize=False, to='experiment.ElectrodeModel', parent_link=True, auto_created=True, primary_key=True)),
                ('conduction_type', models.CharField(choices=[('gelled', 'Gelled'), ('dry', 'Dry')], max_length=20)),
                ('electrode_mode', models.CharField(choices=[('active', 'Active'), ('passive', 'Passive')], max_length=20)),
                ('electrode_shape', models.ForeignKey(to='experiment.ElectrodeShape')),
            ],
            bases=('experiment.electrodemodel',),
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
        migrations.RemoveField(
            model_name='muscle',
            name='anatomy_function',
        ),
        migrations.RemoveField(
            model_name='muscle',
            name='anatomy_insertion',
        ),
        migrations.RemoveField(
            model_name='muscle',
            name='anatomy_orign',
        ),
        migrations.AddField(
            model_name='amplifier',
            name='common_mode_rejection_ratio',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='amplifier',
            name='input_impedance',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='amplifier',
            name='input_impedance_unit',
            field=models.CharField(blank=True, choices=[('ohm', 'Ohm(s)'), ('kilohm', 'Kilohm(s)'), ('megaohm', 'Megaohm(s)'), ('gigaohm', 'Gigaohm(s)')], null=True, max_length=15),
        ),
        migrations.AddField(
            model_name='amplifier',
            name='number_of_channels',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='electrodemodel',
            name='electrode_type',
            field=models.CharField(blank=True, choices=[('surface', 'Surface'), ('intramuscular', 'Intramuscular'), ('needle', 'Needle')], null=True, max_length=50),
        ),
        migrations.AddField(
            model_name='electrodemodel',
            name='inter_electrode_distance',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='electrodemodel',
            name='inter_electrode_distance_unit',
            field=models.CharField(blank=True, choices=[('mm', 'millimeter(s)'), ('cm', 'centimeter(s)')], null=True, max_length=10),
        ),
        migrations.AddField(
            model_name='emgelectrodeplacement',
            name='placement_type',
            field=models.CharField(blank=True, choices=[('surface', 'Surface'), ('intramuscular', 'Intramuscular'), ('needle', 'Needle')], null=True, max_length=50),
        ),
        migrations.AddField(
            model_name='musclesubdivision',
            name='anatomy_function',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='musclesubdivision',
            name='anatomy_insertion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='musclesubdivision',
            name='anatomy_origin',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='electrodesurfacemeasure',
            name='electrode_surface',
            field=models.ForeignKey(to='experiment.SurfaceElectrode'),
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
            model_name='amplifier',
            name='amplifier_detection_type',
            field=models.ForeignKey(blank=True, null=True, to='experiment.AmplifierDetectionType'),
        ),
        migrations.AddField(
            model_name='amplifier',
            name='tethering_system',
            field=models.ForeignKey(blank=True, null=True, to='experiment.TetheringSystem'),
        ),
        migrations.AddField(
            model_name='electrodemodel',
            name='electrode_configuration',
            field=models.ForeignKey(blank=True, null=True, to='experiment.ElectrodeConfiguration'),
        ),
    ]
