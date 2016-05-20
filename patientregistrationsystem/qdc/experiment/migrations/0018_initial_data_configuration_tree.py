# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def backwards_data(apps, schema_editor):
    data_configuration_tree_model = apps.get_model("experiment", "DataConfigurationTree")
    questionnaire_response_model = apps.get_model("experiment", "QuestionnaireResponse")

    for questionnaire in questionnaire_response_model.objects.all():
        questionnaire.data_configuration_tree = None
        questionnaire.save()

    data_configuration_tree_model.objects.all().delete()


def load_data(apps, schema_editor):

    data_configuration_tree_model = apps.get_model("experiment", "DataConfigurationTree")
    questionnaire_response_model = apps.get_model("experiment", "QuestionnaireResponse")

    for questionnaire in questionnaire_response_model.objects.all():
        # criar um data_configuration_tree
        new_data_configuration_tree = data_configuration_tree_model(
            component_configuration=questionnaire.component_configuration
        )
        new_data_configuration_tree.save()

        questionnaire.data_configuration_tree = new_data_configuration_tree
        questionnaire.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0017_create_data_configuration_tree'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
