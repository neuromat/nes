# coding=utf-8
from functools import partial
import re
import datetime
import csv

from StringIO import StringIO

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.db.models.deletion import ProtectedError
from django.db.models import Q
from django.conf import settings

from experiment.models import Experiment, QuestionnaireConfiguration, Subject, TimeUnit, \
    QuestionnaireResponse, SubjectOfGroup, Group, Component, ComponentConfiguration, Questionnaire, Task, Stimulus, \
    Pause, Instruction, Block, ClassificationOfDiseases, ResearchProject, Keyword
from experiment.forms import ExperimentForm, QuestionnaireConfigurationForm, QuestionnaireResponseForm, \
    FileForm, GroupForm, TaskForm, InstructionForm, ComponentForm, StimulusForm, PauseForm, BlockForm, \
    ComponentConfigurationForm, ResearchProjectForm
from patient.models import Patient
from experiment.abc_search_engine import Questionnaires


permission_required = partial(permission_required, raise_exception=True)

icon_class = {
    u'task': 'glyphicon glyphicon-check',
    u'instruction': 'glyphicon glyphicon-comment',
    u'stimulus': 'glyphicon glyphicon-headphones',
    u'pause': 'glyphicon glyphicon-time',
    u'questionnaire': 'glyphicon glyphicon-list-alt',
    u'block': 'glyphicon glyphicon-th-large',
}

delimiter = "-"

# pylint: disable=E1101
# pylint: disable=E1103


@login_required
@permission_required('experiment.view_researchproject')
def research_project_list(request, template_name="experiment/research_project_list.html"):
    research_projects = ResearchProject.objects.order_by('start_date')
    context = {"research_projects": research_projects}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_researchproject')
def research_project_create(request, template_name="experiment/research_project_register.html"):
    research_project_form = ResearchProjectForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if research_project_form.is_valid():
                research_project_added = research_project_form.save()

                messages.success(request, 'Estudo criado com sucesso.')

                redirect_url = reverse("research_project_view", args=(research_project_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "research_project_form": research_project_form,
        "creating": True,
        "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_researchproject')
def research_project_view(request, research_project_id, template_name="experiment/research_project_register.html"):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)
    research_project_form = ResearchProjectForm(request.POST or None, instance=research_project)

    for field in research_project_form.fields:
        research_project_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":
            try:
                for keyword in research_project.keywords.all():
                    manage_keywords(keyword, ResearchProject.objects.exclude(id=research_project.id))

                research_project.delete()
                return redirect('research_project_list')
            except ProtectedError:
                messages.error(request, "Erro ao tentar excluir o estudo.")

    context = {
        "research_project": research_project,
        "research_project_form": research_project_form,
        "keywords": research_project.keywords.all()}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_researchproject')
def research_project_update(request, research_project_id, template_name="experiment/research_project_register.html"):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)
    research_project_form = ResearchProjectForm(request.POST or None, instance=research_project)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if research_project_form.is_valid():
                if research_project_form.has_changed():
                    research_project_form.save()
                    messages.success(request, 'Estudo atualizado com sucesso.')
                else:
                    messages.success(request, 'Não há alterações para salvar.')

                redirect_url = reverse("research_project_view", args=(research_project.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "research_project": research_project,
        "research_project_form": research_project_form,
        "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_researchproject')
def keyword_search_ajax(request):
    keywords_name_list = []
    keywords_list_filtered = []
    search_text = None

    if request.method == "POST":
        search_text = request.POST['search_text']

        if search_text:
            # Avoid suggesting the creation of a keyword that already exists.
            keywords_list = Keyword.objects.filter(name__icontains=search_text)
            keywords_name_list = keywords_list.values_list('name', flat=True)
            # Avoid suggestion keywords that are already associated with this research project
            research_project = get_object_or_404(ResearchProject, pk=request.POST['research_project_id'])
            keywords_included = research_project.keywords.values_list('name', flat=True)
            keywords_list_filtered = keywords_list.exclude(name__in=keywords_included).order_by('name')

    return render_to_response('experiment/keyword_ajax_search.html',
                              {'keywords': keywords_list_filtered,
                               'offer_creation': search_text not in keywords_name_list,
                               'research_project_id': request.POST['research_project_id'],
                               'new_keyword_name': search_text})


@login_required
@permission_required('experiment.change_researchproject')
def keyword_create_ajax(request, research_project_id, keyword_name):
    keyword = Keyword.objects.create(name=keyword_name)
    keyword.save()

    research_project = get_object_or_404(ResearchProject, pk=research_project_id)
    research_project.keywords.add(keyword)

    redirect_url = reverse("research_project_view", args=(research_project_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('experiment.change_researchproject')
def keyword_add_ajax(request, research_project_id, keyword_id):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)
    keyword = get_object_or_404(Keyword, pk=keyword_id)
    research_project.keywords.add(keyword)

    redirect_url = reverse("research_project_view", args=(research_project_id,))
    return HttpResponseRedirect(redirect_url)


def manage_keywords(keyword, research_projects):
    should_remove = True
    for research_project in research_projects:
        if keyword in research_project.keywords.all():
            should_remove = False
            break
    if should_remove:
        keyword.delete()


@login_required
@permission_required('experiment.change_researchproject')
def keyword_remove_ajax(request, research_project_id, keyword_id):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)
    keyword = get_object_or_404(Keyword, pk=keyword_id)
    research_project.keywords.remove(keyword)

    manage_keywords(keyword, ResearchProject.objects.all())

    redirect_url = reverse("research_project_view", args=(research_project_id,))
    return HttpResponseRedirect(redirect_url)


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

                redirect_url = reverse("experiment_view", args=(experiment_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "experiment_form": experiment_form,
        "creating": True,
        "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def experiment_view(request, experiment_id, template_name="experiment/experiment_register.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    group_list = Group.objects.filter(experiment=experiment)
    experiment_form = ExperimentForm(request.POST or None, instance=experiment)

    for field in experiment_form.fields:
        experiment_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":
            try:
                experiment.delete()
                return redirect('experiment_list')
            except ProtectedError:
                messages.error(request, "Não foi possível excluir o experimento, pois há grupos associados")

    context = {
        "experiment_form": experiment_form,
        "group_list": group_list,
        "experiment": experiment}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def experiment_update(request, experiment_id, template_name="experiment/experiment_register.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    group_list = Group.objects.filter(experiment=experiment)
    experiment_form = ExperimentForm(request.POST or None, instance=experiment)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if experiment_form.is_valid():
                if experiment_form.has_changed():
                    experiment_form.save()
                    messages.success(request, 'Experimento atualizado com sucesso.')
                else:
                    messages.success(request, 'Não há alterações para salvar.')

                redirect_url = reverse("experiment_view", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "experiment_form": experiment_form,
        "editing": True,
        "group_list": group_list,
        "experiment": experiment}

    return render(request, template_name, context)


@login_required
def group_create(request, experiment_id, template_name="experiment/group_register.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    group_form = GroupForm(request.POST or None)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if group_form.is_valid():
                group_added = group_form.save(commit=False)
                group_added.experiment_id = experiment_id
                group_added.save()

                messages.success(request, 'Grupo incluído com sucesso.')

                redirect_url = reverse("group_view", args=(group_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "group_form": group_form,
        "creating": True,
        "editing": True,
        "experiment": experiment}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_experiment')
def group_view(request, group_id, template_name="experiment/group_register.html"):
    group = get_object_or_404(Group, pk=group_id)
    group_form = GroupForm(request.POST or None, instance=group)

    for field in group_form.fields:
        group_form.fields[field].widget.attrs['disabled'] = True

    experiment = get_object_or_404(Experiment, pk=group.experiment_id)

    list_of_questionnaires_configuration = QuestionnaireConfiguration.objects.filter(group=group)
    surveys = Questionnaires()
    limesurvey_available = check_limesurvey_access(request, surveys)

    list_of_questionnaires_configuration = [
        {"survey_title": surveys.get_survey_title(questionnaire_configuration.lime_survey_id),
         "number_of_fills": questionnaire_configuration.number_of_fills,
         "interval_between_fills_value": questionnaire_configuration.interval_between_fills_value,
         "interval_between_fills_unit": questionnaire_configuration.interval_between_fills_unit,
         "id": questionnaire_configuration.id}
        for questionnaire_configuration in list_of_questionnaires_configuration]
    surveys.release_session_key()

    if request.method == "POST":
        if request.POST['action'] == "remove":
            try:
                group.delete()
                redirect_url = reverse("experiment_view", args=(experiment.id,))
                return HttpResponseRedirect(redirect_url)
            except ProtectedError:
                messages.error(request, "Não foi possível excluir o grupo, pois há dependências.")
        elif request.POST['action'] == "remove_experimental_protocol":
            group.experimental_protocol = None
            group.save()

    context = {
        "classification_of_diseases_list": group.classification_of_diseases.all(),
        "group_form": group_form,
        "questionnaires_configuration_list": list_of_questionnaires_configuration,
        "experiment": experiment,
        "group": group,
        "editing": False,
        "number_of_subjects": SubjectOfGroup.objects.all().filter(group=group).count(),
        "limesurvey_available": limesurvey_available}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_experiment')
def group_update(request, group_id, template_name="experiment/group_register.html"):
    group = get_object_or_404(Group, pk=group_id)
    group_form = GroupForm(request.POST or None, instance=group)

    experiment = get_object_or_404(Experiment, pk=group.experiment_id)

    list_of_questionnaires_configuration = QuestionnaireConfiguration.objects.filter(group=group)
    surveys = Questionnaires()
    limesurvey_available = check_limesurvey_access(request, surveys)

    list_of_questionnaires_configuration = [
        {"survey_title": surveys.get_survey_title(questionnaire_configuration.lime_survey_id),
         "number_of_fills": questionnaire_configuration.number_of_fills,
         "interval_between_fills_value": questionnaire_configuration.interval_between_fills_value,
         "interval_between_fills_unit": questionnaire_configuration.interval_between_fills_unit,
         "id": questionnaire_configuration.id}
        for questionnaire_configuration in list_of_questionnaires_configuration]
    surveys.release_session_key()

    if request.method == "POST":
        if request.POST['action'] == "save":
            if group_form.is_valid():
                if group_form.has_changed():
                    group_form.save()
                    messages.success(request, 'Grupo atualizado com sucesso.')
                else:
                    messages.success(request, 'Não há alterações para salvar.')

                redirect_url = reverse("group_view", args=(group_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "classification_of_diseases_list": group.classification_of_diseases.all(),
        "group_id": group_id,
        "group_form": group_form,
        "editing": True,
        "questionnaires_configuration_list": list_of_questionnaires_configuration,
        "experiment": experiment,
        "group": group,
        "number_of_subjects": SubjectOfGroup.objects.all().filter(group=group).count(),
        "limesurvey_available": limesurvey_available}

    return render(request, template_name, context)


@permission_required('experiment.add_subject')
def search_cid10_ajax(request):
    cid_10_list = ''

    if request.method == "POST":
        search_text = request.POST['search_text']
        group_id = request.POST['group_id']

        if search_text:
            cid_10_list = ClassificationOfDiseases.objects.filter(Q(abbreviated_description__icontains=search_text) |
                                                                  Q(description__icontains=search_text))

        return render_to_response('experiment/ajax_cid10.html', {'cid_10_list': cid_10_list, 'group_id': group_id})


@login_required
@permission_required('experiment.add_experiment')
def classification_of_diseases_insert(request, group_id, classification_of_diseases_id):
    """Add group disease"""
    group = get_object_or_404(Group, pk=group_id)
    classification_of_diseases = get_object_or_404(ClassificationOfDiseases, pk=classification_of_diseases_id)
    group.classification_of_diseases.add(classification_of_diseases)
    redirect_url = reverse("group_view", args=(group_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('experiment.add_experiment')
def classification_of_diseases_remove(request, group_id, classification_of_diseases_id):
    """Remove group disease"""
    group = get_object_or_404(Group, pk=group_id)
    classification_of_diseases = get_object_or_404(ClassificationOfDiseases, pk=classification_of_diseases_id)
    classification_of_diseases.group_set.remove(group)
    redirect_url = reverse("group_view", args=(group_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('experiment.add_questionnaireconfiguration')
def questionnaire_create(request, group_id, template_name="experiment/questionnaire_register.html"):
    group = get_object_or_404(Group, pk=group_id)

    questionnaire_form = QuestionnaireConfigurationForm(
        request.POST or None,
        initial={'number_of_fills': 1, 'interval_between_fills_value': None})

    questionnaires_list = []

    if request.method == "GET":
        questionnaires_of_group = QuestionnaireConfiguration.objects.filter(group=group)

        if not questionnaires_of_group:
            questionnaires_list = Questionnaires().find_all_active_questionnaires()
        else:
            active_questionnaires_list = Questionnaires().find_all_active_questionnaires()

            for questionnaire in questionnaires_of_group:
                for active_questionnaire in active_questionnaires_list:
                    if active_questionnaire['sid'] == questionnaire.lime_survey_id:
                        active_questionnaires_list.remove(active_questionnaire)

            questionnaires_list = active_questionnaires_list

    if request.method == "POST":
        if request.POST['action'] == "save":
            if questionnaire_form.is_valid():
                lime_survey_id = request.POST['questionnaire_selected']

                questionnaire = QuestionnaireConfiguration()
                questionnaire.lime_survey_id = lime_survey_id
                questionnaire.group = group

                if "number_of_fills" in request.POST:
                    questionnaire.number_of_fills = request.POST['number_of_fills']

                if "interval_between_fills_value" in request.POST:
                    questionnaire.interval_between_fills_value = request.POST['interval_between_fills_value']

                if "interval_between_fills_unit" in request.POST:
                    questionnaire.interval_between_fills_unit = \
                        get_object_or_404(TimeUnit, pk=request.POST['interval_between_fills_unit'])

                questionnaire.save()
                messages.success(request, 'Questionário incluído com sucesso.')
                redirect_url = reverse("group_view", args=(group_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "questionnaire_form": questionnaire_form,
        "creating": True,
        "updating": False,
        "group": group,
        "questionnaires_list": questionnaires_list}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_questionnaireconfiguration')
def questionnaire_update(request, questionnaire_configuration_id,
                         template_name="experiment/questionnaire_register.html"):
    questionnaire_configuration = get_object_or_404(QuestionnaireConfiguration, pk=questionnaire_configuration_id)
    group = get_object_or_404(Group, pk=questionnaire_configuration.group.id)
    questionnaire_form = QuestionnaireConfigurationForm(request.POST or None, instance=questionnaire_configuration)

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
                redirect_url = reverse("group_view", args=(group.id,))
                return HttpResponseRedirect(redirect_url)
        elif request.POST['action'] == "remove":
            try:
                questionnaire_configuration.delete()
                redirect_url = reverse("group_view", args=(group.id,))
                return HttpResponseRedirect(redirect_url)
            except ProtectedError:
                messages.error(request, "Não foi possível excluir o questionário, pois há respostas associadas")

    surveys = Questionnaires()
    questionnaire_title = surveys.get_survey_title(questionnaire_configuration.lime_survey_id)

    limesurvey_available = check_limesurvey_access(request, surveys)

    subject_list_with_status = []

    for subject_of_group in SubjectOfGroup.objects.all().filter(group=group).order_by('subject__patient__name'):
        subject_responses = QuestionnaireResponse.objects.\
            filter(subject_of_group=subject_of_group). \
            filter(questionnaire_configuration=questionnaire_configuration)
        amount_of_completed_questionnaires = 0
        questionnaire_responses_with_status = []

        for subject_response in subject_responses:
            response_result = surveys.get_participant_properties(questionnaire_configuration.lime_survey_id,
                                                                 subject_response.token_id, "completed")
            completed = False

            if response_result != "N" and response_result != "":
                amount_of_completed_questionnaires += 1
                completed = True

            questionnaire_responses_with_status.append(
                {'questionnaire_response': subject_response,
                 'completed': completed}
            )

        # If unlimited fills, percentage is related to the number of completed questionnaires
        if questionnaire_configuration.number_of_fills is None:
            denominator = subject_responses.count()

            if subject_responses.count() > 0:
                percentage = 100 * amount_of_completed_questionnaires / denominator
            else:
                percentage = 0
        else:
            denominator = questionnaire_configuration.number_of_fills

            # Handle cases in which number of possible responses was reduced afterwords.
            if questionnaire_configuration.number_of_fills < amount_of_completed_questionnaires:
                percentage = 100
            else:
                percentage = 100 * amount_of_completed_questionnaires / denominator

        subject_list_with_status.append(
            {'subject': subject_of_group.subject,
             'amount_of_completed_questionnaires': amount_of_completed_questionnaires,
             'denominator': denominator,
             'percentage': percentage,
             'questionnaire_responses': questionnaire_responses_with_status})

    surveys.release_session_key()

    context = {
        "questionnaire_form": questionnaire_form,
        "creating": False,
        "updating": True,
        "group": group,
        "questionnaire_title": questionnaire_title,
        "questionnaire_configuration": questionnaire_configuration,
        'subject_list': subject_list_with_status,
        "limesurvey_available": limesurvey_available
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_subject')
def subjects(request, group_id, template_name="experiment/subjects.html"):
    group = get_object_or_404(Group, id=group_id)

    subject_list_with_status = []

    list_of_questionnaires_configuration = QuestionnaireConfiguration.objects.filter(group=group)

    surveys = Questionnaires()

    limesurvey_available = check_limesurvey_access(request, surveys)

    for subject_of_group in SubjectOfGroup.objects.all().filter(group=group).order_by('subject__patient__name'):
        number_of_questionnaires_filled = 0

        for questionnaire_configuration in list_of_questionnaires_configuration:
            subject_responses = QuestionnaireResponse.objects. \
                filter(subject_of_group=subject_of_group). \
                filter(questionnaire_configuration=questionnaire_configuration)

            if subject_responses:
                if (questionnaire_configuration.number_of_fills is None and subject_responses.count() > 0) or \
                        (questionnaire_configuration.number_of_fills is not None and
                            questionnaire_configuration.number_of_fills <= subject_responses.count()):

                    amount_of_completed_questionnaires = 0

                    for subject_response in subject_responses:
                        response_result = surveys.get_participant_properties(questionnaire_configuration.lime_survey_id,
                                                                             subject_response.token_id, "completed")

                        if response_result == "N" or response_result == "":
                            break
                        else:
                            amount_of_completed_questionnaires += 1

                    if (questionnaire_configuration.number_of_fills is None and
                            amount_of_completed_questionnaires == subject_responses.count()) or \
                            (questionnaire_configuration.number_of_fills is not None and
                                amount_of_completed_questionnaires >= questionnaire_configuration.number_of_fills):
                        number_of_questionnaires_filled += 1

        percentage = 0

        if list_of_questionnaires_configuration.count() > 0:
            percentage = 100 * number_of_questionnaires_filled / list_of_questionnaires_configuration.count()

        subject_list_with_status.append(
            {'subject': subject_of_group.subject,
             'number_of_questionnaires_filled': number_of_questionnaires_filled,
             'total_of_questionnaires': list_of_questionnaires_configuration.count(),
             'percentage': percentage,
             'consent': subject_of_group.consent_form})

    context = {
        'group': group,
        "group_id": group_id,
        'subject_list': subject_list_with_status,
        "limesurvey_available": limesurvey_available
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

        subject_of_group = get_object_or_404(SubjectOfGroup, subject=subject, group=questionnaire_config.group)

        if not questionnaire_lime_survey.survey_has_token_table(questionnaire_config.lime_survey_id):
            messages.warning(request,
                             'Preenchimento não disponível - Tabela de tokens não iniciada')
            return None, None

        if questionnaire_lime_survey.get_survey_properties(questionnaire_config.lime_survey_id, 'active') == 'N':
            messages.warning(request,
                             'Preenchimento não disponível - Questionário não está ativo')
            return None, None

        if not check_required_fields(questionnaire_lime_survey, questionnaire_config.lime_survey_id):
            messages.warning(request,
                             'Preenchimento não disponível - Questionário não contém campos padronizados')
            return None, None

        result = questionnaire_lime_survey.add_participant(questionnaire_config.lime_survey_id, patient.name, '',
                                                           patient.email)

        questionnaire_lime_survey.release_session_key()

        if not result:
            messages.warning(request,
                             'Falha ao gerar token para responder questionário. Verifique se o questionário está ativo')
            return None, None

        questionnaire_response.subject_of_group = subject_of_group
        questionnaire_response.questionnaire_configuration = questionnaire_config
        questionnaire_response.token_id = result['token_id']
        questionnaire_response.date = datetime.datetime.strptime(request.POST['date'], '%d/%m/%Y')
        questionnaire_response.questionnaire_responsible = request.user
        questionnaire_response.save()

        redirect_url = get_limesurvey_response_url(questionnaire_response)

        return redirect_url, questionnaire_response.pk
    else:
        return None, None


def get_limesurvey_response_url(questionnaire_response):
    questionnaire_lime_survey = Questionnaires()
    token = questionnaire_lime_survey.get_participant_properties(
        questionnaire_response.questionnaire_configuration.lime_survey_id,
        questionnaire_response.token_id, "token")
    questionnaire_lime_survey.release_session_key()

    redirect_url = \
        '%s/index.php/%s/token/%s/responsibleid/%s/acquisitiondate/%s/subjectid/%s/newtest/Y' % (
            settings.LIMESURVEY['URL_WEB'],
            questionnaire_response.questionnaire_configuration.lime_survey_id,
            token,
            str(questionnaire_response.questionnaire_responsible.id),
            questionnaire_response.date.strftime('%d-%m-%Y'),
            str(questionnaire_response.subject_of_group.subject.id))

    return redirect_url


@login_required
@permission_required('experiment.add_questionnaireresponse')
def subject_questionnaire_response_create(request, subject_id, questionnaire_id,
                                          template_name="experiment/subject_questionnaire_response_form.html"):
    questionnaire_config = get_object_or_404(QuestionnaireConfiguration, id=questionnaire_id)

    surveys = Questionnaires()
    survey_title = surveys.get_survey_title(questionnaire_config.lime_survey_id)
    survey_active = surveys.get_survey_properties(questionnaire_config.lime_survey_id, 'active')
    # survey_admin = surveys.get_survey_properties(questionnaire_config.lime_survey_id, 'admin')
    surveys.release_session_key()

    questionnaire_response_form = None
    fail = None
    redirect_url = None
    questionnaire_response_id = None

    if request.method == "GET":
        questionnaire_response_form = QuestionnaireResponseForm(request.POST or None)

    if request.method == "POST":
        questionnaire_response_form = QuestionnaireResponseForm(request.POST)

        if request.POST['action'] == "save":
            redirect_url, questionnaire_response_id = \
                subject_questionnaire_response_start_fill_questionnaire(request, subject_id, questionnaire_id)
            if not redirect_url:
                fail = False
            else:
                fail = True
                messages.info(request, 'Você será redirecionado para o questionário. Aguarde.')

    origin = get_origin(request)

    context = {
        "FAIL": fail,
        "URL": redirect_url,
        "questionnaire_response_id": questionnaire_response_id,
        "questionnaire_response_form": questionnaire_response_form,
        "questionnaire_configuration": questionnaire_config,
        "survey_title": survey_title,
        # "survey_admin": survey_admin,
        "survey_active": survey_active,
        "questionnaire_responsible": request.user.get_username(),
        "creating": True,
        "subject": get_object_or_404(Subject, pk=subject_id),
        "group": questionnaire_config.group,
        "origin": origin
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
    # survey_admin = surveys.get_survey_properties(questionnaire_configuration.lime_survey_id, 'admin')
    survey_completed = (surveys.get_participant_properties(questionnaire_configuration.lime_survey_id,
                                                           questionnaire_response.token_id,
                                                           "completed") != "N")
    surveys.release_session_key()

    subject = questionnaire_response.subject_of_group.subject

    questionnaire_response_form = QuestionnaireResponseForm(None, instance=questionnaire_response)

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

        elif request.POST['action'] == "remove":
            surveys = Questionnaires()
            result = surveys.delete_participant(
                questionnaire_configuration.lime_survey_id,
                questionnaire_response.token_id)
            surveys.release_session_key()

            can_delete = False

            if str(questionnaire_response.token_id) in result:
                result = result[str(questionnaire_response.token_id)]
                if result == 'Deleted' or result == 'Invalid token ID':
                    can_delete = True
            else:
                if 'status' in result and result['status'] == u'Error: Invalid survey ID':
                    can_delete = True

            if can_delete:
                questionnaire_response.delete()
                messages.success(request, 'Preenchimento removido com sucesso')
            else:
                messages.error(request, "Erro ao deletar o preenchimento")
            redirect_url = reverse("subject_questionnaire",
                                   args=(questionnaire_configuration.group.id, subject.id,))
            return HttpResponseRedirect(redirect_url)

    origin = get_origin(request)

    context = {
        "FAIL": fail,
        "URL": redirect_url,
        "questionnaire_response_form": questionnaire_response_form,
        "questionnaire_configuration": questionnaire_configuration,
        "survey_title": survey_title,
        # "survey_admin": survey_admin,
        "survey_active": survey_active,
        "questionnaire_response_id": questionnaire_response_id,
        "questionnaire_responsible": questionnaire_response.questionnaire_responsible,
        "creating": False,
        "subject": subject,
        "completed": survey_completed,
        "group": questionnaire_configuration.group,
        "origin": origin
    }

    return render(request, template_name, context)


def get_origin(request):
    origin = '0'

    if request.method == "POST":
        if 'origin' in request.POST:
            origin = request.POST['origin']
    else:
        if 'origin' in request.GET:
            origin = request.GET['origin']

    return origin


def check_required_fields(surveys, lime_survey_id):
    """
    método para verificar se o questionário tem as questões de identificação corretas
    e se seus tipos também são corretos
    """

    fields_to_validate = {
        'responsibleid': {'type': 'N', 'found': False},
        'acquisitiondate': {'type': 'D', 'found': False},
        'subjectid': {'type': 'N', 'found': False},
    }

    validated_quantity = 0
    error = False

    groups = surveys.list_groups(lime_survey_id)

    if 'status' not in groups:

        for group in groups:
            question_list = surveys.list_questions(lime_survey_id, group['id'])
            for question in question_list:
                question_properties = surveys.get_question_properties(question, None)
                if question_properties['title'] in fields_to_validate:
                    field = fields_to_validate[question_properties['title']]
                    if not field['found']:
                        field['found'] = True
                        if field['type'] == question_properties['type']:
                            validated_quantity += 1
                        else:
                            error = True
                if error or validated_quantity == len(fields_to_validate):
                    break
            if error or validated_quantity == len(fields_to_validate):
                break

    return validated_quantity == len(fields_to_validate)


@login_required
@permission_required('experiment.view_questionnaireresponse')
def questionnaire_response_view(request, questionnaire_response_id,
                                template_name="experiment/subject_questionnaire_response_view.html"):
    view = request.GET['view']

    status_mode = None

    if 'status' in request.GET:
        status_mode = request.GET['status']

    questionnaire_responses = []

    questionnaire_response = get_object_or_404(QuestionnaireResponse, id=questionnaire_response_id)
    questionnaire_configuration = questionnaire_response.questionnaire_configuration
    surveys = Questionnaires()
    survey_title = surveys.get_survey_title(questionnaire_configuration.lime_survey_id)
    token = surveys.get_participant_properties(questionnaire_configuration.lime_survey_id,
                                               questionnaire_response.token_id, "token")

    question_properties = []
    groups = surveys.list_groups(questionnaire_configuration.lime_survey_id)

    if not isinstance(groups, dict):

        # defining language to be showed
        languages = surveys.get_survey_languages(questionnaire_configuration.lime_survey_id)
        language = languages['language']
        if request.LANGUAGE_CODE in languages['additional_languages'].split(' '):
            language = request.LANGUAGE_CODE

        for group in groups:
            if 'id' in group and group['id']['language'] == language:

                question_list = surveys.list_questions(questionnaire_configuration.lime_survey_id, group['id'])
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
        responses_string = surveys.get_responses_by_token(questionnaire_configuration.lime_survey_id, token, language)

        # ... transforming to a list:
        #   response_list[0] has the questions
        #   response_list[1] has the answers
        reader = csv.reader(StringIO(responses_string), delimiter=',')
        responses_list = []
        for row in reader:
            responses_list.append(row)

        for question in question_properties:

            if not question['hidden']:

                if isinstance(question['answer_options'], basestring) and question['answer_options'] == "super_question":

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

                        if question['question_id']+"[1]" in responses_list[0]:
                            index = responses_list[0].index(question['question_id']+"[1]")
                            answer_options = question['answer_options']
                            answer = question['attributes_lang']['dualscale_headerA'] + ": "
                            if responses_list[1][index] in answer_options:
                                answer_option = answer_options[responses_list[1][index]]
                                answer += answer_option['answer']
                            else:
                                answer += 'Sem resposta'

                        answer_list.append(answer)

                        if question['question_id']+"[2]" in responses_list[0]:
                            index = responses_list[0].index(question['question_id']+"[2]")
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

    context = {
        "questionnaire_responses": questionnaire_responses,
        "survey_title": survey_title,
        "questionnaire_response": questionnaire_response,
        "view": view,
        "status_mode": status_mode
    }

    return render(request, template_name, context)


def check_limesurvey_access(request, surveys):
    limesurvey_available = True
    if not surveys.session_key:
        limesurvey_available = False
        messages.warning(request, "LimeSurvey indisponível. Sistema funcionando parcialmente.")

    return limesurvey_available


@login_required
@permission_required('experiment.view_questionnaireresponse')
def subject_questionnaire_view(request, group_id, subject_id,
                               template_name="experiment/subject_questionnaire_response_list.html"):
    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)

    subject_questionnaires = []
    can_remove = True

    surveys = Questionnaires()

    limesurvey_available = check_limesurvey_access(request, surveys)

    for questionnaire_configuration in QuestionnaireConfiguration.objects.filter(group=group):

        questionnaire_responses = QuestionnaireResponse.objects. \
            filter(subject_of_group=get_object_or_404(SubjectOfGroup, group=group, subject=subject)). \
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
                 'completed': None if response_result is None else response_result != "N" and response_result != ""}
            )

        subject_questionnaires.append(
            {'questionnaire_configuration': questionnaire_configuration,
             'title': surveys.get_survey_title(questionnaire_configuration.lime_survey_id),
             'questionnaire_responses': questionnaire_responses_with_status}
        )

    if request.method == "POST":
        if request.POST['action'] == "remove":
            if can_remove:
                get_object_or_404(SubjectOfGroup, group=group, subject=subject).delete()

                messages.info(request, 'Participante removido do experimento.')
                redirect_url = reverse("subjects", args=(group_id,))
                return HttpResponseRedirect(redirect_url)
            else:
                messages.error(request, "Não foi possível excluir o paciente, pois há respostas associadas")
                redirect_url = reverse("subject_questionnaire", args=(group_id, subject_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        'subject': subject,
        'group': group,
        'subject_questionnaires': subject_questionnaires,
        'limesurvey_available': limesurvey_available
    }

    surveys.release_session_key()

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_subject')
def subjects_insert(request, group_id, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    subject = Subject()

    try:
        subject = Subject.objects.get(patient=patient)
    except subject.DoesNotExist:
        subject.patient = patient
        subject.save()

    group = get_object_or_404(Group, id=group_id)

    if not SubjectOfGroup.objects.all().filter(group=group, subject=subject):
        SubjectOfGroup(subject=subject, group=group).save()
    else:
        messages.warning(request, 'Participante já inserido para este grupo.')

    redirect_url = reverse("subjects", args=(group_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('experiment.add_subject')
def search_patients_ajax(request):
    patient_list = ''
    if request.method == "POST":
        search_text = request.POST['search_text']
        group_id = request.POST['group_id']
        if search_text:
            if re.match('[a-zA-Z ]+', search_text):
                patient_list = \
                    Patient.objects.filter(name__icontains=search_text).exclude(removed=True).order_by('name')
            else:
                patient_list = \
                    Patient.objects.filter(cpf__icontains=search_text).exclude(removed=True).order_by('name')

        return render_to_response('experiment/ajax_search_patients.html',
                                  {'patients': patient_list, 'group_id': group_id})


def upload_file(request, subject_id, group_id, template_name="experiment/upload_consent_form.html"):
    subject = get_object_or_404(Subject, pk=subject_id)
    group = get_object_or_404(Group, pk=group_id)
    subject_of_group = get_object_or_404(SubjectOfGroup, subject=subject, group=group)

    file_form = None

    if request.method == "POST":
        if request.POST['action'] == "upload":
            file_form = FileForm(request.POST, request.FILES, instance=subject_of_group)
            if 'consent_form' in request.FILES:
                if file_form.is_valid():
                    file_form.save()
                    messages.success(request, 'Termo salvo com sucesso.')

                redirect_url = reverse("subjects", args=(group_id, ))
                return HttpResponseRedirect(redirect_url)
            else:
                messages.error(request, 'Não existem anexos para salvar')
        elif request.POST['action'] == "remove":
                subject_of_group.consent_form.delete()
                subject_of_group.save()
                messages.success(request, 'Anexo removido com sucesso.')

                redirect_url = reverse("subjects", args=(group_id,))
                return HttpResponseRedirect(redirect_url)

    else:
        file_form = FileForm(request.POST or None)

    context = {
        'subject': subject,
        'group': group,
        'file_form': file_form,
        'file_list': subject_of_group.consent_form
    }
    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_experiment')
def component_list(request, experiment_id, template_name="experiment/component_list.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    components = Component.objects.filter(experiment=experiment).order_by("component_type", "identification")

    for component in components:
        component.icon_class = icon_class[component.component_type]

    context = {
        "experiment": experiment,
        "component_list": components,
        "icon_class": icon_class}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def component_change_the_order(request, path_of_the_components, configuration_id, command):
    component_configuration = get_object_or_404(ComponentConfiguration, pk=configuration_id)
    component = get_object_or_404(Component, pk=component_configuration.parent_id)

    component_configuration_to_exchange = ComponentConfiguration.objects.filter(parent_id=component.id)
    if command == "down":
        component_configuration_to_exchange = component_configuration_to_exchange.filter(
            order__gt=component_configuration.order).order_by('order')
    else:
        component_configuration_to_exchange = component_configuration_to_exchange.filter(
            order__lt=component_configuration.order).order_by('-order')
    component_configuration_to_exchange = component_configuration_to_exchange[0]

    configuration_order = component_configuration.order
    configuration_to_exchange_order = component_configuration_to_exchange.order
    last_configuration = ComponentConfiguration.objects.filter(
        parent=component_configuration.parent).order_by('-order').first()

    component_configuration_to_exchange.order = last_configuration.order + 1
    component_configuration_to_exchange.save()

    component_configuration.order = configuration_to_exchange_order
    component_configuration.save()

    component_configuration_to_exchange.order = configuration_order
    component_configuration_to_exchange.save()

    redirect_url = reverse("component_view", args=(path_of_the_components,))

    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('experiment.change_experiment')
def component_create(request, experiment_id, component_type):
    template_name = "experiment/" + component_type + "_component.html"

    experiment = get_object_or_404(Experiment, pk=experiment_id)
    component_form = ComponentForm(request.POST or None)
    questionnaires_list = []
    specific_form = None

    if component_type == 'task':
        specific_form = TaskForm(request.POST or None)
    elif component_type == 'instruction':
        specific_form = InstructionForm(request.POST or None)
    elif component_type == 'stimulus':
        specific_form = StimulusForm(request.POST or None)
    elif component_type == 'pause':
        specific_form = PauseForm(request.POST or None)
    elif component_type == 'questionnaire':
        questionnaires_list = Questionnaires().find_all_active_questionnaires()
    elif component_type == 'block':
        specific_form = BlockForm(request.POST or None, initial={'number_of_mandatory_components': None})

    if request.method == "POST":
        new_specific_component = None

        if component_form.is_valid():
            if component_type == 'questionnaire':
                new_specific_component = Questionnaire()
                new_specific_component.lime_survey_id = request.POST['questionnaire_selected']
            elif specific_form.is_valid():
                new_specific_component = specific_form.save(commit=False)

            if new_specific_component is not None:
                component = component_form.save(commit=False)
                new_specific_component.description = component.description
                new_specific_component.identification = component.identification
                new_specific_component.component_type = component_type
                new_specific_component.experiment = experiment
                new_specific_component.save()

                messages.success(request, 'Componente incluído com sucesso.')

                if component_type == 'block':
                    redirect_url = reverse("component_view", args=(new_specific_component.id,))
                else:
                    redirect_url = reverse("component_list", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "back_cancel_url": "/experiment/" + str(experiment.id) + "/components",
        "component_form": component_form,
        "creating": True,
        "experiment": experiment,
        "questionnaires_list": questionnaires_list,
        "specific_form": specific_form,
    }
    return render(request, template_name, context)


def create_list_of_breadcrumbs(list_of_ids_of_components_and_configurations):
    # Create a list of components or component configurations to be able to show the breadcrumb.
    list_of_breadcrumbs = []

    for idx, id_item in enumerate(list_of_ids_of_components_and_configurations):
        if id_item[0] != "G":
            if id_item[0] == "U":  # If id_item starts with 'U' (from 'use'), it is a configuration.
                cc = get_object_or_404(ComponentConfiguration, pk=id_item[1:])

                if cc.name is not None and cc.name != "":
                    name = cc.name
                else:
                    name = "Uso do componente " + cc.component.identification

                view_name = "component_edit"
            else:
                c = get_object_or_404(Component, pk=id_item)
                name = c.identification
                view_name = "component_view"

            list_of_breadcrumbs.append({
                "name": name, "url":
                reverse(view_name, args=(delimiter.join(list_of_ids_of_components_and_configurations[:idx+1]),))})

    return list_of_breadcrumbs


def create_back_cancel_url(component_type, component_configuration, path_of_the_components,
                           list_of_ids_of_components_and_configurations, experiment, updating):
    if component_type == "block" and component_configuration is None and updating:
        # Return to the screen for viewing a block
        back_cancel_url = "/experiment/component/" + path_of_the_components
    elif len(list_of_ids_of_components_and_configurations) > 1:
        # There is a parent. Remove the current element from the path so that the parent is shown.
        path_without_last = path_of_the_components[:path_of_the_components.rfind("-")]
        last_hyphen_index = path_without_last.rfind("-")

        if last_hyphen_index == -1:
            parent = path_without_last
        else:
            parent = path_without_last[last_hyphen_index + 1:]

        if parent[0] == "G":
            back_cancel_url = "/experiment/group/" + parent[1:]
        else:
            if parent[0] == "U":
                parent = ComponentConfiguration.objects.get(id=parent[1:]).component

            # if parent is block:
            if Block.objects.filter(pk=parent).exists():
                back_cancel_url = "/experiment/component/" + path_without_last
            else:
                back_cancel_url = "/experiment/component/edit/" + path_without_last
    else:
        # Return to the lis of components
        back_cancel_url = "/experiment/" + str(experiment.id) + "/components"

    return back_cancel_url


def access_objects_for_view_and_update(request, path_of_the_components, updating=False):
    list_of_ids_of_components_and_configurations = path_of_the_components.split(delimiter)

    # The last id of the list is the one that we want to show.
    id = list_of_ids_of_components_and_configurations[-1]

    group = None

    if path_of_the_components[0] == "G":
        # The id of the group comes after "G"
        group_id = int(list_of_ids_of_components_and_configurations[0][1:])
        group = get_object_or_404(Group, pk=group_id)

    component_configuration = None
    configuration_form = None

    if id[0] == "U":  # If id starts with 'U' (from 'use'), it is a configuration.
        component_configuration = get_object_or_404(ComponentConfiguration, pk=id[1:])
        configuration_form = ComponentConfigurationForm(request.POST or None, instance=component_configuration)
        component = component_configuration.component
    else:
        component = get_object_or_404(Component, pk=id)

    component_form = ComponentForm(request.POST or None, instance=component)

    list_of_breadcrumbs = create_list_of_breadcrumbs(list_of_ids_of_components_and_configurations)

    experiment = component.experiment

    component_type = component.component_type
    template_name = "experiment/" + component_type + "_component.html"

    if component_configuration is None:
        show_remove = True
    else:
        show_remove = False

    back_cancel_url = create_back_cancel_url(component_type, component_configuration, path_of_the_components,
                                             list_of_ids_of_components_and_configurations, experiment, updating)

    return component, component_configuration, component_form, configuration_form, experiment, component_type,\
        template_name, list_of_ids_of_components_and_configurations, show_remove, list_of_breadcrumbs, group,\
        back_cancel_url


def remove_component_and_related_configurations(component,
                                                list_of_ids_of_components_and_configurations,
                                                path_of_the_components):
    # Before removing anything, we need to know where we should redirect to.

    # If the list has more than one, it has to have more than two, because the last but one element is a component
    # configuration, which has also to be removed from the path.
    if len(list_of_ids_of_components_and_configurations) > 1:
        path_without_last = path_of_the_components[:path_of_the_components.rfind("-")]
        path_without_last_two = path_without_last[:path_without_last.rfind("-")]
        # The parent of the component configuration has to be a block. Then, redirect_url has no "edit" part.
        redirect_url = "/experiment/component/" + path_without_last_two
    else:
        # Return to the list of components
        redirect_url = "/experiment/" + str(component.experiment.id) + "/components"


    # If component is a block, remove the relation with its children
    component_configuration_list = ComponentConfiguration.objects.filter(parent=component)

    for component_configuration_element in component_configuration_list:
        component_configuration_element.delete()

    # Get all the uses of the component that is being removed.
    component_configuration_list = ComponentConfiguration.objects.filter(component=component)

    # Remove the uses.
    for component_configuration_element in component_configuration_list:
        order_of_removed = component_configuration_element.order
        parent_of_removed = component_configuration_element.parent_id
        component_configuration_element.delete()

        configuration_list_of_the_parent = ComponentConfiguration.objects.filter(parent_id=parent_of_removed)

        for siblings in configuration_list_of_the_parent:
            if siblings.order > order_of_removed:
                siblings.order -= 1
                siblings.save()

    component.delete()

    return redirect_url


@login_required
@permission_required('experiment.change_experiment')
def component_view(request, path_of_the_components):
    component, component_configuration, component_form, configuration_form, experiment, component_type, template_name,\
        list_of_ids_of_components_and_configurations, show_remove, list_of_breadcrumbs, group, back_cancel_url =\
        access_objects_for_view_and_update(request, path_of_the_components)

    # It will always be a block because we don't have a view screen for other components.
    block = get_object_or_404(Block, pk=component.id)
    block_form = BlockForm(request.POST or None, instance=block)

    configuration_list = ComponentConfiguration.objects.filter(parent=block)

    if block.type == "sequence":
        configuration_list = configuration_list.order_by('order')
    else:
        configuration_list = configuration_list.order_by('component__component_type',
                                                         'component__identification',
                                                         'name')

    for configuration in configuration_list:
        configuration.component.icon_class = icon_class[configuration.component.component_type]

    # It is not possible to edit fields while viewing a block.
    for form in {block_form, component_form}:
        for field in form.fields:
            form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "save":
            if configuration_form is not None:
                if configuration_form.is_valid():
                    configuration_form.save()
                    messages.success(request, 'Uso do componente atualizado com sucesso.')
                    return HttpResponseRedirect(back_cancel_url)
        elif request.POST['action'] == "remove":
            redirect_url = remove_component_and_related_configurations(component,
                                                                       list_of_ids_of_components_and_configurations,
                                                                       path_of_the_components)
            return HttpResponseRedirect(redirect_url)
        elif request.POST['action'][:7] == "remove-":
            # If action starts with 'remove-' it means that a child is being removed.
            component_configuration_id_to_be_deleted = request.POST['action'].split("-")[-1]
            component_configuration = get_object_or_404(ComponentConfiguration,
                                                        pk=int(component_configuration_id_to_be_deleted))
            component_configuration.delete()
            redirect_url = reverse("component_view", args=(path_of_the_components,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "back_cancel_url": back_cancel_url,
        "component": block,
        "component_configuration": component_configuration,
        "component_form": component_form,
        "configuration_form": configuration_form,
        "configuration_list": configuration_list,
        "experiment": experiment,
        "group": group,
        "icon_class": icon_class,
        "list_of_breadcrumbs": list_of_breadcrumbs,
        "path_of_the_components": path_of_the_components,
        "show_remove": show_remove,
        "specific_form": block_form,
        "type_of_the_parent_block": block.type,
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def component_update(request, path_of_the_components):
    component, component_configuration, component_form, configuration_form, experiment, component_type, template_name,\
        list_of_ids_of_components_and_configurations, show_remove, list_of_breadcrumbs, group, back_cancel_url =\
        access_objects_for_view_and_update(request, path_of_the_components, updating=True)

    questionnaire_id = None
    questionnaire_title = None
    configuration_list = []
    specific_form = None

    if component_type == 'task':
        task = get_object_or_404(Task, pk=component.id)
        specific_form = TaskForm(request.POST or None, instance=task)
    elif component_type == 'instruction':
        instruction = get_object_or_404(Instruction, pk=component.id)
        specific_form = InstructionForm(request.POST or None, instance=instruction)
    elif component_type == 'stimulus':
        stimulus = get_object_or_404(Stimulus, pk=component.id)
        specific_form = StimulusForm(request.POST or None, instance=stimulus)
    elif component_type == 'pause':
        pause = get_object_or_404(Pause, pk=component.id)
        specific_form = PauseForm(request.POST or None, instance=pause)
    elif component_type == 'questionnaire':
        questionnaire = get_object_or_404(Questionnaire, pk=component.id)
        questionnaire_details = Questionnaires().find_questionnaire_by_id(questionnaire.lime_survey_id)

        if questionnaire_details:
            questionnaire_id = questionnaire_details['sid'],
            questionnaire_title = questionnaire_details['surveyls_title']
    elif component_type == 'block':
        block = get_object_or_404(Block, pk=component.id)
        specific_form = BlockForm(request.POST or None, instance=block)

        configuration_list = ComponentConfiguration.objects.filter(parent=block)

        if block.type == "sequence":
            configuration_list = configuration_list.order_by('order')
        else:
            configuration_list = configuration_list.order_by('type, component__identification, name')

        for configuration in configuration_list:
            configuration.component.icon_class = icon_class[configuration.component.component_type]

    if request.method == "POST":
        if request.POST['action'] == "save":
            if configuration_form is None:
                # There is no specific form for a questionnaire.
                if component.component_type == "questionnaire":
                    if component_form.is_valid():
                        # Only save if there was a change.
                        if component_form.has_changed():
                            component_form.save()
                            messages.success(request, 'Componente alterado com sucesso.')
                        else:
                            messages.success(request, 'Não há alterações para salvar.')

                        return HttpResponseRedirect(back_cancel_url)

                elif specific_form.is_valid() and component_form.is_valid():
                    # Only save if there was a change.
                    if component_form.has_changed() or specific_form.has_changed():
                        if component.component_type == 'block':
                            block = specific_form.save(commit=False)

                            # When changing from 'some mandatory' to 'all mandatory', we must set number to null, so
                            # that we know that all components are mandatory.
                            if "number_of_mandatory_components" not in request.POST:
                                block.number_of_mandatory_components = None

                            block.save()
                        else:
                            specific_form.save()

                        component_form.save()
                        messages.success(request, 'Componente alterado com sucesso.')
                    else:
                        messages.success(request, 'Não há alterações para salvar.')

                    return HttpResponseRedirect(back_cancel_url)

            elif configuration_form.is_valid():
                # Only save if there was a change.
                if configuration_form.has_changed():
                    configuration_form.save()
                    messages.success(request, 'Uso do componente atualizado com sucesso.')
                else:
                    messages.success(request, 'Não há alterações para salvar.')

                return HttpResponseRedirect(back_cancel_url)
        elif request.POST['action'] == "remove":
            remove_component_and_related_configurations(component,
                                                        list_of_ids_of_components_and_configurations,
                                                        path_of_the_components)
            return HttpResponseRedirect(back_cancel_url)

    type_of_the_parent_block = None

    # It is not possible to edit the component fields while editing a component configuration.
    if component_configuration is not None:
        if component_type != "questionnaire":
            for field in specific_form.fields:
                specific_form.fields[field].widget.attrs['disabled'] = True

        for field in component_form.fields:
            component_form.fields[field].widget.attrs['disabled'] = True

        type_of_the_parent_block = Block.objects.get(id=component_configuration.parent_id).type


    context = {
        "back_cancel_url": back_cancel_url,
        "component_configuration": component_configuration,
        "component_form": component_form,
        "configuration_form": configuration_form,
        "configuration_list": configuration_list,
        "icon_class": icon_class,
        "experiment": experiment,
        "group": group,
        "list_of_breadcrumbs": list_of_breadcrumbs,
        "path_of_the_components": path_of_the_components,
        "questionnaire_id": questionnaire_id,
        "questionnaire_title": questionnaire_title,
        "show_remove": show_remove,
        "specific_form": specific_form,
        "updating": True,
        "type_of_the_parent_block": type_of_the_parent_block,
    }

    return render(request, template_name, context)


def access_objects_for_add_new_and_reuse(component_type, path_of_the_components):
    template_name = "experiment/" + component_type + "_component.html"
    list_of_ids_of_components_and_configurations = path_of_the_components.split(delimiter)
    list_of_breadcrumbs = create_list_of_breadcrumbs(list_of_ids_of_components_and_configurations)

    block = None
    group = None

    if len(list_of_ids_of_components_and_configurations) > 1 or path_of_the_components[0] != "G":
        # The last id of the list is the block where the new component will be added.
        block_id = list_of_ids_of_components_and_configurations[-1]
        block = get_object_or_404(Block, pk=block_id)
        experiment = block.experiment
    if path_of_the_components[0] == "G":
        # The id of the group comes after "G"
        group_id = int(list_of_ids_of_components_and_configurations[0][1:])
        group = get_object_or_404(Group, pk=group_id)
        experiment = group.experiment

    existing_component_list = Component.objects.filter(experiment=experiment, component_type=component_type)
    specific_form = None

    return existing_component_list, experiment, group, list_of_breadcrumbs, block, template_name, specific_form, \
           list_of_ids_of_components_and_configurations


@login_required
@permission_required('experiment.change_experiment')
def component_add_new(request, path_of_the_components, component_type):
    existing_component_list, experiment, group, list_of_breadcrumbs, block, template_name,\
        specific_form, list_of_ids_of_components_and_configurations = \
        access_objects_for_add_new_and_reuse(component_type, path_of_the_components)

    component_form = ComponentForm(request.POST or None)
    questionnaires_list = []

    if component_type == 'task':
        specific_form = TaskForm(request.POST or None)
    elif component_type == 'instruction':
        specific_form = InstructionForm(request.POST or None)
    elif component_type == 'stimulus':
        specific_form = StimulusForm(request.POST or None)
    elif component_type == 'pause':
        specific_form = PauseForm(request.POST or None)
    elif component_type == 'questionnaire':
        questionnaires_list = Questionnaires().find_all_active_questionnaires()
    elif component_type == 'block':
        specific_form = BlockForm(request.POST or None, initial={'number_of_mandatory_components': None})

    if request.method == "POST":
        new_specific_component = None

        if component_type == 'questionnaire':
            new_specific_component = Questionnaire()
            new_specific_component.lime_survey_id = request.POST['questionnaire_selected']
        elif specific_form.is_valid():
            new_specific_component = specific_form.save(commit=False)

        if component_form.is_valid():
            component = component_form.save(commit=False)
            new_specific_component.description = component.description
            new_specific_component.identification = component.identification
            new_specific_component.component_type = component_type
            new_specific_component.experiment = experiment
            new_specific_component.save()

            if group is None or len(list_of_ids_of_components_and_configurations) > 1:
                new_configuration = ComponentConfiguration()
                new_configuration.component = new_specific_component
                new_configuration.parent = block

                if block.type == 'sequence':
                    new_configuration.random_position = False

                new_configuration.save()

                messages.success(request, 'Componente incluído com sucesso.')

                redirect_url = reverse("component_edit",
                                       args=(path_of_the_components + "-U" + str(new_configuration.id), ))
            else:
                group.experimental_protocol = new_specific_component
                group.save()

                messages.success(request, 'Protocolo experimental incluído com sucesso.')

                redirect_url = reverse("component_view",
                                       args=(path_of_the_components + "-" + str(new_specific_component.id), ))
            return HttpResponseRedirect(redirect_url)

    context = {
        "back_cancel_url": "/experiment/component/" + path_of_the_components,
        "block": block,
        "can_reuse": True,
        "component_form": component_form,
        "creating": True,
        "existing_component_list": existing_component_list,
        "experiment": experiment,
        "group": group,
        "list_of_breadcrumbs": list_of_breadcrumbs,
        "questionnaires_list": questionnaires_list,
        "path_of_the_components": path_of_the_components,
        "specific_form": specific_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def component_reuse(request, path_of_the_components, component_id):
    component_to_add = get_object_or_404(Component, pk=component_id)
    component_type = component_to_add.component_type

    existing_component_list, experiment, group, list_of_breadcrumbs, block, template_name,\
        specific_form, list_of_ids_of_components_and_configurations = \
        access_objects_for_add_new_and_reuse(component_type, path_of_the_components)

    component_form = ComponentForm(request.POST or None, instance=component_to_add)

    questionnaire_id = None
    questionnaire_title = None

    if component_type == 'task':
        task = get_object_or_404(Task, pk=component_to_add.id)
        specific_form = TaskForm(request.POST or None, instance=task)
    elif component_type == 'instruction':
        instruction = get_object_or_404(Instruction, pk=component_to_add.id)
        specific_form = InstructionForm(request.POST or None, instance=instruction)
    elif component_type == 'stimulus':
        stimulus = get_object_or_404(Stimulus, pk=component_to_add.id)
        specific_form = StimulusForm(request.POST or None, instance=stimulus)
    elif component_type == 'pause':
        pause = get_object_or_404(Pause, pk=component_to_add.id)
        specific_form = PauseForm(request.POST or None, instance=pause)
    elif component_type == 'questionnaire':
        questionnaire = get_object_or_404(Questionnaire, pk=component_to_add.id)
        questionnaire_details = Questionnaires().find_questionnaire_by_id(questionnaire.lime_survey_id)

        if questionnaire_details:
            questionnaire_id = questionnaire_details['sid'],
            questionnaire_title = questionnaire_details['surveyls_title']
    elif component_type == 'block':
        sub_block = get_object_or_404(Block, pk=component_id)
        specific_form = BlockForm(request.POST or None, instance=sub_block)

    if component_type == 'questionnaire':
        for field in component_form.fields:
            component_form.fields[field].widget.attrs['disabled'] = True
    else:
        for form_used in {specific_form, component_form}:
            for field in form_used.fields:
                form_used.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if len(list_of_ids_of_components_and_configurations) == 1 and path_of_the_components[0] == "G":
            # If this is a reuse for creating the root of a group's experimental protocol, no component_configuration
            # has to be created.
            group = Group.objects.get(id=path_of_the_components[1:])
            group.experimental_protocol = component_to_add
            group.save()

            redirect_url = reverse("component_view",
                                   args=(path_of_the_components + "-" + str(component_to_add.id), ))
        else:
            new_configuration = ComponentConfiguration()
            new_configuration.component = component_to_add
            new_configuration.parent = block

            if block.type == 'sequence':
                new_configuration.random_position = False

            new_configuration.save()

            redirect_url = reverse("component_edit",
                                   args=(path_of_the_components + "-U" + str(new_configuration.id), ))

        messages.success(request, 'Componente incluído com sucesso.')
        return HttpResponseRedirect(redirect_url)

    context = {
        "back_cancel_url": "/experiment/component/" + path_of_the_components,
        "block": block,
        "component_form": component_form,
        "creating": True, # So that the "Use" button is shown.
        "existing_component_list": existing_component_list,
        "experiment": experiment,
        "group": group,
        "list_of_breadcrumbs": list_of_breadcrumbs,
        "path_of_the_components": path_of_the_components,
        "questionnaire_id": questionnaire_id,
        "questionnaire_title": questionnaire_title,
        "reusing": True,
        "specific_form": specific_form,
    }

    return render(request, template_name, context)
