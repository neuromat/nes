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


# Classe envelope para o API do limesurvey
class Questionnaires(ABCSearchEngine):

    def find_all_questionnaires(self):
        return super(Questionnaires, self).find_all_questionnaires()

    def find_all_active_questionnaires(self):
        return super(Questionnaires, self).find_all_active_questionnaires()

    def find_questionnaire_by_id(self, str_id):
        return super(Questionnaires, self).find_questionnaire_by_id(str_id)
