# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def backwards_data(apps, schema_editor):
    pass


def load_data(apps, schema_editor):

    tag_model = apps.get_model("experiment", "Tag")

    if not tag_model.objects.filter(name="EEG"):
        tag_model(
            name="EEG"
        ).save()

    if not tag_model.objects.filter(name="EMG"):
        tag_model(
            name="EMG"
        ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0035_fileformat_tags'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
