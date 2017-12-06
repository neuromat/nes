# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def get_permission_list_and_senior_research_group(apps):

    ContentType = apps.get_model("contenttypes", "ContentType")

    patient_content_type, created = ContentType.objects.get_or_create(app_label='patient', model='patient')

    medicalrecorddata_content_type, created = ContentType.objects.get_or_create(app_label='patient',
                                                                                model='medicalrecorddata')

    patient_quest_response_content_type, created = ContentType.objects.get_or_create(app_label='patient',
                                                                                     model='questionnaireresponse')

    Group = apps.get_model("auth", "Group")

    senior_researcher_group, created = Group.objects.get_or_create(name='Senior researcher')

    Permission = apps.get_model("auth", "Permission")

    senior_researcher_permission_list = []

    # Export
    permission_data, created = Permission.objects.get_or_create(codename='export_patient',
                                                                content_type=patient_content_type)

    senior_researcher_permission_list.append(permission_data)

    permission_data, created = Permission.objects.get_or_create(codename='export_medicalrecorddata',
                                                                content_type=medicalrecorddata_content_type)
    senior_researcher_permission_list.append(permission_data)

    permission_data, created = Permission.objects.get_or_create(codename='export_questionnaireresponse',
                                                                content_type=patient_quest_response_content_type)

    senior_researcher_permission_list.append(permission_data)

    return senior_researcher_permission_list, senior_researcher_group


def backwards_data(apps, schema_editor):

    senior_researcher_permission_list, senior_researcher_group = get_permission_list_and_senior_research_group(apps)

    for p in senior_researcher_permission_list:
        senior_researcher_group.permissions.remove(p)

    print("backwards data")


def load_data(apps, schema_editor):

    senior_researcher_permission_list, senior_researcher_group = get_permission_list_and_senior_research_group(apps)

    for p in senior_researcher_permission_list:
        senior_researcher_group.permissions.add(p)


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0007_auto_20160321_1436'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
