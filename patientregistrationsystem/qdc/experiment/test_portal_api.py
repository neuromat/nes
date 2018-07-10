from unittest import TestCase

from experiment.models import Experiment
from experiment.portal import send_research_project_to_portal, \
    send_experiment_to_portal
from experiment.tests import ObjectsFactory

# TODO: test with mocking, not really sending experiment objects to portal
class SendExperimentToPortalTest(TestCase):

    def setUp(self):
        pass
        # research_project = ObjectsFactory.create_research_project()
        # ObjectsFactory.create_experiment(research_project)

    def test_send_experiment_researchers_to_portal(self):
        pass
        # experiment = Experiment.objects.last()
        # send_experiment_to_portal(experiment)
        # send_research_project_to_portal(experiment)
        #
        # researcher = ObjectsFactory.create_experiment_researcher(experiment)
        # result = send_experiment_researchers_to_portal(experiment)
        #
        # self.assertEqual(result['status'], '201')
        # self.assertEqual(result['researcher'], researcher.username)