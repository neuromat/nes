# coding=utf-8
import re
import datetime
import json

from functools import partial

from operator import itemgetter

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import PermissionDenied
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.utils.translation import ugettext as _

from neo import io

from experiment.models import Experiment, Subject, QuestionnaireResponse, SubjectOfGroup, Group, Component, \
    ComponentConfiguration, Questionnaire, Task, Stimulus, Pause, Instruction, Block, \
    TaskForTheExperimenter, ClassificationOfDiseases, ResearchProject, Keyword, EEG, EEGData, FileFormat, \
    EEGSetting, Equipment, Manufacturer, EEGMachine, EEGAmplifier, EEGElectrodeNet, DataConfigurationTree, \
    EEGMachineSetting, EEGAmplifierSetting, EEGSolutionSetting, EEGFilterSetting, EEGElectrodeLayoutSetting, \
    EEGFilterType, EEGSolution
from experiment.forms import ExperimentForm, QuestionnaireResponseForm, FileForm, GroupForm, InstructionForm, \
    ComponentForm, StimulusForm, BlockForm, ComponentConfigurationForm, ResearchProjectForm, NumberOfUsesToInsertForm, \
    EEGDataForm, EEGSettingForm, EquipmentForm, EEGForm, EEGMachineForm, EEGMachineSettingForm, EEGAmplifierForm, \
    EEGAmplifierSettingForm, EEGSolutionForm, EEGFilterForm, EEGFilterSettingForm, \
    EEGElectrodeLayoutSettingForm, EEGElectrodeLocalizationSystemForm


from patient.models import Patient, QuestionnaireResponse as PatientQuestionnaireResponse

from survey.abc_search_engine import Questionnaires
from survey.models import Survey
from survey.views import get_questionnaire_responses, check_limesurvey_access, recursively_create_list_of_steps, \
    create_list_of_trees

permission_required = partial(permission_required, raise_exception=True)

icon_class = {
    'block': 'glyphicon glyphicon-th-large',
    'instruction': 'glyphicon glyphicon-comment',
    'pause': 'glyphicon glyphicon-time',
    'questionnaire': 'glyphicon glyphicon-list-alt',
    'stimulus': 'glyphicon glyphicon-headphones',
    'task': 'glyphicon glyphicon-check',
    'task_experiment': 'glyphicon glyphicon-wrench',
    'eeg': 'glyphicon glyphicon-flash'
}

delimiter = "-"

# pylint: disable=E1101
# pylint: disable=E1103


class EEGReading:
    file_format = None
    reading = None


@login_required
@permission_required('experiment.view_researchproject')
def research_project_list(request, template_name="experiment/research_project_list.html"):
    research_projects = ResearchProject.objects.order_by('start_date')
    context = {"research_projects": research_projects}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_researchproject')
def research_project_create(request, template_name="experiment/research_project_register.html"):

    research_project_form = ResearchProjectForm(request.POST or None,
                                                initial={'owners_full_name': request.user.get_full_name()})

    if request.method == "POST":

        if request.POST['action'] == "save":

            if research_project_form.is_valid():

                research_project_added = research_project_form.save(commit=False)
                research_project_added.owner = request.user
                research_project_added.save()

                messages.success(request, _('Study created successfully.'))
                redirect_url = reverse("research_project_view", args=(research_project_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))

        else:
            messages.warning(request, _('Action not available.'))

    context = {
        "research_project_form": research_project_form,
        "creating": True,
        "editing": True
    }

    return render(request, template_name, context)


def get_can_change(user, research_project):
    return (user.has_perm('experiment.change_researchproject') and user == research_project.owner) \
        or user.has_perm('experiment.change_researchproject_from_others')


@login_required
@permission_required('experiment.view_researchproject')
def research_project_view(request, research_project_id, template_name="experiment/research_project_register.html"):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    owners_full_name = ""
    if research_project.owner:
        owners_full_name = research_project.owner.get_full_name()

    research_project_form = ResearchProjectForm(request.POST or None, instance=research_project,
                                                initial={'owners_full_name': owners_full_name})

    for field in research_project_form.fields:
        research_project_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":
            if QuestionnaireResponse.objects.filter(
                    subject_of_group__group__experiment__research_project_id=research_project_id).count() == 0:

                try:
                    for keyword in research_project.keywords.all():
                        manage_keywords(keyword, ResearchProject.objects.exclude(id=research_project.id))

                    research_project.delete()
                    messages.success(request, _('Study removed successfully.'))
                    return redirect('research_project_list')
                except ProtectedError:
                    messages.error(request, _("Error trying to delete research."))
                    redirect_url = reverse("research_project_view", args=(research_project_id,))
                    return HttpResponseRedirect(redirect_url)

            else:
                messages.error(request,
                               _("Impossible to delete group because there is (are) questionnaire(s) answered."))
                redirect_url = reverse("research_project_view", args=(research_project_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": get_can_change(request.user, research_project),
        "experiments": research_project.experiment_set.order_by('title'),
        "keywords": research_project.keywords.order_by('name'),
        "research_project": research_project,
        "research_project_form": research_project_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_researchproject')
def research_project_update(request, research_project_id, template_name="experiment/research_project_register.html"):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    if get_can_change(request.user, research_project):
        owners_full_name = ""
        if research_project.owner:
            owners_full_name = research_project.owner.get_full_name()

        research_project_form = ResearchProjectForm(request.POST or None, instance=research_project,
                                                    initial={'owners_full_name': owners_full_name})

        if request.method == "POST":
            if request.POST['action'] == "save":
                if research_project_form.is_valid():
                    if research_project_form.has_changed():
                        research_project_form.save()
                        messages.success(request, _('Research updated successfully.'))
                    else:
                        messages.success(request, _('There is no changes to save.'))

                    redirect_url = reverse("research_project_view", args=(research_project.id,))
                    return HttpResponseRedirect(redirect_url)

        context = {
            "research_project": research_project,
            "research_project_form": research_project_form,
            "editing": True}

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.view_researchproject')
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
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    if get_can_change(request.user, research_project):
        keyword = Keyword.objects.create(name=keyword_name)
        keyword.save()

        research_project.keywords.add(keyword)

        redirect_url = reverse("research_project_view", args=(research_project_id,))
        return HttpResponseRedirect(redirect_url)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_researchproject')
def keyword_add_ajax(request, research_project_id, keyword_id):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    if get_can_change(request.user, research_project):
        keyword = get_object_or_404(Keyword, pk=keyword_id)
        research_project.keywords.add(keyword)

        redirect_url = reverse("research_project_view", args=(research_project_id,))
        return HttpResponseRedirect(redirect_url)
    else:
        raise PermissionDenied


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

    if get_can_change(request.user, research_project):
        keyword = get_object_or_404(Keyword, pk=keyword_id)
        research_project.keywords.remove(keyword)

        manage_keywords(keyword, ResearchProject.objects.all())

        redirect_url = reverse("research_project_view", args=(research_project_id,))
        return HttpResponseRedirect(redirect_url)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.add_experiment')
def experiment_create(request, research_project_id, template_name="experiment/experiment_register.html"):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    if get_can_change(request.user, research_project):
        experiment_form = ExperimentForm(request.POST or None, initial={'research_project': research_project_id})

        if request.method == "POST":
            if request.POST['action'] == "save":
                if experiment_form.is_valid():
                    experiment_added = experiment_form.save()

                    messages.success(request, _('Experiment created successfully.'))

                    redirect_url = reverse("experiment_view", args=(experiment_added.id,))
                    return HttpResponseRedirect(redirect_url)

        context = {
            "research_project": ResearchProject.objects.get(id=research_project_id),
            "experiment_form": experiment_form,
            "creating": True,
            "editing": True}

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def experiment_view(request, experiment_id, template_name="experiment/experiment_register.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    group_list = Group.objects.filter(experiment=experiment)
    eeg_setting_list = EEGSetting.objects.filter(experiment=experiment)
    experiment_form = ExperimentForm(request.POST or None, instance=experiment)

    for field in experiment_form.fields:
        experiment_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            research_project = experiment.research_project

            if get_can_change(request.user, research_project):

                if QuestionnaireResponse.objects.filter(
                        subject_of_group__group__experiment_id=experiment_id).count() == 0:

                    try:
                        experiment.delete()
                        messages.success(request, _('Experiment removed successfully.'))
                        return redirect('research_project_view', research_project_id=research_project.id)
                    except ProtectedError:
                        messages.error(request,
                                       _("It was not possible to delete experiment, "
                                         "because there are groups connected."))
                        redirect_url = reverse("experiment_view", args=(experiment_id,))
                        return HttpResponseRedirect(redirect_url)
                else:
                    messages.error(request,
                                   _("Impossible to delete group because there is (are) questionnaire(s) answered."))
                    redirect_url = reverse("experiment_view", args=(experiment_id,))
                    return HttpResponseRedirect(redirect_url)

            else:
                raise PermissionDenied

    context = {
        "can_change": get_can_change(request.user, experiment.research_project),
        "experiment": experiment,
        "experiment_form": experiment_form,
        "group_list": group_list,
        "eeg_setting_list": eeg_setting_list,
        "research_project": experiment.research_project,
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def experiment_update(request, experiment_id, template_name="experiment/experiment_register.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    if get_can_change(request.user, experiment.research_project):
        group_list = Group.objects.filter(experiment=experiment)
        experiment_form = ExperimentForm(request.POST or None, instance=experiment)

        if request.method == "POST":
            if request.POST['action'] == "save":
                if experiment_form.is_valid():
                    if experiment_form.has_changed():
                        experiment_form.save()
                        messages.success(request, _('Experiment updated successfully.'))
                    else:
                        messages.success(request, _('There is no changes to save.'))

                    redirect_url = reverse("experiment_view", args=(experiment_id,))
                    return HttpResponseRedirect(redirect_url)

        context = {
            "research_project": experiment.research_project,
            "experiment_form": experiment_form,
            "editing": True,
            "group_list": group_list,
            "experiment": experiment}

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.add_subject')
def group_create(request, experiment_id, template_name="experiment/group_register.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    if get_can_change(request.user, experiment.research_project):
        group_form = GroupForm(request.POST or None)

        if request.method == "POST":
            if request.POST['action'] == "save":
                if group_form.is_valid():
                    group_added = group_form.save(commit=False)
                    group_added.experiment_id = experiment_id
                    group_added.save()

                    messages.success(request, _('Group included successfully.'))

                    redirect_url = reverse("group_view", args=(group_added.id,))
                    return HttpResponseRedirect(redirect_url)

        context = {
            "group_form": group_form,
            "creating": True,
            "editing": True,
            "experiment": experiment}

        return render(request, template_name, context)
    else:
        raise PermissionDenied


def recursively_create_list_of_questionnaires_and_statistics(block_id,
                                                             list_of_questionnaires_configuration,
                                                             surveys,
                                                             num_participants):
    questionnaire_configurations = ComponentConfiguration.objects.filter(parent_id=block_id,
                                                                         component__component_type="questionnaire")

    for questionnaire_configuration in questionnaire_configurations:
        if questionnaire_configuration.number_of_repetitions is not None:
            fills_per_participant = questionnaire_configuration.number_of_repetitions
            total_fills_needed = num_participants * fills_per_participant
        else:
            fills_per_participant = "Ilimitado"
            total_fills_needed = "Ilimitado"

        subject_responses = QuestionnaireResponse.objects.filter(
            data_configuration_tree__component_configuration=questionnaire_configuration)
        amount_of_completed_questionnaires = 0

        questionnaire = Questionnaire.objects.get(id=questionnaire_configuration.component.id)

        for subject_response in subject_responses:
            response_result = surveys.get_participant_properties(questionnaire.survey.lime_survey_id,
                                                                 subject_response.token_id, "completed")

            if response_result != "N" and response_result != "":
                amount_of_completed_questionnaires += 1

        list_of_questionnaires_configuration.append({
            "survey_title": surveys.get_survey_title(questionnaire.survey.lime_survey_id),
            "fills_per_participant": fills_per_participant,
            "total_fills_needed": total_fills_needed,
            "total_fills_done": amount_of_completed_questionnaires,
            "id": questionnaire_configuration.id})

    block_configurations = ComponentConfiguration.objects.filter(parent_id=block_id,
                                                                 component__component_type="block")

    for block_configuration in block_configurations:
        list_of_questionnaires_configuration = recursively_create_list_of_questionnaires_and_statistics(
            Block.objects.get(id=block_configuration.component.id),
            list_of_questionnaires_configuration,
            surveys,
            num_participants)

    return list_of_questionnaires_configuration


@login_required
@permission_required('experiment.view_researchproject')
def group_view(request, group_id, template_name="experiment/group_register.html"):
    group = get_object_or_404(Group, pk=group_id)
    group_form = GroupForm(request.POST or None, instance=group)

    for field in group_form.fields:
        group_form.fields[field].widget.attrs['disabled'] = True

    # Navigate the components of the experimental protocol from the root to see if there is any questionnaire component
    # in this group.
    if group.experimental_protocol is not None:
        surveys = Questionnaires()
        # This method shows a message to the user if limesurvey is not available.
        check_limesurvey_access(request, surveys)

        list_of_questionnaires_configuration = recursively_create_list_of_questionnaires_and_statistics(
            group.experimental_protocol,
            [],
            surveys,
            SubjectOfGroup.objects.filter(group_id=group_id).count())

        surveys.release_session_key()
    else:
        list_of_questionnaires_configuration = None

    can_change = get_can_change(request.user, group.experiment.research_project)

    if request.method == "POST":
        if can_change:
            if request.POST['action'] == "remove":

                if QuestionnaireResponse.objects.filter(subject_of_group__group_id=group_id).count() == 0:
                    try:
                        group.delete()
                        messages.success(request, _('Group removed successfully.'))
                        redirect_url = reverse("experiment_view", args=(group.experiment.id,))
                        return HttpResponseRedirect(redirect_url)
                    except ProtectedError:
                        messages.error(request, _("Impossible to delete group, because there are dependencies."))
                        redirect_url = reverse("group_view", args=(group.id,))
                        return HttpResponseRedirect(redirect_url)
                else:
                    messages.error(request,
                                   _("Impossible to delete group because there is (are) questionnaire(s) answered."))
                    redirect_url = reverse("group_view", args=(group.id,))
                    return HttpResponseRedirect(redirect_url)

            elif request.POST['action'] == "remove_experimental_protocol":
                group.experimental_protocol = None
                group.save()
        else:
            raise PermissionDenied

    context = {
        "can_change": can_change,
        "classification_of_diseases_list": group.classification_of_diseases.all(),
        "group_form": group_form,
        "questionnaires_configuration_list": list_of_questionnaires_configuration,
        "experiment": group.experiment,
        "group": group,
        "editing": False,
        "number_of_subjects": SubjectOfGroup.objects.all().filter(group=group).count()
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def group_update(request, group_id, template_name="experiment/group_register.html"):
    group = get_object_or_404(Group, pk=group_id)

    if get_can_change(request.user, group.experiment.research_project):
        group_form = GroupForm(request.POST or None, instance=group)

        if request.method == "POST":
            if request.POST['action'] == "save":
                if group_form.is_valid():
                    if group_form.has_changed():
                        group_form.save()
                        messages.success(request, _('Group updated successfully.'))
                    else:
                        messages.success(request, _('There is no changes to save.'))

                    redirect_url = reverse("group_view", args=(group_id,))
                    return HttpResponseRedirect(redirect_url)

        context = {
            "group_form": group_form,
            "editing": True,
            "experiment": group.experiment,
            "group": group,
        }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.add_subject')
def eeg_setting_create(request, experiment_id, template_name="experiment/eeg_setting_register.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    if get_can_change(request.user, experiment.research_project):
        eeg_setting_form = EEGSettingForm(request.POST or None)

        if request.method == "POST":
            if request.POST['action'] == "save":
                if eeg_setting_form.is_valid():
                    eeg_setting_added = eeg_setting_form.save(commit=False)
                    eeg_setting_added.experiment_id = experiment_id
                    eeg_setting_added.save()

                    messages.success(request, _('EEG setting included successfully.'))

                    redirect_url = reverse("eeg_setting_view", args=(eeg_setting_added.id,))
                    return HttpResponseRedirect(redirect_url)

        context = {
            "eeg_setting_form": eeg_setting_form,
            "creating": True,
            "editing": True,
            "experiment": experiment}

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.view_researchproject')
def eeg_setting_view(request, eeg_setting_id, template_name="experiment/eeg_setting_register.html"):

    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)
    eeg_setting_form = EEGSettingForm(request.POST or None, instance=eeg_setting)

    for field in eeg_setting_form.fields:
        eeg_setting_form.fields[field].widget.attrs['disabled'] = True

    can_change = get_can_change(request.user, eeg_setting.experiment.research_project)

    if request.method == "POST":
        if can_change:
            if request.POST['action'] == "remove":
                # TODO: checking if there is some EEG Data using it

                # TODO: checking if there is some EEG Step using it

                experiment_id = eeg_setting.experiment_id

                eeg_setting.delete()

                messages.success(request, _('EEG setting was removed successfully.'))

                redirect_url = reverse("experiment_view", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

            if request.POST['action'][:7] == "remove-":
                # If action starts with 'remove-' it means that an equipment should be removed from the eeg_setting.
                eeg_setting_type = request.POST['action'][7:]

                if eeg_setting_type == "eeg_machine":
                    setting_to_be_deleted = get_object_or_404(EEGMachineSetting, pk=eeg_setting_id)
                elif eeg_setting_type == "eeg_amplifier":
                    setting_to_be_deleted = get_object_or_404(EEGAmplifierSetting, pk=eeg_setting_id)
                elif eeg_setting_type == "eeg_solution":
                    setting_to_be_deleted = get_object_or_404(EEGSolutionSetting, pk=eeg_setting_id)
                elif eeg_setting_type == "eeg_filter":
                    setting_to_be_deleted = get_object_or_404(EEGFilterSetting, pk=eeg_setting_id)
                elif eeg_setting_type == "eeg_electrode_net_system":
                    setting_to_be_deleted = get_object_or_404(EEGElectrodeLayoutSetting, pk=eeg_setting_id)

                # eeg_setting.eeg_machine_setting.delete()
                setting_to_be_deleted.delete()

                messages.success(request, _('Setting was removed successfully.'))

                redirect_url = reverse("eeg_setting_view", args=(eeg_setting.id,))
                return HttpResponseRedirect(redirect_url)

    equipment_type_choices = Equipment.EQUIPMENT_TYPES

    context = {
        "can_change": can_change,
        "eeg_setting_form": eeg_setting_form,
        "experiment": eeg_setting.experiment,
        "eeg_setting": eeg_setting,
        "editing": False,
        "equipment_type_choices": equipment_type_choices,
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def eeg_setting_update(request, eeg_setting_id, template_name="experiment/eeg_setting_register.html"):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    if get_can_change(request.user, eeg_setting.experiment.research_project):
        eeg_setting_form = EEGSettingForm(request.POST or None, instance=eeg_setting)

        if request.method == "POST":
            if request.POST['action'] == "save":
                if eeg_setting_form.is_valid():
                    if eeg_setting_form.has_changed():
                        eeg_setting_form.save()
                        messages.success(request, _('EEG setting updated successfully.'))
                    else:
                        messages.success(request, _('There is no changes to save.'))

                    redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

        context = {
            "eeg_setting_form": eeg_setting_form,
            "editing": True,
            "experiment": eeg_setting.experiment,
            "eeg_setting": eeg_setting
        }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def view_eeg_setting_type(request, eeg_setting_id, eeg_setting_type):

    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    if get_can_change(request.user, eeg_setting.experiment.research_project):

        template_name = "experiment/eeg_setting_" + eeg_setting_type + ".html"

        manufacturer_list = None
        equipment_list = None
        equipment_form = None
        selection_form = None
        setting_form = None
        solution_list = None
        solution_selected = None

        creating = False

        equipment_selected = None

        if request.method == "POST":
            if request.POST['action'] == "save":
                if 'equipment_selection' in request.POST and 'number_of_channels_used' in request.POST:

                    eeg_machine = EEGMachine.objects.get(pk=request.POST['equipment_selection'])

                    eeg_machine_setting = EEGMachineSetting()
                    eeg_machine_setting.eeg_machine = eeg_machine
                    eeg_machine_setting.number_of_channels_used = request.POST['number_of_channels_used']
                    eeg_machine_setting.eeg_setting = eeg_setting
                    eeg_machine_setting.save()

                    messages.success(request, _('EEG machine setting created successfully.'))

                    redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

                if 'equipment_selection' in request.POST and 'gain' in request.POST:
                    eeg_amplifier = EEGAmplifier.objects.get(pk=request.POST['equipment_selection'])

                    eeg_amplifier_setting = EEGAmplifierSetting()
                    eeg_amplifier_setting.eeg_amplifier = eeg_amplifier
                    eeg_amplifier_setting.gain = request.POST['gain']
                    eeg_amplifier_setting.eeg_setting = eeg_setting
                    eeg_amplifier_setting.save()

                    messages.success(request, _('EEG amplifier setting created sucessfully.'))

                    redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

                if 'solution_selection' in request.POST:
                    eeg_solution = EEGSolution.objects.get(pk=request.POST['solution_selection'])

                    eeg_solution_setting = EEGSolutionSetting()
                    eeg_solution_setting.eeg_solution = eeg_solution
                    eeg_solution_setting.eeg_setting = eeg_setting
                    eeg_solution_setting.save()

                    messages.success(request, _('EEG solution setting created sucessfully.'))

                    redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

        if eeg_setting_type == "eeg_machine":

            try:
                eeg_machine_setting = EEGMachineSetting.objects.get(eeg_setting_id=eeg_setting_id)

                selection_form = EEGMachineForm(request.POST or None, instance=eeg_machine_setting.eeg_machine)
                setting_form = EEGMachineSettingForm(request.POST or None, instance=eeg_machine_setting)
                equipment_selected = eeg_machine_setting.eeg_machine

                for field in setting_form.fields:
                    setting_form.fields[field].widget.attrs['disabled'] = True

            except:

                creating = True

                selection_form = EEGMachineForm(request.POST or None)
                setting_form = EEGMachineSettingForm(request.POST or None)

        if eeg_setting_type == "eeg_amplifier":

            try:
                eeg_amplifier_setting = EEGAmplifierSetting.objects.get(eeg_setting_id=eeg_setting_id)

                selection_form = EEGAmplifierForm(request.POST or None, instance=eeg_amplifier_setting.eeg_amplifier)
                setting_form = EEGAmplifierSettingForm(request.POST or None, instance=eeg_amplifier_setting)
                equipment_selected = eeg_amplifier_setting.eeg_amplifier

                for field in setting_form.fields:
                    setting_form.fields[field].widget.attrs['disabled'] = True

            except:
                creating = True

                selection_form = EEGAmplifierForm(request.POST or None)
                setting_form = EEGAmplifierSettingForm(request.POST or None)

        if eeg_setting_type == "eeg_solution":

            try:
                eeg_solution_setting = EEGSolutionSetting.objects.get(eeg_setting_id=eeg_setting_id)

                selection_form = EEGSolutionForm(request.POST or None, instance=eeg_solution_setting.eeg_solution)
                solution_selected = eeg_solution_setting.eeg_solution

            except:
                creating = True

                selection_form = EEGSolutionForm(request.POST or None)

        if eeg_setting_type == "eeg_filter":

            try:
                eeg_filter_setting = EEGFilterSetting.objects.get(eeg_setting_id=eeg_setting_id)

            except:
                creating = True

        if eeg_setting_type == "eeg_electrode_net_system":

            if hasattr(eeg_setting, 'eeg_electrode_layout_setting'):

                setting = eeg_setting.eeg_electrode_layout_setting

                selection_form = EEGElectrodeLocalizationSystemForm(
                    request.POST or None,
                    initial={
                        'number_of_electrodes':
                        setting.eeg_electrode_net_system.eeg_electrode_localization_system.number_of_electrodes})
                setting_form = EEGElectrodeLayoutSettingForm(
                    request.POST or None,
                    initial={'number_of_electrodes': setting.number_of_electrodes})

            else:
                creating = True

                selection_form = EEGElectrodeLocalizationSystemForm(request.POST or None)
                setting_form = EEGElectrodeLayoutSettingForm(request.POST or None)

        # Settings related to equipment
        if eeg_setting_type in ["eeg_machine", "eeg-amplifier", "eeg_electrode_net_system"]:

            equipment_list = Equipment.objects.filter(equipment_type=eeg_setting_type)
            manufacturer_list = \
                Manufacturer.objects.filter(set_of_equipment__equipment_type=eeg_setting_type).distinct()

            if creating:
                equipment_form = EquipmentForm(request.POST or None)
            else:
                equipment_form = EquipmentForm(request.POST or None, instance=equipment_selected)

        if eeg_setting_type == "eeg_solution":
            solution_list = EEGSolution.objects.all()
            manufacturer_list = Manufacturer.objects.filter(set_of_solution__isnull=False).distinct()

            if creating:
                equipment_form = EEGSolutionForm(request.POST or None)
            else:
                equipment_form = EEGSolutionForm(request.POST or None, instance=solution_selected)

        if eeg_setting_type == "eeg_filter":
            manufacturer_list = EEGFilterType.objects.all()

            if creating:
                equipment_form = EquipmentForm(request.POST or None)
            else:
                equipment_form = EEGFilterForm(request.POST or None, instance=equipment_selected)

        context = {
            "creating": creating,
            "editing": False,

            "can_change": True,

            "eeg_setting_type": eeg_setting_type,

            "eeg_setting": eeg_setting,
            "equipment_selected": equipment_selected,
            "solution_selected" : solution_selected,

            "manufacturer_list": manufacturer_list,
            "equipment_list": equipment_list,
            "solution_list": solution_list,
            "equipment_form": equipment_form,

            "selection_form": selection_form,
            "setting_form": setting_form,
        }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def edit_eeg_setting_type(request, eeg_setting_id, eeg_setting_type):

    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    if get_can_change(request.user, eeg_setting.experiment.research_project):

        template_name = "experiment/eeg_setting_" + eeg_setting_type + ".html"

        manufacturer_list = None
        equipment_list = None
        equipment_form = None
        selection_form = None
        setting_form = None
        solution_list = None
        solution_selected = None

        equipment_selected = None

        if request.method == "POST":

            if request.POST['action'] == "save":
                if 'equipment_selection' in request.POST and 'number_of_channels_used' in request.POST:

                    eeg_machine = EEGMachine.objects.get(pk=request.POST['equipment_selection'])

                    eeg_machine_setting = eeg_setting.eeg_machine_setting

                    eeg_machine_setting.eeg_machine = eeg_machine
                    eeg_machine_setting.number_of_channels_used = request.POST['number_of_channels_used']
                    eeg_machine_setting.eeg_setting = eeg_setting
                    eeg_machine_setting.save()

                    messages.success(request, _('EEG machine setting updated successfully.'))

                    redirect_url = reverse("view_eeg_setting_type", args=(eeg_setting_id, eeg_setting_type))
                    return HttpResponseRedirect(redirect_url)

                if 'equipment_selection' in request.POST and 'gain' in request.POST:

                    eeg_amplifier = EEGAmplifier.objects.get(pk=request.POST['equipment_selection'])

                    eeg_amplifier_setting = eeg_setting.eeg_amplifier_setting

                    eeg_amplifier_setting.eeg_amplifier = eeg_amplifier
                    eeg_amplifier_setting.gain = request.POST['gain']
                    eeg_amplifier_setting.eeg_setting = eeg_setting
                    eeg_amplifier_setting.save()

                    messages.success(request, _('EEG amplifier setting updated sucessfully.'))

                    redirect_url = reverse("view_eeg_setting_type", args=(eeg_setting_id, eeg_setting_type))
                    return HttpResponseRedirect(redirect_url)

                if 'solution_selection' in request.POST:
                    eeg_solution = EEGSolution.objects.get(pk=request.POST['solution_selection'])

                    eeg_solution_setting = eeg_setting.eeg_solution_setting

                    eeg_solution_setting.eeg_solution = eeg_solution
                    eeg_solution_setting.eeg_setting = eeg_setting
                    eeg_solution_setting.save()

                    messages.success(request, _('EEG solution setting updated sucessfully.'))

                    redirect_url = reverse("view_eeg_setting_type", args=(eeg_setting_id, eeg_setting_type))
                    return HttpResponseRedirect(redirect_url)

        if eeg_setting_type == "eeg_machine":

            eeg_machine_setting = eeg_setting.eeg_machine_setting

            selection_form = EEGMachineForm(request.POST or None, instance=eeg_machine_setting.eeg_machine)
            setting_form = EEGMachineSettingForm(request.POST or None, instance=eeg_machine_setting)
            equipment_selected = eeg_machine_setting.eeg_machine

        if eeg_setting_type == "eeg_amplifier":
            eeg_amplifier_setting = eeg_setting.eeg_amplifier_setting

            selection_form = EEGAmplifierForm(request.POST or None, instance=eeg_amplifier_setting.eeg_amplifier)
            setting_form = EEGAmplifierSettingForm(request.POST or None, instance=eeg_amplifier_setting)
            equipment_selected = eeg_amplifier_setting.eeg_amplifier

        if eeg_setting_type == "eeg_solution":
            eeg_solution_setting = eeg_setting.eeg_solution_setting

            solution_selected = eeg_solution_setting.eeg_solution

        # Settings related to equipment
        if eeg_setting_type in ["eeg_machine", "eeg-amplifier", "eeg_electrode_net_system"]:

            equipment_list = Equipment.objects.filter(equipment_type=eeg_setting_type)
            manufacturer_list = Manufacturer.objects.filter(
                set_of_equipment__equipment_type=eeg_setting_type).distinct()

            equipment_form = EquipmentForm(request.POST or None, instance=equipment_selected)

        if eeg_setting_type == "eeg_solution":
            solution_list = EEGSolution.objects.all()
            manufacturer_list = Manufacturer.objects.filter(set_of_solution__isnull=False).distinct()

            equipment_form = EEGSolutionForm(request.POST or None, instance=solution_selected)


        context = {
            "creating": False,
            "editing": True,

            "can_change": True,

            "eeg_setting_type": eeg_setting_type,

            "eeg_setting": eeg_setting,
            "equipment_selected": equipment_selected,
            "solution_selected": solution_selected,

            "solution_list": solution_list,
            "manufacturer_list": manufacturer_list,
            "equipment_list": equipment_list,
            "equipment_form": equipment_form,

            "selection_form": selection_form,
            "setting_form": setting_form,
        }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def get_json_equipment_by_manufacturer(request, equipment_type, manufacturer_id):
    if equipment_type == "eeg_solution":
        equipment = EEGSolution.objects.all()
    else:
        equipment = Equipment.objects.filter(equipment_type=equipment_type)
    if manufacturer_id != "0":
        equipment = equipment.filter(manufacturer_id=manufacturer_id)
    json_equipment = serializers.serialize("json", equipment)
    return HttpResponse(json_equipment, content_type ='application/json')


@login_required
@permission_required('experiment.change_experiment')
def get_json_equipment_attributes(request, equipment_id):

    equipment = get_object_or_404(Equipment, pk=equipment_id)

    response_data = {
        'description': equipment.description,
    }

    if equipment.equipment_type == "eeg_machine":
        equipment = get_object_or_404(EEGMachine, pk=equipment_id)
        response_data['software_version'] = equipment.software_version,
        response_data['number_of_channels'] = equipment.number_of_channels

    elif equipment.equipment_type == "eeg_amplifier":
        equipment = get_object_or_404(EEGAmplifier, pk=equipment_id)
        response_data['gain'] = equipment.gain

    # elif equipment.equipment_type == "eeg_electrode_net":
    #     equipment = get_object_or_404(EEGElectrodeNet, pk=equipment_id)
    #     response_data[''] =

    return HttpResponse(json.dumps(response_data), content_type='application/json')

@login_required
@permission_required('experiment.change_experiment')
def get_json_solution_attributes(request, solution_id):

    solution = get_object_or_404(EEGSolution, pk=solution_id)

    response_data = {
        'description': solution.components,
    }

    return HttpResponse(json.dumps(response_data), content_type='application/json')


@login_required
@permission_required('experiment.change_experiment')
def equipment_view(request, eeg_setting_id, equipment_id,
                   template_name="experiment/add_equipment_to_eeg_setting.html"):

    equipment = get_object_or_404(Equipment, pk=equipment_id)
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    if get_can_change(request.user, eeg_setting.experiment.research_project):

        equipment_list = Equipment.objects.filter(id=equipment_id)
        manufacturer_list = Manufacturer.objects.filter(set_of_equipment=equipment)

        equipment_form = EquipmentForm(
            request.POST or None, initial={'description': equipment.description,
                                           'serial_number': equipment.serial_number})

        for field in equipment_form.fields:
            equipment_form.fields[field].widget.attrs['disabled'] = True

        equipment_type_name = equipment.equipment_type

        for type_element, type_name in Equipment.EQUIPMENT_TYPES:
            if type_element == equipment.equipment_type:
                equipment_type_name = type_name

        context = {
            "creating": False,
            "editing": False,
            "eeg_setting": eeg_setting,
            "manufacturer_list": manufacturer_list,
            "equipment_list": equipment_list,
            "equipment_form": equipment_form,
            "equipment_type": equipment.equipment_type,
            "equipment_selected": equipment,
            "equipment_type_name": equipment_type_name
        }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


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
@permission_required('experiment.change_experiment')
def classification_of_diseases_insert(request, group_id, classification_of_diseases_id):
    """Add group disease"""
    group = get_object_or_404(Group, pk=group_id)

    if get_can_change(request.user, group.experiment.research_project):
        classification_of_diseases = get_object_or_404(ClassificationOfDiseases, pk=classification_of_diseases_id)
        group.classification_of_diseases.add(classification_of_diseases)
        redirect_url = reverse("group_view", args=(group_id,))
        return HttpResponseRedirect(redirect_url)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def classification_of_diseases_remove(request, group_id, classification_of_diseases_id):
    """Remove group disease"""
    group = get_object_or_404(Group, pk=group_id)

    if get_can_change(request.user, group.experiment.research_project):
        classification_of_diseases = get_object_or_404(ClassificationOfDiseases, pk=classification_of_diseases_id)
        classification_of_diseases.group_set.remove(group)
        redirect_url = reverse("group_view", args=(group_id,))
        return HttpResponseRedirect(redirect_url)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.view_researchproject')
def questionnaire_view(request, group_id, component_configuration_id,
                       template_name="experiment/questionnaire_view.html"):
    questionnaire_configuration = get_object_or_404(ComponentConfiguration, pk=component_configuration_id)
    group = get_object_or_404(Group, pk=group_id)
    questionnaire = Questionnaire.objects.get(id=questionnaire_configuration.component.id)

    surveys = Questionnaires()
    questionnaire_title = surveys.get_survey_title(
        Questionnaire.objects.get(id=questionnaire_configuration.component_id).survey.lime_survey_id)

    limesurvey_available = check_limesurvey_access(request, surveys)

    subject_list_with_status = []

    for subject_of_group in SubjectOfGroup.objects.filter(group=group).order_by('subject__patient__name'):
        subject_responses = QuestionnaireResponse.objects.\
            filter(subject_of_group=subject_of_group,
                   data_configuration_tree__component_configuration=questionnaire_configuration)
        amount_of_completed_questionnaires = 0
        questionnaire_responses_with_status = []

        for subject_response in subject_responses:
            response_result = surveys.get_participant_properties(questionnaire.survey.lime_survey_id,
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
        if questionnaire_configuration.number_of_repetitions is None:
            denominator = subject_responses.count()

            if subject_responses.count() > 0:
                percentage = 100 * amount_of_completed_questionnaires / denominator
            else:
                percentage = 0
        else:
            denominator = questionnaire_configuration.number_of_repetitions

            # Handle cases in which number of possible responses was reduced afterwords.
            if questionnaire_configuration.number_of_repetitions < amount_of_completed_questionnaires:
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
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "questionnaire_title": questionnaire_title,
        "questionnaire_configuration": questionnaire_configuration,
        'subject_list': subject_list_with_status,
        "limesurvey_available": limesurvey_available
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_researchproject')
def subjects(request, group_id, template_name="experiment/subjects.html"):

    experimental_protocol_info = {'number_of_questionnaires': 0,
                                  'number_of_eeg_data': 0}

    group = get_object_or_404(Group, id=group_id)

    subject_id = None

    if request.method == "POST" and request.POST['action'][:6] == "remove":
        subject_id = request.POST['action'][7:]
        subject_list = \
            SubjectOfGroup.objects.filter(group=group, subject_id=subject_id).order_by('subject__patient__name')
    else:
        subject_list = SubjectOfGroup.objects.filter(group=group).order_by('subject__patient__name')

    subject_list_with_status = []
    surveys = Questionnaires()
    limesurvey_available = check_limesurvey_access(request, surveys)

    can_remove = True

    # Navigate the components of the experimental protocol from the root to see if there is any questionnaire component
    # in this group.
    if group.experimental_protocol is not None:
        list_of_questionnaires_configuration = recursively_create_list_of_steps(group.experimental_protocol,
                                                                                "questionnaire",
                                                                                [])

        list_of_eeg_configuration = recursively_create_list_of_steps(group.experimental_protocol,
                                                                     "eeg",
                                                                     [])

        experimental_protocol_info = {'number_of_questionnaires': len(list_of_questionnaires_configuration),
                                      'number_of_eeg_data': len(list_of_eeg_configuration)}

        # For each subject of the group...
        for subject_of_group in subject_list:

            number_of_questionnaires_filled = 0

            # For each questionnaire in the experimental protocol of the group...
            for questionnaire_configuration in list_of_questionnaires_configuration:
                # Get the responses
                subject_responses = QuestionnaireResponse.objects. \
                    filter(subject_of_group=subject_of_group,
                           data_configuration_tree__component_configuration=questionnaire_configuration)

                # This is a shortcut that allows to avid the delay of the connection to LimeSurvey.
                if (questionnaire_configuration.number_of_repetitions is None and subject_responses.count() > 0) or \
                        (questionnaire_configuration.number_of_repetitions is not None and
                         subject_responses.count() >= questionnaire_configuration.number_of_repetitions):

                    # Count the number of completed responses
                    amount_of_completed_responses = 0

                    for subject_response in subject_responses:
                        # Check if completed
                        response_result = surveys.get_participant_properties(
                            Questionnaire.objects.get(
                                id=questionnaire_configuration.component.id).survey.lime_survey_id,
                            subject_response.token_id, "completed")

                        if response_result == "N" or response_result == "":
                            # If there is an incomplete response for a questionnaire, this questionnaire is counted
                            # as not completed.
                            amount_of_completed_responses = 0
                            break
                        else:
                            amount_of_completed_responses += 1

                    # Count this questionnaire as completed if it is unlimited and has at least one completed
                    # response, or it is limited and the amount of completed response is greater than or equal to
                    # the number of expected responses.
                    if (questionnaire_configuration.number_of_repetitions is None and
                            amount_of_completed_responses > 0) or \
                            (questionnaire_configuration.number_of_repetitions is not None and
                             amount_of_completed_responses >= questionnaire_configuration.number_of_repetitions):
                        number_of_questionnaires_filled += 1

            percentage_of_questionnaires = 0

            if len(list_of_questionnaires_configuration) > 0:
                percentage_of_questionnaires = \
                    100 * number_of_questionnaires_filled / len(list_of_questionnaires_configuration)

            # EEG data files
            number_of_eeg_data_files_uploaded = 0

            # for each component_configuration...
            for eeg_configuration in list_of_eeg_configuration:
                eeg_data_files = \
                    EEGData.objects.filter(subject_of_group=subject_of_group,
                                           data_configuration_tree__component_configuration=eeg_configuration)
                if len(eeg_data_files):
                    number_of_eeg_data_files_uploaded += 1

            percentage_of_eeg_data_files_uploaded = 0

            if len(list_of_eeg_configuration) > 0:
                percentage_of_eeg_data_files_uploaded = \
                    100 * number_of_eeg_data_files_uploaded / len(list_of_eeg_configuration)

            # If any questionnaire has responses or any eeg data file was uploaded,
            # the subject can't be removed from the group.
            if number_of_eeg_data_files_uploaded or number_of_questionnaires_filled:
                can_remove = False

            subject_list_with_status.append(
                {'subject': subject_of_group.subject,
                 'number_of_questionnaires_filled': number_of_questionnaires_filled,
                 'total_of_questionnaires': len(list_of_questionnaires_configuration),
                 'percentage_of_questionnaires': int(percentage_of_questionnaires),
                 'consent': subject_of_group.consent_form,
                 'number_of_eeg_data_files_uploaded': number_of_eeg_data_files_uploaded,
                 'total_of_eeg_data_files': len(list_of_eeg_configuration),
                 'percentage_of_eeg_data_files_uploaded': int(percentage_of_eeg_data_files_uploaded)},
            )
    else:
        for subject_of_group in subject_list:
            subject_list_with_status.append(
                {'subject': subject_of_group.subject,
                 'number_of_questionnaires_filled': 0,
                 'total_of_questionnaires': 0,
                 'percentage_of_questionnaires': 0,
                 'consent': subject_of_group.consent_form})

    surveys.release_session_key()

    if request.method == "POST":

        if request.POST['action'][:6] == "remove":

            if can_remove:
                get_object_or_404(SubjectOfGroup, group=group, subject_id=subject_id).delete()

                messages.info(request, _('Participant deleted from experiment.'))
            else:
                messages.error(request, _("It was not possible to delete participant, "
                                          "because there are answers or eeg data associated"))

            redirect_url = reverse("subjects", args=(group_id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        'group': group,
        'subject_list': subject_list_with_status,
        "limesurvey_available": limesurvey_available,
        "experimental_protocol_info": experimental_protocol_info
    }

    return render(request, template_name, context)


def subject_questionnaire_response_start_fill_questionnaire(request, subject_id, group_id, questionnaire_id,
                                                            list_of_path):
    questionnaire_response_form = QuestionnaireResponseForm(request.POST)

    data_configuration_tree_id = list_data_configuration_tree(questionnaire_id, list_of_path)
    if not data_configuration_tree_id:
        data_configuration_tree_id = create_data_configuration_tree(list_of_path)

    if questionnaire_response_form.is_valid():
        questionnaire_response = questionnaire_response_form.save(commit=False)
        questionnaire_config = get_object_or_404(ComponentConfiguration, id=questionnaire_id)
        questionnaire_lime_survey = Questionnaires()
        subject = get_object_or_404(Subject, pk=subject_id)
        subject_of_group = get_object_or_404(SubjectOfGroup, subject=subject, group_id=group_id)
        lime_survey_id = Questionnaire.objects.get(id=questionnaire_config.component_id).survey.lime_survey_id

        if not questionnaire_lime_survey.survey_has_token_table(lime_survey_id):
            messages.warning(request, _('Fill not available - Table of tokens was not started.'))
            return None, None

        if questionnaire_lime_survey.get_survey_properties(lime_survey_id, 'active') == 'N':
            messages.warning(request, _('Fill not available - Questionnaire is not activated.'))
            return None, None

        if not check_required_fields(questionnaire_lime_survey, lime_survey_id):
            messages.warning(request, _('Fill not available - Questionnaire does not contain standard fields.'))
            return None, None

        result = questionnaire_lime_survey.add_participant(lime_survey_id)

        questionnaire_lime_survey.release_session_key()

        if not result:
            messages.warning(request,
                             _('Fail trying to generate token to answer questionnaire. '
                               'Check if questionnaire is active.'))
            return None, None

        questionnaire_response.data_configuration_tree_id = data_configuration_tree_id
        questionnaire_response.subject_of_group = subject_of_group
        questionnaire_response.component_configuration = questionnaire_config
        questionnaire_response.token_id = result['token_id']
        questionnaire_response.date = datetime.datetime.strptime(request.POST['date'], _('%m/%d/%Y'))
        questionnaire_response.questionnaire_responsible = request.user
        questionnaire_response.save()

        redirect_url = get_limesurvey_response_url(questionnaire_response)

        return redirect_url, questionnaire_response.pk
    else:
        return None, None


def get_limesurvey_response_url(questionnaire_response):
    questionnaire = Questionnaire.objects.get(
        id=questionnaire_response.data_configuration_tree.component_configuration.component.id)

    questionnaire_lime_survey = Questionnaires()
    token = questionnaire_lime_survey.get_participant_properties(questionnaire.survey.lime_survey_id,
                                                                 questionnaire_response.token_id, "token")
    questionnaire_lime_survey.release_session_key()

    redirect_url = \
        '%s/index.php/%s/token/%s/responsibleid/%s/acquisitiondate/%s/subjectid/%s/newtest/Y' % (
            settings.LIMESURVEY['URL_WEB'],
            questionnaire.survey.lime_survey_id,
            token,
            str(questionnaire_response.questionnaire_responsible.id),
            questionnaire_response.date.strftime('%d-%m-%Y'),
            str(questionnaire_response.subject_of_group.subject.id))

    return redirect_url


@login_required
@permission_required('experiment.add_questionnaireresponse')
def subject_questionnaire_response_create(request, group_id, subject_id, questionnaire_id,
                                          template_name="experiment/subject_questionnaire_response_form.html"):
    group = get_object_or_404(Group, id=group_id)

    list_of_path = [int(item) for item in questionnaire_id.split('-')]
    questionnaire_id = list_of_path[-1]

    if get_can_change(request.user, group.experiment.research_project):
        questionnaire_config = get_object_or_404(ComponentConfiguration, id=questionnaire_id)
        surveys = Questionnaires()
        lime_survey_id = Questionnaire.objects.get(id=questionnaire_config.component_id).survey.lime_survey_id
        survey_title = surveys.get_survey_title(lime_survey_id)
        surveys.release_session_key()

        fail = None
        redirect_url = None
        questionnaire_response_id = None

        questionnaire_response_form = QuestionnaireResponseForm(request.POST or None)

        if request.method == "POST":
            if request.POST['action'] == "save":
                redirect_url, questionnaire_response_id = subject_questionnaire_response_start_fill_questionnaire(
                    request, subject_id, group_id, questionnaire_id, list_of_path)
                if not redirect_url:
                    fail = True
                else:
                    fail = False

        origin = get_origin(request)

        context = {
            "can_change": True,
            "creating": True,
            "FAIL": fail,
            "group": group,
            "origin": origin,
            "questionnaire_configuration": questionnaire_config,
            "questionnaire_response_form": questionnaire_response_form,
            "questionnaire_response_id": questionnaire_response_id,
            "questionnaire_responsible": request.user.get_username(),
            "subject": get_object_or_404(Subject, pk=subject_id),
            "survey_title": survey_title,
            "URL": redirect_url,
        }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_questionnaireresponse')
def questionnaire_response_edit(request, questionnaire_response_id,
                                template_name="experiment/subject_questionnaire_response_form.html"):
    questionnaire_response = get_object_or_404(QuestionnaireResponse, id=questionnaire_response_id)
    questionnaire = Questionnaire.objects.get(
        id=questionnaire_response.data_configuration_tree.component_configuration.component.id)
    group = questionnaire_response.subject_of_group.group
    subject = questionnaire_response.subject_of_group.subject

    surveys = Questionnaires()
    survey_title = surveys.get_survey_title(questionnaire.survey.lime_survey_id)
    survey_completed = (surveys.get_participant_properties(questionnaire.survey.lime_survey_id,
                                                           questionnaire_response.token_id,
                                                           "completed") != "N")
    surveys.release_session_key()

    questionnaire_response_form = QuestionnaireResponseForm(None, instance=questionnaire_response)

    fail = None
    redirect_url = None

    origin = get_origin(request)

    if request.method == "POST":
        if get_can_change(request.user, group.experiment.research_project):
            if request.POST['action'] == "save":
                redirect_url = get_limesurvey_response_url(questionnaire_response)

                if not redirect_url:
                    fail = True
                else:
                    fail = False
                    messages.info(request, _('You will be redirected to questionnaire. Please wait.'))

            elif request.POST['action'] == "remove":
                if request.user.has_perm('experiment.delete_questionnaireresponse'):
                    surveys = Questionnaires()
                    result = surveys.delete_participant(
                        questionnaire.survey.lime_survey_id,
                        questionnaire_response.token_id)
                    surveys.release_session_key()

                    can_delete = False

                    if str(questionnaire_response.token_id) in result:
                        result = result[str(questionnaire_response.token_id)]
                        if result == 'Deleted' or result == 'Invalid token ID':
                            can_delete = True
                    else:
                        if 'status' in result and result['status'] == 'Error: Invalid survey ID':
                            can_delete = True

                    if can_delete:
                        questionnaire_response.delete()
                        messages.success(request, _('Fill deleted successfully.'))
                    else:
                        messages.error(request, _("Error trying to delete fill"))

                    if origin == "experiment_subject":
                        redirect_url = reverse("subject_questionnaire", args=(group.id, subject.id,))
                    else:
                        redirect_url = \
                            reverse("questionnaire_view",
                                    args=(group.id,
                                          questionnaire_response.data_configuration_tree.component_configuration.id,))

                    return HttpResponseRedirect(redirect_url)
                else:
                    raise PermissionDenied
        else:
            raise PermissionDenied

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "completed": survey_completed,
        "creating": False,
        "FAIL": fail,
        "group": group,
        "origin": origin,
        "questionnaire_configuration": questionnaire_response.data_configuration_tree.component_configuration,
        "questionnaire_response_form": questionnaire_response_form,
        "questionnaire_response_id": questionnaire_response_id,
        "questionnaire_responsible": questionnaire_response.questionnaire_responsible,
        "subject": subject,
        "survey_title": survey_title,
        "URL": redirect_url,
    }

    return render(request, template_name, context)


def get_origin(request):
    origin = '0'

    # origin is in request.GET also when the request is a post!
    if 'origin' in request.GET:
        origin = request.GET['origin']

    return origin


def get_position(request):
    position = None

    # position is in request.GET also when the request is a post!
    if 'position' in request.GET:
        position = request.GET['position']

    return position


def get_number_of_uses(request):
    number_of_uses = 1

    # number_of_uses is in request.GET also when the request is a post!
    if 'number_of_uses' in request.GET:
        number_of_uses = request.GET['number_of_uses']

    return number_of_uses


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
                                template_name="experiment/subject_questionnaire_response_form.html"):
    questionnaire_response = get_object_or_404(QuestionnaireResponse, id=questionnaire_response_id)
    questionnaire = Questionnaire.objects.get(
        id=questionnaire_response.data_configuration_tree.component_configuration.component.id)
    group = questionnaire_response.subject_of_group.group
    subject = questionnaire_response.subject_of_group.subject

    surveys = Questionnaires()
    survey_completed = (surveys.get_participant_properties(questionnaire.survey.lime_survey_id,
                                                           questionnaire_response.token_id,
                                                           "completed") != "N")
    surveys.release_session_key()

    questionnaire_response_form = QuestionnaireResponseForm(None, instance=questionnaire_response)

    lime_survey_id = questionnaire.survey.lime_survey_id
    token_id = questionnaire_response.token_id
    language_code = request.LANGUAGE_CODE

    # Get the responses for each question of the questionnaire.
    survey_title, questionnaire_responses = get_questionnaire_responses(language_code, lime_survey_id, token_id,
                                                                        request)

    origin = get_origin(request)

    if request.method == "POST":
        if get_can_change(request.user, group.experiment.research_project):
            if request.POST['action'] == "remove":
                if request.user.has_perm('experiment.delete_questionnaireresponse'):
                    surveys = Questionnaires()
                    result = surveys.delete_participant(
                        questionnaire.survey.lime_survey_id,
                        questionnaire_response.token_id)
                    surveys.release_session_key()

                    can_delete = False

                    if str(questionnaire_response.token_id) in result:
                        result = result[str(questionnaire_response.token_id)]
                        if result == 'Deleted' or result == 'Invalid token ID':
                            can_delete = True
                    else:
                        if 'status' in result and result['status'] == 'Error: Invalid survey ID':
                            can_delete = True

                    if can_delete:
                        questionnaire_response.delete()
                        messages.success(request, _('Fill deleted successfully.'))
                    else:
                        messages.error(request, _("Error trying to delete fill"))

                    if origin == "experiment_subject":
                        redirect_url = reverse("subject_questionnaire", args=(group.id, subject.id,))
                    else:
                        redirect_url = reverse("questionnaire_view",
                                               args=(group.id, questionnaire_response.component_configuration.id,))

                    return HttpResponseRedirect(redirect_url)
                else:
                    raise PermissionDenied
        else:
            raise PermissionDenied

    status = ""
    if 'status' in request.GET:
        status = request.GET['status']

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "completed": survey_completed,
        "creating": False,
        "group": group,
        "origin": origin,
        "questionnaire_configuration": questionnaire_response.data_configuration_tree.component_configuration,
        "questionnaire_response": questionnaire_response,
        "questionnaire_response_form": questionnaire_response_form,
        "questionnaire_response_id": questionnaire_response_id,
        "questionnaire_responses": questionnaire_responses,
        "questionnaire_responsible": questionnaire_response.questionnaire_responsible,
        "patient": subject.patient,  # This is needed when origin=subject
        "status": status,
        "subject": subject,
        "survey_title": survey_title,
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_researchproject')
def subject_questionnaire_view(request, group_id, subject_id,
                               template_name="experiment/subject_questionnaire_response_list.html"):
    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)

    subject_questionnaires = []

    surveys = Questionnaires()
    limesurvey_available = check_limesurvey_access(request, surveys)

    subject_of_group = get_object_or_404(SubjectOfGroup, group=group, subject=subject)

    list_of_paths = create_list_of_trees(group.experimental_protocol, "questionnaire")

    for path in list_of_paths:
        questionnaire_response = ComponentConfiguration.objects.get(pk=path[-1][0])

        data_configuration_tree_id = list_data_configuration_tree(questionnaire_response.id, [item[0] for item in path])

        questionnaire_responses = \
            QuestionnaireResponse.objects.filter(subject_of_group=subject_of_group,
                                                 data_configuration_tree__id=data_configuration_tree_id)

        questionnaire_responses_with_status = []

        questionnaire_configuration = get_object_or_404(ComponentConfiguration, pk=path[-1][0])
        questionnaire = Questionnaire.objects.get(id=questionnaire_configuration.component.id)

        for questionnaire_response in questionnaire_responses:
            response_result = surveys.get_participant_properties(questionnaire.survey.lime_survey_id,
                                                                 questionnaire_response.token_id,
                                                                 "completed")
            questionnaire_responses_with_status.append(
                {'questionnaire_response': questionnaire_response,
                 'completed': None if response_result is None else response_result != "N" and response_result != ""}
            )

        subject_questionnaires.append(
            {'questionnaire_configuration': questionnaire_configuration,
             'title': surveys.get_survey_title(questionnaire.survey.lime_survey_id),
             'path': path,
             'questionnaire_responses': questionnaire_responses_with_status}
        )

    surveys.release_session_key()

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        'group': group,
        'limesurvey_available': limesurvey_available,
        'subject': subject,
        'subject_questionnaires': subject_questionnaires,
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_researchproject')
def subject_eeg_view(request, group_id, subject_id,
                     template_name="experiment/subject_eeg_collection_list.html"):

    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)

    eeg_collections = []

    # list_of_eeg_configuration = recursively_create_list_of_steps(group.experimental_protocol, "eeg", [])

    list_of_paths = create_list_of_trees(group.experimental_protocol, "eeg")

    subject_of_group = get_object_or_404(SubjectOfGroup, group=group, subject=subject)

    # for eeg_configuration in list_of_eeg_configuration:
    for path in list_of_paths:

        eeg_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])

        data_configuration_tree_id = list_data_configuration_tree(eeg_configuration.id, [item[0] for item in path])

        eeg_data_files = EEGData.objects.filter(subject_of_group=subject_of_group,
                                                data_configuration_tree__id=data_configuration_tree_id)

        # eeg_data_files = EEGData.objects.filter(subject_of_group=subject_of_group,
        #                                         data_configuration_tree__component_configuration=eeg_configuration)

        for eeg_data_file in eeg_data_files:
            eeg_data_file.eeg_reading = eeg_data_reading(eeg_data_file)

        eeg_collections.append(
            {'eeg_configuration': eeg_configuration,
             'path': path,
             'eeg_data_files': eeg_data_files}
        )

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        'group': group,
        'subject': subject,
        'eeg_collections': eeg_collections,
    }

    return render(request, template_name, context)


def file_format_code():
    """

    :return: List of dicts. Each dict contains information about a file format.
    """
    file_format = FileFormat.objects.all()
    file_format_list = []
    for file_format_type in file_format:
        file_format_id = file_format_type.pk
        nes_code = file_format_type.nes_code
        extension = file_format_type.extension
        codes = {"id": file_format_id, "code": nes_code, "extension": extension}
        file_format_list.append(codes)

    return file_format_list


def create_data_configuration_tree(list_of_path):
    parent = None
    data_configuration_tree_id = None
    for item in list_of_path:
        new_path = DataConfigurationTree.objects.create(component_configuration_id=item, parent_id=parent)
        new_path.save()
        parent = new_path.id
        data_configuration_tree_id = parent

    return data_configuration_tree_id


def list_data_configuration_tree(eeg_configuration_id, list_of_path):
    data_configuration_tree = DataConfigurationTree.objects.filter(component_configuration_id=eeg_configuration_id)
    list_of_path_in_db = []
    data_configuration_tree_id = None

    if data_configuration_tree:
        for item in data_configuration_tree:
            list_of_path_in_db.insert(0, item.component_configuration_id)
            parent = item.parent_id
            data_configuration_tree_id = item.id
            while parent:
                path = DataConfigurationTree.objects.get(id=parent)
                list_of_path_in_db.insert(0, path.component_configuration_id)
                parent = path.parent_id

            if list_of_path_in_db == list_of_path:
                break
            else:
                list_of_path_in_db = []
                data_configuration_tree_id = None

    return data_configuration_tree_id


@login_required
@permission_required('experiment.add_questionnaireresponse')
def subject_eeg_data_create(request, group_id, subject_id, eeg_configuration_id,
                            template_name="experiment/subject_eeg_data_form.html"):

    group = get_object_or_404(Group, id=group_id)

    list_of_path = [int(item) for item in eeg_configuration_id.split('-')]
    eeg_configuration_id = list_of_path[-1]

    if get_can_change(request.user, group.experiment.research_project):

        eeg_configuration = get_object_or_404(ComponentConfiguration, id=eeg_configuration_id)
        eeg_step = get_object_or_404(EEG, id=eeg_configuration.component_id)

        redirect_url = None
        eeg_data_id = None

        eeg_data_form = EEGDataForm(None, initial={'experiment': group.experiment,
                                                   'eeg_setting': eeg_step.eeg_setting_id})

        file_format_list = file_format_code()

        if request.method == "POST":
            if request.POST['action'] == "save":

                eeg_data_form = EEGDataForm(request.POST, request.FILES)

                if eeg_data_form.is_valid():

                    data_configuration_tree_id = list_data_configuration_tree(eeg_configuration_id, list_of_path)
                    if not data_configuration_tree_id:
                        data_configuration_tree_id = create_data_configuration_tree(list_of_path)

                    subject = get_object_or_404(Subject, pk=subject_id)
                    subject_of_group = get_object_or_404(SubjectOfGroup, subject=subject, group_id=group_id)

                    eeg_data_added = eeg_data_form.save(commit=False)
                    eeg_data_added.subject_of_group = subject_of_group
                    eeg_data_added.component_configuration = eeg_configuration
                    eeg_data_added.data_configuration_tree_id = data_configuration_tree_id

                    # PS: it was necessary adding these 2 lines because Django raised, I do not why (Evandro),
                    # the following error 'EEGData' object has no attribute 'group'
                    eeg_data_added.group = group
                    eeg_data_added.subject = subject

                    eeg_data_added.save()

                    # Validate known eeg file formats
                    reading_for_eeg_validation(eeg_data_added, request)

                    messages.success(request, _('EEG data collection created successfully.'))

                    redirect_url = reverse("subject_eeg_view", args=(group_id, subject_id))
                    return HttpResponseRedirect(redirect_url)

        context = {
            "can_change": True,
            "creating": True,
            "editing": True,
            "group": group,
            "eeg_configuration": eeg_configuration,
            "eeg_data_form": eeg_data_form,
            "eeg_data_id": eeg_data_id,
            "file_format_list": file_format_list,
            "eeg_setting_default_id": eeg_step.eeg_setting_id,
            "subject": get_object_or_404(Subject, pk=subject_id),
            "URL": redirect_url,
        }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


def reading_for_eeg_validation(eeg_data_added, request):
    eeg_reading = eeg_data_reading(eeg_data_added)
    if eeg_reading.file_format:
        if eeg_reading.reading:
            messages.success(request, _('EEG data file format validated.'))
        else:
            messages.warning(request, _('Not valid EEG file format.'))


def eeg_data_reading(eeg_data):

    eeg_reading = EEGReading()

    # For known formats, try to access data in order to validate the format

    if eeg_data.file_format.nes_code == "NEO-RawBinarySignalIO":

        eeg_reading.file_format = eeg_data.file_format

        reading = io.RawBinarySignalIO(filename=eeg_data.file.path)

        try:
            # Trying to read the segments
            reading.read_segment(lazy=False, cascade=True, )
        except:
            reading = None

        eeg_reading.reading = reading

    return eeg_reading


@login_required
@permission_required('experiment.change_experiment')
def eeg_data_view(request, eeg_data_id, template_name="experiment/subject_eeg_data_form.html"):

    eeg_data = get_object_or_404(EEGData, pk=eeg_data_id)

    eeg_data_form = EEGDataForm(request.POST or None, instance=eeg_data)

    eeg_step = get_object_or_404(EEG, id=eeg_data.data_configuration_tree.component_configuration.component.id)

    for field in eeg_data_form.fields:
        eeg_data_form.fields[field].widget.attrs['disabled'] = True

    file_format_list = file_format_code()

    if request.method == "POST":
        if request.POST['action'] == "remove":

            if get_can_change(request.user, eeg_data.subject_of_group.group.experiment.research_project):

                subject_of_group = eeg_data.subject_of_group
                eeg_data.file.delete()
                eeg_data.delete()
                messages.success(request, _('EEG data removed successfully.'))
                return redirect('subject_eeg_view',
                                group_id=subject_of_group.group_id,
                                subject_id=subject_of_group.subject_id)
            else:
                raise PermissionDenied

    context = {
        "can_change": get_can_change(request.user, eeg_data.subject_of_group.group.experiment.research_project),
        "editing": False,
        "group": eeg_data.subject_of_group.group,
        "subject": eeg_data.subject_of_group.subject,
        "eeg_data_form": eeg_data_form,
        "eeg_data": eeg_data,
        "eeg_setting_default_id": eeg_step.eeg_setting_id,
        "file_format_list": file_format_list
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def eeg_data_edit(request, eeg_data_id, template_name="experiment/subject_eeg_data_form.html"):

    eeg_data = get_object_or_404(EEGData, pk=eeg_data_id)

    eeg_step = get_object_or_404(EEG, id=eeg_data.data_configuration_tree.component_configuration.component.id)

    file_format_list = file_format_code()

    if get_can_change(request.user, eeg_data.subject_of_group.group.experiment.research_project):

        if request.method == "POST":

            eeg_data_form = EEGDataForm(request.POST, request.FILES, instance=eeg_data)

            if request.POST['action'] == "save":
                if eeg_data_form.is_valid():
                    if eeg_data_form.has_changed():
                        eeg_data_to_update = eeg_data_form.save(commit=False)
                        eeg_data_to_update.group = eeg_data.subject_of_group.group
                        eeg_data_to_update.subject = eeg_data.subject_of_group.subject
                        eeg_data_to_update.save()

                        # Validate known eeg file formats
                        reading_for_eeg_validation(eeg_data_to_update, request)

                        messages.success(request, _('EEG data updated successfully.'))
                    else:
                        messages.success(request, _('There is no changes to save.'))

                    redirect_url = reverse("eeg_data_view", args=(eeg_data_id,))
                    return HttpResponseRedirect(redirect_url)

        else:
            eeg_data_form = EEGDataForm(request.POST or None, instance=eeg_data,
                                        initial={'experiment': eeg_data.subject_of_group.group.experiment})

        context = {
            "group": eeg_data.subject_of_group.group,
            "subject": eeg_data.subject_of_group.subject,
            "eeg_data_form": eeg_data_form,
            "eeg_data": eeg_data,
            "file_format_list": file_format_list,
            "eeg_setting_default_id": eeg_step.eeg_setting_id,
            "editing": True
        }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.add_subject')
def subjects_insert(request, group_id, patient_id):
    group = get_object_or_404(Group, id=group_id)

    if get_can_change(request.user, group.experiment.research_project):
        patient = get_object_or_404(Patient, pk=patient_id)

        subject = Subject()

        try:
            subject = Subject.objects.get(patient=patient)
        except subject.DoesNotExist:
            subject.patient = patient
            subject.save()

        if not SubjectOfGroup.objects.all().filter(group=group, subject=subject):
            SubjectOfGroup(subject=subject, group=group).save()
        else:
            messages.warning(request, _('Participant has already been inserted in this group.'))

        redirect_url = reverse("subjects", args=(group_id,))
        return HttpResponseRedirect(redirect_url)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.view_researchproject')
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


@login_required
@permission_required('experiment.change_experiment')
def upload_file(request, subject_id, group_id, template_name="experiment/upload_consent_form.html"):
    group = get_object_or_404(Group, pk=group_id)

    if get_can_change(request.user, group.experiment.research_project):
        subject = get_object_or_404(Subject, pk=subject_id)
        subject_of_group = get_object_or_404(SubjectOfGroup, subject=subject, group=group)

        file_form = None

        if request.method == "POST":
            if request.POST['action'] == "upload":
                file_form = FileForm(request.POST, request.FILES, instance=subject_of_group)
                if 'consent_form' in request.FILES:
                    if file_form.is_valid():
                        file_form.save()
                        messages.success(request, _('Consent term saved successfully.'))

                    redirect_url = reverse("subjects", args=(group_id, ))
                    return HttpResponseRedirect(redirect_url)
                else:
                    messages.error(request, _("There are not attachments to save"))
            elif request.POST['action'] == "remove":
                subject_of_group.consent_form.delete()
                subject_of_group.save()
                messages.success(request, _('Attachment deleted successfully.'))

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
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.view_researchproject')
def component_list(request, experiment_id, template_name="experiment/component_list.html"):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    # As it is not possible to sort_by get_component_type_display, filter without sorting and sort later.
    components = Component.objects.filter(experiment=experiment)

    # Create a temporary list of tuples from the query_set to be able to sort by get_component_type_display,
    # identification and name.
    temp_list_of_tuples = []

    for component in components:
        temp_list_of_tuples.append((component,
                                    component.get_component_type_display(),
                                    component.identification))

    temp_list_of_tuples.sort(key=itemgetter(1, 2))

    # Reduce the complexity by creating list of component configurations without having tuples.
    components = []

    for element in temp_list_of_tuples:
        components.append(element[0])

    for component in components:
        component.icon_class = icon_class[component.component_type]
        component.is_root = False
        component.is_unused = False
        if component.component_type == "block":
            if Group.objects.filter(experimental_protocol=component):
                component.is_root = True
        if not component.is_root:
            if not ComponentConfiguration.objects.filter(component=component):
                component.is_unused = True

    component_type_choices = []

    for type_element, type_name in Component.COMPONENT_TYPES:
        component_type_choices.append((type_element, type_name, icon_class.get(type_element)))

    context = {
        "can_change": get_can_change(request.user, experiment.research_project),
        "component_list": components,
        "component_type_choices": component_type_choices,
        "experiment": experiment,
    }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def component_change_the_order(request, path_of_the_components, component_configuration_index, command):
    # The last id of the list is the one for the current block.
    list_of_ids_of_components_and_configurations = path_of_the_components.split(delimiter)
    parent_block = get_object_or_404(Block, pk=list_of_ids_of_components_and_configurations[-1])

    if get_can_change(request.user, parent_block.experiment.research_project):
        configuration_list = create_configuration_list(parent_block)
        index_parts = component_configuration_index.split("-")
        position_of_the_accordion_to_be_moved = int(index_parts[0])

        if len(index_parts) == 2:  # Check the existence of an extra parameter
            # It means that a single component configuration should be moved
            position_in_accordion_of_the_conf_to_be_moved = int(index_parts[1])
            conf_to_move1 = configuration_list[position_of_the_accordion_to_be_moved][
                position_in_accordion_of_the_conf_to_be_moved]
            conf_to_move1_order = conf_to_move1.order

            if command == "down":
                # First configuration that has an order greater than mine.
                conf_to_move2 = ComponentConfiguration.objects.filter(parent=parent_block).filter(
                    order__gt=conf_to_move1_order).order_by('order')[0]
            else:
                # Last configuration that has an order less than mine.
                conf_to_move2 = ComponentConfiguration.objects.filter(parent=parent_block).filter(
                    order__lt=conf_to_move1_order).order_by('-order')[0]

            conf_to_move2_order = conf_to_move2.order

            # Due to unique and not null restrictions, set a temporary value to conf_to_move order.
            last_conf_order = configuration_list[-1][-1].order
            conf_to_move1.order = last_conf_order + 1
            conf_to_move1.save()

            conf_to_move2.order = conf_to_move1_order
            conf_to_move2.save()

            conf_to_move1.order = conf_to_move2_order
            conf_to_move1.save()

        else:
            # The whole accordion should be moved
            if command == "down":
                last = configuration_list[position_of_the_accordion_to_be_moved][-1].order

                # First configuration that has an order greater than last conf of the accordion.
                conf_to_move2 = ComponentConfiguration.objects.filter(parent=parent_block).filter(
                    order__gt=last).order_by('order')[0]

                accordion = reversed(configuration_list[position_of_the_accordion_to_be_moved])
            else:
                first = configuration_list[position_of_the_accordion_to_be_moved][0].order

                # Last configuration that has an order less than first conf of the accordion.
                conf_to_move2 = ComponentConfiguration.objects.filter(parent=parent_block).filter(
                    order__lt=first).order_by('-order')[0]

                accordion = configuration_list[position_of_the_accordion_to_be_moved]

            next_order = conf_to_move2.order

            # Due to unique and not null restrictions, set a temporary value to conf_to_move2 order.
            last_conf_order = configuration_list[-1][-1].order
            conf_to_move2.order = last_conf_order + 1
            conf_to_move2.save()

            for conf in accordion:
                temp = conf.order
                conf.order = next_order
                conf.save()
                next_order = temp

            conf_to_move2.order = next_order
            conf_to_move2.save()

        redirect_url = reverse("component_view", args=(path_of_the_components,))

        return HttpResponseRedirect(redirect_url)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def component_create(request, experiment_id, component_type):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    if get_can_change(request.user, experiment.research_project):
        template_name = "experiment/" + component_type + "_component.html"
        component_form = ComponentForm(request.POST or None)
        # This is needed for the form to be able to validate the presence of a duration in a pause component only.
        component_form.component_type = component_type
        questionnaires_list = []
        specific_form = None

        if component_type == 'instruction':
            specific_form = InstructionForm(request.POST or None)
        elif component_type == 'stimulus':
            specific_form = StimulusForm(request.POST or None)
        elif component_type == 'eeg':
            specific_form = EEGForm(request.POST or None, initial={'experiment': experiment})
        elif component_type == 'questionnaire':
            questionnaires_list = Questionnaires().find_all_active_questionnaires()
        elif component_type == 'block':
            specific_form = BlockForm(request.POST or None, initial={'number_of_mandatory_components': None})
            # component_form.fields['duration_value'].widget.attrs['disabled'] = True
            # component_form.fields['duration_unit'].widget.attrs['disabled'] = True

        if request.method == "POST":
            new_specific_component = None

            if component_form.is_valid():
                if component_type == 'questionnaire':
                    new_specific_component = Questionnaire()
                    survey, created = Survey.objects.get_or_create(
                        lime_survey_id=request.POST['questionnaire_selected'],
                        is_initial_evaluation=False)
                    new_specific_component.survey = survey
                elif component_type == 'pause':
                    new_specific_component = Pause()
                elif component_type == 'task':
                    new_specific_component = Task()
                elif component_type == 'task_experiment':
                    new_specific_component = TaskForTheExperimenter()
                elif specific_form.is_valid():
                    new_specific_component = specific_form.save(commit=False)

                if new_specific_component is not None:
                    component = component_form.save(commit=False)
                    new_specific_component.description = component.description
                    new_specific_component.identification = component.identification
                    new_specific_component.component_type = component_type
                    new_specific_component.experiment = experiment
                    new_specific_component.duration_value = component.duration_value
                    new_specific_component.duration_unit = component.duration_unit
                    new_specific_component.save()

                    messages.success(request, _('Step included successfully.'))

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
    else:
        raise PermissionDenied


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
                    name = "Uso do passo " + cc.component.identification

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
        path_without_last = path_of_the_components[:path_of_the_components.rfind(delimiter)]
        last_hyphen_index = path_without_last.rfind(delimiter)

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


second_in_milliseconds = 1000
minute_in_milliseconds = 60 * second_in_milliseconds
hour_in_milliseconds = 60 * minute_in_milliseconds
day_in_milliseconds = 24 * hour_in_milliseconds
week_in_milliseconds = 7 * day_in_milliseconds
month_in_milliseconds = 30 * day_in_milliseconds
year_in_milliseconds = 365 * day_in_milliseconds


def convert_to_milliseconds(value, unit):
    if value is None:
        return 0
    else:
        if unit == 'y':
            return value * year_in_milliseconds
        if unit == 'mon':
            return value * month_in_milliseconds
        if unit == 'w':
            return value * week_in_milliseconds
        if unit == 'd':
            return value * day_in_milliseconds
        if unit == 'h':
            return value * hour_in_milliseconds
        if unit == 'min':
            return value * minute_in_milliseconds
        if unit == 's':
            return value * second_in_milliseconds
        if unit == 'ms':
            return value
        else:  # Unit is None or unknown
            return 0


def convert_to_string(duration_in_milliseconds):
    string = ""

    duration_in_years = int(duration_in_milliseconds / year_in_milliseconds)
    if duration_in_years >= 1:
        string += str(duration_in_years) + (_(" years ") if duration_in_years > 1 else _(" year "))
        duration_in_milliseconds -= duration_in_years * year_in_milliseconds

    duration_in_months = int(duration_in_milliseconds / month_in_milliseconds)
    if duration_in_months >= 1:
        string += str(duration_in_months) + (_(" months ") if duration_in_months > 1 else _(" month "))
        duration_in_milliseconds -= duration_in_months * month_in_milliseconds

    duration_in_weeks = int(duration_in_milliseconds / week_in_milliseconds)
    if duration_in_weeks >= 1:
        string += str(duration_in_weeks) + (_(" weeks ") if duration_in_weeks > 1 else _(" week "))
        duration_in_milliseconds -= duration_in_weeks * week_in_milliseconds

    duration_in_days = int(duration_in_milliseconds / day_in_milliseconds)
    if duration_in_days >= 1:
        string += str(duration_in_days) + (_(" days ") if duration_in_days > 1 else _(" day "))
        duration_in_milliseconds -= duration_in_days * day_in_milliseconds

    duration_in_hours = int(duration_in_milliseconds / hour_in_milliseconds)
    if duration_in_hours >= 1:
        string += str(duration_in_hours) + (_(" hours ") if duration_in_hours > 1 else _(" hour "))
        duration_in_milliseconds -= duration_in_hours * hour_in_milliseconds

    duration_in_minutes = int(duration_in_milliseconds / minute_in_milliseconds)
    if duration_in_minutes >= 1:
        string += str(duration_in_minutes) + (_(" minutes ") if duration_in_minutes > 1 else _(" minute "))
        duration_in_milliseconds -= duration_in_minutes * minute_in_milliseconds

    duration_in_seconds = int(duration_in_milliseconds / second_in_milliseconds)
    if duration_in_seconds >= 1:
        string += str(duration_in_seconds) + (_(" seconds ") if duration_in_seconds > 1 else _(" second "))
        duration_in_milliseconds -= duration_in_seconds * second_in_milliseconds

    if duration_in_milliseconds >= 1:
        string += str(duration_in_milliseconds) + \
            (_(" miliseconds ") if duration_in_milliseconds > 1 else _(" milisecond "))

    if string == "":
        string = "0"
    else:
        # Add commas and 'and' to the string
        list_of_words = string.split(" ")
        values = list_of_words[::2]
        units = list_of_words[1::2]
        list_of_values_with_units = [value + " " + unit for value, unit in zip(values, units)]
        before_and = ", ".join(list_of_values_with_units[0:-1])

        if before_and == "":
            string = list_of_values_with_units[-1]
        else:
            string = before_and + _(" and ") + list_of_values_with_units[-1]

    return string


def calculate_block_duration(block):
    duration_value_in_milliseconds = 0
    has_unlimited = False

    for component_configuration in block.children.all():
        component = component_configuration.component

        if component.component_type == 'block':
            component_duration, child_has_unlimited = calculate_block_duration(Block.objects.get(id=component.id))

            if child_has_unlimited:
                has_unlimited = True
        else:
            component_duration = convert_to_milliseconds(component.duration_value, component.duration_unit)

        if component_configuration.number_of_repetitions is None:
            # Considers the duration of only one execution of the component, but notifies parent about this.
            has_unlimited = True
        else:
            interval_in_milliseconds = 0

            if component_configuration.interval_between_repetitions_value is not None:
                interval_in_milliseconds = convert_to_milliseconds(
                    component_configuration.interval_between_repetitions_value,
                    component_configuration.interval_between_repetitions_unit)

            component_duration = component_duration * component_configuration.number_of_repetitions + \
                interval_in_milliseconds * (component_configuration.number_of_repetitions - 1)

        if block.type == Block.SEQUENCE:
            # Add duration of the children
            duration_value_in_milliseconds += component_duration
        elif block.type == Block.PARALLEL_BLOCK:
            # Duration of the block is the duration of the longest child.
            if component_duration > duration_value_in_milliseconds:
                duration_value_in_milliseconds = component_duration

    return duration_value_in_milliseconds, has_unlimited


def access_objects_for_view_and_update(request, path_of_the_components, updating=False):
    list_of_ids_of_components_and_configurations = path_of_the_components.split(delimiter)

    # The last id of the list is the one that we want to show.
    last_id = list_of_ids_of_components_and_configurations[-1]

    group = None

    if path_of_the_components[0] == "G":
        # The id of the group comes after "G"
        group_id = int(list_of_ids_of_components_and_configurations[0][1:])
        group = get_object_or_404(Group, pk=group_id)

    component_configuration = None
    configuration_form = None

    if last_id[0] == "U":  # If id starts with 'U' (from 'use'), it is a configuration.
        component_configuration = get_object_or_404(ComponentConfiguration, pk=last_id[1:])
        configuration_form = ComponentConfigurationForm(request.POST or None, instance=component_configuration)
        component = component_configuration.component
    else:
        component = get_object_or_404(Component, pk=last_id)

    component_form = ComponentForm(request.POST or None, instance=component)

    list_of_breadcrumbs = create_list_of_breadcrumbs(list_of_ids_of_components_and_configurations)

    experiment = component.experiment

    component_type = component.component_type
    template_name = "experiment/" + component_type + "_component.html"

    # This is needed for the form to be able to validate the presence of a duration in a pause component only.
    component_form.component_type = component_type

    back_cancel_url = create_back_cancel_url(component_type, component_configuration, path_of_the_components,
                                             list_of_ids_of_components_and_configurations, experiment, updating)

    return component, component_configuration, component_form, configuration_form, experiment, component_type,\
        template_name, list_of_ids_of_components_and_configurations, list_of_breadcrumbs, group,\
        back_cancel_url


def remove_component_and_related_configurations(component,
                                                list_of_ids_of_components_and_configurations,
                                                path_of_the_components):
    # Before removing anything, we need to know where we should redirect to.

    if len(list_of_ids_of_components_and_configurations) == 1:
        # User is editing a component selected from the list of component of an exepriment.
        # Return to the list of components.
        redirect_url = "/experiment/" + str(component.experiment.id) + "/components"
    else:
        path_without_last = path_of_the_components[:path_of_the_components.rfind(delimiter)]

        if len(list_of_ids_of_components_and_configurations) == 2:
            # User is viewing the block that is the root of an experimental protocol.
            # Return to the group.
            redirect_url = "/experiment/group/" + path_without_last[1:]
        else:
            # The user is viewing/editing a component that is a child of a block. Remove the child and the component
            # configuration that binds it to the block.
            path_without_last_two = path_without_last[:path_without_last.rfind(delimiter)]
            # The parent of the component configuration has to be a block. Then, redirect_url has no "edit" part.
            redirect_url = "/experiment/component/" + path_without_last_two

    # if the questionnaire is a questionnaire and it is the only usage of a survey, the survey should also be removed.
    survey_to_check = None
    if component.component_type == "questionnaire":
        questionnaire = get_object_or_404(Questionnaire, pk=component.id)
        if not questionnaire.survey.is_initial_evaluation:
            survey_to_check = questionnaire.survey

    component.delete()

    # Checking if there is no other use
    if survey_to_check and \
            len(Questionnaire.objects.filter(survey=survey_to_check)) == 0 and \
            len(PatientQuestionnaireResponse.objects.filter(survey=survey_to_check)) == 0:
        survey_to_check.delete()

    return redirect_url


def remove_component_configuration(request, conf):
    order_of_removed = conf.order
    parent_of_removed = conf.parent_id

    try:
        conf.delete()

        if conf.random_position:
            last_conf = ComponentConfiguration.objects.filter(
                parent_id=parent_of_removed, random_position=True).order_by('order').last()

            # If the order of the removed component is smaller than the order of the last random-positioned
            # element, assign the order of the removed to the last random-positioned element. This way, for
            # the user, it is like removing the last position for random components.
            if last_conf is not None and last_conf.order > order_of_removed:
                last_conf.order = order_of_removed
                last_conf.save()
    except ProtectedError:
        messages.error(request, "Não foi possível excluir o uso, pois há dados associados")


@login_required
@permission_required('experiment.view_researchproject')
def component_view(request, path_of_the_components):
    # It will always be a block because we don't have a view screen for other components.
    # This view is also use to show the use of a set of steps (component configuration of a block).

    component, component_configuration, component_form, configuration_form, experiment, component_type, template_name,\
        list_of_ids_of_components_and_configurations, list_of_breadcrumbs, group, back_cancel_url =\
        access_objects_for_view_and_update(request, path_of_the_components)

    block = get_object_or_404(Block, pk=component.id)
    block_form = BlockForm(request.POST or None, instance=block)
    configuration_list = create_configuration_list(block)
    configuration_list_of_random_components = create_configuration_list_of_random_components(block)

    duration_value, has_unlimited = calculate_block_duration(block)
    # Criate a string converting to appropriate units
    duration_string = convert_to_string(duration_value)

    # It is not possible to edit fields while viewing a block.
    for form in {block_form, component_form}:
        for field in form.fields:
            form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if get_can_change(request.user, experiment.research_project):
            if request.POST['action'] == "save":
                if configuration_form is not None:
                    if configuration_form.is_valid():
                        configuration_form.save()
                        messages.success(request, _('Step use updated successfully.'))
                        return HttpResponseRedirect(back_cancel_url)
            elif request.POST['action'] == "remove":
                redirect_url = remove_component_and_related_configurations(component,
                                                                           list_of_ids_of_components_and_configurations,
                                                                           path_of_the_components)
                messages.success(request, _('Component deleted successfully.'))
                return HttpResponseRedirect(redirect_url)
            elif request.POST['action'][:7] == "remove-":
                # If action starts with 'remove-' it means that a child or some children should be removed.
                action_parts = request.POST['action'].split(delimiter)

                if action_parts[1] == "random":
                    list_from_which_to_deleted = configuration_list_of_random_components
                else:  # "fixed"
                    list_from_which_to_deleted = configuration_list

                position_of_the_accordion_to_be_deleted = int(action_parts[2])

                if len(action_parts) == 4:  # Check the existence of an extra parameter
                    # It means that a single component configuration should be removed
                    position_in_accordion_of_the_conf_to_be_deleted = int(action_parts[3])
                    remove_component_configuration(request,
                                                   list_from_which_to_deleted[position_of_the_accordion_to_be_deleted]
                                                   [position_in_accordion_of_the_conf_to_be_deleted])
                else:
                    for conf in list_from_which_to_deleted[position_of_the_accordion_to_be_deleted]:
                        # Only uses that do not have associated data will be excluded.
                        remove_component_configuration(request, conf)

                redirect_url = reverse("component_view", args=(path_of_the_components,))
                return HttpResponseRedirect(redirect_url)
        else:
            raise PermissionDenied

    component_type_choices = []
    for type_element, type_name in Component.COMPONENT_TYPES:
        component_type_choices.append((type_element, type_name, icon_class.get(type_element)))

    can_change = get_can_change(request.user, experiment.research_project)

    # This value is used to define if the options Fixed/Radon should be shown.
    type_of_the_parent_block = None
    if component_configuration:
        type_of_the_parent_block = Block.objects.get(id=component_configuration.parent_id).type

        # If the user is not the owner of the research_project, not event the fields of the component configuration
        # can be edited.
        if not can_change:
            for field in configuration_form.fields:
                configuration_form.fields[field].widget.attrs['disabled'] = True

    context = {
        "back_cancel_url": back_cancel_url,
        "block_duration": duration_string,
        "can_change": can_change,
        "component": block,
        "component_configuration": component_configuration,
        "component_form": component_form,
        "configuration_form": configuration_form,
        "configuration_list": configuration_list,
        "configuration_list_of_random_components": configuration_list_of_random_components,
        "experiment": experiment,
        "group": group,
        "has_unlimited": has_unlimited,
        "icon_class": icon_class,
        "list_of_breadcrumbs": list_of_breadcrumbs,
        "path_of_the_components": path_of_the_components,
        "specific_form": block_form,
        "type_of_the_parent_block": type_of_the_parent_block,
        "component_type_choices": component_type_choices,
    }

    return render(request, template_name, context)


def sort_without_using_order(configuration_list_of_random_components):
    for configuration in configuration_list_of_random_components:
        configuration.component.icon_class = icon_class[configuration.component.component_type]

    # Create a temporary list of tuples from the query_set to be able to sort by get_component_type_display,
    # identification and name.
    temp_list_of_tuples = []

    for cc in configuration_list_of_random_components:
        temp_list_of_tuples.append((cc,
                                    cc.component.get_component_type_display(),
                                    cc.component.identification,
                                    (cc.name if cc.name else '')))

    temp_list_of_tuples.sort(key=itemgetter(1, 2, 3))

    # Reduce the complexity by creating list of component configurations without having tuples.
    configuration_list_of_random_components = []

    for element in temp_list_of_tuples:
        configuration_list_of_random_components.append(element[0])

    return configuration_list_of_random_components


def create_configuration_list(block):
    configuration_list = ComponentConfiguration.objects.filter(parent=block)

    if block.type == "sequence":
        configuration_list = configuration_list.order_by('order')
    else:
        configuration_list = sort_without_using_order(configuration_list)

    for configuration in configuration_list:
        configuration.component.icon_class = icon_class[configuration.component.component_type]

    # Transform configuration_list into a list of lists, to show them in accordions.
    i = 0
    new_list = []
    all_random = True
    while i < len(configuration_list):
        accordion = [configuration_list[i]]
        i += 1

        # Group if same component or if both are random_position
        while i < len(configuration_list) and \
                ((configuration_list[i-1].component == configuration_list[i].component and
                  configuration_list[i-1].random_position == configuration_list[i].random_position) or
                 (configuration_list[i-1].random_position == configuration_list[i].random_position and
                  configuration_list[i].random_position is True)):
            accordion.append(configuration_list[i])
            i += 1

        new_list.append(accordion)

        if not accordion[0].random_position:
            all_random = False

    # If all items of this list are random, set the list to be empty.
    if all_random:
        new_list = []

    return new_list


def create_configuration_list_of_random_components(block):
    if block.type == "sequence":
        # As it is not possible to sort_by get_component_type_display, filter without sorting and sort later.
        configuration_list_of_random_components = sort_without_using_order(
            ComponentConfiguration.objects.filter(parent=block, random_position=True))
    else:
        configuration_list_of_random_components = []

    # Transform configuration_list_of_random_components into a list of lists, to show them in accordions.
    i = 0
    new_random_list = []
    while i < len(configuration_list_of_random_components):
        accordion = [configuration_list_of_random_components[i]]
        i += 1

        while i < len(configuration_list_of_random_components) and \
                configuration_list_of_random_components[i-1].component == \
                configuration_list_of_random_components[i].component:
            accordion.append(configuration_list_of_random_components[i])
            i += 1

        new_random_list.append(accordion)

    return new_random_list


@login_required
@permission_required('experiment.change_experiment')
def component_update(request, path_of_the_components):
    component, component_configuration, component_form, configuration_form, experiment, component_type, template_name,\
        list_of_ids_of_components_and_configurations, list_of_breadcrumbs, group, back_cancel_url =\
        access_objects_for_view_and_update(request, path_of_the_components, updating=True)

    questionnaire_id = None
    questionnaire_title = None
    configuration_list = []
    configuration_list_of_random_components = []
    specific_form = None
    duration_string = None
    has_unlimited = None

    if component_type == 'instruction':
        instruction = get_object_or_404(Instruction, pk=component.id)
        specific_form = InstructionForm(request.POST or None, instance=instruction)
    elif component_type == 'stimulus':
        stimulus = get_object_or_404(Stimulus, pk=component.id)
        specific_form = StimulusForm(request.POST or None, instance=stimulus)
    elif component_type == 'eeg':
        eeg = get_object_or_404(EEG, pk=component.id)
        specific_form = EEGForm(request.POST or None, instance=eeg, initial={'experiment': experiment})
    elif component_type == 'questionnaire':
        questionnaire = get_object_or_404(Questionnaire, pk=component.id)
        questionnaire_details = Questionnaires().find_questionnaire_by_id(questionnaire.survey.lime_survey_id)

        if questionnaire_details:
            questionnaire_id = questionnaire_details['sid'],
            questionnaire_title = questionnaire_details['surveyls_title']
    elif component_type == 'block':
        block = get_object_or_404(Block, pk=component.id)
        specific_form = BlockForm(request.POST or None, instance=block)
        configuration_list = create_configuration_list(block)
        configuration_list_of_random_components = create_configuration_list_of_random_components(block)
        duration_value, has_unlimited = calculate_block_duration(block)
        # Criate a string converting to appropriate units
        duration_string = convert_to_string(duration_value)

    can_change = get_can_change(request.user, experiment.research_project)

    if request.method == "POST":
        if can_change:
            if request.POST['action'] == "save":
                if configuration_form is None:
                    # There is no specific form for a these component types.
                    if component.component_type == "questionnaire" or component.component_type == "task" or \
                            component.component_type == "task_experiment" or component.component_type == 'pause':
                        if component_form.is_valid():
                            # Only save if there was a change.
                            if component_form.has_changed():
                                component_form.save()
                                messages.success(request, _('Step updated successfully.'))
                            else:
                                messages.success(request, _('There is no changes to save.'))

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
                            messages.success(request, _('Step updated successfully.'))
                        else:
                            messages.success(request, _('There is no changes to save.'))

                        return HttpResponseRedirect(back_cancel_url)

                elif configuration_form.is_valid():
                    # Only save if there was a change.
                    if configuration_form.has_changed():
                        configuration_form.save()
                        messages.success(request, _('Step use updated successfully.'))
                    else:
                        messages.success(request, _('There is no changes to save.'))

                    return HttpResponseRedirect(back_cancel_url)
            elif request.POST['action'] == "remove":
                redirect_url = remove_component_and_related_configurations(component,
                                                                           list_of_ids_of_components_and_configurations,
                                                                           path_of_the_components)
                messages.success(request, _('Component deleted successfully.'))
                return HttpResponseRedirect(redirect_url)

    type_of_the_parent_block = None

    # It is not possible to edit the component fields while editing a component configuration.
    if component_configuration or not can_change:
        if specific_form is not None:
            for field in specific_form.fields:
                specific_form.fields[field].widget.attrs['disabled'] = True

        for field in component_form.fields:
            component_form.fields[field].widget.attrs['disabled'] = True

        if component_configuration:
            type_of_the_parent_block = Block.objects.get(id=component_configuration.parent_id).type

            # If the user is not the owner of the research_project, not event the fields of the component configuration
            # can be edited.
            if not can_change:
                for field in configuration_form.fields:
                    configuration_form.fields[field].widget.attrs['disabled'] = True

    context = {
        "back_cancel_url": back_cancel_url,
        "block_duration": duration_string,
        "can_change": can_change,
        "component_configuration": component_configuration,
        "component_form": component_form,
        "configuration_form": configuration_form,
        "configuration_list": configuration_list,
        "configuration_list_of_random_components": configuration_list_of_random_components,
        "icon_class": icon_class,
        "experiment": experiment,
        "group": group,
        "has_unlimited": has_unlimited,
        "list_of_breadcrumbs": list_of_breadcrumbs,
        "path_of_the_components": path_of_the_components,
        "questionnaire_id": questionnaire_id,
        "questionnaire_title": questionnaire_title,
        "specific_form": specific_form,
        "updating": True,
        "type_of_the_parent_block": type_of_the_parent_block,
    }

    return render(request, template_name, context)


def get_recursively_set_of_components_to_exclude(component):
    """
    :param component: component to analyse recursively
    :return: set of components
    """

    # {[component]} returns a set with one element
    component_list = [component]
    output_set_of_components = set(component_list)

    list_of_component_configuration = ComponentConfiguration.objects.filter(component=component)

    if not list_of_component_configuration:
        return output_set_of_components

    for component_configuration in list_of_component_configuration:
        if component_configuration.parent not in output_set_of_components:
            set_of_parents = get_recursively_set_of_components_to_exclude(component_configuration.parent)
            output_set_of_components |= set_of_parents

    return output_set_of_components


def access_objects_for_add_new_and_reuse(component_type, path_of_the_components):
    template_name = "experiment/" + component_type + "_component.html"
    list_of_ids_of_components_and_configurations = path_of_the_components.split(delimiter)
    list_of_breadcrumbs = create_list_of_breadcrumbs(list_of_ids_of_components_and_configurations)

    block = None
    group = None

    experiment = None

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

    if block:
        set_of_components_to_exclude = get_recursively_set_of_components_to_exclude(block)
        for component in set_of_components_to_exclude:
            existing_component_list = existing_component_list.exclude(id=component.id)

    specific_form = None

    # If configuring a new experimental protocol for a group, return to the group. Otherwise, return to the parent
    # block.
    if len(list_of_ids_of_components_and_configurations) == 1 and path_of_the_components[0] == 'G':
        back_cancel_url = "/experiment/group/" + str(group.id)
    else:
        back_cancel_url = "/experiment/component/" + path_of_the_components

    return \
        existing_component_list, experiment, group, list_of_breadcrumbs, block, template_name, specific_form, \
        list_of_ids_of_components_and_configurations, back_cancel_url


@login_required
@permission_required('experiment.change_experiment')
def component_add_new(request, path_of_the_components, component_type):
    existing_component_list, experiment, group, list_of_breadcrumbs, block, template_name,\
        specific_form, list_of_ids_of_components_and_configurations, back_cancel_url = \
        access_objects_for_add_new_and_reuse(component_type, path_of_the_components)

    if get_can_change(request.user, experiment.research_project):
        # Fixed or random
        position = get_position(request)

        # Number of uses to insert
        number_of_uses = get_number_of_uses(request)

        component_form = ComponentForm(request.POST or None)
        # This is needed for the form to be able to validate the presence of a duration in a pause component only.
        component_form.component_type = component_type

        # Check if we are configuring a new experimental protocol
        is_configuring_new_experimental_protocol =\
            group is not None and len(list_of_ids_of_components_and_configurations) == 1

        number_of_uses_form = None

        if not is_configuring_new_experimental_protocol:
            number_of_uses_form = NumberOfUsesToInsertForm(request.POST or None,
                                                           initial={'number_of_uses_to_insert': number_of_uses})

        questionnaires_list = []
        specific_form = None
        duration_string = None

        if component_type == 'instruction':
            specific_form = InstructionForm(request.POST or None)
        elif component_type == 'stimulus':
            specific_form = StimulusForm(request.POST or None)
        elif component_type == 'eeg':
            specific_form = EEGForm(request.POST or None, initial={'experiment': experiment})
        elif component_type == 'questionnaire':
            questionnaires_list = Questionnaires().find_all_active_questionnaires()
        elif component_type == 'block':
            specific_form = BlockForm(request.POST or None, initial={'number_of_mandatory_components': None})
            duration_string = "0"

        if request.method == "POST":
            new_specific_component = None
            survey = None

            if component_type == 'questionnaire':
                new_specific_component = Questionnaire()

                try:
                    survey = Survey.objects.get(lime_survey_id=request.POST['questionnaire_selected'])
                except Survey.DoesNotExist:
                    survey = Survey()
                    survey.lime_survey_id = request.POST['questionnaire_selected']

            elif component_type == 'pause':
                new_specific_component = Pause()
            elif component_type == 'task':
                new_specific_component = Task()
            elif component_type == 'task_experiment':
                new_specific_component = TaskForTheExperimenter()
            elif specific_form.is_valid():
                new_specific_component = specific_form.save(commit=False)

            if component_form.is_valid():
                component = component_form.save(commit=False)
                new_specific_component.experiment = experiment
                new_specific_component.component_type = component_type
                new_specific_component.identification = component.identification
                new_specific_component.description = component.description
                new_specific_component.duration_value = component.duration_value
                new_specific_component.duration_unit = component.duration_unit
                # new_specific_component is not saved until later.

                # If this is a new component for creating the root of a group's experimental protocol, no
                # component_configuration has to be created.
                if is_configuring_new_experimental_protocol:
                    new_specific_component.save()
                    group.experimental_protocol = new_specific_component
                    group.save()

                    messages.success(request, _('Experimental protocol included successfully.'))

                    redirect_url = reverse("component_view",
                                           args=(path_of_the_components + delimiter + str(new_specific_component.id), ))
                    return HttpResponseRedirect(redirect_url)
                else:
                    if number_of_uses_form.is_valid():
                        if component_type == 'questionnaire':
                            survey.save()
                            new_specific_component.survey = survey

                        new_specific_component.save()
                        number_of_uses = number_of_uses_form.cleaned_data['number_of_uses_to_insert']

                        for i in range(number_of_uses):
                            new_configuration = ComponentConfiguration()
                            new_configuration.component = new_specific_component
                            new_configuration.parent = block

                            if position is not None:
                                if position == 'random':
                                    new_configuration.random_position = True
                                else:  # position == 'fixed'
                                    new_configuration.random_position = False

                            new_configuration.save()

                        if number_of_uses > 1:
                            messages.success(request, _('Steps included successfully.'))
                        else:
                            messages.success(request, _('Step included successfully.'))

                        redirect_url = reverse("component_view", args=(path_of_the_components, ))

                        return HttpResponseRedirect(redirect_url)

        context = {
            "back_cancel_url": back_cancel_url,
            "block": block,
            "block_duration": duration_string,
            "can_reuse": True,
            "component_form": component_form,
            "creating": True,
            "existing_component_list": existing_component_list,
            "experiment": experiment,
            "group": group,
            "is_configuring_new_experimental_protocol": is_configuring_new_experimental_protocol,
            "list_of_breadcrumbs": list_of_breadcrumbs,
            "number_of_uses_form": number_of_uses_form,
            "position": position,
            "questionnaires_list": questionnaires_list,
            "path_of_the_components": path_of_the_components,
            "specific_form": specific_form,
        }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def component_reuse(request, path_of_the_components, component_id):
    component_to_add = get_object_or_404(Component, pk=component_id)
    component_type = component_to_add.component_type
    existing_component_list, experiment, group, list_of_breadcrumbs, block, template_name, specific_form, \
        list_of_ids_of_components_and_configurations, back_cancel_url = \
        access_objects_for_add_new_and_reuse(component_type, path_of_the_components)

    if get_can_change(request.user, experiment.research_project):
        # Fixed or random
        position = get_position(request)

        # Number of uses to insert
        number_of_uses = get_number_of_uses(request)

        component_form = ComponentForm(request.POST or None, instance=component_to_add)
        # This is needed for the form to be able to validate the presence of a duration in a pause component only.
        component_form.component_type = component_type

        # Check if we are configuring a new experimental protocol
        is_configuring_new_experimental_protocol =\
            group is not None and len(list_of_ids_of_components_and_configurations) == 1

        number_of_uses_form = None

        if not is_configuring_new_experimental_protocol:
            number_of_uses_form = NumberOfUsesToInsertForm(request.POST or None,
                                                           initial={'number_of_uses_to_insert': number_of_uses})

        questionnaire_id = None
        questionnaire_title = None
        specific_form = None
        duration_string = None
        has_unlimited = None

        if component_type == 'instruction':
            instruction = get_object_or_404(Instruction, pk=component_to_add.id)
            specific_form = InstructionForm(request.POST or None, instance=instruction)
        elif component_type == 'stimulus':
            stimulus = get_object_or_404(Stimulus, pk=component_to_add.id)
            specific_form = StimulusForm(request.POST or None, instance=stimulus)
        elif component_type == 'eeg':
            eeg = get_object_or_404(EEG, pk=component_to_add.id)
            specific_form = EEGForm(request.POST or None, instance=eeg, initial={'experiment': experiment})
        elif component_type == 'questionnaire':
            questionnaire = get_object_or_404(Questionnaire, pk=component_to_add.id)
            questionnaire_details = Questionnaires().find_questionnaire_by_id(questionnaire.survey.lime_survey_id)

            if questionnaire_details:
                questionnaire_id = questionnaire_details['sid'],
                questionnaire_title = questionnaire_details['surveyls_title']
        elif component_type == 'block':
            sub_block = get_object_or_404(Block, pk=component_id)
            specific_form = BlockForm(request.POST or None, instance=sub_block)
            duration_value, has_unlimited = calculate_block_duration(sub_block)
            # Create a string converting to appropriate units
            duration_string = convert_to_string(duration_value)

        if component_type == 'questionnaire':
            for field in component_form.fields:
                component_form.fields[field].widget.attrs['disabled'] = True
        else:
            for field in component_form.fields:
                component_form.fields[field].widget.attrs['disabled'] = True

            if component_type != 'pause' and component_type != 'task' and \
                    component_type != 'task_experiment':
                for field in specific_form.fields:
                    specific_form.fields[field].widget.attrs['disabled'] = True

        if request.method == "POST":
            # If this is a reuse for creating the root of a group's experimental protocol, no component_configuration
            # has to be created.
            if is_configuring_new_experimental_protocol:
                group = Group.objects.get(id=path_of_the_components[1:])
                group.experimental_protocol = component_to_add
                group.save()

                redirect_url = reverse("component_view",
                                       args=(path_of_the_components + delimiter + str(component_to_add.id), ))

                messages.success(request, _('Step included successfully.'))
                return HttpResponseRedirect(redirect_url)
            else:
                if number_of_uses_form.is_valid():
                    number_of_uses = number_of_uses_form.cleaned_data['number_of_uses_to_insert']

                    for i in range(number_of_uses):
                        new_configuration = ComponentConfiguration()
                        new_configuration.component = component_to_add
                        new_configuration.parent = block

                        if position is not None:
                            if position == 'random':
                                new_configuration.random_position = True
                            else:  # position == 'fixed'
                                new_configuration.random_position = False

                        new_configuration.save()

                    redirect_url = reverse("component_view", args=(path_of_the_components, ))

                    if number_of_uses > 1:
                        messages.success(request, _('Steps included successfully.'))
                    else:
                        messages.success(request, _('Step included successfully.'))

                    return HttpResponseRedirect(redirect_url)

        context = {
            "back_cancel_url": back_cancel_url,
            "block": block,
            "block_duration": duration_string,
            "component_form": component_form,
            "creating": True,  # So that the "Use" button is shown.
            "existing_component_list": existing_component_list,
            "experiment": experiment,
            "group": group,
            "has_unlimited": has_unlimited,
            "is_configuring_new_experimental_protocol": is_configuring_new_experimental_protocol,
            "list_of_breadcrumbs": list_of_breadcrumbs,
            "number_of_uses_form": number_of_uses_form,
            "path_of_the_components": path_of_the_components,
            "position": position,
            "questionnaire_id": questionnaire_id,
            "questionnaire_title": questionnaire_title,
            "reusing": True,
            "specific_form": specific_form,
        }

        return render(request, template_name, context)
    else:
        raise PermissionDenied
