# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from survey.models import Survey


def backwards_data(apps, schema_editor):

    model_survey = apps.get_model("survey", "Survey")

    for survey in model_survey.objects.all():

        # update survey
        survey.code = None
        survey.save()


def load_data(apps, schema_editor):

    model_survey = apps.get_model("survey", "Survey")

    for survey in model_survey.objects.all():

        # update survey
        survey.code = Survey.create_random_survey_code()
        survey.save()


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0002_survey_code'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
