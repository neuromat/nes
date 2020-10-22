from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .tests_orig import QuestionnaireFormValidation, UtilTests
from ..models import QuestionnaireResponse

USERNAME = 'joaopedro'
PASSWD = 'password'


class QuestionnaireFillTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username=USERNAME, email='test@dummy.com', password=PASSWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        logged = self.client.login(username=USERNAME, password=PASSWD)
        self.assertEqual(logged, True)

    @patch('survey.abc_search_engine.Server')
    def test_create_entrance_evaluation_response_does_not_display_fill_date_input_field(
            self, mockServer):
        # NES-981 Setting default mocks just passed the test. Not sure if mocks
        # are overloaded
        QuestionnaireFormValidation._set_mocks(mockServer)

        patient = UtilTests.create_patient(self.user)
        survey = UtilTests.create_survey(212121, True)

        data = {
            'date': '01/09/2014', 'action': 'save',
            'initial-date': '2015-09-02'
        }

        url = reverse(
            'questionnaire_response_create', args=(patient.pk, survey.pk,))
        response = self.client.post(
            url + "?origin=subject", data, follow=True)
        self.assertEqual(
            response.context[
                'questionnaire_response_form'
            ].fields['date'].hidden_widget.input_type, 'hidden')
        self.assertNotContains(response, 'Data de preenchimento')

    @patch('survey.abc_search_engine.Server')
    def test_create_entrance_evalution_response_build_limesurvey_url_with_correct_date_format(
            self, mockServer):
        patient = UtilTests.create_patient(self.user)
        survey = UtilTests.create_survey(212121, True)

        for lang in ['en', 'pt_BR']:
            QuestionnaireFormValidation._set_mocks(mockServer)

            mockServer.return_value.get_summary.return_value = 1
            mockServer.return_value.get_survey_properties.side_effect = \
                [{'active': True}, {'language': lang}, {'language': lang}]

            date = '01/09/2014'
            date_limesurvey = '09-01-2014' if lang == 'en' else '01-09-2014'
            data = {
                'date': date, 'action': 'save',
                'initial-date': '2015-09-02'
            }

            url = reverse(
                'questionnaire_response_create', args=(patient.pk, survey.pk,))
            response = self.client.post(
                url + "?origin=subject", data, follow=True)

            self.assertIn(date_limesurvey, response.context['URL'])

    @patch('survey.abc_search_engine.Server')
    def test_view_questionnaires_updates_response_date_for_completed_fills(
            self, mockServer):
        mockServer.return_value.get_participant_properties.return_value = \
            {'token': 'abc', 'completed': '2018-05-15 15:51'}
        # 2019-01-03 00:00:00
        mockServer.return_value.export_responses_by_token.return_value = \
            'ImFjcXVpc2l0aW9uZGF0ZSIKIjIwMTktMDEtMDMgMDA6MDA6MDAi'

        patient = UtilTests.create_patient(self.user)
        survey = UtilTests.create_survey(212121, True)
        UtilTests.create_response_survey(self.user, patient, survey, 1)

        self.client.get(reverse('patient_edit', args=(patient.pk,)), data={
            'currentTab': 4
        })

        questionnaire_response = QuestionnaireResponse.objects.first()

        self.assertEqual(
            questionnaire_response.date.strftime('%Y-%m-%d'), '2019-01-03')

    @patch('survey.abc_search_engine.Server')
    def test_view_questionnaires_updates_response_date_add_updated_key_to_context(
            self, mockServer):
        mockServer.return_value.get_participant_properties.return_value = \
            {'token': 'abc', 'completed': '2018-05-15 15:51'}
        # 2019-01-03 00:00:00
        mockServer.return_value.export_responses_by_token.return_value = \
            'ImFjcXVpc2l0aW9uZGF0ZSIKIjIwMTktMDEtMDMgMDA6MDA6MDAi'

        patient = UtilTests.create_patient(self.user)
        survey = UtilTests.create_survey(212121, True)
        UtilTests.create_response_survey(self.user, patient, survey, 1)

        response = self.client.get(
            reverse('patient_edit', args=(patient.pk,)),
            data={'currentTab': 4})

        self.assertTrue(response.context[
                            'patient_questionnaires_data_list'
                        ][0]['questionnaire_responses'][0][
                            'acquisitiondate_updated'
                        ])

    @patch('survey.abc_search_engine.Server')
    def test_view_questionnaires_updates_response_date_display_tag_updated_in_template(
            self, mockServer):
        mockServer.return_value.get_participant_properties.return_value = \
            {'token': 'abc', 'completed': '2018-05-15 15:51'}
        # 2019-01-03 00:00:00
        mockServer.return_value.export_responses_by_token.return_value = \
            'ImFjcXVpc2l0aW9uZGF0ZSIKIjIwMTktMDEtMDMgMDA6MDA6MDAi'

        patient = UtilTests.create_patient(self.user)
        survey = UtilTests.create_survey(212121, True)
        UtilTests.create_response_survey(self.user, patient, survey, 1)

        response = self.client.get(
            reverse('patient_edit', args=(patient.pk,)),
            data={'currentTab': 4})

        self.assertContains(response, 'Atualizado', 1)
        self.assertRegex(str(response.content), 'class=.+blink')
