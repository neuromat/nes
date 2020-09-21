from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .tests_orig import QuestionnaireFormValidation, UtilTests

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
    def test_entrance_evaluation_response_create_does_not_display_fill_date_input_field(
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
