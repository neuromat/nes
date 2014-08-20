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
    def add_participant(self, sid, participant_data):
        """adiciona participante ao questionario e retorna informacao do mesmo incluindo o sid"""

        server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("evandro", "8YtztuqeGzUU")

        participant_data_result = server.add_participants(
            session_key,
            sid,
            participant_data,
            True)

        server.release_session_key(session_key)

        return participant_data_result

    @abstractmethod
    def get_survey_property_usetokens(self, sid):
        """obtem propriedade 'usetokens' de um determinado questionario"""

        server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("evandro", "8YtztuqeGzUU")

        result = server.get_survey_properties(
            session_key,
            sid,
            ['usetokens']
        )

        server.release_session_key(session_key)

        return result


class Questionnaires(ABCSearchEngine):
    """ Classe envelope para o API do limesurvey """

    def find_all_questionnaires(self):
        return super(Questionnaires, self).find_all_questionnaires()

    def find_all_active_questionnaires(self):
        return super(Questionnaires, self).find_all_active_questionnaires()

    def find_questionnaire_by_id(self, str_id):
        return super(Questionnaires, self).find_questionnaire_by_id(str_id)

    def add_participant(self, str_id, participant_data):
        return super(Questionnaires, self).add_participant(str_id, participant_data)

    def get_survey_property_usetokens(self, sid):
        return super(Questionnaires, self).get_survey_property_usetokens(sid)

