__author__ = ''

import pyjsonrpc
from django.conf import settings
from abc import ABCMeta, abstractmethod
import base64


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
    def get_responses_by_token(self, sid, token):

        responses = self.server.export_responses_by_token(self.session_key, sid, 'csv', token)
        responses_txt = base64.b64decode(responses)

        return responses_txt


    @abstractmethod
    def get_question_properties(self, question_id):
        properties = self.server.get_question_properties(self.session_key, question_id,
                                                         ['question', 'subquestions', 'answeroptions', 'title', 'type'])

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

    def get_survey_properties(self, sid, prop):
        return super(Questionnaires, self).get_survey_properties(sid, prop)

    def get_participant_properties(self, survey_id, token_id, prop):
        return super(Questionnaires, self).get_participant_properties(survey_id, token_id, prop)

    def get_survey_title(self, sid):
        return super(Questionnaires, self).get_survey_title(sid)

    def survey_has_token_table(self, sid):
        return super(Questionnaires, self).survey_has_token_table(sid)

    def get_responses_by_token(self, sid, token):
        return super(Questionnaires, self).get_responses_by_token(sid, token)

    def list_questions(self, sid, gid):
        return super(Questionnaires, self).list_questions(sid, gid)

    def get_question_properties(self, question_id):
        return super(Questionnaires, self).get_question_properties(question_id)

    def list_groups(self, sid):
        return super(Questionnaires, self).list_groups(sid)