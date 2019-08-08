def set_limesurvey_api_mocks(mockServer):
    mockServer.return_value.get_session_key.return_value = 'idk208ghdkdg8bu'  # whatever string
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
    mockServer.return_value.get_question_properties.side_effect = [
        {'other': 'N', 'attributes': {'hidn': '1'}, 'subquestions': 'No available answers', 'type': 'N',
         'question_order': 0, 'answeroptions': 'No available answer options', 'gid': 1576,
         'attributes_lang': 'No available attributes', 'title': 'responsibleid',
         'question': 'Responsible Identification number:'},
        {'other': 'N', 'attributes': {'hidden': '1'}, 'subquestions': 'No available answers', 'type': 'D',
         'question_order': 1, 'answeroptions': 'No available answer options', 'gid': 1576,
         'attributes_lang': 'No available attributes', 'title': 'acquisitiondate',
         'question': 'Acquisition date<strong>:</strong><br />\n'},
        {'other': 'N', 'attributes': {'hidden': '1'}, 'subquestions': 'No available answers', 'type': 'N',
         'question_order': 3, 'answeroptions': 'No available answer options', 'gid': 1576,
         'attributes_lang': 'No available attributes', 'title': 'subjectid',
         'question': 'Participant Identification number<b>:</b>'},
        {'other': 'N', 'attributes': 'No available attributes', 'subquestions': 'No available answers', 'type': 'T',
         'question_order': 1, 'answeroptions': 'No available answer options', 'gid': 1577,
         'attributes_lang': 'No available attributes', 'title': 'q1', 'question': 'Questão 1'},
        {'other': 'N', 'attributes': 'No available attributes', 'subquestions': 'No available answers', 'type': 'L',
         'question_order': 2,
         'answeroptions': {'A2': {'order': 2, 'assessment_value': 0, 'scale_id': 0, 'answer': 'Opção 2'},
                           'A1': {'order': 1, 'assessment_value': 0, 'scale_id': 0, 'answer': 'Opção 1'}}, 'gid': 1577,
         'attributes_lang': 'No available attributes', 'title': 'q2', 'question': 'Questão 2'},
        {'other': 'N', 'attributes': {'hidden': '1'}, 'subquestions': 'No available answers', 'type': 'N',
         'question_order': 0, 'answeroptions': 'No available answer options', 'gid': 1578,
         'attributes_lang': 'No available attributes', 'title': 'responsibleid',
         'question': 'Responsible Identification number:'},
        {'other': 'N', 'attributes': {'hidden': '1'}, 'subquestions': 'No available answers', 'type': 'D',
         'question_order': 1, 'answeroptions': 'No available answer options', 'gid': 1578,
         'attributes_lang': 'No available attributes', 'title': 'acquisitiondate',
         'question': 'Acquisition date<strong>:</strong><br />\n'},
        {'other': 'N', 'attributes': {'hidden': '1'}, 'subquestions': 'No available answers', 'type': 'N',
         'question_order': 3, 'answeroptions': 'No available answer options', 'gid': 1578,
         'attributes_lang': 'No available attributes', 'title': 'subjectid',
         'question': 'Participant Identification number<b>:</b>'},
        {'other': 'N', 'attributes': 'No available attributes',
         'subquestions': {'5016': {'scale_id': 0, 'title': 'SQ002', 'question': 'NoOk'},
                          '5015': {'scale_id': 0, 'title': 'SQ001', 'question': 'Ok'}}, 'type': 'F',
         'question_order': 1,
         'answeroptions': {'A2': {'order': 2, 'assessment_value': 0, 'scale_id': 0, 'answer': 'Opção 2'},
                           'A1': {'order': 1, 'assessment_value': 0, 'scale_id': 0, 'answer': 'Opção 1'}}, 'gid': 1579,
         'attributes_lang': 'No available attributes', 'title': 'q1', 'question': 'Questão 1'},
        {'other': 'N', 'attributes': 'No available attributes', 'subquestions': 'No available answers', 'type': 'T',
         'question_order': 1, 'answeroptions': 'No available answer options', 'gid': 1579,
         'attributes_lang': 'No available attributes', 'title': 'SQ001', 'question': 'Ok'},
        {'other': 'N', 'attributes': 'No available attributes', 'subquestions': 'No available answers', 'type': 'T',
         'question_order': 2, 'answeroptions': 'No available answer options', 'gid': 1579,
         'attributes_lang': 'No available attributes', 'title': 'SQ002', 'question': 'NoOk'},
        {'other': 'N', 'attributes': 'No available attributes', 'subquestions': 'No available answers', 'type': '5',
         'question_order': 3, 'answeroptions': 'No available answer options', 'gid': 1579,
         'attributes_lang': 'No available attributes', 'title': 'q2', 'question': 'Questão 2'}
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
