import tempfile
import zipfile
from os import path

from tablib import Dataset

from experiment.admin import ResearchProjectResource, ExperimentResource
from experiment.models import ResearchProject


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
    print(dataset.csv)  # DEBUG
    result = ExperimentResource().import_data(dataset, dry_run=True)
    if not result:
        print('Error!')  # TODO: return error
    ExperimentResource().import_data(dataset)


def import_all(zip_path):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_path) as f:
        f.extractall(temp_dir)

    research_project = import_research_project(temp_dir, 'research_project.csv')
    import_experiment(temp_dir, 'experiment.csv', research_project)
