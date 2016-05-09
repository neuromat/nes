# -*- coding: utf-8 -*-
import collections
import json
import re

from csv import writer, reader

from datetime import datetime

from django.conf import settings
from django.core.files import File
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.apps import apps

from io import StringIO

from operator import itemgetter

from os import path, makedirs

from patient.models import Patient, QuestionnaireResponse

from survey.abc_search_engine import Questionnaires
# from survey.models import Survey
from survey.views import is_limesurvey_available

import sys

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
    {"field": "participation_code", "header": {"code": "participation_code",
                                               "full": _("Participation code"),
                                               "abbreviated": _("Participation code")},
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


def get_questionnaire_language(questionnaire_lime_survey, questionnaire_id, language_code):

    language = DEFAULT_LANGUAGE
    # defining language to be showed
    languages = questionnaire_lime_survey.get_survey_languages(questionnaire_id)

    # language to be showed can be the base language, or...
    if "language" in languages:

        language = languages['language']

        # ...can be one of the additional languages
        if language.lower() != language_code.lower() and languages['additional_languages']:

            # search for the right language in addional languages,
            # considering that the LimeSurvey uses upper case in the two-letter language code, like en-US and pt-BR.
            additional_languages_list = languages['additional_languages'].split(' ')
            additional_languages_list_lower = [item.lower() for item in additional_languages_list]
            if language_code.lower() in additional_languages_list_lower:
                index = additional_languages_list_lower.index(language_code.lower())
                language = additional_languages_list[index]

    return language


class LogMessages:
    def __init__(self, user, file_name=path.join(settings.MEDIA_ROOT, "export_log")):
        self.user = user
        self.file_name = file_name

    def log_message(self, text, param1="", param2=""):
        current_time = datetime.now()

        text_message = "%s %s %s %s %s" % (smart_str(current_time), smart_str(self.user),
                                           smart_str(text), smart_str(param1), smart_str(param2))
        with open(self.file_name, "a", encoding='UTF-8') as f:
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
        self.questionnaires_data = {}
        self.root_directory = ""
        self.participants_filtered_data = []
        self.questionnaire_code_and_id = {}

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
        # headers_questionnaire format: dict {questinnaire_id: {header:[header]}}

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

    def update_questionnaire_rules(self, questionnaire_id):

        header = []
        fields = []

        heading_type = self.get_heading_type()

        for row in included_questionnaire_fields:
            header_translated = _(row["header"][heading_type])
            header.append(smart_str(header_translated))
            fields.append(smart_str(row["field"]))

        self.append_questionnaire_header_and_field(questionnaire_id, header, fields)

    def transform_questionnaire_data(self, subject_id, fields):

        for row in included_questionnaire_fields:

            model_db = apps.get_model(row["model"])

            model_data = model_db.objects.all()

            if model_data.filter(id=subject_id).exists():
                value = model_data.filter(id=subject_id).values_list(row["model_field"])[0][0]
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

# def read_questionnaire_from_lime_survey(self, questionnaire_id, token, language, questionnaire_lime_survey, fields):
    #     """
    #     :param questionnaire_id:
    #     :param token:
    #     :param language:
    #     :param questionnaire_lime_survey:
    #     :param fields:
    #     :return: header, formatted according to fields
    #              data_rows, formatted according to fields
    #              if error, both data are []
    #     """
    #
    #     # # for each questionnaire response
    #     # token = '2gyciirwrpr54wj'
    #
    #     responses_string = questionnaire_lime_survey.get_responses_by_token(questionnaire_id, token, language)
    #
    #     fill_list = perform_csv_response(responses_string)
    #     # fill_list[0] -> header
    #     # fill_list[1:len(fill_list)] -> data
    #
    #     data_rows = []
    #
    #     if "subjectid" in fill_list[0]:
    #
    #         subject_id = fill_list[0].index("subjectid")
    #
    #         subscripts = []
    #         # find fields that must be used for this process
    #         for field in fields:
    #             if field in fill_list[0]:
    #                 subscripts.append(fill_list[0].index(field))
    #
    #         # header = [smart_str(fill_list[0][index]) for index in subscripts]
    #         self.update_questionnaire_rules(questionnaire_id)
    #
    #         # do not consider first line, because it is header
    #         for line in fill_list[1:len(fill_list) - 1]:
    #             if is_patient_active(line[subject_id]):
    #                 # data_rows.append([data_line])
    #                 # print(data_rows)
    #                 fields = [smart_str(line[index]) for index in subscripts]
    #                 transformed_fields = self.transform_questionnaire_data(to_number(line[subject_id]), fields)
    #                 data_rows.append(transformed_fields)
    #
    #     return data_rows

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

    # def define_questionnaire(self, questionnaire, questionnaire_lime_survey):
    #     """
    #     :param questionnaire:
    #     :return: fields_description: (list)
    #
    #     """
    #     # questionnaire exportation - evaluation questionnaire
    #     # print("define_questionnaire:  ")
    #     questionnaire_id = questionnaire["id"]
    #     language = questionnaire["language"]
    #
    #     headers, fields = self.set_questionnaire_header_and_fields(questionnaire)
    #
    #     export_rows = []
    #
    #     # verify if Lime Survey is running
    #     limesurvey_available = is_limesurvey_available(questionnaire_lime_survey)
    #     questionnaire_exists = QuestionnaireResponse.objects.filter(survey__lime_survey_id=questionnaire_id).exists()
    #
    #     if questionnaire_exists and limesurvey_available:
    #
    #         questionnaire_responses = QuestionnaireResponse.objects.filter(survey__lime_survey_id=questionnaire_id)
    #
    #         # for each questionnaire_id from ResponseQuestionnaire from questionnaire_id
    #         for questionnaire_response in questionnaire_responses:
    #
    #             survey_completed = (questionnaire_lime_survey.get_participant_properties(
    #                 questionnaire_response.survey.lime_survey_id,
    #                 questionnaire_response.token_id, "completed") != "N")
    #
    #             if survey_completed:
    #                 token = questionnaire_lime_survey.get_participant_properties(
    #                     questionnaire_response.survey.lime_survey_id, questionnaire_response.token_id, "token")
    #
    #                 data_rows = self.read_questionnaire_from_lime_survey(
    #                     questionnaire_response.survey.lime_survey_id,
    #                     token, language,
    #                     questionnaire_lime_survey,
    #                     fields)
    #
    #                 if len(data_rows) > 0:
    #                     export_rows.extend(data_rows)
    #
    #                     self.include_in_per_participant_data(data_rows,
    #                                                          questionnaire_response.patient_id,
    #                                                          questionnaire_id)
    #
    #     header = self.get_header_questionnaire(questionnaire_id)
    #     export_rows.insert(0, header)
    #     return export_rows

    def process_per_questionnaire(self):

        error_msg = ""
        export_per_questionnaire_directory = ''
        export_metadata_directory = ''
        path_per_questionnaire = ''

        # and save per_participant data
        if self.get_input_data("export_per_questionnaire"):
            per_questionnaire_directory = self.get_input_data("per_questionnaire_directory")
            error_msg, path_per_questionnaire = create_directory(self.get_export_directory(),
                                                                 per_questionnaire_directory)
            if error_msg != "":
                return error_msg

            export_per_questionnaire_directory = path.join(self.get_input_data("base_directory"),
                                                           self.get_input_data("per_questionnaire_directory"))

            export_metadata_directory = path.join(self.get_input_data("base_directory"), metadata_directory)

        questionnaire_lime_survey = Questionnaires()

        for questionnaire in self.get_input_data("questionnaires"):

            questionnaire_id = questionnaire["id"]
            language = questionnaire["language"]

            print(questionnaire_id)

            # per_participant_data is updated by define_questionnaire method
            fields_description = self.define_questionnaire(questionnaire, questionnaire_lime_survey)

            # create directory for questionnaire: <per_questionnaire>/<q_code_title>
            if self.get_input_data("export_per_questionnaire") and (len(fields_description) > 1):
                # path_questionnaire = str(questionnaire_id)

                questionnaire_code = self.get_questionnaire_code_from_id(questionnaire_id)
                questionnaire_title = self.get_title_reduced(questionnaire_id=questionnaire_id)
                path_questionnaire = "%s_%s" % (str(questionnaire_code), questionnaire_title)
                error_msg, export_path = create_directory(path_per_questionnaire, path_questionnaire)
                if error_msg != "":
                    return error_msg

                export_filename = "%s_%s.csv" % (questionnaire["prefix_filename_responses"], str(questionnaire_code))

                export_directory = path.join(export_per_questionnaire_directory, path_questionnaire)

                complete_filename = path.join(export_path, export_filename)

                save_to_csv(complete_filename, fields_description)

                # create questionnaire fields file ("fields.csv")
                fields = self.get_questionnaire_fields(questionnaire_id)

                questionnaire_fields = self.create_questionnaire_explanation_fields_file(questionnaire_id, language,
                                                                                         questionnaire_lime_survey,
                                                                                         fields)

                self.files_to_zip_list.append([complete_filename, export_directory])

                export_filename = "%s_%s.csv" % (questionnaire["prefix_filename_fields"], str(questionnaire_code))

                export_directory = path.join(export_metadata_directory, path_questionnaire)

                complete_filename = path.join(export_path, export_filename)

                save_to_csv(complete_filename, questionnaire_fields)

                self.files_to_zip_list.append([complete_filename, export_directory])

        questionnaire_lime_survey.release_session_key()

        return error_msg

    def process_per_participant(self):

        error_msg = ''

        if self.get_input_data("export_per_participant"):

            per_participant_directory = self.get_input_data("per_participant_directory")

            error_msg, path_per_participant = create_directory(self.get_export_directory(), per_participant_directory)
            if error_msg != "":
                return error_msg

            prefix_filename_participant = "Participant_"
            export_directory_base = path.join(self.get_input_data("base_directory"),
                                              self.get_input_data("per_participant_directory"))
            # path_questionnaire = "Questionnaires"

            for participant_code in self.get_per_participant_data():

                path_participant = prefix_filename_participant + str(participant_code)
                error_msg, participant_path = create_directory(path_per_participant, path_participant)
                if error_msg != "":
                    return error_msg

                # error_msg, questionnaire_path = create_directory(participant_path, path_questionnaire)
                # if error_msg != "":
                #     return error_msg

                for questionnaire_code in self.get_per_participant_data(participant_code):
                    # print(participant, questionnaire)

                    questionnaire_id = self.get_questionnaire_id_from_code(questionnaire_code)

                    title = self.get_title_reduced(questionnaire_id=questionnaire_id)

                    export_filename = "%s_%s_%s.csv" % (str(participant_code), str(questionnaire_code), title)

                    header = self.get_header_questionnaire(questionnaire_id)

                    per_participant_rows = [header]

                    fields_rows = self.get_per_participant_data(participant_code, questionnaire_code)

                    for fields in fields_rows:
                        per_participant_rows.append(fields)

                    complete_filename = path.join(participant_path, export_filename)

                    save_to_csv(complete_filename, per_participant_rows)

                    export_directory = path.join(export_directory_base, path_participant)
                    # export_directory = path.join(export_directory, path_questionnaire)

                    self.files_to_zip_list.append([complete_filename, export_directory])

        return error_msg

    # def pre_processing(self):
    #
    #     error_msg = ""
    #     # and save per_participant data
    #
    #     questionnaire_lime_survey = Questionnaires()
    #
    #     for questionnaire in self.get_input_data("questionnaires"):
    #
    #         questionnaire_id = questionnaire["id"]
    #         language = questionnaire["language"]
    #
    #         print(questionnaire_id)
    #
    #         # per_participant_data is updated by define_questionnaire method
    #         fields_description = self.define_questionnaire2(questionnaire, questionnaire_lime_survey)
    #
    #     questionnaire_lime_survey.release_session_key()
    #
    #     return error_msg

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

    def define_questionnaire(self, questionnaire, questionnaire_lime_survey):
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
        questionnaire_exists = QuestionnaireResponse.objects.filter(survey__lime_survey_id=questionnaire_id).exists()

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
            questionnaire_responses = QuestionnaireResponse.objects.filter(survey__lime_survey_id=questionnaire_id)

            #  include new filter that come from advanced search
            filtered_data = self.get_participants_filtered_data()
            questionnaire_responses = questionnaire_responses.filter(patient_id__in=filtered_data)

            # process data fields

            # data_rows = []
            self.update_questionnaire_rules(questionnaire_id)

            # for each questionnaire_id from ResponseQuestionnaire from questionnaire_id
            for questionnaire_response in questionnaire_responses:

                # transform data fields
                # include new fields
                token = questionnaire_lime_survey.get_participant_properties(questionnaire_id,
                                                                             questionnaire_response.token_id,
                                                                             "token")
                if token in data_from_lime_survey:

                    lm_data_row = data_from_lime_survey[token]

                    data_fields = [smart_str(data) for data in lm_data_row]
                    transformed_fields = self.transform_questionnaire_data(questionnaire_response.patient_id,
                                                                           data_fields)
                    # data_rows.append(transformed_fields)

                    if len(transformed_fields) > 0:
                        export_rows.append(transformed_fields)

                        # self.include_in_per_participant_data([transformed_fields],
                        #                                      questionnaire_response.patient_id,
                        #                                      questionnaire_id)
                        self.include_questionnaire_code_and_id(questionnaire_response.survey.code,
                                                               questionnaire_response.survey.lime_survey_id)

                        self.include_in_per_participant_data([transformed_fields],
                                                             questionnaire_response.patient.code,
                                                             questionnaire_response.survey.code)

            self.redefine_header_and_fields(questionnaire_id, header_filtered, fields)
        header = self.get_header_questionnaire(questionnaire_id)

        export_rows.insert(0, header)
        return export_rows
