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
from experiment.models import QuestionnaireResponse as ExperimentQuestionnaireResponse, SubjectOfGroup, Group, \
    ComponentConfiguration, Questionnaire, DataConfigurationTree, EEGData, EEGSetting, EMGData, EMGSetting, TMSData, \
    TMSSetting, AdditionalData, DigitalGamePhaseData, Stimulus, TMSLocalizationSystem, GenericDataCollectionData
from experiment.views import get_block_tree, get_experimental_protocol_image, \
    get_description_from_experimental_protocol_tree, get_sensors_position

from survey.abc_search_engine import Questionnaires
from survey.views import is_limesurvey_available, get_questionnaire_language


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
        self.per_participant_data_from_experiment = {}
        self.participants_per_entrance_questionnaire = {}
        self.participants_per_experiment_questionnaire = {}
        self.questionnaires_data = {}
        self.questionnaires_experiment_data = {}
        self.questionnaires_experiment_responses = {}
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

    def set_questionnaire_header_and_fields(self, questionnaire, entrance_questionnaire):

        headers = []
        fields = []

        questionnaire_id = questionnaire["id"]
        for output_list in questionnaire["output_list"]:
            if output_list["field"]:
                headers.append(output_list["header"])
                fields.append(output_list["field"])

        if entrance_questionnaire:
            if questionnaire_id not in self.questionnaires_data:
                self.questionnaires_data[questionnaire_id] = {}

            self.questionnaires_data[questionnaire_id]["header"] = headers
            self.questionnaires_data[questionnaire_id]["fields"] = fields

        else:
            if questionnaire_id not in self.questionnaires_experiment_data:
                self.questionnaires_experiment_data[questionnaire_id] = {}

            self.questionnaires_experiment_data[questionnaire_id]["header"] = headers
            self.questionnaires_experiment_data[questionnaire_id]["fields"] = fields

        return headers, fields

    def set_questionnaire_experiment_header_and_fields(self, questionnaire_id, questionnaire):

        headers = []
        fields = []

        for output_list in questionnaire["output_list"]:
            if output_list["field"]:
                headers.append(output_list["header"])
                fields.append(output_list["field"])

        if questionnaire_id not in self.questionnaires_experiment_data:
            self.questionnaires_experiment_data[questionnaire_id] = {}

        self.questionnaires_experiment_data[questionnaire_id]["header"] = headers
        self.questionnaires_experiment_data[questionnaire_id]["header_questionnaire"] = headers
        self.questionnaires_experiment_data[questionnaire_id]["fields"] = fields

        return headers, fields

    def append_questionnaire_header_and_field(self, questionnaire_id, header, fields):
        # only one header, field instance
        for field in fields:
            if self.get_input_data('questionnaires'):
                if field not in self.questionnaires_data[questionnaire_id]["fields"]:
                    self.questionnaires_data[questionnaire_id]["header"].append(header[fields.index(field)])
                    self.questionnaires_data[questionnaire_id]["fields"].append(field)
            if self.get_input_data('questionnaires_from_experiment'):
                if field not in self.questionnaires_experiment_data[questionnaire_id]["fields"]:
                    self.questionnaires_experiment_data[questionnaire_id]["header"].append(header[fields.index(field)])
                    self.questionnaires_experiment_data[questionnaire_id]["fields"].append(field)

    def append_questionnaire_experiment_header_and_field(self, questionnaire_id, header, fields):
        # only one header, field instance
        for field in fields:
            if field not in self.questionnaires_experiment_data[questionnaire_id]["fields"]:
                self.questionnaires_experiment_data[questionnaire_id]["header"].append(header[fields.index(field)])
                self.questionnaires_experiment_data[questionnaire_id]["header_questionnaire"].\
                    append(header[fields.index(field)])
                self.questionnaires_experiment_data[questionnaire_id]["fields"].append(field)

    def get_header_questionnaire(self, questionnaire_id):
        # headers_questionnaire format: dict {questionnaire_id: {header:[header]}}

        header = []
        if questionnaire_id in self.questionnaires_data:
            header = self.questionnaires_data[questionnaire_id]["header"]
        return header

    def get_header_experiment_questionnaire(self, questionnaire_id):
        # headers_questionnaire format: dict {questionnaire_id: {header:[header]}}

        header = []
        if questionnaire_id in self.questionnaires_experiment_data:
            header = self.questionnaires_experiment_data[questionnaire_id]["header"]
        return header

    def get_questionnaire_fields(self, questionnaire_id, entrance_questionnaire):
        # headers_questionnaire format: dict {questinnaire_id: {fields:[fields]}}

        fields = []
        if entrance_questionnaire:
            if questionnaire_id in self.questionnaires_data:
                fields = self.questionnaires_data[questionnaire_id]["fields"]
        if self.get_input_data('questionnaires_from_experiments'):
            if questionnaire_id in self.questionnaires_experiment_data:
                fields = self.questionnaires_experiment_data[questionnaire_id]["fields"]

        return fields

    def get_questionnaire_experiment_fields(self, questionnaire_id):
        # headers_questionnaire format: dict {questionnaire_id: {fields:[fields]}}
        questionnaire_id = str(questionnaire_id)
        fields = []
        if questionnaire_id in self.questionnaires_experiment_data:
            fields = self.questionnaires_experiment_data[questionnaire_id]["fields"]
        return fields

    def get_header_description(self, questionnaire_id, field, entrance_questionnaire):

        if entrance_questionnaire:
            index = self.questionnaires_data[questionnaire_id]["fields"].index(field)
            header_description = self.questionnaires_data[questionnaire_id]["header"][index]
        else:
            questionnaire_id = str(questionnaire_id)
            index = self.questionnaires_experiment_data[questionnaire_id]["fields"].index(field)
            header_description = self.questionnaires_experiment_data[questionnaire_id]["header"][index]

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

    def include_in_per_participant_data_from_experiment(self, to_be_included_list, participant_id, questionnaire_id,
                                                        token_id, step):
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
        if participant_id not in self.per_participant_data_from_experiment:
            self.per_participant_data_from_experiment[participant_id] = {}

        if questionnaire_id not in self.per_participant_data_from_experiment[participant_id]:
            self.per_participant_data_from_experiment[participant_id][questionnaire_id] = {}

        if token_id not  in self.per_participant_data_from_experiment[participant_id][questionnaire_id]:
            self.per_participant_data_from_experiment[participant_id][questionnaire_id][token_id] = {}
            self.per_participant_data_from_experiment[participant_id][questionnaire_id][token_id]['step'] = step
            self.per_participant_data_from_experiment[participant_id][questionnaire_id][token_id][
                'questionnaire_response'] = []

        for element in to_be_included_list:
            self.per_participant_data_from_experiment[participant_id][questionnaire_id][token_id][
                'questionnaire_response'].append(element)

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
        header_step_list = ['Step', 'Step identification', 'Path questionnaire', 'Data completed']
        for group_id in group_list:
            group = get_object_or_404(Group, pk=group_id)
            title = group.title
            description = group.description
            if group_id not in self.per_group_data:
                self.per_group_data[group_id] = {}
            self.per_group_data[group_id]['group']= {
                'title': title,
                'description': description,
                'directory': '',
                'export_directory': '',
                'questionnaire_data_directory': '',
                'questionnaire_data_export_directory': '',
                'questionnaire_metadata_directory': '',
                'questionnaire_metadata_export_directory': '',
                'participant_data_directory': '',
                'participant_data_export_directory': '',
            }

            participant_group_list = Patient.objects.filter(subject__subjectofgroup__group=group).values('id')
            self.per_group_data[group_id]['participant_list'] = []
            for participant in participant_group_list:
                self.per_group_data[group_id]['participant_list'].append(participant)

            self.per_group_data[group_id]['data_per_participant'] = {}
            self.per_group_data[group_id]['questionnaires_per_group'] = {}
            if group.experimental_protocol is not None:
                if self.get_input_data('questionnaires_from_experiments'):
                    # questionnaire_per_group = {}
                    # questionnaire_response_list = {}
                    for path_experiment in create_list_of_trees(group.experimental_protocol, "questionnaire"):
                        path_questionnaire = ''
                        size = len(path_experiment[0])
                        step = 1
                        while step < size:
                            path_questionnaire += path_experiment[0][step] + "/"
                            step += 2
                        questionnaire_configuration = get_object_or_404(ComponentConfiguration, pk=path_experiment[-1][0])
                        questionnaire = Questionnaire.objects.get(id=questionnaire_configuration.component.id)
                        questionnaire_id = questionnaire.survey.lime_survey_id
                        questionnaire_code = questionnaire.survey.code
                        self.include_questionnaire_code_and_id(questionnaire_code, str(questionnaire_id))
                        configuration_tree_list = DataConfigurationTree.objects.filter(
                            component_configuration=questionnaire_configuration)

                        for data_configuration_tree in configuration_tree_list:
                            experiment_questionnaire_response_list = ExperimentQuestionnaireResponse.objects.filter(
                                data_configuration_tree_id=data_configuration_tree.id)

                            for questionnaire_response in experiment_questionnaire_response_list:
                                token_id = questionnaire_response.token_id
                                # completed = surveys.get_participant_properties(questionnaire_id, token_id, "completed")
                                completed =True
                                # carrega dados de questionarios completos
                                # if completed is not None and completed != "N" and completed != "":
                                if completed:
                                    subject_code = questionnaire_response.subject_of_group.subject.patient.code
                                    step_number = path_experiment[0][4]
                                    path_questionnaire = path_questionnaire
                                    step_identification = questionnaire_configuration.component.identification
                                    protocol_step_list = [header_step_list, [step_number, step_identification, path_questionnaire, completed]]
                                    questionnaire_response_dic = {
                                        'token_id': token_id,
                                        'questionnaire_id': questionnaire_id,
                                        'questionnaire_code': questionnaire_code,
                                        'data_configuration_tree_id': data_configuration_tree.id,
                                        'subject_id': questionnaire_response.subject_of_group.subject.patient.id,
                                        'subject_code': subject_code,
                                        'protocol_step_list': protocol_step_list,
                                        'response_list': []
                                    }

                                    if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                        self.per_group_data[group_id]['data_per_participant'][subject_code] = {}
                                        self.per_group_data[group_id]['data_per_participant'][subject_code][
                                            'token_list'] = []

                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'token_list'].append(questionnaire_response_dic)

                                    if questionnaire_id not in self.per_group_data[group_id]['questionnaires_per_group']:
                                        self.per_group_data[group_id]['questionnaires_per_group'][questionnaire_id] = {
                                            'questionnaire_code': questionnaire_code,
                                            'token_list': []
                                        }

                                    if token_id not in self.per_group_data[group_id]['questionnaires_per_group'][questionnaire_id]['token_list']:
                                        self.per_group_data[group_id]['questionnaires_per_group'][questionnaire_id][
                                            'token_list'].append(questionnaire_response_dic)

                    surveys.release_session_key()

                if self.get_input_data('component_list')['per_additional_data']:
                    subject_of_group = SubjectOfGroup.objects.filter(group=group)
                    additional_data_list = AdditionalData.objects.filter(subject_of_group=subject_of_group)
                    if additional_data_list:
                        component_configuration_list = create_list_of_trees(group.experimental_protocol, "")
                        protocol_step_dic = {}
                        for component_configuration in component_configuration_list:
                            component_configuration_id = component_configuration[0][0]
                            component_type = ComponentConfiguration.objects.filter(
                                id=component_configuration_id)[0].component.component_type
                            protocol_step_dic[component_configuration_id] = {
                                'step_number': component_configuration[0][-1],
                                'component_type': component_type
                            }

                    for additional_data in additional_data_list:
                        subject_code = additional_data.subject_of_group.subject.patient.code
                        if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                            self.per_group_data[group_id]['data_per_participant'][subject_code] = {}
                        if 'additional_data' not in self.per_group_data[group_id]['data_per_participant'][subject_code]:
                            self.per_group_data[group_id]['data_per_participant'][subject_code]['additional_data'] = []

                        step_number = 0
                        component_type = 'root'

                        if additional_data.data_configuration_tree_id:
                            component_configuration_id = DataConfigurationTree.objects.filter(
                                id=additional_data.data_configuration_tree_id).values('component_configuration_id')[0][
                                'component_configuration_id']
                            step_number = protocol_step_dic[component_configuration_id]['step_number']
                            component_type = protocol_step_dic[component_configuration_id]['component_type']

                        self.per_group_data[group_id]['data_per_participant'][subject_code]['additional_data'].append({
                            'description': additional_data.description,
                            'additional_file_name': additional_data.file.name,
                            'step_number': step_number,
                            'component_type': component_type,
                            'directory_step_name': "Step_" + str(step_number) + "_" + component_type.upper()
                        })

                if self.get_input_data('component_list')['per_eeg_raw_data'] or \
                        self.get_input_data('component_list')['per_eeg_nwb_data']:
                    for path_eeg_experiment in create_list_of_trees(group.experimental_protocol, "eeg"):
                        eeg_component_configuration = get_object_or_404(ComponentConfiguration,
                                                                        pk=path_eeg_experiment[-1][0])
                        component_step = eeg_component_configuration.component.component_type
                        step_number = path_eeg_experiment[-1][4]
                        step_identification = path_eeg_experiment[-1][3]

                        configuration_tree_list = DataConfigurationTree.objects.filter(
                            component_configuration=eeg_component_configuration)
                        for data_configuration_tree in configuration_tree_list:
                            eeg_data_list = EEGData.objects.filter(
                                data_configuration_tree_id=data_configuration_tree.id).distinct()
                            for eeg_data in eeg_data_list:
                                subject_code = eeg_data.subject_of_group.subject.patient.code

                                if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code] = {}
                                if 'eeg_data' not in self.per_group_data[group_id]['data_per_participant'][subject_code]:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code]['eeg_data'] = []

                                self.per_group_data[group_id]['data_per_participant'][subject_code]['eeg_data'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'setting_id': eeg_data.eeg_setting_id,
                                    'eeg_data_id': eeg_data.id,
                                    'data_configuration_tree_id': data_configuration_tree.id,
                                    'directory_step_name': "Step_" + str(step_number) + "_" + component_step.upper()
                                })

                if self.get_input_data('component_list')['per_emg_data']:
                    for path_emg_experiment in create_list_of_trees(group.experimental_protocol, "emg"):
                        emg_component_configuration = get_object_or_404(ComponentConfiguration,
                                                                        pk=path_emg_experiment[-1][0])
                        component_step = emg_component_configuration.component.component_type
                        step_number = path_emg_experiment[-1][4]
                        step_identification = path_emg_experiment[-1][3]

                        configuration_tree_list = DataConfigurationTree.objects.filter(
                            component_configuration=emg_component_configuration)
                        for data_configuration_tree in configuration_tree_list:
                            emg_data_list = EMGData.objects.filter(
                                data_configuration_tree_id=data_configuration_tree.id).distinct()
                            for emg_data in emg_data_list:
                                subject_code = emg_data.subject_of_group.subject.patient.code

                                if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code] = {}
                                if 'emg_data' not in self.per_group_data[group_id]['data_per_participant'][subject_code]:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code]['emg_data'] = []

                                self.per_group_data[group_id]['data_per_participant'][subject_code]['emg_data'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'setting_id': emg_data.emg_setting_id,
                                    'emg_data_id': emg_data.id,
                                    'data_configuration_tree_id': data_configuration_tree.id,
                                    'directory_step_name': "Step_" + str(step_number) + "_" + component_step.upper()
                                })

                if self.get_input_data('component_list')['per_tms_data']:
                    for path_tms_experiment in create_list_of_trees(group.experimental_protocol, "tms"):
                        tms_component_configuration = get_object_or_404(ComponentConfiguration,
                                                                        pk=path_tms_experiment[-1][0])
                        component_step = tms_component_configuration.component.component_type
                        step_number = path_tms_experiment[-1][4]
                        step_identification = path_tms_experiment[-1][3]

                        configuration_tree_list = DataConfigurationTree.objects.filter(
                            component_configuration=tms_component_configuration)
                        for data_configuration_tree in configuration_tree_list:
                            tms_data_list = TMSData.objects.filter(
                                data_configuration_tree_id=data_configuration_tree.id).distinct()
                            for tms_data in tms_data_list:
                                subject_code = tms_data.subject_of_group.subject.patient.code

                                if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code] = {}
                                if 'tms_data' not in self.per_group_data[group_id]['data_per_participant'][subject_code]:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code]['tms_data'] = []

                                self.per_group_data[group_id]['data_per_participant'][subject_code]['tms_data'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'setting_id': tms_data.tms_setting_id,
                                    'tms_data_id': tms_data.id,
                                    'data_configuration_tree_id': data_configuration_tree.id,
                                    'directory_step_name': "Step_" + str(step_number) + "_" + component_step.upper()
                                })

                if self.get_input_data('component_list')['per_goalkeeper_game_data']:
                    for path_goalkeeper_game_experiment in create_list_of_trees(group.experimental_protocol,
                                                                                "digital_game_phase"):
                        game_component_configuration = get_object_or_404(ComponentConfiguration,
                                                                         pk=path_goalkeeper_game_experiment[-1][0])
                        component_step = game_component_configuration.component.component_type
                        step_number = path_goalkeeper_game_experiment[-1][4]
                        step_identification = path_goalkeeper_game_experiment[-1][3]
                        configuration_tree_list = DataConfigurationTree.objects.filter(
                            component_configuration=game_component_configuration)

                        for data_configuration_tree in configuration_tree_list:
                            goalkeeper_game_data_list = DigitalGamePhaseData.objects.filter(
                                data_configuration_tree_id=data_configuration_tree.id)
                            for goalkeeper_game_data in goalkeeper_game_data_list:
                                subject_code = goalkeeper_game_data.subject_of_group.subject.patient.code

                                if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code] = {}

                                if 'goalkeeper_game_data' not in self.per_group_data[group_id]['data_per_participant'][
                                    subject_code]:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'goalkeeper_game_data'] = []

                                self.per_group_data[group_id]['data_per_participant'][subject_code][
                                    'goalkeeper_game_data'].append({
                                        'step_number': step_number,
                                        'step_identification': step_identification,
                                        'goalkeeper_game_data_id': goalkeeper_game_data.id,
                                        'data_configuration_tree_id': data_configuration_tree.id,
                                        'directory_step_name': "Step_" + str(step_number) + "_" + component_step.upper(),
                                        'goalkeeper_game_file': goalkeeper_game_data.file.name
                                    })

                if self.get_input_data('component_list')['per_stimulus_data']:
                    for path_stimulus_experiment in create_list_of_trees(group.experimental_protocol, "stimulus"):
                        stimulus_component_configuration = get_object_or_404(ComponentConfiguration,
                                                                             pk=path_stimulus_experiment[-1][0])
                        component_step = stimulus_component_configuration.component.component_type
                        step_number = path_stimulus_experiment[-1][4]
                        step_identification = path_stimulus_experiment[-1][3]

                        stimulus_data_list = Stimulus.objects.filter(id=stimulus_component_configuration.component.id)
                        for stimulus_data in stimulus_data_list:
                            if 'stimulus_data' not in self.per_group_data[group_id]:
                                self.per_group_data[group_id]['stimulus_data'] = []

                            self.per_group_data[group_id]['stimulus_data'].append({
                                'step_number': step_number,
                                'step_identification': step_identification,
                                'directory_step_name': "Step_" + str(step_number) + "_" + component_step.upper(),
                                'stimulus_file': stimulus_data.media_file.name
                            })

                if self.get_input_data('component_list')['per_generic_data']:
                    for path_generic_experiment in create_list_of_trees(group.experimental_protocol,
                                                                        "generic_data_collection"):
                        generic_component_configuration = get_object_or_404(ComponentConfiguration,
                                                                            pk=path_generic_experiment[-1][0])
                        component_step = generic_component_configuration.component.component_type
                        step_number = path_generic_experiment[-1][4]
                        step_identification = path_generic_experiment[-1][3]

                        configuration_tree_list = DataConfigurationTree.objects.filter(
                            component_configuration=generic_component_configuration)

                        for data_configuration_tree in configuration_tree_list:
                            generic_data_collection_list = GenericDataCollectionData.objects.filter(
                                data_configuration_tree_id=data_configuration_tree.id)
                            for generic_data_collection in generic_data_collection_list:
                                subject_code = generic_data_collection.subject_of_group.subject.patient.code

                                if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code] = {}

                                if 'generic_data_collection_data' not in self.per_group_data[
                                    group_id]['data_per_participant'][subject_code]:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'generic_data_collection_data'] = []

                                self.per_group_data[group_id]['data_per_participant'][subject_code]['generic_data_collection_data'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'generic_data_collection_data_id': generic_data_collection.id,
                                    'data_configuration_tree_id': data_configuration_tree.id,
                                    'directory_step_name': "Step_" + str(step_number) + "_" + component_step.upper(),
                                    'generic_data_collection_file': generic_data_collection.file.name
                                })

    def get_experiment_questionnaire_response_per_questionnaire(self, questionnaire_id, group_id):
        experiment_questionnaire_response = []
        if questionnaire_id in self.per_group_data[group_id]['questionnaires_per_group'][0]:
            questionnaire_data_list = self.per_group_data[group_id]['questionnaires_per_group'][0][questionnaire_id]
            questionnaire_list = questionnaire_data_list[1:len(questionnaire_data_list)]
            for element in questionnaire_list:
                for key in element:
                    questionnaire_response = ExperimentQuestionnaireResponse.objects.filter(token_id=key)
                    experiment_questionnaire_response.append(questionnaire_response[0])

        return experiment_questionnaire_response

    def get_participant_list(self, group_id):
        participant_list = []
        if self.per_group_data[group_id]['participant_list']:
            for element in self.per_group_data[group_id]['participant_list']:
                participant_list.append(element['id'])

        return participant_list

    def get_per_participant_data(self, participant=None, questionnaire=None):

        if questionnaire:
            return self.per_participant_data[participant][questionnaire]

        if participant:
            return self.per_participant_data[participant]

        return self.per_participant_data

    def get_per_participant_data_from_experiment(self, participant=None, questionnaire=None):

        if questionnaire:
            return self.per_participant_data_from_experiment[participant][questionnaire]

        if participant:
            return self.per_participant_data_from_experiment[participant]

        return self.per_participant_data_from_experiment

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

    def update_questionnaire_experiment_rules(self, questionnaire_id):

        header = []
        fields = []

        heading_type = self.get_heading_type()

        for row in included_questionnaire_fields:
            header_translated = _(row["header"][heading_type])
            header.append(smart_str(header_translated))
            fields.append(smart_str(row["field"]))

        self.append_questionnaire_experiment_header_and_field(questionnaire_id, header, fields)

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

    def get_title_experiment_questionnaire(self, questionnaire_id):

        title = ''
        questionnaires = self.get_input_data("questionnaires_from_experiments")
        for questionnaire in questionnaires:
            if questionnaire_id == questionnaires[questionnaire][0]['id']:
                title = questionnaires[questionnaire][0]['questionnaire_name']
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
            self.questionnaire_code_and_id[code] = str(questionnaire_id)

    def get_questionnaire_id_from_code(self, code):

        questionnaire_id = 0
        if code in self.questionnaire_code_and_id:
            questionnaire_id = self.questionnaire_code_and_id[code]

        return questionnaire_id

    def get_questionnaire_code_from_id(self, questionnaire_id):
        questionnaire_code = 0

        for code in self.questionnaire_code_and_id:
            if self.questionnaire_code_and_id[code] == str(questionnaire_id):
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

    def create_questionnaire_explanation_fields_file(self, questionnaire_id, language, questionnaire_lime_survey,
                                                     fields, entrance_questionnaire):

        """
        :param questionnaire_id:
        :param language:
        :param questionnaire_lime_survey:
        :param fields: fields from questionnaire that are to be exported
        :param entrance_questionnaire: boolean
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
                    description = self.get_header_description(questionnaire_id, field, entrance_questionnaire)
                    question_to_list = [smart_str(questionnaire_code), smart_str(questionnaire_title),
                                        smart_str(field), smart_str(description)]

                    questionnaire_explanation_fields_list.append(question_to_list)

        return questionnaire_explanation_fields_list

    def merge_participants_data_per_questionnaire_process(self, fields_description, participant_list):
        # get fields from patient
        export_participant_row = self.process_participant_data(self.get_input_data('participants'), participant_list)

        # Merge fields from questionnaires and patient
        export_fields_list = []
        export_row_list = []
        # Building the header
        export_row_list = fields_description[0][0:len(fields_description[0]) - 1]
        # for field in fields_description[0][0:len(fields_description[0]) - 1]:
        #     export_row_list.append(field)
        for field in export_participant_row[0]:
            export_row_list.append(field)
        export_fields_list.append(export_row_list)

        # Including the responses
        for fields in fields_description[1:fields_description.__len__()]:
            participation_code = fields[len(fields) - 1]
            export_row_list = []
            export_row_list = fields[0:len(fields) - 1]
            # for field in fields[0:len(fields) - 1]:
            #     export_row_list.append(field)
            for participant_fields in export_participant_row[1:export_participant_row.__len__()]:
                if participation_code == participant_fields[len(participant_fields) - 1]:
                    for field in participant_fields:
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
            fields_description = self.define_questionnaire(questionnaire, questionnaire_lime_survey)

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

                save_to_csv(complete_filename, fields_description)
                self.files_to_zip_list.append([complete_filename, export_directory])

                entrance_questionnaire = True

                # create questionnaire fields file ("fields.csv") - metadata directory
                fields = self.get_questionnaire_fields(questionnaire_id, entrance_questionnaire)
                questionnaire_fields = self.create_questionnaire_explanation_fields_file(questionnaire_id, language,
                                                                                         questionnaire_lime_survey,
                                                                                         fields, entrance_questionnaire)

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
            path_participant_data_directory = path.join(self.get_export_directory(),
                                                        self.get_input_data("participant_data_directory"))
            if not path.exists(path_participant_data_directory):
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
            export_per_questionnaire_directory = path.join(export_per_entrance_questionnaire_directory,
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
            fields_description = self.define_questionnaire(questionnaire, questionnaire_lime_survey)

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
                # path ex.
                # /qdc/media/export/#user/#export_instance/Participant_data/
                #                   Per_questionnaire/Q123_aaa/Responses_Q123.csv
                complete_filename = path.join(export_path, export_filename)

                # if self.get_input_data('participants')[0]['output_list']:
                #     participant_list = self.participants_per_entrance_questionnaire[questionnaire_code]
                #     export_fields_list = self.merge_participants_data_per_questionnaire_process(fields_description,
                #                                                                                 participant_list)
                #     save_to_csv(complete_filename, export_fields_list)
                # else:
                #     save_to_csv(complete_filename, fields_description)

                save_to_csv(complete_filename, fields_description)
                self.files_to_zip_list.append([complete_filename, export_directory])

                entrance_questionnaire = True

                # create questionnaire fields file ("fields.csv") in Questionnaire_metadata directory
                fields = self.get_questionnaire_fields(questionnaire_id, entrance_questionnaire)

                questionnaire_fields = self.create_questionnaire_explanation_fields_file(questionnaire_id, language,
                                                                                         questionnaire_lime_survey,
                                                                                         fields, entrance_questionnaire)

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

    def create_group_data_directory(self):
        error_msg = ""
        # path ex. /Users/.../NES_EXPORT/Experiment_data
        error_msg, path_experiment_data = create_directory(self.get_export_directory(),
                                                           self.get_input_data("experiment_data_directory"))
        if error_msg != "":
            return error_msg

        # path ex. /NES_EXPORT/Experiment_data
        export_experiment_data = path.join(self.get_input_data("base_directory"),
                                           self.get_input_data("experiment_data_directory"))

        for group_id in self.per_group_data:
            group_title = self.per_group_data[group_id]['group']['title']
            directory_group_name = "Group_" + group_title

            # cria pasta com o nome do grupo ex. Users/..../NES_EXPORT/Experiment_data/Group_xxx
            error_msg, directory_group = create_directory(path_experiment_data, directory_group_name)
            if error_msg != "":
                return error_msg

            # path ex. /NES_EXPORT/Experiment_data/Group_xxx
            export_directory_group = path.join(export_experiment_data, directory_group_name)

            self.per_group_data[group_id]['group']['directory'] = directory_group
            self.per_group_data[group_id]['group']['export_directory'] = export_directory_group

            if self.per_group_data[group_id]['questionnaires_per_group']:
                # ex. Users/..../NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire
                error_msg, directory_questionnaire_data = create_directory(
                    directory_group, self.get_input_data("per_questionnaire_directory"))
                if error_msg != "":
                    return error_msg
                # path ex. /NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire/
                export_directory_questionnaire_data = path.join(
                    export_directory_group, self.get_input_data("per_questionnaire_directory"))

                # ex. Users/..../NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata
                error_msg, directory_questionnaire_metadata = create_directory(
                    directory_group, self.get_input_data("questionnaire_metadata_directory"))
                if error_msg != "":
                    return error_msg
                # path ex. /NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata/
                export_directory__questionnaire_metadata = path.join(
                    export_directory_group, self.get_input_data("questionnaire_metadata_directory"))

                self.per_group_data[group_id]['group'][
                    'questionnaire_data_directory'] = directory_questionnaire_data
                self.per_group_data[group_id]['group'][
                    'questionnaire_data_export_directory'] = export_directory_questionnaire_data
                self.per_group_data[group_id]['group'][
                    'questionnaire_metadata_directory'] = directory_questionnaire_metadata
                self.per_group_data[group_id]['group'][
                    'questionnaire_metadata_export_directory'] = export_directory__questionnaire_metadata

            if self.per_group_data[group_id]['data_per_participant']:
                # ex. Users/..../NES_EXPORT/Experiment_data/Group_xxx/Per_participant
                error_msg, directory_participant_data = create_directory(
                    directory_group, self.get_input_data("per_participant_directory"))
                if error_msg != "":
                    return error_msg
                # path ex. /NES_EXPORT/Experiment_data/Group_xxx/Per_participant/
                participant_data_export_directory = path.join(
                    export_directory_group, self.get_input_data("per_participant_directory"))

                self.per_group_data[group_id]['group'][
                    'participant_data_directory'] = directory_participant_data
                self.per_group_data[group_id]['group'][
                    'participant_data_export_directory'] = participant_data_export_directory

        return error_msg

    def process_per_experiment_questionnaire(self):

        error_msg = ""

        for group_id in self.per_group_data:
            questionnaire_list = self.per_group_data[group_id]['questionnaires_per_group']
            for questionnaire_id in questionnaire_list:
                # create questionnaire_name_directory
                questionnaire = questionnaire_list[questionnaire_id]
                questionnaire_data = self.get_input_data('questionnaires_from_experiments')[group_id][
                    str(questionnaire_id)][0]
                questionnaire_code = questionnaire['questionnaire_code']
                questionnaire_title = self.redefine_questionnaire_title(questionnaire_data['questionnaire_name'])

                questionnaire_prefix_filename = questionnaire_data['prefix_filename_responses']
                # Ex. Q123_aaa
                directory_questionnaire_name = "%s_%s" % (str(questionnaire_code), questionnaire_title)

                # create directory with the code and name of each questionnaire
                # Ex. Users/.../NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire/Q123_aaa/
                path_group_per_questionnaire = self.per_group_data[group_id]['group']['questionnaire_data_directory']
                error_msg, complete_export_path = create_directory(path_group_per_questionnaire,
                                                                   directory_questionnaire_name)
                if error_msg != "":
                    return error_msg
                # Responses_Q123.csv
                export_filename = "%s_%s.csv" % (questionnaire_prefix_filename, str(questionnaire_code))

                # Ex. NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire/Q123_aaaa/
                export_directory_per_questionnaire = self.per_group_data[group_id]['group'][
                    'questionnaire_data_export_directory']
                export_directory = path.join(export_directory_per_questionnaire, directory_questionnaire_name)
                # Ex.
                # Users/.../NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire/Q123_aaa/Responses_Q123.csv
                complete_filename = path.join(complete_export_path, export_filename)

                # save file with data
                fields_description = []
                token_list = questionnaire['token_list']
                for token in token_list:
                    response_list = token['response_list']
                    # header = response_list[0]
                    # fields_description = response_list[1]
                    # for item in token['protocol_step_list'][0]:
                    #     header.append(item)
                    # for item in token['protocol_step_list'][1]:
                    #     fields_description.append(item)
                    fields_description = response_list
                    subject_data = []
                    participants_input_data = self.get_input_data("participants")
                    participants_list = (self.get_participants_filtered_data())
                    export_rows_participants = self.process_participant_data(participants_input_data, participants_list)
                    # if self.get_input_data('participants')[0]['output_list']:
                    #     header = header[0:len(header)-1]
                    #
                    #     patient_id = Patient.objects.filter(code=participant_code)
                    #     if patient_id:
                    #         participant_list = [patient_id.values('id')[0]['id']]
                    #         # get fields from patient 
                    #         export_participant_row = self.process_participant_data(
                    #             self.get_input_data('participants'), participant_list)
                    #         for field in export_participant_row[0]:
                    #             header.append(field)
                    #         per_participant_rows = [header]
                    #         # export_fields_row = self.merge_participant_data_per_participant_process(
                    #         #     questionnaire_code, participant_code, export_participant_row)
                    #         for field in fields_rows:
                    #             per_participant_rows.append(field)

                save_to_csv(complete_filename, fields_description)
                self.files_to_zip_list.append([complete_filename, export_directory])

                # questionnaire metadata directory
                entrance_questionnaire = False
                questionnaire_lime_survey = Questionnaires()
                language = questionnaire_data['language']
                # create questionnaire fields file ("fields.csv") in Questionnaire_metadata directory
                fields = self.get_questionnaire_experiment_fields(questionnaire_id)
                questionnaire_fields = self.create_questionnaire_explanation_fields_file(
                    str(questionnaire_id), language, questionnaire_lime_survey, fields, entrance_questionnaire)
                # Fields_Q123.csv
                export_filename = "%s_%s.csv" % (questionnaire_prefix_filename, str(questionnaire_code))

                # metadata directory para export
                # ('NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata/')
                export_metadata_directory = self.per_group_data[group_id]['group']['questionnaire_metadata_directory']
                # Ex. 'NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata/Q123_aaa/'
                export_directory = self.per_group_data[group_id]['group']['questionnaire_metadata_export_directory']
                # path ex. /Users/.../NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata/Q123_aaa/
                error_msg, complete_export_metadata_path = create_directory(export_metadata_directory,
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
                            # export_fields_row = self.merge_participant_data_per_participant_process(
                            #     questionnaire_code, participant_code, export_participant_row)
                            for field in fields_rows:
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
                                    export_filename = "%s_%s_%s.csv" % (str(participant_code),
                                                                        str(questionnaire_code), title)

                                    header = self.get_header_questionnaire(questionnaire_id)

                                    for row in self.get_input_data('participants'):
                                        headers_participant_data, fields = self.get_headers_and_fields(
                                            row["output_list"])
                                    header = header[0:len(header) - 1]
                                    for field in headers_participant_data:
                                        header.append(field)

                                    per_participant_rows = self.get_per_participant_data(participant_code,
                                                                                         questionnaire_code)
                                    per_participant_rows.insert(0, header)
                                    # path ex. /Users/.../NES_EXPORT/Participant_data/Per_participant/
                                    complete_filename = path.join(participant_path, export_filename)

                                    save_to_csv(complete_filename, per_participant_rows)

                                    export_directory = path.join(export_directory_base, path_participant)

                                    self.files_to_zip_list.append([complete_filename, export_directory])

        return error_msg

    def process_per_participant_per_experiment(self):

        error_msg = ''

        for group_id in self.per_group_data:
            participant_list = self.per_group_data[group_id]['data_per_participant']
            for participant_code in participant_list:
                prefix_filename_participant = "Participant_"
                # ex. Participant_P123
                participant_name = prefix_filename_participant + str(participant_code)
                participant_data_directory = self.per_group_data[group_id]['group']['participant_data_directory']
                # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                path_per_participant = path.join(participant_data_directory, participant_name)

                # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                participant_data_export_directory = self.per_group_data[group_id]['group'][
                    'participant_data_export_directory']
                participant_export_directory = path.join(participant_data_export_directory, participant_name)
                if 'token_list' in participant_list[participant_code]:
                    # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    for token_data in participant_list[participant_code]['token_list']:
                        step_data = token_data['protocol_step_list'][1]
                        directory_step_name = "Step_" + step_data[0] + "_" + step_data[1]
                        questionnaire_code = token_data['questionnaire_code']
                        questionnaire_id = token_data['questionnaire_id']
                        questionnaire_title = self.get_input_data('questionnaires_from_experiments')[group_id][
                            str(questionnaire_id)][0]['questionnaire_name']
                        # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                        error_msg, directory_step_participant = create_directory(path_per_participant, directory_step_name)
                        if error_msg != "":
                            return error_msg

                        # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                        step_participant_export_directory = path.join(participant_export_directory, directory_step_name)
                        #ex. P123_Q123_aaa.csv
                        export_filename = "%s_%s_%s.csv" % (str(participant_code), str(questionnaire_code), questionnaire_title)
                        # path ex. Users/.../Group_xxx/Per_participant/Per_participant/Participant_P123/Step_X_aaa/P123_Q123_aaa.csv
                        complete_filename = path.join(directory_step_participant, export_filename)
                        per_participant_rows = token_data['response_list']
                        # if participant_data selected
                        # per_participant_rows = self.get_per_participant_data_from_experiment(participant_code,
                        #                                                                      questionnaire_code)
                        save_to_csv(complete_filename, per_participant_rows)

                        # path ex.NES_EXPORT/Per_experiment/Per_participant/Per_participant/Participant_P123/Step_X_aaa/
                        export_directory = path.join(participant_export_directory, directory_step_name)
                        self.files_to_zip_list.append([complete_filename, export_directory])

                # for component_list

                if 'eeg_data' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    eeg_data_list = self.per_group_data[group_id]['data_per_participant'][participant_code]['eeg_data']
                    for component in eeg_data_list:
                        eeg_data = get_object_or_404(EEGData, pk=component['eeg_data_id'])
                        if eeg_data:
                            eeg_data_file = path.join(settings.BASE_DIR, 'media') + '/' + eeg_data.file.name

                            directory_step_name = component['directory_step_name']
                            path_per_eeg_participant = path.join(path_per_participant, directory_step_name)
                            if not path.exists(path_per_eeg_participant):
                                # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_aaa
                                error_msg, path_per_eeg_participant = create_directory(path_per_participant,
                                                                                       directory_step_name)
                                if error_msg != "":
                                    return error_msg

                            # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                            export_eeg_step_directory = path.join(participant_export_directory, directory_step_name)

                            eeg_data_filename = eeg_data.file.name.split('/')[-1]
                            complete_eeg_data_filename = path.join(path_per_eeg_participant, eeg_data_filename)

                            with open(eeg_data_file, 'rb') as f:
                                data = f.read()

                            with open(complete_eeg_data_filename, 'wb') as f:
                                f.write(data)

                            self.files_to_zip_list.append([complete_eeg_data_filename, export_eeg_step_directory])

                            eeg_setting_description = get_eeg_setting_description(component['setting_id'])

                            if eeg_setting_description:

                                eeg_setting_filename = "%s.txt" % "eeg_setting_description"

                                # ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/
                                # eeg_setting_description.txt #
                                complete_setting_filename = path.join(path_per_eeg_participant, eeg_setting_filename)

                                self.files_to_zip_list.append([complete_setting_filename, export_eeg_step_directory])

                                with open(complete_setting_filename.encode('utf-8'), 'w', newline='',
                                          encoding='UTF-8') as outfile:
                                    json.dump(eeg_setting_description, outfile, indent=4)

                            # if sensor position image exist
                            sensors_positions_image = get_sensors_position(eeg_data)
                            if sensors_positions_image:
                                sensor_position_filename = sensors_positions_image.split('/')[-1]

                                sensor_position_file = eeg_data_filename.split(".")[0] + "_" + sensor_position_filename
                                complete_sensor_position_filename = path.join(path_per_eeg_participant,
                                                                              sensor_position_file)
                                path_sensor_position_filename = settings.BASE_DIR + sensors_positions_image

                                with open(path_sensor_position_filename, 'rb') as f:
                                    data = f.read()

                                with open(complete_sensor_position_filename, 'wb') as f:
                                    f.write(data)

                                self.files_to_zip_list.append([complete_sensor_position_filename,
                                                               export_eeg_step_directory])

                if 'emg_data' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    emg_data_list = self.per_group_data[group_id]['data_per_participant'][participant_code]['emg_data']
                    for component in emg_data_list:
                        emg_data = get_object_or_404(EMGData, pk=component['emg_data_id'])
                        if emg_data:
                            directory_step_name = component['directory_step_name']
                            # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/
                            # Step_X_aaa
                            path_per_emg_participant = path.join(path_per_participant, directory_step_name)
                            if not path.exists(path_per_emg_participant):
                                error_msg, path_per_emg_participant = create_directory(path_per_participant,
                                                                                       directory_step_name)
                                if error_msg != "":
                                    return error_msg

                            # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                            export_emg_step_directory = path.join(participant_export_directory, directory_step_name)

                            emg_data_filename = emg_data.file.name.split('/')[-1]
                            emg_data_file = path.join(settings.BASE_DIR, 'media') + '/' + emg_data.file.name
                            complete_emg_data_filename = path.join(path_per_emg_participant, emg_data_filename)

                            with open(emg_data_file, 'rb') as f:
                                data = f.read()

                            with open(complete_emg_data_filename, 'wb') as f:
                                f.write(data)

                            self.files_to_zip_list.append([complete_emg_data_filename, export_emg_step_directory])

                            emg_setting_description = get_emg_setting_description(component['setting_id'])

                            if emg_setting_description:

                                emg_setting_filename = "%s.txt" % "emg_setting_description"

                                # ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/
                                # emg_setting_description.txt #
                                complete_setting_filename = path.join(path_per_emg_participant, emg_setting_filename)

                                self.files_to_zip_list.append([complete_setting_filename, export_emg_step_directory])

                                with open(complete_setting_filename.encode('utf-8'), 'w', newline='',
                                          encoding='UTF-8') as outfile:
                                    json.dump(emg_setting_description, outfile, indent=4)

                if 'tms_data' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    tms_data_list = self.per_group_data[group_id]['data_per_participant'][participant_code]['tms_data']
                    for component in tms_data_list:
                        tms_data_description = get_tms_data_description(component['tms_data_id'])
                        if tms_data_description:
                            directory_step_name = component['directory_step_name']
                            path_per_tms_participant = path.join(path_per_participant, directory_step_name)
                            if not path.exists(path_per_tms_participant):
                                # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                                error_msg, path_per_tms_participant = create_directory(path_per_participant,
                                                                                       directory_step_name)
                                if error_msg != "":
                                    return error_msg

                            # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                            export_tms_step_directory = path.join(participant_export_directory, directory_step_name)

                            tms_data_filename = "%s.txt" % "tms_data_description"
                            # ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/tms_data_description.txt #
                            complete_data_filename = path.join(path_per_tms_participant, tms_data_filename)

                            tms_setting_filename = "%s.txt" % "tms_setting_description"
                            # ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/tms_setting_description.txt #
                            complete_setting_filename = path.join(path_per_tms_participant, tms_setting_filename)

                            self.files_to_zip_list.append([complete_data_filename, export_tms_step_directory])

                            with open(complete_data_filename.encode('utf-8'), 'w', newline='',
                                      encoding='UTF-8') as outfile:
                                json.dump(tms_data_description, outfile, indent=4)

                            # TMS hotspot position image file
                            tms_data = get_object_or_404(TMSData, pk=component['tms_data_id'])
                            tms_localization_system = get_object_or_404(
                                TMSLocalizationSystem, pk=tms_data.hotspot.tms_localization_system_id)

                            tms_localization_system_image = tms_localization_system.tms_localization_system_image.name
                            if tms_localization_system_image:
                                hotspot_position_image_filename = tms_localization_system_image.split('/')[-1]
                                complete_hotspot_position_filename = path.join(path_per_tms_participant,
                                                                               hotspot_position_image_filename)
                                path_tms_localization_system_image = path.join(settings.BASE_DIR, "media") + "/" + \
                                                                     tms_localization_system_image
                                with open(path_tms_localization_system_image, 'rb') as f:
                                    data = f.read()

                                with open(complete_hotspot_position_filename, 'wb') as f:
                                    f.write(data)

                                self.files_to_zip_list.append([complete_hotspot_position_filename,
                                                               export_tms_step_directory])


                if 'additional_data' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    additional_data_list = self.per_group_data[group_id]['data_per_participant'][participant_code][
                        'additional_data']

                    for additional_data in additional_data_list:
                        directory_step_name = additional_data['directory_step_name']
                        path_additional_data = path.join(path_per_participant, directory_step_name)
                        if not path.exists(path_additional_data):
                            # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                            # /Step_X_COMPONENT_TYPE
                            error_msg, path_additional_data = create_directory(path_per_participant, directory_step_name)

                            if error_msg != "":
                                return error_msg

                        # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_COMPONENT_TYPE
                        export_additional_data_directory = path.join(participant_export_directory, directory_step_name)

                        file_name = additional_data['additional_file_name'].split('/')[-1]
                        # read file from repository
                        additional_data_filename = path.join(settings.BASE_DIR, 'media') + '/' + \
                                                   additional_data['additional_file_name']
                        # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/
                        # Step_X_COMPONENT_TYPE/file_name.format_type
                        complete_additional_data_filename = path.join(path_additional_data, file_name)
                        with open(additional_data_filename, 'rb') as f:
                            data = f.read()

                        with open(complete_additional_data_filename, 'wb') as f:
                            f.write(data)

                        self.files_to_zip_list.append([complete_additional_data_filename,
                                                       export_additional_data_directory])

                if 'goalkeeper_game_data' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    goalkeeper_game_data_list = self.per_group_data[group_id]['data_per_participant'][participant_code][
                        'goalkeeper_game_data']

                    for goalkeeper_game_data in goalkeeper_game_data_list:
                        directory_step_name = goalkeeper_game_data['directory_step_name']
                        path_goalkeeper_game_data = path.join(path_per_participant, directory_step_name)
                        if not path.exists(path_goalkeeper_game_data):
                            # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                            # /Step_X_COMPONENT_TYPE
                            error_msg, path_goalkeeper_game_data = create_directory(path_per_participant,
                                                                                    directory_step_name)

                            if error_msg != "":
                                return error_msg

                            # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_COMPONENT_TYPE
                            export_goalkeeper_game_directory = path.join(participant_export_directory,
                                                                         directory_step_name)

                            file_name = goalkeeper_game_data['goalkeeper_game_file'].split('/')[-1]
                            # read file from repository
                            goalkeeper_game_data_filename = path.join(settings.BASE_DIR, 'media') + '/' + \
                                                            goalkeeper_game_data['goalkeeper_game_file']
                            # ex. /Users/.../NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/
                            # Step_X_COMPONENT_TYPE/file_name.format_type
                            complete_goalkeeper_game_filename = path.join(path_goalkeeper_game_data, file_name)
                            with open(goalkeeper_game_data_filename, 'rb') as f:
                                data = f.read()

                            with open(complete_goalkeeper_game_filename, 'wb') as f:
                                f.write(data)

                            self.files_to_zip_list.append([complete_goalkeeper_game_filename,
                                                           export_goalkeeper_game_directory])

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

    def get_participant_data_per_id(self, patient_id, questionnaire_response_fields):

        for row in self.get_input_data('participants'):
            headers, fields = self.get_headers_and_fields(row["output_list"])

            model_to_export = getattr(modules['patient.models'], 'Patient')

            if model_to_export.objects.filter(id=patient_id):
                db_data = model_to_export.objects.filter(id=patient_id).values_list(*fields)[0]
            else:
                db_data = ""

            # export_participant_data = [headers]

            # append participant data
            for field in db_data:
                questionnaire_response_fields.append(field)

        return questionnaire_response_fields

    def process_participant_filtered_data(self, per_experiment):
        error_msg = ""
        participants_filtered_list = self.get_participants_filtered_data()
        # process participants/diagnosis (Per_participant directory)
        # path ex. Users/.../NES_EXPORT/
        base_export_directory = self.get_export_directory()
        # /NES_EXPORT/
        base_directory = self.get_input_data("base_directory")
        # Participant_data directory
        participant_data_directory = self.get_input_data("participant_data_directory")
        if per_experiment:
            # path ex. Users/.../NES_EXPORT/Participant_data/
            participant_base_export_directory = path.join(base_export_directory, participant_data_directory)
            # /NES_EXPORT/Participant_data
            base_directory = path.join(base_directory, participant_data_directory)
            if not path.exists(participant_base_export_directory):
                error_msg, base_export_directory = create_directory(base_export_directory, participant_data_directory)

                if error_msg != "":
                    return error_msg

        # create participant.csv file
        export_rows_participants = self.get_input_data('participants')[0]['data_list']

        export_filename = "%s.csv" % self.get_input_data('participants')[0]["output_filename"]  # "export.csv"

        complete_filename = path.join(base_export_directory, export_filename)

        self.files_to_zip_list.append([complete_filename, base_directory])

        with open(complete_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as csv_file:
            export_writer = writer(csv_file)
            for row in export_rows_participants:
                export_writer.writerow(row)

        # process  diagnosis file
        diagnosis_input_data = self.get_input_data("diagnosis")

        if diagnosis_input_data[0]['output_list'] and participants_filtered_list:
            export_rows_diagnosis = self.process_participant_data(diagnosis_input_data, participants_filtered_list)

            export_filename = "%s.csv" % self.get_input_data('diagnosis')[0]["output_filename"]  # "export.csv"

            complete_filename = path.join(base_export_directory, export_filename)

            # files_to_zip_list.append(complete_filename)
            self.files_to_zip_list.append([complete_filename, base_directory])

            with open(complete_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as csv_file:
                export_writer = writer(csv_file)
                for row in export_rows_diagnosis:
                    export_writer.writerow(row)

        return error_msg

    def process_experiment_data(self, language_code):
        error_msg = ""
        # process of filename for experiment resume
        for group_id in self.per_group_data:
            group = get_object_or_404(Group, pk=group_id)

        study = group.experiment.research_project
        experiment = group.experiment
        experiment_resume_header = 'Study' + '\t' + 'Study description' + '\t' + 'Start date' + '\t' + \
                                   'End date' + '\t' + 'Experiment' + '\t' + \
                                   'Experiment description' + '\t' + 'Data aquisition concluded' + "\n"
        experiment_resume = \
            study.title + '\t' + study.description + '\t' + \
            str(study.start_date) + '\t' + str(study.end_date) + '\t' + \
            experiment.title + '\t' + experiment.description + '\t' + \
            str(experiment.data_acquisition_is_concluded) + "\n"

        filename_experiment_resume = "%s.csv" % "Experiment"

        # path ex. /NES_EXPORT/Experiment_data
        export_experiment_data = path.join(self.get_input_data("base_directory"),
                                           self.get_input_data("experiment_data_directory"))

        # path ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data
        experiment_resume_directory = path.join(self.get_export_directory(),
                                                self.get_input_data("experiment_data_directory"))

        # User/.../qdc/media/.../NES_EXPORT/Experiment_data/Experiment.csv
        complete_filename_experiment_resume = path.join(experiment_resume_directory, filename_experiment_resume)

        self.files_to_zip_list.append([complete_filename_experiment_resume, export_experiment_data])

        with open(complete_filename_experiment_resume.encode('utf-8'), 'w', newline='',
                  encoding='UTF-8') as csv_file:
            csv_file.writelines(experiment_resume_header)
            csv_file.writelines(experiment_resume)

        # process of filename for description of each group
        for group_id in self.per_group_data:
            group = get_object_or_404(Group, pk=group_id)
            if group.experimental_protocol:

                tree = get_block_tree(group.experimental_protocol, language_code)
                experimental_protocol_description = get_description_from_experimental_protocol_tree(tree)

                group_resume = "Group name: " + group.title + "\n" + "Group description: " + group.description \
                               + "\n"
                group_directory_name = 'Group_' + group.title
                filename_group_for_export = "%s.txt" % "Experimental_protocol_description"
                # path ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/
                group_file_directory = self.per_group_data[group_id]['group']['directory']
                # path ex. /NES_EXPORT/Experiment_data/Group_xxxx/
                export_group_directory = self.per_group_data[group_id]['group']['export_directory']
                # path ex.
                # User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/Experimental_protocol_description.txt
                complete_group_filename = path.join(group_file_directory, filename_group_for_export)

                self.files_to_zip_list.append([complete_group_filename, export_group_directory])

                with open(complete_group_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as txt_file:
                    txt_file.writelines(group_resume)
                    txt_file.writelines(experimental_protocol_description)

                # save protocol image
                filename_protocol_image = "Protocol_image.png"
                complete_protocol_image_filename = path.join(group_file_directory, filename_protocol_image)
                # self.files_to_zip_list.append([complete_group_filename, complete_protocol_image_filename])

                experimental_protocol_image = get_experimental_protocol_image(group.experimental_protocol, tree)
                image_protocol = settings.BASE_DIR + experimental_protocol_image
                with open(image_protocol, 'rb') as f:
                    data = f.read()

                with open(complete_protocol_image_filename, 'wb') as f:
                    f.write(data)

                self.files_to_zip_list.append([complete_protocol_image_filename, export_group_directory])

                # process participant/diagnosis per Participant of each group
                participant_group_list = []
                subject_of_group = SubjectOfGroup.objects.filter(group=group)
                for subject in subject_of_group:
                    participant_group_list.append(subject.subject.patient_id)

                if 'stimulus_data' in self.per_group_data[group_id]:
                    stimulus_data_list = self.per_group_data[group_id]['stimulus_data']
                    for stimulus_data in stimulus_data_list:
                        # ex. /Users/../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/Step_X_STIMULUS
                        path_stimulus_data = path.join(group_file_directory, stimulus_data['directory_step_name'])
                        if not path.exists(path_stimulus_data):
                            error_msg, directory_stimulus_data = create_directory(group_file_directory,
                                                                                  stimulus_data['directory_step_name'])
                            if error_msg != "":
                                return error_msg

                        # ex. /NES_EXPORT/Experiment_data/Group_xxxx/Step_X_STIMULUS
                        export_directory_stimulus_data = path.join(export_group_directory,
                                                                   stimulus_data['directory_step_name'])
                        stimulus_file_name = stimulus_data['stimulus_file'].split("/")[-1]
                        stimulus_data_file_name = path.join(settings.BASE_DIR, "media") + "/" + \
                                                  stimulus_data['stimulus_file']
                        complete_stimulus_data_filename = path.join(path_stimulus_data, stimulus_file_name)

                        with open(stimulus_data_file_name, "rb") as f:
                            data = f.read()

                        with open(complete_stimulus_data_filename, "wb") as f:
                            f.write(data)

                        self.files_to_zip_list.append([complete_stimulus_data_filename, export_directory_stimulus_data])

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

    def redefine_header_and_fields_experiment(self, questionnaire_id, header_filtered, fields, header_list):

        header = self.questionnaires_experiment_data[questionnaire_id]["header"]
        header_questionnaire = self.questionnaires_experiment_data[questionnaire_id]["header_questionnaire"]
        fields_saved = self.questionnaires_experiment_data[questionnaire_id]["fields"]

        new_header = []
        new_fields = []
        new_header_questionnaire = []

        for item in fields:
            new_header_questionnaire.append(header_questionnaire[fields.index(item)])
            new_fields.append(fields_saved[fields.index(item)])

            if item in header_filtered:
                new_header_questionnaire.append(header_questionnaire[fields.index(item)])
                new_fields.append(fields_saved[fields.index(item)])

        # for element in header_list:
        #     new_header.append(header[element])

        self.questionnaires_experiment_data[questionnaire_id]["header"] = header_list
        self.questionnaires_experiment_data[questionnaire_id]["header_questionnaire"] = new_header_questionnaire
        self.questionnaires_experiment_data[questionnaire_id]["fields"] = new_fields

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

    def get_questionnaires_responses(self):
        questionnaire_lime_survey = Questionnaires()
        response_type = self.get_response_type()
        for group_id in self.get_input_data('questionnaires_from_experiments'):
            for questionnaire_id in self.get_input_data('questionnaires_from_experiments')[group_id]:
                language = questionnaire_lime_survey.get_survey_languages(questionnaire_id)['language']
                questionnaire = self.get_input_data('questionnaires_from_experiments')[group_id][
                    str(questionnaire_id)][0]
                headers, fields = self.set_questionnaire_experiment_header_and_fields(questionnaire_id, questionnaire)
                # headers, fields = self.set_questionnaire_header_and_fields(questionnaire_data)
                # verify if Lime Survey is running
                limesurvey_available = is_limesurvey_available(questionnaire_lime_survey)
                if limesurvey_available:
                    # read all data for questionnaire_id from LimeSurvey
                    responses_string1 = questionnaire_lime_survey.get_responses(questionnaire_id, language,
                                                                                response_type[0])
                    # all the answer from the questionnaire_id in csv format
                    fill_list1 = perform_csv_response(responses_string1)

                    # read "long" information, if necessary
                    if len(response_type) > 1:
                        responses_string2 = questionnaire_lime_survey.get_responses(questionnaire_id, language,
                                                                                    response_type[1])
                        fill_list2 = perform_csv_response(responses_string2)
                    else:
                        fill_list2 = fill_list1

                    data_from_lime_survey = {}

                    duplicate_indices = self.find_duplicates(fill_list1, fill_list2)

                    line_index = 1
                    line_total = len(fill_list1) - 1
                    header_filtered = set()
                    while line_index < line_total:
                        data_fields_filtered = []
                        line1 = fill_list1[line_index]
                        line2 = fill_list2[line_index]

                        data_fields_filtered.append(line1)
                        if duplicate_indices:
                            data_fields_filtered.append(line2)
                            header_filtered.add(fill_list1[0])

                        token = line1[fill_list1[0].index("token")]
                        data_from_lime_survey[token] = list(data_fields_filtered)
                        line_index += 1

                questionnaire_list = self.per_group_data[group_id]['questionnaires_per_group'][int(questionnaire_id)]['token_list']
                for questionnaire_data in questionnaire_list:
                    token_id = questionnaire_data['token_id']
                    token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id, "token")

                    # filter fields
                    subscripts = []
                    # identify the index of the fields selected on the fill_list1[0]
                    for field in fields:
                        if field in fill_list1[0]:
                            subscripts.append(fill_list1[0].index(field))
                    fields_filtered_list = []
                    fields_filtered_list.append(headers)
                    fields_filtered_list.append([])
                    for index in subscripts:
                        fields_filtered_list[1].append(data_from_lime_survey[token][0][index])
                    # data_fields_filtered.insert(0, headers)

                    questionnaire_data['response_list'] = list(fields_filtered_list)
                    if token_id not in self.questionnaires_experiment_responses:
                        self.questionnaires_experiment_responses[token_id] = list(fields_filtered_list)

    def define_experiment_questionnaire(self, questionnaire, questionnaire_lime_survey):
        questionnaire_id = questionnaire["id"]
        language = questionnaire["language"]
        group_id = questionnaire['group_id']
        response_type = self.get_response_type()
        step_header = ['Step', 'Step identification', 'Path of the step', 'Data completed']
        token_id = self.per_group_data[group_id]['questionnaires_per_group'][0][questionnaire_id][1][0]['token_id']

        questionnaire_data = self.per_group_data[group_id]['questionnaires_per_group'][0][questionnaire_id][1][0]
        survey_code = questionnaire_data['questionnaire_code']
        patient_id = questionnaire_data['subject_id']
        lime_survey_id = questionnaire_id
        patient_code = questionnaire_data['subject_code']
        step_identification = questionnaire_data['step_identification']
        step_path = questionnaire_data['path_questionnaire']
        step_number = questionnaire_data['step_number']
        data_completed = questionnaire_data['data_completed']

        step_information_list = [step_number, step_identification, step_path, data_completed]

        export_rows = []
        # verify if Lime Survey is running
        limesurvey_available = is_limesurvey_available(questionnaire_lime_survey)

        headers, fields = self.set_questionnaire_experiment_header_and_fields(questionnaire)

        if limesurvey_available:
            # read all data for questionnaire_id from LimeSurvey
            # responses_string = questionnaire_lime_survey.get_responses(questionnaire_id, language)
            responses_string1 = questionnaire_lime_survey.get_responses(questionnaire_id, language,
                                                                        response_type[0])
            # all the answer from the questionnaire_id in csv format
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
            # identify the index of the fields selected on the fill_list1[0]
            for field in fields:
                if field in fill_list1[0]:
                    subscripts.append(fill_list1[0].index(field))

            data_from_lime_survey = {}

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
            # self.update_questionnaire_experiment_rules(questionnaire_id)

            token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id, "token")

            if token in data_from_lime_survey:

                lm_data_row = data_from_lime_survey[token]

                if lm_data_row:
                    # lm_row = lm_data_row
                    for element in step_information_list:
                        lm_data_row.append(element)

                data_fields = [smart_str(data) for data in lm_data_row]

                if self.get_input_data('participants')[0]['output_list']:
                    transformed_fields = self.get_participant_data_per_id(patient_id, data_fields)
                else:
                    transformed_fields = self.transform_questionnaire_data(patient_id, data_fields)
                # data_rows.append(transformed_fields)

                if len(transformed_fields) > 0:
                    export_rows.append(transformed_fields)

                    self.include_questionnaire_code_and_id(survey_code, lime_survey_id)

                    self.include_in_per_participant_data_from_experiment([transformed_fields], patient_code,
                                                                         survey_code, token_id, step_number)

                    self.include_participant_per_questionnaire(token_id, survey_code)

            # build the header
            for row in self.get_input_data('participants'):
                headers_participant_data, fields_participant_data = self.get_headers_and_fields(row["output_list"])

            header = self.get_header_experiment_questionnaire(questionnaire_id)

            # if header[len(header) - 1] == 'participant_code':
            #     header = header[0:len(header) - 1]
            for element in step_header:
                header.append(element)

            for field in headers_participant_data:
                header.append(field)

            self.redefine_header_and_fields_experiment(questionnaire_id, header_filtered, fields, header)

            export_rows.insert(0, header)
        return export_rows

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

        export_rows = []

        # verify if Lime Survey is running
        limesurvey_available = is_limesurvey_available(questionnaire_lime_survey)

        headers, fields = self.set_questionnaire_header_and_fields(questionnaire, True)
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

            for field in fields:
                if field in fill_list1[0]:
                    subscripts.append(fill_list1[0].index(field))

            data_from_lime_survey = {}

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

            # if group_id != "":
            #     self.update_questionnaire_experiment_rules(questionnaire_id)
            # else:
            self.update_questionnaire_rules(questionnaire_id)

            # for each questionnaire_id from ResponseQuestionnaire from questionnaire_id
            for questionnaire_response in questionnaire_responses:

                # transform data fields
                # include new fieldsm

                patient_id = questionnaire_response.patient_id
                survey_code = questionnaire_response.survey.code
                lime_survey_id = questionnaire_response.survey.lime_survey_id
                patient_code = questionnaire_response.patient.code
                token_id = questionnaire_response.token_id

                token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id, "token")

                if token in data_from_lime_survey:

                    lm_data_row = data_from_lime_survey[token]

                    data_fields = [smart_str(data) for data in lm_data_row]

                    if self.get_input_data('participants')[0]['output_list']:
                        transformed_fields = self.get_participant_data_per_id(patient_id, data_fields)
                    else:
                        transformed_fields = self.transform_questionnaire_data(patient_id, data_fields)
                    # data_rows.append(transformed_fields)

                    if len(transformed_fields) > 0:
                        export_rows.append(transformed_fields)

                        self.include_questionnaire_code_and_id(survey_code, lime_survey_id)

                        self.include_in_per_participant_data([transformed_fields], patient_code, survey_code)

                        self.include_participant_per_questionnaire(token_id, survey_code)

            self.redefine_header_and_fields(questionnaire_id, header_filtered, fields)

        for row in self.get_input_data('participants'):
            headers_participant_data, fields = self.get_headers_and_fields(row["output_list"])

        header = self.get_header_questionnaire(questionnaire_id)
        header = header[0:len(header) - 1]
        for field in headers_participant_data:
            header.append(field)

        export_rows.insert(0, header)
        return export_rows


def get_eeg_setting_description(eeg_setting_id):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)
    description = {}
    description['eeg_amplifier_setting'] = []
    eeg_amplifier_setting = eeg_setting.eeg_amplifier_setting
    description['eeg_amplifier_setting'].append({
        'identification': eeg_amplifier_setting.eeg_amplifier.identification,
        'description': eeg_amplifier_setting.eeg_amplifier.description,
        'gain': eeg_amplifier_setting.gain,
        'sampling_rate': eeg_amplifier_setting.sampling_rate,
        'number_of_channels_used': eeg_amplifier_setting.number_of_channels_used
    })

    description['eeg_filter_setting'] = []
    eeg_filter_setting = eeg_setting.eeg_filter_setting
    description['eeg_filter_setting'].append({
        'filter_type': eeg_filter_setting.eeg_filter_type.name,
        'description': eeg_filter_setting.eeg_filter_type.description,
        'high_pass': eeg_filter_setting.high_pass,
        'low_pass': eeg_filter_setting.low_pass,
        'order': eeg_filter_setting.order,
        'high_band_pass': eeg_filter_setting.high_band_pass,
        'low_band_pass': eeg_filter_setting.low_band_pass,
        'high_notch': eeg_filter_setting.high_notch,
        'low_notch': eeg_filter_setting.low_notch
    })

    description['eeg_solution_setting'] = []
    eeg_solution_setting = eeg_setting.eeg_solution_setting
    description['eeg_solution_setting'].append({
        'manufacturer': eeg_solution_setting.eeg_solution.manufacturer.name,
        'identification': eeg_solution_setting.eeg_solution.name,
        'components': eeg_solution_setting.eeg_solution.components
    })

    description['eeg_electrode_layout_setting'] = []
    eeg_electrode_layout_setting = eeg_setting.eeg_electrode_layout_setting.eeg_electrode_net_system
    description['eeg_electrode_layout_setting'].append({
        'manufacturer': eeg_electrode_layout_setting.eeg_electrode_net.manufacturer.name,
        'identification': eeg_electrode_layout_setting.eeg_electrode_net.identification,
        'description': eeg_electrode_layout_setting.eeg_electrode_net.description,
        'eeg_electrode_localization_system': eeg_electrode_layout_setting.eeg_electrode_localization_system.name,
        'eeg_electrode_model_default': eeg_electrode_layout_setting.eeg_electrode_localization_system.name,
        'cap_size': ''
    })

    return description


def get_emg_setting_description(emg_setting_id):
    emg_setting = get_object_or_404(EMGSetting, pk=emg_setting_id)
    description = {}
    description['emg_ad_converter_setting'] = []
    description['emg_ad_converter_setting'].append({
        'sampling_rate': emg_setting.emg_ad_converter_setting.sampling_rate,
    })

    description['emg_digital_filter_setting'] = []
    emg_digital_filter_setting = emg_setting.emg_digital_filter_setting
    description['emg_digital_filter_setting'].append({
        'high_pass': emg_digital_filter_setting.high_pass,
        'low_pass': emg_digital_filter_setting.low_pass,
        'order': emg_digital_filter_setting.order,
        'high_band_pass': emg_digital_filter_setting.high_band_pass,
        'low_band_pass': emg_digital_filter_setting.low_band_pass,
        'high_notch': emg_digital_filter_setting.high_notch,
        'low_notch': emg_digital_filter_setting.low_notch
    })

    return description


def get_tms_data_description(tms_data_id):
    tms_data = get_object_or_404(TMSData, pk=tms_data_id)

    tms_description = {
        'setting_description': {},
        'stimulation_description': {},
        'hotspot_position': {},
    }

    tms_description['stimulation_description'] = {
        'tms_stimulation_description': tms_data.description,
        'pulse_stimulus': tms_data.tms_setting.tms_device_setting.pulse_stimulus_type,
        'resting_motor threshold-RMT(%)': tms_data.resting_motor_threshold,
        'test_pulse_intensity_of_simulation(% over the %RMT)': tms_data.test_pulse_intensity_of_simulation,
        'interval_between_pulses': tms_data.interval_between_pulses,
        'interval_between_pulses_unit': tms_data.interval_between_pulses_unit,
        'repetitive_pulse_frequency': tms_data.repetitive_pulse_frequency,
        'coil_orientation': tms_data.coil_orientation.name,
        'coil_orientation_angle': tms_data.coil_orientation_angle,
        'second_test_pulse_intensity (% over the %RMT)': tms_data.second_test_pulse_intensity,
        'time_between_mep_trials': tms_data.time_between_mep_trials,
        'time_between_mep_trials_unit': tms_data.time_between_mep_trials_unit,
    }
    localization_system_selected = get_object_or_404(TMSLocalizationSystem,
                                                     pk=tms_data.hotspot.tms_localization_system_id)
    tms_description['hotspot_position'] = {
        'tms_localization_system_name': localization_system_selected.name,
        'tms_localization_system_description': localization_system_selected.description,
        'brain_area': localization_system_selected.brain_area.name,
    }

    tms_setting = get_object_or_404(TMSSetting, pk=tms_data.tms_setting_id)

    tms_description['setting_description'] = {
        'name': tms_setting.name,
        'description': tms_setting.description,
        'pulse_stimulus_type': tms_setting.tms_device_setting.pulse_stimulus_type,
    }

    return tms_description

