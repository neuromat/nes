# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.core.management import call_command


def backwards_data(apps, schema_editor):
    print("backwards data")


def load_data(apps, schema_editor):

    information_type_model = apps.get_model("experiment", "InformationType")

    if information_type_model.objects.all().count() == 0:
        call_command('loaddata', '0091_initial_information_type.json', verbosity=0, interactive=False)


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0090_generic_data_collection'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data),
    ]
