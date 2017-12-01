# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def get_permission_list_and_senior_research_group(apps, researcher_group_name):

    ContentType = apps.get_model("contenttypes", "ContentType")

    equipment_content_type, created = ContentType.objects.get_or_create(app_label='experiment', model='equipment')

    Group = apps.get_model("auth", "Group")

    senior_researcher_group, created = Group.objects.get_or_create(name=researcher_group_name)

    Permission = apps.get_model("auth", "Permission")

    senior_researcher_permission_list = []

    permission_data, created = Permission.objects.get_or_create(codename='register_equipment',
                                                                name="Can register equipment",
                                                                content_type=equipment_content_type)

    senior_researcher_permission_list.append(permission_data)

    return senior_researcher_permission_list, senior_researcher_group


def backwards_data(apps, schema_editor):

    senior_researcher_permission_list, senior_researcher_group = \
        get_permission_list_and_senior_research_group(apps, 'Senior researcher')

    for p in senior_researcher_permission_list:
        senior_researcher_group.permissions.remove(p)

    junior_researcher_permission_list, junior_researcher_group = \
        get_permission_list_and_senior_research_group(apps, 'Junior researcher')

    for p in junior_researcher_permission_list:
        junior_researcher_group.permissions.remove(p)

    print("backwards data")


def load_data(apps, schema_editor):

    senior_researcher_permission_list, senior_researcher_group = \
        get_permission_list_and_senior_research_group(apps, 'Senior researcher')

    for p in senior_researcher_permission_list:
        senior_researcher_group.permissions.add(p)

    junior_researcher_permission_list, junior_researcher_group = \
        get_permission_list_and_senior_research_group(apps, 'Junior researcher')

    for p in junior_researcher_permission_list:
        junior_researcher_group.permissions.add(p)


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0030_auto_20160621_1859'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
