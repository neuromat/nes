# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import experiment.models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0105_add_permission_change_researchproject_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdditionalDataFile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('additional_data', models.ForeignKey(to='experiment.AdditionalData')),
            ],
        ),
        migrations.CreateModel(
            name='DigitalGamePhaseFile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('digital_game_phase_data', models.ForeignKey(to='experiment.DigitalGamePhaseData')),
            ],
        ),
        migrations.CreateModel(
            name='EEGFile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('eeg_data', models.ForeignKey(to='experiment.EEGData')),
            ],
        ),
        migrations.CreateModel(
            name='EMGFile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('emg_data', models.ForeignKey(to='experiment.EMGData')),
            ],
        ),
        migrations.CreateModel(
            name='GenericDataCollectionFile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('file', models.FileField(upload_to=experiment.models.get_data_file_dir)),
                ('generic_data_collection_data', models.ForeignKey(to='experiment.GenericDataCollectionData')),
            ],
        ),
    ]
