# coding=utf-8
import base64
import csv
import json
import os
import random
import re
import tempfile
from datetime import date, datetime, timedelta
from functools import partial
from io import StringIO
from operator import itemgetter
from os import path

import mne
import numpy as np
import nwb
import pydot
from configuration.models import LocalInstitution
from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db.models import Min, Q
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import smart_str
from django.utils.translation import gettext as _
from experiment.import_export import ExportExperiment, ImportExperiment
from export.directory_utils import create_directory
from export.forms import AgeIntervalForm, ParticipantsSelectionForm

# from pynwb.nwbco import *
from patient.models import Patient
from patient.models import QuestionnaireResponse as PatientQuestionnaireResponse
from patient.models import SocialDemographicData
from patient.views import update_acquisition_date, update_completed_status
from django.conf import settings
from survey.abc_search_engine import Questionnaires
from survey.models import SensitiveQuestion, Survey
from survey.survey_utils import QuestionnaireUtils, find_questionnaire_name
from survey.views import (
    check_limesurvey_access,
    create_list_of_trees,
    get_questionnaire_language,
    get_questionnaire_responses,
    get_survey_header,
    questionnaire_evaluation_fields_excluded,
)

from .forms import (
    ADConverterRegisterForm,
    AdditionalDataForm,
    AmplifierRegisterForm,
    BlockForm,
    CoilModelForm,
    CoilModelRegisterForm,
    ComponentConfigurationForm,
    ComponentForm,
    ContextTreeForm,
    DigitalGamePhaseDataForm,
    DigitalGamePhaseForm,
    EEGAmplifierForm,
    EEGAmplifierSettingForm,
    EEGCapSizeRegisterForm,
    EEGDataForm,
    EEGElectrodeCapRegisterForm,
    EEGElectrodeLocalizationSystemRegisterForm,
    EEGElectrodeNETRegisterForm,
    EEGElectrodePositionForm,
    EEGFilterForm,
    EEGFilterSettingForm,
    EEGForm,
    EEGSettingForm,
    EEGSolutionForm,
    EEGSolutionRegisterForm,
    ElectrodeModelForm,
    ElectrodeModelRegisterForm,
    EMGADConverterSettingForm,
    EMGAmplifierSettingForm,
    EMGAnalogFilterSettingForm,
    EMGDataForm,
    EMGDigitalFilterSettingForm,
    EMGElectrodePlacementSettingForm,
    EMGElectrodeSettingForm,
    EMGForm,
    EMGIntramuscularPlacementForm,
    EMGIntramuscularPlacementRegisterForm,
    EMGNeedlePlacementRegisterForm,
    EMGPreamplifierFilterSettingForm,
    EMGPreamplifierSettingForm,
    EMGSettingForm,
    EMGSurfacePlacementForm,
    EMGSurfacePlacementRegisterForm,
    EquipmentForm,
    ExperimentForm,
    FileForm,
    FilterTypeRegisterForm,
    GenericDataCollectionDataForm,
    GenericDataCollectionForm,
    GroupForm,
    HotSpotForm,
    InstructionForm,
    ManufacturerRegisterForm,
    MaterialRegisterForm,
    MediaCollectionDataForm,
    MediaCollectionForm,
    MuscleRegisterForm,
    MuscleSideRegisterForm,
    MuscleSubdivisionRegisterForm,
    NumberOfUsesToInsertForm,
    PublicationForm,
    QuestionnaireResponseForm,
    ResearchProjectForm,
    ResearchProjectOwnerForm,
    ResendExperimentForm,
    SoftwareRegisterForm,
    SoftwareVersionRegisterForm,
    SourceCodeForm,
    StandardizationSystemRegisterForm,
    StimulusForm,
    SubjectStepDataForm,
    TMSDataForm,
    TMSDeviceRegisterForm,
    TMSDeviceSettingForm,
    TMSForm,
    TMSLocalizationSystemForm,
    TMSSettingForm,
)
from .models import (
    EEG,
    EMG,
    TMS,
    ADConverter,
    AdditionalData,
    AdditionalDataFile,
    Amplifier,
    Block,
    ClassificationOfDiseases,
    CoilModel,
    Component,
    ComponentAdditionalFile,
    ComponentConfiguration,
    ContextTree,
    DataConfigurationTree,
    DigitalGamePhase,
    DigitalGamePhaseData,
    DigitalGamePhaseFile,
    EEGAmplifierSetting,
    EEGCapSize,
    EEGData,
    EEGElectrodeCap,
    EEGElectrodeLayoutSetting,
    EEGElectrodeLocalizationSystem,
    EEGElectrodeNet,
    EEGElectrodeNetSystem,
    EEGElectrodePosition,
    EEGElectrodePositionCollectionStatus,
    EEGElectrodePositionSetting,
    EEGFile,
    EEGFilterSetting,
    EEGSetting,
    EEGSolution,
    EEGSolutionSetting,
    ElectrodeModel,
    EMGADConverterSetting,
    EMGAmplifierSetting,
    EMGAnalogFilterSetting,
    EMGData,
    EMGDigitalFilterSetting,
    EMGElectrodePlacement,
    EMGElectrodePlacementSetting,
    EMGElectrodeSetting,
    EMGFile,
    EMGIntramuscularPlacement,
    EMGNeedlePlacement,
    EMGPreamplifierFilterSetting,
    EMGPreamplifierSetting,
    EMGSetting,
    EMGSurfacePlacement,
    Equipment,
    Experiment,
    ExperimentResearcher,
    FileFormat,
    FilterType,
    GenericDataCollection,
    GenericDataCollectionData,
    GenericDataCollectionFile,
    GoalkeeperGameConfig,
    GoalkeeperGameLog,
    GoalkeeperGameResults,
    GoalkeeperPhase,
    Group,
    Instruction,
    Keyword,
    Manufacturer,
    Material,
    MediaCollection,
    MediaCollectionData,
    MediaCollectionFile,
    Muscle,
    MuscleSide,
    MuscleSubdivision,
    Pause,
    PortalSelectedQuestion,
    Publication,
    Questionnaire,
    QuestionnaireResponse,
    ResearchProject,
    ScheduleOfSending,
    Software,
    SoftwareVersion,
    StandardizationSystem,
    Stimulus,
    Subject,
    SubjectOfGroup,
    SubjectStepData,
    Tag,
    Task,
    TaskForTheExperimenter,
    TMSData,
    TMSDevice,
    TMSDeviceSetting,
    TMSLocalizationSystem,
    TMSSetting,
    SourceCode,
)
from .pdf import render as render_to_pdf
from .portal import (
    get_experiment_status_portal,
    get_portal_status,
    send_additional_data_to_portal,
    send_context_tree_to_portal,
    send_digital_game_phase_data_to_portal,
    send_eeg_data_to_portal,
    send_eeg_setting_to_portal,
    send_emg_data_to_portal,
    send_emg_setting_to_portal,
    send_experiment_end_message_to_portal,
    send_experiment_researcher_to_portal,
    send_experiment_to_portal,
    send_experimental_protocol_to_portal,
    send_file_to_portal,
    send_generic_data_collection_data_to_portal,
    send_group_to_portal,
    send_media_collection_data_to_portal,
    send_participant_to_portal,
    send_publication_to_portal,
    send_questionnaire_response_to_portal,
    send_research_project_to_portal,
    send_researcher_to_portal,
    send_steps_to_portal,
    send_tms_data_to_portal,
    send_tms_setting_to_portal,
)

permission_required = partial(permission_required, raise_exception=True)

icon_class = {
    "block": "fa fa-th-large",
    "instruction": "fa fa-comment",
    "pause": "fa fa-clock-o",
    "questionnaire": "fa fa-list-alt",
    "stimulus": "fa fa-headphones",
    "task": "fa fa-check",
    "task_experiment": "fa fa-wrench",
    "eeg": "fa fa-flash",
    "emg": "fa fa-line-chart",
    "tms": "fa fa-magnet",
    "experimental_protocol": "fa fa-tasks",
    "digital_game_phase": "fa fa-play-circle",
    "generic_data_collection": "fa fa-file",
    "additional_data": "fa fa-puzzle-piece",
    "media_collection": "fa fa-camera",
}

data_type_name = {
    "additional_data": _("additional data"),
    "eeg": "EEG",
    "emg": "EMG",
    "tms": "TMS",
    "digital_game_phase": _("goalkeeper game"),
    "generic_data_collection": _("generic data collection"),
    "questionnaire": _("questionnaire"),
    "media_collection": _("media collection"),
}

delimiter = "-"

# pylint: disable=E1101
# pylint: disable=E1103


class EEGReading:
    file_format = None
    reading = None


@login_required
@permission_required("experiment.view_researchproject")
def research_project_list(
    request, template_name="experiment/research_project_list.html"
):
    research_projects = ResearchProject.objects.order_by("start_date")

    can_send_to_portal = False
    if settings.PORTAL_API["URL"] and settings.SHOW_SEND_TO_PORTAL_BUTTON:
        can_send_to_portal = True

    context = {
        "research_projects": research_projects,
        "can_send_to_portal": can_send_to_portal,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_researchproject")
def research_project_create(
    request, template_name="experiment/research_project_register.html"
):
    research_project_form = ResearchProjectForm(request.POST or None)
    research_project_owner_form = ResearchProjectOwnerForm(
        request.POST or None, initial={"owner": request.user}
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if research_project_form.is_valid():
                research_project_added = research_project_form.save(commit=False)
                research_project_added.owner_id = request.POST.get("owner")
                research_project_added.save()

                messages.success(request, _("Study created successfully."))
                redirect_url = reverse(
                    "research_project_view", args=(research_project_added.id,)
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "research_project_form": research_project_form,
        "research_project_owner_form": research_project_owner_form,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


def check_can_change(user, research_project):
    if not get_can_change(user, research_project):
        raise PermissionDenied


def get_can_change(user, research_project):
    return (
        user.has_perm("experiment.change_researchproject")
        and user == research_project.owner
    ) or user.has_perm("experiment.change_researchproject_from_others")


def get_can_change_research_project_owner(user, research_project):
    return user.has_perm("experiment.change_researchproject_owner")


@login_required
@permission_required("experiment.view_researchproject")
def research_project_view(
    request,
    research_project_id,
    template_name="experiment/research_project_register.html",
):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    research_project_form = ResearchProjectForm(
        request.POST or None, instance=research_project
    )
    research_project_owner_form = ResearchProjectOwnerForm(
        request.POST or None, instance=research_project
    )

    for field in research_project_form.fields:
        research_project_form.fields[field].widget.attrs["disabled"] = True

    for field in research_project_owner_form.fields:
        research_project_owner_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            if (
                QuestionnaireResponse.objects.filter(
                    subject_of_group__group__experiment__research_project_id=research_project_id
                ).count()
                == 0
            ):
                try:
                    for keyword in research_project.keywords.all():
                        manage_keywords(
                            keyword,
                            ResearchProject.objects.exclude(id=research_project.id),
                        )

                    research_project.delete()
                    messages.success(request, _("Study removed successfully."))
                    return redirect("research_project_list")
                except ProtectedError:
                    messages.error(request, _("Error trying to delete research."))
                    redirect_url = reverse(
                        "research_project_view", args=(research_project_id,)
                    )
                    return HttpResponseRedirect(redirect_url)

            else:
                messages.error(
                    request,
                    _(
                        "Impossible to delete group because there is (are) questionnaire(s) answered."
                    ),
                )
                redirect_url = reverse(
                    "research_project_view", args=(research_project_id,)
                )
                return HttpResponseRedirect(redirect_url)

        if request.POST["action"] == "copy_experiment":
            experiment_id = request.POST["experiment_id"]
            experiment = get_object_or_404(Experiment, pk=experiment_id)
            copy_experiment(experiment)
            messages.success(request, _("The experiment was copied."))
            redirect_url = reverse("experiment_view", args=(experiment.id,))
            return HttpResponseRedirect(redirect_url)

        if request.POST["action"] == "copy_experiment_with_data":
            experiment_id = request.POST["experiment_id"]
            experiment = get_object_or_404(Experiment, pk=experiment_id)
            copy_experiment(experiment, True)
            messages.success(
                request, _("The experiment was copied with " "all data collections")
            )
            redirect_url = reverse("experiment_view", args=(experiment.id,))
            return HttpResponseRedirect(redirect_url)

        if request.POST["action"][:10] == "create_pdf":
            experiment_id = request.POST["action"][11:]
            experiment = get_object_or_404(Experiment, pk=experiment_id)
            researchers = ExperimentResearcher.objects.filter(experiment=experiment)
            groups = Group.objects.filter(experiment=experiment)
            experimental_protocol_image = []
            language_code = request.LANGUAGE_CODE
            for group in groups:
                if group.experimental_protocol:
                    tree = get_block_tree(group.experimental_protocol, language_code)
                    image = get_experimental_protocol_image(
                        group.experimental_protocol, tree, True
                    )
                    group_and_image = [group.title, image]
                    experimental_protocol_image.append(group_and_image)

            return render_to_pdf(
                "experiment/experiment_info_pdf.html",
                {
                    "pagesize": "A4",
                    "experiment": experiment,
                    "researchers": researchers,
                    "groups": groups,
                    "experimental_protocol_image": experimental_protocol_image,
                },
            )

    context = {
        "can_change": get_can_change(request.user, research_project),
        "experiments": research_project.experiment_set.order_by("title"),
        "keywords": research_project.keywords.order_by("name"),
        "research_project": research_project,
        "research_project_form": research_project_form,
        "research_project_owner_form": research_project_owner_form,
    }

    return render(request, template_name, context)


def get_owner_full_name(research_project):
    owners_full_name = ""
    if research_project.owner:
        owners_full_name = research_project.owner.get_full_name()
    return owners_full_name


@login_required
@permission_required("experiment.change_researchproject")
def research_project_update(
    request,
    research_project_id,
    template_name="experiment/research_project_register.html",
):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    #  com o decorator @permission_required('experiment.change_researchproject'),
    #  a função abaixo é desnecessaria:
    #
    #  check_can_change(request.user, research_project)

    research_project_form = ResearchProjectForm(
        request.POST or None, instance=research_project
    )
    research_project_owner_form = ResearchProjectOwnerForm(
        request.POST or None, instance=research_project
    )

    can_change_research_project_owner = get_can_change_research_project_owner(
        request.user, research_project
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            changed = False
            form_error = False

            # owner field
            if can_change_research_project_owner:
                if research_project_owner_form.is_valid():
                    if research_project_owner_form.has_changed():
                        research_project_owner_form.save()
                        changed = True
                else:
                    form_error = True

            # other fields
            if research_project_form.is_valid():
                if research_project_form.has_changed():
                    research_project_form.save()
                    changed = True
            else:
                form_error = True

            if not form_error:
                if changed:
                    messages.success(request, _("Research updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "research_project_view", args=(research_project.id,)
                )
                return HttpResponseRedirect(redirect_url)

    if not can_change_research_project_owner:
        research_project_owner_form.fields["owner"].widget.attrs["disabled"] = True

    context = {
        "research_project": research_project,
        "research_project_form": research_project_form,
        "research_project_owner_form": research_project_owner_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def keyword_search_ajax(request):
    keywords_name_list = []
    keywords_list_filtered = []
    search_text = None

    if request.method == "POST":
        search_text = request.POST["search_text"]

        if search_text:
            # Avoid suggesting the creation of a keyword that already exists.
            keywords_list = Keyword.objects.filter(name__icontains=search_text)
            keywords_name_list = keywords_list.values_list("name", flat=True)
            # Avoid suggestion keywords that are already associated with this research project
            research_project = get_object_or_404(
                ResearchProject, pk=request.POST["research_project_id"]
            )
            keywords_included = research_project.keywords.values_list("name", flat=True)
            keywords_list_filtered = keywords_list.exclude(
                name__in=keywords_included
            ).order_by("name")

    return render(
        None,
        "experiment/keyword_ajax_search.html",
        {
            "keywords": keywords_list_filtered,
            "offer_creation": search_text not in keywords_name_list,
            "research_project_id": request.POST["research_project_id"],
            "new_keyword_name": search_text,
        },
    )


@login_required
@permission_required("experiment.change_researchproject")
def keyword_create_ajax(request, research_project_id, keyword_name):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    check_can_change(request.user, research_project)

    keyword = Keyword.objects.create(name=keyword_name)
    keyword.save()

    research_project.keywords.add(keyword)

    redirect_url = reverse("research_project_view", args=(research_project_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.change_researchproject")
def keyword_add_ajax(request, research_project_id, keyword_id):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    check_can_change(request.user, research_project)

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
@permission_required("experiment.change_researchproject")
def keyword_remove_ajax(request, research_project_id, keyword_id):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    check_can_change(request.user, research_project)

    keyword = get_object_or_404(Keyword, pk=keyword_id)
    research_project.keywords.remove(keyword)

    manage_keywords(keyword, ResearchProject.objects.all())

    redirect_url = reverse("research_project_view", args=(research_project_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.view_researchproject")
def publication_list(request, template_name="experiment/publication_list.html"):
    publications = Publication.objects.all().order_by("title")
    context = {
        "publications": publications,
    }
    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_researchproject")
def publication_create(request, template_name="experiment/publication_register.html"):
    publication_form = PublicationForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if publication_form.is_valid():
                publication_added = publication_form.save()

                messages.success(request, _("Publication created successfully."))
                redirect_url = reverse("publication_view", args=(publication_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {"publication_form": publication_form, "creating": True, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def publication_view(
    request, publication_id, template_name="experiment/publication_register.html"
):
    publication = get_object_or_404(Publication, pk=publication_id)

    publication_form = PublicationForm(request.POST or None, instance=publication)

    for field in publication_form.fields:
        publication_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            publication.delete()
            messages.success(request, _("Publication removed successfully."))
            redirect_url = reverse("publication_list", args=())
            return HttpResponseRedirect(redirect_url)

        elif request.POST["action"][:7] == "remove-":
            experiment = get_object_or_404(
                Experiment, pk=int(request.POST["action"][7:])
            )
            publication.experiments.remove(experiment)
            messages.success(
                request, _("Experiment removed from publication successfully.")
            )
            redirect_url = reverse("publication_view", args=(publication_id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "publication": publication,
        "publication_form": publication_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_researchproject")
def publication_update(
    request, publication_id, template_name="experiment/publication_register.html"
):
    publication = get_object_or_404(Publication, pk=publication_id)

    publication_form = PublicationForm(request.POST or None, instance=publication)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if publication_form.is_valid():
                if publication_form.has_changed():
                    publication_form.save()
                    messages.success(request, _("Publication updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("publication_view", args=(publication.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "publication": publication,
        "publication_form": publication_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
def publication_add_experiment(
    request, publication_id, template_name="experiment/publication_add_experiment.html"
):
    publication = get_object_or_404(Publication, pk=publication_id)
    research_projects = ResearchProject.objects.all().order_by("title")
    experiments = Experiment.objects.all().order_by("title")

    if request.method == "POST":
        if request.POST["action"] == "add-experiment":
            if "experiment_selected" in request.POST:
                experiment_selected = get_object_or_404(
                    Experiment, pk=int(request.POST["experiment_selected"])
                )
                if experiment_selected in publication.experiments.all():
                    messages.success(
                        request, _("Experiment already included in the publication.")
                    )
                else:
                    publication.experiments.add(experiment_selected)
                    publication.save()
                    messages.success(request, _("Experiment included successfully."))

            redirect_url = reverse("publication_view", args=(publication.id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "publication": publication,
        "research_projects": research_projects,
        "experiments": experiments,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


def get_experiments_by_research_project(request, research_project_id):
    if research_project_id == "0":
        list_of_experiments = Experiment.objects.all().order_by("title")
    else:
        list_of_experiments = Experiment.objects.filter(
            research_project_id=research_project_id
        ).order_by("title")

    json_experiment_list = serializers.serialize("json", list_of_experiments)

    return HttpResponse(json_experiment_list, content_type="application/json")


@login_required
@permission_required("experiment.add_experiment")
def experiment_create(
    request, research_project_id, template_name="experiment/experiment_register.html"
):
    research_project = get_object_or_404(ResearchProject, pk=research_project_id)

    check_can_change(request.user, research_project)

    if request.method == "POST":
        experiment_form = ExperimentForm(
            request.POST or None,
            request.FILES,
            initial={"research_project": research_project_id},
        )
        if request.POST["action"] == "save":
            if experiment_form.is_valid():
                experiment_added = experiment_form.save()

                messages.success(request, _("Experiment created successfully."))

                redirect_url = reverse("experiment_view", args=(experiment_added.id,))
                return HttpResponseRedirect(redirect_url)
    else:
        experiment_form = ExperimentForm(
            request.POST or None, initial={"research_project": research_project_id}
        )

    context = {
        "research_project": ResearchProject.objects.get(id=research_project_id),
        "experiment_form": experiment_form,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def experiment_view(
    request, experiment_id, template_name="experiment/experiment_register.html"
):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    group_list = Group.objects.filter(experiment=experiment).order_by("title")
    source_code_list = SourceCode.objects.filter(experiment=experiment).order_by("name")
    eeg_setting_list = EEGSetting.objects.filter(experiment=experiment).order_by("name")
    emg_setting_list = EMGSetting.objects.filter(experiment=experiment).order_by("name")
    tms_setting_list = TMSSetting.objects.filter(experiment=experiment).order_by("name")
    context_tree_list = ContextTree.objects.filter(experiment=experiment).order_by(
        "name"
    )
    experiment_form = ExperimentForm(request.POST or None, instance=experiment)
    collaborators = ExperimentResearcher.objects.filter(experiment=experiment).order_by(
        "channel_index"
    )
    portal = settings.PORTAL_API.get("URL")

    for field in experiment_form.fields:
        experiment_form.fields[field].widget.attrs["disabled"] = True

    experiment_status_portal = get_experiment_status_portal(experiment_id)

    if request.method == "POST":
        if request.POST["action"][:20] == "remove_collaborator-":
            collaborator = get_object_or_404(
                ExperimentResearcher, pk=request.POST["action"][20:]
            )
            try:
                collaborator.delete()
                messages.success(request, _("Researcher removed successfully."))
            except ProtectedError:
                messages.error(request, _("Error trying to delete a researcher."))
            redirect_url = reverse("experiment_view", args=(experiment_id,))
            return HttpResponseRedirect(redirect_url)

        if request.POST["action"] == "remove":
            check_can_change(request.user, experiment.research_project)

            # Check if there is data collection for its groups
            experiment_has_data_collection = False
            for group in group_list:
                if group_has_data_collection(group):
                    experiment_has_data_collection = True
                    break

            if not experiment_has_data_collection:
                # Check if there is component_configuration
                for component_configuration in ComponentConfiguration.objects.filter(
                    component__experiment=experiment
                ):
                    if not remove_data_configuration_tree(component_configuration):
                        messages.error(
                            request,
                            _(
                                "It was not possible to exclude because there is data collection associated."
                            ),
                        )
                        redirect_url = reverse("experiment_view", args=(experiment_id,))
                        return HttpResponseRedirect(redirect_url)

                try:
                    experiment.delete()
                    messages.success(request, _("Experiment removed successfully."))
                    return redirect(
                        "research_project_view",
                        research_project_id=experiment.research_project.id,
                    )
                except ProtectedError:
                    messages.error(
                        request,
                        _(
                            "It was not possible to delete experiment "
                            "because there are groups connected."
                        ),
                    )
                    redirect_url = reverse("experiment_view", args=(experiment_id,))
                    return HttpResponseRedirect(redirect_url)
            else:
                messages.error(
                    request,
                    _(
                        "Impossible to delete experiment because there is data collection associated."
                    ),
                )

                redirect_url = reverse("experiment_view", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": get_can_change(request.user, experiment.research_project),
        "experiment": experiment,
        "last_schedule_of_sending": ScheduleOfSending.objects.filter(
            experiment=experiment
        )
        .order_by("schedule_datetime")
        .last(),
        "experiment_form": experiment_form,
        "group_list": group_list,
        "source_code_list": source_code_list,
        "eeg_setting_list": eeg_setting_list,
        "emg_setting_list": emg_setting_list,
        "tms_setting_list": tms_setting_list,
        "context_tree_list": context_tree_list,
        "research_project": experiment.research_project,
        "experiment_status_portal": experiment_status_portal,
        "collaborators": collaborators,
        "portal": portal,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def experiment_update(
    request, experiment_id, template_name="experiment/experiment_register.html"
):
    experiment = get_object_or_404(Experiment, pk=experiment_id)
    check_can_change(request.user, experiment.research_project)
    group_list = Group.objects.filter(experiment=experiment)
    portal = settings.PORTAL_API.get("URL")

    if request.method == "POST":
        experiment_form = ExperimentForm(
            request.POST or None, request.FILES, instance=experiment
        )
        if request.POST["action"] == "save":
            if experiment_form.is_valid():
                if experiment_form.has_changed():
                    experiment_form.save()
                    messages.success(request, _("Experiment updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("experiment_view", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)
    else:
        experiment_form = ExperimentForm(request.POST or None, instance=experiment)

    context = {
        "research_project": experiment.research_project,
        "experiment_form": experiment_form,
        "editing": True,
        "group_list": group_list,
        "experiment": experiment,
        "portal": portal,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_experiment")
def collaborator_create(
    request, experiment_id, template_name="experiment/collaborator_register.html"
):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    collaborators_added = ExperimentResearcher.objects.filter(
        experiment_id=experiment_id
    )
    collaborators_added_ids = collaborators_added.values_list(
        "researcher_id", flat=True
    )

    collaborators = (
        User.objects.filter(is_active=True)
        .exclude(pk__in=collaborators_added_ids)
        .order_by("first_name", "last_name")
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            collaborators_selected = request.POST.getlist("collaborators")

            if collaborators_selected:
                num_of_collaborator = len(collaborators_selected)
                for collaborator in collaborators_selected:
                    collaborator = ExperimentResearcher(
                        experiment_id=experiment_id, researcher_id=collaborator
                    )
                    collaborator.save()

                if num_of_collaborator == 1:
                    messages.success(request, _("1 researcher was added successfully."))
                else:
                    messages.success(
                        request,
                        _("%d researchers were added successfully.")
                        % num_of_collaborator,
                    )

                redirect_url = reverse("experiment_view", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Please, select at least one researcher."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "experiment": experiment,
        "collaborators": collaborators,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
# @permission_required('experiment.export_experiment')  # TODO: add permisson
def experiment_export(request, experiment_id):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    export = ExportExperiment(experiment)
    err_code_experiment, err_message_experiment = export.export_all()

    if err_code_experiment:
        messages.warning(request, err_message_experiment)

    file = open(path.join(export.temp_dir, export.FILE_NAME_ZIP), "rb")
    response = HttpResponse(file, content_type="application/zip")
    response["Content-Length"] = path.getsize(file.name)
    response["Content-Disposition"] = "attachment; filename=%s" % smart_str(
        "experiment.zip"
    )

    return response


def handle_uploaded_file(file):
    with tempfile.NamedTemporaryFile("wb+", delete=False) as f:
        for chunk in file.chunks():
            f.write(chunk)
        return f.name


@login_required
# @permission_required('experiment.import_experiment')  # TODO: add permissons
def experiment_import(
    request, template_name="experiment/experiment_import.html", research_project_id=None
):
    if request.method == "GET":
        return render(
            request, template_name, context={"research_project_id": research_project_id}
        )

    if request.method == "POST":
        if not request.POST.get("action"):
            file = request.FILES.get("file")
            if not file:
                messages.warning(request, _("Please select a zip file"))
                return HttpResponseRedirect(reverse("experiment_import"))

            file_name = handle_uploaded_file(file)
            import_experiment = ImportExperiment(file_name)

            # Deal with patients before trying to import the experiment
            (
                err_code_patients,
                err_message_patients,
                patients_with_conflict,
            ) = import_experiment.check_for_duplicates_of_participants()

            if err_code_patients:
                messages.error(request, _(err_message_patients))
                if research_project_id:
                    return HttpResponseRedirect(
                        reverse(
                            "experiment_import",
                            kwargs={"research_project_id": research_project_id},
                        )
                    )
                else:
                    return HttpResponseRedirect(reverse("experiment_import"))

            request.session["patients"] = patients_with_conflict
            request.session["file_name"] = file_name

            if patients_with_conflict and not request.session.get(
                "patients_conflicts_resolved", None
            ):
                return render(
                    request,
                    "experiment/decide_about_patients.html",
                    context={"patients": patients_with_conflict},
                )

    patients_to_update = request.POST.getlist("from[]")

    file_name = request.session.get("file_name")
    import_experiment = ImportExperiment(file_name)
    result_code, result_message = import_experiment.import_all(
        request, research_project_id, patients_to_update
    )
    os.remove(file_name)

    if result_code:
        if result_code == import_experiment.BAD_JSON_FILE_ERROR_CODE:
            messages.error(request, _(result_message))
            if research_project_id:
                return HttpResponseRedirect(
                    reverse(
                        "experiment_import",
                        kwargs={"research_project_id": research_project_id},
                    )
                )
            else:
                return HttpResponseRedirect(reverse("experiment_import"))
        if result_code == import_experiment.LIMESURVEY_ERROR:
            messages.error(request, result_message)
    if research_project_id:
        messages.success(request, _("Experiment successfully imported."))
    else:
        messages.success(
            request, _("Experiment successfully imported. New study was created.")
        )

    # Push new object to session to display log to users
    request.session["objects_imported"] = import_experiment.get_new_objects()
    return HttpResponseRedirect(reverse("import_log"))


@login_required
# @permission_required('experiment.import_experiment')  # TODO: add permissons
def import_log(request):
    context = request.session.get("objects_imported")
    return render(request, "experiment/import_log.html", context)


@login_required
@permission_required("experiment.change_experiment")
def experiment_schedule_of_sending(
    request,
    experiment_id,
    template_name="experiment/experiment_schedule_of_sending.html",
):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    resend_experiment_form = ResendExperimentForm(request.POST or None)

    check_can_change(request.user, experiment.research_project)

    last_schedule_of_sending = (
        ScheduleOfSending.objects.filter(experiment=experiment)
        .order_by("schedule_datetime")
        .last()
    )

    surveys = Questionnaires()
    limesurvey_available = check_limesurvey_access(request, surveys)

    experiment_questionnaires = {}
    for group in experiment.groups.all():
        list_of_eeg_configuration = create_list_of_trees(
            group.experimental_protocol, "questionnaire"
        )
        for path_tree in list_of_eeg_configuration:
            component_id = ComponentConfiguration.objects.get(
                pk=path_tree[-1][0]
            ).component_id
            questionnaire = Questionnaire.objects.get(pk=component_id)
            if questionnaire.survey.lime_survey_id not in experiment_questionnaires:
                language = get_questionnaire_language(
                    surveys, questionnaire.survey.lime_survey_id, request.LANGUAGE_CODE
                )
                questionnaire_title = find_questionnaire_name(
                    questionnaire.survey, language
                )["name"]

                current_sensitive_questions = SensitiveQuestion.objects.filter(
                    survey=questionnaire.survey
                )
                current_portal_selected_questions = (
                    PortalSelectedQuestion.objects.filter(
                        experiment=experiment, survey=questionnaire.survey
                    )
                )

                field_code = get_survey_header(
                    surveys, questionnaire.survey, language, "code"
                )
                field_text = get_survey_header(
                    surveys, questionnaire.survey, language, "full"
                )

                counter = 0
                available_fields = []
                amount_to_send = 0
                while counter < len(field_code):
                    if (
                        field_code[counter]
                        not in questionnaire_evaluation_fields_excluded
                    ):
                        select_to_send = False
                        if (
                            not current_portal_selected_questions.exists()
                            or current_portal_selected_questions.filter(
                                question_code=field_code[counter]
                            ).exists()
                        ):
                            select_to_send = True
                            amount_to_send += 1

                        available_fields.append(
                            {
                                "code": field_code[counter],
                                "text": field_text[counter],
                                "is_sensitive": current_sensitive_questions.filter(
                                    code=field_code[counter]
                                ).exists(),
                                "select_to_send": select_to_send,
                                "is_selected_in_db": current_portal_selected_questions.filter(
                                    question_code=field_code[counter]
                                ).exists(),
                            }
                        )
                    counter += 1

                experiment_questionnaires[questionnaire.survey.lime_survey_id] = {
                    "survey": questionnaire.survey,
                    "title": questionnaire_title,
                    "fields": available_fields,
                    "selected_counter": amount_to_send,
                }

    surveys.release_session_key()

    if request.method == "POST":
        if request.POST["action"] == "send":
            selected_fields = {}
            for field in request.POST.getlist("to[]"):
                sid, field_name = field.split("*")
                sid = int(sid)
                if sid not in selected_fields:
                    selected_fields[sid] = [field_name]
                else:
                    selected_fields[sid].append(field_name)

            # save questionnaire configuration
            for (
                questionnaire_key,
                questionnaire_value,
            ) in experiment_questionnaires.items():
                for field in questionnaire_value["fields"]:
                    is_to_send = False
                    if (
                        not field["is_sensitive"]
                        and questionnaire_key in selected_fields
                        and field["code"] in selected_fields[questionnaire_key]
                    ):
                        is_to_send = True
                    if is_to_send and not field["is_selected_in_db"]:
                        PortalSelectedQuestion.objects.create(
                            experiment=experiment,
                            survey=questionnaire_value["survey"],
                            question_code=field["code"],
                        )
                    else:
                        if not is_to_send and field["is_selected_in_db"]:
                            portal_selected_question = (
                                PortalSelectedQuestion.objects.filter(
                                    experiment=experiment,
                                    survey=questionnaire_value["survey"],
                                    question_code=field["code"],
                                )
                            )
                            if portal_selected_question.exists():
                                portal_selected_question.delete()

            if experiment.last_sending:
                new_schedule = resend_experiment_form.save(commit=False)
            else:
                new_schedule = ScheduleOfSending()

            new_schedule.experiment = experiment
            new_schedule.responsible = request.user
            new_schedule.status = "scheduled"
            send_age = request.POST.get("send_age")
            new_schedule.send_participant_age = True if send_age else False
            new_schedule.save()
            messages.success(
                request, _("Experiment scheduled to be sent successfully.")
            )

            redirect_url = reverse("experiment_view", args=(experiment_id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "experiment": experiment,
        "last_schedule_of_sending": last_schedule_of_sending,
        "resend_experiment_form": resend_experiment_form,
        "experiment_questionnaires": experiment_questionnaires,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def schedule_of_sending_list(
    request, template_name="experiment/schedule_of_sending_list.html"
):
    if request.method == "POST":
        if request.POST["action"] == "send-to-portal":
            send_all_experiments_to_portal()
            messages.success(request, _("Experiments sent successfully."))

    list_of_schedule_of_sending = ScheduleOfSending.objects.filter(
        status="scheduled"
    ).order_by("schedule_datetime")

    portal_status = get_portal_status()
    if not portal_status:
        messages.warning(request, _("Portal is not available to send experiments"))

    context = {
        "list_of_schedule_of_sending": list_of_schedule_of_sending,
        "portal_status": portal_status,
    }

    return render(request, template_name, context)


def date_of_first_data_collection(subject_of_group):
    result = None

    dates_to_compare = [
        QuestionnaireResponse.objects.filter(
            subject_of_group=subject_of_group
        ).aggregate(Min("date"))["date__min"],
        EEGData.objects.filter(subject_of_group=subject_of_group).aggregate(
            Min("date")
        )["date__min"],
        EMGData.objects.filter(subject_of_group=subject_of_group).aggregate(
            Min("date")
        )["date__min"],
        AdditionalData.objects.filter(subject_of_group=subject_of_group).aggregate(
            Min("date")
        )["date__min"],
        TMSData.objects.filter(subject_of_group=subject_of_group).aggregate(
            Min("date")
        )["date__min"],
        DigitalGamePhaseData.objects.filter(
            subject_of_group=subject_of_group
        ).aggregate(Min("date"))["date__min"],
        GenericDataCollectionData.objects.filter(
            subject_of_group=subject_of_group
        ).aggregate(Min("date"))["date__min"],
        MediaCollectionData.objects.filter(subject_of_group=subject_of_group).aggregate(
            Min("date")
        )["date__min"],
    ]

    for date_to_compare in dates_to_compare:
        if date_to_compare:
            result = min(result, date_to_compare) if result else date_to_compare

    return result


def send_all_experiments_to_portal():
    language_code = "en"
    for schedule_of_sending in ScheduleOfSending.objects.filter(
        status="scheduled"
    ).order_by("schedule_datetime"):
        print(
            "\nExperiment %s - %s\n"
            % (schedule_of_sending.experiment.id, schedule_of_sending.experiment.title)
        )

        if send_experiment_to_portal(schedule_of_sending.experiment):
            # sending research project
            created_research_project = send_research_project_to_portal(
                schedule_of_sending.experiment
            )

            # sending researcher
            send_researcher_to_portal(
                created_research_project["id"],
                schedule_of_sending.experiment.research_project.owner,
            )

            list_of_eeg_setting = {}
            list_of_emg_setting = {}
            list_of_tms_setting = {}
            list_of_context_tree = {}

            # sending experiment researchers
            for (
                experiment_researcher
            ) in schedule_of_sending.experiment.researchers.all():
                # only send experiment researcher with first_name and
                # last_name
                if (
                    not experiment_researcher.researcher.first_name
                    and not experiment_researcher.researcher.last_name
                ):
                    continue
                else:
                    send_experiment_researcher_to_portal(experiment_researcher)

            # sending publications
            for publication in schedule_of_sending.experiment.publication_set.all():
                send_publication_to_portal(
                    publication, schedule_of_sending.experiment.id
                )

            # sending groups
            for group in schedule_of_sending.experiment.groups.all():
                portal_group = send_group_to_portal(group)

                # eeg settings
                list_of_eeg_configuration = create_list_of_trees(
                    group.experimental_protocol, "eeg"
                )
                for path_tree in list_of_eeg_configuration:
                    component_id = ComponentConfiguration.objects.get(
                        pk=path_tree[-1][0]
                    ).component_id
                    eeg_setting = EEG.objects.get(pk=component_id).eeg_setting
                    if eeg_setting.id not in list_of_eeg_setting:
                        portal_eeg_setting = send_eeg_setting_to_portal(eeg_setting)
                        list_of_eeg_setting[eeg_setting.id] = portal_eeg_setting["id"]

                for eeg_data in EEGData.objects.filter(
                    subject_of_group__group__experiment=group.experiment
                ):
                    if eeg_data.eeg_setting.id not in list_of_eeg_setting:
                        portal_eeg_setting = send_eeg_setting_to_portal(
                            eeg_data.eeg_setting
                        )
                        list_of_eeg_setting[
                            eeg_data.eeg_setting.id
                        ] = portal_eeg_setting["id"]

                # emg settings
                list_of_emg_configuration = create_list_of_trees(
                    group.experimental_protocol, "emg"
                )
                for path_tree in list_of_emg_configuration:
                    component_id = ComponentConfiguration.objects.get(
                        pk=path_tree[-1][0]
                    ).component_id
                    emg_setting = EMG.objects.get(pk=component_id).emg_setting
                    if emg_setting.id not in list_of_emg_setting:
                        portal_emg_setting = send_emg_setting_to_portal(emg_setting)
                        list_of_emg_setting[emg_setting.id] = portal_emg_setting["id"]

                for emg_data in EMGData.objects.filter(
                    subject_of_group__group__experiment=group.experiment
                ):
                    if emg_data.emg_setting.id not in list_of_emg_setting:
                        portal_emg_setting = send_emg_setting_to_portal(
                            emg_data.emg_setting
                        )
                        list_of_emg_setting[
                            emg_data.emg_setting.id
                        ] = portal_emg_setting["id"]

                # tms settings
                list_of_tms_configuration = create_list_of_trees(
                    group.experimental_protocol, "tms"
                )
                for path_tree in list_of_tms_configuration:
                    component_id = ComponentConfiguration.objects.get(
                        pk=path_tree[-1][0]
                    ).component_id
                    tms_setting = TMS.objects.get(pk=component_id).tms_setting
                    if tms_setting.id not in list_of_tms_setting:
                        portal_tms_setting = send_tms_setting_to_portal(tms_setting)
                        list_of_tms_setting[tms_setting.id] = portal_tms_setting["id"]

                for tms_data in TMSData.objects.filter(
                    subject_of_group__group__experiment=group.experiment
                ):
                    if tms_data.tms_setting.id not in list_of_tms_setting:
                        portal_tms_setting = send_tms_setting_to_portal(
                            tms_data.tms_setting
                        )
                        list_of_tms_setting[
                            tms_data.tms_setting.id
                        ] = portal_tms_setting["id"]

                # context trees
                list_of_digital_game_phase_configuration = create_list_of_trees(
                    group.experimental_protocol, "digital_game_phase"
                )
                for path_tree in list_of_digital_game_phase_configuration:
                    component_id = ComponentConfiguration.objects.get(
                        pk=path_tree[-1][0]
                    ).component_id
                    context_tree = DigitalGamePhase.objects.get(
                        pk=component_id
                    ).context_tree
                    if context_tree.id not in list_of_context_tree:
                        portal_context_tree = send_context_tree_to_portal(context_tree)
                        list_of_context_tree[context_tree.id] = portal_context_tree[
                            "id"
                        ]

                # participants
                portal_participant_list = {}
                for subject_of_group in group.subjectofgroup_set.all():
                    first_data_collection = date_of_first_data_collection(
                        subject_of_group
                    )
                    portal_participant = send_participant_to_portal(
                        schedule_of_sending,
                        portal_group["id"],
                        subject_of_group.subject,
                        first_data_collection,
                    )
                    portal_participant_list[subject_of_group.id] = portal_participant[
                        "id"
                    ]

                # experimental protocol
                portal_step_list = {}

                if group.experimental_protocol:
                    tree = get_block_tree(group.experimental_protocol, language_code)
                    textual_description = (
                        get_description_from_experimental_protocol_tree(tree)
                    )
                    image = get_experimental_protocol_image(
                        group.experimental_protocol, tree, True
                    )

                    # Steps
                    step_list = send_steps_to_portal(
                        portal_group["id"],
                        tree,
                        list_of_eeg_setting,
                        list_of_emg_setting,
                        list_of_tms_setting,
                        list_of_context_tree,
                        language_code,
                    )
                    root_step_id = step_list["0"]["portal_step_id"]

                    list_of_trees = create_list_of_trees(
                        group.experimental_protocol, None
                    )
                    for tree in list_of_trees:
                        path_tree = [item[0] for item in tree]
                        data_configuration_tree_id = list_data_configuration_tree(
                            path_tree[-1], path_tree
                        )
                        numeration = tree[-1][-1]
                        step_list[numeration][
                            "data_configuration_tree_id"
                        ] = data_configuration_tree_id
                        if data_configuration_tree_id:
                            portal_step_list[data_configuration_tree_id] = step_list[
                                numeration
                            ]["portal_step_id"]

                    # eeg data
                    eeg_data_list = EEGData.objects.filter(
                        subject_of_group__group=group
                    )

                    for eeg_data in eeg_data_list:
                        portal_file_id_list = []
                        for eeg_file in eeg_data.eeg_files.all():
                            portal_file = send_file_to_portal(eeg_file.file.name)
                            portal_file_id_list.append(portal_file["id"])

                        send_eeg_data_to_portal(
                            portal_participant_list[eeg_data.subject_of_group.id],
                            portal_step_list[eeg_data.data_configuration_tree.id],
                            portal_file_id_list,
                            list_of_eeg_setting[eeg_data.eeg_setting.id],
                            eeg_data,
                        )

                    # Emg data
                    emg_data_list = EMGData.objects.filter(
                        subject_of_group__group=group
                    )

                    for emg_data in emg_data_list:
                        portal_file_id_list = []
                        for emg_file in emg_data.emg_files.all():
                            portal_file = send_file_to_portal(emg_file.file.name)
                            portal_file_id_list.append(portal_file["id"])

                        send_emg_data_to_portal(
                            portal_participant_list[emg_data.subject_of_group.id],
                            portal_step_list[emg_data.data_configuration_tree.id],
                            portal_file_id_list,
                            list_of_emg_setting[emg_data.emg_setting.id],
                            emg_data,
                        )

                    # Tms data
                    tms_data_files = TMSData.objects.filter(
                        subject_of_group__group=group
                    )

                    for tms_data_file in tms_data_files:
                        send_tms_data_to_portal(
                            portal_participant_list[tms_data_file.subject_of_group.id],
                            portal_step_list[tms_data_file.data_configuration_tree.id],
                            list_of_tms_setting[tms_data_file.tms_setting.id],
                            tms_data_file,
                        )

                    # Digital game phase data
                    digital_game_phase_data_list = DigitalGamePhaseData.objects.filter(
                        subject_of_group__group=group
                    )

                    for digital_game_phase_data in digital_game_phase_data_list:
                        portal_file_id_list = []
                        for (
                            digital_game_phase_file
                        ) in digital_game_phase_data.digital_game_phase_files.all():
                            portal_file = send_file_to_portal(
                                digital_game_phase_file.file.name
                            )
                            portal_file_id_list.append(portal_file["id"])

                        send_digital_game_phase_data_to_portal(
                            portal_participant_list[
                                digital_game_phase_data.subject_of_group.id
                            ],
                            portal_step_list[
                                digital_game_phase_data.data_configuration_tree.id
                            ],
                            portal_file_id_list,
                            digital_game_phase_data,
                        )

                    # Questionnaire response
                    surveys = Questionnaires()
                    if surveys.session_key:
                        # Questionnaire response
                        questionnaire_responses = QuestionnaireResponse.objects.filter(
                            subject_of_group__group=group
                        )

                        for questionnaire_response in questionnaire_responses:
                            component_id = (
                                questionnaire_response.data_configuration_tree.component_configuration.component_id
                            )
                            questionnaire = Questionnaire.objects.get(pk=component_id)
                            limesurvey_id = questionnaire.survey.lime_survey_id
                            token = surveys.get_participant_properties(
                                limesurvey_id, questionnaire_response.token_id, "token"
                            )
                            questionnaire_language = get_questionnaire_language(
                                surveys, limesurvey_id, language_code
                            )
                            responses_string = surveys.get_responses_by_token(
                                limesurvey_id, token, questionnaire_language
                            )
                            limesurvey_response = {"questions": "", "answers": ""}

                            if isinstance(responses_string, bytes):
                                reader = csv.reader(
                                    StringIO(responses_string.decode()), delimiter=","
                                )
                                responses_list = []
                                for row in reader:
                                    responses_list.append(row)

                                # Need multiple choice questions types to make replacement just below
                                # TODO (NES-991): make a test for getting multiple choice questions
                                error, question_list = QuestionnaireUtils.get_questions(
                                    surveys, limesurvey_id, questionnaire_language
                                )
                                if question_list:
                                    # Import here because of ImportError
                                    # (cannot import name) exception
                                    # possibly due to circular import error.
                                    # TODO: see answer in:
                                    # https://stackoverflow.com/questions/744373/circular-or-cyclic-imports-in-python
                                    # TODO: for other solutions
                                    from export.export import (
                                        replace_multiple_choice_question_answers,
                                    )

                                    replace_multiple_choice_question_answers(
                                        responses_list, question_list
                                    )

                                if len(responses_list) > 1:
                                    # Get fields to send
                                    fields_to_send = [
                                        item.question_code
                                        for item in PortalSelectedQuestion.objects.filter(
                                            experiment=group.experiment,
                                            survey=questionnaire.survey,
                                        )
                                    ]

                                    limesurvey_response["questions"] = []
                                    limesurvey_response["answers"] = []

                                    for question_index, question_name in enumerate(
                                        responses_list[0]
                                    ):
                                        if question_name in fields_to_send:
                                            limesurvey_response["questions"].append(
                                                question_name
                                            )
                                            limesurvey_response["answers"].append(
                                                responses_list[1][question_index]
                                            )

                            send_questionnaire_response_to_portal(
                                portal_participant_list[
                                    questionnaire_response.subject_of_group.id
                                ],
                                portal_step_list[
                                    questionnaire_response.data_configuration_tree.id
                                ],
                                json.dumps(limesurvey_response),
                                questionnaire_response,
                            )

                        surveys.release_session_key()

                    # additional data
                    additional_data_list = AdditionalData.objects.filter(
                        subject_of_group__group=group
                    )

                    for additional_data in additional_data_list:
                        portal_file_id_list = []
                        for (
                            additional_data_file
                        ) in additional_data.additional_data_files.all():
                            portal_file = send_file_to_portal(
                                additional_data_file.file.name
                            )
                            portal_file_id_list.append(portal_file["id"])

                        # TODO: send additional_file associated to the whole experiment
                        send_additional_data_to_portal(
                            portal_participant_list[
                                additional_data.subject_of_group.id
                            ],
                            portal_step_list[additional_data.data_configuration_tree.id]
                            if additional_data.data_configuration_tree
                            else None,
                            portal_file_id_list,
                            additional_data,
                        )

                    # Generic data collection data
                    generic_data_collection_data_list = (
                        GenericDataCollectionData.objects.filter(
                            subject_of_group__group=group
                        )
                    )

                    for (
                        generic_data_collection_data
                    ) in generic_data_collection_data_list:
                        portal_file_id_list = []
                        for (
                            generic_data_collection_file
                        ) in (
                            generic_data_collection_data.generic_data_collection_files.all()
                        ):
                            portal_file = send_file_to_portal(
                                generic_data_collection_file.file.name
                            )
                            portal_file_id_list.append(portal_file["id"])

                        send_generic_data_collection_data_to_portal(
                            portal_participant_list[
                                generic_data_collection_data.subject_of_group.id
                            ],
                            portal_step_list[
                                generic_data_collection_data.data_configuration_tree.id
                            ],
                            portal_file_id_list,
                            generic_data_collection_data,
                        )

                    # Media collection data
                    media_collection_data_list = MediaCollectionData.objects.filter(
                        subject_of_group__group=group
                    )

                    for media_collection_data in media_collection_data_list:
                        portal_file_id_list = []
                        for (
                            media_collection_file
                        ) in media_collection_data.media_collection_files.all():
                            portal_file = send_file_to_portal(
                                media_collection_file.file.name
                            )
                            portal_file_id_list.append(portal_file["id"])

                        send_media_collection_data_to_portal(
                            portal_participant_list[
                                media_collection_data.subject_of_group.id
                            ],
                            portal_step_list[
                                media_collection_data.data_configuration_tree.id
                            ],
                            portal_file_id_list,
                            media_collection_data,
                        )

                    send_experimental_protocol_to_portal(
                        portal_group_id=portal_group["id"],
                        textual_description=textual_description,
                        image=image,
                        root_step_id=root_step_id,
                    )

            # End of sending
            send_experiment_end_message_to_portal(schedule_of_sending.experiment)

            # Update the schedule to 'sent'
            schedule_of_sending.status = "sent"
            schedule_of_sending.sending_datetime = datetime.now() + timedelta(seconds=5)
            schedule_of_sending.save()

            # Update the last sending date
            experiment = schedule_of_sending.experiment
            experiment.last_sending = schedule_of_sending.sending_datetime
            experiment.save()

            print("Experiment sent\n")


@login_required
@permission_required("experiment.add_subject")
def group_create(
    request, experiment_id, template_name="experiment/group_register.html"
):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    check_can_change(request.user, experiment.research_project)

    group_form = GroupForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if group_form.is_valid():
                group_added = group_form.save(commit=False)
                group_added.experiment_id = experiment_id
                group_added.save()

                messages.success(request, _("Group included successfully."))

                redirect_url = reverse("group_view", args=(group_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "group_form": group_form,
        "creating": True,
        "editing": True,
        "experiment": experiment,
    }

    return render(request, template_name, context)


def recursively_create_list_of_questionnaires_and_statistics(
    block_id, list_of_questionnaires_configuration, num_participants, language_code
):
    for questionnaire_configuration in ComponentConfiguration.objects.filter(
        parent_id=block_id, component__component_type="questionnaire"
    ):
        if questionnaire_configuration.number_of_repetitions is not None:
            fills_per_participant = questionnaire_configuration.number_of_repetitions
            total_fills_needed = num_participants * fills_per_participant
        else:
            fills_per_participant = "Ilimitado"
            total_fills_needed = "Ilimitado"

        amount_of_completed_questionnaires = 0

        questionnaire = Questionnaire.objects.get(
            id=questionnaire_configuration.component.id
        )

        for subject_response in QuestionnaireResponse.objects.filter(
            data_configuration_tree__component_configuration=questionnaire_configuration
        ):
            if (
                subject_response.is_completed == "N"
                or subject_response.is_completed == ""
            ):
                surveys = Questionnaires()

                is_completed = (
                    surveys.get_participant_properties(
                        questionnaire.survey.lime_survey_id,
                        subject_response.token_id,
                        "completed",
                    )
                    or ""
                )
                subject_response.is_completed = is_completed

                surveys.release_session_key()
                subject_response.save()

            if (
                subject_response.is_completed != "N"
                and subject_response.is_completed != ""
            ):
                amount_of_completed_questionnaires += 1

        list_of_questionnaires_configuration.append(
            {
                "survey_title": find_questionnaire_name(
                    questionnaire.survey, language_code
                )["name"],
                "fills_per_participant": fills_per_participant,
                "total_fills_needed": total_fills_needed,
                "total_fills_done": amount_of_completed_questionnaires,
                "id": questionnaire_configuration.id,
            }
        )

    for block_configuration in ComponentConfiguration.objects.filter(
        parent_id=block_id, component__component_type="block"
    ):
        list_of_questionnaires_configuration = (
            recursively_create_list_of_questionnaires_and_statistics(
                Block.objects.get(id=block_configuration.component.id),
                list_of_questionnaires_configuration,
                num_participants,
                language_code,
            )
        )

    return list_of_questionnaires_configuration


@login_required
@permission_required("experiment.view_researchproject")
def group_view(request, group_id, template_name="experiment/group_register.html"):
    group = get_object_or_404(Group, pk=group_id)

    experiment = group.experiment

    group_form = GroupForm(request.POST or None, instance=group)

    for field in group_form.fields:
        group_form.fields[field].widget.attrs["disabled"] = True

    # Navigate the components of the experimental protocol from the root to see if there is any questionnaire component
    # in this group.
    if group.experimental_protocol is not None:
        list_of_questionnaires_configuration = (
            recursively_create_list_of_questionnaires_and_statistics(
                group.experimental_protocol,
                [],
                SubjectOfGroup.objects.filter(group_id=group_id).count(),
                request.LANGUAGE_CODE,
            )
        )
    else:
        list_of_questionnaires_configuration = None

    can_change = get_can_change(request.user, group.experiment.research_project)

    if request.method == "POST":
        if can_change:
            if request.POST["action"] == "remove":
                if not group_has_data_collection(group_id):
                    try:
                        group.delete()
                        messages.success(request, _("Group removed successfully."))
                        redirect_url = reverse(
                            "experiment_view", args=(group.experiment.id,)
                        )
                        return HttpResponseRedirect(redirect_url)
                    except ProtectedError:
                        messages.error(
                            request,
                            _(
                                "Impossible to delete group, because there are dependencies."
                            ),
                        )
                        redirect_url = reverse("group_view", args=(group.id,))
                        return HttpResponseRedirect(redirect_url)
                else:
                    messages.error(
                        request,
                        _(
                            "Impossible to delete group because there is (are) data collection associated."
                        ),
                    )
                    redirect_url = reverse("group_view", args=(group.id,))
                    return HttpResponseRedirect(redirect_url)

            elif request.POST["action"] == "remove_experimental_protocol":
                group.experimental_protocol = None
                group.save()

            elif request.POST["action"] == "copy_experiment":
                copy_experiment(experiment)
                messages.success(request, _("The experiment was copied."))
                redirect_url = reverse("experiment_view", args=(experiment.id,))
                return HttpResponseRedirect(redirect_url)
        else:
            raise PermissionDenied

    experimental_protocol_description = None
    experimental_protocol_image = None

    if group.experimental_protocol:
        tree = get_block_tree(group.experimental_protocol, request.LANGUAGE_CODE)
        experimental_protocol_description = (
            get_description_from_experimental_protocol_tree(tree)
        )
        experimental_protocol_image = get_experimental_protocol_image(
            group.experimental_protocol, tree, True
        )

    context = {
        "can_change": can_change,
        "classification_of_diseases_list": group.classification_of_diseases.all(),
        "group_form": group_form,
        "questionnaires_configuration_list": list_of_questionnaires_configuration,
        "experiment": group.experiment,
        "group": group,
        "group_has_data_collection": group_has_data_collection(group.id),
        "editing": False,
        "experimental_protocol_description": experimental_protocol_description,
        "number_of_subjects": SubjectOfGroup.objects.all().filter(group=group).count(),
        "experimental_protocol_image": experimental_protocol_image,
    }

    return render(request, template_name, context)


def group_has_data_collection(group_id):
    return (
        QuestionnaireResponse.objects.filter(
            subject_of_group__group_id=group_id
        ).count()
        > 0
        or EEGData.objects.filter(subject_of_group__group_id=group_id).count() > 0
        or EMGData.objects.filter(subject_of_group__group_id=group_id).count() > 0
        or AdditionalData.objects.filter(subject_of_group__group_id=group_id).count()
        > 0
        or TMSData.objects.filter(subject_of_group__group_id=group_id).count() > 0
        or DigitalGamePhaseData.objects.filter(
            subject_of_group__group_id=group_id
        ).count()
        > 0
        or GenericDataCollectionData.objects.filter(
            subject_of_group__group_id=group_id
        ).count()
        > 0
        or MediaCollectionData.objects.filter(
            subject_of_group__group_id=group_id
        ).count()
        > 0
    )


@login_required
@permission_required("experiment.change_experiment")
def group_update(request, group_id, template_name="experiment/group_register.html"):
    group = get_object_or_404(Group, pk=group_id)

    check_can_change(request.user, group.experiment.research_project)

    group_form = GroupForm(request.POST or None, instance=group)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if group_form.is_valid():
                if group_form.has_changed():
                    group_form.save()
                    messages.success(request, _("Group updated successfully."))

                    if (
                        group.experiment.last_sending
                        and group.experiment.last_update > group.experiment.last_sending
                    ):
                        messages.info(
                            request,
                            _(
                                '<a href="/experiment/schedule_of_sending/{!s}">'
                                "This experiment was previously sent to the Portal. Click here to resend it."
                                "</a>"
                            ).format(str(group.experiment.id)),
                        )

                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("group_view", args=(group_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "group_form": group_form,
        "editing": True,
        "experiment": group.experiment,
        "group": group,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_subject")
def source_code_create(
    request, experiment_id, template_name="experiment/source_code_register.html"
):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    check_can_change(request.user, experiment.research_project)

    if request.method == "POST":
        source_code_form = SourceCodeForm(
            request.POST or None,
            request.FILES,
        )
        if request.POST["action"] == "save":
            if source_code_form.is_valid():
                source_code_added = source_code_form.save(commit=False)
                source_code_added.experiment_id = experiment_id
                source_code_added.save()

                messages.success(request, _("Source Code included successfully."))

                redirect_url = reverse("source_code_view", args=(source_code_added.id,))
                return HttpResponseRedirect(redirect_url)
    else:
        source_code_form = SourceCodeForm(request.POST or None)

    context = {
        "source_code_form": source_code_form,
        "creating": True,
        "editing": True,
        "experiment": experiment,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def source_code_view(
    request, source_code_id, template_name="experiment/source_code_register.html"
):
    source_code = get_object_or_404(SourceCode, pk=source_code_id)
    source_code_form = SourceCodeForm(request.POST or None, instance=source_code)

    for field in source_code_form.fields:
        source_code_form.fields[field].widget.attrs["disabled"] = True

    can_change = get_can_change(request.user, source_code.experiment.research_project)

    if request.method == "POST":
        if can_change:
            if request.POST["action"] == "remove":
                # TODO: checking if there is some EEG Data using it

                # TODO: checking if there is some EEG Step using it

                experiment_id = source_code.experiment_id

                source_code.delete()

                messages.success(request, _("Source Code was removed successfully."))

                redirect_url = reverse("experiment_view", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

            # if request.POST["action"][:7] == "remove-":
            #     # If action starts with 'remove-' it means that an equipment should be removed from the source_code.
            #     source_code_type = request.POST["action"][7:]

            #     setting_to_be_deleted = None

            #     if eeg_setting_type == "eeg_amplifier":
            #         setting_to_be_deleted = get_object_or_404(
            #             EEGAmplifierSetting, pk=eeg_setting_id
            #         )
            #     elif eeg_setting_type == "eeg_solution":
            #         setting_to_be_deleted = get_object_or_404(
            #             EEGSolutionSetting, pk=eeg_setting_id
            #         )
            #     elif eeg_setting_type == "eeg_filter":
            #         setting_to_be_deleted = get_object_or_404(
            #             EEGFilterSetting, pk=eeg_setting_id
            #         )
            #     elif eeg_setting_type == "eeg_electrode_net_system":
            #         setting_to_be_deleted = get_object_or_404(
            #             EEGElectrodeLayoutSetting, pk=eeg_setting_id
            #         )

            #     # eeg_setting.eeg_machine_setting.delete()
            #     if setting_to_be_deleted:
            #         setting_to_be_deleted.delete()

            #     messages.success(request, _("Setting was removed successfully."))

            #     redirect_url = reverse("eeg_setting_view", args=(eeg_setting.id,))
            #     return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": can_change,
        "source_code_form": source_code_form,
        "experiment": source_code.experiment,
        "source_code": source_code,
        "editing": False,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def source_code_update(
    request, source_code_id, template_name="experiment/source_code_register.html"
):
    source_code = get_object_or_404(SourceCode, pk=source_code_id)

    check_can_change(request.user, source_code.experiment.research_project)

    if request.method == "POST":
        source_code_form = SourceCodeForm(
            request.POST or None, request.FILES, instance=source_code
        )
        if request.POST["action"] == "save":
            if source_code_form.is_valid():
                if source_code_form.has_changed():
                    source_code_form.save()
                    messages.success(request, _("Source Code updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("source_code_view", args=(source_code_id,))
                return HttpResponseRedirect(redirect_url)
    else:
        source_code_form = SourceCodeForm(request.POST or None, instance=source_code)

    context = {
        "source_code_form": source_code_form,
        "editing": True,
        "experiment": source_code.experiment,
        "source_code": source_code,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_subject")
def eeg_setting_create(
    request, experiment_id, template_name="experiment/eeg_setting_register.html"
):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    check_can_change(request.user, experiment.research_project)

    eeg_setting_form = EEGSettingForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if eeg_setting_form.is_valid():
                eeg_setting_added = eeg_setting_form.save(commit=False)
                eeg_setting_added.experiment_id = experiment_id
                eeg_setting_added.save()

                messages.success(request, _("EEG setting included successfully."))

                redirect_url = reverse("eeg_setting_view", args=(eeg_setting_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "eeg_setting_form": eeg_setting_form,
        "creating": True,
        "editing": True,
        "experiment": experiment,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def eeg_setting_view(
    request, eeg_setting_id, template_name="experiment/eeg_setting_register.html"
):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)
    eeg_setting_form = EEGSettingForm(request.POST or None, instance=eeg_setting)

    for field in eeg_setting_form.fields:
        eeg_setting_form.fields[field].widget.attrs["disabled"] = True

    can_change = get_can_change(request.user, eeg_setting.experiment.research_project)

    if request.method == "POST":
        if can_change:
            if request.POST["action"] == "remove":
                # TODO: checking if there is some EEG Data using it

                # TODO: checking if there is some EEG Step using it

                experiment_id = eeg_setting.experiment_id

                eeg_setting.delete()

                messages.success(request, _("EEG setting was removed successfully."))

                redirect_url = reverse("experiment_view", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

            if request.POST["action"][:7] == "remove-":
                # If action starts with 'remove-' it means that an equipment should be removed from the eeg_setting.
                eeg_setting_type = request.POST["action"][7:]

                setting_to_be_deleted = None

                if eeg_setting_type == "eeg_amplifier":
                    setting_to_be_deleted = get_object_or_404(
                        EEGAmplifierSetting, pk=eeg_setting_id
                    )
                elif eeg_setting_type == "eeg_solution":
                    setting_to_be_deleted = get_object_or_404(
                        EEGSolutionSetting, pk=eeg_setting_id
                    )
                elif eeg_setting_type == "eeg_filter":
                    setting_to_be_deleted = get_object_or_404(
                        EEGFilterSetting, pk=eeg_setting_id
                    )
                elif eeg_setting_type == "eeg_electrode_net_system":
                    setting_to_be_deleted = get_object_or_404(
                        EEGElectrodeLayoutSetting, pk=eeg_setting_id
                    )

                # eeg_setting.eeg_machine_setting.delete()
                if setting_to_be_deleted:
                    setting_to_be_deleted.delete()

                messages.success(request, _("Setting was removed successfully."))

                redirect_url = reverse("eeg_setting_view", args=(eeg_setting.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": can_change,
        "eeg_setting_form": eeg_setting_form,
        "experiment": eeg_setting.experiment,
        "eeg_setting": eeg_setting,
        "editing": False,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def eeg_setting_update(
    request, eeg_setting_id, template_name="experiment/eeg_setting_register.html"
):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    check_can_change(request.user, eeg_setting.experiment.research_project)

    eeg_setting_form = EEGSettingForm(request.POST or None, instance=eeg_setting)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if eeg_setting_form.is_valid():
                if eeg_setting_form.has_changed():
                    eeg_setting_form.save()
                    messages.success(request, _("EEG setting updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "eeg_setting_form": eeg_setting_form,
        "editing": True,
        "experiment": eeg_setting.experiment,
        "eeg_setting": eeg_setting,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def view_eeg_setting_type(request, eeg_setting_id, eeg_setting_type):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    can_change = get_can_change(request.user, eeg_setting.experiment.research_project)

    template_name = "experiment/eeg_setting_" + eeg_setting_type + ".html"

    list_of_manufacturers = None
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
        check_can_change(request.user, eeg_setting.experiment.research_project)

        if request.POST["action"] == "save":
            if (
                eeg_setting_type == "amplifier"
                and "equipment_selection" in request.POST
                and "gain" in request.POST
                and "number_of_channels_used" in request.POST
            ):
                setting_form = EEGAmplifierSettingForm(request.POST or None)

                if setting_form.is_valid():
                    eeg_amplifier = Amplifier.objects.get(
                        pk=request.POST["equipment_selection"]
                    )

                    eeg_amplifier_setting = setting_form.save(commit=False)
                    eeg_amplifier_setting.eeg_amplifier = eeg_amplifier
                    eeg_amplifier_setting.eeg_setting = eeg_setting
                    eeg_amplifier_setting.save()

                    messages.success(
                        request, _("EEG amplifier setting created sucessfully.")
                    )

                    redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

            if (
                eeg_setting_type == "eeg_solution"
                and "solution_selection" in request.POST
            ):
                eeg_solution = EEGSolution.objects.get(
                    pk=request.POST["solution_selection"]
                )

                eeg_solution_setting = EEGSolutionSetting()
                eeg_solution_setting.eeg_solution = eeg_solution
                eeg_solution_setting.eeg_setting = eeg_setting
                eeg_solution_setting.save()

                messages.success(
                    request, _("EEG solution setting created sucessfully.")
                )

                redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                return HttpResponseRedirect(redirect_url)

            if "filter_selection" in request.POST:
                setting_form = EEGFilterSettingForm(request.POST or None)

                if setting_form.is_valid():
                    eeg_filter = FilterType.objects.get(
                        pk=request.POST["filter_selection"]
                    )

                    eeg_filter_setting = setting_form.save(commit=False)
                    eeg_filter_setting.eeg_filter_type = eeg_filter
                    eeg_filter_setting.eeg_setting = eeg_setting
                    eeg_filter_setting.save()

                    messages.success(
                        request, _("EEG filter setting created sucessfully.")
                    )

                    redirect_url = reverse("eeg_setting_view", args=(eeg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

            if (
                eeg_setting_type == "eeg_electrode_net_system"
                and "equipment_selection" in request.POST
                and "localization_system_selection" in request.POST
            ):
                eeg_electrode_net = EEGElectrodeNet.objects.get(
                    pk=request.POST["equipment_selection"]
                )

                eeg_electrode_localization_system = (
                    EEGElectrodeLocalizationSystem.objects.get(
                        pk=request.POST["localization_system_selection"]
                    )
                )

                eeg_electrode_net_system = EEGElectrodeNetSystem.objects.get(
                    eeg_electrode_net=eeg_electrode_net,
                    eeg_electrode_localization_system=eeg_electrode_localization_system,
                )

                eeg_electrode_layout_setting = EEGElectrodeLayoutSetting()
                eeg_electrode_layout_setting.eeg_setting = eeg_setting
                eeg_electrode_layout_setting.eeg_electrode_net_system = (
                    eeg_electrode_net_system
                )
                eeg_electrode_layout_setting.save()

                if eeg_electrode_localization_system.electrode_positions:
                    for (
                        position
                    ) in eeg_electrode_localization_system.electrode_positions.all():
                        new_position_setting = EEGElectrodePositionSetting()
                        new_position_setting.eeg_electrode_layout_setting = (
                            eeg_electrode_layout_setting
                        )
                        new_position_setting.eeg_electrode_position = position
                        new_position_setting.used = True
                        new_position_setting.electrode_model = (
                            eeg_electrode_net.electrode_model_default
                        )
                        new_position_setting.channel_index = (
                            position.channel_default_index
                        )
                        new_position_setting.save()

                messages.info(request, _("Now you can set each electrode position."))

                messages.success(
                    request, _("EEG electrode net system setting created sucessfully.")
                )

                redirect_url = reverse(
                    "eeg_electrode_position_setting", args=(eeg_setting_id,)
                )
                return HttpResponseRedirect(redirect_url)

    if eeg_setting_type == "amplifier":
        if hasattr(eeg_setting, "eeg_amplifier_setting"):
            eeg_amplifier_setting = EEGAmplifierSetting.objects.get(
                eeg_setting_id=eeg_setting_id
            )

            selection_form = EEGAmplifierForm(
                request.POST or None, instance=eeg_amplifier_setting.eeg_amplifier
            )
            setting_form = EEGAmplifierSettingForm(
                request.POST or None, instance=eeg_amplifier_setting
            )
            equipment_selected = eeg_amplifier_setting.eeg_amplifier

            for field in setting_form.fields:
                setting_form.fields[field].widget.attrs["disabled"] = True

        else:
            check_can_change(request.user, eeg_setting.experiment.research_project)
            creating = True

            selection_form = EEGAmplifierForm(request.POST or None)
            setting_form = EEGAmplifierSettingForm(request.POST or None)

    if eeg_setting_type == "eeg_solution":
        if hasattr(eeg_setting, "eeg_solution_setting"):
            eeg_solution_setting = EEGSolutionSetting.objects.get(
                eeg_setting_id=eeg_setting_id
            )

            selection_form = EEGSolutionForm(
                request.POST or None, instance=eeg_solution_setting.eeg_solution
            )
            solution_selected = eeg_solution_setting.eeg_solution

        else:
            check_can_change(request.user, eeg_setting.experiment.research_project)
            creating = True

            selection_form = EEGSolutionForm(request.POST or None)

    if eeg_setting_type == "filter":
        if hasattr(eeg_setting, "eeg_filter_setting"):
            eeg_filter_setting = EEGFilterSetting.objects.get(
                eeg_setting_id=eeg_setting_id
            )

            selection_form = EEGFilterForm(
                request.POST or None, instance=eeg_filter_setting.eeg_filter_type
            )
            setting_form = EEGFilterSettingForm(
                request.POST or None, instance=eeg_filter_setting
            )
            filter_selected = eeg_filter_setting.eeg_filter_type

            for field in setting_form.fields:
                setting_form.fields[field].widget.attrs["disabled"] = True

        else:
            check_can_change(request.user, eeg_setting.experiment.research_project)
            creating = True

            selection_form = EEGFilterForm(request.POST or None)
            setting_form = EEGFilterSettingForm(request.POST or None)

    if eeg_setting_type == "eeg_electrode_net_system":
        localization_system_list = EEGElectrodeLocalizationSystem.objects.filter(
            set_of_electrode_net_system__isnull=False
        )

        if hasattr(eeg_setting, "eeg_electrode_layout_setting"):
            setting = eeg_setting.eeg_electrode_layout_setting

            equipment_selected = setting.eeg_electrode_net_system.eeg_electrode_net
            localization_system_selected = (
                setting.eeg_electrode_net_system.eeg_electrode_localization_system
            )

        else:
            check_can_change(request.user, eeg_setting.experiment.research_project)
            creating = True

    # Settings related to equipment
    if eeg_setting_type in ["amplifier", "eeg_electrode_net_system"]:
        equipment_type = (
            "eeg_electrode_net"
            if eeg_setting_type == "eeg_electrode_net_system"
            else eeg_setting_type
        )

        equipment_list = Equipment.objects.filter(
            equipment_type=equipment_type, tags__name="EEG"
        )
        list_of_manufacturers = Manufacturer.objects.filter(
            set_of_equipment__equipment_type=equipment_type
        ).distinct()

        if eeg_setting_type == "amplifier":
            list_of_manufacturers = Manufacturer.objects.filter(
                set_of_equipment__equipment_type=equipment_type,
                set_of_equipment__tags__name="EEG",
            ).distinct()

        if creating:
            equipment_form = EquipmentForm(request.POST or None)
        else:
            equipment_form = EquipmentForm(
                request.POST or None, instance=equipment_selected
            )

    if eeg_setting_type == "eeg_solution":
        solution_list = EEGSolution.objects.all()
        list_of_manufacturers = Manufacturer.objects.filter(
            set_of_solution__isnull=False
        ).distinct()

        if creating:
            equipment_form = EEGSolutionForm(request.POST or None)
        else:
            equipment_form = EEGSolutionForm(
                request.POST or None, instance=solution_selected
            )

    if eeg_setting_type == "filter":
        filter_list = FilterType.objects.filter(tags__name="EEG")

        if creating:
            equipment_form = EEGFilterForm(request.POST or None)
        else:
            equipment_form = EEGFilterForm(
                request.POST or None, instance=filter_selected
            )

    context = {
        "creating": creating,
        "editing": False,
        "tab": "0",
        "can_change": can_change,
        "eeg_setting_type": eeg_setting_type,
        "eeg_setting": eeg_setting,
        "equipment_selected": equipment_selected,
        "solution_selected": solution_selected,
        "filter_selected": filter_selected,
        "manufacturer_list": list_of_manufacturers,
        "equipment_list": equipment_list,
        "solution_list": solution_list,
        "filter_list": filter_list,
        "equipment_form": equipment_form,
        "selection_form": selection_form,
        "setting_form": setting_form,
        "localization_system_list": localization_system_list,
        "localization_system_selected": localization_system_selected,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def edit_eeg_setting_type(request, eeg_setting_id, eeg_setting_type):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    check_can_change(request.user, eeg_setting.experiment.research_project)

    template_name = "experiment/eeg_setting_" + eeg_setting_type + ".html"

    list_of_manufacturers = None
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
        if request.POST["action"] == "save":
            if (
                "equipment_selection" in request.POST
                and "number_of_channels_used" in request.POST
            ):
                setting_form = EEGAmplifierSettingForm(
                    request.POST or None, instance=eeg_setting.eeg_amplifier_setting
                )

                if setting_form.is_valid():
                    eeg_amplifier = Amplifier.objects.get(
                        pk=request.POST["equipment_selection"]
                    )

                    eeg_amplifier_setting = setting_form.save(commit=False)
                    eeg_amplifier_setting.eeg_amplifier = eeg_amplifier
                    eeg_amplifier_setting.save()

                messages.success(
                    request, _("EEG Amplifier setting updated successfully.")
                )

                redirect_url = reverse(
                    "view_eeg_setting_type", args=(eeg_setting_id, eeg_setting_type)
                )
                return HttpResponseRedirect(redirect_url)

            if "equipment_selection" in request.POST and "gain" in request.POST:
                setting_form = EEGAmplifierSettingForm(
                    request.POST or None, instance=eeg_setting.eeg_amplifier_setting
                )

                if setting_form.is_valid():
                    eeg_amplifier = Amplifier.objects.get(
                        pk=request.POST["equipment_selection"]
                    )

                    eeg_amplifier_setting = setting_form.save(commit=False)
                    eeg_amplifier_setting.eeg_amplifier = eeg_amplifier
                    eeg_amplifier_setting.save()

                    messages.success(
                        request, _("EEG amplifier setting updated sucessfully.")
                    )

                    redirect_url = reverse(
                        "view_eeg_setting_type", args=(eeg_setting_id, eeg_setting_type)
                    )
                    return HttpResponseRedirect(redirect_url)

            if "solution_selection" in request.POST:
                eeg_solution = EEGSolution.objects.get(
                    pk=request.POST["solution_selection"]
                )

                eeg_solution_setting = eeg_setting.eeg_solution_setting

                eeg_solution_setting.eeg_solution = eeg_solution
                eeg_solution_setting.eeg_setting = eeg_setting
                eeg_solution_setting.save()

                messages.success(
                    request, _("EEG solution setting updated sucessfully.")
                )

                redirect_url = reverse(
                    "view_eeg_setting_type", args=(eeg_setting_id, eeg_setting_type)
                )
                return HttpResponseRedirect(redirect_url)

            if "filter_selection" in request.POST:
                setting_form = EEGFilterSettingForm(
                    request.POST or None, instance=eeg_setting.eeg_filter_setting
                )

                if setting_form.is_valid():
                    eeg_filter = FilterType.objects.get(
                        pk=request.POST["filter_selection"]
                    )

                    eeg_filter_setting = setting_form.save(commit=False)

                    # eeg_filter_setting = eeg_setting.eeg_filter_setting

                    eeg_filter_setting.eeg_filter_type = eeg_filter
                    # eeg_filter_setting.high_pass = request.POST['high_pass']
                    # eeg_filter_setting.low_pass = request.POST['low_pass']
                    # eeg_filter_setting.order = request.POST['order']
                    # eeg_filter_setting.eeg_setting = eeg_setting
                    eeg_filter_setting.save()

                    messages.success(
                        request, _("EEG filter setting updated sucessfully.")
                    )

                    redirect_url = reverse(
                        "view_eeg_setting_type", args=(eeg_setting_id, eeg_setting_type)
                    )
                    return HttpResponseRedirect(redirect_url)

            if (
                eeg_setting_type == "eeg_electrode_net_system"
                and "equipment_selection" in request.POST
                and "localization_system_selection" in request.POST
            ):
                eeg_electrode_net = EEGElectrodeNet.objects.get(
                    pk=request.POST["equipment_selection"]
                )

                eeg_electrode_localization_system = (
                    EEGElectrodeLocalizationSystem.objects.get(
                        pk=request.POST["localization_system_selection"]
                    )
                )

                eeg_electrode_net_system = EEGElectrodeNetSystem.objects.get(
                    eeg_electrode_net=eeg_electrode_net,
                    eeg_electrode_localization_system=eeg_electrode_localization_system,
                )

                # get the current layout setting
                eeg_electrode_layout_setting = eeg_setting.eeg_electrode_layout_setting

                # if the electrode localization system changed
                if (
                    eeg_electrode_layout_setting.eeg_electrode_net_system.eeg_electrode_localization_system
                    != eeg_electrode_localization_system
                ):
                    # remove all current position settings
                    for (
                        position
                    ) in eeg_electrode_layout_setting.positions_setting.all():
                        position.delete()

                eeg_electrode_layout_setting.eeg_electrode_net_system = (
                    eeg_electrode_net_system
                )
                eeg_electrode_layout_setting.save()

                if eeg_electrode_localization_system.electrode_positions:
                    for (
                        position
                    ) in eeg_electrode_localization_system.electrode_positions.all():
                        # if not exists a position setting
                        position_setting = EEGElectrodePositionSetting.objects.filter(
                            eeg_electrode_layout_setting=eeg_electrode_layout_setting,
                            eeg_electrode_position=position,
                        )

                        if not position_setting:
                            new_position_setting = EEGElectrodePositionSetting()
                            new_position_setting.eeg_electrode_layout_setting = (
                                eeg_electrode_layout_setting
                            )
                            new_position_setting.eeg_electrode_position = position
                            new_position_setting.used = True
                            new_position_setting.electrode_model = (
                                eeg_electrode_net.electrode_model_default
                            )
                            new_position_setting.channel_index = (
                                position.channel_default_index
                            )
                            new_position_setting.save()

                messages.success(
                    request, _("EEG electrode net system setting updated sucessfully.")
                )

                redirect_url = reverse(
                    "view_eeg_setting_type", args=(eeg_setting_id, eeg_setting_type)
                )
                return HttpResponseRedirect(redirect_url)

    if eeg_setting_type == "amplifier":
        eeg_amplifier_setting = eeg_setting.eeg_amplifier_setting

        selection_form = EEGAmplifierForm(
            request.POST or None, instance=eeg_amplifier_setting.eeg_amplifier
        )
        setting_form = EEGAmplifierSettingForm(
            request.POST or None, instance=eeg_amplifier_setting
        )
        equipment_selected = eeg_amplifier_setting.eeg_amplifier

    if eeg_setting_type == "eeg_solution":
        eeg_solution_setting = eeg_setting.eeg_solution_setting

        solution_selected = eeg_solution_setting.eeg_solution

    if eeg_setting_type == "filter":
        eeg_filter_setting = eeg_setting.eeg_filter_setting

        filter_selected = eeg_filter_setting.eeg_filter_type

        selection_form = EEGFilterForm(
            request.POST or None, instance=eeg_filter_setting.eeg_filter_type
        )
        setting_form = EEGFilterSettingForm(
            request.POST or None, instance=eeg_filter_setting
        )

    if eeg_setting_type == "eeg_solution":
        solution_list = EEGSolution.objects.all()
        list_of_manufacturers = Manufacturer.objects.filter(
            set_of_solution__isnull=False
        ).distinct()

        equipment_form = EEGSolutionForm(
            request.POST or None, instance=solution_selected
        )

    if eeg_setting_type == "filter":
        filter_list = FilterType.objects.filter(tags__name="EEG")

        equipment_form = EEGFilterForm(request.POST or None, instance=filter_selected)

    if eeg_setting_type == "eeg_electrode_net_system":
        setting = eeg_setting.eeg_electrode_layout_setting

        equipment_selected = setting.eeg_electrode_net_system.eeg_electrode_net
        localization_system_selected = (
            setting.eeg_electrode_net_system.eeg_electrode_localization_system
        )

        localization_system_list = EEGElectrodeLocalizationSystem.objects.filter(
            set_of_electrode_net_system__eeg_electrode_net_id=equipment_selected.id
        )

    # Settings related to equipment
    if eeg_setting_type in ["amplifier", "eeg_electrode_net_system"]:
        equipment_type = (
            "eeg_electrode_net"
            if eeg_setting_type == "eeg_electrode_net_system"
            else eeg_setting_type
        )
        equipment_list = Equipment.objects.filter(
            equipment_type=equipment_type, tags__name="EEG"
        )
        list_of_manufacturers = Manufacturer.objects.filter(
            set_of_equipment__equipment_type=equipment_type
        ).distinct()

        if eeg_setting_type == "amplifier":
            list_of_manufacturers = Manufacturer.objects.filter(
                set_of_equipment__equipment_type=equipment_type,
                set_of_equipment__tags__name="EEG",
            ).distinct()

        equipment_form = EquipmentForm(
            request.POST or None, instance=equipment_selected
        )

    context = {
        "creating": False,
        "editing": True,
        "tab": "0",
        "can_change": True,
        "eeg_setting_type": eeg_setting_type,
        "eeg_setting": eeg_setting,
        "equipment_selected": equipment_selected,
        "solution_selected": solution_selected,
        "filter_selected": filter_selected,
        "solution_list": solution_list,
        "manufacturer_list": list_of_manufacturers,
        "equipment_list": equipment_list,
        "filter_list": filter_list,
        "equipment_form": equipment_form,
        "selection_form": selection_form,
        "setting_form": setting_form,
        "localization_system_list": localization_system_list,
        "localization_system_selected": localization_system_selected,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def get_json_positions(request, eeg_electrode_localization_system_id):
    new_positions = json.loads(request.GET.get("positions"))

    count_new = 0
    count_delete = 0
    for position in new_positions:
        if position["existInDB"]:
            if position["delete"]:
                get_object_or_404(EEGElectrodePosition, pk=position["id"]).delete()
                count_delete += 1
            if position["update"]:
                update_electrode_position = get_object_or_404(
                    EEGElectrodePosition, pk=position["id"]
                )
                update_electrode_position.name = position["position"]
                update_electrode_position.coordinate_x = position["x"]
                update_electrode_position.coordinate_y = position["y"]
                update_electrode_position.save()
        else:
            new_electrode_position = EEGElectrodePosition.objects.create(
                eeg_electrode_localization_system_id=eeg_electrode_localization_system_id,
                name=position["position"],
                coordinate_x=float(position["x"]),
                coordinate_y=float(position["y"]),
            )
            count_new += 1
            new_electrode_position.save()

    redirect_url = reverse(
        "eeg_electrode_localization_system_view",
        args=(eeg_electrode_localization_system_id,),
    )
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.change_experiment")
def get_json_equipment_by_manufacturer(request, equipment_type, manufacturer_id):
    if equipment_type == "eeg_solution":
        equipment = EEGSolution.objects.all()
    else:
        equipment = Equipment.objects.filter(equipment_type=equipment_type)
    if manufacturer_id != "0":
        equipment = equipment.filter(manufacturer_id=manufacturer_id)
    json_equipment = serializers.serialize("json", equipment)
    return HttpResponse(json_equipment, content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def get_json_equipment_attributes(request, equipment_id):
    equipment = get_object_or_404(Equipment, pk=equipment_id)

    response_data = {
        "description": equipment.description,
    }

    if equipment.equipment_type == "amplifier":
        equipment = get_object_or_404(Amplifier, pk=equipment_id)
        response_data["gain"] = equipment.gain
        response_data["number_of_channels"] = equipment.number_of_channels

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def get_json_solution_attributes(request, solution_id):
    solution = get_object_or_404(EEGSolution, pk=solution_id)

    response_data = {
        "description": solution.components,
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def get_json_filter_attributes(request, filter_id):
    filter_type = get_object_or_404(FilterType, pk=filter_id)

    response_data = {
        "description": filter_type.description,
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def get_localization_system_by_electrode_net(request, equipment_id):
    list_of_localization_system = EEGElectrodeLocalizationSystem.objects.filter(
        set_of_electrode_net_system__eeg_electrode_net_id=equipment_id
    )
    json_equipment = serializers.serialize("json", list_of_localization_system)
    return HttpResponse(json_equipment, content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def get_equipment_by_manufacturer_and_localization_system(
    request, manufacturer_id, eeg_localization_system_id
):
    set_of_net_system = EEGElectrodeNetSystem.objects.filter(
        eeg_electrode_localization_system_id=eeg_localization_system_id
    )
    list_of_electrode_net = [item.eeg_electrode_net_id for item in set_of_net_system]
    # equipment = Equipment.objects.in_bulk(list_of_electrode_net)
    equipment = Equipment.objects.filter(id__in=list_of_electrode_net)
    if manufacturer_id != "0":
        equipment = equipment.filter(manufacturer_id=manufacturer_id)
    json_equipment = serializers.serialize("json", equipment)
    return HttpResponse(json_equipment, content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def eeg_electrode_position_setting(
    request,
    eeg_setting_id,
    template_name="experiment/eeg_setting_electrode_position_status.html",
):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    can_change = get_can_change(request.user, eeg_setting.experiment.research_project)

    positions = []
    for (
        position_setting
    ) in eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
        positions.append(
            {
                "id": "position_status_" + str(position_setting.id),
                "position": position_setting.eeg_electrode_position.name,
                "x": position_setting.eeg_electrode_position.coordinate_x,
                "y": position_setting.eeg_electrode_position.coordinate_y,
            }
        )

    context = {
        "tab": "1",
        "editing": False,
        "can_change": can_change,
        "eeg_setting": eeg_setting,
        "json_list": json.dumps(positions),
        "number_of_used_electrodes": number_of_used_positions(eeg_setting),
    }

    return render(request, template_name, context)


def number_of_used_positions(eeg_setting):
    return EEGElectrodePositionSetting.objects.filter(
        eeg_electrode_layout_setting=eeg_setting.eeg_electrode_layout_setting, used=True
    ).count()


@login_required
@permission_required("experiment.change_experiment")
def eeg_electrode_cap_setting(
    request,
    eeg_setting_id,
    template_name="experiment/eeg_electrode_cap_coordinates_register.html",
):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)
    check_can_change(request.user, eeg_setting.experiment.research_project)
    context = {"eeg_setting": eeg_setting}
    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def edit_eeg_electrode_position_setting(
    request,
    eeg_setting_id,
    template_name="experiment/eeg_setting_electrode_position_status.html",
):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    check_can_change(request.user, eeg_setting.experiment.research_project)

    positions = []
    for (
        position_setting
    ) in eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
        positions.append(
            {
                "id": "position_status_" + str(position_setting.id),
                "position": position_setting.eeg_electrode_position.name,
                "x": position_setting.eeg_electrode_position.coordinate_x,
                "y": position_setting.eeg_electrode_position.coordinate_y,
            }
        )

    if request.method == "POST":
        if request.POST["action"] == "save":
            for (
                position_setting
            ) in eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
                position_setting.used = (
                    "position_status_" + str(position_setting.id) in request.POST
                )
                position_setting.save()

            messages.success(request, _("Setting saved successfully."))

            redirect_url = reverse(
                "eeg_electrode_position_setting", args=(eeg_setting_id,)
            )
            return HttpResponseRedirect(redirect_url)

    context = {
        "tab": "1",
        "editing": True,
        "eeg_setting": eeg_setting,
        "json_list": json.dumps(positions),
        "number_of_used_electrodes": number_of_used_positions(eeg_setting),
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def eeg_electrode_position_setting_model(
    request,
    eeg_setting_id,
    template_name="experiment/eeg_setting_electrode_position_status_model.html",
):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    can_change = get_can_change(request.user, eeg_setting.experiment.research_project)

    eeg_electrode_model_list = ElectrodeModel.objects.filter(tags__name="EEG")

    context = {
        "tab": "2",
        "editing": False,
        "can_change": can_change,
        "eeg_setting": eeg_setting,
        "eeg_electrode_model_list": eeg_electrode_model_list,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def edit_eeg_electrode_position_setting_model(
    request,
    eeg_setting_id,
    template_name="experiment/eeg_setting_electrode_position_status_model.html",
):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    check_can_change(request.user, eeg_setting.experiment.research_project)

    eeg_electrode_model_list = ElectrodeModel.objects.filter(tags__name="EEG")

    if request.method == "POST":
        if request.POST["action"] == "save":
            for (
                position_setting
            ) in eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
                electrode_model_id = int(
                    request.POST["electrode_model_" + str(position_setting.id)]
                )
                position_setting.electrode_model_id = electrode_model_id
                position_setting.save()

            messages.success(request, _("Setting saved successfully."))

            redirect_url = reverse(
                "eeg_electrode_position_setting_model", args=(eeg_setting_id,)
            )
            return HttpResponseRedirect(redirect_url)

    context = {
        "tab": "2",
        "editing": True,
        "eeg_setting": eeg_setting,
        "eeg_electrode_model_list": eeg_electrode_model_list,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def eeg_electrode_position_setting_change_the_order(
    request, eeg_electrode_position_setting_id, command
):
    position_setting = get_object_or_404(
        EEGElectrodePositionSetting, pk=eeg_electrode_position_setting_id
    )

    all_position_settings = EEGElectrodePositionSetting.objects.filter(
        eeg_electrode_layout_setting=position_setting.eeg_electrode_layout_setting
    )

    if command == "down":
        position_setting_to_change = (
            all_position_settings.filter(
                channel_index__gt=position_setting.channel_index
            )
            .order_by("channel_index")
            .first()
        )
    else:
        position_setting_to_change = (
            all_position_settings.filter(
                channel_index__lt=position_setting.channel_index
            )
            .order_by("-channel_index")
            .first()
        )

    bottom_position_setting = all_position_settings.order_by("-channel_index").first()

    channel_index_current = position_setting.channel_index
    channel_index_to_change = position_setting_to_change.channel_index

    position_setting_to_change.channel_index = bottom_position_setting.channel_index + 1
    position_setting_to_change.save()

    position_setting.channel_index = channel_index_to_change
    position_setting.save()

    position_setting_to_change.channel_index = channel_index_current
    position_setting_to_change.save()

    redirect_url = reverse(
        "eeg_electrode_position_setting_model",
        args=(position_setting.eeg_electrode_layout_setting.eeg_setting_id,),
    )

    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.register_equipment")
def manufacturer_list(request, template_name="experiment/manufacturer_list.html"):
    return render(
        request, template_name, {"equipments": Manufacturer.objects.order_by("name")}
    )


@login_required
@permission_required("experiment.register_equipment")
def manufacturer_create(request, template_name="experiment/manufacturer_register.html"):
    manufacturer_form = ManufacturerRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if manufacturer_form.is_valid():
                manufacturer_added = manufacturer_form.save()

                messages.success(request, _("Manufacturer created successfully."))
                redirect_url = reverse(
                    "manufacturer_view", args=(manufacturer_added.id,)
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {"equipment_form": manufacturer_form, "creating": True, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def manufacturer_update(
    request, manufacturer_id, template_name="experiment/manufacturer_register.html"
):
    manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)

    manufacturer_form = ManufacturerRegisterForm(
        request.POST or None, instance=manufacturer
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if manufacturer_form.is_valid():
                if manufacturer_form.has_changed():
                    manufacturer_form.save()
                    messages.success(request, _("Manufacturer updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("manufacturer_view", args=(manufacturer.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "equipment": manufacturer,
        "equipment_form": manufacturer_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def manufacturer_view(
    request, manufacturer_id, template_name="experiment/manufacturer_register.html"
):
    manufacturer = get_object_or_404(Manufacturer, pk=manufacturer_id)

    manufacturer_form = ManufacturerRegisterForm(
        request.POST or None, instance=manufacturer
    )

    for field in manufacturer_form.fields:
        manufacturer_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                manufacturer.delete()
                messages.success(request, _("Manufacturer removed successfully."))
                return redirect("manufacturer_list")
            except ProtectedError:
                messages.error(request, _("Error trying to delete manufacturer."))
                redirect_url = reverse("manufacturer_view", args=(manufacturer_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "equipment": manufacturer,
        "equipment_form": manufacturer_form,
    }

    return render(request, template_name, context)


def get_tag(data_post):
    tag = []
    for item in data_post:
        if "tag" in item:
            tag.append(item)
    return tag


def get_tag_ids_from_post(data_post):
    tag_ids = []
    for item in data_post:
        if "tag" in item:
            tag_ids.append(int(item.split("_")[-1]))
    return tag_ids


def equipment_tags_update(equipment_id, set_tags, model_name_str):
    model_name = apps.get_model("experiment", model_name_str)
    changed = False

    if model_name.objects.filter(id=equipment_id).exists():
        current_tags_objects = model_name.objects.get(id=equipment_id).tags

        current_tags = [
            item[0] for item in current_tags_objects.all().values_list("id")
        ]

        tags = Tag.objects.all()

        for tag in tags:
            if tag.id not in current_tags and tag.id in set_tags:
                # nao estava e agora está: incluir
                current_tags_objects.add(tag)
                changed = True
            elif tag.id in current_tags and (tag.id not in set_tags):
                # estava e nao está mais: deletar
                current_tags_objects.remove(tag)
                changed = True
            # caso contrario: manter
    return changed


def get_tags(equipment_id, model_name_str):
    tags = None

    model_name = apps.get_model("experiment", model_name_str)

    if model_name.objects.filter(id=equipment_id).exists():
        current_tags_objects = model_name.objects.get(id=equipment_id).tags.all()

        current_tags = [item[0] for item in current_tags_objects.values_list("id")]

        tags = Tag.objects.all()

        for tag in tags:
            tag.checked = True if tag.id in current_tags else False

    return tags


def set_all_tags():
    tags = Tag.objects.all()

    for tag in tags:
        tag.checked = True

    return tags


@login_required
@permission_required("experiment.register_equipment")
def amplifier_list(request, template_name="experiment/amplifier_list.html"):
    return render(
        request,
        template_name,
        {"equipments": Amplifier.objects.all().order_by("identification")},
    )


@login_required
@permission_required("experiment.register_equipment")
def amplifier_create(request, template_name="experiment/amplifier_register.html"):
    amplifier_form = AmplifierRegisterForm(
        request.POST or None, initial={"equipment_type": "amplifier"}
    )

    tags = set_all_tags()

    if request.method == "POST":
        if request.POST["action"] == "save":
            if amplifier_form.is_valid():
                amplifier_added = amplifier_form.save(commit=False)
                amplifier_added.equipment_type = "amplifier"
                amplifier_added.save()

                on_tags = get_tag_ids_from_post(request.POST)

                equipment_tags_update(amplifier_added.id, on_tags, "Amplifier")

                tags = get_tags(amplifier_added.id, "Amplifier")

                messages.success(request, _("Amplifier created successfully."))
                redirect_url = reverse("amplifier_view", args=(amplifier_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "equipment_form": amplifier_form,
        "creating": True,
        "editing": True,
        "tags": tags,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def amplifier_update(
    request, amplifier_id, template_name="experiment/amplifier_register.html"
):
    amplifier = get_object_or_404(Amplifier, pk=amplifier_id)

    amplifier_form = AmplifierRegisterForm(request.POST or None, instance=amplifier)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if amplifier_form.is_valid():
                new_tags = get_tag_ids_from_post(request.POST)
                changed_tags = equipment_tags_update(
                    amplifier_id, new_tags, "Amplifier"
                )

                if amplifier_form.has_changed() or changed_tags:
                    amplifier_form.save()
                    messages.success(request, _("Amplifier updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("amplifier_view", args=(amplifier.id,))
                return HttpResponseRedirect(redirect_url)

    tags = get_tags(amplifier_id, "Amplifier")

    context = {
        "equipment": amplifier,
        "equipment_form": amplifier_form,
        "editing": True,
        "tags": tags,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def amplifier_view(
    request, amplifier_id, template_name="experiment/amplifier_register.html"
):
    amplifier = get_object_or_404(Amplifier, pk=amplifier_id)

    amplifier_form = AmplifierRegisterForm(request.POST or None, instance=amplifier)

    for field in amplifier_form.fields:
        amplifier_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                amplifier.delete()
                messages.success(request, _("Amplifier removed successfully."))
                return redirect("amplifier_list")
            except ProtectedError:
                messages.error(request, _("Error trying to delete amplifier."))
                redirect_url = reverse("amplifier_view", args=(amplifier_id,))
                return HttpResponseRedirect(redirect_url)

    tags = get_tags(amplifier_id, "Amplifier")

    context = {
        "can_change": True,
        "equipment": amplifier,
        "equipment_form": amplifier_form,
        "tags": tags,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eegsolution_list(request, template_name="experiment/eegsolution_list.html"):
    return render(
        request,
        template_name,
        {"equipments": EEGSolution.objects.all().order_by("name")},
    )


@login_required
@permission_required("experiment.register_equipment")
def eegsolution_create(request, template_name="experiment/eegsolution_register.html"):
    eegsolution_form = EEGSolutionRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if eegsolution_form.is_valid():
                eegsolution_added = eegsolution_form.save(commit=False)
                eegsolution_added.save()

                messages.success(request, _("EEG solution created successfully."))
                redirect_url = reverse("eegsolution_view", args=(eegsolution_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {"equipment_form": eegsolution_form, "creating": True, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eegsolution_update(
    request, eegsolution_id, template_name="experiment/eegsolution_register.html"
):
    eegsolution = get_object_or_404(EEGSolution, pk=eegsolution_id)
    eegsolution.equipment_type = "eeg_solution"

    eegsolution_form = EEGSolutionRegisterForm(
        request.POST or None, instance=eegsolution
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if eegsolution_form.is_valid():
                if eegsolution_form.has_changed():
                    eegsolution_form.save()
                    messages.success(request, _("EEG solution updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("eegsolution_view", args=(eegsolution.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "equipment": eegsolution,
        "equipment_form": eegsolution_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eegsolution_view(
    request, eegsolution_id, template_name="experiment/eegsolution_register.html"
):
    eegsolution = get_object_or_404(EEGSolution, pk=eegsolution_id)

    eegsolution_form = EEGSolutionRegisterForm(
        request.POST or None, instance=eegsolution
    )

    for field in eegsolution_form.fields:
        eegsolution_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                eegsolution.delete()
                messages.success(request, _("EEG solution removed successfully."))
                return redirect("eegsolution_list")
            except ProtectedError:
                messages.error(request, _("Error trying to delete eegsolution."))
                redirect_url = reverse("eegsolution_view", args=(eegsolution_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "equipment": eegsolution,
        "equipment_form": eegsolution_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def filtertype_list(request, template_name="experiment/filtertype_list.html"):
    return render(
        request,
        template_name,
        {"equipments": FilterType.objects.all().order_by("name")},
    )


@login_required
@permission_required("experiment.register_equipment")
def filtertype_create(request, template_name="experiment/filtertype_register.html"):
    filtertype_form = FilterTypeRegisterForm(request.POST or None)

    tags = set_all_tags()

    if request.method == "POST":
        if request.POST["action"] == "save":
            if filtertype_form.is_valid():
                filtertype_added = filtertype_form.save(commit=False)
                filtertype_added.save()

                on_tags = get_tag_ids_from_post(request.POST)
                changed_tags = equipment_tags_update(
                    filtertype_added.id, on_tags, "FilterType"
                )

                tags = get_tags(filtertype_added.id, "FilterType")

                messages.success(request, _("Filter type created successfully."))
                redirect_url = reverse("filtertype_view", args=(filtertype_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "equipment_form": filtertype_form,
        "creating": True,
        "editing": True,
        "tags": tags,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def filtertype_update(
    request, filtertype_id, template_name="experiment/filtertype_register.html"
):
    filtertype = get_object_or_404(FilterType, pk=filtertype_id)

    filtertype_form = FilterTypeRegisterForm(request.POST or None, instance=filtertype)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if filtertype_form.is_valid():
                new_tags = get_tag_ids_from_post(request.POST)
                changed_tags = equipment_tags_update(
                    filtertype_id, new_tags, "FilterType"
                )

                if filtertype_form.has_changed() or changed_tags:
                    filtertype_form.save()
                    messages.success(request, _("Filter type updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("filtertype_view", args=(filtertype.id,))
                return HttpResponseRedirect(redirect_url)

    tags = get_tags(filtertype_id, "FilterType")

    context = {
        "equipment": filtertype,
        "equipment_form": filtertype_form,
        "editing": True,
        "tags": tags,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def filtertype_view(
    request, filtertype_id, template_name="experiment/filtertype_register.html"
):
    filtertype = get_object_or_404(FilterType, pk=filtertype_id)

    filtertype_form = FilterTypeRegisterForm(request.POST or None, instance=filtertype)

    for field in filtertype_form.fields:
        filtertype_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                filtertype.delete()
                messages.success(request, _("Filter type removed successfully."))
                return redirect("filtertype_list")
            except ProtectedError:
                messages.error(request, _("Error trying to delete filter type."))
                redirect_url = reverse("filtertype_view", args=(filtertype_id,))
                return HttpResponseRedirect(redirect_url)

    tags = get_tags(filtertype_id, "FilterType")

    context = {
        "can_change": True,
        "equipment": filtertype,
        "equipment_form": filtertype_form,
        "tags": tags,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def standardization_system_list(
    request, template_name="experiment/standardization_system_list.html"
):
    return render(
        request,
        template_name,
        {"equipments": StandardizationSystem.objects.all().order_by("name")},
    )


@login_required
@permission_required("experiment.register_equipment")
def standardization_system_create(
    request, template_name="experiment/standardization_system_register.html"
):
    standardization_system_form = StandardizationSystemRegisterForm(
        request.POST or None
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if standardization_system_form.is_valid():
                standardization_system_added = standardization_system_form.save(
                    commit=False
                )
                standardization_system_added.save()

                messages.success(
                    request, _("Standardization system created successfully.")
                )
                redirect_url = reverse(
                    "standardization_system_view",
                    args=(standardization_system_added.id,),
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "equipment_form": standardization_system_form,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def standardization_system_update(
    request,
    standardization_system_id,
    template_name="experiment/standardization_system_register.html",
):
    standardization_system = get_object_or_404(
        StandardizationSystem, pk=standardization_system_id
    )

    standardization_system_form = StandardizationSystemRegisterForm(
        request.POST or None, instance=standardization_system
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if standardization_system_form.is_valid():
                if standardization_system_form.has_changed():
                    standardization_system_form.save()
                    messages.success(
                        request, _("Standardization system updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "standardization_system_view", args=(standardization_system.id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "equipment": standardization_system,
        "equipment_form": standardization_system_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def emg_electrode_placement_create(request, standardization_system_id, placement_type):
    template_name = "experiment/emg_" + placement_type + "_placement_register.html"

    standardization_system = get_object_or_404(
        StandardizationSystem, pk=standardization_system_id
    )

    emg_electrode_placement_form = None

    if placement_type == "surface":
        emg_electrode_placement_form = EMGSurfacePlacementRegisterForm(
            request.POST or None, request.FILES
        )
    elif placement_type == "intramuscular":
        emg_electrode_placement_form = EMGIntramuscularPlacementRegisterForm(
            request.POST or None, request.FILES
        )
    elif placement_type == "needle":
        emg_electrode_placement_form = EMGNeedlePlacementRegisterForm(
            request.POST or None, request.FILES
        )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if emg_electrode_placement_form.is_valid():
                placement_added = emg_electrode_placement_form.save(commit=False)
                placement_added.standardization_system = standardization_system
                placement_added.placement_type = placement_type
                placement_added.save()

                messages.success(
                    request, _("Electrode placement subdivision created successfully.")
                )
                redirect_url = reverse(
                    "emg_electrode_placement_view", args=(placement_added.id,)
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "emg_electrode_placement_form": emg_electrode_placement_form,
        "standardization_system": standardization_system,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def emg_electrode_placement_view(request, emg_electrode_placement_id):
    emg_electrode_placement = get_object_or_404(
        EMGElectrodePlacement, pk=emg_electrode_placement_id
    )

    template_name = (
        "experiment/emg_"
        + emg_electrode_placement.placement_type
        + "_placement_register.html"
    )

    emg_electrode_placement_form = None

    if emg_electrode_placement.placement_type == "surface":
        emg_electrode_placement = get_object_or_404(
            EMGSurfacePlacement, pk=emg_electrode_placement_id
        )
        emg_electrode_placement_form = EMGSurfacePlacementRegisterForm(
            request.POST or None, instance=emg_electrode_placement
        )
    elif emg_electrode_placement.placement_type == "intramuscular":
        emg_electrode_placement = get_object_or_404(
            EMGIntramuscularPlacement, pk=emg_electrode_placement_id
        )
        emg_electrode_placement_form = EMGIntramuscularPlacementRegisterForm(
            request.POST or None, instance=emg_electrode_placement
        )
    elif emg_electrode_placement.placement_type == "needle":
        emg_electrode_placement = get_object_or_404(
            EMGNeedlePlacement, pk=emg_electrode_placement_id
        )
        emg_electrode_placement_form = EMGNeedlePlacementRegisterForm(
            request.POST or None, instance=emg_electrode_placement
        )

    for field in emg_electrode_placement_form.fields:
        emg_electrode_placement_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                standardization_system = emg_electrode_placement.standardization_system
                # emg_electrode_placement.photo.delete()
                emg_electrode_placement.delete()
                messages.success(
                    request, _("EMG electrode placement removed successfully.")
                )
                redirect_url = reverse(
                    "standardization_system_view", args=(standardization_system.id,)
                )
                return HttpResponseRedirect(redirect_url)
            except ProtectedError:
                messages.error(
                    request, _("Error trying to delete EMG electrode placement.")
                )
                redirect_url = reverse(
                    "emg_electrode_placement_view", args=(emg_electrode_placement_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "emg_electrode_placement_form": emg_electrode_placement_form,
        "emg_electrode_placement": emg_electrode_placement,
        "can_change": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def emg_electrode_placement_update(request, emg_electrode_placement_id):
    emg_electrode_placement = get_object_or_404(
        EMGElectrodePlacement, pk=emg_electrode_placement_id
    )

    template_name = (
        "experiment/emg_"
        + emg_electrode_placement.placement_type
        + "_placement_register.html"
    )

    emg_electrode_placement_form = None

    if emg_electrode_placement.placement_type == "surface":
        emg_electrode_placement = get_object_or_404(
            EMGSurfacePlacement, pk=emg_electrode_placement_id
        )
        emg_electrode_placement_form = EMGSurfacePlacementRegisterForm(
            request.POST or None, instance=emg_electrode_placement
        )
    elif emg_electrode_placement.placement_type == "intramuscular":
        emg_electrode_placement = get_object_or_404(
            EMGIntramuscularPlacement, pk=emg_electrode_placement_id
        )
        emg_electrode_placement_form = EMGIntramuscularPlacementRegisterForm(
            request.POST or None, instance=emg_electrode_placement
        )
    elif emg_electrode_placement.placement_type == "needle":
        emg_electrode_placement = get_object_or_404(
            EMGNeedlePlacement, pk=emg_electrode_placement_id
        )
        emg_electrode_placement_form = EMGNeedlePlacementRegisterForm(
            request.POST or None, instance=emg_electrode_placement
        )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if emg_electrode_placement.placement_type == "surface":
                emg_electrode_placement_form = EMGSurfacePlacementRegisterForm(
                    request.POST or None,
                    request.FILES,
                    instance=emg_electrode_placement,
                )
            elif emg_electrode_placement.placement_type == "intramuscular":
                emg_electrode_placement_form = EMGIntramuscularPlacementRegisterForm(
                    request.POST or None,
                    request.FILES,
                    instance=emg_electrode_placement,
                )
            elif emg_electrode_placement.placement_type == "needle":
                emg_electrode_placement_form = EMGNeedlePlacementRegisterForm(
                    request.POST or None,
                    request.FILES,
                    instance=emg_electrode_placement,
                )

            if emg_electrode_placement_form.is_valid():
                if emg_electrode_placement_form.has_changed():
                    emg_electrode_placement_form.save()
                    messages.success(
                        request, _("EMG electrode placement was updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "emg_electrode_placement_view", args=(emg_electrode_placement_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "emg_electrode_placement_form": emg_electrode_placement_form,
        "emg_electrode_placement": emg_electrode_placement,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def standardization_system_view(
    request,
    standardization_system_id,
    template_name="experiment/standardization_system_register.html",
):
    standardization_system = get_object_or_404(
        StandardizationSystem, pk=standardization_system_id
    )

    standardization_system_form = StandardizationSystemRegisterForm(
        request.POST or None, instance=standardization_system
    )

    for field in standardization_system_form.fields:
        standardization_system_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                standardization_system.delete()
                messages.success(
                    request, _("Standardization system removed successfully.")
                )
                return redirect("standardization_system_list")
            except ProtectedError:
                messages.error(
                    request, _("Error trying to delete standardization system.")
                )
                redirect_url = reverse(
                    "standardization_system_view", args=(standardization_system_id,)
                )
                return HttpResponseRedirect(redirect_url)

    electrode_placement_choices = []
    for type_element, type_name in EMGElectrodePlacement.PLACEMENT_TYPES:
        electrode_placement_choices.append((type_element, type_name))

    context = {
        "can_change": True,
        "equipment": standardization_system,
        "equipment_form": standardization_system_form,
        "electrode_placement_choices": electrode_placement_choices,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def muscle_list(request, template_name="experiment/muscle_list.html"):
    return render(
        request, template_name, {"equipments": Muscle.objects.all().order_by("name")}
    )


@login_required
@permission_required("experiment.register_equipment")
def muscle_create(request, template_name="experiment/muscle_register.html"):
    muscle_form = MuscleRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if muscle_form.is_valid():
                muscle_added = muscle_form.save(commit=False)
                muscle_added.save()

                messages.success(request, _("Muscle created successfully."))
                redirect_url = reverse("muscle_view", args=(muscle_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {"equipment_form": muscle_form, "creating": True, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def muscle_update(request, muscle_id, template_name="experiment/muscle_register.html"):
    muscle = get_object_or_404(Muscle, pk=muscle_id)

    muscle_form = MuscleRegisterForm(request.POST or None, instance=muscle)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if muscle_form.is_valid():
                if muscle_form.has_changed():
                    muscle_form.save()
                    messages.success(request, _("Muscle updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("muscle_view", args=(muscle.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"equipment": muscle, "equipment_form": muscle_form, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def muscle_view(request, muscle_id, template_name="experiment/muscle_register.html"):
    muscle = get_object_or_404(Muscle, pk=muscle_id)
    musclesubdivisions = muscle.musclesubdivision_set.all()
    musclesides = muscle.muscleside_set.all()

    muscle_form = MuscleRegisterForm(request.POST or None, instance=muscle)

    for field in muscle_form.fields:
        muscle_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                muscle.delete()
                messages.success(request, _("Muscle removed successfully."))
                return redirect("muscle_list")
            except ProtectedError:
                messages.error(request, _("Error trying to delete muscle."))
                redirect_url = reverse("muscle_view", args=(muscle_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "equipment": muscle,
        "equipment_form": muscle_form,
        "musclesubdivisions": musclesubdivisions,
        "musclesides": musclesides,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def muscle_subdivision_create(
    request, muscle_id, template_name="experiment/muscle_subdivision_register.html"
):
    muscle = get_object_or_404(Muscle, pk=muscle_id)

    muscle_subdivision_form = MuscleSubdivisionRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if muscle_subdivision_form.is_valid():
                muscle_added = muscle_subdivision_form.save(commit=False)
                muscle_added.muscle = muscle
                muscle_added.save()

                messages.success(request, _("Muscle subdivision created successfully."))
                redirect_url = reverse(
                    "muscle_subdivision_view", args=(muscle_added.id,)
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "equipment_form": muscle_subdivision_form,
        "muscle": muscle,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def muscle_subdivision_view(
    request,
    muscle_subdivision_id,
    template_name="experiment/muscle_subdivision_register.html",
):
    muscle_subdivsion = get_object_or_404(MuscleSubdivision, pk=muscle_subdivision_id)

    muscle_subdivision_form = MuscleSubdivisionRegisterForm(
        request.POST or None, instance=muscle_subdivsion
    )

    for field in muscle_subdivision_form.fields:
        muscle_subdivision_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                muscle_id = muscle_subdivsion.muscle.id
                muscle_subdivsion.delete()
                messages.success(request, _("Muscle subdivision removed successfully."))
                redirect_url = reverse("muscle_view", args=(muscle_id,))
                return HttpResponseRedirect(redirect_url)
            except ProtectedError:
                messages.error(request, _("Error trying to delete muscle subdivision."))
                redirect_url = reverse(
                    "muscle_subdivision_view", args=(muscle_subdivision_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "equipment": muscle_subdivsion,
        "equipment_form": muscle_subdivision_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def muscle_subdivision_update(
    request,
    muscle_subdivision_id,
    template_name="experiment/muscle_subdivision_register.html",
):
    muscle_subdivision = get_object_or_404(MuscleSubdivision, pk=muscle_subdivision_id)

    muscle_subdivision_form = MuscleSubdivisionRegisterForm(
        request.POST or None, instance=muscle_subdivision
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if muscle_subdivision_form.is_valid():
                if muscle_subdivision_form.has_changed():
                    muscle_subdivision_form.save()
                    messages.success(
                        request, _("Muscle subdivision updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "muscle_subdivision_view", args=(muscle_subdivision.id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "equipment": muscle_subdivision,
        "equipment_form": muscle_subdivision_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def muscle_side_create(
    request, muscle_id, template_name="experiment/muscle_side_register.html"
):
    muscle = get_object_or_404(Muscle, pk=muscle_id)

    muscle_side_form = MuscleSideRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if muscle_side_form.is_valid():
                muscle_side_added = muscle_side_form.save(commit=False)
                muscle_side_added.muscle = muscle
                muscle_side_added.save()

                messages.success(request, _("Muscle side created successfully."))
                redirect_url = reverse("muscle_view", args=(muscle.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "equipment_form": muscle_side_form,
        "muscle": muscle,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def muscle_side_view(
    request, muscle_side_id, template_name="experiment/muscle_side_register.html"
):
    muscle_side = get_object_or_404(MuscleSide, pk=muscle_side_id)

    muscle_side_form = MuscleSideRegisterForm(
        request.POST or None, instance=muscle_side
    )

    for field in muscle_side_form.fields:
        muscle_side_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                muscle_id = muscle_side.muscle.id
                muscle_side.delete()
                messages.success(request, _("Muscle side removed successfully."))
                redirect_url = reverse("muscle_view", args=(muscle_id,))
                return HttpResponseRedirect(redirect_url)
            except ProtectedError:
                messages.error(request, _("Error trying to delete muscle side."))
                redirect_url = reverse("muscle_side_view", args=(muscle_side_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "equipment": muscle_side,
        "equipment_form": muscle_side_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def muscle_side_update(
    request, muscle_side_id, template_name="experiment/muscle_side_register.html"
):
    muscle_side = get_object_or_404(MuscleSide, pk=muscle_side_id)

    muscle_side_form = MuscleSideRegisterForm(
        request.POST or None, instance=muscle_side
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if muscle_side_form.is_valid():
                if muscle_side_form.has_changed():
                    muscle_side_form.save()
                    messages.success(request, _("Muscle side updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("muscle_side_view", args=(muscle_side.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "equipment": muscle_side,
        "equipment_form": muscle_side_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def software_list(request, template_name="experiment/software_list.html"):
    return render(
        request, template_name, {"softwares": Software.objects.all().order_by("name")}
    )


@login_required
@permission_required("experiment.register_equipment")
def software_create(request, template_name="experiment/software_register.html"):
    software_form = SoftwareRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if software_form.is_valid():
                software_added = software_form.save(commit=False)
                software_added.save()

                messages.success(request, _("Software created successfully."))
                redirect_url = reverse("software_view", args=(software_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {"software_form": software_form, "creating": True, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def software_view(
    request, software_id, template_name="experiment/software_register.html"
):
    software = get_object_or_404(Software, pk=software_id)
    # musclesubdivisions = muscle.musclesubdivision_set.all()
    # musclesides = muscle.muscleside_set.all()

    software_form = SoftwareRegisterForm(request.POST or None, instance=software)

    for field in software_form.fields:
        software_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                software.delete()
                messages.success(request, _("Software removed successfully."))
                return redirect("software_list")
            except ProtectedError:
                messages.error(request, _("Error trying to delete software."))
                redirect_url = reverse("software_view", args=(software_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "software": software,
        "software_form": software_form,
        # "musclesubdivisions": musclesubdivisions,
        # "musclesides": musclesides
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def software_update(
    request, software_id, template_name="experiment/software_register.html"
):
    software = get_object_or_404(Software, pk=software_id)

    software_form = SoftwareRegisterForm(request.POST or None, instance=software)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if software_form.is_valid():
                if software_form.has_changed():
                    software_form.save()
                    messages.success(request, _("Software updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("software_view", args=(software.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"software": software, "software_form": software_form, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def software_version_create(
    request, software_id, template_name="experiment/software_version_register.html"
):
    software = get_object_or_404(Software, pk=software_id)

    software_version_form = SoftwareVersionRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if software_version_form.is_valid():
                version_added = software_version_form.save(commit=False)
                version_added.software = software
                version_added.save()

                messages.success(request, _("Software version created successfully."))
                # redirect_url = reverse("software_version_view", args=(version_added.id,))
                redirect_url = reverse(
                    "software_view", args=(version_added.software.id,)
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "software_version_form": software_version_form,
        "software": software,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def software_version_view(
    request,
    software_version_id,
    template_name="experiment/software_version_register.html",
):
    software_version = get_object_or_404(SoftwareVersion, pk=software_version_id)

    software_version_form = SoftwareVersionRegisterForm(
        request.POST or None, instance=software_version
    )

    for field in software_version_form.fields:
        software_version_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                software_id = software_version.software.id
                software_version.delete()
                messages.success(request, _("Software version removed successfully."))
                redirect_url = reverse("software_view", args=(software_id,))
                return HttpResponseRedirect(redirect_url)
            except ProtectedError:
                messages.error(request, _("Error trying to delete software version."))
                redirect_url = reverse(
                    "software_version_view", args=(software_version_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "software_version": software_version,
        "software_version_form": software_version_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def software_version_update(
    request,
    software_version_id,
    template_name="experiment/software_version_register.html",
):
    software_version = get_object_or_404(SoftwareVersion, pk=software_version_id)

    software_version_form = SoftwareVersionRegisterForm(
        request.POST or None, instance=software_version
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if software_version_form.is_valid():
                if software_version_form.has_changed():
                    software_version_form.save()
                    messages.success(
                        request, _("Software version updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "software_version_view", args=(software_version.id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "software_version": software_version,
        "software_version_form": software_version_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def electrodemodel_list(request, template_name="experiment/electrodemodel_list.html"):
    return render(
        request,
        template_name,
        {"equipments": ElectrodeModel.objects.all().order_by("name")},
    )


@login_required
@permission_required("experiment.register_equipment")
def electrodemodel_create(
    request, template_name="experiment/electrodemodel_register.html"
):
    electrodemodel_form = ElectrodeModelRegisterForm(request.POST or None)

    tags = set_all_tags()

    if request.method == "POST":
        if request.POST["action"] == "save":
            if electrodemodel_form.is_valid():
                electrodemodel_added = electrodemodel_form.save(commit=False)
                electrodemodel_added.save()

                on_tags = get_tag_ids_from_post(request.POST)
                equipment_tags_update(
                    electrodemodel_added.id, on_tags, "ElectrodeModel"
                )

                tags = get_tags(electrodemodel_added.id, "ElectrodeModel")

                messages.success(request, _("Electrode model created successfully."))
                redirect_url = reverse(
                    "electrodemodel_view", args=(electrodemodel_added.id,)
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "equipment_form": electrodemodel_form,
        "creating": True,
        "editing": True,
        "tags": tags,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def electrodemodel_update(
    request, electrodemodel_id, template_name="experiment/electrodemodel_register.html"
):
    electrodemodel = get_object_or_404(ElectrodeModel, pk=electrodemodel_id)

    electrodemodel_form = ElectrodeModelRegisterForm(
        request.POST or None, instance=electrodemodel
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if electrodemodel_form.is_valid():
                new_tags = get_tag_ids_from_post(request.POST)
                changed_tags = equipment_tags_update(
                    electrodemodel_id, new_tags, "ElectrodeModel"
                )

                if electrodemodel_form.has_changed() or changed_tags:
                    electrodemodel_form.save()
                    messages.success(
                        request, _("Electrode model updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("electrodemodel_view", args=(electrodemodel.id,))
                return HttpResponseRedirect(redirect_url)

    tags = get_tags(electrodemodel_id, "ElectrodeModel")

    context = {
        "equipment": electrodemodel,
        "equipment_form": electrodemodel_form,
        "editing": True,
        "tags": tags,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def electrodemodel_view(
    request, electrodemodel_id, template_name="experiment/electrodemodel_register.html"
):
    electrodemodel = get_object_or_404(ElectrodeModel, pk=electrodemodel_id)

    electrodemodel_form = ElectrodeModelRegisterForm(
        request.POST or None, instance=electrodemodel
    )

    for field in electrodemodel_form.fields:
        electrodemodel_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                electrodemodel.delete()
                messages.success(request, _("Electrode model removed successfully."))
                return redirect("electrodemodel_list")
            except ProtectedError:
                messages.error(request, _("Error trying to delete electrode model."))
                redirect_url = reverse("electrodemodel_view", args=(electrodemodel_id,))
                return HttpResponseRedirect(redirect_url)

    tags = get_tags(electrodemodel_id, "ElectrodeModel")

    context = {
        "can_change": True,
        "equipment": electrodemodel,
        "equipment_form": electrodemodel_form,
        "tags": tags,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def coil_list(request, template_name="experiment/coil_list.html"):
    return render(
        request, template_name, {"equipments": CoilModel.objects.all().order_by("name")}
    )


@login_required
@permission_required("experiment.register_equipment")
def coil_create(request, template_name="experiment/coil_register.html"):
    coil_model_form = CoilModelRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if coil_model_form.is_valid():
                coil_model_added = coil_model_form.save(commit=False)
                coil_model_added.save()

                messages.success(request, _("Coil Model created successfully."))
                redirect_url = reverse("coil_view", args=(coil_model_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {"equipment_form": coil_model_form, "creating": True, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def coil_view(request, coil_id, template_name="experiment/coil_register.html"):
    coilmodel = get_object_or_404(CoilModel, pk=coil_id)

    coilmodel_form = CoilModelRegisterForm(request.POST or None, instance=coilmodel)

    for field in coilmodel_form.fields:
        coilmodel_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                coilmodel.delete()
                messages.success(request, _("Coil model removed successfully."))
                return redirect("coil_list")
            except ProtectedError:
                messages.error(request, _("Error trying to delete coil model."))
                redirect_url = reverse("coil_view", args=(coil_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "equipment": coilmodel,
        "equipment_form": coilmodel_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def coil_update(request, coil_id, template_name="experiment/coil_register.html"):
    coilmodel = get_object_or_404(CoilModel, pk=coil_id)

    coilmodel_form = CoilModelRegisterForm(request.POST or None, instance=coilmodel)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if coilmodel_form.is_valid():
                if coilmodel_form.has_changed():
                    coilmodel_form.save()
                    messages.success(request, _("Coil Model updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("coil_view", args=(coilmodel.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "equipment": coilmodel,
        "equipment_form": coilmodel_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def tmsdevice_list(request, template_name="experiment/tmsdevice_list.html"):
    return render(request, template_name, {"equipments": TMSDevice.objects.all()})


@login_required
@permission_required("experiment.register_equipment")
def tmsdevice_create(request, template_name="experiment/tmsdevice_register.html"):
    tms_device_form = TMSDeviceRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if tms_device_form.is_valid():
                tms_device_added = tms_device_form.save(commit=False)
                tms_device_added.equipment_type = "tms_device"
                tms_device_added.save()

                messages.success(request, _("TMS device created successfully."))
                redirect_url = reverse("tmsdevice_view", args=(tms_device_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {"equipment_form": tms_device_form, "creating": True, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def tmsdevice_view(
    request, tmsdevice_id, template_name="experiment/tmsdevice_register.html"
):
    tmsdevice = get_object_or_404(TMSDevice, pk=tmsdevice_id)

    tmsdevice_form = TMSDeviceRegisterForm(request.POST or None, instance=tmsdevice)

    for field in tmsdevice_form.fields:
        tmsdevice_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                tmsdevice.delete()
                messages.success(request, _("TMS device removed successfully."))
                return redirect("tmsdevice_list")
            except ProtectedError:
                messages.error(request, _("Error trying to delete TMS device."))
                redirect_url = reverse("tmsdevice_view", args=(tmsdevice_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "equipment": tmsdevice,
        "equipment_form": tmsdevice_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def tmsdevice_update(
    request, tmsdevice_id, template_name="experiment/tmsdevice_register.html"
):
    tmsdevice = get_object_or_404(TMSDevice, pk=tmsdevice_id)

    tmsdevice_form = TMSDeviceRegisterForm(request.POST or None, instance=tmsdevice)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if tmsdevice_form.is_valid():
                if tmsdevice_form.has_changed():
                    tmsdevice_form.save()
                    messages.success(request, _("TMS device updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("tmsdevice_view", args=(tmsdevice.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "equipment": tmsdevice,
        "equipment_form": tmsdevice_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def material_list(request, template_name="experiment/material_list.html"):
    return render(
        request, template_name, {"equipments": Material.objects.all().order_by("name")}
    )


@login_required
@permission_required("experiment.register_equipment")
def material_create(request, template_name="experiment/material_register.html"):
    material_form = MaterialRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if material_form.is_valid():
                material_added = material_form.save(commit=False)
                material_added.save()

                messages.success(request, _("Material created successfully."))
                redirect_url = reverse("material_view", args=(material_added.id,))
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {"equipment_form": material_form, "creating": True, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def material_update(
    request, material_id, template_name="experiment/material_register.html"
):
    material = get_object_or_404(Material, pk=material_id)

    material_form = MaterialRegisterForm(request.POST or None, instance=material)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if material_form.is_valid():
                if material_form.has_changed():
                    material_form.save()
                    messages.success(request, _("Material updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("material_view", args=(material.id,))
                return HttpResponseRedirect(redirect_url)

    context = {"equipment": material, "equipment_form": material_form, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def material_view(
    request, material_id, template_name="experiment/material_register.html"
):
    material = get_object_or_404(Material, pk=material_id)

    material_form = MaterialRegisterForm(request.POST or None, instance=material)

    for field in material_form.fields:
        material_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                material.delete()
                messages.success(request, _("Material removed successfully."))
                return redirect("material_list")
            except ProtectedError:
                messages.error(request, _("Error trying to delete material."))
                redirect_url = reverse("material_view", args=(material_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "equipment": material,
        "equipment_form": material_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eegelectrodenet_list(request, template_name="experiment/eegelectrodenet_list.html"):
    return render(
        request,
        template_name,
        {"equipments": EEGElectrodeNet.objects.all().order_by("identification")},
    )


@login_required
@permission_required("experiment.register_equipment")
def eegelectrodenet_create(
    request, template_name="experiment/eegelectrodenet_register.html"
):
    eegelectrodenet_form = EEGElectrodeNETRegisterForm(request.POST or None)
    cap_form = EEGElectrodeCapRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            is_a_cap = "cap_flag" in request.POST

            if eegelectrodenet_form.is_valid() and (
                not is_a_cap or (is_a_cap and cap_form.is_valid())
            ):
                eegelectrodenet_added = eegelectrodenet_form.save(commit=False)
                eegelectrodenet_added.equipment_type = "eeg_electrode_net"

                if not is_a_cap:
                    eegelectrodenet_added.save()
                else:
                    cap_added = cap_form.save(commit=False)
                    cap_added.equipment_type = eegelectrodenet_added.equipment_type
                    cap_added.electrode_model_default = (
                        eegelectrodenet_added.electrode_model_default
                    )
                    cap_added.manufacturer = eegelectrodenet_added.manufacturer
                    cap_added.identification = eegelectrodenet_added.identification
                    cap_added.description = eegelectrodenet_added.description
                    cap_added.serial_number = eegelectrodenet_added.serial_number
                    cap_added.save()

                equipment_added = cap_added if is_a_cap else eegelectrodenet_added

                tag = get_object_or_404(Tag, name="EEG")
                equipment_added.equipment_ptr.tags.add(tag)

                localization_systems = get_localization_system(request.POST)
                if localization_systems:
                    for localization_system_item in localization_systems:
                        localization_system_id = localization_system_item.split("_")[-1]
                        if request.POST[localization_system_item] == "on":
                            eeg_electrode_net_system = EEGElectrodeNetSystem()
                            eeg_electrode_net_system.eeg_electrode_net_id = (
                                equipment_added.id
                            )
                            eeg_electrode_net_system.eeg_electrode_localization_system_id = (
                                localization_system_id
                            )
                            eeg_electrode_net_system.save()

                messages.success(request, _("EEG electrode net created successfully."))
                redirect_url = reverse(
                    "eegelectrodenet_view", args=(equipment_added.id,)
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    eegelectrodelocalizationsystem = EEGElectrodeLocalizationSystem.objects.all()

    for localization_system in eegelectrodelocalizationsystem:
        localization_system.checked = False
        localization_system.used = False
        localization_system.disabled = False

    context = {
        "equipment_form": eegelectrodenet_form,
        "is_a_cap": False,
        "cap_form": cap_form,
        "eegelectrodelocalizationsystem": eegelectrodelocalizationsystem,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


def get_localization_system(data_post):
    localization_list = []
    for item in data_post:
        if "localization_system" in item:
            localization_list.append(item)

    return localization_list


@login_required
@permission_required("experiment.register_equipment")
def eegelectrodenet_update(
    request,
    eegelectrodenet_id,
    template_name="experiment/eegelectrodenet_register.html",
):
    eegelectrodenet = get_object_or_404(EEGElectrodeNet, pk=eegelectrodenet_id)
    eegelectrodenetsystem = EEGElectrodeNetSystem.objects.all()

    eegelectrodenet_form = EEGElectrodeNETRegisterForm(
        request.POST or None, instance=eegelectrodenet
    )

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
        if request.POST["action"] == "save":
            if eegelectrodenet_form.is_valid():
                changed = False

                new_localization_systems = get_localization_system(request.POST)

                current_localization_systems = [
                    item.eeg_electrode_localization_system.id
                    for item in EEGElectrodeNetSystem.objects.filter(
                        eeg_electrode_net_id=eegelectrodenet_id
                    )
                ]

                # Checking if some localization_system was unchecked
                for item in current_localization_systems:
                    if (
                        "localization_system_" + str(item)
                        not in new_localization_systems
                    ):
                        # get the net_system
                        eeg_electrode_net_system = EEGElectrodeNetSystem.objects.filter(
                            eeg_electrode_net=eegelectrodenet,
                            eeg_electrode_localization_system_id=item,
                        )[0]

                        # check if the net_system is not been used by some layout_setting
                        # (the used net_system was rendered as disabled)
                        if not EEGElectrodeLayoutSetting.objects.filter(
                            eeg_electrode_net_system=eeg_electrode_net_system
                        ).exists():
                            eeg_electrode_net_system.delete()
                            changed = True

                # Checking if some localization_system was checked
                for item in new_localization_systems:
                    localization_system_id = item.split("_")[-1]

                    if int(localization_system_id) not in current_localization_systems:
                        # create a new net_system
                        eeg_electrode_net_system = EEGElectrodeNetSystem()
                        eeg_electrode_net_system.eeg_electrode_net_id = (
                            eegelectrodenet.id
                        )
                        eeg_electrode_net_system.eeg_electrode_localization_system_id = (
                            localization_system_id
                        )
                        eeg_electrode_net_system.save()
                        changed = True

                if is_a_cap and cap_form.has_changed():
                    cap_form.save()
                    changed = True

                if eegelectrodenet_form.has_changed():
                    eegelectrodenet_form.save()
                    changed = True

                if changed:
                    messages.success(
                        request, _("EEG electrode net updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "eegelectrodenet_view", args=(eegelectrodenet.id,)
                )
                return HttpResponseRedirect(redirect_url)

    eegelectrodelocalizationsystem = EEGElectrodeLocalizationSystem.objects.all()

    for localization_system in eegelectrodelocalizationsystem:
        localization_system.checked = False
        localization_system.used = False
        localization_system.disabled = False
        net_system = EEGElectrodeNetSystem.objects.filter(
            eeg_electrode_net=eegelectrodenet,
            eeg_electrode_localization_system=localization_system,
        )
        if net_system:
            localization_system.checked = True
            if EEGElectrodeLayoutSetting.objects.filter(
                eeg_electrode_net_system__in=net_system
            ):
                localization_system.used = True
                localization_system.disabled = True

    context = {
        "equipment": eegelectrodenet,
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
@permission_required("experiment.register_equipment")
def eegelectrodenet_view(
    request,
    eegelectrodenet_id,
    template_name="experiment/eegelectrodenet_register.html",
):
    eegelectrodenet = get_object_or_404(EEGElectrodeNet, pk=eegelectrodenet_id)
    eegelectrodenet_form = EEGElectrodeNETRegisterForm(
        request.POST or None, instance=eegelectrodenet
    )

    cap = EEGElectrodeCap.objects.filter(id=eegelectrodenet_id)
    cap_size_list = None
    if cap:
        cap_form = EEGElectrodeCapRegisterForm(request.POST or None, instance=cap[0])
        cap_size_list = EEGCapSize.objects.filter(eeg_electrode_cap=cap[0])
    else:
        cap_form = EEGElectrodeCapRegisterForm(request.POST or None)

    eegelectrodelocalizationsystem = EEGElectrodeLocalizationSystem.objects.all()

    for field in eegelectrodenet_form.fields:
        eegelectrodenet_form.fields[field].widget.attrs["disabled"] = True

    for field in cap_form.fields:
        cap_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            net_system = EEGElectrodeNetSystem.objects.filter(
                eeg_electrode_net=eegelectrodenet
            )
            if net_system and EEGElectrodeLayoutSetting.objects.filter(
                eeg_electrode_net_system__in=net_system
            ):
                messages.error(
                    request,
                    _(
                        "EEG electrode net cannot be removed because it is used in EEG electrode system."
                    ),
                )
                redirect_url = reverse(
                    "eegelectrodenet_view", args=(eegelectrodenet_id,)
                )
                return HttpResponseRedirect(redirect_url)
            else:
                try:
                    if cap:
                        if cap_size_list:
                            eeg_data = EEGData.objects.filter(
                                eeg_cap_size__in=cap_size_list
                            )
                            if eeg_data:
                                messages.error(
                                    request,
                                    _(
                                        "EEG electrode net cannot be removed because "
                                        "cap size is associated with EEG data."
                                    ),
                                )
                                redirect_url = reverse(
                                    "eegelectrodenet_view", args=(eegelectrodenet_id,)
                                )
                                return HttpResponseRedirect(redirect_url)
                            cap_size_list.delete()
                        cap.delete()
                    else:
                        eegelectrodenet.delete()
                    messages.success(
                        request, _("EEG electrode net removed successfully.")
                    )
                    return redirect("eegelectrodenet_list")
                except ProtectedError:
                    messages.error(
                        request, _("Error trying to delete EEG Electrode Net.")
                    )
                    redirect_url = reverse(
                        "eegelectrodenet_view", args=(eegelectrodenet_id,)
                    )
                    return HttpResponseRedirect(redirect_url)

    for localization_system in eegelectrodelocalizationsystem:
        localization_system.checked = False
        localization_system.used = False
        localization_system.disabled = True
        net_system = EEGElectrodeNetSystem.objects.filter(
            eeg_electrode_net=eegelectrodenet,
            eeg_electrode_localization_system=localization_system,
        )
        if net_system:
            localization_system.checked = True
            if EEGElectrodeLayoutSetting.objects.filter(
                eeg_electrode_net_system__in=net_system
            ):
                localization_system.used = True

    context = {
        "can_change": True,
        "equipment": eegelectrodenet,
        "is_a_cap": True if cap else False,
        "equipment_form": eegelectrodenet_form,
        "cap_form": cap_form,
        "cap_size_list": cap_size_list,
        "eegelectrodelocalizationsystem": eegelectrodelocalizationsystem,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eegelectrodenet_cap_size_create(
    request,
    eegelectrode_cap_id,
    template_name="experiment/eegelectrodenet_size_register.html",
):
    cap = get_object_or_404(EEGElectrodeCap, pk=eegelectrode_cap_id)
    cap_size_form = EEGCapSizeRegisterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if cap_size_form.is_valid():
                eegcapsize_added = cap_size_form.save(commit=False)
                eegcapsize_added.eeg_electrode_cap_id = eegelectrode_cap_id
                eegcapsize_added.save()

                messages.success(request, _("EEG cap size created successfully."))
                redirect_url = reverse(
                    "eegelectrodenet_view", args=(eegelectrode_cap_id,)
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "eeg_cap": cap,
        "can_change": True,
        "equipment_form": cap_size_form,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eegelectrodenet_cap_size_update(
    request,
    eegelectrode_cap_size_id,
    template_name="experiment/eegelectrodenet_size_register.html",
):
    eegelectrode_cap_size = get_object_or_404(EEGCapSize, pk=eegelectrode_cap_size_id)

    eegelectrode_cap_size_form = EEGCapSizeRegisterForm(
        request.POST or None, instance=eegelectrode_cap_size
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if eegelectrode_cap_size_form.is_valid():
                if eegelectrode_cap_size_form.has_changed():
                    eegelectrode_cap_size_form.save()
                    messages.success(request, _("Cap size updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "eegelectrodenet_cap_size_view", args=(eegelectrode_cap_size.id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "equipment": eegelectrode_cap_size,
        "equipment_form": eegelectrode_cap_size_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eegelectrodenet_cap_size_view(
    request,
    eegelectrode_cap_size_id,
    template_name="experiment/eegelectrodenet_size_register.html",
):
    eegelectrode_cap_size = get_object_or_404(EEGCapSize, pk=eegelectrode_cap_size_id)

    eegelectrode_cap_size_form = EEGCapSizeRegisterForm(
        request.POST or None, instance=eegelectrode_cap_size
    )

    for field in eegelectrode_cap_size_form.fields:
        eegelectrode_cap_size_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                eegelectrode_cap_size.delete()
                messages.success(request, _("Cap size removed successfully."))
                redirect_url = reverse(
                    "eegelectrodenet_view",
                    args=(eegelectrode_cap_size.eeg_electrode_cap_id,),
                )
                return HttpResponseRedirect(redirect_url)
            except ProtectedError:
                messages.error(request, _("Error trying to delete cap size."))
                redirect_url = reverse(
                    "eegelectrodenet_cap_size_view", args=(eegelectrode_cap_size_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "equipment_form": eegelectrode_cap_size_form,
        "can_change": True,
        "equipment": eegelectrode_cap_size,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def ad_converter_list(request, template_name="experiment/ad_converter_list.html"):
    return render(
        request,
        template_name,
        {"equipments": ADConverter.objects.all().order_by("identification")},
    )


@login_required
@permission_required("experiment.register_equipment")
def ad_converter_create(request, template_name="experiment/ad_converter_register.html"):
    ad_converter_form = ADConverterRegisterForm(
        request.POST or None, initial={"equipment_type": "ad_converter"}
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if ad_converter_form.is_valid():
                ad_converter_added = ad_converter_form.save(commit=False)
                ad_converter_added.equipment_type = "ad_converter"
                ad_converter_added.save()

                messages.success(request, _("A/D converter created successfully."))
                redirect_url = reverse(
                    "ad_converter_view", args=(ad_converter_added.id,)
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))

        else:
            messages.warning(request, _("Action not available."))

    context = {
        "equipment_form": ad_converter_form,
        "creating": True,
        "editing": True
        # "tags": tags
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def ad_converter_update(
    request, ad_converter_id, template_name="experiment/ad_converter_register.html"
):
    ad_converter = get_object_or_404(ADConverter, pk=ad_converter_id)

    ad_converter_form = ADConverterRegisterForm(
        request.POST or None, instance=ad_converter
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if ad_converter_form.is_valid():
                # if ad_converter_form.has_changed() or changed_tags:
                if ad_converter_form.has_changed():
                    ad_converter_form.save()
                    messages.success(request, _("A/D converter updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("ad_converter_view", args=(ad_converter.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "equipment": ad_converter,
        "equipment_form": ad_converter_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def ad_converter_view(
    request, ad_converter_id, template_name="experiment/ad_converter_register.html"
):
    ad_converter = get_object_or_404(ADConverter, pk=ad_converter_id)

    ad_converter_form = ADConverterRegisterForm(
        request.POST or None, instance=ad_converter
    )

    for field in ad_converter_form.fields:
        ad_converter_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                ad_converter.delete()
                messages.success(request, _("A/D converter removed successfully."))
                return redirect("ad_converter_list")
            except ProtectedError:
                messages.error(request, _("Error trying to delete A/D converter."))
                redirect_url = reverse("ad_converter_view", args=(ad_converter_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "equipment": ad_converter,
        "equipment_form": ad_converter_form,
    }

    return render(request, template_name, context)


def search_cid10_ajax(request):
    cid_10_list = ""

    if request.method == "POST":
        search_text = request.POST["search_text"]
        group_id = request.POST["group_id"]

        if search_text:
            cid_10_list = ClassificationOfDiseases.objects.filter(
                Q(abbreviated_description__icontains=search_text)
                | Q(description__icontains=search_text)
                | Q(code__icontains=search_text)
            )

        if group_id:
            return render(
                None,
                "experiment/ajax_cid10.html",
                {"cid_10_list": cid_10_list, "group_id": group_id},
            )
        else:
            return render(
                None,
                "export/diagnoses.html",
                {"classification_of_diseases_list": cid_10_list},
            )


@login_required
@permission_required("experiment.change_experiment")
def classification_of_diseases_insert(request, group_id, classification_of_diseases_id):
    """Add group disease"""
    group = get_object_or_404(Group, pk=group_id)

    check_can_change(request.user, group.experiment.research_project)

    classification_of_diseases = get_object_or_404(
        ClassificationOfDiseases, pk=classification_of_diseases_id
    )
    group.classification_of_diseases.add(classification_of_diseases)
    redirect_url = reverse("group_view", args=(group_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.change_experiment")
def classification_of_diseases_remove(request, group_id, classification_of_diseases_id):
    """Remove group disease"""
    group = get_object_or_404(Group, pk=group_id)

    check_can_change(request.user, group.experiment.research_project)

    classification_of_diseases = get_object_or_404(
        ClassificationOfDiseases, pk=classification_of_diseases_id
    )
    classification_of_diseases.group_set.remove(group)
    redirect_url = reverse("group_view", args=(group_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.view_researchproject")
def questionnaire_view(
    request,
    group_id,
    component_configuration_id,
    template_name="experiment/questionnaire_view.html",
):
    questionnaire_configuration = get_object_or_404(
        ComponentConfiguration, pk=component_configuration_id
    )
    group = get_object_or_404(Group, pk=group_id)
    questionnaire = Questionnaire.objects.get(
        id=questionnaire_configuration.component.id
    )

    surveys = Questionnaires()
    survey = Questionnaire.objects.get(
        id=questionnaire_configuration.component_id
    ).survey
    language = get_questionnaire_language(
        surveys, survey.lime_survey_id, request.LANGUAGE_CODE
    )

    questionnaire_title = find_questionnaire_name(survey, request.LANGUAGE_CODE)["name"]

    limesurvey_available = check_limesurvey_access(request, surveys)

    subject_list_with_status = []

    for subject_of_group in SubjectOfGroup.objects.filter(group=group).order_by(
        "subject__patient__name"
    ):
        subject_responses = QuestionnaireResponse.objects.filter(
            subject_of_group=subject_of_group,
            data_configuration_tree__component_configuration=questionnaire_configuration,
        )
        amount_of_completed_questionnaires = 0
        questionnaire_responses_with_status = []

        for subject_response in subject_responses:
            properties = surveys.get_participant_properties(
                survey.lime_survey_id, subject_response.token_id
            )
            update_completed_status(
                survey.lime_survey_id, properties["completed"], subject_response
            )
            completed = False

            acquisitiondate_updated = update_acquisition_date(
                survey.lime_survey_id, properties["token"], subject_response, language
            )

            if (
                subject_response.is_completed != "N"
                and subject_response.is_completed != ""
            ):
                amount_of_completed_questionnaires += 1
                completed = True

            questionnaire_responses_with_status.append(
                {
                    "questionnaire_response": subject_response,
                    "completed": completed,
                    "acquisitiondate_updated": acquisitiondate_updated,
                }
            )

        # If unlimited fills, percentage is related to the number of completed
        # questionnaires
        if questionnaire_configuration.number_of_repetitions is None:
            denominator = subject_responses.count()

            if subject_responses.count() > 0:
                percentage = 100 * amount_of_completed_questionnaires / denominator
            else:
                percentage = 0
        else:
            denominator = questionnaire_configuration.number_of_repetitions

            # Handle cases in which number of possible responses was reduced
            # afterwords.
            if (
                questionnaire_configuration.number_of_repetitions
                < amount_of_completed_questionnaires
            ):
                percentage = 100
            else:
                percentage = 100 * amount_of_completed_questionnaires / denominator

        subject_list_with_status.append(
            {
                "subject": subject_of_group.subject,
                "amount_of_completed_questionnaires": amount_of_completed_questionnaires,
                "denominator": denominator,
                "percentage": int(percentage),
                "questionnaire_responses": questionnaire_responses_with_status,
            }
        )

    surveys.release_session_key()

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "questionnaire_title": questionnaire_title,
        "questionnaire_configuration": questionnaire_configuration,
        "subject_list": subject_list_with_status,
        "limesurvey_available": limesurvey_available,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def subjects(request, group_id, template_name="experiment/subjects.html"):
    experimental_protocol_info = {
        "number_of_questionnaires": 0,
        "number_of_eeg_data": 0,
        "number_of_emg_data": 0,
        "number_of_tms_data": 0,
        "number_of_digital_game_phase_data": 0,
        "number_of_generic_data_collection_data": 0,
        "number_of_media_collection_data": 0,
    }

    group = get_object_or_404(Group, id=group_id)

    subject_id = None

    goalkeeper = False

    if request.method == "POST" and request.POST["action"][:6] == "remove":
        subject_id = request.POST["action"][7:]
        subject_list = SubjectOfGroup.objects.filter(
            group=group, subject_id=subject_id
        ).order_by("subject__patient__name")
    else:
        subject_list = SubjectOfGroup.objects.filter(group=group).order_by(
            "subject__patient__name"
        )

    subject_list_with_status = []
    surveys = Questionnaires()
    limesurvey_available = check_limesurvey_access(request, surveys)

    can_remove = True

    # Navigate the components of the experimental protocol from the root to see if there is any questionnaire component
    # in this group.
    if group.experimental_protocol is not None:
        list_of_questionnaires_configuration = create_list_of_trees(
            group.experimental_protocol, "questionnaire"
        )

        list_of_eeg_configuration = create_list_of_trees(
            group.experimental_protocol, "eeg"
        )
        list_of_emg_configuration = create_list_of_trees(
            group.experimental_protocol, "emg"
        )
        list_of_tms_configuration = create_list_of_trees(
            group.experimental_protocol, "tms"
        )
        list_of_digital_game_phase_configuration = create_list_of_trees(
            group.experimental_protocol, "digital_game_phase"
        )
        list_of_generic_data_collection_configuration = create_list_of_trees(
            group.experimental_protocol, "generic_data_collection"
        )
        list_of_media_collection_configuration = create_list_of_trees(
            group.experimental_protocol, "media_collection"
        )

        experimental_protocol_info = {
            "number_of_questionnaires": len(list_of_questionnaires_configuration),
            "number_of_eeg_data": len(list_of_eeg_configuration),
            "number_of_emg_data": len(list_of_emg_configuration),
            "number_of_tms_data": len(list_of_tms_configuration),
            "number_of_digital_game_phase_data": len(
                list_of_digital_game_phase_configuration
            ),
            "number_of_generic_data_collection_data": len(
                list_of_generic_data_collection_configuration
            ),
            "number_of_media_collection_data": len(
                list_of_media_collection_configuration
            ),
        }

        if experimental_protocol_info["number_of_digital_game_phase_data"]:
            if (
                "goalkeeper" in settings.DATABASES
                and GoalkeeperGameLog.objects.using("goalkeeper").first()
            ):
                goalkeeper = True

        # For each subject of the group...
        for subject_of_group in subject_list:
            number_of_questionnaires_filled = 0

            # For each questionnaire in the experimental protocol of the group...
            for questionnaire_configuration in list_of_questionnaires_configuration:
                # Get the responses
                path = [item[0] for item in questionnaire_configuration]
                data_configuration_tree_id = list_data_configuration_tree(
                    path[-1], path
                )
                subject_responses = QuestionnaireResponse.objects.filter(
                    subject_of_group=subject_of_group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )

                questionnaire_configuration = get_object_or_404(
                    ComponentConfiguration, pk=path[-1]
                )
                # This is a shortcut that allows to avoid the delay of the connection to LimeSurvey.
                if (
                    questionnaire_configuration.number_of_repetitions is None
                    and subject_responses.count() > 0
                ) or (
                    questionnaire_configuration.number_of_repetitions is not None
                    and subject_responses.count()
                    >= questionnaire_configuration.number_of_repetitions
                ):
                    # Count the number of completed responses
                    amount_of_completed_responses = 0

                    for subject_response in subject_responses:
                        # Check if completed
                        if (
                            subject_response.is_completed == "N"
                            or subject_response.is_completed == ""
                        ):
                            is_completed = (
                                surveys.get_participant_properties(
                                    Questionnaire.objects.get(
                                        id=questionnaire_configuration.component.id
                                    ).survey.lime_survey_id,
                                    subject_response.token_id,
                                    "completed",
                                )
                                or ""
                            )

                            subject_response.is_completed = is_completed
                            subject_response.save()

                        if (
                            subject_response.is_completed == "N"
                            or subject_response.is_completed == ""
                        ):
                            # If there is an incomplete response for a questionnaire, this questionnaire is counted
                            # as not completed.
                            amount_of_completed_responses = 0
                            break
                        else:
                            amount_of_completed_responses += 1

                    # Count this questionnaire as completed if it is unlimited and has at least one completed
                    # response, or it is limited and the amount of completed response is greater than or equal to
                    # the number of expected responses.
                    if (
                        questionnaire_configuration.number_of_repetitions is None
                        and amount_of_completed_responses > 0
                    ) or (
                        questionnaire_configuration.number_of_repetitions is not None
                        and amount_of_completed_responses
                        >= questionnaire_configuration.number_of_repetitions
                    ):
                        number_of_questionnaires_filled += 1

            percentage_of_questionnaires = 0

            if len(list_of_questionnaires_configuration) > 0:
                percentage_of_questionnaires = (
                    100
                    * number_of_questionnaires_filled
                    / len(list_of_questionnaires_configuration)
                )

            # EEG data files
            number_of_eeg_data_files_uploaded = 0
            # for each component_configuration of eeg...
            for eeg_configuration in list_of_eeg_configuration:
                path = [item[0] for item in eeg_configuration]
                data_configuration_tree_id = list_data_configuration_tree(
                    path[-1], path
                )
                eeg_data_files = EEGData.objects.filter(
                    subject_of_group=subject_of_group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                if len(eeg_data_files):
                    number_of_eeg_data_files_uploaded += 1

            percentage_of_eeg_data_files_uploaded = 0
            if len(list_of_eeg_configuration) > 0:
                percentage_of_eeg_data_files_uploaded = (
                    100
                    * number_of_eeg_data_files_uploaded
                    / len(list_of_eeg_configuration)
                )

            # EMG data files
            number_of_emg_data_files_uploaded = 0
            # for each component_configuration of emg...
            for emg_configuration in list_of_emg_configuration:
                path = [item[0] for item in emg_configuration]
                data_configuration_tree_id = list_data_configuration_tree(
                    path[-1], path
                )
                emg_data_files = EMGData.objects.filter(
                    subject_of_group=subject_of_group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                if len(emg_data_files):
                    number_of_emg_data_files_uploaded += 1

            percentage_of_emg_data_files_uploaded = 0
            if len(list_of_emg_configuration) > 0:
                percentage_of_emg_data_files_uploaded = (
                    100
                    * number_of_emg_data_files_uploaded
                    / len(list_of_emg_configuration)
                )

            # TMS data files
            number_of_tms_data_files_uploaded = 0
            # for each component_configuration of tms...
            for tms_configuration in list_of_tms_configuration:
                path = [item[0] for item in tms_configuration]
                data_configuration_tree_id = list_data_configuration_tree(
                    path[-1], path
                )
                tms_data_files = TMSData.objects.filter(
                    subject_of_group=subject_of_group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                if len(tms_data_files):
                    number_of_tms_data_files_uploaded += 1

            percentage_of_tms_data_files_uploaded = 0
            if len(list_of_tms_configuration) > 0:
                percentage_of_tms_data_files_uploaded = (
                    100
                    * number_of_tms_data_files_uploaded
                    / len(list_of_tms_configuration)
                )

            # Digital game phase data files
            number_of_digital_game_phase_data_files_uploaded = 0
            # for each component_configuration of tms...
            for (
                digital_game_phase_configuration
            ) in list_of_digital_game_phase_configuration:
                path = [item[0] for item in digital_game_phase_configuration]
                data_configuration_tree_id = list_data_configuration_tree(
                    path[-1], path
                )
                digital_game_phase_data_files = DigitalGamePhaseData.objects.filter(
                    subject_of_group=subject_of_group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                if len(digital_game_phase_data_files):
                    number_of_digital_game_phase_data_files_uploaded += 1

            percentage_of_digital_game_phase_data_files_uploaded = 0
            if len(list_of_digital_game_phase_configuration) > 0:
                percentage_of_digital_game_phase_data_files_uploaded = (
                    100
                    * number_of_digital_game_phase_data_files_uploaded
                    / len(list_of_digital_game_phase_configuration)
                )

            # Generic data collection data files
            number_of_generic_data_collection_data_files_uploaded = 0
            # for each component_configuration of tms...
            for (
                generic_data_collection_configuration
            ) in list_of_generic_data_collection_configuration:
                path = [item[0] for item in generic_data_collection_configuration]
                data_configuration_tree_id = list_data_configuration_tree(
                    path[-1], path
                )
                generic_data_collection_data_files = (
                    GenericDataCollectionData.objects.filter(
                        subject_of_group=subject_of_group,
                        data_configuration_tree_id=data_configuration_tree_id,
                    )
                )
                if len(generic_data_collection_data_files):
                    number_of_generic_data_collection_data_files_uploaded += 1

            percentage_of_generic_data_collection_data_files_uploaded = 0
            if len(list_of_generic_data_collection_configuration) > 0:
                percentage_of_generic_data_collection_data_files_uploaded = (
                    100
                    * number_of_generic_data_collection_data_files_uploaded
                    / len(list_of_generic_data_collection_configuration)
                )

            # Generic media data files
            number_of_media_collection_data_files_uploaded = 0
            # for each component_configuration of tms...
            for (
                media_collection_configuration
            ) in list_of_media_collection_configuration:
                path = [item[0] for item in media_collection_configuration]
                data_configuration_tree_id = list_data_configuration_tree(
                    path[-1], path
                )
                media_collection_data_files = MediaCollectionData.objects.filter(
                    subject_of_group=subject_of_group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                if len(media_collection_data_files):
                    number_of_media_collection_data_files_uploaded += 1

            percentage_of_media_collection_data_files_uploaded = 0
            if len(list_of_media_collection_configuration) > 0:
                percentage_of_media_collection_data_files_uploaded = (
                    100
                    * number_of_media_collection_data_files_uploaded
                    / len(list_of_media_collection_configuration)
                )

            # If any questionnaire has responses or any eeg/emg/tms/digital_game_phase/generic_data_collection
            # data file was uploaded, the subject can't be removed from the group.
            if (
                number_of_eeg_data_files_uploaded
                or number_of_emg_data_files_uploaded
                or number_of_tms_data_files_uploaded
                or number_of_digital_game_phase_data_files_uploaded
                or number_of_generic_data_collection_data_files_uploaded
                or number_of_media_collection_data_files_uploaded
                or number_of_questionnaires_filled
            ):
                can_remove = False

            subject_list_with_status.append(
                {
                    "subject": subject_of_group.subject,
                    "number_of_questionnaires_filled": number_of_questionnaires_filled,
                    "total_of_questionnaires": len(
                        list_of_questionnaires_configuration
                    ),
                    "percentage_of_questionnaires": int(percentage_of_questionnaires),
                    "consent": subject_of_group.consent_form,
                    "number_of_eeg_data_files_uploaded": number_of_eeg_data_files_uploaded,
                    "total_of_eeg_data_files": len(list_of_eeg_configuration),
                    "percentage_of_eeg_data_files_uploaded": int(
                        percentage_of_eeg_data_files_uploaded
                    ),
                    "number_of_emg_data_files_uploaded": number_of_emg_data_files_uploaded,
                    "total_of_emg_data_files": len(list_of_emg_configuration),
                    "percentage_of_emg_data_files_uploaded": int(
                        percentage_of_emg_data_files_uploaded
                    ),
                    "number_of_tms_data_files_uploaded": number_of_tms_data_files_uploaded,
                    "total_of_tms_data_files": len(list_of_tms_configuration),
                    "percentage_of_tms_data_files_uploaded": int(
                        percentage_of_tms_data_files_uploaded
                    ),
                    "number_of_digital_game_phase_data_files_uploaded": number_of_digital_game_phase_data_files_uploaded,
                    "total_of_digital_game_phase_data_files": len(
                        list_of_digital_game_phase_configuration
                    ),
                    "percentage_of_digital_game_phase_data_files_uploaded": int(
                        percentage_of_digital_game_phase_data_files_uploaded
                    ),
                    "number_of_generic_data_collection_data_files_uploaded": number_of_generic_data_collection_data_files_uploaded,
                    "total_of_generic_data_collection_data_files": len(
                        list_of_generic_data_collection_configuration
                    ),
                    "percentage_of_generic_data_collection_data_files_uploaded": int(
                        percentage_of_generic_data_collection_data_files_uploaded
                    ),
                    "number_of_media_collection_data_files_uploaded": number_of_media_collection_data_files_uploaded,
                    "total_of_media_collection_data_files": len(
                        list_of_media_collection_configuration
                    ),
                    "percentage_of_media_collection_data_files_uploaded": int(
                        percentage_of_media_collection_data_files_uploaded
                    ),
                    "number_of_additional_data_uploaded": AdditionalData.objects.filter(
                        subject_of_group=subject_of_group
                    ).count(),
                },
            )

    else:
        for subject_of_group in subject_list:
            subject_list_with_status.append(
                {
                    "subject": subject_of_group.subject,
                    "number_of_questionnaires_filled": 0,
                    "total_of_questionnaires": 0,
                    "percentage_of_questionnaires": 0,
                    "consent": subject_of_group.consent_form,
                    "number_of_additional_data_uploaded": AdditionalData.objects.filter(
                        subject_of_group=subject_of_group
                    ).count(),
                }
            )

    surveys.release_session_key()

    # info for tab 'per step of the experimental protocol'
    # First element of the list is associated to the whole experimental protocol
    # subject_step_data_query = \
    #     SubjectStepData.objects.filter(subject_of_group=subject_of_group, data_configuration_tree=None)
    data_collections = get_data_collections_from_group(group)

    if request.method == "POST":
        if request.POST["action"][:6] == "remove":
            if can_remove:
                get_object_or_404(
                    SubjectOfGroup, group=group, subject_id=subject_id
                ).delete()

                messages.info(request, _("Participant deleted from experiment."))
            else:
                messages.error(
                    request,
                    _(
                        "It was not possible to delete participant, "
                        "because there are answers or eeg data associated"
                    ),
                )

            redirect_url = reverse("subjects", args=(group_id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "subject_list": subject_list_with_status,
        "limesurvey_available": limesurvey_available,
        "experimental_protocol_info": experimental_protocol_info,
        "goalkeeper": goalkeeper,
        "data_collections": data_collections,
    }

    # to make per_steps_of_experimental_protocol tab active when redirected
    # from data_collection_management view in its post requests
    if request.method == "GET" and request.GET.get("per_steps_tab"):
        context["per_steps_tab_active"] = "active"

    return render(request, template_name, context)


def get_data_collections_from_group(group, data_type=None):
    data_collections = []

    if data_type is None or data_type == "additional_data":
        additional_data_list = AdditionalData.objects.filter(
            subject_of_group__group=group, data_configuration_tree=None
        )

        data_list = (
            [
                {
                    "type": "additional_data",
                    "icon_class": icon_class["additional_data"],
                    "description": _("Additional"),
                    "count": additional_data_list.values("subject_of_group__subject")
                    .distinct()
                    .count(),
                }
            ]
            if additional_data_list
            else []
        )
        data_collections.append(
            {
                "component_configuration": None,
                "path": None,
                "data_list": data_list,
                "icon_class": icon_class["experimental_protocol"],
            }
        )

    list_of_paths = create_list_of_trees(
        group.experimental_protocol,
        data_type if data_type and data_type != "additional_data" else None,
    )
    for path in list_of_paths:
        component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])
        data_configuration_tree_id = list_data_configuration_tree(
            component_configuration.id, [item[0] for item in path]
        )
        participant_quantity = (
            AdditionalData.objects.filter(
                subject_of_group__group=group,
                data_configuration_tree_id=data_configuration_tree_id,
            )
            .values("subject_of_group__subject")
            .distinct()
            .count()
            if data_type is None or data_type == "additional_data"
            else None
        )

        data_list = (
            [
                {
                    "type": "additional_data",
                    "icon_class": icon_class["additional_data"],
                    "description": _("Additional"),
                    "count": participant_quantity,
                }
            ]
            if participant_quantity
            else []
        )

        if component_configuration.component.component_type == "eeg":
            participant_quantity = (
                EEGData.objects.filter(
                    subject_of_group__group=group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                .values("subject_of_group__subject")
                .distinct()
                .count()
                if data_type is None or data_type == "eeg"
                else None
            )
            if participant_quantity:
                data_list.append(
                    {
                        "type": "eeg",
                        "icon_class": icon_class["eeg"],
                        "description": _("EEG"),
                        "count": participant_quantity,
                    }
                )
        elif component_configuration.component.component_type == "emg":
            participant_quantity = (
                EMGData.objects.filter(
                    subject_of_group__group=group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                .values("subject_of_group__subject")
                .distinct()
                .count()
                if data_type is None or data_type == "emg"
                else None
            )
            if participant_quantity:
                data_list.append(
                    {
                        "type": "emg",
                        "icon_class": icon_class["emg"],
                        "description": _("EMG"),
                        "count": participant_quantity,
                    }
                )
        elif component_configuration.component.component_type == "tms":
            participant_quantity = (
                TMSData.objects.filter(
                    subject_of_group__group=group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                .values("subject_of_group__subject")
                .distinct()
                .count()
                if data_type is None or data_type == "tms"
                else None
            )
            if participant_quantity:
                data_list.append(
                    {
                        "type": "tms",
                        "icon_class": icon_class["tms"],
                        "description": _("TMS"),
                        "count": participant_quantity,
                    }
                )
        elif component_configuration.component.component_type == "digital_game_phase":
            participant_quantity = (
                DigitalGamePhaseData.objects.filter(
                    subject_of_group__group=group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                .values("subject_of_group__subject")
                .distinct()
                .count()
                if data_type is None or data_type == "digital_game_phase"
                else None
            )
            if participant_quantity:
                data_list.append(
                    {
                        "type": "digital_game_phase",
                        "icon_class": icon_class["digital_game_phase"],
                        "description": _("Game"),
                        "count": participant_quantity,
                    }
                )
        elif (
            component_configuration.component.component_type
            == "generic_data_collection"
        ):
            participant_quantity = (
                GenericDataCollectionData.objects.filter(
                    subject_of_group__group=group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                .values("subject_of_group__subject")
                .distinct()
                .count()
                if data_type is None or data_type == "generic_data_collection"
                else None
            )
            if participant_quantity:
                data_list.append(
                    {
                        "type": "generic_data_collection",
                        "icon_class": icon_class["generic_data_collection"],
                        "description": _("Data collection"),
                        "count": participant_quantity,
                    }
                )
        elif component_configuration.component.component_type == "media_collection":
            participant_quantity = (
                MediaCollectionData.objects.filter(
                    subject_of_group__group=group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                .values("subject_of_group__subject")
                .distinct()
                .count()
                if data_type is None or data_type == "media_collection"
                else None
            )
            if participant_quantity:
                data_list.append(
                    {
                        "type": "media_collection",
                        "icon_class": icon_class["media_collection"],
                        "description": _("Data collection"),
                        "count": participant_quantity,
                    }
                )
        elif component_configuration.component.component_type == "questionnaire":
            participant_quantity = (
                QuestionnaireResponse.objects.filter(
                    subject_of_group__group=group,
                    data_configuration_tree_id=data_configuration_tree_id,
                )
                .values("subject_of_group__subject")
                .distinct()
                .count()
                if data_type is None or data_type == "questionnaire"
                else None
            )
            if participant_quantity:
                data_list.append(
                    {
                        "type": "questionnaire",
                        "icon_class": icon_class["questionnaire"],
                        "description": _("Response"),
                        "count": participant_quantity,
                    }
                )

        data_collections.append(
            {
                "component_configuration": component_configuration,
                "path": path,
                "data_list": data_list,
                "icon_class": icon_class[
                    component_configuration.component.component_type
                ],
            }
        )
    return data_collections


@login_required
@permission_required("experiment.view_researchproject")
def search_subjects(request, group_id, template_name="experiment/search_subjects.html"):
    experimental_protocol_info = {
        "number_of_questionnaires": 0,
        "number_of_eeg_data": 0,
        "number_of_emg_data": 0,
        "number_of_tms_data": 0,
    }

    group = get_object_or_404(Group, id=group_id)

    subject_id = None

    participant_selection_form = ParticipantsSelectionForm(None)
    age_interval_form = AgeIntervalForm(None)

    if request.method == "POST":
        patient_list = []
        if request.POST["action"] == "next-step-1":
            subject_group_list = SubjectOfGroup.objects.filter(group=group)
            for subject in subject_group_list:
                patient_list.append(subject.subject.patient.id)

            participants_list = Patient.objects.filter(removed=False)

            # selecting participants according the study/experiment/group
            if "study_selected_list" in request.session:
                subject_list = []
                study_selected_list = request.session["study_selected_list"][0]
                for study in study_selected_list:
                    group_id = study.split("-")[2]
                    subject_of_group = SubjectOfGroup.objects.filter(group_id=group_id)

                    for subject in subject_of_group:
                        patient = subject.subject.patient
                        if patient.id not in subject_list:
                            subject_list.append(patient.id)

                participants_list = participants_list.filter(pk__in=subject_list)

            if request.POST["type_of_selection_radio"] == "selected":
                # selecting participants according the filters
                if "gender_checkbox" in request.POST and "gender" in request.POST:
                    gender_list = request.POST.getlist("gender")
                    participants_list = participants_list.filter(
                        gender__id__in=gender_list
                    )

                if (
                    "marital_status_checkbox" in request.POST
                    and "marital_status" in request.POST
                ):
                    marital_status_list = request.POST.getlist("marital_status")
                    participants_list = participants_list.filter(
                        marital_status__id__in=marital_status_list
                    )

                if (
                    "age_checkbox" in request.POST
                    and "max_age" in request.POST
                    and "min_age" in request.POST
                ):
                    date_birth_min = datetime.now() - relativedelta(
                        years=int(request.POST["max_age"])
                    )
                    date_birth_max = datetime.now() - relativedelta(
                        years=int(request.POST["min_age"])
                    )
                    participants_list = participants_list.filter(
                        date_birth__range=(date_birth_min, date_birth_max)
                    )

                if "location_checkbox" in request.POST:
                    if "selected_locals" in request.POST:
                        locations_selected = request.POST.getlist("selected_locals")
                        participants_list = participants_list.filter(
                            city__in=locations_selected
                        )

                if "diagnosis_checkbox" in request.POST:
                    classification_of_diseases_list = request.POST.getlist(
                        "selected_diagnoses"
                    )

                    participants_list = participants_list.filter(
                        medicalrecorddata__diagnosis__classification_of_diseases__in=classification_of_diseases_list
                    ).distinct()

            # participants that not is in group
            filtered_participants_list = [
                item for item in participants_list if item.id not in patient_list
            ]
            participants_list = []
            participants_list = filtered_participants_list

            # putting the list of participants in the user session
            request.session["filtered_participant_data"] = [
                item.id for item in participants_list
            ]

            context = {
                "total_of_participants": len(participants_list),
                "participants_list": participants_list,
                "group": group,
            }
            return render(
                request, "experiment/show_selected_participants.html", context
            )

        if request.POST["action"] == "previous-step-2":
            context = {
                "participant_selection_form": participant_selection_form,
                "age_interval_form": age_interval_form,
                "group": group,
            }

            return render(request, "experiment/search_subjects.html", context)

        if request.POST["action"] == "next-step-2":
            participants_list = request.session["filtered_participant_data"]
            for participant in participants_list:
                patient = get_object_or_404(Patient, pk=participant)

                subject = Subject()

                try:
                    subject = Subject.objects.get(patient=patient)
                except subject.DoesNotExist:
                    subject.patient = patient
                    subject.save()

                if not SubjectOfGroup.objects.all().filter(
                    group=group, subject=subject
                ):
                    SubjectOfGroup(subject=subject, group=group).save()
                else:
                    messages.warning(
                        request,
                        _("Participant has already been inserted in this group."),
                    )

            redirect_url = reverse("subjects", args=(group_id,))
            return HttpResponseRedirect(redirect_url)

        if request.POST["action"][:7] == "remove-":
            action_parts = request.POST["action"].split(delimiter)
            participants_list = request.session["filtered_participant_data"]
            participants_list.remove(int(action_parts[1]))
            participants_list = Patient.objects.filter(pk__in=participants_list)

            context = {
                "total_of_participants": len(participants_list),
                "participants_list": participants_list,
                "group": group,
            }
            return render(
                request, "experiment/show_selected_participants.html", context
            )

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "subject_id": subject_id,
        "experimental_protocol_info": experimental_protocol_info,
        "participant_selection_form": participant_selection_form,
        "age_interval_form": age_interval_form,
    }

    return render(request, template_name, context)


def subject_questionnaire_response_start_fill_questionnaire(
    request, subject_id, group_id, questionnaire_id, list_of_path
):
    questionnaire_response_form = QuestionnaireResponseForm(request.POST)

    data_configuration_tree_id = list_data_configuration_tree(
        questionnaire_id, list_of_path
    )
    if not data_configuration_tree_id:
        data_configuration_tree_id = create_data_configuration_tree(list_of_path)

    if questionnaire_response_form.is_valid():
        questionnaire_response = questionnaire_response_form.save(commit=False)
        questionnaire_config = get_object_or_404(
            ComponentConfiguration, id=questionnaire_id
        )
        questionnaire_lime_survey = Questionnaires()
        subject = get_object_or_404(Subject, pk=subject_id)
        subject_of_group = get_object_or_404(
            SubjectOfGroup, subject=subject, group_id=group_id
        )
        lime_survey_id = Questionnaire.objects.get(
            id=questionnaire_config.component_id
        ).survey.lime_survey_id

        if not questionnaire_lime_survey.survey_has_token_table(lime_survey_id):
            messages.warning(
                request, _("Fill not available - Table of tokens was not started.")
            )
            return None, None

        if (
            questionnaire_lime_survey.get_survey_properties(lime_survey_id, "active")
            == "N"
        ):
            messages.warning(
                request, _("Fill not available - Questionnaire is not activated.")
            )
            return None, None

        if not check_required_fields(questionnaire_lime_survey, lime_survey_id):
            messages.warning(
                request,
                _(
                    "Fill not available - Questionnaire does not contain "
                    "standard fields."
                ),
            )
            return None, None

        result = questionnaire_lime_survey.add_participant(lime_survey_id)

        questionnaire_lime_survey.release_session_key()

        if not result:
            messages.warning(
                request,
                _(
                    "Fail trying to generate token to answer questionnaire. "
                    "Check if questionnaire is active."
                ),
            )
            return None, None

        questionnaire_response.data_configuration_tree_id = data_configuration_tree_id
        questionnaire_response.subject_of_group = subject_of_group
        questionnaire_response.component_configuration = questionnaire_config
        questionnaire_response.token_id = result["tid"]
        questionnaire_response.questionnaire_responsible = request.user
        questionnaire_response.save()

        redirect_url = get_limesurvey_response_url(questionnaire_response)

        return redirect_url, questionnaire_response.pk
    else:
        return None, None


def get_limesurvey_response_url(questionnaire_response):
    survey_component = (
        questionnaire_response.data_configuration_tree.component_configuration.component
    )
    questionnaire = Questionnaire.objects.get(id=survey_component.id)

    questionnaire_lime_survey = Questionnaires()
    token = questionnaire_lime_survey.get_participant_properties(
        questionnaire.survey.lime_survey_id, questionnaire_response.token_id, "token"
    )

    questionnaire_lime_survey.release_session_key()

    redirect_url = (
        "%s/index.php/%s/token/%s/responsibleid/%s/"
        "acquisitiondate/%s/subjectid/%s/newtest/Y"
        % (
            settings.LIMESURVEY["URL_WEB"],
            questionnaire.survey.lime_survey_id,
            token,
            str(questionnaire_response.questionnaire_responsible.id),
            questionnaire_response.date.strftime("%m-%d-%Y"),
            str(questionnaire_response.subject_of_group.subject.patient.id),
        )
    )

    return redirect_url


@login_required
@permission_required("experiment.add_questionnaireresponse")
def subject_questionnaire_response_create(
    request,
    group_id,
    subject_id,
    questionnaire_id,
    template_name="experiment/subject_questionnaire_response_form.html",
):
    group = get_object_or_404(Group, id=group_id)

    list_of_path = [int(item) for item in questionnaire_id.split("-")]
    questionnaire_id = list_of_path[-1]

    check_can_change(request.user, group.experiment.research_project)

    questionnaire_config = get_object_or_404(
        ComponentConfiguration, id=questionnaire_id
    )
    surveys = Questionnaires()
    survey = Questionnaire.objects.get(id=questionnaire_config.component_id).survey

    survey_title = find_questionnaire_name(survey, request.LANGUAGE_CODE)["name"]
    surveys.release_session_key()

    fail = None
    redirect_url = None
    questionnaire_response_id = None

    questionnaire_response_form = QuestionnaireResponseForm(request.POST or None)

    if request.method == "POST":
        if request.POST.get("action") == "save":
            (
                redirect_url,
                questionnaire_response_id,
            ) = subject_questionnaire_response_start_fill_questionnaire(
                request, subject_id, group_id, questionnaire_id, list_of_path
            )

        if request.POST.get("action") == "send_invite":
            subject = Subject.objects.get(pk=subject_id)
            if subject.patient.email is None:
                messages.warning(
                    request,
                    _("Could not send email to")
                    + " "
                    + subject.patient.name
                    + ". "
                    + _(
                        "Patient has not email registered. Please "
                        "register an email for her/him"
                    )
                    + ".",
                )
            else:
                (
                    redirect_url,
                    questionnaire_response_id,
                ) = subject_questionnaire_response_start_fill_questionnaire(
                    request, subject_id, group_id, questionnaire_id, list_of_path
                )

                # TODO: self.update_questionnaire_response()
                questionnaire_response = QuestionnaireResponse.objects.get(
                    pk=questionnaire_response_id
                )
                questionnaire_response.is_completed = "invited"
                questionnaire_response.save()
                send_mail(
                    _("Your link to respond the questionnaire"),
                    redirect_url,
                    "noreply@nes.numec.prp.usp.br",
                    [subject.patient.email],
                )
                messages.success(
                    request,
                    _("Email sent successfully to") + " " + subject.patient.name,
                )

            return HttpResponseRedirect(
                reverse(
                    "questionnaire_view",
                    kwargs={
                        "group_id": group_id,
                        "component_configuration_id": questionnaire_id,
                    },
                )
            )

        fail = True if not redirect_url else False

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


@login_required
@permission_required("experiment.add_questionnaireresponse")
def subject_questionnaire_response_reuse(
    request, group_id, subject_id, questionnaire_id, patient_questionnaire_response_id
):
    group = get_object_or_404(Group, id=group_id)

    list_of_path = [int(item) for item in questionnaire_id.split("-")]
    questionnaire_id = list_of_path[-1]

    check_can_change(request.user, group.experiment.research_project)

    patient_questionnaire_response = get_object_or_404(
        PatientQuestionnaireResponse, id=patient_questionnaire_response_id
    )

    data_configuration_tree_id = list_data_configuration_tree(
        questionnaire_id, list_of_path
    )
    if not data_configuration_tree_id:
        data_configuration_tree_id = create_data_configuration_tree(list_of_path)

    subject = get_object_or_404(Subject, pk=subject_id)
    subject_of_group = get_object_or_404(
        SubjectOfGroup, subject=subject, group_id=group_id
    )

    questionnaire_response = QuestionnaireResponse.objects.create(
        token_id=patient_questionnaire_response.token_id,
        questionnaire_responsible=patient_questionnaire_response.questionnaire_responsible,
        data_configuration_tree_id=data_configuration_tree_id,
        subject_of_group=subject_of_group,
        date=patient_questionnaire_response.date,
    )
    questionnaire_response.save()

    messages.success(request, _("Fill reused successfully."))

    redirect_url = reverse(
        "subject_questionnaire",
        args=(
            group.id,
            subject.id,
        ),
    )

    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.change_questionnaireresponse")
def questionnaire_response_edit(
    request,
    questionnaire_response_id,
    template_name="experiment/subject_questionnaire_response_form.html",
):
    questionnaire_response = get_object_or_404(
        QuestionnaireResponse, id=questionnaire_response_id
    )
    questionnaire = Questionnaire.objects.get(
        id=questionnaire_response.data_configuration_tree.component_configuration.component.id
    )
    group = questionnaire_response.subject_of_group.group
    subject = questionnaire_response.subject_of_group.subject

    surveys = Questionnaires()

    survey_title = find_questionnaire_name(questionnaire.survey, request.LANGUAGE_CODE)[
        "name"
    ]
    if (
        questionnaire_response.is_completed == "N"
        or questionnaire_response.is_completed == ""
    ):
        is_completed = (
            surveys.get_participant_properties(
                questionnaire.survey.lime_survey_id,
                questionnaire_response.token_id,
                "completed",
            )
            or ""
        )
        questionnaire_response.is_completed = is_completed
        questionnaire_response.save()
    survey_completed = questionnaire_response.is_completed != "N"
    surveys.release_session_key()

    questionnaire_response_form = QuestionnaireResponseForm(
        None, instance=questionnaire_response
    )

    fail = None
    redirect_url = None

    origin = get_origin(request)

    if request.method == "POST":
        check_can_change(request.user, group.experiment.research_project)

        if request.POST["action"] == "save":
            redirect_url = get_limesurvey_response_url(questionnaire_response)

            if not redirect_url:
                fail = True
            else:
                fail = False
                messages.info(
                    request, _("You will be redirected to questionnaire. Please wait.")
                )

        elif request.POST["action"] == "remove":
            if request.user.has_perm("experiment.delete_questionnaireresponse"):
                can_delete = False

                token_is_used_patient_questionnaire_response = (
                    PatientQuestionnaireResponse.objects.filter(
                        patient=subject.patient,
                        survey=questionnaire.survey,
                        token_id=questionnaire_response.token_id,
                    ).exists()
                )

                if token_is_used_patient_questionnaire_response:
                    can_delete = True
                else:
                    # remove token from Limesurvey
                    surveys = Questionnaires()
                    result = surveys.delete_participants(
                        questionnaire.survey.lime_survey_id,
                        [questionnaire_response.token_id],
                    )
                    surveys.release_session_key()

                    if str(questionnaire_response.token_id) in result:
                        result = result[str(questionnaire_response.token_id)]
                        if result == "Deleted" or result == "Invalid token ID":
                            can_delete = True
                    else:
                        if (
                            "status" in result
                            and result["status"] == "Error: Invalid survey ID"
                        ):
                            can_delete = True

                if can_delete:
                    questionnaire_response.delete()
                    messages.success(request, _("Fill deleted successfully."))
                else:
                    messages.error(request, _("Error trying to delete fill"))

                if origin == "experiment_subject":
                    redirect_url = reverse(
                        "subject_questionnaire",
                        args=(
                            group.id,
                            subject.id,
                        ),
                    )
                else:
                    redirect_url = reverse(
                        "questionnaire_view",
                        args=(
                            group.id,
                            questionnaire_response.data_configuration_tree.component_configuration.id,
                        ),
                    )

                return HttpResponseRedirect(redirect_url)
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
    origin = "0"

    # origin is in request.GET also when the request is a post!
    if "origin" in request.GET:
        origin = request.GET["origin"]

    return origin


def get_position(request):
    position = None

    # position is in request.GET also when the request is a post!
    if "position" in request.GET:
        position = request.GET["position"]

    return position


def get_number_of_uses(request):
    number_of_uses = 1

    # number_of_uses is in request.GET also when the request is a post!
    if "number_of_uses" in request.GET:
        number_of_uses = request.GET["number_of_uses"]

    return number_of_uses


def check_required_fields(surveys, lime_survey_id):
    """Verify if questionnaire have the identification questions
    and if question types are correct
    """

    fields_to_validate = {
        "responsibleid": {"type": "N", "found": False},
        "acquisitiondate": {"type": "D", "found": False},
        "subjectid": {"type": "N", "found": False},
    }

    validated_quantity = 0
    error = False

    groups = surveys.list_groups(lime_survey_id)

    if "status" not in groups:
        for group in groups:
            question_list = surveys.list_questions_ids(
                lime_survey_id, group["id"]["gid"]
            )
            for question in question_list:
                question_properties = surveys.get_question_properties(question, None)
                if question_properties["title"] in fields_to_validate:
                    field = fields_to_validate[question_properties["title"]]
                    if not field["found"]:
                        field["found"] = True
                        if field["type"] == question_properties["type"]:
                            validated_quantity += 1
                        else:
                            error = True
                if error or validated_quantity == len(fields_to_validate):
                    break
            if error or validated_quantity == len(fields_to_validate):
                break

    return validated_quantity == len(fields_to_validate)


@login_required
@permission_required("experiment.view_questionnaireresponse")
def questionnaire_response_view(
    request,
    questionnaire_response_id,
    template_name="experiment/subject_questionnaire_response_form.html",
):
    questionnaire_response = get_object_or_404(
        QuestionnaireResponse, id=questionnaire_response_id
    )
    questionnaire = Questionnaire.objects.get(
        id=questionnaire_response.data_configuration_tree.component_configuration.component.id
    )
    group = questionnaire_response.subject_of_group.group
    subject = questionnaire_response.subject_of_group.subject

    survey_completed = questionnaire_response.is_completed != "N"

    questionnaire_response_form = QuestionnaireResponseForm(
        None, instance=questionnaire_response
    )

    limesurvey_id = questionnaire.survey.lime_survey_id
    token_id = questionnaire_response.token_id
    language_code = request.LANGUAGE_CODE

    survey_title_key = (
        request.LANGUAGE_CODE
        + "-"
        + str(limesurvey_id)
        + "-"
        + str(token_id)
        + "_survey_title"
    )
    groups_of_questions_key = (
        request.LANGUAGE_CODE
        + "-"
        + str(limesurvey_id)
        + "-"
        + str(token_id)
        + "_group_of_questions"
    )

    # TODO (NES-991): BROKEN! Made a test and fix this before close this issue.
    #  Before that we are putting a generic exception
    try:
        survey_title = cache.get(survey_title_key)
        groups_of_questions = cache.get(groups_of_questions_key)
    except:
        survey_title = None
        groups_of_questions = None

    if not survey_title and not groups_of_questions:
        # Get the responses for each question of the questionnaire.
        survey_title, groups_of_questions = get_questionnaire_responses(
            language_code, limesurvey_id, token_id, request
        )

        # TODO (NES-991): see BROKEN! above
        # cache.set(survey_title_key, survey_title)
        # cache.set(groups_of_questions_key, groups_of_questions)

    origin = get_origin(request)

    if request.method == "POST":
        check_can_change(request.user, group.experiment.research_project)

        if request.POST["action"] == "remove":
            if request.user.has_perm("experiment.delete_questionnaireresponse"):
                deleted = delete_questionnaire_response(
                    questionnaire, questionnaire_response
                )

                if deleted:
                    messages.success(request, _("Fill deleted successfully."))
                else:
                    messages.error(request, _("Error trying to delete fill"))

                if origin == "experiment_subject":
                    redirect_url = reverse(
                        "subject_questionnaire",
                        args=(
                            group.id,
                            subject.id,
                        ),
                    )
                else:
                    redirect_url = reverse(
                        "questionnaire_view",
                        args=(
                            group.id,
                            questionnaire_response.component_configuration.id,
                        ),
                    )

                return HttpResponseRedirect(redirect_url)
            else:
                raise PermissionDenied

    status = ""
    if "status" in request.GET:
        status = request.GET["status"]

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
        "groups_of_questions": groups_of_questions,
        "questionnaire_responsible": questionnaire_response.questionnaire_responsible,
        "patient": subject.patient,  # This is needed when origin=subject
        "status": status,
        "subject": subject,
        "survey_title": survey_title,
    }

    return render(request, template_name, context)


def delete_questionnaire_response(
    questionnaire: Questionnaire, questionnaire_response: QuestionnaireResponse
):
    # Checking if it is used by patient_questionnaire_response
    token_is_used_patient_questionnaire_response = (
        PatientQuestionnaireResponse.objects.filter(
            patient=questionnaire_response.subject_of_group.subject.patient,
            survey=questionnaire.survey,
            token_id=questionnaire_response.token_id,
        ).exists()
    )
    can_delete = False
    if token_is_used_patient_questionnaire_response:
        can_delete = True
    else:
        # Remove token from LimeSurvey
        surveys = Questionnaires()
        result = surveys.delete_participants(
            questionnaire.survey.lime_survey_id, [questionnaire_response.token_id]
        )
        surveys.release_session_key()

        if str(questionnaire_response.token_id) in result:
            result = result[str(questionnaire_response.token_id)]
            if result == "Deleted" or result == "Invalid token ID":
                can_delete = True
        else:
            if "status" in result and result["status"] == "Error: Invalid survey ID":
                can_delete = True
    if can_delete:
        questionnaire_response.delete()
        deleted = True
    return deleted


@login_required
@permission_required("experiment.view_researchproject")
def subject_questionnaire_view(
    request,
    group_id,
    subject_id,
    template_name="experiment/subject_questionnaire_response_list.html",
):
    subject_questionnaires = []
    surveys = Questionnaires()
    subject_of_group = get_object_or_404(
        SubjectOfGroup, group_id=group_id, subject_id=subject_id
    )

    list_of_trees = create_list_of_trees(
        subject_of_group.group.experimental_protocol, "questionnaire"
    )

    used_tokens = {}

    for path in list_of_trees:
        questionnaire_configuration = get_object_or_404(
            ComponentConfiguration, pk=path[-1][0]
        )

        # Questionnaire Responses (in the experiment)
        data_configuration_tree_id = list_data_configuration_tree(
            questionnaire_configuration.id, [item[0] for item in path]
        )
        questionnaire_responses = QuestionnaireResponse.objects.filter(
            subject_of_group=subject_of_group,
            data_configuration_tree__id=data_configuration_tree_id,
        )

        questionnaire = Questionnaire.objects.get(
            id=questionnaire_configuration.component.id
        )
        language = get_questionnaire_language(
            surveys, questionnaire.survey.lime_survey_id, request.LANGUAGE_CODE
        )

        questionnaire_responses_with_status = []
        for questionnaire_response in questionnaire_responses:
            properties = surveys.get_participant_properties(
                questionnaire.survey.lime_survey_id, questionnaire_response.token_id
            )
            update_completed_status(
                questionnaire.survey.lime_survey_id,
                properties["completed"],
                questionnaire_response,
            )
            acquisitiondate_updated = update_acquisition_date(
                questionnaire.survey.lime_survey_id,
                properties["token"],
                questionnaire_response,
                language,
            )
            questionnaire_responses_with_status.append(
                {
                    "questionnaire_response": questionnaire_response,
                    "completed": None
                    if questionnaire_response.is_completed is None
                    else questionnaire_response.is_completed != "N"
                    and questionnaire_response.is_completed != "",
                    "acquisitiondate_updated": acquisitiondate_updated,
                }
            )

            # saving used tokens by questionnaire
            if questionnaire.survey.lime_survey_id not in used_tokens:
                used_tokens[questionnaire.survey.lime_survey_id] = [
                    questionnaire_response.token_id
                ]
            else:
                if (
                    questionnaire_response.token_id
                    not in used_tokens[questionnaire.survey.lime_survey_id]
                ):
                    used_tokens[questionnaire.survey.lime_survey_id].append(
                        questionnaire_response.token_id
                    )

        # saving information about the step
        subject_questionnaires.append(
            {
                "questionnaire_configuration": questionnaire_configuration,
                "questionnaire": questionnaire,
                "title": find_questionnaire_name(
                    questionnaire.survey, request.LANGUAGE_CODE
                )["name"],
                "path": path,
                "questionnaire_responses": questionnaire_responses_with_status,
            }
        )

    # Responses that could be reused
    for subject_questionnaire in subject_questionnaires:
        questionnaire = subject_questionnaire["questionnaire"]

        tokens_already_used = (
            used_tokens[questionnaire.survey.lime_survey_id]
            if questionnaire.survey.lime_survey_id in used_tokens
            else []
        )

        patient_questionnaire_responses = PatientQuestionnaireResponse.objects.filter(
            patient=subject_of_group.subject.patient, survey=questionnaire.survey
        ).exclude(token_id__in=tokens_already_used)
        patient_questionnaire_responses_with_status = []
        for questionnaire_response in patient_questionnaire_responses:
            properties = surveys.get_participant_properties(
                questionnaire.survey.lime_survey_id, questionnaire_response.token_id
            )
            update_completed_status(
                questionnaire.survey.lime_survey_id,
                properties["completed"],
                questionnaire_response,
            )

            if (
                questionnaire_response.is_completed is not None
                and questionnaire_response.is_completed != ""
            ):
                patient_questionnaire_responses_with_status.append(
                    {
                        "patient_questionnaire_response": questionnaire_response,
                        "completed": True
                        if questionnaire_response.is_completed != "N"
                        else False,
                    }
                )
        subject_questionnaire[
            "patient_questionnaire_responses"
        ] = patient_questionnaire_responses_with_status

    surveys.release_session_key()

    return render(
        request,
        template_name,
        {
            "can_change": get_can_change(
                request.user, subject_of_group.group.experiment.research_project
            ),
            "group": subject_of_group.group,
            "limesurvey_available": check_limesurvey_access(request, surveys),
            "subject": subject_of_group.subject,
            "subject_questionnaires": subject_questionnaires,
        },
    )


@login_required
@permission_required("experiment.view_researchproject")
def load_questionnaire_data(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    number_of_imported_data = 0
    list_of_paths = create_list_of_trees(group.experimental_protocol, "questionnaire")

    reused_tokens = {}
    # first loop: knowing tokens that was already reused
    for path_ in list_of_paths:
        questionnaire_configuration = ComponentConfiguration.objects.get(
            pk=path_[-1][0]
        )
        questionnaire_responses = QuestionnaireResponse.objects.filter(
            data_configuration_tree__component_configuration=questionnaire_configuration
        )
        for questionnaire_response in questionnaire_responses:
            questionnaire = get_object_or_404(
                Questionnaire,
                pk=questionnaire_response.data_configuration_tree.component_configuration.component_id,
            )

            # saving used tokens by questionnaire
            update_list_of_reused_tokens(
                questionnaire_response, questionnaire, reused_tokens
            )

    # main loop: importing
    for path_ in list_of_paths:
        questionnaire_configuration = ComponentConfiguration.objects.get(
            pk=path_[-1][0]
        )

        data_configuration_tree_id = list_data_configuration_tree(
            questionnaire_configuration.id, [item[0] for item in path_]
        )

        if not data_configuration_tree_id:
            data_configuration_tree_id = create_data_configuration_tree(
                [item[0] for item in path_]
            )

        data_configuration_tree = get_object_or_404(
            DataConfigurationTree, pk=data_configuration_tree_id
        )

        questionnaire = get_object_or_404(
            Questionnaire, pk=questionnaire_configuration.component_id
        )

        # for each subject
        for subject_of_group in group.subjectofgroup_set.all():
            tokens_already_reused = (
                reused_tokens[questionnaire.survey.lime_survey_id]
                if questionnaire.survey.lime_survey_id in reused_tokens
                else []
            )

            # getting patient-questionnaire-response
            patient_questionnaire_responses = (
                PatientQuestionnaireResponse.objects.filter(
                    patient=subject_of_group.subject.patient,
                    survey=questionnaire.survey,
                ).exclude(token_id__in=tokens_already_reused)
            )

            # check if there is response in patient-questionnaire-response to reuse
            if patient_questionnaire_responses:
                # when configured with 1 repetition, check if there is just one response
                if (
                    questionnaire_configuration.number_of_repetitions == 1
                    and len(patient_questionnaire_responses) == 1
                ):
                    # check if there is no response for this "subject + step"
                    if not QuestionnaireResponse.objects.filter(
                        subject_of_group=subject_of_group,
                        data_configuration_tree=data_configuration_tree,
                    ).exists():
                        # getting the response to reuse
                        patient_questionnaire_response = (
                            patient_questionnaire_responses[0]
                        )

                        # reuse the response
                        new_questionnaire_response = reuse_questionnaire_response(
                            data_configuration_tree_id,
                            patient_questionnaire_response,
                            subject_of_group,
                        )

                        # update list of reused tokens
                        update_list_of_reused_tokens(
                            new_questionnaire_response, questionnaire, reused_tokens
                        )

                        # increments number of imported data
                        number_of_imported_data += 1

                # when configured with unlimited responses, iterate all responses
                if questionnaire_configuration.number_of_repetitions is None:
                    for (
                        patient_questionnaire_response
                    ) in patient_questionnaire_responses:
                        new_questionnaire_response = reuse_questionnaire_response(
                            data_configuration_tree_id,
                            patient_questionnaire_response,
                            subject_of_group,
                        )

                        # increments number of imported data
                        number_of_imported_data += 1

                        # update list of reused tokens
                        update_list_of_reused_tokens(
                            new_questionnaire_response, questionnaire, reused_tokens
                        )

    if number_of_imported_data:
        if number_of_imported_data == 1:
            messages.success(request, _("1 new response was imported."))
        else:
            messages.success(
                request,
                _("%s new responses were imported.") % (str(number_of_imported_data)),
            )
    else:
        messages.info(request, _("No new data loaded."))

    redirect_url = reverse("subjects", args=(group_id,))
    return HttpResponseRedirect(redirect_url)


def update_list_of_reused_tokens(
    new_questionnaire_response, questionnaire, reused_tokens
):
    if questionnaire.survey.lime_survey_id not in reused_tokens:
        reused_tokens[questionnaire.survey.lime_survey_id] = [
            new_questionnaire_response.token_id
        ]
    else:
        if (
            new_questionnaire_response.token_id
            not in reused_tokens[questionnaire.survey.lime_survey_id]
        ):
            reused_tokens[questionnaire.survey.lime_survey_id].append(
                new_questionnaire_response.token_id
            )


def reuse_questionnaire_response(
    data_configuration_tree_id, patient_questionnaire_response, subject_of_group
):
    new_questionnaire_response = QuestionnaireResponse.objects.create(
        token_id=patient_questionnaire_response.token_id,
        questionnaire_responsible=patient_questionnaire_response.questionnaire_responsible,
        data_configuration_tree_id=data_configuration_tree_id,
        subject_of_group=subject_of_group,
        date=patient_questionnaire_response.date,
    )
    new_questionnaire_response.save()
    return new_questionnaire_response


@login_required
@permission_required("experiment.view_researchproject")
def subject_eeg_view(
    request,
    group_id,
    subject_id,
    template_name="experiment/subject_eeg_collection_list.html",
):
    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)

    eeg_collections = []

    list_of_paths = create_list_of_trees(group.experimental_protocol, "eeg")

    subject_of_group = get_object_or_404(SubjectOfGroup, group=group, subject=subject)

    for path in list_of_paths:
        eeg_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])

        data_configuration_tree_id = list_data_configuration_tree(
            eeg_configuration.id, [item[0] for item in path]
        )

        eeg_data_list = EEGData.objects.filter(
            subject_of_group=subject_of_group,
            data_configuration_tree__id=data_configuration_tree_id,
        )

        for eeg_data in eeg_data_list:
            eeg_data.eeg_file_list = []
            for eeg_file in eeg_data.eeg_files.all():
                eeg_file.eeg_reading = eeg_data_reading(eeg_file, preload=False)
                eeg_file.can_export_to_nwb = False

                # v1.5
                # can export to nwb?
                if eeg_file.eeg_reading.file_format and eeg_file.eeg_reading.reading:
                    if (
                        eeg_file.eeg_reading.file_format.nes_code == "MNE-RawFromEGI"
                        and hasattr(eeg_data.eeg_setting, "eeg_amplifier_setting")
                        and eeg_data.eeg_setting.eeg_amplifier_setting.number_of_channels_used
                        and eeg_data.eeg_setting.eeg_amplifier_setting.number_of_channels_used
                        == len(
                            mne.pick_types(eeg_file.eeg_reading.reading.info, eeg=True)
                        )
                    ):
                        eeg_file.can_export_to_nwb = True

                eeg_data.eeg_file_list.append(eeg_file)

        eeg_collections.append(
            {
                "eeg_configuration": eeg_configuration,
                "path": path,
                "eeg_data_list": eeg_data_list,
            }
        )

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "subject": subject,
        "eeg_collections": eeg_collections,
        "process_requisition": int(random.random() * 10000),
    }

    return render(request, template_name, context)


def file_format_code(tag=""):
    """

    :return: List of dicts. Each dict contains information about a file format.
    """
    if tag:
        file_format = FileFormat.objects.filter(tags__name=tag).distinct()
    else:
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
        new_path = DataConfigurationTree.objects.create(
            component_configuration_id=item, parent_id=parent
        )
        new_path.save()
        parent = new_path.id
        data_configuration_tree_id = parent

    return data_configuration_tree_id


def list_data_configuration_tree(eeg_configuration_id, list_of_path):
    data_configuration_tree = DataConfigurationTree.objects.filter(
        component_configuration_id=eeg_configuration_id
    )
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
@permission_required("experiment.add_questionnaireresponse")
def subject_eeg_data_create(
    request,
    group_id,
    subject_id,
    eeg_configuration_id,
    template_name="experiment/subject_eeg_data_form.html",
):
    subject_of_group = get_object_or_404(
        SubjectOfGroup, subject_id=subject_id, group_id=group_id
    )

    list_of_path = [int(item) for item in eeg_configuration_id.split("-")]
    eeg_configuration_id = list_of_path[-1]

    check_can_change(request.user, subject_of_group.group.experiment.research_project)

    eeg_configuration = get_object_or_404(
        ComponentConfiguration, id=eeg_configuration_id
    )
    eeg_step = get_object_or_404(EEG, id=eeg_configuration.component_id)

    redirect_url = None

    eeg_data_form = EEGDataForm(
        None,
        initial={
            "experiment": subject_of_group.group.experiment,
            "eeg_setting": eeg_step.eeg_setting_id,
        },
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            eeg_data_form = EEGDataForm(request.POST, request.FILES)

            if eeg_data_form.is_valid():
                data_configuration_tree_id = list_data_configuration_tree(
                    eeg_configuration_id, list_of_path
                )
                if not data_configuration_tree_id:
                    data_configuration_tree_id = create_data_configuration_tree(
                        list_of_path
                    )

                eeg_data_added = eeg_data_form.save(commit=False)
                eeg_data_added.subject_of_group = subject_of_group
                eeg_data_added.component_configuration = eeg_configuration
                eeg_data_added.data_configuration_tree_id = data_configuration_tree_id

                # PS: it was necessary adding these 2 lines because Django raised, I do not why (Evandro),
                # the following error 'EEGData' object has no attribute 'group'
                eeg_data_added.group = subject_of_group.group
                eeg_data_added.subject = subject_of_group.subject

                eeg_data_added.save()

                # saving uploaded files
                files_to_upload_list = request.FILES.getlist("eeg_files")
                for file_to_upload in files_to_upload_list:
                    eeg_file = EEGFile(eeg_data=eeg_data_added, file=file_to_upload)
                    eeg_file.save()

                # creating position status
                if hasattr(eeg_data_added.eeg_setting, "eeg_electrode_layout_setting"):
                    eeg_electrode_layout_setting = (
                        eeg_data_added.eeg_setting.eeg_electrode_layout_setting
                    )

                    for (
                        position_setting
                    ) in eeg_electrode_layout_setting.positions_setting.all():
                        EEGElectrodePositionCollectionStatus(
                            worked=position_setting.used,
                            eeg_data=eeg_data_added,
                            eeg_electrode_position_setting=position_setting,
                            channel_index=position_setting.channel_index,
                        ).save()

                messages.success(
                    request, _("EEG data collection created successfully.")
                )
                messages.info(
                    request, _("Now you can configure each electrode position")
                )

                redirect_url = reverse("eeg_data_view", args=(eeg_data_added.id, 1))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "creating": True,
        "editing": True,
        "group": subject_of_group.group,
        "eeg_configuration": eeg_configuration,
        "eeg_data_form": eeg_data_form,
        "file_format_list": file_format_code("EEG"),
        "eeg_setting_default_id": eeg_step.eeg_setting_id,
        "subject": get_object_or_404(Subject, pk=subject_id),
        "URL": redirect_url,
        "tab": "1",
    }

    return render(request, template_name, context)


# v1.5
def get_sensors_position(eeg_data):
    # Electrode localization image generation. Validate if EGI
    reading = None
    file_path = None

    # Getting the eeg_file, if exists
    eeg_files = eeg_data.eeg_files.all()

    if len(eeg_files) == 1:
        for eeg_file in eeg_files:
            nes_code = eeg_file.eeg_data.file_format.nes_code
            if nes_code == "MNE-RawFromEGI":
                reading = eeg_data_reading(eeg_file, preload=False)
    elif len(eeg_files) == 3:
        for eeg_file in eeg_files:
            nes_code = eeg_file.eeg_data.file_format.nes_code
            file_extension = eeg_file.file.path.split(".")[-1]
            if nes_code == "MNE-RawFromBrainVision" and file_extension == "vhdr":
                reading = eeg_data_reading(eeg_file, preload=False)

    if reading:
        raw = reading.reading

        if raw is not None:
            picks = mne.pick_types(raw.info, eeg=True)
            ch_names = raw.info["ch_names"]
            channels = len(picks)
            montage = ""

            # If EGI 129 channels
            if nes_code == "MNE-RawFromEGI":
                if channels == 129:
                    montage = mne.channels.read_custom_montage("GSN-HydroCel-129")

                if channels == 128:
                    montage = mne.channels.read_custom_montage("GSN-HydroCel-128")

                if montage != "":
                    i = 0
                    list1 = []
                    list2 = []

                    for ch_name in ch_names:
                        i = i + 1
                        if i < 10:
                            label = "EEG" + " 00" + str(i)
                        if 9 < i < 100:
                            label = "EEG" + " 0" + str(i)
                        if 99 < i < channels:
                            label = "EEG" + " " + str(i)

                        if ch_name == label:
                            list1.insert(i, "E" + str(i))
                            list2.insert(i, ch_name)

                    list1.insert(i + 1, "Cz")
                    list2.insert(i + 1, "E" + str(channels))
                    mapping = dict(zip(list2, list1))

                    raw.rename_channels(mapping)
            if nes_code == "MNE-RawFromBrainVision":
                montage = mne.channels.read_custom_montage("standard_1020")

            if montage != "":
                raw.set_montage(montage)

                file_name = "sensors_position_" + str(eeg_data.id) + ".png"
                errors, path_complete = create_directory(settings.MEDIA_ROOT, "temp")

                # The operation below ensures that the properly backend is set
                import matplotlib as mpl

                mpl.use("agg")

                fig = raw.plot_sensors(
                    ch_type="eeg",
                    show_names=True,
                    show=False,
                    title="Sensor positions",
                    ch_groups="position",
                )
                fig.savefig(path.join(path_complete, file_name))

                file_path = path.join(settings.MEDIA_ROOT, "temp", file_name)

    return file_path


def eeg_data_reading(eeg_file: EEGFile, preload=False):
    eeg_reading = EEGReading()

    # For known formats, try to access data in order to validate the format

    # v1.5
    if eeg_file.eeg_data.file_format.nes_code == "MNE-RawFromEGI":
        eeg_reading.file_format = eeg_file.eeg_data.file_format

        try:
            # Trying to read the segments
            reading = mne.io.read_raw_egi(eeg_file.file.path, preload=preload)
        except:
            reading = None

        eeg_reading.reading = reading

    if eeg_file.eeg_data.file_format.nes_code == "MNE-RawFromBrainVision":
        eeg_reading.file_format = eeg_file.eeg_data.file_format

        try:
            # Trying to read the segments
            reading = mne.io.read_raw_brainvision(
                eeg_file.file.path, preload=preload, stim_channel=False
            )
        except:
            reading = None

        eeg_reading.reading = reading

    return eeg_reading


@login_required
@permission_required("experiment.change_experiment")
def eeg_data_view(
    request, eeg_data_id, tab, template_name="experiment/subject_eeg_data_form.html"
):
    eeg_data = get_object_or_404(EEGData, pk=eeg_data_id)
    eeg_data_form = EEGDataForm(request.POST or None, instance=eeg_data)
    eeg_step = get_object_or_404(
        EEG, id=eeg_data.data_configuration_tree.component_configuration.component.id
    )

    for field in eeg_data_form.fields:
        eeg_data_form.fields[field].widget.attrs["disabled"] = True

    file_format_list = file_format_code("EEG")

    image = False
    positions = []
    if hasattr(eeg_data.eeg_setting, "eeg_electrode_layout_setting"):
        for position_worked in eeg_data.electrode_positions.all().order_by(
            "eeg_electrode_position_setting__eeg_electrode_position__name"
        ):
            point_setting = (
                position_worked.eeg_electrode_position_setting.eeg_electrode_position
            )
            positions.append(
                {
                    "id": position_worked.id,
                    "position": point_setting.name,
                    "x": point_setting.coordinate_x,
                    "y": point_setting.coordinate_y,
                    "status": True,  # 'status' indicates if the point exist at the DB
                    "worked": position_worked.worked,
                }
            )
        if len(positions) > 0:
            image = True

    # Geração da imagem de localização dos electrodos (NES v1.5)
    sensors_positions_filepath = get_sensors_position(eeg_data)
    if sensors_positions_filepath:
        sensors_positions_relativepath = path.join(
            settings.MEDIA_URL, "temp", path.basename(sensors_positions_filepath)
        )
    else:
        sensors_positions_relativepath = None

    if request.method == "POST":
        if request.POST["action"] == "remove":
            check_can_change(
                request.user,
                eeg_data.subject_of_group.group.experiment.research_project,
            )

            subject_of_group = eeg_data.subject_of_group

            # removing uploaded files
            for eeg_uploaded_file in eeg_data.eeg_files.all():
                eeg_uploaded_file.file.delete()

            eeg_data.delete()
            messages.success(request, _("EEG data removed successfully."))
            return redirect(
                "subject_eeg_view",
                group_id=subject_of_group.group_id,
                subject_id=subject_of_group.subject_id,
            )

    context = {
        "can_change": get_can_change(
            request.user, eeg_data.subject_of_group.group.experiment.research_project
        ),
        "editing": False,
        "group": eeg_data.subject_of_group.group,
        "subject": eeg_data.subject_of_group.subject,
        "eeg_data_form": eeg_data_form,
        "eeg_data": eeg_data,
        "eeg_setting_default_id": eeg_step.eeg_setting_id,
        "file_format_list": file_format_list,
        "tab": tab,
        "json_list": json.dumps(positions),
        "image": image,
        "sensors_image": sensors_positions_relativepath,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def eeg_data_edit(
    request, eeg_data_id, tab, template_name="experiment/subject_eeg_data_form.html"
):
    eeg_data = get_object_or_404(EEGData, pk=eeg_data_id)

    # get the current before change
    current_eeg_setting_id = eeg_data.eeg_setting.id

    eeg_step = get_object_or_404(
        EEG, id=eeg_data.data_configuration_tree.component_configuration.component.id
    )

    check_can_change(
        request.user, eeg_data.subject_of_group.group.experiment.research_project
    )

    if request.method == "POST":
        eeg_data_form = EEGDataForm(request.POST, request.FILES, instance=eeg_data)

        if request.POST["action"] == "save":
            if eeg_data_form.is_valid():
                if tab == "1":
                    has_changed = False

                    if eeg_data_form.has_changed():
                        has_changed = True

                        # if the eeg-setting changed
                        if current_eeg_setting_id != int(request.POST["eeg_setting"]):
                            # remove all current position status
                            for position in eeg_data.electrode_positions.all():
                                position.delete()

                        eeg_data_to_update = eeg_data_form.save(commit=False)
                        eeg_data_to_update.group = eeg_data.subject_of_group.group
                        eeg_data_to_update.subject = eeg_data.subject_of_group.subject
                        eeg_data_to_update.save()

                        if hasattr(
                            eeg_data.eeg_setting, "eeg_electrode_layout_setting"
                        ):
                            if (
                                eeg_data.eeg_setting.eeg_electrode_layout_setting.positions_setting
                            ):
                                for (
                                    position_setting
                                ) in (
                                    eeg_data.eeg_setting.eeg_electrode_layout_setting.positions_setting.all()
                                ):
                                    # if not exists a position status
                                    position_status = EEGElectrodePositionCollectionStatus.objects.filter(
                                        eeg_data=eeg_data_to_update,
                                        eeg_electrode_position_setting=position_setting,
                                    )
                                    if not position_status:
                                        EEGElectrodePositionCollectionStatus(
                                            eeg_data=eeg_data_to_update,
                                            eeg_electrode_position_setting=position_setting,
                                            worked=position_setting.used,
                                            channel_index=position_setting.channel_index,
                                        ).save()

                    # removing checked files
                    for current_eeg_file in eeg_data.eeg_files.all():
                        if (
                            "remove_eeg_file_" + str(current_eeg_file.id)
                            in request.POST
                        ):
                            has_changed = True
                            current_eeg_file.delete()

                    # new files to upload
                    files_to_upload_list = request.FILES.getlist("eeg_files")
                    for file_to_upload in files_to_upload_list:
                        has_changed = True
                        eeg_file = EEGFile(eeg_data=eeg_data, file=file_to_upload)
                        eeg_file.save()

                    if has_changed:
                        messages.success(request, _("EEG data updated successfully."))
                    else:
                        messages.info(request, _("There is no changes to save."))

                if tab == "3":
                    for position_worked in eeg_data.electrode_positions.all():
                        position_worked.worked = (
                            "position_worked_" + str(position_worked.id) in request.POST
                        )
                        position_worked.save()

                    messages.success(
                        request, _("EEG position data updated successfully.")
                    )

                else:
                    for position_status in eeg_data.electrode_positions.all():
                        position_status.worked = (
                            "position_status_" + str(position_status.id) in request.POST
                        )
                        position_status.save()

                    messages.success(
                        request, _("EEG position data updated successfully.")
                    )

                redirect_url = reverse("eeg_data_view", args=(eeg_data_id, tab))
                return HttpResponseRedirect(redirect_url)

    else:
        eeg_data_form = EEGDataForm(
            request.POST or None,
            instance=eeg_data,
            initial={"experiment": eeg_data.subject_of_group.group.experiment},
        )

    file_format_list = file_format_code("EEG")

    positions = []
    image = False
    if hasattr(eeg_data.eeg_setting, "eeg_electrode_layout_setting"):
        for position_status in eeg_data.electrode_positions.all().order_by(
            "eeg_electrode_position_setting__eeg_electrode_position__name"
        ):
            point_setting = (
                position_status.eeg_electrode_position_setting.eeg_electrode_position
            )
            positions.append(
                {
                    "id": position_status.id,
                    "position": point_setting.name,
                    "x": point_setting.coordinate_x,
                    "y": point_setting.coordinate_y,
                    # 'status' indicates if the point exist at the DB
                    "status": True,
                    "worked": position_status.worked,
                }
            )
        if positions.__len__() > 0:
            image = True

    context = {
        "group": eeg_data.subject_of_group.group,
        "subject": eeg_data.subject_of_group.subject,
        "eeg_data_form": eeg_data_form,
        "eeg_data": eeg_data,
        "file_format_list": file_format_list,
        "eeg_setting_default_id": eeg_step.eeg_setting_id,
        "editing": True,
        "tab": tab,
        "json_list": json.dumps(positions),
        "image": image,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def eeg_image_edit(
    request, eeg_data_id, tab, template_name="experiment/subject_eeg_image_data.html"
):
    eeg_data = get_object_or_404(EEGData, pk=eeg_data_id)

    eeg_data_form = EEGDataForm(request.POST or None, instance=eeg_data)

    # get the current before change

    eeg_setting = eeg_data.eeg_setting
    positions = []
    if hasattr(eeg_setting, "eeg_electrode_layout_setting"):
        for position_status in eeg_data.electrode_positions.all().order_by(
            "eeg_electrode_position_setting__eeg_electrode_position__name"
        ):
            point_setting = (
                position_status.eeg_electrode_position_setting.eeg_electrode_position
            )
            positions.append(
                {
                    "id": position_status.id,
                    "position": point_setting.name,
                    "x": point_setting.coordinate_x,
                    "y": point_setting.coordinate_y,
                    # 'status' indicates if the point exist at the DB
                    "status": True,
                    "worked": position_status.worked,
                }
            )

    if request.method == "POST":
        if request.POST["action"] == "save":
            for position_status in eeg_data.electrode_positions.all():
                position_status.worked = (
                    "position_status_" + str(position_status.id) in request.POST
                )
                position_status.save()

            messages.success(request, _("Setting saved successfully."))

            redirect_url = reverse("eeg_data_view", args=(eeg_data_id, tab))
            return HttpResponseRedirect(redirect_url)

    context = {
        "group": eeg_data.subject_of_group.group,
        "subject": eeg_data.subject_of_group.subject,
        "eeg_data": eeg_data,
        "eeg_data_form": eeg_data_form,
        "editing": True,
        "json_list": json.dumps(positions),
        "tab": tab,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def eeg_data_get_process_requisition_status(request, process_requisition):
    status = request.session.get(
        "process_requisition_status" + str(process_requisition)
    )
    message = request.session.get(
        "process_requisition_message" + str(process_requisition),
        _("Waiting for status"),
    )
    if status == "finished":
        del request.session["process_requisition_status" + str(process_requisition)]
        del request.session["process_requisition_message" + str(process_requisition)]
    response_data = {"status": status, "message": message}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def update_process_requisition(request, process_requisition, status, message):
    request.session["process_requisition_status" + str(process_requisition)] = status
    request.session["process_requisition_message" + str(process_requisition)] = message
    request.session.save()


def clean(input_string):
    return input_string.encode("ascii", "replace").decode()


@login_required
@permission_required("experiment.change_experiment")
def eeg_file_export_nwb(request, eeg_file_id, some_number, process_requisition):
    update_process_requisition(
        request, process_requisition, "reading_source_file", _("Reading source file")
    )
    eeg_file = get_object_or_404(EEGFile, pk=eeg_file_id)

    # Open and read signal
    eeg_reading = eeg_data_reading(eeg_file, preload=True)

    # Was it open properly?
    ok_opening = False

    if eeg_reading:
        if eeg_reading.file_format.nes_code == "MNE-RawFromEGI":
            ok_opening = True

    if not ok_opening:
        update_process_requisition(
            request, process_requisition, "finished", _("Finished")
        )

        messages.error(
            request,
            _(
                "It was not possible to open the data file. Check if the number of channels configured is correct."
            ),
        )

        return redirect(
            "subject_eeg_view",
            group_id=eeg_file.eeg_data.subject_of_group.group_id,
            subject_id=eeg_file.eeg_data.subject_of_group.subject_id,
        )

    errors, path_complete = create_directory(settings.MEDIA_ROOT, "export_nwb")
    errors, path_complete = create_directory(path_complete, str(request.user.id))
    file_name = (
        "EEG_"
        + eeg_file.eeg_data.subject_of_group.subject.patient.code
        + "_"
        + str(some_number)
        + ".nwb"
    )
    nwb_file_name = path.join(path_complete, file_name)

    nwb_file_name = create_nwb_file(
        eeg_file.eeg_data, eeg_reading, process_requisition, request, nwb_file_name
    )

    response = HttpResponse(open(nwb_file_name, "rb").read())
    response["Content-Type"] = "application/force-download"
    response["Content-Disposition"] = "attachment; filename=%s" % smart_str(file_name)

    update_process_requisition(request, process_requisition, "finished", _("Finished"))

    return response


def create_nwb_file(eeg_data, eeg_reading, process_requisition, request, filename):
    subject_of_group = eeg_data.subject_of_group
    social_demographic_data = None
    social_demographic_query = SocialDemographicData.objects.filter(
        patient=subject_of_group.subject.patient
    )
    if social_demographic_query:
        social_demographic_data = social_demographic_query.first()

    ########################################################################
    # create a new NWB file
    # several settings are specified when doing so. these can be supplied within
    #   the NWB constructor or defined in a dict, as in in this example

    nwb_file_settings = dict()
    nwb_file_settings["filename"] = filename
    # each file should have a descriptive globally unique identifier
    #   that specifies the lab and this experiment session
    # the function nwb.create_identifier() is recommended to use as it takes
    #   the string and appends the present date and time
    nwb_file_settings["identifier"] = nwb.create_identifier(
        "Participant: "
        + subject_of_group.subject.patient.code
        + "; NES experiment: "
        + clean(eeg_data.subject_of_group.group.experiment.title)
    )
    # indicate that it's OK to overwrite exting file
    nwb_file_settings["overwrite"] = True
    # specify the start time of the experiment. all times in the NWB file
    #   are relative to experiment start time
    # if the start time is not specified the present time will be used
    # settings["start_time"] = "Sat Jul 04 2015 3:14:16"
    nwb_file_settings["start_time"] = eeg_data.date.strftime("%Y-%m-%d") + (
        " " + eeg_data.time.strftime("%H:%M:%S") if eeg_data.time else ""
    )
    # provide one or two sentences that describe the experiment and what
    #   data is in the file
    nwb_file_settings["description"] = clean(
        subject_of_group.group.experiment.description
    )
    # create the NWB object. this manages the file
    # print("Creating " + nwb_file_settings["filename"])
    neurodata = nwb.NWBFile(**nwb_file_settings)
    ########################################################################
    # general metadata section
    #
    if request:
        update_process_requisition(
            request, process_requisition, "reading_metadata", _("Reading metadata")
        )

    neurodata.set_metadata(
        EXPERIMENT_DESCRIPTION, clean(subject_of_group.group.experiment.description)
    )
    history_data = eeg_data.history.all().order_by("history_date")
    if history_data:
        experimenter = history_data.last().history_user
        if experimenter.last_name or experimenter.first_name:
            experimenter_description = (
                experimenter.last_name + ", " + experimenter.first_name
            )
        else:
            experimenter_description = experimenter.username

        if experimenter.email:
            experimenter_description += " - " + experimenter.email

        neurodata.set_metadata(EXPERIMENTER, clean(experimenter_description))
    neurodata.set_metadata(SUBJECT_ID, subject_of_group.subject.patient.code)
    neurodata.set_metadata(SEX, clean(subject_of_group.subject.patient.gender.name))
    neurodata.set_metadata(SPECIES, "human")
    neurodata.set_metadata(
        AGE,
        str(
            (date.today() - subject_of_group.subject.patient.date_birth)
            // timedelta(days=365.2425)
        ),
    )
    if social_demographic_data:
        if social_demographic_data.flesh_tone:
            neurodata.set_metadata(
                GENOTYPE, clean(social_demographic_data.flesh_tone.name)
            )
        if social_demographic_data.natural_of:
            neurodata.set_metadata(SUBJECT, clean(social_demographic_data.natural_of))

    ########################################################################
    # general devices section
    #
    if request:
        update_process_requisition(
            request,
            process_requisition,
            "reading_device_data",
            _("Reading device data"),
        )
    # Amplifier device setting
    if hasattr(eeg_data.eeg_setting, "eeg_amplifier_setting"):
        device_identification = clean(
            eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.identification
        )
        device_information = _("Device type: Amplifier; ")

        if eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.description:
            device_information += (
                _("Description: ")
                + eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.description
                + "; "
            )

        device_information += (
            _("Manufacturer: ")
            + eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.manufacturer.name
            + "; "
        )

        device_information += (
            _("Gain: ")
            + str(eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.gain)
            + "; "
        )

        if eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.input_impedance:
            device_information += (
                _("Impedance: ")
                + get_nwb_eeg_amplifier_impedance_description(
                    eeg_data.eeg_setting.eeg_amplifier_setting
                )
                + "; "
            )

        if (
            eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.common_mode_rejection_ratio
        ):
            device_information += (
                _("Common mode rejection ratio: ")
                + str(
                    eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.common_mode_rejection_ratio
                )
                + "; "
            )

        neurodata.set_metadata(DEVICE(device_identification), clean(device_information))

    # EEG machine
    if hasattr(eeg_data.eeg_setting, "eeg_amplifier_setting"):
        device_identification = clean(
            eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.identification
        )
        device_information = _("Device type: EEG Amplifier; ")

        if eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.description:
            device_information += (
                _("Description: ")
                + eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.description
                + "; "
            )

        device_information += (
            _("Manufacturer: ")
            + eeg_data.eeg_setting.eeg_amplifier_setting.eeg_amplifier.manufacturer.name
            + "; "
        )

        device_information += (
            _("Number of used channels: ")
            + str(eeg_data.eeg_setting.eeg_amplifier_setting.number_of_channels_used)
            + "; "
        )

        neurodata.set_metadata(DEVICE(device_identification), clean(device_information))

    # Ephys: Filter device setting
    if hasattr(eeg_data.eeg_setting, "eeg_filter_setting"):
        neurodata.set_metadata(
            EXTRA_FILTERING,
            clean(
                get_nwb_eeg_filter_description(eeg_data.eeg_setting.eeg_filter_setting)
            ),
        )

    # EEG Electrode NET
    if hasattr(eeg_data.eeg_setting, "eeg_electrode_layout_setting"):
        eeg_electrode_net_system = (
            eeg_data.eeg_setting.eeg_electrode_layout_setting.eeg_electrode_net_system
        )

        device_identification = clean(
            eeg_electrode_net_system.eeg_electrode_net.identification
        )
        device_information = _("Device type: EEG Electrode Net; ")

        if eeg_electrode_net_system.eeg_electrode_net.description:
            device_information += (
                _("Description: ")
                + eeg_electrode_net_system.eeg_electrode_net.description
                + "; "
            )

        device_information += (
            _("Manufacturer: ")
            + eeg_electrode_net_system.eeg_electrode_net.manufacturer.name
            + "; "
        )

        neurodata.set_metadata(DEVICE(device_identification), clean(device_information))

        # Electrode map and group
        electrode_map = []
        electrode_group = []

        for (
            position
        ) in (
            eeg_electrode_net_system.eeg_electrode_localization_system.electrode_positions.all()
        ):
            position_name = clean(position.name)
            electrode_group.append(position_name)
            electrode_map.append([position.coordinate_x, position.coordinate_y, 0])
            neurodata.set_metadata(
                EXTRA_SHANK_LOCATION(position_name),
                clean(
                    _("Position: ")
                    + position_name
                    + "; "
                    + _("Coordinates: (")
                    + str(position.coordinate_x)
                    + ", "
                    + str(position.coordinate_y)
                    + "); "
                    + _(
                        "EEG electrode localization system: "
                        + eeg_electrode_net_system.eeg_electrode_localization_system.name
                    )
                ),
            )
            neurodata.set_metadata(
                EXTRA_SHANK_DEVICE(position_name), device_identification
            )

        neurodata.set_metadata(EXTRA_ELECTRODE_MAP, electrode_map)
        neurodata.set_metadata(EXTRA_ELECTRODE_GROUP, electrode_group)

    ########################################################################
    # acquisition section
    #
    ########################################################################
    if request:
        update_process_requisition(
            request,
            process_requisition,
            "reading_acquisition_data",
            _("Reading acquisition data"),
        )
    if eeg_reading:
        if eeg_reading.file_format.nes_code == "MNE-RawFromEGI":
            # v1.5
            number_of_channels = len(mne.pick_types(eeg_reading.reading.info, eeg=True))

            number_of_samples = len(eeg_reading.reading._data[0])

            sampling_rate = 0
            if (
                hasattr(eeg_data.eeg_setting, "eeg_amplifier_setting")
                and eeg_data.eeg_setting.eeg_amplifier_setting.sampling_rate
            ):
                sampling_rate = eeg_data.eeg_setting.eeg_amplifier_setting.sampling_rate

            timestamps = np.arange(number_of_samples) * (
                (1 / sampling_rate) if sampling_rate else 0
            )

            # v1.5
            array_data = np.zeros((number_of_samples, number_of_channels))
            for index_channel in range(number_of_channels):
                channel_reading = eeg_reading.reading._data[
                    mne.pick_types(eeg_reading.reading.info, eeg=True)[index_channel]
                ]
                for index, value in enumerate(channel_reading):
                    array_data[index][index_channel] = value

            acquisition = neurodata.create_timeseries(
                "ElectricalSeries", "data_collection", "acquisition"
            )
            acquisition.set_data(array_data, resolution=1.2345e-6)
            acquisition.set_time(timestamps)
            acquisition.set_value("num_samples", number_of_samples)
            acquisition.set_value("electrode_idx", list(range(number_of_channels)))
            acquisition.finalize()

    # when all data is entered, close the file
    neurodata.close()

    return neurodata.file_name


def get_nwb_eeg_filter_description(eeg_filter_setting):
    response = _("Filter type:") + eeg_filter_setting.eeg_filter_type.name
    if eeg_filter_setting.eeg_filter_type.description:
        response += "(" + eeg_filter_setting.eeg_filter_type.description + ")"
    response += "; "
    if eeg_filter_setting.high_pass:
        response += _("High pass: ") + str(eeg_filter_setting.high_pass) + " Hz; "
    if eeg_filter_setting.low_pass:
        response += _("Low pass: ") + str(eeg_filter_setting.high_pass) + " Hz; "
    if eeg_filter_setting.order:
        response += _("Order: ") + str(eeg_filter_setting.high_pass) + "; "
    return response


def get_nwb_eeg_amplifier_impedance_description(eeg_amplifier_setting):
    response = str(eeg_amplifier_setting.eeg_amplifier.input_impedance)
    if eeg_amplifier_setting.eeg_amplifier.input_impedance_unit:
        response += " " + eeg_amplifier_setting.eeg_amplifier.input_impedance_unit
    return response


@login_required
@permission_required("experiment.change_experiment")
def eeg_electrode_position_collection_status_change_the_order(
    request, eeg_electrode_position_collection_status_id, command
):
    position_status = get_object_or_404(
        EEGElectrodePositionCollectionStatus,
        pk=eeg_electrode_position_collection_status_id,
    )

    all_position_status = EEGElectrodePositionCollectionStatus.objects.filter(
        eeg_data=position_status.eeg_data
    )

    if command == "down":
        position_status_to_change = (
            all_position_status.filter(channel_index__gt=position_status.channel_index)
            .order_by("channel_index")
            .first()
        )
    else:
        position_status_to_change = (
            all_position_status.filter(channel_index__lt=position_status.channel_index)
            .order_by("-channel_index")
            .first()
        )

    bottom_position_setting = all_position_status.order_by("-channel_index").first()

    channel_index_current = position_status.channel_index
    channel_index_to_change = position_status_to_change.channel_index

    position_status_to_change.channel_index = bottom_position_setting.channel_index + 1
    position_status_to_change.save()

    position_status.channel_index = channel_index_to_change
    position_status.save()

    position_status_to_change.channel_index = channel_index_current
    position_status_to_change.save()

    redirect_url = reverse("eeg_data_view", args=(position_status.eeg_data_id, "2"))

    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.view_researchproject")
def subject_tms_view(
    request,
    group_id,
    subject_id,
    template_name="experiment/subject_tms_collection_list.html",
):
    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)

    tms_collections = []

    list_of_paths = create_list_of_trees(group.experimental_protocol, "tms")

    subject_of_group = get_object_or_404(SubjectOfGroup, group=group, subject=subject)

    for path in list_of_paths:
        tms_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])

        data_configuration_tree_id = list_data_configuration_tree(
            tms_configuration.id, [item[0] for item in path]
        )

        tms_data_files = TMSData.objects.filter(
            subject_of_group=subject_of_group,
            data_configuration_tree__id=data_configuration_tree_id,
        )

        tms_collections.append(
            {
                "tms_configuration": tms_configuration,
                "path": path,
                "tms_data_files": tms_data_files,
            }
        )

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "subject": subject,
        "tms_collections": tms_collections,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_questionnaireresponse")
def subject_tms_data_create(
    request,
    group_id,
    subject_id,
    tms_configuration_id,
    template_name="experiment/subject_tms_data_form.html",
):
    group = get_object_or_404(Group, id=group_id)

    list_of_path = [int(item) for item in tms_configuration_id.split("-")]
    tms_configuration_id = list_of_path[-1]

    check_can_change(request.user, group.experiment.research_project)

    tms_configuration = get_object_or_404(
        ComponentConfiguration, id=tms_configuration_id
    )
    tms_step = get_object_or_404(TMS, id=tms_configuration.component_id)

    redirect_url = None
    tms_data_id = None

    tms_data_form = TMSDataForm(
        None,
        initial={
            "experiment": group.experiment,
            "tms_setting": tms_step.tms_setting_id,
        },
    )

    tms_setting = get_object_or_404(TMSSetting, id=tms_step.tms_setting_id)

    pulse_stimulus = (
        get_pulse_stimulus_name(tms_setting.tms_device_setting.pulse_stimulus_type)
        if hasattr(tms_setting, "tms_device_setting")
        else None
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            tms_data_form = TMSDataForm(request.POST, request.FILES)

            if tms_data_form.is_valid():
                data_configuration_tree_id = list_data_configuration_tree(
                    tms_configuration_id, list_of_path
                )
                if not data_configuration_tree_id:
                    data_configuration_tree_id = create_data_configuration_tree(
                        list_of_path
                    )

                subject = get_object_or_404(Subject, pk=subject_id)
                subject_of_group = get_object_or_404(
                    SubjectOfGroup, subject=subject, group_id=group_id
                )

                tms_data_added = tms_data_form.save(commit=False)
                tms_data_added.subject_of_group = subject_of_group
                tms_data_added.component_configuration = tms_configuration
                tms_data_added.data_configuration_tree_id = data_configuration_tree_id

                # PS: it was necessary adding these 2 lines because Django raised, I do not why (Evandro),
                # the following error 'TMSData' object has no attribute 'group'
                tms_data_added.group = group
                tms_data_added.subject = subject

                tms_data_added.save()

                messages.success(
                    request, _("TMS data collection created successfully.")
                )

                redirect_url = reverse("tms_data_view", args=(tms_data_added.id,))
                # redirect_url = reverse("subjects", args=(group.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "creating": True,
        "editing": True,
        "group": group,
        "tms_configuration": tms_configuration,
        "tms_data_form": tms_data_form,
        "tms_data_id": tms_data_id,
        "tms_setting_default_id": tms_step.tms_setting_id,
        "subject": get_object_or_404(Subject, pk=subject_id),
        "pulse_stimulus": pulse_stimulus,
        "URL": redirect_url,
        "tab": "1",
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def tms_data_view(
    request, tms_data_id, template_name="experiment/subject_tms_data_form.html"
):
    tms_data = get_object_or_404(TMSData, pk=tms_data_id)
    tms_step = get_object_or_404(
        TMS, id=tms_data.data_configuration_tree.component_configuration.component.id
    )

    tms_data_form = TMSDataForm(request.POST or None, instance=tms_data)

    pulse_stimulus = (
        get_pulse_stimulus_name(
            tms_data.tms_setting.tms_device_setting.pulse_stimulus_type
        )
        if hasattr(tms_data.tms_setting, "tms_device_setting")
        else None
    )

    for field in tms_data_form.fields:
        tms_data_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            check_can_change(
                request.user,
                tms_data.subject_of_group.group.experiment.research_project,
            )

            subject_of_group = tms_data.subject_of_group
            tms_data.delete()
            messages.success(request, _("TMS data removed successfully."))
            return redirect(
                "subject_tms_view",
                group_id=subject_of_group.group_id,
                subject_id=subject_of_group.subject_id,
            )

    context = {
        "can_change": get_can_change(
            request.user, tms_data.subject_of_group.group.experiment.research_project
        ),
        "editing": False,
        "group": tms_data.subject_of_group.group,
        "subject": tms_data.subject_of_group.subject,
        "tms_data_form": tms_data_form,
        "tms_data": tms_data,
        "pulse_stimulus": pulse_stimulus,
        "tms_setting_default_id": tms_step.tms_setting_id,
        "tab": "1",
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def tms_data_edit(request, tms_data_id, tab):
    tms_data = get_object_or_404(TMSData, pk=tms_data_id)

    tms_step = get_object_or_404(
        TMS, id=tms_data.data_configuration_tree.component_configuration.component.id
    )

    check_can_change(
        request.user, tms_data.subject_of_group.group.experiment.research_project
    )

    pulse_stimulus = get_pulse_stimulus_name(
        tms_data.tms_setting.tms_device_setting.pulse_stimulus_type
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if tab == "1":
                tms_data_form = TMSDataForm(
                    request.POST, request.FILES, instance=tms_data
                )
                if tms_data_form.is_valid() and tms_data_form.has_changed():
                    tms_data_to_update = tms_data_form.save(commit=False)
                    tms_data_to_update.group = tms_data.subject_of_group.group
                    tms_data_to_update.subject = tms_data.subject_of_group.subject
                    tms_data_to_update.save()

                    messages.success(request, _("TMS data updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("tms_data_view", args=(tms_data_id,))

            if tab == "2":
                hotspot_form = HotSpotForm(request.POST or None, request.FILES)

                if hotspot_form.is_valid() and "localization_system_selection":
                    if hotspot_form.has_changed():
                        localization_system_val = request.POST[
                            "localization_system_selection"
                        ].split(",")[0]
                        localization_system = TMSLocalizationSystem.objects.get(
                            pk=localization_system_val
                        )

                        hotspot_to_update = hotspot_form.save(commit=False)
                        hotspot_to_update.tms_localization_system = localization_system
                        hotspot_to_update.tms_data = tms_data
                        # hotspot_to_update.hot_spot_map = hotspot_image.png
                        hotspot_to_update.save()

                        if request.POST.get("spot_image"):
                            data = request.POST.get("spot_image").split(",")[-1]
                            binary_data = base64.encodebytes(base64.b64decode(data))
                            with open("hotspot_tmp.png", "wb") as f:
                                f.write(base64.decodebytes(binary_data))

                            with open("hotspot_tmp.png", "rb") as f:
                                image_file = File(f)
                                hotspot_to_update.hot_spot_map.save(
                                    "hotspot_image.png", image_file
                                )

                        messages.success(
                            request, _("TMS position updated sucessfully.")
                        )

                    else:
                        messages.success(request, _("There is no changes to save"))

                redirect_url = reverse(
                    "tms_data_position_setting_view", args=(tms_data_id,)
                )

        return HttpResponseRedirect(redirect_url)

    else:
        tms_data_form = TMSDataForm(
            request.POST or None,
            instance=tms_data,
            initial={"experiment": tms_data.subject_of_group.group.experiment},
        )

        if tab == "1":
            template_name = "experiment/subject_tms_data_form.html"
            hotspot_form = None
            localization_system_selected = None
        else:
            template_name = "experiment/tms_data_position_setting.html"
            if hasattr(tms_data, "hotspot"):
                hotspot_form = HotSpotForm(
                    request.POST or None, instance=tms_data.hotspot
                )

                localization_system_selected = get_object_or_404(
                    TMSLocalizationSystem,
                    pk=tms_data.hotspot.tms_localization_system_id,
                )
            else:
                hotspot_form = HotSpotForm(request.POST or None)
                localization_system_selected = None

    context = {
        "group": tms_data.subject_of_group.group,
        "subject": tms_data.subject_of_group.subject,
        "tms_data_form": tms_data_form,
        "tms_data": tms_data,
        "pulse_stimulus": pulse_stimulus,
        "tms_setting_default_id": tms_step.tms_setting_id,
        "hotspot_form": hotspot_form,
        "tms_localization_system_list": TMSLocalizationSystem.objects.all(),
        "localization_system_selected": localization_system_selected,
        "editing": True,
        "tab": tab,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def subject_digital_game_phase_view(
    request,
    group_id,
    subject_id,
    template_name="experiment/subject_digital_game_phase_collection_list.html",
):
    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)

    digital_game_phase_collections = []

    list_of_paths = create_list_of_trees(
        group.experimental_protocol, "digital_game_phase"
    )

    subject_of_group = get_object_or_404(SubjectOfGroup, group=group, subject=subject)

    for path in list_of_paths:
        digital_game_phase_configuration = ComponentConfiguration.objects.get(
            pk=path[-1][0]
        )

        data_configuration_tree_id = list_data_configuration_tree(
            digital_game_phase_configuration.id, [item[0] for item in path]
        )

        digital_game_phase_data_list = DigitalGamePhaseData.objects.filter(
            subject_of_group=subject_of_group,
            data_configuration_tree__id=data_configuration_tree_id,
        )

        digital_game_phase_collections.append(
            {
                "digital_game_phase_configuration": digital_game_phase_configuration,
                "path": path,
                "digital_game_phase_data_list": digital_game_phase_data_list,
            }
        )

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "subject": subject,
        "digital_game_phase_collections": digital_game_phase_collections,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def subject_digital_game_phase_data_create(
    request,
    group_id,
    subject_id,
    digital_game_phase_configuration_id,
    template_name="experiment/subject_digital_game_phase_data_form.html",
):
    group = get_object_or_404(Group, id=group_id)

    list_of_path = [
        int(item) for item in digital_game_phase_configuration_id.split("-")
    ]
    digital_game_phase_configuration_id = list_of_path[-1]

    check_can_change(request.user, group.experiment.research_project)

    digital_game_phase_configuration = get_object_or_404(
        ComponentConfiguration, id=digital_game_phase_configuration_id
    )

    redirect_url = None
    digital_game_phase_data_id = None

    digital_game_phase_data_form = DigitalGamePhaseDataForm(
        None, initial={"experiment": group.experiment}
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            digital_game_phase_data_form = DigitalGamePhaseDataForm(
                request.POST, request.FILES
            )

            if digital_game_phase_data_form.is_valid():
                data_configuration_tree_id = list_data_configuration_tree(
                    digital_game_phase_configuration_id, list_of_path
                )
                if not data_configuration_tree_id:
                    data_configuration_tree_id = create_data_configuration_tree(
                        list_of_path
                    )

                subject = get_object_or_404(Subject, pk=subject_id)
                subject_of_group = get_object_or_404(
                    SubjectOfGroup, subject=subject, group_id=group_id
                )

                digital_game_phase_data_added = digital_game_phase_data_form.save(
                    commit=False
                )
                digital_game_phase_data_added.subject_of_group = subject_of_group
                digital_game_phase_data_added.component_configuration = (
                    digital_game_phase_configuration
                )
                digital_game_phase_data_added.data_configuration_tree_id = (
                    data_configuration_tree_id
                )

                # PS: it was necessary adding these 2 lines because Django raised, I do not why (Evandro),
                # the following error 'DigitalGamePhaseData' object has no attribute 'group'
                digital_game_phase_data_added.group = group
                digital_game_phase_data_added.subject = subject

                digital_game_phase_data_added.save()

                # saving uploaded files
                files_to_upload_list = request.FILES.getlist("digital_game_phase_files")
                for file_to_upload in files_to_upload_list:
                    digital_game_phase_file = DigitalGamePhaseFile(
                        digital_game_phase_data=digital_game_phase_data_added,
                        file=file_to_upload,
                    )
                    digital_game_phase_file.save()

                messages.success(
                    request,
                    _("Goalkeeper game phase data collection created successfully."),
                )

                redirect_url = reverse(
                    "digital_game_phase_data_view",
                    args=(digital_game_phase_data_added.id,),
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "creating": True,
        "editing": True,
        "group": group,
        "digital_game_phase_configuration": digital_game_phase_configuration,
        "digital_game_phase_data_form": digital_game_phase_data_form,
        "digital_game_phase_data_id": digital_game_phase_data_id,
        "subject": get_object_or_404(Subject, pk=subject_id),
        "URL": redirect_url,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def digital_game_phase_data_view(
    request,
    digital_game_phase_data_id,
    template_name="experiment/subject_digital_game_phase_data_form.html",
):
    digital_game_phase_data = get_object_or_404(
        DigitalGamePhaseData, pk=digital_game_phase_data_id
    )

    digital_game_phase_data_form = DigitalGamePhaseDataForm(
        request.POST or None, instance=digital_game_phase_data
    )

    for field in digital_game_phase_data_form.fields:
        digital_game_phase_data_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            check_can_change(
                request.user,
                digital_game_phase_data.subject_of_group.group.experiment.research_project,
            )

            subject_of_group = digital_game_phase_data.subject_of_group

            # removing uploaded files
            for (
                digital_game_phase_uploaded_file
            ) in digital_game_phase_data.digital_game_phase_files.all():
                digital_game_phase_uploaded_file.file.delete()

            digital_game_phase_data.delete()
            messages.success(
                request, _("Goalkeeper game phase data removed successfully.")
            )
            return redirect(
                "subject_digital_game_phase_view",
                group_id=subject_of_group.group_id,
                subject_id=subject_of_group.subject_id,
            )

    context = {
        "can_change": get_can_change(
            request.user,
            digital_game_phase_data.subject_of_group.group.experiment.research_project,
        ),
        "editing": False,
        "group": digital_game_phase_data.subject_of_group.group,
        "subject": digital_game_phase_data.subject_of_group.subject,
        "digital_game_phase_data_form": digital_game_phase_data_form,
        "digital_game_phase_data": digital_game_phase_data,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def digital_game_phase_data_edit(request, digital_game_phase_data_id):
    digital_game_phase_data = get_object_or_404(
        DigitalGamePhaseData, pk=digital_game_phase_data_id
    )

    check_can_change(
        request.user,
        digital_game_phase_data.subject_of_group.group.experiment.research_project,
    )

    if request.method == "POST" and request.POST["action"] == "save":
        digital_game_phase_data_form = DigitalGamePhaseDataForm(
            request.POST, request.FILES, instance=digital_game_phase_data
        )

        has_changed = False

        if (
            digital_game_phase_data_form.is_valid()
            and digital_game_phase_data_form.has_changed()
        ):
            has_changed = True

            digital_game_phase_data_to_update = digital_game_phase_data_form.save(
                commit=False
            )
            digital_game_phase_data_to_update.group = (
                digital_game_phase_data.subject_of_group.group
            )
            digital_game_phase_data_to_update.subject = (
                digital_game_phase_data.subject_of_group.subject
            )
            digital_game_phase_data_to_update.save()

        # removing checked files
        for (
            current_digital_game_phase_file
        ) in digital_game_phase_data.digital_game_phase_files.all():
            if (
                "remove_digital_game_phase_file_"
                + str(current_digital_game_phase_file.id)
                in request.POST
            ):
                has_changed = True
                current_digital_game_phase_file.delete()

        # new files to upload
        files_to_upload_list = request.FILES.getlist("digital_game_phase_files")
        for file_to_upload in files_to_upload_list:
            has_changed = True
            digital_game_phase_file = DigitalGamePhaseFile(
                digital_game_phase_data=digital_game_phase_data, file=file_to_upload
            )
            digital_game_phase_file.save()

        if has_changed:
            messages.success(
                request, _("Goalkeeper game phase data updated successfully.")
            )
        else:
            messages.success(request, _("There is no changes to save."))

        redirect_url = reverse(
            "digital_game_phase_data_view", args=(digital_game_phase_data_id,)
        )

        return HttpResponseRedirect(redirect_url)

    else:
        digital_game_phase_data_form = DigitalGamePhaseDataForm(
            request.POST or None,
            instance=digital_game_phase_data,
            initial={
                "experiment": digital_game_phase_data.subject_of_group.group.experiment
            },
        )

    context = {
        "group": digital_game_phase_data.subject_of_group.group,
        "subject": digital_game_phase_data.subject_of_group.subject,
        "digital_game_phase_data_form": digital_game_phase_data_form,
        "digital_game_phase_data": digital_game_phase_data,
        "editing": True,
    }

    return render(
        request, "experiment/subject_digital_game_phase_data_form.html", context
    )


@login_required
@permission_required("experiment.view_researchproject")
def group_goalkeeper_game_data(
    request, group_id, template_name="experiment/group_goalkeeper_game_data.html"
):
    group = get_object_or_404(Group, id=group_id)

    if request.method == "POST":
        if request.POST["action"] == "group-code":
            group_code = (
                request.POST["group-code"] if request.POST["group-code"] else None
            )
            if Group.objects.filter(code__isnull=False, code=group_code):
                messages.warning(
                    request, _("Group code already used. Please choose another name.")
                )
            else:
                group.code = group_code
                group.save()
                messages.success(request, _("Group code changed successfully."))

        elif request.POST["action"][0:7] == "detail-":
            path_of_configuration = request.POST["action"][7:]

            list_of_path = [int(item) for item in path_of_configuration.split("-")]
            data_configuration_tree_id = list_data_configuration_tree(
                list_of_path[-1], list_of_path
            )
            if not data_configuration_tree_id:
                data_configuration_tree_id = create_data_configuration_tree(
                    list_of_path
                )
            data_configuration_tree = get_object_or_404(
                DataConfigurationTree, pk=data_configuration_tree_id
            )

            phase_code = request.POST["code-" + path_of_configuration]
            if phase_code == "":
                data_configuration_tree.code = None
            else:
                data_configuration_tree.code = phase_code
            data_configuration_tree.save()

    enable_upload = False
    digital_game_phase_collections = []

    list_of_paths = create_list_of_trees(
        group.experimental_protocol, "digital_game_phase"
    )

    for path in list_of_paths:
        digital_game_phase_configuration = ComponentConfiguration.objects.get(
            pk=path[-1][0]
        )

        data_configuration_tree_id = list_data_configuration_tree(
            digital_game_phase_configuration.id, [item[0] for item in path]
        )

        data_configuration_tree = DataConfigurationTree.objects.filter(
            id=data_configuration_tree_id
        ).first()

        try:
            game_and_phase = GoalkeeperPhase.objects.get(
                pk=data_configuration_tree.code
            )
        except:
            game_and_phase = None

        digital_game_phase_collections.append(
            {
                "digital_game_phase_configuration": digital_game_phase_configuration,
                "path": path,
                "data_configuration_tree": data_configuration_tree,
                "game_and_phase": game_and_phase,
            }
        )

        if (
            not enable_upload
            and group.code
            and game_and_phase
            and LocalInstitution.get_solo().code
        ):
            enable_upload = True

    digital_games_and_phases = GoalkeeperPhase.objects.all().order_by(
        "game__name", "phase"
    )

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "institution_code": LocalInstitution.get_solo().code,
        "digital_game_phase_collections": digital_game_phase_collections,
        "enable_upload": enable_upload,
        "digital_games_and_phases": digital_games_and_phases,
    }

    return render(request, template_name, context)


def create_csv_for_goalkeeper(complete_filename, config, results):
    header = [
        "player alias",
        "group code",
        "institution",
        "id",
        "soccer team",
        "game",
        "phase",
        "session time(s)",
        "relax time(s)",
        "game data",
        "game time",
        "game random",
        "limit plays",
        "total correct",
        "success rate",
        "game mode",
        "status",
        "plays to relax",
        "scoreboard",
        "final scoreboard",
        "animation type",
        "min hits",
        "playermachine",
        "move",
        "time until any key(s)",
        "time until show again(s)",
        "waited result",
        "eh random?",
        "option chosen",
        "movement time(s)",
        "decision time(s)",
        "sequence executed",
    ]
    rows_to_be_saved = list()
    rows_to_be_saved.append(header)
    for result in results:
        rows_to_be_saved.append(
            [
                config.playeralias,
                config.groupcode,
                config.institution,
                config.idresult,
                config.soccerteam,
                config.game,
                config.phase,
                config.sessiontime,
                config.relaxtime,
                config.gamedata,
                config.gametime,
                config.gamerandom,
                config.limitplays,
                config.totalcorrect,
                config.successrate,
                config.gamemode,
                config.status,
                config.playstorelax,
                config.scoreboard,
                config.finalscoreboard,
                config.animationtype,
                config.minhits,
                config.playermachine,
                result.move,
                result.timeuntilanykey,
                result.timeuntilshowagain,
                result.waitedresult,
                result.ehrandom,
                result.optionchoosen,
                result.movementtime,
                result.decisiontime,
                config.sequexecuted,
            ]
        )

    with open(
        complete_filename.encode("utf-8"), "w", newline="", encoding="UTF-8"
    ) as csv_file:
        export_writer = csv.writer(
            csv_file, quotechar='"', quoting=csv.QUOTE_NONNUMERIC, delimiter=","
        )
        for row in rows_to_be_saved:
            export_writer.writerow(row)


@login_required
@permission_required("experiment.view_researchproject")
def load_group_goalkeeper_game_data(request, group_id):
    group = get_object_or_404(Group, id=group_id)

    if not group.code:
        messages.info(request, _("No group code configured."))
    else:
        institution = (
            LocalInstitution.get_solo().code if LocalInstitution.get_solo().code else ""
        )

        number_of_imported_data = 0
        list_of_paths = create_list_of_trees(
            group.experimental_protocol, "digital_game_phase"
        )

        # for each phase
        for path in list_of_paths:
            digital_game_phase_configuration = ComponentConfiguration.objects.get(
                pk=path[-1][0]
            )

            data_configuration_tree_id = list_data_configuration_tree(
                digital_game_phase_configuration.id, [item[0] for item in path]
            )

            if data_configuration_tree_id:
                data_configuration_tree = get_object_or_404(
                    DataConfigurationTree, pk=data_configuration_tree_id
                )
                if data_configuration_tree.code is not None:
                    try:
                        game_and_phase = GoalkeeperPhase.objects.get(
                            pk=data_configuration_tree.code
                        )
                    except:
                        game_and_phase = None

                    game = None
                    phase = None

                    if game_and_phase:
                        game = game_and_phase.game.code
                        phase = game_and_phase.phase

                        if phase == None:
                            phase = 0

                    # Create the folder to temporarily store the csv files to be saved as participant data collection
                    errors, path_to_goalkeeper_files = create_directory(
                        settings.MEDIA_ROOT, "temp_goalkeepergames"
                    )

                    # for each subject
                    for subject_of_group in group.subjectofgroup_set.all():
                        goalkeeper_games = (
                            GoalkeeperGameConfig.objects.using("goalkeeper")
                            .filter(
                                groupcode=group.code,
                                institution=institution,
                                game=game,
                                phase=phase,
                                playeralias=subject_of_group.subject.patient.code,
                            )
                            .order_by("idconfig")
                        )

                        if goalkeeper_games:
                            for goalkeeper_game_configuration in goalkeeper_games:
                                results = (
                                    GoalkeeperGameResults.objects.using("goalkeeper")
                                    .filter(
                                        idconfig=goalkeeper_game_configuration.idconfig
                                    )
                                    .all()
                                )

                                if results:
                                    game_date = datetime.strptime(
                                        goalkeeper_game_configuration.gamedata, "%y%m%d"
                                    )
                                    game_time = datetime.strptime(
                                        goalkeeper_game_configuration.gametime, "%H%M%S"
                                    )

                                    if not DigitalGamePhaseData.objects.filter(
                                        subject_of_group=subject_of_group,
                                        data_configuration_tree=data_configuration_tree,
                                        date=game_date,
                                        time=game_time,
                                    ):
                                        # saving data
                                        digital_game_phase_data = DigitalGamePhaseData()
                                        digital_game_phase_data.subject_of_group = (
                                            subject_of_group
                                        )
                                        digital_game_phase_data.data_configuration_tree = (
                                            data_configuration_tree
                                        )

                                        digital_game_phase_data.date = game_date
                                        digital_game_phase_data.time = game_time

                                        if game == "AQ":
                                            digital_game_phase_data.description = _(
                                                "Team or structure: %s \nGame code: %s \nParticipant: %s"
                                            ) % (
                                                goalkeeper_game_configuration.soccerteam,
                                                game,
                                                subject_of_group.subject.patient.code,
                                            )
                                        else:
                                            digital_game_phase_data.description = _(
                                                "Team or structure: %s\nGame code: %s\nPhase: %s\nParticipant: %s"
                                            ) % (
                                                goalkeeper_game_configuration.soccerteam,
                                                game,
                                                phase,
                                                subject_of_group.subject.patient.code,
                                            )

                                        digital_game_phase_data.file_format = (
                                            get_object_or_404(
                                                FileFormat, nes_code="other"
                                            )
                                        )

                                        digital_game_phase_data.sequence_used_in_context_tree = (
                                            goalkeeper_game_configuration.sequexecuted
                                        )

                                        digital_game_phase_data.save()

                                        # Digital Game Phase File
                                        file_name = "%s_%s.csv" % (
                                            group.code,
                                            subject_of_group.subject.patient.code,
                                        )

                                        complete_file_name = os.path.join(
                                            path_to_goalkeeper_files, file_name
                                        )

                                        # CSV to be stored as data collection of the participant
                                        create_csv_for_goalkeeper(
                                            complete_file_name,
                                            goalkeeper_game_configuration,
                                            results,
                                        )

                                        with open(complete_file_name, "r") as file:
                                            file_content = file.read()

                                        digital_game_phase_file = DigitalGamePhaseFile(
                                            digital_game_phase_data=digital_game_phase_data
                                        )
                                        digital_game_phase_file.file.save(
                                            file_name, ContentFile(file_content)
                                        )
                                        digital_game_phase_file.save()

                                        number_of_imported_data += 1

                                        # Delete the temporary file created
                                        os.remove(complete_file_name)

                    # Remove directory where the files of each subject were temporarily stored
                    os.rmdir(path_to_goalkeeper_files)

        if number_of_imported_data:
            if number_of_imported_data == 1:
                messages.success(request, _("1 new play was imported."))
            else:
                messages.success(
                    request,
                    _("%s new plays were imported.") % (str(number_of_imported_data)),
                )
        else:
            messages.info(request, _("No new data loaded."))

    redirect_url = reverse("group_goalkeeper_game_data", args=(group_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.view_researchproject")
def subject_generic_data_collection_view(
    request,
    group_id,
    subject_id,
    template_name="experiment/subject_generic_data_collection_collection_list.html",
):
    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)

    generic_data_collection_collections = []

    list_of_paths = create_list_of_trees(
        group.experimental_protocol, "generic_data_collection"
    )

    subject_of_group = get_object_or_404(SubjectOfGroup, group=group, subject=subject)

    for path in list_of_paths:
        generic_data_collection_configuration = ComponentConfiguration.objects.get(
            pk=path[-1][0]
        )

        data_configuration_tree_id = list_data_configuration_tree(
            generic_data_collection_configuration.id, [item[0] for item in path]
        )

        generic_data_collection_data_list = GenericDataCollectionData.objects.filter(
            subject_of_group=subject_of_group,
            data_configuration_tree__id=data_configuration_tree_id,
        )

        generic_data_collection_collections.append(
            {
                "generic_data_collection_configuration": generic_data_collection_configuration,
                "path": path,
                "generic_data_collection_data_list": generic_data_collection_data_list,
            }
        )

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "subject": subject,
        "generic_data_collection_collections": generic_data_collection_collections,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def subject_media_collection_view(
    request,
    group_id,
    subject_id,
    template_name="experiment/subject_media_collection_collection_list.html",
):
    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)

    media_collection_collections = []

    list_of_paths = create_list_of_trees(
        group.experimental_protocol, "media_collection"
    )

    subject_of_group = get_object_or_404(SubjectOfGroup, group=group, subject=subject)

    for path in list_of_paths:
        media_collection_configuration = ComponentConfiguration.objects.get(
            pk=path[-1][0]
        )

        data_configuration_tree_id = list_data_configuration_tree(
            media_collection_configuration.id, [item[0] for item in path]
        )

        media_collection_data_list = MediaCollectionData.objects.filter(
            subject_of_group=subject_of_group,
            data_configuration_tree__id=data_configuration_tree_id,
        )

        media_collection_collections.append(
            {
                "media_collection_configuration": media_collection_configuration,
                "path": path,
                "media_collection_data_list": media_collection_data_list,
            }
        )

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "subject": subject,
        "media_collection_collections": media_collection_collections,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def subject_media_collection_data_create(
    request,
    group_id,
    subject_id,
    media_collection_configuration_id,
    template_name="experiment/subject_media_collection_data_form.html",  #
):
    group = get_object_or_404(Group, id=group_id)

    list_of_path = [int(item) for item in media_collection_configuration_id.split("-")]
    media_collection_configuration_id = list_of_path[-1]

    check_can_change(request.user, group.experiment.research_project)

    media_collection_configuration_id = get_object_or_404(
        ComponentConfiguration, id=media_collection_configuration_id
    )

    redirect_url = None
    media_collection_data_id = None

    media_collection_data_form = MediaCollectionDataForm(
        None, initial={"experiment": group.experiment}
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            media_collection_data_form = MediaCollectionDataForm(
                request.POST, request.FILES
            )

            if media_collection_data_form.is_valid():
                data_configuration_tree_id = list_data_configuration_tree(
                    media_collection_configuration_id, list_of_path
                )
                if not data_configuration_tree_id:
                    data_configuration_tree_id = create_data_configuration_tree(
                        list_of_path
                    )

                subject = get_object_or_404(Subject, pk=subject_id)
                subject_of_group = get_object_or_404(
                    SubjectOfGroup, subject=subject, group_id=group_id
                )

                media_collection_data_added = media_collection_data_form.save(
                    commit=False
                )
                media_collection_data_added.subject_of_group = subject_of_group
                media_collection_data_added.component_configuration = (
                    media_collection_configuration_id
                )
                media_collection_data_added.data_configuration_tree_id = (
                    data_configuration_tree_id
                )

                # PS: it was necessary adding these 2 lines because Django raised, I do not why (Evandro),
                # the following error 'GenericDataCollectionData' object has no attribute 'group'
                media_collection_data_added.group = group
                media_collection_data_added.subject = subject

                media_collection_data_added.save()

                # saving uploaded files
                files_to_upload_list = request.FILES.getlist("media_collection_files")
                for file_to_upload in files_to_upload_list:
                    media_collection_file = MediaCollectionFile(
                        media_collection_data=media_collection_data_added,
                        file=file_to_upload,
                    )
                    media_collection_file.save()

                messages.success(
                    request, _("Generic data collection created successfully.")
                )

                redirect_url = reverse(
                    "media_collection_data_view",
                    args=(media_collection_data_added.id,),
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "creating": True,
        "editing": True,
        "group": group,
        "media_collection_configuration": media_collection_configuration_id,
        "media_collection_data_form": media_collection_data_form,
        "media_collection_data_id": media_collection_data_id,
        "subject": get_object_or_404(Subject, pk=subject_id),
        "URL": redirect_url,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def media_collection_data_view(
    request,
    media_collection_data_id,
    template_name="experiment/subject_media_collection_data_form.html",
):
    media_collection_data = get_object_or_404(
        MediaCollectionData, pk=media_collection_data_id
    )

    media_collection_data_form = MediaCollectionDataForm(
        request.POST or None, instance=media_collection_data
    )

    for field in media_collection_data_form.fields:
        media_collection_data_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            check_can_change(
                request.user,
                media_collection_data.subject_of_group.group.experiment.research_project,
            )

            subject_of_group = media_collection_data.subject_of_group

            # removing uploaded files
            for (
                media_collection_uploaded_file
            ) in media_collection_data.media_collection_files.all():
                media_collection_uploaded_file.file.delete()

            media_collection_data.delete()
            messages.success(request, _("Media collection removed successfully."))
            return redirect(
                "media_data_collection_view",
                group_id=subject_of_group.group_id,
                subject_id=subject_of_group.subject_id,
            )

    context = {
        "can_change": get_can_change(
            request.user,
            media_collection_data.subject_of_group.group.experiment.research_project,
        ),
        "editing": False,
        "group": media_collection_data.subject_of_group.group,
        "subject": media_collection_data.subject_of_group.subject,
        "media_collection_data_form": media_collection_data_form,
        "media_collection_data": media_collection_data,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def subject_generic_data_collection_data_create(
    request,
    group_id,
    subject_id,
    generic_data_collection_configuration_id,
    template_name="experiment/subject_generic_data_collection_data_form.html",
):
    group = get_object_or_404(Group, id=group_id)

    list_of_path = [
        int(item) for item in generic_data_collection_configuration_id.split("-")
    ]
    generic_data_collection_configuration_id = list_of_path[-1]

    check_can_change(request.user, group.experiment.research_project)

    generic_data_collection_configuration = get_object_or_404(
        ComponentConfiguration, id=generic_data_collection_configuration_id
    )

    redirect_url = None
    generic_data_collection_data_id = None

    generic_data_collection_data_form = GenericDataCollectionDataForm(
        None, initial={"experiment": group.experiment}
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            generic_data_collection_data_form = GenericDataCollectionDataForm(
                request.POST, request.FILES
            )

            if generic_data_collection_data_form.is_valid():
                data_configuration_tree_id = list_data_configuration_tree(
                    generic_data_collection_configuration_id, list_of_path
                )
                if not data_configuration_tree_id:
                    data_configuration_tree_id = create_data_configuration_tree(
                        list_of_path
                    )

                subject = get_object_or_404(Subject, pk=subject_id)
                subject_of_group = get_object_or_404(
                    SubjectOfGroup, subject=subject, group_id=group_id
                )

                generic_data_collection_data_added = (
                    generic_data_collection_data_form.save(commit=False)
                )
                generic_data_collection_data_added.subject_of_group = subject_of_group
                generic_data_collection_data_added.component_configuration = (
                    generic_data_collection_configuration
                )
                generic_data_collection_data_added.data_configuration_tree_id = (
                    data_configuration_tree_id
                )

                # PS: it was necessary adding these 2 lines because Django raised, I do not why (Evandro),
                # the following error 'GenericDataCollectionData' object has no attribute 'group'
                generic_data_collection_data_added.group = group
                generic_data_collection_data_added.subject = subject

                generic_data_collection_data_added.save()

                # saving uploaded files
                files_to_upload_list = request.FILES.getlist(
                    "generic_data_collection_files"
                )
                for file_to_upload in files_to_upload_list:
                    generic_data_collection_file = GenericDataCollectionFile(
                        generic_data_collection_data=generic_data_collection_data_added,
                        file=file_to_upload,
                    )
                    generic_data_collection_file.save()

                messages.success(
                    request, _("Generic data collection created successfully.")
                )

                redirect_url = reverse(
                    "generic_data_collection_data_view",
                    args=(generic_data_collection_data_added.id,),
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "creating": True,
        "editing": True,
        "group": group,
        "generic_data_collection_configuration": generic_data_collection_configuration,
        "generic_data_collection_data_form": generic_data_collection_data_form,
        "generic_data_collection_data_id": generic_data_collection_data_id,
        "subject": get_object_or_404(Subject, pk=subject_id),
        "URL": redirect_url,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def generic_data_collection_data_view(
    request,
    generic_data_collection_data_id,
    template_name="experiment/subject_generic_data_collection_data_form.html",
):
    generic_data_collection_data = get_object_or_404(
        GenericDataCollectionData, pk=generic_data_collection_data_id
    )

    generic_data_collection_data_form = GenericDataCollectionDataForm(
        request.POST or None, instance=generic_data_collection_data
    )

    for field in generic_data_collection_data_form.fields:
        generic_data_collection_data_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            check_can_change(
                request.user,
                generic_data_collection_data.subject_of_group.group.experiment.research_project,
            )

            subject_of_group = generic_data_collection_data.subject_of_group

            # removing uploaded files
            for (
                generic_data_collection_uploaded_file
            ) in generic_data_collection_data.generic_data_collection_files.all():
                generic_data_collection_uploaded_file.file.delete()

            generic_data_collection_data.delete()
            messages.success(
                request, _("Generic data collection removed successfully.")
            )
            return redirect(
                "subject_generic_data_collection_view",
                group_id=subject_of_group.group_id,
                subject_id=subject_of_group.subject_id,
            )

    context = {
        "can_change": get_can_change(
            request.user,
            generic_data_collection_data.subject_of_group.group.experiment.research_project,
        ),
        "editing": False,
        "group": generic_data_collection_data.subject_of_group.group,
        "subject": generic_data_collection_data.subject_of_group.subject,
        "generic_data_collection_data_form": generic_data_collection_data_form,
        "generic_data_collection_data": generic_data_collection_data,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def generic_data_collection_data_edit(request, generic_data_collection_data_id):
    generic_data_collection_data = get_object_or_404(
        GenericDataCollectionData, pk=generic_data_collection_data_id
    )

    check_can_change(
        request.user,
        generic_data_collection_data.subject_of_group.group.experiment.research_project,
    )

    if request.method == "POST" and request.POST["action"] == "save":
        generic_data_collection_data_form = GenericDataCollectionDataForm(
            request.POST, request.FILES, instance=generic_data_collection_data
        )

        has_changed = False

        if (
            generic_data_collection_data_form.is_valid()
            and generic_data_collection_data_form.has_changed()
        ):
            has_changed = True

            generic_data_collection_data_to_update = (
                generic_data_collection_data_form.save(commit=False)
            )
            generic_data_collection_data_to_update.group = (
                generic_data_collection_data.subject_of_group.group
            )
            generic_data_collection_data_to_update.subject = (
                generic_data_collection_data.subject_of_group.subject
            )
            generic_data_collection_data_to_update.save()

        # removing checked files
        for (
            current_generic_data_collection_file
        ) in generic_data_collection_data.generic_data_collection_files.all():
            if (
                "remove_generic_data_collection_file_"
                + str(current_generic_data_collection_file.id)
                in request.POST
            ):
                has_changed = True
                current_generic_data_collection_file.delete()

        # new files to upload
        files_to_upload_list = request.FILES.getlist("generic_data_collection_files")
        for file_to_upload in files_to_upload_list:
            has_changed = True
            generic_data_collection_file = GenericDataCollectionFile(
                generic_data_collection_data=generic_data_collection_data,
                file=file_to_upload,
            )
            generic_data_collection_file.save()

        if has_changed:
            messages.success(
                request, _("Generic data collection updated successfully.")
            )
        else:
            messages.success(request, _("There is no changes to save."))

        redirect_url = reverse(
            "generic_data_collection_data_view", args=(generic_data_collection_data_id,)
        )

        return HttpResponseRedirect(redirect_url)

    else:
        generic_data_collection_data_form = GenericDataCollectionDataForm(
            request.POST or None,
            instance=generic_data_collection_data,
            initial={
                "experiment": generic_data_collection_data.subject_of_group.group.experiment
            },
        )

    context = {
        "group": generic_data_collection_data.subject_of_group.group,
        "subject": generic_data_collection_data.subject_of_group.subject,
        "generic_data_collection_data_form": generic_data_collection_data_form,
        "generic_data_collection_data": generic_data_collection_data,
        "editing": True,
    }

    return render(
        request, "experiment/subject_generic_data_collection_data_form.html", context
    )


def get_pulse_stimulus_name(pulse_stimulus_type):
    pulse_stimulus_name = ""
    for type_element, type_name in TMSDeviceSetting.PULSE_STIMULUS_TYPES:
        if type_element == pulse_stimulus_type:
            pulse_stimulus_name = str(type_name)
            break
    return pulse_stimulus_name if pulse_stimulus_name else pulse_stimulus_type


@login_required
@permission_required("experiment.change_experiment")
def get_pulse_by_tms_setting(request, tms_setting_id):
    tms_setting = get_object_or_404(TMSSetting, pk=tms_setting_id)
    stimulus_name = get_pulse_stimulus_name(
        tms_setting.tms_device_setting.pulse_stimulus_type
    )

    response_data = {
        "type": tms_setting.tms_device_setting.pulse_stimulus_type,
        "name": stimulus_name,
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def tms_data_position_setting_register(
    request, tms_data_id, template_name="experiment/tms_data_position_setting.html"
):
    tms_data = get_object_or_404(TMSData, pk=tms_data_id)

    tms_step = get_object_or_404(
        TMS, id=tms_data.data_configuration_tree.component_configuration.component.id
    )

    check_can_change(
        request.user, tms_data.subject_of_group.group.experiment.research_project
    )

    localization_system_list = TMSLocalizationSystem.objects.all()

    # tms_position_list = TMSPosition.objects.all()

    hotspot_form = HotSpotForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if hotspot_form.is_valid() and "localization_system_selection":
                localization_system_val = request.POST["localization_system_selection"]
                localization_system = TMSLocalizationSystem.objects.get(
                    pk=localization_system_val.split(",")[0]
                )

                hotspot_to_update = hotspot_form.save(commit=False)
                hotspot_to_update.tms_localization_system = localization_system
                hotspot_to_update.tms_data = tms_data
                hotspot_to_update.save()
                # Se der erro aqui, como fazer reverse de tms_position????

                messages.success(request, _("TMS position updated successfully."))

            else:
                messages.success(request, _("There is no changes to save."))

            redirect_url = reverse(
                "tms_data_position_setting_view", args=(tms_data_id,)
            )
            return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "creating": True,
        "editing": True,
        "group": tms_data.subject_of_group.group,
        "subject": tms_data.subject_of_group.subject,
        "tms_data": tms_data,
        "tms_setting_default_id": tms_step.tms_setting_id,
        "tms_localization_system_list": localization_system_list,
        "hotspot_form": hotspot_form,
        "tab": "2",
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def tms_data_position_setting_view(
    request, tms_data_id, template_name="experiment/tms_data_position_setting.html"
):
    tms_data = get_object_or_404(TMSData, pk=tms_data_id)

    tms_step = get_object_or_404(
        TMS, id=tms_data.data_configuration_tree.component_configuration.component.id
    )

    check_can_change(
        request.user, tms_data.subject_of_group.group.experiment.research_project
    )

    if request.method == "POST":
        if request.POST["action"] == "remove":
            check_can_change(
                request.user,
                tms_data.subject_of_group.group.experiment.research_project,
            )

            subject_of_group = tms_data.subject_of_group
            tms_data.delete()
            messages.success(request, _("TMS data removed successfully."))
            return redirect(
                "subject_tms_view",
                group_id=subject_of_group.group_id,
                subject_id=subject_of_group.subject_id,
            )

    else:
        if hasattr(tms_data, "hotspot"):
            hotspot_form = HotSpotForm(request.POST or None, instance=tms_data.hotspot)

            localization_system_selected = get_object_or_404(
                TMSLocalizationSystem, pk=tms_data.hotspot.tms_localization_system_id
            )

        else:
            # hotspot_form = HotSpotForm(request.POST or None)
            # localization_system_selected = None
            redirect_url = reverse(
                "tms_data_position_setting_register", args=(tms_data_id,)
            )
            return HttpResponseRedirect(redirect_url)

        tms_localization_system_list = TMSLocalizationSystem.objects.all()

    context = {
        "can_change": get_can_change(
            request.user, tms_data.subject_of_group.group.experiment.research_project
        ),
        "editing": False,
        "creating": False,
        "group": tms_data.subject_of_group.group,
        "subject": tms_data.subject_of_group.subject,
        "tms_data": tms_data,
        "tms_setting_default_id": tms_step.tms_setting_id,
        "hotspot_form": hotspot_form,
        "tms_localization_system_list": tms_localization_system_list,
        "localization_system_selected": localization_system_selected,
        "tab": "2",
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_questionnaireresponse")
def data_collection_manage(
    request,
    group_id,
    path_of_configuration,
    data_type,
    template_name="experiment/data_collection_manage.html",
):
    group = get_object_or_404(Group, id=group_id)

    check_can_change(request.user, group.experiment.research_project)

    if path_of_configuration == "0":
        # related to the whole experiment
        component_configuration = None
        component_icon = icon_class["experimental_protocol"]
        data_configuration_tree_id = None
    else:
        list_of_path = [int(item) for item in path_of_configuration.split("-")]
        component_configuration = ComponentConfiguration.objects.get(
            id=int(list_of_path[-1])
        )
        component_icon = icon_class[component_configuration.component.component_type]
        data_configuration_tree_id = list_data_configuration_tree(
            list_of_path[-1], list_of_path
        )

    data_collections = []

    # get participants
    if data_type == "additional_data":
        data_collections = AdditionalData.objects.filter(
            subject_of_group__group=group,
            data_configuration_tree_id=data_configuration_tree_id,
        ).order_by("subject_of_group__subject__patient")
    elif data_type == "eeg":
        data_collections = EEGData.objects.filter(
            subject_of_group__group=group,
            data_configuration_tree_id=data_configuration_tree_id,
        ).order_by("subject_of_group__subject__patient")
    elif data_type == "emg":
        data_collections = EMGData.objects.filter(
            subject_of_group__group=group,
            data_configuration_tree_id=data_configuration_tree_id,
        ).order_by("subject_of_group__subject__patient")
    elif data_type == "tms":
        data_collections = TMSData.objects.filter(
            subject_of_group__group=group,
            data_configuration_tree_id=data_configuration_tree_id,
        ).order_by("subject_of_group__subject__patient")
    elif data_type == "digital_game_phase":
        data_collections = DigitalGamePhaseData.objects.filter(
            subject_of_group__group=group,
            data_configuration_tree_id=data_configuration_tree_id,
        ).order_by("subject_of_group__subject__patient")
    elif data_type == "questionnaire":
        data_collections = QuestionnaireResponse.objects.filter(
            subject_of_group__group=group,
            data_configuration_tree_id=data_configuration_tree_id,
        ).order_by("subject_of_group__subject__patient")
    elif data_type == "generic_data_collection":
        data_collections = GenericDataCollectionData.objects.filter(
            subject_of_group__group=group,
            data_configuration_tree_id=data_configuration_tree_id,
        ).order_by("subject_of_group__subject__patient")
    elif data_type == "media_collection":
        data_collections = MediaCollectionData.objects.filter(
            subject_of_group__group=group,
            data_configuration_tree_id=data_configuration_tree_id,
        ).order_by("subject_of_group__subject__patient")

    # in case of "transfer", get target candidates
    steps_to_transfer = get_data_collections_from_group(group, data_type)

    # read origin_survey once
    origin_survey = (
        Questionnaire.objects.get(id=component_configuration.component_id).survey
        if data_type == "questionnaire"
        else None
    )

    number_of_steps_to_transfer = 0
    for step_to_transfer in steps_to_transfer:
        step_to_transfer["show_step"] = True

        # do not show current path
        if path_of_configuration == "0":
            if not step_to_transfer["path"]:
                step_to_transfer["show_step"] = False
        else:
            if step_to_transfer["path"] and path_of_configuration.split("-") == [
                str(item[0]) for item in step_to_transfer["path"]
            ]:
                step_to_transfer["show_step"] = False

        if step_to_transfer["show_step"]:
            # if questionnaire, only show the same questionnaire
            if data_type == "questionnaire":
                if (
                    Questionnaire.objects.get(
                        id=ComponentConfiguration.objects.get(
                            id=step_to_transfer["path"][-1][0]
                        ).component_id
                    ).survey
                    != origin_survey
                ):
                    step_to_transfer["show_step"] = False

        if step_to_transfer["show_step"]:
            number_of_steps_to_transfer += 1

    if request.method == "POST":
        if request.POST["action"] == "remove":
            has_changed = False

            for data_collection in data_collections:
                checkbox_name = "data_collection_" + str(data_collection.id)
                if (
                    checkbox_name in request.POST
                    and request.POST[checkbox_name] == "on"
                ):
                    if data_type == "questionnaire":
                        questionnaire = Questionnaire.objects.get(
                            id=data_collection.data_configuration_tree.component_configuration.component_id
                        )
                        has_changed = delete_questionnaire_response(
                            questionnaire, data_collection
                        )

                    else:
                        if data_type == "additional_data":
                            for (
                                uploaded_file
                            ) in data_collection.additional_data_files.all():
                                uploaded_file.file.delete()
                        elif data_type == "eeg":
                            for uploaded_file in data_collection.eeg_files.all():
                                uploaded_file.file.delete()
                        elif data_type == "emg":
                            for uploaded_file in data_collection.emg_files.all():
                                uploaded_file.file.delete()
                        elif data_type == "digital_game_phase":
                            for (
                                uploaded_file
                            ) in data_collection.digital_game_phase_files.all():
                                uploaded_file.file.delete()
                        elif data_type == "generic_data_collection":
                            for (
                                uploaded_file
                            ) in data_collection.generic_data_collection_files.all():
                                uploaded_file.file.delete()
                        elif data_type == "media_collection":
                            for (
                                uploaded_file
                            ) in data_collection.media_collection_files.all():
                                uploaded_file.file.delete()

                        data_collection.delete()
                        has_changed = True

            if has_changed:
                messages.success(
                    request, _("Selected data collections were removed successfully.")
                )
            else:
                messages.info(request, _("There were no items selected to remove."))

            redirect_url = reverse("subjects", args=(group.id,))
            return HttpResponseRedirect(redirect_url + "?per_steps_tab=active")

        if request.POST["action"] == "transfer":
            data_configuration_tree = None

            if request.POST["transfer_to"]:
                if request.POST["transfer_to"] != "experimental_protocol":
                    list_of_path = [
                        item[0]
                        for item in steps_to_transfer[int(request.POST["transfer_to"])][
                            "path"
                        ]
                    ]

                    data_configuration_tree_id = list_data_configuration_tree(
                        list_of_path[-1], list_of_path
                    )
                    if not data_configuration_tree_id:
                        data_configuration_tree_id = create_data_configuration_tree(
                            list_of_path
                        )
                    data_configuration_tree = get_object_or_404(
                        DataConfigurationTree, pk=data_configuration_tree_id
                    )

            has_changed = False

            for data_collection in data_collections:
                checkbox_name = "data_collection_" + str(data_collection.id)
                if (
                    checkbox_name in request.POST
                    and request.POST[checkbox_name] == "on"
                ):
                    data_collection.data_configuration_tree = data_configuration_tree
                    data_collection.save()
                    has_changed = True

            if has_changed:
                messages.success(
                    request,
                    _("Selected data collections were transfered successfully."),
                )
            else:
                messages.info(request, _("There were no items selected to transfer."))

            redirect_url = reverse("subjects", args=(group.id,))
            return HttpResponseRedirect(redirect_url + "?per_steps_tab=active")

    context = {
        "group": group,
        "data_type": data_type,
        "data_type_name": data_type_name[data_type],
        "path_of_configuration": path_of_configuration,
        "component_configuration": component_configuration,
        "component_icon": component_icon,
        "data_collections": data_collections,
        "steps_to_transfer": steps_to_transfer,
        "number_of_steps_to_transfer": number_of_steps_to_transfer,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def subject_emg_view(
    request,
    group_id,
    subject_id,
    template_name="experiment/subject_emg_collection_list.html",
):
    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)

    emg_collections = []

    list_of_paths = create_list_of_trees(group.experimental_protocol, "emg")

    subject_of_group = get_object_or_404(SubjectOfGroup, group=group, subject=subject)

    for path in list_of_paths:
        emg_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])

        data_configuration_tree_id = list_data_configuration_tree(
            emg_configuration.id, [item[0] for item in path]
        )

        emg_data_list = EMGData.objects.filter(
            subject_of_group=subject_of_group,
            data_configuration_tree__id=data_configuration_tree_id,
        )

        emg_collections.append(
            {
                "emg_configuration": emg_configuration,
                "path": path,
                "emg_data_list": emg_data_list,
            }
        )

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "subject": subject,
        "emg_collections": emg_collections,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_questionnaireresponse")
def subject_emg_data_create(
    request,
    group_id,
    subject_id,
    emg_configuration_id,
    template_name="experiment/subject_emg_data_form.html",
):
    group = get_object_or_404(Group, id=group_id)

    list_of_path = [int(item) for item in emg_configuration_id.split("-")]
    emg_configuration_id = list_of_path[-1]

    check_can_change(request.user, group.experiment.research_project)

    emg_configuration = get_object_or_404(
        ComponentConfiguration, id=emg_configuration_id
    )
    emg_step = get_object_or_404(EMG, id=emg_configuration.component_id)

    redirect_url = None
    emg_data_id = None

    emg_data_form = EMGDataForm(
        None,
        initial={
            "experiment": group.experiment,
            "emg_setting": emg_step.emg_setting_id,
        },
    )

    file_format_list = file_format_code("EMG")

    if request.method == "POST":
        if request.POST["action"] == "save":
            emg_data_form = EMGDataForm(request.POST, request.FILES)

            if emg_data_form.is_valid():
                data_configuration_tree_id = list_data_configuration_tree(
                    emg_configuration_id, list_of_path
                )
                if not data_configuration_tree_id:
                    data_configuration_tree_id = create_data_configuration_tree(
                        list_of_path
                    )

                subject = get_object_or_404(Subject, pk=subject_id)
                subject_of_group = get_object_or_404(
                    SubjectOfGroup, subject=subject, group_id=group_id
                )

                emg_data_added = emg_data_form.save(commit=False)
                emg_data_added.subject_of_group = subject_of_group
                emg_data_added.component_configuration = emg_configuration
                emg_data_added.data_configuration_tree_id = data_configuration_tree_id

                # PS: it was necessary adding these 2 lines because Django raised, I do not why (Evandro),
                # the following error 'EMGData' object has no attribute 'group'
                emg_data_added.group = group
                emg_data_added.subject = subject

                emg_data_added.save()

                # saving uploaded files
                files_to_upload_list = request.FILES.getlist("emg_files")
                for file_to_upload in files_to_upload_list:
                    emg_file = EMGFile(emg_data=emg_data_added, file=file_to_upload)
                    emg_file.save()

                messages.success(
                    request, _("EMG data collection created successfully.")
                )

                redirect_url = reverse("emg_data_view", args=(emg_data_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "creating": True,
        "editing": True,
        "group": group,
        "emg_configuration": emg_configuration,
        "emg_data_form": emg_data_form,
        "emg_data_id": emg_data_id,
        "file_format_list": file_format_list,
        "emg_setting_default_id": emg_step.emg_setting_id,
        "subject": get_object_or_404(Subject, pk=subject_id),
        "URL": redirect_url,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_data_view(
    request, emg_data_id, template_name="experiment/subject_emg_data_form.html"
):
    emg_data = get_object_or_404(EMGData, pk=emg_data_id)
    emg_step = get_object_or_404(
        EMG, id=emg_data.data_configuration_tree.component_configuration.component.id
    )

    emg_data_form = EMGDataForm(request.POST or None, instance=emg_data)

    for field in emg_data_form.fields:
        emg_data_form.fields[field].widget.attrs["disabled"] = True

    file_format_list = file_format_code("EMG")

    if request.method == "POST":
        if request.POST["action"] == "remove":
            check_can_change(
                request.user,
                emg_data.subject_of_group.group.experiment.research_project,
            )

            subject_of_group = emg_data.subject_of_group

            # removing uploaded files
            for emg_uploaded_file in emg_data.emg_files.all():
                emg_uploaded_file.file.delete()

            emg_data.delete()
            messages.success(request, _("EMG data removed successfully."))
            return redirect(
                "subject_emg_view",
                group_id=subject_of_group.group_id,
                subject_id=subject_of_group.subject_id,
            )

    context = {
        "can_change": get_can_change(
            request.user, emg_data.subject_of_group.group.experiment.research_project
        ),
        "editing": False,
        "group": emg_data.subject_of_group.group,
        "subject": emg_data.subject_of_group.subject,
        "emg_data_form": emg_data_form,
        "emg_data": emg_data,
        "file_format_list": file_format_list,
        "emg_setting_default_id": emg_step.emg_setting_id,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_data_edit(
    request, emg_data_id, template_name="experiment/subject_emg_data_form.html"
):
    emg_data = get_object_or_404(EMGData, pk=emg_data_id)
    emg_step = get_object_or_404(
        EMG, id=emg_data.data_configuration_tree.component_configuration.component.id
    )

    check_can_change(
        request.user, emg_data.subject_of_group.group.experiment.research_project
    )

    if request.method == "POST":
        emg_data_form = EMGDataForm(request.POST, request.FILES, instance=emg_data)

        if request.POST["action"] == "save":
            if emg_data_form.is_valid():
                has_changed = False

                if emg_data_form.has_changed():
                    has_changed = True

                    emg_data_to_update = emg_data_form.save(commit=False)
                    emg_data_to_update.group = emg_data.subject_of_group.group
                    emg_data_to_update.subject = emg_data.subject_of_group.subject
                    emg_data_to_update.save()

                # removing checked files
                for current_emg_file in emg_data.emg_files.all():
                    if "remove_emg_file_" + str(current_emg_file.id) in request.POST:
                        has_changed = True
                        current_emg_file.delete()

                # new files to upload
                files_to_upload_list = request.FILES.getlist("emg_files")
                for file_to_upload in files_to_upload_list:
                    has_changed = True
                    emg_file = EMGFile(emg_data=emg_data, file=file_to_upload)
                    emg_file.save()

                if has_changed:
                    messages.success(request, _("EMG data updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("emg_data_view", args=(emg_data_id,))
                return HttpResponseRedirect(redirect_url)

    else:
        emg_data_form = EMGDataForm(
            request.POST or None,
            instance=emg_data,
            initial={"experiment": emg_data.subject_of_group.group.experiment},
        )

    file_format_list = file_format_code("EMG")

    context = {
        "group": emg_data.subject_of_group.group,
        "subject": emg_data.subject_of_group.subject,
        "emg_data_form": emg_data_form,
        "emg_data": emg_data,
        "file_format_list": file_format_list,
        "emg_setting_default_id": emg_step.emg_setting_id,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def subject_additional_data_view(
    request,
    group_id,
    subject_id,
    template_name="experiment/additional_data_collection_list.html",
):
    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, id=subject_id)
    subject_of_group = get_object_or_404(SubjectOfGroup, group=group, subject=subject)

    # First element of the list is associated to the whole experimental protocol
    subject_step_data_query = SubjectStepData.objects.filter(
        subject_of_group=subject_of_group, data_configuration_tree=None
    )
    data_collections = [
        {
            "component_configuration": None,
            "path": None,
            "subject_step_data": subject_step_data_query[0]
            if subject_step_data_query
            else None,
            "additional_data_list": AdditionalData.objects.filter(
                subject_of_group=subject_of_group, data_configuration_tree=None
            ),
            "icon_class": icon_class["experimental_protocol"],
        }
    ]

    list_of_paths = create_list_of_trees(group.experimental_protocol, None)

    for path in list_of_paths:
        component_configuration = ComponentConfiguration.objects.get(pk=path[-1][0])

        data_configuration_tree_id = list_data_configuration_tree(
            component_configuration.id, [item[0] for item in path]
        )

        subject_step_data_query = SubjectStepData.objects.filter(
            subject_of_group=subject_of_group,
            data_configuration_tree=data_configuration_tree_id,
        )

        additional_data_list = None
        if data_configuration_tree_id:
            additional_data_list = AdditionalData.objects.filter(
                subject_of_group=subject_of_group,
                data_configuration_tree__id=data_configuration_tree_id,
            )

        data_collections.append(
            {
                "component_configuration": component_configuration,
                "path": path,
                "subject_step_data": subject_step_data_query[0]
                if subject_step_data_query
                else None,
                "additional_data_list": additional_data_list,
                "icon_class": icon_class[
                    component_configuration.component.component_type
                ],
            }
        )

    context = {
        "can_change": get_can_change(request.user, group.experiment.research_project),
        "group": group,
        "subject": subject,
        "data_collections": data_collections,
    }

    return render(request, template_name, context)


def get_subgraph(tree, node_identifier=""):
    block = get_object_or_404(Block, id=tree["component"].id)

    first_node = None
    last_node = None

    # create a subgraph
    subgraph = pydot.Cluster(
        graph_name="subgraph_" + node_identifier,
        label=(tree["numeration"] + " - " if tree["numeration"] else "")
        + block.identification,
        labeljust="left",
        pencolor="#757575",
    )

    # Paralel blocks have additional start and end points
    if block.type == Block.PARALLEL_BLOCK:
        # create start and end points
        start_node = pydot.Node(
            "start_" + node_identifier,
            label="",
            style="filled",
            shape="diamond",
            fillcolor="turquoise4",
            height=0.1,
            width=0.1,
        )
        end_node = pydot.Node(
            "end_" + node_identifier,
            label="",
            style="filled",
            shape="diamond",
            fillcolor="turquoise4",
            height=0.1,
            width=0.1,
        )
        subgraph.add_node(start_node)
        subgraph.add_node(end_node)

        # defining first and last nodes
        first_node = start_node
        last_node = end_node

    # For each use of step
    previous_node = None
    for component_configuration_item in tree["list_of_component_configuration"]:
        # get the component
        component = component_configuration_item["component"]["component"]

        # create node or subgraph
        if component.component_type == "block":
            new_subgraph, new_first_node, new_last_node = get_subgraph(
                component_configuration_item["component"],
                node_identifier + "_" + str(component_configuration_item["id"]),
            )
            subgraph.add_subgraph(new_subgraph)

            if block.type == Block.PARALLEL_BLOCK:
                subgraph.add_edge(pydot.Edge(start_node, new_first_node))
                subgraph.add_edge(pydot.Edge(new_last_node, end_node))
            else:
                if previous_node:
                    subgraph.add_edge(pydot.Edge(previous_node, new_first_node))
                previous_node = new_last_node

                last_node = new_last_node
                if not first_node:
                    first_node = new_first_node

        else:
            color_node = "gainsboro"
            if component.component_type == "instruction":
                color_node = "AntiqueWhite1"
            elif component.component_type == "questionnaire":
                color_node = "PaleGreen2"
            elif component.component_type == "stimulus":
                color_node = "tan1"
            elif component.component_type == "task":
                color_node = "#ffffba"
            elif component.component_type == "task_experiment":
                color_node = "#f9d62e"
            elif component.component_type == "eeg":
                color_node = "#99ccff"
            elif component.component_type == "emg":
                color_node = "#f1cbff"
            elif component.component_type == "tms":
                color_node = "#fe8181"
            elif component.component_type == "digital_game_phase":
                color_node = "#80ced6"
            elif component.component_type == "generic_data_collection":
                color_node = "LightPink"
            elif component.component_type == "media_collection":
                color_node = "LightPink"

            new_node = pydot.Node(
                "node_"
                + node_identifier
                + "_"
                + str(component_configuration_item["id"]),
                label=split_node_identification_for_graph(
                    component_configuration_item["component"]["numeration"]
                    + " - "
                    + component.identification
                    + " ("
                    + get_component_name(component.component_type)
                    + ")"
                ),
                style="filled",
                fillcolor=color_node,
                shape="rectangle",
            )

            subgraph.add_node(new_node)

            if block.type == Block.PARALLEL_BLOCK:
                subgraph.add_edge(pydot.Edge(start_node, new_node))
                subgraph.add_edge(pydot.Edge(new_node, end_node))
            else:
                if previous_node:
                    subgraph.add_edge(pydot.Edge(previous_node, new_node))
                previous_node = new_node

                last_node = new_node
                if not first_node:
                    first_node = new_node

    return subgraph, first_node, last_node


def split_node_identification_for_graph(identification):
    result = []
    current_line = ""

    for item in identification.split():
        if not current_line:
            current_line = item
        else:
            if len(current_line + item) > 15:
                result.append(current_line)
                current_line = item
            else:
                current_line += " " + item

    result.append(current_line)

    return "\n".join(result)


def get_experimental_protocol_image(experimental_protocol, tree, url=False):
    graph = pydot.Dot(graph_type="digraph")

    subgraph, first_node, last_node = get_subgraph(tree)
    graph.add_subgraph(subgraph)

    initial_node = pydot.Node(
        "initial_node", label="", style="filled", shape="circle", fillcolor="green"
    )
    ending_node = pydot.Node(
        "ending_node", label="", style="filled", shape="circle", fillcolor="red"
    )
    subgraph.add_node(initial_node)
    subgraph.add_node(ending_node)
    if first_node:
        subgraph.add_edge(pydot.Edge(initial_node, first_node))
    if last_node:
        subgraph.add_edge(pydot.Edge(last_node, ending_node))

    # graph file name
    file_name = "experimental_protocol_" + str(experimental_protocol.id) + ".png"

    # writing
    errors, path_complete = create_directory(settings.MEDIA_ROOT, "temp")

    try:
        graph.write_png(path.join(path_complete, file_name))
    except:
        return None

    return path.join(
        settings.MEDIA_URL if url else settings.MEDIA_ROOT, "temp", file_name
    )


def get_description_from_experimental_protocol_tree(
    component, component_configuration_attributes=[]
):
    description = (
        _("Step") + " " + component["numeration"]
        if component["numeration"]
        else _("Main step")
    )

    description += ": " + get_component_name(component["component_type"]) + "\n"

    # component attributes
    for attribute in component["attributes"]:
        for key in list(attribute.keys()):
            description += "\t-" + _(key) + ": " + str(attribute[key]) + "\n"

    # component configuration attributes
    for attribute in component_configuration_attributes:
        for key in list(attribute.keys()):
            description += "\t-" + _(key) + ": " + str(attribute[key]) + "\n"

    # Sub-steps
    num_of_sub_steps = len(component["list_of_component_configuration"])
    if num_of_sub_steps > 0:
        description += "\t-" + _("Sub-steps: (")
        for item in range(1, num_of_sub_steps + 1):
            description += (
                component["numeration"] + "." if component["numeration"] else ""
            ) + str(item)
            description += ", " if item != num_of_sub_steps else ""
        description += ")\n"

        counter = 1
        for component_configuration in component["list_of_component_configuration"]:
            description += get_description_from_experimental_protocol_tree(
                component_configuration["component"],
                component_configuration["component_configuration_attributes"],
            )
            counter += 1

    return description


def get_component_name(component_type):
    component_name = ""
    for type_element, type_name in Component.COMPONENT_TYPES:
        if type_element == component_type:
            component_name = str(type_name)
            break
    return component_name if component_name else component_type


def get_block_tree(component, language_code=None, numeration=""):
    attributes = get_component_attributes(component, language_code)

    list_of_component_configuration = []
    if component.component_type == "block":
        configurations = ComponentConfiguration.objects.filter(
            parent=component
        ).order_by("order")
        counter = 1
        for configuration in configurations:
            component_configuration_attributes = get_component_configuration_attributes(
                configuration
            )
            component_info = get_block_tree(
                configuration.component,
                language_code,
                (numeration + "." if numeration else "") + str(counter),
            )
            list_of_component_configuration.append(
                {
                    "component_configuration_attributes": component_configuration_attributes,
                    "component": component_info,
                    "id": configuration.id,
                }
            )
            counter += 1

    return {
        "identification": component.identification,
        "component_type": component.component_type,
        "attributes": attributes,
        "list_of_component_configuration": list_of_component_configuration,
        "numeration": numeration,
        "component": component,
    }


def get_component_attributes(component, language_code):
    attributes = []
    for attribute in get_general_component_attributes(component):
        attributes.append(attribute)

    specific_attributes = []
    if component.component_type == "block":
        specific_attributes = get_block_component_attributes(component)
    elif component.component_type == "instruction":
        specific_attributes = get_instruction_component_attributes(component)
    elif component.component_type == "pause":
        specific_attributes = []
    elif component.component_type == "questionnaire":
        specific_attributes = get_questionnaire_component_attributes(
            component, language_code
        )
    elif component.component_type == "stimulus":
        specific_attributes = get_stimulus_component_attributes(component)
    elif component.component_type == "task":
        specific_attributes = []
    elif component.component_type == "task_experiment":
        specific_attributes = []
    elif component.component_type == "eeg":
        specific_attributes = []
    elif component.component_type == "emg":
        specific_attributes = []
    elif component.component_type == "tms":
        specific_attributes = []
    elif component.component_type == "digital_game_phase":
        specific_attributes = []
    elif component.component_type == "generic_data_collection":
        specific_attributes = []
    elif component.component_type == "media_collection":
        specific_attributes = []

    for attribute in specific_attributes:
        attributes.append(attribute)

    return attributes


def get_general_component_attributes(component):
    attributes = [{_("Identification"): component.identification}]
    if component.description:
        attributes.append({_("Description"): component.description})
    if component.duration_value:
        attributes.append({_("Duration value"): component.duration_value})
        if component.duration_unit:
            attributes.append({_("Duration unit"): component.duration_unit})
    return attributes


def get_block_component_attributes(component):
    block = get_object_or_404(Block, id=component.id)
    attributes = [{_("Type"): get_block_type_name(block.type)}]
    if block.number_of_mandatory_components:
        attributes.append(
            {_("Number of mandatory components"): block.number_of_mandatory_components}
        )
    return attributes


def get_instruction_component_attributes(component):
    instruction = get_object_or_404(Instruction, id=component.id)
    attributes = [{_("Text"): instruction.text}]
    return attributes


def get_questionnaire_component_attributes(component, language_code):
    questionnaire = get_object_or_404(Questionnaire, id=component.id)
    attributes = [{_("LimeSurvey ID"): questionnaire.survey.lime_survey_id}]

    questionnaire_title = find_questionnaire_name(questionnaire.survey, language_code)[
        "name"
    ]

    attributes.append({_("Questionnaire title"): questionnaire_title})

    return attributes


def get_stimulus_component_attributes(component):
    stimulus = get_object_or_404(Stimulus, id=component.id)
    attributes = [{_("Stimulus type"): stimulus.stimulus_type.name}]
    if stimulus.media_file:
        attributes.append({_("Media file"): stimulus.media_file})
    return attributes


def get_block_type_name(block_type):
    block_type_name = ""
    for type_element, type_name in Block.BLOCK_TYPES:
        if type_element == block_type:
            block_type_name = str(type_name)
            break
    return block_type_name if block_type_name else block_type


def get_component_configuration_attributes(configuration):
    attributes = []
    if configuration.name:
        attributes.append({_("Name of use"): configuration.name})

    attributes.append(
        {
            _("Number of repetitions"): configuration.number_of_repetitions
            if configuration.number_of_repetitions
            else _("Unlimited")
        }
    )

    if configuration.interval_between_repetitions_value:
        attributes.append(
            {
                _(
                    "Interval between repetitions value"
                ): configuration.interval_between_repetitions_value
            }
        )
        if configuration.interval_between_repetitions_unit:
            attributes.append(
                {
                    _(
                        "Interval between repetitions unit"
                    ): configuration.interval_between_repetitions_unit
                }
            )
    attributes.append({_("Order"): configuration.order})
    attributes.append(
        {
            _("Position in the set of steps "): _("Random")
            if configuration.random_position
            else _("Fixed")
        }
    )
    attributes.append(
        {
            _("Requires start and end datetime"): _("Yes")
            if configuration.requires_start_and_end_datetime
            else _("No")
        }
    )

    return attributes


@login_required
@permission_required("experiment.add_questionnaireresponse")
def subject_additional_data_create(
    request,
    group_id,
    subject_id,
    path_of_configuration,
    template_name="experiment/subject_additional_data_form.html",
):
    group = get_object_or_404(Group, id=group_id)

    check_can_change(request.user, group.experiment.research_project)

    additional_data_form = AdditionalDataForm(None)

    file_format_list = file_format_code()

    if request.method == "POST":
        if request.POST["action"] == "save":
            additional_data_form = AdditionalDataForm(request.POST, request.FILES)

            if additional_data_form.is_valid():
                data_configuration_tree = None
                if path_of_configuration != "0":
                    list_of_path = [
                        int(item) for item in path_of_configuration.split("-")
                    ]
                    data_configuration_tree_id = list_data_configuration_tree(
                        list_of_path[-1], list_of_path
                    )
                    if not data_configuration_tree_id:
                        data_configuration_tree_id = create_data_configuration_tree(
                            list_of_path
                        )
                    data_configuration_tree = get_object_or_404(
                        DataConfigurationTree, pk=data_configuration_tree_id
                    )

                subject = get_object_or_404(Subject, pk=subject_id)
                subject_of_group = get_object_or_404(
                    SubjectOfGroup, subject=subject, group_id=group_id
                )

                additional_data_added = additional_data_form.save(commit=False)
                additional_data_added.subject_of_group = subject_of_group
                if data_configuration_tree:
                    additional_data_added.data_configuration_tree = (
                        data_configuration_tree
                    )

                # PS: it was necessary adding these 2 lines because Django raised, I do not why (Evandro),
                # the following error 'AdditionalData' object has no attribute 'group'
                additional_data_added.group = group
                additional_data_added.subject = subject

                additional_data_added.save()

                # saving uploaded files
                files_to_upload_list = request.FILES.getlist("additional_data_files")
                for file_to_upload in files_to_upload_list:
                    additional_data_file = AdditionalDataFile(
                        additional_data=additional_data_added, file=file_to_upload
                    )
                    additional_data_file.save()

                messages.success(
                    request, _("Additional data collection created successfully.")
                )

                redirect_url = reverse(
                    "additional_data_view", args=(additional_data_added.id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "creating": True,
        "editing": True,
        "group": group,
        "additional_data_form": additional_data_form,
        "file_format_list": file_format_list,
        "subject": get_object_or_404(Subject, pk=subject_id),
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def additional_data_view(
    request,
    additional_data_id,
    template_name="experiment/subject_additional_data_form.html",
):
    additional_data = get_object_or_404(AdditionalData, pk=additional_data_id)
    additional_data_form = AdditionalDataForm(
        request.POST or None, instance=additional_data
    )

    for field in additional_data_form.fields:
        additional_data_form.fields[field].widget.attrs["disabled"] = True

    file_format_list = file_format_code()

    if request.method == "POST":
        if request.POST["action"] == "remove":
            check_can_change(
                request.user,
                additional_data.subject_of_group.group.experiment.research_project,
            )

            subject_of_group = additional_data.subject_of_group

            # removing uploaded files
            for (
                additional_data_uploaded_file
            ) in additional_data.additional_data_files.all():
                additional_data_uploaded_file.file.delete()

            additional_data.delete()
            messages.success(request, _("Additional data removed successfully."))
            return redirect(
                "subject_additional_data_view",
                group_id=subject_of_group.group_id,
                subject_id=subject_of_group.subject_id,
            )

    context = {
        "can_change": get_can_change(
            request.user,
            additional_data.subject_of_group.group.experiment.research_project,
        ),
        "editing": False,
        "group": additional_data.subject_of_group.group,
        "subject": additional_data.subject_of_group.subject,
        "additional_data_form": additional_data_form,
        "additional_data": additional_data,
        "file_format_list": file_format_list,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def additional_data_edit(
    request,
    additional_data_id,
    template_name="experiment/subject_additional_data_form.html",
):
    additional_data = get_object_or_404(AdditionalData, pk=additional_data_id)

    file_format_list = file_format_code()

    check_can_change(
        request.user, additional_data.subject_of_group.group.experiment.research_project
    )

    if request.method == "POST":
        additional_data_form = AdditionalDataForm(
            request.POST, request.FILES, instance=additional_data
        )

        if request.POST["action"] == "save":
            has_changed = False

            if additional_data_form.is_valid():
                if additional_data_form.has_changed():
                    has_changed = True

                    additional_data_to_update = additional_data_form.save(commit=False)
                    additional_data_to_update.group = (
                        additional_data.subject_of_group.group
                    )
                    additional_data_to_update.subject = (
                        additional_data.subject_of_group.subject
                    )
                    additional_data_to_update.save()

                # removing checked files
                for (
                    current_additional_data_file
                ) in additional_data.additional_data_files.all():
                    if (
                        "remove_additional_data_file_"
                        + str(current_additional_data_file.id)
                        in request.POST
                    ):
                        has_changed = True
                        current_additional_data_file.delete()

                # new files to upload
                files_to_upload_list = request.FILES.getlist("additional_data_files")
                for file_to_upload in files_to_upload_list:
                    has_changed = True
                    additional_data_file = AdditionalDataFile(
                        additional_data=additional_data, file=file_to_upload
                    )
                    additional_data_file.save()

                if has_changed:
                    messages.success(
                        request, _("Additional data updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "additional_data_view", args=(additional_data_id,)
                )
                return HttpResponseRedirect(redirect_url)

    else:
        additional_data_form = AdditionalDataForm(
            request.POST or None, instance=additional_data
        )

    context = {
        "group": additional_data.subject_of_group.group,
        "subject": additional_data.subject_of_group.subject,
        "additional_data_form": additional_data_form,
        "additional_data": additional_data,
        "file_format_list": file_format_list,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_questionnaireresponse")
def subject_step_data_create(
    request,
    group_id,
    subject_id,
    path_of_configuration,
    template_name="experiment/subject_step_data_form.html",
):
    group = get_object_or_404(Group, id=group_id)
    subject = get_object_or_404(Subject, pk=subject_id)

    subject_step_data_form = SubjectStepDataForm(None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            subject_step_data_form = SubjectStepDataForm(request.POST)

            if subject_step_data_form.is_valid():
                data_configuration_tree = None
                if path_of_configuration != "0":
                    list_of_path = [
                        int(item) for item in path_of_configuration.split("-")
                    ]
                    data_configuration_tree_id = list_data_configuration_tree(
                        list_of_path[-1], list_of_path
                    )
                    if not data_configuration_tree_id:
                        data_configuration_tree_id = create_data_configuration_tree(
                            list_of_path
                        )
                    data_configuration_tree = get_object_or_404(
                        DataConfigurationTree, pk=data_configuration_tree_id
                    )

                subject_of_group = get_object_or_404(
                    SubjectOfGroup, subject=subject, group=group
                )

                subject_step_data_added = subject_step_data_form.save(commit=False)
                subject_step_data_added.subject_of_group = subject_of_group
                if data_configuration_tree:
                    subject_step_data_added.data_configuration_tree = (
                        data_configuration_tree
                    )

                # PS: it was necessary adding these 2 lines because Django raised, I do not why (Evandro),
                # the following error 'AdditionalData' object has no attribute 'group'
                subject_step_data_added.group = group
                subject_step_data_added.subject = subject

                subject_step_data_added.save()

                messages.success(
                    request, _("Subject step data was created successfully.")
                )

                redirect_url = reverse(
                    "subject_additional_data_view",
                    args=(
                        group_id,
                        subject_id,
                    ),
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "creating": True,
        "editing": True,
        "group": group,
        "subject_step_data_form": subject_step_data_form,
        "subject": subject,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def subject_step_data_edit(
    request,
    subject_step_data_id,
    template_name="experiment/subject_step_data_form.html",
):
    subject_step_data = get_object_or_404(SubjectStepData, pk=subject_step_data_id)

    if request.method == "POST":
        subject_step_data_form = SubjectStepDataForm(
            request.POST, request.FILES, instance=subject_step_data
        )

        if request.POST["action"] == "save":
            if subject_step_data_form.is_valid():
                if subject_step_data_form.has_changed():
                    subject_step_data_to_update = subject_step_data_form.save(
                        commit=False
                    )
                    subject_step_data_to_update.group = (
                        subject_step_data.subject_of_group.group
                    )
                    subject_step_data_to_update.subject = (
                        subject_step_data.subject_of_group.subject
                    )
                    subject_step_data_to_update.save()

                    messages.success(
                        request, _("Subject step data updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "subject_additional_data_view",
                    args=(
                        subject_step_data.subject_of_group.group.id,
                        subject_step_data.subject_of_group.subject.id,
                    ),
                )
                return HttpResponseRedirect(redirect_url)

    else:
        subject_step_data_form = SubjectStepDataForm(
            request.POST or None, instance=subject_step_data
        )

    context = {
        "group": subject_step_data.subject_of_group.group,
        "subject": subject_step_data.subject_of_group.subject,
        "subject_step_data_form": subject_step_data_form,
        "subject_step_data": subject_step_data,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def get_cap_size_list_from_eeg_setting(request, eeg_setting_id):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)
    list_of_cap_size = EEGCapSize.objects.filter(id=0)
    if hasattr(eeg_setting, "eeg_electrode_layout_setting"):
        eeg_electrode_net_id = (
            eeg_setting.eeg_electrode_layout_setting.eeg_electrode_net_system.eeg_electrode_net.id
        )
        # if the electrode net is a cap
        if EEGElectrodeCap.objects.filter(id=eeg_electrode_net_id):
            list_of_cap_size = EEGCapSize.objects.filter(
                eeg_electrode_cap_id=eeg_electrode_net_id
            )
    json_cap_size = serializers.serialize("json", list_of_cap_size)
    return HttpResponse(json_cap_size, content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def set_worked_positions(request):
    worked_positions = json.loads(request.GET.get("positions"))

    for position in worked_positions:
        EEGElectrodePositionCollectionStatus.objects.filter(pk=position["id"]).update(
            worked=position["worked"]
        )

    json_response = []
    json_response.append(
        {
            "new": 128,
        }
    )
    return HttpResponse(json.dumps(json_response), content_type="application/json")


@login_required
@permission_required("experiment.add_subject")
def subjects_insert(request, group_id, patient_id):
    group = get_object_or_404(Group, id=group_id)

    check_can_change(request.user, group.experiment.research_project)

    patient = get_object_or_404(Patient, pk=patient_id)

    subject = Subject()

    try:
        subject = Subject.objects.get(patient=patient)
    except subject.DoesNotExist:
        subject.patient = patient
        subject.save()

    if not SubjectOfGroup.objects.filter(group=group, subject=subject):
        SubjectOfGroup(subject=subject, group=group).save()
    else:
        messages.warning(
            request, _("Participant has already been inserted in this group.")
        )

    redirect_url = reverse("subjects", args=(group_id,))
    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.view_researchproject")
def search_patients_ajax(request):
    patient_list = ""

    if request.method == "POST":
        search_text = request.POST["search_text"]
        group_id = request.POST["group_id"]

        if request.user.has_perm("patient.sensitive_data_patient"):
            if search_text:
                if re.match("P{1}[0-9]", search_text):
                    patient_list = (
                        Patient.objects.filter(code__icontains=search_text)
                        .exclude(removed=True)
                        .order_by("code")
                    )
                elif re.match("[a-zA-Z ]+", search_text):
                    patient_list = (
                        Patient.objects.filter(name__icontains=search_text)
                        .exclude(removed=True)
                        .order_by("name")
                    )
                else:
                    patient_list = (
                        Patient.objects.filter(cpf__icontains=search_text)
                        .exclude(removed=True)
                        .order_by("name")
                    )

                subjects_of_group = SubjectOfGroup.objects.filter(group_id=group_id)
                for subject in subjects_of_group:
                    if subject.subject.patient in patient_list:
                        patient_list = patient_list.exclude(
                            id=subject.subject.patient.id
                        )

            return render(
                None,
                "experiment/ajax_search_patients.html",
                {"patients": patient_list, "group_id": group_id},
            )
        else:
            if search_text:
                patient_list = (
                    Patient.objects.filter(code__iexact=search_text)
                    .exclude(removed=True)
                    .order_by("code")
                )

                subjects_of_group = SubjectOfGroup.objects.filter(group_id=group_id)
                for subject in subjects_of_group:
                    if subject.subject.patient in patient_list:
                        patient_list = patient_list.exclude(
                            id=subject.subject.patient.id
                        )

            return render(
                None,
                "experiment/ajax_search_patients_not_sensitive.html",
                {"patients": patient_list, "group_id": group_id},
            )


@login_required
@permission_required("experiment.change_experiment")
def upload_file(
    request, subject_id, group_id, template_name="experiment/upload_consent_form.html"
):
    group = get_object_or_404(Group, pk=group_id)

    check_can_change(request.user, group.experiment.research_project)

    subject = get_object_or_404(Subject, pk=subject_id)
    subject_of_group = get_object_or_404(SubjectOfGroup, subject=subject, group=group)

    file_form = None

    if request.method == "POST":
        if request.POST["action"] == "upload":
            file_form = FileForm(request.POST, request.FILES, instance=subject_of_group)
            if "consent_form" in request.FILES:
                if file_form.is_valid():
                    file_form.save()
                    messages.success(request, _("Consent term saved successfully."))

                redirect_url = reverse("subjects", args=(group_id,))
                return HttpResponseRedirect(redirect_url)
            else:
                messages.error(request, _("There are not attachments to save"))
        elif request.POST["action"] == "remove":
            subject_of_group.consent_form.delete()
            subject_of_group.save()
            messages.success(request, _("Attachment deleted successfully."))

            redirect_url = reverse("subjects", args=(group_id,))
            return HttpResponseRedirect(redirect_url)

    else:
        file_form = FileForm(request.POST or None)

    context = {
        "subject": subject,
        "group": group,
        "file_form": file_form,
        "file_list": subject_of_group.consent_form,
    }
    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def component_list(
    request, experiment_id, template_name="experiment/component_list.html"
):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    if request.method == "POST":
        if request.POST["action"] == "copy_experiment":
            copy_experiment(experiment)
            messages.success(request, _("The experiment was copied."))
            redirect_url = reverse("experiment_view", args=(experiment.id,))
            return HttpResponseRedirect(redirect_url)

    # As it is not possible to sort_by get_component_type_display, filter without sorting and sort later.
    components = Component.objects.filter(experiment=experiment)

    # Create a temporary list of tuples from the query_set to be able to sort by get_component_type_display,
    # identification and name.
    temp_list_of_tuples = []

    for component in components:
        temp_list_of_tuples.append(
            (
                component,
                component.get_component_type_display(),
                component.identification,
            )
        )

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
        component_type_choices.append(
            (type_element, type_name, icon_class.get(type_element))
        )

    context = {
        "can_change": get_can_change(request.user, experiment.research_project),
        "component_list": components,
        "component_type_choices": component_type_choices,
        "experiment": experiment,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def component_change_the_order(
    request, path_of_the_components, component_configuration_index, command
):
    # The last id of the list is the one for the current block.
    list_of_ids_of_components_and_configurations = path_of_the_components.split(
        delimiter
    )
    parent_block = get_object_or_404(
        Block, pk=list_of_ids_of_components_and_configurations[-1]
    )

    check_can_change(request.user, parent_block.experiment.research_project)

    configuration_list = create_configuration_list(parent_block)
    index_parts = component_configuration_index.split("-")
    position_of_the_accordion_to_be_moved = int(index_parts[0])

    if len(index_parts) == 2:  # Check the existence of an extra parameter
        # It means that a single component configuration should be moved
        position_in_accordion_of_the_conf_to_be_moved = int(index_parts[1])
        conf_to_move1 = configuration_list[position_of_the_accordion_to_be_moved][
            position_in_accordion_of_the_conf_to_be_moved
        ]
        conf_to_move1_order = conf_to_move1.order

        if command == "down":
            # First configuration that has an order greater than mine.
            conf_to_move2 = (
                ComponentConfiguration.objects.filter(parent=parent_block)
                .filter(order__gt=conf_to_move1_order)
                .order_by("order")[0]
            )
        else:
            # Last configuration that has an order less than mine.
            conf_to_move2 = (
                ComponentConfiguration.objects.filter(parent=parent_block)
                .filter(order__lt=conf_to_move1_order)
                .order_by("-order")[0]
            )

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
            conf_to_move2 = (
                ComponentConfiguration.objects.filter(parent=parent_block)
                .filter(order__gt=last)
                .order_by("order")[0]
            )

            accordion = reversed(
                configuration_list[position_of_the_accordion_to_be_moved]
            )
        else:
            first = configuration_list[position_of_the_accordion_to_be_moved][0].order

            # Last configuration that has an order less than first conf of the accordion.
            conf_to_move2 = (
                ComponentConfiguration.objects.filter(parent=parent_block)
                .filter(order__lt=first)
                .order_by("-order")[0]
            )

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


@login_required
@permission_required("experiment.change_experiment")
def component_create(request, experiment_id, component_type):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    can_change = get_can_change(request.user, experiment.research_project)

    template_name = "experiment/" + component_type + "_component.html"
    component_form = ComponentForm(request.POST or None)
    ###########################################################################
    # This is needed for the form to be able to validate the presence of a
    # duration in a pause component only. Since there is no creation of
    # components (Component) without being an inherited model, eg: 'stimulus',
    # 'instruction' etc., it does not make sense to create a ComponentForm
    # just for model use Pause. It would make more sense to create a PauseForm
    # as is the case for other types of components.

    component_form.component_type = component_type
    ###########################################################################
    questionnaires_list = []
    specific_form = None

    if component_type == "instruction":
        specific_form = InstructionForm(request.POST or None)
    elif component_type == "stimulus":
        specific_form = StimulusForm(request.POST or None, request.FILES)
    elif component_type == "eeg":
        specific_form = EEGForm(
            request.POST or None, initial={"experiment": experiment}
        )
    elif component_type == "emg":
        specific_form = EMGForm(
            request.POST or None, initial={"experiment": experiment}
        )
    elif component_type == "tms":
        specific_form = TMSForm(
            request.POST or None, initial={"experiment": experiment}
        )
    elif component_type == "questionnaire":
        questionnaires_list = Survey.objects.all()
    elif component_type == "block":
        specific_form = BlockForm(
            request.POST or None, initial={"number_of_mandatory_components": None}
        )
        # component_form.fields['duration_value'].widget.attrs['disabled'] = True
        # component_form.fields['duration_unit'].widget.attrs['disabled'] = True
    elif component_type == "digital_game_phase":
        specific_form = DigitalGamePhaseForm(
            request.POST or None, initial={"experiment": experiment}
        )
    elif component_type == "generic_data_collection":
        specific_form = GenericDataCollectionForm(request.POST or None)
    elif component_type == "media_collection":
        specific_form = MediaCollectionForm(request.POST or None)

    if request.method == "POST":
        new_specific_component = None

        if component_form.is_valid():
            if component_type == "questionnaire":
                surveys = Questionnaires()
                limesurvey_available = check_limesurvey_access(request, surveys)

                new_specific_component = Questionnaire()
                survey, created = Survey.objects.get_or_create(
                    lime_survey_id=request.POST["questionnaire_selected"]
                )
                if created:
                    survey.is_initial_evaluation = False

                if (
                    surveys.get_survey_properties(survey.lime_survey_id, "active")
                    == "Y"
                ):
                    new_specific_component.survey = survey
                else:
                    survey.is_active = False

                survey.save()
                new_specific_component.survey = survey
            elif component_type == "pause":
                new_specific_component = Pause()
            elif component_type == "task":
                new_specific_component = Task()
            elif component_type == "task_experiment":
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

                messages.success(request, _("Step included successfully."))

                if component_type == "block":
                    redirect_url = reverse(
                        "component_view", args=(new_specific_component.id,)
                    )
                else:
                    redirect_url = reverse("component_list", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

    questionnaires_with_names = []

    for questionnaire in questionnaires_list:
        questionnaires_with_names.append(
            {
                "sid": questionnaire.lime_survey_id,
                "name": find_questionnaire_name(questionnaire, request.LANGUAGE_CODE)[
                    "name"
                ],
            }
        )

    context = {
        "back_cancel_url": "/experiment/" + str(experiment.id) + "/components",
        "component_form": component_form,
        "creating": True,
        "can_change": can_change,
        "experiment": experiment,
        "questionnaires_list": questionnaires_with_names,
        "specific_form": specific_form,
    }
    return render(request, template_name, context)


def create_list_of_breadcrumbs(list_of_ids_of_components_and_configurations):
    # Create a list of components or component configurations to be able to
    # show the breadcrumb.
    list_of_breadcrumbs = []

    for idx, id_item in enumerate(list_of_ids_of_components_and_configurations):
        if id_item[0] != "G":
            # If id_item starts with 'U' (from 'use'), it is a configuration.
            if id_item[0] == "U":
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

            list_of_breadcrumbs.append(
                {
                    "name": name,
                    "url": reverse(
                        view_name,
                        args=(
                            delimiter.join(
                                list_of_ids_of_components_and_configurations[: idx + 1]
                            ),
                        ),
                    ),
                }
            )

    return list_of_breadcrumbs


def create_back_cancel_url(
    component_type,
    component_configuration,
    path_of_the_components,
    list_of_ids_of_components_and_configurations,
    experiment,
    updating,
):
    if component_type == "block" and component_configuration is None and updating:
        # Return to the screen for viewing a block
        back_cancel_url = "/experiment/component/" + path_of_the_components
    elif len(list_of_ids_of_components_and_configurations) > 1:
        # There is a parent. Remove the current element from the path so that the parent is shown.
        path_without_last = path_of_the_components[
            : path_of_the_components.rfind(delimiter)
        ]
        last_hyphen_index = path_without_last.rfind(delimiter)

        if last_hyphen_index == -1:
            parent = path_without_last
        else:
            parent = path_without_last[last_hyphen_index + 1 :]

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
        if unit == "y":
            return value * year_in_milliseconds
        if unit == "mon":
            return value * month_in_milliseconds
        if unit == "w":
            return value * week_in_milliseconds
        if unit == "d":
            return value * day_in_milliseconds
        if unit == "h":
            return value * hour_in_milliseconds
        if unit == "min":
            return value * minute_in_milliseconds
        if unit == "s":
            return value * second_in_milliseconds
        if unit == "ms":
            return value
        else:  # Unit is None or unknown
            return 0


def convert_to_string(duration_in_milliseconds):
    string = ""

    duration_in_years = int(duration_in_milliseconds / year_in_milliseconds)
    if duration_in_years >= 1:
        string += str(duration_in_years) + (
            _(" years ") if duration_in_years > 1 else _(" year ")
        )
        duration_in_milliseconds -= duration_in_years * year_in_milliseconds

    duration_in_months = int(duration_in_milliseconds / month_in_milliseconds)
    if duration_in_months >= 1:
        string += str(duration_in_months) + (
            _(" months ") if duration_in_months > 1 else _(" month ")
        )
        duration_in_milliseconds -= duration_in_months * month_in_milliseconds

    duration_in_weeks = int(duration_in_milliseconds / week_in_milliseconds)
    if duration_in_weeks >= 1:
        string += str(duration_in_weeks) + (
            _(" weeks ") if duration_in_weeks > 1 else _(" week ")
        )
        duration_in_milliseconds -= duration_in_weeks * week_in_milliseconds

    duration_in_days = int(duration_in_milliseconds / day_in_milliseconds)
    if duration_in_days >= 1:
        string += str(duration_in_days) + (
            _(" days ") if duration_in_days > 1 else _(" day ")
        )
        duration_in_milliseconds -= duration_in_days * day_in_milliseconds

    duration_in_hours = int(duration_in_milliseconds / hour_in_milliseconds)
    if duration_in_hours >= 1:
        string += str(duration_in_hours) + (
            _(" hours ") if duration_in_hours > 1 else _(" hour ")
        )
        duration_in_milliseconds -= duration_in_hours * hour_in_milliseconds

    duration_in_minutes = int(duration_in_milliseconds / minute_in_milliseconds)
    if duration_in_minutes >= 1:
        string += str(duration_in_minutes) + (
            _(" minutes ") if duration_in_minutes > 1 else _(" minute ")
        )
        duration_in_milliseconds -= duration_in_minutes * minute_in_milliseconds

    duration_in_seconds = int(duration_in_milliseconds / second_in_milliseconds)
    if duration_in_seconds >= 1:
        string += str(duration_in_seconds) + (
            _(" seconds ") if duration_in_seconds > 1 else _(" second ")
        )
        duration_in_milliseconds -= duration_in_seconds * second_in_milliseconds

    if duration_in_milliseconds >= 1:
        string += str(duration_in_milliseconds) + (
            _(" miliseconds ") if duration_in_milliseconds > 1 else _(" milisecond ")
        )

    if string == "":
        string = "0"
    else:
        # Add commas and 'and' to the string
        list_of_words = string.split(" ")
        values = list_of_words[::2]
        units = list_of_words[1::2]
        list_of_values_with_units = [
            value + " " + unit for value, unit in zip(values, units)
        ]
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

        if component.component_type == "block":
            component_duration, child_has_unlimited = calculate_block_duration(
                Block.objects.get(id=component.id)
            )

            if child_has_unlimited:
                has_unlimited = True
        else:
            component_duration = convert_to_milliseconds(
                component.duration_value, component.duration_unit
            )

        if component_configuration.number_of_repetitions is None:
            # Considers the duration of only one execution of the component, but notifies parent about this.
            has_unlimited = True
        else:
            interval_in_milliseconds = 0

            if component_configuration.interval_between_repetitions_value is not None:
                interval_in_milliseconds = convert_to_milliseconds(
                    component_configuration.interval_between_repetitions_value,
                    component_configuration.interval_between_repetitions_unit,
                )

            component_duration = (
                component_duration * component_configuration.number_of_repetitions
                + interval_in_milliseconds
                * (component_configuration.number_of_repetitions - 1)
            )

        if block.type == Block.SEQUENCE:
            # Add duration of the children
            duration_value_in_milliseconds += component_duration
        elif block.type == Block.PARALLEL_BLOCK:
            # Duration of the block is the duration of the longest child.
            if component_duration > duration_value_in_milliseconds:
                duration_value_in_milliseconds = component_duration

    return duration_value_in_milliseconds, has_unlimited


def access_objects_for_view_and_update(request, path_of_the_components, updating=False):
    list_of_ids_of_components_and_configurations = path_of_the_components.split(
        delimiter
    )

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
        component_configuration = get_object_or_404(
            ComponentConfiguration, pk=last_id[1:]
        )
        configuration_form = ComponentConfigurationForm(
            request.POST or None, instance=component_configuration
        )
        component = component_configuration.component
    else:
        component = get_object_or_404(Component, pk=last_id)

    component_form = ComponentForm(request.POST or None, instance=component)

    list_of_breadcrumbs = create_list_of_breadcrumbs(
        list_of_ids_of_components_and_configurations
    )

    experiment = component.experiment

    component_type = component.component_type
    template_name = "experiment/" + component_type + "_component.html"

    # This is needed for the form to be able to validate the presence of a duration in a pause component only.
    component_form.component_type = component_type

    back_cancel_url = create_back_cancel_url(
        component_type,
        component_configuration,
        path_of_the_components,
        list_of_ids_of_components_and_configurations,
        experiment,
        updating,
    )

    return (
        component,
        component_configuration,
        component_form,
        configuration_form,
        experiment,
        component_type,
        template_name,
        list_of_ids_of_components_and_configurations,
        list_of_breadcrumbs,
        group,
        back_cancel_url,
    )


def remove_component_and_related_configurations(
    component, list_of_ids_of_components_and_configurations, path_of_the_components
):
    # Before removing anything, we need to know where we should redirect to.

    if len(list_of_ids_of_components_and_configurations) == 1:
        # User is editing a component selected from the list of component of an exepriment.
        # Return to the list of components.
        redirect_url = "/experiment/" + str(component.experiment.id) + "/components"
    else:
        path_without_last = path_of_the_components[
            : path_of_the_components.rfind(delimiter)
        ]

        if len(list_of_ids_of_components_and_configurations) == 2:
            # User is viewing the block that is the root of an experimental protocol.
            # Return to the group.
            redirect_url = "/experiment/group/" + path_without_last[1:]
        else:
            # The user is viewing/editing a component that is a child of a block. Remove the child and the component
            # configuration that binds it to the block.
            path_without_last_two = path_without_last[
                : path_without_last.rfind(delimiter)
            ]
            # The parent of the component configuration has to be a block. Then, redirect_url has no "edit" part.
            redirect_url = "/experiment/component/" + path_without_last_two

    # if the questionnaire is a questionnaire and it is the only usage of a survey, the survey should also be removed.
    survey_to_check = None
    if component.component_type == "questionnaire":
        questionnaire = get_object_or_404(Questionnaire, pk=component.id)
        if not questionnaire.survey.is_initial_evaluation:
            survey_to_check = questionnaire.survey

    if component.component_type == "stimulus":
        stimulus = get_object_or_404(Stimulus, pk=component.id)
        stimulus.media_file.delete()
        stimulus.save()

    component.delete()

    # Checking if there is no other use
    if (
        survey_to_check
        and len(Questionnaire.objects.filter(survey=survey_to_check)) == 0
        and len(PatientQuestionnaireResponse.objects.filter(survey=survey_to_check))
        == 0
    ):
        survey_to_check.delete()

    return redirect_url


def remove_component_configuration(request, component_configuration):
    order_of_removed = component_configuration.order
    parent_of_removed = component_configuration.parent_id

    # Try to remove the data_configuration_tree (if there is no data-collection associated)
    if not remove_data_configuration_tree(component_configuration):
        messages.error(
            request,
            _(
                "It was not possible to exclude because there is data collection associated."
            ),
        )

    component_configuration.delete()

    if component_configuration.random_position:
        last_conf = (
            ComponentConfiguration.objects.filter(
                parent_id=parent_of_removed, random_position=True
            )
            .order_by("order")
            .last()
        )

        # If the order of the removed component is smaller than the order of the last random-positioned
        # element, assign the order of the removed to the last random-positioned element. This way, for
        # the user, it is like removing the last position for random components.
        if last_conf is not None and last_conf.order > order_of_removed:
            last_conf.order = order_of_removed
            last_conf.save()


def remove_data_configuration_tree(component_configuration):
    # Should not exists DataConfigurationTree
    data_configuration_tree_list = DataConfigurationTree.objects.filter(
        component_configuration=component_configuration
    )
    if data_configuration_tree_list:
        for data_configuration_tree in data_configuration_tree_list:
            # before remove the data_configuration_tree, check if some node has no datacollection
            current = data_configuration_tree

            # search the leaf of the path
            child = DataConfigurationTree.objects.filter(parent=current)
            while child:
                current = child[0]
                child = DataConfigurationTree.objects.filter(parent=current)

            leaf = current

            # search from leaf to root
            while current:
                if (
                    EEGData.objects.filter(data_configuration_tree=current)
                    or EMGData.objects.filter(data_configuration_tree=current)
                    or AdditionalData.objects.filter(data_configuration_tree=current)
                    or QuestionnaireResponse.objects.filter(
                        data_configuration_tree=current
                    )
                ):
                    return False

                current = current.parent

            # delete data_configuration_tree (from leaf)
            parent = leaf.parent
            leaf.delete()
            while parent:
                parent = leaf.parent
                leaf.delete()
    return True


def check_experiment(experiment):
    """
    Checks if the experiment has data collection for some participant
    :param experiment:
    :return:
    """
    experiment_with_data = False
    for group in Group.objects.filter(experiment=experiment):
        if group_has_data_collection(group.id):
            experiment_with_data = True
            break
    return experiment_with_data


def get_uses_of_step_with_data(experiment):
    steps_questionnaire = [
        item["data_configuration_tree__component_configuration"]
        for item in QuestionnaireResponse.objects.filter(
            data_configuration_tree__component_configuration__component__experiment=experiment
        )
        .values("data_configuration_tree__component_configuration")
        .distinct()
    ]

    steps_eeg = [
        item["data_configuration_tree__component_configuration"]
        for item in EEGData.objects.filter(
            data_configuration_tree__component_configuration__component__experiment=experiment
        )
        .values("data_configuration_tree__component_configuration")
        .distinct()
    ]

    steps_emg = [
        item["data_configuration_tree__component_configuration"]
        for item in EMGData.objects.filter(
            data_configuration_tree__component_configuration__component__experiment=experiment
        )
        .values("data_configuration_tree__component_configuration")
        .distinct()
    ]

    steps_tms = [
        item["data_configuration_tree__component_configuration"]
        for item in TMSData.objects.filter(
            data_configuration_tree__component_configuration__component__experiment=experiment
        )
        .values("data_configuration_tree__component_configuration")
        .distinct()
    ]

    steps_goalkeeper_game = [
        item["data_configuration_tree__component_configuration"]
        for item in DigitalGamePhaseData.objects.filter(
            data_configuration_tree__component_configuration__component__experiment=experiment
        )
        .values("data_configuration_tree__component_configuration")
        .distinct()
    ]

    steps_additional_data = [
        item["data_configuration_tree__component_configuration"]
        for item in AdditionalData.objects.filter(
            data_configuration_tree__component_configuration__component__experiment=experiment
        )
        .values("data_configuration_tree__component_configuration")
        .distinct()
    ]

    steps_generic_data_collection = [
        item["data_configuration_tree__component_configuration"]
        for item in GenericDataCollectionData.objects.filter(
            data_configuration_tree__component_configuration__component__experiment=experiment
        )
        .values("data_configuration_tree__component_configuration")
        .distinct()
    ]

    steps_media_collection = [
        item["data_configuration_tree__component_configuration"]
        for item in MediaCollectionData.objects.filter(
            data_configuration_tree__component_configuration__component__experiment=experiment
        )
        .values("data_configuration_tree__component_configuration")
        .distinct()
    ]

    return (
        steps_questionnaire
        + steps_eeg
        + steps_emg
        + steps_tms
        + steps_goalkeeper_game
        + steps_additional_data
        + steps_generic_data_collection
        + steps_media_collection
    )


def clone_data_configuration_tree(dct, orig_and_clone):
    old_component_configuration_id = dct.component_configuration.id
    old_dct_id = dct.id
    dct.pk = None
    new_component_configuration = ComponentConfiguration.objects.get(
        pk=orig_and_clone[old_component_configuration_id]
    )
    dct.component_configuration = new_component_configuration
    dct.save()
    orig_and_clone["dct"][old_dct_id] = dct.id

    return dct


def clone_electrode_positions(old_eeg_data, orig_and_clone):
    for eepcs in EEGElectrodePositionCollectionStatus.objects.filter(
        eeg_data=old_eeg_data
    ):
        eepcs.pk = None
        new_eeg_data = EEGData.objects.get(
            pk=orig_and_clone["eeg_data"][old_eeg_data.id]
        )
        new_eeg_electrode_position_setting = EEGElectrodePositionSetting.objects.get(
            pk=orig_and_clone["eeg_electrode_position_setting"][
                eepcs.eeg_electrode_position_setting.id
            ]
        )
        eepcs.eeg_data = new_eeg_data
        eepcs.eeg_electrode_position_setting = new_eeg_electrode_position_setting

        eepcs.save()


def clone_eeg_data(eeg_data, orig_and_clone):
    old_eeg_data_id = eeg_data.id
    eeg_data.pk = None
    new_eeg_setting = EEGSetting.objects.get(
        pk=orig_and_clone["eeg_setting"][eeg_data.eeg_setting.id]
    )
    new_subject_of_group = SubjectOfGroup.objects.get(
        pk=orig_and_clone["subject_of_group"][eeg_data.subject_of_group.id]
    )
    new_data_configuration_tree = DataConfigurationTree.objects.get(
        pk=orig_and_clone["dct"][eeg_data.data_configuration_tree.id]
    )
    eeg_data.eeg_setting = new_eeg_setting
    eeg_data.subject_of_group = new_subject_of_group
    eeg_data.data_configuration_tree = new_data_configuration_tree
    eeg_data.save()
    orig_and_clone["eeg_data"][old_eeg_data_id] = eeg_data.id

    old_eeg_data = EEGData.objects.get(pk=old_eeg_data_id)
    clone_electrode_positions(old_eeg_data, orig_and_clone)

    return eeg_data


def clone_eeg_file(eeg_file, orig_and_clone):
    eeg_file.pk = None
    new_eeg_data = EEGData.objects.get(
        pk=orig_and_clone["eeg_data"][eeg_file.eeg_data.id]
    )
    eeg_file.eeg_data = new_eeg_data
    f = open(os.path.join(settings.MEDIA_ROOT, eeg_file.file.name), "rb")
    eeg_file.file.save(os.path.basename(f.name), File(f))
    eeg_file.save()

    return eeg_file


def clone_emg_data(emg_data, orig_and_clone):
    old_emg_data_id = emg_data.id
    emg_data.pk = None
    new_emg_setting = EMGSetting.objects.get(
        pk=orig_and_clone["emg_setting"][emg_data.emg_setting.id]
    )
    new_subject_of_group = SubjectOfGroup.objects.get(
        pk=orig_and_clone["subject_of_group"][emg_data.subject_of_group.id]
    )
    new_data_configuration_tree = DataConfigurationTree.objects.get(
        pk=orig_and_clone["dct"][emg_data.data_configuration_tree.id]
    )
    emg_data.emg_setting = new_emg_setting
    emg_data.subject_of_group = new_subject_of_group
    emg_data.data_configuration_tree = new_data_configuration_tree
    emg_data.save()
    orig_and_clone["emg_data"][old_emg_data_id] = emg_data.id


def clone_emg_file(emg_file, orig_and_clone):
    emg_file.pk = None
    new_emg_data = EMGData.objects.get(
        pk=orig_and_clone["emg_data"][emg_file.emg_data.id]
    )
    emg_file.emg_data = new_emg_data
    f = open(os.path.join(settings.MEDIA_ROOT, emg_file.file.name), "rb")
    emg_file.file.save(os.path.basename(f.name), File(f))

    emg_file.save()

    return emg_file


def clone_additional_data(additional_data, orig_and_clone):
    old_additional_data_id = additional_data.id
    additional_data.pk = None
    new_subject_of_group = SubjectOfGroup.objects.get(
        pk=orig_and_clone["subject_of_group"][additional_data.subject_of_group.id]
    )
    if additional_data.data_configuration_tree:
        new_data_configuration_tree = DataConfigurationTree.objects.get(
            pk=orig_and_clone["dct"][additional_data.data_configuration_tree.id]
        )
    else:
        new_data_configuration_tree = None
    additional_data.subject_of_group = new_subject_of_group
    additional_data.data_configuration_tree = new_data_configuration_tree
    additional_data.save()
    orig_and_clone["additional_data"][old_additional_data_id] = additional_data.id


def clone_additional_data_file(additional_data_file, orig_and_clone):
    additional_data_file.pk = None
    new_additional_data = AdditionalData.objects.get(
        pk=orig_and_clone["additional_data"][additional_data_file.additional_data.id]
    )
    additional_data_file.additional_data = new_additional_data
    f = open(os.path.join(settings.MEDIA_ROOT, additional_data_file.file.name), "rb")
    additional_data_file.file.save(os.path.basename(f.name), File(f))
    additional_data_file.save()

    return additional_data_file


def clone_digital_game_phase_data(dgp_data, orig_and_clone):
    old_dgp_data_id = dgp_data.id
    dgp_data.pk = None
    new_subject_of_group = SubjectOfGroup.objects.get(
        pk=orig_and_clone["subject_of_group"][dgp_data.subject_of_group.id]
    )
    new_data_configuration_tree = DataConfigurationTree.objects.get(
        pk=orig_and_clone["dct"][dgp_data.data_configuration_tree.id]
    )
    dgp_data.subject_of_group = new_subject_of_group
    dgp_data.data_configuration_tree = new_data_configuration_tree
    dgp_data.save()
    orig_and_clone["digital_game_phase_data"][old_dgp_data_id] = dgp_data.id


def clone_digital_game_phase_file(dgp_file, orig_and_clone):
    dgp_file.pk = None
    new_dgp_data = DigitalGamePhaseData.objects.get(
        pk=orig_and_clone["digital_game_phase_data"][
            dgp_file.digital_game_phase_data.id
        ]
    )
    dgp_file.digital_game_phase_data = new_dgp_data
    f = open(os.path.join(settings.MEDIA_ROOT, dgp_file.file.name), "rb")
    dgp_file.file.save(os.path.basename(f.name), File(f))
    dgp_file.save()

    return dgp_file


def clone_generic_data_collection_data(gdc_data, orig_and_clone):
    old_gdc_data_id = gdc_data.id
    gdc_data.pk = None
    new_subject_of_group = SubjectOfGroup.objects.get(
        pk=orig_and_clone["subject_of_group"][gdc_data.subject_of_group.id]
    )
    new_data_configuration_tree = DataConfigurationTree.objects.get(
        pk=orig_and_clone["dct"][gdc_data.data_configuration_tree.id]
    )
    gdc_data.subject_of_group = new_subject_of_group
    gdc_data.data_configuration_tree = new_data_configuration_tree
    gdc_data.save()
    orig_and_clone["generic_data_collection_data"][old_gdc_data_id] = gdc_data.id


def clone_generic_data_collection_file(gdc_file, orig_and_clone):
    gdc_file.pk = None
    new_gdc_data = GenericDataCollectionData.objects.get(
        pk=orig_and_clone["generic_data_collection_data"][
            gdc_file.generic_data_collection_data.id
        ]
    )
    gdc_file.generic_data_collection_data = new_gdc_data
    f = open(os.path.join(settings.MEDIA_ROOT, gdc_file.file.name), "rb")
    gdc_file.file.save(os.path.basename(f.name), File(f))
    gdc_file.save()

    return gdc_file


def clone_media_collection_data(gdc_data, orig_and_clone):
    old_gdc_data_id = gdc_data.id
    gdc_data.pk = None
    new_subject_of_group = SubjectOfGroup.objects.get(
        pk=orig_and_clone["subject_of_group"][gdc_data.subject_of_group.id]
    )
    new_data_configuration_tree = DataConfigurationTree.objects.get(
        pk=orig_and_clone["dct"][gdc_data.data_configuration_tree.id]
    )
    gdc_data.subject_of_group = new_subject_of_group
    gdc_data.data_configuration_tree = new_data_configuration_tree
    gdc_data.save()
    orig_and_clone["media_collection_data"][old_gdc_data_id] = gdc_data.id


def clone_media_collection_file(gdc_file, orig_and_clone):
    gdc_file.pk = None
    new_gdc_data = MediaCollectionData.objects.get(
        pk=orig_and_clone["media_collection_data"][gdc_file.media_collection_data.id]
    )
    gdc_file.media_collection_data = new_gdc_data
    f = open(os.path.join(settings.MEDIA_ROOT, gdc_file.file.name), "rb")
    gdc_file.file.save(os.path.basename(f.name), File(f))
    gdc_file.save()

    return gdc_file


def clone_component_additional_file(component_additional_file, orig_and_clone):
    component_additional_file.pk = None
    new_component = Component.objects.get(
        pk=orig_and_clone["component"][component_additional_file.component.id]
    )
    component_additional_file.component = new_component
    f = open(os.path.join(settings.MEDIA_ROOT, component_additional_file.file.name), "rb")
    component_additional_file.file.save(os.path.basename(f.name), File(f))
    component_additional_file.save()

    return component_additional_file


def clone_context_tree(context_tree, new_experiment, orig_and_clone):
    old_context_tree_id = context_tree.id
    context_tree.pk = None
    context_tree.experiment = new_experiment
    context_tree.save()
    old_context_tree = ContextTree.objects.get(pk=old_context_tree_id)
    if old_context_tree.setting_file:
        f = open(os.path.join(settings.MEDIA_ROOT, old_context_tree.setting_file.name), "rb")
        context_tree.setting_file.save(os.path.basename(f.name), File(f))
    orig_and_clone["context_tree"][old_context_tree_id] = context_tree.id


def clone_hotspot(hotspot, new_tms_data):
    old_hotspot = hotspot
    hotspot.pk = None
    hotspot.tms_data = new_tms_data
    hotspot.save()
    if old_hotspot.hot_spot_map:
        f = open(os.path.join(settings.MEDIA_ROOT, old_hotspot.hot_spot_map.name), "rb")
        hotspot.hot_spot_map.save(os.path.basename(f.name), File(f))


def clone_tms_data(tms_data, orig_and_clone):
    old_tms_data_id = tms_data.id
    tms_data.pk = None
    new_tms_setting = TMSSetting.objects.get(
        pk=orig_and_clone["tms_setting"][tms_data.tms_setting.id]
    )
    new_subject_of_group = SubjectOfGroup.objects.get(
        pk=orig_and_clone["subject_of_group"][tms_data.subject_of_group.id]
    )
    new_data_configuration_tree = DataConfigurationTree.objects.get(
        pk=orig_and_clone["dct"][tms_data.data_configuration_tree.id]
    )
    tms_data.tms_setting = new_tms_setting
    tms_data.subject_of_group = new_subject_of_group
    tms_data.data_configuration_tree = new_data_configuration_tree
    tms_data.save()

    old_tms_data = TMSData.objects.get(pk=old_tms_data_id)
    if hasattr(old_tms_data, "hotspot"):
        clone_hotspot(old_tms_data.hotspot, tms_data)

    return tms_data


def clone_questionnaire_response_data(q_response, orig_and_clone):
    q_response.pk = None
    new_subject_of_group = SubjectOfGroup.objects.get(
        pk=orig_and_clone["subject_of_group"][q_response.subject_of_group.id]
    )
    new_data_configuration_tree = DataConfigurationTree.objects.get(
        pk=orig_and_clone["dct"][q_response.data_configuration_tree.id]
    )
    q_response.subject_of_group = new_subject_of_group
    q_response.data_configuration_tree = new_data_configuration_tree
    q_response.save()


def copy_experiment(experiment, copy_data_collection=False):
    orig_and_clone = dict()
    orig_and_clone["component"] = {}
    orig_and_clone["context_tree"] = {}
    orig_and_clone["dct"] = {}
    orig_and_clone["subject_of_group"] = {}
    orig_and_clone["eeg_setting"] = {}
    orig_and_clone["emg_setting"] = {}
    orig_and_clone["tms_setting"] = {}
    orig_and_clone["eeg_data"] = {}
    orig_and_clone["emg_data"] = {}
    orig_and_clone["additional_data"] = {}
    orig_and_clone["digital_game_phase_data"] = {}
    orig_and_clone["generic_data_collection_data"] = {}
    orig_and_clone["media_collection_data"] = {}
    orig_and_clone["eeg_electrode_position_setting"] = {}

    experiment_id = experiment.id
    new_experiment = experiment
    new_experiment.pk = None
    new_experiment.title = _("Copy of") + " " + new_experiment.title
    new_experiment.last_sending = None
    new_experiment.save()
    if experiment.ethics_committee_project_file:
        f = open(
            os.path.join(settings.MEDIA_ROOT, experiment.ethics_committee_project_file.name),
            "rb",
        )
        new_experiment.ethics_committee_project_file.save(
            os.path.basename(f.name), File(f)
        )

    # context tree
    for context_tree in ContextTree.objects.filter(experiment_id=experiment_id):
        clone_context_tree(context_tree, new_experiment, orig_and_clone)

    # eeg setting
    for eeg_setting in EEGSetting.objects.filter(experiment_id=experiment_id):
        old_eeg_setting_id = eeg_setting.id
        new_eeg_setting = copy_eeg_setting(eeg_setting, new_experiment, orig_and_clone)
        orig_and_clone["eeg_setting"][old_eeg_setting_id] = new_eeg_setting.id

    # emg setting
    for emg_setting in EMGSetting.objects.filter(experiment_id=experiment_id):
        old_emg_setting_id = emg_setting.id
        new_emg_setting = copy_emg_setting(emg_setting, new_experiment)
        orig_and_clone["emg_setting"][old_emg_setting_id] = new_emg_setting.id

    # tms setting
    for tms_setting in TMSSetting.objects.filter(experiment_id=experiment_id):
        old_tms_setting_id = tms_setting.id
        new_tms_setting = copy_tms_setting(tms_setting, new_experiment)
        orig_and_clone["tms_setting"][old_tms_setting_id] = new_tms_setting.id

    # component
    for component in Component.objects.filter(experiment_id=experiment_id):
        clone_component = create_component(component, new_experiment, orig_and_clone)
        orig_and_clone["component"][component.id] = clone_component.id

    # component configuration
    for component_configuration in ComponentConfiguration.objects.filter(
        component_id__experiment_id=experiment_id
    ).order_by("parent_id", "order"):
        old_component_id = component_configuration.component_id
        parent_id = component_configuration.parent_id

        old_component_configuration_id = component_configuration.id
        component_configuration.pk = None
        if component_configuration.name:
            component_configuration.name = component_configuration.name

        component_configuration.component_id = orig_and_clone["component"][
            old_component_id
        ]
        component_configuration.parent_id = orig_and_clone["component"][parent_id]
        component_configuration.save()
        orig_and_clone[old_component_configuration_id] = component_configuration.id

    # groups
    groups = Group.objects.filter(experiment_id=experiment_id)
    for group in groups:
        experimental_protocol_id = group.experimental_protocol_id
        subject_list = [item.pk for item in SubjectOfGroup.objects.filter(group=group)]
        new_group = group
        new_group.pk = None
        new_group.title = new_group.title
        # group code is unique and not needed to be set at start (goal
        # keeper game integration)
        new_group.code = None
        new_group.experiment_id = new_experiment.id
        if experimental_protocol_id in orig_and_clone["component"]:
            new_group.experimental_protocol_id = orig_and_clone["component"][
                experimental_protocol_id
            ]
        new_group.save()

        # subject of group
        if subject_list:
            new_subject_of_group = SubjectOfGroup.objects.filter(id__in=subject_list)
            for subject_of_group in new_subject_of_group:
                old_subject_of_group_id = subject_of_group.id
                subject_of_group.pk = None
                subject_of_group.group_id = group.id
                subject_of_group.save()
                old_subject_of_group = SubjectOfGroup.objects.get(
                    pk=old_subject_of_group_id
                )
                if old_subject_of_group.consent_form:
                    f = open(
                        os.path.join(
                            settings.MEDIA_ROOT, old_subject_of_group.consent_form.name
                        ),
                        "rb",
                    )
                    subject_of_group.consent_form.save(
                        os.path.basename(f.name), File(f)
                    )
                orig_and_clone["subject_of_group"][
                    old_subject_of_group_id
                ] = subject_of_group.id

    if copy_data_collection:
        # TODO: 1) check if groups has data collection before trying to copy or
        #  check this in template so the option to copy with data
        #  doesn't appear;
        # TODO: 2) explain that orig_and_clone is modified in method
        dct_new_list = []
        for data_configuration_tree in DataConfigurationTree.objects.filter(
            component_configuration_id__component_id__experiment_id=experiment_id
        ):
            dct_new_list.append(
                clone_data_configuration_tree(data_configuration_tree, orig_and_clone)
            )
        for dct in dct_new_list:
            if dct.parent:
                new_dct_parent = DataConfigurationTree.objects.get(
                    pk=orig_and_clone["dct"][dct.parent.id]
                )
                dct.parent = new_dct_parent
                dct.save()
        # eeg_data
        for eeg_data in EEGData.objects.filter(
            eeg_setting_id__experiment_id=experiment_id
        ):
            clone_eeg_data(eeg_data, orig_and_clone)
        # eeg_file
        for eeg_file in EEGFile.objects.filter(
            eeg_data_id__eeg_setting_id__experiment_id=experiment_id
        ):
            clone_eeg_file(eeg_file, orig_and_clone)
        # emg_data
        for emg_data in EMGData.objects.filter(
            emg_setting_id__experiment_id=experiment_id
        ):
            clone_emg_data(emg_data, orig_and_clone)
        # emg_file
        for emg_file in EMGFile.objects.filter(
            emg_data_id__emg_setting_id__experiment_id=experiment_id
        ):
            clone_emg_file(emg_file, orig_and_clone)
        # additional_data
        for additional_data in AdditionalData.objects.filter(
            subject_of_group_id__group_id__experiment_id=experiment_id
        ):
            clone_additional_data(additional_data, orig_and_clone)
        # additional_data_file
        for additional_data_file in AdditionalDataFile.objects.filter(
            additional_data_id__subject_of_group_id__group_id__experiment_id=experiment_id
        ):
            clone_additional_data_file(additional_data_file, orig_and_clone)
        # digital_game_phase_data
        for digital_game_phase_data in DigitalGamePhaseData.objects.filter(
            data_configuration_tree_id__component_configuration_id__component_id__experiment_id=experiment_id
        ):
            clone_digital_game_phase_data(digital_game_phase_data, orig_and_clone)
        # digital_game_phase_file
        for digital_game_phase_file in DigitalGamePhaseFile.objects.filter(
            digital_game_phase_data_id__data_configuration_tree_id__component_configuration_id__component_id__experiment_id=experiment_id
        ):
            clone_digital_game_phase_file(digital_game_phase_file, orig_and_clone)
        # generic_data_collection_data
        for generic_data_collection_data in GenericDataCollectionData.objects.filter(
            data_configuration_tree_id__component_configuration_id__component_id__experiment_id=experiment_id
        ):
            clone_generic_data_collection_data(
                generic_data_collection_data, orig_and_clone
            )
        # generic_data_collection_file
        for generic_data_collection_file in GenericDataCollectionFile.objects.filter(
            generic_data_collection_data_id__data_configuration_tree_id__component_configuration_id__component_id__experiment_id=experiment_id
        ):
            clone_generic_data_collection_file(
                generic_data_collection_file, orig_and_clone
            )
        # media_collection_data
        for media_collection_data in MediaCollectionData.objects.filter(
            data_configuration_tree_id__component_configuration_id__component_id__experiment_id=experiment_id
        ):
            clone_media_collection_data(
                media_collection_data, orig_and_clone
            )
        # media_collection_file
        for media_collection_file in MediaCollectionFile.objects.filter(
            media_collection_data_id__data_configuration_tree_id__component_configuration_id__component_id__experiment_id=experiment_id
        ):
            clone_media_collection_file(media_collection_file, orig_and_clone)
        # component_additional_file
        for component_additional_file in ComponentAdditionalFile.objects.filter(
            component_id__experiment_id=experiment_id
        ):
            clone_component_additional_file(component_additional_file, orig_and_clone)
        # tms_data
        for tms_data in TMSData.objects.filter(
            tms_setting_id__experiment_id=experiment_id
        ):
            clone_tms_data(tms_data, orig_and_clone)

        # questionnaire_response_data
        for questionnaire_response_data in QuestionnaireResponse.objects.filter(
            subject_of_group_id__group_id__experiment_id=experiment_id
        ):
            clone_questionnaire_response_data(
                questionnaire_response_data, orig_and_clone
            )


def copy_eeg_setting(eeg_setting, new_experiment, orig_and_clone):
    eeg_setting_id = eeg_setting.id
    new_eeg_setting = eeg_setting
    new_eeg_setting.pk = None
    new_eeg_setting.experiment = new_experiment
    new_eeg_setting.save()

    # eeg_layout_setting
    if EEGElectrodeLayoutSetting.objects.filter(eeg_setting_id=eeg_setting_id).exists():
        new_eeg_electrode_layout_setting = get_object_or_404(
            EEGElectrodeLayoutSetting, pk=eeg_setting_id
        )
        new_eeg_electrode_layout_setting.pk = None
        new_eeg_electrode_layout_setting.eeg_setting = new_eeg_setting
        new_eeg_electrode_layout_setting.save()

        for position_setting in EEGElectrodePositionSetting.objects.filter(
            eeg_electrode_layout_setting_id=eeg_setting_id
        ):
            old_position_setting_id = position_setting.id
            new_position_setting = position_setting
            new_position_setting.pk = None
            new_position_setting.eeg_electrode_layout_setting = (
                new_eeg_electrode_layout_setting
            )
            new_position_setting.save()

            orig_and_clone["eeg_electrode_position_setting"][
                old_position_setting_id
            ] = new_position_setting.id

    # eeg_amplifier_setting
    if EEGAmplifierSetting.objects.filter(eeg_setting_id=eeg_setting_id).exists():
        new_eeg_amplifier_setting = get_object_or_404(
            EEGAmplifierSetting, pk=eeg_setting_id
        )
        new_eeg_amplifier_setting.pk = None
        new_eeg_amplifier_setting.eeg_setting = new_eeg_setting
        new_eeg_amplifier_setting.save()

    # eeg_solution_setting
    if EEGSolutionSetting.objects.filter(eeg_setting_id=eeg_setting_id).exists():
        new_eeg_solution_setting = get_object_or_404(
            EEGSolutionSetting, pk=eeg_setting_id
        )
        new_eeg_solution_setting.pk = None
        new_eeg_solution_setting.eeg_setting = new_eeg_setting
        new_eeg_solution_setting.save()

    # eeg_filter_setting
    if EEGFilterSetting.objects.filter(eeg_setting_id=eeg_setting_id).exists():
        new_eeg_filter_setting = get_object_or_404(EEGFilterSetting, pk=eeg_setting_id)
        new_eeg_filter_setting.pk = None
        new_eeg_filter_setting.eeg_setting = new_eeg_setting
        new_eeg_filter_setting.save()

    return new_eeg_setting


def copy_emg_setting(emg_setting, new_experiment):
    emg_setting_id = emg_setting.id
    new_emg_setting = emg_setting
    new_emg_setting.pk = None
    new_emg_setting.experiment = new_experiment
    new_emg_setting.save()

    # EMGDigitalFilterSetting
    if EMGDigitalFilterSetting.objects.filter(emg_setting_id=emg_setting_id).exists():
        new_emg_digital_filter_setting = get_object_or_404(
            EMGDigitalFilterSetting, pk=emg_setting_id
        )
        new_emg_digital_filter_setting.pk = None
        new_emg_digital_filter_setting.emg_setting = new_emg_setting
        new_emg_digital_filter_setting.save()

    # EMGADConverterSetting
    if EMGADConverterSetting.objects.filter(emg_setting_id=emg_setting_id).exists():
        new_emg_ad_converter_filter_setting = get_object_or_404(
            EMGADConverterSetting, pk=emg_setting_id
        )
        new_emg_ad_converter_filter_setting.pk = None
        new_emg_ad_converter_filter_setting.emg_setting = new_emg_setting
        new_emg_ad_converter_filter_setting.save()

    # EMGElectrodeSetting
    for emg_electrode_setting in EMGElectrodeSetting.objects.filter(
        emg_setting_id=emg_setting_id
    ):
        emg_electrode_setting_id = emg_electrode_setting.id

        new_emg_electrode_setting = emg_electrode_setting
        new_emg_electrode_setting.pk = None
        new_emg_electrode_setting.emg_setting = new_emg_setting
        new_emg_electrode_setting.save()

        # EMGPreamplifierSetting
        if EMGPreamplifierSetting.objects.filter(
            emg_electrode_setting_id=emg_electrode_setting_id
        ).exists():
            new_emg_preamplifier_setting = get_object_or_404(
                EMGPreamplifierSetting, pk=emg_electrode_setting_id
            )
            new_emg_preamplifier_setting.pk = None
            new_emg_preamplifier_setting.emg_electrode_setting_id = (
                new_emg_electrode_setting.id
            )
            new_emg_preamplifier_setting.save()

            # EMGPreamplifierFilterSetting
            if EMGPreamplifierFilterSetting.objects.filter(
                emg_preamplifier_filter_setting_id=emg_electrode_setting_id
            ).exists():
                new_emg_preamplifier_filter_setting = get_object_or_404(
                    EMGPreamplifierFilterSetting, pk=emg_electrode_setting_id
                )
                new_emg_preamplifier_filter_setting.pk = None
                new_emg_preamplifier_filter_setting.emg_preamplifier_filter_setting = (
                    new_emg_preamplifier_setting
                )
                new_emg_preamplifier_filter_setting.save()

        # EMGAmplifierSetting
        if EMGAmplifierSetting.objects.filter(
            emg_electrode_setting_id=emg_electrode_setting_id
        ).exists():
            new_emg_amplifier_setting = get_object_or_404(
                EMGAmplifierSetting, pk=emg_electrode_setting_id
            )
            new_emg_amplifier_setting.pk = None
            new_emg_amplifier_setting.emg_electrode_setting_id = (
                new_emg_electrode_setting.id
            )
            new_emg_amplifier_setting.save()

            # EMGAnalogFilterSetting
            if EMGAnalogFilterSetting.objects.filter(
                emg_electrode_setting=emg_electrode_setting_id
            ).exists():
                new_emg_analog_filter_setting = get_object_or_404(
                    EMGAnalogFilterSetting, pk=emg_electrode_setting_id
                )
                new_emg_analog_filter_setting.pk = None
                new_emg_analog_filter_setting.emg_electrode_setting = (
                    new_emg_amplifier_setting
                )
                new_emg_analog_filter_setting.save()

        # EMGElectrodePlacementSetting
        if EMGElectrodePlacementSetting.objects.filter(
            emg_electrode_setting_id=emg_electrode_setting_id
        ).exists():
            new_emg_electrode_placement_setting = get_object_or_404(
                EMGElectrodePlacementSetting, pk=emg_electrode_setting_id
            )
            new_emg_electrode_placement_setting.pk = None
            new_emg_electrode_placement_setting.emg_electrode_setting_id = (
                new_emg_electrode_setting.id
            )
            new_emg_electrode_placement_setting.save()

    return new_emg_setting


def clone_tms_device_setting(tms_device_setting, new_tms_setting):
    tms_device_setting.pk = None
    tms_device_setting.tms_setting = new_tms_setting
    tms_device_setting.save()


def copy_tms_setting(tms_setting, new_experiment):
    old_tms_setting_id = tms_setting.id
    new_tms_setting = tms_setting
    new_tms_setting.pk = None
    new_tms_setting.experiment = new_experiment
    new_tms_setting.save()

    old_tms_setting = TMSSetting.objects.get(pk=old_tms_setting_id)

    if hasattr(old_tms_setting, "tms_device_setting"):
        clone_tms_device_setting(old_tms_setting.tms_device_setting, new_tms_setting)

    return new_tms_setting


def create_component(component, new_experiment, orig_and_clone):
    component_type = component.component_type
    file = None  # define variable that can be used in conditionals below

    if component_type == "block":
        block = get_object_or_404(Block, pk=component.id)
        clone = Block(
            number_of_mandatory_components=block.number_of_mandatory_components,
            type=block.type,
        )

    elif component_type == "eeg":
        eeg = get_object_or_404(EEG, pk=component.id)
        clone = EEG(eeg_setting_id=orig_and_clone["eeg_setting"][eeg.eeg_setting_id])

    elif component_type == "emg":
        emg = get_object_or_404(EMG, pk=component.id)
        clone = EMG(emg_setting_id=orig_and_clone["emg_setting"][emg.emg_setting_id])

    elif component_type == "tms":
        tms = get_object_or_404(TMS, pk=component.id)
        clone = TMS(tms_setting_id=orig_and_clone["tms_setting"][tms.tms_setting_id])

    elif component_type == "instruction":
        instruction = get_object_or_404(Instruction, pk=component.id)
        clone = Instruction(text=instruction.text)

    elif component_type == "pause":
        clone = Pause()

    elif component_type == "questionnaire":
        questionnaire = get_object_or_404(Questionnaire, pk=component.id)
        clone = Questionnaire(survey_id=questionnaire.survey_id)

    elif component_type == "stimulus":
        stimulus = get_object_or_404(Stimulus, pk=component.id)
        clone = Stimulus(stimulus_type_id=stimulus.stimulus_type_id)
        if stimulus.media_file:
            file = open(os.path.join(settings.MEDIA_ROOT, stimulus.media_file.name), "rb")

    elif component_type == "task":
        clone = Task()

    elif component_type == "task_experiment":
        clone = TaskForTheExperimenter()

    elif component_type == "digital_game_phase":
        digital_game_phase = get_object_or_404(DigitalGamePhase, pk=component.id)
        clone = DigitalGamePhase(
            context_tree_id=orig_and_clone["context_tree"][
                digital_game_phase.context_tree_id
            ],
            software_version_id=digital_game_phase.software_version_id,
        )

    elif component_type == "generic_data_collection":
        generic_data_collection = get_object_or_404(
            GenericDataCollection, pk=component.id
        )
        clone = GenericDataCollection(
            information_type_id=generic_data_collection.information_type_id
        )

    elif component_type == "media_collection":
        media_collection = get_object_or_404(MediaCollection, pk=component.id)
        clone = MediaCollection(
            information_type_media_id=media_collection.information_type_media_id
        )

    else:
        clone = Component()

    clone.identification = component.identification

    clone.experiment = new_experiment
    clone.description = component.description
    clone.duration_value = component.duration_value
    clone.duration_unit = component.duration_unit
    clone.component_type = component.component_type

    clone.save()

    # Stimulus component has FileField
    if isinstance(clone, Stimulus) and file:
        clone.media_file.save(os.path.basename(file.name), File(file))

    return clone


@login_required
@permission_required("experiment.view_researchproject")
def component_view(request, path_of_the_components):
    # It will always be a block because we don't have a view screen for other components.
    # This view is also use to show the use of a set of steps (component configuration of a block).

    (
        component,
        component_configuration,
        component_form,
        configuration_form,
        experiment,
        component_type,
        template_name,
        list_of_ids_of_components_and_configurations,
        list_of_breadcrumbs,
        group,
        back_cancel_url,
    ) = access_objects_for_view_and_update(request, path_of_the_components)

    # when there are data collected, it is necessary to protect related "steps" and "uses of steps"
    protected_steps, protected_uses_of_step = get_protected_steps_and_uses_of_steps(
        experiment, group
    )

    block = get_object_or_404(Block, pk=component.id)
    block_form = BlockForm(request.POST or None, instance=block)
    configuration_list = create_configuration_list(block)
    configuration_list_of_random_components = (
        create_configuration_list_of_random_components(block)
    )

    duration_value, has_unlimited = calculate_block_duration(block)
    # Criate a string converting to appropriate units
    duration_string = convert_to_string(duration_value)

    # It is not possible to edit fields while viewing a block.
    for form in {block_form, component_form}:
        for field in form.fields:
            form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        check_can_change(request.user, experiment.research_project)

        if request.POST["action"] == "save":
            if configuration_form is not None:
                if configuration_form.is_valid():
                    configuration_form.save()
                    messages.success(request, _("Step use updated successfully."))
                    return HttpResponseRedirect(back_cancel_url)
        elif request.POST["action"] == "remove":
            redirect_url = remove_component_and_related_configurations(
                component,
                list_of_ids_of_components_and_configurations,
                path_of_the_components,
            )
            messages.success(request, _("Component deleted successfully."))
            return HttpResponseRedirect(redirect_url)
        elif request.POST["action"][:7] == "remove-":
            # If action starts with 'remove-' it means that a child or some children should be removed.
            action_parts = request.POST["action"].split(delimiter)

            if action_parts[1] == "random":
                list_from_which_to_deleted = configuration_list_of_random_components
            else:  # "fixed"
                list_from_which_to_deleted = configuration_list

            position_of_the_accordion_to_be_deleted = int(action_parts[2])

            if len(action_parts) == 4:  # Check the existence of an extra parameter
                # It means that a single component configuration should be removed
                position_in_accordion_of_the_conf_to_be_deleted = int(action_parts[3])
                remove_component_configuration(
                    request,
                    list_from_which_to_deleted[position_of_the_accordion_to_be_deleted][
                        position_in_accordion_of_the_conf_to_be_deleted
                    ],
                )
            else:
                for conf in list_from_which_to_deleted[
                    position_of_the_accordion_to_be_deleted
                ]:
                    # Only uses that do not have associated data will be excluded.
                    remove_component_configuration(request, conf)

            redirect_url = reverse("component_view", args=(path_of_the_components,))
            return HttpResponseRedirect(redirect_url)
        elif request.POST["action"] == "copy_experiment":
            copy_experiment(experiment)
            messages.success(request, _("The experiment was copied."))
            redirect_url = reverse("experiment_view", args=(experiment.id,))
            return HttpResponseRedirect(redirect_url)
        elif request.POST["action"] == "copy_experiment_with_data":
            copy_experiment(experiment, True)
            messages.success(
                request, _("The experiment was copied with " "all data collections")
            )
            redirect_url = reverse("experiment_view", args=(experiment.id,))
            return HttpResponseRedirect(redirect_url)

    component_type_choices = []
    for type_element, type_name in Component.COMPONENT_TYPES:
        component_type_choices.append(
            (type_element, type_name, icon_class.get(type_element))
        )

    can_change = get_can_change(request.user, experiment.research_project)

    # This value is used to define if the options Fixed/Radon should be shown.
    type_of_the_parent_block = None
    if component_configuration:
        type_of_the_parent_block = Block.objects.get(
            id=component_configuration.parent_id
        ).type

        # If the user is not the owner of the research_project, not event the fields of the component configuration
        # can be edited.
        if not can_change:
            for field in configuration_form.fields:
                configuration_form.fields[field].widget.attrs["disabled"] = True

    surveys = Questionnaires()
    # This method shows a message to the user if limesurvey is not available.
    limesurvey_available = check_limesurvey_access(request, surveys)

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
        "limesurvey_available": limesurvey_available,
        "protected_uses_of_step": protected_uses_of_step,
        "protected_steps": protected_steps,
    }

    return render(request, template_name, context)


def get_protected_steps_and_uses_of_steps(experiment: Experiment, group: Group):
    groups = (
        [group]
        if group
        else [item for item in Group.objects.filter(experiment=experiment)]
    )

    protected_uses_of_step_set = set()
    related_steps = set()

    for group in groups:
        protected_uses_of_step = get_uses_of_step_with_data(group.experiment)

        if protected_uses_of_step:
            previous_use_of_steps = set()

            # get all paths
            list_of_trees = create_list_of_trees(group.experimental_protocol, None)

            # find paths that contains use_of_steps_with_data in order to protect other "uses of steps"
            for tree in list_of_trees:
                tree_sequence = [item[0] for item in tree]
                for use_of_step in protected_uses_of_step:
                    if use_of_step in tree_sequence:
                        previous_items = tree_sequence[
                            : tree_sequence.index(use_of_step)
                        ]
                        for previous_item in previous_items:
                            previous_use_of_steps.add(previous_item)

            protected_uses_of_step += list(previous_use_of_steps)

        for item in protected_uses_of_step:
            item_component_configuration = ComponentConfiguration.objects.get(id=item)
            related_steps.add(item_component_configuration.component.id)
            if item_component_configuration.parent:
                related_steps.add(item_component_configuration.parent.id)

        protected_uses_of_step_set |= set(protected_uses_of_step)

    return list(related_steps), list(protected_uses_of_step_set)


def sort_without_using_order(configuration_list_of_random_components):
    for configuration in configuration_list_of_random_components:
        configuration.component.icon_class = icon_class[
            configuration.component.component_type
        ]

    # Create a temporary list of tuples from the query_set to be able to sort by get_component_type_display,
    # identification and name.
    temp_list_of_tuples = []

    for cc in configuration_list_of_random_components:
        temp_list_of_tuples.append(
            (
                cc,
                cc.component.get_component_type_display(),
                cc.component.identification,
                (cc.name if cc.name else ""),
            )
        )

    temp_list_of_tuples.sort(key=itemgetter(1, 2, 3))

    # Reduce the complexity by creating list of component configurations without having tuples.
    configuration_list_of_random_components = []

    for element in temp_list_of_tuples:
        configuration_list_of_random_components.append(element[0])

    return configuration_list_of_random_components


def create_configuration_list(block):
    configuration_list = ComponentConfiguration.objects.filter(parent=block)

    if block.type == "sequence":
        configuration_list = configuration_list.order_by("order")
    else:
        configuration_list = sort_without_using_order(configuration_list)

    for configuration in configuration_list:
        configuration.component.icon_class = icon_class[
            configuration.component.component_type
        ]

    # Transform configuration_list into a list of lists, to show them in accordions.
    i = 0
    new_list = []
    all_random = True
    while i < len(configuration_list):
        accordion = [configuration_list[i]]
        i += 1

        # Group if same component or if both are random_position
        while i < len(configuration_list) and (
            (
                configuration_list[i - 1].component == configuration_list[i].component
                and configuration_list[i - 1].random_position
                == configuration_list[i].random_position
            )
            or (
                configuration_list[i - 1].random_position
                == configuration_list[i].random_position
                and configuration_list[i].random_position is True
            )
        ):
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
            ComponentConfiguration.objects.filter(parent=block, random_position=True)
        )
    else:
        configuration_list_of_random_components = []

    # Transform configuration_list_of_random_components into a list of lists, to show them in accordions.
    i = 0
    new_random_list = []
    while i < len(configuration_list_of_random_components):
        accordion = [configuration_list_of_random_components[i]]
        i += 1

        while (
            i < len(configuration_list_of_random_components)
            and configuration_list_of_random_components[i - 1].component
            == configuration_list_of_random_components[i].component
        ):
            accordion.append(configuration_list_of_random_components[i])
            i += 1

        new_random_list.append(accordion)

    return new_random_list


@login_required
@permission_required("experiment.change_experiment")
def component_update(request, path_of_the_components):
    (
        component,
        component_configuration,
        component_form,
        configuration_form,
        experiment,
        component_type,
        template_name,
        list_of_ids_of_components_and_configurations,
        list_of_breadcrumbs,
        group,
        back_cancel_url,
    ) = access_objects_for_view_and_update(
        request, path_of_the_components, updating=True
    )

    # When there are data collected, it is necessary to protect related
    # "steps" and "uses of steps".
    protected_steps, protected_uses_of_step = get_protected_steps_and_uses_of_steps(
        experiment, group
    )

    questionnaire_id = None
    questionnaire_title = None
    configuration_list = []
    configuration_list_of_random_components = []
    specific_form = None
    duration_string = None
    has_unlimited = None

    if component_type == "instruction":
        instruction = get_object_or_404(Instruction, pk=component.id)
        specific_form = InstructionForm(request.POST or None, instance=instruction)
    elif component_type == "stimulus":
        stimulus = get_object_or_404(Stimulus, pk=component.id)
        specific_form = StimulusForm(request.POST or None, instance=stimulus)
    elif component_type == "eeg":
        eeg = get_object_or_404(EEG, pk=component.id)
        specific_form = EEGForm(
            request.POST or None, instance=eeg, initial={"experiment": experiment}
        )
    elif component_type == "emg":
        emg = get_object_or_404(EMG, pk=component.id)
        specific_form = EMGForm(
            request.POST or None, instance=emg, initial={"experiment": experiment}
        )
    elif component_type == "tms":
        tms = get_object_or_404(TMS, pk=component.id)
        specific_form = TMSForm(
            request.POST or None, instance=tms, initial={"experiment": experiment}
        )
    elif component_type == "block":
        block = get_object_or_404(Block, pk=component.id)
        specific_form = BlockForm(request.POST or None, instance=block)
        configuration_list = create_configuration_list(block)
        configuration_list_of_random_components = (
            create_configuration_list_of_random_components(block)
        )
        duration_value, has_unlimited = calculate_block_duration(block)
        # Criate a string converting to appropriate units
        duration_string = convert_to_string(duration_value)
    elif component_type == "digital_game_phase":
        digital_game_phase = get_object_or_404(DigitalGamePhase, pk=component.id)
        specific_form = DigitalGamePhaseForm(
            request.POST or None,
            instance=digital_game_phase,
            initial={"experiment": experiment},
        )
    elif component_type == "generic_data_collection":
        generic_data_collection = get_object_or_404(
            GenericDataCollection, pk=component.id
        )
        specific_form = GenericDataCollectionForm(
            request.POST or None, instance=generic_data_collection
        )
    elif component_type == "media_collection":
        media_collection = get_object_or_404(MediaCollection, pk=component.id)
        specific_form = MediaCollectionForm(
            request.POST or None, instance=media_collection
        )

    can_change = get_can_change(request.user, experiment.research_project)

    if request.method == "POST":
        # Workaround to avoid warning user from changing reused component after
        # redirect.
        request.session["display_warning_reused"] = False

        if can_change:
            if request.POST["action"] == "save":
                if configuration_form is None:
                    has_changed = False

                    # removing checked files
                    for (
                        current_additional_file
                    ) in component.component_additional_files.all():
                        if (
                            "remove_additional_file_" + str(current_additional_file.id)
                            in request.POST
                        ):
                            has_changed = True
                            current_additional_file.delete()

                    # new files to upload
                    files_to_upload_list = request.FILES.getlist("additional_files")
                    for file_to_upload in files_to_upload_list:
                        has_changed = True
                        additional_file = ComponentAdditionalFile(
                            component=component, file=file_to_upload
                        )
                        additional_file.save()

                    # There is no specific form for these component types.
                    if component.component_type in [
                        "questionnaire",
                        "task",
                        "task_experiment",
                        "pause",
                    ]:
                        if component_form.is_valid():
                            # Only save if there was a change.
                            if component_form.has_changed():
                                component_form.save()
                                messages.success(
                                    request, _("Step updated successfully.")
                                )
                            else:
                                messages.success(
                                    request, _("There is no changes to save.")
                                )

                            return HttpResponseRedirect(back_cancel_url)

                    elif specific_form.is_valid() and component_form.is_valid():
                        # Stimulus has media files to read
                        if component_type == "stimulus":
                            stimulus = get_object_or_404(Stimulus, pk=component.id)
                            specific_form = StimulusForm(
                                request.POST or None, request.FILES, instance=stimulus
                            )

                        # Only save if there was a change.
                        if component_form.has_changed() or specific_form.has_changed():
                            has_changed = True

                            if component.component_type == "block":
                                block = specific_form.save(commit=False)

                                # When changing from 'some mandatory' to 'all mandatory', we must set number to null, so
                                # that we know that all components are mandatory.
                                if "number_of_mandatory_components" not in request.POST:
                                    block.number_of_mandatory_components = None

                                block.save()
                            else:
                                specific_form.save()

                            component_form.save()

                        if has_changed:
                            messages.success(request, _("Step updated successfully."))
                        else:
                            messages.success(request, _("There is no changes to save."))

                        return HttpResponseRedirect(back_cancel_url)

                elif configuration_form.is_valid():
                    # Only save if there was a change.
                    if configuration_form.has_changed():
                        configuration_form.save()
                        messages.success(request, _("Step use updated successfully."))
                    else:
                        messages.success(request, _("There is no changes to save."))

                    return HttpResponseRedirect(back_cancel_url)
            elif request.POST["action"] == "remove":
                redirect_url = remove_component_and_related_configurations(
                    component,
                    list_of_ids_of_components_and_configurations,
                    path_of_the_components,
                )
                messages.success(request, _("Component deleted successfully."))
                return HttpResponseRedirect(redirect_url)
            elif request.POST["action"] == "copy_experiment":
                copy_experiment(experiment)
                messages.success(request, _("The experiment was copied."))
                redirect_url = reverse("experiment_view", args=(experiment.id,))
                return HttpResponseRedirect(redirect_url)

    if component_type == "questionnaire":
        questionnaire = get_object_or_404(Questionnaire, pk=component.id)

        questionnaire_id = questionnaire.survey.lime_survey_id

        questionnaire_title = find_questionnaire_name(
            questionnaire.survey, request.LANGUAGE_CODE
        )["name"]

    type_of_the_parent_block = None

    # It is not possible to edit the component fields while editing a component configuration.
    if component_configuration or not can_change:
        if specific_form is not None:
            for field in specific_form.fields:
                specific_form.fields[field].widget.attrs["disabled"] = True

        for field in component_form.fields:
            component_form.fields[field].widget.attrs["disabled"] = True

        if component_configuration:
            type_of_the_parent_block = Block.objects.get(
                id=component_configuration.parent_id
            ).type

            # If the user is not the owner of the research_project, not event the fields of the component configuration
            # can be edited.
            if not can_change:
                for field in configuration_form.fields:
                    configuration_form.fields[field].widget.attrs["disabled"] = True

    configuration_count = component.configuration.count()
    if configuration_count > 1:
        if request.session.get("display_warning_reused", True):
            messages.warning(
                request,
                _("This component is reused in")
                + " "
                + str(configuration_count - 1)
                + " "
                + _(
                    " other step(s). Pay attention to any change made to it will reflect in the other(s)."
                ),
            )
        else:  # session key was setted after a post request (see above)
            del request.session["display_warning_reused"]

    context = {
        "back_cancel_url": back_cancel_url,
        "block_duration": duration_string,
        "can_change": can_change,
        "component": component,
        "component_configuration": component_configuration,
        "component_form": component_form,
        "component_additional_files": component.component_additional_files,
        "configuration_form": configuration_form,
        "configuration_list": configuration_list,
        "configuration_list_of_random_components": configuration_list_of_random_components,
        "icon_class": icon_class,
        "experiment": experiment,
        "protected_steps": protected_steps,
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

    list_of_component_configuration = ComponentConfiguration.objects.filter(
        component=component
    )

    if not list_of_component_configuration:
        return output_set_of_components

    for component_configuration in list_of_component_configuration:
        if component_configuration.parent not in output_set_of_components:
            set_of_parents = get_recursively_set_of_components_to_exclude(
                component_configuration.parent
            )
            output_set_of_components |= set_of_parents

    return output_set_of_components


def access_objects_for_add_new_and_reuse(component_type, path_of_the_components):
    template_name = "experiment/" + component_type + "_component.html"
    list_of_ids_of_components_and_configurations = path_of_the_components.split(
        delimiter
    )
    list_of_breadcrumbs = create_list_of_breadcrumbs(
        list_of_ids_of_components_and_configurations
    )

    block = None
    group = None

    experiment = None

    if (
        len(list_of_ids_of_components_and_configurations) > 1
        or path_of_the_components[0] != "G"
    ):
        # The last id of the list is the block where the new component will be added.
        block_id = list_of_ids_of_components_and_configurations[-1]
        block = get_object_or_404(Block, pk=block_id)
        experiment = block.experiment

    if path_of_the_components[0] == "G":
        # The id of the group comes after "G"
        group_id = int(list_of_ids_of_components_and_configurations[0][1:])
        group = get_object_or_404(Group, pk=group_id)
        experiment = group.experiment

    existing_component_list = Component.objects.filter(
        experiment=experiment, component_type=component_type
    )

    if block:
        set_of_components_to_exclude = get_recursively_set_of_components_to_exclude(
            block
        )
        for component in set_of_components_to_exclude:
            existing_component_list = existing_component_list.exclude(id=component.id)

    specific_form = None

    # If configuring a new experimental protocol for a group, return to the group. Otherwise, return to the parent
    # block.
    if (
        len(list_of_ids_of_components_and_configurations) == 1
        and path_of_the_components[0] == "G"
    ):
        back_cancel_url = "/experiment/group/" + str(group.id)
    else:
        back_cancel_url = "/experiment/component/" + path_of_the_components

    return (
        existing_component_list,
        experiment,
        group,
        list_of_breadcrumbs,
        block,
        template_name,
        specific_form,
        list_of_ids_of_components_and_configurations,
        back_cancel_url,
    )


@login_required
@permission_required("experiment.change_experiment")
def component_add_new(request, path_of_the_components, component_type):
    (
        existing_component_list,
        experiment,
        group,
        list_of_breadcrumbs,
        block,
        template_name,
        specific_form,
        list_of_ids_of_components_and_configurations,
        back_cancel_url,
    ) = access_objects_for_add_new_and_reuse(component_type, path_of_the_components)

    check_can_change(request.user, experiment.research_project)

    # Fixed or random
    position = get_position(request)

    # Number of uses to insert
    number_of_uses = get_number_of_uses(request)

    component_form = ComponentForm(request.POST or None)
    # This is needed for the form to be able to validate the presence of a
    # duration in a pause component only.
    component_form.component_type = component_type

    # Check if we are configuring a new experimental protocol
    is_configuring_new_experimental_protocol = (
        group is not None and len(list_of_ids_of_components_and_configurations) == 1
    )

    number_of_uses_form = None

    if not is_configuring_new_experimental_protocol:
        number_of_uses_form = NumberOfUsesToInsertForm(
            request.POST or None, initial={"number_of_uses_to_insert": number_of_uses}
        )

    questionnaires_list = []
    specific_form = None
    duration_string = None

    if component_type == "instruction":
        specific_form = InstructionForm(request.POST or None)
    elif component_type == "stimulus":
        specific_form = StimulusForm(request.POST or None, request.FILES)
    elif component_type == "eeg":
        specific_form = EEGForm(
            request.POST or None, initial={"experiment": experiment}
        )
    elif component_type == "emg":
        specific_form = EMGForm(
            request.POST or None, initial={"experiment": experiment}
        )
    elif component_type == "tms":
        specific_form = TMSForm(
            request.POST or None, initial={"experiment": experiment}
        )
    elif component_type == "questionnaire":
        questionnaires_list = Survey.objects.all()
    elif component_type == "block":
        specific_form = BlockForm(
            request.POST or None, initial={"number_of_mandatory_components": None}
        )
        duration_string = "0"
    elif component_type == "digital_game_phase":
        specific_form = DigitalGamePhaseForm(
            request.POST or None, initial={"experiment": experiment}
        )
    elif component_type == "generic_data_collection":
        specific_form = GenericDataCollectionForm(request.POST or None)

    elif component_type == "media_collection":
        specific_form = MediaCollectionForm(request.POST or None)

    if request.method == "POST":
        new_specific_component = None
        survey = None

        if component_type == "questionnaire":
            new_specific_component = Questionnaire()

            try:
                survey = Survey.objects.get(
                    lime_survey_id=request.POST["questionnaire_selected"]
                )
            except Survey.DoesNotExist:
                survey = Survey()
                survey.lime_survey_id = request.POST["questionnaire_selected"]

        elif component_type == "pause":
            new_specific_component = Pause()
        elif component_type == "task":
            new_specific_component = Task()
        elif component_type == "task_experiment":
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

            # If this is a new component for creating the root of a group's
            # experimental protocol, no component_configuration has to be
            # created.
            if is_configuring_new_experimental_protocol:
                new_specific_component.save()
                group.experimental_protocol = new_specific_component
                group.save()

                messages.success(
                    request, _("Experimental protocol included successfully.")
                )

                redirect_url = reverse(
                    "component_view",
                    args=(
                        path_of_the_components
                        + delimiter
                        + str(new_specific_component.id),
                    ),
                )
                return HttpResponseRedirect(redirect_url)
            else:
                if number_of_uses_form.is_valid():
                    if component_type == "questionnaire":
                        surveys = Questionnaires()
                        limesurvey_available = check_limesurvey_access(request, surveys)

                        if (
                            surveys.get_survey_properties(
                                survey.lime_survey_id, "active"
                            )
                            == "Y"
                        ):
                            survey.save()
                            new_specific_component.survey = survey
                        else:
                            survey.is_active = False
                            survey.save()

                    new_specific_component.save()

                    # saving uploaded files
                    files_to_upload_list = request.FILES.getlist("additional_files")
                    for file_to_upload in files_to_upload_list:
                        additional_file = ComponentAdditionalFile(
                            component=new_specific_component, file=file_to_upload
                        )
                        additional_file.save()

                    number_of_uses = number_of_uses_form.cleaned_data[
                        "number_of_uses_to_insert"
                    ]

                    for i in range(number_of_uses):
                        new_configuration = ComponentConfiguration()
                        new_configuration.component = new_specific_component
                        new_configuration.parent = block

                        if position is not None:
                            new_configuration.random_position = (
                                True if position == "random" else False
                            )

                        new_configuration.save()

                    if number_of_uses > 1:
                        messages.success(request, _("Steps included successfully."))
                    else:
                        messages.success(request, _("Step included successfully."))

                    redirect_url = reverse(
                        "component_view", args=(path_of_the_components,)
                    )

                    return HttpResponseRedirect(redirect_url)

    questionnaires_with_names = []

    for questionnaire in questionnaires_list:
        questionnaires_with_names.append(
            find_questionnaire_name(questionnaire, request.LANGUAGE_CODE)
        )

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
        "questionnaires_list": questionnaires_with_names,
        "path_of_the_components": path_of_the_components,
        "specific_form": specific_form,
        "can_change": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def component_reuse(request, path_of_the_components, component_id):
    component_to_add = get_object_or_404(Component, pk=component_id)
    component_type = component_to_add.component_type
    (
        existing_component_list,
        experiment,
        group,
        list_of_breadcrumbs,
        block,
        template_name,
        specific_form,
        list_of_ids_of_components_and_configurations,
        back_cancel_url,
    ) = access_objects_for_add_new_and_reuse(component_type, path_of_the_components)

    can_change = get_can_change(request.user, experiment.research_project)

    # Fixed or random
    position = get_position(request)

    # Number of uses to insert
    number_of_uses = get_number_of_uses(request)

    component_form = ComponentForm(request.POST or None, instance=component_to_add)
    # This is needed for the form to be able to validate the presence of a
    # duration in a pause component only.
    component_form.component_type = component_type

    # Check if we are configuring a new experimental protocol
    is_configuring_new_experimental_protocol = (
        group is not None and len(list_of_ids_of_components_and_configurations) == 1
    )

    number_of_uses_form = None

    if not is_configuring_new_experimental_protocol:
        number_of_uses_form = NumberOfUsesToInsertForm(
            request.POST or None, initial={"number_of_uses_to_insert": number_of_uses}
        )

    questionnaire_id = None
    questionnaire_title = None
    specific_form = None
    duration_string = None
    has_unlimited = None

    if component_type == "instruction":
        instruction = get_object_or_404(Instruction, pk=component_to_add.id)
        specific_form = InstructionForm(request.POST or None, instance=instruction)
    elif component_type == "stimulus":
        stimulus = get_object_or_404(Stimulus, pk=component_to_add.id)
        specific_form = StimulusForm(request.POST or None, instance=stimulus)
    elif component_type == "eeg":
        eeg = get_object_or_404(EEG, pk=component_to_add.id)
        specific_form = EEGForm(
            request.POST or None, instance=eeg, initial={"experiment": experiment}
        )
    elif component_type == "emg":
        emg = get_object_or_404(EMG, pk=component_to_add.id)
        specific_form = EMGForm(
            request.POST or None, instance=emg, initial={"experiment": experiment}
        )
    elif component_type == "tms":
        tms = get_object_or_404(TMS, pk=component_to_add.id)
        specific_form = TMSForm(
            request.POST or None, instance=tms, initial={"experiment": experiment}
        )
    elif component_type == "questionnaire":
        questionnaire = get_object_or_404(Questionnaire, pk=component_to_add.id)
        questionnaire_id = questionnaire.survey.lime_survey_id
        questionnaire_title = Questionnaires().get_survey_title(
            questionnaire.survey.lime_survey_id,
            get_questionnaire_language(
                Questionnaires(),
                questionnaire.survey.lime_survey_id,
                request.LANGUAGE_CODE,
            ),
        )

    elif component_type == "block":
        sub_block = get_object_or_404(Block, pk=component_id)
        specific_form = BlockForm(request.POST or None, instance=sub_block)
        duration_value, has_unlimited = calculate_block_duration(sub_block)
        # Create a string converting to appropriate units
        duration_string = convert_to_string(duration_value)

    elif component_type == "digital_game_phase":
        digital_game_phase = get_object_or_404(DigitalGamePhase, pk=component_to_add.id)
        specific_form = DigitalGamePhaseForm(
            request.POST or None,
            instance=digital_game_phase,
            initial={"experiment": experiment},
        )

    elif component_type == "generic_data_collection":
        generic_data_collection = get_object_or_404(
            GenericDataCollection, pk=component_to_add.id
        )
        specific_form = GenericDataCollectionForm(
            request.POST or None, instance=generic_data_collection
        )

    elif component_type == "media_collection":
        media_collection = get_object_or_404(MediaCollection, pk=component_to_add.id)
        specific_form = MediaCollectionForm(
            request.POST or None, instance=media_collection
        )

    if component_type == "questionnaire":
        for field in component_form.fields:
            component_form.fields[field].widget.attrs["disabled"] = True
    else:
        for field in component_form.fields:
            component_form.fields[field].widget.attrs["disabled"] = True

        if component_type not in ["pause", "task", "task_experiment"]:
            for field in specific_form.fields:
                specific_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        # If this is a reuse for creating the root of a group's experimental
        # protocol, no component_configuration has to be created.
        if is_configuring_new_experimental_protocol:
            group = Group.objects.get(id=path_of_the_components[1:])
            group.experimental_protocol = component_to_add
            group.save()

            redirect_url = reverse(
                "component_view",
                args=(path_of_the_components + delimiter + str(component_to_add.id),),
            )

            messages.success(request, _("Step included successfully."))
            return HttpResponseRedirect(redirect_url)
        else:
            if number_of_uses_form.is_valid():
                number_of_uses = number_of_uses_form.cleaned_data[
                    "number_of_uses_to_insert"
                ]

                for i in range(number_of_uses):
                    new_configuration = ComponentConfiguration()
                    new_configuration.component = component_to_add
                    new_configuration.parent = block

                    if position is not None:
                        new_configuration.random_position = (
                            True if position == "random" else False
                        )

                    new_configuration.save()

                redirect_url = reverse("component_view", args=(path_of_the_components,))

                if number_of_uses > 1:
                    messages.success(request, _("Steps included successfully."))
                else:
                    messages.success(request, _("Step included successfully."))

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
        "can_change": can_change,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eeg_electrode_localization_system_list(
    request, template_name="experiment/eeg_electrode_localization_system_list.html"
):
    return render(
        request,
        template_name,
        {
            "eeg_electrode_localization_systems": EEGElectrodeLocalizationSystem.objects.order_by(
                "name"
            )
        },
    )


@login_required
@permission_required("experiment.register_equipment")
def eeg_electrode_localization_system_create(
    request, template_name="experiment/eeg_electrode_localization_system_register.html"
):
    localization_system_form = EEGElectrodeLocalizationSystemRegisterForm(
        request.POST or None
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            localization_system_form = EEGElectrodeLocalizationSystemRegisterForm(
                request.POST, request.FILES
            )

            if localization_system_form.is_valid():
                localization_system_added = localization_system_form.save()

                messages.success(
                    request,
                    _("EEG electrode localization system created successfully."),
                )

                redirect_url = reverse(
                    "eeg_electrode_localization_system_view",
                    args=(localization_system_added.id,),
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))
        else:
            messages.warning(request, _("Action not available."))

    context = {
        "localization_system_form": localization_system_form,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eeg_electrode_localization_system_test(
    request,
    eeg_electrode_localization_system_id,
    template_name="experiment/eeg_electrode_localization_system_test.html",
):
    localization_system = get_object_or_404(
        EEGElectrodeLocalizationSystem, pk=eeg_electrode_localization_system_id
    )
    localization_system_form = EEGElectrodeLocalizationSystemRegisterForm(
        request.POST or None, instance=localization_system
    )

    for field in localization_system_form.fields:
        localization_system_form.fields[field].widget.attrs["disabled"] = True

    context = {
        "localization_system": localization_system,
        "localization_system_form": localization_system_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def eeg_electrode_position_change_the_order(
    request, eeg_electrode_position_id, command
):
    eeg_electrode_position = get_object_or_404(
        EEGElectrodePosition, pk=eeg_electrode_position_id
    )

    all_positions = EEGElectrodePosition.objects.filter(
        eeg_electrode_localization_system=eeg_electrode_position.eeg_electrode_localization_system
    )

    if command == "down":
        position_to_change = (
            all_positions.filter(
                channel_default_index__gt=eeg_electrode_position.channel_default_index
            )
            .order_by("channel_default_index")
            .first()
        )
    else:
        position_to_change = (
            all_positions.filter(
                channel_default_index__lt=eeg_electrode_position.channel_default_index
            )
            .order_by("-channel_default_index")
            .first()
        )

    bottom_position = all_positions.order_by("-channel_default_index").first()

    channel_index_current = eeg_electrode_position.channel_default_index
    channel_index_to_change = position_to_change.channel_default_index

    position_to_change.channel_default_index = bottom_position.channel_default_index + 1
    position_to_change.save()

    eeg_electrode_position.channel_default_index = channel_index_to_change
    eeg_electrode_position.save()

    position_to_change.channel_default_index = channel_index_current
    position_to_change.save()

    redirect_url = reverse(
        "eeg_electrode_localization_system_view",
        args=(eeg_electrode_position.eeg_electrode_localization_system_id,),
    )

    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.change_experiment")
def experiment_research_change_order(request, collaborator_position_id, command):
    position_status = get_object_or_404(
        ExperimentResearcher, pk=collaborator_position_id
    )

    all_positions = ExperimentResearcher.objects.filter(
        experiment=position_status.experiment
    )

    if command == "down":
        position_to_change = (
            all_positions.order_by("channel_index")
            .filter(channel_index__gt=position_status.channel_index)
            .first()
        )
    else:
        # position_to_change = all_positions.order_by('-channel_index').filter(
        #     channel_index__gt=position_status.channel_index).first()
        position_to_change = (
            all_positions.filter(channel_index__lt=position_status.channel_index)
            .order_by("-channel_index")
            .first()
        )

    bottom_position_setting = all_positions.order_by("-channel_index").first()
    # bottom_position_setting = position_status.objects.order_by('-channel_index').first()

    channel_index_current = position_status.channel_index
    channel_index_to_change = position_to_change.channel_index

    position_to_change.channel_index = bottom_position_setting.channel_index + 1
    position_to_change.save()

    position_status.channel_index = channel_index_to_change
    position_status.save()

    position_to_change.channel_index = channel_index_current
    position_to_change.save()

    redirect_url = reverse("experiment_view", args=(position_status.experiment.id,))

    return HttpResponseRedirect(redirect_url)


@login_required
@permission_required("experiment.register_equipment")
def eeg_electrode_localization_system_view(
    request,
    eeg_electrode_localization_system_id,
    template_name="experiment/eeg_electrode_localization_system_register.html",
):
    localization_system = get_object_or_404(
        EEGElectrodeLocalizationSystem, pk=eeg_electrode_localization_system_id
    )
    localization_system_form = EEGElectrodeLocalizationSystemRegisterForm(
        request.POST or None, instance=localization_system
    )

    for field in localization_system_form.fields:
        localization_system_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            if (
                EEGElectrodeNetSystem.objects.filter(
                    eeg_electrode_localization_system=localization_system
                ).count()
                == 0
            ):
                try:
                    localization_system.delete()
                    messages.success(request, _("Study removed successfully."))
                    return redirect("eeg_electrode_localization_system_list")
                except ProtectedError:
                    messages.error(
                        request, _("Error trying to delete localization system.")
                    )
                    redirect_url = reverse(
                        "eeg_electrode_localization_system_view",
                        args=(eeg_electrode_localization_system_id,),
                    )
                    return HttpResponseRedirect(redirect_url)

            else:
                messages.error(
                    request,
                    _(
                        "Impossible to delete localization system because there is (are) Electrode Net associated."
                    ),
                )
                redirect_url = reverse(
                    "eeg_electrode_localization_system_view",
                    args=(eeg_electrode_localization_system_id,),
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "localization_system": localization_system,
        "localization_system_form": localization_system_form,
        "editing": False,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eeg_electrode_localization_system_update(
    request,
    eeg_electrode_localization_system_id,
    template_name="experiment/eeg_electrode_localization_system_register.html",
):
    localization_system = get_object_or_404(
        EEGElectrodeLocalizationSystem, pk=eeg_electrode_localization_system_id
    )
    localization_system_form = EEGElectrodeLocalizationSystemRegisterForm(
        request.POST or None, instance=localization_system
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            localization_system_form = EEGElectrodeLocalizationSystemRegisterForm(
                request.POST, request.FILES, instance=localization_system
            )

            if localization_system_form.is_valid():
                if localization_system_form.has_changed():
                    localization_system_form.save()
                    messages.success(
                        request, _("Localization system updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "eeg_electrode_localization_system_view",
                    args=(eeg_electrode_localization_system_id,),
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "localization_system": localization_system,
        "localization_system_form": localization_system_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eeg_electrode_coordinates_create(
    request,
    eeg_electrode_localization_system_id,
    template_name="experiment/eeg_electrode_coordinates_register.html",
):
    localization_system = get_object_or_404(
        EEGElectrodeLocalizationSystem, pk=eeg_electrode_localization_system_id
    )

    positions = []
    for position_setting in localization_system.electrode_positions.all():
        used = EEGElectrodePositionSetting.objects.filter(
            eeg_electrode_position_id=int(position_setting.id)
        ).exists()

        positions.append(
            {
                "id": position_setting.id,
                "position": position_setting.name,
                "x": position_setting.coordinate_x,
                "y": position_setting.coordinate_y,
                # 'used' indicates when this point is used at least one by some layout
                "used": used,
                # 'existInDB' indicates if the point exist at the DB
                "existInDB": True,
                # 'delete' indicates if this point will be deleted
                "delete": False,
                # 'update' indicates if this point will be updated
                "update": False,
            }
        )

    if request.method == "POST":
        if request.POST["action"] == "save":
            messages.success(
                request, _("EEG electrode positions updated successfully.")
            )
            redirect_url = reverse(
                "eeg_electrode_localization_system_view",
                args=(eeg_electrode_localization_system_id,),
            )
            return HttpResponseRedirect(redirect_url)

    context = {
        "localization_system": localization_system,
        "json_list": json.dumps(positions),
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eeg_electrode_position_create(
    request,
    eeg_electrode_localization_system_id,
    template_name="experiment/eeg_electrode_position_register.html",
):
    localization_system = get_object_or_404(
        EEGElectrodeLocalizationSystem, pk=eeg_electrode_localization_system_id
    )

    position_form = EEGElectrodePositionForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if position_form.is_valid():
                position_added = position_form.save(commit=False)
                position_added.eeg_electrode_localization_system = localization_system
                position_added.save()

                messages.success(
                    request, _("EEG electrode position created successfully.")
                )

                redirect_url = reverse(
                    "eeg_electrode_localization_system_view",
                    args=(eeg_electrode_localization_system_id,),
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))
        else:
            messages.warning(request, _("Action not available."))

    context = {
        "position_form": position_form,
        "localization_system": localization_system,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eeg_electrode_position_view(
    request,
    eeg_electrode_position_id,
    template_name="experiment/eeg_electrode_position_register.html",
):
    position = get_object_or_404(EEGElectrodePosition, pk=eeg_electrode_position_id)
    position_form = EEGElectrodePositionForm(request.POST or None, instance=position)

    for field in position_form.fields:
        position_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            if (
                EEGElectrodePositionSetting.objects.filter(
                    eeg_electrode_position=position
                ).count()
                == 0
            ):
                try:
                    localization_system_id = (
                        position.eeg_electrode_localization_system_id
                    )
                    position.delete()
                    messages.success(request, _("Position removed successfully."))

                    redirect_url = reverse(
                        "eeg_electrode_localization_system_view",
                        args=(localization_system_id,),
                    )
                    return HttpResponseRedirect(redirect_url)
                except ProtectedError:
                    messages.error(request, _("Error trying to delete position."))
                    redirect_url = reverse(
                        "eeg_electrode_position_view", args=(eeg_electrode_position_id,)
                    )
                    return HttpResponseRedirect(redirect_url)

            else:
                messages.error(
                    request,
                    _(
                        "Impossible to delete position because there is (are) Position Setting associated."
                    ),
                )
                redirect_url = reverse(
                    "eeg_electrode_position_view", args=(eeg_electrode_position_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "position": position,
        "position_form": position_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def eeg_electrode_position_update(
    request,
    eeg_electrode_position_id,
    template_name="experiment/eeg_electrode_position_register.html",
):
    position = get_object_or_404(EEGElectrodePosition, pk=eeg_electrode_position_id)
    position_form = EEGElectrodePositionForm(request.POST or None, instance=position)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if position_form.is_valid():
                if position_form.has_changed():
                    position_form.save()
                    messages.success(request, _("Position updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "eeg_electrode_position_view", args=(eeg_electrode_position_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {"position": position, "position_form": position_form, "editing": True}

    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_subject")
def emg_setting_create(
    request, experiment_id, template_name="experiment/emg_setting_register.html"
):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    check_can_change(request.user, experiment.research_project)

    emg_setting_form = EMGSettingForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if emg_setting_form.is_valid() and "software_version" in request.POST:
                emg_setting_added = emg_setting_form.save(commit=False)
                emg_setting_added.experiment_id = experiment_id
                emg_setting_added.acquisition_software_version_id = request.POST[
                    "software_version"
                ]
                emg_setting_added.save()

                messages.success(request, _("EMG setting included successfully."))

                redirect_url = reverse("emg_setting_view", args=(emg_setting_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "emg_setting_form": emg_setting_form,
        "creating": True,
        "editing": True,
        "experiment": experiment,
        "software_version_list": SoftwareVersion.objects.all(),
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def emg_setting_view(
    request, emg_setting_id, template_name="experiment/emg_setting_register.html"
):
    emg_setting = get_object_or_404(EMGSetting, pk=emg_setting_id)
    emg_setting_form = EMGSettingForm(request.POST or None, instance=emg_setting)

    for field in emg_setting_form.fields:
        emg_setting_form.fields[field].widget.attrs["disabled"] = True

    can_change = get_can_change(request.user, emg_setting.experiment.research_project)

    if request.method == "POST":
        if can_change:
            if request.POST["action"] == "remove":
                # TODO: checking if there is some EEG Data using it

                # TODO: checking if there is some EEG Step using it

                experiment_id = emg_setting.experiment_id

                emg_setting.delete()

                messages.success(request, _("EMG setting was removed successfully."))

                redirect_url = reverse("experiment_view", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

            if request.POST["action"][:7] == "remove-":
                # If action starts with 'remove-' it means that a setting should be removed from the emg_setting.
                emg_setting_type = request.POST["action"][7:]

                setting_to_be_deleted = None

                if emg_setting_type == "digital_filter":
                    setting_to_be_deleted = get_object_or_404(
                        EMGDigitalFilterSetting, pk=emg_setting_id
                    )
                elif emg_setting_type == "ad_converter":
                    setting_to_be_deleted = get_object_or_404(
                        EMGADConverterSetting, pk=emg_setting_id
                    )
                elif emg_setting_type[:10] == "electrode-":
                    setting_to_be_deleted = get_object_or_404(
                        EMGElectrodeSetting, pk=int(emg_setting_type[10:])
                    )

                # eeg_setting.eeg_machine_setting.delete()
                if setting_to_be_deleted:
                    setting_to_be_deleted.delete()

                messages.success(request, _("Setting was removed successfully."))

                redirect_url = reverse("emg_setting_view", args=(emg_setting.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": can_change,
        "emg_setting_form": emg_setting_form,
        "experiment": emg_setting.experiment,
        "emg_setting": emg_setting,
        "editing": False,
        "software_version_list": SoftwareVersion.objects.filter(
            id=emg_setting.acquisition_software_version.id
        ),
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_setting_update(
    request, emg_setting_id, template_name="experiment/emg_setting_register.html"
):
    emg_setting = get_object_or_404(EMGSetting, pk=emg_setting_id)

    check_can_change(request.user, emg_setting.experiment.research_project)

    emg_setting_form = EMGSettingForm(request.POST or None, instance=emg_setting)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if emg_setting_form.is_valid() and "software_version" in request.POST:
                changed = False

                if emg_setting_form.has_changed():
                    emg_setting_form.save()
                    changed = True

                if emg_setting.acquisition_software_version_id != int(
                    request.POST["software_version"]
                ):
                    emg_setting.acquisition_software_version_id = request.POST[
                        "software_version"
                    ]
                    emg_setting.save()
                    changed = True

                if changed:
                    messages.success(request, _("EMG setting updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("emg_setting_view", args=(emg_setting_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "emg_setting_form": emg_setting_form,
        "editing": True,
        "experiment": emg_setting.experiment,
        "emg_setting": emg_setting,
        "software_version_list": SoftwareVersion.objects.all(),
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_setting_digital_filter(
    request, emg_setting_id, template_name="experiment/emg_setting_digital_filter.html"
):
    emg_setting = get_object_or_404(EMGSetting, pk=emg_setting_id)

    can_change = get_can_change(request.user, emg_setting.experiment.research_project)

    creating = False

    if hasattr(emg_setting, "emg_digital_filter_setting"):
        emg_digital_filter_setting = EMGDigitalFilterSetting.objects.get(
            emg_setting=emg_setting
        )

        emg_digital_filter_setting_form = EMGDigitalFilterSettingForm(
            request.POST or None, instance=emg_digital_filter_setting
        )

        filter_selected = emg_digital_filter_setting.filter_type

        equipment_form = EEGFilterForm(request.POST or None, instance=filter_selected)

        for field in emg_digital_filter_setting_form.fields:
            emg_digital_filter_setting_form.fields[field].widget.attrs[
                "disabled"
            ] = True

    else:
        creating = True
        emg_digital_filter_setting_form = EMGDigitalFilterSettingForm(
            request.POST or None
        )
        equipment_form = EEGFilterForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if emg_digital_filter_setting_form.is_valid():
                if emg_digital_filter_setting_form.has_changed():
                    new_setting = emg_digital_filter_setting_form.save(commit=False)
                    new_setting.emg_setting = emg_setting
                    new_setting.save()

                    messages.success(
                        request, _("EMG digital filter setting created successfully.")
                    )

                    redirect_url = reverse("emg_setting_view", args=(emg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

    context = {
        "creating": creating,
        "editing": False,
        "can_change": can_change,
        "emg_setting": emg_setting,
        "emg_digital_filter_setting_form": emg_digital_filter_setting_form,
        "equipment_form": equipment_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_setting_digital_filter_edit(
    request, emg_setting_id, template_name="experiment/emg_setting_digital_filter.html"
):
    emg_setting = get_object_or_404(EMGSetting, pk=emg_setting_id)

    check_can_change(request.user, emg_setting.experiment.research_project)

    emg_digital_filter_setting = emg_setting.emg_digital_filter_setting
    emg_digital_filter_setting_form = EMGDigitalFilterSettingForm(
        request.POST or None, instance=emg_digital_filter_setting
    )

    filter_selected = emg_digital_filter_setting.filter_type

    equipment_form = EEGFilterForm(request.POST or None, instance=filter_selected)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if emg_digital_filter_setting_form.is_valid():
                if emg_digital_filter_setting_form.has_changed():
                    emg_digital_filter_setting_form.save()

                    messages.success(
                        request, _("EMG digital filter setting updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "emg_setting_digital_filter", args=(emg_setting_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "creating": False,
        "editing": True,
        "can_change": True,
        "emg_setting": emg_setting,
        "emg_digital_filter_setting_form": emg_digital_filter_setting_form,
        "equipment_form": equipment_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_setting_ad_converter(
    request, emg_setting_id, template_name="experiment/emg_setting_ad_converter.html"
):
    emg_setting = get_object_or_404(EMGSetting, pk=emg_setting_id)

    can_change = get_can_change(request.user, emg_setting.experiment.research_project)

    creating = False

    if hasattr(emg_setting, "emg_ad_converter_setting"):
        emg_ad_converter_setting = EMGADConverterSetting.objects.get(
            emg_setting=emg_setting
        )

        emg_ad_converter_setting_form = EMGADConverterSettingForm(
            request.POST or None, instance=emg_ad_converter_setting
        )

        emg_ad_converter_selected = emg_ad_converter_setting.ad_converter

        equipment_form = EquipmentForm(
            request.POST or None, instance=emg_ad_converter_selected
        )

        for field in emg_ad_converter_setting_form.fields:
            emg_ad_converter_setting_form.fields[field].widget.attrs["disabled"] = True

    else:
        creating = True
        emg_ad_converter_setting_form = EMGADConverterSettingForm(request.POST or None)
        equipment_form = EquipmentForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if emg_ad_converter_setting_form.is_valid():
                if emg_ad_converter_setting_form.has_changed():
                    new_setting = emg_ad_converter_setting_form.save(commit=False)
                    new_setting.emg_setting = emg_setting
                    new_setting.save()

                    messages.success(
                        request, _("EMG A/D converter setting created successfully.")
                    )

                    redirect_url = reverse("emg_setting_view", args=(emg_setting_id,))
                    return HttpResponseRedirect(redirect_url)

    context = {
        "creating": creating,
        "editing": False,
        "can_change": can_change,
        "emg_setting": emg_setting,
        "emg_ad_converter_setting_form": emg_ad_converter_setting_form,
        "equipment_form": equipment_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_setting_ad_converter_edit(
    request, emg_setting_id, template_name="experiment/emg_setting_ad_converter.html"
):
    emg_setting = get_object_or_404(EMGSetting, pk=emg_setting_id)

    check_can_change(request.user, emg_setting.experiment.research_project)

    emg_ad_converter_setting = emg_setting.emg_ad_converter_setting
    emg_ad_converter_setting_form = EMGADConverterSettingForm(
        request.POST or None, instance=emg_ad_converter_setting
    )

    emg_ad_converter_selected = emg_ad_converter_setting.ad_converter

    equipment_form = EquipmentForm(
        request.POST or None, instance=emg_ad_converter_selected
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if emg_ad_converter_setting_form.is_valid():
                if emg_ad_converter_setting_form.has_changed():
                    emg_ad_converter_setting_form.save()

                    messages.success(
                        request, _("EMG A/D converter setting updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "emg_setting_ad_converter", args=(emg_setting_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "creating": False,
        "editing": True,
        "can_change": True,
        "emg_setting": emg_setting,
        "emg_ad_converter_setting_form": emg_ad_converter_setting_form,
        "equipment_form": equipment_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def get_json_coilmodel_attributes(request, coilmodel_id):
    coil_model = get_object_or_404(CoilModel, pk=coilmodel_id)

    response_data = {"description": coil_model.description}

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def get_anatomical_description_by_placement(
    request, emg_electrode_type, emg_electrode_placement_id
):
    response_data = []
    if emg_electrode_type == "surface":
        anatomical_description = EMGSurfacePlacement.objects.get(
            pk=emg_electrode_placement_id
        )
        response_data = {
            "start_posture": anatomical_description.start_posture,
            "orientation": anatomical_description.orientation,
            "fixation_on_the_skin": anatomical_description.fixation_on_the_skin,
            "reference_electrode": anatomical_description.reference_electrode,
            "clinical_test": anatomical_description.clinical_test,
        }

    if emg_electrode_type == "intramuscular":
        anatomical_description = EMGIntramuscularPlacement.objects.get(
            pk=emg_electrode_placement_id
        )
        response_data = {
            "method_of_insertion": anatomical_description.method_of_insertion,
            "depth_of_insertion": anatomical_description.depth_of_insertion,
        }

    if emg_electrode_type == "needle":
        anatomical_description = EMGNeedlePlacement.objects.get(
            pk=emg_electrode_placement_id
        )

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def get_json_muscle_side_by_electrode_placement(request, emg_electrode_placement_id):
    muscle_side_list = MuscleSide.objects.filter(
        muscle__musclesubdivision__emgelectrodeplacement__in=emg_electrode_placement_id
    )

    json_muscle_side = serializers.serialize("json", muscle_side_list)
    return HttpResponse(json_muscle_side, content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def get_json_electrode_model(request, electrode_id):
    electrode_model = get_object_or_404(ElectrodeModel, pk=electrode_id)

    response_data = {
        "description": electrode_model.description,
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def get_json_electrode_by_type(request, electrode_type):
    electrode_list = ElectrodeModel.objects.filter(
        electrode_type=electrode_type, tags__name="EMG"
    )

    json_electrode_list = serializers.serialize("json", electrode_list)
    return HttpResponse(json_electrode_list, content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def get_electrode_placement_by_type(request, electrode_type):
    electrode_placement_list = EMGElectrodePlacement.objects.filter(
        placement_type=electrode_type
    )
    placements = []

    if electrode_placement_list.exists():
        for electrode_placement in electrode_placement_list:
            system_name = electrode_placement.standardization_system.name
            muscle_subdivision_name = electrode_placement.muscle_subdivision.name
            muscle_name = electrode_placement.muscle_subdivision.muscle.name
            muscle_subdivision_anatomy_function = (
                electrode_placement.muscle_subdivision.anatomy_function
            )
            muscle_subdivision_anatomy_insertion = (
                electrode_placement.muscle_subdivision.anatomy_insertion
            )
            muscle_subdivision_anatomy_origin = (
                electrode_placement.muscle_subdivision.anatomy_origin
            )
            start_posture = ""
            orientation = ""
            fixation_on_the_skin = ""
            reference_electrode = ""
            clinical_test = ""

            if electrode_type == "surface":
                surface_placement = EMGSurfacePlacement.objects.filter(
                    pk=electrode_placement.id
                )
                for surface in surface_placement:
                    start_posture = surface.start_posture
                    orientation = surface.orientation
                    fixation_on_the_skin = surface.fixation_on_the_skin
                    reference_electrode = surface.reference_electrode
                    clinical_test = surface.clinical_test

            placements.append(
                {
                    "id": electrode_placement.id,
                    "description": system_name
                    + " - "
                    + muscle_name
                    + " - "
                    + muscle_subdivision_name,
                    "anatomy_function": muscle_subdivision_anatomy_function,
                    "anatomy_insertion": muscle_subdivision_anatomy_insertion,
                    "anatomy_origin": muscle_subdivision_anatomy_origin,
                    "start_posture": start_posture,
                    "orientation": orientation,
                    "fixation_on_the_skin": fixation_on_the_skin,
                    "reference_electrode": reference_electrode,
                    "clinical_test": clinical_test,
                }
            )

    return HttpResponse(json.dumps(placements), content_type="application/json")


@login_required
@permission_required("experiment.change_experiment")
def emg_setting_electrode_add(
    request, emg_setting_id, template_name="experiment/emg_setting_electrode.html"
):
    emg_setting = get_object_or_404(EMGSetting, pk=emg_setting_id)

    check_can_change(request.user, emg_setting.experiment.research_project)

    emg_electrode_setting_form = EMGElectrodeSettingForm(request.POST or None)
    emg_electrode_placement_setting_form = EMGElectrodePlacementSettingForm(
        request.POST or None
    )

    emg_electrode_model_form = ElectrodeModelForm(request.POST or None)

    emg_surface_placement_form = EMGSurfacePlacementForm(request.POST or None)

    emg_intramuscular_placement_form = EMGIntramuscularPlacementForm(
        request.POST or None
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if (
                emg_electrode_setting_form.is_valid()
                and emg_electrode_placement_setting_form.is_valid()
            ):
                # if emg_ad_converter_setting_form.has_changed():

                new_emg_electrode_setting = emg_electrode_setting_form.save(
                    commit=False
                )
                new_emg_electrode_setting.emg_setting = emg_setting
                new_emg_electrode_setting.save()

                new_emg_placement_setting = emg_electrode_placement_setting_form.save(
                    commit=False
                )
                new_emg_placement_setting.emg_electrode_setting = (
                    new_emg_electrode_setting
                )
                new_emg_placement_setting.save()

                messages.success(
                    request, _("EMG electrode setting created successfully.")
                )

                redirect_url = reverse(
                    "emg_electrode_setting_view", args=(new_emg_electrode_setting.id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "creating": True,
        "editing": True,
        "can_change": True,
        "emg_setting": emg_setting,
        "emg_electrode_setting_form": emg_electrode_setting_form,
        "emg_electrode_placement_setting_form": emg_electrode_placement_setting_form,
        "emg_electrode_model_form": emg_electrode_model_form,
        "emg_surface_placement_form": emg_surface_placement_form,
        "emg_intramuscular_placement_form": emg_intramuscular_placement_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_electrode_setting_view(
    request,
    emg_electrode_setting_id,
    template_name="experiment/emg_setting_electrode.html",
):
    emg_electrode_setting = get_object_or_404(
        EMGElectrodeSetting, pk=emg_electrode_setting_id
    )

    can_change = get_can_change(
        request.user, emg_electrode_setting.emg_setting.experiment.research_project
    )

    emg_electrode_setting_form = EMGElectrodeSettingForm(
        request.POST or None, instance=emg_electrode_setting
    )

    emg_electrode_placement_setting_form = EMGElectrodePlacementSettingForm(
        request.POST or None,
        instance=emg_electrode_setting.emg_electrode_placement_setting,
    )

    emg_electrode_model_form = ElectrodeModelForm(
        request.POST or None, instance=emg_electrode_setting.electrode
    )

    emg_surface_placement_form = EMGSurfacePlacementForm(request.POST or None)

    emg_intramuscular_placement_form = EMGIntramuscularPlacementForm(
        request.POST or None
    )

    for field in emg_electrode_setting_form.fields:
        emg_electrode_setting_form.fields[field].widget.attrs["disabled"] = True

    for field in emg_electrode_placement_setting_form.fields:
        emg_electrode_placement_setting_form.fields[field].widget.attrs[
            "disabled"
        ] = True

    for field in emg_electrode_model_form.fields:
        emg_electrode_model_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"][:7] == "remove-":
            # If action starts with 'remove-' it means that a setting should be removed from the emg_setting.
            emg_electrode_setting_type = request.POST["action"][7:]

            setting_to_be_deleted = None

            if emg_electrode_setting_type == "preamplifier":
                setting_to_be_deleted = get_object_or_404(
                    EMGPreamplifierSetting, pk=emg_electrode_setting_id
                )
            elif emg_electrode_setting_type == "amplifier":
                setting_to_be_deleted = get_object_or_404(
                    EMGAmplifierSetting, pk=emg_electrode_setting_id
                )

            # eeg_setting.eeg_machine_setting.delete()
            if setting_to_be_deleted:
                setting_to_be_deleted.delete()
                messages.success(request, _("Setting was removed successfully."))

            redirect_url = reverse(
                "emg_electrode_setting_view", args=(emg_electrode_setting.id,)
            )
            return HttpResponseRedirect(redirect_url)

    context = {
        "creating": False,
        "editing": False,
        "can_change": can_change,
        "emg_setting": emg_electrode_setting.emg_setting,
        "emg_electrode_setting": emg_electrode_setting,
        "emg_electrode_setting_form": emg_electrode_setting_form,
        "emg_electrode_placement_setting_form": emg_electrode_placement_setting_form,
        "emg_electrode_model_form": emg_electrode_model_form,
        "emg_surface_placement_form": emg_surface_placement_form,
        "emg_intramuscular_placement_form": emg_intramuscular_placement_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_electrode_setting_edit(
    request,
    emg_electrode_setting_id,
    template_name="experiment/emg_setting_electrode.html",
):
    emg_electrode_setting = get_object_or_404(
        EMGElectrodeSetting, pk=emg_electrode_setting_id
    )

    check_can_change(
        request.user, emg_electrode_setting.emg_setting.experiment.research_project
    )

    emg_electrode_setting_form = EMGElectrodeSettingForm(
        request.POST or None, instance=emg_electrode_setting
    )

    emg_electrode_placement_setting_form = EMGElectrodePlacementSettingForm(
        request.POST or None,
        instance=emg_electrode_setting.emg_electrode_placement_setting,
    )

    emg_electrode_model_form = ElectrodeModelForm(
        request.POST or None, instance=emg_electrode_setting.electrode
    )

    emg_surface_placement_form = EMGSurfacePlacementForm(request.POST or None)

    emg_intramuscular_placement_form = EMGIntramuscularPlacementForm(
        request.POST or None
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if (
                emg_electrode_setting_form.is_valid()
                and emg_electrode_placement_setting_form.is_valid()
            ):
                # if emg_ad_converter_setting_form.has_changed():

                emg_electrode_setting_form.save()
                emg_electrode_placement_setting_form.save()

                messages.success(
                    request, _("EMG electrode setting was updated successfully.")
                )

                redirect_url = reverse(
                    "emg_electrode_setting_view", args=(emg_electrode_setting_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "creating": False,
        "editing": True,
        "can_change": True,
        "emg_setting": emg_electrode_setting.emg_setting,
        "emg_electrode_setting": emg_electrode_setting,
        "emg_electrode_setting_form": emg_electrode_setting_form,
        "emg_electrode_placement_setting_form": emg_electrode_placement_setting_form,
        "emg_electrode_model_form": emg_electrode_model_form,
        "emg_surface_placement_form": emg_surface_placement_form,
        "emg_intramuscular_placement_form": emg_intramuscular_placement_form,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_electrode_setting_preamplifier(
    request,
    emg_electrode_setting_id,
    template_name="experiment/emg_electrode_setting_preamplifier.html",
):
    emg_electrode_setting = get_object_or_404(
        EMGElectrodeSetting, pk=emg_electrode_setting_id
    )

    can_change = get_can_change(
        request.user, emg_electrode_setting.emg_setting.experiment.research_project
    )

    creating = False

    list_of_manufacturers = Manufacturer.objects.filter(
        set_of_equipment__equipment_type="amplifier", set_of_equipment__tags__name="EMG"
    ).distinct()

    if hasattr(emg_electrode_setting, "emg_preamplifier_setting"):
        emg_preamplifier_setting = EMGPreamplifierSetting.objects.get(
            emg_electrode_setting=emg_electrode_setting
        )

        emg_preamplifier_setting_form = EMGPreamplifierSettingForm(
            request.POST or None, instance=emg_preamplifier_setting
        )

        equipment_selected = emg_preamplifier_setting.amplifier

        equipment_form = EquipmentForm(
            request.POST or None, instance=equipment_selected
        )

        if hasattr(emg_preamplifier_setting, "emg_preamplifier_filter_setting"):
            emg_preamplifier_filter_setting = EMGPreamplifierFilterSetting.objects.get(
                emg_preamplifier_filter_setting=emg_preamplifier_setting
            )

            emg_preamplifier_filter_setting_form = EMGPreamplifierFilterSettingForm(
                request.POST or None, instance=emg_preamplifier_filter_setting
            )

        else:
            emg_preamplifier_filter_setting_form = EMGPreamplifierFilterSettingForm(
                request.POST or None
            )

        for field in emg_preamplifier_setting_form.fields:
            emg_preamplifier_setting_form.fields[field].widget.attrs["disabled"] = True

        for field in emg_preamplifier_filter_setting_form.fields:
            emg_preamplifier_filter_setting_form.fields[field].widget.attrs[
                "disabled"
            ] = True

    else:
        creating = True
        emg_preamplifier_setting_form = EMGPreamplifierSettingForm(request.POST or None)
        emg_preamplifier_filter_setting_form = EMGPreamplifierFilterSettingForm(
            request.POST or None
        )
        equipment_form = EquipmentForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if (
                emg_preamplifier_setting_form.is_valid()
                and emg_preamplifier_filter_setting_form.is_valid()
            ):
                changed = False

                if (
                    emg_preamplifier_setting_form.has_changed()
                    or emg_preamplifier_filter_setting_form.has_changed()
                ):
                    new_setting = emg_preamplifier_setting_form.save(commit=False)
                    new_setting.emg_electrode_setting = emg_electrode_setting
                    new_setting.save()

                    new_setting = emg_preamplifier_filter_setting_form.save(
                        commit=False
                    )
                    new_setting.emg_preamplifier_filter_setting = (
                        emg_electrode_setting.emg_preamplifier_setting
                    )
                    new_setting.save()
                    changed = True

                    if changed:
                        messages.success(
                            request, _("EMG preamplifier setting created successfully.")
                        )
                    else:
                        messages.success(request, _("There is no changes to save."))

                    redirect_url = reverse(
                        "emg_electrode_setting_view", args=(emg_electrode_setting_id,)
                    )
                    return HttpResponseRedirect(redirect_url)

    context = {
        "creating": creating,
        "editing": False,
        "can_change": can_change,
        "emg_electrode_setting": emg_electrode_setting,
        "emg_preamplifier_setting_form": emg_preamplifier_setting_form,
        "emg_preamplifier_filter_setting_form": emg_preamplifier_filter_setting_form,
        "equipment_form": equipment_form,
        "manufacturer_list": list_of_manufacturers,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_electrode_setting_preamplifier_edit(
    request,
    emg_electrode_setting_id,
    template_name="experiment/emg_electrode_setting_preamplifier.html",
):
    emg_electrode_setting = get_object_or_404(
        EMGElectrodeSetting, pk=emg_electrode_setting_id
    )

    check_can_change(
        request.user, emg_electrode_setting.emg_setting.experiment.research_project
    )

    emg_preamplifier_setting = emg_electrode_setting.emg_preamplifier_setting
    emg_preamplifier_setting_form = EMGPreamplifierSettingForm(
        request.POST or None, instance=emg_preamplifier_setting
    )

    emg_preamplifier_selected = emg_preamplifier_setting.amplifier

    equipment_form = EquipmentForm(
        request.POST or None, instance=emg_preamplifier_selected
    )

    list_of_manufacturers = Manufacturer.objects.filter(
        set_of_equipment__equipment_type="amplifier", set_of_equipment__tags__name="EMG"
    ).distinct()

    if hasattr(emg_preamplifier_setting, "emg_preamplifier_filter_setting"):
        emg_preamplifier_filter_setting = (
            emg_electrode_setting.emg_preamplifier_setting.emg_preamplifier_filter_setting
        )
        emg_preamplifier_filter_setting_form = EMGPreamplifierFilterSettingForm(
            request.POST or None, instance=emg_preamplifier_filter_setting
        )
    else:
        emg_preamplifier_filter_setting_form = EMGPreamplifierFilterSettingForm(
            request.POST or None
        )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if emg_preamplifier_setting_form.is_valid():
                changed = False

                if emg_preamplifier_setting_form.has_changed():
                    emg_preamplifier_setting_form.save()
                    changed = True

                if (
                    emg_preamplifier_filter_setting_form.has_changed()
                    or emg_preamplifier_filter_setting_form.has_changed()
                ):
                    if hasattr(
                        emg_preamplifier_setting, "emg_preamplifier_filter_setting"
                    ):
                        emg_preamplifier_filter_setting_form.save()
                    else:
                        new_setting = emg_preamplifier_filter_setting_form.save(
                            commit=False
                        )
                        new_setting.emg_preamplifier_filter_setting = (
                            emg_preamplifier_setting
                        )
                        new_setting.save()

                    changed = True

                if changed:
                    messages.success(
                        request, _("EMG Preamplifier setting updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "emg_electrode_setting_preamplifier",
                    args=(emg_electrode_setting_id,),
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "creating": False,
        "editing": True,
        "can_change": True,
        "emg_electrode_setting": emg_electrode_setting,
        "emg_preamplifier_setting_form": emg_preamplifier_setting_form,
        "emg_preamplifier_filter_setting_form": emg_preamplifier_filter_setting_form,
        "equipment_form": equipment_form,
        "manufacturer_list": list_of_manufacturers,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_electrode_setting_amplifier(
    request,
    emg_electrode_setting_id,
    template_name="experiment/emg_electrode_setting_amplifier.html",
):
    emg_electrode_setting = get_object_or_404(
        EMGElectrodeSetting, pk=emg_electrode_setting_id
    )

    can_change = get_can_change(
        request.user, emg_electrode_setting.emg_setting.experiment.research_project
    )

    creating = False

    list_of_manufacturers = Manufacturer.objects.filter(
        set_of_equipment__equipment_type="amplifier", set_of_equipment__tags__name="EMG"
    ).distinct()

    if hasattr(emg_electrode_setting, "emg_amplifier_setting"):
        emg_amplifier_setting = EMGAmplifierSetting.objects.get(
            emg_electrode_setting=emg_electrode_setting
        )

        emg_amplifier_setting_form = EMGAmplifierSettingForm(
            request.POST or None, instance=emg_amplifier_setting
        )

        equipment_selected = emg_amplifier_setting.amplifier

        equipment_form = EquipmentForm(
            request.POST or None, instance=equipment_selected
        )

        if hasattr(emg_amplifier_setting, "emg_analog_filter_setting"):
            emg_analog_filter_setting = EMGAnalogFilterSetting.objects.get(
                emg_electrode_setting=emg_amplifier_setting
            )

            emg_analog_filter_setting_form = EMGAnalogFilterSettingForm(
                request.POST or None, instance=emg_analog_filter_setting
            )

        else:
            emg_analog_filter_setting_form = EMGAnalogFilterSettingForm(
                request.POST or None
            )

        for field in emg_amplifier_setting_form.fields:
            emg_amplifier_setting_form.fields[field].widget.attrs["disabled"] = True

        for field in emg_analog_filter_setting_form.fields:
            emg_analog_filter_setting_form.fields[field].widget.attrs["disabled"] = True

    else:
        creating = True
        emg_amplifier_setting_form = EMGAmplifierSettingForm(request.POST or None)
        emg_analog_filter_setting_form = EMGAnalogFilterSettingForm(
            request.POST or None
        )
        equipment_form = EquipmentForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if (
                emg_amplifier_setting_form.is_valid()
                and emg_analog_filter_setting_form.is_valid()
            ):
                changed = False

                if (
                    emg_amplifier_setting_form.has_changed()
                    or emg_analog_filter_setting_form.has_changed()
                ):
                    new_setting = emg_amplifier_setting_form.save(commit=False)
                    new_setting.emg_electrode_setting = emg_electrode_setting
                    new_setting.save()

                    new_setting = emg_analog_filter_setting_form.save(commit=False)
                    new_setting.emg_electrode_setting = (
                        emg_electrode_setting.emg_amplifier_setting
                    )
                    new_setting.save()
                    changed = True

                if changed:
                    messages.success(
                        request, _("EMG amplifier setting created successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "emg_electrode_setting_view", args=(emg_electrode_setting_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "creating": creating,
        "editing": False,
        "can_change": can_change,
        "emg_electrode_setting": emg_electrode_setting,
        "emg_amplifier_setting_form": emg_amplifier_setting_form,
        "emg_analog_filter_setting_form": emg_analog_filter_setting_form,
        "equipment_form": equipment_form,
        "manufacturer_list": list_of_manufacturers,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def emg_electrode_setting_amplifier_edit(
    request,
    emg_electrode_setting_id,
    template_name="experiment/emg_electrode_setting_amplifier.html",
):
    emg_electrode_setting = get_object_or_404(
        EMGElectrodeSetting, pk=emg_electrode_setting_id
    )

    check_can_change(
        request.user, emg_electrode_setting.emg_setting.experiment.research_project
    )

    emg_amplifier_setting = emg_electrode_setting.emg_amplifier_setting
    emg_amplifier_setting_form = EMGAmplifierSettingForm(
        request.POST or None, instance=emg_amplifier_setting
    )

    emg_amplifier_selected = emg_amplifier_setting.amplifier

    equipment_form = EquipmentForm(
        request.POST or None, instance=emg_amplifier_selected
    )

    list_of_manufacturers = Manufacturer.objects.filter(
        set_of_equipment__equipment_type="amplifier", set_of_equipment__tags__name="EMG"
    ).distinct()

    if hasattr(emg_amplifier_setting, "emg_analog_filter_setting"):
        emg_analog_filter_setting = (
            emg_electrode_setting.emg_amplifier_setting.emg_analog_filter_setting
        )
        emg_analog_filter_setting_form = EMGAnalogFilterSettingForm(
            request.POST or None, instance=emg_analog_filter_setting
        )
    else:
        emg_analog_filter_setting_form = EMGAnalogFilterSettingForm(
            request.POST or None
        )

    if request.method == "POST":
        if request.POST["action"] == "save":
            if emg_amplifier_setting_form.is_valid():
                changed = False

                if emg_amplifier_setting_form.has_changed():
                    emg_amplifier_setting_form.save()
                    changed = True

                if (
                    emg_amplifier_setting_form.has_changed()
                    or emg_analog_filter_setting_form.has_changed()
                ):
                    if hasattr(emg_amplifier_setting, "emg_analog_filter_setting"):
                        emg_analog_filter_setting_form.save()
                    else:
                        new_setting = emg_analog_filter_setting_form.save(commit=False)
                        new_setting.emg_electrode_setting = emg_amplifier_setting
                        new_setting.save()

                    changed = True

                if changed:
                    messages.success(
                        request, _("EMG Amplifier setting updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "emg_electrode_setting_amplifier", args=(emg_electrode_setting_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "creating": False,
        "editing": True,
        "can_change": True,
        "emg_electrode_setting": emg_electrode_setting,
        "emg_amplifier_setting_form": emg_amplifier_setting_form,
        "emg_analog_filter_setting_form": emg_analog_filter_setting_form,
        "equipment_form": equipment_form,
        "manufacturer_list": list_of_manufacturers,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_subject")
def tms_setting_create(
    request, experiment_id, template_name="experiment/tms_setting_register.html"
):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    check_can_change(request.user, experiment.research_project)

    tms_setting_form = TMSSettingForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if tms_setting_form.is_valid():
                tms_setting_added = tms_setting_form.save(commit=False)
                tms_setting_added.experiment_id = experiment_id
                tms_setting_added.save()

                messages.success(request, _("TMS setting included successfully."))

                redirect_url = reverse("tms_setting_view", args=(tms_setting_added.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "tms_setting_form": tms_setting_form,
        "creating": True,
        "editing": True,
        "experiment": experiment,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def tms_setting_view(
    request, tms_setting_id, template_name="experiment/tms_setting_register.html"
):
    tms_setting = get_object_or_404(TMSSetting, pk=tms_setting_id)
    tms_setting_form = TMSSettingForm(request.POST or None, instance=tms_setting)

    for field in tms_setting_form.fields:
        tms_setting_form.fields[field].widget.attrs["disabled"] = True

    can_change = get_can_change(request.user, tms_setting.experiment.research_project)

    if request.method == "POST":
        if can_change:
            if request.POST["action"] == "remove":
                experiment_id = tms_setting.experiment_id

                tms_setting.delete()

                messages.success(request, _("TMS setting was removed successfully."))

                redirect_url = reverse("experiment_view", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

            if request.POST["action"][:7] == "remove-":
                # If action starts with 'remove-' it means that a setting should be removed from the tms_setting.
                tms_setting_type = request.POST["action"][7:]

                setting_to_be_deleted = None

                if tms_setting_type == "tms_device":
                    setting_to_be_deleted = get_object_or_404(
                        TMSDeviceSetting, pk=tms_setting_id
                    )

                if tms_setting_type == "coil_model":
                    setting_to_be_deleted = get_object_or_404(
                        TMSDeviceSetting, pk=tms_setting_id
                    )

                if setting_to_be_deleted:
                    setting_to_be_deleted.delete()

                messages.success(request, _("Setting was removed successfully."))

                redirect_url = reverse("tms_setting_view", args=(tms_setting.id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": can_change,
        "tms_setting_form": tms_setting_form,
        "experiment": tms_setting.experiment,
        "tms_setting": tms_setting,
        "editing": False,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def tms_setting_update(
    request, tms_setting_id, template_name="experiment/tms_setting_register.html"
):
    tms_setting = get_object_or_404(TMSSetting, pk=tms_setting_id)

    check_can_change(request.user, tms_setting.experiment.research_project)

    tms_setting_form = TMSSettingForm(request.POST or None, instance=tms_setting)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if tms_setting_form.is_valid():
                if tms_setting_form.has_changed():
                    tms_setting_form.save()
                    messages.success(request, _("TMS setting updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("tms_setting_view", args=(tms_setting_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "tms_setting_form": tms_setting_form,
        "editing": True,
        "experiment": tms_setting.experiment,
        "tms_setting": tms_setting,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def tms_setting_coil_model(
    request, tms_setting_id, template_name="experiment/tms_setting_coil_model.html"
):
    tms_setting = get_object_or_404(TMSSetting, pk=tms_setting_id)

    can_change = get_can_change(request.user, tms_setting.experiment.research_project)

    creating = False

    context = {
        "creating": creating,
        "editing": False,
        "can_change": can_change,
        "tms_setting": tms_setting,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def tms_setting_tms_device(
    request, tms_setting_id, template_name="experiment/tms_setting_tms_device.html"
):
    tms_setting = get_object_or_404(TMSSetting, pk=tms_setting_id)

    can_change = get_can_change(request.user, tms_setting.experiment.research_project)

    creating = False

    list_of_manufacturers = Manufacturer.objects.filter(
        set_of_equipment__equipment_type="tms_device"
    ).distinct()

    if hasattr(tms_setting, "tms_device_setting"):
        tms_device_setting = TMSDeviceSetting.objects.get(tms_setting=tms_setting)

        tms_device_setting_form = TMSDeviceSettingForm(
            request.POST or None, instance=tms_device_setting
        )

        tms_device_selected = tms_device_setting.tms_device

        equipment_form = EquipmentForm(
            request.POST or None, instance=tms_device_selected
        )

        coil_model_selected = tms_device_setting.coil_model

        coil_model_form = CoilModelForm(
            request.POST or None, instance=coil_model_selected
        )

        for field in tms_device_setting_form.fields:
            tms_device_setting_form.fields[field].widget.attrs["disabled"] = True

    else:
        creating = True
        tms_device_setting_form = TMSDeviceSettingForm(request.POST or None)
        equipment_form = EquipmentForm(request.POST or None)
        coil_model_form = CoilModelForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if tms_device_setting_form.is_valid():
                if tms_device_setting_form.has_changed():
                    new_setting = tms_device_setting_form.save(commit=False)
                    new_setting.tms_setting = tms_setting
                    new_setting.save()

                    messages.success(
                        request, _("TMS device setting created successfully.")
                    )

                    redirect_url = reverse("tms_setting_view", args=(tms_setting_id,))
                    return HttpResponseRedirect(redirect_url)

    context = {
        "creating": creating,
        "editing": False,
        "can_change": can_change,
        "tms_setting": tms_setting,
        "tms_device_setting_form": tms_device_setting_form,
        "equipment_form": equipment_form,
        "coil_model_form": coil_model_form,
        "manufacturer_list": list_of_manufacturers,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def tms_setting_tms_device_edit(
    request, tms_setting_id, template_name="experiment/tms_setting_tms_device.html"
):
    tms_setting = get_object_or_404(TMSSetting, pk=tms_setting_id)

    check_can_change(request.user, tms_setting.experiment.research_project)

    tms_device_setting = tms_setting.tms_device_setting
    tms_device_setting_form = TMSDeviceSettingForm(
        request.POST or None, instance=tms_device_setting
    )

    tms_device_selected = tms_device_setting.tms_device

    equipment_form = EquipmentForm(request.POST or None, instance=tms_device_selected)

    coil_model_selected = tms_device_setting.coil_model

    coil_model_form = CoilModelForm(request.POST or None, instance=coil_model_selected)

    list_of_manufacturers = Manufacturer.objects.filter(
        set_of_equipment__equipment_type="tms_device"
    ).distinct()

    if request.method == "POST":
        if request.POST["action"] == "save":
            if tms_device_setting_form.is_valid():
                if tms_device_setting_form.has_changed():
                    tms_device_setting_form.save()

                    messages.success(
                        request, _("TMS device setting updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("tms_setting_view", args=(tms_setting_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "creating": False,
        "editing": True,
        "can_change": True,
        "tms_setting": tms_setting,
        "tms_device_setting_form": tms_device_setting_form,
        "equipment_form": equipment_form,
        "coil_model_form": coil_model_form,
        "manufacturer_list": list_of_manufacturers,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def tms_localization_system_list(
    request, template_name="experiment/tms_localization_system_list.html"
):
    return render(
        request,
        template_name,
        {"tms_localization_systems": TMSLocalizationSystem.objects.order_by("name")},
    )


@login_required
@permission_required("experiment.register_equipment")
def tms_localization_system_create(
    request, template_name="experiment/tms_localization_system_register.html"
):
    localization_system_form = TMSLocalizationSystemForm(request.POST or None)

    if request.method == "POST":
        if request.POST["action"] == "save":
            localization_system_form = TMSLocalizationSystemForm(
                request.POST, request.FILES
            )

            if localization_system_form.is_valid():
                localization_system_added = localization_system_form.save()

                messages.success(
                    request, _("TMS localization system created successfully.")
                )

                redirect_url = reverse(
                    "tms_localization_system_view", args=(localization_system_added.id,)
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))
        else:
            messages.warning(request, _("Action not available."))

    context = {
        "localization_system_form": localization_system_form,
        "creating": True,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def tms_localization_system_view(
    request,
    tms_localization_system_id,
    template_name="experiment/tms_localization_system_register.html",
):
    localization_system = get_object_or_404(
        TMSLocalizationSystem, pk=tms_localization_system_id
    )
    localization_system_form = TMSLocalizationSystemForm(
        request.POST or None, instance=localization_system
    )

    for field in localization_system_form.fields:
        localization_system_form.fields[field].widget.attrs["disabled"] = True

    if request.method == "POST":
        if request.POST["action"] == "remove":
            try:
                localization_system.delete()
                messages.success(
                    request, _("TMS localization system removed successfully.")
                )
                return redirect("tms_localization_system_list")
            except ProtectedError:
                messages.error(
                    request, _("Error trying to delete localization system.")
                )
                redirect_url = reverse(
                    "tms_localization_system_view", args=(tms_localization_system_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": True,
        "localization_system": localization_system,
        "localization_system_form": localization_system_form,
        "editing": False,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.register_equipment")
def tms_localization_system_update(
    request,
    tms_localization_system_id,
    template_name="experiment/tms_localization_system_register.html",
):
    localization_system = get_object_or_404(
        TMSLocalizationSystem, pk=tms_localization_system_id
    )
    localization_system_form = TMSLocalizationSystemForm(
        request.POST or None, instance=localization_system
    )

    if request.method == "POST":
        if request.POST["action"] == "save":
            localization_system_form = TMSLocalizationSystemForm(
                request.POST, request.FILES, instance=localization_system
            )

            if localization_system_form.is_valid():
                if localization_system_form.has_changed():
                    localization_system_form.save()
                    messages.success(
                        request, _("Localization system updated successfully.")
                    )
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse(
                    "tms_localization_system_view", args=(tms_localization_system_id,)
                )
                return HttpResponseRedirect(redirect_url)

    context = {
        "localization_system": localization_system,
        "localization_system_form": localization_system_form,
        "editing": True,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.add_subject")
def context_tree_create(
    request, experiment_id, template_name="experiment/context_tree_register.html"
):
    experiment = get_object_or_404(Experiment, pk=experiment_id)

    check_can_change(request.user, experiment.research_project)

    context_tree_form = ContextTreeForm(request.POST or None, request.FILES)

    if request.method == "POST":
        if request.POST["action"] == "save":
            if context_tree_form.is_valid():
                context_tree_added = context_tree_form.save(commit=False)
                context_tree_added.experiment_id = experiment_id
                context_tree_added.save()
                messages.success(request, _("Context tree included successfully."))

                redirect_url = reverse(
                    "context_tree_view", args=(context_tree_added.id,)
                )
                return HttpResponseRedirect(redirect_url)

            else:
                messages.warning(request, _("Information not saved."))
        else:
            messages.warning(request, _("Action not available."))

    context = {
        "context_tree_form": context_tree_form,
        "creating": True,
        "editing": True,
        "experiment": experiment,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def context_tree_view(
    request, context_tree_id, template_name="experiment/context_tree_register.html"
):
    context_tree = get_object_or_404(ContextTree, pk=context_tree_id)
    context_tree_form = ContextTreeForm(request.POST or None, instance=context_tree)

    for field in context_tree_form.fields:
        context_tree_form.fields[field].widget.attrs["disabled"] = True

    can_change = get_can_change(request.user, context_tree.experiment.research_project)

    if request.method == "POST":
        if can_change:
            if request.POST["action"] == "remove":
                experiment_id = context_tree.experiment_id

                context_tree.delete()

                messages.success(request, _("Context tree was removed successfully."))

                redirect_url = reverse("experiment_view", args=(experiment_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "can_change": can_change,
        "context_tree_form": context_tree_form,
        "experiment": context_tree.experiment,
        "context_tree": context_tree,
        "editing": False,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.change_experiment")
def context_tree_update(
    request, context_tree_id, template_name="experiment/context_tree_register.html"
):
    context_tree = get_object_or_404(ContextTree, pk=context_tree_id)

    check_can_change(request.user, context_tree.experiment.research_project)

    if request.method == "POST":
        context_tree_form = ContextTreeForm(
            request.POST, request.FILES, instance=context_tree
        )

        if request.POST["action"] == "save":
            if context_tree_form.is_valid():
                if context_tree_form.has_changed():
                    context_tree_form.save()
                    messages.success(request, _("Context tree updated successfully."))
                else:
                    messages.success(request, _("There is no changes to save."))

                redirect_url = reverse("context_tree_view", args=(context_tree_id,))
                return HttpResponseRedirect(redirect_url)
    else:
        context_tree_form = ContextTreeForm(request.POST or None, instance=context_tree)

    context = {
        "context_tree_form": context_tree_form,
        "editing": True,
        "experiment": context_tree.experiment,
        "context_tree": context_tree,
    }

    return render(request, template_name, context)


@login_required
@permission_required("experiment.view_researchproject")
def setup_menu(request, template_name="experiment/setup_menu.html"):
    basic_register_list = [
        {
            "item": _("Material"),
            "href": reverse("material_list", args=()),
            "quantity": Material.objects.all().count(),
        },
        {
            "item": _("Muscle"),
            "href": reverse("muscle_list", args=()),
            "quantity": Muscle.objects.all().count(),
        },
        {
            "item": _("EEG electrode localization system"),
            "href": reverse("eeg_electrode_localization_system_list", args=()),
            "quantity": EEGElectrodeLocalizationSystem.objects.all().count(),
        },
        {
            "item": _("EMG placement system"),
            "href": reverse("standardization_system_list", args=()),
            "quantity": StandardizationSystem.objects.all().count(),
            # 'warn_list': [{'item': _('Muscle'), 'dependence': Muscle.objects.all().count()}]
        },
        {
            "item": _("TMS localization system"),
            "href": reverse("tms_localization_system_list", args=()),
            "quantity": TMSLocalizationSystem.objects.all().count(),
        },
        {
            "item": _("Manufacturer"),
            "href": reverse("manufacturer_list", args=()),
            "quantity": Manufacturer.objects.all().count(),
        },
    ]

    device_register_list = [
        {
            "item": _("Electrode model"),
            "href": reverse("electrodemodel_list", args=()),
            "quantity": ElectrodeModel.objects.all().count(),
        },
        {
            "item": _("EEG electrode net / Cap"),
            "href": reverse("eegelectrodenet_list", args=()),
            "quantity": EEGElectrodeNet.objects.all().count(),
        },
        {
            "item": _("Solution"),
            "href": reverse("eegsolution_list", args=()),
            "quantity": EEGSolution.objects.all().count(),
        },
        {
            "item": _("Amplifier"),
            "href": reverse("amplifier_list", args=()),
            "quantity": Amplifier.objects.all().count(),
        },
        {
            "item": _("Filter type"),
            "href": reverse("filtertype_list", args=()),
            "quantity": FilterType.objects.all().count(),
        },
        {
            "item": _("Software"),
            "href": reverse("software_list", args=()),
            "quantity": Software.objects.all().count(),
        },
        {
            "item": _("A/D converter"),
            "href": reverse("ad_converter_list", args=()),
            "quantity": ADConverter.objects.all().count(),
        },
        {
            "item": _("Coil model"),
            "href": reverse("coil_list", args=()),
            "quantity": CoilModel.objects.all().count(),
        },
        {
            "item": _("TMS device"),
            "href": reverse("tmsdevice_list", args=()),
            "quantity": TMSDevice.objects.all().count(),
        },
    ]

    context = {
        "basic_register_list": basic_register_list,
        "device_register_list": device_register_list,
    }

    return render(request, template_name, context)
