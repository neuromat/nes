import json
import os
import shutil
import sys
import tempfile
import zipfile
from json import JSONDecodeError
from os import path, mkdir

from django.conf import settings
from django.core.management import call_command
from tablib import Dataset

from experiment.admin import ResearchProjectResource, ExperimentResource, GroupResource, ComponentResource,\
    ComponentConfigResource
from experiment.models import Group, ComponentConfiguration, ResearchProject, Experiment


class ExportExperiment:

    ZIP_FILE_NAME = 'experiment'
    MEDIA_SUBDIR = 'media'
    RESEARCH_PROJECT_CSV = 'research_project.csv'
    EXPERIMENT_CSV = 'experiment.csv'
    GROUPS_CSV = 'groups.csv'
    COMPONENTS_CSV = 'components.csv'
    COMPONENTS_CONFIG_CSV = 'componentsconfig.csv'

    def __init__(self, experiment):
        self.experiment = experiment
        self.temp_dir = tempfile.mkdtemp()
        self.temp_media_dir = path.join(self.temp_dir, self.MEDIA_SUBDIR)
        self.temp_dir_zip = tempfile.mkdtemp()
        mkdir(self.temp_media_dir)

    def __del__(self):
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.temp_dir_zip)

    def copy_file(self, file_path):
        absolute_path = path.join(self.temp_media_dir, path.dirname(file_path))
        if not path.exists(absolute_path):
            os.makedirs(absolute_path)
        shutil.copy(path.join(settings.MEDIA_ROOT, file_path), absolute_path)

    def export_research_project(self):
        dataset = ResearchProjectResource().export(id=self.experiment.research_project.id)
        temp_filename = path.join(self.temp_dir, self.RESEARCH_PROJECT_CSV)
        with open(temp_filename, 'w') as f:
            f.write(dataset.csv)

    def export_experiment(self):
        dataset = ExperimentResource().export(id=self.experiment.id)
        # remove research_project from dataset;
        # it's included when importing (after creating it)
        # see that this is done because we can't include 'research_project' in exclude
        # Meta class attribute: fields listed there are considered both for export as
        # import
        del (dataset['research_project'])
        temp_filename = path.join(self.temp_dir, self.EXPERIMENT_CSV)
        with open(temp_filename, 'w') as f:
            f.write(dataset.csv)

        file_path = dataset['ethics_committee_project_file'][0]
        if file_path:
            self.copy_file(file_path)

    def export_groups(self):
        dataset = GroupResource().export(experiment=self.experiment)
        temp_filename = path.join(self.temp_dir, self.GROUPS_CSV)
        with open(temp_filename, 'w') as f:
            f.write(dataset.csv)

    def export_components(self):
        groups = Group.objects.filter(experiment=self.experiment)
        list_components_ids = []
        list_rootcomponents_ids = []
        for group in groups:
            rootcomponent_id = group.experimental_protocol_id
            list_components_ids.append(rootcomponent_id)
            list_rootcomponents_ids.append(rootcomponent_id)
            components = ComponentConfiguration.objects.filter(parent_id=rootcomponent_id)
            for component in components:
                list_components_ids.append(component.component_id)

        dataset_components = ComponentResource().export(ids=list_components_ids)
        temp_file = path.join(self.temp_dir, self.COMPONENTS_CSV)
        with open(temp_file, 'w') as f:
            f.write(dataset_components.csv)

        dataset_components_config = ComponentConfigResource().export(ids=list_rootcomponents_ids)
        temp_file = path.join(self.temp_dir, self.COMPONENTS_CONFIG_CSV)
        with open(temp_file, 'w') as f:
            f.write(dataset_components_config.csv)

    def export_all(self):
        self.export_research_project()
        self.export_experiment()
        self.export_groups()
        self.export_components()

        shutil.make_archive(path.join(self.temp_dir_zip, self.ZIP_FILE_NAME), 'zip', self.temp_dir)


class ImportExperiment:

    MEDIA_SUBDIR = 'media'
    RESEARCH_PROJECT_CSV = 'research_project.csv'
    EXPERIMENT_CSV = 'experiment.csv'
    BAD_ZIP_FILE_ERROR = 1
    FILE_NOT_FOUND_ERROR = 2
    BAD_CSV_FILE_ERROR = 3

    def __init__(self, file_path):
        self.file_path = file_path
        self.temp_dir = tempfile.mkdtemp()

    def __del__(self):
        shutil.rmtree(self.temp_dir)

    def _check_zip_file(self):
        try:
            zipfile.ZipFile(self.file_path)
        except zipfile.BadZipFile:
            return (
                self.BAD_ZIP_FILE_ERROR, 'Not a zip file. Aborting import experiment.'
            )

        with zipfile.ZipFile(self.file_path) as f:
            f.extractall(self.temp_dir)
        try:
            open(path.join(self.temp_dir, self.RESEARCH_PROJECT_CSV))
        except FileNotFoundError:
            return (
                self.FILE_NOT_FOUND_ERROR, '%s not found in zip file. Aborting import experiment.'
                % self.RESEARCH_PROJECT_CSV
            )
        try:
            open(path.join(self.temp_dir, self.EXPERIMENT_CSV))
        except FileNotFoundError:
            return (
                self.FILE_NOT_FOUND_ERROR, '%s not found in zip file. Aborting import experiment.'
                % self.EXPERIMENT_CSV
            )

        return 0, ''

    @staticmethod
    def _is_dataset_valid(dataset, model):
        """django-import-export package seems do not follow blank=False model field
        validation, neither the check for dataset headers corresponding to that fields,
        so by now we made validation by ourselves.
        """
        if model == Experiment.__name__:
            fields = set([f.name for f in Experiment._meta.get_fields()])
            if not (set(dataset.headers) <= fields):
                return False
            if (not dataset['title']) or (not dataset['description']):
                return False
        elif model == ResearchProject.__name__:
            fields = set([f.name for f in ResearchProject._meta.get_fields()])
            if not (set(dataset.headers) <= fields):
                return False
            if (not dataset['title']) or (not dataset['description']):
                return False
        else:
            raise ValueError('Invalid model')  # TODO: see if there is better exception for argument error

        return True

    def import_research_project(self):
        file_path = path.join(self.temp_dir, self.RESEARCH_PROJECT_CSV)
        dataset = Dataset().load(open(file_path).read())
        result = ResearchProjectResource().import_data(dataset, dry_run=True)
        if (not self._is_dataset_valid(dataset, ResearchProject.__name__)) or result.has_errors():
            return None

        ResearchProjectResource().import_data(dataset)
        return ResearchProject.objects.last()

    def import_experiment(self, research_project):
        file_path = path.join(self.temp_dir, self.EXPERIMENT_CSV)
        dataset = Dataset().load(open(file_path).read())
        dataset.append_col([research_project.id], header='research_project')
        result = ExperimentResource().import_data(dataset, dry_run=True)
        if (not self._is_dataset_valid(dataset, Experiment.__name__)) or result.has_errors():
            return None

        ExperimentResource().import_data(dataset, dry_run=False)
        return Experiment.objects.last()

    def import_all(self):
        err_code, err_message = self._check_zip_file()
        if err_code:
            return err_code, err_message

        with zipfile.ZipFile(self.file_path) as f:
            f.extractall(self.temp_dir)

        research_project = self.import_research_project()
        if not isinstance(research_project, ResearchProject):
            return (
                self.BAD_CSV_FILE_ERROR, 'Bad %s file. Aborting import experiment.' % self.RESEARCH_PROJECT_CSV
            )
        experiment = self.import_experiment(research_project)
        if not isinstance(experiment, Experiment):
            return (
                self.BAD_CSV_FILE_ERROR, 'Bad %s file. Aborting import experiment.' % self.EXPERIMENT_CSV
            )

        return 0, ''


class ExportExperiment2:

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

        list_of_files = ['experimentfixture.json', 'componentconfiguration.json', 'group.json', 'block.json',
                         'instruction.json', 'pause.json', 'questionnaire.json', 'stimulus.json', 'task.json',
                         'task_experiment.json', 'eeg.json', 'emg.json', 'tms.json', 'digital_game_phase.json',
                         'generic_data_collection.json']

        fixtures = []
        for filename in list_of_files:
            fixtures.append(path.join(self.temp_dir, filename))

        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, self.FILE_NAME), 'w')

        call_command('merge_fixtures', *fixtures)

        sys.stdout = sysout

        self.remove_auth_user_model_from_json(self.FILE_NAME)

    def get_file_path(self):
        return path.join(self.temp_dir, self.FILE_NAME)


class ImportExperiment2:
    BAD_JSON_FILE_ERROR = 1
    FIXTURE_FILE_NAME = 'experiment.json'

    def __init__(self, file_path):
        self.file_path = file_path
        self.temp_dir = tempfile.mkdtemp()

    def __del__(self):
        shutil.rmtree(self.temp_dir)

    @staticmethod
    def _update_pk(data, model, request=None):
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == model]
        if model == 'experiment.researchproject':
            data[indexes[0]]['pk'] = ResearchProject.objects.last().id + 1
            data[indexes[0]]['owner'] = request.user.id
            index_experiment = next(
                (index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.experiment'),
                None
            )
            data[index_experiment]['fields']['research_project'] = data[indexes[0]]['pk']
        if model == 'experiment.experiment':
            data[indexes[0]]['pk'] = Experiment.objects.last().id + 1
            for (index_group, dict_) in enumerate(data):
                if dict_['model'] == 'experiment.group':
                    data[index_group]['fields']['experiment'] = data[indexes[0]]['pk']
        if model == 'experiment.group':
            next_group_id = Group.objects.last().id + 1
            for i in indexes:
                data[i]['pk'] = next_group_id
                next_group_id += 1

    def _update_pks(self, data, request):
        self._update_pk(data, 'experiment.researchproject', request)
        self._update_pk(data, 'experiment.experiment')
        has_groups = next((item for item in data if item['model'] == 'experiment.group'), None)
        if has_groups:
            self._update_pk(data, 'experiment.group')

    def import_all(self, request):
        try:
            with open(self.file_path) as f:
                data = json.load(f)
        except (ValueError, JSONDecodeError):
            return self.BAD_JSON_FILE_ERROR, 'Bad json file. Aborting import experiment.'

        self._update_pks(data, request)
        with open(path.join(self.temp_dir, self.FIXTURE_FILE_NAME), 'w') as file:
            file.write(json.dumps(data))

        call_command('loaddata', path.join(self.temp_dir, self.FIXTURE_FILE_NAME))

        return 0, ''
