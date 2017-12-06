# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):

    eeg_data_model = apps.get_model("experiment", "EEGData")
    emg_data_model = apps.get_model("experiment", "EMGData")
    additional_data_model = apps.get_model("experiment", "AdditionalData")
    digital_game_phase_data_model = apps.get_model("experiment", "DigitalGamePhaseData")
    generic_data_collection_data_model = apps.get_model("experiment", "GenericDataCollectionData")

    eeg_file_model = apps.get_model("experiment", "EEGFile")
    emg_file_model = apps.get_model("experiment", "EMGFile")
    additional_data_file_model = apps.get_model("experiment", "AdditionalDataFile")
    digital_game_phase_file_model = apps.get_model("experiment", "DigitalGamePhaseFile")
    generic_data_collection_file_model = apps.get_model("experiment", "GenericDataCollectionFile")

    for eeg_file in eeg_file_model.objects.all():
        # getting the eeg_data
        eeg_data = eeg_data_model.objects.get(pk=eeg_file.eeg_data.id)
        # trying to restore eeg_data.file
        if not eeg_data.file:
            eeg_data.file = eeg_file.file
            eeg_data.save()

    for emg_file in emg_file_model.objects.all():
        emg_data = emg_data_model.objects.get(pk=emg_file.emg_data.id)
        if not emg_data.file:
            emg_data.file = emg_file.file
            emg_data.save()

    for additional_data_file in additional_data_file_model.objects.all():
        additional_data = additional_data_model.objects.get(pk=additional_data_file.additional_data.id)
        if not additional_data.file:
            additional_data.file = additional_data_file.file
            additional_data.save()

    for digital_game_phase_file in digital_game_phase_file_model.objects.all():
        digital_game_phase_data = \
            digital_game_phase_data_model.objects.get(pk=digital_game_phase_file.digital_game_phase_data.id)
        if not digital_game_phase_data.file:
            digital_game_phase_data.file = digital_game_phase_file.file
            digital_game_phase_data.save()

    for generic_data_collection_file in generic_data_collection_file_model.objects.all():
        generic_data_collection_data = \
            generic_data_collection_data_model.objects.get(
                pk=generic_data_collection_file.generic_data_collection_data.id)
        if not generic_data_collection_data.file:
            generic_data_collection_data.file = generic_data_collection_file.file
            generic_data_collection_data.save()


def load_data(apps, schema_editor):

    eeg_data_model = apps.get_model("experiment", "EEGData")
    emg_data_model = apps.get_model("experiment", "EMGData")
    additional_data_model = apps.get_model("experiment", "AdditionalData")
    digital_game_phase_data_model = apps.get_model("experiment", "DigitalGamePhaseData")
    generic_data_collection_data_model = apps.get_model("experiment", "GenericDataCollectionData")

    eeg_file_model = apps.get_model("experiment", "EEGFile")
    emg_file_model = apps.get_model("experiment", "EMGFile")
    additional_data_file_model = apps.get_model("experiment", "AdditionalDataFile")
    digital_game_phase_file_model = apps.get_model("experiment", "DigitalGamePhaseFile")
    generic_data_collection_file_model = apps.get_model("experiment", "GenericDataCollectionFile")

    for eeg_data in eeg_data_model.objects.all():
        if not eeg_file_model.objects.filter(eeg_data=eeg_data, file=eeg_data.file).exists():
            eeg_file_model.objects.create(eeg_data=eeg_data,
                                          file=eeg_data.file)

    for emg_data in emg_data_model.objects.all():
        if not emg_file_model.objects.filter(emg_data=emg_data, file=emg_data.file).exists():
            emg_file_model.objects.create(emg_data=emg_data,
                                          file=emg_data.file)

    for additional_data in additional_data_model.objects.all():
        if not additional_data_file_model.objects.filter(additional_data=additional_data,
                                                         file=additional_data.file).exists():
            additional_data_file_model.objects.create(additional_data=additional_data,
                                                      file=additional_data.file)

    for digital_game_phase_data in digital_game_phase_data_model.objects.all():
        if not digital_game_phase_file_model.objects.filter(digital_game_phase_data=digital_game_phase_data,
                                                            file=digital_game_phase_data.file).exists():
            digital_game_phase_file_model.objects.create(digital_game_phase_data=digital_game_phase_data,
                                                         file=digital_game_phase_data.file)

    for generic_data_collection_data in generic_data_collection_data_model.objects.all():
        if not generic_data_collection_file_model.objects.filter(
                generic_data_collection_data=generic_data_collection_data,
                file=generic_data_collection_data.file).exists():
            generic_data_collection_file_model.objects.create(generic_data_collection_data=generic_data_collection_data,
                                                              file=generic_data_collection_data.file)


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0106_data_file'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
