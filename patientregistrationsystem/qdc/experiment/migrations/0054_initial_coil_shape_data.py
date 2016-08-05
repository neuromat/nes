# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.management import call_command


def backwards_data(apps, schema_editor):
    print("backwards data")


def load_data(apps, schema_editor):

    call_command('loaddata', '0054_initial_coil_shape_data.json', verbosity=0, interactive=False)


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0053_tms_setting'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data),
    ]
