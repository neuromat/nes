# coding=utf-8

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response

from experiment.models import Experiment, QuestionnaireConfiguration, Subject, TimeUnit
from experiment.forms import ExperimentForm, QuestionnaireConfigurationForm

from quiz.models import Patient
from quiz.abc_search_engine import Questionnaires

import re


class QuestionnaireConfigurationCustom(QuestionnaireConfiguration):
    title = ""


@login_required
def experiment_list(request, template_name="experiment/experiment_list.html"):
    experiments = Experiment.objects.order_by('title')

    context = {"experiments": experiments}

    return render(request, template_name, context)


@login_required
def experiment_create(request, template_name="experiment/experiment_register.html"):
    experiment_form = ExperimentForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if experiment_form.is_valid():

                experiment_added = experiment_form.save()

                # if 'chosen_questionnaires' in request.POST:
                #
                #     for survey_id in request.POST.getlist('chosen_questionnaires'):
                #
                #         questionnaire = Questionnaire()
                #
                #         try:
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

    context = {
        "experiment_form": experiment_form,
        "creating": False,
        "questionnaires_list": questionnaires_list,
        "questionnaires_configuration_list": questionnaires_configuration_list,
        "experiment": experiment}

    return render(request, template_name, context)


@login_required
def questionnaire_create(request, experiment_id, template_name="experiment/questionnaire_register.html"):

    experiment = get_object_or_404(Experiment, pk=experiment_id)
    questionnaire_form = QuestionnaireConfigurationForm(request.POST or None)

    questionnaires_list = Questionnaires().find_all_active_questionnaires()

    if request.method == "POST":

        if request.POST['action'] == "save":
            if questionnaire_form.is_valid():

                lime_survey_id = request.POST['questionnaire_selected']

                questionnaire = QuestionnaireConfiguration()
                questionnaire.lime_survey_id = lime_survey_id
                questionnaire.experiment = experiment
                questionnaire.number_of_fills = request.POST['number_of_fills']
                questionnaire.interval_between_fills_value = request.POST['interval_between_fills_value']
                questionnaire.interval_between_fills_unit = get_object_or_404(TimeUnit, pk=request.POST['interval_between_fills_unit'])

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
def questionnaire_update(request, questionnaire_configuration_id, template_name="experiment/questionnaire_register.html"):

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

                questionnaire_configuration.number_of_fills = request.POST['number_of_fills']
                questionnaire_configuration.interval_between_fills_value = request.POST['interval_between_fills_value']
                questionnaire_configuration.interval_between_fills_unit = get_object_or_404(TimeUnit, pk=request.POST['interval_between_fills_unit'])

                questionnaire_configuration.save()

                messages.success(request, 'Questionário atualizado com sucesso.')

                redirect_url = reverse("experiment_edit", args=(experiment.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "questionnaire_form": questionnaire_form,
        "creating": False,
        "experiment": experiment,
        "questionnaires_list": questionnaires_list}

    return render(request, template_name, context)


def subjects(request, experiment_id, template_name="experiment/subjects.html"):
    experiment = get_object_or_404(Experiment, id=experiment_id)
    subject_list = experiment.subjects.all()

    context = {
        'experiment_id': experiment_id,
        'subject_list': subject_list.all()
    }

    return render(request, template_name, context)


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
        messages.warning(request, 'Participante jah inserido para este experimento.')

    redirect_url = reverse("subjects", args=(experiment_id))
    return HttpResponseRedirect(redirect_url)  # + "?status=edit&currentTab=3"


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

    messages.warning(request, 'Participante removido do experimento.')
    redirect_url = reverse("subjects", args=(experiment_id))
    return HttpResponseRedirect(redirect_url)


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
