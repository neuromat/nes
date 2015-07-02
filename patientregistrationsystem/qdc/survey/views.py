# coding=utf-8
# from django.shortcuts import render

import re
import csv
import datetime

from StringIO import StringIO
from operator import itemgetter

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required

from models import Survey
from forms import SurveyForm

from patient.models import Patient, QuestionnaireResponse as PatientQuestionnaireResponse

from experiment.models import ComponentConfiguration, QuestionnaireResponse, Questionnaire

from experiment.abc_search_engine import Questionnaires


@login_required
@permission_required('auth.view_survey')
def survey_list(request, template_name='survey/survey_list.html'):

    surveys = Questionnaires()

    questionnaires_list = []

    for survey in Survey.objects.all():
        questionnaires_list.append(
            {
                'id': survey.id,
                'lime_survey_id': survey.lime_survey_id,
                'title': surveys.get_survey_title(survey.lime_survey_id),
                'is_initial_evaluation': survey.is_initial_evaluation
            }
        )

    surveys.release_session_key()

    questionnaires_list = sorted(questionnaires_list, key=itemgetter('title'), reverse=False)

    data = {'questionnaires_list': questionnaires_list}
    return render(request, template_name, data)


@login_required
@permission_required('survey.view_survey')
def survey_view(request, survey_id, template_name="survey/survey_register.html"):
    survey = get_object_or_404(Survey, pk=survey_id)

    surveys = Questionnaires()
    limesurvey_available = check_limesurvey_access(request, surveys)
    survey_title = surveys.get_survey_title(survey.lime_survey_id)

    survey_form = SurveyForm(request.POST or None, instance=survey,
                             initial={'title': str(survey.lime_survey_id) + ' - ' + survey_title})

    for field in survey_form.fields:
        survey_form.fields[field].widget.attrs['disabled'] = True

    # if request.method == "POST":
    #     if request.POST['action'] == "remove":
    #         try:
    #             for keyword in research_project.keywords.all():
    #                 manage_keywords(keyword, ResearchProject.objects.exclude(id=research_project.id))
    #
    #             research_project.delete()
    #             return redirect('research_project_list')
    #         except ProtectedError:
    #             messages.error(request, "Erro ao tentar excluir o estudo.")

    # Create a list of patients by looking to the answers of this questionnaire. We do this way instead of looking for
    # patients and then looking for answers of each patient to reduce the number of access to the data base.
    # We use a dictionary because it is useful for filtering out duplicate patients from the list.
    patients_questionnaire_data_dictionary = {}

    for response in PatientQuestionnaireResponse.objects.filter(survey=survey):
        if response.patient.id not in patients_questionnaire_data_dictionary:
            patients_questionnaire_data_dictionary[response.patient.id] = {
                'patient_name': response.patient.name,
                'questionnaire_responses': []
            }

        response_result = surveys.get_participant_properties(response.survey.lime_survey_id,
                                                             response.token_id,
                                                             "completed")

        patients_questionnaire_data_dictionary[response.patient.id]['questionnaire_responses'].append({
            'questionnaire_response': response,
            'completed': None if response_result is None else response_result != "N" and response_result != ""
        })

    # Add to the dictionary patients that have not answered any questionnaire yet.
    if survey.is_initial_evaluation:
        patients = Patient.objects.filter(removed=False)

        for patient in patients:
            if patient.id not in patients_questionnaire_data_dictionary:
                patients_questionnaire_data_dictionary[patient.id] = {
                    'patient_name': patient.name,
                    'questionnaire_responses': []
                }

    # Transform the dictionary into a list, so that we can sort it by patient name.
    patients_questionnaire_data_list = []

    for key, dictionary in patients_questionnaire_data_dictionary.items():
        dictionary['patient_id'] = key
        patients_questionnaire_data_list.append(dictionary)

    patients_questionnaire_data_list = sorted(patients_questionnaire_data_list, key=itemgetter('patient_name'))

    # Create a list of questionnaires used in experiments by looking at questionnaires responses. We use a
    # dictionary because it is useful for filtering out duplicate component configurations from the list.
    experiments_questionnaire_data_dictionary = {}

    for qr in QuestionnaireResponse.objects.all():
        q = Questionnaire.objects.get(id=qr.component_configuration.component_id)

        if q.survey == survey:
            use = qr.component_configuration
            group = qr.subject_of_group.group

            if use.id not in experiments_questionnaire_data_dictionary:
                experiments_questionnaire_data_dictionary[use.id] = {
                    'experiment_title': group.experiment.title,
                    'group_title': group.title,
                    'component_identification': use.component.identification,
                    'parent_identification': use.parent.identification,
                    'use_name': use.name,
                    'patients': {}
                }

            patient = qr.subject_of_group.subject.patient

            if patient.id not in experiments_questionnaire_data_dictionary[use.id]['patients']:
                experiments_questionnaire_data_dictionary[use.id]['patients'][patient.id] = {
                    'patient_name': qr.subject_of_group.subject.patient.name,
                    'questionnaire_responses': []
                }

            response_result = surveys.get_participant_properties(q.survey.lime_survey_id,
                                                                 response.token_id,
                                                                 "completed")

            experiments_questionnaire_data_dictionary[use.id]['patients'][patient.id]['questionnaire_responses'].append({
                'questionnaire_response': response,
                'completed': None if response_result is None else response_result != "N" and response_result != ""
            })

    surveys.release_session_key()

    # Add questionnaires from the experiments that are not yet in this list.
    for use in ComponentConfiguration.objects.all():
        if use.component.component_type == 'questionnaire':
            q = Questionnaire.objects.get(id=use.component_id)

            if q.survey == survey:
                if use.id not in experiments_questionnaire_data_dictionary:
                    experiments_questionnaire_data_dictionary[use.id] = {
                        'experiment_title': '',# TODO group.experiment.title,
                        'group_title': '',# TODO group.title,
                        'component_identification': use.component.identification,
                        'parent_identification': use.parent.identification,
                        'use_name': use.name,
                        'patients': {}
                }

    # TODO Sort by experiment title, group title, step identification, and name of the use of step

    # TODO: control functionalities of remove, back, bread crumb etc.

    context = {
        "limesurvey_available": limesurvey_available,
        "patients_questionnaire_data_list": patients_questionnaire_data_list,
        "experiments_questionnaire_data_dictionary": experiments_questionnaire_data_dictionary,
        "survey": survey,
        "survey_form": survey_form,
        "survey_title": survey_title,
    }

    return render(request, template_name, context)


def get_questionnaire_responses(language_code, lime_survey_id, token_id):

    questionnaire_responses = []
    surveys = Questionnaires()
    token = surveys.get_participant_properties(lime_survey_id, token_id, "token")
    question_properties = []
    groups = surveys.list_groups(lime_survey_id)

    survey_title = surveys.get_survey_title(lime_survey_id)

    if not isinstance(groups, dict):

        # defining language to be showed
        languages = surveys.get_survey_languages(lime_survey_id)
        language = languages['language']
        if language_code in languages['additional_languages'].split(' '):
            language = language_code

        for group in groups:
            if 'id' in group and group['id']['language'] == language:

                question_list = surveys.list_questions(lime_survey_id, group['id'])
                question_list = sorted(question_list)

                for question in question_list:

                    properties = surveys.get_question_properties(question, group['id']['language'])

                    # cleaning the question field
                    properties['question'] = re.sub('{.*?}', '', re.sub('<.*?>', '', properties['question']))
                    properties['question'] = properties['question'].replace('&nbsp;', '').strip()

                    is_purely_formula = (properties['type'] == '*') and (properties['question'] == '')

                    if not is_purely_formula and properties['question'] != '':

                        if isinstance(properties['subquestions'], dict):
                            question_properties.append({
                                'question': properties['question'],
                                'question_id': properties['title'],
                                'answer_options': 'super_question',
                                'type': properties['type'],
                                'attributes_lang': properties['attributes_lang'],
                                'hidden': 'hidden' in properties['attributes'] and
                                          properties['attributes']['hidden'] == '1'
                            })
                            for key, value in sorted(properties['subquestions'].iteritems()):
                                question_properties.append({
                                    'question': value['question'],
                                    'question_id': properties['title'] + '[' + value['title'] + ']',
                                    'answer_options': properties['answeroptions'],
                                    'type': properties['type'],
                                    'attributes_lang': properties['attributes_lang'],
                                    'hidden': 'hidden' in properties['attributes'] and
                                              properties['attributes']['hidden'] == '1'
                                })
                        else:
                            question_properties.append({
                                'question': properties['question'],
                                'question_id': properties['title'],
                                'answer_options': properties['answeroptions'],
                                'type': properties['type'],
                                'attributes_lang': properties['attributes_lang'],
                                'hidden': 'hidden' in properties['attributes'] and
                                          properties['attributes']['hidden'] == '1'
                            })

        # Reading from Limesurvey and...
        responses_string = surveys.get_responses_by_token(lime_survey_id, token, language)

        # ... transforming to a list:
        # response_list[0] has the questions
        #   response_list[1] has the answers
        reader = csv.reader(StringIO(responses_string), delimiter=',')
        responses_list = []
        for row in reader:
            responses_list.append(row)

        for question in question_properties:

            if not question['hidden']:

                if isinstance(question['answer_options'], basestring) and \
                        question['answer_options'] == "super_question":

                    if question['question'] != '':
                        questionnaire_responses.append({
                            'question': question['question'],
                            'answer': '',
                            'type': question['type']
                        })
                else:

                    answer = ''

                    if question['type'] == '1':

                        answer_list = []

                        if question['question_id'] + "[1]" in responses_list[0]:
                            index = responses_list[0].index(question['question_id'] + "[1]")
                            answer_options = question['answer_options']
                            answer = question['attributes_lang']['dualscale_headerA'] + ": "
                            if responses_list[1][index] in answer_options:
                                answer_option = answer_options[responses_list[1][index]]
                                answer += answer_option['answer']
                            else:
                                answer += 'Sem resposta'

                        answer_list.append(answer)

                        if question['question_id'] + "[2]" in responses_list[0]:
                            index = responses_list[0].index(question['question_id'] + "[2]")
                            answer_options = question['answer_options']
                            answer = question['attributes_lang']['dualscale_headerB'] + ": "
                            if responses_list[1][index] in answer_options:
                                answer_option = answer_options[responses_list[1][index]]
                                answer += answer_option['answer']
                            else:
                                answer += 'Sem resposta'

                        answer_list.append(answer)

                        questionnaire_responses.append({
                            'question': question['question'],
                            'answer': answer_list,
                            'type': question['type']
                        })
                    else:

                        if question['question_id'] in responses_list[0]:

                            index = responses_list[0].index(question['question_id'])

                            answer_options = question['answer_options']

                            if isinstance(answer_options, dict):

                                if responses_list[1][index] in answer_options:
                                    answer_option = answer_options[responses_list[1][index]]
                                    answer = answer_option['answer']
                                else:
                                    answer = 'Sem resposta'
                            else:
                                if question['type'] == 'D':
                                    if responses_list[1][index]:
                                        answer = datetime.datetime.strptime(responses_list[1][index],
                                                                            '%Y-%m-%d %H:%M:%S')
                                    else:
                                        answer = ''
                                else:
                                    answer = responses_list[1][index]

                        questionnaire_responses.append({
                            'question': question['question'],
                            'answer': answer,
                            'type': question['type']
                        })

    surveys.release_session_key()

    return survey_title, questionnaire_responses


def check_limesurvey_access(request, surveys):
    limesurvey_available = True
    if not surveys.session_key:
        limesurvey_available = False
        messages.warning(request, "LimeSurvey indisponível. Sistema funcionando parcialmente.")

    return limesurvey_available
