import io
import os
import zipfile
from datetime import date, datetime, timedelta
from json import load

from django.contrib.auth.models import Group
from django.test import TestCase

from custom_user.tests_helper import create_user
from experiment.tests.tests_helper import ObjectsFactory
from patient.tests.tests_orig import UtilTests


class ExportTestCase(TestCase):

    def setUp(self):
        # create the groups of users and their permissions
        exec(open('add_initial_data.py').read())

        # return user password to use when necessary in subclasses
        self.user, self.user_passwd = create_user(Group.objects.all())
        self.client.login(username=self.user.username, password=self.user_passwd)

        # create experiment/experimental protocol/group
        self.research_project = ObjectsFactory.create_research_project(self.user)
        self.experiment = ObjectsFactory.create_experiment(self.research_project)
        self.root_component = ObjectsFactory.create_block(self.experiment)
        self.group = ObjectsFactory.create_group(self.experiment, self.root_component)

        # create patient/subject/subject_of_group
        self.patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(self.patient)
        self.subject_of_group = ObjectsFactory.create_subject_of_group(self.group, subject)

    def append_session_variable(self, key, value):
        """See:
        https://docs.djangoproject.com/en/1.8/topics/testing/tools/#django.test.Client.session
        for the form that it is done

        :param key: key to be appended to session
        :param value: list of group ids (strings) as the value of the
        session variable
        """
        session = self.client.session
        session[key] = value
        session.save()

    def get_zipped_file(self, response):
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        return zipped_file

    def get_datapackage_json_data(self, dir_, response):
        zipped_file = self.get_zipped_file(response)
        zipped_file.extractall(dir_)
        with open(os.path.join(dir_, 'datapackage.json')) as file:
            json_data = load(file)

        return json_data

    def assert_per_participant_step_file_exists(
            self, step_number, component_step, data_collection_folder, filename, zipped_file):
        self.assertTrue(
            any(os.path.join(
                'Per_participant', 'Participant_' + self.patient.code,
                'Step_' + str(step_number) + '_' +
                component_step.component_type.upper(),
                data_collection_folder,
                filename
            )
                in element for element in zipped_file.namelist()),
            os.path.join(
                'Per_participant', 'Participant_' + self.patient.code,
                'Step_' + str(step_number) + '_' +
                component_step.component_type.upper(),data_collection_folder,filename
            ) + ' not in: ' + str(zipped_file.namelist())
        )

    def assert_step_data_files_exists(self,step_number, component_step,
                                      data_collection_folder,filename,
                                      zipped_file):
        self.assertTrue(
            any(os.path.join(
                'Experimental_protocol', 'Step_' + str(step_number) + '_' +
                component_step.component_type.upper(),
                data_collection_folder,
                filename
            )
                in element for element in zipped_file.namelist()),
            os.path.join(
                'Experimental_protocol', 'Step_' + str(step_number) + '_' +
                component_step.component_type.upper(),data_collection_folder,filename
            ) + ' not in: ' + str(zipped_file.namelist())
        )

    @staticmethod
    def subject_age(birth_date, data_collection=None):
        date_ = data_collection.date if data_collection else date.today()
        return format(
            (date_ - datetime.strptime(birth_date, '%Y-%m-%d').date()) /
            timedelta(days=365.2425), '0.4'
        )

