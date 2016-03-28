from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from io import StringIO
from os import path, makedirs
from csv import writer, reader
import re
from sys import modules
from zipfile import ZipFile
from django.http import HttpResponse
from patient.models import Patient, QuestionnaireResponse
from patient.views import check_limesurvey_access
from survey.abc_search_engine import Questionnaires

from django.conf import settings
from shutil import copy, rmtree
import collections
from operator import itemgetter
import json
from datetime import datetime
from django.core.files import File

from export.models import Export
from export.export import ExportExecution, perform_csv_response, create_directory, save_to_csv, is_patient_active

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


def read_configuration_data(json_file):
    json_data = open(json_file)

    read_data = json.load(json_data)

    json_data.close()

    return read_data


json_format = [
    '      {\n',
    '        "id": %d,\n',
    '        "questionnaire_name": "%s",\n',
    '        "language": "pt-BR",\n',
    '        "depends_on": "",\n',
    '        "output_list": [\n',
    '          {\n',
    '            "field": "%s",\n',
    '            "header": "%s"\n',
    '          },\n',
    '        ],\n',
    '        "prefix_filename_responses": "Questionnaire",\n',
    '        "prefix_filename_fields": "Fields"\n',
    '      },\n',
]

questionnaire_code_list_example = [
    113491,
    256242,
    271192,
    345282,
    367311,
    456776,
    471898,
    578559,
    599846,
    885183,
    944684,
    969322,
]


def prepare_json(questionnaire_code_list=questionnaire_code_list_example):
    """
    :param questionnaire_code_list: list with questionnaire id to be formatted with json file
    :return: 2 lists: questionnaires_included - questionnaire_id that was included in the .txt file
                      questionnaires_excluded - questionnaire_id that was not included because
                                there was an error when preparing the data
                      MEDIA_ROOT/prep_json.txt - file created to be used with json export

         IMPORTANT NOTE: only questionnaires with data(with answers) can be obtained to include in the .txt file
    """
    id_index = 1
    language = "pt-BR"

    questionnaires_included = []
    questionnaires_excluded = []

    with (open(path.join(settings.MEDIA_ROOT, "prep_json.txt"), "w")) as f:
        json_file = File(f)

        questionnaire_lime_survey = Questionnaires()
        for questionnaire_id in questionnaire_code_list:
            for index in range(id_index):
                json_file.write(json_format[index])

            responses_string = questionnaire_lime_survey.get_responses(questionnaire_id, language)

            index = id_index
            print("id: %d " % questionnaire_id)

            if not isinstance(responses_string, dict):

                questionnaires_included.append(questionnaire_id)

                json_file.write(json_format[index] % questionnaire_id)
                index += 1
                questionnaire_title = questionnaire_lime_survey.get_survey_title(questionnaire_id)
                json_file.write(json_format[index] % questionnaire_title)
                index += 1
                for i in range(index, index + 3):
                    json_file.write(json_format[i])
                index = 6
                # questionnaire_questions = questionnaire_lime_survey.list_questions(questionnaire_id, 0)

                questionnaire_questions = perform_csv_response(responses_string)

                for question in questionnaire_questions[0]:
                    # properties = questionnaire_lime_survey.get_question_properties(question, language)
                    json_file.write(json_format[index])
                    json_file.write(json_format[index + 1] % question)
                    json_file.write(json_format[index + 2] % question)
                    json_file.write(json_format[index + 3])

                index = 10
                for i in range(index, len(json_format)):
                    json_file.write(json_format[i])
            else:
                print(smart_str(
                    "error: %d - questionnaire was not included because there is no data." % questionnaire_id))
                questionnaires_excluded.append(questionnaire_id)

        questionnaire_lime_survey.release_session_key()
    json_file.close()
    return questionnaires_included, questionnaires_excluded


def process_participant_data(participants, participants_list):
    export_rows_participants = []

    for participant in participants:
        headers, fields = get_headers_and_fields(participant["output_list"])

        model_to_export = getattr(modules['patient.models'], 'Patient')

        db_data = model_to_export.objects.filter(pk__in=participants_list).values_list(*fields).extra(order_by=['pk'])

        export_rows_participants = [headers]

        # transform data
        for record in db_data:
            export_rows_participants.append([smart_str(field) for field in record])

    return export_rows_participants


def create_export_instance(user):
    export_instance = Export(user=user)

    export_instance.save()

    return export_instance


def update_export_instance(input_file, output_export, export_instance):
    export_instance.input_file = input_file
    export_instance.output_export = output_export
    export_instance.save()


@login_required
# @permission_required('questionnaire.create_export')
def export_create(request, template_name="export/export_data.html"):
    try:
        export = ExportExecution()

        files_to_zip_list = []

        export_instance = create_export_instance(request.user)

        # directory_root = path.join("export", path.join(str(request.user.id), str(export_instance.id)))
        export.set_directory_base(request.user.id, export_instance.id)

        base_directory = path.split(export.get_directory_base())

        path_to_create = base_directory[1]
        base_directory = base_directory[0]

        error_msg, base_directory_name = create_directory(base_directory, path_to_create)
        if error_msg != "":
            messages.error(request, error_msg)
            return render(request, template_name)

        # Read initial json file
        json_filename = "json_export.json"
        path_source = path.join(settings.BASE_DIR, "export")
        input_name = path.join(path_source, json_filename)

        input_export_file = path.join("export", path.join(str(request.user.id),
                                                          path.join(str(export_instance.id), str(json_filename))))

        # copy data to .../media/export/<user_id>/<export_id>/
        input_filename = path.join(settings.MEDIA_ROOT, input_export_file)

        copy(input_name, input_filename)

        # prepare data to be processed

        input_data = export.read_configuration_data(input_filename)

        if not export.is_input_data_consistent() or not input_data:
            messages.error(request, error_msg)
            return render(request, template_name)

        # create directory base for export: /NES_EXPORT
        error_msg = export.create_export_directory()

        # error_msg, base_export_directory = create_directory(base_directory_name, base_directory)

        if error_msg != "":
            messages.error(request, error_msg)
            return render(request, template_name)

        # process per questionnaire data

        error_msg = export.process_per_questionnaire()
        if error_msg != "":
            messages.error(request, error_msg)
            return render(request, template_name)

        # process per participant data

        if export.get_input_data("export_per_participant"):
            per_participant_directory = export.get_input_data("per_participant_directory")

            error_msg, path_per_participant = create_directory(export.get_export_directory(), per_participant_directory)
            if error_msg != "":
                messages.error(request, error_msg)
                return render(request, template_name)

            prefix_filename_participant = "Participant"
            export_directory_base = path.join(export.get_input_data("base_directory"),
                                              export.get_input_data("per_participant_directory"))
            path_questionnaire = "Questionnaires"

            for participant in export.get_per_participant_data():

                path_participant = str(participant)
                error_msg, participant_path = create_directory(path_per_participant, path_participant)
                if error_msg != "":
                    messages.error(request, error_msg)
                    return render(request, template_name)

                error_msg, questionnaire_path = create_directory(participant_path, path_questionnaire)
                if error_msg != "":
                    messages.error(request, error_msg)
                    return render(request, template_name)

                for questionnaire in export.get_per_participant_data(participant):
                    # print(participant, questionnaire)

                    export_filename = "%s_%s.csv" % (prefix_filename_participant, str(questionnaire))

                    complete_filename = path.join(questionnaire_path, export_filename)

                    save_to_csv(complete_filename, export.get_per_participant_data(participant, questionnaire))

                    export_directory = path.join(export_directory_base, path_participant)
                    export_directory = path.join(export_directory, path_questionnaire)

                    files_to_zip_list.append([complete_filename, export_directory])

        # process participants
        participants_list = (export.get_per_participant_data().keys())

        export_rows_participants = process_participant_data(export.get_input_data("participants"), participants_list)

        export_filename = "%s.csv" % export.get_input_data('participants')[0]["output_filename"]  # "export.csv"

        base_export_directory = export.get_export_directory()
        base_directory = export.get_directory_base()

        complete_filename = path.join(base_export_directory, export_filename)

        files_to_zip_list.append([complete_filename, base_directory])

        with open(complete_filename, 'w', newline='') as csv_file:
            export_writer = writer(csv_file)
            for row in export_rows_participants:
                export_writer.writerow(row)

        # process  diagnosis file
        export_rows_diagnosis = process_participant_data(export.get_input_data("diagnosis"), participants_list)

        export_filename = "%s.csv" % export.get_input_data('diagnosis')[0]["output_filename"]  # "export.csv"

        complete_filename = path.join(base_export_directory, export_filename)

        # files_to_zip_list.append(complete_filename)
        files_to_zip_list.append([complete_filename, base_directory])

        with open(complete_filename, 'w', newline='') as csv_file:
            export_writer = writer(csv_file)
            for row in export_rows_diagnosis:
                export_writer.writerow(row)

        # create zip file and include files
        export_filename = export.get_input_data("export_filename")  # 'export.zip'

        complete_filename = path.join(base_directory_name, export_filename)

        with ZipFile(complete_filename, 'w') as zip_file:
            for filename, directory in files_to_zip_list:
                fdir, fname = path.split(filename)

                zip_file.write(filename, path.join(directory, fname))

        zip_file.close()

        output_export_file = path.join("export", path.join(str(export_instance.user.id),
                                                           path.join(str(export_instance.id), str(export_filename))))

        update_export_instance(input_export_file, output_export_file, export_instance)

        # print(export_filename)
        # print(complete_filename)

        # delete temporary directory: from base_directory and below
        rmtree(base_export_directory)

        print("finalizado corretamente")

        messages.success(request, _("Export was finished correctly"))

        # return file to the user
        zip_file = open(complete_filename, 'rb')
        response = HttpResponse(zip_file, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="export.zip"'
        response['Content-Length'] = path.getsize(complete_filename)
        return response

    except OSError as e:
        print(e)
        error_msg = e
        messages.error(request, error_msg)
        return render(request, template_name)
