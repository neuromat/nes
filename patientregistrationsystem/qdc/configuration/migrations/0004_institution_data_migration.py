# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):

    current_institution_model = apps.get_model("configuration", "Institution")
    local_institution_model = apps.get_model("configuration", "LocalInstitution")
    institution_model = apps.get_model("team", "Institution")

    # copy to current from local
    for local_institution in local_institution_model.objects.all():

        # copy to current-institution
        new_current_institution = current_institution_model(
            code=local_institution.code,
            name=local_institution.institution.name,
            url=local_institution.url,
            logo=local_institution.logo
        )
        new_current_institution.save()

    # remove institution
    institution_model.objects.all().delete()


def load_data(apps, schema_editor):

    current_institution_model = apps.get_model("configuration", "Institution")
    local_institution_model = apps.get_model("configuration", "LocalInstitution")
    institution_model = apps.get_model("team", "Institution")

    for current_institution in current_institution_model.objects.all():

        # create a new institution
        new_institution = institution_model(
            name=current_institution.name if current_institution.name else '',
            acronym='',
            country='',
            parent=None
        )
        new_institution.save()

        # copy to local-institution
        new_local_institution = local_institution_model(
            code=current_institution.code,
            institution=new_institution,
            url=current_institution.url,
            logo=current_institution.logo
        )
        new_local_institution.save()


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0003_localinstitution'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data),
    ]
