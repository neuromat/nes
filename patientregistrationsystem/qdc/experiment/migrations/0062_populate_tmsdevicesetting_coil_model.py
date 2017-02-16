# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):
    tms_device_setting_model = apps.get_model("experiment", "TMSDeviceSetting")

    for tms_device_setting in tms_device_setting_model.objects.all():
        tms_device_setting.coil_model_id = None
        tms_device_setting.save()


def load_data(apps, schema_editor):
    tms_device_setting_model = apps.get_model("experiment", "TMSDeviceSetting")

    for tms_device_setting in tms_device_setting_model.objects.all():
        tms_device_setting.coil_model_id = tms_device_setting.tms_device.coil_model.id
        tms_device_setting.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0061_tmsdevicesetting_coil_model'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data),
    ]
