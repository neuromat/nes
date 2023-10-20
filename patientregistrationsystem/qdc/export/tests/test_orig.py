# -*- coding: utf-8 -*-
import os
from datetime import datetime
from os import mkdir, path, remove
from shutil import rmtree
from typing import Any
from unittest.mock import patch

from custom_user.models import User
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.translation import gettext as _
from export.export import is_patient_active
from export.input_export import InputExport, build_complete_export_structure
from export.views import QuestionnaireResponse, Questionnaires, Survey, create_directory
from patient.models import Gender, MaritalStatus, Patient

USER_EDIT = "user_edit"
USER_USERNAME = "myadmin"
USER_PWD = "mypassword"
USER_NEW = "user_new"

QUESTIONNAIRE_ID = 957421
TEST_QUESTIONNAIRE = 271192


marital_status_list: list[str] = ["Single", "Married", "Widow"]


class UtilTests:
    def create_patient_mock(
        self,
        name="Pacient Test",
        user=None,
        gender_name="Masculino",
        date_birth="2001-01-15",
    ) -> Patient:
        """Cria um participante para ser utilizado durante os testes"""

        gender = self.create_gender_mock(gender_name)
        return Patient.objects.create(
            name=name, date_birth=date_birth, gender=gender, changed_by=user
        )

    @staticmethod
    def create_marital_status_mock(marital_status_name="Single") -> MaritalStatus:
        marital_status = MaritalStatus.objects.create(name=marital_status_name)
        marital_status.save()

        return marital_status

    @staticmethod
    def create_gender_mock(gender_name="Masculino") -> Gender:
        gender_exists = Gender.objects.filter(name=gender_name).exists()
        if gender_exists:
            gender = Gender.objects.get(name=gender_name)
        else:
            gender = Gender.objects.create(name=gender_name)
            gender.save()

        return gender

    @staticmethod
    def create_survey_mock(survey_id, is_initial_evaluation) -> Survey:
        survey = Survey(
            lime_survey_id=survey_id, is_initial_evaluation=is_initial_evaluation
        )
        survey.save()

        return survey

    @staticmethod
    def create_token_id_mock(patient, survey):
        questionnaire_lime_survey = Questionnaires()
        result = questionnaire_lime_survey.add_participant(survey.lime_survey_id)
        questionnaire_lime_survey.release_session_key()

        return result["tid"]

    def create_response_survey_mock(
        self, user, patient, survey, token_id=None
    ) -> QuestionnaireResponse:
        if not token_id:
            # TODO (NES-981): maybe this is not necessary. We want just the token id.
            #  It's not necessary to really create participant in LimeSurvey
            token_id = self.create_token_id_mock(patient, survey)

        questionnaire_response = QuestionnaireResponse(
            patient=patient,
            survey=survey,
            token_id=token_id,
            questionnaire_responsible=user,
        )
        questionnaire_response.save()

        return questionnaire_response


class DirectoryTest(TestCase):
    user: User
    data: dict[str, Any] = {}

    def setUp(self):
        """Cria um participante para ser utilizado durante os testes"""
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        self.client.login(username=USER_USERNAME, password=USER_PWD)

        self.basedir = path.join(
            path.dirname(path.realpath("__file__")), "test_directory"
        )

        mkdir(self.basedir)

    def tearDown(self):
        #  delete directory and files created for testing
        rmtree(self.basedir)

    def test_directory_create(self):
        """Test if directory is created correctly"""
        path_to_create = "opt/"
        create_directory(self.basedir, path_to_create)

        self.assertTrue(path.exists(path.join(self.basedir, path_to_create)))

    def test_directory_already_exists(self):
        """Test directory creation when it already exists"""

        # in this case, nothing will change
        path_to_create = "opt/"

        mkdir(path.join(self.basedir, path_to_create))

        self.assertTrue(path.exists(path.join(self.basedir, path_to_create)))

        # call function to create an already created directory
        msg, path_created = create_directory(self.basedir, path_to_create)
        self.assertEqual(msg, "")
        self.assertEqual(path_created, path.join(self.basedir, path_to_create))

    def test_base_directory_does_not_exist(self):
        """
        Test when base directory does not exist or contains incorrect name
        """

        path_to_create = "opt/"
        path_with_error = self.basedir + "/error_path"

        msg, path_created = create_directory(path_with_error, path_to_create)

        self.assertEqual(msg, _("Base path does not exist"))


class PatientActiveTest(TestCase):
    """Cria um participante para ser utilizado durante os testes"""

    user: User
    data: dict[str, Any] = {}
    util = UtilTests()

    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        self.client.login(username=USER_USERNAME, password=USER_PWD)

    @patch("survey.abc_search_engine.Server")
    def test_active_patient(self, mockServer):
        """Test correct path - everything is ok"""

        mockServer.return_value.add_participants.return_value = [
            {
                "emailstatus": "OK",
                "sent": "N",
                "usesleft": 1,
                "lastname": "",
                "blacklisted": None,
                "token": "hXDBhg9JWC1TlTV",
                "email": "",
                "language": None,
                "remindercount": 0,
                "validuntil": None,
                "firstname": "",
                "validfrom": None,
                "completed": "N",
                "remindersent": "N",
                "tid": "4501",
                "participant_id": None,
                "mpid": None,
            }
        ]

        patient_mock = self.util.create_patient_mock(user=self.user)
        survey_mock = self.util.create_survey_mock(QUESTIONNAIRE_ID, True)
        self.util.create_response_survey_mock(self.user, patient_mock, survey_mock)

        subject_id = str(float(patient_mock.pk))

        response = is_patient_active(subject_id)
        self.assertTrue(response)

        subject_id = str(patient_mock.pk)
        response = is_patient_active(subject_id)
        self.assertTrue(response)

    def test_subject_is_not_number(self):
        """Test when subject value is incorrect"""

        subject_id = "subject_error"

        response = is_patient_active(subject_id)
        self.assertTrue(not response)

    def test_patient_not_in_questionnaire_response(self):
        """Test when subject is not in questionnaire response"""

        patient_mock = self.util.create_patient_mock(user=self.user)
        self.util.create_survey_mock(QUESTIONNAIRE_ID, True)

        subject_id = str(float(patient_mock.pk))
        response = is_patient_active(subject_id)
        self.assertTrue(not response)

    def test_patient_removed_from_database(self):
        """Test when patient is removed"""

        patient_mock = self.util.create_patient_mock(user=self.user)
        patient_mock.removed = True
        patient_mock.save()

        survey_mock = self.util.create_survey_mock(QUESTIONNAIRE_ID, True)
        self.util.create_response_survey_mock(
            self.user, patient_mock, survey_mock, token_id=1
        )

        subject_id = str(float(patient_mock.pk))
        response = is_patient_active(subject_id)
        self.assertTrue(not response)


class JsonTest(TestCase):
    """Cria um participante para ser utilizado durante os testes"""

    user = ""
    data: dict[str, Any] = {}

    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

    @staticmethod
    def test_explanation_fields():
        questionnaire_lime_survey = Questionnaires()
        questionnaire_lime_survey.release_session_key()


class InputExportTest(TestCase):
    """Cria um participante para ser utilizado durante os testes"""

    user = ""
    data: dict[str, Any] = {}
    util = UtilTests()

    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

    @patch("survey.abc_search_engine.Server")
    def test_write_dynamic_json(self, mockServer):
        mockServer.return_value.get_survey_properties.return_value = {
            "language": "pt-BR",
            "additional_languages": "en",
        }
        input_data = InputExport()

        self.assertEqual(len(input_data.data), 0)

        input_data.build_header(export_per_experiment=False)

        self.assertEqual(len(input_data.data), 5)
        input_data.build_dynamic_header("export_per_participant", 1)

        self.assertEqual(len(input_data.data), 6)

        participant_field_header_list = [("id", "id"), ("name", "name")]

        self.assertNotIn("participants", input_data.data)

        input_data.build_diagnosis_participant(
            "participants", "Participants", participant_field_header_list
        )

        self.assertIn("participants", input_data.data)

        questionnaire_list = [
            (0, 286684, "title", [("header1", "field1")]),
        ]

        self.assertNotIn("questionnaires", input_data.data)

        input_data.build_questionnaire(
            questionnaire_list, "pt-BR", entrance_questionnaire=True
        )

        self.assertIn("questionnaires", input_data.data)

    @patch("survey.abc_search_engine.Server")
    def test_create_dynamic_json(self, mockServer):
        mockServer.return_value.get_survey_properties.return_value = {
            "language": "pt-BR",
            "additional_languages": "en",
        }

        participant_field_header_list = [("id", "id"), ("name", "name")]

        questionnaires_list = [
            (0, 271192, "title", [("header1", "field1")]),
        ]

        diagnosis_field_header_list = ""

        output_filename = path.join(settings.MEDIA_ROOT, "export/test123.json")

        if path.isfile(output_filename):
            remove(output_filename)

        self.assertTrue(not path.isfile(output_filename))

        os.makedirs(path.join(settings.MEDIA_ROOT, "export"), exist_ok=True)
        experiment_questionnaires_list = []
        component_list = []
        build_complete_export_structure(
            0,
            1,
            0,
            participant_field_header_list,
            diagnosis_field_header_list,
            questionnaires_list,
            experiment_questionnaires_list,
            ["short"],
            "full",
            output_filename,
            component_list,
            "pt-BR",
            "tsv",
        )

        self.assertTrue(path.isfile(output_filename))

        remove(output_filename)
        experiment_questionnaires_list = []
        build_complete_export_structure(
            1,
            0,
            0,
            participant_field_header_list,
            diagnosis_field_header_list,
            questionnaires_list,
            experiment_questionnaires_list,
            ["short", "long"],
            "full",
            output_filename,
            component_list,
            "en",
            "csv",
        )

        self.assertTrue(path.isfile(output_filename))
        remove(output_filename)


class AdvancedSearchTest(TestCase):
    """Cria um participante para ser utilizado durante os testes"""

    user = ""
    data: dict[str, Any] = {}
    util = UtilTests()

    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)
        self.data: dict[str, Any] = {}

    def create_initial_patients_data(self):
        female_list = [1, 2, 4]

        delta = 1
        for index in range(6):
            if index in female_list:
                gender_name = "Female"
            else:
                gender_name = "Male"

            birthday = datetime.now() - relativedelta(years=delta)
            date_birth = "%s-%s-%s" % (birthday.year, birthday.month, birthday.day)
            self.util.create_patient_mock(
                name=self._testMethodName + str(index),
                user=self.user,
                gender_name=gender_name,
                date_birth=date_birth,
            )
            delta += 5

        for marital_status_name in marital_status_list:
            self.util.create_marital_status_mock(marital_status_name)

        for index in range(6):
            patient = Patient.objects.get(name=self._testMethodName + str(index))
            marital_status_id = int(index / 2.5)
            marital_status = MaritalStatus.objects.get(
                name=marital_status_list[marital_status_id]
            )
            patient.marital_status = marital_status
            patient.save()

    def test_filter_all_participants(self):
        for index in range(3):
            self.util.create_patient_mock(
                name=self._testMethodName + str(index), user=self.user
            )

        response = self.client.get(reverse("filter_participants"))
        self.assertEqual(response.status_code, 200)

        self.data["action"] = "next-step-1"
        self.data["type_of_selection_radio"] = "all"
        response = self.client.post(reverse("filter_participants"), self.data)
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            len(response.wsgi_request.session["filtered_participant_data"]),
            Patient.objects.count(),
        )

    def test_filter_gender_participants(self):
        self.create_initial_patients_data()

        self.data["action"] = "next-step-1"
        self.data["type_of_selection_radio"] = "selected"
        self.data["gender_checkbox"] = True

        gender_list = Gender.objects.filter(name="Female").values_list("id")
        gender_list = [data[0] for data in gender_list]
        self.data["gender"] = gender_list

        response = self.client.post(reverse("filter_participants"), self.data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.wsgi_request.session["filtered_participant_data"]),
            Patient.objects.filter(gender__name="Female").count(),
        )

    def test_filter_age_participants(self) -> None:
        self.create_initial_patients_data()

        self.data["action"] = "next-step-1"
        self.data["type_of_selection_radio"] = "selected"
        self.data["age_checkbox"] = True

        self.data["min_age"] = 5
        self.data["max_age"] = 17

        response = self.client.post(reverse("filter_participants"), self.data)
        self.assertEqual(response.status_code, 200)

        birthday_min = datetime.now() - relativedelta(years=5)
        birthday_max = datetime.now() - relativedelta(years=17)

        date_birth_min = "%s-%s-%s" % (
            birthday_min.year,
            birthday_min.month,
            birthday_min.day,
        )
        date_birth_max = "%s-%s-%s" % (
            birthday_max.year,
            birthday_max.month,
            birthday_max.day,
        )

        self.assertEqual(
            len(response.wsgi_request.session["filtered_participant_data"]), 3
        )

    def test_filter_marital_status_participants(self):
        self.create_initial_patients_data()

        self.data["action"] = "next-step-1"
        self.data["type_of_selection_radio"] = "selected"
        self.data["marital_status_checkbox"] = True

        marital_list = MaritalStatus.objects.filter(name="Married").values_list("id")
        marital_list = [data[0] for data in marital_list]

        self.data["marital_status"] = marital_list

        response = self.client.post(reverse("filter_participants"), self.data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            len(response.wsgi_request.session["filtered_participant_data"]),
            Patient.objects.filter(marital_status__name="Married").count(),
        )

    def test_second_page(self):
        self.data["action"] = "previous-step-2"
        response = self.client.post(reverse("filter_participants"), self.data)
        self.assertEqual(response.status_code, 200)

        self.data["action"] = "next-step-2"
        response = self.client.post(reverse("filter_participants"), self.data)
        self.assertEqual(response.status_code, 302)
