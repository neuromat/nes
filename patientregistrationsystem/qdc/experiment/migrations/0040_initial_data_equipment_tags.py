# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def clear_equipment(apps, model_name):
    equipment_model = apps.get_model("experiment", model_name)

    for equipment in equipment_model.objects.all():
        equipment.tags = []
        equipment.save()


def update_equipment(apps, model_name):
    tag_model = apps.get_model("experiment", "Tag")
    equipment_model = apps.get_model("experiment", model_name)

    for equipment in equipment_model.objects.all():
        for tag in tag_model.objects.all():
            equipment.tags.add(tag)
            equipment.save()


def backwards_data(apps, schema_editor):
    clear_equipment(apps, "EEGMachine")
    clear_equipment(apps, "Amplifier")
    clear_equipment(apps, "ADConversor")


def load_data(apps, schema_editor):
    update_equipment(apps, "EEGMachine")
    update_equipment(apps, "Amplifier")
    update_equipment(apps, "ADConversor")


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0039_equipment_tags'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
