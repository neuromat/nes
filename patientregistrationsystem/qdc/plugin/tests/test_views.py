import csv
import os
import re
import shutil
import tempfile
import zipfile
from unittest import skip
from unittest.mock import patch

from django.conf import settings
from django.contrib.messages import get_messages
from django.core.urlresolvers import reverse, resolve
from django.utils.translation import ugettext_lazy as _
from django.test import override_settings

from export import input_export
from export.models import Export
from export.tests.tests_helper import ExportTestCase
from plugin.models import RandomForests
from plugin.tests.LimeSurveyAPI_mocks import set_limesurvey_api_mocks, update_limesurvey_api_mocks, \
    set_limesurvey_api_mocks2
from plugin.views import send_to_plugin
from patient.tests.tests_orig import UtilTests
from survey.models import Survey
from survey.tests.tests_helper import create_survey

TEMP_MEDIA_ROOT = tempfile.mkdtemp()


class PluginTest(ExportTestCase):

    def setUp(self):
        super(PluginTest, self).setUp()

    def tearDown(self):
        self.client.logout()

    def _create_basic_objects(self):
        self.survey1 = create_survey()
        # Specify the survey code for matching with mocks.
        # In code, export.process_per_participant sorts surveys by survey code, already.
        # for matching the mocks. See comment in export.process_per_participant method.
        self.survey1.code = 'Q212121'
        self.survey1.save()
        self.survey2 = create_survey(505050)
        self.survey2.code = 'Q505050'
        self.survey2.save()
        self.survey3 = create_survey(717171)
        self.survey3.code = 'Q717171'
        self.survey3.save()
        RandomForests.objects.create(
            admission_assessment=self.survey1,
            surgical_evaluation=self.survey2,
            followup_assessment=self.survey3,
            plugin_url='http://plugin_url')
        UtilTests.create_response_survey(
            self.user, self.patient, self.survey1, 21)
        UtilTests.create_response_survey(
            self.user, self.patient, self.survey2, 21)
        UtilTests.create_response_survey(
            self.user, self.patient, self.survey3, 21)

    def test_GET_send_to_plugin_returns_right_status_code(self):
        response = self.client.get(reverse('send-to-plugin'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'plugin/send_to_plugin.html')

    def test_root_url_resolves_send_to_plugin_view(self):
        view = resolve('/plugin/')
        self.assertEquals(view.func, send_to_plugin)

    def test_GET_send_to_plugin_display_questionnaire_names_in_interface_in_current_language_or_display_message1(
            self):
        """Current language is pt-BR"""

        self._create_basic_objects()
        random_forest = RandomForests.objects.get()
        random_forest.admission_assessment.pt_title = None
        random_forest.admission_assessment.save()
        random_forest.surgical_evaluation.pt_title = None
        random_forest.surgical_evaluation.save()
        random_forest.followup_assessment.pt_title = None
        random_forest.followup_assessment.save()

        response = self.client.get(reverse('send-to-plugin'))
        self.assertContains(
            response, 'Título do Questionário Avaliação de Entrada não '
                      'disponível em pt-BR')
        self.assertContains(
            response, 'Título do Questionário Avaliação Cirúrgica não '
                      'disponível em pt-BR')
        self.assertContains(
            response, 'Título do Questionário Avaliação de Seguimento não '
                      'disponível em pt-BR')

    @override_settings(LANGUAGE_CODE='en')
    def test_GET_send_to_plugin_display_questionnaire_names_in_interface_in_current_language_or_display_message2(
            self):
        """Current language is en"""

        self._create_basic_objects()
        random_forest = RandomForests.objects.get()
        random_forest.admission_assessment.en_title = None
        random_forest.admission_assessment.save()
        random_forest.surgical_evaluation.en_title = None
        random_forest.surgical_evaluation.save()
        random_forest.followup_assessment.en_title = None
        random_forest.followup_assessment.save()

        response = self.client.get(reverse('send-to-plugin'))
        self.assertContains(response, 'Questionnaire title for Unified Admission Assessment not available in en')
        self.assertContains(response, 'Questionnaire title for Surgical Assessment not available in en')

    def test_does_not_define_admission_questionnaire_attribute_does_not_display_plugin_entry_in_menu(self):
        self._create_basic_objects()

        plugin = RandomForests.objects.last()
        plugin.admission_assessment = None
        plugin.save()

        response = self.client.get('home')
        self.assertNotIn('Plugin', response.content.decode('utf-8'),
                         'Plugin appears')

    def test_does_not_define_surgical_questionnaire_attribute_does_not_display_plugin_entry_in_menu(self):
        self._create_basic_objects()

        plugin = RandomForests.objects.last()
        plugin.surgical_evaluation = None
        plugin.save()

        response = self.client.get('home')
        self.assertNotIn('Plugin', response.content.decode('utf-8'),
                         'Plugin appears')

    def test_does_not_define_followup_questionnaire_attribute_does_not_display_plugin_entry_in_menu(self):
        self._create_basic_objects()

        plugin = RandomForests.objects.last()
        plugin.followup_assessment = None
        plugin.save()

        response = self.client.get('home')
        self.assertNotIn('Plugin', response.content.decode('utf-8'),
                         'Plugin appears')

    def test_does_not_define_plugin_url_attribute_does_not_display_plugin_entry_in_menu(self):
        self._create_basic_objects()

        plugin = RandomForests.objects.last()
        plugin.plugin_url = ''
        plugin.save()

        response = self.client.get('home')
        self.assertNotIn('Plugin', response.content.decode('utf-8'),
                         'Plugin appears')

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_group_selected_list_in_request_session_removes_session_key(self, mockServer):
        # Simulate 'group_selected_list' already in request session when
        # sending to Plugin in Per Participant way
        self.append_session_variable('group_selected_list', 21)

        set_limesurvey_api_mocks(mockServer)
        self._create_basic_objects()

        self.client.post(
            reverse('send-to-plugin'),
            data={
                'headings': ['code'],
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })

        self.assertIsNone(self.client.session.get('group_selected_list', None))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_creates_zip_file(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        patient2 = UtilTests.create_patient(self.user)
        for survey in Survey.objects.all():
            UtilTests.create_response_survey(self.user, patient2, survey, 50)
        # Update mocks for calling the two patients
        update_limesurvey_api_mocks(mockServer)

        self.client.post(
            reverse('send-to-plugin'),
            data={
                'headings': ['code'],
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id), str(patient2.id)]
            })

        export = Export.objects.last()
        with open(os.path.join(
                settings.MEDIA_ROOT, 'export', str(self.user.id), str(export.id), 'export.zip'), 'rb') as file:
            zipped_file = zipfile.ZipFile(file, 'r')
            self.assertIsNone(zipped_file.testzip())
            zipped_file.close()

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_returns_zip_file_with_only_data_from_participants_selected(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        # Reset get_participants_properties to deal with only one participant
        # selected
        mockServer.return_value.get_participant_properties.side_effect = [
            {'token': 'sIbj3gwjvwpa2QY'}, {'token': 'OSSMaFVewVl8D0J'},
            {'token': 'OSSMaFVewVl8D0J'}, {'token': 'fFPnTsNUJwRye3g'},
            {'token': 'fFPnTsNUJwRye3g'}, {'token': 'fFPnTsNUJwRye3g'},
        ]

        self._create_basic_objects()
        patient2 = UtilTests.create_patient(self.user)
        for survey in Survey.objects.all():
            UtilTests.create_response_survey(self.user, patient2, survey, 50)
        self.client.post(
            reverse('send-to-plugin'),
            data={
                'headings': ['code'],
                # TODO (NES-963): about 'patient_selected see TODO (NES-963) in export.views
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)],
            })

        export = Export.objects.last()
        with open(os.path.join(
                settings.MEDIA_ROOT, 'export', str(self.user.id), str(export.id), 'export.zip'), 'rb') as file:
            zipped_file = zipfile.ZipFile(file, 'r')
            self.assertIsNone(zipped_file.testzip())
            # Tests for Per_participant subdir
            list_items = zipped_file.namelist()
            in_items = re.compile(input_export.BASE_DIRECTORY + '/Per_participant/Participant_%s' % self.patient.code)
            in_items = [in_items.match(item) for item in list_items]
            in_items = [item for item in in_items if item is not None]
            self.assertEqual(3, len(in_items))
            out_items = re.compile('data/Per_participant/Participant_%s' % patient2.code)
            out_items = [out_items.match(item) for item in list_items]
            out_items = [item for item in out_items if item is not None]
            self.assertEqual(0, len(out_items))

            # Tests for Per_questionnaire subdir
            questionnaire1 = zipped_file.extract(
                input_export.BASE_DIRECTORY +
                '/Per_questionnaire/QA_unified_admission_assessment/Responses_QA_en.csv',
                TEMP_MEDIA_ROOT)
            with open(questionnaire1) as q1_file:
                reader = list(csv.reader(q1_file))
                self.assertEqual(2, len(reader))
                self.assertEqual(self.patient.code, reader[1][0])
            questionnaire2 = zipped_file.extract(
                input_export.BASE_DIRECTORY +
                '/Per_questionnaire/QS_surgical_evaluation/Responses_QS_en.csv',
                TEMP_MEDIA_ROOT)
            with open(questionnaire2) as q3_file:
                reader = list(csv.reader(q3_file))
                self.assertEqual(2, len(reader))
                self.assertEqual(self.patient.code, reader[1][0])
            questionnaire3 = zipped_file.extract(
                input_export.BASE_DIRECTORY +
                '/Per_questionnaire/QF_unified_followup_assessment/Responses_QF_en.csv',
                TEMP_MEDIA_ROOT)
            with open(questionnaire3) as q3_file:
                reader = list(csv.reader(q3_file))
                self.assertEqual(2, len(reader))
                self.assertEqual(self.patient.code, reader[1][0])

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_adds_plugin_url_session_key_and_redirect_to_send_to_plugin_view(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'headings': ['code'],
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })

        export = Export.objects.last()
        plugin = RandomForests.objects.last()
        plugin_url = plugin.plugin_url + '?user_id=' + str(self.user.id) + '&export_id=' + str(export.id)
        self.assertEqual(self.client.session.get('plugin_url'), plugin_url)
        self.assertRedirects(response, reverse('send-to-plugin'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_redirect_to_send_to_plugin_view_with_right_context(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'headings': ['code'],
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            }, follow=True)
        self.assertEqual(response.status_code, 200)

        export = Export.objects.last()
        plugin_url = 'http://plugin_url?user_id=' + str(self.user.id) + '&export_id=' + str(export.id)
        self.assertEqual(response.context['plugin_url'], plugin_url)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_redirect_to_send_to_plugin_view_and_remove_plugin_url_key_from_session(
            self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        self.client.post(
            reverse('send-to-plugin'),
            data={
                'headings': ['code'],
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            }, follow=True)

        self.assertIsNone(self.client.session.get('plugin_url'), None)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    @patch('plugin.views.build_zip_file')
    def test_POST_send_to_plugin_does_not_build_zip_file_display_error_message(self, mock_build_zip_file, mockServer, ):
        set_limesurvey_api_mocks(mockServer)
        # Simulate an empty file path to represent that zip file was not created
        mock_build_zip_file.return_value = 0, ''

        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            }, follow=True)

        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _('Could not open zip file to send to Forest Plugin'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_display_success_message(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'headings': ['code'],
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            }, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _('Data from questionnaires was sent to Forest Plugin'))

    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_does_not_select_any_attribute_display_warning_message(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': [],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _('Please select at least Gender participant attribute'))

    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_does_not_select_any_patient_display_warning_message(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age'],
                'patients_selected[]': []
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _('Please select at least one patient'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_does_not_select_patient_gender_display_warning_message(self, mockServer):
        set_limesurvey_api_mocks(mockServer)

        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _('The Floresta Plugin needs to send at least Gender attribute'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_write_files_and_dirs_the_right_way_and_always_in_english(self, mockServer):
        set_limesurvey_api_mocks2(mockServer)

        self._create_basic_objects()
        self.client.post(
            reverse('send-to-plugin'),
            data={
                'headings': ['code'],
                'opt_floresta': ['on'],
                'patient_selected': ['gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        export = Export.objects.last()
        with open(os.path.join(
                settings.MEDIA_ROOT, 'export', str(self.user.id),
                str(export.id), 'export.zip'), 'rb') as file:
            zip_file = zipfile.ZipFile(file, 'r')
            self.assertIsNone(zip_file.testzip())
            self.assertTrue(
                any(os.path.join(
                    'data/Per_questionnaire',
                    'QA_unified_admission_assessment', 'Responses_QA_en.csv')
                    in element for element in zip_file.namelist()),
                os.path.join(
                    'data/Per_questionnaire',
                    'QA_unified_admission_assessment', 'Responses_QA_en.csv')
                + ' not in: ' + str(zip_file.namelist()))
            self.assertTrue(
                any(os.path.join(
                    'data/Per_questionnaire', 'QS_surgical_evaluation',
                    'Responses_QS_en.csv')
                    in element for element in zip_file.namelist()),
                os.path.join('data/Per_questionnaire',
                             'QS_surgical_evaluation', 'Responses_QS_en.csv')
                + ' not in: ' + str(zip_file.namelist()))
            self.assertTrue(
                any(os.path.join(
                    'data/Per_questionnaire',
                    'QF_unified_followup_assessment', 'Responses_QF_en.csv')
                    in element for element in zip_file.namelist()),
                os.path.join('data/Per_questionnaire',
                             'QF_unified_followup_assessment',
                             'Responses_QF_en.csv')
                + ' not in: ' + str(zip_file.namelist()))

            self.assertTrue(
                any(os.path.join(
                    'data/Per_participant',
                    'Participant_' + self.patient.code,
                    'QA_unified_admission_assessment',
                    'Responses_QA_en.csv')
                    in element for element in zip_file.namelist()),
                os.path.join(
                    'data/Per_participant', 
                    'Participant_' + self.patient.code,
                    'QA_unified_admission_assessment',
                    'Responses_QA_en.csv')
                + ' not in: ' + str(zip_file.namelist()))
            self.assertTrue(
                any(os.path.join(
                    'data/Per_participant',
                    'Participant_' + self.patient.code,
                    'QS_surgical_evaluation',
                    'Responses_QS_en.csv')
                    in element for element in zip_file.namelist()),
                os.path.join(
                    'data/Per_participant',
                    'Participant_' + self.patient.code,
                    'QS_surgical_evaluation',
                    'Responses_QS_en.csv')
                + ' not in: ' + str(zip_file.namelist()))
            self.assertTrue(
                any(os.path.join(
                    'data/Per_participant',
                    'Participant_' + self.patient.code,
                    'QF_unified_followup_assessment',
                    'Responses_QF_en.csv')
                    in element for element in zip_file.namelist()),
                os.path.join(
                    'data/Per_participant',
                    'Participant_' + self.patient.code,
                    'QF_unified_followup_assessment',
                    'Responses_QF_en.csv')
                + ' not in: ' + str(zip_file.namelist()))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_make_subdirs_questionnaire_titles_in_english(self, mockServer):
        pass

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_write_csv_participant_data_in_english(self, mockServer):
        pass

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_get_error_in_consuming_limesurvey_api_returns_error_message1(self, mockServer):
        set_limesurvey_api_mocks(mockServer)
        # Could not get session key
        mockServer.return_value.get_session_key.return_value = {'status': 'Invalid user name or password'}
        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _(
            'Error: some thing went wrong consuming LimeSurvey API. Please try again. If '
            'problem persists please contact System Administrator.'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_get_error_in_consuming_limesurvey_api_returns_error_message2(self, mockServer):
        set_limesurvey_api_mocks(mockServer)
        # Could not get survey properties
        mockServer.return_value.get_survey_properties.return_value = {'status': 'Error: Invalid survey ID'}
        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _(
            'Error: some thing went wrong consuming LimeSurvey API. Please try again. If '
            'problem persists please contact System Administrator.'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_get_error_in_consuming_limesurvey_api_returns_error_message3(self, mockServer):
        set_limesurvey_api_mocks(mockServer)
        # Could not get responses
        mockServer.return_value.export_responses.side_effect = 2*[{'status': 'No Data, survey table does not exist.'}]
        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _(
            'Error: some thing went wrong consuming LimeSurvey API. Please try again. If '
            'problem persists please contact System Administrator.'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_get_error_in_consuming_limesurvey_api_returns_error_message4(self, mockServer):
        set_limesurvey_api_mocks(mockServer)
        # Could not get responses by token
        mockServer.return_value.export_responses_by_token.side_effect = \
            4 * [{'status': 'No Data, survey table does not exist.'}]
        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _(
            'Error: some thing went wrong consuming LimeSurvey API. Please try again. If '
            'problem persists please contact System Administrator.'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_get_error_in_consuming_limesurvey_api_returns_error_message5(self, mockServer):
        set_limesurvey_api_mocks(mockServer)
        # Could not list groups
        mockServer.return_value.list_groups.side_effect = 8 * [{'status': 'No groups found'}]
        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _(
            'Error: some thing went wrong consuming LimeSurvey API. Please try again. If '
            'problem persists please contact System Administrator.'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_get_error_in_consuming_limesurvey_api_returns_error_message6(self, mockServer):
        set_limesurvey_api_mocks(mockServer)
        # Could not list questions
        mockServer.return_value.list_questions.side_effect = 6 * [{'status': 'No questions found'}]
        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _(
            'Error: some thing went wrong consuming LimeSurvey API. Please try again. If '
            'problem persists please contact System Administrator.'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_get_error_in_consuming_limesurvey_api_returns_error_message7(self, mockServer):
        set_limesurvey_api_mocks(mockServer)
        # Could not get question properties
        mockServer.return_value.get_question_properties.side_effect = 4 * [{'status': 'Error: Invalid questionid'}]
        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _(
            'Error: some thing went wrong consuming LimeSurvey API. Please try again. If '
            'problem persists please contact System Administrator.'))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_get_error_in_consuming_limesurvey_api_returns_error_message8(self, mockServer):
        set_limesurvey_api_mocks(mockServer)
        # Could not get participant properties
        mockServer.return_value.get_participant_properties.side_effect = 6 * [{'status': 'Error: No token table'}]
        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _(
            'Error: some thing went wrong consuming LimeSurvey API. Please try again. If '
            'problem persists please contact System Administrator.'))

    @skip  # get_language_properties already deal with errors returned by LimeSurvey
    def test_POST_send_to_plugin_get_error_in_consuming_limesurvey_api_returns_error_message9(self, mockServer):
        set_limesurvey_api_mocks(mockServer)
        # Could not get language properties
        mockServer.return_value.get_language_properties.side_effect = 4 * [{'status': 'No valid Data'}]
        self._create_basic_objects()
        response = self.client.post(
            reverse('send-to-plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age', 'gender__name*gender'],
                'patients_selected[]': [str(self.patient.id)]
            })
        self.assertRedirects(response, reverse('send-to-plugin'))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, _(
            'Error: some thing went wrong consuming LimeSurvey API. Please try again. If '
            'problem persists please contact System Administrator.'))


def tearDownModule():
    shutil.rmtree(TEMP_MEDIA_ROOT)
