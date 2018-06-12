#!/usr/bin/python3

import getopt
import sys
import os
import django
sys.path.append(
    '/home/caco/Workspace/nes-system/nes/patientregistrationsystem/qdc'
)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qdc.settings')
django.setup()

from experiment.models import Questionnaire


def parse_options(argv):
    questionnaire_id = ''
    try:
        opts, args = getopt.getopt(
            argv, 'hq:', ['questionnaire=']
        )
    except getopt.GetoptError:
        print('change_questionnaire_participants.py -q <questionnaire_id>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('change_questionnaire_participants.py -q <questionnaire_id>')
            sys.exit(1)
        elif opt in ('-q', '--questionnaire'):
            questionnaire_id = arg

    if questionnaire_id == '':
        print('change_questionnaire_participants.py -q <questionnaire_id>')
        sys.exit(2)

    return questionnaire_id


def main(argv):
    questionnaire_id = parse_options(argv)
    questionnaire = Questionnaire.objects.get(id=questionnaire_id)
    print(questionnaire)  # DEBUG


if __name__ == "__main__":
    main(sys.argv[1:])
