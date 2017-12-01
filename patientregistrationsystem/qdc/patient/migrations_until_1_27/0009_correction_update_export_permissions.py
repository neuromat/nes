# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def update_permission_data(apps):

    ContentType = apps.get_model("contenttypes", "ContentType")

    patient_content_type, created = ContentType.objects.get_or_create(app_label='patient', model='patient')

    medicalrecorddata_content_type, created = ContentType.objects.get_or_create(app_label='patient',
                                                                                model='medicalrecorddata')

    patient_quest_response_content_type, created = ContentType.objects.get_or_create(app_label='patient',
                                                                                     model='questionnaireresponse')

    Permission = apps.get_model("auth", "Permission")

    # Export
    permission_data, created = Permission.objects.get_or_create(codename='export_patient',
                                                                content_type=patient_content_type)
    permission_data.name = "Can export patient"
    permission_data.save()

    permission_data, created = Permission.objects.get_or_create(codename='export_medicalrecorddata',
                                                                content_type=medicalrecorddata_content_type)
    permission_data.name = "Can export medical record"
    permission_data.save()

    permission_data, created = Permission.objects.get_or_create(codename='export_questionnaireresponse',
                                                                content_type=patient_quest_response_content_type)

    permission_data.name = "Can export questionnaire response"
    permission_data.save()


def backwards_data(apps, schema_editor):

    print("backwards data")


def load_data(apps, schema_editor):

    update_permission_data(apps)


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0008_update_export_permissions'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
