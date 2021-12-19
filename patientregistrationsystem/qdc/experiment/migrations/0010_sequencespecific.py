# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2021-12-19 14:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0009_auto_20211219_1301'),
    ]

    operations = [
        migrations.CreateModel(
            name='SequenceSpecific',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scanning_sequence', models.CharField(max_length=255)),
                ('sequence_variant', models.CharField(max_length=255)),
                ('scan_options', models.CharField(max_length=255)),
                ('sequence_name', models.CharField(max_length=255)),
                ('pulse_sequence_details', models.CharField(max_length=255)),
                ('non_linear_gradient_collection', models.BooleanField()),
                ('mr_acquisition_type', models.CharField(max_length=255)),
                ('mt_state', models.BooleanField()),
                ('mt_offset_frequency', models.IntegerField()),
                ('mt_pulse_bandwith', models.IntegerField()),
                ('mt_number_of_pulses', models.IntegerField()),
                ('mt_pulse_duration', models.IntegerField()),
                ('mt_pulse_shape', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.PulseShape')),
                ('pulse_sequence_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.PulseSequence')),
            ],
        ),
    ]
