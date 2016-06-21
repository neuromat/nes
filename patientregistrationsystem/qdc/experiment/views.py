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
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, render_to_response
from django.utils.translation import ugettext as _

from neo import io

from experiment.models import Experiment, Subject, QuestionnaireResponse, SubjectOfGroup, Group, Component, \
    ComponentConfiguration, Questionnaire, Task, Stimulus, Pause, Instruction, Block, \
    TaskForTheExperimenter, ClassificationOfDiseases, ResearchProject, Keyword, EEG, EMG, EEGData, FileFormat, \
    EEGSetting, Equipment, Manufacturer, EEGMachine, EEGAmplifier, EEGElectrodeNet, DataConfigurationTree, \
    EEGMachineSetting, EEGAmplifierSetting, EEGSolutionSetting, EEGFilterSetting, EEGElectrodeLayoutSetting, \
    EEGFilterType, EEGSolution, EEGElectrodeLocalizationSystem, EEGElectrodeNetSystem, EEGElectrodePositionSetting, \
    EEGElectrodeModel, EEGElectrodePositionCollectionStatus, EEGCapSize, EEGElectrodeCap, EEGElectrodePosition, \
    Material, AdditionalData, EMGData
from experiment.forms import ExperimentForm, QuestionnaireResponseForm, FileForm, GroupForm, InstructionForm, \
    ComponentForm, StimulusForm, BlockForm, ComponentConfigurationForm, ResearchProjectForm, NumberOfUsesToInsertForm, \
    EEGDataForm, EEGSettingForm, EquipmentForm, EEGForm, EEGMachineForm, EEGMachineSettingForm, EEGAmplifierForm, \
    EEGAmplifierSettingForm, EEGSolutionForm, EEGFilterForm, EEGFilterSettingForm, \
    EEGElectrodeLocalizationSystemRegisterForm, \
    ManufacturerRegisterForm, EEGMachineRegisterForm, EEGAmplifierRegisterForm, EEGSolutionRegisterForm, \
    EEGFilterTypeRegisterForm, EEGElectrodeModelRegisterForm, MaterialRegisterForm, EEGElectrodeNETRegisterForm, \
    EEGElectrodePositionForm, EEGElectrodeCapRegisterForm, EEGCapSizeRegisterForm, AdditionalDataForm, EMGDataForm


from patient.models import Patient, QuestionnaireResponse as PatientQuestionnaireResponse

from survey.abc_search_engine import Questionnaires
from survey.models import Survey
from survey.views import get_questionnaire_responses, check_limesurvey_access, create_list_of_trees, \
    get_questionnaire_language

permission_required = partial(permission_required, raise_exception=True)

icon_class = {
    'block': 'glyphicon glyphicon-th-large',
    'instruction': 'glyphicon glyphicon-comment',
    'pause': 'glyphicon glyphicon-time',
    'questionnaire': 'glyphicon glyphicon-list-alt',
    'stimulus': 'glyphicon glyphicon-headphones',
    'task': 'glyphicon glyphicon-check',
    'task_experiment': 'glyphicon glyphicon-wrench',
    'eeg': 'glyphicon glyphicon-flash',
    'emg': 'glyphicon glyphicon-stats'
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

    context = {"research_project_form": research_project_form,
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

    context = {"can_change": get_can_change(request.user, research_project),
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

        context = {"research_project": research_project,
                   "research_project_form": research_project_form,
                   "editing": True
                   }

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

        context = {"research_project": ResearchProject.objects.get(id=research_project_id),
                   "experiment_form": experiment_form,
                   "creating": True,
                   "editing": True
                   }

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

    context = {"can_change": get_can_change(request.user, experiment.research_project),
               "experiment": experiment,
               "experiment_form": experiment_form,
               "group_list": group_list,
               "eeg_setting_list": eeg_setting_list,
               "research_project": experiment.research_project
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

        context = {"research_project": experiment.research_project,
                   "experiment_form": experiment_form,
                   "editing": True,
                   "group_list": group_list,
                   "experiment": experiment
                   }

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

        context = {"group_form": group_form,
                   "creating": True,
                   "editing": True,
                   "experiment": experiment
                   }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


def recursively_create_list_of_questionnaires_and_statistics(block_id,
                                                             list_of_questionnaires_configuration,
                                                             surveys,
                                                             num_participants,
                                                             language_code):
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

        language = get_questionnaire_language(surveys, questionnaire.survey.lime_survey_id, language_code)
        list_of_questionnaires_configuration.append({
            "survey_title": surveys.get_survey_title(questionnaire.survey.lime_survey_id, language),
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
            num_participants,
            language_code)

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
            SubjectOfGroup.objects.filter(group_id=group_id).count(),
            request.LANGUAGE_CODE)

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

    context = {"can_change": can_change,
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

        context = {"group_form": group_form,
                   "editing": True,
                   "experiment": group.experiment,
                   "group": group
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

        context = {"eeg_setting_form": eeg_setting_form,
                   "creating": True,
                   "editing": True,
                   "experiment": experiment
                   }

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

                setting_to_be_deleted = None

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
                if setting_to_be_deleted:
                    setting_to_be_deleted.delete()

                messages.success(request, _('Setting was removed successfully.'))

                redirect_url = reverse("eeg_setting_view", args=(eeg_setting.id,))
                return HttpResponseRedirect(redirect_url)

    equipment_type_choices = Equipment.EQUIPMENT_TYPES

    context = {"can_change": can_change,
               "eeg_setting_form": eeg_setting_form,
               "experiment": eeg_setting.experiment,
               "eeg_setting": eeg_setting,
               "editing": False,
               "equipment_type_choices": equipment_type_choices
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

        context = {"eeg_setting_form": eeg_setting_form,
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
        filter_list = None
        filter_selected = None

        creating = False

        equipment_selected = None

        localization_system_list = None
        localization_system_selected = None

        if request.method == "POST":
            if request.POST['action'] == "save":

                if eeg_setting_type == "eeg_machine" \
                        and 'equipment_selection' in request.POST \
                        and 'number_of_channels_used' in request.POST:

                    eeg_machine = EEGMachine.objects.get(pk=request.POST['equipment_selection'])

                    eeg_machine_setting = EEGMachineSetting()
                    eeg_machine_setting.eeg_machine = eeg_machine
                    eeg_machine_setting.number_of_channels_used = request.POST['number_of_channels_used']
                    eeg_machine_setting.eeg_setting = eeg_setting
                    eeg_machine_setting.save()

                    messages.success(request, _('EEG machine setting created successfully.'))

                    redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

                if eeg_setting_type == "eeg_amplifier" \
                        and 'equipment_selection' in request.POST \
                        and 'gain' in request.POST:

                    eeg_amplifier = EEGAmplifier.objects.get(pk=request.POST['equipment_selection'])

                    eeg_amplifier_setting = EEGAmplifierSetting()
                    eeg_amplifier_setting.eeg_amplifier = eeg_amplifier
                    eeg_amplifier_setting.gain = request.POST['gain']
                    eeg_amplifier_setting.eeg_setting = eeg_setting
                    eeg_amplifier_setting.save()

                    messages.success(request, _('EEG amplifier setting created sucessfully.'))

                    redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

                if eeg_setting_type == "eeg_solution" and 'solution_selection' in request.POST:

                    eeg_solution = EEGSolution.objects.get(pk=request.POST['solution_selection'])

                    eeg_solution_setting = EEGSolutionSetting()
                    eeg_solution_setting.eeg_solution = eeg_solution
                    eeg_solution_setting.eeg_setting = eeg_setting
                    eeg_solution_setting.save()

                    messages.success(request, _('EEG solution setting created sucessfully.'))

                    redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

                if 'filter_selection' in request.POST:
                    eeg_filter = EEGFilterType.objects.get(pk=request.POST['filter_selection'])

                    eeg_filter_setting = EEGFilterSetting()
                    eeg_filter_setting.eeg_filter_type = eeg_filter
                    eeg_filter_setting.high_pass = request.POST['high_pass']
                    eeg_filter_setting.low_pass = request.POST['low_pass']
                    eeg_filter_setting.order = request.POST['order']
                    eeg_filter_setting.eeg_setting = eeg_setting
                    eeg_filter_setting.save()

                    messages.success(request, _('EEG filter setting created sucessfully.'))

                    redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

                if eeg_setting_type == "eeg_electrode_net_system" \
                        and 'equipment_selection' in request.POST \
                        and 'localization_system_selection' in request.POST:

                    eeg_electrode_net = \
                        EEGElectrodeNet.objects.get(pk=request.POST['equipment_selection'])

                    eeg_electrode_localization_system = \
                        EEGElectrodeLocalizationSystem.objects.get(pk=request.POST['localization_system_selection'])

                    eeg_electrode_net_system = EEGElectrodeNetSystem.objects.get(
                        eeg_electrode_net=eeg_electrode_net,
                        eeg_electrode_localization_system=eeg_electrode_localization_system)

                    eeg_electrode_layout_setting = EEGElectrodeLayoutSetting()
                    eeg_electrode_layout_setting.eeg_setting = eeg_setting
                    eeg_electrode_layout_setting.eeg_electrode_net_system = eeg_electrode_net_system
                    # eeg_electrode_layout_setting.number_of_electrodes = request.POST['number_of_electrodes']
                    eeg_electrode_layout_setting.save()

                    if eeg_electrode_localization_system.electrode_positions:
                        for position in eeg_electrode_localization_system.electrode_positions.all():
                            new_position_setting = EEGElectrodePositionSetting()
                            new_position_setting.eeg_electrode_layout_setting = eeg_electrode_layout_setting
                            new_position_setting.eeg_electrode_position = position
                            new_position_setting.used = True
                            new_position_setting.electrode_model = eeg_electrode_net.electrode_model_default
                            new_position_setting.save()

                    messages.info(request, _('Now you can set each electrode position.'))

                    messages.success(request, _('EEG electrode net system setting created sucessfully.'))

                    redirect_url = reverse("eeg_electrode_position_setting", args=(eeg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

        if eeg_setting_type == "eeg_machine":

            if hasattr(eeg_setting, 'eeg_machine_setting'):

                eeg_machine_setting = EEGMachineSetting.objects.get(eeg_setting_id=eeg_setting_id)

                selection_form = EEGMachineForm(request.POST or None, instance=eeg_machine_setting.eeg_machine)
                setting_form = EEGMachineSettingForm(request.POST or None, instance=eeg_machine_setting)
                equipment_selected = eeg_machine_setting.eeg_machine

                for field in setting_form.fields:
                    setting_form.fields[field].widget.attrs['disabled'] = True

            else:
                creating = True

                selection_form = EEGMachineForm(request.POST or None)
                setting_form = EEGMachineSettingForm(request.POST or None)

        if eeg_setting_type == "eeg_amplifier":

            if hasattr(eeg_setting, 'eeg_amplifier_setting'):

                eeg_amplifier_setting = EEGAmplifierSetting.objects.get(eeg_setting_id=eeg_setting_id)

                selection_form = EEGAmplifierForm(request.POST or None, instance=eeg_amplifier_setting.eeg_amplifier)
                setting_form = EEGAmplifierSettingForm(request.POST or None, instance=eeg_amplifier_setting)
                equipment_selected = eeg_amplifier_setting.eeg_amplifier

                for field in setting_form.fields:
                    setting_form.fields[field].widget.attrs['disabled'] = True

            else:
                creating = True

                selection_form = EEGAmplifierForm(request.POST or None)
                setting_form = EEGAmplifierSettingForm(request.POST or None)

        if eeg_setting_type == "eeg_solution":

            if hasattr(eeg_setting, 'eeg_solution_setting'):

                eeg_solution_setting = EEGSolutionSetting.objects.get(eeg_setting_id=eeg_setting_id)

                selection_form = EEGSolutionForm(request.POST or None, instance=eeg_solution_setting.eeg_solution)
                solution_selected = eeg_solution_setting.eeg_solution

            else:
                creating = True

                selection_form = EEGSolutionForm(request.POST or None)

        if eeg_setting_type == "eeg_filter":

            if hasattr(eeg_setting, 'eeg_filter_setting'):

                eeg_filter_setting = EEGFilterSetting.objects.get(eeg_setting_id=eeg_setting_id)

                selection_form = EEGFilterForm(request.POST or None, instance=eeg_filter_setting.eeg_filter_type)
                setting_form = EEGFilterSettingForm(request.POST or None, instance=eeg_filter_setting)
                filter_selected = eeg_filter_setting.eeg_filter_type

                for field in setting_form.fields:
                    setting_form.fields[field].widget.attrs['disabled'] = True

            else:
                creating = True

                selection_form = EEGFilterForm(request.POST or None)
                setting_form = EEGFilterSettingForm(request.POST or None)

        if eeg_setting_type == "eeg_electrode_net_system":

            localization_system_list = EEGElectrodeLocalizationSystem.objects.filter(
                set_of_electrode_net_system__isnull=False)

            if hasattr(eeg_setting, 'eeg_electrode_layout_setting'):

                setting = eeg_setting.eeg_electrode_layout_setting

                equipment_selected = setting.eeg_electrode_net_system.eeg_electrode_net
                localization_system_selected = setting.eeg_electrode_net_system.eeg_electrode_localization_system

                # selection_form = EEGElectrodeLocalizationSystemForm(
                #     request.POST or None,
                #     initial={
                #         'number_of_electrodes':
                #         setting.eeg_electrode_net_system.eeg_electrode_localization_system.number_of_electrodes})

                # setting_form = EEGElectrodeLayoutSettingForm(
                #     request.POST or None,
                #     initial={'number_of_electrodes': setting.number_of_electrodes})

                # for field in setting_form.fields:
                #     setting_form.fields[field].widget.attrs['disabled'] = True

            else:
                creating = True

                # selection_form = EEGElectrodeLocalizationSystemForm(request.POST or None)
                # setting_form = EEGElectrodeLayoutSettingForm(request.POST or None)

        # Settings related to equipment
        if eeg_setting_type in ["eeg_machine", "eeg_amplifier", "eeg_electrode_net_system"]:

            equipment_type = "eeg_electrode_net" if eeg_setting_type == "eeg_electrode_net_system" else eeg_setting_type

            equipment_list = Equipment.objects.filter(equipment_type=equipment_type)
            manufacturer_list = \
                Manufacturer.objects.filter(set_of_equipment__equipment_type=equipment_type).distinct()

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
            filter_list = EEGFilterType.objects.all()

            if creating:
                equipment_form = EEGFilterForm(request.POST or None)
            else:
                equipment_form = EEGFilterForm(request.POST or None, instance=filter_selected)

        context = {"creating": creating,
                   "editing": False,
                   "tab": "0",

                   "can_change": True,

                   "eeg_setting_type": eeg_setting_type,

                   "eeg_setting": eeg_setting,
                   "equipment_selected": equipment_selected,
                   "solution_selected": solution_selected,
                   "filter_selected": filter_selected,

                   "manufacturer_list": manufacturer_list,
                   "equipment_list": equipment_list,
                   "solution_list": solution_list,
                   "filter_list": filter_list,
                   "equipment_form": equipment_form,

                   "selection_form": selection_form,
                   "setting_form": setting_form,

                   "localization_system_list": localization_system_list,
                   "localization_system_selected": localization_system_selected
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
        filter_list = None
        filter_selected = None

        equipment_selected = None

        localization_system_list = None
        localization_system_selected = None

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

                if 'filter_selection' in request.POST:
                    eeg_filter = EEGFilterType.objects.get(pk=request.POST['filter_selection'])

                    eeg_filter_setting = eeg_setting.eeg_filter_setting

                    eeg_filter_setting.eeg_filter_type = eeg_filter
                    eeg_filter_setting.high_pass = request.POST['high_pass']
                    eeg_filter_setting.low_pass = request.POST['low_pass']
                    eeg_filter_setting.order = request.POST['order']
                    eeg_filter_setting.eeg_setting = eeg_setting
                    eeg_filter_setting.save()

                    messages.success(request, _('EEG filter setting updated sucessfully.'))

                    redirect_url = reverse("view_eeg_setting_type", args=(eeg_setting_id, eeg_setting_type))
                    return HttpResponseRedirect(redirect_url)

                if eeg_setting_type == "eeg_electrode_net_system" \
                        and 'equipment_selection' in request.POST \
                        and 'localization_system_selection' in request.POST:

                    eeg_electrode_net = \
                        EEGElectrodeNet.objects.get(pk=request.POST['equipment_selection'])

                    eeg_electrode_localization_system = \
                        EEGElectrodeLocalizationSystem.objects.get(pk=request.POST['localization_system_selection'])

                    eeg_electrode_net_system = EEGElectrodeNetSystem.objects.get(
                        eeg_electrode_net=eeg_electrode_net,
                        eeg_electrode_localization_system=eeg_electrode_localization_system)

                    # get the current layout setting
                    eeg_electrode_layout_setting = eeg_setting.eeg_electrode_layout_setting

                    # if the electrode localization system changed
                    if eeg_electrode_layout_setting.eeg_electrode_net_system.eeg_electrode_localization_system != \
                            eeg_electrode_localization_system:
                        # remove all current position settings
                        for position in eeg_electrode_layout_setting.positions_setting.all():
                            position.delete()

                    eeg_electrode_layout_setting.eeg_electrode_net_system = eeg_electrode_net_system
                    # eeg_electrode_layout_setting.number_of_electrodes = request.POST['number_of_electrodes']
                    eeg_electrode_layout_setting.save()

                    if eeg_electrode_localization_system.electrode_positions:
                        for position in eeg_electrode_localization_system.electrode_positions.all():
                            # if not exists a position setting
                            position_setting = \
                                EEGElectrodePositionSetting.objects.filter(
                                    eeg_electrode_layout_setting=eeg_electrode_layout_setting,
                                    eeg_electrode_position=position)

                            if not position_setting:
                                new_position_setting = EEGElectrodePositionSetting()
                                new_position_setting.eeg_electrode_layout_setting = eeg_electrode_layout_setting
                                new_position_setting.eeg_electrode_position = position
                                new_position_setting.used = True
                                new_position_setting.electrode_model = eeg_electrode_net.electrode_model_default
                                new_position_setting.save()

                    messages.success(request, _('EEG electrode net system setting updated sucessfully.'))

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

        if eeg_setting_type == "eeg_filter":
            eeg_filter_setting = eeg_setting.eeg_filter_setting

            filter_selected = eeg_filter_setting.eeg_filter_type

            selection_form = EEGFilterForm(request.POST or None, instance=eeg_filter_setting.eeg_filter_type)
            setting_form = EEGFilterSettingForm(request.POST or None, instance=eeg_filter_setting)

        if eeg_setting_type == "eeg_solution":
            solution_list = EEGSolution.objects.all()
            manufacturer_list = Manufacturer.objects.filter(set_of_solution__isnull=False).distinct()

            equipment_form = EEGSolutionForm(request.POST or None, instance=solution_selected)

        if eeg_setting_type == "eeg_filter":
            filter_list = EEGFilterType.objects.all()

            equipment_form = EEGFilterForm(request.POST or None, instance=filter_selected)

        if eeg_setting_type == "eeg_electrode_net_system":

            localization_system_list = EEGElectrodeLocalizationSystem.objects.filter(
                set_of_electrode_net_system__isnull=False)

            setting = eeg_setting.eeg_electrode_layout_setting

            # selection_form = EEGElectrodeLocalizationSystemForm(
            #     request.POST or None,
            #     instance=setting.eeg_electrode_net_system.eeg_electrode_localization_system)
            # setting_form = EEGElectrodeLayoutSettingForm(request.POST or None, instance=setting)

            equipment_selected = setting.eeg_electrode_net_system.eeg_electrode_net
            localization_system_selected = setting.eeg_electrode_net_system.eeg_electrode_localization_system

        # Settings related to equipment
        if eeg_setting_type in ["eeg_machine", "eeg_amplifier", "eeg_electrode_net_system"]:

            equipment_type = "eeg_electrode_net" if eeg_setting_type == "eeg_electrode_net_system" else eeg_setting_type
            equipment_list = Equipment.objects.filter(equipment_type=equipment_type)
            manufacturer_list = Manufacturer.objects.filter(
                set_of_equipment__equipment_type=equipment_type).distinct()

            equipment_form = EquipmentForm(request.POST or None, instance=equipment_selected)

        context = {"creating": False,
                   "editing": True,
                   "tab": "0",

                   "can_change": True,

                   "eeg_setting_type": eeg_setting_type,

                   "eeg_setting": eeg_setting,
                   "equipment_selected": equipment_selected,
                   "solution_selected": solution_selected,
                   "filter_selected": filter_selected,

                   "solution_list": solution_list,
                   "manufacturer_list": manufacturer_list,
                   "equipment_list": equipment_list,
                   "filter_list": filter_list,
                   "equipment_form": equipment_form,

                   "selection_form": selection_form,
                   "setting_form": setting_form,

                   "localization_system_list": localization_system_list,
                   "localization_system_selected": localization_system_selected
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
    return HttpResponse(json_equipment, content_type='application/json')


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
def get_json_filter_attributes(request, filter_id):

    filter_type = get_object_or_404(EEGFilterType, pk=filter_id)

    response_data = {
        'description': filter_type.description,
    }

    return HttpResponse(json.dumps(response_data), content_type='application/json')


# @login_required
# @permission_required('experiment.change_experiment')
# def get_json_eeg_localization_system_attributes(request, eeg_localization_system_id):
#
#     eeg_localization_system = get_object_or_404(EEGElectrodeLocalizationSystem, pk=eeg_localization_system_id)
#
#     response_data = {
#         'number_of_electrodes': eeg_localization_system.number_of_electrodes,
#     }
#
#     return HttpResponse(json.dumps(response_data), content_type='application/json')


@login_required
@permission_required('experiment.change_experiment')
def get_localization_system_by_electrode_net(request, equipment_id):
    list_of_localization_system = EEGElectrodeLocalizationSystem.objects.filter(
        set_of_electrode_net_system__eeg_electrode_net_id=equipment_id)
    json_equipment = serializers.serialize("json", list_of_localization_system)
    return HttpResponse(json_equipment, content_type='application/json')


@login_required
@permission_required('experiment.change_experiment')
def get_equipment_by_manufacturer_and_localization_system(request, manufacturer_id, eeg_localization_system_id):
    set_of_net_system = EEGElectrodeNetSystem.objects.filter(
        eeg_electrode_localization_system_id=eeg_localization_system_id)
    list_of_electrode_net = [item.eeg_electrode_net_id for item in set_of_net_system]
    # equipment = Equipment.objects.in_bulk(list_of_electrode_net)
    equipment = Equipment.objects.filter(id__in=list_of_electrode_net)
    if manufacturer_id != "0":
        equipment = equipment.filter(manufacturer_id=manufacturer_id)
    json_equipment = serializers.serialize("json", equipment)
    return HttpResponse(json_equipment, content_type='application/json')


@login_required
@permission_required('experiment.change_experiment')
def eeg_electrode_position_setting(request, eeg_setting_id,
                                   template_name="experiment/eeg_setting_electrode_position_status.html"):

    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    if get_can_change(request.user, eeg_setting.experiment.research_project):

        positions = []
        for position_setting in eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
            positions.append({
                'id': 'position_status_' + str(position_setting.id),
                'position': position_setting.eeg_electrode_position.name,
                'x': position_setting.eeg_electrode_position.coordinate_x,
                'y': position_setting.eeg_electrode_position.coordinate_y
            })

        context = {"tab": "1",
                   "editing": False,
                   "eeg_setting": eeg_setting,
                   "json_list": json.dumps(positions),
                   "number_of_used_electrodes": number_of_used_positions(eeg_setting)
                   }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


def number_of_used_positions(eeg_setting):
    return EEGElectrodePositionSetting.objects.filter(
        eeg_electrode_layout_setting=eeg_setting.eeg_electrode_layout_setting, used=True).count()


@login_required
@permission_required('experiment.change_experiment')
def edit_eeg_electrode_position_setting(request, eeg_setting_id,
                                        template_name="experiment/eeg_setting_electrode_position_status.html"):

    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    if get_can_change(request.user, eeg_setting.experiment.research_project):

        positions = []
        for position_setting in eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
            positions.append({
                'id': 'position_status_' + str(position_setting.id),
                'position': position_setting.eeg_electrode_position.name,
                'x': position_setting.eeg_electrode_position.coordinate_x,
                'y': position_setting.eeg_electrode_position.coordinate_y
            })

        if request.method == "POST":
            if request.POST['action'] == "save":
                for position_setting in eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
                    position_setting.used = 'position_status_' + str(position_setting.id) in request.POST
                    position_setting.save()

                messages.success(request, _('Setting saved successfully.'))

                redirect_url = reverse("eeg_electrode_position_setting", args=(eeg_setting_id,))
                return HttpResponseRedirect(redirect_url)

        context = {"tab": "1",
                   "editing": True,
                   "eeg_setting": eeg_setting,
                   "json_list": json.dumps(positions),
                   "number_of_used_electrodes": number_of_used_positions(eeg_setting)
                   }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def eeg_electrode_position_setting_model(request, eeg_setting_id,
                                         template_name="experiment/eeg_setting_electrode_position_status_model.html"):

    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    if get_can_change(request.user, eeg_setting.experiment.research_project):

        eeg_electrode_model_list = EEGElectrodeModel.objects.all()

        context = {"tab": "2",
                   "editing": False,
                   "eeg_setting": eeg_setting,
                   "eeg_electrode_model_list": eeg_electrode_model_list
                   }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def edit_eeg_electrode_position_setting_model(
        request, eeg_setting_id, template_name="experiment/eeg_setting_electrode_position_status_model.html"):

    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    if get_can_change(request.user, eeg_setting.experiment.research_project):

        eeg_electrode_model_list = EEGElectrodeModel.objects.all()

        if request.method == "POST":
            if request.POST['action'] == "save":

                for position_setting in eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
                    electrode_model_id = int(request.POST['electrode_model_' + str(position_setting.id)])
                    position_setting.electrode_model_id = electrode_model_id
                    position_setting.save()

                messages.success(request, _('Setting saved successfully.'))

                redirect_url = reverse("eeg_electrode_position_setting_model", args=(eeg_setting_id,))
                return HttpResponseRedirect(redirect_url)

        context = {"tab": "2",
                   "editing": True,
                   "eeg_setting": eeg_setting,
                   "eeg_electrode_model_list": eeg_electrode_model_list
                   }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


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

        context = {"creating": False,
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


@login_required
@permission_required('experiment.add_equipment')
def manufacturer_list(request, template_name="experiment/manufacturer_list.html"):
    return render(request, template_name, {"equipments": Manufacturer.objects.order_by('name')})


@login_required
@permission_required('experiment.add_manufacturer')
def manufacturer_create(request, template_name="experiment/manufacturer_register.html"):

    manufacturer_form = ManufacturerRegisterForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if manufacturer_form.is_valid():

                manufacturer_added = manufacturer_form.save(commit=False)
                manufacturer_added.save()

                messages.success(request, _('Manufacturer created successfully.'))
                redirect_url = reverse("manufacturer_view", args=(manufacturer_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))

        else:
            messages.warning(request, _('Action not available.'))

    context = {"equipment_form": manufacturer_form,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_manufacturer')
def manufacturer_update(request, manufacturer_id, template_name="experiment/manufacturer_register.html"):
    manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)

    manufacturer_form = ManufacturerRegisterForm(request.POST or None, instance=manufacturer)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if manufacturer_form.is_valid():
                if manufacturer_form.has_changed():
                    manufacturer_form.save()
                    messages.success(request, _('Manufacturer updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("manufacturer_view", args=(manufacturer.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"equipment": manufacturer,
               "equipment_form": manufacturer_form,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_manufacturer')
def manufacturer_view(request, manufacturer_id, template_name="experiment/manufacturer_register.html"):
    manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)

    manufacturer_form = ManufacturerRegisterForm(request.POST or None, instance=manufacturer)

    for field in manufacturer_form.fields:
        manufacturer_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            try:
                manufacturer.delete()
                messages.success(request, _('Manufacturer removed successfully.'))
                return redirect('manufacturer_list')
            except ProtectedError:
                messages.error(request, _("Error trying to delete manufacturer."))
                redirect_url = reverse("manufacturer_view", args=(manufacturer_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"can_change": True,
               "equipment": manufacturer,
               "equipment_form": manufacturer_form
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_equipment')
def eegmachine_list(request, template_name="experiment/eegmachine_list.html"):
    return render(request, template_name, {"equipments": EEGMachine.objects.all().order_by('identification')})


@login_required
@permission_required('experiment.add_eegmachine')
def eegmachine_create(request, template_name="experiment/eegmachine_register.html"):

    eegmachine_form = EEGMachineRegisterForm(request.POST or None, initial={'equipment_type': 'eeg_machine'})

    if request.method == "POST":

        if request.POST['action'] == "save":

            if eegmachine_form.is_valid():

                eegmachine_added = eegmachine_form.save(commit=False)
                eegmachine_added.equipment_type = 'eeg_machine'
                eegmachine_added.save()

                messages.success(request, _('EEG machine created successfully.'))
                redirect_url = reverse("eegmachine_view", args=(eegmachine_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))

        else:
            messages.warning(request, _('Action not available.'))

    context = {"equipment_form": eegmachine_form,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_eegmachine')
def eegmachine_update(request, eegmachine_id, template_name="experiment/eegmachine_register.html"):

    eegmachine = get_object_or_404(EEGMachine, pk=eegmachine_id)
    # eegmachine.equipment_type = 'eeg_machine'

    eegmachine_form = EEGMachineRegisterForm(request.POST or None, instance=eegmachine)

    # eegmachine_form.fields['equipment_type'].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "save":
            if eegmachine_form.is_valid():
                if eegmachine_form.has_changed():
                    eegmachine_form.save()
                    messages.success(request, _('EEG machine updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("eegmachine_view", args=(eegmachine.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"equipment": eegmachine,
               "equipment_form": eegmachine_form,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_eegmachine')
def eegmachine_view(request, eegmachine_id, template_name="experiment/eegmachine_register.html"):
    eegmachine = get_object_or_404(EEGMachine, pk=eegmachine_id)

    eegmachine_form = EEGMachineRegisterForm(request.POST or None, instance=eegmachine)

    for field in eegmachine_form.fields:
        eegmachine_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            try:
                eegmachine.delete()
                messages.success(request, _('EEG machine removed successfully.'))
                return redirect('eegmachine_list')
            except ProtectedError:
                messages.error(request, _("Error trying to delete eegmachine."))
                redirect_url = reverse("eegmachine_view", args=(eegmachine_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"can_change": True,
               "equipment": eegmachine,
               "equipment_form": eegmachine_form
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_equipment')
def eegamplifier_list(request, template_name="experiment/eegamplifier_list.html"):
    return render(request, template_name, {"equipments": EEGAmplifier.objects.all().order_by('identification')})


@login_required
@permission_required('experiment.add_eegamplifier')
def eegamplifier_create(request, template_name="experiment/eegamplifier_register.html"):

    eegamplifier_form = EEGAmplifierRegisterForm(request.POST or None, initial={'equipment_type': 'eeg_amplifier'})

    if request.method == "POST":

        if request.POST['action'] == "save":

            if eegamplifier_form.is_valid():

                eegamplifier_added = eegamplifier_form.save(commit=False)
                eegamplifier_added.equipment_type = 'eeg_amplifier'
                eegamplifier_added.save()

                messages.success(request, _('EEG amplifier created successfully.'))
                redirect_url = reverse("eegamplifier_view", args=(eegamplifier_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))

        else:
            messages.warning(request, _('Action not available.'))

    context = {"equipment_form": eegamplifier_form,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_eegamplifier')
def eegamplifier_update(request, eegamplifier_id, template_name="experiment/eegamplifier_register.html"):
    eegamplifier = get_object_or_404(EEGAmplifier, pk=eegamplifier_id)

    eegamplifier_form = EEGAmplifierRegisterForm(request.POST or None, instance=eegamplifier)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if eegamplifier_form.is_valid():
                if eegamplifier_form.has_changed():
                    eegamplifier_form.save()
                    messages.success(request, _('EEG amplifier updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("eegamplifier_view", args=(eegamplifier.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"equipment": eegamplifier,
               "equipment_form": eegamplifier_form,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_eegamplifier')
def eegamplifier_view(request, eegamplifier_id, template_name="experiment/eegamplifier_register.html"):
    eegamplifier = get_object_or_404(EEGAmplifier, pk=eegamplifier_id)

    eegamplifier_form = EEGAmplifierRegisterForm(request.POST or None, instance=eegamplifier)

    for field in eegamplifier_form.fields:
        eegamplifier_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            try:
                eegamplifier.delete()
                messages.success(request, _('EEG amplifier removed successfully.'))
                return redirect('eegamplifier_list')
            except ProtectedError:
                messages.error(request, _("Error trying to delete eegamplifier."))
                redirect_url = reverse("eegamplifier_view", args=(eegamplifier_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"can_change": True,
               "equipment": eegamplifier,
               "equipment_form": eegamplifier_form
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_equipment')
def eegsolution_list(request, template_name="experiment/eegsolution_list.html"):
    return render(request, template_name, {"equipments": EEGSolution.objects.all().order_by('name')})


@login_required
@permission_required('experiment.add_eegsolution')
def eegsolution_create(request, template_name="experiment/eegsolution_register.html"):

    eegsolution_form = EEGSolutionRegisterForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if eegsolution_form.is_valid():

                eegsolution_added = eegsolution_form.save(commit=False)
                eegsolution_added.save()

                messages.success(request, _('EEG solution created successfully.'))
                redirect_url = reverse("eegsolution_view", args=(eegsolution_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))

        else:
            messages.warning(request, _('Action not available.'))

    context = {"equipment_form": eegsolution_form,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_eegsolution')
def eegsolution_update(request, eegsolution_id, template_name="experiment/eegsolution_register.html"):
    eegsolution = get_object_or_404(EEGSolution, pk=eegsolution_id)
    eegsolution.equipment_type = 'eeg_solution'

    eegsolution_form = EEGSolutionRegisterForm(request.POST or None, instance=eegsolution)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if eegsolution_form.is_valid():
                if eegsolution_form.has_changed():

                    eegsolution_form.save()
                    messages.success(request, _('EEG solution updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("eegsolution_view", args=(eegsolution.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"equipment": eegsolution,
               "equipment_form": eegsolution_form,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_eegsolution')
def eegsolution_view(request, eegsolution_id, template_name="experiment/eegsolution_register.html"):
    eegsolution = get_object_or_404(EEGSolution, pk=eegsolution_id)

    eegsolution_form = EEGSolutionRegisterForm(request.POST or None, instance=eegsolution)

    for field in eegsolution_form.fields:
        eegsolution_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            try:
                eegsolution.delete()
                messages.success(request, _('EEG solution removed successfully.'))
                return redirect('eegsolution_list')
            except ProtectedError:
                messages.error(request, _("Error trying to delete eegsolution."))
                redirect_url = reverse("eegsolution_view", args=(eegsolution_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"can_change": True,
               "equipment": eegsolution,
               "equipment_form": eegsolution_form
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_equipment')
def eegfiltertype_list(request, template_name="experiment/eegfiltertype_list.html"):
    return render(request, template_name, {"equipments": EEGFilterType.objects.all().order_by('name')})


@login_required
@permission_required('experiment.add_eegfiltertype')
def eegfiltertype_create(request, template_name="experiment/eegfiltertype_register.html"):

    eegfiltertype_form = EEGFilterTypeRegisterForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if eegfiltertype_form.is_valid():

                eegfiltertype_added = eegfiltertype_form.save(commit=False)
                eegfiltertype_added.save()

                messages.success(request, _('EEG filter type created successfully.'))
                redirect_url = reverse("eegfiltertype_view", args=(eegfiltertype_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))

        else:
            messages.warning(request, _('Action not available.'))

    context = {"equipment_form": eegfiltertype_form,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_eegfiltertype')
def eegfiltertype_update(request, eegfiltertype_id, template_name="experiment/eegfiltertype_register.html"):
    eegfiltertype = get_object_or_404(EEGFilterType, pk=eegfiltertype_id)

    eegfiltertype_form = EEGFilterTypeRegisterForm(request.POST or None, instance=eegfiltertype)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if eegfiltertype_form.is_valid():
                if eegfiltertype_form.has_changed():

                    eegfiltertype_form.save()
                    messages.success(request, _('EEG filter type updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("eegfiltertype_view", args=(eegfiltertype.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"equipment": eegfiltertype,
               "equipment_form": eegfiltertype_form,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_eegfiltertype')
def eegfiltertype_view(request, eegfiltertype_id, template_name="experiment/eegfiltertype_register.html"):
    eegfiltertype = get_object_or_404(EEGFilterType, pk=eegfiltertype_id)

    eegfiltertype_form = EEGFilterTypeRegisterForm(request.POST or None, instance=eegfiltertype)

    for field in eegfiltertype_form.fields:
        eegfiltertype_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            try:
                eegfiltertype.delete()
                messages.success(request, _('EEG filter type removed successfully.'))
                return redirect('eegfiltertype_list')
            except ProtectedError:
                messages.error(request, _("Error trying to delete EEG filter type."))
                redirect_url = reverse("eegfiltertype_view", args=(eegfiltertype_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"can_change": True,
               "equipment": eegfiltertype,
               "equipment_form": eegfiltertype_form
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_equipment')
def eegelectrodemodel_list(request, template_name="experiment/eegelectrodemodel_list.html"):
    return render(request, template_name, {"equipments": EEGElectrodeModel.objects.all().order_by('name')})


@login_required
@permission_required('experiment.add_eegelectrodemodel')
def eegelectrodemodel_create(request, template_name="experiment/eegelectrodemodel_register.html"):

    eegelectrodemodel_form = EEGElectrodeModelRegisterForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if eegelectrodemodel_form.is_valid():

                eegelectrodemodel_added = eegelectrodemodel_form.save(commit=False)
                eegelectrodemodel_added.save()

                messages.success(request, _('EEG electrode model created successfully.'))
                redirect_url = reverse("eegelectrodemodel_view", args=(eegelectrodemodel_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))

        else:
            messages.warning(request, _('Action not available.'))

    context = {"equipment_form": eegelectrodemodel_form,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_eegelectrodemodel')
def eegelectrodemodel_update(request, eegelectrodemodel_id, template_name="experiment/eegelectrodemodel_register.html"):
    eegelectrodemodel = get_object_or_404(EEGElectrodeModel, pk=eegelectrodemodel_id)

    eegelectrodemodel_form = EEGElectrodeModelRegisterForm(request.POST or None, instance=eegelectrodemodel)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if eegelectrodemodel_form.is_valid():
                if eegelectrodemodel_form.has_changed():

                    eegelectrodemodel_form.save()
                    messages.success(request, _('EEG electrode model updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("eegelectrodemodel_view", args=(eegelectrodemodel.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"equipment": eegelectrodemodel,
               "equipment_form": eegelectrodemodel_form,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_eegelectrodemodel')
def eegelectrodemodel_view(request, eegelectrodemodel_id, template_name="experiment/eegelectrodemodel_register.html"):
    eegelectrodemodel = get_object_or_404(EEGElectrodeModel, pk=eegelectrodemodel_id)

    eegelectrodemodel_form = EEGElectrodeModelRegisterForm(request.POST or None, instance=eegelectrodemodel)

    for field in eegelectrodemodel_form.fields:
        eegelectrodemodel_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            try:
                eegelectrodemodel.delete()
                messages.success(request, _('EEG electrode model removed successfully.'))
                return redirect('eegelectrodemodel_list')
            except ProtectedError:
                messages.error(request, _("Error trying to delete EEG electrode model."))
                redirect_url = reverse("eegelectrodemodel_view", args=(eegelectrodemodel_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"can_change": True,
               "equipment": eegelectrodemodel,
               "equipment_form": eegelectrodemodel_form}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_equipment')
def material_list(request, template_name="experiment/material_list.html"):
    return render(request, template_name, {"equipments": Material.objects.all().order_by('name')})


@login_required
@permission_required('experiment.add_material')
def material_create(request, template_name="experiment/material_register.html"):

    material_form = MaterialRegisterForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if material_form.is_valid():

                material_added = material_form.save(commit=False)
                material_added.save()

                messages.success(request, _('Material created successfully.'))
                redirect_url = reverse("material_view", args=(material_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))

        else:
            messages.warning(request, _('Action not available.'))

    context = {"equipment_form": material_form,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_material')
def material_update(request, material_id, template_name="experiment/material_register.html"):
    material = get_object_or_404(Material, pk=material_id)

    material_form = MaterialRegisterForm(request.POST or None, instance=material)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if material_form.is_valid():
                if material_form.has_changed():

                    material_form.save()
                    messages.success(request, _('Material updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("material_view", args=(material.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"equipment": material,
               "equipment_form": material_form,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_material')
def material_view(request, material_id, template_name="experiment/material_register.html"):
    material = get_object_or_404(Material, pk=material_id)

    material_form = MaterialRegisterForm(request.POST or None, instance=material)

    for field in material_form.fields:
        material_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            try:
                material.delete()
                messages.success(request, _('Material removed successfully.'))
                return redirect('material_list')
            except ProtectedError:
                messages.error(request, _("Error trying to delete material."))
                redirect_url = reverse("material_view", args=(material_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"can_change": True,
               "equipment": material,
               "equipment_form": material_form
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_equipment')
def eegelectrodenet_list(request, template_name="experiment/eegelectrodenet_list.html"):
    return render(request, template_name, {"equipments": EEGElectrodeNet.objects.all().order_by('identification')})


@login_required
@permission_required('experiment.add_eegelectrodenet')
def eegelectrodenet_create(request, template_name="experiment/eegelectrodenet_register.html"):

    eegelectrodenet_form = EEGElectrodeNETRegisterForm(request.POST or None)
    cap_form = EEGElectrodeCapRegisterForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            is_a_cap = 'cap_flag' in request.POST

            if eegelectrodenet_form.is_valid() and (not is_a_cap or (is_a_cap and cap_form.is_valid())):

                eegelectrodenet_added = eegelectrodenet_form.save(commit=False)
                eegelectrodenet_added.equipment_type = "eeg_electrode_net"

                if not is_a_cap:
                    eegelectrodenet_added.save()
                else:
                    cap_added = cap_form.save(commit=False)
                    cap_added.equipment_type = eegelectrodenet_added.equipment_type
                    cap_added.electrode_model_default = eegelectrodenet_added.electrode_model_default
                    cap_added.manufacturer = eegelectrodenet_added.manufacturer
                    cap_added.identification = eegelectrodenet_added.identification
                    cap_added.description = eegelectrodenet_added.description
                    cap_added.serial_number = eegelectrodenet_added.serial_number
                    cap_added.save()

                equipment_added = cap_added if is_a_cap else eegelectrodenet_added

                localization_systems = get_localization_system(request.POST)
                if localization_systems:
                    for localization_system_item in localization_systems:
                        localization_system_id = localization_system_item.split("_")[-1]
                        if request.POST[localization_system_item] == "on":
                            eeg_electrode_net_system = EEGElectrodeNetSystem()
                            eeg_electrode_net_system.eeg_electrode_net_id = equipment_added.id
                            eeg_electrode_net_system.eeg_electrode_localization_system_id = localization_system_id
                            eeg_electrode_net_system.save()

                messages.success(request, _('EEG electrode net created successfully.'))
                redirect_url = reverse("eegelectrodenet_view", args=(equipment_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))

        else:
            messages.warning(request, _('Action not available.'))

    eegelectrodelocalizationsystem = EEGElectrodeLocalizationSystem.objects.all()

    for localization_system in eegelectrodelocalizationsystem:
        localization_system.checked = False
        localization_system.used = False
        localization_system.disabled = False

    context = {"equipment_form": eegelectrodenet_form,
               "is_a_cap": False,
               "cap_form": cap_form,
               "eegelectrodelocalizationsystem": eegelectrodelocalizationsystem,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)


def get_localization_system(data_post):

    localization_list = []
    for item in data_post:
        if "localization_system" in item:
            localization_list.append(item)

    return localization_list


@login_required
@permission_required('experiment.change_eegelectrodenet')
def eegelectrodenet_update(request, eegelectrodenet_id, template_name="experiment/eegelectrodenet_register.html"):
    eegelectrodenet = get_object_or_404(EEGElectrodeNet, pk=eegelectrodenet_id)
    eegelectrodenetsystem = EEGElectrodeNetSystem.objects.all()

    eegelectrodenet_form = EEGElectrodeNETRegisterForm(request.POST or None, instance=eegelectrodenet)

    cap_size_list = None
    cap = EEGElectrodeCap.objects.filter(id=eegelectrodenet_id)
    is_a_cap = False
    if cap:
        is_a_cap = True
        cap_form = EEGElectrodeCapRegisterForm(request.POST or None, instance=cap[0])
        cap_size_list = EEGCapSize.objects.filter(eeg_electrode_cap=cap[0])
    else:
        cap_form = EEGElectrodeCapRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if eegelectrodenet_form.is_valid():
                localization_systems = get_localization_system(request.POST)
                if eegelectrodenet_form.has_changed() or localization_systems:
                    if localization_systems:
                        for localization_system_item in localization_systems:
                            localization_system_id = localization_system_item.split("_")[-1]
                            if request.POST[localization_system_item] == "on":
                                eeg_electrode_net_system = EEGElectrodeNetSystem()
                                eeg_electrode_net_system.eeg_electrode_net_id=eegelectrodenet.id
                                eeg_electrode_net_system.eeg_electrode_localization_system_id=localization_system_id
                                eeg_electrode_net_system.save()
                            else:
                                net_system = EEGElectrodeNetSystem.objects.filter(
                                    eeg_electrode_net=eegelectrodenet,
                                    eeg_electrode_localization_system=localization_system_item)
                                if net_system:
                                    messages.error(
                                        request,
                                        _('It is not possible to delete localization system, since it in use.'))
                                else:
                                    eeg_electrode_net_system = EEGElectrodeNetSystem.objects.get(
                                        eeg_electrode_net_id=eegelectrodenet.id,
                                        eeg_electrode_localization_system_id=localization_system_id)
                                    eeg_electrode_net_system.delete()

                    if is_a_cap and cap_form.has_changed():
                        cap_form.save()
                    if eegelectrodenet_form.has_changed():
                        eegelectrodenet_form.save()
                    messages.success(request, _('EEG electrode net updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("eegelectrodenet_view", args=(eegelectrodenet.id,))
                return HttpResponseRedirect(redirect_url)

    eegelectrodelocalizationsystem = EEGElectrodeLocalizationSystem.objects.all()

    for localization_system in eegelectrodelocalizationsystem:
        localization_system.checked = False
        localization_system.used = False
        localization_system.disabled = False
        net_system = EEGElectrodeNetSystem.objects.filter(eeg_electrode_net=eegelectrodenet,
                                                          eeg_electrode_localization_system=localization_system)
        if net_system:
            localization_system.checked = True
            if EEGElectrodeLayoutSetting.objects.filter(eeg_electrode_net_system=net_system):
                localization_system.used = True
                localization_system.disabled = True

    context = {"equipment": eegelectrodenet,
               "equipment_form": eegelectrodenet_form,
               "is_a_cap": is_a_cap,
               "cap_form": cap_form,
               "eegelectrodenetsystem": eegelectrodenetsystem,
               "eegelectrodelocalizationsystem": eegelectrodelocalizationsystem,
               "editing": True,
               "cap_size_list": cap_size_list,
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_eegelectrodenet')
def eegelectrodenet_view(request, eegelectrodenet_id, template_name="experiment/eegelectrodenet_register.html"):
    eegelectrodenet = get_object_or_404(EEGElectrodeNet, pk=eegelectrodenet_id)
    eegelectrodenet_form = EEGElectrodeNETRegisterForm(request.POST or None, instance=eegelectrodenet)

    # cap_form = None
    cap = EEGElectrodeCap.objects.filter(id=eegelectrodenet_id)
    is_a_cap = False
    cap_size_list = None
    if cap:
        is_a_cap = True
        cap_form = EEGElectrodeCapRegisterForm(request.POST or None, instance=cap[0])
        cap_size_list = EEGCapSize.objects.filter(eeg_electrode_cap=cap[0])
    else:
        cap_form = EEGElectrodeCapRegisterForm(request.POST or None)

    eegelectrodelocalizationsystem = EEGElectrodeLocalizationSystem.objects.all()

    for field in eegelectrodenet_form.fields:
        eegelectrodenet_form.fields[field].widget.attrs['disabled'] = True

    for field in cap_form.fields:
        cap_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":
            net_system = EEGElectrodeNetSystem.objects.filter(eeg_electrode_net=eegelectrodenet)
            if net_system and EEGElectrodeLayoutSetting.objects.filter(eeg_electrode_net_system=net_system):
                messages.error(request, _('EEG electrode net cannot be removed because it is used in EEG electrode system.'))
                redirect_url = reverse("eegelectrodenet_view", args=(eegelectrodenet_id,))
                return HttpResponseRedirect(redirect_url)
            else:
                try:
                    if cap:
                        if cap_size_list:
                            eeg_data = EEGData.objects.filter(eeg_electrode_net=cap_size_list)
                            if eeg_data:
                                messages.error(request, _('EEG electrode net cannot be removed because cap size is associated with EEG data.'))
                                redirect_url = reverse("eegelectrodenet_view", args=(eegelectrodenet_id,))
                                return HttpResponseRedirect(redirect_url)
                            cap_size_list.delete()
                        cap.delete()
                    else:
                        eegelectrodenet.delete()
                    messages.success(request, _('EEG electrode net removed successfully.'))
                    return redirect('eegelectrodenet_list')
                except ProtectedError:
                    messages.error(request, _("Error trying to delete EEG Electrode Net."))
                    redirect_url = reverse("eegelectrodenet_view", args=(eegelectrodenet_id,))
                    return HttpResponseRedirect(redirect_url)

    for localization_system in eegelectrodelocalizationsystem:
        localization_system.checked = False
        localization_system.used = False
        localization_system.disabled = True
        net_system = EEGElectrodeNetSystem.objects.filter(eeg_electrode_net=eegelectrodenet,
                                                          eeg_electrode_localization_system=localization_system)
        if net_system:
            localization_system.checked = True
            if EEGElectrodeLayoutSetting.objects.filter(eeg_electrode_net_system=net_system):
                localization_system.used = True

    context = {"can_change": True,
               "equipment": eegelectrodenet,
               "is_a_cap": is_a_cap,
               "equipment_form": eegelectrodenet_form,
               "cap_form": cap_form,
               "cap_size_list": cap_size_list,
               "eegelectrodelocalizationsystem": eegelectrodelocalizationsystem
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_eegelectrodenet')
def eegelectrodenet_cap_size_create(request, eegelectrode_cap_id,
                                template_name="experiment/eegelectrodenet_size_register.html"):

    cap = get_object_or_404(EEGElectrodeCap, pk=eegelectrode_cap_id)
    cap_size_form = EEGCapSizeRegisterForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if cap_size_form.is_valid():

                eegcapsize_added = cap_size_form.save(commit=False)
                eegcapsize_added.eeg_electrode_cap_id = eegelectrode_cap_id
                eegcapsize_added.save()

                messages.success(request, _('EEG cap size created successfully.'))
                redirect_url = reverse("eegelectrodenet_view", args=(eegelectrode_cap_id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))

        else:
            messages.warning(request, _('Action not available.'))

    context = {"eeg_cap": cap,
               "can_change": True,
               "equipment_form": cap_size_form,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)


# @login_required
# @permission_required('experiment.view_eegelectrodenet')
# def eegelectrodenet_cap_size_remove(request, eegelectrode_cap_size_id):
#     # cap = get_object_or_404(EEGElectrodeCap, pk=eegelectrode_cap_id)
#
#     if request.method == "POST":
#         if request.POST['action'] == "remove_cap_size":
#             cap_size = get_object_or_404(EEGCapSize, pk=eegelectrode_cap_size_id)
#             eegelectrode_cap_id = cap_size.eeg_electrode_cap.id
#             cap_size.delete()
#
#             messages.success(request, _('Cap size removed successfully.'))
#
#             redirect_url = reverse("eegelectrodenet_view", args=(eegelectrode_cap_id,))
#             return HttpResponseRedirect(redirect_url)
#     # else:
#     #     raise PermissionDenied


@login_required
@permission_required('experiment.change_cap_size')
def eegelectrodenet_cap_size_update(request, eegelectrode_cap_size_id,
                                    template_name="experiment/eegelectrodenet_size_register.html"):
    eegelectrode_cap_size = get_object_or_404(EEGCapSize, pk=eegelectrode_cap_size_id)

    eegelectrode_cap_size_form = EEGCapSizeRegisterForm(request.POST or None, instance=eegelectrode_cap_size)

    if request.method == "POST":
        if request.POST['action'] == "save":
            if eegelectrode_cap_size_form.is_valid():
                if eegelectrode_cap_size_form.has_changed():

                    eegelectrode_cap_size_form.save()
                    messages.success(request, _('Cap size updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("eegelectrodenet_cap_size_view", args=(eegelectrode_cap_size.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "equipment": eegelectrode_cap_size,
        "equipment_form": eegelectrode_cap_size_form,
        "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_cap_size')
def eegelectrodenet_cap_size_view(request, eegelectrode_cap_size_id,
                                  template_name="experiment/eegelectrodenet_size_register.html"):
    eegelectrode_cap_size = get_object_or_404(EEGCapSize, pk=eegelectrode_cap_size_id)

    eegelectrode_cap_size_form = EEGCapSizeRegisterForm(request.POST or None, instance=eegelectrode_cap_size)

    for field in eegelectrode_cap_size_form.fields:
        eegelectrode_cap_size_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            try:
                eegelectrode_cap_size.delete()
                messages.success(request, _('Cap size removed successfully.'))
                redirect_url = reverse('eegelectrodenet_view', args=(eegelectrode_cap_size.eeg_electrode_cap_id,))
                return HttpResponseRedirect(redirect_url)
            except ProtectedError:
                messages.error(request, _("Error trying to delete cap size."))
                redirect_url = reverse("eegelectrodenet_cap_size_view", args=(eegelectrode_cap_size_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"equipment_form": eegelectrode_cap_size_form,
               "can_change": True,
               "equipment": eegelectrode_cap_size,
               }

    return render(request, template_name, context)

# @login_required
# @permission_required('experiment.add_equipment')
# def equipment_configuration(request,
#                    template_name="experiment/equipment_configuration.html"):
#     context = {
#             "creating": False,
#             "editing": False,
#             "can_change": True
#             # "eeg_setting": eeg_setting,
#             # "manufacturer_list": manufacturer_list,
#             # "equipment_list": equipment_list,
#             # "equipment_form": equipment_form,
#             # "equipment_type": equipment.equipment_type,
#             # "equipment_selected": equipment,
#             # "equipment_type_name": equipment_type_name
#         }
#
#     return render(request, template_name, context)


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
    lime_survey_id = Questionnaire.objects.get(id=questionnaire_configuration.component_id).survey.lime_survey_id
    language = get_questionnaire_language(surveys, lime_survey_id, request.LANGUAGE_CODE)
    questionnaire_title = surveys.get_survey_title(lime_survey_id, language)

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

    context = {"can_change": get_can_change(request.user, group.experiment.research_project),
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
                                  'number_of_eeg_data': 0,
                                  'number_of_emg_data': 0}

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
        list_of_questionnaires_configuration = create_list_of_trees(group.experimental_protocol, "questionnaire")

        list_of_eeg_configuration = create_list_of_trees(group.experimental_protocol, "eeg")
        list_of_emg_configuration = create_list_of_trees(group.experimental_protocol, "emg")

        experimental_protocol_info = {'number_of_questionnaires': len(list_of_questionnaires_configuration),
                                      'number_of_eeg_data': len(list_of_eeg_configuration),
                                      'number_of_emg_data': len(list_of_emg_configuration)}

        # For each subject of the group...
        for subject_of_group in subject_list:

            number_of_questionnaires_filled = 0

            # For each questionnaire in the experimental protocol of the group...
            for questionnaire_configuration in list_of_questionnaires_configuration:
                # Get the responses
                path = [item[0] for item in questionnaire_configuration]
                data_configuration_tree_id = list_data_configuration_tree(path[-1], path)
                subject_responses = QuestionnaireResponse.objects. \
                    filter(subject_of_group=subject_of_group,
                           data_configuration_tree_id=data_configuration_tree_id)

                questionnaire_configuration = get_object_or_404(ComponentConfiguration, pk=path[-1])
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
            # for each component_configuration of eeg...
            for eeg_configuration in list_of_eeg_configuration:
                path = [item[0] for item in eeg_configuration]
                data_configuration_tree_id = list_data_configuration_tree(path[-1], path)
                eeg_data_files = \
                    EEGData.objects.filter(subject_of_group=subject_of_group,
                                           data_configuration_tree_id=data_configuration_tree_id)
                if len(eeg_data_files):
                    number_of_eeg_data_files_uploaded += 1

            percentage_of_eeg_data_files_uploaded = 0
            if len(list_of_eeg_configuration) > 0:
                percentage_of_eeg_data_files_uploaded = \
                    100 * number_of_eeg_data_files_uploaded / len(list_of_eeg_configuration)

            # EMG data files
            number_of_emg_data_files_uploaded = 0
            # for each component_configuration of emg...
            for emg_configuration in list_of_emg_configuration:
                path = [item[0] for item in emg_configuration]
                data_configuration_tree_id = list_data_configuration_tree(path[-1], path)
                emg_data_files = \
                    EMGData.objects.filter(subject_of_group=subject_of_group,
                                           data_configuration_tree_id=data_configuration_tree_id)
                if len(emg_data_files):
                    number_of_emg_data_files_uploaded += 1

            percentage_of_emg_data_files_uploaded = 0
            if len(list_of_emg_configuration) > 0:
                percentage_of_emg_data_files_uploaded = \
                    100 * number_of_emg_data_files_uploaded / len(list_of_emg_configuration)

            # If any questionnaire has responses or any eeg data file was uploaded,
            # the subject can't be removed from the group.
            if number_of_eeg_data_files_uploaded or \
                    number_of_emg_data_files_uploaded or \
                    number_of_questionnaires_filled:
                can_remove = False

            subject_list_with_status.append(
                {'subject': subject_of_group.subject,
                 'number_of_questionnaires_filled': number_of_questionnaires_filled,
                 'total_of_questionnaires': len(list_of_questionnaires_configuration),
                 'percentage_of_questionnaires': int(percentage_of_questionnaires),
                 'consent': subject_of_group.consent_form,
                 'number_of_eeg_data_files_uploaded': number_of_eeg_data_files_uploaded,
                 'total_of_eeg_data_files': len(list_of_eeg_configuration),
                 'percentage_of_eeg_data_files_uploaded': int(percentage_of_eeg_data_files_uploaded),

                 'number_of_emg_data_files_uploaded': number_of_emg_data_files_uploaded,
                 'total_of_emg_data_files': len(list_of_emg_configuration),
                 'percentage_of_emg_data_files_uploaded': int(percentage_of_emg_data_files_uploaded),

                 'number_of_additional_data_uploaded':
                     AdditionalData.objects.filter(subject_of_group=subject_of_group).count()},
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

    context = {"can_change": get_can_change(request.user, group.experiment.research_project),
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

        language = get_questionnaire_language(surveys, lime_survey_id, request.LANGUAGE_CODE)
        survey_title = surveys.get_survey_title(lime_survey_id, language)
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

        context = {"can_change": True,
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
                   "URL": redirect_url
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

    language = get_questionnaire_language(surveys, questionnaire.survey.lime_survey_id, request.LANGUAGE_CODE)
    survey_title = surveys.get_survey_title(questionnaire.survey.lime_survey_id, language)
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

    context = {"can_change": get_can_change(request.user, group.experiment.research_project),
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
               "URL": redirect_url
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

    context = {"can_change": get_can_change(request.user, group.experiment.research_project),
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
               "survey_title": survey_title
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

    language_code = request.LANGUAGE_CODE

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

        language = get_questionnaire_language(surveys, questionnaire.survey.lime_survey_id, language_code)
        subject_questionnaires.append(
            {'questionnaire_configuration': questionnaire_configuration,
             'title': surveys.get_survey_title(questionnaire.survey.lime_survey_id, language),
             'path': path,
             'questionnaire_responses': questionnaire_responses_with_status}
        )

    surveys.release_session_key()

    context = {"can_change": get_can_change(request.user, group.experiment.research_project),
               'group': group,
               'limesurvey_available': limesurvey_available,
               'subject': subject,
               'subject_questionnaires': subject_questionnaires
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_researchproject')
def subject_eeg_view(request, group_id, subject_id,
                     template_name="experiment/subject_eeg_collection_list.html"):

    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)

    eeg_collections = []

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

    context = {"can_change": get_can_change(request.user, group.experiment.research_project),
               'group': group,
               'subject': subject,
               'eeg_collections': eeg_collections
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

                    has_position_status = False

                    # creating position status
                    if hasattr(eeg_data_added.eeg_setting, 'eeg_electrode_layout_setting'):
                        eeg_electrode_layout_setting = eeg_data_added.eeg_setting.eeg_electrode_layout_setting

                        if eeg_electrode_layout_setting.positions_setting:
                            has_position_status = True

                        for position_setting in eeg_electrode_layout_setting.positions_setting.all():
                            EEGElectrodePositionCollectionStatus(
                                worked=position_setting.used,
                                eeg_data=eeg_data_added,
                                eeg_electrode_position_setting=position_setting
                            ).save()

                    # Validate known eeg file formats
                    reading_for_eeg_validation(eeg_data_added, request)

                    messages.success(request, _('EEG data collection created successfully.'))
                    messages.info(request, _('Now you can configure each electrode position'))

                    redirect_url = reverse("eeg_data_view", args=(eeg_data_added.id,
                                                                  2 if has_position_status else 1))
                    return HttpResponseRedirect(redirect_url)

        context = {"can_change": True,
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
                   "tab": "1"
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
def eeg_data_view(request, eeg_data_id, tab, template_name="experiment/subject_eeg_data_form.html"):

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

    context = {"can_change": get_can_change(request.user, eeg_data.subject_of_group.group.experiment.research_project),
               "editing": False,
               "group": eeg_data.subject_of_group.group,
               "subject": eeg_data.subject_of_group.subject,
               "eeg_data_form": eeg_data_form,
               "eeg_data": eeg_data,
               "eeg_setting_default_id": eeg_step.eeg_setting_id,
               "file_format_list": file_format_list,
               "tab": tab
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def eeg_data_edit(request, eeg_data_id, tab, template_name="experiment/subject_eeg_data_form.html"):

    eeg_data = get_object_or_404(EEGData, pk=eeg_data_id)

    # get the current before change
    current_eeg_setting_id = eeg_data.eeg_setting.id

    eeg_step = get_object_or_404(EEG, id=eeg_data.data_configuration_tree.component_configuration.component.id)

    file_format_list = file_format_code()

    if get_can_change(request.user, eeg_data.subject_of_group.group.experiment.research_project):

        if request.method == "POST":

            eeg_data_form = EEGDataForm(request.POST, request.FILES, instance=eeg_data)

            if request.POST['action'] == "save":
                if eeg_data_form.is_valid():

                    if tab == "1":

                        if eeg_data_form.has_changed():

                            # if the eeg-setting changed
                            if current_eeg_setting_id != int(request.POST['eeg_setting']):
                                # remove all current position status
                                for position in eeg_data.electrode_positions.all():
                                    position.delete()

                            eeg_data_to_update = eeg_data_form.save(commit=False)
                            eeg_data_to_update.group = eeg_data.subject_of_group.group
                            eeg_data_to_update.subject = eeg_data.subject_of_group.subject
                            eeg_data_to_update.save()

                            if hasattr(eeg_data.eeg_setting, "eeg_electrode_layout_setting"):
                                if eeg_data.eeg_setting.eeg_electrode_layout_setting.positions_setting:
                                    for position_setting in \
                                            eeg_data.eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
                                        # if not exists a position status
                                        position_status = EEGElectrodePositionCollectionStatus.objects.filter(
                                            eeg_data=eeg_data_to_update,
                                            eeg_electrode_position_setting=position_setting
                                        )
                                        if not position_status:
                                            EEGElectrodePositionCollectionStatus(
                                                eeg_data=eeg_data_to_update,
                                                eeg_electrode_position_setting=position_setting,
                                                worked=position_setting.used
                                            ).save()

                            # Validate known eeg file formats
                            reading_for_eeg_validation(eeg_data_to_update, request)

                            messages.success(request, _('EEG data updated successfully.'))
                        else:
                            messages.success(request, _('There is no changes to save.'))

                    else:

                        for position_status in eeg_data.electrode_positions.all():
                            position_status.worked = 'position_status_' + str(position_status.id) in request.POST
                            position_status.save()

                        messages.success(request, _('EEG position data updated successfully.'))

                    redirect_url = reverse("eeg_data_view", args=(eeg_data_id, tab))
                    return HttpResponseRedirect(redirect_url)

        else:
            eeg_data_form = EEGDataForm(request.POST or None, instance=eeg_data,
                                        initial={'experiment': eeg_data.subject_of_group.group.experiment})

        context = {"group": eeg_data.subject_of_group.group,
                   "subject": eeg_data.subject_of_group.subject,
                   "eeg_data_form": eeg_data_form,
                   "eeg_data": eeg_data,
                   "file_format_list": file_format_list,
                   "eeg_setting_default_id": eeg_step.eeg_setting_id,
                   "editing": True,
                   "tab": tab
                   }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.view_researchproject')
def subject_emg_view(request, group_id, subject_id,
                     template_name="experiment/subject_emg_collection_list.html"):

    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)

    emg_collections = []

    list_of_paths = create_list_of_trees(group.experimental_protocol, "emg")

    subject_of_group = get_object_or_404(SubjectOfGroup, group=group, subject=subject)

    # for emg_configuration in list_of_emg_configuration:
    for path in list_of_paths:

        emg_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])

        data_configuration_tree_id = list_data_configuration_tree(emg_configuration.id, [item[0] for item in path])

        emg_data_files = EMGData.objects.filter(subject_of_group=subject_of_group,
                                                data_configuration_tree__id=data_configuration_tree_id)

        emg_collections.append(
            {'emg_configuration': emg_configuration,
             'path': path,
             'emg_data_files': emg_data_files}
        )

    context = {"can_change": get_can_change(request.user, group.experiment.research_project),
               'group': group,
               'subject': subject,
               'emg_collections': emg_collections
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_questionnaireresponse')
def subject_emg_data_create(request, group_id, subject_id, emg_configuration_id,
                            template_name="experiment/subject_emg_data_form.html"):

    group = get_object_or_404(Group, id=group_id)

    list_of_path = [int(item) for item in emg_configuration_id.split('-')]
    emg_configuration_id = list_of_path[-1]

    if get_can_change(request.user, group.experiment.research_project):

        emg_configuration = get_object_or_404(ComponentConfiguration, id=emg_configuration_id)
        emg_step = get_object_or_404(EMG, id=emg_configuration.component_id)

        redirect_url = None
        emg_data_id = None

        emg_data_form = EMGDataForm(None)

        file_format_list = file_format_code()

        if request.method == "POST":
            if request.POST['action'] == "save":

                emg_data_form = EMGDataForm(request.POST, request.FILES)

                if emg_data_form.is_valid():

                    data_configuration_tree_id = list_data_configuration_tree(emg_configuration_id, list_of_path)
                    if not data_configuration_tree_id:
                        data_configuration_tree_id = create_data_configuration_tree(list_of_path)

                    subject = get_object_or_404(Subject, pk=subject_id)
                    subject_of_group = get_object_or_404(SubjectOfGroup, subject=subject, group_id=group_id)

                    emg_data_added = emg_data_form.save(commit=False)
                    emg_data_added.subject_of_group = subject_of_group
                    emg_data_added.component_configuration = emg_configuration
                    emg_data_added.data_configuration_tree_id = data_configuration_tree_id

                    # PS: it was necessary adding these 2 lines because Django raised, I do not why (Evandro),
                    # the following error 'EMGData' object has no attribute 'group'
                    emg_data_added.group = group
                    emg_data_added.subject = subject

                    emg_data_added.save()

                    messages.success(request, _('EMG data collection created successfully.'))

                    redirect_url = reverse("emg_data_view", args=(emg_data_added.id,))
                    # redirect_url = reverse("subjects", args=(group.id,))
                    return HttpResponseRedirect(redirect_url)

        context = {"can_change": True,
                   "creating": True,
                   "editing": True,
                   "group": group,
                   "emg_configuration": emg_configuration,
                   "emg_data_form": emg_data_form,
                   "emg_data_id": emg_data_id,
                   "file_format_list": file_format_list,
                   "subject": get_object_or_404(Subject, pk=subject_id),
                   "URL": redirect_url,
                   }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def emg_data_view(request, emg_data_id, template_name="experiment/subject_emg_data_form.html"):

    emg_data = get_object_or_404(EMGData, pk=emg_data_id)

    emg_data_form = EMGDataForm(request.POST or None, instance=emg_data)

    for field in emg_data_form.fields:
        emg_data_form.fields[field].widget.attrs['disabled'] = True

    file_format_list = file_format_code()

    if request.method == "POST":
        if request.POST['action'] == "remove":

            if get_can_change(request.user, emg_data.subject_of_group.group.experiment.research_project):

                subject_of_group = emg_data.subject_of_group
                emg_data.file.delete()
                emg_data.delete()
                messages.success(request, _('EMG data removed successfully.'))
                return redirect('subject_emg_view',
                                group_id=subject_of_group.group_id,
                                subject_id=subject_of_group.subject_id)
            else:
                raise PermissionDenied

    context = {"can_change": get_can_change(request.user, emg_data.subject_of_group.group.experiment.research_project),
               "editing": False,
               "group": emg_data.subject_of_group.group,
               "subject": emg_data.subject_of_group.subject,
               "emg_data_form": emg_data_form,
               "emg_data": emg_data,
               "file_format_list": file_format_list
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def emg_data_edit(request, emg_data_id, template_name="experiment/subject_emg_data_form.html"):

    emg_data = get_object_or_404(EMGData, pk=emg_data_id)

    file_format_list = file_format_code()

    if get_can_change(request.user, emg_data.subject_of_group.group.experiment.research_project):

        if request.method == "POST":

            emg_data_form = EMGDataForm(request.POST, request.FILES, instance=emg_data)

            if request.POST['action'] == "save":
                if emg_data_form.is_valid():

                    if emg_data_form.has_changed():

                        emg_data_to_update = emg_data_form.save(commit=False)
                        emg_data_to_update.group = emg_data.subject_of_group.group
                        emg_data_to_update.subject = emg_data.subject_of_group.subject
                        emg_data_to_update.save()

                        messages.success(request, _('EMG data updated successfully.'))
                    else:
                        messages.success(request, _('There is no changes to save.'))

                    redirect_url = reverse("emg_data_view", args=(emg_data_id,))
                    return HttpResponseRedirect(redirect_url)

        else:
            emg_data_form = EMGDataForm(request.POST or None, instance=emg_data)

        context = {"group": emg_data.subject_of_group.group,
                   "subject": emg_data.subject_of_group.subject,
                   "emg_data_form": emg_data_form,
                   "emg_data": emg_data,
                   "file_format_list": file_format_list,
                   "editing": True
                   }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.view_researchproject')
def subject_additional_data_view(request, group_id, subject_id,
                                 template_name="experiment/additional_data_collection_list.html"):

    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)
    subject_of_group = get_object_or_404(SubjectOfGroup, group=group, subject=subject)

    data_collections = []

    list_of_paths = create_list_of_trees(group.experimental_protocol, None)

    for path in list_of_paths:

        component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])

        data_configuration_tree_id = list_data_configuration_tree(component_configuration.id,
                                                                  [item[0] for item in path])

        additional_data_files = AdditionalData.objects.filter(subject_of_group=subject_of_group,
                                                              data_configuration_tree__id=data_configuration_tree_id)

        data_collections.append(
            {'component_configuration': component_configuration,
             'path': path,
             'additional_data_files': additional_data_files,
             'icon_class': icon_class[component_configuration.component.component_type]}
        )

    context = {"can_change": get_can_change(request.user, group.experiment.research_project),
               'group': group,
               'subject': subject,
               'data_collections': data_collections
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.add_questionnaireresponse')
def subject_additional_data_create(request, group_id, subject_id, path_of_configuration,
                                   template_name="experiment/subject_additional_data_form.html"):

    group = get_object_or_404(Group, id=group_id)

    if get_can_change(request.user, group.experiment.research_project):

        list_of_path = [int(item) for item in path_of_configuration.split('-')]
        component_configuration_id = list_of_path[-1]

        component_configuration = get_object_or_404(ComponentConfiguration, id=component_configuration_id)

        additional_data_form = AdditionalDataForm(None)

        file_format_list = file_format_code()

        if request.method == "POST":
            if request.POST['action'] == "save":

                additional_data_form = AdditionalDataForm(request.POST, request.FILES)

                if additional_data_form.is_valid():

                    data_configuration_tree_id = list_data_configuration_tree(component_configuration_id, list_of_path)
                    if not data_configuration_tree_id:
                        data_configuration_tree_id = create_data_configuration_tree(list_of_path)

                    subject = get_object_or_404(Subject, pk=subject_id)
                    subject_of_group = get_object_or_404(SubjectOfGroup, subject=subject, group_id=group_id)

                    additional_data_added = additional_data_form.save(commit=False)
                    additional_data_added.subject_of_group = subject_of_group
                    additional_data_added.component_configuration = component_configuration
                    additional_data_added.data_configuration_tree_id = data_configuration_tree_id

                    # PS: it was necessary adding these 2 lines because Django raised, I do not why (Evandro),
                    # the following error 'AdditionalData' object has no attribute 'group'
                    additional_data_added.group = group
                    additional_data_added.subject = subject

                    additional_data_added.save()

                    messages.success(request, _('Additional data collection created successfully.'))

                    redirect_url = reverse("additional_data_view", args=(additional_data_added.id,))
                    return HttpResponseRedirect(redirect_url)

        context = {"can_change": True,
                   "creating": True,
                   "editing": True,
                   "group": group,
                   "component_configuration": component_configuration,
                   "additional_data_form": additional_data_form,
                   "file_format_list": file_format_list,
                   "subject": get_object_or_404(Subject, pk=subject_id)
                   }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def additional_data_view(request, additional_data_id, template_name="experiment/subject_additional_data_form.html"):

    additional_data = get_object_or_404(AdditionalData, pk=additional_data_id)
    additional_data_form = AdditionalDataForm(request.POST or None, instance=additional_data)

    for field in additional_data_form.fields:
        additional_data_form.fields[field].widget.attrs['disabled'] = True

    file_format_list = file_format_code()

    if request.method == "POST":
        if request.POST['action'] == "remove":

            if get_can_change(request.user, additional_data.subject_of_group.group.experiment.research_project):

                subject_of_group = additional_data.subject_of_group
                additional_data.file.delete()
                additional_data.delete()
                messages.success(request, _('Additional data removed successfully.'))
                return redirect('subject_additional_data_view',
                                group_id=subject_of_group.group_id,
                                subject_id=subject_of_group.subject_id)
            else:
                raise PermissionDenied

    context = {"can_change": get_can_change(request.user, additional_data.subject_of_group.group.experiment.research_project),
               "editing": False,
               "group": additional_data.subject_of_group.group,
               "subject": additional_data.subject_of_group.subject,
               "additional_data_form": additional_data_form,
               "additional_data": additional_data,
               "file_format_list": file_format_list,
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.change_experiment')
def additional_data_edit(request, additional_data_id, template_name="experiment/subject_additional_data_form.html"):

    additional_data = get_object_or_404(AdditionalData, pk=additional_data_id)

    file_format_list = file_format_code()

    if get_can_change(request.user, additional_data.subject_of_group.group.experiment.research_project):

        if request.method == "POST":

            additional_data_form = AdditionalDataForm(request.POST, request.FILES, instance=additional_data)

            if request.POST['action'] == "save":
                if additional_data_form.is_valid():
                    if additional_data_form.has_changed():

                        additional_data_to_update = additional_data_form.save(commit=False)
                        additional_data_to_update.group = additional_data.subject_of_group.group
                        additional_data_to_update.subject = additional_data.subject_of_group.subject
                        additional_data_to_update.save()

                        messages.success(request, _('Additional data updated successfully.'))
                    else:
                        messages.success(request, _('There is no changes to save.'))

                    redirect_url = reverse("additional_data_view", args=(additional_data_id,))
                    return HttpResponseRedirect(redirect_url)

        else:
            additional_data_form = AdditionalDataForm(request.POST or None, instance=additional_data)

        context = {"group": additional_data.subject_of_group.group,
                   "subject": additional_data.subject_of_group.subject,
                   "additional_data_form": additional_data_form,
                   "additional_data": additional_data,
                   "file_format_list": file_format_list,
                   "editing": True,
                   }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.change_experiment')
def get_cap_size_list_from_eeg_setting(request, eeg_setting_id):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)
    list_of_cap_size = EEGCapSize.objects.filter(id=0)
    if hasattr(eeg_setting, 'eeg_electrode_layout_setting'):
        eeg_electrode_net_id = eeg_setting.eeg_electrode_layout_setting.eeg_electrode_net_system.eeg_electrode_net.id
        # if the electrode net is a cap
        if EEGElectrodeCap.objects.filter(id=eeg_electrode_net_id):
            list_of_cap_size = EEGCapSize.objects.filter(eeg_electrode_cap_id=eeg_electrode_net_id)
    json_cap_size = serializers.serialize("json", list_of_cap_size)
    return HttpResponse(json_cap_size, content_type='application/json')


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

        context = {'subject': subject,
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

    context = {"can_change": get_can_change(request.user, experiment.research_project),
               "component_list": components,
               "component_type_choices": component_type_choices,
               "experiment": experiment
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
            questionnaires_list = find_active_questionnaires(request.LANGUAGE_CODE)  # Questionnaires().find_all_active_questionnaires()
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
                elif component_type == 'emg':
                    new_specific_component = EMG()
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

        context = {"back_cancel_url": "/experiment/" + str(experiment.id) + "/components",
                   "component_form": component_form,
                   "creating": True,
                   "experiment": experiment,
                   "questionnaires_list": questionnaires_list,
                   "specific_form": specific_form
                   }
        return render(request, template_name, context)
    else:
        raise PermissionDenied

def find_active_questionnaires(language_code):

    surveys = Questionnaires()

    questionnaires_list = surveys.find_all_active_questionnaires()

    for questionnaire in questionnaires_list:
        questionnaire_id = questionnaire["sid"]
        language = get_questionnaire_language(surveys, questionnaire_id, language_code)
        questionnaire['surveyls_title'] = surveys.get_survey_title(questionnaire_id, language)

    surveys.release_session_key()

    return questionnaires_list


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
                    name = _("Use of step ") + cc.component.identification

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


def check_experiment(experiment):
    experiment_id = experiment.id
    experiment_with_data = False

    for group in Group.objects.filter(experiment_id=experiment_id):
        subject_list = [item.pk for item in SubjectOfGroup.objects.filter(group=group)]
        eegdata_list = EEGData.objects.filter(subject_of_group_id__in=subject_list)
        questionnaire_response_list = QuestionnaireResponse.objects.filter(subject_of_group_id__in=subject_list)
        if eegdata_list or questionnaire_response_list:
            experiment_with_data = True

    return experiment_with_data


def copy_experiment(experiment):
    experiment_id = experiment.id

    new_experiment = experiment
    new_experiment.pk = None
    new_experiment.title = _('Copy of') + ' ' + new_experiment.title
    new_experiment.save()

    orig_and_clone = {}
    for component in Component.objects.filter(experiment_id=experiment_id):
        clone_component = create_component(component, new_experiment)
        orig_and_clone[component.id] = clone_component.id

    groups = Group.objects.filter(experiment_id=experiment_id)
    for group in groups:
        experimental_protocol_id = group.experimental_protocol_id
        subject_list = [item.pk for item in SubjectOfGroup.objects.filter(group=group)]
        new_group = group
        new_group.pk = None
        new_group.title = _('Copy of') + ' ' + new_group.title
        new_group.experiment_id = new_experiment.id
        if experimental_protocol_id in orig_and_clone:
            new_group.experimental_protocol_id = orig_and_clone[experimental_protocol_id]
        new_group.save()

        if subject_list:
            new_subject_of_group = SubjectOfGroup.objects.filter(id__in=subject_list)
            for subject_of_group in new_subject_of_group:
                subject_of_group.pk = None
                subject_of_group.group_id = group.id
                subject_of_group.save()

    for component_configuration in ComponentConfiguration.objects.filter(
            component_id__experiment_id=experiment_id).order_by('parent_id', 'order'):

        component_id = component_configuration.component_id
        parent_id = component_configuration.parent_id

        component_configuration.pk = None
        if component_configuration.name:
            component_configuration.name = _('Copy of') + ' ' + component_configuration.name
        else:
            component_configuration.name = _('Copy')

        component_configuration.component_id = orig_and_clone[component_id]
        component_configuration.parent_id = orig_and_clone[parent_id]
        component_configuration.save()


def create_component(component, new_experiment):

    clone = None
    component_type = component.component_type

    if component_type == 'block':
        block = get_object_or_404(Block, pk=component.id)
        clone = Block(number_of_mandatory_components=block.number_of_mandatory_components, type=block.type)

    elif component_type == 'eeg':
        eeg = get_object_or_404(EEG, pk=component.id)
        clone = EEG(eeg_setting_id=eeg.eeg_setting_id)

    elif component_type == 'emg':
        clone = EMG()

    elif component_type == 'instruction':
        instruction = get_object_or_404(Instruction, pk=component.id)
        clone = Instruction(text=instruction.text)

    elif component_type == 'pause':
        clone = Pause()

    elif component_type == 'questionnaire':
        questionnaire = get_object_or_404(Questionnaire, pk=component.id)
        clone = Questionnaire(survey_id=questionnaire.survey_id)

    elif component_type == 'stimulus':
        stimulus = get_object_or_404(Stimulus, pk=component.id)
        clone = Stimulus(stimulus_type_id=stimulus.stimulus_type_id)

    elif component_type == 'task':
        clone = Task()

    elif component_type == 'task_experiment':
        clone = TaskForTheExperimenter()

    else:
        clone = Component()

    if component.identification:
        clone.identification = _('Copy of') + ' ' + component.identification
    else:
        clone.identification = _('Copy')

    clone.experiment = new_experiment
    clone.description = component.description
    clone.duration_value = component.duration_value
    clone.duration_unit = component.duration_unit
    clone.component_type = component.component_type

    clone.save()

    return clone


@login_required
@permission_required('experiment.view_researchproject')
def component_view(request, path_of_the_components):
    # It will always be a block because we don't have a view screen for other components.
    # This view is also use to show the use of a set of steps (component configuration of a block).

    component, component_configuration, component_form, configuration_form, experiment, component_type, template_name,\
        list_of_ids_of_components_and_configurations, list_of_breadcrumbs, group, back_cancel_url =\
        access_objects_for_view_and_update(request, path_of_the_components)

    experiment_in_use = check_experiment(experiment)

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
            elif request.POST['action'] == "copy_experiment":
                copy_experiment(experiment)
                messages.success(request, _('The experiment was copied.'))
                redirect_url = reverse("experiment_view", args=(experiment.id,))
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

    context = {"back_cancel_url": back_cancel_url,
               "block_duration": duration_string,
               "can_change": can_change,
               "component": block,
               "component_configuration": component_configuration,
               "component_form": component_form,
               "configuration_form": configuration_form,
               "configuration_list": configuration_list,
               "configuration_list_of_random_components": configuration_list_of_random_components,
               "experiment": experiment,
               "experiment_in_use": experiment_in_use,
               "group": group,
               "has_unlimited": has_unlimited,
               "icon_class": icon_class,
               "list_of_breadcrumbs": list_of_breadcrumbs,
               "path_of_the_components": path_of_the_components,
               "specific_form": block_form,
               "type_of_the_parent_block": type_of_the_parent_block,
               "component_type_choices": component_type_choices
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

    experiment_in_use = check_experiment(experiment)

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
                    if component.component_type in ["questionnaire", "task", "task_experiment", 'pause', 'emg']:
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

    context = {"back_cancel_url": back_cancel_url,
               "block_duration": duration_string,
               "can_change": can_change,
               "component_configuration": component_configuration,
               "component_form": component_form,
               "configuration_form": configuration_form,
               "configuration_list": configuration_list,
               "configuration_list_of_random_components": configuration_list_of_random_components,
               "icon_class": icon_class,
               "experiment": experiment,
               "experiment_in_use": experiment_in_use,
               "group": group,
               "has_unlimited": has_unlimited,
               "list_of_breadcrumbs": list_of_breadcrumbs,
               "path_of_the_components": path_of_the_components,
               "questionnaire_id": questionnaire_id,
               "questionnaire_title": questionnaire_title,
               "specific_form": specific_form,
               "updating": True,
               "type_of_the_parent_block": type_of_the_parent_block
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
            questionnaires_list = find_active_questionnaires(request.LANGUAGE_CODE)
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
            elif component_type == 'emg':
                new_specific_component = EMG()
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

        context = {"back_cancel_url": back_cancel_url,
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
                   "specific_form": specific_form
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

            if component_type not in ['pause', 'task', 'task_experiment', 'emg']:
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

        context = {"back_cancel_url": back_cancel_url,
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
                   "specific_form": specific_form
                   }

        return render(request, template_name, context)
    else:
        raise PermissionDenied


@login_required
@permission_required('experiment.view_equipment')
def eeg_electrode_localization_system_list(
        request, template_name="experiment/eeg_electrode_localization_system_list.html"):
    return render(request, template_name,
                  {"eeg_electrode_localization_systems": EEGElectrodeLocalizationSystem.objects.order_by('name')})


@login_required
@permission_required('experiment.view_equipment')
def eeg_electrode_localization_system_create(
        request,
        template_name="experiment/eeg_electrode_localization_system_register.html"):

    localization_system_form = EEGElectrodeLocalizationSystemRegisterForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            localization_system_form = EEGElectrodeLocalizationSystemRegisterForm(request.POST, request.FILES)

            if localization_system_form.is_valid():

                localization_system_added = localization_system_form.save()

                messages.success(request, _('EEG electrode localization system created successfully.'))

                redirect_url = reverse("eeg_electrode_localization_system_view", args=(localization_system_added.id,))
                # redirect_url = reverse("eeg_electrode_localization_system_list", args=())
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))
        else:
            messages.warning(request, _('Action not available.'))

    context = {"localization_system_form": localization_system_form,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_equipment')
def eeg_electrode_localization_system_view(
        request,
        eeg_electrode_localization_system_id,
        template_name="experiment/eeg_electrode_localization_system_register.html"):

    localization_system = get_object_or_404(EEGElectrodeLocalizationSystem, pk=eeg_electrode_localization_system_id)
    localization_system_form = EEGElectrodeLocalizationSystemRegisterForm(
        request.POST or None, instance=localization_system)

    for field in localization_system_form.fields:
        localization_system_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            if EEGElectrodeNetSystem.objects.filter(
                    eeg_electrode_localization_system=localization_system).count() == 0:
                try:
                    localization_system.delete()
                    messages.success(request, _('Study removed successfully.'))
                    return redirect('eeg_electrode_localization_system_list')
                except ProtectedError:
                    messages.error(request, _("Error trying to delete localization system."))
                    redirect_url = reverse("eeg_electrode_localization_system_view",
                                           args=(eeg_electrode_localization_system_id,))
                    return HttpResponseRedirect(redirect_url)

            else:
                messages.error(
                    request,
                    _("Impossible to delete localization system because there is (are) Electrode Net associated."))
                redirect_url = reverse("eeg_electrode_localization_system_view",
                                       args=(eeg_electrode_localization_system_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"localization_system": localization_system,
               "localization_system_form": localization_system_form
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_equipment')
def eeg_electrode_localization_system_update(
        request,
        eeg_electrode_localization_system_id,
        template_name="experiment/eeg_electrode_localization_system_register.html"):

    localization_system = get_object_or_404(EEGElectrodeLocalizationSystem, pk=eeg_electrode_localization_system_id)
    localization_system_form = \
        EEGElectrodeLocalizationSystemRegisterForm(request.POST or None, instance=localization_system)

    if request.method == "POST":

        if request.POST['action'] == "save":

            localization_system_form = \
                EEGElectrodeLocalizationSystemRegisterForm(request.POST, request.FILES, instance=localization_system)

            if localization_system_form.is_valid():
                if localization_system_form.has_changed():
                    localization_system_form.save()
                    messages.success(request, _('Localization system updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("eeg_electrode_localization_system_view",
                                       args=(eeg_electrode_localization_system_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"localization_system": localization_system,
               "localization_system_form": localization_system_form,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_equipment')
def eeg_electrode_position_create(
        request,
        eeg_electrode_localization_system_id,
        template_name="experiment/eeg_electrode_position_register.html"):

    localization_system = get_object_or_404(EEGElectrodeLocalizationSystem, pk=eeg_electrode_localization_system_id)

    position_form = EEGElectrodePositionForm(request.POST or None)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if position_form.is_valid():

                position_added = position_form.save(commit=False)
                position_added.eeg_electrode_localization_system = localization_system
                position_added.save()

                messages.success(request, _('EEG electrode position created successfully.'))

                redirect_url = reverse("eeg_electrode_localization_system_view",
                                       args=(eeg_electrode_localization_system_id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _('Information not saved.'))
        else:
            messages.warning(request, _('Action not available.'))

    context = {"position_form": position_form,
               "localization_system": localization_system,
               "creating": True,
               "editing": True
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_equipment')
def eeg_electrode_position_view(
        request,
        eeg_electrode_position_id,
        template_name="experiment/eeg_electrode_position_register.html"):

    position = get_object_or_404(EEGElectrodePosition, pk=eeg_electrode_position_id)
    position_form = EEGElectrodePositionForm(request.POST or None, instance=position)

    for field in position_form.fields:
        position_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":

            if EEGElectrodePositionSetting.objects.filter(
                    eeg_electrode_position=position).count() == 0:
                try:
                    localization_system_id = position.eeg_electrode_localization_system_id
                    position.delete()
                    messages.success(request, _('Position removed successfully.'))

                    redirect_url = reverse("eeg_electrode_localization_system_view",
                                           args=(localization_system_id,))
                    return HttpResponseRedirect(redirect_url)
                except ProtectedError:
                    messages.error(request, _("Error trying to delete position."))
                    redirect_url = reverse("eeg_electrode_position_view",
                                           args=(eeg_electrode_position_id,))
                    return HttpResponseRedirect(redirect_url)

            else:
                messages.error(request,
                               _("Impossible to delete position because there is (are) Position Setting associated."))
                redirect_url = reverse("eeg_electrode_position_view",
                                       args=(eeg_electrode_position_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"position": position,
               "position_form": position_form,
               }

    return render(request, template_name, context)


@login_required
@permission_required('experiment.view_equipment')
def eeg_electrode_position_update(
        request,
        eeg_electrode_position_id,
        template_name="experiment/eeg_electrode_position_register.html"):

    position = get_object_or_404(EEGElectrodePosition, pk=eeg_electrode_position_id)
    position_form = EEGElectrodePositionForm(request.POST or None, instance=position)

    if request.method == "POST":

        if request.POST['action'] == "save":

            if position_form.is_valid():
                if position_form.has_changed():
                    position_form.save()
                    messages.success(request, _('Position updated successfully.'))
                else:
                    messages.success(request, _('There is no changes to save.'))

                redirect_url = reverse("eeg_electrode_position_view", args=(eeg_electrode_position_id,))
                return HttpResponseRedirect(redirect_url)

    context = {"position": position,
               "position_form": position_form,
               "editing": True
               }

    return render(request, template_name, context)
