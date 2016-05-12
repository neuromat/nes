# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):

    model_eeg_step = apps.get_model("experiment", "EEG")
    model_eeg_data = apps.get_model("experiment", "EEGData")
    model_eeg_setting = apps.get_model("experiment", "EEGSetting")

    for eeg_step in model_eeg_step.objects.all():
        eeg_step.eeg_setting = None
        eeg_step.save()

    for eeg_data in model_eeg_data.objects.all():
        eeg_data.eeg_setting = None
        eeg_data.save()

    model_eeg_setting.objects.filter(name="EEG Setting without equipment associated used by migration").delete()


def load_data(apps, schema_editor):

    model_experiment = apps.get_model("experiment", "Experiment")
    model_eeg_step = apps.get_model("experiment", "EEG")
    model_eeg_setting = apps.get_model("experiment", "EEGSetting")
    model_eeg_data = apps.get_model("experiment", "EEGData")

    for experiment in model_experiment.objects.all():

        eeg_steps = model_eeg_step.objects.filter(experiment=experiment, component_type="eeg")

        if eeg_steps:

            # criar um eeg_setting_fake
            new_eeg_setting = model_eeg_setting(
                experiment=experiment,
                name="EEG Setting without equipment associated used by migration",
                description="EEG Setting without equipment. It is necessary to configure it properly"
            )
            new_eeg_setting.save()

            # for each eeg_step, associate the new eeg_setting
            for eeg_step in eeg_steps:
                eeg_step.eeg_setting = new_eeg_setting
                eeg_step.save()

            # for each eeg_data, associate the new eeg_setting
            for eeg_data in model_eeg_data.objects.filter(subject_of_group__group__experiment=experiment):
                eeg_data.eeg_setting = new_eeg_setting
                eeg_data.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0011_equipment_and_eeg_setting'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
