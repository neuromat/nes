from django.test import TestCase

from survey.abc_search_engine import Questionnaires

# This is the survey id of the lss survey file for the integration tests
# that is at this directory
LS_ID = 472711


class LimeSurveyIntegrationTestCase(TestCase):

    def test_acquisitiondate_field_is_not_hidden(self):
        ls = Questionnaires()
        groups = ls.list_groups(LS_ID)
        identification_group = next(
            item for item in groups if item['group_name'] == 'Identification')
        questions = ls.list_questions(LS_ID, identification_group['gid'])
        acquisitiondate_question = next(
            item for item in questions if item['title'] == 'acquisitiondate')
        question_properties = ls.get_question_properties(
            acquisitiondate_question['qid'], 'en')

        self.assertEqual(question_properties['attributes']['hidden'], '0')
