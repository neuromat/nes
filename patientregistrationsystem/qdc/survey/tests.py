import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from jsonrpc_requests import Server, TransportError

from patient.tests import UtilTests
from .models import Survey
from .views import survey_update
from .abc_search_engine import Questionnaires

from custom_user.views import User

from experiment.models import QuestionnaireResponse, Questionnaire, Experiment, ComponentConfiguration, \
    Block, Group, Subject, SubjectOfGroup, ResearchProject, DataConfigurationTree


USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'

LIME_SURVEY_ID = 828636
LIME_SURVEY_TOKEN_ID_1 = 1


# @unittest.skip("Don't want to test")
class ABCSearchEngineTest(TestCase):

    session_key = None
    server = None

    def setUp(self):

        self.server = Server(settings.LIMESURVEY['URL_API'] + '/index.php/admin/remotecontrol')

        try:
            self.session_key = self.server.get_session_key(settings.LIMESURVEY['USER'], settings.LIMESURVEY['PASSWORD'])
            self.session_key = None if isinstance(self.session_key, dict) else self.session_key
        except TransportError:
            self.session_key = None

    def test_complete_survey(self):
        lime_survey = Questionnaires()
        sid = None

        try:
            # Cria uma nova survey no lime survey
            title_survey = 'Questionario de teste'
            sid = lime_survey.add_survey(9999, title_survey, 'en', 'G')

            # Obtenho o titulo da survey
            survey_title = lime_survey.get_survey_title(sid)
            self.assertEqual(survey_title, title_survey)

            # Verifica se esta ativa
            survey_active = lime_survey.get_survey_properties(sid, 'active')
            self.assertEqual(survey_active, 'N')

            # Obtem uma propriedade - Administrador da Survey
            survey_admin = lime_survey.get_survey_properties(sid, 'admin')
            self.assertEqual(survey_admin, None)

            # Importar grupo de questoes
            handle_file_import = \
                open('quiz/static/quiz/tests/limesurvey_groups.lsg', 'r')
            questions_data = handle_file_import.read()
            questions_id = \
                lime_survey.insert_questions(sid, questions_data, 'lsg')
            self.assertGreaterEqual(questions_id, 1)

            # Inicia tabela de tokens
            self.assertEqual(lime_survey.activate_tokens(sid), 'OK')

            # Ativar survey
            self.assertEqual(lime_survey.activate_survey(sid), 'OK')

            # Verifica se esta ativa
            survey_active = lime_survey.get_survey_properties(sid, 'active')
            self.assertEqual(survey_active, 'Y')

            # Adiciona participante e obtem o token
            result_token = lime_survey.add_participant(sid)

            # Verifica se o token está presente na tabela de participantes
            token = lime_survey.get_participant_properties(sid, result_token, "token")
            self.assertEqual(token, result_token['token'])
        finally:
            # Deleta a survey gerada no Lime Survey
            self.assertEqual(lime_survey.delete_survey(sid), 'OK')

    def test_find_all_questionnaires_method_returns_correct_result(self):
        questionnaires = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        self.assertEqual(questionnaires.find_all_questionnaires(), list_survey)
        questionnaires.release_session_key()

    def test_find_questionnaire_by_id_method_found_survey(self):
        questionnaires = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        self.assertEqual(questionnaires.find_questionnaire_by_id(list_survey[3]['sid']), list_survey[3])
        questionnaires.release_session_key()

    def test_find_questionnaire_by_id_method_not_found_survey_by_string(self):
        questionnaires = Questionnaires()
        self.assertEqual(None, questionnaires.find_questionnaire_by_id('three'))
        questionnaires.release_session_key()

    def test_find_questionnaire_by_id_method_not_found_survey_by_out_of_range(self):
        questionnaires = Questionnaires()
        self.assertEqual(None, questionnaires.find_questionnaire_by_id(10000000))
        questionnaires.release_session_key()

    def test_list_active_questionnaires(self):
        questionnaires = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        list_active_survey = []
        for survey in list_survey:
            survey_has_token = questionnaires.survey_has_token_table(survey['sid'])
            if survey['active'] == "Y" and survey_has_token is True:
                list_active_survey.append(survey)
        self.assertEqual(questionnaires.find_all_active_questionnaires(), list_active_survey)
        questionnaires.release_session_key()

    def test_add_participant_to_a_survey(self):
        """testa a insercao de participante em um questionario """

        surveys = Questionnaires()
        list_active_surveys = surveys.find_all_active_questionnaires()

        self.assertNotEqual(list_active_surveys, None)

        survey = list_active_surveys[0]
        sid = int(survey['sid'])

        # list_participants = self.server.list_participants(self.session_key, sid)

        # participant_data = {'email': 'juquinha@hotmail.com', 'lastname': 'junqueira', 'firstname': 'juca'}
        participant_data_result = surveys.add_participant(sid)

        # verificar se info retornada eh a mesma
        # self.assertEqual(participant_data_result[0]['email'], participant_data['email'])
        # self.assertEqual(participant_data_result[0]['lastname'], participant_data['lastname'])
        # self.assertEqual(participant_data_result[0]['firsStname'], participant_data['firstname'])

        self.assertNotEqual(participant_data_result, None)

        # list_participants_new = self.server.list_participants(self.session_key, sid)

        # self.assertEqual(len(list_participants_new), len(list_participants) + 1)

        # token_id = participant_data_result[0]['tid']
        token_id = participant_data_result['tid']
        # tokens_to_delete = [token_id]

        # remover participante do questionario
        result = self.server.delete_participants(self.session_key, sid, [token_id])

        self.assertEqual(result[str(token_id)], 'Deleted')

        surveys.release_session_key()

    def test_add_and_delete_survey(self):
        """
        TDD - Criar uma survey de teste e apos devera ser excluida
        """
        survey_id_generated = self.server.add_survey(self.session_key, 9999, 'Questionario de Teste', 'en', 'G')
        self.assertGreaterEqual(survey_id_generated, 0)

        status = self.server.delete_survey(self.session_key, survey_id_generated)
        self.assertEqual(status['status'], 'OK')
        self.server.release_session_key(self.session_key)

    def test_add_and_delete_survey_methods(self):
        questionnaires = Questionnaires()
        sid = questionnaires.add_survey('9999', 'Questionario de Teste', 'en', 'G')
        self.assertGreaterEqual(sid, 0)

        status = questionnaires.delete_survey(sid)
        self.assertEqual(status, 'OK')

    # def test_get_survey_property_usetokens(self):
    # """testa a obtencao das propriedades de um questionario"""
    #
    # surveys = Questionnaires()
    # result = surveys.get_survey_properties(641729, "usetokens")
    # surveys.release_session_key()
    #
    # pass

    # def test_get_participant_property_usetokens(self):
    # """testa a obtencao das propriedades de um participant/token"""
    #
    # surveys = Questionnaires()
    #
    # # completo
    # result1 = surveys.get_participant_properties(426494, 2, "completed")
    #
    # # nao completo
    # result2 = surveys.get_participant_properties(426494, 230, "completed")
    # result3 = surveys.get_participant_properties(426494, 230, "token")
    # surveys.release_session_key()
    #
    # pass

    # def test_survey_has_token_table(self):
    # """testa se determinado questionario tem tabela de tokens criada"""
    #
    # surveys = Questionnaires()
    #
    #     # exemplo de "true"
    #     result = surveys.survey_has_token_table(426494)
    #
    #     # exemplo de "false"
    #     result2 = surveys.survey_has_token_table(642916)
    #     surveys.release_session_key()
    #
    #     pass

    def test_delete_participant_to_a_survey(self):
        """
        Remove survey participant test
        testa a insercao de participante em um questionario
        """

        surveys = Questionnaires()
        list_active_surveys = surveys.find_all_active_questionnaires()

        self.assertNotEqual(list_active_surveys, None)

        survey = list_active_surveys[0]
        sid = int(survey['sid'])

        # list_participants = self.server.list_participants(self.session_key, sid)

        # participant_data = {'email': 'juquinha@hotmail.com', 'lastname': 'junqueira', 'firstname': 'juca'}
        participant_data_result = surveys.add_participant(sid)

        # verificar se info retornada eh a mesma
        # self.assertEqual(participant_data_result[0]['email'], participant_data['email'])
        # self.assertEqual(participant_data_result[0]['lastname'], participant_data['lastname'])
        # self.assertEqual(participant_data_result[0]['firstname'], participant_data['firstname'])

        self.assertNotEqual(participant_data_result, None)

        # list_participants_new = self.server.list_participants(self.session_key, sid)

        # self.assertEqual(len(list_participants_new), len(list_participants) + 1)

        # token_id = participant_data_result[0]['tid']
        token_id = participant_data_result['tid']
        # tokens_to_delete = [token_id]

        # remover participante do questionario
        result = surveys.delete_participant(sid, token_id)

        self.assertEqual(result[str(token_id)], 'Deleted')

        surveys.release_session_key()


class SurveyTest(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        self.factory = RequestFactory()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

    def test_survey_list(self):

        # Check if list of survey is empty before inserting anything
        response = self.client.get(reverse('survey_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['questionnaires_list']), 0)

        # Check if list of surveys returns one item after inserting one
        survey = Survey.objects.create(lime_survey_id=1)
        survey.save()
        response = self.client.get(reverse('survey_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['questionnaires_list']), 1)

    def test_survey_create(self):

        # Request the survey register screen
        response = self.client.get(reverse('survey_create'))
        self.assertEqual(response.status_code, 200)

        # Set survey data
        # self.data = {'action': 'save', 'title': 'Survey title'}
        self.data = {'action': 'save', 'questionnaire_selected': response.context['questionnaires_list'][0]['sid']}

        # Count the number of surveys currently in database
        count_before_insert = Survey.objects.all().count()

        # Add the new survey
        response = self.client.post(reverse('survey_create'), self.data)
        self.assertEqual(response.status_code, 302)

        # Count the number of surveys currently in database
        count_after_insert = Survey.objects.all().count()

        # Check if it has increased
        self.assertEqual(count_after_insert, count_before_insert + 1)

    def test_survey_update(self):

        # Create a survey to be used in the test
        survey = Survey.objects.create(lime_survey_id=1)
        survey.save()

        # Create an instance of a GET request.
        request = self.factory.get(reverse('survey_edit', args=[survey.pk, ]))
        request.user = self.user
        request.LANGUAGE_CODE = 'pt-BR'

        response = survey_update(request, survey_id=survey.pk)
        self.assertEqual(response.status_code, 200)

        # Update with changes
        self.data = {'action': 'save', 'is_initial_evaluation': True, 'Title': '1 - 1'}
        response = self.client.post(reverse('survey_edit', args=(survey.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Update without changes
        response = self.client.post(reverse('survey_edit', args=(survey.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)

    def _test_survey_view(self):

        # Create a survey to be used in the test
        # survey = Survey.objects.create(lime_survey_id=1)
        # survey.save()

        # Create a research project
        research_project = ResearchProject.objects.create(title="Research project title",
                                                          start_date=datetime.date.today(),
                                                          description="Research project description")
        research_project.save()

        # Criar um experimento mock para ser utilizado no teste
        experiment = Experiment.objects.create(title="Experimento-Update",
                                               description="Descricao do Experimento-Update",
                                               research_project=research_project)
        experiment.save()

        # Create the root of the experimental protocol
        block = Block.objects.create(identification='Root',
                                     description='Root description',
                                     experiment=Experiment.objects.first(),
                                     component_type='block',
                                     type="sequence")
        block.save()

        # Using a known questionnaire at LiveSurvey to use in this test.
        survey, created = Survey.objects.get_or_create(lime_survey_id=LIME_SURVEY_ID)

        # Create a questionnaire
        questionnaire = Questionnaire.objects.create(identification='Questionnaire',
                                                     description='Questionnaire description',
                                                     experiment=Experiment.objects.first(),
                                                     component_type='questionnaire',
                                                     survey=survey)
        questionnaire.save()

        # Include the questionnaire in the root.
        component_configuration = ComponentConfiguration.objects.create(
            name='ComponentConfiguration',
            parent=block,
            component=questionnaire
        )
        component_configuration.save()

        data_configuration_tree = DataConfigurationTree.objects.create(
            component_configuration=component_configuration
        )
        data_configuration_tree.save()

        # Create a mock group
        group = Group.objects.create(experiment=experiment,
                                     title="Group-update",
                                     description="Description of the Group-update",
                                     experimental_protocol_id=block.id)
        group.save()

        # Insert subject in the group
        util = UtilTests()
        patient_mock = util.create_patient_mock(changed_by=self.user)

        subject_mock = Subject(patient=patient_mock)
        subject_mock.save()

        subject_group = SubjectOfGroup(subject=subject_mock, group=group)
        subject_group.save()

        group.subjectofgroup_set.add(subject_group)
        experiment.save()

        # Setting the response
        questionnaire_response = QuestionnaireResponse()
        questionnaire_response.data_configuration_tree = data_configuration_tree
        questionnaire_response.subject_of_group = subject_group
        questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_1
        questionnaire_response.questionnaire_responsible = self.user
        questionnaire_response.date = datetime.datetime.now()
        questionnaire_response.save()

        response = self.client.get(reverse('survey_view', args=(survey.pk,)))
        self.assertEqual(response.status_code, 200)
