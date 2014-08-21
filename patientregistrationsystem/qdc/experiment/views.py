# coding=utf-8
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from experiment.models import Experiment, QuestionnaireConfiguration, Subject, TimeUnit, QuestionnaireResponse
from experiment.forms import ExperimentForm, QuestionnaireConfigurationForm, QuestionnaireResponseForm

from quiz.models import Patient
from quiz.abc_search_engine import Questionnaires

import re
import datetime


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

                # if 'chosen_questionnaires' in request.POST:
                #
                # for survey_id in request.POST.getlist('chosen_questionnaires'):
                #
                # questionnaire = Questionnaire()
                #
                # try:
                #             questionnaire = Questionnaire.objects.get(survey_id=survey_id)
                #         except questionnaire.DoesNotExist:
                #             Questionnaire(survey_id=survey_id).save()
                #             questionnaire = Questionnaire.objects.get(survey_id=survey_id)
                #
                #         experiment_added.questionnaires.add(questionnaire)

                messages.success(request, 'Experimento criado com sucesso.')

                redirect_url = reverse("experiment_edit", args=(experiment_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "experiment_form": experiment_form,
        "creating": True}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
# @permission_required('experiment.delete_experiment')
def experiment_update(request, experiment_id, template_name="experiment/experiment_register.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    questionnaires_list = []

    if experiment:
        questionnaires_configuration_list = QuestionnaireConfiguration.objects.filter(experiment=experiment)
        questionnaires_list = Questionnaires().find_all_active_questionnaires()

        experiment_form = ExperimentForm(request.POST or None, instance=experiment)

        if request.method == "POST":

            if request.POST['action'] == "save":

                if experiment_form.is_valid():
                    experiment_form.save()
                    redirect_url = reverse("experiment_edit", args=(experiment_id,))
                    return HttpResponseRedirect(redirect_url)

            else:
                if request.POST['action'] == "remove":
                    experiment.delete()
                    return redirect('experiment_list')

    context = {
        "experiment_form": experiment_form,
        "creating": False,
        "questionnaires_list": questionnaires_list,
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

    questionnaires_list = Questionnaires().find_all_active_questionnaires()

    if request.method == "POST":

        if request.POST['action'] == "save":

            if questionnaire_form.is_valid():

                lime_survey_id = request.POST['questionnaire_selected']

                questionnaire = QuestionnaireConfiguration()
                questionnaire.lime_survey_id = lime_survey_id
                questionnaire.experiment = experiment
                # questionnaire.number_of_fills = request.POST['number_of_fills']
                # questionnaire.interval_between_fills_value = request.POST['interval_between_fills_value']
                # questionnaire.interval_between_fills_unit = get_object_or_404(TimeUnit, pk=request.POST['interval_between_fills_unit'])

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

    questionnaires_origin_list = Questionnaires().find_all_active_questionnaires()
    questionnaires_list = []

    for questionnaire_origin in questionnaires_origin_list:
        if questionnaire_origin['sid'] == questionnaire_configuration.lime_survey_id:
            questionnaires_list.append(questionnaire_origin)

    if request.method == "POST":

        if request.POST['action'] == "save":
            if questionnaire_form.is_valid():

                if "number_of_fills" in request.POST:
                    questionnaire_configuration.number_of_fills = request.POST['number_of_fills']

                # questionnaire_configuration.number_of_fills = request.POST['number_of_fills']
                # questionnaire_configuration.interval_between_fills_value = request.POST['interval_between_fills_value']
                # questionnaire_configuration.interval_between_fills_unit = get_object_or_404(TimeUnit, pk=request.POST[
                #     'interval_between_fills_unit'])

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
                questionnaire_configuration.delete()
                redirect_url = reverse("experiment_edit", args=(experiment.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "questionnaire_form": questionnaire_form,
        "creating": False,
        "experiment": experiment,
        "questionnaires_list": questionnaires_list}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_subject')
def subjects(request, experiment_id, template_name="experiment/subjects.html"):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    subject_list = experiment.subjects.all()

    context = {
        'experiment_id': experiment_id,
        'subject_list': subject_list,
        'experiment_title': experiment.title
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_questionnaireresponse')
def subject_questionnaire_response_start_fill_questionnaire(request, experiment_id, subject_id, questionnaire_id):
    questionnaire_response_form = QuestionnaireResponseForm(request.POST)

    if questionnaire_response_form.is_valid():
        questionnaire_response = questionnaire_response_form.save(commit=False)

        questionnaire_config = get_object_or_404(QuestionnaireConfiguration, id=questionnaire_id)

        questionnaire_lime_survey = Questionnaires()

        subject = get_object_or_404(Subject, pk=subject_id)
        patient = subject.patient

        result = questionnaire_lime_survey.add_participant(questionnaire_config.lime_survey_id, patient.name_txt, '',
                                                           patient.email_txt)

        if not result:
            messages.warning(request,
                             'Falha ao gerar token para responder questionário. Verifique se o questionário está ativo')
            return None

        questionnaire_response.subject = subject
        questionnaire_response.questionnaire_configuration = questionnaire_config
        questionnaire_response.token_id = result['token_id']
        questionnaire_response.date = datetime.datetime.strptime(request.POST['date'], '%d/%m/%Y')
        questionnaire_response.save()

        redirect_url = 'http://survey.numec.prp.usp.br/index.php/survey/index/sid/%s/token/%s' % (
            questionnaire_config.lime_survey_id, result['token'])

        return redirect_url
    else:
        return None


@login_required
@permission_required('experiment.add_questionnaireresponse')
def subject_questionnaire_response_create(request, experiment_id, subject_id, questionnaire_id,
                                          template_name="experiment/subject_questionnaire_response_form.html"):

    experiment = get_object_or_404(Experiment, id=experiment_id)
    if request.method == "GET":
        questionnaire_response_form = QuestionnaireResponseForm(request.POST or None)
        questionnaire_config = get_object_or_404(QuestionnaireConfiguration, id=questionnaire_id)
        subject = get_object_or_404(Subject, pk=subject_id)
        survey_title = Questionnaires().get_survey_title(questionnaire_config.lime_survey_id)
        survey_active = Questionnaires().get_survey_properties(questionnaire_config.lime_survey_id, 'active')
        survey_admin = Questionnaires().get_survey_properties(questionnaire_config.lime_survey_id, 'admin')
        questionnaire_responsible = request.user.get_full_name()
        date_fill_today = datetime.datetime.now().date().strftime('%d/%m/%Y')

    if request.method == "POST":
        if request.POST['action'] == "save":
            redirect_url = subject_questionnaire_response_start_fill_questionnaire(request, experiment_id, subject_id,
                                                                                   questionnaire_id)
            if not redirect_url:
                context = {'FAIL': True}
            else:
                context = {'FAIL': False,
                           'URL': redirect_url}

            messages.info(request, 'Você será redirecionado para o questionário... Aguarde')

            return render(request, template_name, context)

    context = {
        "questionnaire_response_form": questionnaire_response_form,
        "questionnaire_configuration": questionnaire_config,
        "date_fill_today": date_fill_today,
        "experiment_id": experiment_id,
        "experiment_title": experiment.title,
        "survey_title": survey_title,
        "survey_admin": survey_admin,
        "survey_active": survey_active,
        "questionnaire_responsible": questionnaire_responsible,
        "creating": True,
        "subject": subject,
        "subject_id": subject_id}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_questionnaireresponse')
def subject_questionnaire_view(request, experiment_id, subject_id,
                               template_name="experiment/subject_questionnaire_response_list.html"):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    questionnaires_configuration_list = QuestionnaireConfiguration.objects.filter(experiment=experiment)
    questionnaires_list = Questionnaires().find_all_active_questionnaires()

    context = {
        'subject_id': subject_id,
        'experiment_id': experiment_id,
        'experiment_title': experiment.title,
        'questionnaires_configuration_list': questionnaires_configuration_list,
        'questionnaires_list': questionnaires_list
    }

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

    if not experiment.subjects.all().filter(patient=patient):
        experiment.subjects.add(subject)
        experiment.save()
    else:
        messages.warning(request, 'Participante já inserido para este experimento.')

    redirect_url = reverse("subjects", args=(experiment_id))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('experiment.delete_subject')
def subjects_delete(request, experiment_id, subject_id):
    subject = Subject()

    try:
        subject = Subject.objects.get(pk=subject_id)
    except subject.DoesNotExist:
        messages.warning(request, 'Falha ao remover participante do experimento.')
        redirect_url = reverse("subjects", args=(experiment_id))
        return HttpResponseRedirect(redirect_url)

    experiment = get_object_or_404(Experiment, id=experiment_id)
    experiment.subjects.remove(subject)

    messages.info(request, 'Participante removido do experimento.')
    redirect_url = reverse("subjects", args=(experiment_id))
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
