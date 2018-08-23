import io
import zipfile

from django.contrib.auth.models import Group
from django.test import TestCase

from custom_user.tests_helper import create_user
from experiment.tests_original import ObjectsFactory
from patient.tests import UtilTests


class ExportTestCase(TestCase):

    def setUp(self):

        # create the groups of users and their permissions
        exec(open('add_initial_data.py').read())

        self.user, passwd = create_user(Group.objects.all())
        # TODO: passar password de self.user e não como 'passwd'
        self.client.login(username=self.user.username, password=passwd)

        # create experiment/experimental protocol/group
        self.experiment = ObjectsFactory.create_experiment(
            ObjectsFactory.create_research_project(self.user)
        )
        self.root_component = ObjectsFactory.create_block(self.experiment)
        self.group = ObjectsFactory.create_group(
            self.experiment, self.root_component
        )

        # create patient/subject/subject_of_group
        self.patient = UtilTests().create_patient_mock(changed_by=self.user)
        subject = ObjectsFactory.create_subject(self.patient)
        self.subject_of_group = \
            ObjectsFactory.create_subject_of_group(self.group, subject)

    def append_group_session_variable(self, variable, group_ids):
        """
        See:
        # https://docs.djangoproject.com/en/1.8/topics/testing/tools/#django.test.Client.session
        # for the form that it is done

        :param variable: variable to be appended to session
        :param group_ids: list of group ids (strins) as the value of the
        session variable
        """
        session = self.client.session
        session[variable] = group_ids
        session.save()

    def get_zipped_file(self, response):
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        return zipped_file

