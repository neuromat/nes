# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


# def load_data(apps, schema_editor):
#
#     current_institution_model = apps.get_model("configuration", "Institution")
#     local_institution_model = apps.get_model("configuration", "LocalInstitution")
#     institution_model = apps.get_model("team", "Institution")
#
#     for current_institution in current_institution_model.objects.all():
#


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0003_localinstitution'),
    ]

    operations = [
        # migrations.RunPython(load_data, backwards_data),
    ]
