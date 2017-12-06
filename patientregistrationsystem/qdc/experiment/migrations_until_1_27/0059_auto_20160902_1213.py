# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.management import call_command


def backwards_data(apps, schema_editor):
    print("backwards data")


def load_data(apps, schema_editor):

    muscle_model = apps.get_model("experiment", "Muscle")
    standardization_system_model = apps.get_model("experiment", "StandardizationSystem")

    if muscle_model.objects.all().count() == 0 and standardization_system_model.objects.all().count() == 0:
        call_command('loaddata', '0059_initial_muscle_and_emg_placement.json', verbosity=0, interactive=False)


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0058_eegamplifiersetting_sampling_rate'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data),
    ]
