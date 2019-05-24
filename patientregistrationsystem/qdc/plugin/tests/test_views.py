import io
import shutil
import tempfile
import zipfile
from unittest.mock import patch

from django.core.urlresolvers import reverse, resolve
from django.test import override_settings
from django.utils.encoding import smart_str

from export.tests.tests_helper import ExportTestCase
from plugin.models import RandomForests
from plugin.views import send_to_plugin
from patient.tests.tests_orig import UtilTests
from survey.tests.tests_helper import create_survey


class PluginTest(ExportTestCase):
    TEMP_MEDIA_ROOT = tempfile.mkdtemp()

    def setUp(self):
        super(PluginTest, self).setUp()

    def tearDown(self):
        self.client.logout()

    def test_send_to_plugin_status_code(self):
        url = reverse('send_to_plugin')
        response = self.client.get(url, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'plugin/send_to_plugin.html')

    def test_animal_new_url_resolves_animal_new_view(self):
        view = resolve('/plugin/')
        self.assertEquals(view.func, send_to_plugin)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    @patch('survey.abc_search_engine.Server')
    def test_POST_send_to_plugin_returns_zip_file(self, mockServer):
        mockServer.return_value.session_key.return_value = 'idk208ghdkdg8bu'  # whatever string
        mockServer.return_value.get_survey_properties.return_value = {'language': 'en', 'additional_languages': ''}
        mockServer.return_value.export_responses.side_effect = [
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0'
            'aW9uZGF0ZSIsInN1YmplY3RpZCIsInExIiwicTIiCiIxIiwiMTk4MC0wMS0wMSAwMDowMDowMCIsIjIiLCJlbiIsInNJYmozZ3dqdndw'
            'YTJRWSIsIjIiLCIyMDIwLTA5LTA1IDAwOjAwOjAwIiwiOTU5MTYiLCJhYmMiLCJBMSIKIjIiLCIxOTgwLTAxLTAxIDAwOjAwOjAwIiwi'
            'MiIsImVuIiwiV1JGVUFnVGVtenV1OG5EIiwiMiIsIjIwMjAtMDktMDUgMDA6MDA6MDAiLCI5NTkxNyIsImNiYSIsIkEyIgoK',
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0'
            'aW9uZGF0ZSIsInN1YmplY3RpZCIsInExW1NRMDAxXSIsInExW1NRMDAyXSIsInEyIgoiMSIsIjE5ODAtMDEtMDEgMDA6MDA6MDAiLCIyI'
            'iwiZW4iLCJPU1NNYUZWZXdWbDhEMEoiLCIyIiwiMjAyMC0wOS0wNSAwMDowMDowMCIsIjk1OTE2IiwiQTEiLCJBMiIsIjQiCiIyIiwiMT'
            'k4MC0wMS0wMSAwMDowMDowMCIsIjIiLCJlbiIsImZGUG5Uc05VSndSeWUzZyIsIjIiLCIyMDIwLTA5LTA1IDAwOjAwOjAwIiwiOTU5MTc'
            'iLCJBMiIsIkExIiwiMSIKCg=='
        ]
        mockServer.return_value.export_responses_by_token.side_effect = [
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0a'
            'W9uZGF0ZSIsInN1YmplY3RpZCIsInExIiwicTIiCiIxIiwiMTk4MC0wMS0wMSAwMDowMDowMCIsIjIiLCJlbiIsInNJYmozZ3dqdndwYT'
            'JRWSIsIjIiLCIyMDIwLTA5LTA1IDAwOjAwOjAwIiwiOTU5MTYiLCJhYmMiLCJBMSIKCg==',
            'IlJlc3BvbnNlIElEIiwiRGF0ZSBzdWJtaXR0ZWQiLCJMYXN0IHBhZ2UiLCJTdGFydCBsYW5ndWFnZSIsIlRva2VuIiwiUmVzcG9uc2lib'
            'GUgSWRlbnRpZmljYXRpb24gbnVtYmVyOiIsIkFjcXVpc2l0aW9uIGRhdGU6IiwiUGFydGljaXBhbnQgSWRlbnRpZmljYXRpb24gbnVtYm'
            'VyOiIsIlF1ZXN0w6NvIDEiLCJRdWVzdMOjbyAyIgoiMSIsIjE5ODAtMDEtMDEgMDA6MDA6MDAiLCIyIiwiZW4iLCJzSWJqM2d3anZ3cGE'
            'yUVkiLCIyIiwiMjAyMC0wOS0wNSAwMDowMDowMCIsIjk1OTE2IiwiYWJjIiwiQTEiCgo=',
            'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0a'
            'W9uZGF0ZSIsInN1YmplY3RpZCIsInExW1NRMDAxXSIsInExW1NRMDAyXSIsInEyIgoiMSIsIjE5ODAtMDEtMDEgMDA6MDA6MDAiLCIyIi'
            'wiZW4iLCJPU1NNYUZWZXdWbDhEMEoiLCIyIiwiMjAyMC0wOS0wNSAwMDowMDowMCIsIjk1OTE2IiwiQTEiLCJBMiIsIjQiCgo=',
            'IlJlc3BvbnNlIElEIiwiRGF0ZSBzdWJtaXR0ZWQiLCJMYXN0IHBhZ2UiLCJTdGFydCBsYW5ndWFnZSIsIlRva2VuIiwiUmVzcG9uc2lib'
            'GUgSWRlbnRpZmljYXRpb24gbnVtYmVyOiIsIkFjcXVpc2l0aW9uIGRhdGU6IiwiUGFydGljaXBhbnQgSWRlbnRpZmljYXRpb24gbnVtYm'
            'VyOiIsIlF1ZXN0w6NvIDEgW09rXSIsIlF1ZXN0w6NvIDEgW05vT2tdIiwiUXVlc3TDo28gMiIKIjEiLCIxOTgwLTAxLTAxIDAwOjAwOjA'
            'wIiwiMiIsImVuIiwiT1NTTWFGVmV3Vmw4RDBKIiwiMiIsIjIwMjAtMDktMDUgMDA6MDA6MDAiLCI5NTkxNiIsIkExIiwiQTIiLCI0IgoK'
        ]
        mockServer.return_value.list_groups.side_effect = \
            4 * [[
                {'id': {'gid': 1576, 'language': 'en'}, 'group_order': 1, 'randomization_group': '',
                 'description': '', 'sid': 225461, 'gid': 1576, 'language': 'en', 'group_name': 'Identification',
                 'grelevance': ''},
                {'id': {'gid': 1577, 'language': 'en'}, 'group_order': 2, 'randomization_group': '',
                 'description': '', 'sid': 225461, 'gid': 1577, 'language': 'en', 'group_name': 'Grupo 1',
                 'grelevance': ''},
            ]] + 4 * [[
                {'id': {'gid': 1578, 'language': 'en'}, 'group_order': 1, 'randomization_group': '', 'description': '',
                 'sid': 888656, 'gid': 1578, 'language': 'en', 'group_name': 'Identification', 'grelevance': ''},
                {'id': {'gid': 1579, 'language': 'en'}, 'group_order': 2, 'randomization_group': '', 'description': '',
                 'sid': 888656, 'gid': 1579, 'language': 'en', 'group_name': 'Grupo 1', 'grelevance': ''}
            ]]
        mockServer.return_value.list_questions.side_effect = [
            [
                {'type': 'N', 'same_default': 0, 'help': '', 'gid': 1576, 'preg': '', 'language': 'en',
                 'title': 'responsibleid', 'sid': 225461, 'modulename': None, 'parent_qid': 0, 'qid': 5006,
                 'mandatory': 'Y', 'other': 'N', 'question': 'Responsible Identification number:', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5006}, 'relevance': '1', 'question_order': 0},
                {'type': 'D', 'same_default': 0, 'help': '', 'gid': 1576, 'preg': '', 'language': 'en',
                 'title': 'acquisitiondate', 'sid': 225461, 'modulename': None, 'parent_qid': 0, 'qid': 5007,
                 'mandatory': 'Y', 'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5007}, 'relevance': '1', 'question_order': 1},
                {'type': 'N', 'same_default': 0, 'help': '', 'gid': 1576, 'preg': '', 'language': 'en',
                 'title': 'subjectid', 'sid': 225461, 'modulename': None, 'parent_qid': 0, 'qid': 5008, 'mandatory': 'Y',
                 'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5008}, 'relevance': '1', 'question_order': 3}
            ],
            [
                {'type': 'T', 'same_default': 0, 'help': '', 'gid': 1577, 'preg': '', 'language': 'en', 'title': 'q1',
                 'sid': 225461, 'modulename': '', 'parent_qid': 0, 'qid': 5009, 'mandatory': 'N', 'other': 'N',
                 'question': 'Questão 1', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5009}, 'relevance': '1',
                 'question_order': 1},
                {'type': 'L', 'same_default': 0, 'help': '', 'gid': 1577, 'preg': '', 'language': 'en', 'title': 'q2',
                 'sid': 225461, 'modulename': None, 'parent_qid': 0, 'qid': 5010, 'mandatory': 'N', 'other': 'N',
                 'question': 'Questão 2', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5010}, 'relevance': '1',
                 'question_order': 2}
            ],
            [
                {'type': 'N', 'same_default': 0, 'help': '', 'gid': 1576, 'preg': '', 'language': 'en',
                 'title': 'responsibleid', 'sid': 225461, 'modulename': None, 'parent_qid': 0, 'qid': 5006,
                 'mandatory': 'Y', 'other': 'N', 'question': 'Responsible Identification number:', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5006}, 'relevance': '1', 'question_order': 0},
                {'type': 'D', 'same_default': 0, 'help': '', 'gid': 1576, 'preg': '', 'language': 'en',
                 'title': 'acquisitiondate', 'sid': 225461, 'modulename': None, 'parent_qid': 0, 'qid': 5007,
                 'mandatory': 'Y', 'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5007}, 'relevance': '1', 'question_order': 1},
                {'type': 'N', 'same_default': 0, 'help': '', 'gid': 1576, 'preg': '', 'language': 'en',
                 'title': 'subjectid', 'sid': 225461, 'modulename': None, 'parent_qid': 0, 'qid': 5008, 'mandatory': 'Y',
                 'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5008}, 'relevance': '1', 'question_order': 3},
                {'type': 'T', 'same_default': 0, 'help': '', 'gid': 1577, 'preg': '', 'language': 'en', 'title': 'q1',
                 'sid': 225461, 'modulename': '', 'parent_qid': 0, 'qid': 5009, 'mandatory': 'N', 'other': 'N',
                 'question': 'Questão 1', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5009}, 'relevance': '1',
                 'question_order': 1},
                {'type': 'L', 'same_default': 0, 'help': '', 'gid': 1577, 'preg': '', 'language': 'en', 'title': 'q2',
                 'sid': 225461, 'modulename': None, 'parent_qid': 0, 'qid': 5010, 'mandatory': 'N', 'other': 'N',
                 'question': 'Questão 2', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5010}, 'relevance': '1',
                 'question_order': 2}
            ],
            [
                {'type': 'N', 'same_default': 0, 'help': '', 'gid': 1578, 'preg': '', 'language': 'en',
                 'title': 'responsibleid', 'sid': 888656, 'modulename': None, 'parent_qid': 0, 'qid': 5011,
                 'mandatory': 'Y', 'other': 'N', 'question': 'Responsible Identification number:', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5011}, 'relevance': '1', 'question_order': 0},
                {'type': 'D', 'same_default': 0, 'help': '', 'gid': 1578, 'preg': '', 'language': 'en',
                 'title': 'acquisitiondate', 'sid': 888656, 'modulename': None, 'parent_qid': 0, 'qid': 5012,
                 'mandatory': 'Y', 'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5012}, 'relevance': '1', 'question_order': 1},
                {'type': 'N', 'same_default': 0, 'help': '', 'gid': 1578, 'preg': '', 'language': 'en',
                 'title': 'subjectid', 'sid': 888656, 'modulename': None, 'parent_qid': 0, 'qid': 5013, 'mandatory': 'Y',
                 'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5013}, 'relevance': '1', 'question_order': 3}
            ],
            [
                {'type': 'F', 'same_default': 0, 'help': '', 'gid': 1579, 'preg': '', 'language': 'en', 'title': 'q1',
                 'sid': 888656, 'modulename': None, 'parent_qid': 0, 'qid': 5014, 'mandatory': 'N', 'other': 'N',
                 'question': 'Questão 1', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5014}, 'relevance': '1',
                 'question_order': 1},
                {'type': 'T', 'same_default': 0, 'help': None, 'gid': 1579, 'preg': None, 'language': 'en',
                 'title': 'SQ001', 'sid': 888656, 'modulename': None, 'parent_qid': 5014, 'qid': 5015, 'mandatory': None,
                 'other': 'N', 'question': 'Ok', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5015}, 'relevance': '1',
                 'question_order': 1},
                {'type': 'T', 'same_default': 0, 'help': None, 'gid': 1579, 'preg': None, 'language': 'en',
                 'title': 'SQ002', 'sid': 888656, 'modulename': None, 'parent_qid': 5014, 'qid': 5016, 'mandatory': None,
                 'other': 'N', 'question': 'NoOk', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5016}, 'relevance': '',
                 'question_order': 2},
                {'type': '5', 'same_default': 0, 'help': '', 'gid': 1579, 'preg': '', 'language': 'en', 'title': 'q2',
                 'sid': 888656, 'modulename': '', 'parent_qid': 0, 'qid': 5017, 'mandatory': 'N', 'other': 'N',
                 'question': 'Questão 2', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5017}, 'relevance': '1',
                 'question_order': 3}
            ],
            [
                {'type': 'N', 'same_default': 0, 'help': '', 'gid': 1578, 'preg': '', 'language': 'en',
                 'title': 'responsibleid', 'sid': 888656, 'modulename': None, 'parent_qid': 0, 'qid': 5011,
                 'mandatory': 'Y', 'other': 'N', 'question': 'Responsible Identification number:', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5011}, 'relevance': '1', 'question_order': 0},
                {'type': 'D', 'same_default': 0, 'help': '', 'gid': 1578, 'preg': '', 'language': 'en',
                 'title': 'acquisitiondate', 'sid': 888656, 'modulename': None, 'parent_qid': 0, 'qid': 5012,
                 'mandatory': 'Y', 'other': 'N', 'question': 'Acquisition date<strong>:</strong><br />\n', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5012}, 'relevance': '1', 'question_order': 1},
                {'type': 'N', 'same_default': 0, 'help': '', 'gid': 1578, 'preg': '', 'language': 'en',
                 'title': 'subjectid', 'sid': 888656, 'modulename': None, 'parent_qid': 0, 'qid': 5013, 'mandatory': 'Y',
                 'other': 'N', 'question': 'Participant Identification number<b>:</b>', 'scale_id': 0,
                 'id': {'language': 'en', 'qid': 5013}, 'relevance': '1', 'question_order': 3},
                {'type': 'F', 'same_default': 0, 'help': '', 'gid': 1579, 'preg': '', 'language': 'en', 'title': 'q1',
                 'sid': 888656, 'modulename': None, 'parent_qid': 0, 'qid': 5014, 'mandatory': 'N', 'other': 'N',
                 'question': 'Questão 1', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5014}, 'relevance': '1',
                 'question_order': 1},
                {'type': 'T', 'same_default': 0, 'help': None, 'gid': 1579, 'preg': None, 'language': 'en',
                 'title': 'SQ001', 'sid': 888656, 'modulename': None, 'parent_qid': 5014, 'qid': 5015, 'mandatory': None,
                 'other': 'N', 'question': 'Ok', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5015}, 'relevance': '1',
                 'question_order': 1},
                {'type': 'T', 'same_default': 0, 'help': None, 'gid': 1579, 'preg': None, 'language': 'en',
                 'title': 'SQ002', 'sid': 888656, 'modulename': None, 'parent_qid': 5014, 'qid': 5016, 'mandatory': None,
                 'other': 'N', 'question': 'NoOk', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5016}, 'relevance': '',
                 'question_order': 2},
                {'type': '5', 'same_default': 0, 'help': '', 'gid': 1579, 'preg': '', 'language': 'en', 'title': 'q2',
                 'sid': 888656, 'modulename': '', 'parent_qid': 0, 'qid': 5017, 'mandatory': 'N', 'other': 'N',
                 'question': 'Questão 2', 'scale_id': 0, 'id': {'language': 'en', 'qid': 5017}, 'relevance': '1',
                 'question_order': 3}],
        ]
        mockServer.return_value.get_question_properties.side_effect = \
            2 * [
                {'subquestions': 'No available answers', 'gid': 1576, 'type': 'N', 'other': 'N',
                 'attributes_lang': 'No available attributes', 'answeroptions': 'No available answer options',
                 'title': 'responsibleid', 'question_order': 0, 'question': 'Responsible Identification number:',
                 'attributes': {'hidden': '1'}},
                {'subquestions': 'No available answers', 'gid': 1576, 'type': 'D', 'other': 'N',
                 'attributes_lang': 'No available attributes', 'answeroptions': 'No available answer options',
                 'title': 'acquisitiondate', 'question_order': 1, 'question': 'Acquisition date<strong>:</strong><br />\n',
                 'attributes': {'hidden': '1'}},
                {'subquestions': 'No available answers', 'gid': 1576, 'type': 'N', 'other': 'N',
                 'attributes_lang': 'No available attributes', 'answeroptions': 'No available answer options',
                 'title': 'subjectid', 'question_order': 3, 'question': 'Participant Identification number<b>:</b>',
                 'attributes': {'hidden': '1'}},
                {'subquestions': 'No available answers', 'gid': 1577, 'type': 'T', 'other': 'N',
                 'attributes_lang': 'No available attributes', 'answeroptions': 'No available answer options',
                 'title': 'q1', 'question_order': 1, 'question': 'Questão 1', 'attributes': 'No available attributes'},
                {'subquestions': 'No available answers', 'gid': 1577, 'type': 'L', 'other': 'N',
                 'attributes_lang': 'No available attributes',
                 'answeroptions': {'A1': {'assessment_value': 0, 'answer': 'Opção 1', 'scale_id': 0, 'order': 1},
                                   'A2': {'assessment_value': 0, 'answer': 'Opção 2', 'scale_id': 0, 'order': 2}},
                 'title': 'q2', 'question_order': 2, 'question': 'Questão 2', 'attributes': 'No available attributes'}
            ] + 2 * [
                {'subquestions': 'No available answers', 'gid': 1578, 'type': 'N', 'other': 'N',
                 'attributes_lang': 'No available attributes', 'answeroptions': 'No available answer options',
                 'title': 'responsibleid', 'question_order': 0, 'question': 'Responsible Identification number:',
                 'attributes': {'hidden': '1'}},
                {'subquestions': 'No available answers', 'gid': 1578, 'type': 'D', 'other': 'N',
                 'attributes_lang': 'No available attributes', 'answeroptions': 'No available answer options',
                 'title': 'acquisitiondate', 'question_order': 1, 'question': 'Acquisition date<strong>:</strong><br />\n',
                 'attributes': {'hidden': '1'}},
                {'subquestions': 'No available answers', 'gid': 1578, 'type': 'N', 'other': 'N',
                 'attributes_lang': 'No available attributes', 'answeroptions': 'No available answer options',
                 'title': 'subjectid', 'question_order': 3, 'question': 'Participant Identification number<b>:</b>',
                 'attributes': {'hidden': '1'}},
                {'subquestions': {'5016': {'title': 'SQ002', 'question': 'NoOk', 'scale_id': 0},
                                  '5015': {'title': 'SQ001', 'question': 'Ok', 'scale_id': 0}}, 'gid': 1579, 'type': 'F',
                 'other': 'N', 'attributes_lang': 'No available attributes',
                 'answeroptions': {'A1': {'assessment_value': 0, 'answer': 'Opção 1', 'scale_id': 0, 'order': 1},
                                   'A2': {'assessment_value': 0, 'answer': 'Opção 2', 'scale_id': 0, 'order': 2}},
                 'title': 'q1', 'question_order': 1, 'question': 'Questão 1', 'attributes': 'No available attributes'},
                {'subquestions': 'No available answers', 'gid': 1579, 'type': 'T', 'other': 'N',
                 'attributes_lang': 'No available attributes', 'answeroptions': 'No available answer options',
                 'title': 'SQ001', 'question_order': 1, 'question': 'Ok', 'attributes': 'No available attributes'},
                {'subquestions': 'No available answers', 'gid': 1579, 'type': 'T', 'other': 'N',
                 'attributes_lang': 'No available attributes', 'answeroptions': 'No available answer options',
                 'title': 'SQ002', 'question_order': 2, 'question': 'NoOk', 'attributes': 'No available attributes'},
                {'subquestions': 'No available answers', 'gid': 1579, 'type': '5', 'other': 'N',
                 'attributes_lang': 'No available attributes', 'answeroptions': 'No available answer options',
                 'title': 'q2', 'question_order': 3, 'question': 'Questão 2', 'attributes': 'No available attributes'}
            ]

        mockServer.return_value.get_participant_properties.side_effect = [
            {'token': 'sIbj3gwjvwpa2QY'}, {'token': 'OSSMaFVewVl8D0J'},
            {'token': 'sIbj3gwjvwpa2QY'}, {'token': 'WRFUAgTemzuu8nD'},
            {'token': 'OSSMaFVewVl8D0J'}, {'token': 'fFPnTsNUJwRye3g'}
        ]
        mockServer.return_value.get_language_properties.side_effect = [
            {'surveyls_title': 'Admission Assessment Plugin'},
            {'surveyls_title': 'Surgical Evaluation Plugin'},
            {'surveyls_title': 'Admission Assessment Plugin'},
            {'surveyls_title': 'Surgical Evaluation Plugin'}
        ]

        patient2 = UtilTests.create_patient(self.user)
        survey1 = create_survey()
        survey2 = create_survey(505050)
        RandomForests.objects.create(admission_assessment=survey1, surgical_evaluation=survey2)
        UtilTests.create_response_survey(self.user, self.patient, survey1, 21)
        UtilTests.create_response_survey(self.user, self.patient, survey2, 21)
        UtilTests.create_response_survey(self.user, patient2, survey1, 50)
        UtilTests.create_response_survey(self.user, patient2, survey2, 50)
        response = self.client.post(
            reverse('send_to_plugin'),
            data={
                'opt_floresta': ['on'], 'patient_selected': ['age*age'],
                'to[]': [str(self.patient.id), str(patient2.id)]
            })
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.get('Content-Disposition'), 'attachment; filename="%s"' % smart_str('export.zip'))
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

        shutil.rmtree(self.TEMP_MEDIA_ROOT)
