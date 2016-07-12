# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def clear_equipment(apps, model_name):
    equipment_model = apps.get_model("experiment", model_name)

    for equipment in equipment_model.objects.all():
        equipment.tags = []
        equipment.save()


def update_equipment_tag(apps, model_name, tag_list):
    tag_model = apps.get_model("experiment", "Tag")
    equipment_model = apps.get_model("experiment", model_name)

    tags = tag_model.objects.filter(name__in=tag_list)
    for equipment in equipment_model.objects.all():
        for tag in tags:
            equipment.tags.add(tag)
            equipment.save()


def backwards_data(apps, schema_editor):
    clear_equipment(apps, "ElectrodeModel")


def load_data(apps, schema_editor):
    update_equipment_tag(apps, "ElectrodeModel", ["EEG", "EMG"])


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0041_auto_20160712_1150'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
