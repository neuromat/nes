# coding=utf-8
# from django.shortcuts import render

import re
import csv
import datetime

from StringIO import StringIO
from operator import itemgetter

from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from models import Survey
from forms import SurveyForm

from patient.models import Patient, QuestionnaireResponse as PatientQuestionnaireResponse

from experiment.models import Questionnaire

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

    questionnaires_list = sorted(questionnaires_list, key=itemgetter('title'))

    data = {'questionnaires_list': questionnaires_list}
    return render(request, template_name, data)


@login_required
@permission_required('survey.add_survey')
def survey_create(request, template_name="survey/survey_register.html"):
    survey_form = SurveyForm(request.POST or None, initial={'title': 'title'})

    surveys = Questionnaires()
    questionnaires_list = surveys.find_all_active_questionnaires()
    surveys.release_session_key()

    # removing surveys already registered
    used_surveys = Survey.objects.all()
    for used_survey in used_surveys:
        for questionnaire in questionnaires_list:
            if used_survey.lime_survey_id == questionnaire['sid']:
                questionnaires_list.remove(questionnaire)
                break

    if request.method == "POST":
        if request.POST['action'] == "save":
            if survey_form.is_valid():

                survey_added = survey_form.save(commit=False)

                survey, created = Survey.objects.get_or_create(
                    lime_survey_id=request.POST['questionnaire_selected'],
                    is_initial_evaluation=survey_added.is_initial_evaluation)

                if created:
                    messages.success(request, 'Questionário criado com sucesso.')
                    redirect_url = reverse("survey_list")
                    return HttpResponseRedirect(redirect_url)

    context = {
        "survey_form": survey_form,
        "creating": True,
        "editing": True,
        "questionnaires_list": questionnaires_list}

    return render(request, template_name, context)


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

    # list of patients
    patients_questionnaire_data_dictionary = {}

    responses = PatientQuestionnaireResponse.objects.all().filter(survey=survey).order_by('patient__id')

    for response in responses:

        if response.patient.id not in patients_questionnaire_data_dictionary:
            patients_questionnaire_data_dictionary[response.patient.id] = \
                {
                    'patient_name': response.patient.name,
                    'questionnaire_responses': []
                }

        response_result = surveys.get_participant_properties(
            response.survey.lime_survey_id, response.token_id, "completed")

        patients_questionnaire_data_dictionary[response.patient.id]['questionnaire_responses'].append(
            {
                'questionnaire_response':
                response,

                'completed':
                None if response_result is None else response_result != "N" and response_result != ""
            }
        )

    patients = Patient.objects.all().filter(removed=False)

    for patient in patients:
        if patient.id not in patients_questionnaire_data_dictionary:
            patients_questionnaire_data_dictionary[patient.id] = \
                {
                    'patient_name': patient.name,
                    'questionnaire_responses': []
                }

    patients_questionnaire_data_list = []

    # adjusting and sorting
    for key, dictionary in patients_questionnaire_data_dictionary.items():
        dictionary['patient_id'] = key
        patients_questionnaire_data_list.append(dictionary)

    patients_questionnaire_data_list = \
        sorted(patients_questionnaire_data_list, key=itemgetter('patient_name'), reverse=False)

    # TODO: list of experiments that use this survey
    questionnaires = Questionnaire.objects.filter(survey=survey).distinct('experiment')

    # TODO: control functionalities of remove, back, bread crumb etc.

    surveys.release_session_key()

    context = {
        "survey": survey,
        "survey_form": survey_form,
        "survey_title": survey_title,
        "limesurvey_available": limesurvey_available,
        "patients_questionnaire_data_list": patients_questionnaire_data_list,
        "questionnaires": questionnaires
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
