# import pyjsonrpc
# from django.test import TestCase
# from abc_search_engine import Questionnaires
#
#
# class ABCSearchEngineTest(TestCase):
#
#     session_key = None
#     server = None
#
#     def setUp(self):
#
#         self.server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
#         username = "evandro"
#         password = "8YtztuqeGzUU"
#         self.session_key = self.server.get_session_key(username, password)
#
#     def test_find_all_questionnaires_method_returns_correct_result(self):
#
#         q = Questionnaires()
#         list_survey = self.server.list_surveys(self.session_key, None)
#         self.server.release_session_key(self.session_key)
#         self.assertEqual(q.findAllQuestionnaires(), list_survey)
#
#     def test_find_questionnaire_by_id_method_found_survey(self):
#         q = Questionnaires()
#         list_survey = self.server.list_surveys(self.session_key, None)
#         self.server.release_session_key(self.session_key)
#         self.assertEqual(q.findQuestionnaireByID(list_survey[3]['sid']), list_survey[3])
#
#     def test_find_questionnaire_by_id_method_not_found_survey_by_string(self):
#         q = Questionnaires()
#         self.assertEqual(None, q.findQuestionnaireByID('three'))
#
#     def test_find_questionnaire_by_id_method_not_found_survey_by_out_of_range(self):
#         q = Questionnaires()
#         self.assertEqual(None, q.findQuestionnaireByID(10000000))
