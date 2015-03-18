# coding=utf-8
from functools import partial
import re
import datetime

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
    Pause, Sequence, Instruction, ClassificationOfDiseases, ResearchProject, Keyword
from experiment.forms import ExperimentForm, QuestionnaireConfigurationForm, QuestionnaireResponseForm, \
    FileForm, GroupForm, TaskForm, InstructionForm, ComponentForm, StimulusForm, PauseForm, SequenceForm, \
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
    u'sequence': 'glyphicon glyphicon-list',
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

                redirect_url = reverse("research_project_edit", args=(research_project_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "research_project_form": research_project_form,
        "creating": True}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_researchproject')
def research_project_update(request, research_project_id, template_name="experiment/research_project_register.html"):

    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    if research_project:

        research_project_form = ResearchProjectForm(request.POST or None, instance=research_project)

        if request.method == "POST":

            if request.POST['action'] == "save":

                if research_project_form.is_valid():

                    if research_project_form.has_changed():
                        research_project_form.save()
                        messages.success(request, 'Estudo atualizado com sucesso.')

            else:
                if request.POST['action'] == "remove":
                    try:
                        for keyword in research_project.keywords.all():
                            manage_keywords(keyword, ResearchProject.objects.exclude(id=research_project.id))
                        research_project.delete()
                    except ProtectedError:
                        messages.error(request, "Erro ao tentar excluir o estudo.")
                        redirect_url = reverse("research_project_edit", args=(research_project.id,))
                        return HttpResponseRedirect(redirect_url)
                    return redirect('research_project_list')

        context = {
            "research_project_form": research_project_form,
            "creating": False,
            "research_project": research_project,
            "keywords": research_project.keywords.all()}

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

    redirect_url = reverse("research_project_edit", args=(research_project_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('experiment.change_researchproject')
def keyword_add_ajax(request, research_project_id, keyword_id):

    research_project = get_object_or_404(ResearchProject, pk=research_project_id)
    keyword = get_object_or_404(Keyword, pk=keyword_id)
    research_project.keywords.add(keyword)

    redirect_url = reverse("research_project_edit", args=(research_project_id,))
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

    redirect_url = reverse("research_project_edit", args=(research_project_id,))
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

                redirect_url = reverse("experiment_edit", args=(experiment_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "experiment_form": experiment_form,
        "creating": True}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def experiment_update(request, experiment_id, template_name="experiment/experiment_register.html"):

    experiment = get_object_or_404(Experiment, pk=experiment_id)

    if experiment:

        group_list = Group.objects.filter(experiment=experiment)

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
                        messages.error(request, "Não foi possível excluir o experimento, pois há grupos associados")
                        redirect_url = reverse("experiment_edit", args=(experiment.id,))
                        return HttpResponseRedirect(redirect_url)
                    return redirect('experiment_list')

        context = {
            "experiment_form": experiment_form,
            "creating": False,
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

                redirect_url = reverse("group_edit", args=(group_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "group_form": group_form,
        "creating": True,
        "updating": False,
        "experiment": experiment}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_experiment')
def group_update(request, group_id, template_name="experiment/group_register.html"):

    group = get_object_or_404(Group, pk=group_id)
    experiment = get_object_or_404(Experiment, pk=group.experiment_id)

    if group:

        group_form = GroupForm(request.POST or None, instance=group)

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

                    redirect_url = reverse("group_edit", args=(group_id,))
                    return HttpResponseRedirect(redirect_url)

            else:
                if request.POST['action'] == "remove":
                    try:
                        group.delete()
                    except ProtectedError:
                        messages.error(request, "Não foi possível excluir o grupo, pois há dependências.")
                        redirect_url = reverse("group_edit", args=(group.id,))
                        return HttpResponseRedirect(redirect_url)
                    redirect_url = reverse("experiment_edit", args=(experiment.id,))
                    return HttpResponseRedirect(redirect_url)

        context = {
            "classification_of_diseases_list": group.classification_of_diseases.all(),
            "group_id": group_id,
            "group_form": group_form,
            "creating": False,
            "questionnaires_configuration_list": list_of_questionnaires_configuration,
            "experiment": experiment,
            "group": group,
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
    redirect_url = reverse("group_edit", args=(group_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('experiment.add_experiment')
def classification_of_diseases_remove(request, group_id, classification_of_diseases_id):
    """Remove group disease"""
    group = get_object_or_404(Group, pk=group_id)
    classification_of_diseases = get_object_or_404(ClassificationOfDiseases, pk=classification_of_diseases_id)
    classification_of_diseases.group_set.remove(group)
    redirect_url = reverse("group_edit", args=(group_id,))
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

                redirect_url = reverse("group_edit", args=(group_id,))
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

                redirect_url = reverse("group_edit", args=(group.id,))
                return HttpResponseRedirect(redirect_url)
        else:
            if request.POST['action'] == "remove":
                try:
                    questionnaire_configuration.delete()
                except ProtectedError:
                    messages.error(request, "Não foi possível excluir o questionário, pois há respostas associadas")
                    redirect_url = reverse("questionnaire_edit", args=(questionnaire_configuration_id,))
                    return HttpResponseRedirect(redirect_url)

                redirect_url = reverse("group_edit", args=(group.id,))
                return HttpResponseRedirect(redirect_url)



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
    survey_admin = surveys.get_survey_properties(questionnaire_config.lime_survey_id, 'admin')
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
        "survey_admin": survey_admin,
        "survey_active": survey_active,
        "questionnaire_responsible": request.user.get_full_name(),
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
    survey_admin = surveys.get_survey_properties(questionnaire_configuration.lime_survey_id, 'admin')
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

        else:
            if request.POST['action'] == "remove":
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
        "survey_admin": survey_admin,
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
                question_properties = surveys.get_question_properties(question)
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
                    if ('{int' not in properties['question']) and ('{(' not in properties['question'])\
                            and ('{if' not in properties['question']) and ('{pont' not in properties['question']):
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
                                'answer_options': properties['answeroptions'],
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
                            if responses_list[1][index]:
                                answer = datetime.datetime.strptime(responses_list[1][index], '%Y-%m-%d %H:%M:%S')
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
                patient_list = Patient.objects.filter(name__icontains=search_text).exclude(removed=True).order_by('name')
            else:
                patient_list = Patient.objects.filter(cpf__icontains=search_text).exclude(removed=True).order_by('name')

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
        else:
            if request.POST['action'] == "remove":
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
    components = Component.objects.filter(experiment=experiment).order_by("identification")

    for component in components:
        component.icon_class = icon_class[component.component_type]

    context = {
        "experiment": experiment,
        "component_list": components,
        "icon_class": icon_class}
    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def component_configuration_change_the_order(request, path_of_the_sub_components, command):

    list_of_component_configuration_id = path_of_the_sub_components.split(delimiter)
    component_configuration_id = list_of_component_configuration_id[-1]

    component_configuration = get_object_or_404(ComponentConfiguration, pk=component_configuration_id)
    component = get_object_or_404(Component, pk=component_configuration.parent_id)

    component_configuration_to_exchange = ComponentConfiguration.objects.filter(parent_id=component.id)
    if command == "down":
        component_configuration_to_exchange = \
            component_configuration_to_exchange.filter(order__gt=component_configuration.order).order_by('order')
    else:
        component_configuration_to_exchange = \
            component_configuration_to_exchange.filter(order__lt=component_configuration.order).order_by('-order')
    component_configuration_to_exchange = component_configuration_to_exchange[0]

    configuration_order = component_configuration.order
    configuration_to_exchange_order = component_configuration_to_exchange.order
    last_configuration = \
        ComponentConfiguration.objects.filter(parent=component_configuration.parent).order_by('-order').first()

    component_configuration_to_exchange.order = last_configuration.order + 1
    component_configuration_to_exchange.save()

    component_configuration.order = configuration_to_exchange_order
    component_configuration.save()

    component_configuration_to_exchange.order = configuration_order
    component_configuration_to_exchange.save()

    if len(list_of_component_configuration_id) > 2:
        redirect_url = \
            reverse("component_configuration_update", args=(delimiter.join(list_of_component_configuration_id[:-1]),))
    else:
        redirect_url = \
            reverse("component_edit", args=(component.id,))

    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required('experiment.change_experiment')
def component_create(request, experiment_id, component_type):

    template_name = "experiment/" + component_type + "_component.html"

    experiment = get_object_or_404(Experiment, pk=experiment_id)
    component_form = ComponentForm(request.POST or None)
    questionnaires_list = []
    form = None

    if component_type == 'task':
        form = TaskForm(request.POST or None)
    else:
        if component_type == 'instruction':
            form = InstructionForm(request.POST or None)
        else:
            if component_type == 'stimulus':
                form = StimulusForm(request.POST or None)
            else:
                if component_type == 'pause':
                    form = PauseForm(request.POST or None)
                else:
                    if component_type == 'questionnaire':
                        questionnaires_list = Questionnaires().find_all_active_questionnaires()
                    else:
                        if component_type == 'sequence':
                            form = SequenceForm(request.POST or None,
                                                initial={'number_of_mandatory_components': None})

    if request.method == "POST":
        new_component = None
        if component_type == 'questionnaire':
            new_component = Questionnaire()
            new_component.lime_survey_id = request.POST['questionnaire_selected']
        else:
            if form.is_valid():
                new_component = form.save(commit=False)
                if component_type == 'sequence':
                    if "number_of_mandatory_components" in request.POST:
                        new_component.number_of_mandatory_components = request.POST['number_of_mandatory_components']
                    if "has_random_components" in request.POST:
                        new_component.has_random_components = True
                    else:
                        new_component.has_random_components = False

        if component_form.is_valid():
            component = component_form.save(commit=False)
            new_component.description = component.description
            new_component.identification = component.identification
            new_component.component_type = component_type
            new_component.experiment = experiment
            new_component.save()

            messages.success(request, 'Componente incluído com sucesso.')

            if component_type == 'sequence':
                redirect_url = reverse("component_edit", args=(new_component.id,))
            else:
                redirect_url = reverse("component_list", args=(experiment_id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "experimental_protocol": False,
        "creating_workflow": False,
        "form": form,
        "experiment": experiment,
        "component_form": component_form,
        "creating": True,
        "updating": False,
        "questionnaires_list": questionnaires_list,
    }
    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def component_update(request, component_id):

    component = get_object_or_404(Component, pk=component_id)

    template_name = "experiment/" + component.component_type + "_component.html"

    experiment = get_object_or_404(Experiment, pk=component.experiment.id)

    questionnaire_id = None
    questionnaire_title = None
    component_form = None
    form = None
    sequence = None
    configuration_list = []

    if component:
        component_form = ComponentForm(request.POST or None, instance=component)
        form = None

        if component.component_type == 'task':
            task = get_object_or_404(Task, pk=component.id)
            form = TaskForm(request.POST or None, instance=task)
        else:
            if component.component_type == 'instruction':
                instruction = get_object_or_404(Instruction, pk=component.id)
                form = InstructionForm(request.POST or None, instance=instruction)
            else:
                if component.component_type == 'stimulus':
                    stimulus = get_object_or_404(Stimulus, pk=component.id)
                    form = StimulusForm(request.POST or None, instance=stimulus)
                else:
                    if component.component_type == 'pause':
                        pause = get_object_or_404(Pause, pk=component.id)
                        form = PauseForm(request.POST or None, instance=pause)
                    else:
                        if component.component_type == 'questionnaire':
                            questionnaire = get_object_or_404(Questionnaire, pk=component.id)
                            questionnaire_details = Questionnaires().\
                                find_questionnaire_by_id(questionnaire.lime_survey_id)
                            if questionnaire_details:
                                questionnaire_id = questionnaire_details['sid'],
                                questionnaire_title = questionnaire_details['surveyls_title']
                        else:
                            if component.component_type == 'sequence':
                                sequence = get_object_or_404(Sequence, pk=component_id)
                                form = SequenceForm(request.POST or None, instance=sequence)
                                configuration_list = ComponentConfiguration.objects.filter(parent=sequence)\
                                    .order_by('order')

                                for configuration in configuration_list:
                                    configuration.component.icon_class = \
                                        icon_class[configuration.component.component_type]

    if request.method == "POST":
        if request.POST['action'] == "save":
            if component.component_type == "questionnaire" or form.is_valid():

                if component.component_type != "questionnaire":
                    form.save()

                if component_form.is_valid():
                    component_form.save()

                    messages.success(request, 'Componente alterado com sucesso.')

                    if component.component_type == 'sequence':
                        redirect_url = reverse("component_edit", args=(sequence.id,))
                    else:
                        redirect_url = reverse("component_list", args=(experiment.id,))
                    return HttpResponseRedirect(redirect_url)
        else:
            if request.POST['action'] == "remove":
                dependent_components = ComponentConfiguration.objects.filter(parent=component)
                if dependent_components:
                    messages.error(request,
                                   'Componente não pode ser removido pois contém outros componentes dependentes.')
                    redirect_url = reverse("component_edit", args=(component.id,))
                else:
                    component.delete()
                    redirect_url = reverse("component_list", args=(experiment.id,))
                return HttpResponseRedirect(redirect_url)
            else:
                if request.POST['action'][:7] == "remove-":
                    component_configuration_id_to_be_deleted = request.POST['action'].split("-")[-1]
                    component_configutation = get_object_or_404(
                        ComponentConfiguration, pk=int(component_configuration_id_to_be_deleted))
                    component_configutation.delete()
                    redirect_url = reverse("component_edit", args=(sequence.id,))
                    return HttpResponseRedirect(redirect_url)

    context = {
        "experimental_protocol": False,
        "creating_workflow": False,
        "form": form,
        "experiment": experiment,
        "component_form": component_form,
        "creating": False,
        "updating": True,
        "sequence": sequence,
        "questionnaire_id": questionnaire_id,
        "questionnaire_title": questionnaire_title,
        "configuration_list": configuration_list,
        "icon_class": icon_class,
    }
    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def component_configuration_add_new_component(request, path_of_the_sub_components, component_type):

    template_name = "experiment/" + component_type + "_component.html"

    list_of_identifiers = path_of_the_sub_components.split(delimiter)

    if len(list_of_identifiers) == 1:
        component_id = int(list_of_identifiers[0])
    else:
        component_id = get_object_or_404(ComponentConfiguration, pk=int(list_of_identifiers[-1])).component.id

    sequence = get_object_or_404(Sequence, pk=component_id)
    experiment = get_object_or_404(Experiment, pk=sequence.experiment_id)

    component_form = ComponentForm(request.POST or None)
    configuration_form = ComponentConfigurationForm(request.POST or None,
                                                    initial={'number_of_repetitions': 1,
                                                             'interval_between_repetitions_value': None})
    questionnaires_list = []
    form = None

    existing_component_list = Component.objects.filter(experiment=experiment, component_type=component_type)

    if component_type == 'task':
        form = TaskForm(request.POST or None)
    else:
        if component_type == 'instruction':
            form = InstructionForm(request.POST or None)
        else:
            if component_type == 'stimulus':
                form = StimulusForm(request.POST or None)
            else:
                if component_type == 'pause':
                    form = PauseForm(request.POST or None)
                else:
                    if component_type == 'questionnaire':
                        questionnaires_list = Questionnaires().find_all_active_questionnaires()
                    else:
                        if component_type == 'sequence':
                            form = SequenceForm(request.POST or None,
                                                initial={'number_of_mandatory_components': None})

    if request.method == "POST":

        new_component = None

        if component_type == 'questionnaire':
            new_component = Questionnaire()
            new_component.lime_survey_id = request.POST['questionnaire_selected']
        else:
            if form.is_valid():

                new_component = form.save(commit=False)

                if component_type == 'sequence':

                    if "number_of_mandatory_components" in request.POST:
                        new_component.number_of_mandatory_components = request.POST['number_of_mandatory_components']
                    if "has_random_components" in request.POST:
                        new_component.has_random_components = True
                    else:
                        new_component.has_random_components = False

        if component_form.is_valid() and configuration_form.is_valid():

            component = component_form.save(commit=False)

            new_component.description = component.description
            new_component.identification = component.identification
            new_component.component_type = component_type
            new_component.experiment = experiment
            new_component.save()

            configuration = configuration_form.save(commit=False)
            configuration.component = new_component
            configuration.parent = sequence

            if "number_of_fills" in request.POST:
                configuration.number_of_repetitions = request.POST['number_of_repetitions']

            if "interval_between_fills_value" in request.POST:
                configuration.interval_between_repetitions_value = request.POST['interval_between_repetitions_value']

            if "interval_between_fills_unit" in request.POST:
                configuration.interval_between_repetitions_unit = \
                    get_object_or_404(TimeUnit, pk=request.POST['interval_between_repetitions_unit'])

            configuration.save()

            messages.success(request, 'Componente incluído com sucesso.')

            if component_type == "sequence":
                redirect_url = reverse("component_configuration_update",
                                       args=(path_of_the_sub_components + "-" + str(configuration.id), ))
            else:
                if len(list_of_identifiers) == 1:
                    redirect_url = reverse("component_edit", args=(component_id,))
                else:
                    redirect_url = reverse("component_configuration_update", args=(path_of_the_sub_components,))

            return HttpResponseRedirect(redirect_url)

    context = {
        "experimental_protocol": False,
        "creating_workflow": True,
        "form": form,
        "experiment": experiment,
        "component_form": component_form,
        "configuration_form": configuration_form,
        "creating": True,
        "updating": False,
        "questionnaires_list": questionnaires_list,
        "existing_component_list": existing_component_list,
        "sequence": sequence,
        "reusing_component": False,
        "path_of_the_sub_components": path_of_the_sub_components,
    }
    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def component_configuration_reuse_component(request, path_of_the_sub_components, component_id):

    component = get_object_or_404(Component, pk=component_id)
    component_type = component.component_type

    template_name = "experiment/" + component_type + "_component.html"

    list_of_identifiers = path_of_the_sub_components.split(delimiter)

    if len(list_of_identifiers) == 1:
        component_id = int(list_of_identifiers[0])
    else:
        component_id = get_object_or_404(ComponentConfiguration, pk=int(list_of_identifiers[-1])).component.id

    experiment = get_object_or_404(Experiment, pk=component.experiment.id)
    sequence = get_object_or_404(Sequence, pk=component_id)

    component_form = ComponentForm(request.POST or None, instance=component)
    configuration_form = ComponentConfigurationForm(request.POST or None,
                                                    initial={'number_of_repetitions': 1,
                                                             'interval_between_repetitions_value': None})

    existing_component_list = Component.objects.filter(component_type=component_type, experiment=experiment)

    questionnaire_id = None
    questionnaire_title = None

    form = None

    if component_type == 'task':
        task = get_object_or_404(Task, pk=component.id)
        form = TaskForm(request.POST or None, instance=task)
    else:
        if component_type == 'instruction':
            instruction = get_object_or_404(Instruction, pk=component.id)
            form = InstructionForm(request.POST or None, instance=instruction)
        else:
            if component_type == 'stimulus':
                stimulus = get_object_or_404(Stimulus, pk=component.id)
                form = StimulusForm(request.POST or None, instance=stimulus)
            else:
                if component_type == 'pause':
                    pause = get_object_or_404(Pause, pk=component.id)
                    form = PauseForm(request.POST or None, instance=pause)
                else:
                    if component_type == 'questionnaire':
                        questionnaire = get_object_or_404(Questionnaire, pk=component.id)
                        questionnaire_details = Questionnaires().\
                            find_questionnaire_by_id(questionnaire.lime_survey_id)
                        if questionnaire_details:
                            questionnaire_id = questionnaire_details['sid'],
                            questionnaire_title = questionnaire_details['surveyls_title']
                    else:
                        if component_type == 'sequence':
                            sub_sequence = get_object_or_404(Sequence, pk=component_id)
                            form = SequenceForm(request.POST or None, instance=sub_sequence)

    if component_type == 'questionnaire':
        for field in component_form.fields:
            component_form.fields[field].widget.attrs['disabled'] = True
    else:
        for form_used in {form, component_form}:
            for field in form_used.fields:
                form_used.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":

        if configuration_form.is_valid():

            configuration = configuration_form.save(commit=False)
            configuration.component = component
            configuration.parent = sequence
            if "number_of_fills" in request.POST:
                configuration.number_of_repetitions = request.POST['number_of_repetitions']
            if "interval_between_fills_value" in request.POST:
                configuration.interval_between_repetitions_value = request.POST['interval_between_repetitions_value']

            if "interval_between_fills_unit" in request.POST:
                configuration.interval_between_repetitions_unit = \
                    get_object_or_404(TimeUnit, pk=request.POST['interval_between_repetitions_unit'])

            configuration.save()

            messages.success(request, 'Componente incluído com sucesso.')

            if component_type == "sequence":
                redirect_url = reverse("component_configuration_update",
                                       args=(path_of_the_sub_components + "-" + str(configuration.id),))
            else:
                if len(list_of_identifiers) == 1:
                    redirect_url = reverse("component_edit", args=(component_id,))
                else:
                    redirect_url = reverse("component_configuration_update", args=(path_of_the_sub_components,))

            return HttpResponseRedirect(redirect_url)

    context = {
        "experimental_protocol": False,
        "creating_workflow": True,
        "form": form,
        "experiment": experiment,
        "component_form": component_form,
        "configuration_form": configuration_form,
        "creating": True,
        "updating": False,
        "existing_component_list": existing_component_list,
        "sequence": sequence,
        "questionnaire_id": questionnaire_id,
        "questionnaire_title": questionnaire_title,
        "reusing_component": True,
        "path_of_the_sub_components": path_of_the_sub_components,
    }
    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def component_configuration_update(request, path_of_the_sub_components):

    list_of_component_configuration_id = path_of_the_sub_components.split(delimiter)

    component_configuration_id = list_of_component_configuration_id[-1]
    component_configuration = get_object_or_404(ComponentConfiguration, pk=component_configuration_id)

    previous_component_configuration = \
        delimiter.join(list_of_component_configuration_id[:-1]) if len(list_of_component_configuration_id) > 2 else None

    component = get_object_or_404(Component, pk=component_configuration.component.id)
    experiment = get_object_or_404(Experiment, pk=component.experiment.id)

    component_type = component.component_type

    template_name = "experiment/" + component_type + "_component.html"

    questionnaire_id = None
    questionnaire_title = None
    component_form = None
    form = None
    sequence = None

    configuration_form = ComponentConfigurationForm(request.POST or None, instance=component_configuration)

    configuration_list = []

    if component:
        component_form = ComponentForm(request.POST or None, instance=component)
        form = None
        if component_type == 'task':
            task = get_object_or_404(Task, pk=component.id)
            form = TaskForm(request.POST or None, instance=task)
        else:
            if component_type == 'instruction':
                instruction = get_object_or_404(Instruction, pk=component.id)
                form = InstructionForm(request.POST or None, instance=instruction)
            else:
                if component_type == 'stimulus':
                    stimulus = get_object_or_404(Stimulus, pk=component.id)
                    form = StimulusForm(request.POST or None, instance=stimulus)
                else:
                    if component_type == 'pause':
                        pause = get_object_or_404(Pause, pk=component.id)
                        form = PauseForm(request.POST or None, instance=pause)
                    else:
                        if component_type == 'questionnaire':
                            questionnaire = get_object_or_404(Questionnaire, pk=component.id)
                            questionnaire_details = Questionnaires().\
                                find_questionnaire_by_id(questionnaire.lime_survey_id)
                            if questionnaire_details:
                                questionnaire_id = questionnaire_details['sid'],
                                questionnaire_title = questionnaire_details['surveyls_title']
                        else:
                            if component_type == 'sequence':
                                sequence = get_object_or_404(Sequence, pk=component.id)
                                form = SequenceForm(request.POST or None, instance=sequence)
                                configuration_list = ComponentConfiguration.objects.filter(parent=sequence)\
                                    .order_by('order')

                                for configuration in configuration_list:
                                    configuration.component.icon_class = \
                                        icon_class[configuration.component.component_type]

    if request.method == "POST":
        if request.POST['action'] == "save":

            if configuration_form.is_valid():

                configuration = configuration_form.save(commit=False)
                configuration.save()

                messages.success(request, 'Componente atualizado com sucesso.')

                redirect_url = reverse("component_edit", args=(component_configuration.parent.id,))
                return HttpResponseRedirect(redirect_url)

        else:
            if request.POST['action'] == "remove":
                component_configuration_list = ComponentConfiguration.objects.filter(
                    parent_id=component_configuration.parent_id).order_by('order')
                for component_configuration_element in component_configuration_list:
                    if component_configuration_element.order > component_configuration.order:
                        component_configuration_element.order -= 1
                        component_configuration_element.save()
                component.delete()
                redirect_url = reverse("component_list", args=(experiment.id,))
                return HttpResponseRedirect(redirect_url)
            else:
                if request.POST['action'][:7] == "remove-":
                    component_configuration_id_to_be_deleted = request.POST['action'].split("-")[-1]
                    component_configutation = get_object_or_404(
                        ComponentConfiguration, pk=int(component_configuration_id_to_be_deleted))
                    component_configutation.delete()
                    redirect_url = reverse("component_configuration_update", args=(path_of_the_sub_components,))
                    return HttpResponseRedirect(redirect_url)

    if component_type == 'questionnaire':
        for field in component_form.fields:
            component_form.fields[field].widget.attrs['disabled'] = True
    else:
        for form_used in {form, component_form}:
            for field in form_used.fields:
                form_used.fields[field].widget.attrs['disabled'] = True

    context = {
        "experimental_protocol": False,
        "creating_workflow": True,
        "form": form,
        "experiment": experiment,
        "component_form": component_form,
        "configuration_form": configuration_form,
        "creating": False,
        "updating": True,
        "existing_component_list": [],
        "sequence": sequence,
        "questionnaire_id": questionnaire_id,
        "questionnaire_title": questionnaire_title,
        "reusing_component": True,
        "sequence_id": component_configuration.parent_id,
        "configuration_list": configuration_list,
        "icon_class": icon_class,
        "path_of_the_sub_components": path_of_the_sub_components,
        "previous_component_configuration": previous_component_configuration
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def experimental_protocol_create(request, group_id):

    component_type = "sequence"
    template_name = "experiment/" + component_type + "_component.html"

    group = get_object_or_404(Group, pk=group_id)
    experiment = group.experiment
    sequence = None
    path_of_the_sub_components = ""

    component_form = ComponentForm(request.POST or None)
    configuration_form = ComponentConfigurationForm(request.POST or None,
                                                    initial={'number_of_repetitions': 1,
                                                             'interval_between_repetitions_value': None})
    questionnaires_list = []

    existing_component_list = Component.objects.filter(experiment=experiment, component_type=component_type)

    form = SequenceForm(request.POST or None,
                        initial={'number_of_mandatory_components': None})

    if request.method == "POST":

        new_component = None

        if form.is_valid():

            new_component = form.save(commit=False)

            if "number_of_mandatory_components" in request.POST:
                new_component.number_of_mandatory_components = request.POST['number_of_mandatory_components']
            if "has_random_components" in request.POST:
                new_component.has_random_components = True
            else:
                new_component.has_random_components = False

        if component_form.is_valid() and configuration_form.is_valid():

            component = component_form.save(commit=False)

            new_component.description = component.description
            new_component.identification = component.identification
            new_component.component_type = component_type
            new_component.experiment = experiment
            new_component.save()

            configuration = configuration_form.save(commit=False)
            configuration.component = new_component
            configuration.parent = None

            if "number_of_fills" in request.POST:
                configuration.number_of_repetitions = request.POST['number_of_repetitions']

            if "interval_between_fills_value" in request.POST:
                configuration.interval_between_repetitions_value = request.POST['interval_between_repetitions_value']

            if "interval_between_fills_unit" in request.POST:
                configuration.interval_between_repetitions_unit = \
                    get_object_or_404(TimeUnit, pk=request.POST['interval_between_repetitions_unit'])

            configuration.save()

            group.experimental_protocol = configuration
            group.save()

            messages.success(request, 'Protocolo experimental incluído com sucesso.')

            redirect_url = reverse("experimental_protocol_update", args=(group_id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "experimental_protocol": True,
        "creating_workflow": True,
        "form": form,
        "experiment": experiment,
        "component_form": component_form,
        "configuration_form": configuration_form,
        "creating": True,
        "updating": False,
        "questionnaires_list": questionnaires_list,
        "existing_component_list": existing_component_list,
        "sequence": sequence,
        "reusing_component": False,
        "path_of_the_sub_components": path_of_the_sub_components,
    }
    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def experimental_protocol_update(request, group_id):

    group = get_object_or_404(Group, pk=group_id)
    component_configuration = group.experimental_protocol
    experiment = group.experiment

    component_type = component_configuration.component.component_type
    template_name = "experiment/" + component_type + "_component.html"

    questionnaire_id = None
    questionnaire_title = None

    component = get_object_or_404(Component, pk=component_configuration.component.id)
    component_form = ComponentForm(request.POST or None, instance=component)

    configuration_form = ComponentConfigurationForm(request.POST or None, instance=component_configuration)

    sequence = get_object_or_404(Sequence, pk=component_configuration.component.id)
    form = SequenceForm(request.POST or None, instance=sequence)

    existing_component_list = Component.objects.filter(experiment=experiment, component_type=component_type)
    configuration_list = ComponentConfiguration.objects.filter(parent=sequence).order_by('order')

    for configuration in configuration_list:
        configuration.component.icon_class = icon_class[configuration.component.component_type]

    if request.method == "POST":

        if request.POST['action'] == "save":

            if configuration_form.is_valid():

                # important: form.save() must be performed before component_form.save()
                form.save()
                component_form.save()

                configuration_form.save()

                messages.success(request, 'Componente atualizado com sucesso.')

                redirect_url = reverse("experimental_protocol_update", args=(group_id,))
                return HttpResponseRedirect(redirect_url)

    # for form_used in {form, component_form}:
    #     for field in form_used.fields:
    #         form_used.fields[field].widget.attrs['disabled'] = True

    context = {
        "experimental_protocol": True,
        "group": group,
        "creating_workflow": True,
        "form": form,
        "experiment": experiment,
        "component_form": component_form,
        "configuration_form": configuration_form,
        "creating": False,
        "updating": True,
        "existing_component_list": existing_component_list,
        "sequence": sequence,
        "questionnaire_id": questionnaire_id,
        "questionnaire_title": questionnaire_title,
        "reusing_component": False,
        "sequence_id": component_configuration.parent_id,
        "configuration_list": configuration_list,
        "icon_class": icon_class,
        "path_of_the_sub_components": None,
        "previous_component_configuration": None
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def experimental_protocol_reuse_component(request, group_id, component_id):

    group = get_object_or_404(Group, pk=group_id)
    # component_configuration = group.experimental_protocol
    experiment = group.experiment

    # component_type = component_configuration.component.component_type
    component_type = "sequence"
    template_name = "experiment/" + component_type + "_component.html"

    questionnaire_id = None
    questionnaire_title = None

    # component = get_object_or_404(Component, pk=component_configuration.component.id)
    component = get_object_or_404(Component, pk=component_id)
    component_form = ComponentForm(request.POST or None, instance=component)

    configuration_form = None

    if group.experimental_protocol.component_id == int(component_id):
        configuration_form = ComponentConfigurationForm(request.POST or None, instance=group.experimental_protocol)
    else:
        configuration_form = ComponentConfigurationForm(request.POST or None,
                                                        initial={'number_of_repetitions': 1,
                                                                 'interval_between_repetitions_value': None})

    # sequence = get_object_or_404(Sequence, pk=component_configuration.component.id)
    sequence = get_object_or_404(Sequence, pk=component_id)
    form = SequenceForm(request.POST or None, instance=sequence)

    existing_component_list = Component.objects.filter(experiment=experiment, component_type=component_type)
    configuration_list = ComponentConfiguration.objects.filter(parent=sequence).order_by('order')

    for configuration in configuration_list:
        configuration.component.icon_class = icon_class[configuration.component.component_type]

    if request.method == "POST":

        if request.POST['action'] == "save":

            if configuration_form.is_valid():

                # important: form.save() must be performed before component_form.save()
                # form.save()
                # component_form.save()

                new_component_configuration = configuration_form.save(commit=False)

                component_configuration = group.experimental_protocol
                component_configuration.name = new_component_configuration.name
                component_configuration.component_id = component_id

                if "number_of_repetitions" in request.POST:
                    component_configuration.number_of_repetitions = request.POST['number_of_repetitions']

                if "interval_between_repetitions_value" in request.POST:
                    component_configuration.interval_between_repetitions_value = \
                        request.POST['interval_between_repetitions_value']

                if "interval_between_repetitions_unit" in request.POST:
                    component_configuration.interval_between_repetitions_unit = \
                        get_object_or_404(TimeUnit, pk=request.POST['interval_between_repetitions_unit'])

                component_configuration.save()

                messages.success(request, 'Componente atualizado com sucesso.')

                redirect_url = reverse("experimental_protocol_update", args=(group_id,))
                return HttpResponseRedirect(redirect_url)

    for form_used in {form, component_form}:
        for field in form_used.fields:
            form_used.fields[field].widget.attrs['disabled'] = True

    context = {
        "experimental_protocol": True,
        "group": group,
        "creating_workflow": True,
        "form": form,
        "experiment": experiment,
        "component_form": component_form,
        "configuration_form": configuration_form,
        "creating": False,
        "updating": True,
        "existing_component_list": existing_component_list,
        "sequence": sequence,
        "questionnaire_id": questionnaire_id,
        "questionnaire_title": questionnaire_title,
        "reusing_component": True,
        # "sequence_id": component_configuration.parent_id,
        "sequence_id": None,
        "configuration_list": configuration_list,
        "icon_class": icon_class,
        "path_of_the_sub_components": None,
        "previous_component_configuration": None
    }

    return render(request, template_name, context)
