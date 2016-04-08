# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from patient.views import Patient as Participant


def backwards_data(apps, schema_editor):

    model_patient = apps.get_model("patient", "Patient")
    model_historical_patient = apps.get_model("patient", "HistoricalPatient")

    for patient in model_patient.objects.all():

        # update patient
        patient.code = None
        patient.save()

        # update patient history
        patient_history = model_historical_patient.objects.filter(id=patient.id)

        # update patient history
        for patient_historical in patient_history:
            patient_historical.code = None
            patient_historical.save()


def load_data(apps, schema_editor):

    model_patient = apps.get_model("patient", "Patient")
    model_historical_patient = apps.get_model("patient", "HistoricalPatient")

    for patient in model_patient.objects.all():

        # update patient
        patient.code = Participant.create_random_patient_code()
        patient.save()

        # update patient history
        patient_history = model_historical_patient.objects.filter(id=patient.id)

        # update patient history
        for patient_historical in patient_history:
            patient_historical.code = patient.code
            patient_historical.save()


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0010_create_patient_code'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
