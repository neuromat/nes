# coding=utf-8

from base64 import b64decode, b64encode
from jsonrpc_requests import Server
from django.conf import settings
from abc import ABCMeta, abstractmethod


class ABCSearchEngine(metaclass=ABCMeta):
    session_key = None
    server = None

    def __init__(self):
        self.get_session_key()

    def get_session_key(self):

        self.server = Server(settings.LIMESURVEY['URL_API'] + '/index.php/admin/remotecontrol')
        self.session_key = self.server.get_session_key(settings.LIMESURVEY['USER'], settings.LIMESURVEY['PASSWORD'])
        self.session_key = None if isinstance(self.session_key, dict) else self.session_key

    def release_session_key(self):
        if self.session_key:
            self.server.release_session_key(self.session_key)

    @abstractmethod
    def find_all_questionnaires(self):
        """retorna todos os questionarios armazenados no banco de dados da instancia do LimeSurvey"""

        list_survey = self.server.list_surveys(self.session_key, None)

        return list_survey

    @abstractmethod
    def find_all_active_questionnaires(self):
        """retorna todos os questionarios ativos armazenados no banco de dados da instancia do LimeSurvey"""

        list_survey = self.server.list_surveys(self.session_key, None)

        list_active_survey = []

        for survey in list_survey:
            if survey['active'] == "Y" and self.survey_has_token_table(survey['sid']):
                list_active_survey.append(survey)

        return list_active_survey

    @abstractmethod
    def find_questionnaire_by_id(self, sid):
        """retorna o questionario que tenha o identiricador especificado"""

        list_survey = self.server.list_surveys(self.session_key, None)

        try:
            survey = next((survey for survey in list_survey if survey['sid'] == sid))
        except StopIteration:
            survey = None
        return survey

    @abstractmethod
    def add_participant(self, sid, firstname, lastname, email):
        """adiciona participante ao questionario e retorna informacao do mesmo incluindo o sid"""

        participant_data = {'email': '', 'firstname': '', 'lastname': ''}

        participant_data_result = self.server.add_participants(
            self.session_key,
            sid,
            [participant_data],
            True)

        result = None

        try:
            if len(participant_data_result) <= 0 or 'error' in participant_data_result[0]:
                result = None
            else:
                result = {'token': participant_data_result[0]['token'],
                          'token_id': participant_data_result[0]['tid']}
        except:
            result = None
            pass

        return result

    @abstractmethod
    def delete_participant(self, survey_id, tokens_ids):
        """Delete survey participant and return on success a array of deletion status for each participant or a failure
         status array"""
        result = self.server.delete_participants(
            self.session_key,
            survey_id,
            [tokens_ids]
        )
        return result

    @abstractmethod
    def get_survey_title(self, sid):
        """Retorna o titulo da survey pelo id"""

        if self.session_key:
            survey_title = self.server.get_language_properties(self.session_key, sid, {'method': 'surveyls_title'})

            if 'surveyls_title' in survey_title:
                survey_title = survey_title.get('surveyls_title')
            else:
                survey_title = str(sid)
        else:
            survey_title = str(sid)

        return survey_title

    @abstractmethod
    def get_survey_properties(self, sid, prop):
        """Retorna uma determinada propriedade de um questionario"""

        result = self.server.get_survey_properties(self.session_key, sid, {'method': prop})

        return result.get(prop)

    @abstractmethod
    def get_survey_languages(self, sid):
        """Retorna o idioma base e os idiomas adicionais"""

        result = self.server.get_survey_properties(self.session_key, sid, ['additional_languages', 'language'])

        return result

    # @abstractmethod
    # def set_survey_properties(self, sid, prop):
    #     """Configura uma determinada propriedade de um questionario"""
    #
    #     result = self.server.set_survey_properties(self.session_key, sid, {'method': prop})
    #
    #     return result.get(prop)

    @abstractmethod
    def activate_survey(self, sid):
        """Ativa uma survey criada e disponibiliza para os participantes"""

        result = self.server.activate_survey(self.session_key, sid)

        return result['status']

    @abstractmethod
    def activate_tokens(self, sid):
        """Ativa tokens para uma survey """

        result = self.server.activate_tokens(self.session_key, sid)

        return result['status']

    @abstractmethod
    def get_participant_properties(self, survey_id, token_id, prop):
        """Retorna uma determinada propriedade de um participante/token"""

        if self.session_key:
            result = self.server.get_participant_properties(self.session_key, survey_id, token_id, {'method': prop})
            result = result.get(prop)
        else:
            result = ""

        return result

    @abstractmethod
    def survey_has_token_table(self, sid):
        """Retorna flag indicando se a tabela de tokens foi iniciada para determinado questionario"""

        result = self.server.get_summary(self.session_key, sid, "token_completed")
        return isinstance(result, int)

    @abstractmethod
    def add_survey(self, wish_sid, title, language, survey_format):
        """
        Adiciona uma survey ao Lime Survey
        """
        survey_id_generated = self.server.add_survey(self.session_key, wish_sid, title, language, survey_format)
        return survey_id_generated

    @abstractmethod
    def delete_survey(self, sid):
        """
        Deleta uma survey do Lime Survey
        """
        status = self.server.delete_survey(self.session_key, sid)
        return status['status']

    @abstractmethod
    def get_responses_by_token(self, sid, token, language):

        responses = self.server.export_responses_by_token(self.session_key, sid, 'csv', token, language, 'complete')
        responses_txt = b64decode(responses)

        return responses_txt

    # @abstractmethod
    # def insert_group(self, sid, groups_data, format_import_file):
    #     groups_data_b64 = b64encode(groups_data)
    #     result = self.server.import_group(self.session_key, sid, groups_data_b64,
    #                                       format_import_file)  # format_import_file (lsg | csv)
    #
    #     if isinstance(result, dict):
    #         if 'status' in result:
    #             return result['status']
    #     else:
    #         return result

    # def add_group_questions(self, sid, group_title, description):
    #     result = self.server.add_group(self.session_key, sid, group_title, description)
    #
    #     if isinstance(result, dict):
    #         if 'status' in result:
    #             return result['status']
    #     else:
    #         return result

    def insert_questions(self, sid, questions_data, format_import_file):
        questions_data_b64 = b64encode(questions_data.encode('utf-8'))
        result = self.server.import_group(self.session_key, sid, questions_data_b64.decode('utf-8'),
                                          format_import_file)  # format_import_file (lsg | csv)

        if isinstance(result, dict):
            if 'status' in result:
                return None
        else:
            return result

    @abstractmethod
    def get_question_properties(self, question_id, language):
        properties = self.server.get_question_properties(self.session_key, question_id,
                                                         ['question', 'subquestions', 'answeroptions', 'title', 'type',
                                                          'attributes_lang', 'attributes'],
                                                         language)

        return properties

    @abstractmethod
    def list_groups(self, sid):
        groups = self.server.list_groups(self.session_key, sid)

        return groups

    @abstractmethod
    def list_questions(self, sid, gid):
        question_list = []
        questions = self.server.list_questions(self.session_key, sid, gid)
        for question in questions:
            question_list.append(question['id']['qid'])

        return question_list


class Questionnaires(ABCSearchEngine):
    """ Classe envelope para o API do limesurvey """

    def find_all_questionnaires(self):
        return super(Questionnaires, self).find_all_questionnaires()

    def find_all_active_questionnaires(self):
        return super(Questionnaires, self).find_all_active_questionnaires()

    def find_questionnaire_by_id(self, str_id):
        return super(Questionnaires, self).find_questionnaire_by_id(str_id)

    def add_participant(self, str_id, firstname, lastname, email):
        return super(Questionnaires, self).add_participant(str_id, firstname, lastname, email)

    def delete_participant(self, survey_id, tokens_ids):
        return super(Questionnaires, self).delete_participant(survey_id, tokens_ids)

    def get_survey_properties(self, sid, prop):
        return super(Questionnaires, self).get_survey_properties(sid, prop)

    # def set_survey_properties(self, sid, prop):
    #     return super(Questionnaires, self).get_survey_properties(sid, prop)

    def get_survey_languages(self, sid):
        return super(Questionnaires, self).get_survey_languages(sid)

    def get_participant_properties(self, survey_id, token_id, prop):
        return super(Questionnaires, self).get_participant_properties(survey_id, token_id, prop)

    def get_survey_title(self, sid):
        return super(Questionnaires, self).get_survey_title(sid)

    def survey_has_token_table(self, sid):
        return super(Questionnaires, self).survey_has_token_table(sid)

    def add_survey(self, wish_sid, title, language, survey_format):
        return super(Questionnaires, self).add_survey(wish_sid, title, language, survey_format)

    def delete_survey(self, sid):
        return super(Questionnaires, self).delete_survey(sid)

    def activate_survey(self, sid):
        return super(Questionnaires, self).activate_survey(sid)

    def activate_tokens(self, sid):
        return super(Questionnaires, self).activate_tokens(sid)

    def get_responses_by_token(self, sid, token, language):
        return super(Questionnaires, self).get_responses_by_token(sid, token, language)

    def list_questions(self, sid, gid):
        return super(Questionnaires, self).list_questions(sid, gid)

    def get_question_properties(self, question_id, language):
        return super(Questionnaires, self).get_question_properties(question_id, language)

    def list_groups(self, sid):
        return super(Questionnaires, self).list_groups(sid)

    def insert_questions(self, sid, questions_data, format_import_file):
        return super(Questionnaires, self).insert_questions(sid, questions_data, format_import_file)

    # def insert_group(self, sid, groups_data, format_import_file):
    #     return super(Questionnaires, self).insert_group(sid, groups_data, format_import_file)

    # def add_group_questions(self, sid, group_title, description):
    #     return super(Questionnaires, self).add_group_questions(sid, group_title, description)
