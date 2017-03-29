# -*- coding: utf-8 -*-
import collections
import json
import re

from csv import writer, reader
from sys import modules

from datetime import datetime

from django.conf import settings
from django.core.files import File
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.apps import apps
from django.shortcuts import get_object_or_404

from export.export_utils import create_list_of_trees

from io import StringIO

from operator import itemgetter

from os import path, makedirs

from patient.models import Patient, QuestionnaireResponse
from experiment.models import QuestionnaireResponse as ExperimentQuestionnaireResponse, SubjectOfGroup, Group, Survey, \
    ComponentConfiguration, Questionnaire
from experiment.views import get_experimental_protocol_description

from survey.abc_search_engine import Questionnaires
from survey.views import is_limesurvey_available


DEFAULT_LANGUAGE = "pt-BR"

metadata_directory = "Questionnaire_metadata"

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

input_data_keys = [
    "base_directory",
    "export_per_participant",
    "export_per_questionnaire",
    "per_participant_directory",
    "per_questionnaire_directory",
    "export_filename",
    "questionnaires"
]

directory_structure = [
    {"per_questionnaire": ["root", "base_directory", "export_per_questionnaire"],
     "per_participant": ["root", "base_directory", "export_per_participant"],
     "participant": ["root", "base_directory"],
     "diagnosis": ["root", "base_directory"],
     }
]

# valid for all questionnaires (no distinction amongst questionnaires)
included_questionnaire_fields = [
    {"field": "participant_code", "header": {"code": "participant_code",
                                             "full": _("Participant code"),
                                             "abbreviated": _("Participant code")},
     "model": "patient.patient", "model_field": "code"},
]


# questionnaire_special_fields = [
#     ["code", {"code": "participation_code", "full": _("Participation code"),"abbreviated": _("Participation code")}],
# ]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def to_number(value):
    return int(float(value))


def save_to_csv(complete_filename, rows_to_be_saved):
    """
    :param complete_filename: filename and directory structure where file is going to be saved
    :param rows_to_be_saved: list of rows that are going to be written on the file
    :return:
    """
    with open(complete_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as csv_file:
        export_writer = writer(csv_file)
        for row in rows_to_be_saved:
            export_writer.writerow(row)


def perform_csv_response(responses_string):
    """
    :param responses_string:
    :return:
    """
    response_reader = reader(StringIO(responses_string.decode()), delimiter=',')
    responses_list = []
    for row in response_reader:
        responses_list.append(row)
    return responses_list


def create_directory(basedir, path_to_create):
    """
    Create a directory

    :param basedir: directory that already exists (parent path where new path must be included)
    :param path_to_create: directory to be created
    :return:
            - "" if path was correctly created or error message if there was an error
            - complete_path -> basedir + path created
    """

    complete_path = ""

    if not path.exists(basedir.encode('utf-8')):
        return _("Base path does not exist"), complete_path

    complete_path = path.join(basedir, path_to_create)

    # print("encode: ", sys.getfilesystemencoding(), sys.getdefaultencoding())
    # print("create_directory-encode:", complete_path.encode('utf-8'))
    if not path.exists(complete_path.encode('utf-8')):
        # print("create_directory:", basedir, path_to_create)
        # print("create_directory:", complete_path)
        makedirs(complete_path.encode('utf-8'))

    return "", complete_path


def is_patient_active(subject_id):
    response = False

    if is_number(subject_id):
        patient_id = to_number(subject_id)

        if QuestionnaireResponse.objects.filter(patient_id=patient_id).exists():
            if not Patient.objects.filter(pk=patient_id)[0].removed:
                response = True

    return response


class LogMessages:
    def __init__(self, user, file_name=path.join(settings.MEDIA_ROOT, "export_log")):
        self.user = user
        self.file_name = file_name

    def log_message(self, text, param1="", param2=""):
        current_time = datetime.now()

        text_message = "%s %s %s %s %s" % (smart_str(current_time), smart_str(self.user),
                                           smart_str(text), smart_str(param1), smart_str(param2))
        with open(self.file_name.encode('utf-8'), "a", encoding='UTF-8') as f:
            file_log = File(f)
            file_log.write(text_message)

        file_log.close()


class ExportExecution:
    def get_username(self, request):
        self.user_name = None
        if request.user.is_authenticated():
            self.user_name = request.user.username
        return self.user_name

    def __init__(self, user_id, export_id):
        # self.get_session_key()

        # questionnaire_id = 0
        self.files_to_zip_list = []
        # self.headers = []
        # self.fields = []
        self.directory_base = ''
        self.base_directory_name = path.join(settings.MEDIA_ROOT, "export")
        # self.directory_base = self.base_directory_name
        self.set_directory_base(user_id, export_id)
        self.base_export_directory = ""
        self.user_name = None
        self.input_data = {}
        self.per_participant_data = {}
        self.participants_per_entrance_questionnaire = {}
        self.participants_per_experiment_questionnaire = {}
        self.questionnaires_data = {}
        self.root_directory = ""
        self.participants_filtered_data = []
        self.questionnaire_code_and_id = {}
        self.per_group_data = {}

    def set_directory_base(self, user_id, export_id):
        self.directory_base = path.join(self.base_directory_name, str(user_id))
        self.directory_base = path.join(self.directory_base, str(export_id))

    def get_directory_base(self):

        return self.directory_base  # MEDIA_ROOT/export/username_id/export_id

    def create_export_directory(self):

        base_directory = self.get_input_data("base_directory")

        error_msg, self.base_export_directory = create_directory(self.get_directory_base(), base_directory)

        return error_msg

    def get_export_directory(self):

        return self.base_export_directory   # MEDIA_ROOT/export/username_id/export_id/NES_EXPORT

    def read_configuration_data(self, json_file, update_input_data=True):
        json_data = open(json_file)

        input_data_temp = json.load(json_data)

        if update_input_data:
            self.input_data = input_data_temp

        json_data.close()

        return input_data_temp

    def is_input_data_consistent(self):

        # verify if important tags from input_data are available

        for data_key in input_data_keys:
            # if not self.get_input_data(data_key):
            if data_key not in self.input_data.keys():
                return False
        return True

    def get_input_data(self, key):

        if key in self.input_data.keys():
            return self.input_data[key]
        return ""

    def set_questionnaire_header_and_fields(self, questionnaire):

        headers = []
        fields = []

        questionnaire_id = questionnaire["id"]
        for output_list in questionnaire["output_list"]:
            if output_list["field"]:
                headers.append(output_list["header"])
                fields.append(output_list["field"])

        if questionnaire_id not in self.questionnaires_data:
            self.questionnaires_data[questionnaire_id] = {}

        self.questionnaires_data[questionnaire_id]["header"] = headers
        self.questionnaires_data[questionnaire_id]["fields"] = fields

        return headers, fields

    def append_questionnaire_header_and_field(self, questionnaire_id, header, fields):
        # only one header, field instance
        for field in fields:
            if field not in self.questionnaires_data[questionnaire_id]["fields"]:
                self.questionnaires_data[questionnaire_id]["header"].append(header[fields.index(field)])
                self.questionnaires_data[questionnaire_id]["fields"].append(field)

    def get_header_questionnaire(self, questionnaire_id):
        # headers_questionnaire format: dict {questionnaire_id: {header:[header]}}

        header = []
        if questionnaire_id in self.questionnaires_data:
            header = self.questionnaires_data[questionnaire_id]["header"]
        return header

    def get_questionnaire_fields(self, questionnaire_id):
        # headers_questionnaire format: dict {questinnaire_id: {fields:[fields]}}

        fields = []
        if questionnaire_id in self.questionnaires_data:
            fields = self.questionnaires_data[questionnaire_id]["fields"]
        return fields

    def get_header_description(self, questionnaire_id, field):

        index = self.questionnaires_data[questionnaire_id]["fields"].index(field)

        header_description = self.questionnaires_data[questionnaire_id]["header"][index]

        return header_description

    def include_in_per_participant_data(self, to_be_included_list, participant_id, questionnaire_id):
        """
        :param to_be_included_list: list with information to be included in include_data dict
        :param participant_id: participant identification (number)
        :param questionnaire_id: questionnaire identification (number)
        :return: include_data dict is updated with new information from parameters

        Note: include_data format example:
        {10: {1: [[5, 7, 8], [4, 9, 6], [11, 12, 13]]}}
        10: participant_id
        1: questionnaire_id

        """
        if participant_id not in self.per_participant_data:
            self.per_participant_data[participant_id] = {}

        if questionnaire_id not in self.per_participant_data[participant_id]:
            self.per_participant_data[participant_id][questionnaire_id] = []

        for element in to_be_included_list:
            self.per_participant_data[participant_id][questionnaire_id].append(element)

    def include_participant_per_questionnaire(self, token_id, code):

        if code not in self.participants_per_entrance_questionnaire:
            self.participants_per_entrance_questionnaire[code] = []

        if code not in self.participants_per_experiment_questionnaire:
            self.participants_per_experiment_questionnaire[code] = []

        questionnaire_response = QuestionnaireResponse.objects.filter(token_id=token_id)
        if questionnaire_response:
            patient_id = QuestionnaireResponse.objects.filter(token_id=token_id).values('patient_id')[0]['patient_id']
            if patient_id not in self.participants_per_entrance_questionnaire[code]:
                self.participants_per_entrance_questionnaire[code].append(patient_id)
        else:
            questionnaire_response = ExperimentQuestionnaireResponse.objects.filter(token_id=token_id)
            if questionnaire_response:
                subject_of_group = questionnaire_response.values('subject_of_group')
                patient = Patient.objects.filter(subject__subjectofgroup=subject_of_group)
                if patient:
                    patient_id = patient.values('id')[0]['id']

                    if patient_id is not None \
                            and patient_id not in self.participants_per_experiment_questionnaire[code]:
                        self.participants_per_experiment_questionnaire[code].append(patient_id)

    def include_group_data(self, group_list):
        surveys = Questionnaires()
        for group_id in group_list:
            group = get_object_or_404(Group, pk=group_id)
            title = group.title
            description = group.description
            if group_id not in self.per_group_data:
                self.per_group_data[group_id] = []
            self.per_group_data[group_id].append(title)
            self.per_group_data[group_id].append(description)

            participant_group_list = Patient.objects.filter(subject__subjectofgroup__group=group).values('id')
            self.per_group_data[group_id].append(participant_group_list)
            questionnaire_per_group = {}

            if group.experimental_protocol is not None:
                questionnaire_response_list = ExperimentQuestionnaireResponse.objects.filter(
                    subject_of_group__group=group)

                for path_experiment in create_list_of_trees(group.experimental_protocol, "questionnaire"):
                    path_questionnaire = ''
                    size = len(path_experiment[0])
                    step = 1
                    while step < size:
                        path_questionnaire += path_experiment[0][step] + "/"
                        step += 2
                    questionnaire_configuration = get_object_or_404(ComponentConfiguration, pk=path_experiment[-1][0])
                    questionnaire = Questionnaire.objects.get(id=questionnaire_configuration.component.id)
                    questionnaire_identification = questionnaire.identification
                    questionnaire_id = questionnaire.survey.lime_survey_id
                    questionnaire_code = questionnaire.survey.code

                    # if questionnaire_code not in questionnaire_per_group:
                    #     questionnaire_per_group[questionnaire_code] = []
                    for questionnaire_response in questionnaire_response_list:
                        completed = surveys.get_participant_properties(questionnaire_id,
                                                                       questionnaire_response.token_id, "completed")
                        # carrega os questionarios completos
                        if completed is not None and completed != "N" and completed != "":

                            questionnaire_data_dic = {
                                'token': str(questionnaire_response.token_id),
                                'patient_id': questionnaire_response.subject_of_group.subject.patient_id,
                                'identification': questionnaire_identification,
                                'path_questionnaire': path_questionnaire,
                                'data_completed': completed
                            }
                            if questionnaire_code not in questionnaire_per_group:
                                questionnaire_per_group[questionnaire_code] = []
                            questionnaire_per_group[questionnaire_code].append(questionnaire_data_dic)

            # dados(token,patient_id) dos questionarios no grupo
            self.per_group_data[group_id].append(questionnaire_per_group)
        surveys.release_session_key()

    def get_experiment_questionnaire_response_per_questionnaire(self, questionnaire_code, group_id):
        experiment_questionnaire_response = []
        if questionnaire_code in self.per_group_data[group_id][3]:
            for element in self.per_group_data[group_id][3][questionnaire_code]:
                questionnaire_response = ExperimentQuestionnaireResponse.objects.filter(token_id=element['token'])[0]
                experiment_questionnaire_response.append(questionnaire_response)

        return experiment_questionnaire_response

    def get_participant_list(self, group_id):
        participant_list = []
        if self.per_group_data[group_id][2]:
            for element in self.per_group_data[group_id][2]:
                participant_list.append(element['id'])

        return participant_list

    def get_per_participant_data(self, participant=None, questonnaire=None):

        if questonnaire:
            return self.per_participant_data[participant][questonnaire]

        if participant:
            return self.per_participant_data[participant]

        return self.per_participant_data

    def set_participants_filtered_data(self, participants_filtered_list):

        participants = Patient.objects.filter(removed=False).values_list("id")

        self.participants_filtered_data = participants.filter(id__in=participants_filtered_list)

        # return participants

    def get_participants_filtered_data(self):

        # participants = Patient.objects.filter(removed=False).values_list("id")

        return self.participants_filtered_data

    # def set_participants_from_entrance_questionnaire(self, participants_entrance_questionnaire_list):
    #
    #     participants = Patient.objects.filter(removed=False).values_list("id")
    #
    #     self.participants_from_entrance_questionnaire = \
    #         participants.filter(id__in=participants_entrance_questionnaire_list)
    #
    #     # return participants
    #
    # def get_participants_from_entrance_questionnaire(self):
    #
    #     # participants = Patient.objects.filter(removed=False).values_list("id")
    #
    #     return self.participants_from_entrance_questionnaire
    #
    # def set_participants_from_experiment_questionnaire(self, participants_experiment_questionnaire_list):
    #
    #     participants = Patient.objects.filter(removed=False).values_list("id")
    #
    #     self.participants_from_experiment_questionnaire = \
    #         participants.filter(id__in=participants_experiment_questionnaire_list)
    #
    #     # return participants
    #
    # def get_participants_from_experiment_questionnaire(self):
    #
    #     # participants = Patient.objects.filter(removed=False).values_list("id")
    #
    #     return self.participants_from_experiment_questionnaire

    def update_questionnaire_rules(self, questionnaire_id):

        header = []
        fields = []

        heading_type = self.get_heading_type()

        for row in included_questionnaire_fields:
            header_translated = _(row["header"][heading_type])
            header.append(smart_str(header_translated))
            fields.append(smart_str(row["field"]))

        self.append_questionnaire_header_and_field(questionnaire_id, header, fields)

    def transform_questionnaire_data(self, patient_id, fields):

        for row in included_questionnaire_fields:

            model_db = apps.get_model(row["model"])

            model_data = model_db.objects.all()

            if model_data.filter(id=patient_id).exists():
                value = model_data.filter(id=patient_id).values_list(row["model_field"])[0][0]
            else:
                value = ''

            fields.append(smart_str(value))

        return fields

    def get_title(self, questionnaire_id):

        title = ''
        questionnaires = self.get_input_data("questionnaires")
        for questionnaire in questionnaires:
            if questionnaire_id == questionnaire["id"]:
                title = questionnaire["questionnaire_name"]
                break
        return title

    def get_title_reduced(self, questionnaire_id=None, questionnaire_code=None):

        reduced_title = ''
        title = ''

        if questionnaire_code:
            # if Survey.objects.filter(code=questionnaire_code).exists():
            questionnaire_id = self.get_questionnaire_id_from_code(questionnaire_code)

        if questionnaire_id:
            title = self.get_title(questionnaire_id)

        if title:
            title = re.sub(r'[^\w]', ' ', title)
            title = title.split(" ")

            for part in title:
                if len(part):
                    reduced_title += part + "-"

            reduced_title = reduced_title[:-1]
            reduced_title = reduced_title[:30]

        return reduced_title

    def include_questionnaire_code_and_id(self, code, questionnaire_id):

        if code not in self.questionnaire_code_and_id:
            self.questionnaire_code_and_id[code] = questionnaire_id

    def get_questionnaire_id_from_code(self, code):

        questionnaire_id = 0
        if code in self.questionnaire_code_and_id:
            questionnaire_id = self.questionnaire_code_and_id[code]

        return questionnaire_id

    def get_questionnaire_code_from_id(self, questionnaire_id):
        questionnaire_code = 0

        for code in self.questionnaire_code_and_id:
            if self.questionnaire_code_and_id[code] == questionnaire_id:
                questionnaire_code = code
                break

        return questionnaire_code

    @staticmethod
    def redefine_questionnaire_title(title):
        reduced_title = ''
        if title:
            title = re.sub(r'[^\w]', ' ', title)
            title = title.split(" ")

            for part in title:
                if len(part):
                    reduced_title += part + "-"

            reduced_title = reduced_title[:-1]
            reduced_title = reduced_title[:30]

        return reduced_title

    def create_questionnaire_explanation_fields_file(self, questionnaire_id, language,
                                                     questionnaire_lime_survey, fields):

        """
        :param questionnaire_id:
        :param language:
        :param questionnaire_lime_survey:
        :param fields: fields from questionnaire that are to be exported
        :return: header, formatted according to fields
                 data_rows, formatted according to fields
                 if error, both data are []
        """
        # clear fields
        fields_cleared = [field.split("[")[0] for field in fields]

        questionnaire_explanation_fields_list = [header_explanation_fields]

        fields_from_questions = []

        # for each field, verify the question description
        # get title

        questionnaire_title = questionnaire_lime_survey.get_survey_title(questionnaire_id, language)
        # questionnaire_title = self.get_title(questionnaire_id)

        questionnaire_code = self.get_questionnaire_code_from_id(questionnaire_id)

        # get fields description
        questionnaire_questions = questionnaire_lime_survey.list_questions(questionnaire_id, 0)

        for question in questionnaire_questions:

            properties = questionnaire_lime_survey.get_question_properties(question, language)

            if ('title' in properties) and (properties['title'] in fields_cleared):

                fields_from_questions.append(properties['title'])

                # cleaning the question field
                properties['question'] = re.sub('{.*?}', '', re.sub('<.*?>', '', properties['question']))
                properties['question'] = properties['question'].replace('&nbsp;', '').strip()

                question_to_list = [smart_str(questionnaire_code), smart_str(questionnaire_title),
                                    smart_str(properties['title']), smart_str(properties['question'])]

                options_list = []

                if isinstance(properties['answeroptions'], dict):

                    options = collections.OrderedDict(sorted(properties['answeroptions'].items()))

                    column_scale = ['']
                    if isinstance(properties['attributes_lang'], dict):
                        column_scale = [attribute for attribute in sorted(properties['attributes_lang'].values())]

                    for option_key, option_values in options.items():
                        if len(column_scale) > option_values['scale_id']:
                            column_title = column_scale[option_values['scale_id']]
                        else:
                            column_title = ''
                        options_list.append([smart_str(option_key), smart_str(option_values['answer']),
                                             smart_str(option_values['assessment_value']), smart_str(column_title)])
                else:
                    options_list = [[smart_str(" ") for blank in range(4)]]  # includes blank line

                if isinstance(properties['subquestions'], dict):

                    sub_questions_list = [[smart_str(value['title']), smart_str(value['question'])]
                                          for value in properties['subquestions'].values()]

                    sub_questions_list = sorted(sub_questions_list, key=itemgetter(0))
                else:
                    sub_questions_list = [[smart_str(" ") for blank in range(2)]]  # includes blank line

                for sub_question in sub_questions_list:

                    for option in options_list:
                        questionnaire_explanation_fields_list.append(question_to_list + sub_question + option)

        if len(fields_cleared) != len(fields_from_questions):

            for field in fields_cleared:

                if field not in fields_from_questions:
                    description = self.get_header_description(questionnaire_id, field)
                    question_to_list = [smart_str(questionnaire_code), smart_str(questionnaire_title),
                                        smart_str(field), smart_str(description)]

                    questionnaire_explanation_fields_list.append(question_to_list)

        return questionnaire_explanation_fields_list

    def merge_participants_data_per_questionnaire_process(self, fields_description, participant_list):
        # get fields from patient
        export_participant_row = self.process_participant_data(self.get_input_data('participants'),
                                                               participant_list)
        # Merge fields from questionnaires and patient
        export_fields_list = []
        export_row_list = []
        # Building the header
        for field in fields_description[0][0:len(fields_description[0]) - 1]:
            export_row_list.append(field)
        for field in export_participant_row[0]:
            export_row_list.append(field)
        export_fields_list.append(export_row_list)
        # Including the responses
        for fields in fields_description[1:fields_description.__len__()]:
            participation_code = fields[len(fields) - 1]
            export_row_list = []
            for field in fields[0:len(fields) - 1]:
                export_row_list.append(field)
            for fields in export_participant_row[1:export_participant_row.__len__()]:
                if participation_code == fields[len(fields) - 1]:
                    for field in fields:
                        export_row_list.append(field)
            export_fields_list.append(export_row_list)

        return export_fields_list

    def merge_participant_data_per_participant_process(self, questionnaire_code, participant_code,
                                                       export_participant_row):
        export_fields_list = []

        fields_rows = self.get_per_participant_data(participant_code, questionnaire_code)

        for rows in fields_rows:
            export_rows = rows[0:len(rows) - 1]
            for fields in export_participant_row[1:export_participant_row.__len__()]:
                if rows[len(rows)-1] == fields[len(fields) - 1]:
                    for field in fields:
                        export_rows.append(field)
            export_fields_list.append(export_rows)

        return export_fields_list

    def process_per_questionnaire(self):

        error_msg = ""
        export_per_questionnaire_directory = ''
        export_metadata_directory = ''
        path_per_questionnaire = ''
        path_per_questionnaire_metadata = ''

        # and save per_participant data
        if self.get_input_data("export_per_questionnaire"):
            # check if exist fields selected from questionnaires
            # path ex. /Users/.../qdc/media/.../NES_EXPORT/Per_questionnaire/
            error_msg, path_per_questionnaire = create_directory(self.get_export_directory(),
                                                                 self.get_input_data("per_questionnaire_directory"))
            if error_msg != "":
                return error_msg
            # path: /NES_EXPORT/Per_questionnaire
            export_per_questionnaire_directory = path.join(self.get_input_data("base_directory"),
                                                           self.get_input_data("per_questionnaire_directory"))
            # path: /NES_EXPORT/Questionnaire_metadata
            export_metadata_directory = path.join(self.get_input_data("base_directory"),
                                                  self.get_input_data("questionnaire_metadata_directory"))
            # path ex. /Users/.../media/NES_EXPORT/Questionnaire_metadata/
            error_msg, path_per_questionnaire_metadata = create_directory(
                self.get_export_directory(), self.get_input_data("questionnaire_metadata_directory"))
            if error_msg != "":
                return error_msg

        questionnaire_lime_survey = Questionnaires()

        for questionnaire in self.get_input_data("questionnaires"):

            questionnaire_id = questionnaire["id"]
            language = questionnaire["language"]

            print(questionnaire_id)

            # per_participant_data is updated by define_questionnaire method
            fields_description = self.define_questionnaire(questionnaire, questionnaire_lime_survey, group_id="")

            # create directory for questionnaire: <per_questionnaire>/<q_code_title>
            if self.get_input_data("export_per_questionnaire") and (len(fields_description) > 1):
                # path_questionnaire = str(questionnaire_id)

                questionnaire_code = self.get_questionnaire_code_from_id(questionnaire_id)
                questionnaire_title = self.get_title_reduced(questionnaire_id=questionnaire_id)
                # ex. Per_questionnaire.Q123_aaa
                path_questionnaire = "%s_%s" % (str(questionnaire_code), questionnaire_title)

                # path ex. /Users/.../media/NES_EXPORT/Per_questionnaire/Q123_aaa
                error_msg, export_path = create_directory(path_per_questionnaire, path_questionnaire)
                if error_msg != "":
                    return error_msg

                # path ex. /NES_EXPORT/Per_questionnaire/Q123_aaa/
                export_directory = path.join(export_per_questionnaire_directory, path_questionnaire)
                export_filename = \
                    "%s_%s.csv" % (questionnaire["prefix_filename_responses"], str(questionnaire_code))
                # path ex. /Users/.../media/NES_EXPORT/Per_questionnaire.Q123_aaa/Responses_Q123.csv
                complete_filename = path.join(export_path, export_filename)

                if self.get_input_data('participants')[0]['output_list']:
                    participant_list = self.participants_per_entrance_questionnaire[questionnaire_code]
                    export_field_list = self.merge_participants_data_per_questionnaire_process(fields_description,
                                                                                               participant_list)
                    save_to_csv(complete_filename, export_field_list)
                else:
                    save_to_csv(complete_filename, fields_description)

                self.files_to_zip_list.append([complete_filename, export_directory])

                # create questionnaire fields file ("fields.csv") - metadata directory
                fields = self.get_questionnaire_fields(questionnaire_id)
                questionnaire_fields = self.create_questionnaire_explanation_fields_file(questionnaire_id, language,
                                                                                         questionnaire_lime_survey,
                                                                                         fields)

                export_filename = "%s_%s.csv" % (questionnaire["prefix_filename_fields"], str(questionnaire_code))

                # path ex. /Users/.../media/NES_EXPORT/Questionnaire_metadata/Q123_aaa
                error_msg, export_path = create_directory(path_per_questionnaire_metadata, path_questionnaire)
                if error_msg != "":
                    return error_msg

                # path: /NES_EXPORT/Questionnaire_metadata/Q123_aaa
                export_directory = path.join(export_metadata_directory, path_questionnaire)
                # path ex. /Users/.../media/NES_EXPORT/Questionnaire_metadata/Q123_aaa/Fields_Q123.csv
                complete_filename = path.join(export_path, export_filename)

                save_to_csv(complete_filename, questionnaire_fields)

                self.files_to_zip_list.append([complete_filename, export_directory])

        questionnaire_lime_survey.release_session_key()

        return error_msg

    def process_per_entrance_questionnaire(self):

        error_msg = ""
        export_per_questionnaire_directory = ''
        export_metadata_directory = ''
        path_per_questionnaire = ''
        path_per_questionnaire_metadata = ''

        # and save per_participant data
        if self.get_input_data("export_per_questionnaire"):
            # path ex. /Users/.../NES_EXPORT/Participant_data
            error_msg, path_participant_data = create_directory(self.get_export_directory(),
                                                                self.get_input_data("participant_data_directory"))
            if error_msg != "":
                return error_msg

            # criar no path /qdc/media/export/#user/#export_instance/Participant_data/Per_questionnaire
            error_msg, path_per_questionnaire = create_directory(path_participant_data,
                                                                 self.get_input_data("per_questionnaire_directory"))
            if error_msg != "":
                return error_msg

            # criar no path /qdc/media/export/#user/#export_instance/Participant_data/Questionnaire_metadata/
            error_msg, path_per_questionnaire_metadata = create_directory(
                path_participant_data, self.get_input_data("questionnaire_metadata_directory"))
            if error_msg != "":
                return error_msg

            # path:'NES_EXPORT/Participant_data/'
            export_per_entrance_questionnaire_directory = path.join(self.get_input_data("base_directory"),
                                                                    self.get_input_data("participant_data_directory"))
            # path:'NES_EXPORT/Participant_data/Per_questionnaire/'
            export_per_questionnaire_directory= path.join(export_per_entrance_questionnaire_directory,
                                                          self.get_input_data("per_questionnaire_directory"))

            # path: 'NES_EXPORT/Participant_data/Questionnaire_metadata'
            export_metadata_directory = path.join(export_per_entrance_questionnaire_directory,
                                                  self.get_input_data("questionnaire_metadata_directory"))

        questionnaire_lime_survey = Questionnaires()

        for questionnaire in self.get_input_data("questionnaires"):

            questionnaire_id = questionnaire["id"]
            language = questionnaire["language"]

            print(questionnaire_id)

            # per_participant_data is updated by define_questionnaire method
            fields_description = self.define_questionnaire(questionnaire, questionnaire_lime_survey, group_id="")

            # create directory for questionnaire: <per_questionnaire>/<q_code_title>
            if self.get_input_data("export_per_questionnaire") and (len(fields_description) > 1):
                # path_questionnaire = str(questionnaire_id)

                questionnaire_code = self.get_questionnaire_code_from_id(questionnaire_id)
                questionnaire_title = self.get_title_reduced(questionnaire_id=questionnaire_id)
                path_questionnaire = "%s_%s" % (str(questionnaire_code), questionnaire_title)

                # path ex. /qdc/media/export/#user/#export_instance/Participant_data/Per_questionnaire/Q123_aaa/
                error_msg, export_path = create_directory(path_per_questionnaire, path_questionnaire)
                if error_msg != "":
                    return error_msg

                export_filename = "%s_%s.csv" % (questionnaire["prefix_filename_responses"], str(questionnaire_code))
                # path:'NES_EXPORT/Participant_data/Per_questionnaire/Q123_aaa/'
                export_directory = path.join(export_per_questionnaire_directory, path_questionnaire)
                # path ex. /qdc/media/export/#user/#export_instance/Participant_data/Per_questionnaire/Q123_aaa/Responses_Q123.csv
                complete_filename = path.join(export_path, export_filename)

                if self.get_input_data('participants')[0]['output_list']:
                    participant_list = self.participants_per_entrance_questionnaire[questionnaire_code]
                    export_fields_list = self.merge_participants_data_per_questionnaire_process(fields_description,
                                                                                                participant_list)
                    save_to_csv(complete_filename, export_fields_list)
                else:
                    save_to_csv(complete_filename, fields_description)

                self.files_to_zip_list.append([complete_filename, export_directory])

                # create questionnaire fields file ("fields.csv") in Questionnaire_metadata directory
                fields = self.get_questionnaire_fields(questionnaire_id)

                questionnaire_fields = self.create_questionnaire_explanation_fields_file(questionnaire_id, language,
                                                                                         questionnaire_lime_survey,
                                                                                         fields)

                export_filename = "%s_%s.csv" % (questionnaire["prefix_filename_fields"], str(questionnaire_code))
                # path: 'NES_EXPORT/Participant_data/Questionnaire_metadata/Q123_aaa/'
                export_directory = path.join(export_metadata_directory, path_questionnaire)

                # path ex. '/User/.../NES_EXPORT/Participant_data/Questionnaire_metadata/Q123_aaa'
                error_msg, export_path = create_directory(path_per_questionnaire_metadata, path_questionnaire)
                if error_msg != "":
                    return error_msg

                # path ex. '/User/.../NES_EXPORT/Participant_data/Questionnaire_metadata/Q123_aaa/Fields_Q123.csv'
                complete_filename = path.join(export_path, export_filename)

                save_to_csv(complete_filename, questionnaire_fields)

                self.files_to_zip_list.append([complete_filename, export_directory])

        questionnaire_lime_survey.release_session_key()

        return error_msg

    def process_per_experiment_questionnaire(self):

        error_msg = ""
        export_per_questionnaire_directory = ''
        export_metadata_directory = ''
        path_per_questionnaire = ''
        path_experiment_data = ''

        # and save per_participant data
        if self.get_input_data("export_per_experiment"):
            # path ex. /Users/.../NES_EXPORT/Experiment_data
            error_msg, path_experiment_data = create_directory(self.get_export_directory(),
                                                               self.get_input_data("experiment_data_directory"))
            if error_msg != "":
                return error_msg

            #path ex. /NES_EXPORT/Experiment_data
            export_experiment_data = path.join(self.get_input_data("base_directory"),
                                               self.get_input_data("experiment_data_directory"))

        questionnaire_lime_survey = Questionnaires()

        for questionnaire in self.get_input_data("questionnaires_from_experiments"):

            questionnaire_id = questionnaire["id"]
            language = questionnaire["language"]
            # cria directorio por cada grupo
            for group_data in self.per_group_data:
                group_title = self.per_group_data[group_data][0]
                path_group = "Group_" + group_title
                path_directory_group = path.join(path_per_questionnaire, path_group)
                if not path.exists(path_directory_group):
                    # cria pasta com o nome do grupo ex. Users/..../NES_EXPORT/Experiment_data/Group_xxx
                    error_msg, path_per_group = create_directory(path_experiment_data, path_group)
                    if error_msg != "":
                        return error_msg
                if self.get_participant_list(group_data):
                    # path para exportaçao ('NES_EXPORT/Experiment_data/Group_xxx/')
                    export_directory_group = path.join(export_experiment_data, path_group)
                    # Ex 'NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire/'
                    export_directory_group_per_questionnaire = path.join(
                        export_directory_group, self.get_input_data("per_questionnaire_directory"))

                    # path ex. Users/.../NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire/ '
                    error_msg, path_group_per_questionnaire = create_directory(
                        path_per_group, self.get_input_data("per_questionnaire_directory"))
                    if error_msg != "":
                        return error_msg

                    # path ex. Users/.../NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata/ '
                    error_msg, path_group_per_metadata = create_directory(
                        path_per_group, self.get_input_data("questionnaire_metadata_directory"))
                    if error_msg != "":
                        return error_msg

                    print(questionnaire_id)

                    # per_participant_data is updated by define_questionnaire method
                    fields_description = self.define_questionnaire(questionnaire, questionnaire_lime_survey,group_data)

                    # create directory for questionnaire: <per_questionnaire>/<q_code_title>
                    if self.get_input_data("export_per_experiment") and (len(fields_description) > 1):
                        # path_questionnaire = str(questionnaire_id)
                        questionnaire_code = self.get_questionnaire_code_from_id(questionnaire_id)
                        questionnaire_title = self.redefine_questionnaire_title(questionnaire['questionnaire_name'])
                        # Ex. Q123_aaa
                        directory_questionnaire_name = "%s_%s" % (str(questionnaire_code), questionnaire_title)

                        # Cria directory com o nome do questionario
                        # Ex. Users/.../NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire/Q123_aaa/
                        error_msg, complete_export_path = create_directory(path_group_per_questionnaire,
                                                                           directory_questionnaire_name)
                        if error_msg != "":
                            return error_msg
                        # Responses_Q123.csv
                        export_filename = "%s_%s.csv" % (questionnaire["prefix_filename_responses"],
                                                         str(questionnaire_code))

                        # Ex. NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire/Q123_aaaa/
                        export_directory = path.join(export_directory_group_per_questionnaire,
                                                     directory_questionnaire_name)
                        # Ex. Users/.../NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire/Q123_aaa/Responses_Q123.csv
                        complete_filename = path.join(complete_export_path, export_filename)

                        if self.get_input_data('participants')[0]['output_list']:
                            participant_list = self.get_participant_list(group_data)
                            # add questionnaire experiment path to export_rows

                            export_fields_list = self.merge_participants_data_per_questionnaire_process(
                                fields_description, participant_list)
                            save_to_csv(complete_filename, export_fields_list)
                        else:
                            save_to_csv(complete_filename, fields_description)

                        self.files_to_zip_list.append([complete_filename, export_directory])

                        # create questionnaire fields file ("fields.csv") in Questionnaire_metadata directory
                        fields = self.get_questionnaire_fields(questionnaire_id)
                        questionnaire_fields = self.create_questionnaire_explanation_fields_file(
                            questionnaire_id, language,questionnaire_lime_survey,fields)
                        # Fields_Q123.csv
                        export_filename = "%s_%s.csv" % (questionnaire["prefix_filename_fields"],
                                                         str(questionnaire_code))

                        # metadata directory para export ('NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata/')
                        export_metadata_directory = path.join(export_directory_group,
                                                              self.get_input_data("questionnaire_metadata_directory"))
                        # Ex. 'NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata/Q123_aaa/'
                        export_directory = path.join(export_metadata_directory, directory_questionnaire_name)
                        # path ex. /Users/.../NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata/Q123_aaa/
                        error_msg, complete_export_metadata_path = create_directory(path_group_per_metadata,
                                                                                    directory_questionnaire_name)
                        if error_msg != "":
                            return error_msg

                        complete_filename = path.join(complete_export_metadata_path, export_filename)

                        save_to_csv(complete_filename, questionnaire_fields)

                        self.files_to_zip_list.append([complete_filename, export_directory])

        questionnaire_lime_survey.release_session_key()

        return error_msg

    def process_per_participant(self):

        error_msg = ''

        if self.get_input_data("export_per_participant"):
            # path ex. /Users/.../NES_EXPORT/Per_participant/
            error_msg, path_per_participant = create_directory(self.get_export_directory(),
                                                               self.get_input_data("per_participant_directory"))
            if error_msg != "":
                return error_msg

            prefix_filename_participant = "Participant_"
            # path ex. /NES_EXPORT/Per_participant/
            export_directory_base = path.join(self.get_input_data("base_directory"),
                                              self.get_input_data("per_participant_directory"))

            for participant_code in self.get_per_participant_data():
                # ex. Participant_P123
                path_participant = prefix_filename_participant + str(participant_code)
                # path ex. /Users/.../NES_EXPORT/Per_participant/Participant_P123/
                error_msg, participant_path = create_directory(path_per_participant, path_participant)
                if error_msg != "":
                    return error_msg

                for questionnaire_code in self.get_per_participant_data(participant_code):

                    questionnaire_id = self.get_questionnaire_id_from_code(questionnaire_code)
                    title = self.get_title_reduced(questionnaire_id=questionnaire_id)
                    export_filename = "%s_%s_%s.csv" % (str(participant_code), str(questionnaire_code), title)
                    header = self.get_header_questionnaire(questionnaire_id)
                    fields_rows = self.get_per_participant_data(participant_code, questionnaire_code)

                    if self.get_input_data('participants')[0]['output_list']:
                        header = header[0:len(header)-1]

                        patient_id = Patient.objects.filter(code=participant_code)
                        if patient_id:
                            participant_list = [patient_id.values('id')[0]['id']]
                            # get fields from patient 
                            export_participant_row = self.process_participant_data(
                                self.get_input_data('participants'), participant_list)
                            for field in export_participant_row[0]:
                                header.append(field)
                            per_participant_rows = [header]
                            export_fields_row = self.merge_participant_data_per_participant_process(
                                questionnaire_code, participant_code, export_participant_row)
                            for field in export_fields_row:
                                per_participant_rows.append(field)
                    else:
                        per_participant_rows = [header]
                        for fields in fields_rows:
                            per_participant_rows.append(fields)
                    # path ex. /Users/.../NES_EXPORT/Per_participant/Participant_P123/P123_Q123_aaa.csv
                    complete_filename = path.join(participant_path, export_filename)

                    save_to_csv(complete_filename, per_participant_rows)
                    # path ex. /NES_EXPORT/Per_participant/Participant_P123/
                    export_directory = path.join(export_directory_base, path_participant)

                    self.files_to_zip_list.append([complete_filename, export_directory])

        return error_msg

    def process_per_participant_per_entrance_questionnaire(self):

        error_msg = ''

        if self.get_input_data("export_per_participant"):
            # path ex. /Users/.../NES_EXPORT/Participant_data/
            path_participant_data = path.join(self.get_export_directory(),
                                              self.get_input_data("participant_data_directory"))
            # path ex. /Users/.../NES_EXPORT/Participant_data/Per_participant/
            error_msg, path_per_participant = create_directory(path_participant_data,
                                                               self.get_input_data("per_participant_directory"))
            if error_msg != "":
                return error_msg

            prefix_filename_participant = "Participant_"
            # path ex. /NES_EXPORT/Participant_data/Per_participant/
            export_participant_data = path.join(self.get_input_data("base_directory"),
                                                self.get_input_data("participant_data_directory"))
            # path ex. /NES_EXPORT/Participant_data/Per_participant/
            export_directory_base = path.join(export_participant_data, self.get_input_data("per_participant_directory"))

            for participant_code in self.get_per_participant_data():
                # for participant_filtered in self.participants_from_entrance_questionnaire:
                patient_id = Patient.objects.filter(code=participant_code).values('id')[0]['id']

                path_participant = prefix_filename_participant + str(participant_code)
                # /Users/.../NES_EXPORT/Participant_data/Per_participant/Participant_P123/
                error_msg, participant_path = create_directory(path_per_participant, path_participant)
                if error_msg != "":
                    return error_msg

                for questionnaire_code in self.get_per_participant_data(participant_code):
                    if self.participants_per_entrance_questionnaire[questionnaire_code]:
                        if patient_id in self.participants_per_entrance_questionnaire[questionnaire_code]:
                            questionnaire_id = self.get_questionnaire_id_from_code(questionnaire_code)
                            # seleciona os participantes dos questionnarios de entrada
                            for questionnaire in self.get_input_data("questionnaires"):
                                if questionnaire_id == questionnaire['id']:
                                    title = self.get_title_reduced(questionnaire_id=questionnaire_id)
                                    export_filename = "%s_%s_%s.csv" % (str(participant_code), str(questionnaire_code), title)

                                    header = self.get_header_questionnaire(questionnaire_id)
                                    per_participant_rows = [header]

                                    if self.get_input_data('participants')[0]['output_list']:
                                        header = header[0:len(header)-1]
                                        participant_list = [patient_id]
                                        # get fields from patient 
                                        export_participant_row = self.process_participant_data(
                                            self.get_input_data('participants'), participant_list)

                                        for field in export_participant_row[0]:
                                            header.append(field)
                                        per_participant_rows = [header]

                                        export_fields_rows = self.merge_participant_data_per_participant_process(
                                            questionnaire_code, participant_code, export_participant_row)
                                        for fields in export_fields_rows:
                                            per_participant_rows.append(fields)
                                    else:
                                        fields_rows = self.get_per_participant_data(participant_code,
                                                                                    questionnaire_code)
                                        for fields in fields_rows:
                                            per_participant_rows.append(fields)
                                    # path ex. /Users/.../NES_EXPORT/Participant_data/Per_participant/
                                    complete_filename = path.join(participant_path, export_filename)

                                    save_to_csv(complete_filename, per_participant_rows)

                                    export_directory = path.join(export_directory_base, path_participant)

                                    self.files_to_zip_list.append([complete_filename, export_directory])

        return error_msg

    def process_per_participant_per_experiment(self):

        error_msg = ''

        if self.get_input_data("export_per_participant"):
            # path ex. /Users/.../NES_EXPORT/Experiment_data/
            per_experiment_directory = path.join(self.get_export_directory(),
                                                 self.get_input_data("experiment_data_directory"))
            prefix_filename_participant = "Participant_"
            # path: NES_EXPORT/Experiment_data/
            export_directory_base = path.join(self.get_input_data("base_directory"),
                                              self.get_input_data("experiment_data_directory"))

            for group_data in self.per_group_data:
                group_title = self.per_group_data[group_data][0]
                path_group = "Group_" + group_title
                path_per_group = path.join(per_experiment_directory, path_group)

                if self.per_group_data[group_data][3]:
                    # path ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant
                    error_msg, path_group_per_participant = create_directory(
                        path_per_group, self.get_input_data("per_participant_directory"))
                    if error_msg != "":
                        return error_msg
                    # ex. /NES_EXPORT/Experiment_data/Group_XXX/
                    export_directory_group = path.join(export_directory_base, path_group)
                    # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant
                    export_directory_group_per_participant = path.join(export_directory_group,
                                                                       self.get_input_data("per_participant_directory"))

                    for patient_id in self.get_participant_list(group_data):
                        participant_code = Patient.objects.filter(id=patient_id).values('code')[0]['code']
                        # ex. Participant_P123
                        path_participant = prefix_filename_participant + str(participant_code)

                        for questionnaire_code in self.get_per_participant_data(participant_code):
                            if self.participants_per_experiment_questionnaire[questionnaire_code]:
                                if patient_id in self.participants_per_experiment_questionnaire[questionnaire_code]:
                                    # print(participant, questionnaire)
                                    questionnaire_id = self.get_questionnaire_id_from_code(questionnaire_code)
                                    # seleciona os participantes dos questionnarios de experimentos
                                    for questionnaire in self.get_input_data('questionnaires_from_experiments'):
                                        if questionnaire_id == questionnaire['id']:
                                            questionnaire_title = self.redefine_questionnaire_title(questionnaire['questionnaire_name'])
                                            # ex. Users/.../Experiment_data/Group_xxx/Per_participant/Participant_P123/
                                            error_msg, complete_group_participant_directory = create_directory(
                                                path_group_per_participant,path_participant)
                                            if error_msg != "":
                                                return error_msg

                                            export_filename = "%s_%s_%s.csv" % (str(participant_code), str(questionnaire_code),
                                                                                questionnaire_title)

                                            header = self.get_header_questionnaire(questionnaire_id)

                                            per_participant_rows = [header]

                                            if self.get_input_data('participants')[0]['output_list']:
                                                header = header[0:len(header)-1]
                                                participant_list = [patient_id]
                                                # get fields from patient 
                                                export_participant_row = self.process_participant_data(
                                                        self.get_input_data('participants'), participant_list)

                                                for field in export_participant_row[0]:
                                                    header.append(field)
                                                per_participant_rows = [header]
                                                export_fields_row = self.merge_participant_data_per_participant_process(
                                                    questionnaire_code, participant_code, export_participant_row)
                                                for field in export_fields_row:
                                                    per_participant_rows.append(field)
                                            else:
                                                fields_rows = self.get_per_participant_data(participant_code,
                                                                                            questionnaire_code)
                                                for fields in fields_rows:
                                                    per_participant_rows.append(fields)
                                            # path ex. Users/.../Group_xxx/Per_participant/Per_participant
                                            # /Participant_P123/P123_Q123_aaa.csv
                                            complete_filename = path.join(complete_group_participant_directory,
                                                                          export_filename)

                                            save_to_csv(complete_filename, per_participant_rows)
                                            # path ex.NES_EXPORT/Per_experiment/Per_participant/Per_participant/Participant_P123
                                            export_directory = path.join(export_directory_group_per_participant,
                                                                         path_participant)

                                            self.files_to_zip_list.append([complete_filename, export_directory])
        return error_msg

    def handle_exported_field(self, field):
        if field is None:
            result = ''
        elif isinstance(field, bool):
            result = _('Yes') if field else _('No')
        else:
            result = smart_str(field)
        return result

    def get_headers_and_fields(self, output_list):
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

    def process_participant_data(self, participants, participants_list):
        export_rows_participants = []

        for participant in participants:
            headers, fields = self.get_headers_and_fields(participant["output_list"])

            model_to_export = getattr(modules['patient.models'], 'Patient')

            db_data = model_to_export.objects.filter(id__in=participants_list).values_list(*fields).extra(
                order_by=['id'])

            export_rows_participants = [headers]

            # transform data
            for record in db_data:
                export_rows_participants.append([self.handle_exported_field(field) for field in record])

        return export_rows_participants

    def process_participant_filtered_data(self, participants_filtered_list, base_export_directory, base_directory):
        error_msg = ""

        self.set_participants_filtered_data(participants_filtered_list)
        participants_input_data = self.get_input_data("participants")
        participants_list = (self.get_participants_filtered_data())
        if participants_input_data[0]["output_list"] and participants_list:

            export_rows_participants = self.process_participant_data(participants_input_data, participants_list)

            export_filename = "%s.csv" % self.get_input_data('participants')[0]["output_filename"]  # "export.csv"

            complete_filename = path.join(base_export_directory, export_filename)

            self.files_to_zip_list.append([complete_filename, base_directory])

            with open(complete_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as csv_file:
                export_writer = writer(csv_file)
                for row in export_rows_participants:
                    export_writer.writerow(row)

        # process  diagnosis file
        diagnosis_input_data = self.get_input_data("diagnosis")

        if diagnosis_input_data[0]['output_list'] and participants_list:
            export_rows_diagnosis = self.process_participant_data(diagnosis_input_data, participants_list)

            export_filename = "%s.csv" % self.get_input_data('diagnosis')[0]["output_filename"]  # "export.csv"

            complete_filename = path.join(base_export_directory, export_filename)

            # files_to_zip_list.append(complete_filename)
            self.files_to_zip_list.append([complete_filename, base_directory])

            with open(complete_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as csv_file:
                export_writer = writer(csv_file)
                for row in export_rows_diagnosis:
                    export_writer.writerow(row)

        return error_msg

    def process_experiment_data(self, group_list, language_code):
        error_msg = ""
        # process of filename for experiment resume
        for group_data in group_list:
            group = get_object_or_404(Group, pk=group_data)

        study = group.experiment.research_project
        experiment = group.experiment
        experiment_resume_header = 'Study' + '\t' + 'Study description' + '\t' + 'Start date' + '\t' + \
                                   'End date' + '\t' + 'Experiment' + '\t' + 'Experiment description' + '\t' \
                                   + 'Data aquisition concluded' + "\n"
        experiment_resume = study.title + '\t' + study.description + '\t' + str(study.start_date) + '\t' + \
                            str(study.end_date) + '\t' + experiment.title + '\t' + experiment.description \
                            + '\t' + str(experiment.data_acquisition_is_concluded) + "\n"

        filename_experiment_resume = "%s.csv" % "Experiment"
        base_export_directory = self.get_export_directory()
        # path ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data
        experiment_resume_directory = path.join(base_export_directory, self.get_input_data("experiment_data_directory"))
        # User/.../qdc/media/.../NES_EXPORT/Experiment_data/Experiment.csv
        complete_filename_experiment_resume = path.join(experiment_resume_directory, filename_experiment_resume)
        # /NES_EXPORT/
        base_directory = self.get_input_data("base_directory")
        # path ex. NES_EXPORT/Experiment_data
        export_experiment_resume_directory = path.join(base_directory, self.get_input_data("experiment_data_directory"))
        self.files_to_zip_list.append([complete_filename_experiment_resume,
                                         export_experiment_resume_directory])

        with open(complete_filename_experiment_resume.encode('utf-8'), 'w', newline='',
                  encoding='UTF-8') as csv_file:
            csv_file.writelines(experiment_resume_header)
            csv_file.writelines(experiment_resume)

        # process of filename for description of each group
        for group_data in group_list:
            group = get_object_or_404(Group, pk=group_data)
            if group.experimental_protocol:
                experimental_protocol_description = get_experimental_protocol_description(
                    group.experimental_protocol, language_code)
                group_resume = "Group name: " + group.title + "\n" + "Group description: " + group.description \
                               + "\n"
                group_directory_name = 'Group_' + group.title
                filename_group_for_export = "%s.txt" % "Experimental_protocol_description"
                # path ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/
                group_file_directory = path.join(experiment_resume_directory, group_directory_name)
                # path ex. /NES_EXPORT/Experiment_data/Group_xxxx/
                export_group_directory = path.join(export_experiment_resume_directory, group_directory_name)
                # path ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/Experimental_protocol_description.txt
                complete_group_filename = path.join(group_file_directory, filename_group_for_export)
                self.files_to_zip_list.append([complete_group_filename, export_group_directory])

                with open(complete_group_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as txt_file:
                    txt_file.writelines(group_resume)
                    txt_file.writelines(experimental_protocol_description)

                # process participant/diagnosis per Participant of each group
                participant_group_list = []
                subject_of_group = SubjectOfGroup.objects.filter(group=group)
                for subject in subject_of_group:
                    participant_group_list.append(subject.subject.patient_id)

                if participant_group_list:
                    self.process_participant_filtered_data(participant_group_list, group_file_directory,
                                                           export_group_directory)

        return error_msg

    def find_duplicates(self, fill_list1, fill_list2):

        line1 = fill_list1[1]
        line2 = fill_list2[1]

        index = 0
        total = len(line1)

        duplicate_list = []

        while index != total:
            if line1[index] != line2[index]:
                duplicate_list.append(index)
            index += 1

        return duplicate_list

    def redefine_header_and_fields(self, questionnaire_id, header_filtered, fields):

        header = self.questionnaires_data[questionnaire_id]["header"]
        fields_saved = self.questionnaires_data[questionnaire_id]["fields"]

        new_header = []
        new_fields = []

        for item in fields:
            new_header.append(header[fields.index(item)])
            new_fields.append(fields_saved[fields.index(item)])

            if item in header_filtered:
                new_header.append(header[fields.index(item)])
                new_fields.append(fields_saved[fields.index(item)])

        self.questionnaires_data[questionnaire_id]["header"] = new_header
        self.questionnaires_data[questionnaire_id]["fields"] = new_fields

    def get_response_type(self):

        response_type = self.get_input_data("response_type")

        if not response_type:
            response_type = ["short"]

        return response_type

    def get_heading_type(self):

        heading_type = self.get_input_data("heading_type")

        if not heading_type:
            heading_type = ["code"]

        return heading_type

    def define_questionnaire(self, questionnaire, questionnaire_lime_survey, group_id):
        """
        :param questionnaire:
        :return: fields_description: (list)

        """
        # questionnaire exportation - evaluation questionnaire
        # print("define_questionnaire:  ")
        questionnaire_id = questionnaire["id"]
        language = questionnaire["language"]

        response_type = self.get_response_type()

        headers, fields = self.set_questionnaire_header_and_fields(questionnaire)

        export_rows = []

        # verify if Lime Survey is running
        limesurvey_available = is_limesurvey_available(questionnaire_lime_survey)

        if group_id != "":
            questionnaire_exists = False
            survey_code = Survey.objects.filter(lime_survey_id=questionnaire_id).values('code')[0]['code']
            questionnaire_responses = self.get_experiment_questionnaire_response_per_questionnaire(survey_code,
                                                                                                   group_id)

            if questionnaire_responses:
                questionnaire_exists = True
        else:
            questionnaire_exists = QuestionnaireResponse.objects.filter(
            survey__lime_survey_id=questionnaire_id).exists()
            # filter data (participants)
            questionnaire_responses = QuestionnaireResponse.objects.filter(survey__lime_survey_id=questionnaire_id)

            #  include new filter that come from advanced search
            filtered_data = self.get_participants_filtered_data()
            questionnaire_responses = questionnaire_responses.filter(patient_id__in=filtered_data)

        if questionnaire_exists and limesurvey_available:

            # read all data for questionnaire_id from LimeSurvey
            # responses_string = questionnaire_lime_survey.get_responses(questionnaire_id, language)
            responses_string1 = questionnaire_lime_survey.get_responses(questionnaire_id, language, response_type[0])
            # fill_list = perform_csv_response(responses_string)
            fill_list1 = perform_csv_response(responses_string1)

            # read "long" information, if necessary
            if len(response_type) > 1:
                responses_string2 = questionnaire_lime_survey.get_responses(questionnaire_id, language,
                                                                            response_type[1])
                fill_list2 = perform_csv_response(responses_string2)
            else:
                fill_list2 = fill_list1

            # filter fields
            subscripts = []
            # find fields that must be used for this process
            # for field in fields:
            #     if field in fill_list[0]:
            #         subscripts.append(fill_list[0].index(field))

            for field in fields:
                if field in fill_list1[0]:
                    subscripts.append(fill_list1[0].index(field))

            data_from_lime_survey = {}

            # do not consider first line, because it is header TODO: verificar token_id
            # for line in fill_list[1:len(fill_list) - 1]:
            #     token_id = int(line[fill_list[0].index("id")])
            #     data_fields_filtered = [line[index] for index in subscripts]
            #     data_from_lime_survey[token_id] = data_fields_filtered

            duplicate_indices = self.find_duplicates(fill_list1, fill_list2)

            line_index = 1
            line_total = len(fill_list1) - 1
            header_filtered = set()
            while line_index < line_total:
                data_fields_filtered = []
                line1 = fill_list1[line_index]
                line2 = fill_list2[line_index]

                for index in subscripts:
                    data_fields_filtered.append(line1[index])
                    if index in duplicate_indices:
                        data_fields_filtered.append(line2[index])
                        header_filtered.add(fill_list1[0][index])

                token = line1[fill_list1[0].index("token")]
                data_from_lime_survey[token] = list(data_fields_filtered)
                line_index += 1

            # filter data (participants)
            # questionnaire_responses = QuestionnaireResponse.objects.filter(survey__lime_survey_id=questionnaire_id)

            #  include new filter that come from advanced search
            # filtered_data = self.get_participants_filtered_data()
            # questionnaire_responses = questionnaire_responses.filter(patient_id__in=filtered_data)

            # process data fields

            # data_rows = []
            self.update_questionnaire_rules(questionnaire_id)

            # for each questionnaire_id from ResponseQuestionnaire from questionnaire_id
            for questionnaire_response in questionnaire_responses:

                # transform data fields
                # include new fieldsm

                if group_id != "":
                    patient = Patient.objects.filter(subject__subjectofgroup=questionnaire_response.subject_of_group)[0]
                    patient_id = patient.id
                    lime_survey_id = questionnaire_id
                    patient_code = patient.code
                    token_id = questionnaire_response.token_id
                else:
                    patient_id = questionnaire_response.patient_id
                    survey_code = questionnaire_response.survey.code
                    lime_survey_id = questionnaire_response.survey.lime_survey_id
                    patient_code = questionnaire_response.patient.code
                    token_id = questionnaire_response.token_id

                token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id, "token")

                if token in data_from_lime_survey:

                    lm_data_row = data_from_lime_survey[token]

                    data_fields = [smart_str(data) for data in lm_data_row]

                    transformed_fields = self.transform_questionnaire_data(patient_id, data_fields)
                    # data_rows.append(transformed_fields)

                    if len(transformed_fields) > 0:
                        export_rows.append(transformed_fields)

                        if group_id != "":
                            identification = self.per_group_data[group_id][3][survey_code][0]['identification']

                        # self.include_in_per_participant_data([transformed_fields],
                        #                                      questionnaire_response.patient_id,
                        #                                      questionnaire_id)
                        self.include_questionnaire_code_and_id(survey_code, lime_survey_id)

                        self.include_in_per_participant_data([transformed_fields], patient_code, survey_code)

                        self.include_participant_per_questionnaire(token_id, survey_code)

            self.redefine_header_and_fields(questionnaire_id, header_filtered, fields)
        header = self.get_header_questionnaire(questionnaire_id)

        export_rows.insert(0, header)
        return export_rows


def define_experiment_questionnaire(self, questionnaire, questionnaire_lime_survey):
    """
    :param questionnaire:
    :return: fields_description: (list)
    """
    # questionnaire exportation - evaluation questionnaire
    # print("define_questionnaire:  ")
    questionnaire_id = questionnaire["id"]
    language = questionnaire["language"]

    response_type = self.get_response_type()

    headers, fields = self.set_questionnaire_header_and_fields(questionnaire)

    export_rows = []

    # verify if Lime Survey is running
    limesurvey_available = is_limesurvey_available(questionnaire_lime_survey)

    return export_rows
