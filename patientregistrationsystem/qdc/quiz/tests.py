import pyjsonrpc
from django.test import TestCase
from quiz.abc_search_engine import ABCSearchEngine, Questionnaires
        

class ABCSearchEngineTest(TestCase):

    def test_findAllQuestionnaires_method_returns_correct_result(self):
        server = pyjsonrpc.HttpClient("http://noel.ime.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("mori","u4drrxp963n5")
        q = Questionnaires()
        list_survey = server.list_surveys(session_key, None)
        server.release_session_key(session_key)
        self.assertEqual(q.findAllQuestionnaires(), list_survey)

    def test_findQuestionnaireByID_method_found_survey(self):
        server = pyjsonrpc.HttpClient("http://noel.ime.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("mori","u4drrxp963n5")
        q = Questionnaires()
        list_survey = server.list_surveys(session_key, None)
        server.release_session_key(session_key)
        self.assertEqual(q.findQuestionnaireByID(list_survey[3]['sid']), list_survey[3])

    def test_findQuestionnaireByID_method_not_found_survey_by_string(self):
        q = Questionnaires()
        self.assertEqual(None, q.findQuestionnaireByID('three'))

    def test_findQuestionnaireByID_method_not_found_survey_by_out_of_range(self):
        q = Questionnaires()
        self.assertEqual(None, q.findQuestionnaireByID(10000000))


# comentario na branch DEV-Evandro-0.1
# outro comentario