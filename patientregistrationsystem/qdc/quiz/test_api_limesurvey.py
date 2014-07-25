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
        """testa a insercao de participante em um questionario """

        surveys = Questionnaires()
        list_active_surveys = surveys.find_all_active_questionnaires()

        if list_active_surveys:

            survey = list_active_surveys[0]
            sid = int(survey['sid'])

            list_participants = self.server.list_participants(self.session_key, sid)

            participant_data = {'email': 'evandro2001@hotmail.com', 'lastname': 'rocha', 'firstname': 'evandro'}
            participant_data_result = surveys.add_participant(sid, [participant_data])

            # verificar se info retornada eh a mesma
            self.assertEqual(participant_data_result[0]['email'], participant_data['email'])
            self.assertEqual(participant_data_result[0]['lastname'], participant_data['lastname'])
            self.assertEqual(participant_data_result[0]['firstname'], participant_data['firstname'])

            list_participants_new = self.server.list_participants(self.session_key, sid)

            self.assertEqual(len(list_participants_new), len(list_participants) + 1)

            token_id = participant_data_result[0]['tid']
            tokens_to_delete = []
            tokens_to_delete.append(token_id)

            # remover participante do questionario
            result = self.server.delete_participants(self.session_key, sid, [token_id])

            self.assertEqual(result[str(token_id)], 'Deleted')
