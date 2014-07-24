__author__ = ''

import pyjsonrpc
from abc import ABCMeta, abstractmethod

class ABCSearchEngine:
    __metaclass__ = ABCMeta

    @abstractmethod
    def findAllQuestionnaires(self):
    #retorna todos os questionarios armazenados no banco de dados da instancia do LimeSurvey
        server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("evandro","8YtztuqeGzUU")
        list_survey = server.list_surveys(session_key, None)
        server.release_session_key(session_key)
        return list_survey

    #retorna o questionario que tenha o nome especificado (assumir que cada questionario tem um nome unico)
    #@abstractmethod
    #def findQuestionnaireByName(self, str_name):pass

    #retorna o questionario que tenha o identiricador especificado
    @abstractmethod
    def findQuestionnaireByID(self, id):
        server = pyjsonrpc.HttpClient("http://survey.numec.prp.usp.br/index.php/admin/remotecontrol")
        session_key = server.get_session_key("evandro","8YtztuqeGzUU")
        list_survey = server.list_surveys(session_key, None)
        server.release_session_key(session_key)
        try:
            survey = (survey for survey in list_survey if survey['sid'] == id).next()
        except StopIteration:
            survey = None
        return survey

# Classe envelope para o API do limesurvey
class Questionnaires(ABCSearchEngine):

    def findAllQuestionnaires(self):
        return super(Questionnaires, self).findAllQuestionnaires()
    def findQuestionnaireByID(self, str_id):
        return super(Questionnaires, self).findQuestionnaireByID(str_id)
