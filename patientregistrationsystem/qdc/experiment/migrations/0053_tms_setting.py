# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0052_electrode_and_placement_types_not_null'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoilModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(null=True, blank=True)),
                ('coil_design', models.CharField(max_length=50, choices=[('air_core_coil', 'Air core coil'), ('solid_core_coil', 'Solid core coil')], blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CoilShape',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('name_pt_br', models.CharField(max_length=150, null=True)),
                ('name_en', models.CharField(max_length=150, null=True)),
            ],
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
                ('coil_model', models.ForeignKey(to='experiment.CoilModel')),
            ],
            bases=('experiment.equipment',),
        ),
        migrations.CreateModel(
            name='TMSSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='adconverter',
            name='resolution',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='adconverter',
            name='sampling_rate',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='adconverter',
            name='signal_to_noise_rate',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='amplifier',
            name='common_mode_rejection_ratio',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='amplifier',
            name='gain',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='amplifier',
            name='input_impedance',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='amplifier',
            name='number_of_channels',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='block',
            name='number_of_mandatory_components',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='eegamplifiersetting',
            name='gain',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='eegcapsize',
            name='electrode_adjacent_distance',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='eegelectrodeposition',
            name='coordinate_x',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='eegelectrodeposition',
            name='coordinate_y',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='eegfiltersetting',
            name='high_pass',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='eegfiltersetting',
            name='low_pass',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='eegfiltersetting',
            name='order',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='eegmachine',
            name='number_of_channels',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='eegmachinesetting',
            name='number_of_channels_used',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='electrodemodel',
            name='impedance',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='electrodemodel',
            name='inter_electrode_distance',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='electrodesurfacemeasure',
            name='value',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgadconvertersetting',
            name='sampling_rate',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgamplifiersetting',
            name='gain',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emganalogfiltersetting',
            name='band_pass',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emganalogfiltersetting',
            name='high_pass',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emganalogfiltersetting',
            name='low_pass',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emganalogfiltersetting',
            name='notch',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgdigitalfiltersetting',
            name='band_pass',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgdigitalfiltersetting',
            name='high_pass',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgdigitalfiltersetting',
            name='low_pass',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgdigitalfiltersetting',
            name='notch',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgdigitalfiltersetting',
            name='order',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgpreamplifierfiltersetting',
            name='band_pass',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgpreamplifierfiltersetting',
            name='high_pass',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgpreamplifierfiltersetting',
            name='low_pass',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgpreamplifierfiltersetting',
            name='notch',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='emgpreamplifiersetting',
            name='gain',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='intramuscularelectrode',
            name='length_of_exposed_tip',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='needleelectrode',
            name='number_of_conductive_contact_points_at_the_tip',
            field=models.IntegerField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='needleelectrode',
            name='size',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='needleelectrode',
            name='size_of_conductive_contact_points_at_the_tip',
            field=models.FloatField(null=True, blank=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.CreateModel(
            name='TMSDeviceSetting',
            fields=[
                ('tms_setting', models.OneToOneField(related_name='tms_device_setting', serialize=False, to='experiment.TMSSetting', primary_key=True)),
                ('pulse_stimulus_type', models.CharField(max_length=50, choices=[('single_pulse', 'Single pulse'), ('paired_pulse', 'Paired pulse'), ('repetitive_pulse', 'Repetitive pulse')], blank=True, null=True)),
                ('tms_device', models.ForeignKey(to='experiment.TMSDevice')),
            ],
        ),
        migrations.AddField(
            model_name='tmssetting',
            name='copied_from',
            field=models.ForeignKey(related_name='children', to='experiment.TMSSetting', null=True),
        ),
        migrations.AddField(
            model_name='tmssetting',
            name='experiment',
            field=models.ForeignKey(to='experiment.Experiment'),
        ),
        migrations.AddField(
            model_name='tms',
            name='tms_setting',
            field=models.ForeignKey(to='experiment.TMSSetting'),
        ),
        migrations.AddField(
            model_name='coilmodel',
            name='coil_shape',
            field=models.ForeignKey(to='experiment.CoilShape'),
        ),
        migrations.AddField(
            model_name='coilmodel',
            name='material',
            field=models.ForeignKey(blank=True, to='experiment.Material', null=True),
        ),
    ]
