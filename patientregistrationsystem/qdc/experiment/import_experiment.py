import tempfile
import zipfile
from os import path

from django.core.files import File
from tablib import Dataset

from experiment.admin import ResearchProjectResource, ExperimentResource
from experiment.models import ResearchProject, Experiment


MEDIA_DIR = 'media'


def import_research_project(base_dir, file_name):
    file_path = path.join(base_dir, file_name)
    dataset = Dataset().load(open(file_path).read())
    result = ResearchProjectResource().import_data(dataset, dry_run=True)
    if not result:
        print('Error!')  # TODO: return error
    ResearchProjectResource().import_data(dataset)

    return ResearchProject.objects.last()


def import_experiment(base_dir, file_name, research_project):
    file_path = path.join(base_dir, file_name)
    dataset = Dataset().load(open(file_path).read())
    dataset.append_col([research_project.id], header='research_project')
    result = ExperimentResource().import_data(dataset, dry_run=True)
    if not result:
        print('Error!')  # TODO: return error
    ExperimentResource().import_data(dataset)

    return Experiment.objects.last()


def upload_file(base_dir, experiment):
    ethics_committee_filename = experiment.ethics_committee_project_file.name
    with open(path.join(base_dir, ethics_committee_filename), 'rb') as f:
        experiment.ethics_committee_project_file.save(path.basename(f.name), File(f))


def import_all(zip_path):
    temp_dir = tempfile.mkdtemp()
    temp_media = path.join(temp_dir, MEDIA_DIR)
    with zipfile.ZipFile(zip_path) as f:
        f.extractall(temp_dir)

    research_project = import_research_project(temp_dir, 'research_project.csv')
    experiment = import_experiment(temp_dir, 'experiment.csv', research_project)
    print(experiment.ethics_committee_project_file.name)  # DEBUG
    if experiment.ethics_committee_project_file.name:
        upload_file(temp_media, experiment)
