# coding=utf-8

from abc import abstractmethod, ABC
from base64 import b64decode, b64encode
from jsonrpc_requests import Server, TransportError
from django.conf import settings


class ABCSearchEngine(ABC):
    QUESTION_PROPERTIES = [
        'gid', 'question', 'question_order', 'subquestions', 'answeroptions',
        'title', 'type', 'attributes_lang', 'attributes', 'other'
    ]

    session_key = None
    server = None

    def __init__(self):
        self.get_session_key()

    def get_session_key(self):

        self.server = Server(
            # settings.LIMESURVEY['URL_API'] + '/index.php/admin/remotecontrol')
            # TODO: make this link optional if the extended plugin is used
            settings.LIMESURVEY['URL_API'] +
            '/index.php/plugins/unsecure?plugin=extendRemoteControl&function=action')

        try:
            self.session_key = self.server.get_session_key(
                settings.LIMESURVEY['USER'], settings.LIMESURVEY['PASSWORD']
            )
            self.session_key = None if isinstance(self.session_key, dict) \
                else self.session_key
        except TransportError:
            self.session_key = None

    def release_session_key(self):
        if self.session_key:
            self.server.release_session_key(self.session_key)

    @abstractmethod
    def find_all_questionnaires(self):
        """
        :return: all stored surveys
        """

        list_survey = self.server.list_surveys(self.session_key, None)

        return list_survey

    @abstractmethod
    def find_all_active_questionnaires(self):
        """
        :return: all active surveys
        """

        list_survey = self.server.list_surveys(self.session_key, None)

        list_active_survey = []

        if isinstance(list_survey, list):
            for survey in list_survey:
                if survey['active'] == "Y" and self.survey_has_token_table(survey['sid']):
                    list_active_survey.append(survey)
        else:
            list_active_survey = None

        return list_active_survey

    @abstractmethod
    def find_questionnaire_by_id(self, sid):
        """
        :param sid: survey ID
        :return: survey
        """

        list_survey = self.server.list_surveys(self.session_key, None)

        try:
            survey = next((survey for survey in list_survey if survey['sid'] == sid))
        except StopIteration:
            survey = None
        return survey

    @abstractmethod
    def add_participant(self, sid):
        """
        :param sid: Survey ID
        :return: dictionary with token and token_id; None if error.
        """

        participant_data = {'email': '', 'firstname': '', 'lastname': ''}

        result = self.server.add_participants(
            self.session_key, sid, [participant_data], True
        )

        if result \
                and isinstance(result, list) \
                and isinstance(result[0], dict) \
                and 'error' not in result[0]:

            return {'token': result[0]['token'],
                    'tid': result[0]['tid']}
        else:
            return None

    @abstractmethod
    def delete_participant(self, survey_id, tokens_ids):
        """ Delete survey participant
        :param survey_id: survey ID
        :param tokens_ids: token_id to put in a list
        :return: on success, an array of deletion status for each participant; on failure, status array.
        """
        result = self.server.delete_participants(
            self.session_key,
            survey_id,
            [tokens_ids]
        )
        return result

    @abstractmethod
    def get_survey_title(self, sid, language):
        """
        :param sid: survey ID
        :param language: language
        :return: title of the survey
        """

        if self.session_key:
            survey_title = self.server.get_language_properties(self.session_key, sid, {'method': 'surveyls_title'},
                                                               language)

            if 'surveyls_title' in survey_title:
                survey_title = survey_title.get('surveyls_title')
            else:
                survey_title = str(sid)
        else:
            survey_title = str(sid)

        return survey_title

    @abstractmethod
    def get_survey_properties(self, sid, prop):
        """
        :param sid: survey ID
        :param prop: the name of the propriety of the survey
        :return: value of the property
        """

        result = self.server.get_survey_properties(self.session_key, sid, {'method': prop})

        return result.get(prop)

    @abstractmethod
    def get_survey_languages(self, sid):
        """
        :param sid: survey ID
        :return: the base and the additional idioms
        """

        result = self.server.get_survey_properties(self.session_key, sid, ['additional_languages', 'language'])

        return result

    @abstractmethod
    def activate_survey(self, sid):
        """ Activates a survey
        :param sid: survey ID
        :return: status of the survey
        """

        result = self.server.activate_survey(self.session_key, sid)

        return result['status']

    @abstractmethod
    def activate_tokens(self, sid):
        """ Activates tokens for a determined survey
        :param sid: survey ID
        :return: status of the survey
        """

        result = self.server.activate_tokens(self.session_key, sid)

        return result['status']

    @abstractmethod
    def get_participant_properties(self, survey_id, token_id, prop):
        """
        :param survey_id: survey ID
        :param token_id: token ID
        :param prop: property name
        :return: value of a determined property from a participant/token
        """

        if self.session_key:
            result = self.server.get_participant_properties(
                self.session_key, survey_id, token_id, {'method': prop}
            )
            result = result.get(prop)
        else:
            result = ''

        return result

    @abstractmethod
    def survey_has_token_table(self, sid):
        """
        :param sid: survey ID
        :return: True if the survey has token table; False, if not.
        """

        result = self.server.get_summary(self.session_key, sid, "token_completed")
        return isinstance(result, int)

    @abstractmethod
    def add_survey(self, sid, title, language, survey_format):
        """ Adds a survey to the LimeSurvey
        :param sid: survey ID
        :param title: title of the survey
        :param language: language of the survey
        :param survey_format: format of the survey
        :return: survey ID generated
        """

        survey_id_generated = self.server.add_survey(
            self.session_key, sid, title, language, survey_format
        )
        return survey_id_generated

    @abstractmethod
    def delete_survey(self, sid):
        """ remove a survey from the LimeSurvey
        :param sid: survey ID
        :return: status of the operation
        """

        status = self.server.delete_survey(self.session_key, sid)
        return status['status']

    @abstractmethod
    def get_responses_by_token(self, sid, token, language, fields=[]):
        """ obtains responses from a determined token
        :param sid: survey ID
        :param token: token
        :param language: language
        :param fields: fields array, using SGQA identifier
        :return: responses in the txt format
        """

        if fields:
            responses = self.server.export_responses_by_token(
                self.session_key, sid, 'csv', token, language, 'complete', 'code', 'short', fields)
        else:
            responses = self.server.export_responses_by_token(
                self.session_key, sid, 'csv', token, language, 'complete')

        if isinstance(responses, str):
            responses_txt = b64decode(responses)
        else:
            responses_txt = responses

        return responses_txt

    @abstractmethod
    def get_responses(self, sid, language, response_type, fields, heading_type):
        """ Obtains responses from a determined survey
        :param sid: survey ID
        :param language: language
        :param response_type: (optional)'short' or 'long'
        Optional defaults to 'short'
        :param fields: filter fields that must be returned
        :param heading_type: (optional) 'code','full' or 'abbreviated'
        Optional defaults to 'code'
        :return: responses in txt format
        """
        responses = self.server.export_responses(
            self.session_key, sid, 'csv', language, 'complete', heading_type,
            response_type
        )

        if isinstance(responses, str):
            responses_txt = b64decode(responses)
        else:
            responses_txt = responses

        return responses_txt

    def get_header_response(self, sid, language, token, heading_type):
        """ Obtain header responses
        :param sid: survey ID
        :param language: language
        :param heading_type: heading type (can be 'code' or 'full')
        :return: responses in the txt format
        """

        responses = self.server.export_responses_by_token(
            self.session_key, sid, 'csv', token, language,
            'complete', heading_type, 'short'
        )

        if not isinstance(responses, str):
            responses = self.server.export_responses(
                self.session_key, sid, 'csv', language,
                'complete', heading_type, 'short'
            )
        if isinstance(responses, str):
            responses_txt = b64decode(responses)
        else:
            responses_txt = responses

        return responses_txt

    @abstractmethod
    def get_summary(self, sid, stat_name):
        """
        :param sid: survey ID
        :param stat_name: name of the summary option - valid values are 'token_count', 'token_invalid', 'token_sent',
         'token_opted_out', 'token_completed', 'completed_responses', 'incomplete_responses', 'full_responses' or 'all'
        :return: summary information
        """
        summary_responses = self.server.get_summary(self.session_key, sid, stat_name)

        return summary_responses

    @abstractmethod
    def insert_questions(self, sid, questions_data, format_import_file):
        """ Imports a group of questions from a file
        :param sid: survey ID
        :param questions_data: question data
        :param format_import_file: lsg file
        :return:
        """
        questions_data_b64 = b64encode(questions_data.encode('utf-8'))
        result = self.server.import_group(
            self.session_key, sid, questions_data_b64.decode('utf-8'),
            format_import_file
        )

        if isinstance(result, dict):
            if 'status' in result:
                return None
        else:
            return result

    @abstractmethod
    def get_question_properties(self, question_id, language):
        """
        :param question_id: question ID
        :param language: language of the answer
        :return: properties of a question of a survey
        """

        properties = self.server.get_question_properties(
            self.session_key, question_id, self.QUESTION_PROPERTIES, language
        )

        return properties

    def set_question_properties(self, sid, data):
        return self.server.set_question_properties(self.session_key, sid, data)

    @abstractmethod
    def list_groups(self, sid):
        """
        :param sid: survey ID
        :return: ids and info of groups belonging to survey
        """

        groups = self.server.list_groups(self.session_key, sid)

        return groups

    @abstractmethod
    def get_group_properties(self, gid):
        """
        :param gid: group ID
        :param lang: group language to return correct group, as Remote
        Control API does not do that
        :return: list of group properties
        """
        return self.server.get_group_properties(self.session_key, gid)

    def set_group_properties(self, sid, data):
        return self.server.set_group_properties(
            self.session_key, sid, data
        )

    @abstractmethod
    def list_questions(self, sid, gid):
        """
        :param sid: survey ID
        :param gid: group ID
        :return: ids and info of (sub-)questions of a survey/group
        """

        question_list = []
        questions = self.server.list_questions(self.session_key, sid, gid)
        for question in questions:
            question_list.append(question['id']['qid'])

        return question_list

    @abstractmethod
    def find_tokens_by_questionnaire(self, sid):
        """
        :param sid:
        :return: tokens for specific id
        """
        tokens = self.server.list_participants(
            self.session_key, sid, 0, 99999999
        )

        return tokens

    def add_group(self, sid, title, description):
        return self.server.add_group(self.session_key, sid, title)

    def add_response(self, sid, response_data):
        return self.server.add_response(self.session_key, sid, response_data)

    def set_participant_properties(self, sid, tid, properties_dict):
        return self.server.set_participant_properties(
            self.session_key, sid, tid, properties_dict
        )

    # TODO:
    # def import_survey(self, sid):
    #     return self.server.import_survey(self.session_key, sid)

    def export_survey(self, sid):
        return self.server.export_survey(self.session_key, sid)


class Questionnaires(ABCSearchEngine):
    """ Wrapper class for LimeSurvey API"""

    def find_all_questionnaires(self):
        return super(Questionnaires, self).find_all_questionnaires()

    def find_all_active_questionnaires(self):
        return super(Questionnaires, self).find_all_active_questionnaires()

    def find_questionnaire_by_id(self, str_id):
        return super(Questionnaires, self).find_questionnaire_by_id(str_id)

    def add_participant(self, str_id):
        return super(Questionnaires, self).add_participant(str_id)

    def delete_participant(self, survey_id, tokens_ids):
        return super(Questionnaires, self).delete_participant(survey_id, tokens_ids)

    def get_survey_properties(self, sid, prop):
        return super(Questionnaires, self).get_survey_properties(sid, prop)

    def get_survey_languages(self, sid):
        return super(Questionnaires, self).get_survey_languages(sid)

    def get_participant_properties(self, survey_id, token_id, prop):
        return super(Questionnaires, self).get_participant_properties(survey_id, token_id, prop)

    def get_survey_title(self, sid, language=None):
        return super(Questionnaires, self).get_survey_title(sid, language)

    def survey_has_token_table(self, sid):
        return super(Questionnaires, self).survey_has_token_table(sid)

    def add_survey(self, sid, title, language, survey_format):
        return super(Questionnaires, self).add_survey(
            sid, title, language, survey_format
        )

    def delete_survey(self, sid):
        return super(Questionnaires, self).delete_survey(sid)

    def activate_survey(self, sid):
        return super(Questionnaires, self).activate_survey(sid)

    def activate_tokens(self, sid):
        return super(Questionnaires, self).activate_tokens(sid)

    def get_responses_by_token(self, sid, token, language, fields=[]):
        return super(Questionnaires, self).get_responses_by_token(sid, token, language, fields)

    def get_responses(self, sid, language, response_type='short', fields=None, heading_type='code'):
        return super(Questionnaires, self).get_responses(sid, language, response_type, fields, heading_type)

    def get_header_response(self, sid, language, token=1, heading_type='code'):
        return super(Questionnaires, self).get_header_response(
            sid, language, token, heading_type
        )

    def get_summary(self, sid, stat_name):
        return super(Questionnaires, self).get_summary(sid, stat_name)

    def list_questions(self, sid, gid):
        return super(Questionnaires, self).list_questions(sid, gid)

    def get_question_properties(self, question_id, language):
        return super(Questionnaires, self).get_question_properties(question_id, language)

    def set_question_properties(self, sid, data):
        return super(Questionnaires, self).set_question_properties(sid, data)

    def list_groups(self, sid):
        return super(Questionnaires, self).list_groups(sid)

    def get_group_properties(self, gid):
        return super(Questionnaires, self).get_group_properties(gid)
    
    def set_group_properties(self, sid, data):
        return super(Questionnaires, self).set_group_properties(sid, data)

    def insert_questions(self, sid, questions_data, format_import_file):
        return super(Questionnaires, self).insert_questions(sid, questions_data, format_import_file)

    def find_tokens_by_questionnaire(self, sid):
        return super(Questionnaires, self).find_tokens_by_questionnaire(sid)

    def add_group(self, sid, title, description=None):
        return super(Questionnaires, self).add_group(sid, title, description)

    def add_response(self, sid, response_data):
        return super(Questionnaires, self).add_response(sid, response_data)

    def set_participant_properties(self, sid, tid, properties_dict):
        return super(Questionnaires, self).set_participant_properties(
            sid, tid, properties_dict
        )

    # TODO:
    # def import_survey(self, sid):
    #     return super(Questionnaires, self).import_survey(sid)

    def export_survey(self, sid):
        return super(Questionnaires, self).export_survey(sid)
