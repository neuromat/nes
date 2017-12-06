# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def backwards_data(apps, schema_editor):
    pass


def load_data(apps, schema_editor):

    file_format_model = apps.get_model("experiment", "FileFormat")

    if not file_format_model.objects.filter(nes_code="NEO-RawBinarySignalIO"):
        file_format_model(
            nes_code="NEO-RawBinarySignalIO",
            extension="raw",
            description="",
            name="EEG raw binary signal (NEO)"
        ).save()

    if not file_format_model.objects.filter(nes_code="other"):
        file_format_model(
            nes_code="other",
            extension=".*",
            description="",
            name="Other"
        ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0007_auto_20160425_1216'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
