# Mocks to replace old tests that had using real consumption of
# LimeSurvey RPC API. The mocks were created based in old responses from
# the consumption of the API. So they are thick and can be decreased.

LIMESURVEY_SURVEY_ID = 212121


def set_mocks1(mockServer):
    mockServer.return_value.get_survey_properties.return_value = {'additional_languages': '', 'language': 'en'}
    mockServer.return_value.get_participant_properties.side_effect = 4 * [
        {'completed': '2019-06-26'},
    ] + [
        {'token': 'JLsKj3ZDO3Iof91'},
        {'completed': '2019-06-26'},
        {'token': 'VLqIkSdSRzCanyW'},
        {'completed': '2019-06-26'},
        {'token': 'IhbAZg38yDSt8jZ'}
    ]
    mockServer.return_value.export_responses.return_value = \
        'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9u' \
        'ZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVj' \
        'b3VudF0iCiIxIiwiMjAxOS0wNi0yNiAwOToxNjo0MyIsIjIiLCJlbiIsIkpMc0tqM1pETzNJb2Y5MSIsIjUzOTYzIiwiMjAxOS0wNi0yNiAw' \
        'OToxNjo0Mi43NzI2MiIsIjE3NzQ4MiIsIk9sw6EgTXVuZG8hIiwiSGFsbG8gV2VsdCEiLCIiLCIiCiIyIiwiMjAxOS0wNi0yNiAxMDowMjoy' \
        'NCIsIjIiLCJlbiIsIlZMcUlrU2RTUnpDYW55VyIsIjUzOTYzIiwiMjAxOS0wNi0yNiAxMDowMjoyMi40ODI5MzgiLCIxNzc0ODMiLCJPbMOh' \
        'IE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoiMyIsIjIwMTktMDYtMjYgMTA6MDM6MjAiLCIyIiwiZW4iLCJJaGJBWmczOHlEU3Q4aloi' \
        'LCI1Mzk2MyIsIjIwMTktMDYtMjYgMTA6MDM6MTkuNjg3ODA3IiwiMTc3NDg0IiwiT2zDoSBNdW5kbyEiLCJIYWxsbyBXZWx0ISIsIiIsIiIK' \
        'Cg=='
    mockServer.return_value.list_groups.return_value = \
        [
            {
                'language': 'en', 'group_name': 'First group', 'randomization_group': '',
                'id': {'language': 'en', 'gid': 1831}, 'sid': LIMESURVEY_SURVEY_ID, 'description': '', 'gid': 1831,
                'grelevance': '', 'group_order': 2},
            {
                'language': 'en', 'group_name': 'Identification', 'randomization_group': '',
                'id': {'language': 'en', 'gid': 1830}, 'sid': LIMESURVEY_SURVEY_ID, 'description': '', 'gid': 1830,
                'grelevance': '', 'group_order': 1
            },
            {
                'language': 'pt', 'group_name': 'Identification', 'randomization_group': '',
                'id': {'language': 'pt', 'gid': 1830}, 'sid': LIMESURVEY_SURVEY_ID, 'description': '', 'gid': 1830,
                'grelevance': '', 'group_order': 1
            },
        ]
    mockServer.return_value.list_questions.side_effect = [
        [{'language': 'en', 'type': '|', 'modulename': None, 'id': {'language': 'en', 'qid': 5793},
          'same_default': 0, 'gid': 1831, 'qid': 5793, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'fileUpload', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'N', 'parent_qid': 0,
          'question_order': 3, 'question': 'Has fileupload?'},
         {'language': 'en', 'type': 'T', 'modulename': '', 'id': {'language': 'en', 'qid': 5792}, 'same_default': 0,
          'gid': 1831, 'qid': 5792, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'secondQuestion', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
          'question_order': 2, 'question': 'Second question'},
         {'language': 'en', 'type': 'T', 'modulename': '', 'id': {'language': 'en', 'qid': 5791}, 'same_default': 0,
          'gid': 1831, 'qid': 5791, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'firstQuestion', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
          'question_order': 1, 'question': 'First question'}],
        [{'language': 'en', 'type': 'N', 'modulename': None, 'id': {'language': 'en', 'qid': 5790},
          'same_default': 0, 'gid': 1830, 'qid': 5790, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'subjectid', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
          'question_order': 3, 'question': 'Participant Identification number<b>:</b>'},
         {'language': 'en', 'type': 'D', 'modulename': None, 'id': {'language': 'en', 'qid': 5789},
          'same_default': 0, 'gid': 1830, 'qid': 5789, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'acquisitiondate', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
          'question_order': 1, 'question': 'Acquisition date<strong>:</strong><br />\n'},
         {'language': 'en', 'type': 'N', 'modulename': None, 'id': {'language': 'en', 'qid': 5788},
          'same_default': 0, 'gid': 1830, 'qid': 5788, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'responsibleid', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
          'question_order': 0, 'question': 'Responsible Identification number:'}],
        [{'language': 'en', 'type': '|', 'modulename': None, 'id': {'language': 'en', 'qid': 5793},
          'same_default': 0, 'gid': 1831, 'qid': 5793, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'fileUpload', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'N', 'parent_qid': 0,
          'question_order': 3, 'question': 'Has fileupload?'},
         {'language': 'en', 'type': 'T', 'modulename': '', 'id': {'language': 'en', 'qid': 5792}, 'same_default': 0,
          'gid': 1831, 'qid': 5792, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'secondQuestion', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
          'question_order': 2, 'question': 'Second question'},
         {'language': 'en', 'type': 'T', 'modulename': '', 'id': {'language': 'en', 'qid': 5791}, 'same_default': 0,
          'gid': 1831, 'qid': 5791, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'firstQuestion', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
          'question_order': 1, 'question': 'First question'},
         {'language': 'en', 'type': 'N', 'modulename': None, 'id': {'language': 'en', 'qid': 5790},
          'same_default': 0, 'gid': 1830, 'qid': 5790, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'subjectid', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
          'question_order': 3, 'question': 'Participant Identification number<b>:</b>'},
         {'language': 'en', 'type': 'D', 'modulename': None, 'id': {'language': 'en', 'qid': 5789},
          'same_default': 0, 'gid': 1830, 'qid': 5789, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'acquisitiondate', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
          'question_order': 1, 'question': 'Acquisition date<strong>:</strong><br />\n'},
         {'language': 'en', 'type': 'N', 'modulename': None, 'id': {'language': 'en', 'qid': 5788},
          'same_default': 0, 'gid': 1830, 'qid': 5788, 'relevance': '1', 'preg': '', 'other': 'N', 'help': '',
          'title': 'responsibleid', 'sid': LIMESURVEY_SURVEY_ID, 'scale_id': 0, 'mandatory': 'Y', 'parent_qid': 0,
          'question_order': 0, 'question': 'Responsible Identification number:'}]
    ]
    mockServer.return_value.get_question_properties.side_effect = 2 * [
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
    ]
    mockServer.return_value.get_language_properties.return_value = {'surveyls_title': 'Test questionnaire'}


def set_mocks2(mockServer):
    mockServer.return_value.get_survey_properties.return_value = {'additional_languages': '', 'language': 'en'}
    mockServer.return_value.get_participant_properties.side_effect = 3 * [
        {'completed': '2019-06-24'}
    ] + [
        {'token': 'vnCfOsrabtuTfYs'},
        {'completed': '2019-06-24'},
        {'token': 'G0lmOoIe6IElYKF'}
    ]
    mockServer.return_value.export_responses.return_value = \
        'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9u' \
        'ZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVj' \
        'b3VudF0iCiIxIiwiMjAxOS0wNi0yNCAxNTo0OToxMSIsIjIiLCJlbiIsInZuQ2ZPc3JhYnR1VGZZcyIsIjUzOTUzIiwiMjAxOS0wNi0yNCAx' \
        'NTo0OTowNi43ODcwODIiLCIxNzc0NjEiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoiMiIsIjIwMTktMDYtMjQgMTU6NTE6' \
        'MTUiLCIyIiwiZW4iLCJHMGxtT29JZTZJRWxZS0YiLCI1Mzk1MyIsIjIwMTktMDYtMjQgMTU6NTE6MDcuNzIwNDgxIiwiMTc3NDYyIiwiT2zD' \
        'oSBNdW5kbyEiLCJIYWxsbyBXZWx0ISIsIiIsIiIKCg=='
    mockServer.return_value.list_groups.return_value = [
        {'gid': 1825, 'group_name': 'First group', 'description': '', 'group_order': 2, 'sid': LIMESURVEY_SURVEY_ID,
         'randomization_group': '', 'grelevance': '', 'id': {'gid': 1825, 'language': 'en'}, 'language': 'en'},
        {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': LIMESURVEY_SURVEY_ID,
         'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'en'}, 'language': 'en'},
        {'gid': 1824, 'group_name': 'Identification', 'description': '', 'group_order': 1, 'sid': LIMESURVEY_SURVEY_ID,
         'randomization_group': '', 'grelevance': '', 'id': {'gid': 1824, 'language': 'pt-BR'},
         'language': 'pt-BR'}
    ]
    mockServer.return_value.list_questions.side_effect = [
        [{'other': 'N', 'parent_qid': 0, 'type': '|', 'question_order': 3, 'question': 'Has fileupload?',
          'modulename': None, 'relevance': '1', 'id': {'qid': 5775, 'language': 'en'}, 'title': 'fileUpload',
          'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0,
          'qid': 5775, 'mandatory': 'N'},
         {'other': 'N', 'parent_qid': 0, 'type': 'T', 'question_order': 2, 'question': 'Second question',
          'modulename': '', 'relevance': '1', 'id': {'qid': 5774, 'language': 'en'}, 'title': 'secondQuestion',
          'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0,
          'qid': 5774, 'mandatory': 'Y'},
         {'other': 'N', 'parent_qid': 0, 'type': 'T', 'question_order': 1, 'question': 'First question',
          'modulename': '', 'relevance': '1', 'id': {'qid': 5773, 'language': 'en'}, 'title': 'firstQuestion',
          'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0,
          'qid': 5773, 'mandatory': 'Y'}],
        [{'other': 'N', 'parent_qid': 0, 'type': 'N', 'question_order': 3,
          'question': 'Participant Identification number<b>:</b>', 'modulename': None, 'relevance': '1',
          'id': {'qid': 5772, 'language': 'en'}, 'title': 'subjectid', 'language': 'en', 'gid': 1824, 'preg': '',
          'help': '', 'scale_id': 0, 'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0, 'qid': 5772, 'mandatory': 'Y'},
         {'other': 'N', 'parent_qid': 0, 'type': 'D', 'question_order': 1,
          'question': 'Acquisition date<strong>:</strong><br />\n', 'modulename': None, 'relevance': '1',
          'id': {'qid': 5771, 'language': 'en'}, 'title': 'acquisitiondate', 'language': 'en', 'gid': 1824,
          'preg': '', 'help': '', 'scale_id': 0, 'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0, 'qid': 5771, 'mandatory': 'Y'},
         {'other': 'N', 'parent_qid': 0, 'type': 'N', 'question_order': 0,
          'question': 'Responsible Identification number:', 'modulename': None, 'relevance': '1',
          'id': {'qid': 5770, 'language': 'en'}, 'title': 'responsibleid', 'language': 'en', 'gid': 1824,
          'preg': '', 'help': '', 'scale_id': 0, 'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0, 'qid': 5770, 'mandatory': 'Y'}],
        [{'other': 'N', 'parent_qid': 0, 'type': '|', 'question_order': 3, 'question': 'Has fileupload?',
          'modulename': None, 'relevance': '1', 'id': {'qid': 5775, 'language': 'en'}, 'title': 'fileUpload',
          'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0,
          'qid': 5775, 'mandatory': 'N'},
         {'other': 'N', 'parent_qid': 0, 'type': 'T', 'question_order': 2, 'question': 'Second question',
          'modulename': '', 'relevance': '1', 'id': {'qid': 5774, 'language': 'en'}, 'title': 'secondQuestion',
          'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0,
          'qid': 5774, 'mandatory': 'Y'},
         {'other': 'N', 'parent_qid': 0, 'type': 'T', 'question_order': 1, 'question': 'First question',
          'modulename': '', 'relevance': '1', 'id': {'qid': 5773, 'language': 'en'}, 'title': 'firstQuestion',
          'language': 'en', 'gid': 1825, 'preg': '', 'help': '', 'scale_id': 0, 'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0,
          'qid': 5773, 'mandatory': 'Y'},
         {'other': 'N', 'parent_qid': 0, 'type': 'N', 'question_order': 3,
          'question': 'Participant Identification number<b>:</b>',
          'modulename': None, 'relevance': '1',
          'id': {'qid': 5772, 'language': 'en'}, 'title': 'subjectid',
          'language': 'en', 'gid': 1824, 'preg': '', 'help': '', 'scale_id': 0,
          'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0, 'qid': 5772, 'mandatory': 'Y'},
         {'other': 'N', 'parent_qid': 0, 'type': 'D', 'question_order': 1,
          'question': 'Acquisition date<strong>:</strong><br />\n', 'modulename': None, 'relevance': '1',
          'id': {'qid': 5771, 'language': 'en'}, 'title': 'acquisitiondate', 'language': 'en', 'gid': 1824,
          'preg': '', 'help': '', 'scale_id': 0, 'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0, 'qid': 5771, 'mandatory': 'Y'},
         {'other': 'N', 'parent_qid': 0, 'type': 'N', 'question_order': 0,
          'question': 'Responsible Identification number:', 'modulename': None, 'relevance': '1',
          'id': {'qid': 5770, 'language': 'en'}, 'title': 'responsibleid', 'language': 'en', 'gid': 1824,
          'preg': '', 'help': '', 'scale_id': 0, 'sid': LIMESURVEY_SURVEY_ID, 'same_default': 0, 'qid': 5770, 'mandatory': 'Y'}]

    ]
    mockServer.return_value.get_question_properties.side_effect = 2 * [
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


def set_mocks3(mockServer):
    mockServer.return_value.get_survey_properties.return_value = {'additional_languages': '', 'language': 'en'}
    mockServer.return_value.get_participant_properties.side_effect = 3 * [
        {'completed': '2019-06-26'}
    ] + [
        {'token': 'pO9iPqlkQzD4zwG'},
        {'completed': '2019-06-26'},
        {'token': 'g7GaPTLHc2rB6TV'}
    ]
    mockServer.return_value.export_responses.return_value = \
        'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9u' \
        'ZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVj' \
        'b3VudF0iCiIxIiwiMjAxOS0wNi0yNiAxMTozNDo1MCIsIjIiLCJlbiIsImc3R2FQVExIYzJyQjZUViIsIjUzOTY3IiwiMjAxOS0wNi0yNiAx' \
        'MTozNDo1MC43MDYzNzMiLCIxNzc0OTMiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoiMiIsIjIwMTktMDYtMjYgMTE6MzQ6' \
        'NTEiLCIyIiwiZW4iLCJwTzlpUHFsa1F6RDR6d0ciLCI1Mzk2NyIsIjIwMTktMDYtMjYgMTE6MzQ6NTEuMzI0MzgiLCIxNzc0OTQiLCJPbMOh' \
        'IE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoK'
    mockServer.return_value.list_groups.return_value = [
        {'grelevance': '', 'group_name': 'First group', 'group_order': 2, 'gid': 1835, 'description': '',
         'randomization_group': '', 'sid': LIMESURVEY_SURVEY_ID, 'id': {'language': 'en', 'gid': 1835},
         'language': 'en'},
        {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
         'randomization_group': '', 'sid': LIMESURVEY_SURVEY_ID, 'id': {'language': 'en', 'gid': 1834},
         'language': 'en'},
        {'grelevance': '', 'group_name': 'Identification', 'group_order': 1, 'gid': 1834, 'description': '',
         'randomization_group': '', 'sid': LIMESURVEY_SURVEY_ID, 'id': {'language': 'pt-BR', 'gid': 1834},
         'language': 'pt-BR'},
    ]
    mockServer.return_value.list_questions.side_effect = 2 * [
        [{'same_default': 0, 'parent_qid': 0, 'question': 'Has fileupload?', 'preg': '', 'question_order': 3,
          'other': 'N', 'modulename': None, 'type': '|', 'qid': 5805, 'mandatory': 'N', 'sid': LIMESURVEY_SURVEY_ID,
          'help': '',
          'scale_id': 0, 'id': {'qid': 5805, 'language': 'en'}, 'relevance': '1', 'language': 'en',
          'title': 'fileUpload', 'gid': 1835},
         {'same_default': 0, 'parent_qid': 0, 'question': 'Second question', 'preg': '', 'question_order': 2,
          'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5804, 'mandatory': 'Y', 'sid': LIMESURVEY_SURVEY_ID,
          'help': '',
          'scale_id': 0, 'id': {'qid': 5804, 'language': 'en'}, 'relevance': '1', 'language': 'en',
          'title': 'secondQuestion', 'gid': 1835},
         {'same_default': 0, 'parent_qid': 0, 'question': 'First question', 'preg': '', 'question_order': 1,
          'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5803, 'mandatory': 'Y', 'sid': LIMESURVEY_SURVEY_ID,
          'help': '',
          'scale_id': 0, 'id': {'qid': 5803, 'language': 'en'}, 'relevance': '1', 'language': 'en',
          'title': 'firstQuestion', 'gid': 1835}],
        [{'same_default': 0, 'parent_qid': 0, 'question': 'Participant Identification number<b>:</b>', 'preg': '',
          'question_order': 3, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5802, 'mandatory': 'Y',
          'sid': LIMESURVEY_SURVEY_ID, 'help': '', 'scale_id': 0, 'id': {'qid': 5802, 'language': 'en'},
          'relevance': '1',
          'language': 'en', 'title': 'subjectid', 'gid': 1834},
         {'same_default': 0, 'parent_qid': 0, 'question': 'Acquisition date<strong>:</strong><br />\n', 'preg': '',
          'question_order': 1, 'other': 'N', 'modulename': None, 'type': 'D', 'qid': 5801, 'mandatory': 'Y',
          'sid': LIMESURVEY_SURVEY_ID, 'help': '', 'scale_id': 0, 'id': {'qid': 5801, 'language': 'en'},
          'relevance': '1',
          'language': 'en', 'title': 'acquisitiondate', 'gid': 1834},
         {'same_default': 0, 'parent_qid': 0, 'question': 'Responsible Identification number:', 'preg': '',
          'question_order': 0, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5800, 'mandatory': 'Y',
          'sid': LIMESURVEY_SURVEY_ID, 'help': '', 'scale_id': 0, 'id': {'qid': 5800, 'language': 'en'},
          'relevance': '1',
          'language': 'en', 'title': 'responsibleid', 'gid': 1834}]
    ] + 2 * [
        [{'same_default': 0, 'parent_qid': 0, 'question': 'Has fileupload?', 'preg': '', 'question_order': 3,
          'other': 'N', 'modulename': None, 'type': '|', 'qid': 5805, 'mandatory': 'N', 'sid': LIMESURVEY_SURVEY_ID,
          'help': '',
          'scale_id': 0, 'id': {'qid': 5805, 'language': 'en'}, 'relevance': '1', 'language': 'en',
          'title': 'fileUpload', 'gid': 1835},
         {'same_default': 0, 'parent_qid': 0, 'question': 'Second question', 'preg': '', 'question_order': 2,
          'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5804, 'mandatory': 'Y', 'sid': LIMESURVEY_SURVEY_ID,
          'help': '',
          'scale_id': 0, 'id': {'qid': 5804, 'language': 'en'}, 'relevance': '1', 'language': 'en',
          'title': 'secondQuestion', 'gid': 1835},
         {'same_default': 0, 'parent_qid': 0, 'question': 'First question', 'preg': '', 'question_order': 1,
          'other': 'N', 'modulename': '', 'type': 'T', 'qid': 5803, 'mandatory': 'Y', 'sid': LIMESURVEY_SURVEY_ID,
          'help': '',
          'scale_id': 0, 'id': {'qid': 5803, 'language': 'en'}, 'relevance': '1', 'language': 'en',
          'title': 'firstQuestion', 'gid': 1835},
         {'same_default': 0, 'parent_qid': 0, 'question': 'Participant Identification number<b>:</b>', 'preg': '',
          'question_order': 3, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5802, 'mandatory': 'Y',
          'sid': LIMESURVEY_SURVEY_ID, 'help': '', 'scale_id': 0, 'id': {'qid': 5802, 'language': 'en'},
          'relevance': '1',
          'language': 'en', 'title': 'subjectid', 'gid': 1834},
         {'same_default': 0, 'parent_qid': 0, 'question': 'Acquisition date<strong>:</strong><br />\n', 'preg': '',
          'question_order': 1, 'other': 'N', 'modulename': None, 'type': 'D', 'qid': 5801, 'mandatory': 'Y',
          'sid': LIMESURVEY_SURVEY_ID, 'help': '', 'scale_id': 0, 'id': {'qid': 5801, 'language': 'en'},
          'relevance': '1',
          'language': 'en', 'title': 'acquisitiondate', 'gid': 1834},
         {'same_default': 0, 'parent_qid': 0, 'question': 'Responsible Identification number:', 'preg': '',
          'question_order': 0, 'other': 'N', 'modulename': None, 'type': 'N', 'qid': 5800, 'mandatory': 'Y',
          'sid': LIMESURVEY_SURVEY_ID, 'help': '', 'scale_id': 0, 'id': {'qid': 5800, 'language': 'en'},
          'relevance': '1',
          'language': 'en', 'title': 'responsibleid', 'gid': 1834}]
    ]
    mockServer.return_value.get_question_properties.side_effect = 4 * [
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
    ]
    mockServer.return_value.get_language_properties.return_value = {'surveyls_title': 'Test questionnaire'}


def set_mocks4(mockServer):
    mockServer.return_value.get_survey_properties.return_value = {'additional_languages': '', 'language': 'en'}
    mockServer.return_value.get_participant_properties.side_effect = [
        {'token': 'obyBy4HizUhe3j0'},
        {'completed': '2019-06-26'},
        {'completed': '2019-06-26'},
        {'token': 'obyBy4HizUhe3j0'}

    ]
    mockServer.return_value.export_responses.return_value = \
        'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9u' \
        'ZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVj' \
        'b3VudF0iCiIxIiwiMjAxOS0wNi0yNiAxMzozNTo1NyIsIjIiLCJlbiIsIm9ieUJ5NEhpelVoZTNqMCIsIjUzOTc0IiwiMjAxOS0wNi0yNiAx' \
        'MzozNTo1Ny42MDU3MzMiLCIxNzc1MDUiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoK'
    mockServer.return_value.export_responses_by_token.side_effect = [
        'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9u'
        'ZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVj'
        'b3VudF0iCiIxIiwiMjAxOS0wNi0yNiAxMzo1NDo1NyIsIjIiLCJlbiIsImlPYVFLS2VsVmZTcUpROSIsIjUzOTc5IiwiMjAxOS0wNi0yNiAxM'
        'zo1NDo1Ny44NzczOTQiLCIxNzc1MTAiLCJPbMOhIE11bmRvISIsIkhhbGxvIFdlbHQhIiwiIiwiIgoK',
        'IlJlc3BvbnNlIElEIiwiRGF0ZSBzdWJtaXR0ZWQiLCJMYXN0IHBhZ2UiLCJTdGFydCBsYW5ndWFnZSIsIlRva2VuIiwiUmVzcG9uc2libGUg'
        'SWRlLi4gIiwiQWNxdWlzaXRpb24gZGF0ZToiLCJQYXJ0aWNpcGFudCBJZGUuLiAiLCJGaXJzdCBxdWVzdGlvbiIsIlNlY29uZCBxdWVzdGlv'
        'biIsIkhhcyBmaWxldXBsb2FkPyIsImZpbGVjb3VudCAtIEhhcy4uICIKIjEiLCIyMDE5LTA2LTI2IDEzOjU0OjU3IiwiMiIsImVuIiwiaU9h'
        'UUtLZWxWZlNxSlE5IiwiNTM5NzkiLCIyMDE5LTA2LTI2IDEzOjU0OjU3Ljg3NzM5NCIsIjE3NzUxMCIsIk9sw6EgTXVuZG8hIiwiSGFsbG8g'
        'V2VsdCEiLCIiLCIiCgo='
    ]
    mockServer.return_value.list_groups.return_value = [
            {
                'randomization_group': '', 'grelevance': '', 'sid': LIMESURVEY_SURVEY_ID, 'group_order': 2, 'gid': 1841,
                'description': '', 'id': {'gid': 1841, 'language': 'en'}, 'group_name': 'First group', 'language': 'en'
            },
            {
                'randomization_group': '', 'grelevance': '', 'sid': LIMESURVEY_SURVEY_ID, 'group_order': 1, 'gid': 1840,
                'description': '', 'id': {'gid': 1840, 'language': 'en'}, 'group_name': 'Identification',
                'language': 'en'
            },
            {
                'randomization_group': '', 'grelevance': '', 'sid': LIMESURVEY_SURVEY_ID, 'group_order': 1, 'gid': 1840,
                'description': '', 'id': {'gid': 1840, 'language': 'pt-BR'}, 'group_name': 'Identification',
                'language': 'pt-BR'
            },
         ]
    mockServer.return_value.list_questions.side_effect = [
        [{'same_default': 0, 'type': '|', 'other': 'N', 'scale_id': 0, 'mandatory': 'N', 'question_order': 3,
          'modulename': None, 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5823, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1841, 'id': {'qid': 5823, 'language': 'en'}, 'question': 'Has fileupload?', 'relevance': '1',
          'title': 'fileUpload'},
         {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 2,
          'modulename': '', 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5822, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1841, 'id': {'qid': 5822, 'language': 'en'}, 'question': 'Second question', 'relevance': '1',
          'title': 'secondQuestion'},
         {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
          'modulename': '', 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5821, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1841, 'id': {'qid': 5821, 'language': 'en'}, 'question': 'First question', 'relevance': '1',
          'title': 'firstQuestion'}],
        [{'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 3,
          'modulename': None, 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5820, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1840, 'id': {'qid': 5820, 'language': 'en'},
          'question': 'Participant Identification number<b>:</b>', 'relevance': '1', 'title': 'subjectid'},
         {'same_default': 0, 'type': 'D', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
          'modulename': None, 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5819, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1840, 'id': {'qid': 5819, 'language': 'en'},
          'question': 'Acquisition date<strong>:</strong><br />\n', 'relevance': '1', 'title': 'acquisitiondate'},
         {'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 0,
          'modulename': None, 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5818, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1840, 'id': {'qid': 5818, 'language': 'en'}, 'question': 'Responsible Identification number:',
          'relevance': '1', 'title': 'responsibleid'}],
        [{'same_default': 0, 'type': '|', 'other': 'N', 'scale_id': 0, 'mandatory': 'N', 'question_order': 3,
          'modulename': None, 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5823, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1841, 'id': {'qid': 5823, 'language': 'en'}, 'question': 'Has fileupload?', 'relevance': '1',
          'title': 'fileUpload'},
         {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 2,
          'modulename': '', 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5822, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1841, 'id': {'qid': 5822, 'language': 'en'}, 'question': 'Second question', 'relevance': '1',
          'title': 'secondQuestion'},
         {'same_default': 0, 'type': 'T', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
          'modulename': '', 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5821, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1841, 'id': {'qid': 5821, 'language': 'en'}, 'question': 'First question', 'relevance': '1',
          'title': 'firstQuestion'},
         {'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 3,
          'modulename': None, 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5820, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1840, 'id': {'qid': 5820, 'language': 'en'},
          'question': 'Participant Identification number<b>:</b>', 'relevance': '1', 'title': 'subjectid'},
         {'same_default': 0, 'type': 'D', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 1,
          'modulename': None, 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5819, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1840, 'id': {'qid': 5819, 'language': 'en'},
          'question': 'Acquisition date<strong>:</strong><br />\n', 'relevance': '1', 'title': 'acquisitiondate'},
         {'same_default': 0, 'type': 'N', 'other': 'N', 'scale_id': 0, 'mandatory': 'Y', 'question_order': 0,
          'modulename': None, 'sid': LIMESURVEY_SURVEY_ID, 'qid': 5818, 'language': 'en', 'help': '', 'parent_qid': 0,
          'preg': '',
          'gid': 1840, 'id': {'qid': 5818, 'language': 'en'}, 'question': 'Responsible Identification number:',
          'relevance': '1', 'title': 'responsibleid'}]
    ]
    mockServer.return_value.get_question_properties.side_effect = 2 * [
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
    ]
    mockServer.return_value.get_language_properties.return_value = {'surveyls_title': 'Test questionnaire'}


def set_mocks5(mockServer):
    mockServer.return_value.get_survey_properties.return_value = {'language': 'en', 'additional_languages': ''}
    mockServer.return_value.get_participant_properties.side_effect = [{'token': 'ceBAtUYdVXOF3ie'}]
    mockServer.return_value.export_responses.return_value = \
        'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRva2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9u' \
        'ZGF0ZSIsInN1YmplY3RpZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIsImZpbGVVcGxvYWQiLCJmaWxlVXBsb2FkW2ZpbGVj' \
        'b3VudF0iCiIxIiwiMjAxOS0wNi0yNiAxNjozNzoyOSIsIjIiLCJlbiIsIkFhMEdYbG5DYWw2Zmt6ZCIsIjU0MDAwIiwiMjAxOS0wNi0yNiAx' \
        'NjozNzoyOS40OTUyOCIsIjE3NzUzNCIsIk9sw6EgTXVuZG8hIiwiSGFsbG8gV2VsdCEiLCIiLCIiCgo='
    mockServer.return_value.list_groups.return_value = [
        {'grelevance': '', 'id': {'gid': 1855, 'language': 'en'}, 'language': 'en', 'randomization_group': '',
         'gid': 1855, 'group_order': 2, 'group_name': 'First group', 'description': '', 'sid': LIMESURVEY_SURVEY_ID},
        {'grelevance': '', 'id': {'gid': 1854, 'language': 'en'}, 'language': 'en', 'randomization_group': '',
         'gid': 1854, 'group_order': 1, 'group_name': 'Identification', 'description': '',
         'sid': LIMESURVEY_SURVEY_ID},
        {'grelevance': '', 'id': {'gid': 1854, 'language': 'pt-BR'}, 'language': 'pt-BR',
         'randomization_group': '', 'gid': 1854, 'group_order': 1, 'group_name': 'Identification',
         'description': '', 'sid': LIMESURVEY_SURVEY_ID},
    ]
    mockServer.return_value.list_questions.side_effect = [
        [{'id': {'qid': 5865, 'language': 'en'}, 'language': 'en', 'title': 'fileUpload', 'help': '', 'preg': '',
          'type': '|', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
          'question': 'Has fileupload?', 'scale_id': 0, 'gid': 1855, 'qid': 5865, 'mandatory': 'N',
          'question_order': 3, 'sid': LIMESURVEY_SURVEY_ID},
         {'id': {'qid': 5864, 'language': 'en'}, 'language': 'en', 'title': 'secondQuestion', 'help': '',
          'preg': '', 'type': 'T', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': '',
          'parent_qid': 0, 'question': 'Second question', 'scale_id': 0, 'gid': 1855, 'qid': 5864, 'mandatory': 'Y',
          'question_order': 2, 'sid': LIMESURVEY_SURVEY_ID},
         {'id': {'qid': 5863, 'language': 'en'}, 'language': 'en', 'title': 'firstQuestion', 'help': '', 'preg': '',
          'type': 'T', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': '', 'parent_qid': 0,
          'question': 'First question', 'scale_id': 0, 'gid': 1855, 'qid': 5863, 'mandatory': 'Y',
          'question_order': 1, 'sid': LIMESURVEY_SURVEY_ID}],
        [{'id': {'qid': 5862, 'language': 'en'}, 'language': 'en', 'title': 'subjectid', 'help': '', 'preg': '',
          'type': 'N', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
          'question': 'Participant Identification number<b>:</b>', 'scale_id': 0, 'gid': 1854, 'qid': 5862,
          'mandatory': 'Y', 'question_order': 3, 'sid': LIMESURVEY_SURVEY_ID},
         {'id': {'qid': 5861, 'language': 'en'}, 'language': 'en', 'title': 'acquisitiondate', 'help': '',
          'preg': '', 'type': 'D', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None,
          'parent_qid': 0, 'question': 'Acquisition date<strong>:</strong><br />\n', 'scale_id': 0, 'gid': 1854,
          'qid': 5861, 'mandatory': 'Y', 'question_order': 1, 'sid': LIMESURVEY_SURVEY_ID},
         {'id': {'qid': 5860, 'language': 'en'}, 'language': 'en', 'title': 'responsibleid', 'help': '', 'preg': '',
          'type': 'N', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
          'question': 'Responsible Identification number:', 'scale_id': 0, 'gid': 1854, 'qid': 5860,
          'mandatory': 'Y', 'question_order': 0, 'sid': LIMESURVEY_SURVEY_ID}],
        [{'id': {'qid': 5865, 'language': 'en'}, 'language': 'en', 'title': 'fileUpload', 'help': '', 'preg': '',
          'type': '|', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
          'question': 'Has fileupload?', 'scale_id': 0, 'gid': 1855, 'qid': 5865, 'mandatory': 'N',
          'question_order': 3, 'sid': LIMESURVEY_SURVEY_ID},
         {'id': {'qid': 5864, 'language': 'en'}, 'language': 'en', 'title': 'secondQuestion', 'help': '',
          'preg': '', 'type': 'T', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': '',
          'parent_qid': 0, 'question': 'Second question', 'scale_id': 0, 'gid': 1855, 'qid': 5864, 'mandatory': 'Y',
          'question_order': 2, 'sid': LIMESURVEY_SURVEY_ID},
         {'id': {'qid': 5863, 'language': 'en'}, 'language': 'en', 'title': 'firstQuestion', 'help': '', 'preg': '',
          'type': 'T', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': '', 'parent_qid': 0,
          'question': 'First question', 'scale_id': 0, 'gid': 1855, 'qid': 5863, 'mandatory': 'Y',
          'question_order': 1, 'sid': LIMESURVEY_SURVEY_ID},
         {'id': {'qid': 5862, 'language': 'en'}, 'language': 'en', 'title': 'subjectid', 'help': '', 'preg': '',
          'type': 'N', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
          'question': 'Participant Identification number<b>:</b>', 'scale_id': 0, 'gid': 1854, 'qid': 5862,
          'mandatory': 'Y', 'question_order': 3, 'sid': LIMESURVEY_SURVEY_ID},
         {'id': {'qid': 5861, 'language': 'en'}, 'language': 'en', 'title': 'acquisitiondate', 'help': '',
          'preg': '', 'type': 'D', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None,
          'parent_qid': 0, 'question': 'Acquisition date<strong>:</strong><br />\n', 'scale_id': 0, 'gid': 1854,
          'qid': 5861, 'mandatory': 'Y', 'question_order': 1, 'sid': LIMESURVEY_SURVEY_ID},
         {'id': {'qid': 5860, 'language': 'en'}, 'language': 'en', 'title': 'responsibleid', 'help': '', 'preg': '',
          'type': 'N', 'same_default': 0, 'relevance': '1', 'other': 'N', 'modulename': None, 'parent_qid': 0,
          'question': 'Responsible Identification number:', 'scale_id': 0, 'gid': 1854, 'qid': 5860,
          'mandatory': 'Y', 'question_order': 0, 'sid': LIMESURVEY_SURVEY_ID}]
    ]
    mockServer.return_value.get_question_properties.side_effect = 2 * [
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
