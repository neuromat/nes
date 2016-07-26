# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):
    print("Nothing to do!")


def load_data(apps, schema_editor):

    electrode_model_model = apps.get_model("experiment", "ElectrodeModel")
    electrode_placement_model = apps.get_model("experiment", "EMGElectrodePlacement")

    for electrode_model in electrode_model_model.objects.all():
        electrode_model.electrode_type = "surface"
        electrode_model.save()

    for electrode_placement in electrode_placement_model.objects.all():
        electrode_placement.placement_type = "surface"
        electrode_placement.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0050_initial_data_new_models'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data),
    ]
