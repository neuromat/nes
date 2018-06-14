#!/usr/bin/python3

import getopt
import sys
import os
import django
import json

sys.path.append(
    '/home/caco/Workspace/nes-system/nes/patientregistrationsystem/qdc'
)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qdc.settings')
django.setup()

from survey.abc_search_engine import Questionnaires
from experiment.models import Questionnaire, QuestionnaireResponse


def parse_options(argv):
    questionnaire_id = ''
    new_limesurvey_id = ''
    try:
        opts, args = getopt.getopt(
            argv, 'hq:l:', ['questionnaire=', 'new_limesurvey=']
        )
    except getopt.GetoptError:
        print(
            'change_questionnaire_participants.py -q <questionnaire_id> -l '
            '<new_limesurvey_id>'
        )
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(
                'change_questionnaire_participants.py -q <questionnaire_id> '
                '-l <new_limesurvey_id>'

            )
            sys.exit(1)
        elif opt in ('-q', '--questionnaire'):
            questionnaire_id = arg
        elif opt in ('-l', '--new_limesurvey'):
            new_limesurvey_id = arg

    if questionnaire_id == '' or new_limesurvey_id == '':
        print(
            'change_questionnaire_participants.py -q <questionnaire_id> -l '
            '<new_limesurvey_id>'
        )
        sys.exit(2)

    return [questionnaire_id, new_limesurvey_id]


def main(argv):
    # TODO: test for new_limesurvey_id existence
    questionnaire_id, new_limesurvey_id = parse_options(argv)
    questionnaire = Questionnaire.objects.get(id=questionnaire_id)
    survey = questionnaire.survey
    old_limesurvey_id = survey.lime_survey_id
    survey.lime_survey_id = new_limesurvey_id
    survey.save()

    limesurvey_surveys = Questionnaires()
    old_tokens = \
        limesurvey_surveys.find_tokens_by_questionnaire(old_limesurvey_id)
    print('Getting old tokens ...')
    new_tokens = \
        limesurvey_surveys.find_tokens_by_questionnaire(survey.lime_survey_id)
    print('Getting new tokens ...')

    for q_response in QuestionnaireResponse.objects.filter(
            data_configuration_tree__component_configuration__component
            =questionnaire.id
    ):
        old_token = next(
            item for item in old_tokens if item["tid"] == q_response.token_id
        )
        new_token = next(
            item for item in new_tokens if item['token'] == old_token['token']
        )
        q_response.token_id = new_token['tid']
        q_response.save()


if __name__ == "__main__":
    main(sys.argv[1:])
