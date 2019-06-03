import csv
import io
import re
import shutil
import tempfile
import zipfile
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse, resolve
from django.test import override_settings
from django.utils.encoding import smart_str

from export.tests.tests_helper import ExportTestCase
from plugin.models import RandomForests
from plugin.tests.LimeSurveyAPI_mocks import set_limesurvey_api_mocks
from plugin.views import send_to_plugin
from patient.tests.tests_orig import UtilTests
from survey.models import Survey
from survey.tests.tests_helper import create_survey


class PluginTest(ExportTestCase):
    TEMP_MEDIA_ROOT = tempfile.mkdtemp()

    def setUp(self):
        super(PluginTest, self).setUp()

    def tearDown(self):
        self.client.logout()

    def _create_basic_objects(self):
        survey1 = create_survey()
        survey2 = create_survey(505050)
        RandomForests.objects.create(admission_assessment=survey1, surgical_evaluation=survey2)
        UtilTests.create_response_survey(self.user, self.patient, survey1, 21)
        UtilTests.create_response_survey(self.user, self.patient, survey2, 21)

    def test_send_to_plugin_status_code(self):
        response = self.client.get(reverse('send_to_plugin'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'plugin/send_to_plugin.html')

    def test_animal_new_url_resolves_animal_new_view(self):
        view = resolve('/plugin/')
        self.assertEquals(view.func, send_to_plugin)

    def test_GET_send_to_plugin_display_questionnaire_names_in_interface(self):
        self._create_basic_objects()
        response = self.client.get(reverse('send_to_plugin'))
        for survey in Survey.objects.all():
            self.assertContains(response, survey.pt_title)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_returns_zip_file(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        patient2 = UtilTests.create_patient(self.user)
        for survey in Survey.objects.all():
            UtilTests.create_response_survey(self.user, patient2, survey, 50)
        response = self.client.post(
            reverse('send_to_plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id), str(patient2.id)]
            })
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.get('Content-Disposition'), 'attachment; filename="%s"' % smart_str('export.zip'))
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())
        zipped_file.close()

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_returns_zip_file_with_only_data_from_participants_selected(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        # Reset get_participants_properties to deal with only one participant
        # selected
        mockServer.return_value.get_participant_properties.side_effect = [
            {'token': 'sIbj3gwjvwpa2QY'}, {'token': 'OSSMaFVewVl8D0J'},
            {'token': 'WRFUAgTemzuu8nD'}, {'token': 'fFPnTsNUJwRye3g'}
        ]

        self._create_basic_objects()
        patient2 = UtilTests.create_patient(self.user)
        for survey in Survey.objects.all():
            UtilTests.create_response_survey(self.user, patient2, survey, 50)
        response = self.client.post(
            reverse('send_to_plugin'),
            data={
                # TODO (NES-963): about 'patient_selected see TODO (NES-963) in export.views
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)],
            })
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.get('Content-Disposition'), 'attachment; filename="%s"' % smart_str('export.zip'))
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())
        # Tests for Per_participant subdir
        list_items = zipped_file.namelist()
        in_items = re.compile('NES_EXPORT/Per_participant/Participant_%s' % self.patient.code)
        in_items = [in_items.match(item) for item in list_items]
        in_items = [item for item in in_items if item is not None]
        self.assertEqual(2, len(in_items))
        out_items = re.compile('NES_EXPORT/Per_participant/Participant_%s' % patient2.code)
        out_items = [out_items.match(item) for item in list_items]
        out_items = [item for item in out_items if item is not None]
        self.assertEqual(0, len(out_items))

        # Tests for Per_questionnaire subdir
        questionnaire1 = zipped_file.extract(
            'NES_EXPORT/Per_questionnaire/212121_admission-assessment-plugin/Responses_212121_en.csv',
            self.TEMP_MEDIA_ROOT)
        with open(questionnaire1) as file:
            reader = list(csv.reader(file))
            self.assertEqual(2, len(reader))
            self.assertEqual(self.patient.code, reader[1][0])
        questionnaire2 = zipped_file.extract(
            'NES_EXPORT/Per_questionnaire/505050_surgical-evaluation-plugin/Responses_505050_en.csv',
            self.TEMP_MEDIA_ROOT)
        with open(questionnaire2) as file:
            reader = list(csv.reader(file))
            self.assertEqual(2, len(reader))
            self.assertEqual(self.patient.code, reader[1][0])

        zipped_file.close()

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_does_not_select_any_attribute_display_warning_message(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        response = self.client.post(
            reverse('send_to_plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': [],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send_to_plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Please select at least Gender participant attribute')

    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_does_not_select_any_patient_display_warning_message(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        response = self.client.post(
            reverse('send_to_plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age'],
                'patients_selected[]': []
            })
        self.assertRedirects(response, reverse('send_to_plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Please select at least one patient')

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_does_not_patient_gender_display_warning_message(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        response = self.client.post(
            reverse('send_to_plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send_to_plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'The Floresta Plugin needs to send at least Gender attribute')

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_get_error_in_consuming_limesurvey_api_returns_error_message1(self, mockServer):
        set_limesurvey_api_mocks(mockServer)
        # Could not get session key
        mockServer.return_value.get_session_key.return_value = {'status': 'Invalid user name or password'}
        self._create_basic_objects()
        response = self.client.post(
            reverse('send_to_plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send_to_plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Error: some thing went wrong consuming LimeSurvey API. Please try again. If '
                                  'problem persists please contact System Administrator.')

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_get_error_in_consuming_limesurvey_api_returns_error_message2(self, mockServer):
        set_limesurvey_api_mocks(mockServer)
        # Could not get survey properties
        mockServer.return_value.get_survey_properties.return_value = {'status': 'Error: Invalid survey ID'}
        self._create_basic_objects()
        response = self.client.post(
            reverse('send_to_plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send_to_plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Error: some thing went wrong consuming LimeSurvey API. Please try again. If '
                                  'problem persists please contact System Administrator.')

        shutil.rmtree(self.TEMP_MEDIA_ROOT)
