# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):
    pass


def load_data(apps, schema_editor):

    file_format_model = apps.get_model("experiment", "FileFormat")

    if not file_format_model.objects.filter(nes_code="txt"):

        # create new file format
        file_format_model(
            nes_code="txt",
            extension=".txt",
            description="",
            name="Text file",
            name_en="Text file",
            name_pt_br="Arquivo texto",
        ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0092_group_and_data_configuration_tree_codes'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
