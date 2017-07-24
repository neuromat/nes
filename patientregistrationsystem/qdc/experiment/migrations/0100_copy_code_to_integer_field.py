# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):
    data_configuration_tree_model = apps.get_model("experiment", "DataConfigurationTree")

    for data_configuration_tree in data_configuration_tree_model.objects.all():
        if data_configuration_tree.code_number:
            data_configuration_tree.code_number = None
            data_configuration_tree.save()


def load_data(apps, schema_editor):

    data_configuration_tree_model = apps.get_model("experiment", "DataConfigurationTree")

    for data_configuration_tree in data_configuration_tree_model.objects.all():
        if data_configuration_tree.code and \
                data_configuration_tree.code[:2] == 'ph' and \
                data_configuration_tree.code[2:].isnumeric():
            data_configuration_tree.code_number = int(data_configuration_tree.code[2:])
            data_configuration_tree.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0099_data_configuration_tree_code_temp'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
