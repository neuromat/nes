import os
import shutil
import tempfile
from os import path

from django.conf import settings

from experiment.admin import ExperimentResource, ResearchProjectResource
from experiment.models import Experiment


TEMP_DIR = tempfile.mkdtemp()
TEMP_MEDIA = path.join(TEMP_DIR, 'media')
ZIP_FILE_NAME = 'experiment'


def export_research_project(experiment):
    dataset = ResearchProjectResource().export(id=experiment.research_project.id)
    temp_file = path.join(TEMP_DIR, 'research_project.csv')
    with open(temp_file, 'w') as f:
        f.write(dataset.csv)


def make_zip(temp_dir):
    temp_dir_zip = tempfile.mkdtemp()
    shutil.make_archive(path.join(temp_dir_zip, ZIP_FILE_NAME), 'zip', temp_dir)


def copy_media_file(file_path):
    dir_media_file = path.join(TEMP_MEDIA, path.dirname(file_path))
    os.makedirs(dir_media_file)  # TODO: test for existence
    shutil.copy(path.join(settings.MEDIA_ROOT, file_path), dir_media_file)


def export_experiment(id_):
    experiment = Experiment.objects.get(id=id_)  # TODO: test for existence
    export_research_project(experiment)
    dataset = ExperimentResource().export(id=experiment.id)
    temp_file = path.join(TEMP_DIR, 'experiment.csv')
    with open(temp_file, 'w') as f:
        f.write(dataset.csv)

    os.mkdir(TEMP_MEDIA)
    file_path = dataset['ethics_committee_project_file'][0]  # TODO: better way?
    copy_media_file(file_path)

    make_zip(TEMP_DIR)


def remove_tem_dir():
    shutil.rmtree(TEMP_DIR)
