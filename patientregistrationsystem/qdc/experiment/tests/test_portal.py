import csv
from io import StringIO
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.test import TestCase

from custom_user.tests.tests_helper import create_user
from experiment.models import ScheduleOfSending, Component
from experiment.portal import (
    send_experiment_to_portal,
    send_experiment_researcher_to_portal,
    send_researcher_to_portal,
    send_steps_to_portal,
)
from experiment.tests.tests_helper import ObjectsFactory
from experiment.views import get_block_tree
from survey.abc_search_engine import ABCSearchEngine
from survey.survey_utils import HEADER_EXPLANATION_FIELDS
from survey.tests.tests_helper import create_survey


class PortalAPITest(TestCase):
    @patch("experiment.portal.RestApiClient")
    def test_send_experiment_to_portal(self, mockRestApiClientClass):
        # create the groups of users and their permissions
        exec(open("add_initial_data.py").read())

        user, user_passwd = create_user(Group.objects.all())

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        ScheduleOfSending.objects.create(
            experiment=experiment,
            responsible=user,
            status="scheduled",
            send_participant_age=False,
            reason_for_resending="Ein guter Grund",
        )

        send_experiment_to_portal(experiment)

        api_fields = {
            "nes_id",
            "title",
            "description",
            "data_acquisition_done",
            "project_url",
            "ethics_committee_url",
            "ethics_committee_file",
            "release_notes",
        }

        (
            api_schema,
            action_keys,
        ), kwargs = mockRestApiClientClass.return_value.client.action.call_args
        self.assertTrue(
            set(kwargs["params"].keys()).issubset(api_fields),
            str(set(kwargs["params"].keys())) + " not in " + str(api_fields),
        )

    @patch("experiment.portal.RestApiClient")
    def test_send_researcher_to_portal(self, mockRestApiClientClass):
        # create the groups of users and their permissions
        exec(open("add_initial_data.py").read())

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        researcher = ObjectsFactory.create_experiment_researcher(experiment)

        send_researcher_to_portal(research_project.id, researcher.researcher)

        api_fields = {"id", "first_name", "last_name", "email", "citation_name"}

        (
            api_schema,
            action_keys,
        ), kwargs = mockRestApiClientClass.return_value.client.action.call_args
        self.assertTrue(
            set(kwargs["params"].keys()).issubset(api_fields),
            str(set(kwargs["params"].keys())) + " not in " + str(api_fields),
        )

    @patch("experiment.portal.RestApiClient")
    def test_send_experiment_researcher_to_portal(self, mockRestApiClientClass):
        # create the groups of users and their permissions
        exec(open("add_initial_data.py").read())

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        researcher = ObjectsFactory.create_experiment_researcher(experiment)

        send_experiment_researcher_to_portal(researcher)

        api_fields = {
            "experiment_nes_id",
            "first_name",
            "last_name",
            "email",
            "institution",
            "citation_name",
            "citation_order",
        }

        (
            api_schema,
            action_keys,
        ), kwargs = mockRestApiClientClass.return_value.client.action.call_args
        self.assertTrue(
            set(kwargs["params"].keys()).issubset(api_fields),
            str(set(kwargs["params"].keys())) + " not in " + str(api_fields),
        )

    @patch("experiment.portal.RestApiClient")
    @patch("survey.abc_search_engine.Server")
    def test_send_questionnaire_to_portal_has_correct_metadata_columns(
        self, mockServerClass, mockRestApiClientClass
    ):
        # Create the groups of users and their permissions
        exec(open("add_initial_data.py").read())

        # Create objects necessary to send questionnaire step to portal
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        experimental_protocol = ObjectsFactory.create_block(experiment)
        group = ObjectsFactory.create_group(experiment, experimental_protocol)
        survey = create_survey(212121)  # fake number
        questionnaire_step = ObjectsFactory.create_component(
            experiment, Component.QUESTIONNAIRE, kwargs={"survey": survey}
        )
        ObjectsFactory.create_component_configuration(
            experimental_protocol, questionnaire_step
        )
        tree = get_block_tree(group.experimental_protocol, "en")

        # Mock methods used in test calling methods
        survey_languages = {"language": "en", "additional_languages": None}
        mockServerClass.return_value.get_survey_properties.return_value = (
            survey_languages
        )
        mockServerClass.return_value.export_responses.return_value = (
            b"ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFn"
            b"ZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImZha2VRdWVzdGlvbiIKI"
            b"jgiLCIxOTgwLTAxLTAxIDAwOjAwOjAwIiwiMiIsImVuIiwieDQ0cmRxeT"
            b"RhMGxoYjRMIiwiMiIsNSIsInRleHRvIGxvbmdvIgoK"
        )
        mockServerClass.return_value.get_language_properties.return_value = {
            "surveyls_title": "Ein wunderbar Titel"
        }
        mockServerClass.return_value.list_questions.return_value = [{"id": {"qid": 1}}]
        # Mock get_question_properties LimeSurvey API method using
        # ABCSearchEngine.QUESTION_PROPERTIES constant list with fake values
        question_order = 21
        group_id = 981
        question_properties = dict(
            zip(
                ABCSearchEngine.QUESTION_PROPERTIES,
                [
                    group_id,
                    "Question Title",
                    question_order,
                    "No available answers",
                    "No available answer options",
                    "fakeQuestion",
                    "N",
                    "No available attributes",
                    {"hidden", "1"},
                    "N",
                ],
            )
        )
        mockServerClass.return_value.get_question_properties.return_value = (
            question_properties
        )
        # mock list_groups LimeSurvey API method (fake values)
        language = "en"
        mockServerClass.return_value.list_groups.return_value = [
            {
                "randomization_group": "",
                "id": {"gid": group_id, "language": language},
                "group_name": "Grupo 1",
                "description": "",
                "group_order": 1,
                "sid": survey.lime_survey_id,
                "gid": group_id,
                "language": language,
                "grelevance": "",
            }
        ]

        send_steps_to_portal(21, tree, None, None, None, None, "en")

        # use mockRestApiClientClass to get metadata value that will be sent
        (
            api_schema,
            action_keys,
        ), kwargs = mockRestApiClientClass.return_value.client.action.call_args
        for field in [item[0] for item in HEADER_EXPLANATION_FIELDS]:
            self.assertIn(field, kwargs["params"]["survey_metadata"])
        survey_metadata = csv.reader(StringIO(kwargs["params"]["survey_metadata"]))
        for row in survey_metadata:
            self.assertEqual(len(row), len(HEADER_EXPLANATION_FIELDS))
