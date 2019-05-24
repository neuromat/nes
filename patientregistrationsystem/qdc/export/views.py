# -*- coding: utf-8 -*-
import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as ug_, ugettext_lazy as _
from django.db.models import Q

from datetime import datetime
from dateutil.relativedelta import relativedelta

from os import path
from zipfile import ZipFile
from shutil import rmtree

from survey.survey_utils import QuestionnaireUtils
from .forms import ExportForm, ParticipantsSelectionForm, AgeIntervalForm
from .models import Export

from export.export import ExportExecution, create_directory
from export.input_export import build_complete_export_structure
from export.export_utils import create_list_of_trees, can_export_nwb

from patient.models import QuestionnaireResponse, Patient
from patient.views import check_limesurvey_access

from survey.models import Survey
from survey.abc_search_engine import Questionnaires
from survey.views import get_questionnaire_language

from experiment.models import ResearchProject, Experiment, Group, \
    SubjectOfGroup, Component, ComponentConfiguration, \
    Block, Instruction, Questionnaire, Stimulus, DataConfigurationTree, \
    QuestionnaireResponse as ExperimentQuestionnaireResponse, \
    ClassificationOfDiseases, EEGData, AdditionalData, EMGData, TMSData, \
    DigitalGamePhaseData, GenericDataCollectionData

JSON_FILENAME = "json_export.json"
JSON_EXPERIMENT_FILENAME = "json_experiment_export.json"
EXPORT_DIRECTORY = "export"
EXPORT_FILENAME = "export.zip"
EXPORT_EXPERIMENT_FILENAME = "export_experiment.zip"
MAX_STRING_LENGTH = 17

patient_fields = [
    {"field": 'age', "header": 'age', "description": _("Age")},
    {"field": 'gender__name', "header": 'gender', "description": _("Gender")},
    {"field": 'date_birth', "header": 'date_birth', "description": _("Date of birth")},
    {"field": 'marital_status__name', "header": 'marital_status',
     "description": _("Marital status")},
    {"field": 'origin', "header": 'origin', "description": _("Origin")},
    {"field": 'city', "header": 'city', "description": _("City")},
    {"field": 'state', "header": 'state', "description": _("State")},
    {"field": 'country', "header": 'country', "description": _("Country")},
    {"field": 'socialdemographicdata__natural_of', "header": 'natural_of', "description": _("Natural of")},
    {"field": 'socialdemographicdata__schooling__name', "header": 'schooling', "description": _("Schooling")},
    {"field": 'socialdemographicdata__patient_schooling__name', "header": 'patient_schooling',
     "description": _("Schooling of the patient")},
    {"field": 'socialdemographicdata__profession', "header": 'profession', "description": _("Profession")},
    {"field": 'socialdemographicdata__social_class', "header": 'social_class',
     "description": _("Calculated social class")},
    {"field": 'socialdemographicdata__occupation', "header": 'occupation', "description": _("Occupation")},
    {"field": 'socialdemographicdata__benefit_government', "header": 'benefit_government',
     "description": _("Do you receive some benefit from the municipal level, state or federal government?")},
    {"field": 'socialdemographicdata__religion__name', "header": 'religion', "description": _("Religion")},
    {"field": 'socialdemographicdata__flesh_tone__name', "header": 'flesh_tone', "description": _("Flesh tone")},
    {"field": 'socialdemographicdata__citizenship', "header": 'citizenship', "description": _("Citizenship")},
    {"field": 'socialdemographicdata__payment__name', "header": 'payment', "description": _("What form of payment of "
                                                                                            "the treatment performed")},
    {"field": 'socialhistorydata__smoker', "header": 'smoker', "description": _("Smoker")},
    {"field": 'socialhistorydata__amount_cigarettes__name', "header": 'amount_cigarettes', "description": _(
        "Cigarretes/Day")},
    {"field": 'socialhistorydata__ex_smoker', "header": 'former_smoker', "description": _("Former smoker")},
    {"field": 'socialhistorydata__alcoholic', "header": 'alcoholic', "description": _("Alcoholic")},
    {"field": 'socialhistorydata__alcohol_frequency__name', "header": 'alcohol_frequency', "description": _(
        "Frequency")},
    {"field": 'socialhistorydata__alcohol_period__name', "header": 'alcohol_period', "description": _("Period")},
    {"field": 'socialhistorydata__drugs', "header": 'drugs', "description": _("Drugs")},
]

diagnosis_fields = [
    {"field": "medicalrecorddata__diagnosis__date", "header": 'diagnosis_date', "description": _("Date")},
    {"field": "medicalrecorddata__diagnosis__description", "header": 'diagnosis_description',
     "description": _("Observation")},
    {"field": "medicalrecorddata__diagnosis__classification_of_diseases__code",
     "header": 'classification_of_diseases_code', "description": _("Disease code (ICD)")},
    {"field": "medicalrecorddata__diagnosis__classification_of_diseases__description",
     "header": 'classification_of_diseases_description', "description": _("Disease Description")},
    {"field": "medicalrecorddata__diagnosis__classification_of_diseases__abbreviated_description",
     "header": 'classification_of_diseases_description', "description": _("Disease Abbreviated Description")},
]

PATIENT_FIELDS_INCLUSION = [
    ["code", {"code": "participant_code", "full": _("Participant code"),
              "abbreviated": _("Participant code")}],
]

diagnosis_fields_inclusion = [
    ["code", {"code": "participant_code", "full": _("Participant code"),
              "abbreviated": _("Participant code")}],
]

questionnaire_evaluation_fields_excluded = [
    "subjectid",
    "responsibleid",
    "id",
    "submitdate",
    "lastpage",
    "startlanguage",
    "token",
    "startdate",
    "datestamp",
    "ipaddr",
    "refurl"
]

header_explanation_fields = ['questionnaire_id',
                             'questionnaire_title',
                             'question_code',
                             'question_description',
                             'subquestion_code',
                             'subquestion_description',
                             'option_code',
                             'option_description',
                             'option_value',
                             'column_title']


def update_export_instance(input_file, output_export, export_instance):
    export_instance.input_file = input_file
    export_instance.output_export = output_export
    export_instance.save()


def find_description(field_to_find, fields_inclusion):
    for field_dict in fields_inclusion:
        if field_dict["field"] == field_to_find:
            return ug_(field_dict["description"])
    return ""


def abbreviated_data(data_to_abbreviate, heading_type):

    if heading_type == 'abbreviated' and len(data_to_abbreviate) > \
            MAX_STRING_LENGTH:
        return data_to_abbreviate[:MAX_STRING_LENGTH] + '..'
    else:
        return data_to_abbreviate


def update_participants_list(participants_list, heading_type):

    if participants_list:

        # update header, if necessary
        if heading_type != "code":
            for participant in participants_list:
                header_translated = find_description(participant[0], patient_fields)
                participant[1] = abbreviated_data(header_translated, heading_type)

        # include participant_code
        for field, header in PATIENT_FIELDS_INCLUSION:
            header_translated = ug_(header[heading_type])
            participants_list.insert(
                0, [field, abbreviated_data(header_translated, heading_type)]
            )


def update_diagnosis_list(diagnosis_list, heading_type):

    if diagnosis_list:
        # update header, if necessary
        if heading_type != "code":
            for diagnosis in diagnosis_list:
                header_translated = find_description(diagnosis[0], diagnosis_fields)
                diagnosis[1] = abbreviated_data(header_translated, heading_type)

        # include participant_code
        for field, header in diagnosis_fields_inclusion:
            header_translated = ug_(header[heading_type])
            diagnosis_list.insert(0, [field, abbreviated_data(header_translated, heading_type)])


def export_create(request, export_id, input_filename, template_name="export/export_data.html"):
    try:
        export_instance = Export.objects.get(user=request.user, id=export_id)

        export = ExportExecution(export_instance.user.id, export_instance.id)

        language_code = request.LANGUAGE_CODE

        # all participants filtered
        if 'filtered_participant_data' in request.session:
            participants_filtered_list = request.session['filtered_participant_data']
        else:
            participants_filtered_list = Patient.objects.filter(removed=False)
        export.set_participants_filtered_data(participants_filtered_list)

        # set path of the directory base
        base_directory, path_to_create = path.split(export.get_directory_base())
        # create directory base
        error_msg, base_directory_name = create_directory(base_directory, path_to_create)
        if error_msg != '':
            messages.error(request, error_msg)
            return render(request, template_name)

        # read initial json file
        input_export_file = path.join(
            "export",
            path.join(
                str(request.user.id),
                path.join(str(export_instance.id), str(input_filename))
            )
        )

        # prepare data to be processed
        input_data = export.read_configuration_data(input_filename)

        if not export.is_input_data_consistent() or not input_data:
            messages.error(request, _("Inconsistent data read from json file"))
            return render(request, template_name)

        # create directory base for export: /NES_EXPORT
        error_msg = export.create_export_directory()

        if error_msg != '':
            messages.error(request, error_msg)
            return render(request, template_name)
        # export participants data
        if export.get_input_data('participants')['output_list']:
            participants_input_data = export.get_input_data("participants")['output_list']
            participants_list = export.get_participants_filtered_data()
            # If it's Per experiment exporting, add subject of group to
            # participants list of tuples for further processing participant
            # age based on first data collection
            if 'group_selected_list' in request.session:
                participants_list = export.add_subject_of_group(
                    # required convertion from ValuesListQuerySet to list
                    list(participants_list),
                    request.session['group_selected_list']
                )
            export_rows_participants = export.process_participant_data(
                participants_input_data, participants_list, language_code
            )
            export.get_input_data('participants')['data_list'] = export_rows_participants
            # create file participants.csv and diagnosis.csv
            error_msg = export.build_participant_export_data('group_selected_list' in request.session)
            if error_msg != "":
                messages.error(request, error_msg)
                return render(request, template_name)

        if 'group_selected_list' in request.session:
            # export method: filter by experiments
            export.include_group_data(request.session['group_selected_list'])
            # if fields from questionnaires were selected
            if export.get_input_data("questionnaire_list"):
                export.get_questionnaires_responses()

            error_msg = export.create_group_data_directory()
            if error_msg != '':
                messages.error(request, error_msg)
                return render(request, template_name)

            # create files of experimental protocol description file
            error_msg = export.process_experiment_data(language_code)

            if error_msg != "":
                messages.error(request, error_msg)
                return render(request, template_name)

            # if questionnaire from entrance evaluation was selected
            if export.get_input_data('questionnaires'):
                # Process per questionnaire data - entrance evaluation
                # questionnaires (Particpant data directory)
                if export.get_input_data("export_per_questionnaire"):
                    error_msg = export.process_per_entrance_questionnaire()
                    if error_msg != "":
                        messages.error(request, error_msg)
                        return render(request, template_name)
                if export.get_input_data("export_per_participant"):
                    error_msg = export.process_per_participant_per_entrance_questionnaire()
                    if error_msg != "":
                        messages.error(request, error_msg)
                        return render(request, template_name)

            # If questionnaire from experiments was selected (Experiment
            # data directory)
            if export.get_input_data('questionnaires_from_experiments'):
                if export.get_input_data("export_per_questionnaire"):
                    error_msg = export.process_per_experiment_questionnaire()
                    if error_msg != "":
                        messages.error(request, error_msg)
                        return render(request, template_name)
            # build export data by each component
            error_msg = export.process_per_participant_per_experiment()
            if error_msg != "":
                messages.error(request, error_msg)
                return render(request, template_name)

        else:
            # Export method: filter by entrance questionnaire
            if export.get_input_data('questionnaires'):
                # Process per questionnaire data - entrance evaluation questionnaires
                error_msg = export.process_per_questionnaire()
                if error_msg != "":
                    messages.error(request, error_msg)
                    return render(request, template_name)

                error_msg = export.process_per_participant()
                if error_msg != "":
                    messages.error(request, error_msg)
                    return render(request, template_name)

        # create zip file and include files
        export_complete_filename = ""
        if export.files_to_zip_list:
            # export.zip file
            export_filename = export.get_input_data('export_filename')
            export_complete_filename = path.join(
                base_directory_name, export_filename
            )
            # print(export.files_to_zip_list)  # DEBUG

            with ZipFile(export_complete_filename, 'w') as zip_file:
                for filename, directory in export.files_to_zip_list:
                    fdir, fname = path.split(filename)
                    zip_file.write(filename.encode('utf-8'), path.join(directory, fname))

            output_export_file = path.join(
                "export",
                path.join(str(export_instance.user.id), str(export_instance.id), str(export_filename)))

            update_export_instance(
                input_export_file, output_export_file, export_instance
            )

        # delete temporary directory: from base_directory and below
        base_export_directory = export.get_export_directory()
        rmtree(base_export_directory, ignore_errors=True)

        return export_complete_filename

    except OSError as e:
        print(e)
        error_msg = e
        messages.error(request, error_msg)
        return render(request, template_name)


@login_required
def export_view(request, template_name="export/export_data.html"):
    export_form = ExportForm(
        request.POST or None,
        initial={'title': 'title', 'responses': ['short'], 'headings': 'code', 'filesformat': 'csv'}
    )

    selected_ev_quest = []
    selected_participant = []
    selected_diagnosis = []
    selected_ev_quest_experiments = []
    questionnaires_fields_list = []
    questionnaires_experiment_fields_list = []
    language_code = request.LANGUAGE_CODE

    component_list = []

    if request.method == "POST":
        questionnaires_selected_list = request.POST.getlist('to[]')
        experiment_questionnaires_selected_list = []

        questionnaires_list = []
        experiment_questionnaires_list = []

        # for entrance questionnaires
        previous_questionnaire_id = -1
        output_list = []
        for questionnaire in questionnaires_selected_list:
            index, sid, title, field, header = questionnaire.split("*")

            if index != previous_questionnaire_id:
                if previous_questionnaire_id != 0:
                    output_list = []

                questionnaires_list.append(
                    [index, int(sid), title, output_list]
                )

                previous_questionnaire_id = index

            output_list.append((field, header))

        # for experiment questionnaires
        if request.POST.getlist('to_experiment[]'):
            experiment_questionnaires_selected_list = \
                request.POST.getlist('to_experiment[]')
            previous_questionnaire_id = -1
            output_list = []
            for questionnaire in experiment_questionnaires_selected_list:
                index, group_id, sid, title, field, header = questionnaire.split("*")

                if index != previous_questionnaire_id:
                    if previous_questionnaire_id != 0:
                        output_list = []

                    experiment_questionnaires_list.append(
                        [index, group_id, int(sid), title, output_list]
                    )

                    previous_questionnaire_id = index

                output_list.append((field, header))

        participant_selected_list = request.POST.getlist('patient_selected')

        participants_list = []

        for participant in participant_selected_list:
            participants_list.append(participant.split("*"))

        diagnosis_selected_list = request.POST.getlist('diagnosis_selected')

        diagnosis_list = []

        for diagnosis in diagnosis_selected_list:
            diagnosis_list.append(diagnosis.split("*"))

        selected_data_available = \
            (
                    len(questionnaires_selected_list) or
                    len(experiment_questionnaires_selected_list) or
                    len(participant_selected_list) or
                    len(diagnosis_selected_list)
            )

        if selected_data_available:
            component_list = {}
            if export_form.is_valid():
                per_experiment = 'group_selected_list' in request.session
                per_participant = True
                per_questionnaire = False
                responses_type = None
                # TODO:
                #  When there'are not questionnaires avulsely answered
                #  by participants, export_form.cleaned_data['headings'] = ''.
                #  In fact there aren't questionnaires stuff at all. So this
                #  form attribute doesn't make sense. By now we make 'code'
                #  as value of that attribute for doesn't breaking the code.

                filesformat_type = export_form.cleaned_data['filesformat'] or 'csv'
                heading_type = export_form.cleaned_data['headings'] or 'code'

                update_participants_list(participants_list, heading_type)
                update_diagnosis_list(diagnosis_list, heading_type)

                component_list['per_eeg_raw_data'] = export_form.cleaned_data['per_eeg_raw_data']
                component_list['per_eeg_nwb_data'] = export_form.cleaned_data['per_eeg_nwb_data']
                component_list['per_emg_data'] = export_form.cleaned_data['per_emg_data']
                component_list['per_tms_data'] = export_form.cleaned_data['per_tms_data']
                component_list['per_additional_data'] = export_form.cleaned_data['per_additional_data']
                component_list['per_goalkeeper_game_data'] = export_form.cleaned_data['per_goalkeeper_game_data']
                component_list['per_stimulus_data'] = export_form.cleaned_data['per_stimulus_data']
                component_list['per_generic_data'] = export_form.cleaned_data['per_generic_data']

                if questionnaires_selected_list or experiment_questionnaires_list:
                    per_participant = export_form.cleaned_data['per_participant']
                    per_questionnaire = export_form.cleaned_data['per_questionnaire']
                    responses_type = export_form.cleaned_data['responses']

                    if questionnaires_selected_list:
                        questionnaires_list = update_questionnaire_list(
                            questionnaires_list, heading_type, False, request.LANGUAGE_CODE)

                    if experiment_questionnaires_list:
                        per_experiment = True
                        experiment_questionnaires_list = update_questionnaire_list(
                                experiment_questionnaires_list, heading_type, True, request.LANGUAGE_CODE)

                export_instance = Export.objects.create(user=request.user)

                input_export_file = path.join(
                    EXPORT_DIRECTORY, str(request.user.id), str(export_instance.id), str(JSON_FILENAME))

                # copy data to media/export/<user_id>/<export_id>/
                input_filename = path.join(settings.MEDIA_ROOT, input_export_file)

                create_directory(settings.MEDIA_ROOT, path.split(input_export_file)[0])

                build_complete_export_structure(
                    per_participant, per_questionnaire, per_experiment, participants_list,
                    diagnosis_list, questionnaires_list, experiment_questionnaires_list, responses_type,
                    heading_type, input_filename, component_list, language_code, filesformat_type)

                complete_filename = export_create(request, export_instance.id, input_filename)

                if complete_filename:
                    messages.success(request, _("Export was finished correctly"))
                    zip_file = open(complete_filename, 'rb')
                    response = HttpResponse(zip_file, content_type='application/zip')
                    response['Content-Disposition'] = 'attachment; filename="export.zip"'
                    response['Content-Length'] = path.getsize(complete_filename)
                    return response
                else:
                    messages.error(request, _("Export data was not generated."))

            else:
                for questionnaire in questionnaires_list:
                    for field in questionnaire[2]:  # get output_list
                        selected_ev_quest.append((questionnaire[0], field[0]))

                for questionnaire in experiment_questionnaires_list:
                    for field in questionnaire[2]:
                        selected_ev_quest_experiments.append(questionnaire[0], field[0])

                for participant in participants_list:
                    selected_participant.append(participant[0])

                for diagnosis in diagnosis_list:
                    selected_diagnosis.append(diagnosis[0])
        else:
            messages.error(
                request,
                _("No data was select. Export data was not generated.")
            )

    surveys = Questionnaires()
    questionnaires_experiment_list_final = []
    # experiments export
    if 'group_selected_list' in request.session:
        group_list = request.session['group_selected_list']

        component_list = []
        for group_id in group_list:
            group = get_object_or_404(Group, pk=group_id)
            if group.experimental_protocol is not None:
                component_list = get_component_with_data_and_metadata(
                    group, component_list
                )
                questionnaire_response_list = \
                    ExperimentQuestionnaireResponse.objects.filter(
                        subject_of_group__group=group
                    )
                questionnaire_in_list = []
                for path_experiment in \
                        create_list_of_trees(group.experimental_protocol,
                                             "questionnaire"):
                    questionnaire_configuration = get_object_or_404(
                        ComponentConfiguration, pk=path_experiment[-1][0]
                    )
                    questionnaire = Questionnaire.objects.get(
                        id=questionnaire_configuration.component.id
                    )
                    questionnaire_id = questionnaire.survey.lime_survey_id

                    for questionnaire_response in questionnaire_response_list:
                        completed = surveys.get_participant_properties(
                            questionnaire_id,
                            questionnaire_response.token_id,
                            "completed"
                        )
                        if completed is not None and completed != "N" \
                                and completed != "":
                            questionnaire_dic = {
                                'questionnaire': questionnaire,
                                'token': str(questionnaire_response.token_id),
                                'group_id': group_id,
                                'group_title': group.title
                            }
                            if questionnaire_id not in questionnaire_in_list:
                                questionnaire_in_list.append(questionnaire_id)
                                questionnaires_experiment_list_final.append(
                                    questionnaire_dic
                                )

        if questionnaires_experiment_list_final:
            questionnaires_experiment_fields_list = \
                get_questionnaire_experiment_fields(
                    questionnaires_experiment_list_final, language_code
                )

    if surveys:
        # If called from expired session return to fist export options.
        # This is to workaround in a code break arising from trying to
        # export after an expired session
        if 'filtered_participant_data' not in request.session:
            return HttpResponseRedirect(reverse('export_menu'))

        # Obter a lista dos participantes filtrados que têm questionários de
        # entrada preenchidos.
        patient_questionnaire_response_list = \
            QuestionnaireResponse.objects.filter(
                patient_id__in=request.session['filtered_participant_data']
            )

        surveys_with_ev_list = []
        surveys_id_list = []
        # verificar se os questionnarios estão completos
        for patient_questionnaire_response in patient_questionnaire_response_list:

            lime_survey_id = patient_questionnaire_response.survey.lime_survey_id
            if lime_survey_id not in surveys_id_list:
                completed = surveys.get_participant_properties(lime_survey_id,
                                                               patient_questionnaire_response.token_id, "completed")
                # if completed is a data
                if completed is not None and completed != "N" and completed != "":
                    surveys_id_list.append(lime_survey_id)
                    surveys_with_ev_list.append(get_object_or_404(Survey, pk=patient_questionnaire_response.survey_id))

        # load the questionnaires_list_final with the lime_survey_id
        index = 0
        if surveys_with_ev_list:
            # check if limesurvey is available
            limesurvey_available = check_limesurvey_access(request, surveys)

            questionnaires_list = []
            # if available get all the questionnaires
            if limesurvey_available:
                questionnaires_list = surveys.find_all_active_questionnaires()

            surveys.release_session_key()

            questionnaires_list_final = []
            for survey in surveys_with_ev_list:
                for questionnaire in questionnaires_list:
                    if survey.lime_survey_id == questionnaire['sid']:
                        questionnaires_list_final.append(questionnaire)
                        break

            # Get the questionnaire fields from the
            # questionnaires_list_final and show them for selection
            questionnaires_fields_list = get_questionnaire_fields(
                [dict_['sid'] for index, dict_ in enumerate(questionnaires_list_final)], request.LANGUAGE_CODE)

            if len(selected_ev_quest):
                questionnaire_ids, field_id = zip(*selected_ev_quest)
            else:
                questionnaire_ids = ()

            for questionnaire in questionnaires_fields_list:
                questionnaire["selected_counter"] = questionnaire_ids.count(questionnaire["sid"])
                questionnaire["index"] = index
                index += 1
                for output_list in questionnaire["output_list"]:
                    if (questionnaire["sid"], output_list["field"]) in selected_ev_quest:
                        output_list["selected"] = True

    if not index:
        index = 0
    if 'group_selected_list' in request.session and questionnaires_experiment_list_final:
        if len(selected_ev_quest_experiments):
            questionnaire_ids, field_id = zip(*selected_ev_quest_experiments)
        else:
            questionnaire_ids = ()

        for questionnaire in questionnaires_experiment_fields_list:
            questionnaire["selected_field_counter"] = questionnaire_ids.count(questionnaire["sid"])
            questionnaire["index"] = index
            index += 1
            for output_list in questionnaire["output_list"]:
                if (questionnaire["sid"], output_list["field"]) in selected_ev_quest_experiments:
                    output_list["selected"] = True

    context = {
        "export_form": export_form,
        "patient_fields": patient_fields,
        "diagnosis_fields": diagnosis_fields,
        "questionnaires_fields_list": questionnaires_fields_list,
        "questionnaires_experiment_fields_list":
            questionnaires_experiment_fields_list,
        "component_list": component_list,
        "selected_participant": selected_participant,
        "selected_diagnosis": selected_diagnosis,
        "tab": '1',
    }

    if 'group_selected_list' in request.session:
        return render(request, "export/export_experiment_data.html", context)
    else:
        return render(request, template_name, context)


def get_component_with_data_and_metadata(group, component_list):

    # data collection
    if 'eeg' not in component_list:
        # eeg_data_list = EEGData.objects.filter(subject_of_group__group=group).distinct('data_configuration_tree')
        eeg_data_list = EEGData.objects.filter(subject_of_group__group=group)
        if eeg_data_list:
            component_list.append('eeg')
    if 'eeg_nwb' not in component_list:
        # eeg_data_list = EEGData.objects.filter(subject_of_group__group=group).distinct('data_configuration_tree')
        eeg_data_list = EEGData.objects.filter(subject_of_group__group=group)
        export_nwb = can_export_nwb(eeg_data_list)
        if export_nwb:
            component_list.append('eeg_nwb')
    if 'emg' not in component_list:
        # emg_data_list = EMGData.objects.filter(subject_of_group__group=group).distinct('data_configuration_tree')
        emg_data_list = EMGData.objects.filter(subject_of_group__group=group)
        if emg_data_list:
            component_list.append('emg')
    if 'tms' not in component_list:
        # tms_data_list = TMSData.objects.filter(subject_of_group__group=group).distinct('data_configuration_tree')
        tms_data_list = TMSData.objects.filter(subject_of_group__group=group)
        if tms_data_list:
            component_list.append('tms')
    if 'additional_data' not in component_list:
        # additional_data_list = AdditionalData.objects.filter(subject_of_group__group=group).distinct(
            # 'data_configuration_tree')
        additional_data_list = AdditionalData.objects.filter(subject_of_group__group=group)
        if additional_data_list:
            component_list.append('additional_data')
    if 'goalkeeper_game_data' not in component_list:
        # goalkeeper_game_data_list = DigitalGamePhaseData.objects.filter(subject_of_group__group=group).distinct(
            # 'data_configuration_tree')
        goalkeeper_game_data_list = DigitalGamePhaseData.objects.filter(subject_of_group__group=group)
        if goalkeeper_game_data_list:
            component_list.append('goalkeeper_game_data')
    if 'stimulus_data' not in component_list:
        stimulus_data_list = Stimulus.objects.filter(experiment=group.experiment)
        if stimulus_data_list:
            component_list.append('stimulus_data')
    if 'generic_data' not in component_list:
        generic_data_list = GenericDataCollectionData.objects.filter(
            subject_of_group__group=group
        )
        if generic_data_list:
            component_list.append('generic_data')

    return component_list


def get_experiment_questionnaire_response_list(group_id):
    experiment_questionnaire_response_dict = {}
    group = get_object_or_404(Group, pk=group_id)
    if group.experimental_protocol:
        for path_experiment in create_list_of_trees(group.experimental_protocol, "questionnaire"):

            questionnaire_configuration = get_object_or_404(ComponentConfiguration,
                                                            pk=path_experiment[-1][0])
            questionnaire = Questionnaire.objects.get(id=questionnaire_configuration.component.id)
            lime_survey_id = questionnaire.survey.lime_survey_id
            if lime_survey_id not in experiment_questionnaire_response_dict:
                experiment_questionnaire_response_dict[lime_survey_id] = []

            configuration_tree_list = DataConfigurationTree.objects.filter(
                component_configuration=questionnaire_configuration)
            experiment_questionnaire_response_list = []

            for data_configuration_tree in configuration_tree_list:
                experiment_questionnaire_response_list = ExperimentQuestionnaireResponse.objects.filter(
                    data_configuration_tree_id=data_configuration_tree.id)

            if experiment_questionnaire_response_list:
                if group_id not in experiment_questionnaire_response_dict:
                    experiment_questionnaire_response_dict[group_id] = {}
                if lime_survey_id not in experiment_questionnaire_response_dict[group_id]:
                    experiment_questionnaire_response_dict[group_id][lime_survey_id] = []
                experiment_questionnaire_response_dict[group_id][lime_survey_id] = \
                    experiment_questionnaire_response_list

    return experiment_questionnaire_response_dict


def get_questionnaire_experiment_header(questionnaire_lime_survey, questionnaire_id, token_id, fields,
                                        heading_type="code", current_language="pt-BR"):

    questionnaire_list = []
    language_new = get_questionnaire_language(
        questionnaire_lime_survey, questionnaire_id, current_language
    )

    token = questionnaire_lime_survey.get_participant_properties(
        questionnaire_id, token_id, "token"
    )

    responses_string = questionnaire_lime_survey.get_header_response(
        questionnaire_id, language_new, token
    )

    if not isinstance(responses_string, dict):
        questionnaire_questions = QuestionnaireUtils.responses_to_csv(responses_string)

        responses_heading_type = \
            questionnaire_lime_survey.get_header_response(
                questionnaire_id, language_new, token,
                heading_type=heading_type
            )

        questionnaire_questions_heading_type = \
            QuestionnaireUtils.responses_to_csv(responses_heading_type)

        questionnaire_header = list(zip(
            questionnaire_questions_heading_type[0], questionnaire_questions[0]
        ))

        # line 0 - header information
        for question in questionnaire_header:
            if question[1] in fields:
                questionnaire_list.append(question)

    return questionnaire_list


def update_questionnaire_list(questionnaire_list, heading_type, experiment_questionnaire, current_language="pt-BR"):

    questionnaire_list_updated = []

    if heading_type == 'code':
        return questionnaire_list

    questionnaire_lime_survey = Questionnaires()
    for questionnaire in questionnaire_list:
        # position 2: id, position 3: title,
        # position 4: output_list (field, header)
        if experiment_questionnaire:
            questionnaire_id = questionnaire[2]
            fields, headers = zip(*questionnaire[4])
            index = questionnaire[0]
            title = questionnaire[3]
            group_id = questionnaire[1]

            experiment_questionnaire_response_dict = \
                get_experiment_questionnaire_response_list(group_id)
            token_id = \
                experiment_questionnaire_response_dict[group_id][questionnaire_id][0].token_id
            questionnaire_field_header = \
                get_questionnaire_experiment_header(
                    questionnaire_lime_survey,
                    questionnaire_id, token_id, fields,
                    heading_type, current_language
                )

            questionnaire_list_updated.append(
                [index, group_id, questionnaire_id, title,
                 questionnaire_field_header]
            )
        # position 1: id, postion 2: title,
        # position 2: output_list (field, header)
        else:
            questionnaire_id = questionnaire[1]
            fields, headers = zip(*questionnaire[3])
            index = questionnaire[0]
            title = questionnaire[2]

            questionnaire_field_header = get_questionnaire_header(
                questionnaire_lime_survey, questionnaire_id,
                fields, heading_type, current_language
            )

            questionnaire_list_updated.append(
                [index, questionnaire_id, title, questionnaire_field_header]
            )

    questionnaire_lime_survey.release_session_key()

    return questionnaire_list_updated


def get_questionnaire_header(questionnaire_lime_survey, questionnaire_id, fields, heading_type="code",
                             current_language="pt-BR"):

    questionnaire_list = []

    language_new = get_questionnaire_language(questionnaire_lime_survey, questionnaire_id, current_language)

    # get a valid token (anyone)
    survey = Survey.objects.filter(lime_survey_id=questionnaire_id).first()
    questionnaire_response_list = QuestionnaireResponse.objects.filter(survey=survey)
    if questionnaire_response_list:
        token_id = questionnaire_response_list.first().token_id
        token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id, "token")

        responses_string = questionnaire_lime_survey.get_header_response(questionnaire_id, language_new, token)

        if not isinstance(responses_string, dict):

            questionnaire_questions = QuestionnaireUtils.responses_to_csv(responses_string)

            responses_heading_type = questionnaire_lime_survey.get_header_response(questionnaire_id,
                                                                                   language_new, token,
                                                                                   heading_type=heading_type)

            questionnaire_questions_heading_type = QuestionnaireUtils.responses_to_csv(responses_heading_type)

            questionnaire_header = list(zip(questionnaire_questions_heading_type[0], questionnaire_questions[0]))

            # line 0 - header information
            for question in questionnaire_header:
                if question[1] in fields:
                    questionnaire_list.append(question)

    return questionnaire_list


def get_questionnaire_experiment_fields(questionnaire_code_list, language_current="pt-BR"):
    questionnaires_included = []
    questionnaire_lime_survey = Questionnaires()

    for questionnaire in questionnaire_code_list:
        questionnaire_id = questionnaire['questionnaire'].survey.lime_survey_id
        token = questionnaire['token']
        group_id = questionnaire['group_id']
        group_title = questionnaire['group_title']

        language_new = get_questionnaire_language(questionnaire_lime_survey, questionnaire_id, language_current)

        responses_string = questionnaire_lime_survey.get_header_response(questionnaire_id, language_new, token)

        questionnaire_title = questionnaire_lime_survey.get_survey_title(questionnaire_id, language_new)

        if not isinstance(responses_string, dict):

            record_question = {'group_id': group_id, 'group_title': group_title, 'sid': questionnaire_id,
                               "title": questionnaire_title, "output_list": []}

            questionnaire_questions = QuestionnaireUtils.responses_to_csv(responses_string)

            responses_full = questionnaire_lime_survey.get_header_response(questionnaire_id,
                                                                           language_new, token, heading_type='full')
            questionnaire_questions_full = QuestionnaireUtils.responses_to_csv(responses_full)

            index = 0
            for question in questionnaire_questions[0]:
                if question not in questionnaire_evaluation_fields_excluded:

                    description = questionnaire_questions_full[0][index]

                    record_question["output_list"].append({"field": question,
                                                           "header": question,
                                                           "description": description
                                                           })

                index += 1

            questionnaires_included.append(record_question)

    questionnaire_lime_survey.release_session_key()

    return questionnaires_included


def get_questionnaire_fields(questionnaire_code_list, current_language="pt-BR"):
    """
    :param questionnaire_code_list: list with questionnaire id to be formatted with json file
    :param current_language: current language used by the caller, indicating the preferred language
    :return: 1 list: questionnaires_included - questionnaire_id that was included in the .txt file
    """

    questionnaires_included = []

    questionnaire_lime_survey = Questionnaires()
    for questionnaire_id in questionnaire_code_list:

        language_new = get_questionnaire_language(questionnaire_lime_survey, questionnaire_id, current_language)

        # get a valid token (anyone)
        survey = Survey.objects.filter(lime_survey_id=questionnaire_id).first()

        token_id = QuestionnaireResponse.objects.filter(survey=survey).first().token_id

        token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id, "token")

        responses_string = questionnaire_lime_survey.get_header_response(questionnaire_id, language_new, token)

        questionnaire_title = questionnaire_lime_survey.get_survey_title(questionnaire_id, language_new)

        if not isinstance(responses_string, dict):

            record_question = {'sid': questionnaire_id, "title": questionnaire_title, "output_list": []}

            questionnaire_questions = QuestionnaireUtils.responses_to_csv(responses_string)

            responses_full = questionnaire_lime_survey.get_header_response(questionnaire_id,
                                                                           language_new, token, heading_type='full')
            questionnaire_questions_full = QuestionnaireUtils.responses_to_csv(responses_full)

            index = 0
            # line 0 - header information
            for question in questionnaire_questions[0]:
                if question not in questionnaire_evaluation_fields_excluded:

                    description = questionnaire_questions_full[0][index]
                    record_question["output_list"].append({"field": question,
                                                           "header": question,
                                                           "description": description
                                                           })

                index += 1

            questionnaires_included.append(record_question)

    questionnaire_lime_survey.release_session_key()

    return questionnaires_included


@login_required
def filter_participants(request):

    participant_selection_form = ParticipantsSelectionForm(None)
    age_interval_form = AgeIntervalForm(None)

    if request.method == "POST":

        if request.POST['action'] == "next-step-1":

            participants_list = Patient.objects.filter(removed=False)
            # selecting participants according the study/experiment/group
            if 'study_selected_list' in request.session:
                subject_list = []
                study_selected_list = request.session['study_selected_list'][0]
                for study in study_selected_list:
                    group_id = study.split('-')[2]
                    subject_of_group = SubjectOfGroup.objects.filter(group_id=group_id)

                    for subject in subject_of_group:
                        patient = subject.subject.patient
                        if patient.id not in subject_list:
                            subject_list.append(patient.id)

                participants_list = participants_list.filter(pk__in=subject_list)

            if request.POST['type_of_selection_radio'] == 'selected':

                total_of_participants = len(participants_list)

                # selecting participants according the filters
                if "gender_checkbox" in request.POST and 'gender' in request.POST:
                    gender_list = request.POST.getlist('gender')
                    participants_list = participants_list.filter(gender__id__in=gender_list)

                if "marital_status_checkbox" in request.POST and 'marital_status' in request.POST:
                    marital_status_list = request.POST.getlist('marital_status')
                    participants_list = participants_list.filter(marital_status__id__in=marital_status_list)

                if "age_checkbox" in request.POST and 'max_age' in request.POST and 'min_age' in request.POST:
                    date_birth_min = datetime.now() - relativedelta(years=int(request.POST['max_age']))
                    date_birth_max = datetime.now() - relativedelta(years=int(request.POST['min_age']))
                    participants_list = participants_list.filter(date_birth__range=(date_birth_min, date_birth_max))

                if "location_checkbox" in request.POST:
                    if 'selected_locals' in request.POST:
                        locations_selected = request.POST.getlist('selected_locals')
                        participants_list = participants_list.filter(city__in=locations_selected)

                if "diagnosis_checkbox" in request.POST:
                    classification_of_diseases_list = request.POST.getlist('selected_diagnoses')

                    participants_list = participants_list.filter(
                        medicalrecorddata__diagnosis__classification_of_diseases__in=classification_of_diseases_list).\
                        distinct()

                # putting the list of participants in the user session
                request.session['filtered_participant_data'] = [item.id for item in participants_list]

                context = {
                    "total_of_participants": total_of_participants,
                    "participants_list": participants_list
                }
                return render(request, "export/show_selected_participants.html", context)

            else:
                request.session['filtered_participant_data'] = [item.id for item in participants_list]

                redirect_url = reverse("export_view", args=())
                return HttpResponseRedirect(redirect_url)

        if request.POST['action'] == 'previous-step-2':

            context = {
                "participant_selection_form": participant_selection_form,
                "age_interval_form": age_interval_form,
            }

            return render(request, "export/participant_selection.html", context)

        if request.POST['action'] == "next-step-2":

            redirect_url = reverse("export_view", args=())
            return HttpResponseRedirect(redirect_url)

    context = {
        "participant_selection_form": participant_selection_form,
        "age_interval_form": age_interval_form,
    }

    return render(request, "export/participant_selection.html", context)


@login_required
def export_main(request):
    redirect_url = reverse("export_menu", args=())
    return HttpResponseRedirect(redirect_url)


@login_required
def export_menu(request, template_name="export/export_menu.html"):

    export_type_list = [
        {
            'item': _('Per participant'),
            'href': reverse("filter_participants", args=()),
            'enabled': True
        },
        {
            'item': _('Per experiments'),
            'href': reverse("experiment_selection", args=()),
            'enabled': True
        },
    ]
    if 'group_selected_list' in request.session.keys():
        del request.session['group_selected_list']

    context = {
        "export_type_list": export_type_list
    }

    return render(request, template_name, context)


@login_required
def experiment_selection(request, template_name="export/experiment_selection.html"):
    research_projects = ResearchProject.objects.order_by('start_date')
    experiment_list = Experiment.objects.all()
    group_list = None
    study_list = []
    study_selected = []

    if request.method == "POST":
        participants_list = Patient.objects.filter(removed=False)
        if request.POST['action'] == "next-step-participants":
            subject_list = []
            group_selected_list = request.POST.getlist('group_selected')
            request.session['group_selected_list'] = group_selected_list

            if len(group_selected_list) > 0:
                for group_selected_id in group_selected_list:
                    group_selected = Group.objects.filter(pk=group_selected_id)
                    subject_of_group = SubjectOfGroup.objects.filter(group=group_selected)
                    for subject in subject_of_group:
                        patient = subject.subject.patient
                        if patient.id not in subject_list:
                            subject_list.append(patient.id)

                participants_list = participants_list.filter(pk__in=subject_list)
                request.session['filtered_participant_data'] = [item.id for item in participants_list]
                redirect_url = reverse("export_view", args=())
                return HttpResponseRedirect(redirect_url)
            else:
                messages.error(request, _("No group(s) selected!"))

    context = {
        "study_list": study_list,
        "study_selected": study_selected,
        "experiment_list": experiment_list,
        "group_list": group_list,
        "creating": True,
        "editing": True,
        "research_projects": research_projects
    }

    return render(request, template_name, context)


def get_block_tree(component_id, language_code=None):

    component = get_object_or_404(Component, id=component_id)

    attributes = get_component_attributes(component, language_code)

    list_of_component_configuration = []
    if component.component_type == 'block':
        configurations = ComponentConfiguration.objects.filter(parent_id=component_id).order_by('order')
        for configuration in configurations:
            component_configuration_attributes = get_component_configuration_attributes(configuration)
            component_info = get_block_tree(configuration.component_id, language_code)
            list_of_component_configuration.append(
                {'component_configuration_attributes': component_configuration_attributes,
                 'component': component_info})

    return {'identification': component.identification,
            'component_type': component.component_type,
            'attributes': attributes,
            'list_of_component_configuration': list_of_component_configuration}


def get_component_configuration_attributes(configuration):
    attributes = []
    if configuration.name:
        attributes.append({_('Name of use'): configuration.name})
    if configuration.number_of_repetitions:
        attributes.append({_('Number of repetitions'): configuration.number_of_repetitions})
    if configuration.interval_between_repetitions_value:
        attributes.append({_('Interval between repetitions value'): configuration.interval_between_repetitions_value})
        if configuration.interval_between_repetitions_unit:
            attributes.append({_('Interval between repetitions unit'): configuration.interval_between_repetitions_unit})
    attributes.append({_('Order'): configuration.order})
    attributes.append({
        _('Position in the set of steps '): _('Random') if configuration.random_position else _('Fixed')})
    attributes.append({
        _('Requires start and end datetime'): _('Yes') if configuration.requires_start_and_end_datetime else _('No')})

    return attributes


def get_component_attributes(component, language_code):
    attributes = []
    for attribute in get_general_component_attributes(component):
        attributes.append(attribute)

    specific_attributes = []
    if component.component_type == 'block':
        specific_attributes = get_block_component_attributes(component)
    elif component.component_type == 'instruction':
        specific_attributes = get_instruction_component_attributes(component)
    elif component.component_type == 'pause':
        specific_attributes = []
    elif component.component_type == 'questionnaire':
        specific_attributes = get_questionnaire_component_attributes(component, language_code)
    elif component.component_type == 'stimulus':
        specific_attributes = get_stimulus_component_attributes(component)
    elif component.component_type == 'task':
        specific_attributes = []
    elif component.component_type == 'task_experiment':
        specific_attributes = []
    elif component.component_type == 'eeg':
        specific_attributes = []
    elif component.component_type == 'emg':
        specific_attributes = []
    elif component.component_type == 'tms':
        specific_attributes = []

    for attribute in specific_attributes:
        attributes.append(attribute)

    return attributes


def get_general_component_attributes(component):
    attributes = [{_('Identification'): component.identification}]
    if component.description:
        attributes.append({_('Description'): component.description})
    if component.duration_value:
        attributes.append({_('Duration value'): component.duration_value})
        if component.duration_unit:
            attributes.append({_('Duration unit'): component.duration_unit})
    return attributes


def get_block_component_attributes(component):
    block = get_object_or_404(Block, id=component.id)
    attributes = [{_('Type'): get_block_type_name(block.type)}]
    if block.number_of_mandatory_components:
        attributes.append({_('Number of mandatory components'): block.number_of_mandatory_components})
    return attributes


def get_instruction_component_attributes(component):
    instruction = get_object_or_404(Instruction, id=component.id)
    attributes = [{_('Text'): instruction.text}]
    return attributes


def get_questionnaire_component_attributes(component, language_code):
    questionnaire = get_object_or_404(Questionnaire, id=component.id)
    attributes = [{_('LimeSurvey ID'): questionnaire.survey.lime_survey_id}]

    surveys = Questionnaires()
    questionnaire_title = surveys.get_survey_title(
        questionnaire.survey.lime_survey_id,
        get_questionnaire_language(surveys, questionnaire.survey.lime_survey_id, language_code))
    surveys.release_session_key()

    attributes.append({_('Questionnaire title'): questionnaire_title})

    return attributes


def get_stimulus_component_attributes(component):
    stimulus = get_object_or_404(Stimulus, id=component.id)
    attributes = [{_('Stimulus type'): stimulus.stimulus_type.name}]
    if stimulus.media_file:
        attributes.append({_('Media file'): stimulus.media_file})
    return attributes


def get_block_type_name(block_type):
    block_type_name = ''
    for type_element, type_name in Block.BLOCK_TYPES:
        if type_element == block_type:
            block_type_name = str(type_name)
            break
    return block_type_name if block_type_name else block_type


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


def search_locations(request):

    if request.is_ajax():
        search_text = request.GET.get('term', '')

        if search_text:
            location_list = \
                Patient.objects.filter(
                    city__icontains=search_text).exclude(removed=True).values('id', 'city').distinct('city')

            results = []
            for location in location_list:
                location_dict = {
                    'id': location['city'],
                    'label': location['city'],
                    'value': location['city']}
                results.append(location_dict)

            data = json.dumps(results)
        else:
            data = 'fail'

        mimetype = 'application/json'

        return HttpResponse(data, mimetype)


def search_diagnoses(request):

    if request.is_ajax():
        search_text = request.GET.get('term', '')

        if search_text:

            classification_of_diseases_list = ClassificationOfDiseases.objects.filter(diagnosis__isnull=False).filter(
                Q(abbreviated_description__icontains=search_text) |
                Q(description__icontains=search_text) |
                Q(code__icontains=search_text)).distinct().order_by("code")

            results = []
            for classification_of_diseases in classification_of_diseases_list:
                label = classification_of_diseases.code + ' - ' + \
                        classification_of_diseases.abbreviated_description
                diseases_dict = \
                    {'id': classification_of_diseases.id,
                     'label': label,
                     'value': classification_of_diseases.abbreviated_description}

                results.append(diseases_dict)
            data = json.dumps(results)
        else:
            data = 'fail'

        mimetype = 'application/json'

        return HttpResponse(data, mimetype)


def select_experiments_by_study(request, study_id):
    research_project = ResearchProject.objects.filter(pk=study_id)

    experiment_list = Experiment.objects.filter(research_project=research_project)

    json_experiment_list = serializers.serialize("json", experiment_list)

    return HttpResponse(json_experiment_list, content_type='application/json')


def select_groups_by_experiment(request, experiment_id):
    experiment = Experiment.objects.filter(pk=experiment_id)

    group_list = Group.objects.filter(experiment=experiment)

    json_group_list = serializers.serialize("json", group_list)

    return HttpResponse(json_group_list, content_type='application/json')
