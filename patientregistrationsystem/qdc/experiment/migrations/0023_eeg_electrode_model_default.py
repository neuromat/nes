# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):

    eeg_electrode_position_setting_model = apps.get_model("experiment", "EEGElectrodePositionSetting")

    for position_setting in eeg_electrode_position_setting_model.objects.all():
        position_setting.electrode_model = None
        position_setting.save()


def load_data(apps, schema_editor):

    eeg_electrode_position_setting_model = apps.get_model("experiment", "EEGElectrodePositionSetting")

    for position_setting in eeg_electrode_position_setting_model.objects.all():

        eeg_electrode_net = position_setting.eeg_electrode_layout_setting.eeg_electrode_net_system.eeg_electrode_net

        position_setting.electrode_model = eeg_electrode_net.electrode_model_default
        position_setting.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0022_eeg_electrode_model_for_eeg_position_setting'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
