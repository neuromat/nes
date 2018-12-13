import os
import shutil
import tempfile
from os import path

from django.conf import settings

from experiment.admin import ExperimentResource, ResearchProjectResource
from experiment.models import Experiment


MEDIA_SUBDIR = 'media'
ZIP_FILE_NAME = 'experiment'


def export_research_project(temp_dirname, experiment):
    dataset = ResearchProjectResource().export(id=experiment.research_project.id)
    temp_filename = path.join(temp_dirname, 'research_project.csv')
    with open(temp_filename, 'w') as f:
        f.write(dataset.csv)


def make_zip(temp_dir):
    temp_dir_zip = tempfile.mkdtemp()
    shutil.make_archive(path.join(temp_dir_zip, ZIP_FILE_NAME), 'zip', temp_dir)


def copy_media_file(temp_media_subdir, file_path):
    data_collection_subdir = path.join(temp_media_subdir, path.dirname(file_path))
    os.makedirs(data_collection_subdir)
    shutil.copy(path.join(settings.MEDIA_ROOT, file_path), data_collection_subdir)


def export_experiment(id_):
    temp_dirname = tempfile.mkdtemp()
    temp_media_subdir = path.join(temp_dirname, MEDIA_SUBDIR)
    os.mkdir(temp_media_subdir)

    experiment = Experiment.objects.get(id=id_)  # TODO: test for existence
    export_research_project(temp_dirname, experiment)
    dataset = ExperimentResource().export(id=experiment.id)
    # remove research_project from dataset; it'll be included when importing
    del(dataset['research_project'])
    temp_file = path.join(temp_dirname, 'experiment.csv')
    with open(temp_file, 'w') as f:
        f.write(dataset.csv)

    file_path = dataset['ethics_committee_project_file'][0]  # TODO: better way using tablib?
    if file_path:
        copy_media_file(temp_media_subdir, file_path)

    make_zip(temp_dirname)


def remove_temp_dir(temp_dir):
    shutil.rmtree(temp_dir)
