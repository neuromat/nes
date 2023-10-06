from base64 import b64decode
from unittest.mock import patch

from custom_user.tests.tests_helper import create_user
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.urls import reverse
from experiment.models import (
    Block,
    Component,
    ComponentConfiguration,
    DataConfigurationTree,
    Experiment,
    Questionnaire,
    QuestionnaireResponse,
    ResearchProject,
    Subject,
    SubjectOfGroup,
)
from experiment.tests.tests_helper import ObjectsFactory
from patient.models import QuestionnaireResponse as PatientQuestionnaireResponse
from patient.tests.tests_orig import UtilTests
from survey.abc_search_engine import Questionnaires
from survey.models import Survey
from survey.tests.tests_helper import create_survey
from survey.views import survey_update, update_acquisitiondate

USER_USERNAME = "myadmin"
USER_PWD = "mypassword"

LIME_SURVEY_ID = 828636
LIME_SURVEY_TOKEN_ID_1 = 1


# TODO (NES-981): This class run integration tests. Separate in a file/dir for integraion tests.
#  Integration tests are to run separated from unit tests and to less often
# class ABCSearchEngineTest(TestCase):
#     session_key = None
#     server = None
#
#     def setUp(self):
#
#         self.server = Server(settings.LIMESURVEY['URL_API'] + '/index.php/admin/remotecontrol')
#
#         try:
#             self.session_key = self.server.get_session_key(settings.LIMESURVEY['USER'], settings.LIMESURVEY['PASSWORD'])
#             self.session_key = None if isinstance(self.session_key, dict) else self.session_key
#         except TransportError:
#             self.session_key = None
#
#     def test_complete_survey(self):
#         lime_survey = Questionnaires()
#         sid = None
#
#         try:
#             # Cria uma nova survey no lime survey
#             title_survey = 'Questionario de teste'
#             sid = lime_survey.add_survey(9999, title_survey, 'en', 'G')
#
#             # Obtenho o titulo da survey
#             survey_title = lime_survey.get_survey_title(sid)
#             self.assertEqual(survey_title, title_survey)
#
#             # Verifica se esta ativa
#             survey_active = lime_survey.get_survey_properties(sid, 'active')
#             self.assertEqual(survey_active, 'N')
#
#             # Obtem uma propriedade - Administrador da Survey
#             survey_admin = lime_survey.get_survey_properties(sid, 'admin')
#             self.assertEqual(survey_admin, None)
#
#             # Importar grupo de questoes
#             handle_file_import = \
#                 open('data/static/quiz/tests/limesurvey_groups.lsg', 'r')
#             questions_data = handle_file_import.read()
#             questions_id = \
#                 lime_survey.insert_questions(sid, questions_data, 'lsg')
#             self.assertGreaterEqual(questions_id, 1)
#
#             # Inicia tabela de tokens
#             self.assertEqual(lime_survey.activate_tokens(sid), 'OK')
#
#             # Ativar survey
#             self.assertEqual(lime_survey.activate_survey(sid), 'OK')
#
#             # Verifica se esta ativa
#             survey_active = lime_survey.get_survey_properties(sid, 'active')
#             self.assertEqual(survey_active, 'Y')
#
#             # Adiciona participante e obtem o token
#             result_token = lime_survey.add_participant(sid)
#
#             # Verifica se o token está presente na tabela de participantes
#             token = lime_survey.get_participant_properties(sid, result_token, "token")
#             self.assertEqual(token, result_token['token'])
#         finally:
#             # Deleta a survey gerada no Lime Survey
#             self.assertEqual(lime_survey.delete_survey(sid), 'OK')
#
#     def test_find_all_questionnaires_method_returns_correct_result(self):
#         questionnaires = Questionnaires()
#         list_survey = self.server.list_surveys(self.session_key, None)
#         self.server.release_session_key(self.session_key)
#         self.assertEqual(questionnaires.find_all_questionnaires(), list_survey)
#         questionnaires.release_session_key()
#
#     def test_find_questionnaire_by_id_method_found_survey(self):
#         questionnaires = Questionnaires()
#         list_survey = self.server.list_surveys(self.session_key, None)
#         self.server.release_session_key(self.session_key)
#         self.assertEqual(questionnaires.find_questionnaire_by_id(list_survey[3]['sid']), list_survey[3])
#         questionnaires.release_session_key()
#
#     def test_find_questionnaire_by_id_method_not_found_survey_by_string(self):
#         questionnaires = Questionnaires()
#         self.assertEqual(None, questionnaires.find_questionnaire_by_id('three'))
#         questionnaires.release_session_key()
#
#     def test_find_questionnaire_by_id_method_not_found_survey_by_out_of_range(self):
#         questionnaires = Questionnaires()
#         self.assertEqual(None, questionnaires.find_questionnaire_by_id(10000000))
#         questionnaires.release_session_key()
#
#     def test_list_active_questionnaires(self):
#         questionnaires = Questionnaires()
#         list_survey = self.server.list_surveys(self.session_key, None)
#         self.server.release_session_key(self.session_key)
#         list_active_survey = []
#         for survey in list_survey:
#             survey_has_token = questionnaires.survey_has_token_table(survey['sid'])
#             if survey['active'] == "Y" and survey_has_token is True:
#                 list_active_survey.append(survey)
#         self.assertEqual(questionnaires.find_all_active_questionnaires(), list_active_survey)
#         questionnaires.release_session_key()
#
#     def test_add_participant_to_a_survey(self):
#         """testa a insercao de participante em um questionario """
#
#         surveys = Questionnaires()
#         list_active_surveys = surveys.find_all_active_questionnaires()
#
#         self.assertNotEqual(list_active_surveys, None)
#
#         survey = list_active_surveys[0]
#         sid = int(survey['sid'])
#
#         participant_data_result = surveys.add_participant(sid)
#
#         # verificar se info retornada eh a mesma
#         # self.assertEqual(participant_data_result[0]['email'], participant_data['email'])
#         # self.assertEqual(participant_data_result[0]['lastname'], participant_data['lastname'])
#         # self.assertEqual(participant_data_result[0]['firsStname'], participant_data['firstname'])
#
#         self.assertNotEqual(participant_data_result, None)
#
#         token_id = participant_data_result['tid']
#
#         # remover participante do questionario
#         result = self.server.delete_participants(self.session_key, sid, [token_id])
#
#         self.assertEqual(result[str(token_id)], 'Deleted')
#
#         surveys.release_session_key()
#
#     def test_add_and_delete_survey(self):
#         """TDD - Criar uma survey de teste e apos devera ser excluida
#         """
#         survey_id_generated = self.server.add_survey(self.session_key, 9999, 'Questionario de Teste', 'en', 'G')
#         self.assertGreaterEqual(survey_id_generated, 0)
#
#         status = self.server.delete_survey(self.session_key, survey_id_generated)
#         self.assertEqual(status['status'], 'OK')
#         self.server.release_session_key(self.session_key)
#
#     def test_add_and_delete_survey_methods(self):
#         questionnaires = Questionnaires()
#         sid = questionnaires.add_survey('9999', 'Questionario de Teste', 'en', 'G')
#         self.assertGreaterEqual(sid, 0)
#
#         status = questionnaires.delete_survey(sid)
#         self.assertEqual(status, 'OK')
#
#     def test_delete_survey_participant(self):
#         """Remove survey participant test"""
#
#         surveys = Questionnaires()
#         list_active_surveys = surveys.find_all_active_questionnaires()
#
#         self.assertNotEqual(list_active_surveys, None)
#
#         survey = list_active_surveys[0]
#         sid = int(survey['sid'])
#
#         participant_data_result = surveys.add_participant(sid)
#
#         # verificar se info retornada eh a mesma
#         # self.assertEqual(participant_data_result[0]['email'], participant_data['email'])
#         # self.assertEqual(participant_data_result[0]['lastname'], participant_data['lastname'])
#         # self.assertEqual(participant_data_result[0]['firstname'], participant_data['firstname'])
#
#         self.assertNotEqual(participant_data_result, None)
#
#         token_id = participant_data_result['tid']
#
#         # remover participante do questionario
#         result = surveys.delete_participants(sid, [token_id])
#
#         self.assertEqual(result[str(token_id)], 'Deleted')
#
#         surveys.release_session_key()


class SurveyTest(TestCase):
    def setUp(self):
        # create the groups of users and their permissions
        exec(open("add_initial_data.py", encoding="utf-8").read())

        self.user, passwd = create_user(Group.objects.all())
        self.client.login(username=self.user.username, password=passwd)

        self.survey = create_survey()
        self.patient = UtilTests.create_patient(self.user)
        # token_id=1 from mocks
        self.response = UtilTests.create_response_survey(
            self.user, self.patient, self.survey, token_id=1
        )

    @patch("survey.abc_search_engine.Server")
    def test_survey_list(self, mockServer):
        mockServer.return_value.get_session_key.return_value = (
            "vz224sb7jzkvh8i4kpx8fxbcxd67meht"
        )
        mockServer.return_value.get_language_properties.return_value = {
            "status": "Error: Invalid survey ID"
        }

        survey_response = PatientQuestionnaireResponse.objects.first()
        survey_response.delete()
        self.survey.delete()
        response = self.client.get(reverse("survey_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["questionnaires_list"]), 0)

        create_survey()
        response = self.client.get(reverse("survey_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["questionnaires_list"]), 1)

    @patch("survey.abc_search_engine.Server")
    def test_survey_create(self, mockServer):
        mockServer.return_value.get_session_key.return_value = (
            "vz224sb7jzkvh8i4kpx8fxbcxd67meht"
        )
        mockServer.return_value.list_surveys.return_value = [
            {
                "sid": 915325,
                "active": "Y",
                "expires": None,
                "surveyls_title": "First Survey",
                "startdate": None,
            },
            {
                "sid": 397442,
                "active": "Y",
                "expires": None,
                "surveyls_title": "Test questionnaire",
                "startdate": None,
            },
        ]
        mockServer.return_value.get_summary.return_value = 2

        # Request the survey register screen
        response = self.client.get(reverse("survey_create"))
        self.assertEqual(response.status_code, 200)

        # Set survey data
        self.data = {
            "action": "save",
            "questionnaire_selected": response.context["questionnaires_list"][0]["sid"],
        }

        # Count the number of surveys currently in database
        count_before_insert = Survey.objects.all().count()

        # Add the new survey
        response = self.client.post(reverse("survey_create"), self.data)
        self.assertEqual(response.status_code, 302)

        # Count the number of surveys currently in database
        count_after_insert = Survey.objects.all().count()

        # Check if it has increased
        self.assertEqual(count_after_insert, count_before_insert + 1)

    @patch("survey.abc_search_engine.Server")
    def test_survey_update(self, mockServer):
        mockServer.return_value.get_session_key.return_value = (
            "vz224sb7jzkvh8i4kpx8fxbcxd67meht"
        )
        # TODO (NES-981): probably this errors are due to running without LIMESURVEY=remote.
        #  Run with it.
        mockServer.return_value.get_survey_properties.return_value = {
            "status": "Error: Invalid survey ID"
        }
        mockServer.return_value.get_language_properties.return_value = {
            "status": "Error: Invalid survey ID"
        }

        # Create an instance of a GET request.
        self.factory = RequestFactory()
        request = self.factory.get(
            reverse(
                "survey_edit",
                args=[
                    self.survey.pk,
                ],
            )
        )
        request.user = self.user
        request.LANGUAGE_CODE = "pt-BR"

        response = survey_update(request, survey_id=self.survey.pk)
        self.assertEqual(response.status_code, 200)

        # Update with changes
        self.data = {"action": "save", "is_initial_evaluation": True, "Title": "1 - 1"}
        response = self.client.post(
            reverse("survey_edit", args=(self.survey.pk,)), self.data, follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Update without changes
        response = self.client.post(
            reverse("survey_edit", args=(self.survey.pk,)), self.data, follow=True
        )
        self.assertEqual(response.status_code, 200)

    @patch("survey.abc_search_engine.Server")
    def test_survey_view(self, mockServer):
        self._set_mocks(mockServer)
        response = self.client.get(reverse("survey_view", args=(self.survey.pk,)))
        self.assertEqual(response.status_code, 200)

    @patch("survey.abc_search_engine.Server")
    def test_GET_survey_view_display_update_acquisitiondate_buttons(self, mockServer):
        self._set_mocks(mockServer)
        # token_id=2 from mocks
        self.create_experiment_questionnaire_response(self.patient, 2, self.survey)

        response = self.client.get(reverse("survey_view", args=(self.survey.pk,)))
        self.assertContains(
            response, "Atualizar data de preenchimento do LimeSurvey", 2
        )

    @patch("survey.abc_search_engine.Server")
    def test_update_acquisitiondate_from_limesurvey(self, mockServer):
        self._set_mocks(mockServer)

        self.create_experiment_questionnaire_response(self.patient, 2, self.survey)

        # This dates are in export_responses mock for the acquisitiondate
        # field in the decoded responses
        new_acquisitiondate_1 = "03/09/2021"
        new_acquisitiondate_2 = "04/09/2021"

        self.client.get(
            reverse("update_survey_acquisitiondate", args=(self.survey.pk,))
        )

        entrance_questionnaire_response = PatientQuestionnaireResponse.objects.get(
            token_id=1
        )
        experiment_questionnaire_response = QuestionnaireResponse.objects.get(
            token_id=2
        )

        self.assertEqual(
            entrance_questionnaire_response.date.strftime("%m/%d/%Y"),
            new_acquisitiondate_1,
        )
        self.assertEqual(
            experiment_questionnaire_response.date.strftime("%m/%d/%Y"),
            new_acquisitiondate_2,
        )

    @patch("survey.abc_search_engine.Server")
    def test_update_acquisitiondate_from_limesurvey_with_date_in_wrong_format_fails_silently(
        self, mockServer
    ):
        self._set_mocks(mockServer)

        # Refefine the two responses so the response from token_id=2 is 'N/A':
        # bad format for the date
        mockServer.return_value.export_responses.return_value = (
            "ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInR"
            "va2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1YmplY3"
            "RpZCIsImFiYyIKIjIiLCIxOTgwLTAxLTAxIDAwOjAwOjAwIiwiMiIsImVuIiwiZ"
            "2R1ZTFIbFR2Z0tCeDJnIiwiMiIsIk4vQSIsIjQiLCJhYmMiCgo="
        )

        response = self.client.get(
            reverse("update_survey_acquisitiondate", args=(self.survey.pk,)),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    @patch("survey.abc_search_engine.Server")
    def test_GET_update_survey_acquisitiondate_view_redirects_to_survey_view(
        self, mockServer
    ):
        self._set_mocks(mockServer)

        response = self.client.get(
            reverse("update_survey_acquisitiondate", args=(self.survey.pk,))
        )
        survey_view_url = reverse("survey_view", args=(self.survey.pk,))
        self.assertRedirects(response, survey_view_url, 302)

    @patch("survey.abc_search_engine.Server")
    def test_update_acquisitiondate_from_limesurvey_returns_responses_updated1(
        self, mockServer
    ):
        """Two responses are updated"""

        self._set_mocks(mockServer)

        patient2 = UtilTests.create_patient(self.user)
        UtilTests.create_response_survey(self.user, patient2, self.survey, token_id=2)

        tokens = mockServer.return_value.list_participants.return_value
        ls_responses = b64decode(
            mockServer.return_value.export_responses.return_value
        ).decode()
        nes_responses = PatientQuestionnaireResponse.objects.all()

        responses = update_acquisitiondate(tokens, ls_responses, nes_responses)

        # The 2 responses in ls_responses have dates differentes from the
        # dates created in questionnaire responses, so the dates were updated
        self.assertEqual(len(responses), 2)

    @patch("survey.abc_search_engine.Server")
    def test_update_acquisitiondate_from_limesurvey_returns_responses_updated2(
        self, mockServer
    ):
        """No responses were updated"""

        self._set_mocks(mockServer)

        patient2 = UtilTests.create_patient(self.user)

        # The date in ls_responses for token_id=1
        self.response.date = "2021-03-09"
        self.response.save()

        questionnaire_response_2 = UtilTests.create_response_survey(
            self.user, patient2, self.survey, token_id=2
        )
        # The date in ls_responses for the first token
        questionnaire_response_2.date = "2021-04-09"
        questionnaire_response_2.save()

        tokens = mockServer.return_value.list_participants.return_value
        ls_responses = b64decode(
            mockServer.return_value.export_responses.return_value
        ).decode()
        nes_responses = PatientQuestionnaireResponse.objects.all()

        responses = update_acquisitiondate(tokens, ls_responses, nes_responses)

        # The 2 responses in ls_responses have dates differentes from the
        # dates created in questionnaire responses, so the dates were updated
        self.assertEqual(len(responses), 0)

    @patch("survey.abc_search_engine.Server")
    def test_GET_update_survey_acquisitiondate_view_redirects_to_survey_view_with_right_message1(
        self, mockServer
    ):
        """No responses were updated"""

        self._set_mocks(mockServer)

        patient2 = UtilTests.create_patient(self.user)

        # The date in ls_responses for the first token
        self.response.date = "2021-03-09"
        self.response.save()

        questionnaire_response_2 = UtilTests.create_response_survey(
            self.user, patient2, self.survey, token_id=2
        )
        # The date in ls_responses for the first token
        questionnaire_response_2.date = "2021-04-09"
        questionnaire_response_2.save()

        response = self.client.get(
            reverse("update_survey_acquisitiondate", args=(self.survey.pk,)),
            follow=True,
        )

        self.assertContains(
            response,
            "Nenhuma data de aquisição de respostas concluídas foi "
            "alterada no LimeSurvey desde a última atualização, "
            "a data de aquisição não está preenchida no "
            "LimeSurvey, ou foi preenchida em um formato não "
            "reconhecido pelo NES.",
        )

    @patch("survey.abc_search_engine.Server")
    def test_GET_update_survey_acquisitiondate_view_redirects_to_survey_view_with_right_message2(
        self, mockServer
    ):
        """Two responses were updated"""

        self._set_mocks(mockServer)

        patient2 = UtilTests.create_patient(self.user)
        self.create_experiment_questionnaire_response(patient2, 2, self.survey)

        response = self.client.get(
            reverse("update_survey_acquisitiondate", args=(self.survey.pk,)),
            follow=True,
        )

        self.assertContains(response, "2 respostas foram atualizadas!")

    @patch("survey.abc_search_engine.Server")
    def test_survey_without_pt_title_gets_pt_title_filled_with_limesurvey_code_when_there_is_not_en_title(
        self, mockServer
    ):
        mockServer.return_value.get_session_key.return_value = (
            "vz224sb7jzkvh8i4kpx8fxbcxd67meht"
        )
        mockServer.return_value.get_language_properties.return_value = {
            "status": "Error: Invalid survey ID"
        }

        # Create a survey with a dummy lime survey id and without any code
        survey = Survey.objects.create(lime_survey_id=-1)
        self.assertIsNone(survey.pt_title)

        response = self.client.get(reverse("survey_list"))
        self.assertIsNotNone(Survey.objects.last().pt_title)
        self.assertEqual(Survey.objects.last().pt_title, str(survey.lime_survey_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["questionnaires_list"]), 2)

    @override_settings(LANGUAGE_CODE="en")
    @patch("survey.abc_search_engine.Server")
    def test_survey_without_en_title_gets_en_title_filled_with_limesurvey_code_when_there_is_not_pt_title(
        self, mockServer
    ):
        mockServer.return_value.get_session_key.return_value = (
            "vz224sb7jzkvh8i4kpx8fxbcxd67meht"
        )
        mockServer.return_value.get_language_properties.return_value = {
            "status": "Error: Invalid survey ID"
        }

        # Create a survey with a dummy lime survey id and without any code
        survey = Survey.objects.create(lime_survey_id=-1)
        self.assertIsNone(survey.en_title)

        response = self.client.get(reverse("survey_list"))
        self.assertIsNotNone(Survey.objects.last().en_title)
        self.assertEqual(Survey.objects.last().en_title, str(survey.lime_survey_id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["questionnaires_list"]), 2)

    @patch("survey.abc_search_engine.Server")
    def test_survey_without_pt_title_gets_listed_with_en_title_instead_but_remains_without_pt_title(
        self, mockServer
    ):
        mockServer.return_value.get_session_key.return_value = (
            "vz224sb7jzkvh8i4kpx8fxbcxd67meht"
        )

        # Create an survey with a dummy lime survey id and without any code
        survey = Survey.objects.create(lime_survey_id=-1, en_title="Test_en_title")
        self.assertIsNone(survey.pt_title)

        response = self.client.get(reverse("survey_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["questionnaires_list"]), 2)

        # Check if the page renders the en title of the survey
        self.assertContains(response, survey.en_title)

        # Check that the pt_title field remains null
        self.assertIsNone(Survey.objects.last().pt_title)

    @override_settings(LANGUAGE_CODE="en")
    @patch("survey.abc_search_engine.Server")
    def test_survey_without_en_title_gets_listed_with_pt_title_instead_but_remains_without_en_title(
        self, mockServer
    ):
        mockServer.return_value.get_session_key.return_value = (
            "vz224sb7jzkvh8i4kpx8fxbcxd67meht"
        )

        # Create a survey with a dummy lime survey id and without any code
        survey = Survey.objects.create(lime_survey_id=-1, pt_title="Teste_pt_title")
        self.assertIsNone(survey.en_title)

        response = self.client.get(reverse("survey_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["questionnaires_list"]), 2)

        # Check if the page renders the pt title of the survey
        self.assertContains(response, survey.pt_title)

        # Check that the en_title field remains null
        self.assertIsNone(Survey.objects.last().en_title)

    @patch("survey.abc_search_engine.Server")
    def test_survey_without_pt_or_en_title_returns_default_language_title_to_be_listed_but_does_not_save(
        self, mockServer
    ):
        mockServer.return_value.get_session_key.return_value = (
            "vz224sb7jzkvh8i4kpx8fxbcxd67meht"
        )
        mockServer.return_value.add_survey.return_value = 21212150
        mockServer.return_value.get_language_properties.side_effect = [
            {"surveyls_title": None},
            {"surveyls_title": None},
            {"surveyls_title": "Test Questionnaire in French"},
        ]
        mockServer.return_value.get_survey_properties.return_value = {"active": "N"}

        lime_survey = Questionnaires()

        # Create a new survey at LimeSurvey withou titles in pt or en languages
        fr_title_survey = "Test Questionnaire in French"
        sid = lime_survey.add_survey(9999, fr_title_survey, "fr", "G")

        Survey.objects.create(lime_survey_id=sid)
        response = self.client.get(reverse("survey_list"))

        # Check if the page renders the fr title of the survey
        self.assertContains(response, fr_title_survey)

        # Check that pt_title and en_title remain null
        self.assertIsNone(Survey.objects.last().en_title)
        self.assertIsNone(Survey.objects.last().pt_title)

    @patch("survey.abc_search_engine.Server")
    def test_surveys_list_get_updated(self, mockServer):
        mockServer.return_value.get_session_key.return_value = (
            "vz224sb7jzkvh8i4kpx8fxbcxd67meht"
        )
        mockServer.return_value.add_survey.return_value = 212121
        mockServer.return_value.get_language_properties.side_effect = [
            {"surveyls_title": "Questionário Teste"},
            {"surveyls_title": None},
            {"surveyls_title": "Questionário Teste"},
            {"surveyls_title": None},
        ]
        mockServer.return_value.get_survey_properties.return_value = {"active": "N"}

        # Simulate a discrepancy between the survey informations at
        # limesurvey and NES
        self.survey.pt_title = "Título discrepante"
        self.survey.save()

        self.assertNotEqual(Survey.objects.last().pt_title, "Questionário Teste")

        # Simulate clicking to update the list with new limesurvey information
        self.client.post(reverse("survey_list"), {"action": "update"}, follow=True)

        # Check if the pt_title was updated properly
        self.assertEqual(Survey.objects.last().pt_title, "Questionário Teste")

    @staticmethod
    def _set_mocks(mockServer):
        mockServer.return_value.get_session_key.return_value = "abc"
        mockServer.return_value.get_survey_properties.return_value = {
            "language": "en",
            "additional_languages": "",
        }
        mockServer.return_value.get_participant_properties.return_value = {
            "completed": "2020-09-25 09:19"
        }
        mockServer.return_value.get_language_properties.return_value = {
            "surveyls_title": "Survey title"
        }
        mockServer.return_value.list_participants.return_value = [
            {
                "tid": 1,
                "token": "gdue1HlTvgKBx2g",
                "participant_info": {"firstname": "", "lastname": "", "email": ""},
            },
            {
                "tid": 2,
                "token": "liVg8aNvtXpEFXP",
                "participant_info": {"firstname": "", "lastname": "", "email": ""},
            },
        ]
        mockServer.return_value.export_responses.return_value = (
            "ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsIn"
            "Rva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1Ympl"
            "Y3RpZCIsImFiYyIKIjIiLCIxOTgwLTAxLTAxIDAwOjAwOjAwIiwiMiIsImVuIi"
            "wiZ2R1ZTFIbFR2Z0tCeDJnIiwiMiIsIjIwMjEtMDMtMDkgMDA6MDA6MDAiLCI0"
            "IiwiYWJjIgoiNCIsIjE5ODAtMDEtMDEgMDA6MDA6MDAiLCIyIiwiZW4iLCJsaV"
            "ZnOGFOdnRYcEVGWFAiLCIyIiwiMjAyMS0wNC0wOSAwMDowMDowMCIsIjYiLCJh"
            "YmMiCgo="
        )

    def create_experiment_questionnaire_response(self, patient, token_id, survey):
        resource_project = ObjectsFactory.create_research_project(self.user)
        experiment = ObjectsFactory.create_experiment(resource_project)
        group = ObjectsFactory.create_group(experiment)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = ObjectsFactory.create_subject_of_group(group, subject)
        rootcomponent = ObjectsFactory.create_component(
            experiment, "block", "root component"
        )
        questionnaire = ObjectsFactory.create_component(
            experiment, Component.QUESTIONNAIRE, kwargs={"survey": survey}
        )
        component_config = ObjectsFactory.create_component_configuration(
            rootcomponent, questionnaire
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        ObjectsFactory.create_questionnaire_response(
            dct, self.user, token_id=token_id, subject_of_group=subject_of_group
        )
