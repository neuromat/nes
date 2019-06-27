import csv
import os
import io
import tempfile
import zipfile
from datetime import datetime, date

import shutil
from unittest.mock import patch

from django.core.files import File
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.test import override_settings

from experiment.models import Component, ComponentConfiguration, \
    ComponentAdditionalFile, BrainAreaSystem, BrainArea,\
    TMSLocalizationSystem, HotSpot, TMSData, \
    CoilOrientation, DirectionOfTheInducedCurrent
from experiment.tests.tests_original import ObjectsFactory
from export.export_utils import create_list_of_trees
from export.tests.tests_helper import ExportTestCase
from patient.tests.tests_orig import UtilTests
from qdc import settings
from survey.abc_search_engine import Questionnaires
from survey.tests.tests_helper import create_survey

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'


class ExportQuestionnaireTest(ExportTestCase):
    TEMP_MEDIA_ROOT = tempfile.mkdtemp()

    def setUp(self):
        super(ExportQuestionnaireTest, self).setUp()
        # self.lime_survey = Questionnaires()
        #
        # self.sid = self.create_limesurvey_questionnaire()
        #
        # # create questionnaire data collection in NES
        # # TODO: use method already existent in patient.tests. See other places
        # self.survey = create_survey(self.sid)
        # self.data_configuration_tree = self.create_nes_questionnaire(
        #     self.root_component
        # )
        #
        # # Add response's participant to limesurvey survey and the references
        # # in our db
        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, self.subject_of_group.subject
        # )
        # self.questionnaire_response = \
        #     ObjectsFactory.create_questionnaire_response(
        #         dct=self.data_configuration_tree,
        #         responsible=self.user, token_id=result['tid'],
        #         subject_of_group=self.subject_of_group
        #     )

    def tearDown(self):
        # self.lime_survey.delete_survey(self.sid)
        # self.lime_survey.release_session_key()
        self.client.logout()

    def create_limesurvey_questionnaire(self):
        # create questionnaire at LiveSurvey
        survey_title = 'Test questionnaire'
        sid = self.lime_survey.add_survey(999999, survey_title, 'en', 'G')

        # create required group/questions for LimeSurvey/NES integration
        with open(os.path.join(
                settings.BASE_DIR, 'export', 'tests',
                'NESIdentification_group.lsg'
        )) as file:
            content = file.read()
            self.lime_survey.insert_questions(sid, content, 'lsg')

        # create other group of questions/questions for the tests
        with open(os.path.join(
                settings.BASE_DIR, 'export', 'tests',
                'limesurvey_group_2.lsg'
        )) as file:
            content = file.read()
            self.lime_survey.insert_questions(sid, content, 'lsg')

        # activate survey and tokens
        self.lime_survey.activate_survey(sid)
        self.lime_survey.activate_tokens(sid)

        return sid

    def get_lime_survey_question_groups(self, sid):
        question_groups_all = \
            [item for item in self.lime_survey.list_groups(sid)
             if item['language'] == 'en']
        question_groups = dict()
        for question_group_all in question_groups_all:
            question_groups[question_group_all['gid']] = \
                question_group_all['group_name']

        return question_groups

    def make_column_names(self, question_groups):
        column_names_dict = dict()
        for question_group in question_groups:
            for question_id \
                    in self.lime_survey.list_questions_ids(self.sid,
                                                           question_group):
                key = \
                    self.lime_survey.get_question_properties(question_id,
                                                             'en')['title']
                column_names_dict[key] = \
                    str(self.sid) + 'X' + str(question_group) + 'X' + str(
                        question_id)

        return column_names_dict

    def get_limesurvey_table_question_codes(self):
        question_groups = self.get_lime_survey_question_groups(self.sid)
        column_names_dict = self.make_column_names(question_groups)

        return column_names_dict

    def create_nes_questionnaire(self, root_component):
        """Create questionnaire component in experimental protocol and return
        data configuration tree associated to that questionnaire component
        :param root_component: Block(Component) model instance
        :return: DataConfigurationTree model instance
        """
        questionnaire = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE,
            kwargs={'survey': self.survey}
        )
        # include questionnaire in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            root_component, questionnaire
        )
        return ObjectsFactory.create_data_configuration_tree(component_config)

    def add_responses_to_limesurvey_survey(self, result, subject):
        response_table_columns = self.get_limesurvey_table_question_codes()
        response_data = {
            'token': result['token'],
            'lastpage': 2,
            response_table_columns['acquisitiondate']: str(datetime.now()),
            response_table_columns['responsibleid']: self.user.id,
            response_table_columns['subjectid']: subject.id,
            response_table_columns['firstQuestion']: 'Olá Mundo!',
            response_table_columns['secondQuestion']: 'Hallo Welt!'
        }
        self.lime_survey.add_response(self.sid, response_data)

        # Set participant as completed (in participants table).
        # See:
        # https://www.limesurvey.org/de/foren/can-i-do-this-with-limesurvey/113443-help-with-remote-control-add-response
        self.lime_survey.set_participant_properties(
            self.sid, result['tid'], {'completed': datetime.utcnow().strftime('%Y-%m-%d')})

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_same_questionnaire_used_in_different_steps_return_correct_responses_content(self, mockServer):
        """Without reuse"""

        mockServer.return_value.get_survey_properties.return_value = {'additional_languages': '', 'language': 'en'}
        mockServer.return_value.get_participant_properties.side_effect = [
            {'completed': '2019-06-26'},
            {'completed': '2019-06-26'},
            {'completed': '2019-06-26'},
            {'completed': '2019-06-26'},
            {'token': 'JLsKj3ZDO3Iof91'},
            {'completed': '2019-06-26'},
            {'token': 'VLqIkSdSRzCanyW'},
            {'completed': '2019-06-26'},
            {'token': 'IhbAZg38yDSt8jZ'}
        ]
        mockServer.return_value.export_responses.return_value = \
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVjb3VudF0iCiIxIiwiMjAxOS0wNi0yNiAwOToxNjo0MyIsIjIiLCJlbiIsIkpMc0tqM1pETzNJb2Y5MSIsIjUzOTYzIiwiMjAxOS0wNi0yNiAwOToxNjo0Mi43NzI2MiIsIjE3NzQ4MiIsIk9sw6EgTXVuZG8hIiwiSGFsbG8gV2VsdCEiLCIiLCIiCiIyIiwiMjAxOS0wNi0yNiAxMDowMjoyNCIsIjIiLCJlbiIsIlZMcUlrU2RTUnpDYW55VyIsIjUzOTYzIiwiMjAxOS0wNi0yNiAxMDowMjoyMi40ODI5MzgiLCIxNzc0ODMiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoiMyIsIjIwMTktMDYtMjYgMTA6MDM6MjAiLCIyIiwiZW4iLCJJaGJBWmczOHlEU3Q4aloiLCI1Mzk2MyIsIjIwMTktMDYtMjYgMTA6MDM6MTkuNjg3ODA3IiwiMTc3NDg0IiwiT2zDoSBNdW5kbyEiLCJIYWxsbyBXZWx0ISIsIiIsIiIKCg=='
        mockServer.return_value.list_groups.side_effect = [
            [{'language': 'en', 'group_name': 'First group', 'randomization_group': '',
              'id': {'language': 'en', 'gid': 1831}, 'sid': 597155, 'description': '', 'gid': 1831, 'grelevance': '',
              'group_order': 2}, {'language': 'en', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'en', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'zh-Hans', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'zh-Hans', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
              'grelevance': '', 'group_order': 1},
             {'language': 'nl', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'nl', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'fr', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'fr', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'de', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'de', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'pt-BR', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'pt-BR', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1},
             {'language': 'el', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'el', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'hi', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'hi', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'it', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'it', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'ja', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'ja', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'pt', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'pt', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'ru', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'ru', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'es', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'es', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'es-AR', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'es-AR', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1},
             {'language': 'es-CL', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'es-CL', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'es-MX', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'es-MX', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1}],
            [{'language': 'en', 'group_name': 'First group', 'randomization_group': '',
              'id': {'language': 'en', 'gid': 1831}, 'sid': 597155, 'description': '', 'gid': 1831, 'grelevance': '',
              'group_order': 2}, {'language': 'en', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'en', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'zh-Hans', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'zh-Hans', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
              'grelevance': '', 'group_order': 1},
             {'language': 'nl', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'nl', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'fr', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'fr', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'de', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'de', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'pt-BR', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'pt-BR', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1},
             {'language': 'el', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'el', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'hi', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'hi', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'it', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'it', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'ja', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'ja', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'pt', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'pt', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'ru', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'ru', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'es', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'es', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'es-AR', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'es-AR', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1},
             {'language': 'es-CL', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'es-CL', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'es-MX', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'es-MX', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1}],
            [{'language': 'en', 'group_name': 'First group', 'randomization_group': '',
              'id': {'language': 'en', 'gid': 1831}, 'sid': 597155, 'description': '', 'gid': 1831, 'grelevance': '',
              'group_order': 2}, {'language': 'en', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'en', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'zh-Hans', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'zh-Hans', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
              'grelevance': '', 'group_order': 1},
             {'language': 'nl', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'nl', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'fr', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'fr', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'de', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'de', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'pt-BR', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'pt-BR', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1},
             {'language': 'el', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'el', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'hi', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'hi', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'it', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'it', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'ja', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'ja', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'pt', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'pt', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'ru', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'ru', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'es', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'es', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'es-AR', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'es-AR', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1},
             {'language': 'es-CL', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'es-CL', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'es-MX', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'es-MX', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1}],
            [{'language': 'en', 'group_name': 'First group', 'randomization_group': '',
              'id': {'language': 'en', 'gid': 1831}, 'sid': 597155, 'description': '', 'gid': 1831, 'grelevance': '',
              'group_order': 2}, {'language': 'en', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'en', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'zh-Hans', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'zh-Hans', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
              'grelevance': '', 'group_order': 1},
             {'language': 'nl', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'nl', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'fr', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'fr', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'de', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'de', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'pt-BR', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'pt-BR', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1},
             {'language': 'el', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'el', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'hi', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'hi', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'it', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'it', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'ja', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'ja', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'pt', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'pt', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'ru', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'ru', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'es', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'es', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'es-AR', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'es-AR', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1},
             {'language': 'es-CL', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'es-CL', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'es-MX', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'es-MX', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1}],
            [{'language': 'en', 'group_name': 'First group', 'randomization_group': '',
              'id': {'language': 'en', 'gid': 1831}, 'sid': 597155, 'description': '', 'gid': 1831, 'grelevance': '',
              'group_order': 2}, {'language': 'en', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'en', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'zh-Hans', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'zh-Hans', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
              'grelevance': '', 'group_order': 1},
             {'language': 'nl', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'nl', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'fr', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'fr', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'de', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'de', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'pt-BR', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'pt-BR', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1},
             {'language': 'el', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'el', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'hi', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'hi', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'it', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'it', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'ja', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'ja', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'pt', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'pt', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'ru', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'ru', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830,
                                  'grelevance': '', 'group_order': 1},
             {'language': 'es', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'es', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'es-AR', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'es-AR', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1},
             {'language': 'es-CL', 'group_name': 'Identification', 'randomization_group': '',
              'id': {'language': 'es-CL', 'gid': 1830}, 'sid': 597155, 'description': '', 'gid': 1830, 'grelevance': '',
              'group_order': 1}, {'language': 'es-MX', 'group_name': 'Identification', 'randomization_group': '',
                                  'id': {'language': 'es-MX', 'gid': 1830}, 'sid': 597155, 'description': '',
                                  'gid': 1830, 'grelevance': '', 'group_order': 1}]
        ]
        mockServer.return_value.list_questions.side_effect = [
            [{'language': 'en', 'type': '|', 'modulename': None, 'id': {'language': 'en', 'qid': 5793},
              'same_default': 0, 'gid': 1831, 'qid': 5793, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'fileUpload', 'sid': 597155, 'scale_id': 0, 'mandatory': 'N', 'parent_qid': 0,
              'question_order': 3, 'question': 'Has fileupload?'},
             {'language': 'en', 'type': 'T', 'modulename': '', 'id': {'language': 'en', 'qid': 5792}, 'same_default': 0,
              'gid': 1831, 'qid': 5792, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'secondQuestion', 'sid': 597155, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
              'question_order': 2, 'question': 'Second question'},
             {'language': 'en', 'type': 'T', 'modulename': '', 'id': {'language': 'en', 'qid': 5791}, 'same_default': 0,
              'gid': 1831, 'qid': 5791, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'firstQuestion', 'sid': 597155, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
              'question_order': 1, 'question': 'First question'}],
            [{'language': 'en', 'type': 'N', 'modulename': None, 'id': {'language': 'en', 'qid': 5790},
              'same_default': 0, 'gid': 1830, 'qid': 5790, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'subjectid', 'sid': 597155, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
              'question_order': 3, 'question': 'Participant Identification number<b>:</b>'},
             {'language': 'en', 'type': 'D', 'modulename': None, 'id': {'language': 'en', 'qid': 5789},
              'same_default': 0, 'gid': 1830, 'qid': 5789, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'acquisitiondate', 'sid': 597155, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
              'question_order': 1, 'question': 'Acquisition date<strong>:</strong><br />\n'},
             {'language': 'en', 'type': 'N', 'modulename': None, 'id': {'language': 'en', 'qid': 5788},
              'same_default': 0, 'gid': 1830, 'qid': 5788, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'responsibleid', 'sid': 597155, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
              'question_order': 0, 'question': 'Responsible Identification number:'}],
            [{'language': 'en', 'type': '|', 'modulename': None, 'id': {'language': 'en', 'qid': 5793},
              'same_default': 0, 'gid': 1831, 'qid': 5793, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'fileUpload', 'sid': 597155, 'scale_id': 0, 'mandatory': 'N', 'parent_qid': 0,
              'question_order': 3, 'question': 'Has fileupload?'},
             {'language': 'en', 'type': 'T', 'modulename': '', 'id': {'language': 'en', 'qid': 5792}, 'same_default': 0,
              'gid': 1831, 'qid': 5792, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'secondQuestion', 'sid': 597155, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
              'question_order': 2, 'question': 'Second question'},
             {'language': 'en', 'type': 'T', 'modulename': '', 'id': {'language': 'en', 'qid': 5791}, 'same_default': 0,
              'gid': 1831, 'qid': 5791, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'firstQuestion', 'sid': 597155, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
              'question_order': 1, 'question': 'First question'},
             {'language': 'en', 'type': 'N', 'modulename': None, 'id': {'language': 'en', 'qid': 5790},
              'same_default': 0, 'gid': 1830, 'qid': 5790, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'subjectid', 'sid': 597155, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
              'question_order': 3, 'question': 'Participant Identification number<b>:</b>'},
             {'language': 'en', 'type': 'D', 'modulename': None, 'id': {'language': 'en', 'qid': 5789},
              'same_default': 0, 'gid': 1830, 'qid': 5789, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'acquisitiondate', 'sid': 597155, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
              'question_order': 1, 'question': 'Acquisition date<strong>:</strong><br />\n'},
             {'language': 'en', 'type': 'N', 'modulename': None, 'id': {'language': 'en', 'qid': 5788},
              'same_default': 0, 'gid': 1830, 'qid': 5788, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
              'title': 'responsibleid', 'sid': 597155, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
              'question_order': 0, 'question': 'Responsible Identification number:'}]
        ]
        mockServer.return_value.get_question_properties.side_effect = [
            {'attributes_lang': 'No available attributes', 'question_order': 3, 'type': '|', 'title': 'fileUpload',
             'attributes': 'No available attributes', 'gid': 1831, 'question': 'Has fileupload?',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'},
            {'attributes_lang': 'No available attributes', 'question_order': 2, 'type': 'T', 'title': 'secondQuestion',
             'attributes': 'No available attributes', 'gid': 1831, 'question': 'Second question',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'},
            {'attributes_lang': 'No available attributes', 'question_order': 1, 'type': 'T', 'title': 'firstQuestion',
             'attributes': 'No available attributes', 'gid': 1831, 'question': 'First question',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'},
            {'attributes_lang': 'No available attributes', 'question_order': 3, 'type': 'N', 'title': 'subjectid',
             'attributes': {'hidden': '1'}, 'gid': 1830, 'question': 'Participant Identification number<b>:</b>',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'},
            {'attributes_lang': 'No available attributes', 'question_order': 1, 'type': 'D', 'title': 'acquisitiondate',
             'attributes': {'hidden': '1'}, 'gid': 1830, 'question': 'Acquisition date<strong>:</strong><br />\n',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'},
            {'attributes_lang': 'No available attributes', 'question_order': 0, 'type': 'N', 'title': 'responsibleid',
             'attributes': {'hidden': '1'}, 'gid': 1830, 'question': 'Responsible Identification number:',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'},
            {'attributes_lang': 'No available attributes', 'question_order': 3, 'type': '|', 'title': 'fileUpload',
             'attributes': 'No available attributes', 'gid': 1831, 'question': 'Has fileupload?',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'},
            {'attributes_lang': 'No available attributes', 'question_order': 2, 'type': 'T', 'title': 'secondQuestion',
             'attributes': 'No available attributes', 'gid': 1831, 'question': 'Second question',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'},
            {'attributes_lang': 'No available attributes', 'question_order': 1, 'type': 'T', 'title': 'firstQuestion',
             'attributes': 'No available attributes', 'gid': 1831, 'question': 'First question',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'},
            {'attributes_lang': 'No available attributes', 'question_order': 3, 'type': 'N', 'title': 'subjectid',
             'attributes': {'hidden': '1'}, 'gid': 1830, 'question': 'Participant Identification number<b>:</b>',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'},
            {'attributes_lang': 'No available attributes', 'question_order': 1, 'type': 'D', 'title': 'acquisitiondate',
             'attributes': {'hidden': '1'}, 'gid': 1830, 'question': 'Acquisition date<strong>:</strong><br />\n',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'},
            {'attributes_lang': 'No available attributes', 'question_order': 0, 'type': 'N', 'title': 'responsibleid',
             'attributes': {'hidden': '1'}, 'gid': 1830, 'question': 'Responsible Identification number:',
             'subquestions': 'No available answers', 'other': 'N', 'answeroptions': 'No available answer options'}
        ]
        mockServer.return_value.get_language_properties.return_value = {'surveyls_title': 'Test questionnaire'}

        ## Ínicio - Estava no setUp
        # self.lime_survey = Questionnaires()

        # self.sid = self.create_limesurvey_questionnaire()

        # create questionnaire data collection in NES
        # TODO: use method already existent in patient.tests. See other places
        self.survey = create_survey(597155)
        self.data_configuration_tree = self.create_nes_questionnaire(
            self.root_component
        )

        # Add response's participant to limesurvey survey and the references
        # in our db
        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, self.subject_of_group.subject
        # )
        self.questionnaire_response = \
            ObjectsFactory.create_questionnaire_response(
                dct=self.data_configuration_tree,
                responsible=self.user, token_id=1,
                subject_of_group=self.subject_of_group
            )
        ## Fim - Estava no setUp

        # create questionnaire in NES
        dct = self.create_nes_questionnaire(self.root_component)  # TODO: já criado no setUP

        # Create first patient/subject/subject_of_group besides those of
        # setUp
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = \
            ObjectsFactory.create_subject_of_group(self.group, subject)

        # TODO: before commit DRY this passage
        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, subject_of_group.subject
        # )
        ObjectsFactory.create_questionnaire_response(
            dct=dct,
            responsible=self.user, token_id=2,
            subject_of_group=subject_of_group
        )

        # Create second patient/subject/subject_of_group
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group2 = \
            ObjectsFactory.create_subject_of_group(self.group, subject)

        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, subject_of_group2.subject
        # )
        ObjectsFactory.create_questionnaire_response(
            dct=dct,
            responsible=self.user, token_id=3,
            subject_of_group=subject_of_group2
        )
        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(597155) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(597155) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(597155) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(597155) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ), '/tmp'  # TODO: 1) use os.sep; 2) use tempfile
        )

        with open(
            os.path.join(
                os.sep, 'tmp',  # TODO: use tempfile
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            )
        ) as file:
            # there's 3 lines, header line + 2 responses lines
            self.assertEqual(len(file.readlines()), 3)

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_same_questionnaire_used_in_different_steps_return_correct_zipfile_content(self, mockServer):
        # TODO (NES-981): remover diretórios temporários criados
        mockServer.return_value.get_survey_properties.return_value = {'additional_languages': '', 'language': 'en'}
        mockServer.return_value.get_participant_properties.side_effect = [
            {'completed': '2019-06-24'},
            {'completed': '2019-06-24'},
            {'completed': '2019-06-24'},
            {'token': 'vnCfOsrabtuTfYs'},
            {'completed': '2019-06-24'},
            {'token': 'G0lmOoIe6IElYKF'}
        ]
        mockServer.return_value.export_responses.return_value = \
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVjb3VudF0iCiIxIiwiMjAxOS0wNi0yNCAxNTo0OToxMSIsIjIiLCJlbiIsInZuQ2ZPc3JhYnR1VGZZcyIsIjUzOTUzIiwiMjAxOS0wNi0yNCAxNTo0OTowNi43ODcwODIiLCIxNzc0NjEiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoiMiIsIjIwMTktMDYtMjQgMTU6NTE6MTUiLCIyIiwiZW4iLCJHMGxtT29JZTZJRWxZS0YiLCI1Mzk1MyIsIjIwMTktMDYtMjQgMTU6NTE6MDcuNzIwNDgxIiwiMTc3NDYyIiwiT2zDoSBNdW5kbyEiLCJIYWxsbyBXZWx0ISIsIiIsIiIKCg=='
        mockServer.return_value.list_groups.side_effect = [
            [{'gid': 1825, 'group_name': 'First group', 'description': '', 'group_order': 2, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1825, 'language': 'en'}, 'language': 'en'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'en'}, 'language': 'en'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'zh-Hans'},
              'language': 'zh-Hans'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'nl'}, 'language': 'nl'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'fr'}, 'language': 'fr'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'de'}, 'language': 'de'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'pt-BR'},
              'language': 'pt-BR'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'el'}, 'language': 'el'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'hi'}, 'language': 'hi'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'it'}, 'language': 'it'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'ja'}, 'language': 'ja'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'pt'}, 'language': 'pt'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'ru'}, 'language': 'ru'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es'}, 'language': 'es'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-AR'},
              'language': 'es-AR'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-CL'},
              'language': 'es-CL'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-MX'},
              'language': 'es-MX'}],
            [{'gid': 1825, 'group_name': 'First group', 'description': '', 'group_order': 2, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1825, 'language': 'en'}, 'language': 'en'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'en'}, 'language': 'en'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'zh-Hans'},
              'language': 'zh-Hans'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'nl'}, 'language': 'nl'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'fr'}, 'language': 'fr'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'de'}, 'language': 'de'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'pt-BR'},
              'language': 'pt-BR'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'el'}, 'language': 'el'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'hi'}, 'language': 'hi'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'it'}, 'language': 'it'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'ja'}, 'language': 'ja'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'pt'}, 'language': 'pt'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'ru'}, 'language': 'ru'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es'}, 'language': 'es'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-AR'},
              'language': 'es-AR'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-CL'},
              'language': 'es-CL'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-MX'},
              'language': 'es-MX'}],
            [{'gid': 1825, 'group_name': 'First group', 'description': '', 'group_order': 2, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1825, 'language': 'en'}, 'language': 'en'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'en'}, 'language': 'en'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'zh-Hans'},
              'language': 'zh-Hans'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'nl'}, 'language': 'nl'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'fr'}, 'language': 'fr'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'de'}, 'language': 'de'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'pt-BR'},
              'language': 'pt-BR'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'el'}, 'language': 'el'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'hi'}, 'language': 'hi'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'it'}, 'language': 'it'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'ja'}, 'language': 'ja'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'pt'}, 'language': 'pt'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'ru'}, 'language': 'ru'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es'}, 'language': 'es'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-AR'},
              'language': 'es-AR'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-CL'},
              'language': 'es-CL'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-MX'},
              'language': 'es-MX'}],
            [{'gid': 1825, 'group_name': 'First group', 'description': '', 'group_order': 2, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1825, 'language': 'en'}, 'language': 'en'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'en'}, 'language': 'en'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'zh-Hans'},
              'language': 'zh-Hans'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'nl'}, 'language': 'nl'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'fr'}, 'language': 'fr'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'de'}, 'language': 'de'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'pt-BR'},
              'language': 'pt-BR'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'el'}, 'language': 'el'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'hi'}, 'language': 'hi'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'it'}, 'language': 'it'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'ja'}, 'language': 'ja'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'pt'}, 'language': 'pt'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'ru'}, 'language': 'ru'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es'}, 'language': 'es'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-AR'},
              'language': 'es-AR'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-CL'},
              'language': 'es-CL'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-MX'},
              'language': 'es-MX'}],
            [{'gid': 1825, 'group_name': 'First group', 'description': '', 'group_order': 2, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1825, 'language': 'en'}, 'language': 'en'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'en'}, 'language': 'en'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'zh-Hans'},
              'language': 'zh-Hans'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'nl'}, 'language': 'nl'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'fr'}, 'language': 'fr'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'de'}, 'language': 'de'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'pt-BR'},
              'language': 'pt-BR'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'el'}, 'language': 'el'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'hi'}, 'language': 'hi'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'it'}, 'language': 'it'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'ja'}, 'language': 'ja'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'pt'}, 'language': 'pt'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'ru'}, 'language': 'ru'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es'}, 'language': 'es'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-AR'},
              'language': 'es-AR'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-CL'},
              'language': 'es-CL'},
             {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': 753774,
              'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'es-MX'},
              'language': 'es-MX'}]
        ]
        mockServer.return_value.list_questions.side_effect = [
            [{'other': 'N', 'parent_qid': 0, 'type': '|', 'question_order': 3, 'question': 'Has fileupload?',
              'modulename': None, 'relevance': '1', 'id': {'qid': 5775, 'language': 'en'}, 'title': 'fileUpload',
              'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': 753774, 'same_default': 0,
              'qid': 5775, 'mandatory': 'N'},
             {'other': 'N', 'parent_qid': 0, 'type': 'T', 'question_order': 2, 'question': 'Second question',
              'modulename': '', 'relevance': '1', 'id': {'qid': 5774, 'language': 'en'}, 'title': 'secondQuestion',
              'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': 753774, 'same_default': 0,
              'qid': 5774, 'mandatory': 'Y'},
             {'other': 'N', 'parent_qid': 0, 'type': 'T', 'question_order': 1, 'question': 'First question',
              'modulename': '', 'relevance': '1', 'id': {'qid': 5773, 'language': 'en'}, 'title': 'firstQuestion',
              'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': 753774, 'same_default': 0,
              'qid': 5773, 'mandatory': 'Y'}],
            [{'other': 'N', 'parent_qid': 0, 'type': 'N', 'question_order': 3,
              'question': 'Participant Identification number<b>:</b>', 'modulename': None, 'relevance': '1',
              'id': {'qid': 5772, 'language': 'en'}, 'title': 'subjectid', 'language': 'en', 'gid': 1824, 'preg': '',
              'help': '', 'scale_id': 0, 'sid': 753774, 'same_default': 0, 'qid': 5772, 'mandatory': 'Y'},
             {'other': 'N', 'parent_qid': 0, 'type': 'D', 'question_order': 1,
              'question': 'Acquisition date<strong>:</strong><br />\n', 'modulename': None, 'relevance': '1',
              'id': {'qid': 5771, 'language': 'en'}, 'title': 'acquisitiondate', 'language': 'en', 'gid': 1824,
              'preg': '', 'help': '', 'scale_id': 0, 'sid': 753774, 'same_default': 0, 'qid': 5771, 'mandatory': 'Y'},
             {'other': 'N', 'parent_qid': 0, 'type': 'N', 'question_order': 0,
              'question': 'Responsible Identification number:', 'modulename': None, 'relevance': '1',
              'id': {'qid': 5770, 'language': 'en'}, 'title': 'responsibleid', 'language': 'en', 'gid': 1824,
              'preg': '', 'help': '', 'scale_id': 0, 'sid': 753774, 'same_default': 0, 'qid': 5770, 'mandatory': 'Y'}],
            [{'other': 'N', 'parent_qid': 0, 'type': '|', 'question_order': 3, 'question': 'Has fileupload?',
              'modulename': None, 'relevance': '1', 'id': {'qid': 5775, 'language': 'en'}, 'title': 'fileUpload',
              'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': 753774, 'same_default': 0,
              'qid': 5775, 'mandatory': 'N'},
             {'other': 'N', 'parent_qid': 0, 'type': 'T', 'question_order': 2, 'question': 'Second question',
              'modulename': '', 'relevance': '1', 'id': {'qid': 5774, 'language': 'en'}, 'title': 'secondQuestion',
              'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': 753774, 'same_default': 0,
              'qid': 5774, 'mandatory': 'Y'},
             {'other': 'N', 'parent_qid': 0, 'type': 'T', 'question_order': 1, 'question': 'First question',
              'modulename': '', 'relevance': '1', 'id': {'qid': 5773, 'language': 'en'}, 'title': 'firstQuestion',
              'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': 753774, 'same_default': 0,
              'qid': 5773, 'mandatory': 'Y'}, {'other': 'N', 'parent_qid': 0, 'type': 'N', 'question_order': 3,
                                               'question': 'Participant Identification number<b>:</b>',
                                               'modulename': None, 'relevance': '1',
                                               'id': {'qid': 5772, 'language': 'en'}, 'title': 'subjectid',
                                               'language': 'en', 'gid': 1824, 'preg': '', 'help': '', 'scale_id': 0,
                                               'sid': 753774, 'same_default': 0, 'qid': 5772, 'mandatory': 'Y'},
             {'other': 'N', 'parent_qid': 0, 'type': 'D', 'question_order': 1,
              'question': 'Acquisition date<strong>:</strong><br />\n', 'modulename': None, 'relevance': '1',
              'id': {'qid': 5771, 'language': 'en'}, 'title': 'acquisitiondate', 'language': 'en', 'gid': 1824,
              'preg': '', 'help': '', 'scale_id': 0, 'sid': 753774, 'same_default': 0, 'qid': 5771, 'mandatory': 'Y'},
             {'other': 'N', 'parent_qid': 0, 'type': 'N', 'question_order': 0,
              'question': 'Responsible Identification number:', 'modulename': None, 'relevance': '1',
              'id': {'qid': 5770, 'language': 'en'}, 'title': 'responsibleid', 'language': 'en', 'gid': 1824,
              'preg': '', 'help': '', 'scale_id': 0, 'sid': 753774, 'same_default': 0, 'qid': 5770, 'mandatory': 'Y'}]

        ]
        mockServer.return_value.get_question_properties.side_effect = [
            {'gid': 1825, 'question': 'Has fileupload?', 'subquestions': 'No available answers', 'type': '|',
             'question_order': 3, 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'attributes': 'No available attributes', 'other': 'N',
             'title': 'fileUpload'},
            {'gid': 1825, 'question': 'Second question', 'subquestions': 'No available answers', 'type': 'T',
             'question_order': 2, 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'attributes': 'No available attributes', 'other': 'N',
             'title': 'secondQuestion'},
            {'gid': 1825, 'question': 'First question', 'subquestions': 'No available answers', 'type': 'T',
             'question_order': 1, 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'attributes': 'No available attributes', 'other': 'N',
             'title': 'firstQuestion'},
            {'gid': 1824, 'question': 'Participant Identification number<b>:</b>',
             'subquestions': 'No available answers', 'type': 'N', 'question_order': 3,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'attributes': {'hidden': '1'}, 'other': 'N', 'title': 'subjectid'},
            {'gid': 1824, 'question': 'Acquisition date<strong>:</strong><br />\n',
             'subquestions': 'No available answers', 'type': 'D', 'question_order': 1,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'attributes': {'hidden': '1'}, 'other': 'N', 'title': 'acquisitiondate'},
            {'gid': 1824, 'question': 'Responsible Identification number:', 'subquestions': 'No available answers',
             'type': 'N', 'question_order': 0, 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'attributes': {'hidden': '1'}, 'other': 'N',
             'title': 'responsibleid'},
            {'gid': 1825, 'question': 'Has fileupload?', 'subquestions': 'No available answers', 'type': '|',
             'question_order': 3, 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'attributes': 'No available attributes', 'other': 'N',
             'title': 'fileUpload'},
            {'gid': 1825, 'question': 'Second question', 'subquestions': 'No available answers', 'type': 'T',
             'question_order': 2, 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'attributes': 'No available attributes', 'other': 'N',
             'title': 'secondQuestion'},
            {'gid': 1825, 'question': 'First question', 'subquestions': 'No available answers', 'type': 'T',
             'question_order': 1, 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'attributes': 'No available attributes', 'other': 'N',
             'title': 'firstQuestion'},
            {'gid': 1824, 'question': 'Participant Identification number<b>:</b>',
             'subquestions': 'No available answers', 'type': 'N', 'question_order': 3,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'attributes': {'hidden': '1'}, 'other': 'N', 'title': 'subjectid'},
            {'gid': 1824, 'question': 'Acquisition date<strong>:</strong><br />\n',
             'subquestions': 'No available answers', 'type': 'D', 'question_order': 1,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'attributes': {'hidden': '1'}, 'other': 'N', 'title': 'acquisitiondate'},
            {'gid': 1824, 'question': 'Responsible Identification number:', 'subquestions': 'No available answers',
             'type': 'N', 'question_order': 0, 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'attributes': {'hidden': '1'}, 'other': 'N',
             'title': 'responsibleid'}
        ]
        mockServer.return_value.get_language_properties.return_value = {'surveyls_title': 'Test questionnaire'}

        ## Ínicio - Estava no setUp
        # self.lime_survey = Questionnaires()

        # self.sid = self.create_limesurvey_questionnaire()

        # create questionnaire data collection in NES
        # TODO: use method already existent in patient.tests. See other places
        self.survey = create_survey(753774)
        self.data_configuration_tree = self.create_nes_questionnaire(
            self.root_component
        )

        # Add response's participant to limesurvey survey and the references
        # in our db
        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, self.subject_of_group.subject
        # )
        self.questionnaire_response = \
            ObjectsFactory.create_questionnaire_response(
                dct=self.data_configuration_tree,
                responsible=self.user, token_id=1,
                subject_of_group=self.subject_of_group
            )
        ## Fim - Estava no setUp

        # Create other component (step) QUESTIONNAIRE in same experimental
        # protocol, from LimeSurvey survey created in setUp
        # TODO: see if it's correct before commit. It's creating other questionnaire
        dct = self.create_nes_questionnaire(self.root_component)

        # Create one more patient/subject/subject_of_group besides those of
        # setUp
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = \
            ObjectsFactory.create_subject_of_group(self.group, subject)

        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, subject_of_group.subject
        # )
        ObjectsFactory.create_questionnaire_response(
            dct=dct,
            responsible=self.user, token_id=2,
            subject_of_group=subject_of_group
        )

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(753774) + '*Test '
                'questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(753774) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(753774) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(753774) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        self.assertTrue(
            any(os.path.join(
                'Per_questionnaire',
                'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Per_questionnaire',
                'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ) +
            'not in: ' + str(zipped_file.namelist())
        )
        self.assertTrue(any(os.path.join(
            'Per_questionnaire', 'Step_2_QUESTIONNAIRE', self.survey.code + '_test-questionnaire_en.csv')
                            in element for element in zipped_file.namelist()),
            os.path.join(
                'Per_questionnaire',
                'Step_2_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ) +
            'not in: ' + str(zipped_file.namelist())
        )

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    def test_same_questionnaire_used_in_different_steps_return_correct_responses_content_2(self):
        """
        With reuse
        """
        # by now: simple testing in browser is working (but, make this test ;)
        pass

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_two_groups_with_questionnaire_step_in_both_returns_correct_directory_structure(self, mockServer):
        mockServer.return_value.get_survey_properties.return_value = {'additional_languages': '', 'language': 'en'}
        mockServer.return_value.get_participant_properties.side_effect = [
            {'completed': '2019-06-26'},
            {'completed': '2019-06-26'},
            {'completed': '2019-06-26'},
            {'token': 'pO9iPqlkQzD4zwG'},
            {'completed': '2019-06-26'},
            {'token': 'g7GaPTLHc2rB6TV'},

        ]
        mockServer.return_value.export_responses.return_value = \
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVjb3VudF0iCiIxIiwiMjAxOS0wNi0yNiAxMTozNDo1MCIsIjIiLCJlbiIsImc3R2FQVExIYzJyQjZUViIsIjUzOTY3IiwiMjAxOS0wNi0yNiAxMTozNDo1MC43MDYzNzMiLCIxNzc0OTMiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoiMiIsIjIwMTktMDYtMjYgMTE6MzQ6NTEiLCIyIiwiZW4iLCJwTzlpUHFsa1F6RDR6d0ciLCI1Mzk2NyIsIjIwMTktMDYtMjYgMTE6MzQ6NTEuMzI0MzgiLCIxNzc0OTQiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoK'
        mockServer.return_value.list_groups.side_effect = [
            [{'grelevance': '', 'group_name': 'First group', 'group_order': 2, 'gid': 1835, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1835}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1834}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'zh-Hans', 'gid': 1834},
              'language': 'zh-Hans'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'nl', 'gid': 1834}, 'language': 'nl'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'fr', 'gid': 1834}, 'language': 'fr'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'de', 'gid': 1834}, 'language': 'de'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt-BR', 'gid': 1834}, 'language': 'pt-BR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'el', 'gid': 1834}, 'language': 'el'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'hi', 'gid': 1834}, 'language': 'hi'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'it', 'gid': 1834}, 'language': 'it'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ja', 'gid': 1834}, 'language': 'ja'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt', 'gid': 1834}, 'language': 'pt'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ru', 'gid': 1834}, 'language': 'ru'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es', 'gid': 1834}, 'language': 'es'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-AR', 'gid': 1834}, 'language': 'es-AR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-CL', 'gid': 1834}, 'language': 'es-CL'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-MX', 'gid': 1834}, 'language': 'es-MX'}],
            [{'grelevance': '', 'group_name': 'First group', 'group_order': 2, 'gid': 1835, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1835}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1834}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'zh-Hans', 'gid': 1834},
              'language': 'zh-Hans'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'nl', 'gid': 1834}, 'language': 'nl'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'fr', 'gid': 1834}, 'language': 'fr'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'de', 'gid': 1834}, 'language': 'de'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt-BR', 'gid': 1834}, 'language': 'pt-BR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'el', 'gid': 1834}, 'language': 'el'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'hi', 'gid': 1834}, 'language': 'hi'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'it', 'gid': 1834}, 'language': 'it'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ja', 'gid': 1834}, 'language': 'ja'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt', 'gid': 1834}, 'language': 'pt'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ru', 'gid': 1834}, 'language': 'ru'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es', 'gid': 1834}, 'language': 'es'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-AR', 'gid': 1834}, 'language': 'es-AR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-CL', 'gid': 1834}, 'language': 'es-CL'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-MX', 'gid': 1834}, 'language': 'es-MX'}],
            [{'grelevance': '', 'group_name': 'First group', 'group_order': 2, 'gid': 1835, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1835}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1834}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'zh-Hans', 'gid': 1834},
              'language': 'zh-Hans'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'nl', 'gid': 1834}, 'language': 'nl'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'fr', 'gid': 1834}, 'language': 'fr'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'de', 'gid': 1834}, 'language': 'de'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt-BR', 'gid': 1834}, 'language': 'pt-BR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'el', 'gid': 1834}, 'language': 'el'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'hi', 'gid': 1834}, 'language': 'hi'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'it', 'gid': 1834}, 'language': 'it'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ja', 'gid': 1834}, 'language': 'ja'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt', 'gid': 1834}, 'language': 'pt'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ru', 'gid': 1834}, 'language': 'ru'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es', 'gid': 1834}, 'language': 'es'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-AR', 'gid': 1834}, 'language': 'es-AR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-CL', 'gid': 1834}, 'language': 'es-CL'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-MX', 'gid': 1834}, 'language': 'es-MX'}],
            [{'grelevance': '', 'group_name': 'First group', 'group_order': 2, 'gid': 1835, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1835}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1834}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'zh-Hans', 'gid': 1834},
              'language': 'zh-Hans'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'nl', 'gid': 1834}, 'language': 'nl'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'fr', 'gid': 1834}, 'language': 'fr'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'de', 'gid': 1834}, 'language': 'de'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt-BR', 'gid': 1834}, 'language': 'pt-BR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'el', 'gid': 1834}, 'language': 'el'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'hi', 'gid': 1834}, 'language': 'hi'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'it', 'gid': 1834}, 'language': 'it'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ja', 'gid': 1834}, 'language': 'ja'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt', 'gid': 1834}, 'language': 'pt'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ru', 'gid': 1834}, 'language': 'ru'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es', 'gid': 1834}, 'language': 'es'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-AR', 'gid': 1834}, 'language': 'es-AR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-CL', 'gid': 1834}, 'language': 'es-CL'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-MX', 'gid': 1834}, 'language': 'es-MX'}],
            [{'grelevance': '', 'group_name': 'First group', 'group_order': 2, 'gid': 1835, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1835}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1834}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'zh-Hans', 'gid': 1834},
              'language': 'zh-Hans'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'nl', 'gid': 1834}, 'language': 'nl'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'fr', 'gid': 1834}, 'language': 'fr'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'de', 'gid': 1834}, 'language': 'de'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt-BR', 'gid': 1834}, 'language': 'pt-BR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'el', 'gid': 1834}, 'language': 'el'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'hi', 'gid': 1834}, 'language': 'hi'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'it', 'gid': 1834}, 'language': 'it'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ja', 'gid': 1834}, 'language': 'ja'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt', 'gid': 1834}, 'language': 'pt'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ru', 'gid': 1834}, 'language': 'ru'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es', 'gid': 1834}, 'language': 'es'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-AR', 'gid': 1834}, 'language': 'es-AR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-CL', 'gid': 1834}, 'language': 'es-CL'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-MX', 'gid': 1834}, 'language': 'es-MX'}],
            [{'grelevance': '', 'group_name': 'First group', 'group_order': 2, 'gid': 1835, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1835}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1834}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'zh-Hans', 'gid': 1834},
              'language': 'zh-Hans'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'nl', 'gid': 1834}, 'language': 'nl'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'fr', 'gid': 1834}, 'language': 'fr'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'de', 'gid': 1834}, 'language': 'de'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt-BR', 'gid': 1834}, 'language': 'pt-BR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'el', 'gid': 1834}, 'language': 'el'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'hi', 'gid': 1834}, 'language': 'hi'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'it', 'gid': 1834}, 'language': 'it'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ja', 'gid': 1834}, 'language': 'ja'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt', 'gid': 1834}, 'language': 'pt'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ru', 'gid': 1834}, 'language': 'ru'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es', 'gid': 1834}, 'language': 'es'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-AR', 'gid': 1834}, 'language': 'es-AR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-CL', 'gid': 1834}, 'language': 'es-CL'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-MX', 'gid': 1834}, 'language': 'es-MX'}],
            [{'grelevance': '', 'group_name': 'First group', 'group_order': 2, 'gid': 1835, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1835}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1834}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'zh-Hans', 'gid': 1834},
              'language': 'zh-Hans'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'nl', 'gid': 1834}, 'language': 'nl'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'fr', 'gid': 1834}, 'language': 'fr'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'de', 'gid': 1834}, 'language': 'de'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt-BR', 'gid': 1834}, 'language': 'pt-BR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'el', 'gid': 1834}, 'language': 'el'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'hi', 'gid': 1834}, 'language': 'hi'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'it', 'gid': 1834}, 'language': 'it'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ja', 'gid': 1834}, 'language': 'ja'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt', 'gid': 1834}, 'language': 'pt'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ru', 'gid': 1834}, 'language': 'ru'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es', 'gid': 1834}, 'language': 'es'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-AR', 'gid': 1834}, 'language': 'es-AR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-CL', 'gid': 1834}, 'language': 'es-CL'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-MX', 'gid': 1834}, 'language': 'es-MX'}],
            [{'grelevance': '', 'group_name': 'First group', 'group_order': 2, 'gid': 1835, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1835}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1834}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'zh-Hans', 'gid': 1834},
              'language': 'zh-Hans'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'nl', 'gid': 1834}, 'language': 'nl'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'fr', 'gid': 1834}, 'language': 'fr'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'de', 'gid': 1834}, 'language': 'de'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt-BR', 'gid': 1834}, 'language': 'pt-BR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'el', 'gid': 1834}, 'language': 'el'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'hi', 'gid': 1834}, 'language': 'hi'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'it', 'gid': 1834}, 'language': 'it'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ja', 'gid': 1834}, 'language': 'ja'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt', 'gid': 1834}, 'language': 'pt'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ru', 'gid': 1834}, 'language': 'ru'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es', 'gid': 1834}, 'language': 'es'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-AR', 'gid': 1834}, 'language': 'es-AR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-CL', 'gid': 1834}, 'language': 'es-CL'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-MX', 'gid': 1834}, 'language': 'es-MX'}],
            [{'grelevance': '', 'group_name': 'First group', 'group_order': 2, 'gid': 1835, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1835}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1834}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'zh-Hans', 'gid': 1834},
              'language': 'zh-Hans'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'nl', 'gid': 1834}, 'language': 'nl'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'fr', 'gid': 1834}, 'language': 'fr'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'de', 'gid': 1834}, 'language': 'de'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt-BR', 'gid': 1834}, 'language': 'pt-BR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'el', 'gid': 1834}, 'language': 'el'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'hi', 'gid': 1834}, 'language': 'hi'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'it', 'gid': 1834}, 'language': 'it'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ja', 'gid': 1834}, 'language': 'ja'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt', 'gid': 1834}, 'language': 'pt'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ru', 'gid': 1834}, 'language': 'ru'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es', 'gid': 1834}, 'language': 'es'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-AR', 'gid': 1834}, 'language': 'es-AR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-CL', 'gid': 1834}, 'language': 'es-CL'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-MX', 'gid': 1834}, 'language': 'es-MX'}],
            [{'grelevance': '', 'group_name': 'First group', 'group_order': 2, 'gid': 1835, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1835}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'en', 'gid': 1834}, 'language': 'en'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'zh-Hans', 'gid': 1834},
              'language': 'zh-Hans'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'nl', 'gid': 1834}, 'language': 'nl'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'fr', 'gid': 1834}, 'language': 'fr'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'de', 'gid': 1834}, 'language': 'de'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt-BR', 'gid': 1834}, 'language': 'pt-BR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'el', 'gid': 1834}, 'language': 'el'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'hi', 'gid': 1834}, 'language': 'hi'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'it', 'gid': 1834}, 'language': 'it'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ja', 'gid': 1834}, 'language': 'ja'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'pt', 'gid': 1834}, 'language': 'pt'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'ru', 'gid': 1834}, 'language': 'ru'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es', 'gid': 1834}, 'language': 'es'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-AR', 'gid': 1834}, 'language': 'es-AR'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-CL', 'gid': 1834}, 'language': 'es-CL'},
             {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
              'randomization_group': '', 'sid': 939763, 'id': {'language': 'es-MX', 'gid': 1834}, 'language': 'es-MX'}],


        ]
        mockServer.return_value.list_questions.side_effect = [
            [{'same_default': 0, 'parent_qid': 0, 'question': 'Has fileupload?', 'preg': '', 'question_order': 3,
              'other': 'N', 'modulename': None, 'type': '|', 'qid': 5805, 'mandatory': 'N', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5805, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'fileUpload', 'gid': 1835},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Second question', 'preg': '', 'question_order': 2,
              'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5804, 'mandatory': 'Y', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5804, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'secondQuestion', 'gid': 1835},
             {'same_default': 0, 'parent_qid': 0, 'question': 'First question', 'preg': '', 'question_order': 1,
              'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5803, 'mandatory': 'Y', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5803, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'firstQuestion', 'gid': 1835}],
            [{'same_default': 0, 'parent_qid': 0, 'question': 'Participant Identification number<b>:</b>', 'preg': '',
              'question_order': 3, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5802, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5802, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'subjectid', 'gid': 1834},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Acquisition date<strong>:</strong><br />\n', 'preg': '',
              'question_order': 1, 'other': 'N', 'modulename': None, 'type': 'D', 'qid': 5801, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5801, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'acquisitiondate', 'gid': 1834},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Responsible Identification number:', 'preg': '',
              'question_order': 0, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5800, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5800, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'responsibleid', 'gid': 1834}],
            [{'same_default': 0, 'parent_qid': 0, 'question': 'Has fileupload?', 'preg': '', 'question_order': 3,
              'other': 'N', 'modulename': None, 'type': '|', 'qid': 5805, 'mandatory': 'N', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5805, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'fileUpload', 'gid': 1835},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Second question', 'preg': '', 'question_order': 2,
              'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5804, 'mandatory': 'Y', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5804, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'secondQuestion', 'gid': 1835},
             {'same_default': 0, 'parent_qid': 0, 'question': 'First question', 'preg': '', 'question_order': 1,
              'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5803, 'mandatory': 'Y', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5803, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'firstQuestion', 'gid': 1835}],
            [{'same_default': 0, 'parent_qid': 0, 'question': 'Participant Identification number<b>:</b>', 'preg': '',
              'question_order': 3, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5802, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5802, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'subjectid', 'gid': 1834},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Acquisition date<strong>:</strong><br />\n', 'preg': '',
              'question_order': 1, 'other': 'N', 'modulename': None, 'type': 'D', 'qid': 5801, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5801, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'acquisitiondate', 'gid': 1834},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Responsible Identification number:', 'preg': '',
              'question_order': 0, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5800, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5800, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'responsibleid', 'gid': 1834}],
            [{'same_default': 0, 'parent_qid': 0, 'question': 'Has fileupload?', 'preg': '', 'question_order': 3,
              'other': 'N', 'modulename': None, 'type': '|', 'qid': 5805, 'mandatory': 'N', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5805, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'fileUpload', 'gid': 1835},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Second question', 'preg': '', 'question_order': 2,
              'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5804, 'mandatory': 'Y', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5804, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'secondQuestion', 'gid': 1835},
             {'same_default': 0, 'parent_qid': 0, 'question': 'First question', 'preg': '', 'question_order': 1,
              'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5803, 'mandatory': 'Y', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5803, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'firstQuestion', 'gid': 1835},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Participant Identification number<b>:</b>', 'preg': '',
              'question_order': 3, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5802, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5802, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'subjectid', 'gid': 1834},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Acquisition date<strong>:</strong><br />\n', 'preg': '',
              'question_order': 1, 'other': 'N', 'modulename': None, 'type': 'D', 'qid': 5801, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5801, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'acquisitiondate', 'gid': 1834},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Responsible Identification number:', 'preg': '',
              'question_order': 0, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5800, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5800, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'responsibleid', 'gid': 1834}],
            [{'same_default': 0, 'parent_qid': 0, 'question': 'Has fileupload?', 'preg': '', 'question_order': 3,
              'other': 'N', 'modulename': None, 'type': '|', 'qid': 5805, 'mandatory': 'N', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5805, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'fileUpload', 'gid': 1835},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Second question', 'preg': '', 'question_order': 2,
              'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5804, 'mandatory': 'Y', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5804, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'secondQuestion', 'gid': 1835},
             {'same_default': 0, 'parent_qid': 0, 'question': 'First question', 'preg': '', 'question_order': 1,
              'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5803, 'mandatory': 'Y', 'sid': 939763, 'help': '',
              'scale_id': 0, 'id': {'qid': 5803, 'language': 'en'}, 'relevance': '1', 'language': 'en',
              'title': 'firstQuestion', 'gid': 1835},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Participant Identification number<b>:</b>', 'preg': '',
              'question_order': 3, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5802, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5802, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'subjectid', 'gid': 1834},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Acquisition date<strong>:</strong><br />\n', 'preg': '',
              'question_order': 1, 'other': 'N', 'modulename': None, 'type': 'D', 'qid': 5801, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5801, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'acquisitiondate', 'gid': 1834},
             {'same_default': 0, 'parent_qid': 0, 'question': 'Responsible Identification number:', 'preg': '',
              'question_order': 0, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5800, 'mandatory': 'Y',
              'sid': 939763, 'help': '', 'scale_id': 0, 'id': {'qid': 5800, 'language': 'en'}, 'relevance': '1',
              'language': 'en', 'title': 'responsibleid', 'gid': 1834}]
        ]
        mockServer.return_value.get_question_properties.side_effect = [
            {'question': 'Has fileupload?', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': '|',
             'question_order': 3, 'subquestions': 'No available answers', 'other': 'N', 'title': 'fileUpload'},
            {'question': 'Second question', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'T',
             'question_order': 2, 'subquestions': 'No available answers', 'other': 'N', 'title': 'secondQuestion'},
            {'question': 'First question', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'T',
             'question_order': 1, 'subquestions': 'No available answers', 'other': 'N', 'title': 'firstQuestion'},
            {'question': 'Participant Identification number<b>:</b>', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'N',
             'question_order': 3, 'subquestions': 'No available answers', 'other': 'N', 'title': 'subjectid'},
            {'question': 'Acquisition date<strong>:</strong><br />\n', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'D',
             'question_order': 1, 'subquestions': 'No available answers', 'other': 'N', 'title': 'acquisitiondate'},
            {'question': 'Responsible Identification number:', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'N',
             'question_order': 0, 'subquestions': 'No available answers', 'other': 'N', 'title': 'responsibleid'},
            {'question': 'Has fileupload?', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': '|',
             'question_order': 3, 'subquestions': 'No available answers', 'other': 'N', 'title': 'fileUpload'},
            {'question': 'Second question', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'T',
             'question_order': 2, 'subquestions': 'No available answers', 'other': 'N', 'title': 'secondQuestion'},
            {'question': 'First question', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'T',
             'question_order': 1, 'subquestions': 'No available answers', 'other': 'N', 'title': 'firstQuestion'},
            {'question': 'Participant Identification number<b>:</b>', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'N',
             'question_order': 3, 'subquestions': 'No available answers', 'other': 'N', 'title': 'subjectid'},
            {'question': 'Acquisition date<strong>:</strong><br />\n', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'D',
             'question_order': 1, 'subquestions': 'No available answers', 'other': 'N', 'title': 'acquisitiondate'},
            {'question': 'Responsible Identification number:', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'N',
             'question_order': 0, 'subquestions': 'No available answers', 'other': 'N', 'title': 'responsibleid'},
            {'question': 'Has fileupload?', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': '|',
             'question_order': 3, 'subquestions': 'No available answers', 'other': 'N', 'title': 'fileUpload'},
            {'question': 'Second question', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'T',
             'question_order': 2, 'subquestions': 'No available answers', 'other': 'N', 'title': 'secondQuestion'},
            {'question': 'First question', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'T',
             'question_order': 1, 'subquestions': 'No available answers', 'other': 'N', 'title': 'firstQuestion'},
            {'question': 'Participant Identification number<b>:</b>', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'N',
             'question_order': 3, 'subquestions': 'No available answers', 'other': 'N', 'title': 'subjectid'},
            {'question': 'Acquisition date<strong>:</strong><br />\n', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'D',
             'question_order': 1, 'subquestions': 'No available answers', 'other': 'N', 'title': 'acquisitiondate'},
            {'question': 'Responsible Identification number:', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'N',
             'question_order': 0, 'subquestions': 'No available answers', 'other': 'N', 'title': 'responsibleid'},
            {'question': 'Has fileupload?', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': '|',
             'question_order': 3, 'subquestions': 'No available answers', 'other': 'N', 'title': 'fileUpload'},
            {'question': 'Second question', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'T',
             'question_order': 2, 'subquestions': 'No available answers', 'other': 'N', 'title': 'secondQuestion'},
            {'question': 'First question', 'attributes': 'No available attributes', 'gid': 1835,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'T',
             'question_order': 1, 'subquestions': 'No available answers', 'other': 'N', 'title': 'firstQuestion'},
            {'question': 'Participant Identification number<b>:</b>', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'N',
             'question_order': 3, 'subquestions': 'No available answers', 'other': 'N', 'title': 'subjectid'},
            {'question': 'Acquisition date<strong>:</strong><br />\n', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'D',
             'question_order': 1, 'subquestions': 'No available answers', 'other': 'N', 'title': 'acquisitiondate'},
            {'question': 'Responsible Identification number:', 'attributes': {'hidden': '1'}, 'gid': 1834,
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes', 'type': 'N',
             'question_order': 0, 'subquestions': 'No available answers', 'other': 'N', 'title': 'responsibleid'}
        ]
        mockServer.return_value.get_language_properties.return_value = {'surveyls_title': 'Test questionnaire'}

        ## Ínicio - Estava no setUp
        # self.lime_survey = Questionnaires()

        # self.sid = self.create_limesurvey_questionnaire()

        # create questionnaire data collection in NES
        # TODO: use method already existent in patient.tests. See other places
        self.survey = create_survey(939763)
        self.data_configuration_tree = self.create_nes_questionnaire(
            self.root_component
        )

        # Add response's participant to limesurvey survey and the references
        # in our db
        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, self.subject_of_group.subject
        # )
        self.questionnaire_response = \
            ObjectsFactory.create_questionnaire_response(
                dct=self.data_configuration_tree,
                responsible=self.user, token_id=1,
                subject_of_group=self.subject_of_group
            )
        ## Fim - Estava no setUp

        # create other group/experimental protocol
        root_component2 = ObjectsFactory.create_block(self.experiment)
        group2 = ObjectsFactory.create_group(self.experiment, root_component2)

        # create questionnaire component (reuse Survey created in setUp)
        dct2 = self.create_nes_questionnaire(root_component2)

        # create patient/subject/subject_of_group
        patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group2 = ObjectsFactory.create_subject_of_group(group2, subject)

        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, subject_of_group2.subject
        # )
        ObjectsFactory.create_questionnaire_response(
            dct=dct2,
            responsible=self.user, token_id=2,
            subject_of_group=subject_of_group2
        )

        self.append_session_variable(
            'group_selected_list', [str(self.group.id), str(group2.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(939763) + '*Test '
                'questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(939763) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(939763) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(939763) +
                '*Test questionnaire*fileUpload*fileUpload',

                '1*' + str(group2.id) + '*' + str(939763) + '*Test '
                'questionnaire*acquisitiondate*acquisitiondate',
                '1*' + str(group2.id) + '*' + str(939763) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '1*' + str(group2.id) + '*' + str(939763) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '1*' + str(group2.id) + '*' + str(939763) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }

        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # assertions for first group
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(self.group.title), 'Experimental_protocol'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(self.group.title), 'Experimental_Protocol'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(self.group.title), 'Per_participant'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(self.group.title), 'Per_participant'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(self.group.title), 'Per_questionnaire'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(self.group.title), 'Per_questionnaire'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(self.group.title), 'Questionnaire_metadata'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(self.group.title), 'Questionnaire_metadata'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )

        # assertions for second group
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group2.title), 'Experimental_protocol'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group2.title), 'Experimental_Protocol'
            ) +
            ' not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group2.title), 'Per_participant'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group2.title), 'Per_participant'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group2.title), 'Per_questionnaire'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group2.title), 'Per_questionnaire'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )
        self.assertTrue(
            any(os.path.join(
                'Group_' + slugify(group2.title), 'Questionnaire_metadata'
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group2.title), 'Questionnaire_metadata'
            ) +
            'not in:' +
            str(zipped_file.namelist())
        )

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_export_with_abbreviated_question_text(self, mockServer):
        mockServer.return_value.get_survey_properties.return_value = {'additional_languages': '', 'language': 'en'}
        mockServer.return_value.get_participant_properties.side_effect = [
            {'token': 'obyBy4HizUhe3j0'},
            {'completed': '2019-06-26'},
            {'completed': '2019-06-26'},
            {'token': 'obyBy4HizUhe3j0'}

        ]
        mockServer.return_value.export_responses.return_value = \
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVjb3VudF0iCiIxIiwiMjAxOS0wNi0yNiAxMzozNTo1NyIsIjIiLCJlbiIsIm9ieUJ5NEhpelVoZTNqMCIsIjUzOTc0IiwiMjAxOS0wNi0yNiAxMzozNTo1Ny42MDU3MzMiLCIxNzc1MDUiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoK'
        mockServer.return_value.export_responses_by_token.side_effect = [
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVjb3VudF0iCiIxIiwiMjAxOS0wNi0yNiAxMzo1NDo1NyIsIjIiLCJlbiIsImlPYVFLS2VsVmZTcUpROSIsIjUzOTc5IiwiMjAxOS0wNi0yNiAxMzo1NDo1Ny44NzczOTQiLCIxNzc1MTAiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoK',
            'IlJlc3BvbnNlIElEIiwiRGF0ZSBzdWJtaXR0ZWQiLCJMYXN0IHBhZ2UiLCJTdGFydCBsYW5ndWFnZSIsIlRva2VuIiwiUmVzcG9uc2libGUgSWRlLi4gIiwiQWNxdWlzaXRpb24gZGF0ZToiLCJQYXJ0aWNpcGFudCBJZGUuLiAiLCJGaXJzdCBxdWVzdGlvbiIsIlNlY29uZCBxdWVzdGlvbiIsIkhhcyBmaWxldXBsb2FkPyIsImZpbGVjb3VudCAtIEhhcy4uICIKIjEiLCIyMDE5LTA2LTI2IDEzOjU0OjU3IiwiMiIsImVuIiwiaU9hUUtLZWxWZlNxSlE5IiwiNTM5NzkiLCIyMDE5LTA2LTI2IDEzOjU0OjU3Ljg3NzM5NCIsIjE3NzUxMCIsIk9sw6EgTXVuZG8hIiwiSGFsbG8gV2VsdCEiLCIiLCIiCgo='
        ]
        mockServer.return_value.list_groups.side_effect = [
            [{'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 2, 'gid': 1841,
              'description': '', 'id': {'gid': 1841, 'language': 'en'}, 'group_name': 'First group', 'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'en'}, 'group_name': 'Identification',
              'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'zh-Hans'}, 'group_name': 'Identification',
              'language': 'zh-Hans'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'nl'}, 'group_name': 'Identification',
              'language': 'nl'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'fr'}, 'group_name': 'Identification',
              'language': 'fr'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'de'}, 'group_name': 'Identification',
              'language': 'de'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt-BR'}, 'group_name': 'Identification',
              'language': 'pt-BR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'el'}, 'group_name': 'Identification',
              'language': 'el'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'hi'}, 'group_name': 'Identification',
              'language': 'hi'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'it'}, 'group_name': 'Identification',
              'language': 'it'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ja'}, 'group_name': 'Identification',
              'language': 'ja'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt'}, 'group_name': 'Identification',
              'language': 'pt'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ru'}, 'group_name': 'Identification',
              'language': 'ru'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es'}, 'group_name': 'Identification',
              'language': 'es'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-AR'}, 'group_name': 'Identification',
              'language': 'es-AR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-CL'}, 'group_name': 'Identification',
              'language': 'es-CL'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-MX'}, 'group_name': 'Identification',
              'language': 'es-MX'}],
            [{'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 2, 'gid': 1841,
              'description': '', 'id': {'gid': 1841, 'language': 'en'}, 'group_name': 'First group', 'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'en'}, 'group_name': 'Identification',
              'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'zh-Hans'}, 'group_name': 'Identification',
              'language': 'zh-Hans'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'nl'}, 'group_name': 'Identification',
              'language': 'nl'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'fr'}, 'group_name': 'Identification',
              'language': 'fr'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'de'}, 'group_name': 'Identification',
              'language': 'de'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt-BR'}, 'group_name': 'Identification',
              'language': 'pt-BR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'el'}, 'group_name': 'Identification',
              'language': 'el'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'hi'}, 'group_name': 'Identification',
              'language': 'hi'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'it'}, 'group_name': 'Identification',
              'language': 'it'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ja'}, 'group_name': 'Identification',
              'language': 'ja'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt'}, 'group_name': 'Identification',
              'language': 'pt'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ru'}, 'group_name': 'Identification',
              'language': 'ru'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es'}, 'group_name': 'Identification',
              'language': 'es'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-AR'}, 'group_name': 'Identification',
              'language': 'es-AR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-CL'}, 'group_name': 'Identification',
              'language': 'es-CL'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-MX'}, 'group_name': 'Identification',
              'language': 'es-MX'}],
            [{'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 2, 'gid': 1841,
              'description': '', 'id': {'gid': 1841, 'language': 'en'}, 'group_name': 'First group', 'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'en'}, 'group_name': 'Identification',
              'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'zh-Hans'}, 'group_name': 'Identification',
              'language': 'zh-Hans'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'nl'}, 'group_name': 'Identification',
              'language': 'nl'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'fr'}, 'group_name': 'Identification',
              'language': 'fr'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'de'}, 'group_name': 'Identification',
              'language': 'de'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt-BR'}, 'group_name': 'Identification',
              'language': 'pt-BR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'el'}, 'group_name': 'Identification',
              'language': 'el'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'hi'}, 'group_name': 'Identification',
              'language': 'hi'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'it'}, 'group_name': 'Identification',
              'language': 'it'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ja'}, 'group_name': 'Identification',
              'language': 'ja'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt'}, 'group_name': 'Identification',
              'language': 'pt'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ru'}, 'group_name': 'Identification',
              'language': 'ru'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es'}, 'group_name': 'Identification',
              'language': 'es'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-AR'}, 'group_name': 'Identification',
              'language': 'es-AR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-CL'}, 'group_name': 'Identification',
              'language': 'es-CL'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-MX'}, 'group_name': 'Identification',
              'language': 'es-MX'}],
            [{'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 2, 'gid': 1841,
              'description': '', 'id': {'gid': 1841, 'language': 'en'}, 'group_name': 'First group', 'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'en'}, 'group_name': 'Identification',
              'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'zh-Hans'}, 'group_name': 'Identification',
              'language': 'zh-Hans'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'nl'}, 'group_name': 'Identification',
              'language': 'nl'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'fr'}, 'group_name': 'Identification',
              'language': 'fr'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'de'}, 'group_name': 'Identification',
              'language': 'de'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt-BR'}, 'group_name': 'Identification',
              'language': 'pt-BR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'el'}, 'group_name': 'Identification',
              'language': 'el'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'hi'}, 'group_name': 'Identification',
              'language': 'hi'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'it'}, 'group_name': 'Identification',
              'language': 'it'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ja'}, 'group_name': 'Identification',
              'language': 'ja'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt'}, 'group_name': 'Identification',
              'language': 'pt'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ru'}, 'group_name': 'Identification',
              'language': 'ru'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es'}, 'group_name': 'Identification',
              'language': 'es'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-AR'}, 'group_name': 'Identification',
              'language': 'es-AR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-CL'}, 'group_name': 'Identification',
              'language': 'es-CL'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-MX'}, 'group_name': 'Identification',
              'language': 'es-MX'}],
            [{'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 2, 'gid': 1841,
              'description': '', 'id': {'gid': 1841, 'language': 'en'}, 'group_name': 'First group', 'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'en'}, 'group_name': 'Identification',
              'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'zh-Hans'}, 'group_name': 'Identification',
              'language': 'zh-Hans'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'nl'}, 'group_name': 'Identification',
              'language': 'nl'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'fr'}, 'group_name': 'Identification',
              'language': 'fr'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'de'}, 'group_name': 'Identification',
              'language': 'de'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt-BR'}, 'group_name': 'Identification',
              'language': 'pt-BR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'el'}, 'group_name': 'Identification',
              'language': 'el'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'hi'}, 'group_name': 'Identification',
              'language': 'hi'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'it'}, 'group_name': 'Identification',
              'language': 'it'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ja'}, 'group_name': 'Identification',
              'language': 'ja'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt'}, 'group_name': 'Identification',
              'language': 'pt'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ru'}, 'group_name': 'Identification',
              'language': 'ru'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es'}, 'group_name': 'Identification',
              'language': 'es'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-AR'}, 'group_name': 'Identification',
              'language': 'es-AR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-CL'}, 'group_name': 'Identification',
              'language': 'es-CL'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-MX'}, 'group_name': 'Identification',
              'language': 'es-MX'}]

        ]
        mockServer.return_value.list_questions.side_effect = [
            [{'same_default': 0, 'type': '|', 'other': 'N', 'scale_id': 0, 'mandatory': 'N', 'question_order': 3,
              'modulename': None, 'sid': 199237, 'qid': 5823, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5823, 'language': 'en'}, 'question': 'Has fileupload?', 'relevance': '1',
              'title': 'fileUpload'},
             {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 2,
              'modulename': '', 'sid': 199237, 'qid': 5822, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5822, 'language': 'en'}, 'question': 'Second question', 'relevance': '1',
              'title': 'secondQuestion'},
             {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
              'modulename': '', 'sid': 199237, 'qid': 5821, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5821, 'language': 'en'}, 'question': 'First question', 'relevance': '1',
              'title': 'firstQuestion'}],
            [{'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 3,
              'modulename': None, 'sid': 199237, 'qid': 5820, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5820, 'language': 'en'},
              'question': 'Participant Identification number<b>:</b>', 'relevance': '1', 'title': 'subjectid'},
             {'same_default': 0, 'type': 'D', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
              'modulename': None, 'sid': 199237, 'qid': 5819, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5819, 'language': 'en'},
              'question': 'Acquisition date<strong>:</strong><br />\n', 'relevance': '1', 'title': 'acquisitiondate'},
             {'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 0,
              'modulename': None, 'sid': 199237, 'qid': 5818, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5818, 'language': 'en'}, 'question': 'Responsible Identification number:',
              'relevance': '1', 'title': 'responsibleid'}],
            [{'same_default': 0, 'type': '|', 'other': 'N', 'scale_id': 0, 'mandatory': 'N', 'question_order': 3,
              'modulename': None, 'sid': 199237, 'qid': 5823, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5823, 'language': 'en'}, 'question': 'Has fileupload?', 'relevance': '1',
              'title': 'fileUpload'},
             {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 2,
              'modulename': '', 'sid': 199237, 'qid': 5822, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5822, 'language': 'en'}, 'question': 'Second question', 'relevance': '1',
              'title': 'secondQuestion'},
             {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
              'modulename': '', 'sid': 199237, 'qid': 5821, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5821, 'language': 'en'}, 'question': 'First question', 'relevance': '1',
              'title': 'firstQuestion'},
             {'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 3,
              'modulename': None, 'sid': 199237, 'qid': 5820, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5820, 'language': 'en'},
              'question': 'Participant Identification number<b>:</b>', 'relevance': '1', 'title': 'subjectid'},
             {'same_default': 0, 'type': 'D', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
              'modulename': None, 'sid': 199237, 'qid': 5819, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5819, 'language': 'en'},
              'question': 'Acquisition date<strong>:</strong><br />\n', 'relevance': '1', 'title': 'acquisitiondate'},
             {'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 0,
              'modulename': None, 'sid': 199237, 'qid': 5818, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5818, 'language': 'en'}, 'question': 'Responsible Identification number:',
              'relevance': '1', 'title': 'responsibleid'}]
        ]
        mockServer.return_value.get_question_properties.side_effect = [
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'fileUpload', 'question_order': 3, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'Has fileupload?', 'attributes': 'No available attributes', 'type': '|'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'secondQuestion', 'question_order': 2, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'Second question', 'attributes': 'No available attributes', 'type': 'T'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'firstQuestion', 'question_order': 1, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'First question', 'attributes': 'No available attributes', 'type': 'T'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'subjectid', 'question_order': 3, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'attributes': {'hidden': '1'},
             'type': 'N'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'acquisitiondate', 'question_order': 1, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'attributes': {'hidden': '1'},
             'type': 'D'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'responsibleid', 'question_order': 0, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Responsible Identification number:', 'attributes': {'hidden': '1'},
             'type': 'N'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'fileUpload', 'question_order': 3, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'Has fileupload?', 'attributes': 'No available attributes', 'type': '|'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'secondQuestion', 'question_order': 2, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'Second question', 'attributes': 'No available attributes', 'type': 'T'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'firstQuestion', 'question_order': 1, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'First question', 'attributes': 'No available attributes', 'type': 'T'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'subjectid', 'question_order': 3, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'attributes': {'hidden': '1'},
             'type': 'N'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'acquisitiondate', 'question_order': 1, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'attributes': {'hidden': '1'},
             'type': 'D'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'responsibleid', 'question_order': 0, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Responsible Identification number:', 'attributes': {'hidden': '1'}, 'type': 'N'}
        ]
        mockServer.return_value.get_language_properties.return_value = {'surveyls_title': 'Test questionnaire'}

        ## Ínicio - Estava no setUp
        # self.lime_survey = Questionnaires()

        # self.sid = self.create_limesurvey_questionnaire()

        # create questionnaire data collection in NES
        # TODO: use method already existent in patient.tests. See other places
        self.survey = create_survey(199237)
        self.data_configuration_tree = self.create_nes_questionnaire(
            self.root_component
        )

        # Add response's participant to limesurvey survey and the references
        # in our db
        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, self.subject_of_group.subject
        # )
        self.questionnaire_response = \
            ObjectsFactory.create_questionnaire_response(
                dct=self.data_configuration_tree,
                responsible=self.user, token_id=1,
                subject_of_group=self.subject_of_group
            )
        ## Fim - Estava no setUp

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['abbreviated'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(199237) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(199237) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(199237) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(199237) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ), temp_dir
        )

        with open(
                os.path.join(
                    temp_dir,
                    'NES_EXPORT',
                    'Experiment_data',
                    'Group_' + self.group.title.lower(),
                    'Per_questionnaire',
                    'Step_1_QUESTIONNAIRE',
                    self.survey.code + '_test-questionnaire_en.csv'
                )
        ) as file:
            csv_line1 = next(csv.reader(file))
            self.assertEqual(len(csv_line1), 6)

        shutil.rmtree(temp_dir)
        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_reusing_experimental_protocol_in_two_groups_returns_correct_directory_structure(self, mockServer):
        mockServer.return_value.get_survey_properties.return_value = {'language': 'en', 'additional_languages': ''}
        mockServer.return_value.get_participant_properties.side_effect = [
            {'completed': '2019-06-26'},
            {'completed': '2019-06-26'},
            {'completed': '2019-06-26'},
            {'token': 'QGQ179PE0cUlkh7'},
            {'completed': '2019-06-26'},
            {'token': '0IwhuLul4lRmNjD'}
        ]
        mockServer.return_value.export_responses.return_value = \
        'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVjb3VudF0iCiIxIiwiMjAxOS0wNi0yNiAxNDowNTowMyIsIjIiLCJlbiIsIlFHUTE3OVBFMGNVbGtoNyIsIjUzOTgzIiwiMjAxOS0wNi0yNiAxNDowNTowMy4wNzEyMjQiLCIxNzc1MTUiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoiMiIsIjIwMTktMDYtMjYgMTQ6MDU6MDQiLCIyIiwiZW4iLCIwSXdodUx1bDRsUm1OakQiLCI1Mzk4MyIsIjIwMTktMDYtMjYgMTQ6MDU6MDQuMTM5MTc1IiwiMTc3NTE2IiwiT2zDoSBNdW5kbyEiLCJIYWxsbyBXZWx0ISIsIiIsIiIKCg=='
        mockServer.return_value.list_groups.side_effect = [
            [{'language': 'en', 'grelevance': '', 'gid': 1850, 'id': {'language': 'en', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'zh-Hans', 'grelevance': '', 'gid': 1850, 'id': {'language': 'zh-Hans', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'nl', 'grelevance': '', 'gid': 1850, 'id': {'language': 'nl', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'fr', 'grelevance': '', 'gid': 1850, 'id': {'language': 'fr', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'de', 'grelevance': '', 'gid': 1850, 'id': {'language': 'de', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'pt-BR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt-BR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'el', 'grelevance': '', 'gid': 1850, 'id': {'language': 'el', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'hi', 'grelevance': '', 'gid': 1850, 'id': {'language': 'hi', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'it', 'grelevance': '', 'gid': 1850, 'id': {'language': 'it', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ja', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ja', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'pt', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ru', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ru', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'es', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'es-AR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-AR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-CL', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-CL', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-MX', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-MX', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'en', 'grelevance': '', 'gid': 1851, 'id': {'language': 'en', 'gid': 1851},
                                  'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'First group',
                                  'group_order': 2}],
            [{'language': 'en', 'grelevance': '', 'gid': 1850, 'id': {'language': 'en', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'zh-Hans', 'grelevance': '', 'gid': 1850, 'id': {'language': 'zh-Hans', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'nl', 'grelevance': '', 'gid': 1850, 'id': {'language': 'nl', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'fr', 'grelevance': '', 'gid': 1850, 'id': {'language': 'fr', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'de', 'grelevance': '', 'gid': 1850, 'id': {'language': 'de', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'pt-BR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt-BR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'el', 'grelevance': '', 'gid': 1850, 'id': {'language': 'el', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'hi', 'grelevance': '', 'gid': 1850, 'id': {'language': 'hi', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'it', 'grelevance': '', 'gid': 1850, 'id': {'language': 'it', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ja', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ja', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'pt', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ru', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ru', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'es', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'es-AR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-AR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-CL', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-CL', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-MX', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-MX', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'en', 'grelevance': '', 'gid': 1851, 'id': {'language': 'en', 'gid': 1851},
                                  'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'First group',
                                  'group_order': 2}],
            [{'language': 'en', 'grelevance': '', 'gid': 1850, 'id': {'language': 'en', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'zh-Hans', 'grelevance': '', 'gid': 1850, 'id': {'language': 'zh-Hans', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'nl', 'grelevance': '', 'gid': 1850, 'id': {'language': 'nl', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'fr', 'grelevance': '', 'gid': 1850, 'id': {'language': 'fr', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'de', 'grelevance': '', 'gid': 1850, 'id': {'language': 'de', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'pt-BR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt-BR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'el', 'grelevance': '', 'gid': 1850, 'id': {'language': 'el', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'hi', 'grelevance': '', 'gid': 1850, 'id': {'language': 'hi', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'it', 'grelevance': '', 'gid': 1850, 'id': {'language': 'it', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ja', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ja', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'pt', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ru', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ru', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'es', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'es-AR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-AR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-CL', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-CL', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-MX', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-MX', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'en', 'grelevance': '', 'gid': 1851, 'id': {'language': 'en', 'gid': 1851},
                                  'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'First group',
                                  'group_order': 2}],
            [{'language': 'en', 'grelevance': '', 'gid': 1850, 'id': {'language': 'en', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'zh-Hans', 'grelevance': '', 'gid': 1850, 'id': {'language': 'zh-Hans', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'nl', 'grelevance': '', 'gid': 1850, 'id': {'language': 'nl', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'fr', 'grelevance': '', 'gid': 1850, 'id': {'language': 'fr', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'de', 'grelevance': '', 'gid': 1850, 'id': {'language': 'de', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'pt-BR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt-BR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'el', 'grelevance': '', 'gid': 1850, 'id': {'language': 'el', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'hi', 'grelevance': '', 'gid': 1850, 'id': {'language': 'hi', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'it', 'grelevance': '', 'gid': 1850, 'id': {'language': 'it', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ja', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ja', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'pt', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ru', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ru', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'es', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'es-AR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-AR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-CL', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-CL', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-MX', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-MX', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'en', 'grelevance': '', 'gid': 1851, 'id': {'language': 'en', 'gid': 1851},
                                  'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'First group',
                                  'group_order': 2}],
            [{'language': 'en', 'grelevance': '', 'gid': 1850, 'id': {'language': 'en', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'zh-Hans', 'grelevance': '', 'gid': 1850, 'id': {'language': 'zh-Hans', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'nl', 'grelevance': '', 'gid': 1850, 'id': {'language': 'nl', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'fr', 'grelevance': '', 'gid': 1850, 'id': {'language': 'fr', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'de', 'grelevance': '', 'gid': 1850, 'id': {'language': 'de', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'pt-BR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt-BR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'el', 'grelevance': '', 'gid': 1850, 'id': {'language': 'el', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'hi', 'grelevance': '', 'gid': 1850, 'id': {'language': 'hi', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'it', 'grelevance': '', 'gid': 1850, 'id': {'language': 'it', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ja', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ja', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'pt', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ru', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ru', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'es', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'es-AR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-AR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-CL', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-CL', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-MX', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-MX', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'en', 'grelevance': '', 'gid': 1851, 'id': {'language': 'en', 'gid': 1851},
                                  'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'First group',
                                  'group_order': 2}],
            [{'language': 'en', 'grelevance': '', 'gid': 1850, 'id': {'language': 'en', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'zh-Hans', 'grelevance': '', 'gid': 1850, 'id': {'language': 'zh-Hans', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'nl', 'grelevance': '', 'gid': 1850, 'id': {'language': 'nl', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'fr', 'grelevance': '', 'gid': 1850, 'id': {'language': 'fr', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'de', 'grelevance': '', 'gid': 1850, 'id': {'language': 'de', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'pt-BR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt-BR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'el', 'grelevance': '', 'gid': 1850, 'id': {'language': 'el', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'hi', 'grelevance': '', 'gid': 1850, 'id': {'language': 'hi', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'it', 'grelevance': '', 'gid': 1850, 'id': {'language': 'it', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ja', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ja', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'pt', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ru', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ru', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'es', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'es-AR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-AR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-CL', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-CL', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-MX', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-MX', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'en', 'grelevance': '', 'gid': 1851, 'id': {'language': 'en', 'gid': 1851},
                                  'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'First group',
                                  'group_order': 2}],
            [{'language': 'en', 'grelevance': '', 'gid': 1850, 'id': {'language': 'en', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'zh-Hans', 'grelevance': '', 'gid': 1850, 'id': {'language': 'zh-Hans', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'nl', 'grelevance': '', 'gid': 1850, 'id': {'language': 'nl', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'fr', 'grelevance': '', 'gid': 1850, 'id': {'language': 'fr', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'de', 'grelevance': '', 'gid': 1850, 'id': {'language': 'de', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'pt-BR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt-BR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'el', 'grelevance': '', 'gid': 1850, 'id': {'language': 'el', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'hi', 'grelevance': '', 'gid': 1850, 'id': {'language': 'hi', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'it', 'grelevance': '', 'gid': 1850, 'id': {'language': 'it', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ja', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ja', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'pt', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ru', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ru', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'es', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'es-AR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-AR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-CL', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-CL', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-MX', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-MX', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'en', 'grelevance': '', 'gid': 1851, 'id': {'language': 'en', 'gid': 1851},
                                  'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'First group',
                                  'group_order': 2}],
            [{'language': 'en', 'grelevance': '', 'gid': 1850, 'id': {'language': 'en', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'zh-Hans', 'grelevance': '', 'gid': 1850, 'id': {'language': 'zh-Hans', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'nl', 'grelevance': '', 'gid': 1850, 'id': {'language': 'nl', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'fr', 'grelevance': '', 'gid': 1850, 'id': {'language': 'fr', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'de', 'grelevance': '', 'gid': 1850, 'id': {'language': 'de', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'pt-BR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt-BR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'el', 'grelevance': '', 'gid': 1850, 'id': {'language': 'el', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'hi', 'grelevance': '', 'gid': 1850, 'id': {'language': 'hi', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'it', 'grelevance': '', 'gid': 1850, 'id': {'language': 'it', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ja', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ja', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'pt', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ru', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ru', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'es', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'es-AR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-AR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-CL', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-CL', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-MX', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-MX', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'en', 'grelevance': '', 'gid': 1851, 'id': {'language': 'en', 'gid': 1851},
                                  'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'First group',
                                  'group_order': 2}],
            [{'language': 'en', 'grelevance': '', 'gid': 1850, 'id': {'language': 'en', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'zh-Hans', 'grelevance': '', 'gid': 1850, 'id': {'language': 'zh-Hans', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'nl', 'grelevance': '', 'gid': 1850, 'id': {'language': 'nl', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'fr', 'grelevance': '', 'gid': 1850, 'id': {'language': 'fr', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'de', 'grelevance': '', 'gid': 1850, 'id': {'language': 'de', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'pt-BR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt-BR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'el', 'grelevance': '', 'gid': 1850, 'id': {'language': 'el', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'hi', 'grelevance': '', 'gid': 1850, 'id': {'language': 'hi', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'it', 'grelevance': '', 'gid': 1850, 'id': {'language': 'it', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ja', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ja', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'pt', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ru', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ru', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'es', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'es-AR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-AR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-CL', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-CL', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-MX', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-MX', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'en', 'grelevance': '', 'gid': 1851, 'id': {'language': 'en', 'gid': 1851},
                                  'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'First group',
                                  'group_order': 2}],
            [{'language': 'en', 'grelevance': '', 'gid': 1850, 'id': {'language': 'en', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'zh-Hans', 'grelevance': '', 'gid': 1850, 'id': {'language': 'zh-Hans', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'nl', 'grelevance': '', 'gid': 1850, 'id': {'language': 'nl', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'fr', 'grelevance': '', 'gid': 1850, 'id': {'language': 'fr', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'de', 'grelevance': '', 'gid': 1850, 'id': {'language': 'de', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'pt-BR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt-BR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'el', 'grelevance': '', 'gid': 1850, 'id': {'language': 'el', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'hi', 'grelevance': '', 'gid': 1850, 'id': {'language': 'hi', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'it', 'grelevance': '', 'gid': 1850, 'id': {'language': 'it', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ja', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ja', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'pt', 'grelevance': '', 'gid': 1850, 'id': {'language': 'pt', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'ru', 'grelevance': '', 'gid': 1850, 'id': {'language': 'ru', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'es', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es', 'gid': 1850},
                                  'randomization_group': '', 'sid': 191731, 'description': '',
                                  'group_name': 'Identification', 'group_order': 1},
             {'language': 'es-AR', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-AR', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-CL', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-CL', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1},
             {'language': 'es-MX', 'grelevance': '', 'gid': 1850, 'id': {'language': 'es-MX', 'gid': 1850},
              'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'Identification',
              'group_order': 1}, {'language': 'en', 'grelevance': '', 'gid': 1851, 'id': {'language': 'en', 'gid': 1851},
                                  'randomization_group': '', 'sid': 191731, 'description': '', 'group_name': 'First group',
                                  'group_order': 2}]
        ]
        mockServer.return_value.list_questions.side_effect = [
            [{'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5848}, 'type': 'N', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Responsible Identification number:', 'modulename': None, 'help': '', 'qid': 5848,
              'title': 'responsibleid', 'preg': '', 'mandatory': 'Y', 'question_order': 0},
             {'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5849}, 'type': 'D', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Acquisition date<strong>:</strong><br />\n', 'modulename': None, 'help': '', 'qid': 5849,
              'title': 'acquisitiondate', 'preg': '', 'mandatory': 'Y', 'question_order': 1},
             {'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5850}, 'type': 'N', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Participant Identification number<b>:</b>', 'modulename': None, 'help': '', 'qid': 5850,
              'title': 'subjectid', 'preg': '', 'mandatory': 'Y', 'question_order': 3}],
            [{'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5853}, 'type': '|', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Has fileupload?', 'modulename': None, 'help': '', 'qid': 5853, 'title': 'fileUpload', 'preg': '',
              'mandatory': 'N', 'question_order': 3},
             {'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5852}, 'type': 'T', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Second question', 'modulename': '', 'help': '', 'qid': 5852, 'title': 'secondQuestion',
              'preg': '', 'mandatory': 'Y', 'question_order': 2},
             {'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5851}, 'type': 'T', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'First question', 'modulename': '', 'help': '', 'qid': 5851, 'title': 'firstQuestion', 'preg': '',
              'mandatory': 'Y', 'question_order': 1}],
            [{'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5848}, 'type': 'N', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Responsible Identification number:', 'modulename': None, 'help': '', 'qid': 5848,
              'title': 'responsibleid', 'preg': '', 'mandatory': 'Y', 'question_order': 0},
             {'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5849}, 'type': 'D', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Acquisition date<strong>:</strong><br />\n', 'modulename': None, 'help': '', 'qid': 5849,
              'title': 'acquisitiondate', 'preg': '', 'mandatory': 'Y', 'question_order': 1},
             {'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5850}, 'type': 'N', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Participant Identification number<b>:</b>', 'modulename': None, 'help': '', 'qid': 5850,
              'title': 'subjectid', 'preg': '', 'mandatory': 'Y', 'question_order': 3}],
            [{'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5853}, 'type': '|', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Has fileupload?', 'modulename': None, 'help': '', 'qid': 5853, 'title': 'fileUpload', 'preg': '',
              'mandatory': 'N', 'question_order': 3},
             {'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5852}, 'type': 'T', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Second question', 'modulename': '', 'help': '', 'qid': 5852, 'title': 'secondQuestion',
              'preg': '', 'mandatory': 'Y', 'question_order': 2},
             {'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5851}, 'type': 'T', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'First question', 'modulename': '', 'help': '', 'qid': 5851, 'title': 'firstQuestion', 'preg': '',
              'mandatory': 'Y', 'question_order': 1}],
            [{'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5848}, 'type': 'N', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Responsible Identification number:', 'modulename': None, 'help': '', 'qid': 5848,
              'title': 'responsibleid', 'preg': '', 'mandatory': 'Y', 'question_order': 0},
             {'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5849}, 'type': 'D', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Acquisition date<strong>:</strong><br />\n', 'modulename': None, 'help': '', 'qid': 5849,
              'title': 'acquisitiondate', 'preg': '', 'mandatory': 'Y', 'question_order': 1},
             {'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5850}, 'type': 'N', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Participant Identification number<b>:</b>', 'modulename': None, 'help': '', 'qid': 5850,
              'title': 'subjectid', 'preg': '', 'mandatory': 'Y', 'question_order': 3},
             {'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5851}, 'type': 'T', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'First question', 'modulename': '', 'help': '', 'qid': 5851, 'title': 'firstQuestion', 'preg': '',
              'mandatory': 'Y', 'question_order': 1},
             {'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5852}, 'type': 'T', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Second question', 'modulename': '', 'help': '', 'qid': 5852, 'title': 'secondQuestion',
              'preg': '', 'mandatory': 'Y', 'question_order': 2},
             {'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5853}, 'type': '|', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Has fileupload?', 'modulename': None, 'help': '', 'qid': 5853, 'title': 'fileUpload', 'preg': '',
              'mandatory': 'N', 'question_order': 3}],
            [{'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5848}, 'type': 'N', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Responsible Identification number:', 'modulename': None, 'help': '', 'qid': 5848,
              'title': 'responsibleid', 'preg': '', 'mandatory': 'Y', 'question_order': 0},
             {'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5849}, 'type': 'D', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Acquisition date<strong>:</strong><br />\n', 'modulename': None, 'help': '', 'qid': 5849,
              'title': 'acquisitiondate', 'preg': '', 'mandatory': 'Y', 'question_order': 1},
             {'language': 'en', 'scale_id': 0, 'gid': 1850, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5850}, 'type': 'N', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Participant Identification number<b>:</b>', 'modulename': None, 'help': '', 'qid': 5850,
              'title': 'subjectid', 'preg': '', 'mandatory': 'Y', 'question_order': 3},
             {'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5851}, 'type': 'T', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'First question', 'modulename': '', 'help': '', 'qid': 5851, 'title': 'firstQuestion', 'preg': '',
              'mandatory': 'Y', 'question_order': 1},
             {'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5852}, 'type': 'T', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Second question', 'modulename': '', 'help': '', 'qid': 5852, 'title': 'secondQuestion',
              'preg': '', 'mandatory': 'Y', 'question_order': 2},
             {'language': 'en', 'scale_id': 0, 'gid': 1851, 'parent_qid': 0, 'other': 'N',
              'id': {'language': 'en', 'qid': 5853}, 'type': '|', 'sid': 191731, 'same_default': 0, 'relevance': '1',
              'question': 'Has fileupload?', 'modulename': None, 'help': '', 'qid': 5853, 'title': 'fileUpload', 'preg': '',
              'mandatory': 'N', 'question_order': 3}]
        ]
        mockServer.return_value.get_question_properties.side_effect = [
            {'other': 'N', 'question': 'Responsible Identification number:', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'responsibleid', 'type': 'N',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 0, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'acquisitiondate', 'type': 'D',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 1, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'subjectid', 'type': 'N',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 3, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'Has fileupload?', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'fileUpload', 'type': '|', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 3, 'attributes': 'No available attributes'},
            {'other': 'N', 'question': 'Second question', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'secondQuestion', 'type': 'T', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 2, 'attributes': 'No available attributes'},
            {'other': 'N', 'question': 'First question', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'firstQuestion', 'type': 'T', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 1, 'attributes': 'No available '
                                                                                              'attributes'},
            {'other': 'N', 'question': 'Responsible Identification number:', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'responsibleid', 'type': 'N',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 0, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'acquisitiondate', 'type': 'D',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 1, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'subjectid', 'type': 'N',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 3, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'Has fileupload?', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'fileUpload', 'type': '|', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 3, 'attributes': 'No available attributes'},
            {'other': 'N', 'question': 'Second question', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'secondQuestion', 'type': 'T', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 2, 'attributes': 'No available attributes'},
            {'other': 'N', 'question': 'First question', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'firstQuestion', 'type': 'T', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 1, 'attributes': 'No available attributes'},
            {'other': 'N', 'question': 'Responsible Identification number:', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'responsibleid', 'type': 'N',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 0, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'acquisitiondate', 'type': 'D',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 1, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'subjectid', 'type': 'N',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 3, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'First question', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'firstQuestion', 'type': 'T', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 1, 'attributes': 'No available attributes'},
            {'other': 'N', 'question': 'Second question', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'secondQuestion', 'type': 'T', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 2, 'attributes': 'No available attributes'},
            {'other': 'N', 'question': 'Has fileupload?', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'fileUpload', 'type': '|', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 3, 'attributes': 'No available attributes'},
            {'other': 'N', 'question': 'Responsible Identification number:', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'responsibleid', 'type': 'N',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 0, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'acquisitiondate', 'type': 'D',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 1, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'gid': 1850,
             'subquestions': 'No available answers', 'title': 'subjectid', 'type': 'N',
             'answeroptions': 'No available answer options', 'attributes_lang': 'No available attributes',
             'question_order': 3, 'attributes': {'hidden': '1'}},
            {'other': 'N', 'question': 'First question', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'firstQuestion', 'type': 'T', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 1, 'attributes': 'No available attributes'},
            {'other': 'N', 'question': 'Second question', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'secondQuestion', 'type': 'T', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 2, 'attributes': 'No available attributes'},
            {'other': 'N', 'question': 'Has fileupload?', 'gid': 1851, 'subquestions': 'No available answers',
             'title': 'fileUpload', 'type': '|', 'answeroptions': 'No available answer options',
             'attributes_lang': 'No available attributes', 'question_order': 3, 'attributes': 'No available attributes'}
        ]

        mockServer.return_value.get_language_properties.return_value = {'surveyls_title': 'Test questionnaire'}

        ## Ínicio - Estava no setUp
        # self.lime_survey = Questionnaires()

        # self.sid = self.create_limesurvey_questionnaire()

        # create questionnaire data collection in NES
        # TODO: use method already existent in patient.tests. See other places
        self.survey = create_survey(191731)
        self.data_configuration_tree = self.create_nes_questionnaire(
            self.root_component
        )

        # Add response's participant to limesurvey survey and the references
        # in our db
        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, self.subject_of_group.subject
        # )
        self.questionnaire_response = \
            ObjectsFactory.create_questionnaire_response(
                dct=self.data_configuration_tree,
                responsible=self.user, token_id=1,
                subject_of_group=self.subject_of_group
            )
        ## Fim - Estava no setUp

        # create other group and associate the same experimental protocol
        group2 = ObjectsFactory.create_group(self.experiment, self.root_component)

        # create patient/subject/subject_of_group
        patient2 = UtilTests().create_patient(changed_by=self.user)
        subject2 = ObjectsFactory.create_subject(patient2)
        subject_of_group2 = ObjectsFactory.create_subject_of_group(group2, subject2)

        # TODO: before commit add this comment in other tests
        # add response to limesurvey survey and the references in our db
        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, subject_of_group2.subject
        # )
        ObjectsFactory.create_questionnaire_response(
            dct=self.data_configuration_tree,
            responsible=self.user, token_id=2,
            subject_of_group=subject_of_group2
        )

        self.append_session_variable(
            'group_selected_list', [str(self.group.id), str(group2.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['code'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(191731) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(191731) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(191731) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(191731) +
                '*Test questionnaire*fileUpload*fileUpload',

                '1*' + str(group2.id) + '*' + str(191731) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '1*' + str(group2.id) + '*' + str(191731) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '1*' + str(group2.id) + '*' + str(191731) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '1*' + str(group2.id) + '*' + str(191731) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # assertions for first group
        self.assertFalse(
            any(os.path.join(
                'Group_' + slugify(self.group.title), 'Per_participant',
                'Participant_' + patient2.code
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(self.group.title), 'Per_participant',
                'Participant_' + patient2.code
            ) + ' is in: ' + str(zipped_file.namelist())
        )
        self.assertFalse(
            any(os.path.join(
                'Group_' + slugify(group2.title), 'Per_participant',
                'Participant_' + self.patient.code
            ) in element for element in zipped_file.namelist()),
            os.path.join(
                'Group_' + slugify(group2.title), 'Per_participant',
                'Participant_' + self.patient.code
            ) + ' is in: ' + str(zipped_file.namelist())
        )

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_participant_age_in_responses_is_age_when_questionnaire_was_filled_1(self, mockServer):
        """Test over experiment questionnaire response"""

        mockServer.return_value.get_survey_properties.return_value = {'additional_languages': '', 'language': 'en'}
        mockServer.return_value.get_participant_properties.side_effect = [
            {'token': 'obyBy4HizUhe3j0'},
            {'completed': '2019-06-26'},
            {'completed': '2019-06-26'},
            {'token': 'obyBy4HizUhe3j0'}

        ]
        mockServer.return_value.export_responses.return_value = \
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVjb3VudF0iCiIxIiwiMjAxOS0wNi0yNiAxMzozNTo1NyIsIjIiLCJlbiIsIm9ieUJ5NEhpelVoZTNqMCIsIjUzOTc0IiwiMjAxOS0wNi0yNiAxMzozNTo1Ny42MDU3MzMiLCIxNzc1MDUiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoK'
        mockServer.return_value.export_responses_by_token.side_effect = [
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVjb3VudF0iCiIxIiwiMjAxOS0wNi0yNiAxMzo1NDo1NyIsIjIiLCJlbiIsImlPYVFLS2VsVmZTcUpROSIsIjUzOTc5IiwiMjAxOS0wNi0yNiAxMzo1NDo1Ny44NzczOTQiLCIxNzc1MTAiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoK',
            'IlJlc3BvbnNlIElEIiwiRGF0ZSBzdWJtaXR0ZWQiLCJMYXN0IHBhZ2UiLCJTdGFydCBsYW5ndWFnZSIsIlRva2VuIiwiUmVzcG9uc2libGUgSWRlLi4gIiwiQWNxdWlzaXRpb24gZGF0ZToiLCJQYXJ0aWNpcGFudCBJZGUuLiAiLCJGaXJzdCBxdWVzdGlvbiIsIlNlY29uZCBxdWVzdGlvbiIsIkhhcyBmaWxldXBsb2FkPyIsImZpbGVjb3VudCAtIEhhcy4uICIKIjEiLCIyMDE5LTA2LTI2IDEzOjU0OjU3IiwiMiIsImVuIiwiaU9hUUtLZWxWZlNxSlE5IiwiNTM5NzkiLCIyMDE5LTA2LTI2IDEzOjU0OjU3Ljg3NzM5NCIsIjE3NzUxMCIsIk9sw6EgTXVuZG8hIiwiSGFsbG8gV2VsdCEiLCIiLCIiCgo='
        ]
        mockServer.return_value.list_groups.side_effect = [
            [{'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 2, 'gid': 1841,
              'description': '', 'id': {'gid': 1841, 'language': 'en'}, 'group_name': 'First group', 'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'en'}, 'group_name': 'Identification',
              'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'zh-Hans'}, 'group_name': 'Identification',
              'language': 'zh-Hans'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'nl'}, 'group_name': 'Identification',
              'language': 'nl'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'fr'}, 'group_name': 'Identification',
              'language': 'fr'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'de'}, 'group_name': 'Identification',
              'language': 'de'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt-BR'}, 'group_name': 'Identification',
              'language': 'pt-BR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'el'}, 'group_name': 'Identification',
              'language': 'el'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'hi'}, 'group_name': 'Identification',
              'language': 'hi'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'it'}, 'group_name': 'Identification',
              'language': 'it'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ja'}, 'group_name': 'Identification',
              'language': 'ja'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt'}, 'group_name': 'Identification',
              'language': 'pt'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ru'}, 'group_name': 'Identification',
              'language': 'ru'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es'}, 'group_name': 'Identification',
              'language': 'es'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-AR'}, 'group_name': 'Identification',
              'language': 'es-AR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-CL'}, 'group_name': 'Identification',
              'language': 'es-CL'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-MX'}, 'group_name': 'Identification',
              'language': 'es-MX'}],
            [{'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 2, 'gid': 1841,
              'description': '', 'id': {'gid': 1841, 'language': 'en'}, 'group_name': 'First group', 'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'en'}, 'group_name': 'Identification',
              'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'zh-Hans'}, 'group_name': 'Identification',
              'language': 'zh-Hans'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'nl'}, 'group_name': 'Identification',
              'language': 'nl'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'fr'}, 'group_name': 'Identification',
              'language': 'fr'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'de'}, 'group_name': 'Identification',
              'language': 'de'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt-BR'}, 'group_name': 'Identification',
              'language': 'pt-BR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'el'}, 'group_name': 'Identification',
              'language': 'el'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'hi'}, 'group_name': 'Identification',
              'language': 'hi'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'it'}, 'group_name': 'Identification',
              'language': 'it'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ja'}, 'group_name': 'Identification',
              'language': 'ja'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt'}, 'group_name': 'Identification',
              'language': 'pt'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ru'}, 'group_name': 'Identification',
              'language': 'ru'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es'}, 'group_name': 'Identification',
              'language': 'es'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-AR'}, 'group_name': 'Identification',
              'language': 'es-AR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-CL'}, 'group_name': 'Identification',
              'language': 'es-CL'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-MX'}, 'group_name': 'Identification',
              'language': 'es-MX'}],
            [{'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 2, 'gid': 1841,
              'description': '', 'id': {'gid': 1841, 'language': 'en'}, 'group_name': 'First group', 'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'en'}, 'group_name': 'Identification',
              'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'zh-Hans'}, 'group_name': 'Identification',
              'language': 'zh-Hans'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'nl'}, 'group_name': 'Identification',
              'language': 'nl'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'fr'}, 'group_name': 'Identification',
              'language': 'fr'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'de'}, 'group_name': 'Identification',
              'language': 'de'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt-BR'}, 'group_name': 'Identification',
              'language': 'pt-BR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'el'}, 'group_name': 'Identification',
              'language': 'el'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'hi'}, 'group_name': 'Identification',
              'language': 'hi'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'it'}, 'group_name': 'Identification',
              'language': 'it'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ja'}, 'group_name': 'Identification',
              'language': 'ja'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt'}, 'group_name': 'Identification',
              'language': 'pt'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ru'}, 'group_name': 'Identification',
              'language': 'ru'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es'}, 'group_name': 'Identification',
              'language': 'es'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-AR'}, 'group_name': 'Identification',
              'language': 'es-AR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-CL'}, 'group_name': 'Identification',
              'language': 'es-CL'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-MX'}, 'group_name': 'Identification',
              'language': 'es-MX'}],
            [{'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 2, 'gid': 1841,
              'description': '', 'id': {'gid': 1841, 'language': 'en'}, 'group_name': 'First group', 'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'en'}, 'group_name': 'Identification',
              'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'zh-Hans'}, 'group_name': 'Identification',
              'language': 'zh-Hans'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'nl'}, 'group_name': 'Identification',
              'language': 'nl'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'fr'}, 'group_name': 'Identification',
              'language': 'fr'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'de'}, 'group_name': 'Identification',
              'language': 'de'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt-BR'}, 'group_name': 'Identification',
              'language': 'pt-BR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'el'}, 'group_name': 'Identification',
              'language': 'el'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'hi'}, 'group_name': 'Identification',
              'language': 'hi'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'it'}, 'group_name': 'Identification',
              'language': 'it'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ja'}, 'group_name': 'Identification',
              'language': 'ja'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt'}, 'group_name': 'Identification',
              'language': 'pt'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ru'}, 'group_name': 'Identification',
              'language': 'ru'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es'}, 'group_name': 'Identification',
              'language': 'es'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-AR'}, 'group_name': 'Identification',
              'language': 'es-AR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-CL'}, 'group_name': 'Identification',
              'language': 'es-CL'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-MX'}, 'group_name': 'Identification',
              'language': 'es-MX'}],
            [{'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 2, 'gid': 1841,
              'description': '', 'id': {'gid': 1841, 'language': 'en'}, 'group_name': 'First group', 'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'en'}, 'group_name': 'Identification',
              'language': 'en'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'zh-Hans'}, 'group_name': 'Identification',
              'language': 'zh-Hans'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'nl'}, 'group_name': 'Identification',
              'language': 'nl'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'fr'}, 'group_name': 'Identification',
              'language': 'fr'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'de'}, 'group_name': 'Identification',
              'language': 'de'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt-BR'}, 'group_name': 'Identification',
              'language': 'pt-BR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'el'}, 'group_name': 'Identification',
              'language': 'el'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'hi'}, 'group_name': 'Identification',
              'language': 'hi'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'it'}, 'group_name': 'Identification',
              'language': 'it'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ja'}, 'group_name': 'Identification',
              'language': 'ja'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'pt'}, 'group_name': 'Identification',
              'language': 'pt'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'ru'}, 'group_name': 'Identification',
              'language': 'ru'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es'}, 'group_name': 'Identification',
              'language': 'es'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-AR'}, 'group_name': 'Identification',
              'language': 'es-AR'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-CL'}, 'group_name': 'Identification',
              'language': 'es-CL'},
             {'randomization_group': '', 'grelevance': '', 'sid': 199237, 'group_order': 1, 'gid': 1840,
              'description': '', 'id': {'gid': 1840, 'language': 'es-MX'}, 'group_name': 'Identification',
              'language': 'es-MX'}]

        ]
        mockServer.return_value.list_questions.side_effect = [
            [{'same_default': 0, 'type': '|', 'other': 'N', 'scale_id': 0, 'mandatory': 'N', 'question_order': 3,
              'modulename': None, 'sid': 199237, 'qid': 5823, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5823, 'language': 'en'}, 'question': 'Has fileupload?', 'relevance': '1',
              'title': 'fileUpload'},
             {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 2,
              'modulename': '', 'sid': 199237, 'qid': 5822, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5822, 'language': 'en'}, 'question': 'Second question', 'relevance': '1',
              'title': 'secondQuestion'},
             {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
              'modulename': '', 'sid': 199237, 'qid': 5821, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5821, 'language': 'en'}, 'question': 'First question', 'relevance': '1',
              'title': 'firstQuestion'}],
            [{'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 3,
              'modulename': None, 'sid': 199237, 'qid': 5820, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5820, 'language': 'en'},
              'question': 'Participant Identification number<b>:</b>', 'relevance': '1', 'title': 'subjectid'},
             {'same_default': 0, 'type': 'D', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
              'modulename': None, 'sid': 199237, 'qid': 5819, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5819, 'language': 'en'},
              'question': 'Acquisition date<strong>:</strong><br />\n', 'relevance': '1', 'title': 'acquisitiondate'},
             {'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 0,
              'modulename': None, 'sid': 199237, 'qid': 5818, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5818, 'language': 'en'}, 'question': 'Responsible Identification number:',
              'relevance': '1', 'title': 'responsibleid'}],
            [{'same_default': 0, 'type': '|', 'other': 'N', 'scale_id': 0, 'mandatory': 'N', 'question_order': 3,
              'modulename': None, 'sid': 199237, 'qid': 5823, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5823, 'language': 'en'}, 'question': 'Has fileupload?', 'relevance': '1',
              'title': 'fileUpload'},
             {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 2,
              'modulename': '', 'sid': 199237, 'qid': 5822, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5822, 'language': 'en'}, 'question': 'Second question', 'relevance': '1',
              'title': 'secondQuestion'},
             {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
              'modulename': '', 'sid': 199237, 'qid': 5821, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1841, 'id': {'qid': 5821, 'language': 'en'}, 'question': 'First question', 'relevance': '1',
              'title': 'firstQuestion'},
             {'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 3,
              'modulename': None, 'sid': 199237, 'qid': 5820, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5820, 'language': 'en'},
              'question': 'Participant Identification number<b>:</b>', 'relevance': '1', 'title': 'subjectid'},
             {'same_default': 0, 'type': 'D', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
              'modulename': None, 'sid': 199237, 'qid': 5819, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5819, 'language': 'en'},
              'question': 'Acquisition date<strong>:</strong><br />\n', 'relevance': '1', 'title': 'acquisitiondate'},
             {'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 0,
              'modulename': None, 'sid': 199237, 'qid': 5818, 'language': 'en', 'help': '', 'parent_qid': 0, 'preg': '',
              'gid': 1840, 'id': {'qid': 5818, 'language': 'en'}, 'question': 'Responsible Identification number:',
              'relevance': '1', 'title': 'responsibleid'}]
        ]
        mockServer.return_value.get_question_properties.side_effect = [
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'fileUpload', 'question_order': 3, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'Has fileupload?', 'attributes': 'No available attributes', 'type': '|'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'secondQuestion', 'question_order': 2, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'Second question', 'attributes': 'No available attributes', 'type': 'T'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'firstQuestion', 'question_order': 1, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'First question', 'attributes': 'No available attributes', 'type': 'T'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'subjectid', 'question_order': 3, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'attributes': {'hidden': '1'},
             'type': 'N'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'acquisitiondate', 'question_order': 1, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'attributes': {'hidden': '1'},
             'type': 'D'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'responsibleid', 'question_order': 0, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Responsible Identification number:', 'attributes': {'hidden': '1'},
             'type': 'N'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'fileUpload', 'question_order': 3, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'Has fileupload?', 'attributes': 'No available attributes', 'type': '|'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'secondQuestion', 'question_order': 2, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'Second question', 'attributes': 'No available attributes', 'type': 'T'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'firstQuestion', 'question_order': 1, 'attributes_lang': 'No available attributes', 'gid': 1841,
             'other': 'N', 'question': 'First question', 'attributes': 'No available attributes', 'type': 'T'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'subjectid', 'question_order': 3, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'attributes': {'hidden': '1'},
             'type': 'N'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'acquisitiondate', 'question_order': 1, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'attributes': {'hidden': '1'},
             'type': 'D'},
            {'answeroptions': 'No available answer options', 'subquestions': 'No available answers',
             'title': 'responsibleid', 'question_order': 0, 'attributes_lang': 'No available attributes', 'gid': 1840,
             'other': 'N', 'question': 'Responsible Identification number:', 'attributes': {'hidden': '1'}, 'type': 'N'}
        ]
        mockServer.return_value.get_language_properties.return_value = {'surveyls_title': 'Test questionnaire'}

        ## Ínicio - Estava no setUp
        # self.lime_survey = Questionnaires()

        # self.sid = self.create_limesurvey_questionnaire()

        # create questionnaire data collection in NES
        # TODO: use method already existent in patient.tests. See other places
        self.survey = create_survey(199237)
        self.data_configuration_tree = self.create_nes_questionnaire(
            self.root_component
        )

        # Add response's participant to limesurvey survey and the references
        # in our db
        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, self.subject_of_group.subject
        # )
        self.questionnaire_response = \
            ObjectsFactory.create_questionnaire_response(
                dct=self.data_configuration_tree,
                responsible=self.user, token_id=1,
                subject_of_group=self.subject_of_group
            )
        ## Fim - Estava no setUp

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # change questionnaire respose date for testing
        self.questionnaire_response.date = date(2016, 7, 7)
        self.questionnaire_response.save()

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'per_questionnaire': ['on'],
            'action': ['run'],
            'headings': ['abbreviated'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(199237) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(199237) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(199237) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(199237) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ), temp_dir
        )

        with open(os.path.join(
                temp_dir,
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
        )) as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            self.assertEqual(
                rows[1][1],
                ExportParticipants.subject_age(
                    self.patient.date_birth, self.questionnaire_response
                )
            )

        shutil.rmtree(temp_dir)
        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_participant_age_in_responses_is_age_when_questionnaire_was_filled_2(self, mockServer):
        """Test over participant questionnaire responses"""

        mockServer.return_value.get_survey_properties.return_value = {'language': 'en', 'additional_languages': ''}
        mockServer.return_value.get_participant_properties.side_effect = [
            {'token': 'ceBAtUYdVXOF3ie'}

        ]
        mockServer.return_value.export_responses.return_value = \
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVjb3VudF0iCiIxIiwiMjAxOS0wNi0yNiAxNjozNzoyOSIsIjIiLCJlbiIsIkFhMEdYbG5DYWw2Zmt6ZCIsIjU0MDAwIiwiMjAxOS0wNi0yNiAxNjozNzoyOS40OTUyOCIsIjE3NzUzNCIsIk9sw6EgTXVuZG8hIiwiSGFsbG8gV2VsdCEiLCIiLCIiCgo='
        mockServer.return_value.list_groups.side_effect = [
            [{'grelevance': '', 'id': {'gid': 1855, 'language': 'en'}, 'language': 'en', 'randomization_group': '',
              'gid': 1855, 'group_order': 2, 'group_name': 'First group', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'en'}, 'language': 'en', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'zh-Hans'}, 'language': 'zh-Hans',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'nl'}, 'language': 'nl', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'fr'}, 'language': 'fr', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'de'}, 'language': 'de', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'pt-BR'}, 'language': 'pt-BR',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'el'}, 'language': 'el', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'hi'}, 'language': 'hi', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'it'}, 'language': 'it', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'ja'}, 'language': 'ja', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'pt'}, 'language': 'pt', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'ru'}, 'language': 'ru', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es'}, 'language': 'es', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-AR'}, 'language': 'es-AR',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-CL'}, 'language': 'es-CL',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-MX'}, 'language': 'es-MX',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111}],
            [{'grelevance': '', 'id': {'gid': 1855, 'language': 'en'}, 'language': 'en', 'randomization_group': '',
              'gid': 1855, 'group_order': 2, 'group_name': 'First group', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'en'}, 'language': 'en', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'zh-Hans'}, 'language': 'zh-Hans',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'nl'}, 'language': 'nl', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'fr'}, 'language': 'fr', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'de'}, 'language': 'de', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'pt-BR'}, 'language': 'pt-BR',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'el'}, 'language': 'el', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'hi'}, 'language': 'hi', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'it'}, 'language': 'it', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'ja'}, 'language': 'ja', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'pt'}, 'language': 'pt', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'ru'}, 'language': 'ru', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es'}, 'language': 'es', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-AR'}, 'language': 'es-AR',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-CL'}, 'language': 'es-CL',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-MX'}, 'language': 'es-MX',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111}],
            [{'grelevance': '', 'id': {'gid': 1855, 'language': 'en'}, 'language': 'en', 'randomization_group': '',
              'gid': 1855, 'group_order': 2, 'group_name': 'First group', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'en'}, 'language': 'en', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'zh-Hans'}, 'language': 'zh-Hans',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'nl'}, 'language': 'nl', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'fr'}, 'language': 'fr', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'de'}, 'language': 'de', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'pt-BR'}, 'language': 'pt-BR',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'el'}, 'language': 'el', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'hi'}, 'language': 'hi', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'it'}, 'language': 'it', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'ja'}, 'language': 'ja', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'pt'}, 'language': 'pt', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'ru'}, 'language': 'ru', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es'}, 'language': 'es', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-AR'}, 'language': 'es-AR',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-CL'}, 'language': 'es-CL',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-MX'}, 'language': 'es-MX',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111}],
            [{'grelevance': '', 'id': {'gid': 1855, 'language': 'en'}, 'language': 'en', 'randomization_group': '',
              'gid': 1855, 'group_order': 2, 'group_name': 'First group', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'en'}, 'language': 'en', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'zh-Hans'}, 'language': 'zh-Hans',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'nl'}, 'language': 'nl', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'fr'}, 'language': 'fr', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'de'}, 'language': 'de', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'pt-BR'}, 'language': 'pt-BR',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'el'}, 'language': 'el', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'hi'}, 'language': 'hi', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'it'}, 'language': 'it', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'ja'}, 'language': 'ja', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'pt'}, 'language': 'pt', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'ru'}, 'language': 'ru', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es'}, 'language': 'es', 'randomization_group': '',
              'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-AR'}, 'language': 'es-AR',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-CL'}, 'language': 'es-CL',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111},
             {'grelevance': '', 'id': {'gid': 1854, 'language': 'es-MX'}, 'language': 'es-MX',
              'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
              'description': '', 'sid': 913111}]
        ]
        mockServer.return_value.list_questions.side_effect = [
            [{'id': {'qid': 5865, 'language': 'en'}, 'language': 'en', 'title': 'fileUpload', 'help': '', 'preg': '',
              'type': '|', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
              'question': 'Has fileupload?', 'scale_id': 0, 'gid': 1855, 'qid': 5865, 'mandatory': 'N',
              'question_order': 3, 'sid': 913111},
             {'id': {'qid': 5864, 'language': 'en'}, 'language': 'en', 'title': 'secondQuestion', 'help': '',
              'preg': '', 'type': 'T', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': '',
              'parent_qid': 0, 'question': 'Second question', 'scale_id': 0, 'gid': 1855, 'qid': 5864, 'mandatory': 'Y',
              'question_order': 2, 'sid': 913111},
             {'id': {'qid': 5863, 'language': 'en'}, 'language': 'en', 'title': 'firstQuestion', 'help': '', 'preg': '',
              'type': 'T', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': '', 'parent_qid': 0,
              'question': 'First question', 'scale_id': 0, 'gid': 1855, 'qid': 5863, 'mandatory': 'Y',
              'question_order': 1, 'sid': 913111}],
            [{'id': {'qid': 5862, 'language': 'en'}, 'language': 'en', 'title': 'subjectid', 'help': '', 'preg': '',
              'type': 'N', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
              'question': 'Participant Identification number<b>:</b>', 'scale_id': 0, 'gid': 1854, 'qid': 5862,
              'mandatory': 'Y', 'question_order': 3, 'sid': 913111},
             {'id': {'qid': 5861, 'language': 'en'}, 'language': 'en', 'title': 'acquisitiondate', 'help': '',
              'preg': '', 'type': 'D', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None,
              'parent_qid': 0, 'question': 'Acquisition date<strong>:</strong><br />\n', 'scale_id': 0, 'gid': 1854,
              'qid': 5861, 'mandatory': 'Y', 'question_order': 1, 'sid': 913111},
             {'id': {'qid': 5860, 'language': 'en'}, 'language': 'en', 'title': 'responsibleid', 'help': '', 'preg': '',
              'type': 'N', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
              'question': 'Responsible Identification number:', 'scale_id': 0, 'gid': 1854, 'qid': 5860,
              'mandatory': 'Y', 'question_order': 0, 'sid': 913111}],
            [{'id': {'qid': 5865, 'language': 'en'}, 'language': 'en', 'title': 'fileUpload', 'help': '', 'preg': '',
              'type': '|', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
              'question': 'Has fileupload?', 'scale_id': 0, 'gid': 1855, 'qid': 5865, 'mandatory': 'N',
              'question_order': 3, 'sid': 913111},
             {'id': {'qid': 5864, 'language': 'en'}, 'language': 'en', 'title': 'secondQuestion', 'help': '',
              'preg': '', 'type': 'T', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': '',
              'parent_qid': 0, 'question': 'Second question', 'scale_id': 0, 'gid': 1855, 'qid': 5864, 'mandatory': 'Y',
              'question_order': 2, 'sid': 913111},
             {'id': {'qid': 5863, 'language': 'en'}, 'language': 'en', 'title': 'firstQuestion', 'help': '', 'preg': '',
              'type': 'T', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': '', 'parent_qid': 0,
              'question': 'First question', 'scale_id': 0, 'gid': 1855, 'qid': 5863, 'mandatory': 'Y',
              'question_order': 1, 'sid': 913111},
             {'id': {'qid': 5862, 'language': 'en'}, 'language': 'en', 'title': 'subjectid', 'help': '', 'preg': '',
              'type': 'N', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
              'question': 'Participant Identification number<b>:</b>', 'scale_id': 0, 'gid': 1854, 'qid': 5862,
              'mandatory': 'Y', 'question_order': 3, 'sid': 913111},
             {'id': {'qid': 5861, 'language': 'en'}, 'language': 'en', 'title': 'acquisitiondate', 'help': '',
              'preg': '', 'type': 'D', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None,
              'parent_qid': 0, 'question': 'Acquisition date<strong>:</strong><br />\n', 'scale_id': 0, 'gid': 1854,
              'qid': 5861, 'mandatory': 'Y', 'question_order': 1, 'sid': 913111},
             {'id': {'qid': 5860, 'language': 'en'}, 'language': 'en', 'title': 'responsibleid', 'help': '', 'preg': '',
              'type': 'N', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
              'question': 'Responsible Identification number:', 'scale_id': 0, 'gid': 1854, 'qid': 5860,
              'mandatory': 'Y', 'question_order': 0, 'sid': 913111}]
        ]
        mockServer.return_value.get_question_properties.side_effect = [
            {'attributes_lang': 'No available attributes', 'title': 'fileUpload',
             'attributes': 'No available attributes', 'question': 'Has fileupload?', 'other': 'N',
             'subquestions': 'No available answers', 'gid': 1855, 'answeroptions': 'No available answer options',
             'question_order': 3, 'type': '|'},
            {'attributes_lang': 'No available attributes', 'title': 'secondQuestion',
             'attributes': 'No available attributes', 'question': 'Second question', 'other': 'N',
             'subquestions': 'No available answers', 'gid': 1855, 'answeroptions': 'No available answer options',
             'question_order': 2, 'type': 'T'},
            {'attributes_lang': 'No available attributes', 'title': 'firstQuestion',
             'attributes': 'No available attributes', 'question': 'First question', 'other': 'N',
             'subquestions': 'No available answers', 'gid': 1855, 'answeroptions': 'No available answer options',
             'question_order': 1, 'type': 'T'},
            {'attributes_lang': 'No available attributes', 'title': 'subjectid', 'attributes': {'hidden': '1'},
             'question': 'Participant Identification number<b>:</b>', 'other': 'N',
             'subquestions': 'No available answers', 'gid': 1854, 'answeroptions': 'No available answer options',
             'question_order': 3, 'type': 'N'},
            {'attributes_lang': 'No available attributes', 'title': 'acquisitiondate', 'attributes': {'hidden': '1'},
             'question': 'Acquisition date<strong>:</strong><br />\n', 'other': 'N',
             'subquestions': 'No available answers', 'gid': 1854, 'answeroptions': 'No available answer options',
             'question_order': 1, 'type': 'D'},
            {'attributes_lang': 'No available attributes', 'title': 'responsibleid', 'attributes': {'hidden': '1'},
             'question': 'Responsible Identification number:', 'other': 'N', 'subquestions': 'No available answers',
             'gid': 1854, 'answeroptions': 'No available answer options', 'question_order': 0, 'type': 'N'},
            {'attributes_lang': 'No available attributes', 'title': 'fileUpload',
             'attributes': 'No available attributes', 'question': 'Has fileupload?', 'other': 'N',
             'subquestions': 'No available answers', 'gid': 1855, 'answeroptions': 'No available answer options',
             'question_order': 3, 'type': '|'},
            {'attributes_lang': 'No available attributes', 'title': 'secondQuestion',
             'attributes': 'No available attributes', 'question': 'Second question', 'other': 'N',
             'subquestions': 'No available answers', 'gid': 1855, 'answeroptions': 'No available answer options',
             'question_order': 2, 'type': 'T'},
            {'attributes_lang': 'No available attributes', 'title': 'firstQuestion',
             'attributes': 'No available attributes', 'question': 'First question', 'other': 'N',
             'subquestions': 'No available answers', 'gid': 1855, 'answeroptions': 'No available answer options',
             'question_order': 1, 'type': 'T'},
            {'attributes_lang': 'No available attributes', 'title': 'subjectid', 'attributes': {'hidden': '1'},
             'question': 'Participant Identification number<b>:</b>', 'other': 'N',
             'subquestions': 'No available answers', 'gid': 1854, 'answeroptions': 'No available answer options',
             'question_order': 3, 'type': 'N'},
            {'attributes_lang': 'No available attributes', 'title': 'acquisitiondate', 'attributes': {'hidden': '1'},
             'question': 'Acquisition date<strong>:</strong><br />\n', 'other': 'N',
             'subquestions': 'No available answers', 'gid': 1854, 'answeroptions': 'No available answer options',
             'question_order': 1, 'type': 'D'},
            {'attributes_lang': 'No available attributes', 'title': 'responsibleid', 'attributes': {'hidden': '1'},
             'question': 'Responsible Identification number:', 'other': 'N', 'subquestions': 'No available answers',
             'gid': 1854, 'answeroptions': 'No available answer options', 'question_order': 0, 'type': 'N'}
        ]
        mockServer.return_value.get_language_properties.return_value = {'surveyls_title': 'Test questionnaire'}
        mockServer.return_value.add_participants.return_value = [
            {
                'token': 'GQ5rP7eMjbTaNVf', 'sent': 'N', 'language': None, 'participant_id': None, 'mpid': None,
                'tid': '2', 'validuntil': None, 'completed': 'N', 'emailstatus': 'OK', 'validfrom': None,
                'lastname': '', 'email': '', 'usesleft': 1, 'blacklisted': None, 'remindersent': 'N', 'firstname': '',
                'remindercount': 0
            }
        ]

        ## Ínicio - Estava no setUp
        # self.lime_survey = Questionnaires()

        # self.sid = self.create_limesurvey_questionnaire()

        # create questionnaire data collection in NES
        # TODO: use method already existent in patient.tests. See other places
        self.survey = create_survey(913111)
        self.data_configuration_tree = self.create_nes_questionnaire(
            self.root_component
        )

        # Add response's participant to limesurvey survey and the references
        # in our db
        # result = self.lime_survey.add_participant(self.survey.lime_survey_id)
        # self.add_responses_to_limesurvey_survey(
        #     result, self.subject_of_group.subject
        # )
        self.questionnaire_response = \
            ObjectsFactory.create_questionnaire_response(
                dct=self.data_configuration_tree,
                responsible=self.user, token_id=1,
                subject_of_group=self.subject_of_group
            )
        ## Fim - Estava no setUp

        # In setUp we created experiment questionnaire response. Here we
        # create a participant questionnaire response (entrance questionnaire)
        questionnaire_response = UtilTests.create_response_survey(
            responsible=self.user, patient=self.patient, survey=self.survey)
        # change questionnaire respose date for testing
        questionnaire_response.date = date(2016, 4, 17)
        questionnaire_response.save()

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'per_questionnaire': ['on'],
            'action': ['run'],
            'headings': ['code'],
            'to[]': [
                '0*' + str(913111) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(913111) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(913111) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(913111) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short'],
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join('NES_EXPORT', 'Participants.csv'), temp_dir
        )

        with open(os.path.join(
                temp_dir, 'NES_EXPORT', 'Participants.csv'
        )) as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            self.assertEqual(
                rows[1][1],
                self.subject_age(
                    self.patient.date_birth, self.questionnaire_response
                )
            )

        shutil.rmtree(temp_dir)
        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    def test_export_create_file_csv_separated_with_commas(self):
        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['abbreviated'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short'],
            'filesformat': ['csv']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.csv'
            ),
            '/tmp'  # TODO: 1) use os.sep; 2) use tempfile
        )

        with open(
                os.path.join(
                    os.sep, 'tmp',  # TODO: use tempfile
                    'NES_EXPORT',
                    'Experiment_data',
                    'Group_' + self.group.title.lower(),
                    'Per_questionnaire',
                    'Step_1_QUESTIONNAIRE',
                    self.survey.code + '_test-questionnaire_en.csv'
                )
        ) as file:
            dialect = csv.Sniffer().sniff(file.readline(), [',', '\t'])
            file.seek(0)
            self.assertEqual(dialect.delimiter, ",")

    def test_export_create_file_tsv_separated_with_tabs(self):
        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_participant': ['on'],
            'action': ['run'],
            'per_questionnaire': ['on'],
            'headings': ['abbreviated'],
            'to_experiment[]': [
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*acquisitiondate*acquisitiondate',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*firstQuestion*firstQuestion',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*secondQuestion*secondQuestion',
                '0*' + str(self.group.id) + '*' + str(self.sid) +
                '*Test questionnaire*fileUpload*fileUpload'
            ],
            'patient_selected': ['age*age'],
            'responses': ['short'],
            'filesformat': ['tsv']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        zipped_file.extract(
            os.path.join(
                'NES_EXPORT',
                'Experiment_data',
                'Group_' + self.group.title.lower(),
                'Per_questionnaire', 'Step_1_QUESTIONNAIRE',
                self.survey.code + '_test-questionnaire_en.tsv'
            ),
            '/tmp'  # TODO: 1) use os.sep; 2) use tempfile
        )

        with open(
                os.path.join(
                    os.sep, 'tmp',  # TODO: use tempfile
                    'NES_EXPORT',
                    'Experiment_data',
                    'Group_' + self.group.title.lower(),
                    'Per_questionnaire',
                    'Step_1_QUESTIONNAIRE',
                    self.survey.code + '_test-questionnaire_en.tsv'
                )
        ) as file:
            dialect = csv.Sniffer().sniff(file.readline(), [',', '\t'])
            file.seek(0)
            self.assertEqual(dialect.delimiter, "\t")


class ExportDataCollectionTest(ExportTestCase):
    TEMP_MEDIA_ROOT = tempfile.mkdtemp()

    def setUp(self):
        super(ExportDataCollectionTest, self).setUp()

    def tearDown(self):
        self.client.logout()

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_generic_data_colletion(self):
        # create generic data collection (gdc) component
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(
            self.experiment, Component.GENERIC_DATA_COLLECTION,
            kwargs={'it': it}
        )

        # include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, gdc
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' generic data collection file
        gdc_data = ObjectsFactory.create_generic_data_collection_data(
            dct, self.subject_of_group
        )
        gdcf = ObjectsFactory.create_generic_data_collection_file(gdc_data)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_generic_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # we have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(
            self.group.experimental_protocol, "generic_data_collection"
        )[0]

        generic_component_configuration = \
            ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = generic_component_configuration.component
        step_number = path[-1][4]

        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'Generic_Data_Collection_1',
            os.path.basename(gdcf.file.name), zipped_file
        )
        self.assert_per_participant_step_file_exists(
            step_number, component_step, 'AdditionalData_1',
            os.path.basename(adf.file.name), zipped_file
        )

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_digital_game_phase_data_colletion(self):
        # create digital game phase (dgp) component
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        context_tree = ObjectsFactory.create_context_tree(self.experiment)

        dgp = ObjectsFactory.create_component(
            self.experiment, Component.DIGITAL_GAME_PHASE,
            kwargs={'software_version': software_version, 'context_tree': context_tree}
        )

        # include dgp component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, dgp
        )

        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' digital game data file
        dgp_data = ObjectsFactory.create_digital_game_phase_data(
            dct, self.subject_of_group
        )

        dgpf = ObjectsFactory.create_digital_game_phase_file(dgp_data)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_goalkeeper_game_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # we have only the digital_game_phase step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "digital_game_phase")[0]

        digital_game_phase_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = digital_game_phase_component_configuration.component
        step_number = path[-1][4]

        self.assert_per_participant_step_file_exists(step_number, component_step,
                                                     'DigitalGamePhaseData_1',
                                                     os.path.basename(dgpf.file.name),
                                                     zipped_file)
        self.assert_per_participant_step_file_exists(step_number, component_step,
                                                     'AdditionalData_1',
                                                     os.path.basename(adf.file.name),
                                                     zipped_file)

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_eeg(self):
        # create eeg component
        eeg_set = ObjectsFactory.create_eeg_setting(self.experiment)
        eeg_comp = ObjectsFactory.create_component(
            self.experiment, Component.EEG,
            kwargs={'eeg_set': eeg_set}
        )

        # include eeg component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, eeg_comp
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' eeg file
        eegdata = ObjectsFactory.create_eeg_data(
            dct, self.subject_of_group, eeg_set
        )

        eegf = ObjectsFactory.create_eeg_file(eegdata)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_eeg_raw_data ': ['on'],
            'per_additional_data': ['on'],
            'headings': ['abbreviated'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # we have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "eeg")[0]
        eeg_conf = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = eeg_conf.component
        step_number = path[-1][4]
        self.assert_per_participant_step_file_exists(step_number, component_step, 'EEGData_1',
                                                     os.path.basename(eegf.file.name), zipped_file)

        self.assert_per_participant_step_file_exists(step_number, component_step, 'AdditionalData_1',
                                                     os.path.basename(adf.file.name), zipped_file)

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_emg(self):
        # create emg component
        self.manufacturer = ObjectsFactory.create_manufacturer()
        self.software = ObjectsFactory.create_software(self.manufacturer)
        self.software_version = ObjectsFactory.create_software_version(
            self.software)
        self.tag_emg = ObjectsFactory.create_tag('EMG')
        emg_set = ObjectsFactory.create_emg_setting(self.experiment,
                                                    self.software_version)
        emg_comp = ObjectsFactory.create_component(self.experiment,
                                                   Component.EMG,
                                                   kwargs={'emg_set': emg_set}
                                                   )

        # include emg component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, emg_comp
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' emg file
        emgdata = ObjectsFactory.create_emg_data_collection_data(
            dct, self.subject_of_group, emg_set
        )

        emgf = ObjectsFactory.create_emg_data_collection_file(emgdata)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_emg_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['abbreviated'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        # we have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "emg")[0]
        emg_conf = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = emg_conf.component
        step_number = path[-1][4]

        self.assert_per_participant_step_file_exists(step_number, component_step, 'EMGData_1',
                                                     os.path.basename(emgf.file.name), zipped_file)

        self.assert_per_participant_step_file_exists(step_number, component_step, 'AdditionalData_1',
                                                     os.path.basename(adf.file.name), zipped_file)

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_tms(self):

        # create tms component
        tms_set = ObjectsFactory.create_tms_setting(self.experiment)

        tms_comp = ObjectsFactory.create_component(
            self.experiment, Component.TMS,
            kwargs={'tms_set': tms_set}
        )

        # include tms component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, tms_comp
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        doic = DirectionOfTheInducedCurrent.objects.create(
            name="Direction of Induced Current"
        )

        coilor = CoilOrientation.objects.create(
            name="Coil Orientation"
        )

        tmsdataaux = TMSData.objects.create(
            tms_setting=tms_set,
            data_configuration_tree=dct,
            subject_of_group=self.subject_of_group,
            coil_orientation=coilor,
            description="Teste TMS",
            direction_of_induced_current=doic
        )

        brainareasystem = BrainAreaSystem.objects.create(name='Lobo frontal')

        brainarea = BrainArea.objects.create(name='Lobo frontal',
                                             brain_area_system=brainareasystem)

        temp_dir = tempfile.mkdtemp()
        with open(os.path.join(temp_dir, 'image.bin'), 'wb') as f:
            f.write(b'carambola')
        temp_file = f.name

        tms_local_sys = TMSLocalizationSystem.objects.create(
            name="TMS name", brain_area=brainarea,
            tms_localization_system_image=temp_file
        )

        hotspot = HotSpot.objects.create(
            tms_data=tmsdataaux,
            name="TMS Data Collection File",
            tms_localization_system=tms_local_sys
        )

        ObjectsFactory.create_hotspot_data_collection_file(hotspot)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_tms_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['abbreviated'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        for path in create_list_of_trees(self.group.experimental_protocol,
                                         "tms"):
            tms_conf = \
                ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = tms_conf.component
            step_number = path[-1][4]

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         '',
                                                         'hotspot_map.png',
                                                         zipped_file)

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         'AdditionalData_1',
                                                         'file.bin',
                                                         zipped_file)

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_generic_data_colletion_2_groups(self):
        # create second group
        # create patient/subject/subject_of_group
        root_component1 = ObjectsFactory.create_block(self.experiment)
        group1 = ObjectsFactory.create_group(
            self.experiment, root_component1
        )
        patient1 = UtilTests().create_patient(changed_by=self.user)
        subject1 = ObjectsFactory.create_subject(patient1)
        subject_of_group1 = \
            ObjectsFactory.create_subject_of_group(group1, subject1)

        # create generic data collection (gdc) component
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(
            self.experiment, Component.GENERIC_DATA_COLLECTION,
            kwargs={'it': it}
        )

        # include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, gdc
        )
        component_config1 = ObjectsFactory.create_component_configuration(
            root_component1, gdc
        )

        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        dct1 = ObjectsFactory.create_data_configuration_tree(component_config1)

        # 'upload' generic data collection file
        gdc_data = ObjectsFactory.create_generic_data_collection_data(
            dct, self.subject_of_group
        )
        gdc_data1 = ObjectsFactory.create_generic_data_collection_data(
            dct1, subject_of_group1
        )

        ObjectsFactory.create_generic_data_collection_file(gdc_data)
        ObjectsFactory.create_generic_data_collection_file(gdc_data1)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id), str(group1.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_generic_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }

        response = self.client.post(reverse('export_view'), data)

        zipped_file = self.get_zipped_file(response)

        for path in create_list_of_trees(self.group.experimental_protocol,
                                         "generic_data_collection"):
            generic_component_configuration = \
                ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = generic_component_configuration.component
            step_number = path[-1][4]

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         'Generic_Data_Collection_1',
                                                         'file.bin',
                                                         zipped_file)

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         'AdditionalData_1',
                                                         'file.bin',
                                                         zipped_file)

        for path in create_list_of_trees(group1.experimental_protocol,
                                         "generic_data_collection"):
            generic_component_configuration = \
                ComponentConfiguration.objects.get(pk=path[-1][0])
            component_step = generic_component_configuration.component
            step_number = path[-1][4]

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         'Generic_Data_Collection_1',
                                                         'file.bin',
                                                         zipped_file)

            self.assert_per_participant_step_file_exists(step_number, component_step,
                                                         'AdditionalData_1',
                                                         'file.bin',
                                                         zipped_file)

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_experiment_with_goalkeeper_game_data_2_groups(self):

        # create second group
        # create patient/subject/subject_of_group
        root_component1 = ObjectsFactory.create_block(self.experiment)
        group1 = ObjectsFactory.create_group(
            self.experiment, root_component1
        )
        patient1 = UtilTests().create_patient(changed_by=self.user)
        subject1 = ObjectsFactory.create_subject(patient1)
        subject_of_group1 = \
            ObjectsFactory.create_subject_of_group(group1, subject1)

        # create digital game phase (dgp) component
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        context_tree = ObjectsFactory.create_context_tree(self.experiment)

        dgp = ObjectsFactory.create_component(
            self.experiment, Component.DIGITAL_GAME_PHASE,
            kwargs={'software_version': software_version, 'context_tree': context_tree}
        )

        # include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, dgp
        )
        component_config1 = ObjectsFactory.create_component_configuration(
            root_component1, dgp
        )

        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        dct1 = ObjectsFactory.create_data_configuration_tree(component_config1)

        # 'upload' data game phase collection file
        dgp_data = ObjectsFactory.create_digital_game_phase_data(
            dct, self.subject_of_group
        )

        dgp_data1 = ObjectsFactory.create_digital_game_phase_data(
            dct1, subject_of_group1
        )

        ObjectsFactory.create_digital_game_phase_file(dgp_data)
        ObjectsFactory.create_digital_game_phase_file(dgp_data1)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id), str(group1.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_goalkeeper_game_data': ['on'],
            # 'per_additional_data': ['on'],
            'headings': ['code'],
            'filesformat': ['csv'],
            'responses': ['short'],
            'patient_selected': ['age*age'],
            'action': ['run']
        }
        response = self.client.post(reverse('export_view'), data)

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_step_additional_data(self):
        # create generic data collection (gdc) component, it could've been any data collection
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(
            self.experiment, Component.GENERIC_DATA_COLLECTION,
            kwargs={'it': it}
        )

        # create a file and add it as an additional file of the step
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(os.path.join(tmpdirname, 'stepadditionaldata.bin'), 'wb') as f:
                f.write(b'carambola')

                with File(open(f.name, 'rb')) as file:
                    ComponentAdditionalFile.objects.create(component=gdc, file=file)

        # include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, gdc
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # 'upload' generic data collection file
        gdc_data = ObjectsFactory.create_generic_data_collection_data(
            dct, self.subject_of_group
        )
        gdcf = ObjectsFactory.create_generic_data_collection_file(gdc_data)

        # Create additional data to this step
        additional_data = ObjectsFactory.create_additional_data_data(dct, self.subject_of_group)

        adf = ObjectsFactory.create_additional_data_file(additional_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_generic_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }

        response = self.client.post(reverse('export_view'), data)

        # get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        # we have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "generic_data_collection")[0]
        generic_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = generic_component_configuration.component
        step_number = path[-1][4]

        self.assert_step_data_files_exists(step_number, component_step,
                                           'AdditionalData',
                                           os.path.basename(f.name),
                                           zipped_file)

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_stimulus_media_file(self):

        # create a stimulus component
        stimulus_type = ObjectsFactory.create_stimulus_type()

        with tempfile.TemporaryDirectory() as tmpdirname:
            f = ObjectsFactory.create_binary_file(tmpdirname)

            with File(open(f.name, 'rb')) as file:
                stimulus = ObjectsFactory.create_component(
                    self.experiment, Component.STIMULUS,
                    kwargs={'stimulus_type': stimulus_type,
                            'media_file': file}
                )

        # include gdc component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, stimulus
        )

        dtc = ObjectsFactory.create_data_configuration_tree(component_config)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_generic_data': ['on'],
            'per_stimulus_data': ['on'],
            'per_additional_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }

        response = self.client.post(reverse('export_view'), data)

        # get the zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        # we have only the generic_data_collection step, so we get the first
        # element: [0]
        path = create_list_of_trees(self.group.experimental_protocol, "stimulus")[0]
        stimulus_component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
        component_step = stimulus_component_configuration.component
        step_number = path[-1][4]

        self.assert_step_data_files_exists(step_number, component_step, '',
                                           os.path.basename(f.name), zipped_file)

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_participants_age_is_age_at_first_data_collection(self):
        """
        Create two data collections: generic data collection and eeg data-
        collection
        """
        # generic data collection (gdc) stuff
        it = ObjectsFactory.create_information_type()
        gdc = ObjectsFactory.create_component(
            self.experiment, Component.GENERIC_DATA_COLLECTION,
            kwargs={'it': it}
        )
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, gdc
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        gdc_data = ObjectsFactory.create_generic_data_collection_data(
            dct, self.subject_of_group
        )
        # change generic data collection date for testing
        gdc_data.date = date(2018, 7, 7)
        gdc_data.save()
        ObjectsFactory.create_generic_data_collection_file(gdc_data)

        # eeg data collection stuff
        eeg_set = ObjectsFactory.create_eeg_setting(self.experiment)
        eeg_comp = ObjectsFactory.create_component(
            self.experiment, Component.EEG,
            kwargs={'eeg_set': eeg_set}
        )
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, eeg_comp
        )
        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        eeg_data = ObjectsFactory.create_eeg_data(
            dct, self.subject_of_group, eeg_set
        )
        # change eeg data collection date for testing
        eeg_data.date = date(2012, 5, 5)
        eeg_data.save()
        ObjectsFactory.create_eeg_file(eeg_data)

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_generic_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join(
                'NES_EXPORT', 'Participant_data', 'Participants.csv'
            ), temp_dir
        )

        with open(os.path.join(
                temp_dir, 'NES_EXPORT', 'Participant_data', 'Participants.csv'
        )) as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            self.assertEqual(
                rows[1][1], self.subject_age(self.patient.date_birth, eeg_data)
            )

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_export_participants_age_is_age_today_if_no_data_collection(self):

        # create eeg step
        eeg_set = ObjectsFactory.create_eeg_setting(self.experiment)
        eeg_comp = ObjectsFactory.create_component(
            self.experiment, Component.EEG,
            kwargs={'eeg_set': eeg_set}
        )
        ObjectsFactory.create_component_configuration(
            self.root_component, eeg_comp
        )

        self.append_session_variable(
            'group_selected_list', [str(self.group.id)]
        )

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'per_generic_data': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(
            os.path.join(
                'NES_EXPORT', 'Participant_data', 'Participants.csv'
            ), temp_dir
        )

        with open(os.path.join(
                temp_dir, 'NES_EXPORT', 'Participant_data', 'Participants.csv'
        )) as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            self.assertEqual(
                rows[1][1], self.subject_age(self.patient.date_birth)
            )

        shutil.rmtree(temp_dir)


class ExportParticipants(ExportTestCase):

    def setUp(self):
        super(ExportParticipants, self).setUp()

    def tearDown(self):
        self.client.logout()

    def test_export_participants_without_questionnaires_returns_zipped_file(self):
        """Test created when exporting participants, without questionnaires
        avulsely answered by them, gave yellow screen. See Jira Issue NES-864.
        """
        data = {'patient_selected': ['age*age'], 'action': ['run']}
        response = self.client.post(reverse('export_view'), data)
        self.assertEqual(response.status_code, 200)

        self.get_zipped_file(response)

    def test_export_participants_age_is_age_at_export_date_if_no_questionnaire_response(self):
        data = {'patient_selected': ['age*age'], 'action': ['run']}
        response = self.client.post(reverse('export_view'), data)
        self.assertEqual(response.status_code, 200)

        temp_dir = tempfile.mkdtemp()
        zipped_file = self.get_zipped_file(response)
        zipped_file.extract(os.path.join('NES_EXPORT', 'Participants.csv'), temp_dir)

        with open(os.path.join(temp_dir, 'NES_EXPORT', 'Participants.csv')) \
                as file:
            csvreader = csv.reader(file)
            rows = []
            for row in csvreader:
                rows.append(row)
            self.assertEqual(rows[1][1], self.subject_age(self.patient.date_birth))

        shutil.rmtree(temp_dir)

    def test_export_participants_does_not_select_any_attribute_returns_redirect_and_display_warning_message(self):
        response = self.client.post(reverse('export_view'), {'action': ['run']}, follow=True)
        # After POSTing without 'patient_selected' as key for data nargs, the
        # system first redirects to export/view, then to export/, so take
        # the first redirection url and status code.
        first_redirect_url, status_code = response.redirect_chain[0]
        self.assertEqual(status_code, 302)
        self.assertEqual(first_redirect_url, reverse('export_view'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, _('Please select at least one patient attribute'))


class ExportSelection(ExportTestCase):
    TEMP_MEDIA_ROOT = tempfile.mkdtemp()

    def setUp(self):
        super(ExportSelection, self).setUp()

    def tearDown(self):
        self.client.logout()

    def test_experiment_selection_selecting_group(self):
        data = {
            'id_research_projects': self.experiment.research_project.id,
            'id_experiments': self.experiment.id,
            'group_selected': self.group.id,
            'action': 'next-step-participants'
        }

        self.append_session_variable('id_research_projects', [str(self.experiment.research_project.id)])
        self.append_session_variable('id_experiments', [str(self.experiment.id)])
        self.append_session_variable('group_selected', [str(self.group.id)])

        response = self.client.post(reverse('experiment_selection'), data)

        self.assertRedirects(response, '/export/view/', status_code=302, target_status_code=200)

    def test_experiment_selection_withou_select_group(self):

        data = {
            'id_research_projects': self.experiment.research_project.id,
            'id_experiments': self.experiment.id,
            'action': 'next-step-participants'
        }

        self.append_session_variable('id_research_projects', [str(self.experiment.research_project.id)])
        self.append_session_variable('id_experiments', [str(self.experiment.id)])
        response = self.client.post(reverse('experiment_selection'), data)
        self.assertEqual(response.status_code, 200)

    def test_expire_section_when_in_last_export_form_returns_to_first_export_page(self):
        """ Path that is followed when the session is expired and it tries
        to generates the zipped file after loggin again
        1. Flush the session
        2. Post data to export view: the response contains the url to
        reverse to login page
        3. Post credentials in login page to login
        4. Get the reversed url that has to point at export's first page
        """

        self.client.session.flush()

        # Post data to view: data style that is posted to export_view in
        # template
        data = {
            'per_questionnaire': ['on'],
            'per_participant': ['on'],
            'headings': ['code'],
            'patient_selected': ['age*age'],
            'action': ['run'],
            'responses': ['short']
        }
        response = self.client.post(reverse('export_view'), data)

        response2 = self.client.post(response.url, {
            'username': self.user.username,
            'password': self.user_passwd
        })

        # when session expires the request is made with get
        response3 = self.client.get(response2.url)
        self.assertRedirects(response3, reverse('export_menu'), status_code=302, target_status_code=200)
