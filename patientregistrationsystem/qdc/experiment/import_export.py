import json
import shutil
import sys
import tempfile
from json import JSONDecodeError
from os import path

from django.core.management import call_command
from django.apps import apps

from experiment.models import Group, ComponentConfiguration, ResearchProject, Experiment,\
    Keyword, Component, TaskForTheExperimenter, EEG, EMG, TMS, DigitalGamePhase, GenericDataCollection
from survey.models import Survey


class ExportExperiment:

    FILE_NAME = 'experiment.json'

    def __init__(self, experiment):
        self.experiment = experiment
        self.temp_dir = tempfile.mkdtemp()

    def __del__(self):
        shutil.rmtree(self.temp_dir)

    def generate_fixture(self, filename, element, key_path):
        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, filename), 'w')

        call_command('dump_object', 'experiment.' + element, '--query',
                     '{"' + key_path + '": ' + str([self.experiment.id]) + '}'
                     )

        sys.stdout = sysout

    def remove_auth_user_model_from_json(self, filename):
        with open(path.join(self.temp_dir, filename)) as f:
            data = f.read().replace('\n', '')

        deserialized = json.loads(data)
        key = next((index for (index, d) in enumerate(deserialized) if d['model'] == 'auth.user'), None)
        del (deserialized[key])

        with open(path.join(self.temp_dir, filename), 'w') as f:
            f.write(json.dumps(deserialized))

    def remove_researchproject_keywords_model_from_json(self, filename):
        with open(path.join(self.temp_dir, filename)) as f:
            data = f.read().replace('\n', '')

        deserialized = json.loads(data)
        indexes = [index for (index, dict_) in enumerate(deserialized) if
                   dict_['model'] == 'experiment.researchproject_keywords']
        for i in sorted(indexes, reverse=True):
            del (deserialized[i])

        with open(path.join(self.temp_dir, filename), 'w') as f:
            f.write(json.dumps(deserialized))

    # TODO: In future, import groups verifying existence of group_codes in the database, not excluding them
    def change_group_code_to_null_from_json(self, filename):
        with open(path.join(self.temp_dir, filename)) as f:
            data = f.read().replace('\n', '')

        serialized = json.loads(data)
        indexes = [index for (index, dict_) in enumerate(serialized) if
                   dict_['model'] == 'experiment.group']
        for i in sorted(indexes, reverse=True):
            serialized[i]['fields']['code'] = None

        with open(path.join(self.temp_dir, filename), 'w') as f:
            f.write(json.dumps(serialized))

    def export_all(self):
        key_path = 'component_ptr_id__experiment_id__in'

        self.generate_fixture('experimentfixture.json', 'experiment', 'id__in')
        self.generate_fixture('componentconfiguration.json', 'componentconfiguration', 'component_id__experiment_id__in')
        self.generate_fixture('group.json', 'group', 'experiment_id__in')
        self.generate_fixture('block.json', 'block', key_path)
        self.generate_fixture('instruction.json', 'instruction', key_path)
        self.generate_fixture('pause.json', 'pause', key_path)
        self.generate_fixture('questionnaire.json', 'questionnaire', key_path)
        self.generate_fixture('stimulus.json', 'stimulus', key_path)
        self.generate_fixture('task.json', 'task', key_path)
        self.generate_fixture('task_experiment.json', 'taskfortheexperimenter', key_path)
        self.generate_fixture('eeg.json', 'eeg', key_path)
        self.generate_fixture('emg.json', 'emg', key_path)
        self.generate_fixture('tms.json', 'tms', key_path)
        self.generate_fixture('digital_game_phase.json', 'digitalgamephase', key_path)
        self.generate_fixture('generic_data_collection.json', 'genericdatacollection', key_path)

        # Generate fixture to keywords of the research project
        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, 'keywords.json'), 'w')
        call_command('dump_object', 'experiment.researchproject_keywords', '--query',
                     '{"researchproject_id__in": ' + str([self.experiment.research_project.id]) + '}')
        sys.stdout = sysout

        list_of_files = ['experimentfixture.json', 'componentconfiguration.json', 'group.json', 'block.json',
                         'instruction.json', 'pause.json', 'questionnaire.json', 'stimulus.json', 'task.json',
                         'task_experiment.json', 'eeg.json', 'emg.json', 'tms.json', 'digital_game_phase.json',
                         'generic_data_collection.json', 'keywords.json']

        fixtures = []
        for filename in list_of_files:
            fixtures.append(path.join(self.temp_dir, filename))

        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, self.FILE_NAME), 'w')

        call_command('merge_fixtures', *fixtures)

        sys.stdout = sysout

        self.remove_auth_user_model_from_json(self.FILE_NAME)
        self.remove_researchproject_keywords_model_from_json(self.FILE_NAME)
        self.change_group_code_to_null_from_json(self.FILE_NAME)

    def get_file_path(self):
        return path.join(self.temp_dir, self.FILE_NAME)


class ImportExperiment:
    BAD_JSON_FILE_ERROR = 1
    FIXTURE_FILE_NAME = 'experiment.json'

    def __init__(self, file_path):
        self.file_path = file_path
        self.temp_dir = tempfile.mkdtemp()

    def __del__(self):
        shutil.rmtree(self.temp_dir)

    def _get_model_name_by_component_type(self, component_type):
        if component_type == Component.TASK_EXPERIMENT:
            model_name = TaskForTheExperimenter.__name__
        elif component_type == Component.DIGITAL_GAME_PHASE:
            model_name = DigitalGamePhase.__name__
        elif component_type == Component.GENERIC_DATA_COLLECTION:
            model_name = GenericDataCollection.__name__
        elif component_type == Component.EEG:
            model_name = EEG.__name__
        elif component_type == Component.EMG:
            model_name = EMG.__name__
        elif component_type == Component.TMS:
            model_name = TMS.__name__
        else:
            model_name = component_type

        return model_name

    def _update_pk(self, data, model, request=None, research_project_id=None):
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == model]
        if model == 'experiment.researchproject':
            if research_project_id:
                data[indexes[0]]['pk'] = int(research_project_id)
            else:
                data[indexes[0]]['pk'] = ResearchProject.objects.last().id + 1 \
                    if ResearchProject.objects.count() > 0 else 1
            data[indexes[0]]['owner'] = request.user.id

            for (index_row, dict_) in enumerate(data):
                if dict_['model'] == 'experiment.experiment':
                    data[index_row]['fields']['research_project'] = data[indexes[0]]['pk']
                if dict_['model'] == 'experiment.researchproject_keywords':
                    data[index_row]['fields']['researchproject'] = data[indexes[0]]['pk']

        if model == 'experiment.keyword':
            next_keyword_id = Keyword.objects.last().id + 1 if Keyword.objects.count() > 0 else 1
            indexes_of_keywords_already_updated = []
            for i in indexes:
                old_keyword_id = data[i]['pk']
                old_keyword_string = data[i]['fields']['name']
                keyword_on_database = Keyword.objects.filter(name=old_keyword_string)
                if keyword_on_database.count() > 0:
                    data[i]['pk'] = keyword_on_database.first().id
                else:
                    data[i]['pk'] = next_keyword_id
                    next_keyword_id += 1

                for (index_row, dict_) in enumerate(data):
                    if dict_['model'] == 'experiment.researchproject_keywords':
                        if dict_['fields']['keyword'] == old_keyword_id:
                            data[index_row]['fields']['keyword'] = data[i]['pk']
                    if dict_['model'] == 'experiment.researchproject':
                        for (keyword_index, keyword) in enumerate(dict_['fields']['keywords']):
                            if keyword == old_keyword_id and keyword_index not in indexes_of_keywords_already_updated:
                                data[index_row]['fields']['keywords'][keyword_index] = data[i]['pk']
                                indexes_of_keywords_already_updated.append(keyword_index)

        if model == 'experiment.experiment':
            data[indexes[0]]['pk'] = Experiment.objects.last().id + 1 if Experiment.objects.count() > 0 else 1
            for (index_row, dict_) in enumerate(data):
                if "experiment" in data[index_row]['fields']:
                    data[index_row]['fields']['experiment'] = data[indexes[0]]['pk']

        if model == 'experiment.group':
            next_group_id = Group.objects.last().id + 1 if Group.objects.count() > 0 else 1
            for i in indexes:
                data[i]['pk'] = next_group_id
                next_group_id += 1

        if model == 'experiment.component':
            next_component_id = Component.objects.last().id + 1 if Component.objects.count() > 0 else 1
            for i in indexes:
                old_component_id = data[i]['pk']
                data[i]['pk'] = next_component_id
                component_type = self._get_model_name_by_component_type(data[i]['fields']['component_type'])
                for (index_row, dict_) in enumerate(data):
                    if dict_['model'] == 'experiment.' + component_type.lower():
                        if dict_['pk'] == old_component_id:
                            data[index_row]['pk'] = next_component_id
                    if dict_['model'] == 'experiment.componentconfiguration':
                        if dict_['fields']['component'] == old_component_id:
                            data[index_row]['fields']['component'] = next_component_id
                        if dict_['fields']['parent'] == old_component_id:
                            data[index_row]['fields']['parent'] = next_component_id
                    if dict_['model'] == 'experiment.group':
                        if dict_['fields']['experimental_protocol'] == old_component_id:
                            data[index_row]['fields']['experimental_protocol'] = next_component_id
                next_component_id += 1

        if model == 'experiment.componentconfiguration':
            next_component_config_id = ComponentConfiguration.objects.last().id + 1 \
                if ComponentConfiguration.objects.count() > 0 else 1
            for i in indexes:
                data[i]['pk'] = next_component_config_id
                next_component_config_id += 1

        list_of_dependent_models = ['experiment.eegsetting', 'experiment.emgsetting', 'experiment.tmssetting',
                                    'experiment.informationtype', 'experiment.contexttree', 'experiment.stimulustype']
        list_of_dependent_models_fields = ['eeg_setting', 'emg_setting', 'tms_setting',
                                           'information_type', 'context_tree', 'stimulus_type']

        if model in list_of_dependent_models:
            model_ = apps.get_model('experiment', model.split('.')[-1])
            next_model_id = model_.objects.last().id + 1 if model_.objects.count() > 0 else 1
            for i in indexes:
                data[i]['pk'] = next_model_id
                field = list_of_dependent_models_fields[list_of_dependent_models.index(model)]
                field_indexes = [field_index for (field_index, dict_) in
                                 enumerate(data) if field in data[field_index]['fields']]
                for i in field_indexes:
                    data[i]['fields'][field] = next_model_id
                next_model_id += 1

        if model == 'survey.survey':
            next_survey_id = Survey.objects.last().id + 1 if Survey.objects.count() > 0 else 1
            for i in indexes:
                data[i]['pk'] = next_survey_id
                for (index_row, dict_) in enumerate(data):
                    if 'survey' in dict_[index_row]['fields']:
                        data[index_row]['fields']['survey'] = next_model_id
                next_survey_id += 1

    def _update_pks(self, data, request, research_project_id=None):
        self._update_pk(data, 'experiment.researchproject', request, research_project_id)
        self._update_pk(data, 'experiment.keyword')
        self._update_pk(data, 'experiment.experiment')

        dependent_models = ['experiment.eegsetting', 'experiment.emgsetting', 'experiment.tmssetting',
                            'experiment.informationtype', 'experiment.contexttree', 'experiment.stimulustype',
                            'survey.survey']
        has_dependent_models = next((item for item in data if item['model'] in dependent_models), None)
        if has_dependent_models:
            self._update_pk(data, 'experiment.eegsetting')
            self._update_pk(data, 'experiment.emgsetting')
            self._update_pk(data, 'experiment.tmssetting')
            self._update_pk(data, 'experiment.informationtype')
            self._update_pk(data, 'experiment.contexttree')
            self._update_pk(data, 'experiment.stimulustype')
            self._update_pk(data, 'survey.survey')

        has_components = next((item for item in data if item['model'] == 'experiment.component'), None)
        if has_components:
            self._update_pk(data, 'experiment.component')
        has_component_configurations = next((item for item in data
                                             if item['model'] == 'experiment.componentconfiguration'), None)
        if has_component_configurations:
            self._update_pk(data, 'experiment.componentconfiguration')

        has_groups = next((item for item in data if item['model'] == 'experiment.group'), None)
        if has_groups:
            self._update_pk(data, 'experiment.group')

    def import_all(self, request, research_project_id=None):
        try:
            with open(self.file_path) as f:
                data = json.load(f)
        except (ValueError, JSONDecodeError):
            return self.BAD_JSON_FILE_ERROR, 'Bad json file. Aborting import experiment.'

        self._update_pks(data, request, research_project_id)
        with open(path.join(self.temp_dir, self.FIXTURE_FILE_NAME), 'w') as file:
            file.write(json.dumps(data))

        call_command('loaddata', path.join(self.temp_dir, self.FIXTURE_FILE_NAME))

        return 0, ''

