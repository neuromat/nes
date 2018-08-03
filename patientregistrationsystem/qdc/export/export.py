# -*- coding: utf-8 -*-
import csv
import json
import random
import re

from csv import writer
from datetime import date, datetime, timedelta
from sys import modules
from os import path, makedirs

from django.conf import settings
from django.core.files import File
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.apps import apps
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify

from export.export_utils import create_list_of_trees, can_export_nwb

from survey.survey_utils import QuestionnaireUtils

from patient.models import Patient, QuestionnaireResponse
from experiment.models import QuestionnaireResponse as ExperimentQuestionnaireResponse, SubjectOfGroup, Group, \
    ComponentConfiguration, Questionnaire, DataConfigurationTree, EEGData, EEGSetting, EMGData, EMGSetting, TMSData, \
    TMSSetting, AdditionalData, DigitalGamePhaseData, Stimulus, GenericDataCollectionData, \
    ContextTree, SubjectStepData, EEGElectrodePositionSetting, SurfaceElectrode, IntramuscularElectrode, \
    NeedleElectrode, EMGElectrodeSetting, EMGIntramuscularPlacement, EMGSurfacePlacement, EMGNeedlePlacement
from experiment.views import get_block_tree, get_experimental_protocol_image, \
    get_description_from_experimental_protocol_tree, get_sensors_position, create_nwb_file, \
    list_data_configuration_tree

from survey.abc_search_engine import Questionnaires
from survey.views import limesurvey_available


DEFAULT_LANGUAGE = "pt-BR"

metadata_directory = "Questionnaire_metadata"

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
    {
        "per_questionnaire":
            ["root", "base_directory", "export_per_questionnaire"],
        "per_participant":
            ["root", "base_directory", "export_per_participant"],
        "participant": ["root", "base_directory"],
        "diagnosis": ["root", "base_directory"],
    }
]

# valid for all questionnaires (no distinction amongst questionnaires)
included_questionnaire_fields = [
    {
        "field": "participant_code",
        "header": {
            "code": "participant_code",
            "full": _("Participant code"),
            "abbreviated": _("Participant code")
        },
        "model": "patient.patient", "model_field": "code"
    },
]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def to_number(value):
    return int(float(value))


def save_to_csv(complete_filename, rows_to_be_saved, mode='w'):
    """
    :param complete_filename: filename and directory structure where file is
    going to be saved
    :param rows_to_be_saved: list of rows that are going to be written on the
    file
    :param mode: mode for openning file
    :return:
    """
    with open(
            complete_filename.encode('utf-8'), mode, newline='',
            encoding='UTF-8'
    ) as csv_file:
        export_writer = csv.writer(
            csv_file, quotechar='"', quoting=csv.QUOTE_NONNUMERIC
        )
        for row in rows_to_be_saved:
            export_writer.writerow(row)


def replace_multiple_question_answers(responses, question_list):
    """
    Get responses list - after limesurvey participants answers obtained from
    get_responses_by_token or get_responses limesurvey api methods - that
    are multiple choices/multiple choices with comments question types (from
    question_list), and replaces the options that was not selected by
    participants with a 'N' (options that was selected have 'Y' - or 'S'
    in Portuguese - filled.
    :param responses: double array with questions in first line and answers
    in the other lines
    :param question_list: list of multiple choice/multiple choice with
    comments questions types
    Obs.: modifies responses list
    """
    i = 0
    m = len(responses[0])
    while i < m:
        question_match = re.match('(^.+)\[', responses[0][i])
        question = question_match.group(1) if question_match else None
        if question and question in question_list:
            index_subquestions = []
            while i < m and question in responses[0][i]:
                index_subquestions.append(i)
                i += 1
            for j in range(1, len(responses) - 1):
                filled = False
                for k in index_subquestions:
                    if responses[j][k] != '':
                        filled = True
                        break
                if filled:
                    for k in index_subquestions:
                        if responses[j][k] == '':
                            responses[j][k] = 'N'
        else:
            i += 1


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

    if not path.exists(complete_path.encode('utf-8')):
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
        self.files_to_zip_list = []
        self.directory_base = ''
        self.base_directory_name = path.join(settings.MEDIA_ROOT, "export")
        self.set_directory_base(user_id, export_id)
        self.base_export_directory = ""
        self.user_name = None
        self.input_data = {}
        self.per_participant_data = {}
        self.per_participant_data_from_experiment = {}
        self.participants_per_entrance_questionnaire = {}
        self.participants_per_experiment_questionnaire = {}
        self.questionnaires_experiment_responses = {}
        self.root_directory = ""
        self.participants_filtered_data = []
        self.per_group_data = {}
        self.questionnaire_utils = QuestionnaireUtils()

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

        # MEDIA_ROOT/export/username_id/export_id/NES_EXPORT
        return self.base_export_directory

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
            if data_key not in self.input_data.keys():
                return False
        return True

    def get_input_data(self, key):

        return self.input_data[key] if key in self.input_data.keys() else ''

    def include_in_per_participant_data(self, to_be_included_list, participant_id, questionnaire_id, language):
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
            self.per_participant_data[participant_id][questionnaire_id] = {}

        if language not in self.per_participant_data[participant_id][questionnaire_id]:
            self.per_participant_data[participant_id][questionnaire_id][language] = []

        for element in to_be_included_list:
            self.per_participant_data[participant_id][questionnaire_id][language].append(element)

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

        if token_id not in self.per_participant_data_from_experiment[participant_id][questionnaire_id]:
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
        header_step_list = \
            [
                'Step', 'Step identification', 'Path questionnaire',
                'Data completed'
            ]
        for group_id in group_list:
            group = get_object_or_404(Group, pk=group_id)
            subject_of_group = SubjectOfGroup.objects.filter(group=group)
            title = '_'.join(slugify(group.title).split('-'))

            description = group.description
            if group_id not in self.per_group_data:
                self.per_group_data[group_id] = {}
            self.per_group_data[group_id]['group'] = {
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
                'eeg_default_setting_id': '',
                'emg_default_setting_id': '',
                'tms_default_setting_id': '',
                'context_tree_default_id': ''
            }

            participant_group_list = \
                Patient.objects.filter(subject__subjectofgroup__group=group).values('id')
            self.per_group_data[group_id]['participant_list'] = []
            for participant in participant_group_list:
                self.per_group_data[group_id]['participant_list'].append(participant)

            self.per_group_data[group_id]['data_per_participant'] = {}
            self.per_group_data[group_id]['questionnaires_per_group'] = {}
            if group.experimental_protocol is not None and self.get_input_data('questionnaires_from_experiments'):
                if group_id in self.get_input_data('questionnaires_from_experiments'):
                    for path_experiment in create_list_of_trees(group.experimental_protocol, "questionnaire"):
                        path_questionnaire = ''
                        size = len(path_experiment[0])
                        step = 1
                        while step < size:
                            path_questionnaire += path_experiment[0][step] + "/"
                            step += 2
                        questionnaire_configuration = get_object_or_404(ComponentConfiguration,
                                                                        pk=path_experiment[-1][0])
                        component_type = \
                            questionnaire_configuration.component.component_type
                        questionnaire = Questionnaire.objects.get(
                            id=questionnaire_configuration.component.id
                        )
                        questionnaire_id = questionnaire.survey.lime_survey_id
                        if str(questionnaire_id) in self.get_input_data('questionnaires_from_experiments')[group_id]:
                            questionnaire_code = questionnaire.survey.code
                            self.questionnaire_utils.include_questionnaire_code_and_id(
                                questionnaire_code, str(questionnaire_id)
                            )
                            configuration_tree_list = DataConfigurationTree.objects.filter(
                                component_configuration=questionnaire_configuration
                            )

                            for data_configuration_tree in configuration_tree_list:
                                experiment_questionnaire_response_list = ExperimentQuestionnaireResponse.objects.filter(
                                    data_configuration_tree_id=data_configuration_tree.id)
                                for questionnaire_response in experiment_questionnaire_response_list:
                                    token_id = questionnaire_response.token_id
                                    completed = surveys.get_participant_properties(
                                        questionnaire_id, token_id, "completed")
                                    # load complete questionnaires data
                                    if completed is not None and completed != 'N' and completed != '':
                                        subject_code = questionnaire_response.subject_of_group.subject.patient.code
                                        step_number = path_experiment[0][4]
                                        step_identification = questionnaire_configuration.component.identification
                                        protocol_step_list = \
                                            [header_step_list,
                                             [step_number, step_identification,
                                              path_questionnaire, completed]
                                             ]
                                        questionnaire_response_dic = {
                                            'token_id': token_id,
                                            'questionnaire_id': questionnaire_id,
                                            'questionnaire_code': questionnaire_code,
                                            'data_configuration_tree_id': data_configuration_tree.id,
                                            'subject_id': questionnaire_response.subject_of_group.subject.patient.id,
                                            'subject_code': subject_code,
                                            'directory_step_name': "Step_" + str(step_number) + "_" +
                                                                   component_type.upper(),
                                            'protocol_step_list': protocol_step_list,
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
                                                'header_filtered_list': [],
                                                'token_list': []
                                            }

                                        if token_id not in self.per_group_data[group_id]['questionnaires_per_group'][
                                            questionnaire_id]['token_list']:
                                            self.per_group_data[group_id]['questionnaires_per_group'][questionnaire_id][
                                                'token_list'].append(questionnaire_response_dic)

                    surveys.release_session_key()

                if self.get_input_data('component_list')['per_additional_data']:
                    subject_step_data_query = \
                        SubjectStepData.objects.filter(subject_of_group=subject_of_group,
                                                       data_configuration_tree=None)
                    data_collections = [
                        {'component_configuration': None,
                         'path': None,
                         'subject_step_data': subject_step_data_query[0] if subject_step_data_query else None,
                         'additional_data_list': AdditionalData.objects.filter(
                             subject_of_group=subject_of_group, data_configuration_tree=None),
                         }
                    ]
                    for additional_data_path in create_list_of_trees(group.experimental_protocol, None):
                        component_configuration = ComponentConfiguration.objects.get(pk=additional_data_path[-1][0])
                        data_configuration_tree_id = list_data_configuration_tree(component_configuration.id,
                                                                                  [item[0] for item in
                                                                                   additional_data_path])

                        additional_data_list = None
                        if data_configuration_tree_id:
                            additional_data_list = \
                                AdditionalData.objects.filter(subject_of_group=subject_of_group,
                                                              data_configuration_tree__id=data_configuration_tree_id)

                        data_collections.append(
                            {'component_configuration': component_configuration,
                             'path': path,
                             'subject_step_data': subject_step_data_query[0] if subject_step_data_query else None,
                             'additional_data_list': additional_data_list,
                             'step_number': additional_data_path[-1][-1],
                             }
                        )

                    for data in data_collections:
                        if data['additional_data_list']:
                            if data['component_configuration']:
                                component_type = data['component_configuration'].component.component_type
                                step_number = data['step_number']
                            else:
                                step_number = 0
                                component_type = 'experimental_protocol' # root
                            for additional_data in data['additional_data_list']:
                                subject_code = additional_data.subject_of_group.subject.patient.code
                                additional_data_file_list = []
                                for additional_data_file in additional_data.additional_data_files.all():
                                    additional_data_file_list.append({
                                        'additional_data_filename':
                                            settings.BASE_DIR +
                                            settings.MEDIA_URL +
                                            additional_data_file.file.name
                                    })
                                if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code] = {}

                                if 'additional_data_list' not in self.per_group_data[group_id]['data_per_participant'][
                                        subject_code]:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'additional_data_list'] = []
                                if component_type not in self.per_group_data[group_id]['data_per_participant'][
                                        subject_code]:
                                        self.per_group_data[group_id]['data_per_participant'][subject_code][
                                            component_type] = {'data_index': 1}
                                else:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][component_type][
                                        'data_index'] += 1

                                index = str(self.per_group_data[group_id]['data_per_participant'][subject_code][
                                                component_type]['data_index'])
                                self.per_group_data[group_id]['data_per_participant'][subject_code][
                                    'additional_data_list'].append({
                                        'description': additional_data.description,
                                        'step_number': step_number,
                                        'component_type': component_type,
                                        'directory_step_name': "Step_" + str(step_number) + "_" +
                                                               component_type.upper(),
                                        'additional_data_directory': "AdditionalData_" + index,
                                        'additional_data_file_list': additional_data_file_list,
                                    })

                if self.get_input_data('component_list')['per_eeg_raw_data'] or \
                        self.get_input_data('component_list')['per_eeg_nwb_data']:

                    for path_eeg in create_list_of_trees(group.experimental_protocol, "eeg"):
                        eeg_component_configuration = ComponentConfiguration.objects.get(pk=path_eeg[-1][0])
                        component_step = eeg_component_configuration.component

                        self.per_group_data[group_id]['eeg_default_setting_id'] = \
                            eeg_component_configuration.component.eeg.eeg_setting.id
                        step_number = path_eeg[-1][4]
                        step_identification = path_eeg[-1][3]

                        data_configuration_tree_id = list_data_configuration_tree(eeg_component_configuration.id,
                                                                                  [item[0] for item in path_eeg])

                        eeg_data_list = EEGData.objects.filter(subject_of_group=subject_of_group,
                                                               data_configuration_tree_id=data_configuration_tree_id)
                        eeg_data_list = can_export_nwb(eeg_data_list)

                        for eeg_data in eeg_data_list:
                            subject_code = eeg_data.subject_of_group.subject.patient.code
                            sensors_positions_image = get_sensors_position(eeg_data)
                            sensors_positions_filename = None
                            if sensors_positions_image:
                                sensors_positions_filename = settings.BASE_DIR + str(sensors_positions_image)

                            if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                self.per_group_data[group_id]['data_per_participant'][subject_code] = {}

                            if 'eeg_data_list' not in self.per_group_data[group_id]['data_per_participant'][
                                    subject_code]:
                                self.per_group_data[group_id]['data_per_participant'][subject_code]['eeg_data_list']\
                                    = []
                                self.per_group_data[group_id]['data_per_participant'][subject_code]['data_index'] = 1
                            else:
                                self.per_group_data[group_id]['data_per_participant'][subject_code]['data_index'] += 1
                            index = str(self.per_group_data[group_id]['data_per_participant'][subject_code][
                                            'data_index'])
                            self.per_group_data[group_id]['data_per_participant'][subject_code][
                                'eeg_data_list'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'setting_id': eeg_data.eeg_setting_id,
                                    'sensor_filename': sensors_positions_filename,
                                    'eeg_data_directory_name': "EEGData_" + index,
                                    'data_configuration_tree_id': data_configuration_tree_id,
                                    'directory_step_name': "Step_" + str(step_number) + "_" +
                                                           component_step.component_type.upper(),
                                    'export_nwb': self.get_input_data('component_list')['per_eeg_nwb_data'],
                                    'eeg_file_list': eeg_data.eeg_file_list,
                                })

                if self.get_input_data('component_list')['per_emg_data']:
                    for path_emg in create_list_of_trees(group.experimental_protocol, "emg"):
                        emg_component_configuration = ComponentConfiguration.objects.get(pk=path_emg[-1][0])
                        component_step = emg_component_configuration.component

                        self.per_group_data[group_id]['emg_default_setting_id'] = \
                            emg_component_configuration.component.emg.emg_setting.id

                        step_number = path_emg[-1][4]
                        step_identification = path_emg[-1][3]

                        data_configuration_tree_id = list_data_configuration_tree(emg_component_configuration.id,
                                                                                  [item[0] for item in path_emg])
                        emg_data_list = EMGData.objects.filter(subject_of_group=subject_of_group,
                                                               data_configuration_tree_id=data_configuration_tree_id)

                        for emg_data in emg_data_list:
                            subject_code = emg_data.subject_of_group.subject.patient.code
                            emg_file_list = []
                            for emg_file in emg_data.emg_files.all():
                                emg_file_list.append({
                                    'file_name': settings.BASE_DIR + settings.MEDIA_URL + emg_file.file.name,
                                })

                            if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                self.per_group_data[group_id]['data_per_participant'][subject_code] = {}
                            if 'emg_data_list' not in self.per_group_data[group_id]['data_per_participant'][
                                subject_code]:
                                self.per_group_data[group_id]['data_per_participant'][subject_code]['emg_data_list'] \
                                    = []
                                self.per_group_data[group_id]['data_per_participant'][subject_code]['data_index'] = 1
                            else:
                                self.per_group_data[group_id]['data_per_participant'][subject_code]['data_index'] += 1
                            index = str(self.per_group_data[group_id]['data_per_participant'][subject_code][
                                            'data_index'])
                            self.per_group_data[group_id]['data_per_participant'][subject_code][
                                'emg_data_list'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'emg_data_directory_name': "EMGData_" + index,
                                    'setting_id': emg_data.emg_setting.id,
                                    'directory_step_name': "Step_" + str(step_number) + "_" +
                                                           component_step.component_type.upper(),
                                    'emg_file_list': emg_file_list,
                                })

                if self.get_input_data('component_list')['per_tms_data']:
                    for path_tms in create_list_of_trees(group.experimental_protocol, "tms"):
                        tms_component_configuration = ComponentConfiguration.objects.get(pk=path_tms[-1][0])
                        component_step = tms_component_configuration.component
                        self.per_group_data[group_id]['tms_default_setting_id'] = \
                            tms_component_configuration.component.tms.tms_setting_id

                        step_number = path_tms[-1][4]
                        step_identification = path_tms[-1][3]

                        data_configuration_tree_id = list_data_configuration_tree(tms_component_configuration.id,
                                                                                  [item[0] for item in path_tms])

                        tms_data_list = TMSData.objects.filter(subject_of_group=subject_of_group,
                                                               data_configuration_tree_id=data_configuration_tree_id)

                        for tms_data in tms_data_list:
                            subject_code = tms_data.subject_of_group.subject.patient.code

                            if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                self.per_group_data[group_id]['data_per_participant'][subject_code] = {}
                            if 'tms_data_list' not in self.per_group_data[group_id]['data_per_participant'][
                                subject_code]:
                                self.per_group_data[group_id]['data_per_participant'][subject_code]['tms_data_list'] \
                                    = []

                            self.per_group_data[group_id]['data_per_participant'][subject_code][
                                'tms_data_list'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'setting_id': tms_data.tms_setting_id,
                                    'tms_data_id': tms_data.id,
                                    'data_configuration_tree_id': data_configuration_tree_id,
                                    'directory_step_name': "Step_" + str(step_number) + "_" +
                                                           component_step.component_type.upper()
                                })

                if self.get_input_data('component_list')['per_goalkeeper_game_data']:
                    for path_goalkeeper_game in create_list_of_trees(group.experimental_protocol, "digital_game_phase"):
                        digital_game_component_configuration = ComponentConfiguration.objects.get(
                            pk=path_goalkeeper_game[-1][0])

                        component_step = digital_game_component_configuration.component
                        self.per_group_data[group_id]['context_tree_default_id'] = \
                            digital_game_component_configuration.component.digitalgamephase.context_tree_id

                        step_number = path_goalkeeper_game[-1][4]
                        step_identification = path_goalkeeper_game[-1][3]
                        data_configuration_tree_id = \
                            list_data_configuration_tree(digital_game_component_configuration.id,
                                                         [item[0] for item in path_goalkeeper_game])

                        digital_game_data_list = DigitalGamePhaseData.objects.filter(
                            subject_of_group=subject_of_group, data_configuration_tree_id=data_configuration_tree_id)

                        for digital_game_data in digital_game_data_list:
                            subject_code = digital_game_data.subject_of_group.subject.patient.code
                            digital_game_file_list = []
                            for digital_game_file in digital_game_data.digital_game_phase_files.all():
                                digital_game_file_list.append({
                                    'digital_game_filename': settings.BASE_DIR + settings.MEDIA_URL +
                                                             digital_game_file.file.name
                                })

                            if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                self.per_group_data[group_id]['data_per_participant'][subject_code] = {}

                            if 'digital_game_data_list' not in self.per_group_data[group_id]['data_per_participant'][
                                subject_code]:
                                self.per_group_data[group_id]['data_per_participant'][subject_code][
                                    'digital_game_data_list'] = []
                                self.per_group_data[group_id]['data_per_participant'][subject_code]['data_index'] = 1
                            else:
                                self.per_group_data[group_id]['data_per_participant'][subject_code]['data_index'] += 1
                            index = str(self.per_group_data[group_id]['data_per_participant'][subject_code][
                                            'data_index'])
                            self.per_group_data[group_id]['data_per_participant'][subject_code][
                                'digital_game_data_list'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'directory_step_name': "Step_" + str(step_number) + "_" +
                                                           component_step.component_type.upper(),
                                    'digital_game_data_directory': "DigitalGamePhaseData_" + index,
                                    'digital_game_file_list': digital_game_file_list,
                                })

                if self.get_input_data('component_list')['per_stimulus_data']:
                    for path_stimulus in create_list_of_trees(group.experimental_protocol, "stimulus"):
                        stimulus_component_configuration = ComponentConfiguration.objects.get(pk=path_stimulus[-1][0])

                        component_step = stimulus_component_configuration.component
                        step_number = path_stimulus[-1][4]
                        step_identification = path_stimulus[-1][3]

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
                    for path_generic in create_list_of_trees(group.experimental_protocol, "generic_data_collection"):
                        generic_component_configuration = ComponentConfiguration.objects.get(pk=path_generic[-1][0])
                        component_step = generic_component_configuration.component
                        step_number = path_generic[-1][4]
                        step_identification = path_generic[-1][3]

                        data_configuration_tree_id = \
                            list_data_configuration_tree(generic_component_configuration.id, [item[0] for item in
                                                                                              path_generic])
                        generic_data_collection_data_list = GenericDataCollectionData.objects.filter(
                            subject_of_group=subject_of_group, data_configuration_tree__id=data_configuration_tree_id)

                        for generic_data_collection_data in generic_data_collection_data_list:
                            subject_code = generic_data_collection_data.subject_of_group.subject.patient.code
                            generic_data_collection_data_list = []
                            for generic_data in generic_data_collection_data.generic_data_collection_files.all():
                                generic_data_collection_data_list.append({
                                    'generic_data_filename': settings.BASE_DIR + settings.MEDIA_URL +
                                                             generic_data.file.name,
                                })

                            if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                self.per_group_data[group_id]['data_per_participant'][subject_code] = {}

                            if 'generic_data_collection_data_list' not in self.per_group_data[group_id][
                                    'data_per_participant'][subject_code]:
                                self.per_group_data[group_id]['data_per_participant'][subject_code][
                                    'generic_data_collection_data_list'] = []
                                self.per_group_data[group_id]['data_per_participant'][subject_code]['data_index'] = 1
                            else:
                                self.per_group_data[group_id]['data_per_participant'][subject_code]['data_index'] += 1
                            index = str(self.per_group_data[group_id]['data_per_participant'][subject_code][
                                            'data_index'])
                            self.per_group_data[group_id]['data_per_participant'][subject_code][
                                'generic_data_collection_data_list'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'directory_step_name': "Step_" + str(step_number) + "_" +
                                                           component_step.component_type.upper(),
                                    'generic_data_collection_directory': "Generic_Collection_Data_" + index,
                                    'generic_data_collection_file_list': generic_data_collection_data_list,
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

    def get_participant_row_data(self, subject_code):
        participant_rows = []
        participant_data_list = self.get_input_data('participants')['data_list']
        header = participant_data_list[0]
        for sublist in participant_data_list[1:len(participant_data_list)]:
            if subject_code in sublist:
                participant_rows.append(sublist)
                participant_rows.insert(0, header)

        return participant_rows

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

    def get_participants_filtered_data(self):

        return self.participants_filtered_data

    def update_questionnaire_rules(self, questionnaire_id):

        header = []
        fields = []

        heading_type = self.get_heading_type()

        for row in included_questionnaire_fields:
            header_translated = _(row["header"][heading_type])
            header.append(smart_str(header_translated))
            fields.append(smart_str(row["field"]))

        self.questionnaire_utils.append_questionnaire_header_and_field(
            questionnaire_id, header, fields,
            self.get_input_data('questionnaires'),
            self.get_input_data('questionnaires_from_experiment'))

    def update_questionnaire_experiment_rules(self, questionnaire_id):

        header = []
        fields = []

        heading_type = self.get_heading_type()

        for row in included_questionnaire_fields:
            header_translated = _(row["header"][heading_type])
            header.append(smart_str(header_translated))
            fields.append(smart_str(row["field"]))

        self.questionnaire_utils.append_questionnaire_experiment_header_and_field(questionnaire_id, header, fields)

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
            questionnaire_id = self.questionnaire_utils.get_questionnaire_id_from_code(questionnaire_code)

        if questionnaire_id:
            title = self.get_title(questionnaire_id)

        if title:
            reduced_title = slugify(title)

        return reduced_title

    @staticmethod
    def redefine_questionnaire_title(title):
        reduced_title = ''
        if title:
            reduced_title = slugify(title)

        return reduced_title

    @staticmethod
    def build_header_questionnaire_per_participant(
            header_participant_data, header_answer_list
    ):
        header = []
        for field in header_participant_data[0:2]:
            header.append(field)
        for field in header_answer_list:
            header.append(field)
        for field in header_participant_data[2:len(header_participant_data)]:
            header.append(field)

        return header

    @staticmethod
    def merge_questionnaire_answer_list_per_participant(row_participant_data, answer_list):
        questionnaire_answer_list = []

        # building questionnaire_answer_list with row_participant data
        subject_code = row_participant_data[0]
        age = row_participant_data[1]
        for sublist in answer_list:
            answer = [subject_code, age]
            for item in sublist:
                answer.append(item)
            for item in row_participant_data[2:len(row_participant_data)]:
                answer.append(item)
            questionnaire_answer_list.append(answer)

        return questionnaire_answer_list

    def merge_participants_data_per_questionnaire_process(self, fields_description, participant_list):
        # get fields from patient
        export_participant_row = self.process_participant_data(self.get_input_data('participants'), participant_list)

        # merge fields from questionnaires and patient
        export_fields_list = []
        # building the header
        export_row_list = fields_description[0][0:len(fields_description[0]) - 1]
        for field in export_participant_row[0]:
            export_row_list.append(field)
        export_fields_list.append(export_row_list)

        # including the responses
        for fields in fields_description[1:fields_description.__len__()]:
            participation_code = fields[len(fields) - 1]
            export_row_list = fields[0:len(fields) - 1]
            for participant_fields in export_participant_row[1:export_participant_row.__len__()]:
                if participation_code == participant_fields[len(participant_fields) - 1]:
                    for field in participant_fields:
                        export_row_list.append(field)
            export_fields_list.append(export_row_list)

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
            error_msg, path_per_questionnaire = create_directory(
                self.get_export_directory(),
                self.get_input_data("per_questionnaire_directory")
            )
            if error_msg != "":
                return error_msg
            export_per_questionnaire_directory = path.join(self.get_input_data("base_directory"),
                                                           self.get_input_data("per_questionnaire_directory"))
            export_metadata_directory = path.join(self.get_input_data("base_directory"),
                                                  self.get_input_data("questionnaire_metadata_directory"))
            error_msg, path_per_questionnaire_metadata = create_directory(
                self.get_export_directory(), self.get_input_data("questionnaire_metadata_directory"))
            if error_msg != "":
                return error_msg

        questionnaire_lime_survey = Questionnaires()

        for questionnaire in self.get_input_data("questionnaires"):

            questionnaire_id = questionnaire["id"]
            # if it was selected ful answer for questionnaire responses
            questionnaire_language = self.get_input_data("questionnaire_language")[str(questionnaire_id)]
            if 'long' in self.get_input_data('response_type'):
                language_list = questionnaire_language['language_list']
            else:
                language_list = [questionnaire_language['output_language']]

            questionnaire_code = self.questionnaire_utils.get_questionnaire_code_from_id(questionnaire_id)
            questionnaire_title = self.get_title_reduced(questionnaire_id=questionnaire_id)
            # ex. Per_questionnaire.Q123_aaa
            path_questionnaire = "%s_%s" % (str(questionnaire_code), questionnaire_title)

            # path ex. /.../media/NES_EXPORT/Per_questionnaire/Q123_aaa
            error_msg, export_path = create_directory(path_per_questionnaire, path_questionnaire)
            if error_msg != "":
                return error_msg

            # path ex. /NES_EXPORT/Per_questionnaire/Q123_aaa/
            export_directory = path.join(export_per_questionnaire_directory, path_questionnaire)

            # path ex. /NES_EXPORT/Questionnaire_metadata/Q123_aaa
            error_msg, export_metadata_path = create_directory(path_per_questionnaire_metadata, path_questionnaire)
            if error_msg != "":
                return error_msg

            # path: /NES_EXPORT/Questionnaire_metadata/Q123_aaa
            export_questionnaire_metadata_directory = path.join(export_metadata_directory, path_questionnaire)

            # print(questionnaire_id)
            for language in language_list:
                # Per_participant_data is updated by define_questionnaire
                # method
                fields_description = self.define_questionnaire(questionnaire, questionnaire_lime_survey, language)

                # create directory for questionnaire:
                # <per_questionnaire>/<q_code_title>
                if self.get_input_data("export_per_questionnaire") and (len(fields_description) > 1):
                    export_filename = \
                        "%s_%s_%s.csv" % (questionnaire["prefix_filename_responses"], str(questionnaire_code), language)
                    # path ex. media/NES_EXPORT/Per_questionnaire.Q123_aaa/Responses_Q123.csv
                    complete_filename = path.join(export_path, export_filename)

                    save_to_csv(complete_filename, fields_description)
                    self.files_to_zip_list.append([complete_filename, export_directory])

            # questionnaire metadata
            entrance_questionnaire = True
            # create questionnaire fields file ("fields.csv") - metadata
            # directory
            fields = self.questionnaire_utils.get_questionnaire_fields(
                questionnaire_id, entrance_questionnaire, self.get_input_data('questionnaires_from_experiments'))

            for language in questionnaire_language['language_list']:
                    questionnaire_fields = \
                        self.questionnaire_utils.create_questionnaire_explanation_fields(
                            questionnaire_id, language,
                            questionnaire_lime_survey, fields,
                            entrance_questionnaire
                        )

                    export_filename = "%s_%s_%s.csv" % (questionnaire["prefix_filename_fields"],
                                                        str(questionnaire_code), language)

                    complete_filename = path.join(export_metadata_path, export_filename)

                    save_to_csv(complete_filename, questionnaire_fields)

                    self.files_to_zip_list.append([complete_filename, export_questionnaire_metadata_directory])

        questionnaire_lime_survey.release_session_key()

        return error_msg

    def process_per_entrance_questionnaire(self):
        path_participant_data = path.join(
            self.get_export_directory(),
            self.get_input_data("participant_data_directory")
        )
        if not path.exists(path_participant_data):
            # path ex. /NES_EXPORT/Participant_data
            error_msg, path_participant_data = create_directory(
                self.get_export_directory(),
                self.get_input_data("participant_data_directory")
            )
            if error_msg != "":
                return error_msg

        # path NES_EXPORT/Participant_data/Per_questionnaire
        error_msg, path_per_questionnaire = create_directory(
            path_participant_data,
            self.get_input_data("per_questionnaire_directory")
        )
        if error_msg != "":
            return error_msg

        # path /NES_EXPORT/Participant_data/Questionnaire_metadata/
        error_msg, path_per_questionnaire_metadata = create_directory(
            path_participant_data,
            self.get_input_data("questionnaire_metadata_directory")
        )
        if error_msg != "":
            return error_msg

        # path /NES_EXPORT/Participant_data/
        export_per_entrance_questionnaire_directory = path.join(
            self.get_input_data("base_directory"),
            self.get_input_data("participant_data_directory")
        )
        # path /NES_EXPORT/Participant_data/Per_questionnaire/
        export_per_questionnaire_directory = path.join(
            export_per_entrance_questionnaire_directory,
            self.get_input_data("per_questionnaire_directory")
        )

        # path /NES_EXPORT/Participant_data/Questionnaire_metadata/
        export_metadata_directory = path.join(
            export_per_entrance_questionnaire_directory,
            self.get_input_data("questionnaire_metadata_directory")
        )

        questionnaire_lime_survey = Questionnaires()

        for questionnaire in self.get_input_data("questionnaires"):
            questionnaire_id = questionnaire["id"]
            questionnaire_code = \
                self.questionnaire_utils.get_questionnaire_code_from_id(questionnaire_id)
            questionnaire_title = \
                self.get_title_reduced(questionnaire_id=questionnaire_id)
            path_questionnaire = \
                "%s_%s" % (str(questionnaire_code), questionnaire_title)

            # path ex. /NES_EXPORT/Participant_data/Per_questionnaire/Q123_aaa/
            error_msg, export_path = create_directory(
                path_per_questionnaire, path_questionnaire
            )
            if error_msg != "":
                return error_msg
            # path /NES_EXPORT/Participant_data/Per_questionnaire/Q123_aaa/
            export_directory = path.join(
                export_per_questionnaire_directory, path_questionnaire
            )

            # path /NES_EXPORT/Participant_data/Questionnaire_metadata/Q123_aaa
            error_msg, export_metadata_path = create_directory(
                path_per_questionnaire_metadata,
                path_questionnaire
            )
            if error_msg != "":
                return error_msg

            # path /NES_EXPORT/Participant_data/Questionnaire_metadata/Q123_aaa/
            export_questionnaire_metadata_directory = path.join(
                export_metadata_directory, path_questionnaire
            )

            # defining language to be displayed
            questionnaire_language = \
                self.get_input_data("questionnaire_language")[str(questionnaire_id)]
            if 'long' in self.get_input_data('response_type'):
                language_list = questionnaire_language['language_list']
            else:
                language_list = [questionnaire_language['output_language']]
            for language in language_list:
                # per_participant_data is updated by define_questionnaire
                # method
                fields_description = self.define_questionnaire(
                    questionnaire, questionnaire_lime_survey, language
                )
                if self.get_input_data("export_per_questionnaire") and \
                        (len(fields_description) > 1):
                    export_filename = "%s_%s_%s.csv" % \
                                      (questionnaire["prefix_filename_responses"],
                                       str(questionnaire_code), language)
                    # /NES_EXPORT/Participant_data/Per_questionnaire/Q123_aaa/Responses_Q123.csv
                    complete_filename = path.join(export_path, export_filename)

                    save_to_csv(complete_filename, fields_description)
                    self.files_to_zip_list.append([complete_filename, export_directory])

            entrance_questionnaire = True

            # create questionnaire fields file ("fields.csv") in
            # Questionnaire_metadata directory
            fields = self.questionnaire_utils.get_questionnaire_fields(
                questionnaire_id, entrance_questionnaire,
                self.get_input_data('questionnaires_from_experiments')
            )

            for language in questionnaire_language['language_list']:
                questionnaire_fields = \
                    self.questionnaire_utils.create_questionnaire_explanation_fields(
                        questionnaire_id, language,
                        questionnaire_lime_survey, fields,
                        entrance_questionnaire
                    )

                export_filename = "%s_%s_%s.csv" % \
                                  (questionnaire["prefix_filename_fields"],
                                   str(questionnaire_code), language)

                # path ex. /NES_EXPORT/Participant_data/Questionnaire_metadata/Q123_aaa/Fields_Q123.csv'
                complete_filename = path.join(
                    export_metadata_path, export_filename
                )
                save_to_csv(complete_filename, questionnaire_fields)
                self.files_to_zip_list.append(
                    [complete_filename, export_questionnaire_metadata_directory]
                )

        questionnaire_lime_survey.release_session_key()

        return error_msg

    def create_group_data_directory(self):
        # path ex. /NES_EXPORT/Experiment_data
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
                # ex. NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire
                error_msg, directory_questionnaire_data = create_directory(
                    directory_group, self.get_input_data("per_questionnaire_directory"))
                if error_msg != "":
                    return error_msg
                # path ex. NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire/
                export_directory_questionnaire_data = path.join(
                    export_directory_group, self.get_input_data("per_questionnaire_directory"))

                # ex. NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata
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
        error_msg = ''

        for group_id in self.per_group_data:
            if 'questionnaires_per_group' in self.per_group_data[group_id]:
                questionnaire_list = \
                    self.per_group_data[group_id]['questionnaires_per_group']
                for questionnaire_id in questionnaire_list:

                    # create questionnaire_name_directory
                    questionnaires = questionnaire_list[questionnaire_id]
                    dir_questionnaire_step = dict()
                    dir_questionnaire_step[questionnaire_id] = set()

                    questionnaire_data = \
                        self.get_input_data('questionnaires_from_experiments')[
                            group_id][str(questionnaire_id)]
                    questionnaire_code = questionnaires['questionnaire_code']
                    questionnaire_title = self.redefine_questionnaire_title(
                        questionnaire_data['questionnaire_name']
                    )

                    questionnaire_prefix_filename = questionnaire_data[
                        'prefix_filename_responses']
                    prefix_filename_fields = questionnaire_data[
                        'prefix_filename_fields']
                    # Ex. Q123_aaa
                    directory_questionnaire_name = "%s_%s" % (
                        str(questionnaire_code), questionnaire_title
                    )

                    # metadata directory para export
                    # ex.: 'NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata/'
                    metadata_directory = \
                    self.per_group_data[group_id]['group'][
                        'questionnaire_metadata_directory']
                    # Ex. 'NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata/Q123_aaa/'
                    export_metadata_directory = path.join(
                        self.per_group_data[group_id]['group'][
                            'questionnaire_metadata_export_directory'],
                        directory_questionnaire_name)
                    # path ex. /NES_EXPORT/Experiment_data/Group_xxx/Questionnaire_metadata/Q123_aaa/
                    error_msg, complete_export_metadata_path = create_directory(
                        metadata_directory,
                        directory_questionnaire_name
                    )
                    if error_msg != "":
                        return error_msg

                    questionnaire_language = \
                        self.get_input_data("questionnaire_language")[
                            str(questionnaire_id)]
                    if 'long' in self.get_input_data('response_type'):
                        language_list = questionnaire_language['language_list']
                    else:
                        language_list = [
                            questionnaire_language['output_language']]

                    # getting unique steps for each questionnaire so we can
                    # aggregate directories by steps if there are same
                    # questionnaire in more than one step
                    for token in questionnaires['token_list']:
                        dir_questionnaire_step[questionnaire_id].add(
                            token['directory_step_name']
                        )

                    for token in questionnaires['token_list']:
                        path_group_per_questionnaire = \
                            self.per_group_data[group_id]['group'][
                                'questionnaire_data_directory']
                        error_msg, complete_export_path = create_directory(
                            path_group_per_questionnaire,
                            token['directory_step_name']
                        )
                        if error_msg != '':
                            return error_msg

                        export_directory_per_questionnaire = \
                            self.per_group_data[group_id]['group'][
                            'questionnaire_data_export_directory']
                        export_directory = path.join(
                            export_directory_per_questionnaire,
                            token['directory_step_name']
                        )

                        # save file with data
                        fields_description = []

                        for language in language_list:
                            # Q123_<questionnaire_title>_<lang>.csv
                            export_filename = "%s_%s_%s.csv" % (
                                str(questionnaire_code), questionnaire_title,
                                language
                            )
                            # NES_EXPORT/Experiment_data/Group_xxx/Per_questionnaire/Step_x_QUESTIONNAIRE/Q123_<questionnaire_title>_<lang>.csv
                            complete_filename = path.join(
                                complete_export_path, export_filename
                            )
                            token_id = token['token_id']
                            answer_list = self.questionnaires_responses[str(questionnaire_id)][token_id][language]
                            rows_participant_data = \
                                self.get_participant_row_data(
                                    token['subject_code']
                                )
                            participant_response_list = \
                                self.merge_questionnaire_answer_list_per_participant(
                                    rows_participant_data[1],
                                    answer_list[1:len(answer_list)]
                                )
                            for sublist in participant_response_list:
                                index = len(fields_description) + 1
                                fields_description.insert(index, sublist)

                        # header
                        if fields_description:
                            header = \
                                self.build_header_questionnaire_per_participant(
                                    rows_participant_data[0],
                                    answer_list[0]
                                )
                            fields_description.insert(0, header)

                            ###
                            # Jury-rig detected!
                            file_exists = False
                            for item in self.files_to_zip_list:
                                if complete_filename in item[0]:
                                    # Append in complete_filename
                                    # fields_description in the file that
                                    # already exists
                                    save_to_csv(complete_filename,
                                                fields_description[1:],
                                                mode='a')
                                    file_exists = True
                                    break
                            #
                            ###

                            # save array list into a file to export
                            if not file_exists:
                                save_to_csv(complete_filename, fields_description)
                                self.files_to_zip_list.append(
                                    [complete_filename, export_directory]
                                )

                    # questionnaire metadata directory
                    entrance_questionnaire = False
                    questionnaire_lime_survey = Questionnaires()
                    # create questionnaire fields file ("fields.csv") in
                    # Questionnaire_metadata directory
                    fields = self.questionnaire_utils.get_questionnaire_experiment_fields(questionnaire_id)
                    for language in questionnaire_language['language_list']:
                        questionnaire_fields = self.questionnaire_utils.create_questionnaire_explanation_fields(
                            str(questionnaire_id), language, questionnaire_lime_survey, fields, entrance_questionnaire)

                        # # build metadata export - Fields_Q123.csv
                        export_filename = "%s_%s_%s.csv" % (prefix_filename_fields, str(questionnaire_code),
                                                            language)

                        complete_filename = path.join(complete_export_metadata_path, export_filename)

                        save_to_csv(complete_filename, questionnaire_fields)

                        self.files_to_zip_list.append([complete_filename, export_metadata_directory])

                    questionnaire_lime_survey.release_session_key()

        return error_msg

    def process_per_participant(self):

        error_msg = ''

        if self.get_input_data("export_per_participant"):
            # path ex. /NES_EXPORT/Per_participant/
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
                # path ex. /NES_EXPORT/Per_participant/Participant_P123/
                error_msg, participant_path = create_directory(path_per_participant, path_participant)
                if error_msg != "":
                    return error_msg

                for questionnaire_code in self.get_per_participant_data(participant_code):
                    questionnaire_id = int(self.questionnaire_utils.get_questionnaire_id_from_code(questionnaire_code))
                    title = self.get_title_reduced(questionnaire_id=int(questionnaire_id))
                    questionnaire_directory_name = "%s_%s" % (str(questionnaire_code), title)
                    # create questionnaire directory
                    # path ex. /NES_EXPORT/Per_participant/Participant_PCode/QCode_Title/
                    error_msg, path_per_questionnaire = create_directory(participant_path, questionnaire_directory_name)
                    # path ex. /NES_EXPORT/Per_participant/QCode_Title/
                    export_questionnaire_directory = path.join(path.join(export_directory_base, path_participant),
                                                               questionnaire_directory_name)

                    # add participant personal data header
                    questionnaire_header = self.questionnaire_utils.get_header_questionnaire(questionnaire_id)
                    participant_data_header = self.get_input_data('participants')['data_list'][0]
                    header = self.build_header_questionnaire_per_participant(
                        participant_data_header,
                        questionnaire_header[0:len(questionnaire_header)-1]
                    )

                    # select language list
                    questionnaire_language = self.get_input_data("questionnaire_language")[str(questionnaire_id)]
                    if 'long' in self.get_input_data('response_type'):
                        language_list = questionnaire_language['language_list']
                    else:
                        language_list = [questionnaire_language['output_language']]

                    for language in language_list:
                        export_filename = "%s_%s_%s.csv" % ("Responses", str(questionnaire_code), language)

                        participant_rows = self.get_per_participant_data(participant_code, questionnaire_code)[
                            language][0]
                        per_participant_rows = [header, participant_rows]

                        # path ex. /NES_EXPORT/Per_participant/Participant_P123/QCode_Title
                        # /Responses_Q123_aaa.csv
                        complete_filename = path.join(path_per_questionnaire, export_filename)

                        save_to_csv(complete_filename, per_participant_rows)

                        self.files_to_zip_list.append([complete_filename, export_questionnaire_directory])

        return error_msg

    def process_per_participant_per_entrance_questionnaire(self):
        # path ex. /NES_EXPORT/Participant_data/
        path_participant_data = path.join(
            self.get_export_directory(),
            self.get_input_data("participant_data_directory")
        )
        # path ex. /NES_EXPORT/Participant_data/Per_participant/
        error_msg, path_per_participant = create_directory(
            path_participant_data,
            self.get_input_data("per_participant_directory")
        )
        if error_msg != "":
            return error_msg

        prefix_filename_participant = "Participant_"
        # path ex. /NES_EXPORT/Participant_data/Per_participant/
        export_participant_data = path.join(
            self.get_input_data("base_directory"),
            self.get_input_data("participant_data_directory")
        )
        # path ex. /NES_EXPORT/Participant_data/Per_participant/
        export_directory_base = path.join(export_participant_data, self.get_input_data("per_participant_directory"))

        for participant_code in self.get_per_participant_data():
            patient_id = \
                Patient.objects.filter(code=participant_code).values('id')[0]['id']
            path_participant = prefix_filename_participant + \
                               str(participant_code)
            # /NES_EXPORT/Participant_data/Per_participant/Participant_P123/
            error_msg, participant_path = create_directory(
                path_per_participant, path_participant
            )
            if error_msg != "":
                return error_msg

            for questionnaire_code in \
                    self.get_per_participant_data(participant_code):
                if self.participants_per_entrance_questionnaire[questionnaire_code]:
                    if patient_id in \
                            self.participants_per_entrance_questionnaire[questionnaire_code]:
                        questionnaire_id = \
                            int(self.questionnaire_utils.get_questionnaire_id_from_code(questionnaire_code))
                        # select entry questionnaires' participants
                        for questionnaire in \
                                self.get_input_data("questionnaires"):
                            if questionnaire_id == questionnaire['id']:
                                title = self.get_title_reduced(
                                    questionnaire_id=questionnaire_id
                                )
                                questionnaire_language = \
                                    self.get_input_data("questionnaire_language")[str(questionnaire_id)]
                                if 'long' in \
                                        self.get_input_data('response_type'):
                                    language_list = questionnaire_language['language_list']
                                else:
                                    language_list = [questionnaire_language['output_language']]
                                # create questionnaire directory
                                path_questionnaire = "%s_%s" % (str(questionnaire_code), title)
                                # /NES_EXPORT/Participant_data/Per_participant/Participant_P123/Q123_title
                                error_msg, questionnaire_path_directory = create_directory(participant_path,
                                                                                           path_questionnaire)
                                if error_msg != '':
                                    return error_msg
                                export_participant_directory = path.join(export_directory_base, path_participant)
                                # NES_EXPORT/Participant_data/Per_participant/Participant_P123/Q123_title
                                export_directory = path.join(export_participant_directory, path_questionnaire)

                                for language in language_list:
                                    export_filename = \
                                        "%s_%s_%s.csv" % \
                                        (questionnaire["prefix_filename_responses"],
                                         str(questionnaire_code), language)

                                    # add participant personal data header
                                    questionnaire_header = \
                                        self.questionnaire_utils.get_header_questionnaire(
                                            questionnaire_id
                                        )
                                    participant_data_header = \
                                        self.get_input_data('participants')['data_list'][0]
                                    header = \
                                        self.build_header_questionnaire_per_participant(
                                            participant_data_header,
                                            questionnaire_header[0:len(questionnaire_header) - 1]
                                        )

                                    per_participant_rows = self.per_participant_data[participant_code][
                                        questionnaire_code][language]
                                    per_participant_rows.insert(0, header)
                                    # path ex. /NES_EXPORT/Participant_data/Per_participant/Q123_title
                                    complete_filename = path.join(questionnaire_path_directory, export_filename)

                                    save_to_csv(complete_filename, per_participant_rows)

                                    self.files_to_zip_list.append([complete_filename, export_directory])

        return error_msg

    def process_per_participant_per_experiment(self):

        error_msg = ''

        for group_id in self.per_group_data:
            participant_list = self.per_group_data[group_id]['data_per_participant']
            # participant data
            for participant_code in participant_list:
                prefix_filename_participant = "Participant_"
                # ex. Participant_P123
                participant_name = prefix_filename_participant + str(participant_code)
                participant_data_directory = self.per_group_data[group_id]['group']['participant_data_directory']
                # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                path_per_participant = path.join(participant_data_directory, participant_name)

                # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                participant_data_export_directory = self.per_group_data[group_id]['group'][
                    'participant_data_export_directory']
                participant_export_directory = path.join(participant_data_export_directory, participant_name)
                if 'token_list' in participant_list[participant_code] and self.get_input_data('export_per_participant'):
                    # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    for token_data in participant_list[participant_code]['token_list']:
                        questionnaire_code = token_data['questionnaire_code']
                        questionnaire_id = token_data['questionnaire_id']
                        questionnaire_title = self.get_input_data('questionnaires_from_experiments')[group_id][
                            str(questionnaire_id)]['questionnaire_name']
                        # ex. NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_Questionnaire
                        error_msg, directory_step_participant = \
                            create_directory(
                                path_per_participant,
                                token_data['directory_step_name']
                            )
                        if error_msg != "":
                            return error_msg

                        # ex. NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_Questionnaire
                        step_participant_export_directory = path.join(
                            participant_export_directory,
                            token_data['directory_step_name']
                        )
                        # select questionnaire language
                        questionnaire_language = self.get_input_data("questionnaire_language")[str(questionnaire_id)]
                        if 'long' in self.get_input_data('response_type'):
                            language_list = questionnaire_language['language_list']
                        else:
                            language_list = [questionnaire_language['output_language']]
                        for language in language_list:
                            # Responses_Q123.csv
                            export_filename = "%s_%s_%s.csv" % (str(questionnaire_code), slugify(questionnaire_title), language)

                            # ex. /NES_EXPORT/Experiment_data/Group_xxx/Per_participant/Per_participant/Participant_P123/Step_X_aaa/P123_Q123_aaa.csv
                            complete_filename = path.join(directory_step_participant, export_filename)

                            export_rows_participants = self.get_participant_row_data(token_data['subject_code'])

                            # questionnaire response by participant
                            token_id = token_data['token_id']
                            answer_list = self.questionnaires_responses[str(questionnaire_id)][token_id][language]

                            per_participant_rows = self.merge_questionnaire_answer_list_per_participant(
                                export_rows_participants[1], answer_list[1: len(answer_list)])

                            header = \
                                self.build_header_questionnaire_per_participant(
                                    export_rows_participants[0],
                                    answer_list[0]
                                )
                            per_participant_rows.insert(0, header)

                            save_to_csv(complete_filename, per_participant_rows)

                            self.files_to_zip_list.append([complete_filename, step_participant_export_directory])

                # for component_list
                if 'eeg_data_list' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    eeg_data_list = self.per_group_data[group_id]['data_per_participant'][participant_code]['eeg_data_list']
                    for eeg_data in eeg_data_list:
                        if eeg_data['eeg_file_list']:
                            directory_step_name = eeg_data['directory_step_name']
                            path_per_eeg_participant = path.join(path_per_participant, directory_step_name)
                            if not path.exists(path_per_eeg_participant):
                                # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                                error_msg, path_per_eeg_participant = create_directory(path_per_participant,
                                                                                       directory_step_name)
                                if error_msg != "":
                                    return error_msg

                            # /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                            export_eeg_step_directory = path.join(participant_export_directory, directory_step_name)

                            # to create EEGData directory
                            directory_data_name = eeg_data['eeg_data_directory_name']
                            path_per_eeg_data = path.join(path_per_eeg_participant, directory_data_name)
                            if not path.exists(path_per_eeg_data):
                                # ex. NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_aaa/EEGDATA_#
                                error_msg, path_per_eeg_data = create_directory(path_per_eeg_participant,
                                                                                directory_data_name)
                                if error_msg != "":
                                    return error_msg

                            # ex. NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                            # /EEGData_#
                            export_eeg_data_directory = path.join(export_eeg_step_directory, directory_data_name)

                            eeg_setting_description = get_eeg_setting_description(eeg_data['setting_id'])

                            if eeg_setting_description:
                                eeg_setting_filename = "%s.json" % "eeg_setting_description"

                                # ex. NES_EXPORT/Experiment_data/Group_xxxx/eeg_setting_description.json
                                complete_setting_filename = path.join(path_per_eeg_data, eeg_setting_filename)

                                self.files_to_zip_list.append([complete_setting_filename, export_eeg_data_directory])

                                with open(complete_setting_filename.encode('utf-8'), 'w', newline='',
                                          encoding='UTF-8') as outfile:
                                    json.dump(eeg_setting_description, outfile, indent=4)

                            # if sensor position image exist
                            sensors_positions_image = eeg_data['sensor_filename']
                            if sensors_positions_image:
                                sensor_position_filename = "%s.png" % "sensor_position"

                                complete_sensor_position_filename = path.join(path_per_eeg_data,
                                                                              sensor_position_filename)

                                with open(sensors_positions_image, 'rb') as f:
                                    data = f.read()

                                with open(complete_sensor_position_filename, 'wb') as f:
                                    f.write(data)

                                self.files_to_zip_list.append([complete_sensor_position_filename,
                                                               export_eeg_data_directory])

                            for eeg_file in eeg_data['eeg_file_list']:
                                path_eeg_data_file = settings.BASE_DIR + settings.MEDIA_URL + eeg_file.file.name

                                eeg_data_filename = eeg_file.file.name.split('/')[-1]
                                complete_eeg_data_filename = path.join(path_per_eeg_data, eeg_data_filename)

                                with open(path_eeg_data_file, 'rb') as f:
                                    data = f.read()

                                with open(complete_eeg_data_filename, 'wb') as f:
                                    f.write(data)

                                self.files_to_zip_list.append([complete_eeg_data_filename, export_eeg_data_directory])

                                # v1.5
                                # can export to nwb?
                                if eeg_file.can_export_to_nwb:
                                    process_requisition = int(random.random() * 10000)
                                    eeg_file_name = eeg_data_filename.split('.')[0]
                                    nwb_file_name = "%s.nwb" % eeg_file_name
                                    complete_nwb_file_name = path.join(path_per_eeg_data, nwb_file_name)
                                    req = None

                                    # was it open properly?
                                    ok_opening = False

                                    if eeg_file.eeg_reading.file_format:
                                        if eeg_file.eeg_reading.file_format.nes_code == "MNE-RawFromEGI":
                                            ok_opening = True

                                    if ok_opening:
                                        complete_nwb_file_name = create_nwb_file(eeg_file.eeg_data,
                                                                                 eeg_file.eeg_reading,
                                                                                 process_requisition, req,
                                                                                 complete_nwb_file_name)
                                        if complete_nwb_file_name:
                                            self.files_to_zip_list.append([complete_nwb_file_name,
                                                                           export_eeg_data_directory])
                                        else:
                                            return error_msg

                if 'emg_data_list' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    emg_data_list = self.per_group_data[group_id]['data_per_participant'][participant_code][
                        'emg_data_list']
                    for emg_data in emg_data_list:
                        if emg_data['emg_file_list']:
                            directory_step_name = emg_data['directory_step_name']
                            path_per_emg_participant = path.join(path_per_participant, directory_step_name)
                            if not path.exists(path_per_emg_participant):
                                # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_aaa
                                error_msg, path_per_emg_participant = create_directory(path_per_participant,
                                                                                       directory_step_name)
                                if error_msg != "":
                                    return error_msg

                            # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                            export_emg_step_directory = path.join(participant_export_directory, directory_step_name)

                            # to create EMGData directory
                            directory_data_name = emg_data['emg_data_directory_name']
                            path_per_emg_data = path.join(path_per_emg_participant, directory_data_name)
                            if not path.exists(path_per_emg_data):
                                # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_aaa/EMGDATA_#
                                error_msg, path_per_emg_data = create_directory(path_per_emg_participant,
                                                                                directory_data_name)
                                if error_msg != "":
                                    return error_msg

                            # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                            # /EMGData_#
                            export_emg_data_directory = path.join(export_emg_step_directory, directory_data_name)

                            for emg_file in emg_data['emg_file_list']:
                                path_emg_data_file = emg_file['file_name']

                                emg_data_filename = path_emg_data_file.split('/')[-1]
                                complete_emg_data_filename = path.join(path_per_emg_data, emg_data_filename)

                                with open(path_emg_data_file, 'rb') as f:
                                    data = f.read()

                                with open(complete_emg_data_filename, 'wb') as f:
                                    f.write(data)

                                self.files_to_zip_list.append([complete_emg_data_filename, export_emg_data_directory])

                            # Create documento json with emg settings
                            emg_setting_description = get_emg_setting_description(emg_data['setting_id'])

                            if emg_setting_description:

                                emg_setting_filename = "%s.json" % "emg_setting_description"

                                # ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/
                                # emg_setting_description.txt #
                                complete_setting_filename = path.join(path_per_emg_data, emg_setting_filename)

                                self.files_to_zip_list.append([complete_setting_filename, export_emg_data_directory])

                                with open(complete_setting_filename.encode('utf-8'), 'w', newline='',
                                          encoding='UTF-8') as outfile:
                                    json.dump(emg_setting_description, outfile, indent=4)

                if 'tms_data_list' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    tms_data_list = self.per_group_data[group_id]['data_per_participant'][participant_code][
                        'tms_data_list']
                    for tms_data in tms_data_list:
                        tms_data_description = get_tms_data_description(tms_data['tms_data_id'])
                        if tms_data_description:
                            directory_step_name = tms_data['directory_step_name']
                            path_per_tms_participant = path.join(path_per_participant, directory_step_name)
                            if not path.exists(path_per_tms_participant):
                                # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_aaa
                                error_msg, path_per_tms_participant = create_directory(path_per_participant,
                                                                                       directory_step_name)
                                if error_msg != "":
                                    return error_msg

                            # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                            export_tms_step_directory = path.join(participant_export_directory, directory_step_name)

                            tms_data_filename = "%s.json" % "tms_data_description"
                            # ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/tms_data_description.txt
                            complete_data_filename = path.join(path_per_tms_participant, tms_data_filename)

                            self.files_to_zip_list.append([complete_data_filename, export_tms_step_directory])

                            with open(complete_data_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as \
                                    outfile:
                                json.dump(tms_data_description, outfile, indent=4)

                            # TMS hotspot position image file
                            tms_data = get_object_or_404(TMSData, pk=tms_data['tms_data_id'])

                            if hasattr(tms_data, 'hotspot'):
                                hotspot_image = tms_data.hotspot.hot_spot_map.name
                                if hotspot_image:
                                    hotspot_map_filename = "%s.png" % "hotspot_map"
                                    complete_hotspot_filename = path.join(path_per_tms_participant,
                                                                          hotspot_map_filename)
                                    path_hot_spot_image = path.join(settings.BASE_DIR, "media") + "/" + hotspot_image
                                    with open(path_hot_spot_image, 'rb') as f:
                                        data = f.read()

                                    with open(complete_hotspot_filename, 'wb') as f:
                                        f.write(data)

                                    self.files_to_zip_list.append([complete_hotspot_filename,
                                                                   export_tms_step_directory])

                if 'additional_data_list' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    additional_data_list = self.per_group_data[group_id]['data_per_participant'][participant_code][
                        'additional_data_list']

                    for additional_data in additional_data_list:
                        directory_step_name = additional_data['directory_step_name']
                        path_additional_data = path.join(path_per_participant, directory_step_name)
                        if not path.exists(path_additional_data):
                            # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                            # /Step_X_COMPONENT_TYPE
                            error_msg, path_additional_data = create_directory(path_per_participant,
                                                                               directory_step_name)

                            if error_msg != "":
                                return error_msg

                        # ex. /NES_EXPORT/Experiment_data/Group_XX/Per_participant/Participant_123/Step_X_COMPONENT_TYPE
                        export_step_additional_data_directory = path.join(participant_export_directory,
                                                                       directory_step_name)

                        # to create AdditionalData directory
                        directory_data_name = additional_data['additional_data_directory']
                        path_per_additional_data = path.join(path_additional_data, directory_data_name)
                        if not path.exists(path_per_additional_data):
                            error_msg, path_per_additional_data = create_directory(path_additional_data,
                                                                                   directory_data_name)
                            if error_msg != "":
                                return error_msg

                        export_additional_data_directory = path.join(export_step_additional_data_directory,
                                                                     directory_data_name)

                        for additional_file in additional_data['additional_data_file_list']:
                            path_additional_data_file = additional_file['additional_data_filename']

                            file_name = path_additional_data_file.split('/')[-1]

                            # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123/
                            # Step_X_COMPONENT_TYPE/file_name.format_type
                            complete_additional_data_filename = path.join(path_per_additional_data, file_name)
                            with open(path_additional_data_file, 'rb') as f:
                                data = f.read()

                            with open(complete_additional_data_filename, 'wb') as f:
                                f.write(data)

                            self.files_to_zip_list.append([complete_additional_data_filename,
                                                           export_additional_data_directory])

                if 'digital_game_data_list' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != "":
                            return error_msg

                    goalkeeper_game_data_list = self.per_group_data[group_id]['data_per_participant'][participant_code][
                        'digital_game_data_list']

                    for goalkeeper_game_data in goalkeeper_game_data_list:
                        if goalkeeper_game_data['digital_game_file_list']:
                            directory_step_name = goalkeeper_game_data['directory_step_name']
                            path_goalkeeper_game_data = path.join(path_per_participant, directory_step_name)
                            if not path.exists(path_goalkeeper_game_data):
                                # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_COMPONENT_TYPE
                                error_msg, path_goalkeeper_game_data = create_directory(path_per_participant,
                                                                                        directory_step_name)
                                if error_msg != "":
                                    return error_msg

                                # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_COMPONENT_TYPE
                                export_goalkeeper_game_directory = path.join(participant_export_directory,
                                                                             directory_step_name)

                                # to create Game_digital_dataData directory 
                                directory_data_name = goalkeeper_game_data['digital_game_data_directory']

                                path_per_emg_data = path.join(path_goalkeeper_game_data, directory_data_name)
                                if not path.exists(path_per_emg_data):
                                    # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123 
                                    #  /Step_X_aaa/GoalkeeperDATA_
                                    error_msg, path_per_goalkeeper_game_data = create_directory(
                                        path_goalkeeper_game_data, directory_data_name)

                                    if error_msg != "":
                                        return error_msg

                                # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_aaa/GoalkeeperDATA_
                                export_goalkeeper_data_directory = path.join(export_goalkeeper_game_directory,
                                                                             directory_data_name)

                                for context_tree_file in goalkeeper_game_data['digital_game_file_list']:
                                    path_context_tree_file = context_tree_file['digital_game_filename']
                                    file_name = path_context_tree_file.split('/')[-1]
                                    # ex. /NES_EXPORT/Experiment_data/Group_XXX/Per_participant
                                    #  /Participant_123/Step_X_COMPONENT_TYPE/file_name.format_type
                                    complete_goalkeeper_game_filename = path.join(path_per_goalkeeper_game_data,
                                                                                  file_name)
                                    with open(path_context_tree_file, 'rb') as f:
                                        data = f.read()

                                    with open(complete_goalkeeper_game_filename, 'wb') as f:
                                        f.write(data)

                                    self.files_to_zip_list.append([complete_goalkeeper_game_filename,
                                                                   export_goalkeeper_data_directory])

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

        :param output_list:
        :return: list of headers and list of fields
        """

        headers = []
        fields = []

        for element in output_list:
            if element["field"]:
                headers.append(element["header"])
                fields.append(element["field"])

        return headers, fields

    def get_field_en(self, fields):
        fields_en = []
        for field in fields:
            if field == 'gender__name':
                field = 'gender__name_en'
            if field == 'marital_status__name':
                field = 'marital_status__name_en'
            if field == 'socialdemographicdata__religion__name':
                field = 'socialdemographicdata__religion__name_en'
            if field == 'socialdemographicdata__payment__name':
                field = 'socialdemographicdata__payment__name_en'
            if field == 'socialdemographicdata__patient_schooling__name':
                field = 'socialdemographicdata__patient_schooling__name_en'
            if field == 'socialdemographicdata__schooling__name':
                field = 'socialdemographicdata__schooling__name_en'
            if field == 'socialdemographicdata__flesh_tone__name':
                field = 'socialdemographicdata__flesh_tone__name_en'
            if field == 'socialhistorydata__amount_cigarettes__name':
                field = 'socialhistorydata__amount_cigarettes__name_en'
            if field == 'socialhistorydata__alcohol_period__name':
                field = 'socialhistorydata__alcohol_period__name_en'
            if field == 'socialhistorydata__alcohol_frequency__name':
                field = 'socialhistorydata__alcohol_frequency__name_en'

            fields_en.append(field)

        return fields_en

    def calculate_age_by_participant(self, participants_list):
        age_value_dict = {}
        for participant_id in participants_list:
            subject = get_object_or_404(Patient, pk=participant_id[0])
            age_value = format((date.today() - subject.date_birth) / timedelta(days=365.2425), '.4')
            if subject.code not in age_value_dict:
                age_value_dict[subject.code] = age_value

        return age_value_dict

    def process_participant_data(self, participants_output_fields, participants_list, language):
        # TODO: fix translation model functionality
        # for participant in participants_output_fields:
        age_value_dict = {}
        headers, fields = self.get_headers_and_fields(participants_output_fields)
        model_to_export = getattr(modules['patient.models'], 'Patient')
        if 'age' in fields:
            age_value_dict = self.calculate_age_by_participant(participants_list)
            fields.remove('age')

        if language != 'pt-br':  # read english fields
            fields = self.get_field_en(fields)

        db_data = model_to_export.objects.filter(id__in=participants_list).values_list(*fields).extra(order_by=['id'])

        export_rows_participants = [headers]

        # transform data
        for record in db_data:
            participant_rows = []
            for value in record:
                participant_rows.append(value)
            if age_value_dict:
                participant_rows.insert(1, age_value_dict[record[0]])
            export_rows_participants.append(participant_rows)

        return export_rows_participants

    def process_diagnosis_data(self, participants_output_fields, participants_list):
        headers, fields = self.get_headers_and_fields(participants_output_fields)
        model_to_export = getattr(modules['patient.models'], 'Patient')
        db_data = model_to_export.objects.filter(id__in=participants_list).values_list(*fields).extra(
            order_by=['id'])

        export_rows_participants = [headers]

        # transform data
        for record in db_data:
            export_rows_participants.append([self.handle_exported_field(field) for field in record])

        return export_rows_participants

    def get_participant_data_per_code(self, subject_code, questionnaire_response_fields):
        db_data =[]
        for record in self.get_input_data('participants')['data_list']:
            if record[-1] == subject_code:
                db_data = record

        # append participant data to questionnaire response
        for field in db_data:
            questionnaire_response_fields.append(field)

        return questionnaire_response_fields

    def build_participant_export_data(self, per_experiment):
        error_msg = ""
        export_rows_participants = []
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


        export_filename = "%s.csv" % self.get_input_data('participants')["output_filename"]  # "participants.csv"

        complete_filename = path.join(base_export_directory, export_filename)

        # save_to_csv(complete_filename, export_rows_participants)

        self.files_to_zip_list.append([complete_filename, base_directory])

        export_rows_participants = self.get_input_data('participants')['data_list']

        with open(complete_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as csv_file:
            export_writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            for row in export_rows_participants:
                export_writer.writerow(row)

        # process  diagnosis file
        diagnosis_input_data = self.get_input_data("diagnosis")

        if diagnosis_input_data['output_list'] and participants_filtered_list:
            export_rows_diagnosis = self.process_diagnosis_data(diagnosis_input_data['output_list'], participants_filtered_list)

            export_filename = "%s.csv" % self.get_input_data('diagnosis')["output_filename"]  # "Diagnosis.csv"

            complete_filename = path.join(base_export_directory, export_filename)

            # files_to_zip_list.append(complete_filename)
            self.files_to_zip_list.append([complete_filename, base_directory])

            with open(complete_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as csv_file:
                export_writer = writer(csv_file, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
                for row in export_rows_diagnosis:
                    export_writer.writerow(row)

        return error_msg

    def process_experiment_data(self, language_code):
        error_msg = ""
        # process of experiment description
        for group_id in self.per_group_data:
            group = get_object_or_404(Group, pk=group_id)

        study = group.experiment.research_project
        experiment = group.experiment

        experiment_resume_header = ['Study', 'Study description', 'Start date', 'End date', 'Experiment Title',
                                    'Experiment description']

        experiment_resume = [study.title, study.description, str(study.start_date), str(study.end_date),
                             experiment.title, experiment.description]

        filename_experiment_resume = "%s.csv" % "Experiment"

        # path ex. /NES_EXPORT/Experiment_data
        export_experiment_data = path.join(self.get_input_data("base_directory"),
                                           self.get_input_data("experiment_data_directory"))

        # path ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data
        experiment_resume_directory = path.join(self.get_export_directory(),
                                                self.get_input_data("experiment_data_directory"))

        # User/.../qdc/media/.../NES_EXPORT/Experiment_data/Experiment.csv
        complete_filename_experiment_resume = path.join(experiment_resume_directory, filename_experiment_resume)

        experiment_description_fields = []
        experiment_description_fields.insert(0, experiment_resume_header)
        experiment_description_fields.insert(1, experiment_resume)
        save_to_csv(complete_filename_experiment_resume, experiment_description_fields)

        self.files_to_zip_list.append([complete_filename_experiment_resume, export_experiment_data])

        # process of filename for description of each group
        for group_id in self.per_group_data:
            group = get_object_or_404(Group, pk=group_id)
            if group.experimental_protocol:

                tree = get_block_tree(group.experimental_protocol, language_code)
                experimental_protocol_description = get_description_from_experimental_protocol_tree(tree)

                if experimental_protocol_description:

                    group_resume = "Group name: " + group.title + "\n" + "Group description: " + group.description \
                                   + "\n"
                    # group_directory_name = 'Group_' + group.title
                    filename_group_for_export = "%s.txt" % "Experimental_protocol_description"
                    # path ex. User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/
                    group_file_directory = self.per_group_data[group_id]['group']['directory']
                    # path ex. /NES_EXPORT/Experiment_data/Group_xxxx/
                    export_group_directory = self.per_group_data[group_id]['group']['export_directory']
                    # ex. Users/..../NES_EXPORT/Experiment_data/Group_xxx/Experimental_protocol
                    error_msg, directory_experimental_protocol = create_directory(group_file_directory,
                                                                                  "Experimental_protocol")
                    if error_msg != "":
                        return error_msg

                    # path ex. /NES_EXPORT/Experiment_data/Group_xxx
                    export_directory_experimental_protocol = path.join(export_group_directory, "Experimental_protocol")

                    # User/.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/Experimental_protocol/
                    # Experimental_protocol_description.txt
                    complete_group_filename = path.join(directory_experimental_protocol, filename_group_for_export)

                    self.files_to_zip_list.append([complete_group_filename, export_directory_experimental_protocol])

                    with open(complete_group_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as txt_file:
                        txt_file.writelines(group_resume)
                        txt_file.writelines(experimental_protocol_description)

                # save protocol image
                experimental_protocol_image = get_experimental_protocol_image(group.experimental_protocol, tree)
                if experimental_protocol_image:
                    filename_protocol_image = "Protocol_image.png"
                    complete_protocol_image_filename = path.join(directory_experimental_protocol,
                                                                 filename_protocol_image)

                    image_protocol = settings.BASE_DIR + experimental_protocol_image
                    with open(image_protocol, 'rb') as f:
                        data = f.read()

                    with open(complete_protocol_image_filename, 'wb') as f:
                        f.write(data)

                    self.files_to_zip_list.append([complete_protocol_image_filename,
                                                   export_directory_experimental_protocol])

                # save eeg, emg, tms, context tree setting default in Experimental Protocol directory
                if 'eeg_default_setting_id' in self.per_group_data[group_id]:
                    eeg_default_setting_description = get_eeg_setting_description(self.per_group_data[group_id][
                                                                                  'eeg_default_setting_id'])

                    if eeg_default_setting_description:
                        eeg_setting_description = "%s.json" % "eeg_default_setting"
                        complete_filename_eeg_setting = path.join(directory_experimental_protocol, eeg_setting_description)
                        self.files_to_zip_list.append([complete_filename_eeg_setting,
                                                       export_directory_experimental_protocol])

                        with open(complete_filename_eeg_setting.encode('utf-8'), 'w', newline='',
                                  encoding='UTF-8') as outfile:
                            json.dump(eeg_default_setting_description, outfile, indent=4)

                if 'emg_default_setting_id' in self.per_group_data[group_id]:
                    emg_default_setting_description = get_emg_setting_description(self.per_group_data[group_id][
                                                                                  'emg_default_setting_id'])
                    if emg_default_setting_description:
                        emg_setting_description = "%s.json" % "emg_default_setting"
                        complete_filename_emg_setting = path.join(directory_experimental_protocol,
                                                                          emg_setting_description)
                        self.files_to_zip_list.append([complete_filename_emg_setting,
                                                       export_directory_experimental_protocol])

                        with open(complete_filename_emg_setting.encode('utf-8'), 'w', newline='',
                                  encoding='UTF-8') as outfile:
                            json.dump(emg_default_setting_description, outfile, indent=4)

                if 'tms_default_setting_id' in self.per_group_data[group_id]:
                    tms_default_setting_description = get_tms_setting_description(self.per_group_data[group_id][
                                                                                      'tms_default_setting_id'])
                    if tms_default_setting_description:
                        tms_setting_description = "%s.json" % "tms_default_setting"
                        complete_filename_tms_setting = path.join(directory_experimental_protocol,
                                                                  tms_setting_description)
                        self.files_to_zip_list.append([complete_filename_tms_setting,
                                                       export_directory_experimental_protocol])

                        with open(complete_filename_tms_setting.encode('utf-8'), 'w', newline='',
                                  encoding='UTF-8') as outfile:
                            json.dump(tms_default_setting_description, outfile, indent=4)

                if 'context_tree_default_id' in self.per_group_data[group_id]:
                    context_tree_default_description = get_context_tree_description(self.per_group_data[group_id][
                                                                                   'context_tree_default_id'])
                    if context_tree_default_description:
                        context_tree_description = "%s.json" % "context_tree_default"
                        complete_filename_context_tree = path.join(directory_experimental_protocol,
                                                                   context_tree_description)
                        self.files_to_zip_list.append([complete_filename_context_tree,
                                                       export_directory_experimental_protocol])

                        with open(complete_filename_context_tree.encode('utf-8'), 'w', newline='',
                                  encoding='UTF-8') as outfile:
                            json.dump(context_tree_default_description, outfile, indent=4)

                        context_tree = get_object_or_404(ContextTree, pk=self.per_group_data[group_id][
                            'context_tree_default_id'])

                    if context_tree.setting_file.name:
                        context_tree_filename = path.join(settings.BASE_DIR, "media") + "/" + context_tree.setting_file.name
                        complete_context_tree_filename = path.join(directory_experimental_protocol,
                                                                   context_tree.setting_file.name.split('/')[-1])
                        with open(context_tree_filename, "rb") as f:
                            data = f.read()
                        with open(complete_context_tree_filename, "wb") as f:
                            f.write(data)

                        self.files_to_zip_list.append([complete_context_tree_filename,
                                                       export_directory_experimental_protocol])

                # process participant/diagnosis per Participant of each group
                participant_group_list = []
                subject_of_group = SubjectOfGroup.objects.filter(group=group)
                for subject in subject_of_group:
                    participant_group_list.append(subject.subject.patient_id)

                if 'stimulus_data' in self.per_group_data[group_id]:
                    stimulus_data_list = self.per_group_data[group_id]['stimulus_data']
                    for stimulus_data in stimulus_data_list:
                        if stimulus_data['stimulus_file']:
                            # ex. /.../qdc/media/.../NES_EXPORT/Experiment_data/Group_xxxx/Step_X_STIMULUS
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

                            self.files_to_zip_list.append([complete_stimulus_data_filename,
                                                           export_directory_stimulus_data])

        return error_msg

    @staticmethod
    def find_duplicates(fill_list1, fill_list2):

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
        self.questionnaires_responses = {}
        for group_id in self.get_input_data('questionnaires_from_experiments'):
            for questionnaire_id in self.get_input_data(
                    'questionnaires_from_experiments')[group_id]:
                language_list = self.get_input_data(
                    'questionnaire_language'
                )[questionnaire_id]['language_list']
                questionnaire = self.get_input_data(
                    'questionnaires_from_experiments')[group_id][str(questionnaire_id)]
                headers, fields = \
                    self.questionnaire_utils.set_questionnaire_experiment_header_and_fields(
                        questionnaire_id, questionnaire
                    )

                # TODO: This if is the first thing to do not inside for.
                # TODO: Put this as the first line of method.
                if limesurvey_available(questionnaire_lime_survey):
                    data_from_lime_survey = {}
                    for language in language_list:
                        # read all data for questionnaire_id from LimeSurvey
                        responses_string1 = \
                            questionnaire_lime_survey.get_responses(
                                questionnaire_id, language, response_type[0]
                            )
                        # all the answer from the questionnaire_id in csv format
                        fill_list1 = QuestionnaireUtils.responses_to_csv(
                            responses_string1
                        )

                        # need types of questions to make replacement just
                        # below
                        question_list = QuestionnaireUtils.get_question_list(
                            questionnaire_lime_survey, questionnaire_id,
                            language
                        )
                        replace_multiple_question_answers(
                            fill_list1, question_list
                        )

                        # read "long" information, if necessary
                        if len(response_type) > 1:
                            responses_string2 = \
                                questionnaire_lime_survey.get_responses(
                                    questionnaire_id, language,
                                    response_type[1]
                                )
                            fill_list2 = QuestionnaireUtils.responses_to_csv(
                                responses_string2
                            )
                            # need types of questions to make replacement just
                            # below
                            question_list = \
                                QuestionnaireUtils.get_question_list(
                                questionnaire_lime_survey, questionnaire_id,
                                language
                            )
                            replace_multiple_question_answers(
                                fill_list2, question_list
                            )
                        else:
                            fill_list2 = fill_list1

                        # filter fields
                        subscripts = []

                        for field in fields:
                            if field in fill_list1[0]:
                                subscripts.append(fill_list1[0].index(field))

                        data_from_lime_survey[language] = {}

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
                            data_from_lime_survey[language][token] = list(data_fields_filtered)
                            line_index += 1
                    self.questionnaire_utils.redefine_header_and_fields_experiment(questionnaire_id, header_filtered,
                                                                                   fields, headers)

                    if self.per_group_data[group_id]['questionnaires_per_group']:
                        questionnaire_list = self.per_group_data[group_id]['questionnaires_per_group'][int(
                            questionnaire_id)]['token_list']
                        for questionnaire_data in questionnaire_list:
                            token_id = questionnaire_data['token_id']
                            completed = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id,
                                                                                             "completed")
                            if completed is not None and completed != "N" and completed != "":
                                token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id,
                                                                                             "token")
                                new_header = self.questionnaire_utils.questionnaires_experiment_data[questionnaire_id][
                                    "header_questionnaire"]

                                if questionnaire_id not in self.questionnaires_responses:
                                    self.questionnaires_responses[questionnaire_id] = {}
                                if token not in self.questionnaires_responses[questionnaire_id]:
                                    self.questionnaires_responses[questionnaire_id][token_id] = {}

                                for language in data_from_lime_survey:
                                    fields_filtered_list = [new_header, data_from_lime_survey[language][token]]
                                    self.questionnaires_responses[questionnaire_id][token_id][language] = \
                                        fields_filtered_list

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
        available = limesurvey_available(questionnaire_lime_survey)

        headers, fields = \
            self.questionnaire_utils.set_questionnaire_experiment_header_and_fields(questionnaire_id, questionnaire)

        if available:
            # read all data for questionnaire_id from LimeSurvey
            responses_string1 = questionnaire_lime_survey.get_responses(
                questionnaire_id, language, response_type[0]
            )
            # all the answer from the questionnaire_id in csv format
            fill_list1 = QuestionnaireUtils.responses_to_csv(responses_string1)

            # read "long" information, if necessary
            if len(response_type) > 1:
                responses_string2 = questionnaire_lime_survey.get_responses(questionnaire_id, language,
                                                                            response_type[1])
                fill_list2 = QuestionnaireUtils.responses_to_csv(responses_string2)
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
                    transformed_fields = self.get_participant_data_per_code(patient_code, data_fields)
                else:
                    transformed_fields = self.transform_questionnaire_data(patient_id, data_fields)
                # data_rows.append(transformed_fields)

                if len(transformed_fields) > 0:
                    export_rows.append(transformed_fields)

                    self.questionnaire_utils.include_questionnaire_code_and_id(survey_code, lime_survey_id)

                    self.include_in_per_participant_data_from_experiment([transformed_fields], patient_code,
                                                                         survey_code, token_id, step_number)

                    self.include_participant_per_questionnaire(token_id, survey_code)

            # build the header
            for row in self.get_input_data('participants'):
                headers_participant_data, fields_participant_data = self.get_headers_and_fields(row["output_list"])

            header = self.questionnaire_utils.get_header_experiment_questionnaire(questionnaire_id)

            # if header[len(header) - 1] == 'participant_code':
            #     header = header[0:len(header) - 1]
            for element in step_header:
                header.append(element)

            for field in headers_participant_data:
                header.append(field)

            self.questionnaire_utils.redefine_header_and_fields_experiment(
                questionnaire_id, header_filtered, fields, header)

            export_rows.insert(0, header)
        return export_rows

    def define_questionnaire(self, questionnaire, questionnaire_lime_survey, language):
        """
        :param questionnaire:
        :return: fields_description: (list)

        """
        # questionnaire exportation - evaluation questionnaire
        questionnaire_id = questionnaire["id"]
        response_type = self.get_response_type()
        export_rows = []

        # verify if LimeSurvey is running
        available = limesurvey_available(questionnaire_lime_survey)

        headers, fields = \
            self.questionnaire_utils.set_questionnaire_header_and_fields(
                questionnaire, True
            )

        questionnaire_exists = QuestionnaireResponse.objects.filter(
            survey__lime_survey_id=questionnaire_id).exists()
        # filter data (participants)
        questionnaire_responses = QuestionnaireResponse.objects.filter(
            survey__lime_survey_id=questionnaire_id
        )

        #  include new filter that come from advanced search
        filtered_data = self.get_participants_filtered_data()
        questionnaire_responses = questionnaire_responses.filter(
            patient_id__in=filtered_data
        )

        if questionnaire_exists and available:
            # read all data for questionnaire_id from LimeSurvey
            responses_string1 = questionnaire_lime_survey.get_responses(
                questionnaire_id, language, response_type[0]
            )
            fill_list1 = QuestionnaireUtils.responses_to_csv(responses_string1)

            # need types of questions to make replacement just
            # below
            question_list = QuestionnaireUtils.get_question_list(
                questionnaire_lime_survey, questionnaire_id,
                language
            )
            replace_multiple_question_answers(
                fill_list1, question_list
            )

            # read "long" information, if necessary
            if len(response_type) > 1:
                responses_string2 = questionnaire_lime_survey.get_responses(
                    questionnaire_id, language, response_type[1]
                )
                fill_list2 = QuestionnaireUtils.responses_to_csv(responses_string2)
                # need types of questions to make replacement just
                # below
                question_list = QuestionnaireUtils.get_question_list(
                    questionnaire_lime_survey, questionnaire_id,
                    language
                )
                replace_multiple_question_answers(
                    fill_list2, question_list
                )
            else:
                fill_list2 = fill_list1

            # filter fields
            subscripts = []

            for field in fields:
                if field in fill_list1[0]:
                    subscripts.append(fill_list1[0].index(field))

            # if responses exits
            if subscripts:
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

                self.update_questionnaire_rules(questionnaire_id)

                # for each questionnaire_id from ResponseQuestionnaire from questionnaire_id
                for questionnaire_response in questionnaire_responses:

                    # transform data fields
                    # include new fieldsm

                    survey_code = questionnaire_response.survey.code
                    lime_survey_id = questionnaire_response.survey.lime_survey_id
                    patient_code = questionnaire_response.patient.code
                    token_id = questionnaire_response.token_id

                    token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id, "token")

                    if token in data_from_lime_survey:
                        lm_data_row = data_from_lime_survey[token]

                        data_fields = [smart_str(data) for data in lm_data_row]
                        export_rows_participants = self.get_participant_row_data(patient_code)
                        transformed_fields = self.merge_questionnaire_answer_list_per_participant(
                            export_rows_participants[1], [data_fields])

                        if len(transformed_fields) > 0:
                            for sublist in transformed_fields:
                                export_rows.append(sublist)

                            self.questionnaire_utils.include_questionnaire_code_and_id(survey_code, lime_survey_id)

                            self.include_in_per_participant_data(transformed_fields, patient_code, survey_code, language)

                            self.include_participant_per_questionnaire(token_id, survey_code)

                headers, fields = \
                    self.questionnaire_utils.redefine_header_and_fields(
                        questionnaire_id, header_filtered, fields
                    )

            # build header
            participant_data_header = \
                self.get_input_data('participants')['data_list'][0]

            header = self.build_header_questionnaire_per_participant(
                participant_data_header, headers[0:len(headers)-1]
            )

            export_rows.insert(0, header)
        return export_rows


def handling_values(dictionary_object):
    result = {}
    for key, value in dictionary_object.items():
        if dictionary_object[key] is None:
            result[key] = ''
        elif isinstance(dictionary_object[key], bool):
            result[key] = _('Yes') if dictionary_object[key] else _('No')
        else:
            result[key] = smart_str(dictionary_object[key])

    return result


def get_eeg_setting_description(eeg_setting_id):
    eeg_setting = get_object_or_404(EEGSetting, pk=eeg_setting_id)

    eeg_setting_attributes = vars(eeg_setting)

    eeg_setting_attributes = handling_values(eeg_setting_attributes)

    description = {
        'name': eeg_setting_attributes['name'],
        'description': eeg_setting_attributes['description'],
    }

    if hasattr(eeg_setting, 'eeg_amplifier_setting'):
        eeg_amplifier_setting_attributes = vars(eeg_setting.eeg_amplifier_setting)
        eeg_amplifier_setting_attributes = handling_values(eeg_amplifier_setting_attributes)
        # amplifier attributes
        eeg_amplifier_attributes = vars(eeg_setting.eeg_amplifier_setting.eeg_amplifier)
        eeg_amplifier_attributes = handling_values(eeg_amplifier_attributes)
        impedance_description = ''
        amplifier_detection_type_name = ''
        tethering_system_name = ''
        if eeg_amplifier_attributes['input_impedance'] and eeg_amplifier_attributes['input_impedance_unit']:
            impedance_description = eeg_amplifier_attributes['input_impedance'] + " (" + eeg_amplifier_attributes[
                'input_impedance_unit'] + ")"
        amplifier_detection_type = eeg_setting.eeg_amplifier_setting.eeg_amplifier.amplifier_detection_type
        tethering_system = eeg_setting.eeg_amplifier_setting.eeg_amplifier.tethering_system
        if amplifier_detection_type:
            amplifier_detection_type_name = amplifier_detection_type.name
        if tethering_system:
            tethering_system_name = tethering_system.name
        description['eeg_amplifier_setting'] = {
            'identification': eeg_amplifier_attributes['identification'],
            'manufacturer_name': eeg_setting.eeg_amplifier_setting.eeg_amplifier.manufacturer.name,
            'serial_number': eeg_amplifier_attributes['serial_number'],
            'description': eeg_amplifier_attributes['description'],
            'gain_setted': eeg_amplifier_setting_attributes['gain'],
            'sampling_rate_setted': eeg_amplifier_setting_attributes['sampling_rate'],
            'number_of_channels_used': eeg_amplifier_setting_attributes['number_of_channels_used'],
            'gain (equipment)': eeg_amplifier_attributes['gain'],
            'number_of_channels (equipment)': eeg_amplifier_attributes['number_of_channels'],
            'common_mode_rejection_ratio': eeg_amplifier_attributes['common_mode_rejection_ratio'],
            'input_impedance': impedance_description,
            'amplifier_detection_type_name': amplifier_detection_type_name,
            'tethering_system_name': tethering_system_name,
        }

    if hasattr(eeg_setting, 'eeg_filter_setting'):
        eeg_filter_setting_attributes = vars(eeg_setting.eeg_filter_setting)
        eeg_filter_setting_attributes = handling_values(eeg_filter_setting_attributes)
        filter_type_description = eeg_setting.eeg_filter_setting.eeg_filter_type.description if \
            eeg_setting.eeg_filter_setting.eeg_filter_type.description else ''
        description['eeg_filter_setting'] = {
            'filter_type': eeg_setting.eeg_filter_setting.eeg_filter_type.name,
            'description': filter_type_description,
            'high_pass': eeg_filter_setting_attributes['high_pass'],
            'low_pass': eeg_filter_setting_attributes['low_pass'],
            'order': eeg_filter_setting_attributes['order'],
            'high_band_pass': eeg_filter_setting_attributes['high_band_pass'],
            'low_band_pass': eeg_filter_setting_attributes['low_band_pass'],
            'high_notch': eeg_filter_setting_attributes['high_notch'],
            'low_notch': eeg_filter_setting_attributes['low_notch']
        }

    if hasattr(eeg_setting, 'eeg_solution'):
        description['eeg_solution_setting'] = {
            'manufacturer': eeg_setting.eeg_solution_setting.eeg_solution.manufacturer.name,
            'identification': eeg_setting.eeg_solution_setting.eeg_solution.name,
            'components': eeg_setting.eeg_solution_setting.eeg_solution.components if
            eeg_setting.eeg_solution_setting.eeg_solution.components else ''
        }

    if hasattr(eeg_setting, 'eeg_electrode_layout_setting'):
        eeg_electrode_localization_system_attributes = vars(
            eeg_setting.eeg_electrode_layout_setting.eeg_electrode_net_system.eeg_electrode_localization_system)
        eeg_electrode_localization_system_attributes = handling_values(eeg_electrode_localization_system_attributes)
        # eeg_electrode_net
        eeg_electrode_net_attributes = vars(
            eeg_setting.eeg_electrode_layout_setting.eeg_electrode_net_system.eeg_electrode_net)
        eeg_electrode_net_attributes = handling_values(eeg_electrode_net_attributes)
        description['eeg_electrode_layout_setting'] = {
            'name': eeg_electrode_localization_system_attributes['name'],
            'description': eeg_electrode_localization_system_attributes['description'],
            'map_filename': eeg_electrode_localization_system_attributes['map_image_file'].split('/')[-1],
            'eeg_electrode_net': {
                'manufacturer_name': eeg_setting.eeg_electrode_layout_setting.eeg_electrode_net_system
                    .eeg_electrode_net.manufacturer.name,
                'equipment_type': eeg_electrode_net_attributes['equipment_type'],
                'identification': eeg_electrode_net_attributes['identification'],
                'description': eeg_electrode_net_attributes['description'],
                'serial_number': eeg_electrode_net_attributes['serial_number'],
            },
            'electrode_position_list': [],
        }

        eeg_electrode_position_setting_list = EEGElectrodePositionSetting.objects.filter(
            eeg_electrode_layout_setting=eeg_setting.eeg_electrode_layout_setting)
        for eeg_electrode_position_setting in eeg_electrode_position_setting_list:

            # eeg_electrode_position
            eeg_electrode_position_attributes = vars(eeg_electrode_position_setting.eeg_electrode_position)
            eeg_electrode_position_attributes = handling_values(eeg_electrode_position_attributes)
            # electrode_model
            electrode_model_attributes = vars(eeg_electrode_position_setting.electrode_model)
            electrode_model_attributes = handling_values(electrode_model_attributes)
            impedance_description = ''
            electrode_distance_description = ''
            material_name = ''
            material_description = ''
            electrode_configuration_name = ''
            material = eeg_electrode_position_setting.electrode_model.material
            electrode_configuration = eeg_electrode_position_setting.electrode_model.electrode_configuration
            if material:
                material_description = material.description if material.description else ''
            if electrode_configuration:
                electrode_configuration_name = electrode_configuration.name if electrode_configuration.name else ''
            if electrode_model_attributes['impedance'] and electrode_model_attributes['impedance_unit']:
                impedance_description = electrode_model_attributes['impedance'] + " (" + electrode_model_attributes[
                    'impedance_unit'] + ")"
            if electrode_model_attributes['inter_electrode_distance'] and \
                    electrode_model_attributes['inter_electrode_distance_unit']:
                electrode_distance_description = electrode_model_attributes['inter_electrode_distance'] + " (" + \
                                                 electrode_model_attributes['inter_electrode_distance_unit'] + ")"
            # electrode type desription
            electrode_type_description = {}
            if electrode_model_attributes['electrode_type'] == 'surface' and hasattr(
                    eeg_electrode_position_setting.electrode_model, 'surfaceelectrode'):
                eeg_surface_placement = get_object_or_404(SurfaceElectrode,
                                                          pk=eeg_electrode_position_setting.electrode_model.id)
                electrode_type_description = {
                    'electrode_mode': eeg_surface_placement.electrode_mode,
                    'electrode_shape': eeg_surface_placement.electrode_shape.name,
                    'conduction_type': eeg_surface_placement.conduction_type,
                    }

            if electrode_model_attributes['electrode_type'] == 'intramuscular' and hasattr(
                    eeg_electrode_position_setting.electrode_model, 'intramuscularelectrode'):
                eeg_intramuscular_placement = get_object_or_404(IntramuscularElectrode,
                                                                pk=eeg_electrode_position_setting.electrode_model.id)
                electrode_type_description = {
                    'strand': eeg_intramuscular_placement.strand,
                    'insulation_material': eeg_intramuscular_placement.insulation_material.name,
                    'length_of_exposed_tip': '',
                }

            if electrode_model_attributes['electrode_type'] == 'needle' and hasattr(
                    eeg_electrode_position_setting.electrode_model, 'needleelectrode'):
                eeg_needle_placement = get_object_or_404(NeedleElectrode,
                                                          pk=eeg_electrode_position_setting.electrode_model.id)
                eeg_needle_placement_attributes = vars(eeg_needle_placement)
                eeg_needle_placement_attributes = handling_values(eeg_needle_placement_attributes)
                electrode_type_description = {
                    'number_of_conductive_contact_points_at_the_tip': eeg_needle_placement_attributes[
                        'number_of_conductive_contact_points_at_the_tip'],
                    'size': eeg_needle_placement_attributes['size'] + '-' + eeg_needle_placement_attributes[
                        'size_unit'],
                }

            description['eeg_electrode_layout_setting']['electrode_position_list'].append({
                'name': eeg_electrode_position_attributes['name'],
                'coordinate_x': eeg_electrode_position_attributes['coordinate_x'],
                'coordinate_y': eeg_electrode_position_attributes['coordinate_y'],
                'channel_index': eeg_electrode_position_setting.channel_index,
                'used': eeg_electrode_position_setting.used,
                'electrode_model': {
                    'model_name': electrode_model_attributes['name'],
                    'electrode type': electrode_model_attributes['electrode_type'],
                    'description': electrode_model_attributes['description'],
                    'material_name': material_name,
                    'material_description': material_description,
                    'usability': electrode_model_attributes['usability'],
                    'impedance': impedance_description,
                    'distance_inter_electrode': electrode_distance_description,
                    'electrode_configuration_name': electrode_configuration_name,
                    'placement_type_description': electrode_type_description if electrode_type_description else '',
                }
            })

    return description


def get_emg_setting_description(emg_setting_id):
    emg_setting = get_object_or_404(EMGSetting, pk=emg_setting_id)

    emg_setting_attributes = vars(emg_setting)

    emg_setting_attributes = handling_values(emg_setting_attributes)

    software = emg_setting.acquisition_software_version.software
    description = {
        'name': emg_setting_attributes['name'],
        'description': emg_setting_attributes['description'],
        'acquisition_software_name': emg_setting.acquisition_software_version.name,
        'software_name': software.name,
        'software_description': software.description if software.description else '',
        'manufacturer_name': software.manufacturer.name,
    }

    if hasattr(emg_setting, 'emg_ad_converter_setting'):
        emg_ad_converter_setting_attributes = vars(emg_setting.emg_ad_converter_setting)
        emg_ad_converter_setting_attributes = handling_values(emg_ad_converter_setting_attributes)

        description['emg_ad_converter_setting'] = {
            'sampling_rate_setted': emg_ad_converter_setting_attributes['sampling_rate']
        }

        ad_converter_attributes = vars(emg_setting.emg_ad_converter_setting.ad_converter)
        ad_converter_attributes = handling_values(ad_converter_attributes)
        description['emg_ad_converter_setting']['ad_converter'] = ad_converter_attributes['identification']
        description['emg_ad_converter_setting']['sample_rate (equipment)'] = ad_converter_attributes[
            'sampling_rate']
        description['emg_ad_converter_setting']['signal_to_noise (equipment)'] = ad_converter_attributes[
            'signal_to_noise_rate']
        description['emg_ad_converter_setting']['resolution (equipment)'] = ad_converter_attributes['resolution']

    if hasattr(emg_setting, 'emg_digital_filter_setting'):
        emg_digital_filter_setting = vars(emg_setting.emg_digital_filter_setting)
        emg_digital_filter_setting = handling_values(emg_digital_filter_setting)
        filter_type = emg_setting.emg_digital_filter_setting.filter_type
        description['emg_digital_filter_setting'] = {
            'filter type name': filter_type.name,
            'filter_type_description': filter_type.description if filter_type.description else '',
            'high_pass': emg_digital_filter_setting['high_pass'],
            'low_pass': emg_digital_filter_setting['low_pass'],
            'high_band_pass': emg_digital_filter_setting['high_band_pass'],
            'low_band_pass': emg_digital_filter_setting['low_band_pass'],
            'high_notch': emg_digital_filter_setting['high_notch'],
            'low_notch': emg_digital_filter_setting['low_notch'],
            'order': emg_digital_filter_setting['order'],
        }

    description['emg_electrode_setting_list'] = []

    # to_many
    emg_electrode_setting_list = EMGElectrodeSetting.objects.filter(emg_setting=emg_setting)
    for emg_electrode_setting in emg_electrode_setting_list:

        emg_electrode_setting_dict = {}

        electrode_model_attributes = vars(emg_electrode_setting.electrode)
        electrode_model_attributes = handling_values(electrode_model_attributes)

        impedance_description = ''
        if electrode_model_attributes['impedance'] and electrode_model_attributes['impedance_unit']:
            impedance_description = \
                electrode_model_attributes['impedance'] + " (" + electrode_model_attributes['impedance_unit'] + ")"

        electrode_distance_description = ''
        if electrode_model_attributes['inter_electrode_distance'] and \
                electrode_model_attributes['inter_electrode_distance_unit']:
            electrode_distance_description = electrode_model_attributes['inter_electrode_distance'] + " (" + \
                                             electrode_model_attributes['inter_electrode_distance_unit'] + ")"

        material_name = ''
        material_description = ''
        electrode_configuration_name = ''
        material = emg_electrode_setting.electrode.material
        electrode_configuration = emg_electrode_setting.electrode.electrode_configuration
        if material:
            material_name = material.name
            material_description = material.description
        if electrode_configuration:
            electrode_configuration_name = electrode_configuration.name

        emg_electrode_setting_dict['electrode_model'] = {
            'model_name': electrode_model_attributes['name'],
            'electrode type': electrode_model_attributes['electrode_type'],
            'description': electrode_model_attributes['description'],
            'material_name': material_name,
            'material_description': material_description,
            'usability': electrode_model_attributes['usability'],
            'impedance': impedance_description,
            'distance inter electrode': electrode_distance_description,
            'electrode_configuration_name': electrode_configuration_name,
        }

        if hasattr(emg_electrode_setting, 'emg_amplifier_setting'):
            emg_amplifier_setting_attributes = vars(emg_electrode_setting.emg_amplifier_setting)
            emg_amplifier_setting_attributes = handling_values(emg_amplifier_setting_attributes)
            # amplifier equipment
            emg_amplifier = emg_electrode_setting.emg_amplifier_setting.amplifier
            amplifier_detection_type_name = ''
            tethering_system_name = ''
            amplifier_detection_type = emg_amplifier.amplifier_detection_type
            tethering_system = emg_amplifier.tethering_system
            if amplifier_detection_type:
                amplifier_detection_type_name = amplifier_detection_type.name
            if tethering_system:
                tethering_system_name = tethering_system.name
            emg_amplifier_attributes = vars(emg_amplifier)
            emg_amplifier_attributes = handling_values(emg_amplifier_attributes)
            impedance_description = emg_amplifier_attributes['input_impedance'] + " (" + emg_amplifier_attributes[
                'input_impedance_unit'] + ")"
            emg_electrode_setting_dict['emg_amplifier_setting'] = {
                'identification': emg_amplifier_attributes['identification'],
                'manufacturer_name': emg_electrode_setting.emg_amplifier_setting.amplifier.manufacturer.name,
                'serial_number': emg_amplifier_attributes['serial_number'],
                'description': emg_amplifier_attributes['description'],
                'gain_setted': emg_amplifier_setting_attributes['gain'],
                'gain (equipment)': emg_amplifier_attributes['gain'],
                'number_of_channels (equipment)': emg_amplifier_attributes['number_of_channels'],
                'common_mode_rejection_ratio': emg_amplifier_attributes['common_mode_rejection_ratio'],
                'input_impedance': impedance_description,
                'amplifier_detection_type_name': amplifier_detection_type_name,
                'tethering_system_name': tethering_system_name,
            }

            if hasattr(emg_electrode_setting.emg_amplifier_setting, 'emg_analog_filter_setting'):
                emg_amplifier_setting = emg_electrode_setting.emg_amplifier_setting
                emg_analog_filter_setting_attributes = vars(emg_amplifier_setting.emg_analog_filter_setting)
                emg_analog_filter_setting_attributes = handling_values(emg_analog_filter_setting_attributes)

                emg_electrode_setting_dict['emg_amplifier_setting']['emg_analog_filter_setting'] = {
                    'low_pass': emg_analog_filter_setting_attributes['low_pass'],
                    'high_pass': emg_analog_filter_setting_attributes['high_pass'],
                    'low_band_pass': emg_analog_filter_setting_attributes['low_band_pass'],
                    'high_band_pass': emg_analog_filter_setting_attributes['high_band_pass'],
                    'low_notch': emg_analog_filter_setting_attributes['low_notch'],
                    'high_notch': emg_analog_filter_setting_attributes['high_notch'],
                    'order': emg_analog_filter_setting_attributes['order'],
                }

        if hasattr(emg_electrode_setting, 'emg_preamplifier_setting'):
            emg_preamplifier_setting_attributes = vars(emg_electrode_setting.emg_preamplifier_setting)
            emg_preamplifier_setting_attributes = handling_values(emg_preamplifier_setting_attributes)
            # preamplifier equipment
            emg_preamplifier = emg_electrode_setting.emg_preamplifier_setting.amplifier
            amplifier_detection_type_name = ''
            tethering_system_name = ''
            amplifier_detection_type = emg_preamplifier.amplifier_detection_type
            tethering_system = emg_preamplifier.tethering_system
            if amplifier_detection_type:
                amplifier_detection_type_name = amplifier_detection_type.name
            if tethering_system:
                tethering_system_name = tethering_system.name
            preamplifier_attributes = vars(emg_electrode_setting.emg_preamplifier_setting.amplifier)
            preamplifier_attributes = handling_values(preamplifier_attributes)
            preamplifier_impedance_description = ''
            if preamplifier_attributes['input_impedance'] and preamplifier_attributes['input_impedance_unit']:
                preamplifier_impedance_description = preamplifier_attributes['input_impedance'] + " (" + \
                                                     preamplifier_attributes['input_impedance_unit'] + ")"

            emg_electrode_setting_dict['emg_preamplifier_setting'] = {
                'amplifier_name': preamplifier_attributes['identification'],
                'manufacturer_name': emg_preamplifier.manufacturer.name,
                'description': preamplifier_attributes['description'],
                'serial_number': preamplifier_attributes['serial_number'],
                'gain_setted': emg_preamplifier_setting_attributes['gain'],
                'gain (equipment)': preamplifier_attributes['gain'],
                'number of channels': preamplifier_attributes['number_of_channels'],
                'common_mode_rejection_ratio': preamplifier_attributes['common_mode_rejection_ratio'],
                'impedance': preamplifier_impedance_description,
                'detection type': amplifier_detection_type_name,
                'tethering system': tethering_system_name,
            }

            if hasattr(emg_electrode_setting.emg_preamplifier_setting,
                       'emg_preamplifier_filter_setting'):
                emg_preamplifier_setting = emg_electrode_setting.emg_preamplifier_setting
                emg_preamplifier_filter_setting_attributes = \
                    vars(emg_preamplifier_setting.emg_preamplifier_filter_setting)
                emg_preamplifier_filter_setting_attributes = handling_values(emg_preamplifier_filter_setting_attributes)

                emg_electrode_setting_dict['emg_preamplifier_setting']['emg_preamplifier_filter_setting'] = {
                    'low_pass': emg_preamplifier_filter_setting_attributes['low_pass'],
                    'high_pass': emg_preamplifier_filter_setting_attributes['high_pass'],
                    'low_band_pass': emg_preamplifier_filter_setting_attributes['low_band_pass'],
                    'high_band_pass': emg_preamplifier_filter_setting_attributes['high_band_pass'],
                    'low_notch': emg_preamplifier_filter_setting_attributes['low_notch'],
                    'high_notch': emg_preamplifier_filter_setting_attributes['high_notch'],
                    'order': emg_preamplifier_filter_setting_attributes['order'],
                }

        if hasattr(emg_electrode_setting, 'emg_electrode_placement_setting'):
            emg_electrode_placement_setting_attributes = vars(emg_electrode_setting.emg_electrode_placement_setting)
            emg_electrode_placement_setting_attributes = handling_values(emg_electrode_placement_setting_attributes)
            # muscle
            muscle_side = emg_electrode_setting.emg_electrode_placement_setting.muscle_side
            muscle_side_name = ''
            muscle_name = ''
            if muscle_side:
                muscle_side_name = muscle_side.name
                muscle_name = muscle_side.muscle.name
            # emg_electrode_placement
            emg_electrode_placement = emg_electrode_setting.emg_electrode_placement_setting.emg_electrode_placement
            emg_electrode_setting_dict['emg_electrode_placement_setting'] = {
                'muscle_side_name': muscle_name,
                'muscle_name': muscle_side_name,
                'remarks': emg_electrode_placement_setting_attributes['remarks'],
            }

            standardization_system_description = emg_electrode_placement.standardization_system.description
            muscle_subdivision_attributes = vars(emg_electrode_placement.muscle_subdivision)
            muscle_subdivision_attributes = handling_values(muscle_subdivision_attributes)
            emg_electrode_setting_dict['emg_electrode_placement_setting']['electrode_placement'] = {
                'standardization system': emg_electrode_placement.standardization_system.name,
                'standardization system description': standardization_system_description if
                standardization_system_description else '',
                'muscle_anatomy_origin': muscle_subdivision_attributes['anatomy_origin'],
                'muscle_anatomy_insertion': muscle_subdivision_attributes['anatomy_insertion'],
                'muscle_anatomy_function': muscle_subdivision_attributes['anatomy_function'],
                'location': emg_electrode_placement.location if emg_electrode_placement.location else '',
                'placement type': emg_electrode_placement.placement_type,
            }

            if emg_electrode_placement.placement_type == 'intramuscular':
                emg_intramuscular_placement = \
                    get_object_or_404(EMGIntramuscularPlacement, pk=emg_electrode_placement.id)
                emg_intramuscular_placement_attributes = vars(emg_intramuscular_placement)
                emg_intramuscular_placement_attributes = handling_values(emg_intramuscular_placement_attributes)
                emg_electrode_setting_dict['emg_electrode_placement_setting']['electrode_placement'][
                    'placement_type_description'] = {
                        'method_of_insertion': emg_intramuscular_placement_attributes['method_of_insertion'],
                        'depth_of_insertion': emg_intramuscular_placement_attributes['depth_of_insertion'],
                    }

            if emg_electrode_placement.placement_type == 'needle':
                emg_needle_placement = get_object_or_404(EMGNeedlePlacement, pk=emg_electrode_placement.id)
                emg_needle_placement_attributes = vars(emg_needle_placement)
                emg_needle_placement_attributes = handling_values(emg_needle_placement_attributes)
                emg_electrode_setting_dict['emg_electrode_placement_setting']['electrode_placement'][
                    'placement_type_description'] = {
                        'depth_of_insertion': emg_needle_placement_attributes['depth_of_insertion'],
                    }

            if emg_electrode_placement.placement_type == 'surface':
                emg_surface_placement = get_object_or_404(EMGSurfacePlacement, pk=emg_electrode_placement.id)
                emg_surface_placement_attributes = vars(emg_surface_placement)
                emg_surface_placement_attributes = handling_values(emg_surface_placement_attributes)
                emg_electrode_setting_dict['emg_electrode_placement_setting']['electrode_placement'][
                    'placement_type_description'] = {
                        'start_posture': emg_surface_placement_attributes['start_posture'],
                        'orientation': emg_surface_placement_attributes['orientation'],
                        'fixation_on_the_skin': emg_surface_placement_attributes['fixation_on_the_skin'],
                        'reference_electrode': emg_surface_placement_attributes['reference_electrode'],
                        'clinical_test': emg_surface_placement_attributes['clinical_test'],
                    }

        description['emg_electrode_setting_list'].append(emg_electrode_setting_dict)

    return description


def get_tms_data_description(tms_data_id):
    tms_data = get_object_or_404(TMSData, pk=tms_data_id)

    tms_description = {}
    tms_data_attributes = vars(tms_data)
    tms_data_attributes = handling_values(tms_data_attributes)
    coil_orientation = tms_data.coil_orientation
    coil_orientation_name = ''
    if coil_orientation:
        coil_orientation_name = coil_orientation.name
    tms_description['stimulation_description'] = {
        'tms_stimulation_description': tms_data_attributes['description'],
        'resting_motor threshold-RMT(%)': tms_data_attributes['resting_motor_threshold'],
        'test_pulse_intensity_of_simulation(% over the %RMT)': tms_data_attributes[
            'test_pulse_intensity_of_simulation'],
        'interval_between_pulses': tms_data_attributes['interval_between_pulses'],
        'interval_between_pulses_unit': tms_data_attributes['interval_between_pulses_unit'],
        'repetitive_pulse_frequency': tms_data_attributes['repetitive_pulse_frequency'],
        'coil_orientation': coil_orientation_name,
        'coil_orientation_angle': tms_data_attributes['coil_orientation_angle'],
        'second_test_pulse_intensity (% over the %RMT)': tms_data_attributes['second_test_pulse_intensity'],
        'time_between_mep_trials': tms_data_attributes['time_between_mep_trials'],
        'time_between_mep_trials_unit': tms_data_attributes['time_between_mep_trials_unit'],
    }

    hotspot = tms_data.hotspot
    brain_area = hotspot.tms_localization_system.brain_area
    tms_description['hotspot_position'] = {
        'hotspot_filename': hotspot.hot_spot_map.name.split('/')[-1],
        'tms_localization_system_name': hotspot.tms_localization_system.name,
        'tms_localization_system_description': hotspot.tms_localization_system.description if
        hotspot.tms_localization_system.description else '',
        'brain_area_name': brain_area.name,
        'brain_area_description': brain_area.description if brain_area.description else '',
        'brain_area_system_name': brain_area.brain_area_system.name,
        'brain_area_system_description': brain_area.brain_area_system.description if
        brain_area.brain_area_system.description else '',
    }

    tms_setting = tms_data.tms_setting
    tms_device_setting_dict = {}
    if hasattr(tms_data.tms_setting, 'tms_device_setting'):
        tms_device_setting = tms_data.tms_setting.tms_device_setting
        pulse_stimulus_type = tms_device_setting.pulse_stimulus_type

        tms_coil_model_attributes = vars(tms_device_setting.coil_model)
        tms_coil_model_attributes = handling_values(tms_coil_model_attributes)
        coil_shape = tms_device_setting.coil_model.coil_shape
        material = tms_device_setting.coil_model.material
        coil_shape_name = ''
        coil_material_name = ''
        coil_material_description = ''
        if coil_shape:
            coil_shape_name = coil_shape.name
        if material:
            coil_material_name = material.name
            coil_material_description = material.description

        tms_device_attributes = vars(tms_device_setting.tms_device)
        tms_device_attributes = handling_values(tms_device_attributes)

        tms_device_setting_dict = {
            'pulse_stimulus_type': pulse_stimulus_type if pulse_stimulus_type else '',
            'manufacturer_name': tms_device_setting.tms_device.manufacturer.name,
            'equipment_type': tms_device_attributes['equipment_type'],
            'identification': tms_device_attributes['identification'],
            'description': tms_device_attributes['description'],
            'serial_number': tms_device_attributes['serial_number'],
            'pulse_type': tms_device_attributes['pulse_type'],
            'coil_name': tms_coil_model_attributes['name'],
            'coil_description': tms_coil_model_attributes['description'],
            'coil_shape_name': coil_shape_name,
            'material_name': coil_material_name,
            'material_description': coil_material_description,
            'coil_design': tms_coil_model_attributes['coil_design'],
        }

    tms_description['setting_description'] = {
        'name': tms_setting.name,
        'description': tms_setting.description,
        'tms_device_setting': tms_device_setting_dict,
    }

    return tms_description


def get_tms_setting_description(tms_setting_id):
    tms_setting = get_object_or_404(TMSSetting, pk=tms_setting_id)

    tms_setting_description = {
        'name': tms_setting.name,
        'description': tms_setting.description,
    }

    return tms_setting_description


def get_context_tree_description(context_tree_id):
    context_tree = get_object_or_404(ContextTree, pk=context_tree_id)
    if context_tree:
        context_tree_description = {'name': context_tree.name, 'description': context_tree.description,
                                    'setting_text': context_tree.setting_text}

    return context_tree_description
