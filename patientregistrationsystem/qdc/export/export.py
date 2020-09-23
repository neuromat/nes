# -*- coding: utf-8 -*-
import csv
import json
import random
import re
import string
from collections import OrderedDict

from csv import writer
from datetime import date, datetime, timedelta
from sys import modules
from os import path, makedirs

from django.conf import settings
from django.core.files import File
from django.db.models import CharField, DateField, TextField, FloatField, BooleanField, NullBooleanField
from django.utils.encoding import smart_str
from django.utils.translation import ugettext as _
from django.apps import apps
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import slugify

from export.export_utils import create_list_of_trees, can_export_nwb
from plugin.models import RandomForests

from survey.survey_utils import HEADER_EXPLANATION_FIELDS, QUESTION_TYPES

from patient.models import Patient, QuestionnaireResponse, Gender, MaritalStatus, SocialDemographicData, Schooling, \
    Religion, FleshTone, Payment, SocialHistoryData, AmountCigarettes, AlcoholFrequency, AlcoholPeriod, Diagnosis, \
    ClassificationOfDiseases
from experiment.models import \
    QuestionnaireResponse as ExperimentQuestionnaireResponse, SubjectOfGroup, \
    Group, \
    ComponentConfiguration, Questionnaire, DataConfigurationTree, EEGData, \
    EEGSetting, EMGData, EMGSetting, TMSData, \
    TMSSetting, AdditionalData, DigitalGamePhaseData, Stimulus, \
    GenericDataCollectionData, \
    ContextTree, SubjectStepData, EEGElectrodePositionSetting, \
    SurfaceElectrode, IntramuscularElectrode, \
    NeedleElectrode, EMGElectrodeSetting, EMGIntramuscularPlacement, \
    EMGSurfacePlacement, EMGNeedlePlacement, ComponentAdditionalFile, ResearchProject, Experiment

from experiment.views import get_block_tree, get_experimental_protocol_image, \
    get_description_from_experimental_protocol_tree, get_sensors_position, \
    create_nwb_file, \
    list_data_configuration_tree, date_of_first_data_collection

from survey.abc_search_engine import Questionnaires
from survey.views import limesurvey_available
from survey.survey_utils import QuestionnaireUtils

DEFAULT_LANGUAGE = 'pt-BR'

METADATA_DIRECTORY = 'Questionnaire_metadata'

INPUT_DATA_KEYS = [
    'base_directory', 'export_per_participant', 'export_per_questionnaire',
    'per_participant_directory', 'per_questionnaire_directory', 'export_filename',
    'questionnaires'
]

directory_structure = [
    {
        'per_questionnaire':
            ['root', 'base_directory', 'export_per_questionnaire'],
        'per_participant':
            ['root', 'base_directory', 'export_per_participant'],
        'participant': ['root', 'base_directory'],
        'diagnosis': ['root', 'base_directory'],
    }
]

# Valid for all questionnaires (no distinction amongst questionnaires)
INCLUDED_QUESTIONNAIRE_FIELDS = [
    {
        'field': 'participant_code',
        'header': {
            'code': 'participant_code',
            'full': _('Participant code'),
            'abbreviated': _('Participant code')
        },
        'model': 'patient.patient', 'model_field': 'code'
    },
]

LICENSES = {
    0: {'name': 'CC', 'path': 'https://creativecommons.org', 'title': 'Creative Commons'},
    1: {'name': '©', 'path': 'https://simple.wikipedia.org/wiki/Copyright', 'title': 'Copyright'},
}

PROTOCOL_IMAGE_FILENAME = 'Protocol_image.png'
PROTOCOL_DESCRIPTION_FILENAME = 'Experimental_protocol_description.txt'
EEG_DEFAULT_SETTING_FILENAME = 'eeg_default_setting.json'
EEG_SETTING_FILENAME = 'eeg_setting_description.json'
TMS_DATA_FILENAME = 'tms_data_description.json'
HOTSPOT_MAP = 'hotspot_map.png'
EMG_SETTING_FILENAME = 'emg_setting_description.json'
EMG_DEFAULT_SETTING = 'emg_default_setting.json'
TMS_DEFAULT_SETTING_FILENAME = 'tms_default_setting.json'
CONTEXT_TREE_DEFAULT = 'context_tree_default.json'


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def to_number(value):
    return int(float(value))


def save_to_csv(complete_filename, rows_to_be_saved, filesformat_type, mode='w'):
    """
    :param complete_filename: filename and directory structure where file is
    going to be saved
    :param rows_to_be_saved: list of rows that are going to be written on the
    file
    :param filesformat_type: file extension
    :param mode: mode for openning file
    :return:
    """

    if filesformat_type == 'tsv':
        separator = '\t'
    else:
        separator = ','

    with open(complete_filename.encode('utf-8'), mode, newline='', encoding='UTF-8') as csv_file:
        export_writer = csv.writer(
            csv_file, quotechar='"', quoting=csv.QUOTE_NONNUMERIC, delimiter=separator
        )
        for row in rows_to_be_saved:
            export_writer.writerow(row)


def replace_multiple_choice_question_answers(responses_short, question_list):
    """Get responses list - after limesurvey participants answers obtained from
    get_responses_by_token or get_responses limesurvey api methods - that
    are multiple choices/multiple choices with comments question types (from
    question_list), and replaces the options that was not selected by
    participants with a 'N' (options that was selected have 'Y' - or 'S'
    in Portuguese - filled.
    :param responses_short: double array with questions in first line and answers
    in the other lines
    :param question_list: list of multiple choice/multiple choice with
    comments questions types
    Obs.: modifies responses list
    """
    i = 0
    m = len(responses_short[0])
    while i < m:
        question_match = re.match('(^.+)\[', responses_short[0][i])
        question = question_match.group(1) if question_match else None
        if question and question in [
            q['title'] for q in question_list if q['title'] == question
        ]:
            index_subquestions = []
            while i < m and question in responses_short[0][i]:
                index_subquestions.append(i)
                i += 1
            for j in range(1, len(responses_short) - 1):
                filled = False
                for k in index_subquestions:
                    if responses_short[j][k] != '':
                        filled = True
                        break
                if filled:
                    for k in index_subquestions:
                        if responses_short[j][k] == '':
                            responses_short[j][k] = 'N'
        else:
            i += 1


def create_directory(basedir, path_to_create):
    """Create a directory
    :param basedir: directory that already exists (parent path where new path must be included)
    :param path_to_create: directory to be created
    :return:
            - '' if path was correctly created or error message if there was an error
            - complete_path -> basedir + path created
    """
    if not path.exists(basedir.encode('utf-8')):
        return _('Base path does not exist'), ''

    complete_path = path.join(basedir, path_to_create)
    if not path.exists(complete_path.encode('utf-8')):
        makedirs(complete_path.encode('utf-8'))

    return '', complete_path


def is_patient_active(subject_id):
    response = False

    if is_number(subject_id):
        patient_id = to_number(subject_id)

        if QuestionnaireResponse.objects.filter(patient_id=patient_id).exists():
            if not Patient.objects.filter(pk=patient_id)[0].removed:
                response = True

    return response


class LogMessages:
    def __init__(self, user, file_name=path.join(settings.MEDIA_ROOT, 'export_log')):
        self.user = user
        self.file_name = file_name

    def log_message(self, text, param1='', param2=''):
        current_time = datetime.now()

        text_message = '%s %s %s %s %s' % (smart_str(current_time), smart_str(self.user),
                                           smart_str(text), smart_str(param1), smart_str(param2))
        with open(self.file_name.encode('utf-8'), 'a', encoding='UTF-8') as f:
            file_log = File(f)
            file_log.write(text_message)

        file_log.close()


class ExportExecution:

    def __init__(self, user_id, export_id):
        self.files_to_zip_list = []
        self.directory_base = ''
        self.base_directory_name = path.join(settings.MEDIA_ROOT, 'export')
        self.set_directory_base(user_id, export_id)
        self.base_export_directory = ''
        self.user_name = None
        self.input_data = {}
        self.per_participant_data = {}
        self.per_participant_data_from_experiment = {}
        self.participants_per_entrance_questionnaire = {}
        self.participants_per_experiment_questionnaire = {}
        self.questionnaires_experiment_responses = {}
        self.root_directory = ''
        self.participants_filtered_data = []
        self.per_group_data = {}
        self.questionnaire_utils = QuestionnaireUtils()

    @staticmethod
    def _temp_method_to_remove_undesirable_line(fields):
        items = [item for item in fields if 'participant_code' in item]
        for item in items:
            fields.remove(item)

    @staticmethod
    def update_duplicates(fields):
        """
        Update duplicates in fields list by adding numbers for duplicates, started
        in 1, then 2 etc.
        :param fields: list
        """
        for field in fields:
            duplicated_indexes = [i for i, duplicated_fields in enumerate(fields) if field == duplicated_fields]
            if len(duplicated_indexes) > 1:
                j = 1
                for i in duplicated_indexes:
                    fields[i] += str(j)
                    j += 1

    def get_username(self, request):
        self.user_name = None
        if request.user.is_authenticated():
            self.user_name = request.user.username
        return self.user_name

    def set_directory_base(self, user_id, export_id):
        self.directory_base = path.join(self.base_directory_name, str(user_id), str(export_id))

    def get_directory_base(self):
        return self.directory_base  # MEDIA_ROOT/export/username_id/export_id

    def create_export_directory(self):
        base_directory = self.get_input_data('base_directory')
        error_msg, self.base_export_directory = create_directory(self.get_directory_base(), base_directory)
        return error_msg

    def get_export_directory(self):

        # MEDIA_ROOT/export/username_id/export_id/data
        return self.base_export_directory

    def read_configuration_data(self, json_file, update_input_data=True):
        json_data = open(json_file)
        input_data_temp = json.load(json_data)
        if update_input_data:
            self.input_data = input_data_temp
        json_data.close()

        return input_data_temp

    def is_input_data_consistent(self):
        """Verify if important tags from input_data are available
        :return: bool
        """
        for data_key in INPUT_DATA_KEYS:
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

    def include_in_per_participant_data_from_experiment(
            self, to_be_included_list, participant_id, questionnaire_id, token_id, step):
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

    def include_group_data(self, groups, subjects_of_groups=None):
        """
        :param groups: list of groups
        :param subjects_of_groups: participants
        """
        surveys = Questionnaires()
        header_step_list = ['Step', 'Step identification', 'Path questionnaire', 'Data completed']
        for group_id in groups:
            group = get_object_or_404(Group, pk=group_id)
            if subjects_of_groups is not None:
                subjects_of_group = SubjectOfGroup.objects.filter(group=group, pk__in=subjects_of_groups)
            else:
                subjects_of_group = SubjectOfGroup.objects.filter(group=group)
            title = slugify(group.title).replace('-', '_')

            description = group.description  # TODO: code bloat
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
                'goalkeeper_game_data_directory': '',
                'goalkeeper_game_data_export_directory': '',
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
                    for path_experiment in create_list_of_trees(group.experimental_protocol, 'questionnaire'):
                        path_questionnaire = ''
                        size = len(path_experiment[0])
                        step = 1
                        while step < size:
                            path_questionnaire += path_experiment[0][step] + '/'
                            step += 2
                        questionnaire_configuration = get_object_or_404(
                            ComponentConfiguration, pk=path_experiment[-1][0])
                        component_type = questionnaire_configuration.component.component_type
                        questionnaire = Questionnaire.objects.get(id=questionnaire_configuration.component.id)
                        questionnaire_id = questionnaire.survey.lime_survey_id
                        if str(questionnaire_id) in self.get_input_data('questionnaires_from_experiments')[group_id]:
                            questionnaire_code = questionnaire.survey.code
                            self.questionnaire_utils.include_questionnaire_code_and_id(
                                questionnaire_code, str(questionnaire_id))
                            configuration_tree_list = DataConfigurationTree.objects.filter(
                                component_configuration=questionnaire_configuration)

                            for data_configuration_tree in configuration_tree_list:
                                for subject_of_group in subjects_of_group:
                                    experiment_questionnaire_response_list = \
                                        ExperimentQuestionnaireResponse.objects.filter(
                                            data_configuration_tree_id=data_configuration_tree.id,
                                            subject_of_group=subject_of_group)
                                    for questionnaire_response in experiment_questionnaire_response_list:
                                        token_id = questionnaire_response.token_id
                                        completed = surveys.get_participant_properties(
                                            questionnaire_id, token_id, 'completed')
                                        # load complete questionnaires data
                                        if completed is not None and completed != 'N' and completed != '':
                                            subject_code = questionnaire_response.subject_of_group.subject.patient.code
                                            step_number = path_experiment[0][4]
                                            step_identification = questionnaire_configuration.component.identification
                                            protocol_step_list = [
                                                header_step_list,
                                                [step_number, step_identification, path_questionnaire, completed]
                                            ]
                                            questionnaire_response_dic = {
                                                'token_id': token_id,
                                                'questionnaire_id': questionnaire_id,
                                                'questionnaire_code': questionnaire_code,
                                                'data_configuration_tree_id': data_configuration_tree.id,
                                                'subject_id':
                                                    questionnaire_response.subject_of_group.subject.patient.id,
                                                'subject_code': subject_code,
                                                'directory_step_name': 'Step_' + str(step_number) + '_' +
                                                                       component_type.upper(),
                                                'protocol_step_list': protocol_step_list,
                                            }

                                            if subject_code not in \
                                                    self.per_group_data[group_id]['data_per_participant']:
                                                self.per_group_data[group_id]['data_per_participant'][subject_code] = {}
                                                self.per_group_data[group_id]['data_per_participant'][subject_code][
                                                    'token_list'
                                                ] = []

                                            self.per_group_data[group_id]['data_per_participant'][subject_code][
                                                'token_list'
                                            ].append(questionnaire_response_dic)

                                            if questionnaire_id not in self.per_group_data[
                                                group_id
                                            ]['questionnaires_per_group']:
                                                self.per_group_data[
                                                    group_id
                                                ]['questionnaires_per_group'][questionnaire_id] = {
                                                    'questionnaire_code': questionnaire_code,
                                                    'header_filtered_list': [],
                                                    'token_list': []
                                                }

                                            if token_id not in self.per_group_data[group_id][
                                                'questionnaires_per_group'
                                            ][questionnaire_id]['token_list']:
                                                self.per_group_data[group_id]['questionnaires_per_group'][
                                                    questionnaire_id
                                                ]['token_list'].append(questionnaire_response_dic)

            if group.experimental_protocol is not None:
                if self.get_input_data('component_list')['per_additional_data']:
                    for subject_of_group in subjects_of_group:
                        subject_step_data_query = SubjectStepData.objects.filter(
                            subject_of_group=subject_of_group, data_configuration_tree=None)
                        data_collections = [{
                            'component_configuration': None,
                            'path': None,
                            'subject_step_data': subject_step_data_query[0] if subject_step_data_query else None,
                            'additional_data_list': AdditionalData.objects.filter(
                                subject_of_group=subject_of_group, data_configuration_tree=None),
                        }]
                        for additional_data_path in create_list_of_trees(group.experimental_protocol, None):
                            component_configuration = ComponentConfiguration.objects.get(pk=additional_data_path[-1][0])
                            data_configuration_tree_id = list_data_configuration_tree(
                                component_configuration.id, [item[0] for item in additional_data_path])

                            additional_data_list = None
                            if data_configuration_tree_id:
                                additional_data_list = AdditionalData.objects.filter(
                                        subject_of_group=subject_of_group,
                                        data_configuration_tree_id=data_configuration_tree_id)

                            data_collections.append({
                                'component_configuration': component_configuration,
                                'path': path,
                                'subject_step_data': subject_step_data_query[0] if subject_step_data_query else None,
                                'additional_data_list': additional_data_list,
                                'step_number': additional_data_path[-1][-1],
                            })

                        for data in data_collections:
                            if data['additional_data_list']:
                                if data['component_configuration']:
                                    component_type = data['component_configuration'].component.component_type
                                    step_number = data['step_number']
                                else:
                                    step_number = 0
                                    component_type = 'experimental_protocol'  # root
                                for additional_data in data['additional_data_list']:
                                    subject_code = additional_data.subject_of_group.subject.patient.code
                                    additional_data_file_list = []
                                    for additional_data_file in additional_data.additional_data_files.all():
                                        additional_data_file_list.append({
                                            'additional_data_filename': additional_data_file
                                        })
                                    if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                        self.per_group_data[group_id]['data_per_participant'][subject_code] = {}

                                    if 'additional_data_list' not in self.per_group_data[group_id][
                                        'data_per_participant'
                                    ][subject_code]:
                                        self.per_group_data[group_id]['data_per_participant'][subject_code][
                                            'additional_data_list'] = []
                                    if component_type not in self.per_group_data[group_id]['data_per_participant'][
                                        subject_code
                                    ]:
                                        self.per_group_data[group_id]['data_per_participant'][subject_code][
                                            component_type] = {'data_index': 1}
                                    else:
                                        self.per_group_data[group_id]['data_per_participant'][subject_code][
                                            component_type]['data_index'] += 1

                                    index = str(self.per_group_data[group_id]['data_per_participant'][subject_code][
                                                    component_type]['data_index'])
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'additional_data_list'
                                    ].append({
                                        'description': additional_data.description,
                                        'step_number': step_number,
                                        'component_type': component_type,
                                        'directory_step_name': 'Step_' + str(step_number) + '_' +
                                                               component_type.upper(),
                                        'additional_data_directory': 'AdditionalData_' + index,
                                        'additional_data_file_list': additional_data_file_list,
                                    })

                if self.get_input_data('component_list')['per_eeg_raw_data'] or \
                        self.get_input_data('component_list')['per_eeg_nwb_data']:

                    for path_eeg in create_list_of_trees(group.experimental_protocol, 'eeg'):
                        eeg_component_configuration = ComponentConfiguration.objects.get(pk=path_eeg[-1][0])
                        component_step = eeg_component_configuration.component

                        self.per_group_data[group_id]['eeg_default_setting_id'] = \
                            eeg_component_configuration.component.eeg.eeg_setting.id
                        step_number = path_eeg[-1][4]
                        step_identification = path_eeg[-1][3]

                        data_configuration_tree_id = list_data_configuration_tree(
                            eeg_component_configuration.id, [item[0] for item in path_eeg])

                        for subject_of_group in subjects_of_group:
                            eeg_data_list = EEGData.objects.filter(
                                subject_of_group=subject_of_group,
                                data_configuration_tree_id=data_configuration_tree_id)
                            eeg_data_list = can_export_nwb(eeg_data_list)

                            for eeg_data in eeg_data_list:
                                subject_code = eeg_data.subject_of_group.subject.patient.code
                                sensors_positions_filename = get_sensors_position(eeg_data)

                                if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code] = {}

                                if 'eeg_data_list' not in \
                                        self.per_group_data[group_id]['data_per_participant'][subject_code]:
                                    self.per_group_data[group_id]['data_per_participant'][
                                        subject_code]['eeg_data_list'] = []
                                    self.per_group_data[group_id]['data_per_participant'][
                                        subject_code]['data_index'] = 1
                                else:
                                    self.per_group_data[group_id]['data_per_participant'][
                                        subject_code]['data_index'] += 1
                                index = str(
                                    self.per_group_data[group_id]['data_per_participant'][subject_code]['data_index'])
                                self.per_group_data[group_id]['data_per_participant'][
                                    subject_code
                                ]['eeg_data_list'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'setting_id': eeg_data.eeg_setting_id,
                                    'sensor_filename': sensors_positions_filename,
                                    'eeg_data_directory_name': 'EEGData_' + index,
                                    'data_configuration_tree_id': data_configuration_tree_id,
                                    'directory_step_name': 'Step_' + str(step_number) + '_'
                                                           + component_step.component_type.upper(),
                                    'export_nwb': self.get_input_data('component_list')['per_eeg_nwb_data'],
                                    'eeg_file_list': eeg_data.eeg_file_list,
                                })

                if self.get_input_data('component_list')['per_emg_data']:
                    for path_emg in create_list_of_trees(group.experimental_protocol, 'emg'):
                        emg_component_configuration = ComponentConfiguration.objects.get(pk=path_emg[-1][0])
                        component_step = emg_component_configuration.component

                        self.per_group_data[group_id]['emg_default_setting_id'] = \
                            emg_component_configuration.component.emg.emg_setting.id

                        step_number = path_emg[-1][4]
                        step_identification = path_emg[-1][3]

                        data_configuration_tree_id = list_data_configuration_tree(emg_component_configuration.id,
                                                                                  [item[0] for item in path_emg])
                        for subject_of_group in subjects_of_group:
                            emg_data_list = EMGData.objects.filter(
                                subject_of_group=subject_of_group,
                                data_configuration_tree_id=data_configuration_tree_id)

                            for emg_data in emg_data_list:
                                subject_code = emg_data.subject_of_group.subject.patient.code
                                if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code] = {}
                                if 'emg_data_list' not in self.per_group_data[group_id]['data_per_participant'][
                                    subject_code]:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'emg_data_list'] = []
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'data_index'] = 1
                                else:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'data_index'] += 1
                                index = str(self.per_group_data[group_id]['data_per_participant'][subject_code][
                                                'data_index'])
                                self.per_group_data[
                                    group_id
                                ]['data_per_participant'][subject_code]['emg_data_list'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'emg_data_directory_name': 'EMGData_' + index,
                                    'setting_id': emg_data.emg_setting.id,
                                    'directory_step_name': 'Step_' + str(step_number) + '_' +
                                                           component_step.component_type.upper(),
                                    'emg_file_list': emg_data.emg_files.all(),
                                })

                if self.get_input_data('component_list')['per_tms_data']:
                    for path_tms in create_list_of_trees(group.experimental_protocol, 'tms'):
                        tms_component_configuration = ComponentConfiguration.objects.get(pk=path_tms[-1][0])
                        component_step = tms_component_configuration.component
                        self.per_group_data[group_id]['tms_default_setting_id'] = \
                            tms_component_configuration.component.tms.tms_setting_id

                        step_number = path_tms[-1][4]
                        step_identification = path_tms[-1][3]

                        data_configuration_tree_id = list_data_configuration_tree(tms_component_configuration.id,
                                                                                  [item[0] for item in path_tms])
                        for subject_of_group in subjects_of_group:
                            tms_data_list = TMSData.objects.filter(
                                subject_of_group=subject_of_group,
                                data_configuration_tree_id=data_configuration_tree_id)

                            for tms_data in tms_data_list:
                                subject_code = tms_data.subject_of_group.subject.patient.code

                                if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code] = {}
                                if 'tms_data_list' not in self.per_group_data[group_id]['data_per_participant'][
                                    subject_code
                                ]:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'tms_data_list'] = []

                                self.per_group_data[group_id]['data_per_participant'][subject_code][
                                    'tms_data_list'
                                ].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'setting_id': tms_data.tms_setting_id,
                                    'tms_data_id': tms_data.id,
                                    'data_configuration_tree_id': data_configuration_tree_id,
                                    'directory_step_name': 'Step_' + str(step_number) + '_'
                                                           + component_step.component_type.upper()
                                })

                if self.get_input_data('component_list')['per_goalkeeper_game_data']:
                    for path_goalkeeper_game in create_list_of_trees(group.experimental_protocol, 'digital_game_phase'):
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
                        for subject_of_group in subjects_of_group:
                            digital_game_data_list = DigitalGamePhaseData.objects.filter(
                                subject_of_group=subject_of_group,
                                data_configuration_tree_id=data_configuration_tree_id)

                            for digital_game_data in digital_game_data_list:
                                subject_code = digital_game_data.subject_of_group.subject.patient.code
                                digital_game_file_list = []
                                for digital_game_file in digital_game_data.digital_game_phase_files.all():
                                    digital_game_file_list.append({'digital_game_file': digital_game_file})

                                if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code] = {}

                                if 'digital_game_data_list' not in self.per_group_data[
                                    group_id
                                ]['data_per_participant'][subject_code]:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'digital_game_data_list'] = []
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'data_index'] = 1
                                else:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'data_index'] += 1
                                index = str(self.per_group_data[group_id]['data_per_participant'][subject_code][
                                                'data_index'])
                                self.per_group_data[group_id]['data_per_participant'][subject_code][
                                    'digital_game_data_list'
                                ].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'directory_step_name': 'Step_' + str(step_number) + '_' +
                                                           component_step.component_type.upper(),
                                    'digital_game_data_directory': 'DigitalGamePhaseData_' + index,
                                    'digital_game_file_list': digital_game_file_list,
                                })

                if self.get_input_data('component_list')['per_stimulus_data']:
                    for path_stimulus in create_list_of_trees(group.experimental_protocol, 'stimulus'):
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
                                'directory_step_name': 'Experimental_protocol/' + 'Step_' + str(step_number) + '_' +
                                                       component_step.component_type.upper(),
                                'stimulus_file': stimulus_data
                            })

                if self.get_input_data('component_list')['per_generic_data']:
                    for path_generic in create_list_of_trees(group.experimental_protocol, 'generic_data_collection'):
                        generic_component_configuration = ComponentConfiguration.objects.get(pk=path_generic[-1][0])
                        component_step = generic_component_configuration.component
                        step_number = path_generic[-1][4]
                        step_identification = path_generic[-1][3]

                        data_configuration_tree_id = list_data_configuration_tree(
                            generic_component_configuration.id, [item[0] for item in path_generic])
                        for subject_of_group in subjects_of_group:
                            generic_data_collection_data_list = GenericDataCollectionData.objects.filter(
                                subject_of_group=subject_of_group,
                                data_configuration_tree_id=data_configuration_tree_id)

                            for generic_data_collection_data in generic_data_collection_data_list:
                                subject_code = generic_data_collection_data.subject_of_group.subject.patient.code
                                generic_data_collection_data_list = []
                                for generic_data in generic_data_collection_data.generic_data_collection_files.all():
                                    generic_data_collection_data_list.append({
                                        'generic_data_filename': path.join(settings.MEDIA_ROOT, generic_data.file.name)
                                    })

                                if subject_code not in self.per_group_data[group_id]['data_per_participant']:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code] = {}

                                if 'generic_data_collection_data_list' not in \
                                        self.per_group_data[group_id]['data_per_participant'][subject_code]:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'generic_data_collection_data_list'] = []
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'data_index'] = 1
                                else:
                                    self.per_group_data[group_id]['data_per_participant'][subject_code][
                                        'data_index'] += 1
                                index = str(self.per_group_data[group_id]['data_per_participant'][subject_code][
                                                'data_index'])
                                self.per_group_data[
                                    group_id
                                ]['data_per_participant'][subject_code]['generic_data_collection_data_list'].append({
                                    'step_number': step_number,
                                    'step_identification': step_identification,
                                    'directory_step_name': 'Step_' + str(step_number) + '_' +
                                                           component_step.component_type.upper(),
                                    'generic_data_collection_directory': 'Generic_Data_Collection_' + index,
                                    'generic_data_collection_file_list':
                                        generic_data_collection_data.generic_data_collection_files.all(),
                                })

        surveys.release_session_key()

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

        participants = Patient.objects.filter(removed=False).values_list('id')

        self.participants_filtered_data = participants.filter(id__in=participants_filtered_list)

    def get_participants_filtered_data(self):
        return self.participants_filtered_data

    def update_questionnaire_rules(self, questionnaire_id):

        header = []
        fields = []

        heading_type = self.get_heading_type()

        for row in INCLUDED_QUESTIONNAIRE_FIELDS:
            header_translated = _(row['header'][heading_type])
            header.append(smart_str(header_translated))
            fields.append(smart_str(row['field']))

        self.questionnaire_utils.append_questionnaire_header_and_field(
            questionnaire_id, header, fields,
            self.get_input_data('questionnaires'),
            self.get_input_data('questionnaires_from_experiment'))

    def update_questionnaire_experiment_rules(self, questionnaire_id):

        header = []
        fields = []

        heading_type = self.get_heading_type()

        for row in INCLUDED_QUESTIONNAIRE_FIELDS:
            header_translated = _(row['header'][heading_type])
            header.append(smart_str(header_translated))
            fields.append(smart_str(row['field']))

        self.questionnaire_utils.append_questionnaire_experiment_header_and_field(questionnaire_id, header, fields)

    def transform_questionnaire_data(self, patient_id, fields):

        for row in INCLUDED_QUESTIONNAIRE_FIELDS:

            model_db = apps.get_model(row['model'])

            model_data = model_db.objects.all()

            if model_data.filter(id=patient_id).exists():
                value = model_data.filter(id=patient_id).values_list(row['model_field'])[0][0]
            else:
                value = ''

            fields.append(smart_str(value))

        return fields

    def get_title(self, questionnaire_id):
        title = ''
        questionnaires = self.get_input_data('questionnaires')
        for questionnaire in questionnaires:
            if questionnaire_id == questionnaire['id']:
                title = questionnaire['questionnaire_name']
                break
        return title

    def get_title_experiment_questionnaire(self, questionnaire_id):

        title = ''
        questionnaires = self.get_input_data('questionnaires_from_experiments')
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
    def build_header_questionnaire_per_participant(header_participant_data, header_answer_list):
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

        # Building questionnaire_answer_list with row_participant data
        subject_code = row_participant_data[0]
        attribute = row_participant_data[1]
        for sublist in answer_list:
            answer = [subject_code, attribute]
            for item in sublist:
                answer.append(item)
            for item in row_participant_data[2:len(row_participant_data)]:
                answer.append(item)
            questionnaire_answer_list.append(answer)

        return questionnaire_answer_list

    def merge_participants_data_per_questionnaire_process(self, fields_description, participant_list):
        # Get fields from patient
        export_participant_row = self.process_participant_data(self.get_input_data('participants'), participant_list)

        # Merge fields from questionnaires and patient
        export_fields_list = []
        # Building the header
        export_row_list = fields_description[0][0:len(fields_description[0]) - 1]
        for field in export_participant_row[0]:
            export_row_list.append(field)
        export_fields_list.append(export_row_list)

        # Including the responses
        for fields in fields_description[1:fields_description.__len__()]:
            participation_code = fields[len(fields) - 1]
            export_row_list = fields[0:len(fields) - 1]
            for participant_fields in export_participant_row[1:export_participant_row.__len__()]:
                if participation_code == participant_fields[len(participant_fields) - 1]:
                    for field in participant_fields:
                        export_row_list.append(field)
            export_fields_list.append(export_row_list)

        return export_fields_list

    def process_per_questionnaire(self, heading_type, plugin):
        """
        :return: str - error message
        """
        error_msg = ''
        export_per_questionnaire_directory = ''
        export_metadata_directory = ''
        path_per_questionnaire = ''
        path_per_questionnaire_metadata = ''

        filesformat_type = self.get_input_data('filesformat_type')

        # Save per_participant data
        if self.get_input_data('export_per_questionnaire'):
            # Check if exist fields selected from questionnaires
            error_msg, path_per_questionnaire = create_directory(
                self.get_export_directory(), self.get_input_data('per_questionnaire_directory'))
            if error_msg != '':
                return error_msg
            export_per_questionnaire_directory = path.join(
                self.get_input_data('base_directory'), self.get_input_data('per_questionnaire_directory'))
            export_metadata_directory = path.join(
                self.get_input_data('base_directory'), self.get_input_data('questionnaire_metadata_directory'))
            error_msg, path_per_questionnaire_metadata = create_directory(
                self.get_export_directory(), self.get_input_data('questionnaire_metadata_directory'))
            if error_msg != '':
                return error_msg

        questionnaire_lime_survey = Questionnaires()

        for questionnaire in self.get_input_data('questionnaires'):

            questionnaire_id = questionnaire['id']
            # If it was selected ful answer for questionnaire responses
            questionnaire_language = self.get_input_data('questionnaire_language')[str(questionnaire_id)]
            if 'long' in self.get_input_data('response_type'):
                language_list = questionnaire_language['language_list']
            else:
                language_list = [questionnaire_language['output_language']]

            questionnaire_code = self.questionnaire_utils.get_questionnaire_code_from_id(questionnaire_id)
            if not plugin:
                # Ex. Per_questionnaire.Q123_aaa
                questionnaire_title = self.get_title_reduced(questionnaire_id=questionnaire_id)
                path_questionnaire = '%s_%s' % (str(questionnaire_code), questionnaire_title)
            else:
                random_forest = RandomForests.objects.first()
                if questionnaire_id == random_forest.admission_assessment.lime_survey_id:
                    path_questionnaire = 'QA_unified_admission_assessment'
                elif questionnaire_id == \
                        random_forest.surgical_evaluation.lime_survey_id:
                    path_questionnaire = 'QS_surgical_evaluation'
                elif questionnaire_id == \
                        random_forest.followup_assessment.lime_survey_id:
                    path_questionnaire = 'QF_unified_followup_assessment'
                else:
                    # TODO: error
                    pass

            # Path ex. data/Per_questionnaire/Q123_aaa
            error_msg, export_path = create_directory(path_per_questionnaire, path_questionnaire)
            if error_msg != '':
                return error_msg

            # Path ex. data/Per_questionnaire/Q123_aaa/
            export_directory = path.join(export_per_questionnaire_directory, path_questionnaire)

            # Path ex. data/Questionnaire_metadata/Q123_aaa
            error_msg, export_metadata_path = create_directory(path_per_questionnaire_metadata, path_questionnaire)
            if error_msg != '':
                return error_msg

            # Path: /data/Questionnaire_metadata/Q123_aaa
            export_questionnaire_metadata_directory = path.join(export_metadata_directory, path_questionnaire)

            for language in language_list:
                # Per_participant_data is updated by define_questionnaire method
                result = self.define_questionnaire(questionnaire, questionnaire_lime_survey, language)
                if result == Questionnaires.ERROR_CODE:
                    return result

                # Create directory for questionnaire:
                # <per_questionnaire>/<q_code_title>
                if self.get_input_data('export_per_questionnaire') and (len(result) > 1):
                    if not plugin:
                        export_filename = '%s_%s_%s' % (
                            questionnaire['prefix_filename_responses'], str(questionnaire_code), language)
                    else:
                        if questionnaire_id == \
                                RandomForests.objects.first().admission_assessment.lime_survey_id:
                            export_filename = '%s_%s' % (questionnaire['prefix_filename_responses'], 'QA_en')
                        elif questionnaire_id == \
                                RandomForests.objects.first().surgical_evaluation.lime_survey_id:
                            export_filename = '%s_%s' % (questionnaire['prefix_filename_responses'], 'QS_en')
                        elif questionnaire_id == \
                                RandomForests.objects.first().followup_assessment.lime_survey_id:
                            export_filename = '%s_%s' % (questionnaire['prefix_filename_responses'], 'QF_en')
                        else:
                            # TODO: error
                            pass

                    # Path ex. data/Per_questionnaire/Q123_aaa/Responses_Q123.csv
                    complete_filename = path.join(
                        export_path, export_filename + '.' + filesformat_type)
                    save_to_csv(complete_filename, result, filesformat_type)

                    # TODO (NES-911): extends conditional to the other parts
                    if not plugin:
                        # Get data for datapackage resource questionnaire
                        # response table schema
                        rows_participant_data = \
                            self.get_input_data('participants')['data_list']
                        answer_list = {
                            'fields': [], 'header': [], 'header_questionnaire': []
                        }
                        for question in questionnaire['output_list']:
                            answer_list['fields'].append(question['field'])
                            answer_list['header'].append(question['header'])
                            answer_list['header_questionnaire'].append(
                                question['header'])
                        # TODO (NES-991): treat error!
                        error, questions = QuestionnaireUtils.get_questions(
                            questionnaire_lime_survey, questionnaire_id,
                            language)
                        datapackage_json = {
                            'name': slugify(export_filename),
                            'title': export_filename,
                            'path': path.join(
                                export_directory, export_filename + '.'
                                                  + filesformat_type),
                            'format': filesformat_type,
                            'mediatype': 'text/' + filesformat_type,
                            'description': 'Questionnaire response',
                            'profile': 'tabular-data-resource',
                            'schema': {
                                'fields':
                                    self._set_questionnaire_response_fields(
                                        heading_type, rows_participant_data[0],
                                        answer_list, questions)
                            }
                        }
                    else:
                        datapackage_json = ''
                    self.files_to_zip_list.append([complete_filename, export_directory, datapackage_json])

            # Questionnaire metadata
            entrance_questionnaire = True
            # Create questionnaire fields file ('fields.csv') - metadata directory
            fields = self.questionnaire_utils.get_questionnaire_fields(
                questionnaire_id, entrance_questionnaire, self.get_input_data('questionnaires_from_experiments'))

            for language in questionnaire_language['language_list']:
                error, questionnaire_fields = self.questionnaire_utils.create_questionnaire_explanation_fields(
                        questionnaire_id, language, questionnaire_lime_survey, fields, entrance_questionnaire)
                if error:
                    return Questionnaires.ERROR_CODE  # TODO (NES-971): patternalize this

                export_filename = '%s_%s_%s.%s' % (
                    questionnaire['prefix_filename_fields'], str(questionnaire_code), language, filesformat_type)

                complete_filename = path.join(export_metadata_path, export_filename)

                # At this point of the championship, fix it right here
                self._temp_method_to_remove_undesirable_line(questionnaire_fields)

                save_to_csv(complete_filename, questionnaire_fields, filesformat_type)

                self.files_to_zip_list.append([
                    complete_filename, export_questionnaire_metadata_directory,
                    {
                        'name': slugify(
                            questionnaire['prefix_filename_fields'] + '_' + str(questionnaire_code) + '_' + language),
                        'title':
                            questionnaire['prefix_filename_fields'] + '_' + str(questionnaire_code) + '_' + language,
                        'path': path.join(export_questionnaire_metadata_directory, export_filename),
                        'format': filesformat_type, 'mediatype': 'text/' + filesformat_type,
                        'description': 'Questionnaire metadata',
                        'profile': 'tabular-data-resource',
                        'schema': {'fields': self._set_questionnaire_metadata_fields()}
                    }
                ])

        questionnaire_lime_survey.release_session_key()

        return error_msg

    def process_per_entrance_questionnaire(self, heading_type):
        filesformat_type = self.get_input_data('filesformat_type')

        path_participant_data = path.join(
            self.get_export_directory(),
            self.get_input_data('participant_data_directory')
        )
        if not path.exists(path_participant_data):
            # path ex. data/Participant_data
            error_msg, path_participant_data = create_directory(
                self.get_export_directory(), self.get_input_data('participant_data_directory'))
            if error_msg != '':
                return error_msg

        # path ex. data/Participant_data/Per_questionnaire
        error_msg, path_per_questionnaire = create_directory(
            path_participant_data, self.get_input_data('per_questionnaire_directory'))
        if error_msg != '':
            return error_msg

        # Path ex. data/Participant_data/Questionnaire_metadata
        error_msg, path_per_questionnaire_metadata = create_directory(
            path_participant_data, self.get_input_data('questionnaire_metadata_directory'))
        if error_msg != '':
            return error_msg

        # path ex. data/Participant_data/
        export_per_entrance_questionnaire_directory = path.join(
            self.get_input_data('base_directory'),
            self.get_input_data('participant_data_directory'))
        # path ex. data/Participant_data/Per_questionnaire/
        export_per_questionnaire_directory = path.join(
            export_per_entrance_questionnaire_directory,
            self.get_input_data('per_questionnaire_directory'))

        # Path ex. data/Participant_data/Questionnaire_metadata/
        export_metadata_directory = path.join(
            export_per_entrance_questionnaire_directory,
            self.get_input_data('questionnaire_metadata_directory'))

        questionnaire_lime_survey = Questionnaires()

        for questionnaire in self.get_input_data('questionnaires'):
            questionnaire_id = questionnaire['id']
            questionnaire_code = \
                self.questionnaire_utils.get_questionnaire_code_from_id(questionnaire_id)
            questionnaire_title = \
                self.get_title_reduced(questionnaire_id=questionnaire_id)
            path_questionnaire = \
                '%s_%s' % (str(questionnaire_code), questionnaire_title)

            # Path ex. data/Participant_data/Per_questionnaire/Q123_aaa/
            error_msg, export_path = create_directory(path_per_questionnaire, path_questionnaire)
            if error_msg != '':
                return error_msg
            # Path ex. data/Participant_data/Per_questionnaire/Q123_aaa/
            export_directory = path.join(export_per_questionnaire_directory, path_questionnaire)

            # Path ex. data/Participant_data/Questionnaire_metadata/Q123_aaa
            error_msg, export_metadata_path = create_directory(path_per_questionnaire_metadata, path_questionnaire)
            if error_msg != '':
                return error_msg

            # Path ex. data/Participant_data/Questionnaire_metadata/Q123_aaa/
            export_questionnaire_metadata_directory = path.join(export_metadata_directory, path_questionnaire)

            # Defining language to be displayed
            questionnaire_language = self.get_input_data('questionnaire_language')[str(questionnaire_id)]
            if 'long' in self.get_input_data('response_type'):
                language_list = questionnaire_language['language_list']
            else:
                language_list = [questionnaire_language['output_language']]

            entrance_questionnaire = True

            for language in language_list:
                # Get data for datapackage resource questionnaire response table schema
                rows_participant_data = self.get_input_data('participants')['data_list']
                answer_list = {'fields': [], 'header': [], 'header_questionnaire': []}
                for question in questionnaire['output_list']:
                    answer_list['fields'].append(question['field'])
                    answer_list['header'].append(question['header'])
                    answer_list['header_questionnaire'].append(question['header'])
                # TODO (NES-991): treat error!
                error, questions = QuestionnaireUtils.get_questions(
                    questionnaire_lime_survey, questionnaire_id, language)

                # per_participant_data is updated by define_questionnaire method
                fields_description = self.define_questionnaire(questionnaire, questionnaire_lime_survey, language)
                if self.get_input_data('export_per_questionnaire') and (len(fields_description) > 1):
                    export_filename = '%s_%s_%s' % (
                        questionnaire['prefix_filename_responses'], str(questionnaire_code), language)
                    # /data/Participant_data/Per_questionnaire/Q123_aaa/Responses_Q123.csv
                    complete_filename = path.join(export_path, export_filename + '.' + filesformat_type)
                    save_to_csv(complete_filename, fields_description, filesformat_type)

                    self.files_to_zip_list.append([
                        complete_filename, export_directory,
                        {
                            'name': slugify(export_filename), 'title': export_filename,
                            'path': path.join(export_directory, export_filename + '.' + filesformat_type),
                            'format': filesformat_type, 'mediatype': 'text/' + filesformat_type,
                            'description': 'Questionnaire response',
                            'profile': 'tabular-data-resource',
                            'schema': {
                                'fields': self._set_questionnaire_response_fields(
                                    heading_type, rows_participant_data[0], answer_list, questions)
                            }
                        }
                    ])

                # Create questionnaire fields file ('fields.csv') in
                # Questionnaire_metadata directory
                fields = self.questionnaire_utils.get_questionnaire_fields(
                    questionnaire_id, entrance_questionnaire,
                    self.get_input_data('questionnaires_from_experiments'))

                error, questionnaire_fields = \
                    self.questionnaire_utils.create_questionnaire_explanation_fields(
                        questionnaire_id, language, questionnaire_lime_survey, fields, entrance_questionnaire)
                export_filename = '%s_%s_%s' % (
                    questionnaire['prefix_filename_fields'], str(questionnaire_code), language)
                # Path ex. data/Participant_data/Questionnaire_metadata/Q123_aaa/Fields_Q123.csv'
                complete_filename = path.join(export_metadata_path, export_filename + '.' + filesformat_type)

                # At this point of the championship, fix it right here
                self._temp_method_to_remove_undesirable_line(questionnaire_fields)

                save_to_csv(complete_filename, questionnaire_fields, filesformat_type)

                self.files_to_zip_list.append([
                    complete_filename, export_questionnaire_metadata_directory,
                    {
                        'name': slugify(export_filename), 'title': export_filename,
                        'path': path.join(export_questionnaire_metadata_directory,
                                          export_filename + '.' + filesformat_type),
                        'format': filesformat_type, 'mediatype': 'text/' + filesformat_type,
                        'description': 'Questionnaire metadata',
                        'profile': 'tabular-data-resource',
                        'schema': {
                            'fields': self._set_questionnaire_metadata_fields()
                        }
                    }
                ])

        questionnaire_lime_survey.release_session_key()

        return error_msg

    def create_group_data_directory(self):
        # path ex. data/Experiment_data
        error_msg, path_experiment_data = create_directory(
            self.get_export_directory(), self.get_input_data('experiment_data_directory'))
        if error_msg != '':
            return error_msg

        # path ex. data/Experiment_data
        export_experiment_data = path.join(self.get_input_data('base_directory'),
                                           self.get_input_data('experiment_data_directory'))

        for group_id in self.per_group_data:
            group_title = self.per_group_data[group_id]['group']['title']
            directory_group_name = 'Group_' + group_title

            # path ex. data/Experiment_data/Group_xxx
            error_msg, directory_group = create_directory(path_experiment_data, directory_group_name)
            if error_msg != '':
                return error_msg

            # path ex. data/Experiment_data/Group_xxx
            export_directory_group = path.join(export_experiment_data, directory_group_name)

            self.per_group_data[group_id]['group']['directory'] = directory_group
            self.per_group_data[group_id]['group']['export_directory'] = export_directory_group

            if self.per_group_data[group_id]['questionnaires_per_group']:
                # path ex.
                # data/Experiment_data/Group_xxx/Per_questionnaire
                error_msg, directory_questionnaire_data = create_directory(
                    directory_group, self.get_input_data('per_questionnaire_directory'))
                if error_msg != '':
                    return error_msg
                # path ex. data/Experiment_data/Group_xxx/Per_questionnaire/
                export_directory_questionnaire_data = path.join(
                    export_directory_group, self.get_input_data('per_questionnaire_directory'))

                # path ex. data/Experiment_data/Group_xxx
                # /Questionnaire_metadata
                error_msg, directory_questionnaire_metadata = create_directory(
                    directory_group, self.get_input_data('questionnaire_metadata_directory'))
                if error_msg != '':
                    return error_msg
                # path ex. data/Experiment_data/Group_xxx/Questionnaire_metadata/
                export_directory__questionnaire_metadata = path.join(
                    export_directory_group, self.get_input_data('questionnaire_metadata_directory'))

                self.per_group_data[group_id]['group'][
                    'questionnaire_data_directory'] = directory_questionnaire_data
                self.per_group_data[group_id]['group'][
                    'questionnaire_data_export_directory'] = export_directory_questionnaire_data
                self.per_group_data[group_id]['group'][
                    'questionnaire_metadata_directory'] = directory_questionnaire_metadata
                self.per_group_data[group_id]['group'][
                    'questionnaire_metadata_export_directory'] = export_directory__questionnaire_metadata

            if self.per_group_data[group_id]['data_per_participant']:
                # path ex. data/Experiment_data/Group_xxx/Per_participant
                error_msg, directory_participant_data = create_directory(
                    directory_group, self.get_input_data('per_participant_directory'))
                if error_msg != '':
                    return error_msg
                # path ex. data/Experiment_data/Group_xxx/Per_participant/
                participant_data_export_directory = path.join(
                    export_directory_group, self.get_input_data('per_participant_directory'))

                self.per_group_data[group_id]['group'][
                    'participant_data_directory'] = directory_participant_data
                self.per_group_data[group_id]['group'][
                    'participant_data_export_directory'] = participant_data_export_directory

            if self.get_input_data('component_list')['per_goalkeeper_game_data']:
                # path ex. data/Experiment_data/Group_xxx/Goalkeeper_game_data
                error_msg, directory_participant_data = create_directory(
                    directory_group, self.get_input_data('goalkeeper_game_data_directory'))
                if error_msg != '':
                    return error_msg
                # path ex. data/Experiment_data/Group_xxx/Goalkeeper_game_data/
                participant_data_export_directory = path.join(
                    export_directory_group, self.get_input_data('goalkeeper_game_data_directory'))

                self.per_group_data[group_id]['group'][
                    'goalkeeper_game_data_directory'] = directory_participant_data
                self.per_group_data[group_id]['group'][
                    'goalkeeper_game_data_export_directory'] = participant_data_export_directory

        return error_msg

    def process_per_experiment_questionnaire(self, heading_type, per_experiment_plugin=False):
        """
        :param heading_type: str, type of header csv columns
        :param per_experiment_plugin: bool - if sending to plugin by experiment
        :return:
        """
        error_msg = ''

        filesformat_type = self.get_input_data('filesformat_type')

        for group_id in self.per_group_data:
            if 'questionnaires_per_group' in self.per_group_data[group_id]:
                questionnaire_list = self.per_group_data[group_id]['questionnaires_per_group']
                for questionnaire_id in questionnaire_list:
                    # Create questionnaire_name_directory
                    questionnaires = questionnaire_list[questionnaire_id]
                    dir_questionnaire_step = dict()
                    dir_questionnaire_step[questionnaire_id] = set()

                    questionnaire_data = self.get_input_data('questionnaires_from_experiments')[
                        group_id
                    ][str(questionnaire_id)]
                    questionnaire_code = questionnaires['questionnaire_code']
                    questionnaire_title = self.redefine_questionnaire_title(questionnaire_data['questionnaire_name'])

                    prefix_filename_fields = questionnaire_data['prefix_filename_fields']
                    # Ex. Q123_aaa
                    directory_questionnaire_name = '%s_%s' % (str(questionnaire_code), questionnaire_title)
                    if per_experiment_plugin:
                        randomforests = RandomForests.objects.first()
                        if questionnaire_id == randomforests.admission_assessment.lime_survey_id:
                            directory_questionnaire_name = 'QA_unified_admission_assessment'
                        elif questionnaire_id == randomforests.surgical_evaluation.lime_survey_id:
                            directory_questionnaire_name = 'QS_surgical_evaluation'
                        elif questionnaire_id == \
                                randomforests.followup_assessment.lime_survey_id:
                            directory_questionnaire_name = \
                                'QF_unified_followup_assessment'

                    # Metadata directory for export
                    # Path ex. data/Experiment_data/Group_xxx/Questionnaire_metadata/
                    metadata_directory = self.per_group_data[group_id]['group']['questionnaire_metadata_directory']
                    # Path ex. data/Experiment_data/Group_xxx/Questionnaire_metadata/Q123_aaa/
                    export_metadata_directory = path.join(
                        self.per_group_data[group_id]['group']['questionnaire_metadata_export_directory'],
                        directory_questionnaire_name)
                    # Path ex. data/Experiment_data/Group_xxx/Questionnaire_metadata/Q123_aaa/
                    error_msg, complete_export_metadata_path = create_directory(
                        metadata_directory, directory_questionnaire_name)
                    if error_msg != '':
                        return error_msg

                    questionnaire_language = self.get_input_data('questionnaire_language')[str(questionnaire_id)]
                    if 'long' in self.get_input_data('response_type'):
                        language_list = questionnaire_language['language_list']
                    else:
                        language_list = [questionnaire_language['output_language']]

                    # Get unique steps for each questionnaire so we can
                    # aggregate directories by steps if there are same
                    # questionnaire in more than one step
                    for token in questionnaires['token_list']:
                        dir_questionnaire_step[questionnaire_id].add(token['directory_step_name'])

                    for token in questionnaires['token_list']:
                        path_group_per_questionnaire = self.per_group_data[
                            group_id
                        ]['group']['questionnaire_data_directory']
                        error_msg, complete_export_path = create_directory(
                            path_group_per_questionnaire, token['directory_step_name'])
                        if error_msg != '':
                            return error_msg

                        export_directory_per_questionnaire = self.per_group_data[
                            group_id
                        ]['group']['questionnaire_data_export_directory']
                        export_directory = path.join(export_directory_per_questionnaire, token['directory_step_name'])

                        # Save file with data
                        fields_description = []

                        for language in language_list:
                            # Q123_<questionnaire_title>_<lang>.csv
                            export_filename = str(questionnaire_code) + '_' + questionnaire_title + '_' + language
                            if per_experiment_plugin:
                                randomforests = RandomForests.objects.first()
                                if questionnaire_id == randomforests.admission_assessment.lime_survey_id:
                                    export_filename = 'QA_unified_admission_assessment_en'
                                elif questionnaire_id == randomforests.surgical_evaluation.lime_survey_id:
                                    export_filename = 'QS_surgical_evaluation_en'
                                elif questionnaire_id == \
                                        randomforests.followup_assessment.lime_survey_id:
                                    export_filename = \
                                        'QF_unified_followup_assessment_en'
                                else:
                                    # TODO: error
                                    pass
                            # data/Experiment_data/Group_xxx/Per_questionnaire/Step_x_QUESTIONNAIRE/
                            # Q123_<questionnaire_title>_<lang>.csv
                            complete_filename = path.join(
                                complete_export_path, export_filename + '.' + filesformat_type)
                            token_id = token['token_id']
                            answer_list = self.questionnaires_responses[str(questionnaire_id)][token_id][language]
                            rows_participant_data = self.get_participant_row_data(token['subject_code'])
                            participant_response_list = self.merge_questionnaire_answer_list_per_participant(
                                rows_participant_data[1], answer_list[1:len(answer_list)])
                            for sublist in participant_response_list:
                                index = len(fields_description) + 1
                                fields_description.insert(index, sublist)

                        # Header
                        if fields_description:
                            field_type = 'fields' if heading_type == 'code' else 'header_questionnaire'
                            header = self.build_header_questionnaire_per_participant(
                                rows_participant_data[0], answer_list[0][field_type])
                            fields_description.insert(0, header)

                            ###
                            # Jury-rig detected!
                            file_exists = False
                            for item in self.files_to_zip_list:
                                if complete_filename in item[0]:
                                    # Append in complete_filename fields_description in the file
                                    # that already exists
                                    save_to_csv(complete_filename, fields_description[1:], filesformat_type, mode='a')
                                    file_exists = True
                                    break
                            ###

                            # Save array list into a file to expor
                            questionnaire_lime_survey = Questionnaires()
                            if not file_exists:
                                save_to_csv(complete_filename, fields_description, filesformat_type)
                                # TODO (NES-991): treat possible error
                                error, questions = QuestionnaireUtils.get_questions(
                                    questionnaire_lime_survey, questionnaire_id, language)
                                self.files_to_zip_list.append([
                                    complete_filename, export_directory,
                                    {
                                        'name': slugify(export_filename), 'title': export_filename,
                                        'path': path.join(export_directory, export_filename + '.' + filesformat_type),
                                        'format': filesformat_type, 'mediatype': 'text/' + filesformat_type,
                                        'description': 'Questionnaire response',
                                        'profile': 'tabular-data-resource',
                                        'schema': {
                                            'fields': self._set_questionnaire_response_fields(
                                                heading_type, rows_participant_data[0], answer_list[0], questions)
                                        }
                                    }
                                ])

                    # Questionnaire metadata directory
                    entrance_questionnaire = False
                    # Create questionnaire fields file ('fields.csv') in
                    # Questionnaire_metadata directory
                    fields = self.questionnaire_utils.get_questionnaire_experiment_fields(questionnaire_id)
                    for language in questionnaire_language['language_list']:
                        error, questionnaire_fields = self.questionnaire_utils.create_questionnaire_explanation_fields(
                            str(questionnaire_id), language, questionnaire_lime_survey, fields, entrance_questionnaire)

                        # Build metadata export - Fields_Q123.csv
                        export_filename = '%s_%s_%s.%s' % (
                            prefix_filename_fields, str(questionnaire_code), language, filesformat_type)
                        if per_experiment_plugin:
                            randomforests = RandomForests.objects.first()
                            if questionnaire_id == randomforests.admission_assessment.lime_survey_id:
                                export_filename = '%s_%s_%s.%s' % (
                                    prefix_filename_fields, 'QA', language, filesformat_type)
                            elif questionnaire_id == randomforests.surgical_evaluation.lime_survey_id:
                                export_filename = '%s_%s_%s.%s' % (
                                    prefix_filename_fields, 'QS', language, filesformat_type)

                        complete_filename = path.join(complete_export_metadata_path, export_filename)
                        save_to_csv(complete_filename, questionnaire_fields, filesformat_type)

                        self.files_to_zip_list.append([
                            complete_filename, export_metadata_directory,
                            {
                                'name': slugify(prefix_filename_fields + '_' + questionnaire_code),
                                'title': prefix_filename_fields + '_' + questionnaire_code,
                                'path': path.join(export_metadata_directory, export_filename),
                                'format': filesformat_type, 'mediatype': 'text/' + filesformat_type,
                                'description': 'Questionnaire metadata',
                                'profile': 'tabular-data-resource',
                                'schema': {
                                    'fields': self._set_questionnaire_metadata_fields()
                                }
                            }
                        ])

                    questionnaire_lime_survey.release_session_key()

        return error_msg

    def process_per_participant(self, heading_type, participants_plugin):

        error_msg = ''

        if self.get_input_data('export_per_participant'):
            # Path ex. data/Per_participant/
            error_msg, path_per_participant = create_directory(
                self.get_export_directory(), self.get_input_data('per_participant_directory'))
            if error_msg != '':
                return error_msg

            prefix_filename_participant = 'Participant_'
            # Path ex. data/Per_participant/
            export_directory_base = path.join(
                self.get_input_data('base_directory'), self.get_input_data('per_participant_directory'))

            questionnaire_lime_survey = Questionnaires()

            for participant_code in self.get_per_participant_data():
                # path ex. Participant_P123
                path_participant = prefix_filename_participant + str(participant_code)
                # path ex. data/Per_participant/Participant_P123/
                error_msg, participant_path = create_directory(path_per_participant, path_participant)
                if error_msg != '':
                    return error_msg

                # Make the list of questionnaires ordered: for unitary tests.
                # Because the loop bellow can come in whatever order and so the mocks
                # associated. See test_export_per_participant_add_questionnaire_response_file_to_datapackage_json_file2
                # comments
                questionnaires = self.get_per_participant_data(participant_code)
                ordered_questionnaires = OrderedDict(sorted(questionnaires.items()))

                for questionnaire_code in ordered_questionnaires:
                    questionnaire_id = int(self.questionnaire_utils.get_questionnaire_id_from_code(questionnaire_code))
                    title = self.get_title_reduced(questionnaire_id=int(questionnaire_id))
                    questionnaire_directory_name = '%s_%s' % (str(questionnaire_code), title)
                    if participants_plugin:
                        randomforests = RandomForests.objects.first()
                        if questionnaire_id == randomforests.admission_assessment.lime_survey_id:
                            questionnaire_directory_name = 'QA_unified_admission_assessment'
                        elif questionnaire_id == randomforests.surgical_evaluation.lime_survey_id:
                            questionnaire_directory_name = 'QS_surgical_evaluation'
                        elif questionnaire_id == \
                                randomforests.followup_assessment.lime_survey_id:
                            questionnaire_directory_name = \
                                'QF_unified_followup_assessment'
                        else:
                            # TODO: error
                            pass
                    # Create questionnaire directory
                    # path ex. data/Per_participant/Participant_<participant_code>/questionnaire_code_Title/
                    error_msg, path_per_questionnaire = create_directory(participant_path, questionnaire_directory_name)
                    # path ex. data/Per_participant/QCode_Title/
                    export_questionnaire_directory = path.join(
                        path.join(export_directory_base, path_participant), questionnaire_directory_name)

                    # add participant personal data header
                    questionnaire_header = self.questionnaire_utils.get_header_questionnaire(questionnaire_id)
                    participant_data_header = self.get_input_data('participants')['data_list'][0]
                    header = self.build_header_questionnaire_per_participant(
                        participant_data_header, questionnaire_header[0:len(questionnaire_header) - 1])

                    # select language list
                    questionnaire_language = self.get_input_data('questionnaire_language')[str(questionnaire_id)]
                    filesformat_type = self.get_input_data('filesformat_type')

                    if 'long' in self.get_input_data('response_type'):
                        language_list = questionnaire_language['language_list']
                    else:
                        language_list = [questionnaire_language['output_language']]

                    for language in language_list:
                        export_filename = '%s_%s_%s' % ('Responses', str(questionnaire_code), language)
                        if participants_plugin:
                            randomforests = RandomForests.objects.first()
                            if questionnaire_id == randomforests.admission_assessment.lime_survey_id:
                                export_filename = 'Responses_QA_en'
                            elif questionnaire_id == randomforests.surgical_evaluation.lime_survey_id:
                                export_filename = 'Responses_QS_en'
                            elif questionnaire_id == \
                                    randomforests.followup_assessment.lime_survey_id:
                                export_filename = 'Responses_QF_en'
                            else:
                                # TODO: error
                                pass
                        # Path ex. data/Per_participant/Participant_P123/QCode_Title/Responses_Q123_aaa.csv
                        complete_filename = path.join(path_per_questionnaire, export_filename + '.' + filesformat_type)

                        participant_rows = self.get_per_participant_data(
                            participant_code, questionnaire_code)[language][0]
                        per_participant_rows = [header, participant_rows]
                        save_to_csv(complete_filename, per_participant_rows, filesformat_type)

                        answer_list = {'fields': [], 'header': [], 'header_questionnaire': []}
                        questionnaire = next(
                            item for item in self.get_input_data('questionnaires') if item['id'] == questionnaire_id)
                        for question in questionnaire['output_list']:
                            answer_list['fields'].append(question['field'])
                            answer_list['header'].append(question['header'])
                            answer_list['header_questionnaire'].append(question['header'])
                        # TODO (NES-991): treat error!
                        # TODO (NES-991): QuestionnaireUtils already in self.questionnaire_utils
                        error, questions = QuestionnaireUtils.get_questions(
                            questionnaire_lime_survey, questionnaire_id, language)
                        datapackage_json = {
                            'name': slugify(export_filename), 'title': export_filename,
                            'path': path.join(export_questionnaire_directory, export_filename + '.' + filesformat_type),
                            'format': filesformat_type, 'mediatype': 'text/' + filesformat_type,
                            'description': 'Questionnaire response',
                            'profile': 'tabular-data-resource',
                            'schema': {
                                'fields': self._set_questionnaire_response_fields(
                                    heading_type, participant_data_header, answer_list, questions)
                            }
                        }

                        self.files_to_zip_list.append([
                            complete_filename, export_questionnaire_directory, datapackage_json
                        ])

        return error_msg

    def process_per_participant_per_entrance_questionnaire(self, heading_type):
        # Path ex. data/Participant_data/
        path_participant_data = path.join(
            self.get_export_directory(),
            self.get_input_data('participant_data_directory'))
        # Path ex. data/Participant_data/Per_participant/
        error_msg, path_per_participant = create_directory(
            path_participant_data,
            self.get_input_data('per_participant_directory'))
        if error_msg != '':
            return error_msg

        prefix_filename_participant = 'Participant_'
        # Path ex. data/Participant_data/Per_participant/
        export_participant_data = path.join(
            self.get_input_data('base_directory'),
            self.get_input_data('participant_data_directory'))
        # Path ex. data/Participant_data/Per_participant/
        export_directory_base = path.join(export_participant_data, self.get_input_data('per_participant_directory'))

        filesformat_type = self.get_input_data('filesformat_type')

        questionnaire_lime_survey = Questionnaires()

        for participant_code in self.get_per_participant_data():
            patient_id = Patient.objects.filter(code=participant_code).values('id')[0]['id']
            path_participant = prefix_filename_participant + str(participant_code)
            # /data/Participant_data/Per_participant/Participant_P123/
            error_msg, participant_path = create_directory(path_per_participant, path_participant)
            if error_msg != '':
                return error_msg

            for questionnaire_code in self.get_per_participant_data(participant_code):
                if self.participants_per_entrance_questionnaire[questionnaire_code]:
                    if patient_id in self.participants_per_entrance_questionnaire[questionnaire_code]:
                        questionnaire_id = int(
                            self.questionnaire_utils.get_questionnaire_id_from_code(questionnaire_code))
                        # select entry questionnaires' participants
                        for questionnaire in self.get_input_data('questionnaires'):
                            if questionnaire_id == questionnaire['id']:
                                title = self.get_title_reduced(questionnaire_id=questionnaire_id)
                                questionnaire_language = \
                                    self.get_input_data('questionnaire_language')[str(questionnaire_id)]
                                if 'long' in self.get_input_data('response_type'):
                                    language_list = questionnaire_language['language_list']
                                else:
                                    language_list = [questionnaire_language['output_language']]
                                # Create questionnaire directory
                                path_questionnaire = '%s_%s' % (str(questionnaire_code), title)
                                # /data/Participant_data/Per_participant/Participant_P123/Q123_title
                                error_msg, questionnaire_path_directory = create_directory(
                                    participant_path, path_questionnaire)
                                if error_msg != '':
                                    return error_msg
                                export_participant_directory = path.join(export_directory_base, path_participant)
                                # data/Participant_data/Per_participant/Participant_P123/Q123_title
                                export_directory = path.join(export_participant_directory, path_questionnaire)

                                for language in language_list:
                                    export_filename = '%s_%s_%s' % (
                                        questionnaire['prefix_filename_responses'], str(questionnaire_code), language)
                                    # Path ex. data/Participant_data/Per_participant/Q123_title
                                    complete_filename = path.join(
                                        questionnaire_path_directory, export_filename + '.' + filesformat_type)

                                    # Add participant personal data header
                                    questionnaire_header = self.questionnaire_utils.get_header_questionnaire(
                                        questionnaire_id)
                                    participant_data_header = self.get_input_data('participants')['data_list'][0]
                                    header = self.build_header_questionnaire_per_participant(
                                            participant_data_header,
                                            questionnaire_header[0:len(questionnaire_header) - 1])

                                    per_participant_rows = \
                                        self.per_participant_data[participant_code][questionnaire_code][language]
                                    per_participant_rows.insert(0, header)
                                    save_to_csv(complete_filename, per_participant_rows, filesformat_type)

                                    # Get data for datapackage resource questionnaire response table schema
                                    rows_participant_data = self.get_input_data('participants')['data_list']
                                    answer_list = {'fields': [], 'header': [], 'header_questionnaire': []}
                                    for question in questionnaire['output_list']:
                                        answer_list['fields'].append(question['field'])
                                        answer_list['header'].append(question['header'])
                                        answer_list['header_questionnaire'].append(question['header'])
                                    # TODO (NES-991): treat error!
                                    # TODO (NES-991): QuestionnaireUtils already in self.questionnaire_utils
                                    error, questions = QuestionnaireUtils.get_questions(
                                        questionnaire_lime_survey, questionnaire_id, language)

                                    self.files_to_zip_list.append([
                                        complete_filename, export_directory,
                                        {
                                            'name': slugify(export_filename), 'title': export_filename,
                                            'path': path.join(
                                                export_directory, export_filename + '.' + filesformat_type),
                                            'format': filesformat_type, 'mediatype': 'text/' + filesformat_type,
                                            'description': 'Questionnaire response',
                                            'profile': 'tabular-data-resource',
                                            'schema': {
                                                'fields': self._set_questionnaire_response_fields(
                                                    heading_type, rows_participant_data[0], answer_list, questions
                                                )
                                            }
                                        }
                                    ])

        return error_msg

    def process_per_participant_per_experiment(self, heading_type, per_experiment_plugin=False):
        error_msg = ''
        questionnaire_lime_survey = Questionnaires()

        for group_id in self.per_group_data:
            header_saved = False
            participant_list = self.per_group_data[group_id]['data_per_participant']
            # Participant data
            for participant_code in participant_list:
                prefix_filename_participant = 'Participant_'
                # Ex. Participant_P123
                participant_name = prefix_filename_participant + str(participant_code)
                participant_data_directory = self.per_group_data[group_id]['group']['participant_data_directory']
                # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                path_per_participant = path.join(participant_data_directory, participant_name)

                # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                participant_data_export_directory = self.per_group_data[group_id]['group'][
                    'participant_data_export_directory']
                participant_export_directory = path.join(participant_data_export_directory, participant_name)
                if 'token_list' in participant_list[participant_code] and self.get_input_data('export_per_participant'):
                    # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != '':
                            return error_msg

                    for token_data in participant_list[participant_code]['token_list']:
                        questionnaire_code = token_data['questionnaire_code']
                        questionnaire_id = token_data['questionnaire_id']
                        questionnaire_title = self.get_input_data(
                            'questionnaires_from_experiments')[group_id][str(questionnaire_id)]['questionnaire_name']
                        # ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_Questionnaire
                        error_msg, directory_step_participant = create_directory(
                            path_per_participant, token_data['directory_step_name'])
                        if error_msg != '':
                            return error_msg

                        # Ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_Questionnaire
                        step_participant_export_directory = path.join(
                            participant_export_directory, token_data['directory_step_name'])
                        # Select questionnaire language
                        questionnaire_language = self.get_input_data('questionnaire_language')[str(questionnaire_id)]

                        filesformat_type = self.get_input_data('filesformat_type')

                        if 'long' in self.get_input_data('response_type'):
                            language_list = questionnaire_language['language_list']
                        else:
                            language_list = [questionnaire_language['output_language']]
                        response_english_plugin_done = False
                        for language in language_list:
                            if response_english_plugin_done:
                                break
                            export_filename = '%s_%s_%s' % (str(
                                questionnaire_code), slugify(questionnaire_title), language)
                            if per_experiment_plugin:
                                randomforests = RandomForests.objects.first()
                                if questionnaire_id == randomforests.admission_assessment.lime_survey_id:
                                    export_filename = 'QA_unified_admission_assessment_en'
                                elif questionnaire_id == randomforests.surgical_evaluation.lime_survey_id:
                                    export_filename = 'QS_surgical_evaluation_en'
                                elif questionnaire_id == \
                                        randomforests.followup_assessment.lime_survey_id:
                                    export_filename = \
                                        'QF_unified_followup_assessment_en'
                                else:
                                    # TODO: error
                                    pass
                                response_english_plugin_done = True

                            # Path ex. data/Experiment_data/Group_xxx/Per_participant/Participant_P123/Step_X_aaa
                            complete_filename = path.join(
                                directory_step_participant, export_filename + '.' + filesformat_type)

                            export_rows_participants = self.get_participant_row_data(token_data['subject_code'])

                            # Questionnaire response by participant
                            token_id = token_data['token_id']
                            answer_list = self.questionnaires_responses[str(questionnaire_id)][token_id][language]

                            per_participant_rows = self.merge_questionnaire_answer_list_per_participant(
                                export_rows_participants[1], answer_list[1: len(answer_list)])

                            field_type = 'fields' if heading_type == 'code' else 'header_questionnaire'
                            header = self.build_header_questionnaire_per_participant(
                                export_rows_participants[0], answer_list[0][field_type])
                            per_participant_rows.insert(0, header)

                            save_to_csv(complete_filename, per_participant_rows, filesformat_type)

                            # TODO (NES-991): treat error!
                            # TODO (NES-991): QuestionnaireUtils already in self.questionnaire_utils
                            error, questions = QuestionnaireUtils.get_questions(
                                questionnaire_lime_survey, questionnaire_id, language)

                            self.files_to_zip_list.append([
                                complete_filename, step_participant_export_directory,
                                {
                                    'name': slugify(export_filename) + '_per-participant', 'title': export_filename,
                                    'path': path.join(
                                        step_participant_export_directory, export_filename + '.' + filesformat_type),
                                    'format': 'csv', 'mediatype': 'text/csv', 'description': 'Questionnaire response',
                                    'profile': 'tabular-data-resource',
                                    'schema': {
                                        'fields': self._set_questionnaire_response_fields(
                                            heading_type, export_rows_participants[0], answer_list[0], questions
                                        )
                                    }
                                }
                            ])

                # For component_list
                if 'eeg_data_list' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != '':
                            return error_msg

                    eeg_data_list = \
                        self.per_group_data[group_id]['data_per_participant'][participant_code]['eeg_data_list']
                    for eeg_data in eeg_data_list:
                        if eeg_data['eeg_file_list']:
                            directory_step_name = eeg_data['directory_step_name']
                            path_per_eeg_participant = path.join(path_per_participant, directory_step_name)
                            if not path.exists(path_per_eeg_participant):
                                # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_a
                                error_msg, path_per_eeg_participant = create_directory(
                                    path_per_participant, directory_step_name)
                                if error_msg != '':
                                    return error_msg

                            # data/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_a
                            export_eeg_step_directory = path.join(participant_export_directory, directory_step_name)

                            # To create EEGData directory
                            directory_data_name = eeg_data['eeg_data_directory_name']
                            path_per_eeg_data = path.join(path_per_eeg_participant, directory_data_name)
                            if not path.exists(path_per_eeg_data):
                                # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_aaa/EEGDATA_#
                                error_msg, path_per_eeg_data = create_directory(
                                    path_per_eeg_participant, directory_data_name)
                                if error_msg != '':
                                    return error_msg

                            # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_a
                            # /EEGData_#
                            export_eeg_data_directory = path.join(export_eeg_step_directory, directory_data_name)

                            eeg_setting_description = get_eeg_setting_description(eeg_data['setting_id'])

                            if eeg_setting_description:
                                filename, extension = EEG_SETTING_FILENAME.split('.')
                                # Path ex. data/Experiment_data/Group_xxxx/eeg_setting_description.json
                                complete_setting_filename = path.join(path_per_eeg_data, EEG_SETTING_FILENAME)
                                self.files_to_zip_list.append([
                                    complete_setting_filename, export_eeg_data_directory,
                                    {
                                        'name': filename, 'title': filename,
                                        'path': path.join(export_eeg_data_directory, EEG_SETTING_FILENAME),
                                        # TODO (NES-987): implement get_mediatype(extension) method and apply in the
                                        #  other places
                                        'format': extension, 'mediatype': 'application/%s' % extension
                                    }
                                ])

                                with open(complete_setting_filename.encode('utf-8'), 'w', newline='',
                                          encoding='UTF-8') as outfile:
                                    json.dump(eeg_setting_description, outfile, indent=4)

                            # If sensor position image exist
                            sensors_positions_image = eeg_data['sensor_filename']
                            if sensors_positions_image:
                                sensor_position_filename = 'sensor_position.png'
                                complete_sensor_position_filename = path.join(
                                    path_per_eeg_data, sensor_position_filename)

                                with open(sensors_positions_image, 'rb') as f:
                                    data = f.read()
                                with open(complete_sensor_position_filename, 'wb') as f:
                                    f.write(data)

                                self.files_to_zip_list.append([
                                    complete_sensor_position_filename, export_eeg_data_directory,
                                    {
                                        'name': slugify(sensor_position_filename), 'title': 'sensor_position',
                                        'path': path.join(export_eeg_data_directory, sensor_position_filename),
                                        'description': 'Data Collection (format: png)'
                                    }
                                ])

                            for eeg_file in eeg_data['eeg_file_list']:
                                path_eeg_data_file = str(eeg_file.file.file)
                                eeg_data_filename = path.basename(path_eeg_data_file)
                                complete_eeg_data_filename = path.join(path_per_eeg_data, eeg_data_filename)

                                # For datapackage resources
                                unique_name = slugify(eeg_data_filename)
                                file_format_nes_code = eeg_file.eeg_data.file_format.nes_code
                                datapackage_resource = {
                                    'name': unique_name, 'title': unique_name,
                                    'path': path.join(export_eeg_data_directory, eeg_data_filename),
                                    'description': 'Data Collection (format: %s)' % file_format_nes_code
                                }

                                with open(path_eeg_data_file, 'rb') as f:
                                    data = f.read()
                                with open(complete_eeg_data_filename, 'wb') as f:
                                    f.write(data)

                                self.files_to_zip_list.append([
                                    complete_eeg_data_filename, export_eeg_data_directory, datapackage_resource
                                ])

                                # v1.5
                                # can export to nwb?
                                if eeg_file.can_export_to_nwb:
                                    process_requisition = int(random.random() * 10000)
                                    eeg_file_name = eeg_data_filename.split('.')[0]
                                    nwb_file_name = eeg_file_name + '.nwb'
                                    complete_nwb_file_name = path.join(path_per_eeg_data, nwb_file_name)
                                    req = None

                                    # Was it open properly?
                                    ok_opening = False

                                    if eeg_file.eeg_reading.file_format:
                                        if eeg_file.eeg_reading.file_format.nes_code == 'MNE-RawFromEGI':
                                            ok_opening = True

                                    if ok_opening:
                                        complete_nwb_file_name = create_nwb_file(
                                            eeg_file.eeg_data, eeg_file.eeg_reading, process_requisition,
                                            req, complete_nwb_file_name)
                                        if complete_nwb_file_name:
                                            self.files_to_zip_list.append([
                                                complete_nwb_file_name, export_eeg_data_directory,
                                                {
                                                    'name': slugify(nwb_file_name), 'title': eeg_file_name,
                                                    'path': path.join(export_eeg_data_directory, nwb_file_name),
                                                    'description': 'Data Collection (format: nwb)'
                                                }
                                            ])
                                        else:
                                            return error_msg

                if 'emg_data_list' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != '':
                            return error_msg

                    emg_data_list = \
                        self.per_group_data[group_id]['data_per_participant'][participant_code]['emg_data_list']
                    for emg_data in emg_data_list:
                        if emg_data['emg_file_list']:
                            directory_step_name = emg_data['directory_step_name']
                            path_per_emg_participant = path.join(path_per_participant, directory_step_name)
                            if not path.exists(path_per_emg_participant):
                                # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_aaa
                                error_msg, path_per_emg_participant = create_directory(
                                    path_per_participant, directory_step_name)
                                if error_msg != '':
                                    return error_msg

                            # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                            export_emg_step_directory = path.join(participant_export_directory, directory_step_name)

                            # To create EMGData directory
                            directory_data_name = emg_data['emg_data_directory_name']
                            path_per_emg_data = path.join(path_per_emg_participant, directory_data_name)
                            if not path.exists(path_per_emg_data):
                                # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_aaa/EMGDATA_#
                                error_msg, path_per_emg_data = create_directory(
                                    path_per_emg_participant, directory_data_name)
                                if error_msg != '':
                                    return error_msg

                            # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                            # /EMGData_#
                            export_emg_data_directory = path.join(export_emg_step_directory, directory_data_name)

                            url_segment1 = path_per_emg_data.rpartition('export')
                            url1 = url_segment1[0]

                            url_partial = emg_data['emg_file_list'][0].file.name
                            url_segment2 = url_partial.rpartition('media/')
                            url2 = url_segment2[2]

                            url = url1 + url2

                            for emg_file in emg_data['emg_file_list']:
                                path_emg_data_file = emg_file.file.name
                                emg_data_filename = path.basename(path_emg_data_file)
                                complete_emg_data_filename = path.join(path_per_emg_data, emg_data_filename)

                                # For datapackage resources
                                unique_name = slugify(emg_data_filename)
                                file_format_nes_code = emg_file.emg_data.file_format.nes_code
                                datapackage_resource = {
                                    'name': unique_name, 'title': unique_name,
                                    'path': path.join(export_emg_data_directory, emg_data_filename),
                                    'description': 'Data Collection (format: %s)' % file_format_nes_code
                                }

                                with open(url, 'rb') as f:
                                    data = f.read()
                                with open(complete_emg_data_filename, 'wb') as f:
                                    f.write(data)

                                self.files_to_zip_list.append([
                                    complete_emg_data_filename, export_emg_data_directory, datapackage_resource
                                ])

                            # Create documento json with emg settings
                            emg_setting_description = get_emg_setting_description(emg_data['setting_id'])

                            if emg_setting_description:
                                filename, extension = EMG_SETTING_FILENAME.split('.')
                                # Path ex. data/Experiment_data/Group_xxxx/emg_setting_description.txt 
                                complete_setting_filename = path.join(path_per_emg_data, EMG_SETTING_FILENAME)
                                self.files_to_zip_list.append([
                                    complete_setting_filename, export_emg_data_directory,
                                    {
                                        'name': filename, 'title': filename,
                                        'path': path.join(export_emg_data_directory, EMG_SETTING_FILENAME),
                                        # TODO (NES-987): implement get_mediatype(extension) method
                                        'format': extension, 'mediatype': 'application/%s' % extension
                                    }
                                ])

                                with open(complete_setting_filename.encode('utf-8'), 'w', newline='',
                                          encoding='UTF-8') as outfile:
                                    json.dump(emg_setting_description, outfile, indent=4)

                if 'tms_data_list' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != '':
                            return error_msg

                    tms_data_list = self.per_group_data[group_id]['data_per_participant'][participant_code][
                        'tms_data_list']
                    for tms_data in tms_data_list:
                        tms_data_description = get_tms_data_description(tms_data['tms_data_id'])
                        if tms_data_description:
                            directory_step_name = tms_data['directory_step_name']
                            path_per_tms_participant = path.join(path_per_participant, directory_step_name)
                            if not path.exists(path_per_tms_participant):
                                # path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_aaa
                                error_msg, path_per_tms_participant = create_directory(
                                    path_per_participant, directory_step_name)
                                if error_msg != '':
                                    return error_msg

                            # path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123/Step_X_aaa
                            export_tms_step_directory = path.join(participant_export_directory, directory_step_name)

                            filename, extension = TMS_DATA_FILENAME.split('.')
                            # Path ex. data/Experiment_data/Group_xxxx/tms_data_description.txt
                            complete_data_filename = path.join(path_per_tms_participant, TMS_DATA_FILENAME)
                            self.files_to_zip_list.append([
                                complete_data_filename, export_tms_step_directory,
                                {
                                    'name': filename, 'title': filename,
                                    'path': path.join(export_tms_step_directory, TMS_DATA_FILENAME),
                                    # TODO (NES-987): implement get_mediatype(extension) method
                                    'format': extension, 'mediatype': 'application/%s' % extension
                                }
                            ])

                            with open(complete_data_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as \
                                    outfile:
                                json.dump(tms_data_description, outfile, indent=4)

                            # TMS hotspot position image file
                            tms_data = get_object_or_404(TMSData, pk=tms_data['tms_data_id'])

                            if hasattr(tms_data, 'hotspot'):
                                hotspot_image = tms_data.hotspot.hot_spot_map.name
                                if hotspot_image:
                                    filename, extension = HOTSPOT_MAP.split('.')
                                    complete_hotspot_filename = path.join(path_per_tms_participant, HOTSPOT_MAP)
                                    path_hot_spot_image = path.join(
                                        settings.MEDIA_ROOT,
                                        hotspot_image)
                                    with open(path_hot_spot_image, 'rb') as f:
                                        data = f.read()
                                    with open(complete_hotspot_filename, 'wb') as f:
                                        f.write(data)

                                    self.files_to_zip_list.append([
                                        complete_hotspot_filename, export_tms_step_directory,
                                        {
                                            'name': filename, 'title': filename,
                                            'path': path.join(export_tms_step_directory, HOTSPOT_MAP),
                                            # TODO (NES-987): implement get_mediatype(extension) method
                                            'format': extension, 'mediatype': 'image/%s' % extension
                                        }
                                    ])

                if 'digital_game_data_list' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != '':
                            return error_msg

                    goalkeeper_game_directory = self.per_group_data[group_id]['group']['goalkeeper_game_data_directory']
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(goalkeeper_game_directory, '')
                        if error_msg != '':
                            return error_msg

                    goalkeeper_game_data_list = self.per_group_data[
                        group_id
                    ]['data_per_participant'][participant_code]['digital_game_data_list']

                    for goalkeeper_game_data in goalkeeper_game_data_list:
                        if goalkeeper_game_data['digital_game_file_list']:
                            directory_step_name = goalkeeper_game_data['directory_step_name']
                            path_goalkeeper_game_data = path.join(path_per_participant, directory_step_name)
                            if not path.exists(path_goalkeeper_game_data):
                                # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_COMPONENT_TYPE
                                error_msg, path_goalkeeper_game_data = create_directory(path_per_participant,
                                                                                        directory_step_name)
                                if error_msg != '':
                                    return error_msg

                                # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_COMPONENT_TYPE
                                export_goalkeeper_game_directory = path.join(participant_export_directory,
                                                                             directory_step_name)

                                # To create Game_digital_dataData directory 
                                directory_data_name = goalkeeper_game_data['digital_game_data_directory']

                                path_per_goalkeeper_game_data = path.join(
                                    path_goalkeeper_game_data, directory_data_name)
                                if not path.exists(path_per_goalkeeper_game_data):
                                    # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123 
                                    #  /Step_X_aaa/GoalkeeperDATA_
                                    error_msg, path_per_goalkeeper_game_data = create_directory(
                                        path_goalkeeper_game_data, directory_data_name)
                                    if error_msg != '':
                                        return error_msg

                                # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                                # /Step_X_aaa/GoalkeeperDATA_
                                export_goalkeeper_data_directory = path.join(
                                    export_goalkeeper_game_directory, directory_data_name)

                                for context_tree_file in goalkeeper_game_data['digital_game_file_list']:
                                    digital_game_file = context_tree_file['digital_game_file']
                                    path_context_tree_file = path.join(settings.MEDIA_ROOT, digital_game_file.file.name)
                                    filename = path.basename(path_context_tree_file)
                                    unique_name1 = slugify(filename)

                                    # General csv file
                                    file_name_digital = filename.split('_')[0]
                                    unique_name2 = slugify(file_name_digital)

                                    # Path ex. data/Experiment_data/Group_XXX/Per_participant
                                    #  /Participant_123/Step_X_COMPONENT_TYPE/file_name.format_type
                                    complete_goalkeeper_game_filename = path.join(
                                        path_per_goalkeeper_game_data, filename)

                                    with open(path_context_tree_file, 'rb') as f:
                                        data = f.read()
                                    with open(complete_goalkeeper_game_filename, 'wb') as f:
                                        f.write(data)

                                    self.files_to_zip_list.append([
                                        complete_goalkeeper_game_filename, export_goalkeeper_data_directory,
                                        {
                                            'name': unique_name1, 'title': unique_name1,
                                            'path': path.join(export_goalkeeper_data_directory, filename),
                                            'description': 'Data Collection (format: %s)'
                                                           % digital_game_file.digital_game_phase_data.file_format.nes_code
                                        }
                                    ])

                                    file_extension = 'tsv' if 'tsv' in self.get_input_data(
                                        'filesformat_type') else 'csv'
                                    export_filename = file_name_digital + '.' + file_extension

                                    complete_digital_filename = path.join(goalkeeper_game_directory, export_filename)

                                    with open(complete_goalkeeper_game_filename, 'r') as infile, \
                                            open(complete_digital_filename, 'a') as outfile:
                                        header = next(infile)

                                        if not header_saved:
                                            outfile.write(header)
                                            header_saved = True

                                        for line in infile:
                                            outfile.write(line)

                    goalkeeper_game_data_export_directory = self.per_group_data[
                        group_id
                    ]['group']['goalkeeper_game_data_export_directory']
                    self.files_to_zip_list.append([
                        complete_digital_filename, goalkeeper_game_data_export_directory,
                        {
                            'name': unique_name2, 'title': unique_name2,
                            'path': path.join(
                                goalkeeper_game_data_export_directory, export_filename),
                            'encoding': 'UTF-8',
                        }
                    ])

                if 'generic_data_collection_data_list' \
                        in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != '':
                            return error_msg
                    generic_data_collection_data_list = self.per_group_data[
                        group_id
                    ]['data_per_participant'][participant_code]['generic_data_collection_data_list']
                    for generic_data_collection_data in generic_data_collection_data_list:
                        directory_step_name = generic_data_collection_data['directory_step_name']
                        path_generic_data_collection_data = path.join(path_per_participant, directory_step_name)
                        if not path.exists(path_generic_data_collection_data):
                            error_msg, path_generic_data_collection_data = create_directory(
                                path_per_participant, directory_step_name)
                            if error_msg:
                                return error_msg
                        export_generic_data_directory = path.join(participant_export_directory, directory_step_name)
                        directory_data_name = generic_data_collection_data['generic_data_collection_directory']
                        path_per_generic_data = path.join(path_generic_data_collection_data, directory_data_name)
                        if not path.exists(path_per_generic_data):
                            error_msg, path_per_generic_data = create_directory(
                                path_generic_data_collection_data, directory_data_name)
                            if error_msg:
                                return error_msg
                        export_generic_data_directory = path.join(export_generic_data_directory, directory_data_name)
                        for generic_data_file in generic_data_collection_data['generic_data_collection_file_list']:
                            path_generic_data_collection_file = path.join(
                                settings.MEDIA_ROOT, generic_data_file.file.name)
                            filename = path.basename(path_generic_data_collection_file)
                            complete_generic_data_filename = path.join(path_per_generic_data, filename)

                            # For datapackage resources
                            unique_name = slugify(filename)
                            file_format_nes_code = generic_data_file.generic_data_collection_data.file_format.nes_code
                            information_type = generic_data_file.generic_data_collection_data.data_configuration_tree.\
                                component_configuration.component.genericdatacollection.information_type.name
                            datapackage_resource = {
                                'name': unique_name, 'title': unique_name,
                                'path': path.join(export_generic_data_directory, filename),
                                'description': 'Data Collection (format: %s), information type: %s'
                                               % (file_format_nes_code, information_type)
                            }

                            with open(path_generic_data_collection_file, 'rb') as f:
                                data = f.read()
                            with open(complete_generic_data_filename, 'wb') as f:
                                f.write(data)
                            self.files_to_zip_list.append([
                                complete_generic_data_filename, export_generic_data_directory, datapackage_resource
                            ])

                if 'additional_data_list' in self.per_group_data[group_id]['data_per_participant'][participant_code]:
                    # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                    if not path.exists(path_per_participant):
                        error_msg, path_per_participant = create_directory(participant_data_directory, participant_name)
                        if error_msg != '':
                            return error_msg

                    additional_data_list = self.per_group_data[
                        group_id
                    ]['data_per_participant'][participant_code]['additional_data_list']

                    for additional_data in additional_data_list:
                        directory_step_name = additional_data['directory_step_name']
                        path_additional_data = path.join(path_per_participant, directory_step_name)
                        if not path.exists(path_additional_data):
                            # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123
                            # /Step_X_COMPONENT_TYPE
                            error_msg, path_additional_data = create_directory(
                                path_per_participant, directory_step_name)

                            if error_msg != '':
                                return error_msg

                        # Path ex. data/Experiment_data/Group_XX/Per_participant/Participant_123/Step_X_COMP._TYPE
                        export_step_additional_data_directory = path.join(
                            participant_export_directory, directory_step_name)

                        # To create AdditionalData directory
                        directory_data_name = additional_data['additional_data_directory']
                        path_per_additional_data = path.join(path_additional_data, directory_data_name)
                        if not path.exists(path_per_additional_data):
                            error_msg, path_per_additional_data = create_directory(
                                path_additional_data, directory_data_name)
                            if error_msg != '':
                                return error_msg

                        export_additional_data_directory = path.join(export_step_additional_data_directory,
                                                                     directory_data_name)

                        for additional_file in additional_data['additional_data_file_list']:
                            additional_file_object =  additional_file['additional_data_filename']
                            path_additional_data_file = path.join(settings.MEDIA_ROOT, additional_file_object.file.name)
                            filename = path.basename(path_additional_data_file)
                            unique_name = slugify(filename)
                            file_format_nes_code = additional_file_object.additional_data.file_format.nes_code

                            # Path ex. data/Experiment_data/Group_XXX/Per_participant/Participant_123/
                            # Step_X_COMPONENT_TYPE/file_name.format_type
                            complete_additional_data_filename = path.join(path_per_additional_data, filename)
                            with open(path_additional_data_file, 'rb') as f:
                                data = f.read()
                            with open(complete_additional_data_filename, 'wb') as f:
                                f.write(data)

                            self.files_to_zip_list.append([
                                complete_additional_data_filename, export_additional_data_directory,
                                {
                                    'name': unique_name, 'title': unique_name,
                                    'path': path.join(export_additional_data_directory, filename),
                                    'description': 'Data Collection (additional file, format: %s)'
                                                   % file_format_nes_code
                                }
                            ])

        return error_msg

    @staticmethod
    def handle_exported_field(field):
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
            if element['field']:
                headers.append(element['header'])
                fields.append(element['field'])

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

    @staticmethod
    def calculate_age_by_participant(participants_list):
        age_value_dict = {}
        for participant in participants_list:
            # (a, b, c,) -> patient is subject of a group: a: patient; b, c,
            #  are subjects of group
            # (a,) -> patient comes from exporting Per participant
            length_tupple = len(participant)
            if length_tupple > 1:
                # put first data collection 1 day ahead for first iteration
                first_data_collection = date.today() + timedelta(days=1)
                for i in range(1, length_tupple):
                    date_data_collection = \
                        date_of_first_data_collection(participant[i])
                    # subject of group has no data collection
                    if date_data_collection:
                        first_data_collection = min(
                            first_data_collection,
                            date_of_first_data_collection(participant[i])
                        )
                # if first_data_collection = date.today() + timedelta(days=1),
                # there're no data collections for all subjects of groups
                if first_data_collection > date.today():
                    first_data_collection = None
            else:
                first_data_collection = None
            subject = get_object_or_404(Patient, pk=participant[0])
            date_ = \
                first_data_collection if first_data_collection else date.today()
            age_value = format(
                (date_ - subject.date_birth) / timedelta(days=365.2425),
                '.4'
            )
            if subject.code not in age_value_dict:
                age_value_dict[subject.code] = age_value

        return age_value_dict

    @staticmethod
    def add_subject_of_group(participants, group_ids):
        for group_id in group_ids:
            group = Group.objects.get(id=group_id)
            # Patient.objects.filter(subject__subjectofgroup__group=group).values('id')
            subjects_of_group = group.subjectofgroup_set.all()
            for sog in subjects_of_group:
                patient_sog = sog.subject.patient
                for i in range(len(participants)):
                    if participants[i][0] == patient_sog.id:
                        participants[i] = participants[i] + (sog.id,)

        return participants

    def process_participant_data(self, participants_output_fields, participants, language, participants_plugin=False):
        # TODO: fix translation model functionality
        age_value_dict = {}
        headers, fields = self.get_headers_and_fields(participants_output_fields)
        model_to_export = getattr(modules['patient.models'], 'Patient')
        if 'age' in fields:
            age_value_dict = self.calculate_age_by_participant(participants)
            fields.remove('age')

        if language != 'pt-br' or participants_plugin:  # Read english fields
            fields = self.get_field_en(fields)

        # Pick up the first terms of participants: required because
        # participants list of tupples can have subject of groups elements
        # corresponding to participants when we have to consider in case of
        # calculating based in data collections
        participants = [item[0] for item in list(participants)]
        db_data = model_to_export.objects.filter(id__in=participants).values_list(*fields).extra(order_by=['id'])

        export_rows_participants = [headers]

        # Transform data
        for record in db_data:
            participant_rows = []
            for value in record:
                participant_rows.append(value)
            if age_value_dict:
                participant_rows.insert(1, age_value_dict[record[0]])
            export_rows_participants.append(participant_rows)

        return export_rows_participants

    def process_diagnosis_data(self, participants_output_fields, participants_list, heading_type):
        headers, fields = self.get_headers_and_fields(participants_output_fields)
        model_to_export = getattr(modules['patient.models'], 'Patient')
        db_data = model_to_export.objects.filter(id__in=participants_list).values_list(*fields).extra(
            order_by=['id'])

        export_rows_participants = [headers]

        # Transform data
        for record in db_data:
            export_rows_participants.append([self.handle_exported_field(field) for field in record])

        if heading_type == 'abbreviated':
            self.update_duplicates(export_rows_participants[0])

        return export_rows_participants

    def get_participant_data_per_code(self, subject_code, questionnaire_response_fields):
        db_data = []
        for record in self.get_input_data('participants')['data_list']:
            if record[-1] == subject_code:
                db_data = record

        # append participant data to questionnaire response
        for field in db_data:
            questionnaire_response_fields.append(field)

        return questionnaire_response_fields

    def build_participant_export_data(self, per_experiment, heading_type):
        error_msg = ''
        participants_filtered_list = self.get_participants_filtered_data()
        # Process participants/diagnosis (Per_participant directory)
        # Path ex. Users/.../data/
        base_export_directory = self.get_export_directory()
        # /data/
        base_directory = self.get_input_data('base_directory')
        # Participant_data directory
        participant_data_directory = self.get_input_data('participant_data_directory')
        if per_experiment:
            # Path ex. Users/.../data/Participant_data/
            participant_base_export_directory = path.join(base_export_directory, participant_data_directory)
            # /data/Participant_data
            base_directory = path.join(base_directory, participant_data_directory)
            if not path.exists(participant_base_export_directory):
                error_msg, base_export_directory = create_directory(base_export_directory, participant_data_directory)
                if error_msg != '':
                    return error_msg

        if 'tsv' in self.get_input_data('filesformat_type'):
            # TODO (NES-987): change this like in other places
            file_extension = 'tsv'
            separator = '\t'
        else:
            file_extension = 'csv'
            separator = ','

        export_filename = '%s.%s' % (self.get_input_data('participants')['output_filename'], file_extension)

        complete_filename = path.join(base_export_directory, export_filename)

        export_rows_participants = self.get_input_data('participants')['data_list']
        participants_headers, participants_field_types = self._set_participants_fields()

        self.files_to_zip_list.append([
            complete_filename, base_directory,
            {
                # For datapackages.json resources
                'name': 'participants', 'title': 'Participants',
                'path': path.join(base_directory, export_filename),
                'format': file_extension, 'mediatype': 'text/%s' % file_extension, 'encoding': 'UTF-8',
                'profile': 'tabular-data-resource',
                'schema': {
                    'fields': self._set_datapackage_table_schema(participants_headers, participants_field_types)
                }
            }
        ])

        with open(complete_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as csv_file:
            export_writer = csv.writer(csv_file, quotechar='"', delimiter=separator, quoting=csv.QUOTE_NONNUMERIC)
            for row in export_rows_participants:
                export_writer.writerow(row)

        # Process diagnosis file
        diagnosis_input_data = self.get_input_data('diagnosis')

        if diagnosis_input_data['output_list'] and participants_filtered_list:
            export_rows_diagnosis = self.process_diagnosis_data(
                diagnosis_input_data['output_list'], participants_filtered_list, heading_type)

            # TODO (NES-987): refactor this as in other places
            file_extension = 'tsv' if 'tsv' in self.get_input_data('filesformat_type') else 'csv'
            export_filename = ('%s.' + file_extension) % self.get_input_data('diagnosis')['output_filename']
            complete_filename = path.join(base_export_directory, export_filename)

            diagnosis_field_types = self._set_diagnosis_fields()

            self.files_to_zip_list.append([
                complete_filename, base_directory,
                {
                    'name': 'diagnosis', 'title': 'Diagnosis',
                    'path': path.join(base_directory, export_filename),
                    'format': file_extension, 'mediatype': 'text/%s' % file_extension, 'encoding': 'UTF-8',
                    'profile': 'tabular-data-resource',
                    'schema': {
                        'fields': self._set_datapackage_table_schema(export_rows_diagnosis[0], diagnosis_field_types)
                    }
                }
            ])

            with open(complete_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as csv_file:
                export_writer = writer(csv_file, quotechar='"', delimiter=separator, quoting=csv.QUOTE_NONNUMERIC)
                for row in export_rows_diagnosis:
                    export_writer.writerow(row)

        return error_msg

    @staticmethod
    def _get_type(model_field):
        if model_field is CharField or model_field is TextField:
            return 'string'
        elif model_field is DateField:
            return 'date'
        elif model_field is FloatField:
            # TODO (NES-987): change for 'number' cf. https://tools.ietf.org/html/draft-zyp-json-schema-03#section-5.1
            return 'number'
        elif model_field is BooleanField or model_field is NullBooleanField:
            return 'boolean'

    def _set_datapackage_table_schema(self, headers, model_fields):
        fields = []
        for header, field in zip(headers, model_fields):
            field_info = {
                'name': header, 'title': header, 'format': 'default', 'type': self._get_type(field)
            }
            fields.append(field_info)

        return fields

    def _set_participants_fields(self):
        field_types = {
            'code': Patient._meta.get_field('code').__class__,
            'age': FloatField,
            'gender__name': Gender._meta.get_field('name').__class__,
            'date_birth': Patient._meta.get_field('date_birth').__class__,
            'marital_status__name': MaritalStatus._meta.get_field('name').__class__,
            'origin': Patient._meta.get_field('origin').__class__,
            'city': Patient._meta.get_field('city').__class__,
            'state': Patient._meta.get_field('state').__class__,
            'country': Patient._meta.get_field('country').__class__,
            'socialdemographicdata__natural_of': SocialDemographicData._meta.get_field('natural_of').__class__,
            'socialdemographicdata__schooling__name': Schooling._meta.get_field('name').__class__,
            'socialdemographicdata__patient_schooling__name': Schooling._meta.get_field('name').__class__,
            'socialdemographicdata__profession': SocialDemographicData._meta.get_field('profession').__class__,
            'socialdemographicdata__social_class': SocialDemographicData._meta.get_field('social_class').__class__,
            'socialdemographicdata__occupation': SocialDemographicData._meta.get_field('occupation').__class__,
            'socialdemographicdata__benefit_government': SocialDemographicData._meta.get_field(
                'benefit_government').__class__,
            'socialdemographicdata__religion__name': Religion._meta.get_field('name').__class__,
            'socialdemographicdata__flesh_tone__name': FleshTone._meta.get_field('name').__class__,
            'socialdemographicdata__citizenship': SocialDemographicData._meta.get_field('citizenship').__class__,
            'socialdemographicdata__payment__name': Payment._meta.get_field('name').__class__,
            'socialhistorydata__smoker': SocialHistoryData._meta.get_field('smoker').__class__,
            'socialhistorydata__amount_cigarettes__name': AmountCigarettes._meta.get_field('name').__class__,
            'socialhistorydata__ex_smoker': SocialHistoryData._meta.get_field('ex_smoker').__class__,
            'socialhistorydata__alcoholic': SocialHistoryData._meta.get_field('alcoholic').__class__,
            'socialhistorydata__alcohol_frequency__name': AlcoholFrequency._meta.get_field('name').__class__,
            'socialhistorydata__alcohol_period__name': AlcoholPeriod._meta.get_field('name').__class__,
            'socialhistorydata__drugs': SocialHistoryData._meta.get_field('drugs').__class__
        }
        participants_headers = []
        participants_field_types = []
        for field in self.get_input_data('participants')['output_list']:
            participants_headers.append(field['header'])
            participants_field_types.append(field_types[field['field']])

        return participants_headers, participants_field_types

    def _set_diagnosis_fields(self):
        field_types = {
            'code': Patient._meta.get_field('code').__class__,
            'medicalrecorddata__diagnosis__date': Diagnosis._meta.get_field('date').__class__,
            'medicalrecorddata__diagnosis__description': Diagnosis._meta.get_field('description').__class__,
            'medicalrecorddata__diagnosis__classification_of_diseases__code':
                ClassificationOfDiseases._meta.get_field('code').__class__,
            'medicalrecorddata__diagnosis__classification_of_diseases__description':
                ClassificationOfDiseases._meta.get_field('description').__class__,
            'medicalrecorddata__diagnosis__classification_of_diseases__abbreviated_description':
                ClassificationOfDiseases._meta.get_field('abbreviated_description').__class__
        }
        diagnosis_field_types = []
        for field in self.get_input_data('diagnosis')['output_list']:
            diagnosis_field_types.append(field_types[field['field']])

        return diagnosis_field_types

    @staticmethod
    def _set_questionnaire_metadata_fields():
        fields = []
        for field in HEADER_EXPLANATION_FIELDS:
            fields.append({'name': field[0], 'title': field[0], 'type': field[1], 'format': 'default'})
        return fields

    @staticmethod
    def _set_questionnaire_response_fields(heading_type, participant_fields, question_fields, questions):
        # TODO (NES-991): put here because of circular import with export.views.
        #  See if it's a better way.
        from export.views import PATIENT_FIELDS, abbreviated_data
        fields = []
        # Field participant_code is different: by now NES writes 'participant_code'
        # for all heading types
        field_info = next(item for item in PATIENT_FIELDS if item['header'] == 'participant_code')
        fields.append({
            'name': field_info['header'], 'title': field_info['header'], 'type': field_info['json_data_type'],
            'format': 'default'
        })

        # Needs copy because of participant_fields is referred more than
        # once if we have more than one group
        participant_fields_copy = participant_fields.copy()
        participant_fields_copy.remove('participant_code')

        key = 'header' if heading_type == 'code' else 'description'
        for participant_field in participant_fields_copy:
            field_info = next(
                item for item in PATIENT_FIELDS
                if abbreviated_data(item[key], heading_type) == participant_field)
            fields.append({
                # str(field_info[key]) needed because of PATIENT_FIELDS 'description' keys are localized
                'name': abbreviated_data(str(field_info[key]), heading_type),
                'title': abbreviated_data(str(field_info[key]), heading_type), 'type': field_info['json_data_type'],
                'format': 'default'
            })
        for i in range(len(question_fields['fields'])):
            question_field, question_header, question_header_questionnaire = \
            question_fields['fields'][i], question_fields['header'][i], \
            question_fields['header_questionnaire'][i]
            question_cleared = ExportExecution._get_parent_question(
                question_field)
            question = next(
                item for item in questions
                if item['title'] == question_cleared)
            title = question_header_questionnaire \
                if heading_type != 'code' else question_field
            type = QUESTION_TYPES[question['type']][1]
            format = QUESTION_TYPES[question['type']][2]
            # i + 2: currently in export, question headers are inserted between
            # [participant_code, age] and the rest of participant fields
            # when those exists
            fields.insert(i + 2, {
                'name': title, 'title': title, 'type': type, 'format': format
            })

        return fields

    @staticmethod
    def _get_parent_question(field):
        """Some types of LimeSurvey questions are of the the form
        'question21[subquestion]'. Return only 'question21' part if this is the
        case.
        :param field: str, LimeSurvey question
        :return: str, substring of field
        """
        return re.search('([a-zA-Z0-9_]+)(\[?)', field).group(1)

    @staticmethod
    def _randomword(length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def _set_unique_resources_names(self, datapackage):
        for index, resource in enumerate(datapackage['resources']):
            resources_same_name = [
                resource['name'] for resource in datapackage['resources']
                if resource['name'] == datapackage['resources'][index]['name']
            ]
            if len(resources_same_name) > 1:  # There's a duplicate
                datapackage['resources'][index]['name'] = resource['name'] + self._randomword(3)

    def _build_resources(self, datapackage):
        for file in self.files_to_zip_list:
            if len(file) == 3:  # TODO (NES-987): just by now until having all files added
                datapackage['resources'].append(file[2])

    def _get_questionnaire_owners(self):
        limesurvey = Questionnaires()
        contributors = []
        for questionnaire in self.input_data['questionnaires']:
            sid = questionnaire['id']
            contributors.append({
                'title': limesurvey.get_survey_properties(sid, 'admin'),
                'email': limesurvey.get_survey_properties(sid, 'adminemail'),
                'questionnaire': str(sid) + ' - ' + questionnaire['questionnaire_name']
            })

        return contributors

    def _build_participant_datapackage_dict(self, request):
        title = 'Questionnaires Answered by Participants Outside Experiment Scope'
        name = slugify(title)
        description = 'Export made \"Per Participant\": the files contain metadata and responses of ' \
                      'questionnaires filled outside any experiment in the system. They can be entrance ' \
                      'questionnaires.'
        date_created = str(datetime.now().replace(microsecond=0))
        datapackage = {
            'title': title, 'name': name, 'description': description,
            'created': date_created,
            'contributors': self._get_questionnaire_owners(),
            'licenses': [LICENSES[int(request.POST.get('license', None))]],
            'resources': []  # Will be built below
        }

        self._build_resources(datapackage)

        return datapackage

    def _build_experiment_datapackage_dict(self, experiment, request):
        name = slugify(experiment.title)
        researcher_owner = experiment.research_project.owner

        datapackage = {
            'title': experiment.title, 'name': name, 'description': experiment.description,
            'created': str(datetime.now().replace(microsecond=0)),
            'homepage': request.get_host() + '/experiments/' + name,
            'contributors': [
                {
                    'title': researcher_owner.first_name + ' ' + researcher_owner.last_name,
                    'email': researcher_owner.email
                }
            ],
            'licenses': [LICENSES[int(request.session['license'])]],
            'resources': []  # Will be built below
        }
        # Add the other contributors (besides research project owner)
        for contributor in experiment.researchers.all():
            datapackage['contributors'].append({
                'title': contributor.researcher.first_name + ' ' + contributor.researcher.last_name,
                'email': contributor.researcher.email
            })
        # Add to datapackage resources
        self._build_resources(datapackage)

        return datapackage

    def process_experiment_data(self, language_code):
        error_msg = ''

        filesformat_type = self.get_input_data('filesformat_type')

        # process of experiment description
        for group_id in self.per_group_data:
            group = get_object_or_404(Group, pk=group_id)

        study = group.experiment.research_project
        experiment = group.experiment

        experiment_summary_header = [
            'Study', 'Study description', 'Start date', 'End date', 'Experiment Title',
            'Experiment description'
        ]
        experiment_summary = [
            study.title, study.description, str(study.start_date), str(study.end_date),
            experiment.title, experiment.description
        ]
        experiment_summary_field_types = [
            ResearchProject._meta.get_field('title').__class__,
            ResearchProject._meta.get_field('description').__class__,
            ResearchProject._meta.get_field('start_date').__class__,
            ResearchProject._meta.get_field('end_date').__class__,
            Experiment._meta.get_field('title').__class__,
            Experiment._meta.get_field('description').__class__
        ]

        file_extension = 'tsv' if 'tsv' in self.get_input_data('filesformat_type') else 'csv'
        filename_experiment_resume = 'Experiment' + '.' + file_extension

        # path ex. data/Experiment_data
        export_experiment_data = path.join(
            self.get_input_data('base_directory'), self.get_input_data('experiment_data_directory'))

        # path ex. User/.../qdc/media/.../data/Experiment_data
        experiment_resume_directory = path.join(
            self.get_export_directory(), self.get_input_data('experiment_data_directory'))

        # User/.../qdc/media/.../data/Experiment_data/Experiment.csv
        complete_filename_experiment_resume = path.join(experiment_resume_directory, filename_experiment_resume)

        experiment_description_fields = []
        experiment_description_fields.insert(0, experiment_summary_header)
        experiment_description_fields.insert(1, experiment_summary)
        save_to_csv(complete_filename_experiment_resume, experiment_description_fields, filesformat_type)

        self.files_to_zip_list.append([
            complete_filename_experiment_resume, export_experiment_data,
            {
                # For datapackages.json resources
                'name': 'Experiment', 'title': 'Experiment',
                'path': path.join(export_experiment_data, filename_experiment_resume),
                'format': file_extension, 'mediatype': 'text/%s' % file_extension,
                'encoding': 'UTF-8',
                'profile': 'tabular-data-resource',
                'schema': {
                    'fields': self._set_datapackage_table_schema(
                        experiment_summary_header, experiment_summary_field_types)
                }
            }
        ])

        # Process of filename for description of each group
        for group_id in self.per_group_data:
            group = get_object_or_404(Group, pk=group_id)
            if group.experimental_protocol:

                tree = get_block_tree(group.experimental_protocol, language_code)
                experimental_protocol_description = get_description_from_experimental_protocol_tree(tree)

                if experimental_protocol_description:
                    group_resume = 'Group name: ' + group.title + '\n' + 'Group description: ' \
                                   + group.description + '\n'
                    # group_directory_name = 'Group_' + group.title
                    filename_group_for_export = '%s.txt' % 'Experimental_protocol_description'
                    # path ex. User/.../qdc/media/.../data/Experiment_data/Group_xxxx/
                    group_file_directory = self.per_group_data[group_id]['group']['directory']
                    # path ex. data/Experiment_data/Group_xxxx/
                    export_group_directory = self.per_group_data[group_id]['group']['export_directory']
                    # path ex. data/Experiment_data/Group_xxx/Experimental_protocol
                    error_msg, directory_experimental_protocol = create_directory(
                        group_file_directory, 'Experimental_protocol')
                    if error_msg != '':
                        return error_msg

                    # path ex. data/Experiment_data/Group_xxx
                    export_directory_experimental_protocol = path.join(export_group_directory, 'Experimental_protocol')

                    # User/.../qdc/media/.../data/Experiment_data/Group_xxxx/Experimental_protocol/
                    # Experimental_protocol_description.txt
                    complete_group_filename = path.join(directory_experimental_protocol, filename_group_for_export)

                    filename, extension = PROTOCOL_DESCRIPTION_FILENAME.split('.')
                    self.files_to_zip_list.append([
                        complete_group_filename, export_directory_experimental_protocol,
                        {
                            'name': filename, 'title': filename,
                            'path': path.join(export_directory_experimental_protocol, PROTOCOL_DESCRIPTION_FILENAME),
                            'format': extension, 'mediatype': 'text/%s' % extension
                        }
                    ])

                    with open(complete_group_filename.encode('utf-8'), 'w', newline='', encoding='UTF-8') as txt_file:
                        txt_file.writelines(group_resume)
                        txt_file.writelines(experimental_protocol_description)

                # Save protocol image
                experimental_protocol_image = get_experimental_protocol_image(group.experimental_protocol, tree)
                if experimental_protocol_image:
                    complete_protocol_image_filename = path.join(
                        directory_experimental_protocol, PROTOCOL_IMAGE_FILENAME)
                    image_protocol = experimental_protocol_image
                    with open(image_protocol, 'rb') as f:
                        data = f.read()
                    with open(complete_protocol_image_filename, 'wb') as f:
                        f.write(data)
                    filename, extension = PROTOCOL_IMAGE_FILENAME.split('.')
                    self.files_to_zip_list.append([
                        complete_protocol_image_filename, export_directory_experimental_protocol,
                        {
                            'name': filename, 'title': filename,
                            'path': path.join(export_directory_experimental_protocol, PROTOCOL_IMAGE_FILENAME),
                            'format': extension, 'mediatype': 'image/%s' % extension
                        }
                    ])

                # Save eeg, emg, tms, context tree setting default in Experimental Protocol directory
                if 'eeg_default_setting_id' in self.per_group_data[group_id]:
                    eeg_default_setting_description = get_eeg_setting_description(
                        self.per_group_data[group_id]['eeg_default_setting_id'])

                    if eeg_default_setting_description:
                        filename, extension = EEG_DEFAULT_SETTING_FILENAME.split('.')
                        complete_filename_eeg_setting = path.join(
                            directory_experimental_protocol, EEG_DEFAULT_SETTING_FILENAME)
                        self.files_to_zip_list.append([
                            complete_filename_eeg_setting, export_directory_experimental_protocol,
                            {
                                'name': filename, 'title': filename,
                                'path': path.join(export_directory_experimental_protocol, EEG_DEFAULT_SETTING_FILENAME),
                                # TODO (NES-987): implement get_mediatype(extension) method
                                'format': extension, 'mediatype': 'application/%s' % extension
                            }
                        ])

                        with open(complete_filename_eeg_setting.encode('utf-8'), 'w', newline='',
                                  encoding='UTF-8') as outfile:
                            json.dump(eeg_default_setting_description, outfile, indent=4)

                if 'emg_default_setting_id' in self.per_group_data[group_id]:
                    emg_default_setting_description = get_emg_setting_description(
                        self.per_group_data[group_id]['emg_default_setting_id'])
                    if emg_default_setting_description:
                        filename, extension = EMG_DEFAULT_SETTING.split('.')
                        complete_filename_emg_setting = path.join(
                            directory_experimental_protocol, EMG_DEFAULT_SETTING)
                        self.files_to_zip_list.append([
                            complete_filename_emg_setting, export_directory_experimental_protocol,
                            {
                                'name': filename, 'title': filename,
                                'path': path.join(export_directory_experimental_protocol, EMG_DEFAULT_SETTING),
                                # TODO (NES-987): implement get_mediatype(extension) method
                                'format': extension, 'mediatype': 'application/%s' % extension
                            }
                        ])

                        with open(complete_filename_emg_setting.encode('utf-8'), 'w', newline='',
                                  encoding='UTF-8') as outfile:
                            json.dump(emg_default_setting_description, outfile, indent=4)

                if 'tms_default_setting_id' in self.per_group_data[group_id]:
                    tms_default_setting_description = get_tms_setting_description(
                        self.per_group_data[group_id]['tms_default_setting_id'])
                    if tms_default_setting_description:
                        filename, extension = TMS_DEFAULT_SETTING_FILENAME.split('.')
                        complete_filename_tms_setting = path.join(
                            directory_experimental_protocol, TMS_DEFAULT_SETTING_FILENAME)
                        self.files_to_zip_list.append([
                            complete_filename_tms_setting, export_directory_experimental_protocol,
                            {
                                'name': filename, 'title': filename,
                                'path': path.join(export_directory_experimental_protocol, TMS_DEFAULT_SETTING_FILENAME),
                                # TODO (NES-987): implement get_mediatype(extension) method
                                'format': extension, 'mediatype': 'application/%s' % extension
                            }
                        ])

                        with open(complete_filename_tms_setting.encode('utf-8'), 'w', newline='',
                                  encoding='UTF-8') as outfile:
                            json.dump(tms_default_setting_description, outfile, indent=4)

                if 'context_tree_default_id' in self.per_group_data[group_id]:
                    context_tree_default_description = get_context_tree_description(
                        self.per_group_data[group_id]['context_tree_default_id'])
                    if context_tree_default_description:
                        filename, extension = CONTEXT_TREE_DEFAULT.split('.')
                        complete_filename_context_tree = path.join(
                            directory_experimental_protocol, CONTEXT_TREE_DEFAULT)
                        self.files_to_zip_list.append([
                            complete_filename_context_tree, export_directory_experimental_protocol,
                            {
                                'name': filename, 'title': filename,
                                'path': path.join(export_directory_experimental_protocol, CONTEXT_TREE_DEFAULT),
                                # TODO (NES-987): implement get_mediatype(extension) method
                                'format': extension, 'mediatype': 'application/%s' % extension
                            }
                        ])

                        with open(complete_filename_context_tree.encode('utf-8'), 'w', newline='',
                                  encoding='UTF-8') as outfile:
                            json.dump(context_tree_default_description, outfile, indent=4)

                        context_tree = get_object_or_404(ContextTree, pk=self.per_group_data[group_id][
                            'context_tree_default_id'])

                    if context_tree.setting_file.name:
                        file_path = context_tree.setting_file.name
                        filename = path.basename(file_path)
                        context_tree_filename = path.join(settings.MEDIA_ROOT, file_path)
                        unique_name = slugify(filename)
                        # TODO (NES-987): change context_tree.setting_file.name.split('/')[-1]
                        complete_context_tree_filename = path.join(directory_experimental_protocol, filename)
                        with open(path.join(context_tree_filename), 'rb') as f:
                            data = f.read()
                        with open(complete_context_tree_filename, 'wb') as f:
                            f.write(data)

                        self.files_to_zip_list.append([
                            complete_context_tree_filename, export_directory_experimental_protocol,
                            {
                                'name': unique_name, 'title': unique_name,
                                'path': path.join(export_directory_experimental_protocol, filename),
                                'description': 'Context tree setting file'
                            }
                        ])

                for component in tree['list_of_component_configuration']:
                    for additionalfile in ComponentAdditionalFile.objects.filter(
                            component=component['component']['component']):
                        step_number = str(component['component']['numeration'])

                        step_name = additionalfile.component.component_type.upper()

                        path_additional_data = path.join(
                            group_file_directory, 'Experimental_protocol',
                            'Step_' + step_number + '_' + step_name, 'AdditionalData')
                        if not path.exists(path_additional_data):
                            error_msg, directory_additional_data = create_directory(
                                group_file_directory,
                                path.join(
                                    'Experimental_protocol', 'Step_' + step_number + '_' + step_name, 'AdditionalData'))
                            if error_msg != '':
                                return error_msg

                        export_directory_additional_data = path.join(
                            export_group_directory, 'Experimental_protocol', 'Step_' + step_number + '_' + step_name,
                            'AdditionalData')
                        filename = path.basename(additionalfile.file.name)
                        unique_name = slugify(filename)
                        path_additional_file = path.join(settings.MEDIA_ROOT, additionalfile.file.name)

                        complete_additional_data_filename = path.join(path_additional_data, filename)

                        with open(path_additional_file, 'rb') as f:
                            data = f.read()
                        with open(complete_additional_data_filename, 'wb') as f:
                            f.write(data)

                        self.files_to_zip_list.append([
                            complete_additional_data_filename, export_directory_additional_data,
                            {
                                'name': unique_name, 'title': unique_name,
                                'path': path.join(export_directory_additional_data, filename),
                                'description': 'Step additional file'
                            }
                        ])

                # Process participant/diagnosis per Participant of each group
                participant_group_list = []
                subject_of_group = SubjectOfGroup.objects.filter(group=group)
                for subject in subject_of_group:
                    participant_group_list.append(subject.subject.patient_id)

                if 'stimulus_data' in self.per_group_data[group_id]:
                    stimulus_data_list = self.per_group_data[group_id]['stimulus_data']
                    for stimulus_data in stimulus_data_list:
                        if stimulus_data['stimulus_file']:
                            # Path ex. data/Experiment_data/Group_xxxx/Step_X_STIMULUS
                            path_stimulus_data = path.join(group_file_directory, stimulus_data['directory_step_name'])
                            if not path.exists(path_stimulus_data):
                                error_msg, directory_stimulus_data = create_directory(
                                    group_file_directory, stimulus_data['directory_step_name'])
                                if error_msg != '':
                                    return error_msg

                            # Path ex. data/Experiment_data/Group_xxxx/Step_X_STIMULUS
                            export_directory_stimulus_data = path.join(
                                export_group_directory, stimulus_data['directory_step_name'])
                            path_stimulus_filename = path.join(
                                settings.MEDIA_ROOT, stimulus_data['stimulus_file'].media_file.name)
                            stimulus_filename = path.basename(path_stimulus_filename)
                            complete_stimulus_data_filename = path.join(path_stimulus_data, stimulus_filename)

                            # For datapackage resources
                            unique_name = slugify(stimulus_filename)
                            datapackage_resource = {
                                'name': unique_name, 'title': unique_name,
                                'path': path.join(export_directory_stimulus_data, stimulus_filename),
                                'description': 'Stimulus type: %s' % stimulus_data['stimulus_file'].stimulus_type.name
                            }

                            with open(path_stimulus_filename, 'rb') as f:
                                data = f.read()
                            with open(complete_stimulus_data_filename, 'wb') as f:
                                f.write(data)

                            self.files_to_zip_list.append([
                                complete_stimulus_data_filename, export_directory_stimulus_data, datapackage_resource
                            ])

        return error_msg

    def process_datapackage_json_file(self, request):
        """TODO (NES-987)
        :param request: request object
        """
        if 'group_selected_list' in request.session:
            # Get arbitrary key: all groups pertain to same experiment
            group = Group.objects.get(id=int(list(self.per_group_data.keys())[0]))
            datapackage_dict = self._build_experiment_datapackage_dict(group.experiment, request)
        else:
            datapackage_dict = self._build_participant_datapackage_dict(request)

        self._set_unique_resources_names(datapackage_dict)

        file_path = path.join(self.get_directory_base(), 'datapackage.json')
        with open(file_path, 'w') as file:
            json.dump(datapackage_dict, file)
        self.files_to_zip_list.append([file_path, ''])

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

        response_type = self.get_input_data('response_type')

        if not response_type:
            response_type = ['short']

        return response_type

    def get_heading_type(self):
        heading_type = self.get_input_data('heading_type')
        if not heading_type:
            heading_type = ['code']
        return heading_type

    def get_filesformat_type(self):

        filesformat_type = self.get_input_data('filesformat_type')

        if not filesformat_type:
            filesformat_type = ['csv']

        return filesformat_type

    def get_questionnaires_responses(self, heading_type):
        questionnaire_lime_survey = Questionnaires()
        response_type = self.get_response_type()
        self.questionnaires_responses = {}
        for group_id in self.get_input_data('questionnaires_from_experiments'):
            for questionnaire_id in self.get_input_data('questionnaires_from_experiments')[group_id]:
                language_list = self.get_input_data('questionnaire_language')[questionnaire_id]['language_list']
                questionnaire = self.get_input_data('questionnaires_from_experiments')[group_id][str(questionnaire_id)]
                headers, fields = self.questionnaire_utils.set_questionnaire_experiment_header_and_fields(
                        questionnaire_id, questionnaire)

                # TODO: This if is the first thing to do not inside for.
                # TODO: Put this as the first line of method.
                if limesurvey_available(questionnaire_lime_survey):
                    data_from_lime_survey = {}
                    for language in language_list:
                        responses_string1 = questionnaire_lime_survey.get_responses(
                            questionnaire_id, language, response_type[0])
                        fill_list1 = QuestionnaireUtils.responses_to_csv(responses_string1)

                        # Multiple choice answers need replacement
                        # TODO (NES-991): make a test for getting multiple choice questions
                        error, multiple_choice_questions = QuestionnaireUtils.get_questions(
                            questionnaire_lime_survey, questionnaire_id,
                            language, ['M', 'P'])
                        replace_multiple_choice_question_answers(
                            fill_list1, multiple_choice_questions)

                        # Read 'long' information, if necessary
                        if len(response_type) > 1:
                            responses_string2 = questionnaire_lime_survey.get_responses(
                                questionnaire_id, language, response_type[1])
                            fill_list2 = QuestionnaireUtils.responses_to_csv(
                                responses_string2)
                            # Multiple choice answers need replacement
                            # TODO (NES-991): make a test for getting multiple choice questions
                            error, multiple_choice_questions = QuestionnaireUtils.get_questions(
                                questionnaire_lime_survey, questionnaire_id, language)
                            replace_multiple_choice_question_answers(
                                fill_list2, multiple_choice_questions)
                        else:
                            fill_list2 = fill_list1

                        # Filter fields
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

                            token = line1[fill_list1[0].index('token')]
                            data_from_lime_survey[language][token] = list(data_fields_filtered)
                            line_index += 1
                    self.questionnaire_utils.redefine_header_and_fields_experiment(
                        questionnaire_id, header_filtered, fields, headers)

                    # "And" part is inserted because when exporting from plugin, all groups
                    # are being processed independently of participant has
                    # responses in the two questionnaires or not.
                    if self.per_group_data[group_id]['questionnaires_per_group'] \
                            and int(questionnaire_id) in self.per_group_data[group_id]['questionnaires_per_group']:
                        questionnaire_list = self.per_group_data[
                            group_id
                        ]['questionnaires_per_group'][int(questionnaire_id)]['token_list']
                        for questionnaire_data in questionnaire_list:
                            token_id = questionnaire_data['token_id']
                            completed = questionnaire_lime_survey.get_participant_properties(
                                questionnaire_id, token_id, 'completed')
                            if completed is not None and completed != 'N' and completed != '':
                                token = questionnaire_lime_survey.get_participant_properties(
                                    questionnaire_id, token_id, 'token')
                                header = self.questionnaire_utils.questionnaires_experiment_data[
                                    questionnaire_id
                                ]

                                if questionnaire_id not in self.questionnaires_responses:
                                    self.questionnaires_responses[questionnaire_id] = {}
                                if token not in self.questionnaires_responses[questionnaire_id]:
                                    self.questionnaires_responses[questionnaire_id][token_id] = {}

                                for language in data_from_lime_survey:
                                    fields_filtered_list = [header, data_from_lime_survey[language][token]]
                                    self.questionnaires_responses[questionnaire_id][token_id][language] = \
                                        fields_filtered_list

    def define_experiment_questionnaire(self, questionnaire, questionnaire_lime_survey):
        questionnaire_id = questionnaire['id']
        language = questionnaire['language']
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

            # read 'long' information, if necessary
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

                token = line1[fill_list1[0].index('token')]
                data_from_lime_survey[token] = list(data_fields_filtered)
                line_index += 1
            # self.update_questionnaire_experiment_rules(questionnaire_id)

            token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id, 'token')

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
                headers_participant_data, fields_participant_data = self.get_headers_and_fields(row['output_list'])

            header = self.questionnaire_utils.get_header_experiment_questionnaire(questionnaire_id)

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
        :param questionnaire_lime_survey:
        :param language:
        :return: list - fields_description, in case of success, else error code
        """
        # Questionnaire exportation - evaluation questionnaire
        questionnaire_id = questionnaire['id']
        response_type = self.get_response_type()
        export_rows = []

        # Verify if LimeSurvey is running
        available = limesurvey_available(questionnaire_lime_survey)

        headers, fields = self.questionnaire_utils.set_questionnaire_header_and_fields(questionnaire, True)

        questionnaire_exists = QuestionnaireResponse.objects.filter(survey__lime_survey_id=questionnaire_id).exists()
        # Filter data (participants)
        questionnaire_responses = QuestionnaireResponse.objects.filter(survey__lime_survey_id=questionnaire_id)

        # Include new filter that comes from advanced search
        filtered_data = self.get_participants_filtered_data()
        questionnaire_responses = questionnaire_responses.filter(patient_id__in=filtered_data)

        if questionnaire_exists and available:
            # Read all data for questionnaire_id from LimeSurvey
            result = questionnaire_lime_survey.get_responses(questionnaire_id, language, response_type[0])
            if result is None:
                return Questionnaires.ERROR_CODE

            fill_list1 = QuestionnaireUtils.responses_to_csv(result)

            # Multiple choice answers need replacement
            # TODO (NES-991): make a test for getting multiple choice questions
            error, multiple_choice_questions = QuestionnaireUtils.get_questions(
                questionnaire_lime_survey, questionnaire_id, language, ['M', 'P'])
            if error:
                return error
            replace_multiple_choice_question_answers(
                fill_list1, multiple_choice_questions)

            # Read 'long' information, if necessary
            if len(response_type) > 1:
                responses_string2 = questionnaire_lime_survey.get_responses(
                    questionnaire_id, language, response_type[1])
                fill_list2 = QuestionnaireUtils.responses_to_csv(
                    responses_string2)
                # Multiple choice answers need replacement
                # TODO (NES-991): make a test for getting multiple choice questions
                error, multiple_choice_questions = QuestionnaireUtils.get_questions(
                    questionnaire_lime_survey, questionnaire_id, language)
                replace_multiple_choice_question_answers(
                    fill_list1, multiple_choice_questions)
            else:
                fill_list2 = fill_list1

            # filter fields
            subscripts = []

            for field in fields:
                if field in fill_list1[0]:
                    subscripts.append(fill_list1[0].index(field))

            # If responses exists
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

                    token = line1[fill_list1[0].index('token')]
                    data_from_lime_survey[token] = list(data_fields_filtered)
                    line_index += 1

                self.update_questionnaire_rules(questionnaire_id)

                # For each questionnaire_id from ResponseQuestionnaire from questionnaire_id
                for questionnaire_response in questionnaire_responses:

                    # Transform data fields
                    # Include new fields

                    survey_code = questionnaire_response.survey.code
                    lime_survey_id = questionnaire_response.survey.lime_survey_id
                    patient_code = questionnaire_response.patient.code
                    token_id = questionnaire_response.token_id

                    token = questionnaire_lime_survey.get_participant_properties(questionnaire_id, token_id, 'token')
                    if token is None:
                        return Questionnaires.ERROR_CODE

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

                            self.include_in_per_participant_data(
                                transformed_fields, patient_code, survey_code, language)

                            self.include_participant_per_questionnaire(token_id, survey_code)

                headers, fields = self.questionnaire_utils.redefine_header_and_fields(
                    questionnaire_id, header_filtered, fields)

            # Build header
            participant_data_header = self.get_input_data('participants')['data_list'][0]

            header = self.build_header_questionnaire_per_participant(
                participant_data_header, headers[0:len(headers) - 1])

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
            impedance_description = eeg_amplifier_attributes['input_impedance'] + ' (' + eeg_amplifier_attributes[
                'input_impedance_unit'] + ')'
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
                'manufacturer_name': eeg_setting.eeg_electrode_layout_setting.eeg_electrode_net_system.eeg_electrode_net.manufacturer.name,
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
                impedance_description = electrode_model_attributes['impedance'] + ' (' + electrode_model_attributes[
                    'impedance_unit'] + ')'
            if electrode_model_attributes['inter_electrode_distance'] and \
                    electrode_model_attributes['inter_electrode_distance_unit']:
                electrode_distance_description = electrode_model_attributes['inter_electrode_distance'] + ' (' + \
                                                 electrode_model_attributes['inter_electrode_distance_unit'] + ')'
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
                electrode_model_attributes['impedance'] + ' (' + electrode_model_attributes['impedance_unit'] + ')'

        electrode_distance_description = ''
        if electrode_model_attributes['inter_electrode_distance'] and \
                electrode_model_attributes['inter_electrode_distance_unit']:
            electrode_distance_description = electrode_model_attributes['inter_electrode_distance'] + ' (' + \
                                             electrode_model_attributes['inter_electrode_distance_unit'] + ')'

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
            impedance_description = emg_amplifier_attributes['input_impedance'] + ' (' + emg_amplifier_attributes[
                'input_impedance_unit'] + ')'
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
                preamplifier_impedance_description = preamplifier_attributes['input_impedance'] + ' (' + \
                                                     preamplifier_attributes['input_impedance_unit'] + ')'

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
    if coil_orientation:
        coil_orientation_name = coil_orientation.name
        tms_description['stimulation_description'] = {
            'tms_stimulation_description': tms_data_attributes['description'],
            'resting_motor threshold-RMT(%)': tms_data_attributes['resting_motor_threshold'],
            'test_pulse_intensity_of_simulation(% over the %RMT)':
                tms_data_attributes['test_pulse_intensity_of_simulation'],
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
    tms_setting_description = {'name': tms_setting.name, 'description': tms_setting.description}

    return tms_setting_description


def get_context_tree_description(context_tree_id):
    context_tree = get_object_or_404(ContextTree, pk=context_tree_id)
    if context_tree:
        context_tree_description = {
            'name': context_tree.name, 'description': context_tree.description,
            'setting_text': context_tree.setting_text
        }

    return context_tree_description
