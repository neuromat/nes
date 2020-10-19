# coding=utf-8
import re
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

    def __init__(self, limesurvey_rpc=None):
        self.limesurvey_rpc = limesurvey_rpc or settings.LIMESURVEY['URL_API'] + '/index.php/admin/remotecontrol'
        self.get_session_key()

    def get_session_key(self):
        self.server = Server(self.limesurvey_rpc)
        try:
            self.session_key = self.server.get_session_key(
                settings.LIMESURVEY['USER'], settings.LIMESURVEY['PASSWORD'])
            self.session_key = None if isinstance(self.session_key, dict) else self.session_key
        except TransportError:
            self.session_key = None
        # TODO: catch user/password exception

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

        result = self.server.add_participants(self.session_key, sid, [participant_data], True)

        if result and isinstance(result, list) and isinstance(result[0], dict) and 'error' not in result[0]:
            return {'token': result[0]['token'], 'tid': result[0]['tid']}
        else:
            return None

    @abstractmethod
    def delete_participants(self, survey_id, tokens_ids):
        """ Delete survey participant
        :param survey_id: survey ID
        :param tokens_ids: list of token ids
        :return: on success, a dict of deletion status for each participant; on failure, status dict.
        """
        result = self.server.delete_participants(self.session_key, survey_id, tokens_ids)
        # TODO: verify if there exists participants table. The questionnary
        #  may be deactivated but NES keep tracking it.

        # In case of success RPC returs a list, otherwise a dict with error status
        return result if 'status' not in result else None

    @abstractmethod
    def get_survey_title(self, sid, language):
        """
        :param sid: survey ID
        :param language: language
        :return: title of the survey
        """

        if self.session_key:
            survey_title = self.server.get_language_properties(
                self.session_key, sid, {'method': 'surveyls_title'}, language)

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
        :param prop: the name of the property of the survey
        :return: value of the property
        """
        result = self.server.get_survey_properties(
            self.session_key, sid, {'method': prop})

        return result.get(prop)

    @abstractmethod
    def get_survey_languages(self, sid):
        """
        :param sid: survey ID
        :return: the base and the additional idioms
        """
        result = self.server.get_survey_properties(
            self.session_key, sid, ['additional_languages', 'language'])

        # If failed to consume API, it return a dict with one element with
        # 'status' as key
        return None if 'status' in result else result

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
        :return: on success, dict with value of a determined property,
        else dict with error status
        """
        # Backward compatibility with last method signature.
        # TODO: refactor the code and remove this if
        if isinstance(prop, str):
            prop = [prop]

        result = self.server.get_participant_properties(
            self.session_key, survey_id, token_id, prop)

        # This if-else for backward compatibility with last method signature
        # TODO: refactor the code and remove this if-else
        if prop is not None and len(prop) == 1:
            return result.get(prop[0]) if 'status' not in result else None
        else:
            return result if 'status' not in result else None

    @abstractmethod
    def survey_has_token_table(self, sid):
        """
        :param sid: survey ID
        :return: True if the survey has token table; False, if not.
        """

        result = self.server.get_summary(
            self.session_key, sid, "token_completed")
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

        survey_id_generated = self.server.add_survey(self.session_key, sid, title, language, survey_format)

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
    def get_responses_by_token(self, sid, token, language, doctype, fields):
        """Obtain responses from a determined token.
        Limesurvey returns a string that, when b65decoded, has two new lines at the end.
        We eliminate that new lines.
        If doctype == 'csv-allanswer' export as 'csv'. The
        exportCompleteAnswers plugin may be not installed. See
        https://gitlab.com/SondagesPro/ExportAndStats/exportCompleteAnswers
        :param sid: survey ID
        :param token: token
        :param doctype: type of coded string ('csv', 'json, ...)
        :param language: language
        :param fields: fields array, using SGQA identifier
        :return: responses in the txt format
        """
        responses = {}
        if fields:
            try:
                responses = self.server.export_responses_by_token(
                    self.session_key, sid, doctype, token, language,
                    'complete', 'code', 'short', fields)
            except AttributeError:
                if doctype == 'csv-allanswer':
                    responses = self.server.export_responses_by_token(
                        self.session_key, sid, 'csv', token, language,
                        'complete', 'code', 'short', fields)
        else:
            try:
                responses = self.server.export_responses_by_token(
                    self.session_key, sid, doctype, token, language,
                    'complete')
            except AttributeError:
                if doctype == 'csv-allanswer':
                    responses = self.server.export_responses_by_token(
                        self.session_key, sid, 'csv', token, language,
                        'complete')

        if isinstance(responses, dict):
            return None

        responses = b64decode(responses).decode()
        return re.sub('\n\n', '\n', responses)

    @abstractmethod
    def get_responses(self, sid, language, response_type, fields, heading_type):
        """ Obtains responses from a determined survey.
        If doctype == 'csv-allanswer' try to export. The plugin may by not
        installed.
        :param sid: survey ID
        :param language: language
        :param response_type: (optional)'short' or 'long'
        Optional defaults to 'short'
        :param fields: filter fields that must be returned
        :param heading_type: (optional) 'code','full' or 'abbreviated'
        Optional defaults to 'code'
        :return: responses in txt format
        """
        if response_type == 'long':
            responses = self.server.export_responses(
                self.session_key, sid, 'csv', language, 'complete',
                heading_type, response_type)
        else:
            try:
                responses = self.server.export_responses(
                    self.session_key, sid, 'csv-allanswer', language,
                    'complete', heading_type, response_type)
            except AttributeError:
                responses = self.server.export_responses(
                    self.session_key, sid, 'csv', language, 'complete',
                    heading_type, response_type)

        return None if isinstance(responses, dict) \
            else b64decode(responses).decode()

    def get_header_response(self, sid, language, token, heading_type):
        """Obtain header responses.
        If doctype == 'csv-allanswer' try to export. The plugin may be not
        installed.
        :param sid: survey ID
        :param language: language
        :param token: token
        :param heading_type: heading type (can be 'code', 'abbreviated',
        'full')
        :return: str - responses in the txt format in case of success, else None
        """
        if heading_type != 'abbreviated':
            try:
                responses = self.server.export_responses_by_token(
                    self.session_key, sid, 'csv-allanswer', token, language,
                    'complete', heading_type, 'short')
            except AttributeError:
                # TODO: sid: 843661
                responses = self.server.export_responses_by_token(
                    self.session_key, sid, 'csv', token, language,
                    'complete', heading_type, 'short')
        else:
            responses = self.server.export_responses_by_token(
                self.session_key, sid, 'csv', token, language,
                'complete', heading_type, 'short')

        # For compatibility with export view call: when export_responses
        # returns {'status': 'No Response found by Token'} export view call
        # export_responses, that returns a string to responses variable and
        # can mount the screen with the possible data to export
        if isinstance(responses, dict) \
                and responses['status'] == 'No Response found for Token':
            try:
                responses = self.server.export_responses(
                    self.session_key, sid, 'csv-allanswer', language,
                    'complete', heading_type, 'short')
            except AttributeError:
                responses = self.server.export_responses(
                    self.session_key, sid, 'csv', language,
                    'complete', heading_type, 'short')

        return None if isinstance(responses, dict) \
            else b64decode(responses).decode()

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
        """ Import a group of questions from a file
        :param sid: survey ID
        :param questions_data: question data
        :param format_import_file: lsg file
        :return:
        """
        questions_data_b64 = b64encode(questions_data.encode('utf-8'))
        result = self.server.import_group(
            self.session_key, sid, questions_data_b64.decode('utf-8'), format_import_file)

        return None if isinstance(result, dict) else result

    @abstractmethod
    def get_question_properties(self, question_id, language):
        """
        :param question_id: question ID
        :param language: language of the answer
        :return: properties of a question of a survey
        """
        properties = self.server.get_question_properties(
            self.session_key, question_id, self.QUESTION_PROPERTIES, language)

        if 'status' in properties and properties['status'] in [
            'Error: Invalid questionid', 'Error: Invalid language', 'Error: Invalid questionid', 'No valid Data',
            'No permission', 'Invalid session key'
        ]:
            return None

        return properties

    def set_question_properties(self, sid, data):
        return self.server.set_question_properties(self.session_key, sid, data)

    @abstractmethod
    def list_groups(self, sid):
        """
        :param sid: survey ID
        :return: on success, list of ids and info of groups belonging to survey, else, None
        """
        groups = self.server.list_groups(self.session_key, sid)

        return groups if isinstance(groups, list) else None

    @abstractmethod
    def get_group_properties(self, gid):
        """
        :param gid: LimeSurvey group id
        :param lang: group language to return correct group, as Remote
        Control API does not do that (TODO (NES-956): see why lang is gone
        :return: list of group properties
        """
        result = self.server.get_group_properties(self.session_key, gid)

        # TODO (NES-963): treat errors
        return result

    def set_group_properties(self, sid, data):
        result = self.server.set_group_properties(self.session_key, sid, data)

        # TODO (NES-963): treat errors
        return result

    def list_questions(self, sid, gid):
        """List questions with their properties
        :param sid: LimeSurvey survey id
        :param gid: LimeSurvey group id
        :return: on success, list of question properties, else None
        """
        questions = self.server.list_questions(self.session_key, sid, gid)

        return questions if isinstance(questions, list) else None

    @abstractmethod
    def list_questions_ids(self, sid, gid):
        """
        :param sid: LimeSurvey survey id
        :param gid: LimeSurvey group id
        :return: ids and info of (sub-)questions of a survey/group
        """

        question_ids = []
        questions = self.list_questions(sid, gid)
        if questions is not None:
            for question in questions:
                question_ids.append(question['id']['qid'])

        return question_ids

    @abstractmethod
    def find_tokens_by_questionnaire(self, sid):
        """
        :param sid:
        :return: list of tokens | dict with error status
        """
        tokens = self.server.list_participants(
            self.session_key, sid, 0, 99999999)

        # If some error occurs RPC returns a dict, so return None
        return tokens if isinstance(tokens, list) else None

    def add_group(self, sid, title, description):
        result = self.server.add_group(self.session_key, sid, title)

        # TODO (NES-963): treat errors
        return result

    def add_response(self, sid, response_data):
        result = self.server.add_response(self.session_key, sid, response_data)

        # TODO (NES-963): treat errors
        return result

    def set_participant_properties(self, sid, tid, properties_dict):
        result = self.server.set_participant_properties(self.session_key, sid, tid, properties_dict)

        # TODO (NES-963): treat errors
        return result

    def import_survey(self, base64_encoded_lsa):
        """
        :param base64_encoded_lsa: Base 64 encoded string from lsa archive
        :return: lime survey id of survey created
        """
        result = self.server.import_survey(self.session_key, base64_encoded_lsa, 'lsa')

        # RPC returns dict with error status if an issue occurred
        return None if isinstance(result, dict) else result

    def export_survey(self, sid):
        """TODO (NES-956): insert docstring
        :param sid: LimeSurvey survey id
        :return: on success base64 encoded survey, else None
        """
        result = self.server.export_survey(self.session_key, sid)
        if isinstance(result, dict):  # Returned a dict element (error)
            return None

        return result

    def delete_responses(self, sid, responses):
        """Delete responses from LimeSurvey survey
        :param sid: LimeSurvey survey id
        :param responses: list of response ids
        :return: on success, dict with status ok, else None
        """
        result = self.server.delete_responses(self.session_key, sid, responses)
        return result if result['status'] == 'OK' else None

    def update_response(self, sid, response_data):
        result = self.server.update_response(self.session_key, sid, response_data)
        return result if result['status'] == 'OK' else None


class Questionnaires(ABCSearchEngine):
    """ Wrapper class for LimeSurvey API"""

    ERROR_CODE = 1
    ERROR_MESSAGE = \
        'Error: some thing went wrong consuming LimeSurvey API. Please try ' \
        'again. If problem persists please contact System Administrator.'

    def find_all_questionnaires(self):
        return super(Questionnaires, self).find_all_questionnaires()

    def find_all_active_questionnaires(self):
        return super(Questionnaires, self).find_all_active_questionnaires()

    def find_questionnaire_by_id(self, str_id):
        return super(Questionnaires, self).find_questionnaire_by_id(str_id)

    def add_participant(self, str_id):
        return super(Questionnaires, self).add_participant(str_id)

    def delete_participants(self, survey_id, tokens_ids):
        return super(Questionnaires, self).delete_participants(survey_id, tokens_ids)

    def get_survey_properties(self, sid, prop):
        return super(Questionnaires, self).get_survey_properties(sid, prop)

    def get_survey_languages(self, sid):
        return super(Questionnaires, self).get_survey_languages(sid)

    def get_participant_properties(self, survey_id, token_id, prop=None):
        return super(Questionnaires, self).get_participant_properties(
            survey_id, token_id, prop)

    def get_survey_title(self, sid, language=None):
        return super(Questionnaires, self).get_survey_title(sid, language)

    def survey_has_token_table(self, sid):
        return super(Questionnaires, self).survey_has_token_table(sid)

    def add_survey(self, sid, title, language, survey_format):
        return super(Questionnaires, self).add_survey(sid, title, language, survey_format)

    def delete_survey(self, sid):
        return super(Questionnaires, self).delete_survey(sid)

    def activate_survey(self, sid):
        return super(Questionnaires, self).activate_survey(sid)

    def activate_tokens(self, sid):
        return super(Questionnaires, self).activate_tokens(sid)

    def get_responses_by_token(
            self, sid, token, language=None, doctype='csv', fields=[]):
        return super(Questionnaires, self).get_responses_by_token(
            sid, token, language, doctype, fields)

    def get_responses(self, sid, language, response_type='short', fields=None, heading_type='code'):
        return super(Questionnaires, self).get_responses(sid, language, response_type, fields, heading_type)

    def get_header_response(self, sid, language, token=1, heading_type='code'):
        return super(Questionnaires, self).get_header_response(sid, language, token, heading_type)

    def get_summary(self, sid, stat_name):
        return super(Questionnaires, self).get_summary(sid, stat_name)

    def list_questions(self, sid, gid):
        return super(Questionnaires, self).list_questions(sid, gid)

    def list_questions_ids(self, sid, gid):
        return super(Questionnaires, self).list_questions_ids(sid, gid)

    def get_question_properties(self, question_id, language):
        return super(Questionnaires, self).get_question_properties(question_id, language)

    # TODO (NES-956): see when this was created
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
        return super(Questionnaires, self).set_participant_properties(sid, tid, properties_dict)

    def import_survey(self, base64_encoded_lsa_file):
        return super(Questionnaires, self).import_survey(base64_encoded_lsa_file)

    def export_survey(self, sid):
        return super(Questionnaires, self).export_survey(sid)

    def delete_responses(self, sid, responses):
        return super(Questionnaires, self).delete_responses(sid, responses)

    def update_response(self, sid, response_data):
        return super(Questionnaires, self).update_response(sid, response_data)
