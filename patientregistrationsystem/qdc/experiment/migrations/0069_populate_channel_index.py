# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):

    # channel_index in EEGElectrodePositionCollectionStatus
    eeg_electrode_position_collection_status_model = \
        apps.get_model("experiment", "EEGElectrodePositionCollectionStatus")

    for eeg_electrode_position_collection_status in eeg_electrode_position_collection_status_model.objects.all():
        eeg_electrode_position_collection_status.channel_index = None
        eeg_electrode_position_collection_status.save()

    # channel_index in EEGElectrodePositionSetting
    eeg_electrode_position_setting_model = apps.get_model("experiment", "EEGElectrodePositionSetting")

    for eeg_electrode_position_setting in eeg_electrode_position_setting_model.objects.all():
        eeg_electrode_position_setting.channel_index = None
        eeg_electrode_position_setting.save()

    # channel_default_index in EEGElectrodePosition
    eeg_electrode_position_model = apps.get_model("experiment", "EEGElectrodePosition")

    for eeg_electrode_position in eeg_electrode_position_model.objects.all():
        eeg_electrode_position.channel_default_index = None
        eeg_electrode_position.save()


def load_data(apps, schema_editor):

    # channel_default_index in EEGElectrodePosition
    eeg_electrode_localization_system_model = apps.get_model("experiment", "EEGElectrodeLocalizationSystem")

    for eeg_electrode_localization_system in eeg_electrode_localization_system_model.objects.all():
        channel_default_index = 1
        for electrode_position in eeg_electrode_localization_system.electrode_positions.all():
            electrode_position.channel_default_index = channel_default_index
            electrode_position.save()
            channel_default_index += 1

    # channel_index in EEGElectrodePositionSetting
    eeg_electrode_position_setting_model = apps.get_model("experiment", "EEGElectrodePositionSetting")

    for eeg_electrode_position_setting in eeg_electrode_position_setting_model.objects.all():
        eeg_electrode_position_setting.channel_index = \
            eeg_electrode_position_setting.eeg_electrode_position.channel_default_index
        eeg_electrode_position_setting.save()

    # channel_index in EEGElectrodePositionCollectionStatus
    eeg_electrode_position_collection_status_model = \
        apps.get_model("experiment", "EEGElectrodePositionCollectionStatus")

    for eeg_electrode_position_collection_status in eeg_electrode_position_collection_status_model.objects.all():
        eeg_electrode_position_collection_status.channel_index = \
            eeg_electrode_position_collection_status.eeg_electrode_position_setting.channel_index
        eeg_electrode_position_collection_status.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0068_eeg_electrode_position_channel_index'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data),
    ]
