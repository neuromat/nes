# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def update_equipment_type(apps, current_value, new_value):

    equipment_model = apps.get_model("experiment", "Equipment")

    equipments = equipment_model.objects.filter(equipment_type=current_value)
    for equipment in equipments:
        equipment.equipment_type = new_value
        equipment.save()


def backwards_data(apps, schema_editor):
    update_equipment_type(apps, "amplifier", "eeg_amplifier")


def load_data(apps, schema_editor):
    update_equipment_type(apps, "eeg_amplifier", "amplifier")


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0044_initial_data_filtertype_tags'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
