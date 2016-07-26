# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command


def backwards_data(apps, schema_editor):
    print("backwards data")


def load_data(apps, schema_editor):

    call_command('loaddata', '0050_initial_data_new_models.json', verbosity=0, interactive=False)


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0049_update_emg_equipment'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data),
    ]
