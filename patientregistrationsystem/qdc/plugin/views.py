import json
import os
from operator import itemgetter
from os import path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from experiment.models import Component, Experiment, Group, Questionnaire
from experiment.models import QuestionnaireResponse as ExperimentResponse
from experiment.models import SubjectOfGroup
from experiment.views import get_block_tree
from export.forms import ExportForm
from export.input_export import build_complete_export_structure
from export.models import Export
from export.views import PATIENT_FIELDS, export_create, get_questionnaire_fields
from patient.models import QuestionnaireResponse as IndependentResponse
from plugin.models import RandomForests
from survey.abc_search_engine import Questionnaires
from survey.models import Survey


def participants_dict(survey):
    """
    Function to check who answered a questionnaire
    :param survey: Which questionnaire will be checked
    :return: Participants that answered the survey
    """
    participants = {}

    for response in IndependentResponse.objects.filter(survey=survey).filter(
        patient__removed=False
    ):
        participants[response.patient.id] = {
            "patient_id": response.patient.id,
            "patient_name": response.patient.name
            if response.patient.name
            else response.patient.code,
        }

    return participants


def update_patient_attributes(participants):
    """Add item to patient_selected POST list to suit to export method
    :param participants: list - participants
    :return: list - updated participants
    """
    participant_attributes = participants
    participants = [["code", "participant_code"]]  # First entry is that (see export)
    for participant in participant_attributes:
        participants.append(participant.split("*"))

    return participants


def has_questionnaire(components, survey):
    for component in components["list_of_component_configuration"]:
        if component["component"]["component_type"] == "block":
            if has_questionnaire(component["component"], survey):
                return True
        if component["component"]["component_type"] == Component.QUESTIONNAIRE:
            questionnaire = Questionnaire.objects.get(
                id=component["component"]["component"].id
            )
            if questionnaire.survey == survey:
                return True

    return False


def build_questionnaires_list(language_code, groups=None):
    """Build questionnaires list that will be used in export method to build
    export structure
    :param language_code: str - questionnaire language code
    :return: list - questionnaires
    """
    random_forests = get_object_or_404(RandomForests)
    surveys = [
        random_forests.admission_assessment.lime_survey_id,
        random_forests.surgical_evaluation.lime_survey_id,
        random_forests.followup_assessment.lime_survey_id,
    ]
    limesurvey_error, questionnaires = get_questionnaire_fields(surveys, language_code)
    if limesurvey_error:
        return limesurvey_error, questionnaires
    # Transform questionnaires (to get the format of build_complete_export
    # structure questionnaires list argument)
    for i, questionnaire in enumerate(questionnaires):
        questionnaire["index"] = str(i)
    questionnaires = [
        [
            dict0["index"],
            dict0["sid"],
            dict0["title"],
            [
                (dict1["header"], dict1["field"])
                for index1, dict1 in enumerate(dict0["output_list"])
            ],
        ]
        for index, dict0 in enumerate(questionnaires)
    ]

    if groups is not None:
        # TODO (NES-995): break at least this part in another method.
        #  Keep attention to the principle of (sic) one method -> do one thing.
        # If questionnaires list is for experiment questionnaires,
        # update questionnaires list
        for questionnaire in questionnaires:
            del questionnaire[0]

        new_questionnaires = []
        admission_survey = questionnaires[0]
        surgical_survey = questionnaires[1]
        followup_assessment = questionnaires[2]
        for group_id in groups:
            group_id = str(group_id)
            copy_admission = admission_survey.copy()
            copy_admission.insert(0, group_id)
            new_questionnaires.append(copy_admission)
            group = Group.objects.get(id=group_id)
            components = get_block_tree(group.experimental_protocol, language_code="en")
            if has_questionnaire(components, random_forests.surgical_evaluation):
                copy_surgical = surgical_survey.copy()
                copy_surgical.insert(0, group_id)
                new_questionnaires.append(copy_surgical)
            if has_questionnaire(components, random_forests.followup_assessment):
                copy_followup = followup_assessment.copy()
                copy_followup.insert(0, group_id)
                new_questionnaires.append(copy_followup)

        for i, questionnaire in enumerate(new_questionnaires):
            questionnaire.insert(0, str(i))

        return 0, new_questionnaires

    return 0, questionnaires


def build_zip_file(
    request,
    participants_plugin,
    participants_headers,
    questionnaires,
    per_experiment=True,
):
    """Define components to use as the component list argument of
    build_complete_export_structure export method
    :param request: Request object
    :param participants_plugin: list - list of participants selected to send to Plugin
    :param participants_headers: list
    :param questionnaires: list
    :param per_experiment: boolean - True if per_experiment, else False (per_participant)
    :return: str = zip file path if success, else Questoinaires.ERROR_CODE
    """
    components = {
        "per_additional_data": False,
        "per_eeg_nwb_data": False,
        "per_eeg_raw_data": False,
        "per_emg_data": False,
        "per_generic_data": False,
        "per_goalkeeper_game_data": False,
        "per_stimulus_data": False,
        "per_tms_data": False,
    }
    export = Export.objects.create(user=request.user)
    # TODO (NES-983): creation of export_dir is made calling export_create bellow
    export_dir = path.join(
        settings.MEDIA_ROOT, "export", str(request.user.id), str(export.id)
    )
    os.makedirs(export_dir)
    input_filename = path.join(export_dir, "json_export.json")
    build_complete_export_structure(
        True,
        True,
        per_experiment,
        participants_headers,
        [],
        [] if per_experiment else questionnaires,
        questionnaires if per_experiment else [],
        ["short"],
        "code",
        input_filename,
        components,
        request.LANGUAGE_CODE,
        "csv",
    )
    result = export_create(
        request,
        export.id,
        input_filename,
        participants_plugin=participants_plugin,
        per_experiment_plugin=per_experiment,
    )
    if result == Questionnaires.ERROR_CODE:
        return result, None

    return 0, result


def select_participants(request, experiment_id):
    participants = []
    random_forests = RandomForests.objects.get()
    admission = Survey.objects.get(pk=random_forests.admission_assessment.pk)
    experiment = Experiment.objects.get(pk=experiment_id)
    for component in experiment.components.all():
        if component.component_type == Component.QUESTIONNAIRE:
            questionnaire = Questionnaire.objects.get(pk=component.id)
            if questionnaire.survey == admission:
                questionnaire_responses = ExperimentResponse.objects.filter(
                    data_configuration_tree__component_configuration__component=questionnaire
                )
                for questionnaire_response in questionnaire_responses:
                    subject_of_group = questionnaire_response.subject_of_group
                    if subject_of_group:
                        participants.append(
                            {
                                "subject_of_group_id": subject_of_group.id,
                                "participant_id": subject_of_group.subject.patient.id,
                                "participant_name": subject_of_group.subject.patient.name,
                                "group_id": subject_of_group.group.id,
                                "group_name": subject_of_group.group.title,
                            }
                        )
    if participants:
        json_participants = json.dumps(participants)
    else:
        json_participants = json.dumps({})

    return HttpResponse(json_participants, content_type="application/json")


@login_required
def send_to_plugin(request, template_name="plugin/send_to_plugin.html"):
    if request.method == "POST":
        if request.POST.get("per_experiment"):
            # TODO (NES-995): change name for subjects_of_groups_selected
            subjects_of_groups = request.POST.getlist("patients_selected[]")
            group_ids = (
                Group.objects.filter(subjectofgroup__in=subjects_of_groups)
                .distinct()
                .values_list("id", flat=True)
            )
            request.session["group_selected_list"] = [
                str(group_id) for group_id in list(group_ids)
            ]
            request.session["license"] = 0
            # Need to delete before call export_create method
            if "filtered_participant_data" in request.session:
                del request.session["filtered_participant_data"]
            participants_headers = update_patient_attributes(
                request.POST.getlist("patient_selected")
            )
            # TODO (NES-995): build always in English, but possibly not hard coded
            limesurvey_error, questionnaires = build_questionnaires_list(
                "en", group_ids
            )
            if limesurvey_error:
                messages.error(
                    request,
                    _(
                        "Error: some thing went wrong consuming LimeSurvey API. Please try again. "
                        "If problem persists please contact System Administrator."
                    ),
                )
                return redirect(reverse("send-to-plugin"))
            limesurvey_error, zip_file = build_zip_file(
                request, subjects_of_groups, participants_headers, questionnaires
            )
            if limesurvey_error:
                messages.error(
                    request,
                    _(
                        "Error: some thing went wrong consuming LimeSurvey API. Please try again. "
                        "If problem persists please contact System Administrator."
                    ),
                )
                return redirect(reverse("send-to-plugin"))
            if zip_file:
                export = Export.objects.last()
                plugin_url = RandomForests.objects.first().plugin_url
                plugin_url += (
                    "?user_id=" + str(request.user.id) + "&export_id=" + str(export.id)
                )
                # Puts in session to open plugin and load posted values
                request.session["plugin_url"] = plugin_url
                request.session["experiment_selected_id"] = int(
                    request.POST.get("experiment_selected", None)
                )
                request.session["participants_from"] = list(
                    map(int, request.POST.getlist("from[]", None))
                )
                request.session["participants_to"] = list(
                    map(int, request.POST.getlist("patients_selected[]"))
                )
                return redirect(reverse("send-to-plugin"))
            else:
                messages.error(
                    request, _("Could not open zip file to send to Forest Plugin")
                )
                return redirect(reverse("send-to-plugin"))
        else:
            if "group_selected_list" in request.session:
                del request.session["group_selected_list"]
            if not request.POST.getlist("patients_selected[]"):
                messages.warning(request, _("Please select at least one patient"))
                return redirect(reverse("send-to-plugin"))
            # Export experiment (from export app) requires at least one patient
            # attribute selected (patient_selected is the list of attributes).
            # This may be changed to a better key name
            if not request.POST.getlist("patient_selected"):
                messages.warning(
                    request, _("Please select at least Gender participant attribute")
                )
                return redirect(reverse("send-to-plugin"))
            if "gender__name*gender" not in request.POST.getlist("patient_selected"):
                messages.warning(
                    request,
                    _("The Floresta Plugin needs to send at least Gender attribute"),
                )
                return redirect(reverse("send-to-plugin"))
            participants = request.POST.getlist("patients_selected[]")
            participants_headers = update_patient_attributes(
                request.POST.getlist("patient_selected")
            )
            limesurvey_error, questionnaires = build_questionnaires_list(
                request.LANGUAGE_CODE
            )
            if limesurvey_error:
                messages.error(
                    request,
                    _(
                        "Error: some thing went wrong consuming LimeSurvey API. Please try again. "
                        "If problem persists please contact System Administrator."
                    ),
                )
                return redirect(reverse("send-to-plugin"))
            limesurvey_error, zip_file = build_zip_file(
                request, participants, participants_headers, questionnaires, False
            )
            if limesurvey_error:
                messages.error(
                    request,
                    _(
                        "Error: some thing went wrong consuming LimeSurvey API. Please try again. "
                        "If problem persists please contact System Administrator."
                    ),
                )
                return redirect(reverse("send-to-plugin"))
            if zip_file:
                export = Export.objects.last()
                plugin_url = RandomForests.objects.first().plugin_url
                plugin_url += (
                    "?user_id=" + str(request.user.id) + "&export_id=" + str(export.id)
                )
                request.session["plugin_url"] = plugin_url
                return redirect(reverse("send-to-plugin"))
            else:
                messages.error(
                    request, _("Could not open zip file to send to Forest Plugin")
                )
                return redirect(reverse("send-to-plugin"))

    try:
        random_forests = RandomForests.objects.get()
    except RandomForests.DoesNotExist:
        random_forests = None

    admission_participants = {}
    surgical_participants = {}
    followup_participants = {}
    admission_title = None
    surgical_title = None
    followup_title = None

    # Patients that answered the admission assessment,
    # surgical evaluation and followup assessment questionnaires
    if (
        random_forests
        and random_forests.admission_assessment
        and random_forests.surgical_evaluation
        and random_forests.followup_assessment
    ):
        admission = Survey.objects.get(pk=random_forests.admission_assessment.pk)
        admission_participants = participants_dict(admission)
        surgical = Survey.objects.get(pk=random_forests.surgical_evaluation.pk)
        surgical_participants = participants_dict(surgical)
        followup = Survey.objects.get(pk=random_forests.followup_assessment.pk)
        followup_participants = participants_dict(followup)
        if admission:
            admission_title = (
                admission.en_title
                if request.LANGUAGE_CODE == "en"
                else admission.pt_title
            )
        if surgical:
            surgical_title = (
                surgical.en_title
                if request.LANGUAGE_CODE == "en"
                else surgical.pt_title
            )
        if followup:
            followup_title = (
                followup.en_title
                if request.LANGUAGE_CODE == "en"
                else followup.pt_title
            )

    # The intersection of admission assessment, surgical evaluation and
    # followup questionnaires
    intersection_dict = {}
    for patient_id in admission_participants:
        if (
            patient_id in surgical_participants
            and patient_id in followup_participants
            and admission_participants[patient_id] == surgical_participants[patient_id]
            and admission_participants[patient_id] == followup_participants[patient_id]
        ):
            intersection_dict[patient_id] = admission_participants[patient_id]

    # Transform the intersection dictionary into a list, so that we can sort
    # it by patient name
    participants_headers = []

    for key, dictionary in list(intersection_dict.items()):
        dictionary["patient_id"] = key
        participants_headers.append(dictionary)

    participants_headers = sorted(participants_headers, key=itemgetter("patient_name"))

    # Exclude PATIENT_FIELDS item correspondent to patient code
    # Did that as of NES-987 issue refactorings (this was a major refactoring)
    patient_fields = PATIENT_FIELDS.copy()
    key = next(item for item in PATIENT_FIELDS if item["field"] == "code")
    del patient_fields[patient_fields.index(key)]

    context = {
        "participants": participants_headers,
        "patient_fields": patient_fields,
        "admission_title": admission_title,
        "surgical_title": surgical_title,
        "followup_title": followup_title,
    }

    # START - Here goes the selections for Sending by Experiment
    if (
        random_forests
        and random_forests.admission_assessment
        and random_forests.surgical_evaluation
        and random_forests.followup_assessment
    ):
        admission = Survey.objects.get(pk=random_forests.admission_assessment.pk)
        surgical = Survey.objects.get(pk=random_forests.surgical_evaluation.pk)
        followup = Survey.objects.get(pk=random_forests.followup_assessment.pk)
        questionnaires = Questionnaire.objects.filter(
            survey__in=[admission, surgical, followup]
        )
        questionnaire_responses = ExperimentResponse.objects.filter(
            data_configuration_tree__component_configuration__component__in=questionnaires
        )
        experiments = Experiment.objects.filter(
            groups__subjectofgroup__questionnaireresponse__in=questionnaire_responses
        ).distinct()

        context["experiments"] = experiments
        context["experiment_selected_id"] = request.session.get(
            "experiment_selected_id", None
        )
        if "experiment_selected_id" in request.session:
            del request.session["experiment_selected_id"]

        context["participants_from"] = dict(
            (el, "") for el in request.session.get("participants_from", [])
        )
        for key in context["participants_from"]:
            subject_of_group = SubjectOfGroup.objects.get(pk=key)
            patient = subject_of_group.subject.patient
            context["participants_from"][key] = (
                patient.name + " - " + subject_of_group.group.title
            )
        if "participants_from" in request.session:
            del request.session["participants_from"]

        context["participants_to"] = dict(
            (el, "") for el in request.session.get("participants_to", [])
        )
        for key in context["participants_to"]:
            subject_of_group = SubjectOfGroup.objects.get(pk=key)
            patient = subject_of_group.subject.patient
            context["participants_to"][key] = (
                patient.name + " - " + subject_of_group.group.title
            )
        if "participants_to" in request.session:
            del request.session["participants_to"]

        export_form = ExportForm(
            request.POST or None,
            initial={
                "title": "title",
                "responses": ["short"],
                "headings": "code",
                "filesformat": "csv",
            },
        )

        context["export_form"] = export_form
    # END - Here goes the selections for Sending by Experiment

    plugin_url = request.session.get("plugin_url", None)
    if plugin_url is not None:
        context["plugin_url"] = plugin_url
        messages.success(
            request, _("Data from questionnaires was sent to Forest Plugin")
        )
        del request.session["plugin_url"]

    return render(request, template_name, context)
