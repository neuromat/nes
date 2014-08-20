__author__ = ''

import pyjsonrpc
from abc import ABCMeta, abstractmethod


class ABCSearchEngine:
    __metaclass__ = ABCMeta

    @abstractmethod
    def find_all_questionnaires(self):
        """retorna todos os questionarios armazenados no banco de dados da instancia do LimeSurvey"""

        server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("evandro", "8YtztuqeGzUU")

        list_survey = server.list_surveys(session_key, None)

        server.release_session_key(session_key)

        return list_survey

    @abstractmethod
    def find_all_active_questionnaires(self):
        """retorna todos os questionarios ativos armazenados no banco de dados da instancia do LimeSurvey"""

        server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("evandro", "8YtztuqeGzUU")

        list_survey = server.list_surveys(session_key, None)

        server.release_session_key(session_key)

        list_active_survey = []
        for survey in list_survey:
            if survey['active'] == "Y":
                list_active_survey.append(survey)

        return list_active_survey

    @abstractmethod
    def find_questionnaire_by_id(self, sid):
        """retorna o questionario que tenha o identiricador especificado"""

        server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("evandro", "8YtztuqeGzUU")

        list_survey = server.list_surveys(session_key, None)

        server.release_session_key(session_key)

        try:
            survey = (survey for survey in list_survey if survey['sid'] == sid).next()
        except StopIteration:
            survey = None
        return survey

    @abstractmethod
    def add_participant(self, sid, firstname, lastname, email):
        """adiciona participante ao questionario e retorna informacao do mesmo incluindo o sid"""

        server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("evandro", "8YtztuqeGzUU")

        participant_data = {'email': email, 'firstname': firstname, 'lastname': lastname}

        participant_data_result = server.add_participants(
            session_key,
            sid,
            [participant_data],
            True)

        server.release_session_key(session_key)

        if len(participant_data_result) > 0:
            if 'error' in participant_data_result[0]:
                result = None
            else:
                result = participant_data_result[0]['token']
        else:
            result = None

        return result

    @abstractmethod
    def get_survey_title(self, sid):
        """Retorna o titulo da survey pelo id"""

        server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("evandro", "8YtztuqeGzUU")

        survey_title = server.get_language_properties(session_key, sid, {'method': 'surveyls_title'})

        server.release_session_key(session_key)

        return survey_title.get('surveyls_title')

    @abstractmethod
    def get_survey_properties(self, sid, prop):
        """Retorna uma determinada propriedade de um questionario"""

        server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("evandro", "8YtztuqeGzUU")

        result = server.get_survey_properties(session_key, sid, {'method': prop})

        server.release_session_key(session_key)

        return result.get(prop)


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

    def get_survey_title(self, sid):
        return super(Questionnaires, self).get_survey_title(sid)
