# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def backwards_data(apps, schema_editor):
    pass


def load_data(apps, schema_editor):
    file_format_model = apps.get_model("experiment", "FileFormat")

    if not file_format_model.objects.filter(nes_code="MNE-RawFromBrainVision"):
        file_format_model(
            nes_code="MNE-RawFromBrainVision",
            name="EEG raw data - Brain Vision binary (MNE)",
            extension=".eeg .vhdr .vmrk",
            description="File format to stores the three different filetypes (.vhdr, .eeg, .vmrk) from Brain Vision "
                        "Recorder Software",
            tags="EEG",
        ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
