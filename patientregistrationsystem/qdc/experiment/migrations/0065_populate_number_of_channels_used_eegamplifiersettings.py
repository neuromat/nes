# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):
    eeg_amplifier_setting_model = apps.get_model("experiment", "EEGAmplifierSetting")

    for eeg_amplifier_setting in eeg_amplifier_setting_model.objects.all():
        eeg_amplifier_setting.number_of_channels_used = None
        eeg_amplifier_setting.save()


def load_data(apps, schema_editor):
    eeg_amplifier_setting_model = apps.get_model("experiment", "EEGAmplifierSetting")

    for eeg_amplifier_setting in eeg_amplifier_setting_model.objects.all():
        if hasattr(eeg_amplifier_setting.eeg_setting, "eeg_machine_setting"):
            eeg_amplifier_setting.number_of_channels_used = \
                eeg_amplifier_setting.eeg_setting.eeg_machine_setting.number_of_channels_used
            eeg_amplifier_setting.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0064_eegamplifiersetting_number_of_channels_used'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data),
    ]
