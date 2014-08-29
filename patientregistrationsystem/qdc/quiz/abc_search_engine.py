__author__ = ''

import pyjsonrpc
from django.conf import settings
from abc import ABCMeta, abstractmethod


class ABCSearchEngine:
    __metaclass__ = ABCMeta

    session_key = None
    server = None

    def __init__(self):
        self.get_session_key()

    def get_session_key(self):
        self.server = pyjsonrpc.HttpClient(settings.LIMESURVEY['URL'] + "/index.php/admin/remotecontrol")
        self.session_key = self.server.get_session_key(settings.LIMESURVEY['USER'], settings.LIMESURVEY['PASSWORD'])

    def release_session_key(self):
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
            if survey['active'] == "Y":
                list_active_survey.append(survey)

        return list_active_survey

    @abstractmethod
    def find_questionnaire_by_id(self, sid):
        """retorna o questionario que tenha o identiricador especificado"""

        list_survey = self.server.list_surveys(self.session_key, None)

        try:
            survey = (survey for survey in list_survey if survey['sid'] == sid).next()
        except StopIteration:
            survey = None
        return survey

    @abstractmethod
    def add_participant(self, sid, firstname, lastname, email):
        """adiciona participante ao questionario e retorna informacao do mesmo incluindo o sid"""

        participant_data = {'email': email, 'firstname': firstname, 'lastname': lastname}

        participant_data_result = self.server.add_participants(
            self.session_key,
            sid,
            [participant_data],
            True)

        if len(participant_data_result) <= 0 or 'error' in participant_data_result[0]:
            result = None
        else:
            result = {'token': participant_data_result[0]['token'],
                      'token_id': participant_data_result[0]['tid']}

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

        survey_title = self.server.get_language_properties(self.session_key, sid, {'method': 'surveyls_title'})

        return survey_title.get('surveyls_title')

    @abstractmethod
    def get_survey_properties(self, sid, prop):
        """Retorna uma determinada propriedade de um questionario"""

        result = self.server.get_survey_properties(self.session_key, sid, {'method': prop})

        return result.get(prop)

    @abstractmethod
    def set_survey_properties(self, sid, prop):
        """Configura uma determinada propriedade de um questionario"""

        result = self.server.set_survey_properties(self.session_key, sid, {'method': prop})

        return result.get(prop)

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

        result = self.server.get_participant_properties(self.session_key, survey_id, token_id, {'method': prop})

        return result.get(prop)

    @abstractmethod
    def survey_has_token_table(self, sid):
        """Retorna flag indicando se a tabela de tokens foi iniciada para determinado questionario"""

        result = self.server.get_summary(self.session_key, sid, "all")

        return "token_completed" in result

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

    def set_survey_properties(self, sid, prop):
        return super(Questionnaires, self).get_survey_properties(sid, prop)

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
