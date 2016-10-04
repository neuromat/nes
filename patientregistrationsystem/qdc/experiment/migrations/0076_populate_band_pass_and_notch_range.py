# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def backwards_data(apps, schema_editor):
    emg_analog_filter_setting_model = apps.get_model("experiment", "EMGAnalogFilterSetting")

    for emg_analog_filter_setting in emg_analog_filter_setting_model.objects.all():
        emg_analog_filter_setting.low_band_pass = None
        emg_analog_filter_setting.high_band_pass = None
        emg_analog_filter_setting.low_notch = None
        emg_analog_filter_setting.high_notch = None
        emg_analog_filter_setting.save()


def load_data(apps, schema_editor):
    emg_analog_filter_setting_model = apps.get_model("experiment", "EMGAnalogFilterSetting")

    for emg_analog_filter_setting in emg_analog_filter_setting_model.objects.all():
        emg_analog_filter_setting.low_band_pass = emg_analog_filter_setting.band_pass
        emg_analog_filter_setting.high_band_pass = emg_analog_filter_setting.band_pass
        emg_analog_filter_setting.low_notch = emg_analog_filter_setting.notch
        emg_analog_filter_setting.high_notch = emg_analog_filter_setting.notch
        emg_analog_filter_setting.save()

class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0075_EMGAnalogFilterSetting_add_band_pass_and_notch_range'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data),
    ]
