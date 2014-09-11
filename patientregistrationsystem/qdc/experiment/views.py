# coding=utf-8
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.db.models.deletion import ProtectedError

from experiment.models import Experiment, QuestionnaireConfiguration, Subject, TimeUnit, \
    QuestionnaireResponse, SubjectOfExperiment
from experiment.forms import ExperimentForm, QuestionnaireConfigurationForm, QuestionnaireResponseForm, FileForm

from quiz.models import Patient
from quiz.abc_search_engine import Questionnaires

from django.conf import settings

from functools import partial

import re

import datetime

permission_required = partial(permission_required, raise_exception=True)

@login_required
@permission_required('experiment.view_experiment')
def experiment_list(request, template_name="experiment/experiment_list.html"):
    experiments = Experiment.objects.order_by('title')

    context = {"experiments": experiments}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_experiment')
def experiment_create(request, template_name="experiment/experiment_register.html"):
    experiment_form = ExperimentForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if experiment_form.is_valid():
                experiment_added = experiment_form.save()

                messages.success(request, 'Experimento criado com sucesso.')

                redirect_url = reverse("experiment_edit", args=(experiment_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "experiment_form": experiment_form,
        "creating": True}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_experiment')
def experiment_update(request, experiment_id, template_name="experiment/experiment_register.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    if experiment:
        questionnaires_configuration_list = QuestionnaireConfiguration.objects.filter(experiment=experiment)
        surveys = Questionnaires()
        questionnaires_configuration_list = [
            {"survey_title": surveys.get_survey_title(questionnaire_configuration.lime_survey_id),
             "number_of_fills": questionnaire_configuration.number_of_fills,
             "interval_between_fills_value": questionnaire_configuration.interval_between_fills_value,
             "interval_between_fills_unit": questionnaire_configuration.interval_between_fills_unit,
             "id": questionnaire_configuration.id}
            for questionnaire_configuration in questionnaires_configuration_list]
        surveys.release_session_key()

        experiment_form = ExperimentForm(request.POST or None, instance=experiment)

        if request.method == "POST":

            if request.POST['action'] == "save":

                if experiment_form.is_valid():
                    if experiment_form.has_changed():
                        experiment_form.save()

                    redirect_url = reverse("experiment_edit", args=(experiment_id,))
                    return HttpResponseRedirect(redirect_url)

            else:
                if request.POST['action'] == "remove":
                    try:
                        experiment.delete()
                    except ProtectedError:
                        messages.error(request, "Não foi possível excluir o experimento, pois há questões associadas")
                        redirect_url = reverse("experiment_edit", args=(experiment.id,))
                        return HttpResponseRedirect(redirect_url)
                    return redirect('experiment_list')

    context = {
        "experiment_form": experiment_form,
        "creating": False,
        "questionnaires_configuration_list": questionnaires_configuration_list,
        "experiment": experiment}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_questionnaireconfiguration')
def questionnaire_create(request, experiment_id, template_name="experiment/questionnaire_register.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    questionnaire_form = QuestionnaireConfigurationForm(
        request.POST or None,
        initial={'number_of_fills': 1, 'interval_between_fills_value': None})

    questionnaires_of_experiment = QuestionnaireConfiguration.objects.filter(experiment=experiment)
    if not questionnaires_of_experiment:
        questionnaires_list = Questionnaires().find_all_active_questionnaires()
    else:
        active_questionnaires_list = Questionnaires().find_all_active_questionnaires()
        for active_questionnaire in active_questionnaires_list:
            for questionnaire in questionnaires_of_experiment:
                if active_questionnaire['sid'] == questionnaire.lime_survey_id:
                    active_questionnaires_list.remove(active_questionnaire)
                    break
        questionnaires_list = active_questionnaires_list

    if request.method == "POST":

        if request.POST['action'] == "save":

            if questionnaire_form.is_valid():

                lime_survey_id = request.POST['questionnaire_selected']

                questionnaire = QuestionnaireConfiguration()
                questionnaire.lime_survey_id = lime_survey_id
                questionnaire.experiment = experiment

                if "number_of_fills" in request.POST:
                    questionnaire.number_of_fills = request.POST['number_of_fills']

                if "interval_between_fills_value" in request.POST:
                    questionnaire.interval_between_fills_value = request.POST['interval_between_fills_value']

                if "interval_between_fills_unit" in request.POST:
                    questionnaire.interval_between_fills_unit = \
                        get_object_or_404(TimeUnit, pk=request.POST['interval_between_fills_unit'])

                questionnaire.save()

                messages.success(request, 'Questionário incluído com sucesso.')

                redirect_url = reverse("experiment_edit", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "questionnaire_form": questionnaire_form,
        "creating": True,
        "updating": False,
        "experiment": experiment,
        "questionnaires_list": questionnaires_list}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_questionnaireconfiguration')
def questionnaire_update(request, questionnaire_configuration_id,
                         template_name="experiment/questionnaire_register.html"):
    questionnaire_configuration = get_object_or_404(QuestionnaireConfiguration, pk=questionnaire_configuration_id)
    experiment = get_object_or_404(Experiment, pk=questionnaire_configuration.experiment.id)
    questionnaire_form = QuestionnaireConfigurationForm(request.POST or None, instance=questionnaire_configuration)

    surveys = Questionnaires()
    questionnaire_title = surveys.get_survey_title(questionnaire_configuration.lime_survey_id)
    surveys.release_session_key()

    if request.method == "POST":

        if request.POST['action'] == "save":
            if questionnaire_form.is_valid():

                if "number_of_fills" in request.POST:
                    questionnaire_configuration.number_of_fills = request.POST['number_of_fills']

                if "interval_between_fills_value" in request.POST:
                    questionnaire_configuration.interval_between_fills_value = \
                        request.POST['interval_between_fills_value']

                if "interval_between_fills_unit" in request.POST:
                    questionnaire_configuration.interval_between_fills_unit = \
                        get_object_or_404(TimeUnit, pk=request.POST['interval_between_fills_unit'])

                questionnaire_configuration.save()

                messages.success(request, 'Questionário atualizado com sucesso.')

                redirect_url = reverse("experiment_edit", args=(experiment.id,))
                return HttpResponseRedirect(redirect_url)
        else:
            if request.POST['action'] == "remove":
                try:
                    questionnaire_configuration.delete()
                except ProtectedError:
                    messages.error(request, "Não foi possível excluir o questionário, pois há respostas associadas")
                    redirect_url = reverse("questionnaire_edit", args=(questionnaire_configuration_id,))
                    return HttpResponseRedirect(redirect_url)

                redirect_url = reverse("experiment_edit", args=(experiment.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "questionnaire_form": questionnaire_form,
        "creating": False,
        "updating": True,
        "experiment": experiment,
        "questionnaire_title": questionnaire_title,
        "questionnaire_id": questionnaire_configuration.lime_survey_id}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_subject')
def subjects(request, experiment_id, template_name="experiment/subjects.html"):
    experiment = get_object_or_404(Experiment, id=experiment_id)

    subject_of_experiment_list = SubjectOfExperiment.objects.all().filter(experiment=experiment)

    subject_list_with_status = []

    questionnaires_configuration_list = QuestionnaireConfiguration.objects.filter(experiment=experiment)

    surveys = Questionnaires()

    for subject_of_experiment in subject_of_experiment_list:

        number_of_questionnaires_filled = 0

        for questionnaire_configuration in questionnaires_configuration_list:

            subject_responses = QuestionnaireResponse.objects. \
                filter(subject_of_experiment=subject_of_experiment). \
                filter(questionnaire_configuration=questionnaire_configuration)

            if subject_responses:
                if (questionnaire_configuration.number_of_fills is None and subject_responses.count() > 0) or \
                        (questionnaire_configuration.number_of_fills is not None and
                                 questionnaire_configuration.number_of_fills == subject_responses.count()):

                    number_of_questionnaires_completed = 0

                    for subject_response in subject_responses:

                        response_result = surveys.get_participant_properties(questionnaire_configuration.lime_survey_id,
                                                                             subject_response.token_id, "completed")

                        if response_result == "N":
                            break
                        else:
                            number_of_questionnaires_completed += 1

                    if (questionnaire_configuration.number_of_fills is None and
                                number_of_questionnaires_completed > 0) or \
                            (questionnaire_configuration.number_of_fills is not None and
                                     number_of_questionnaires_completed >= questionnaire_configuration.number_of_fills):
                        number_of_questionnaires_filled += 1

        subject_list_with_status.append(
            {'subject': subject_of_experiment.subject,
             'number_of_questionnaires_filled': number_of_questionnaires_filled,
             'total_of_questionnaires': questionnaires_configuration_list.count(),
             'percentage': 100 * number_of_questionnaires_filled / questionnaires_configuration_list.count(),
             'consent': subject_of_experiment.consent_form})

    context = {
        'experiment_id': experiment_id,
        'subject_list': subject_list_with_status,
        'experiment_title': experiment.title
    }

    surveys.release_session_key()

    return render(request, template_name, context)


def subject_questionnaire_response_start_fill_questionnaire(request, subject_id, questionnaire_id):
    questionnaire_response_form = QuestionnaireResponseForm(request.POST)

    if questionnaire_response_form.is_valid():

        questionnaire_response = questionnaire_response_form.save(commit=False)

        questionnaire_config = get_object_or_404(QuestionnaireConfiguration, id=questionnaire_id)

        questionnaire_lime_survey = Questionnaires()

        subject = get_object_or_404(Subject, pk=subject_id)
        patient = subject.patient

        subject_of_experiment = get_object_or_404(SubjectOfExperiment, subject=subject,
                                                  experiment=questionnaire_config.experiment)

        if not questionnaire_lime_survey.survey_has_token_table(questionnaire_config.lime_survey_id):
            messages.warning(request,
                             'Preenchimento não disponível - Tabela de tokens não iniciada')
            return None

        if questionnaire_lime_survey.get_survey_properties(questionnaire_config.lime_survey_id, 'active') == 'N':
            messages.warning(request,
                             'Preenchimento não disponível - Questionário não está ativo')
            return None

        result = questionnaire_lime_survey.add_participant(questionnaire_config.lime_survey_id, patient.name_txt, '',
                                                           patient.email_txt)

        questionnaire_lime_survey.release_session_key()

        if not result:
            messages.warning(request,
                             'Falha ao gerar token para responder questionário. Verifique se o questionário está ativo')
            return None

        questionnaire_response.subject_of_experiment = subject_of_experiment
        questionnaire_response.questionnaire_configuration = questionnaire_config
        questionnaire_response.token_id = result['token_id']
        questionnaire_response.date = datetime.datetime.strptime(request.POST['date'], '%d/%m/%Y')
        questionnaire_response.questionnaire_responsible = request.user
        questionnaire_response.save()

        redirect_url = get_limesurvey_response_url(questionnaire_response)

        return redirect_url
    else:
        return None


def get_limesurvey_response_url(questionnaire_response):
    questionnaire_lime_survey = Questionnaires()
    token = questionnaire_lime_survey.get_participant_properties(
        questionnaire_response.questionnaire_configuration.lime_survey_id,
        questionnaire_response.token_id, "token")
    questionnaire_lime_survey.release_session_key()

    redirect_url = \
        '%s/index.php/%s/token/%s/idavaliador/%s/datdataaquisicao/%s/idparticipante/%s/newtest/Y' % (
            settings.LIMESURVEY['URL'],
            questionnaire_response.questionnaire_configuration.lime_survey_id,
            token,
            str(questionnaire_response.questionnaire_responsible.id),
            questionnaire_response.date.strftime('%d-%m-%Y'),
            str(questionnaire_response.subject_of_experiment.subject.id))

    # redirect_url = \
    # '%s/index.php/survey/index/sid/%s/token/%s/lang/pt-BR/idavaliador/%s/datdataaquisicao/%s/idparticipante/%s' % (
    # settings.LIMESURVEY['URL'],
    # questionnaire_response.questionnaire_configuration.lime_survey_id,
    #     token,
    #     questionnaire_response.questionnaire_responsible.id,
    #     questionnaire_response.date.strftime('%d-%m-%Y'),
    #     questionnaire_response.subject.id)

    return redirect_url


@login_required
@permission_required('experiment.add_questionnaireresponse')
def subject_questionnaire_response_create(request, experiment_id, subject_id, questionnaire_id,
                                          template_name="experiment/subject_questionnaire_response_form.html"):
    questionnaire_config = get_object_or_404(QuestionnaireConfiguration, id=questionnaire_id)

    surveys = Questionnaires()
    survey_title = surveys.get_survey_title(questionnaire_config.lime_survey_id)
    survey_active = surveys.get_survey_properties(questionnaire_config.lime_survey_id, 'active')
    survey_admin = surveys.get_survey_properties(questionnaire_config.lime_survey_id, 'admin')
    surveys.release_session_key()

    questionnaire_responsible = request.user.get_full_name()
    subject = get_object_or_404(Subject, pk=subject_id)

    if request.method == "GET":
        questionnaire_response_form = QuestionnaireResponseForm(request.POST or None)
        fail = None
        redirect_url = None

    if request.method == "POST":
        questionnaire_response_form = QuestionnaireResponseForm(request.POST)

        if request.POST['action'] == "save":
            redirect_url = subject_questionnaire_response_start_fill_questionnaire(request, subject_id,
                                                                                   questionnaire_id)
            if not redirect_url:
                fail = False
            else:
                fail = True
                messages.info(request, 'Você será redirecionado para o questionário. Aguarde.')

    context = {
        "FAIL": fail,
        "URL": redirect_url,
        "questionnaire_response_form": questionnaire_response_form,
        "questionnaire_configuration": questionnaire_config,
        "survey_title": survey_title,
        "survey_admin": survey_admin,
        "survey_active": survey_active,
        "questionnaire_responsible": questionnaire_responsible,
        "creating": True,
        "subject": subject
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_questionnaireresponse')
def questionnaire_response_update(request, questionnaire_response_id,
                                  template_name="experiment/subject_questionnaire_response_form.html"):
    questionnaire_response = get_object_or_404(QuestionnaireResponse, id=questionnaire_response_id)

    questionnaire_configuration = questionnaire_response.questionnaire_configuration

    surveys = Questionnaires()
    survey_title = surveys.get_survey_title(questionnaire_configuration.lime_survey_id)
    survey_active = surveys.get_survey_properties(questionnaire_configuration.lime_survey_id, 'active')
    survey_admin = surveys.get_survey_properties(questionnaire_configuration.lime_survey_id, 'admin')
    survey_completed = (surveys.get_participant_properties(questionnaire_configuration.lime_survey_id,
                                                           questionnaire_response.token_id,
                                                           "completed") != "N")
    surveys.release_session_key()

    questionnaire_responsible = questionnaire_response.questionnaire_responsible
    subject = questionnaire_response.subject_of_experiment.subject

    questionnaire_response_form = QuestionnaireResponseForm(None, instance=questionnaire_response)

    if request.method == "GET":
        fail = None
        redirect_url = None

    if request.method == "POST":

        if request.POST['action'] == "save":

            redirect_url = get_limesurvey_response_url(questionnaire_response)

            if not redirect_url:
                fail = False
            else:
                fail = True
                messages.info(request, 'Você será redirecionado para o questionário. Aguarde.')

        else:
            if request.POST['action'] == "remove":
                surveys = Questionnaires()
                result = surveys.delete_participant(
                    questionnaire_configuration.lime_survey_id,
                    questionnaire_response.token_id)
                surveys.release_session_key()
                result = result[str(questionnaire_response.token_id)]
                if result == 'Deleted' or result == 'Invalid token ID':
                    questionnaire_response.delete()
                    messages.success(request, 'Preenchimento removido com sucesso')
                else:
                    messages.error(request, "Erro ao deletar o preenchimento")
                redirect_url = reverse("subject_questionnaire",
                                       args=(questionnaire_configuration.experiment.id, subject.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "FAIL": fail,
        "URL": redirect_url,
        "questionnaire_response_form": questionnaire_response_form,
        "questionnaire_configuration": questionnaire_configuration,
        "survey_title": survey_title,
        "survey_admin": survey_admin,
        "survey_active": survey_active,
        "questionnaire_response_id": questionnaire_response_id,
        "questionnaire_responsible": questionnaire_responsible,
        "creating": False,
        "subject": subject,
        "completed": survey_completed
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_questionnaireresponse')
def questionnaire_response_view(request, questionnaire_response_id,
                                template_name="experiment/subject_questionnaire_response_view.html"):
    questionnaire_response = get_object_or_404(QuestionnaireResponse, id=questionnaire_response_id)
    questionnaire_configuration = questionnaire_response.questionnaire_configuration
    surveys = Questionnaires()
    survey_title = surveys.get_survey_title(questionnaire_configuration.lime_survey_id)
    token = surveys.get_participant_properties(questionnaire_configuration.lime_survey_id,
                                               questionnaire_response.token_id, "token")

    question_properties = []
    groups = surveys.list_groups(questionnaire_configuration.lime_survey_id)
    questionnaire_responses = []

    if not isinstance(groups, dict):
        for group in groups:
            if 'id' in group:
                question_list = surveys.list_questions(questionnaire_configuration.lime_survey_id, group['id'])
                question_list = sorted(question_list)
                for question in question_list:
                    properties = surveys.get_question_properties(question)
                    if ('{if' not in properties['question']) and ('{(' not in properties['question']) and (
                                'pont' not in properties['question']):
                        properties['question'] = re.sub('<.*?>', '', properties['question'])

                        if isinstance(properties['subquestions'], dict):
                            question_properties.append({
                                'question': properties['question'],
                                'question_id': properties['title'],
                                'answer_options': 'super_question',
                                'type': properties['type']
                            })
                            for key, value in sorted(properties['subquestions'].iteritems()):
                                question_properties.append({
                                    'question': value['question'],
                                    'question_id': properties['title'] + '[' + value['title'] + ']',
                                    'answer_options': properties['answeroptions'],
                                    'type': properties['type']
                                })
                        else:
                            question_properties.append({
                                'question': properties['question'],
                                'question_id': properties['title'],
                                'answer_options': '',
                                'type': properties['type']
                            })

        responses_list = surveys.get_responses_by_token(questionnaire_configuration.lime_survey_id, token)
        responses_list = responses_list.replace('\"', '')
        responses_list = responses_list.split('\n')
        responses_list[0] = responses_list[0].split(",")
        responses_list[1] = responses_list[1].split(",")

        for question in question_properties:

            if isinstance(question['answer_options'], basestring) and question['answer_options'] == "super_question":

                if question['question'] != '':
                    questionnaire_responses.append({
                        'question': question['question'],
                        'answer': '',
                        'type': question['type']
                    })
            else:

                answer = ''

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
                            answer = datetime.datetime.strptime(responses_list[1][index], '%Y-%m-%d %H:%M:%S')
                        else:
                            answer = responses_list[1][index]

                questionnaire_responses.append({
                    'question': question['question'],
                    'answer': answer,
                    'type': question['type']
                })

    surveys.release_session_key()

    context = {
        "questionnaire_responses": questionnaire_responses,
        "survey_title": survey_title,
        "questionnaire_response": questionnaire_response
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_questionnaireresponse')
def subject_questionnaire_view(request, experiment_id, subject_id,
                               template_name="experiment/subject_questionnaire_response_list.html"):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    subject = get_object_or_404(Subject, id=subject_id)

    questionnaires_configuration_list = QuestionnaireConfiguration.objects.filter(experiment=experiment)

    subject_questionnaires = []
    can_remove = True

    surveys = Questionnaires()

    for questionnaire_configuration in questionnaires_configuration_list:

        subject_of_experiment = get_object_or_404(SubjectOfExperiment, experiment=experiment, subject=subject)

        questionnaire_responses = QuestionnaireResponse.objects. \
            filter(subject_of_experiment=subject_of_experiment). \
            filter(questionnaire_configuration=questionnaire_configuration)

        questionnaire_responses_with_status = []

        if questionnaire_responses:
            can_remove = False

        for questionnaire_response in questionnaire_responses:
            response_result = surveys.get_participant_properties(questionnaire_configuration.lime_survey_id,
                                                                 questionnaire_response.token_id,
                                                                 "completed")
            questionnaire_responses_with_status.append(
                {'questionnaire_response': questionnaire_response,
                 'completed': response_result != "N"}
            )

        subject_questionnaires.append(
            {'questionnaire_configuration': questionnaire_configuration,
             'title': surveys.get_survey_title(questionnaire_configuration.lime_survey_id),
             'questionnaire_responses': questionnaire_responses_with_status}
        )

    if request.method == "POST":

        if request.POST['action'] == "remove":
            if can_remove:
                subject_of_experiment = get_object_or_404(SubjectOfExperiment, experiment=experiment, subject=subject)
                subject_of_experiment.delete()

                messages.info(request, 'Participante removido do experimento.')
                redirect_url = reverse("subjects", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)
            else:
                messages.error(request, "Não foi possível excluir o paciente, pois há respostas associadas")
                redirect_url = reverse("subject_questionnaire", args=(experiment_id, subject_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        'subject': subject,
        'experiment': experiment,
        'subject_questionnaires': subject_questionnaires
    }

    surveys.release_session_key()

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_subject')
def subjects_insert(request, experiment_id, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    subject = Subject()

    try:
        subject = Subject.objects.get(patient=patient)
    except subject.DoesNotExist:
        subject.patient = patient
        subject.save()

    experiment = get_object_or_404(Experiment, id=experiment_id)

    if not SubjectOfExperiment.objects.all().filter(experiment=experiment, subject=subject):
        SubjectOfExperiment(subject=subject, experiment=experiment).save()
    else:
        messages.warning(request, 'Participante já inserido para este experimento.')

    redirect_url = reverse("subjects", args=(experiment_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('experiment.add_subject')
def search_patients_ajax(request):
    patient_list = ''
    if request.method == "POST":
        search_text = request.POST['search_text']
        experiment_id = request.POST['experiment_id']
        if search_text:
            if re.match('[a-zA-Z ]+', search_text):
                patient_list = Patient.objects.filter(name_txt__icontains=search_text).exclude(removed=True)
            else:
                patient_list = Patient.objects.filter(cpf_id__icontains=search_text).exclude(removed=True)

    return render_to_response('experiment/ajax_search_patients.html',
                              {'patients': patient_list, 'experiment_id': experiment_id})


def upload_file(request, subject_id, experiment_id, template_name="experiment/upload_consent_form.html"):
    subject = get_object_or_404(Subject, pk=subject_id)
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    subject_of_experiment = get_object_or_404(SubjectOfExperiment, subject=subject, experiment=experiment)

    if request.method == "POST":

        if request.POST['action'] == "upload":
            file_form = FileForm(request.POST, request.FILES, instance=subject_of_experiment)
            if 'consent_form' in request.FILES:
                if file_form.is_valid():
                    file_form.save()
                    messages.success(request, 'Termo salvo com sucesso.')

                redirect_url = reverse("subjects", args=(experiment_id, ))
                return HttpResponseRedirect(redirect_url)
            else:
                messages.error(request, 'Não existem anexos para salvar')
        else:
            if request.POST['action'] == "remove":
                subject_of_experiment.consent_form = ''
                subject_of_experiment.save()
                messages.success(request, 'Anexo removido com sucesso.')

                redirect_url = reverse("subjects", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

    else:
        file_form = FileForm(request.POST or None)

    context = {
        'subject': subject,
        'experiment': experiment,
        'file_form': file_form,
        'file_list': subject_of_experiment.consent_form
    }
    return render(request, template_name, context)
