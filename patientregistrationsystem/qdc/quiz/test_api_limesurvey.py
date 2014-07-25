import pyjsonrpc
from django.test import TestCase
from abc_search_engine import Questionnaires


class ABCSearchEngineTest(TestCase):

    session_key = None
    server = None

    def setUp(self):
        self.server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        username = "evandro"
        password = "8YtztuqeGzUU"
        self.session_key = self.server.get_session_key(username, password)

    def test_find_all_questionnaires_method_returns_correct_result(self):
        q = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        self.assertEqual(q.find_all_questionnaires(), list_survey)

    def test_find_questionnaire_by_id_method_found_survey(self):
        q = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        self.assertEqual(q.find_questionnaire_by_id(list_survey[3]['sid']), list_survey[3])

    def test_find_questionnaire_by_id_method_not_found_survey_by_string(self):
        q = Questionnaires()
        self.assertEqual(None, q.find_questionnaire_by_id('three'))

    def test_find_questionnaire_by_id_method_not_found_survey_by_out_of_range(self):
        q = Questionnaires()
        self.assertEqual(None, q.find_questionnaire_by_id(10000000))

    def test_list_active_questionnaires(self):
        q = Questionnaires()
        list_survey = self.server.list_surveys(self.session_key, None)
        self.server.release_session_key(self.session_key)
        list_active_survey = []
        for survey in list_survey:
            if survey['active'] == "Y":
                list_active_survey.append(survey)
        self.assertEqual(q.find_all_active_questionnaires(), list_active_survey)

    def test_add_participant_to_a_survey(self):
        """testa a inserção de participante em um questionario """

        surveys = Questionnaires()

        # listar questionarios ativos
        list_active_surveys = surveys.find_all_active_questionnaires()

        # pegar 1o questionario
        survey = list_active_surveys[0]

        # verificar a qtde de participantes
        list_participants = self.server.list_partipants(self.session_key, survey['sid'], None, None, False, False)

        # adicionar um participante
        participant_data = []
        participant_data.append(['email', 'evandro2001@hotmail.com'])
        participant_data.append(['email', 'evandro2001@hotmail.com'])
        self.server.add_participant(self.session_key, survey['sid'], )

        # verificar se adicionou participante e retornou um token

        # remover participante do questionario
