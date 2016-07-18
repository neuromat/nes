# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):

    model_emg_step = apps.get_model("experiment", "EMG")
    model_emg_data = apps.get_model("experiment", "EMGData")
    model_emg_setting = apps.get_model("experiment", "EMGSetting")

    for emg_step in model_emg_step.objects.all():
        emg_step.emg_setting = None
        emg_step.save()

    for emg_data in model_emg_data.objects.all():
        emg_data.emg_setting = None
        emg_data.save()

    model_emg_setting.objects.filter(name="EMG Setting without equipment associated used by migration").delete()


def load_data(apps, schema_editor):

    model_experiment = apps.get_model("experiment", "Experiment")
    model_emg_step = apps.get_model("experiment", "EMG")
    model_emg_setting = apps.get_model("experiment", "EMGSetting")
    model_emg_data = apps.get_model("experiment", "EMGData")

    model_manufacturer = apps.get_model("experiment", "Manufacturer")
    model_software = apps.get_model("experiment", "Software")
    model_software_version = apps.get_model("experiment", "SoftwareVersion")

    # getting or creating a fake software_version
    query_set = model_software_version.objects.filter(name="Software Version created by migration")

    if query_set:
        fake_software_version = query_set[0]
    else:

        query_set = model_software.objects.filter(name="Software created by migration")

        if query_set:
            fake_software = query_set[0]
        else:

            query_set = model_manufacturer.objects.filter(name="Manufacturer created by migration")

            if query_set:
                fake_manufacturer = query_set[0]
            else:
                fake_manufacturer = model_manufacturer(
                    name="Manufacturer created by migration"
                )
                fake_manufacturer.save()

            fake_software = model_software(
                manufacturer=fake_manufacturer,
                name="Software created by migration"
            )
            fake_software.save()

        fake_software_version = model_software_version(
            software=fake_software,
            name="Software Version created by migration"
        )
        fake_software_version.save()



    for experiment in model_experiment.objects.all():

        emg_steps = model_emg_step.objects.filter(experiment=experiment, component_type="emg")

        if emg_steps:

            # criar um emg_setting_fake
            new_emg_setting = model_emg_setting(
                experiment=experiment,
                name="EMG Setting without equipment associated used by migration",
                description="EMG Setting without equipment. It is necessary to configure it properly",
                acquisition_software_version=fake_software_version
            )
            new_emg_setting.save()

            # for each emg_step, associate the new emg_setting
            for emg_step in emg_steps:
                emg_step.emg_setting = new_emg_setting
                emg_step.save()

            # for each emg_data, associate the new emg_setting
            for emg_data in model_emg_data.objects.filter(subject_of_group__group__experiment=experiment):
                emg_data.emg_setting = new_emg_setting
                emg_data.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0046_emg_setting_to_emg_data'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
