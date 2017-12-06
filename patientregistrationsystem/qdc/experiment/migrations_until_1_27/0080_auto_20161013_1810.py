# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):
    pass


def load_data(apps, schema_editor):

    file_format_model = apps.get_model("experiment", "FileFormat")
    tag_model = apps.get_model("experiment", "Tag")
    eeg_data_model = apps.get_model("experiment", "EEGData")

    if not file_format_model.objects.filter(nes_code="MNE-RawFromEGI"):

        # create new file format
        file_format_model(
            nes_code="MNE-RawFromEGI",
            extension=".raw .egi",
            description="",
            name="EEG raw data - EGI simple binary (MNE)",
            name_en="EEG raw data - EGI simple binary (MNE)",
            name_pt_br="Dados brutos de EEG - arquivo binário EGI (MNE)",
        ).save()

        file_format_mne = file_format_model.objects.get(nes_code="MNE-RawFromEGI")

        # tag for EEG
        for tag in tag_model.objects.all():
            if tag.name == "EEG":
                file_format_mne.tags.add(tag)
                file_format_mne.save()

        file_format_neo = file_format_model.objects.get(nes_code="NEO-RawBinarySignalIO")

        # put all data files to mne
        for eeg_data in eeg_data_model.objects.filter(file_format=file_format_neo):
            eeg_data.file_format = file_format_mne
            eeg_data.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0079_emgpreamplifierfiltersetting_add_attributes'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
