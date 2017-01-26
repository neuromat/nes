# -*- coding: utf-8 -*-
import json
import re
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core import serializers
from django.core.urlresolvers import reverse
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as ug_, ugettext_lazy as _
from django.db.models import Q

from datetime import datetime
from dateutil.relativedelta import relativedelta

from os import path
from csv import writer
from sys import modules
from zipfile import ZipFile
from shutil import rmtree

from .forms import ExportForm, ParticipantsSelectionForm, AgeIntervalForm
from .models import Export
from .export import ExportExecution, perform_csv_response, create_directory

from export.input_export import build_complete_export_structure, build_partial_export_structure

from patient.models import QuestionnaireResponse, Patient, ClassificationOfDiseases, Diagnosis, MedicalRecordData
from patient.views import check_limesurvey_access

from survey.models import Survey
from survey.abc_search_engine import Questionnaires
from survey.views import get_questionnaire_language

from experiment.models import ResearchProject, Experiment, Group, SubjectOfGroup, Component, ComponentConfiguration, \
    Block, Instruction, Questionnaire, Stimulus, DataConfigurationTree

JSON_FILENAME = "json_export.json"
EXPORT_DIRECTORY = "export"

# patient_fields = [
#     {"field": 'id', "header": 'id'},
#     {"field": 'name', "header": 'name'},
#     {"field": 'gender__name', "header": 'gender'},
#     {"field": 'date_birth', "header": 'date_birth'},
#     {"field": 'marital_status', "header": 'marital_status'},
#     {"field": 'origin', "header": 'origin'},
#     {"field": 'city', "header": 'city'},
#     {"field": 'state', "header": 'state'},
#     {"field": 'country', "header": 'country'},
#     {"field": 'socialdemographicdata__natural_of', "header": 'natural_of'},
#     {"field": 'socialdemographicdata__schooling', "header": 'schooling'},
#     {"field": 'socialdemographicdata__profession', "header": 'profession'},
#     {"field": 'socialdemographicdata__social_class', "header": 'social_class'},
#     {"field": 'socialdemographicdata__occupation', "header": 'occupation'},
#     {"field": 'socialdemographicdata__benefit_government', "header": 'benefit_government'},
#     {"field": 'socialdemographicdata__religion', "header": 'religion'},
#     {"field": 'socialdemographicdata__flesh_tone', "header": 'flesh_tone'},
#     {"field": 'socialdemographicdata__citizenship', "header": 'citizenship'},
#     {"field": 'socialdemographicdata__payment', "header": 'payment'},
#     {"field": 'socialhistorydata__alcohol_period', "header": 'alcohol_period'},
#     {"field": 'socialhistorydata__alcohol_frequency', "header": 'alcohol_frequency'},
#     {"field": 'socialhistorydata__smoker', "header": 'smoker'},
#     {"field": 'socialhistorydata__alcoholic', "header": 'alcoholic'},
#     {"field": 'socialhistorydata__drugs', "header": 'drugs'},
#     {"field": 'socialhistorydata__ex_smoker', "header": 'former_smoker'},
#     {"field": 'socialhistorydata__alcohol_frequency', "header": 'alcohol_frequency'},
#     {"field": 'socialhistorydata__amount_cigarettes', "header": 'amount_cigarettes'},
# ]
#
# diagnosis_fields = [
#
#     {"field": "medicalrecorddata__record_responsible_id", "header": 'responsible_id'},
#     {"field": "medicalrecorddata__record_responsible__username", "header": 'responsible_username'},
#     {"field": "medicalrecorddata__diagnosis__date", "header": 'diagnosis_date'},
#     {"field": "medicalrecorddata__diagnosis__description", "header": 'diagnosis_description'},
#     {"field": "medicalrecorddata__diagnosis__classification_of_diseases__description",
#      "header": 'classification_of_diseases_description'},
#  {"field": "medicalrecorddata__diagnosis__classification_of_diseases_id", "header": 'classification_of_diseases_id'},
# ]


patient_fields = [
    # {"field": 'id', "header": 'id', "description": _("Identification")},
    # {"field": 'name', "header": 'name', "description": _("Full name")},
    {"field": 'gender__name', "header": 'gender', "description": _("Gender")},
    {"field": 'date_birth', "header": 'date_birth', "description": _("Date of birth")},
    {"field": 'marital_status', "header": 'marital_status', "description": _("Marital status")},
    {"field": 'origin', "header": 'origin', "description": _("Origin")},
    {"field": 'city', "header": 'city', "description": _("City")},
    {"field": 'state', "header": 'state', "description": _("State")},
    {"field": 'country', "header": 'country', "description": _("Country")},
    {"field": 'socialdemographicdata__natural_of', "header": 'natural_of', "description": _("Natural of")},
    {"field": 'socialdemographicdata__schooling', "header": 'schooling', "description": _("Schooling")},
    {"field": 'socialdemographicdata__patient_schooling', "header": 'patient_schooling',
     "description": _("Schooling of the patient")},
    {"field": 'socialdemographicdata__profession', "header": 'profession', "description": _("Profession")},
    {"field": 'socialdemographicdata__social_class', "header": 'social_class',
     "description": _("Calculated social class")},
    {"field": 'socialdemographicdata__occupation', "header": 'occupation', "description": _("Occupation")},
    {"field": 'socialdemographicdata__benefit_government', "header": 'benefit_government',
     "description": _("What form of payment of the treatment performed")},
    {"field": 'socialdemographicdata__religion', "header": 'religion', "description": _("Religion")},
    {"field": 'socialdemographicdata__flesh_tone', "header": 'flesh_tone', "description": _("Flesh tone")},
    {"field": 'socialdemographicdata__citizenship', "header": 'citizenship', "description": _("Citizenship")},
    {"field": 'socialdemographicdata__payment', "header": 'payment',
     "description": _("Do you receive some benefit from the municipal level, state or federal government?")},
    {"field": 'socialhistorydata__smoker', "header": 'smoker', "description": _("Smoker")},
    {"field": 'socialhistorydata__amount_cigarettes', "header": 'amount_cigarettes',
     "description": _("Cigarretes/Day")},
    {"field": 'socialhistorydata__ex_smoker', "header": 'former_smoker', "description": _("Former smoker")},
    {"field": 'socialhistorydata__alcoholic', "header": 'alcoholic', "description": _("Alcoholic")},
    {"field": 'socialhistorydata__alcohol_frequency', "header": 'alcohol_frequency', "description": _("Frequency")},
    {"field": 'socialhistorydata__alcohol_period', "header": 'alcohol_period', "description": _("Period")},
    {"field": 'socialhistorydata__drugs', "header": 'drugs', "description": _("Drugs")},
]

diagnosis_fields = [
    {"field": "medicalrecorddata__diagnosis__date", "header": 'diagnosis_date', "description": _("Date")},
    {"field": "medicalrecorddata__diagnosis__description", "header": 'diagnosis_description',
     "description": _("Observation")},
    {"field": "medicalrecorddata__diagnosis__classification_of_diseases_id", "header": 'classification_of_diseases_id',
     "description": _("Disease code (ICD)")},
    {"field": "medicalrecorddata__diagnosis__classification_of_diseases__description",
     "header": 'classification_of_diseases_description', "description": _("Disease Description")},
    {"field": "medicalrecorddata__diagnosis__classification_of_diseases__abbreviated_description",
     "header": 'classification_of_diseases_description', "description": _("Disease Abbreviated Description")},
]

patient_fields_inclusion = [
    ["code", {"code": "participation_code", "full": _("Participation code"),
              "abbreviated": _("Participation code")}],
]

diagnosis_fields_inclusion = [
    ["medicalrecorddata__patient__code", {"code": "participation_code", "full": _("Participation code"),
                                          "abbreviated": _("Participation code")}],
]

questionnaire_evaluation_fields_excluded = [
    "subjectid",
    "responsibleid",
]

'''

Diagnosis._meta.get_all_field_names()
['description', 'medical_record_data_id', 'complementaryexam', 'classification_of_diseases_id',
'classification_of_diseases', 'date', 'id', 'medical_record_data']


SocialDemographicData._meta.get_all_field_names()
['natural_of', 'changed_by_id', 'tv', 'wash_machine', 'flesh_tone', 'payment_id',
'house_maid', 'automobile', 'patient_schooling', 'schooling', 'radio', 'profession', 'dvd', 'bath', 'freezer',
'social_class', 'schooling_id', 'occupation', 'changed_by', 'benefit_government', 'religion_id',
'flesh_tone_id', 'refrigerator', 'patient', 'religion', 'citizenship', 'id', 'patient_id', 'payment']

SocialHistoryData._meta.get_all_field_names()
['alcohol_period', 'alcohol_period_id', 'alcohol_frequency_id', 'smoker', 'alcoholic', 'drugs',
'ex_smoker', 'changed_by', 'changed_by_id',
'alcohol_frequency', 'amount_cigarettes_id', 'id', 'patient_id', 'amount_cigarettes', 'patient']


    ['email', 'address_complement', 'changed_by_id', 'cpf', 'medicalrecorddata',
     'district',
     'zipcode', 'address_number',

     'marital_status_id',
     'telephone', 'rg', 'state',
     'socialhistorydata', 'gender_id', 'changed_by', 'subject',
     'origin', 'medical_record', 'removed',
     'city',
     'marital_status',
     'country',
     'street', 'questionnaireresponse']
     'socialdemographicdata',


'''
# BASE_DIRECTORY = 'NES_EXPORT'

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


def get_headers_and_fields(output_list):
    """
    :param output_list: list with fields and headers
    :return: list of headers
             list of fields
    """

    headers = []
    fields = []

    for element in output_list:
        if element["field"]:
            headers.append(element["header"])
            fields.append(element["field"])

    return headers, fields


# def read_configuration_data(json_file):
#     json_data = open(json_file)
#
#     read_data = json.load(json_data)
#
#     json_data.close()
#
#     return read_data


def process_participant_data(participants, participants_list):
    export_rows_participants = []

    for participant in participants:
        headers, fields = get_headers_and_fields(participant["output_list"])

        model_to_export = getattr(modules['patient.models'], 'Patient')

        db_data = model_to_export.objects.filter(id__in=participants_list).values_list(*fields).extra(order_by=['id'])

        export_rows_participants = [headers]

        # transform data
        for record in db_data:
            export_rows_participants.append([smart_str(field) for field in record])

    return export_rows_participants


def create_export_instance(user):
    export_instance = Export(user=user)

    export_instance.save()

    return export_instance


def get_export_instance(user, export_id):
    export_instance = Export.objects.get(user=user, id=export_id)

    return export_instance


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

    if heading_type == "abbreviated":
        data_updated = data_to_abbreviate[:17] + ".."
    else:
        data_updated = data_to_abbreviate

    return data_updated


def update_participants_list(participants_list, heading_type):

    if participants_list:

        # update header, if necessary
        if heading_type != "code":
            for participant in participants_list:
                header_translated = find_description(participant[0], patient_fields)
                participant[1] = abbreviated_data(header_translated, heading_type)

        # include participation_code

        for field, header in patient_fields_inclusion:
            header_translated = ug_(header[heading_type])
            participants_list.append([field, abbreviated_data(header_translated, heading_type)])


def update_diagnosis_list(diagnosis_list, heading_type):

    if diagnosis_list:
        # update header, if necessary
        if heading_type != "code":
            for diagnosis in diagnosis_list:
                header_translated = find_description(diagnosis[0], diagnosis_fields)
                diagnosis[1] = abbreviated_data(header_translated, heading_type)

        # include participation_code
        for field, header in diagnosis_fields_inclusion:
            header_translated = ug_(header[heading_type])
            diagnosis_list.append([field, abbreviated_data(header_translated, heading_type)])


# @login_required
# @permission_required('questionnaire.create_export')
# def export_create(request, template_name="export/export_data.html"):
def export_create(request, export_id, input_filename, template_name="export/export_data.html"):
    try:

        export_instance = get_export_instance(request.user, export_id)

        export = ExportExecution(export_instance.user.id, export_instance.id)

        # update data from advanced search
        if 'filtered_participant_data' in request.session:
            participants_filtered_list = request.session['filtered_participant_data']
        else:
            participants_filtered_list = Patient.objects.filter(removed=False)
        export.set_participants_filtered_data(participants_filtered_list)

        # files_to_zip_list = []

        # export_instance = create_export_instance(request.user)
        #
        # # directory_root = path.join("export", path.join(str(request.user.id), str(export_instance.id)))
        # export.set_directory_base(request.user.id, export_instance.id)
        #
        base_directory, path_to_create = path.split(export.get_directory_base())
        #
        # path_to_create = base_directory[1]
        # base_directory = base_directory[0]
        #
        error_msg, base_directory_name = create_directory(base_directory, path_to_create)
        if error_msg != "":
            messages.error(request, error_msg)
            return render(request, template_name)
        #
        # # Read initial json file
        # json_filename = "json_export.json"
        # path_source = path.join(settings.BASE_DIR, "export")
        # input_name = path.join(path_source, json_filename)
        #
        input_export_file = path.join("export", path.join(str(request.user.id),
                                                          path.join(str(export_instance.id), str(JSON_FILENAME))))
        #
        # # copy data to .../media/export/<user_id>/<export_id>/
        # input_filename = path.join(settings.MEDIA_ROOT, input_export_file)
        #
        # copy(input_name, input_filename)

        # prepare data to be processed

        input_data = export.read_configuration_data(input_filename)

        # gady #####
        if not export.is_input_data_consistent() or not input_data:
            messages.error(request, _("Inconsistent data read from json file"))
            return render(request, template_name)
        ##########################################

        # create directory base for export: /NES_EXPORT
        error_msg = export.create_export_directory()

        # error_msg, base_export_directory = create_directory(base_directory_name, base_directory)

        if error_msg != "":
            messages.error(request, error_msg)
            return render(request, template_name)

        # process per questionnaire data

        #### gady ##################
        error_msg = export.process_per_questionnaire()
        if error_msg != "":
            messages.error(request, error_msg)
            return render(request, template_name)
        ##################################################

        # process per participant data
        error_msg = export.process_per_participant()
        if error_msg != "":
            messages.error(request, error_msg)
            return render(request, template_name)

        # process participants
        # only participants that were used in questionnaire: export.get_per_participant_data().keys()
        participants_list = (export.get_participants_filtered_data())
        # participants_list = (export.get_per_participant_data().keys())
        participants_input_data = export.get_input_data("participants")

        if participants_input_data[0]["output_list"] and participants_list:

            export_rows_participants = process_participant_data(participants_input_data, participants_list)

            export_filename = "%s.csv" % export.get_input_data('participants')[0]["output_filename"]  # "export.csv"

            base_export_directory = export.get_export_directory()
            base_directory = export.get_input_data("base_directory")   # /NES_EXPORT

            complete_filename = path.join(base_export_directory, export_filename)

            export.files_to_zip_list.append([complete_filename, base_directory])

            with open(complete_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as csv_file:
                export_writer = writer(csv_file)
                for row in export_rows_participants:
                    export_writer.writerow(row)

        # process  diagnosis file
        diagnosis_input_data = export.get_input_data("diagnosis")

        if diagnosis_input_data[0]['output_list'] and participants_list:
            export_rows_diagnosis = process_participant_data(diagnosis_input_data, participants_list)

            export_filename = "%s.csv" % export.get_input_data('diagnosis')[0]["output_filename"]  # "export.csv"

            base_directory = export.get_input_data("base_directory")   # /NES_EXPORT
            base_export_directory = export.get_export_directory()

            complete_filename = path.join(base_export_directory, export_filename)

            # files_to_zip_list.append(complete_filename)
            export.files_to_zip_list.append([complete_filename, base_directory])

            with open(complete_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as csv_file:
                export_writer = writer(csv_file)
                for row in export_rows_diagnosis:
                    export_writer.writerow(row)

        # create zip file and include files
        export_complete_filename = ""
        if export.files_to_zip_list:
            export_filename = export.get_input_data("export_filename")  # 'export.zip'

            export_complete_filename = path.join(base_directory_name, export_filename)

            with ZipFile(export_complete_filename, 'w') as zip_file:
                for filename, directory in export.files_to_zip_list:
                    fdir, fname = path.split(filename)

                    zip_file.write(filename.encode('utf-8'), path.join(directory, fname))

            zip_file.close()

            output_export_file = path.join("export", path.join(str(export_instance.user.id),
                                                               path.join(str(export_instance.id),
                                                                         str(export_filename))))

            update_export_instance(input_export_file, output_export_file, export_instance)

            print("finalizado corretamente")

        # print(export_filename)
        # print(complete_filename)

        # delete temporary directory: from base_directory and below
        base_export_directory = export.get_export_directory()
        rmtree(base_export_directory)

        # messages.success(request, _("Export was finished correctly"))
        print("finalizado corretamente 2")

        return export_complete_filename
        # return file to the user
        # zip_file = open(complete_filename, 'rb')
        # response = HttpResponse(zip_file, content_type='application/zip')
        # response['Content-Disposition'] = 'attachment; filename="export.zip"'
        # response['Content-Length'] = path.getsize(complete_filename)
        # return response

    except OSError as e:
        print(e)
        error_msg = e
        messages.error(request, error_msg)
        return render(request, template_name)


@login_required
def export_view(request, template_name="export/export_data.html"):
    export_form = ExportForm(request.POST or None, initial={'title': 'title',
                                                            'responses': ['short'], 'headings': 'code'})

    selected_ev_quest = []
    selected_participant = []
    selected_diagnosis = []

    if request.method == "POST":

        questionnaires_selected_list = request.POST.getlist('to[]')

        questionnaires_list = []

        # fields = {}

        # previous_questionnaire_id = 0
        previous_questionnaire_id = -1
        output_list = []
        for questionnaire in questionnaires_selected_list:
            index, sid, title, field, header = questionnaire.split("*")

            sid = int(sid)    # transform to integer
            #
            # if sid not in fields:
            #     fields[sid] = []
            # fields[sid].append(field)

            # if sid != previous_questionnaire_id:
            if index != previous_questionnaire_id:
                if previous_questionnaire_id != 0:
                    output_list = []

                questionnaires_list.append([index, sid, title, output_list])

                # previous_questionnaire_id = sid
                previous_questionnaire_id = index

            output_list.append((field, header))

        # get participants list
        participant_selected_list = request.POST.getlist('patient_selected')

        participants_list = []

        for participant in participant_selected_list:
            participants_list.append(participant.split("*"))

        # get diagnosis list
        diagnosis_selected_list = request.POST.getlist('diagnosis_selected')

        diagnosis_list = []

        for diagnosis in diagnosis_selected_list:
            diagnosis_list.append(diagnosis.split("*"))

        selected_data_available = (len(questionnaires_selected_list) or
                                   len(participant_selected_list) or len(diagnosis_selected_list))

        # selected_data_available = (len(participant_selected_list) or len(diagnosis_selected_list))

        if selected_data_available:

            if export_form.is_valid():
                print("valid data")

                if questionnaires_selected_list:
                    per_participant = export_form.cleaned_data['per_participant']
                    per_questionnaire = export_form.cleaned_data['per_questionnaire']
                    heading_type = export_form.cleaned_data['headings']
                    responses_type = export_form.cleaned_data['responses']
                    questionnaires_list = update_questionnaire_list(questionnaires_list, heading_type,
                                                                    request.LANGUAGE_CODE)
                    # insert participation_code
                    update_participants_list(participants_list, heading_type)
                    update_diagnosis_list(diagnosis_list, heading_type)
                else:
                    per_participant = True
                    per_questionnaire = False
                    heading_type = None
                    responses_type = None
                    questionnaires_list = []

                # heading_type = export_form.cleaned_data['headings']
                # responses_type = export_form.cleaned_data['responses']

                # questionnaires_list = update_questionnaire_list(questionnaires_list, heading_type,
                #                                                 request.LANGUAGE_CODE)

                # insert participation_code
                # update_participants_list(participants_list, heading_type)
                # update_diagnosis_list(diagnosis_list, heading_type)

                export_instance = create_export_instance(request.user)

                input_export_file = path.join(EXPORT_DIRECTORY,
                                              path.join(str(request.user.id),
                                                        path.join(str(export_instance.id), str(JSON_FILENAME))))

                # copy data to .../media/export/<user_id>/<export_id>/
                input_filename = path.join(settings.MEDIA_ROOT, input_export_file)
                create_directory(settings.MEDIA_ROOT, path.split(input_export_file)[0])

                build_complete_export_structure(per_participant, per_questionnaire,
                                                participants_list, diagnosis_list,
                                                questionnaires_list, responses_type, heading_type,
                                                input_filename, request.LANGUAGE_CODE)

                complete_filename = export_create(request, export_instance.id, input_filename)

                if complete_filename:

                    messages.success(request, _("Export was finished correctly"))

                    print("antes do fim: httpResponse")

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

                for participant in participants_list:
                    selected_participant.append(participant[0])

                for diagnosis in diagnosis_list:
                    selected_diagnosis.append(diagnosis[0])
        else:
            # if not questionnaires_selected_list
            # if not questionnaires_selected_list:
            #     # per_participant = export_form.cleaned_data['per_participant']
            #     per_participant = True
            #     export_instance = create_export_instance(request.user)
            #     input_export_file = path.join(EXPORT_DIRECTORY,
            #                                   path.join(str(request.user.id),
            #                                             path.join(str(export_instance.id), str(JSON_FILENAME))))
            #
            #     # copy data to .../media/export/<user_id>/<export_id>/
            #     input_filename = path.join(settings.MEDIA_ROOT, input_export_file)
            #     create_directory(settings.MEDIA_ROOT, path.split(input_export_file)[0])
            #
            #     build_partial_export_structure(per_participant, participants_list, input_filename,request.LANGUAGE_CODE)
            #
            #     complete_filename = export_create(request, export_instance.id, input_filename)
            #
            #     if complete_filename:
            #
            #         messages.success(request, _("Export was finished correctly"))
            #
            #         print("antes do fim: httpResponse")
            #
            #         zip_file = open(complete_filename, 'rb')
            #         response = HttpResponse(zip_file, content_type='application/zip')
            #         response['Content-Disposition'] = 'attachment; filename="export.zip"'
            #         response['Content-Length'] = path.getsize(complete_filename)
            #         return response
            #     else:
            #         messages.error(request, _("Export data was not generated."))
            #
            # else:
            messages.error(request, _("No data was select. Export data was not generated."))

    # else:
    # page 1 - list of questionnaires
    if 'study_selected_list' in request.session:
        studies_list = request.session['study_selected_list'][0]
        survey_list = []
        for study in studies_list:
            group_id = study.split('-')[2]
            group = get_object_or_404(Group, pk=group_id)
            if group.experimental_protocol is not None:
                for path_experiment in create_list_of_trees(group.experimental_protocol, "questionnaire"):
                    questionnaire_configuration = get_object_or_404(ComponentConfiguration, pk=path_experiment[-1][0])
                    questionnaire = Questionnaire.objects.get(id=questionnaire_configuration.component.id)
                    survey_list.append(questionnaire.survey.lime_survey_id)

            # if group.experimental_protocol is not None:
            #     tree = get_block_tree(group.experimental_protocol.id, request.LANGUAGE_CODE)
            #     for component in tree['list_of_component_configuration']:
            #         if component['component']['component_type'] == 'questionnaire':
            #             limesurvey_id = component['component']['attributes'][1]['LimeSurvey ID']
            #             survey_list.append(limesurvey_id)
                # surveys = Questionnaires()

    surveys = Questionnaires()

    limesurvey_available = check_limesurvey_access(request, surveys)

    questionnaires_list = []

    if limesurvey_available:
        questionnaires_list = surveys.find_all_active_questionnaires()

    surveys.release_session_key()

    questionnaires_list_final = []

    # removing surveys that are not entrance evaluation
    # entrance_evaluation_questionnaires = QuestionnaireResponse.objects.all()
    entrance_evaluation_questionnaire_ids_list = set(QuestionnaireResponse.objects.values_list('survey',
                                                                                               flat=True))

    # ev_questionnaire_ids_list = entrance_evaluation_questionnaires.values_list("survey")
    surveys_with_ev_list = Survey.objects.filter(id__in=entrance_evaluation_questionnaire_ids_list)

    if 'study_selected_list' in request.session:
        for survey_item in survey_list:
            for questionnaire in questionnaires_list:
                if questionnaire['sid'] == survey_item:
                    questionnaires_list_final.append(questionnaire)
                    break
    else:
        for survey in surveys_with_ev_list:
            for questionnaire in questionnaires_list:
                if survey.lime_survey_id == questionnaire['sid']:
                    questionnaires_list_final.append(questionnaire)
                    break

    # page 2 fields

    # entrance evaluation questionnarie fields

    # if len(language_code) > 2:
    #     language_code = "{}-{}".format(language_code[:2],language_code[-2:].upper())

    questionnaires_fields_list = get_questionnaire_fields(questionnaires_list_final, request.LANGUAGE_CODE)

    if len(selected_ev_quest):
        questionnaire_ids, field_id = zip(*selected_ev_quest)
    else:
        questionnaire_ids = ()

    index = 0
    for questionnaire in questionnaires_fields_list:
        questionnaire["selected_counter"] = questionnaire_ids.count(questionnaire["sid"])
        questionnaire["index"] = index
        index += 1
        for output_list in questionnaire["output_list"]:
            if (questionnaire["sid"], output_list["field"]) in selected_ev_quest:
                output_list["selected"] = True

    # for field in questionnaires_fields_list:
    #     for questionnaire in questionnaires_list_final:
    #         if field["sid"] == questionnaire['sid']:
    #             field["title"] = questionnaire["surveyls_title"]
    #             break

    context = {

        # "limesurvey_available": limesurvey_available,
        "export_form": export_form,
        # "questionnaires_list": questionnaires_list_final,
        # "contacts": contacts,
        "patient_fields": patient_fields,
        "diagnosis_fields": diagnosis_fields,
        "questionnaires_fields_list": questionnaires_fields_list,
        "selected_ev_quest": selected_ev_quest,
        "selected_participant": selected_participant,
        "selected_diagnosis": selected_diagnosis,
    }

    # elif page == 2:

    return render(request, template_name, context)


def update_questionnaire_list(questionnaire_list, heading_type, current_language="pt-BR"):

    questionnaire_list_updated = []

    if heading_type == 'code':
        return questionnaire_list

    questionnaire_lime_survey = Questionnaires()

    for questionnaire in questionnaire_list:

        # position 0: id, postion 1: title

        questionnaire_id = questionnaire[0]

        # position 2: output_list (field, header)
        fields, headers = zip(*questionnaire[2])

        questionnaire_field_header = get_questionnaire_header(questionnaire_lime_survey, questionnaire_id,
                                                              fields, heading_type, current_language)

        questionnaire_list_updated.append([questionnaire_id, questionnaire[1], questionnaire_field_header])

    questionnaire_lime_survey.release_session_key()

    return questionnaire_list_updated


def get_questionnaire_header(questionnaire_lime_survey,
                             questionnaire_id, fields, heading_type="code", current_language="pt-BR"):
    # return: {"<question_code>": "question_heading_type", "<question_code1>": "question_heading_type1"...}
    # ("<question_code>": "question_heading_type")

    # questionnaire_header = []
    questionnaire_list = []

    language_new = get_questionnaire_language(questionnaire_lime_survey, questionnaire_id, current_language)

    # get a valid token (anyone)
    survey = Survey.objects.filter(lime_survey_id=questionnaire_id).first()
    token_id = QuestionnaireResponse.objects.filter(survey=survey).first().token_id
    token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id, "token")

    responses_string = questionnaire_lime_survey.get_header_response(questionnaire_id, language_new, token)

    if not isinstance(responses_string, dict):

        questionnaire_questions = perform_csv_response(responses_string)

        responses_heading_type = questionnaire_lime_survey.get_header_response(questionnaire_id,
                                                                               language_new, token,
                                                                               heading_type=heading_type)

        questionnaire_questions_heading_type = perform_csv_response(responses_heading_type)

        questionnaire_header = list(zip(questionnaire_questions_heading_type[0], questionnaire_questions[0]))

        # line 0 - header information
        for question in questionnaire_header:
            if question[1] in fields:
                questionnaire_list.append(question)

    return questionnaire_list


def get_questionnaire_fields(questionnaire_code_list, language_current="pt-BR"):
    """
    :param questionnaire_code_list: list with questionnaire id to be formatted with json file
    :return: 1 list: questionnaires_included - questionnaire_id that was included in the .txt file

    """

    questionnaires_included = []

    questionnaire_lime_survey = Questionnaires()
    for questionnaire in questionnaire_code_list:

        questionnaire_id = questionnaire["sid"]

        language_new = get_questionnaire_language(questionnaire_lime_survey, questionnaire_id, language_current)

        # get a valid token (anyone)
        survey = Survey.objects.filter(lime_survey_id=questionnaire_id).first()
        token_id = QuestionnaireResponse.objects.filter(survey=survey).first().token_id
        token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id, "token")

        responses_string = questionnaire_lime_survey.get_header_response(questionnaire_id, language_new, token)

        questionnaire_title = questionnaire_lime_survey.get_survey_title(questionnaire_id, language_new)

        # print("id: %d " % questionnaire_id)

        if not isinstance(responses_string, dict):

            record_question = {'sid': questionnaire_id, "title": questionnaire_title, "output_list": []}

            questionnaire_questions = perform_csv_response(responses_string)

            responses_full = questionnaire_lime_survey.get_header_response(questionnaire_id,
                                                                           language_new, token, heading_type='full')
            questionnaire_questions_full = perform_csv_response(responses_full)

            index = 0
            # line 0 - header information
            for question in questionnaire_questions[0]:
                if question not in questionnaire_evaluation_fields_excluded:

                    # properties = questionnaire_lime_survey.get_question_properties(question, language)

                    # record_question["output_list"].append({"field": question,
                    #                                        "header": question})

                    description = questionnaire_questions_full[0][index]

                    # if len(description)+3+len(question) > 120:
                    #     length = 120 - (3+len(question))
                    #
                    #     description_part1 = description[:length-30]
                    #     description_part2 = description[-25:]
                    #     description = description_part1 + "..." + description_part2

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
                    diagnosis_list = Diagnosis.objects.filter(
                        classification_of_diseases_id__in=classification_of_diseases_list).values(
                        'medical_record_data__patient_id')
                    participants_list = participants_list.filter(
                        changed_by__medicalrecorddata__patient_id__in=diagnosis_list).distinct(
                        'changed_by__medicalrecorddata__patient_id')

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
            'item': _('Information from input questionnaires'),
            'href': reverse("filter_participants", args=()),
        },
        {
            'item': _('Information from experiments'),
            'href': reverse("experiment_selection", args=()),
        },
    ]
    if 'study_selected_list' in request.session.keys():
        del request.session['study_selected_list']

    context = {
        "export_type_list": export_type_list
    }


    return render(request, template_name, context)


@login_required
def experiment_selection(request, template_name="export/experiment_selection.html"):
    research_projects = ResearchProject.objects.order_by('start_date')
    experiment_list = Experiment.objects.all()
    group_list = Group.objects.all()
    study_list = []
    study_selected = []
    index = 0

    if request.method == "POST":
        participants_list = Patient.objects.filter(removed=False)
        if request.POST['action'] == "next-step-participants":
            subject_list = []
            group_selected = request.POST['group_selected']
            subject_of_group = SubjectOfGroup.objects.filter(group=group_selected)
            for subject in subject_of_group:
                patient = subject.subject.patient
                if patient.id not in subject_list:
                    subject_list.append(patient.id)

            participants_list = participants_list.filter(pk__in=subject_list)

            context = {
                "total_of_participants": len(participants_list),
                "participants_list": participants_list
            }
            return render(request, "export/show_selected_participants.html", context)

            # request.session['study_selected_list'] = [study_selected]

            # redirect_url = reverse("filter_participants", args=())
            # return HttpResponseRedirect(redirect_url)

    # for research in research_projects:
    #     research_project = get_object_or_404(ResearchProject, pk=research.id)
    #     if hasattr(Experiment, 'research_project'):
    #         experiments = Experiment.objects.filter(research_project=research_project)
    #         for exp in experiments:
    #             experiment = get_object_or_404(Experiment, pk=exp.id)
    #             if hasattr(Group, 'experiment'):
    #                 groups = Group.objects.filter(experiment=experiment)
    #                 for group in groups:
    #                     index = index + 1
    #                     study_list.append({
    #                         'study_index': index,
    #                         'study_id': research.id,
    #                         'study_title': research_project.title,
    #                         'experiment_id': experiment.id,
    #                         'experiment_title': experiment.title,
    #                         'group_id': group.id,
    #                         'group_title': group.title
    #                     })

    # putting the list of participants in the user session
    # request.session['filtered_participant_data'] = [item.id for item in participants_list]

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
        _('Requires start and end datetime'): _('Yes') if configuration.requires_start_and_end_datetime else _('No') })

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


def create_list_of_trees(block_id, component_type):

    list_of_path = []

    configurations = ComponentConfiguration.objects.filter(parent_id=block_id)

    if component_type:
        configurations = configurations.filter(component__component_type=component_type)

    for configuration in configurations:
        list_of_path.append(
            [[configuration.id,
              configuration.parent.identification,
              configuration.name,
              configuration.component.identification]]
        )

    # Look for steps in descendant blocks.
    block_configurations = ComponentConfiguration.objects.filter(parent_id=block_id,
                                                                 component__component_type="block")

    for block_configuration in block_configurations:
        list_of_configurations = create_list_of_trees(block_configuration.component.id, component_type)
        for item in list_of_configurations:
            item.insert(0,
                        [block_configuration.id,
                         block_configuration.parent.identification,
                         block_configuration.name,
                         block_configuration.component.identification])
            list_of_path.append(item)

    return list_of_path


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
    location_list = ''

    if request.method == "POST":
        search_text = request.POST['search_text']

        if search_text:
            if re.match('[a-zA-Z ]+', search_text):
                location_list = \
                    Patient.objects.filter(city__icontains=search_text).exclude(removed=True).distinct('city')

        return render_to_response('export/locations.html', {'location_list': location_list})


def search_diagnoses(request):
    diagnosis_list = ''

    if request.method == "POST":
        search_text = request.POST['search_text']

        if search_text:
            if re.match('[a-zA-Z ]+', search_text):
                # classification_of_diseases_list = \
                #     Diagnosis.objects.filter(classification_of_diseases__description__icontains=search_text).\
                #         distinct('classification_of_diseases')
                classification_of_diseases_list =  ClassificationOfDiseases.objects.\
                    filter(Q(abbreviated_description__icontains=search_text) | Q(description__icontains=search_text) |
                           Q(code__icontains=search_text)).distinct('description')

        return render_to_response('export/diagnoses.html',
                                  {'classification_of_diseases_list': classification_of_diseases_list})


def select_experiments_by_study(request, study_id):
    research_project = ResearchProject.objects.filter(pk= study_id)

    experiment_list = Experiment.objects.filter(research_project=research_project)

    json_experiment_list = serializers.serialize("json", experiment_list)

    return HttpResponse(json_experiment_list, content_type='application/json')


def select_groups_by_experiment(request, experiment_id):
    experiment = Experiment.objects.filter(pk= experiment_id)

    group_list = Group.objects.filter(experiment=experiment)

    json_group_list = serializers.serialize("json", group_list)

    return HttpResponse(json_group_list, content_type='application/json')