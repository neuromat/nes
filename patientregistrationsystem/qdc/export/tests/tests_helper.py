import io
import os
import zipfile
from datetime import date, datetime, timedelta
from json import load

from django.contrib.sessions.backends.base import SessionBase

from custom_user.tests.tests_helper import create_user
from django.contrib.auth.models import Group
from django.test import TestCase
from experiment.tests.tests_helper import ExperimentTestCase, ObjectsFactory


class ExportTestCase(ExperimentTestCase):
    def setUp(self) -> None:
        super(ExportTestCase, self).setUp()

        self.client.login(username=self.user.username, password=self.user_passwd)

    def append_session_variable(self, key, value) -> None:
        """See:
        https://docs.djangoproject.com/en/1.8/topics/testing/tools/#django.test.Client.session
        for the form that it is done

        :param key: key to be appended to session
        :param value: list of group ids (strings) as the value of the
        session variable
        """
        session: SessionBase = self.client.session
        session[key] = value
        session.save()

    def get_zipped_file(self, response) -> zipfile.ZipFile:
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, "r")
        self.assertIsNone(zipped_file.testzip())

        return zipped_file

    def get_datapackage_json_data(self, dir_, response):
        zipped_file: zipfile.ZipFile = self.get_zipped_file(response)
        zipped_file.extractall(dir_)
        with open(os.path.join(dir_, "datapackage.json")) as file:
            json_data = load(file)

        return json_data

    def assert_per_participant_step_file_exists(
        self, step_number, component_step, data_collection_folder, filename, zipped_file
    ) -> None:
        """Only checks self.patient"""
        self.assertTrue(
            any(
                os.path.join(
                    "Per_participant",
                    "Participant_" + self.patient.code,
                    "Step_"
                    + str(step_number)
                    + "_"
                    + component_step.component_type.upper(),
                    data_collection_folder,
                    filename,
                )
                in element
                for element in zipped_file.namelist()
            ),
            os.path.join(
                "Per_participant",
                "Participant_" + self.patient.code,
                "Step_"
                + str(step_number)
                + "_"
                + component_step.component_type.upper(),
                data_collection_folder,
                filename,
            )
            + " not in: "
            + str(zipped_file.namelist()),
        )

    def assert_step_data_files_exists(
        self, step_number, component_step, data_collection_folder, filename, zipped_file
    ) -> None:
        self.assertTrue(
            any(
                os.path.join(
                    "Experimental_protocol",
                    "Step_"
                    + str(step_number)
                    + "_"
                    + component_step.component_type.upper(),
                    data_collection_folder,
                    filename,
                )
                in element
                for element in zipped_file.namelist()
            ),
            os.path.join(
                "Experimental_protocol",
                "Step_"
                + str(step_number)
                + "_"
                + component_step.component_type.upper(),
                data_collection_folder,
                filename,
            )
            + " not in: "
            + str(zipped_file.namelist()),
        )

    @staticmethod
    def subject_age(birth_date, data_collection=None) -> str:
        date_ = data_collection.date if data_collection else date.today()
        return format(
            (date_ - datetime.strptime(birth_date, "%Y-%m-%d").date())
            / timedelta(days=365.2425),
            "0.4",
        )
