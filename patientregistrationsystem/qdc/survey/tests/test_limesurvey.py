from unittest.mock import patch

from django.test import TestCase

from survey.abc_search_engine import Questionnaires, ABCSearchEngine
from survey.survey_utils import QuestionnaireUtils


class LimeSurveyAPITest(TestCase):

    @patch('survey.abc_search_engine.Server')
    def test_get_question_properties(self, mockServer):
        lime_survey = Questionnaires()
        lime_survey.get_question_properties(1, 'en')

        question_properties = {
            'gid', 'question', 'question_order', 'subquestions',
            'answeroptions', 'title', 'type', 'attributes_lang',
            'attributes', 'other'
        }
        (session_key, question_id, properties, language), kwargs = \
            mockServer.return_value.get_question_properties.call_args
        self.assertTrue(
            set(question_properties).issubset(properties),
            str(set(question_properties)) + ' is not a subset of ' +
            str(set(properties))
        )


class SurveyUtilsTest(TestCase):

    @patch('survey.abc_search_engine.Server')
    def test_create_questionnaire_explanation_fields_has_question_order(self, mockServerClass):
        # There are fields that
        # create_questionnaire_explanation_fields method get filled we must
        # to define before calling it (fake values)
        survey_utils = QuestionnaireUtils()
        questionnaire_id = '999999'
        fields = ['question']
        survey_utils.questionnaires_experiment_data[questionnaire_id] = {}
        survey_utils.questionnaires_experiment_data[questionnaire_id]['fields'] = fields
        survey_utils.questionnaires_experiment_data[questionnaire_id]['header'] = 'dummie_header'
        # mock needed LimeSurvey RPC API methods
        mockServerClass.return_value.get_language_properties.return_value = \
            {'surveyls_title': 'Ein wunderbar Titel'}
        mockServerClass.return_value.list_questions.return_value = [{'id': {'qid': 1}}]
        # mock get_question_properties LimeSurvey API method using
        # ABCSearchEngine.QUESTION_PROPERTIES constant list with fake values
        question_order = 21
        group_id = 981
        question_properties = dict(
            zip(
                ABCSearchEngine.QUESTION_PROPERTIES,
                [group_id, 'Question Title', question_order,
                 'No available answers', 'No available answer options',
                 'question', 'N', 'No available attributes', {'hidden', '1'},
                 'N']
            )
        )
        mockServerClass.return_value.get_question_properties.return_value = \
            question_properties
        # mock list_groups LimeSurvey API method (fake values)
        language = 'en'
        entrance_survey = False
        mockServerClass.return_value.list_groups.return_value = \
            [{'randomization_group': '',
              'id': {'gid': group_id, 'language': language},
              'group_name': 'Grupo 1', 'description': '', 'group_order': 1,
              'sid': 376459, 'gid': group_id,
              'language': language, 'grelevance': ''}]

        lime_survey = Questionnaires()
        error, questionnaire_fields = survey_utils.create_questionnaire_explanation_fields(
                questionnaire_id, language, lime_survey, fields, entrance_survey)

        # First line contains metadata column headers, subsequent lines
        # contains the metadata column values.
        # Assert for correct length for metadata headers and values
        self.assertTrue(len(questionnaire_fields[0]), len(questionnaire_fields[1]))

        # asserts for question_order field
        self.assertTrue('question_order' in questionnaire_fields[0])
        index_ = questionnaire_fields[0].index('question_order')
        self.assertEqual(questionnaire_fields[1][index_], str(question_order))
