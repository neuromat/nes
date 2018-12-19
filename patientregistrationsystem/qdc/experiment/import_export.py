import os
import shutil
import tempfile
import zipfile
from os import path, mkdir

from django.conf import settings
from tablib import Dataset

from experiment.admin import ResearchProjectResource, ExperimentResource
from experiment.models import ResearchProject, Experiment


class ExportExperiment:

    ZIP_FILE_NAME = 'experiment'
    MEDIA_SUBDIR = 'media'
    RESEARCH_PROJECT_CSV = 'research_project.csv'
    EXPERIMENT_CSV = 'experiment.csv'

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

    def export_all(self):
        self.export_research_project()
        self.export_experiment()

        shutil.make_archive(path.join(self.temp_dir_zip, self.ZIP_FILE_NAME), 'zip', self.temp_dir)


class ImportExperiment:

    MEDIA_SUBDIR = 'media'
    RESEARCH_PROJECT_CSV = 'research_project.csv'
    EXPERIMENT_CSV = 'experiment.csv'
    BAD_ZIP_FILE = 1
    FILE_NOT_FOUND_ERROR = 2
    BAD_CSV_FILE = 3

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
                self.BAD_ZIP_FILE, 'Not a zip file. Aborting import experiment.'
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

    def import_research_project(self):
        file_path = path.join(self.temp_dir, self.RESEARCH_PROJECT_CSV)
        dataset = Dataset().load(open(file_path).read())
        result = ResearchProjectResource().import_data(dataset, dry_run=True)
        if result.has_errors():
            return 'Bad %s file' % self.RESEARCH_PROJECT_CSV

        ResearchProjectResource().import_data(dataset)
        return ResearchProject.objects.last()

    def import_experiment(self, research_project):
        file_path = path.join(self.temp_dir, self.EXPERIMENT_CSV)
        dataset = Dataset().load(open(file_path).read())
        dataset.append_col([research_project.id], header='research_project')
        result1 = self._validate_dataset(dataset, 'Experiment')
        result2 = ExperimentResource().import_data(dataset, dry_run=True)
        if result2.has_errors():
            return 'Bad %s file' % self.EXPERIMENT_CSV

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
                self.BAD_CSV_FILE, 'Bad %s file. Aborting import experiment.' % self.RESEARCH_PROJECT_CSV
            )
        experiment = self.import_experiment(research_project)
        if not isinstance(experiment, Experiment):
            return (
                self.BAD_CSV_FILE, 'Bad %s file. Aborting import experiment.' % self.EXPERIMENT_CSV
            )

    def _validate_dataset(self, dataset, model):
        pass
