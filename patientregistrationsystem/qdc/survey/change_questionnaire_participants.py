#!/usr/bin/python3

import getopt
import os
import sys

import django
from experiment.models import Questionnaire
from experiment.models import QuestionnaireResponse as EQuestionnaireResponse
from patient.models import QuestionnaireResponse as PQuestionnaireResponse
from survey.abc_search_engine import Questionnaires

sys.path.append("/home/caco/Workspace/nes-system/nes/patientregistrationsystem/qdc")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "qdc.settings")
django.setup()


def parse_options(argv):
    questionnaire_id = ""
    new_limesurvey_id = ""
    try:
        opts, args = getopt.getopt(argv, "hq:l:", ["questionnaire=", "new_limesurvey="])
    except getopt.GetoptError:
        print(
            "change_questionnaire_participants.py -q <questionnaire_id> -l "
            "<new_limesurvey_id>"
        )
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(
                "change_questionnaire_participants.py -q <questionnaire_id> "
                "-l <new_limesurvey_id>"
            )
            sys.exit(1)
        elif opt in ("-q", "--questionnaire"):
            questionnaire_id = arg
        elif opt in ("-l", "--new_limesurvey"):
            new_limesurvey_id = arg

    if questionnaire_id == "" or new_limesurvey_id == "":
        print(
            "change_questionnaire_participants.py -q <questionnaire_id> -l "
            "<new_limesurvey_id>"
        )
        sys.exit(2)

    return [questionnaire_id, new_limesurvey_id]


def update_questionnaire_response(old_tokens, new_tokens, q_response):
    old_token = next(item for item in old_tokens if item["tid"] == q_response.token_id)
    new_token = next(item for item in new_tokens if item["token"] == old_token["token"])
    q_response.token_id = new_token["tid"]
    q_response.save()
    return q_response


def main(argv):
    # TODO: test for new_limesurvey_id existence
    questionnaire_id, new_limesurvey_id = parse_options(argv)
    questionnaire = Questionnaire.objects.get(id=questionnaire_id)
    survey = questionnaire.survey
    old_limesurvey_id = survey.lime_survey_id
    survey.lime_survey_id = new_limesurvey_id
    # TODO:
    # if old_limesurvey_id == new_limesurvey_id do nothing, exit with message
    survey.save()

    limesurvey_surveys = Questionnaires()
    print("Getting old tokens ...")
    old_tokens = limesurvey_surveys.find_tokens_by_questionnaire(old_limesurvey_id)
    print("Getting new tokens ...")
    new_tokens = limesurvey_surveys.find_tokens_by_questionnaire(survey.lime_survey_id)

    print("Updating experiment questionnaire responses ...")
    for q_experiment_response in EQuestionnaireResponse.objects.filter(
        data_configuration_tree__component_configuration__component=questionnaire.id
    ):
        update_questionnaire_response(old_tokens, new_tokens, q_experiment_response)

    print("Updating patients questionnaire responses ...")
    for q_patient_response in PQuestionnaireResponse.objects.filter(survey=survey):
        update_questionnaire_response(old_tokens, new_tokens, q_patient_response)


if __name__ == "__main__":
    main(sys.argv[1:])
