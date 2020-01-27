# -*- coding: utf-8 -*-
from json import dump, load
from survey.abc_search_engine import Questionnaires
from survey.views import get_questionnaire_language


BASE_DIRECTORY = "data"
PER_PARTICIPANT_DIRECTORY = "Per_participant"
PER_QUESTIONNAIRE_DIRECTORY = "Per_questionnaire"
QUESTIONNAIRE_METADATA_DIRECTORY = "Questionnaire_metadata"
PARTICIPANT_DATA_DIRECTORY = "Participant_data"
EXPERIMENT_DATA_DIRECTORY = "Experiment_data"
GOALKEEPER_GAME_DATA_DIRECTORY = "Goalkeeper_game_data"
EXPORT_FILENAME = "export.zip"
EXPORT_EXPERIMENT_FILENAME = "export_experiment.zip"

EXPORT_PER_PARTICIPANT = 1
EXPORT_PER_QUESTIONNAIRE = 1

DEFAULT_LANGUAGE = "pt-BR"
PREFIX_FILENAME_FIELDS = "Fields"
PREFIX_FILENAME_RESPONSES = "Responses"

OUTPUT_FILENAME_PARTICIPANTS = "Participants"
OUTPUT_FILENAME_DIAGNOSIS = "Diagnosis"


class InputExport:
    def __init__(self):
        self.data = {}

    def read(self, input_filename, update_input_data=True):
        with open(input_filename.encode('utf-8'), 'r') as input_file:
            input_data_temp = load(self.data, input_file)

            if update_input_data:
                self.data = input_data_temp

        return self.data

    def write(self, output_filename):
        with open(output_filename.encode('utf-8'), 'w', encoding='UTF-8') as outfile:
            dump(self.data, outfile)

    def build_header(self, export_per_experiment):
        # /data
        self.data["base_directory"] = BASE_DIRECTORY
        self.data["per_participant_directory"] = PER_PARTICIPANT_DIRECTORY
        self.data["per_questionnaire_directory"] = PER_QUESTIONNAIRE_DIRECTORY
        self.data["questionnaire_metadata_directory"] = QUESTIONNAIRE_METADATA_DIRECTORY
        self.data["export_filename"] = EXPORT_FILENAME
        if export_per_experiment:
            self.data["experiment_data_directory"] = EXPERIMENT_DATA_DIRECTORY
            self.data["participant_data_directory"] = PARTICIPANT_DATA_DIRECTORY
            self.data["goalkeeper_game_data_directory"] = GOALKEEPER_GAME_DATA_DIRECTORY

    def build_dynamic_header(self, variable_name, variable_data):
        self.data[variable_name] = variable_data

    def build_diagnosis_participant(self, strut_name, output_filename, field_header_list):
        self.data[strut_name] = {"output_filename": output_filename, "output_list": [], "data_list": []}
        for field, header in field_header_list:
            output_data = {"header": header, "field": field}
            self.data[strut_name]["output_list"].append(output_data)

    def build_questionnaire(self, questionnaire_list, language, entrance_questionnaire):
        questionnaire_lime_survey = Questionnaires()
        if "questionnaire_language" not in self.data:
            self.data["questionnaire_language"] = {}

        if entrance_questionnaire:
            self.data["questionnaires"] = []

            for index, sid, title, field_header_list in questionnaire_list:
                output_language = get_questionnaire_language(questionnaire_lime_survey, sid, language)

                languages = questionnaire_lime_survey.get_survey_languages(sid)
                language_list = [languages['language']]
                if languages['additional_languages']:
                    additional_language = languages['additional_languages'].split(' ')
                else:
                    additional_language = ['']
                for item in additional_language:
                    if item != '':
                        language_list.append(item)

                if sid not in self.data["questionnaire_language"]:
                    self.data["questionnaire_language"][sid] = {
                        "language_list": language_list,
                        "output_language": output_language,
                    }

                self.data["questionnaires"].append({
                    "id": sid,
                    "prefix_filename_fields": PREFIX_FILENAME_FIELDS,
                    "questionnaire_name": title,
                    "prefix_filename_responses": PREFIX_FILENAME_RESPONSES,
                    "output_list": [], "responses_list": []
                })
                for header, field in field_header_list:
                    output_data = {"header": header, "field": field}
                    self.data["questionnaires"][-1]["output_list"].append(output_data)

        else:
            self.data["questionnaires_from_experiments"] = {}

            for index, group_id, sid, title, field_header_list in questionnaire_list:
                output_language = get_questionnaire_language(questionnaire_lime_survey, sid, language)
                languages = questionnaire_lime_survey.get_survey_languages(sid)
                language_list = [languages['language']]
                if languages['additional_languages']:
                    additional_language = languages['additional_languages'].split(' ')
                else:
                    additional_language = ['']
                for item in additional_language:
                    if item != '':
                        language_list.append(item)

                if sid not in self.data["questionnaire_language"]:
                    self.data["questionnaire_language"][sid] = {
                        "language_list": language_list,
                        "output_language": output_language,
                    }

                if group_id not in self.data['questionnaires_from_experiments']:
                    self.data['questionnaires_from_experiments'][group_id] = {}

                if sid not in self.data['questionnaires_from_experiments'][group_id]:
                    self.data['questionnaires_from_experiments'][group_id][sid] = {
                        "prefix_filename_fields": PREFIX_FILENAME_FIELDS,
                        "questionnaire_name": title,
                        "prefix_filename_responses": PREFIX_FILENAME_RESPONSES,
                        "output_list": []
                    }

                for header, field in field_header_list:
                    output_data = {"header": header, "field": field}
                    self.data["questionnaires_from_experiments"][group_id][sid]["output_list"].append(output_data)

                if sid not in self.data["questionnaire_list"]:
                    self.data["questionnaire_list"].append(sid)

        questionnaire_lime_survey.release_session_key()


def build_partial_export_structure(export_per_participant, participant_field_header_list, output_filename):

    json_data = InputExport()

    json_data.build_header()
    json_data.build_dynamic_header("export_per_participant", export_per_participant)
    json_data.build_diagnosis_participant("participants", OUTPUT_FILENAME_PARTICIPANTS, participant_field_header_list)
    json_data.write(output_filename)


def build_complete_export_structure(
        export_per_participant, export_per_questionnaire, export_per_experiment,
        participant_field_header_list, diagnosis_field_header_list, questionnaires_list,
        experiment_questionnaires_list, response_type, heading_type,
        output_filename, component_list, language, filesformat_type):

    json_data = InputExport()

    json_data.build_header(export_per_experiment)

    json_data.build_dynamic_header("export_per_participant", export_per_participant)

    json_data.build_dynamic_header("export_per_questionnaire", export_per_questionnaire)

    json_data.build_dynamic_header("response_type", response_type)

    json_data.build_dynamic_header("heading_type", heading_type)

    json_data.build_dynamic_header("filesformat_type", filesformat_type)

    json_data.build_dynamic_header("output_language", language)

    json_data.build_diagnosis_participant("participants", OUTPUT_FILENAME_PARTICIPANTS, participant_field_header_list)

    json_data.build_diagnosis_participant("diagnosis", OUTPUT_FILENAME_DIAGNOSIS, diagnosis_field_header_list)

    json_data.data["questionnaire_list"] = []

    json_data.build_questionnaire(questionnaires_list, language, entrance_questionnaire=True)

    if export_per_experiment:
        json_data.build_dynamic_header("export_per_experiment", export_per_experiment)
        json_data.build_questionnaire(experiment_questionnaires_list, language, entrance_questionnaire=False)
        json_data.data["component_list"] = component_list
    json_data.write(output_filename)
