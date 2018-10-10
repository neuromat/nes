from unittest.mock import patch

from django.contrib.auth.models import Group
from django.test import TestCase

from custom_user.tests_helper import create_user
from experiment.models import ScheduleOfSending
from experiment.portal import send_experiment_to_portal, send_experiment_researcher_to_portal,\
    send_researcher_to_portal
from experiment.tests.tests_original import ObjectsFactory

class PortalAPITest(TestCase):

    @patch('experiment.portal.RestApiClient')
    def test_send_experiment_to_portal(self, mockRestApiClientClass):
        # create the groups of users and their permissions
        exec(open('add_initial_data.py').read())

        user, user_passwd = create_user(Group.objects.all())

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        ScheduleOfSending.objects.create(
            experiment=experiment, responsible=user, status='scheduled',
            send_participant_age=False, reason_for_resending='Ein guter Grund'
        )

        send_experiment_to_portal(experiment)

        api_fields = {
            'nes_id', 'title', 'description', 'data_acquisition_done',
            'project_url', 'ethics_committee_url', 'ethics_committee_file',
            'release_notes'
        }

        (api_schema, action_keys), kwargs = \
            mockRestApiClientClass.return_value.client.action.call_args
        self.assertTrue(
            set(kwargs['params'].keys()).issubset(api_fields),
            str(set(kwargs['params'].keys())) + ' not in ' + str(api_fields)
        )

    @patch('experiment.portal.RestApiClient')
    def test_send_researcher_to_portal(self, mockRestApiClientClass):
        # create the groups of users and their permissions
        exec(open('add_initial_data.py').read())

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        researcher = ObjectsFactory.create_experiment_researcher(experiment)

        send_researcher_to_portal(research_project.id, researcher.researcher)

        api_fields = {'id', 'first_name', 'last_name', 'email', 'citation_name'}

        (api_schema, action_keys), kwargs = \
            mockRestApiClientClass.return_value.client.action.call_args
        self.assertTrue(
            set(kwargs['params'].keys()).issubset(api_fields),
            str(set(kwargs['params'].keys())) + ' not in ' + str(api_fields)
        )

    @patch('experiment.portal.RestApiClient')
    def test_send_experiment_researcher_to_portal(self, mockRestApiClientClass):
        # create the groups of users and their permissions
        exec(open('add_initial_data.py').read())

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        researcher = ObjectsFactory.create_experiment_researcher(experiment)

        send_experiment_researcher_to_portal(researcher)

        api_fields = {'experiment_nes_id', 'first_name', 'last_name',
                      'email', 'institution', 'citation_name', 'citation_order'}

        (api_schema, action_keys), kwargs = \
            mockRestApiClientClass.return_value.client.action.call_args
        self.assertTrue(
            set(kwargs['params'].keys()).issubset(api_fields),
            str(set(kwargs['params'].keys())) + ' not in ' + str(api_fields)
        )
