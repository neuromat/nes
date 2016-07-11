# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def backwards_data(apps, schema_editor):
    file_format_model = apps.get_model("experiment", "FileFormat")

    for file_format in file_format_model.objects.all():
        file_format.tags = []
        file_format.save()


def load_data(apps, schema_editor):

    tag_model = apps.get_model("experiment", "Tag")
    file_format_model = apps.get_model("experiment", "FileFormat")

    for file_format in file_format_model.objects.all():
        for tag in tag_model.objects.all():
            file_format.tags.add(tag)
            file_format.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0036_initial_data_tag'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
