# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from experiment.views import create_list_of_trees, list_data_configuration_tree, create_data_configuration_tree


def backwards_data(apps, schema_editor):
    data_configuration_tree_model = apps.get_model("experiment", "DataConfigurationTree")
    questionnaire_response_model = apps.get_model("experiment", "QuestionnaireResponse")

    for questionnaire in questionnaire_response_model.objects.all():
        questionnaire.component_configuration = questionnaire.data_configuration_tree.component_configuration
        questionnaire.save()
        questionnaire.data_configuration_tree = None
        questionnaire.save()

    data_configuration_tree_model.objects.all().delete()


def load_data(apps, schema_editor):

    data_configuration_tree_model = apps.get_model("experiment", "DataConfigurationTree")
    questionnaire_response_model = apps.get_model("experiment", "QuestionnaireResponse")

    for questionnaire_response in questionnaire_response_model.objects.all():

        # print("\nq_id {} conf_id {} token_id {} protocol_id {}".format(
        #     str(questionnaire_response.id),
        #     str(questionnaire_response.component_configuration_id),
        #     str(questionnaire_response.token_id),
        #     str(questionnaire_response.subject_of_group.group.experimental_protocol_id)))

        chosen_path = []

        # Get all paths related to this group
        if questionnaire_response.subject_of_group.group.experimental_protocol:
            list_of_paths = \
                create_list_of_trees(questionnaire_response.subject_of_group.group.experimental_protocol_id,
                                     "questionnaire")

            # print("\n")
            # print(list_of_paths)

            # trying to find some path
            for path in list_of_paths:
                if path[-1][0] == questionnaire_response.component_configuration_id:
                    chosen_path = path

        # print("\nChosen path:")
        # print(chosen_path)

        data_configuration_tree = None

        if chosen_path:

            # search for the path in data_configuration_tree
            data_configuration_tree_id = \
                list_data_configuration_tree(questionnaire_response.component_configuration_id,
                                             [item[0] for item in path])

            if not data_configuration_tree_id:
                print("\nCreating a new data_configuration_tree for path {}".format(chosen_path))
                data_configuration_tree_id = create_data_configuration_tree([item[0] for item in path])

            data_configuration_tree = data_configuration_tree_model.objects.get(pk=data_configuration_tree_id)

        else:
            # if there is not a path, creating a simple data_configuration_tree
            print("\ncreating a simple data_configuration_tree for {} ({})"
                  .format(questionnaire_response.token_id, str(questionnaire_response.id)))

            data_configuration_tree = data_configuration_tree_model(
                component_configuration=questionnaire_response.component_configuration
            )
            data_configuration_tree.save()

        questionnaire_response.data_configuration_tree = data_configuration_tree
        questionnaire_response.save()


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0017_create_data_configuration_tree'),
    ]

    operations = [
        migrations.RunPython(load_data, backwards_data)
    ]
