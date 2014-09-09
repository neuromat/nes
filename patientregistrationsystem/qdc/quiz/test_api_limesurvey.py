import pyjsonrpc
from django.test import TestCase
from abc_search_engine import Questionnaires


class ABCSearchEngineTest(TestCase):
    session_key = None
    server = None

    def setUp(self):
        self.server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        username = "jenkins"
        password = "numecusp"
        self.session_key = self.server.get_session_key(username, password)
        # Checa se conseguiu conectar no lime Survey com as credenciais fornecidas no settings.py
        if isinstance(self.session_key, dict):
            if 'status' in self.session_key:
                self.assertNotEqual(self.session_key['status'], 'Invalid user name or password')
                print 'Failed to connect Lime Survey %s' % self.session_key['status']

    def test_find_all_questionnaires_method_returns_correct_result(self):
        q = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        self.assertEqual(q.find_all_questionnaires(), list_survey)
        q.release_session_key()

    def test_find_questionnaire_by_id_method_found_survey(self):
        q = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        self.assertEqual(q.find_questionnaire_by_id(list_survey[3]['sid']), list_survey[3])
        q.release_session_key()

    def test_find_questionnaire_by_id_method_not_found_survey_by_string(self):
        q = Questionnaires()
        self.assertEqual(None, q.find_questionnaire_by_id('three'))
        q.release_session_key()

    def test_find_questionnaire_by_id_method_not_found_survey_by_out_of_range(self):
        q = Questionnaires()
        self.assertEqual(None, q.find_questionnaire_by_id(10000000))
        q.release_session_key()

    def test_list_active_questionnaires(self):
        q = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        list_active_survey = []
        for survey in list_survey:
            survey_has_token = q.survey_has_token_table(survey['sid'])
            if survey['active'] == "Y" and survey_has_token is True:
                list_active_survey.append(survey)
        self.assertEqual(q.find_all_active_questionnaires(), list_active_survey)
        q.release_session_key()

    def test_add_participant_to_a_survey(self):
        """testa a insercao de participante em um questionario """

        surveys = Questionnaires()
        list_active_surveys = surveys.find_all_active_questionnaires()

        self.assertNotEqual(list_active_surveys, None)

        survey = list_active_surveys[0]
        sid = int(survey['sid'])

        # list_participants = self.server.list_participants(self.session_key, sid)

        participant_data = {'email': 'juquinha@hotmail.com', 'lastname': 'junqueira', 'firstname': 'juca'}
        participant_data_result = surveys.add_participant(
            sid, participant_data['firstname'], participant_data['lastname'], participant_data['email'])

        # verificar se info retornada eh a mesma
        # self.assertEqual(participant_data_result[0]['email'], participant_data['email'])
        # self.assertEqual(participant_data_result[0]['lastname'], participant_data['lastname'])
        # self.assertEqual(participant_data_result[0]['firsStname'], participant_data['firstname'])

        self.assertNotEqual(participant_data_result, None)

        # list_participants_new = self.server.list_participants(self.session_key, sid)

        # self.assertEqual(len(list_participants_new), len(list_participants) + 1)

        # token_id = participant_data_result[0]['tid']
        token_id = participant_data_result['token_id']
        tokens_to_delete = []
        tokens_to_delete.append(token_id)

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
        q = Questionnaires()
        sid = q.add_survey('9999', 'Questionario de Teste', 'en', 'G')
        self.assertGreaterEqual(sid, 0)

        status = q.delete_survey(sid)
        self.assertEqual(status, 'OK')


    # def test_get_survey_property_usetokens(self):
    # """testa a obtencao das propriedades de um questionario"""
    #
    # surveys = Questionnaires()
    # result = surveys.get_survey_properties(641729, "usetokens")
    # surveys.release_session_key()
    #
    #     pass

    # def test_get_participant_property_usetokens(self):
    #     """testa a obtencao das propriedades de um participant/token"""
    #
    #     surveys = Questionnaires()
    #
    #     # completo
    #     result1 = surveys.get_participant_properties(426494, 2, "completed")
    #
    #     # nao completo
    #     result2 = surveys.get_participant_properties(426494, 230, "completed")
    #     result3 = surveys.get_participant_properties(426494, 230, "token")
    #     surveys.release_session_key()
    #
    #     pass

    # def test_survey_has_token_table(self):
    #     """testa se determinado questionario tem tabela de tokens criada"""
    #
    #     surveys = Questionnaires()
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
        """Remove survey participant test"""
        """testa a insercao de participante em um questionario """

        surveys = Questionnaires()
        list_active_surveys = surveys.find_all_active_questionnaires()

        self.assertNotEqual(list_active_surveys, None)

        survey = list_active_surveys[0]
        sid = int(survey['sid'])

        # list_participants = self.server.list_participants(self.session_key, sid)

        participant_data = {'email': 'juquinha@hotmail.com', 'lastname': 'junqueira', 'firstname': 'juca'}
        participant_data_result = surveys.add_participant(
            sid, participant_data['firstname'], participant_data['lastname'], participant_data['email'])

        # verificar se info retornada eh a mesma
        # self.assertEqual(participant_data_result[0]['email'], participant_data['email'])
        # self.assertEqual(participant_data_result[0]['lastname'], participant_data['lastname'])
        # self.assertEqual(participant_data_result[0]['firstname'], participant_data['firstname'])

        self.assertNotEqual(participant_data_result, None)

        # list_participants_new = self.server.list_participants(self.session_key, sid)

        # self.assertEqual(len(list_participants_new), len(list_participants) + 1)

        # token_id = participant_data_result[0]['tid']
        token_id = participant_data_result['token_id']
        tokens_to_delete = []
        tokens_to_delete.append(token_id)

        # remover participante do questionario
        result = surveys.delete_participant(sid, token_id)

        self.assertEqual(result[str(token_id)], 'Deleted')

        surveys.release_session_key()
