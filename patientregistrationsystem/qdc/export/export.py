from django.conf import settings
from django.core.files import File
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _

import json
from datetime import datetime
from os import path, makedirs
from csv import writer, reader
from io import StringIO
import collections
import re
from operator import itemgetter

from patient.models import Patient, QuestionnaireResponse

from survey.abc_search_engine import Questionnaires
from survey.views import is_limesurvey_available

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


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def save_to_csv(complete_filename, rows_to_be_saved):
    """
    :param complete_filename: filename and directory structure where file is going to be saved
    :param rows_to_be_saved: list of rows that are going to be written on the file
    :return:
    """
    with open(complete_filename, 'w', newline='', encoding='UTF-8') as csv_file:
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

    if not path.exists(basedir):
        return _("Base path does not exist"), complete_path

    complete_path = path.join(basedir, path_to_create)

    if not path.exists(complete_path):
        makedirs(complete_path)

    return "", complete_path


def is_patient_active(subject_id):
    response = False

    if is_number(subject_id):
        patient_id = int(float(subject_id))

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

        questionnaire_id = 0
        self.files_to_zip_list = []
        # self.headers = []
        # self.fields = []
        self.base_directory_name = path.join(settings.MEDIA_ROOT, "export")
        # self.directory_base = self.base_directory_name
        self.set_directory_base(user_id, export_id)
        self.base_export_directory = ""
        self.user_name = None
        self.input_data = {}
        self.per_participant_data = {}
        self.questionnaires_data = {}
        self.root_directory = ""

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

    def read_questionnaire_from_lime_survey(self, questionnaire_id, token, language, questionnaire_lime_survey, fields):
        """
        :param questionnaire_id:
        :param token:
        :param language:
        :param questionnaire_lime_survey:
        :param fields:
        :return: header, formatted according to fields
                 data_rows, formatted according to fields
                 if error, both data are []
        """

        # # for each questionnaire response
        # token = '2gyciirwrpr54wj'

        responses_string = questionnaire_lime_survey.get_responses_by_token(questionnaire_id, token, language)

        fill_list = perform_csv_response(responses_string)
        # fill_list[0] -> header
        # fill_list[1:len(fill_list)] -> data

        data_rows = []
        header = []

        if "subjectid" in fill_list[0]:

            subject_id = fill_list[0].index("subjectid")

            subscripts = []
            # find fields that must be used for this process
            for field in fields:
                if field in fill_list[0]:
                    subscripts.append(fill_list[0].index(field))

            header = [smart_str(fill_list[0][index]) for index in subscripts]

            # do not consider first line, because it is header
            for line in fill_list[1:len(fill_list) - 1]:
                if is_patient_active(line[subject_id]):
                    # data_line = []
                    # for index in subscripts:
                    #     data_line.append([smart_str(line[index])])
                    #
                    # data_rows.append([data_line])
                    # print(data_rows)
                    data_rows.append([smart_str(line[index]) for index in subscripts])

        return header, data_rows

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

        # for each field, verify the question description
        # get title
        questionnaire_title = questionnaire_lime_survey.get_survey_title(questionnaire_id)

        # get fields description
        questionnaire_questions = questionnaire_lime_survey.list_questions(questionnaire_id, 0)

        for question in questionnaire_questions:

            properties = questionnaire_lime_survey.get_question_properties(question, language)

            if properties['title'] in fields_cleared:

                # cleaning the question field
                properties['question'] = re.sub('{.*?}', '', re.sub('<.*?>', '', properties['question']))
                properties['question'] = properties['question'].replace('&nbsp;', '').strip()

                question_to_list = [smart_str(questionnaire_id), smart_str(questionnaire_title),
                                    smart_str(properties['title']), smart_str(properties['question'])]

                options_list = []

                if isinstance(properties['answeroptions'], dict):

                    options = collections.OrderedDict(sorted(properties['answeroptions'].items()))

                    column_scale = ['']
                    if isinstance(properties['attributes_lang'], dict):
                        column_scale = [attribute for attribute in sorted(properties['attributes_lang'].values())]

                    for option_key, option_values in options.items():
                        column_title = column_scale[option_values['scale_id']]
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

        return questionnaire_explanation_fields_list

    def define_questionnaire(self, questionnaire, questionnaire_lime_survey):
        """
        :param questionnaire:
        :return: fields_description: (list)

        """
        # questionnaire exportation - evaluation questionnaire
        # print("define_questionnaire:  ")
        questionnaire_id = questionnaire["id"]
        language = questionnaire["language"]

        headers, fields = self.set_questionnaire_header_and_fields(questionnaire)

        export_rows = [headers]

        # verify if Lime Survey is running
        limesurvey_available = is_limesurvey_available(questionnaire_lime_survey)
        questionnaire_exists = QuestionnaireResponse.objects.filter(survey__lime_survey_id=questionnaire_id).exists()

        if questionnaire_exists and limesurvey_available:

            questionnaire_responses = QuestionnaireResponse.objects.filter(survey__lime_survey_id=questionnaire_id)

            # for each questionnaire_id from ResponseQuestionnaire from questionnaire_id
            for questionnaire_response in questionnaire_responses:

                survey_completed = (questionnaire_lime_survey.get_participant_properties(
                    questionnaire_response.survey.lime_survey_id,
                    questionnaire_response.token_id, "completed") != "N")

                if survey_completed:
                    token = questionnaire_lime_survey.get_participant_properties(
                        questionnaire_response.survey.lime_survey_id, questionnaire_response.token_id, "token")

                    header, data_rows = self.read_questionnaire_from_lime_survey(
                        questionnaire_response.survey.lime_survey_id,
                        token, language,
                        questionnaire_lime_survey,
                        fields)

                    if len(data_rows) > 0:
                        export_rows.extend(data_rows)

                        self.include_in_per_participant_data(data_rows,
                                                             questionnaire_response.patient_id,
                                                             questionnaire_id)

        return export_rows

    def process_per_questionnaire(self):

        error_msg = ""
        # and save per_participant data
        if self.get_input_data("export_per_questionnaire"):
            per_questionnaire_directory = self.get_input_data("per_questionnaire_directory")
            error_msg, path_per_questionnaire = create_directory(self.get_export_directory(),
                                                                 per_questionnaire_directory)
            if error_msg != "":
                return error_msg

            export_per_questionnaire_directory = path.join(self.get_input_data("base_directory"),
                                                           self.get_input_data("per_questionnaire_directory"))

        questionnaire_lime_survey = Questionnaires()

        for questionnaire in self.get_input_data("questionnaires"):

            questionnaire_id = questionnaire["id"]
            language = questionnaire["language"]

            print(questionnaire_id)

            # per_participant_data is updated by define_questionnaire method
            fields_description = self.define_questionnaire(questionnaire, questionnaire_lime_survey)

            fields = self.get_questionnaire_fields(questionnaire_id)

            questionnaire_fields = self.create_questionnaire_explanation_fields_file(questionnaire_id, language,
                                                                                     questionnaire_lime_survey,
                                                                                     fields)

            # create directory for questionnaire: <per_questionnaire>/<questionnaire_id>
            if self.get_input_data("export_per_questionnaire"):
                path_questionnaire = str(questionnaire_id)
                error_msg, export_path = create_directory(path_per_questionnaire, path_questionnaire)
                if error_msg != "":
                    return error_msg

                export_filename = "%s_%s.csv" % (questionnaire["prefix_filename_responses"], str(questionnaire_id))

                export_directory = path.join(export_per_questionnaire_directory, path_questionnaire)

                complete_filename = path.join(export_path, export_filename)

                save_to_csv(complete_filename, fields_description)

                self.files_to_zip_list.append([complete_filename, export_directory])

                export_filename = "%s_%s.csv" % (questionnaire["prefix_filename_fields"], str(questionnaire_id))

                complete_filename = path.join(export_path, export_filename)

                save_to_csv(complete_filename, questionnaire_fields)

                self.files_to_zip_list.append([complete_filename, export_directory])

        questionnaire_lime_survey.release_session_key()

        return error_msg
