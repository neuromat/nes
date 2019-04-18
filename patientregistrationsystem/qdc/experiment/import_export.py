import base64
import os
import re
import shutil
import sys
import tempfile
import json
import zipfile
from json import JSONDecodeError
from os import path

from functools import reduce
from operator import or_

import networkx as nx
from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.apps import apps
from django.db.models import Count, Q
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient

from experiment.models import Group, ResearchProject, Experiment, \
    Keyword, Component, Questionnaire
from experiment.import_export_model_relations import ONE_TO_ONE_RELATION, FOREIGN_RELATIONS, MODEL_ROOT_NODES, \
    EXPERIMENT_JSON_FILES, PATIENT_JSON_FILES, JSON_FILES_DETACHED_MODELS, PRE_LOADED_MODELS_FOREIGN_KEYS, \
    PRE_LOADED_MODELS_INHERITANCE, PRE_LOADED_MODELS_NOT_EDITABLE, PRE_LOADED_PATIENT_MODEL, \
    PRE_LOADED_MODELS_NOT_EDITABLE_INHERITANCE, MODELS_WITH_FILE_FIELD, MODELS_WITH_RELATION_TO_AUTH_USER
from patient.models import Patient, ClassificationOfDiseases
from survey.abc_search_engine import Questionnaires
from survey.models import Survey


class ExportExperiment:

    FILE_NAME_JSON = 'experiment.json'
    FILE_NAME_ZIP = 'experiment.zip'

    def __init__(self, experiment):
        self.experiment = experiment
        self.temp_dir = tempfile.mkdtemp()

    def __del__(self):
        shutil.rmtree(self.temp_dir)

    def _generate_fixture(self, filename, elements, app='experiment.'):
        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, filename + '.json'), 'w')
        call_command(
            'dump_object', app + elements[0], '--query',
            '{"' + elements[1] + '": ' + str([self.experiment.id]) + '}'
        )
        sys.stdout = sysout

    def _generate_detached_fixture(self, filename, elements):
        with open(path.join(self.temp_dir, elements[3] + '.json')) as file:
            data = json.load(file)
        parent_ids = [dict_['pk'] for index, dict_ in enumerate(data) if dict_['model'] == elements[2]]

        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, filename + '.json'), 'w')
        call_command(
            'dump_object', 'experiment.' + elements[0], '--query', '{"' + elements[1] + '": ' + str(parent_ids) + '}')
        sys.stdout = sysout

    def _generate_keywords_fixture(self):
        # Generate fixture to keywords of the research project
        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, 'keywords.json'), 'w')
        call_command('dump_object', 'experiment.researchproject_keywords', '--query',
                     '{"researchproject_id__in": ' + str([self.experiment.research_project.id]) + '}')
        sys.stdout = sysout

    def _remove_auth_user_model_from_json(self, filename):
        with open(path.join(self.temp_dir, filename)) as f:
            data = f.read().replace('\n', '')

        deserialized = json.loads(data)
        while True:
            index = next(
                (index for (index, dict_) in enumerate(deserialized) if dict_['model'] == 'auth.user'),
                None
            )
            if index is None:
                break
            del deserialized[index]

        with open(path.join(self.temp_dir, filename), 'w') as f:
            f.write(json.dumps(deserialized))

    def _remove_researchproject_keywords_model_from_json(self, filename):
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
    def _change_group_code_to_null_from_json(self, filename):
        with open(path.join(self.temp_dir, filename)) as f:
            data = f.read().replace('\n', '')

        serialized = json.loads(data)
        indexes = [index for (index, dict_) in enumerate(serialized) if
                   dict_['model'] == 'experiment.group']
        for i in sorted(indexes, reverse=True):
            serialized[i]['fields']['code'] = None

        with open(path.join(self.temp_dir, filename), 'w') as f:
            f.write(json.dumps(serialized))

    def _remove_survey_code(self, filename):
        with open(path.join(self.temp_dir, filename)) as f:
            data = f.read().replace('\n', '')

        serialized = json.loads(data)
        indexes = [index for (index, dict_) in enumerate(serialized) if
                   dict_['model'] == 'survey.survey']
        for i in indexes:
            serialized[i]['fields']['code'] = ''

        with open(path.join(self.temp_dir, filename), 'w') as f:
            f.write(json.dumps(serialized))

    def _update_classification_of_diseases_reference(self, filename):
        """Change json data exported to replace references to classification
        of diseases so the reference is to code not to id. We consider that
        NES instances all share the same classification of diseases data
        """
        with open(path.join(self.temp_dir, filename)) as f:
            data = f.read().replace('\n', '')

        serialized = json.loads(data)
        indexes = [index for (index, dict_) in enumerate(serialized) if dict_['model'] == 'patient.diagnosis']
        for index in indexes:
            pk = serialized[index]['fields']['classification_of_diseases']
            code = ClassificationOfDiseases.objects.get(id=int(pk)).code
            # make a list with one element as natural key in dumped data has to be a list
            serialized[index]['fields']['classification_of_diseases'] = [code]

        # Remove ClassificationOfDiseases items: these data are preloaded in database
        while True:
            index = next(
                (index for (index, dict_) in enumerate(serialized) if dict_['model'] ==
                 'patient.classificationofdiseases'), None)
            if index is None:
                break
            del serialized[index]

        with open(path.join(self.temp_dir, filename), 'w') as f:
            f.write(json.dumps(serialized))

    def _copy_from_limesurvey_server(self, remote_archive_paths):
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy)  # TODO (NES-956): add only for Limesurvey host?
        # TODO (NES-956): put exception trying to connect
        ssh.connect(
            settings.LIMESURVEY_SERVER['host'], settings.LIMESURVEY_SERVER['port'],
            settings.LIMESURVEY_SERVER['user'], settings.LIMESURVEY_SERVER['password'],
            sock=None)
        scp = SCPClient(ssh.get_transport())
        local_survey_paths = []
        for remote_archive_path in remote_archive_paths:
            dest_file = os.path.join(self.temp_dir, '%s.lsa' % remote_archive_path[1])
            # TODO (NES-956): put exception trying to download file
            scp.get(remote_archive_path[0], dest_file)
            local_survey_paths.append(dest_file)

        ssh.close()

        return local_survey_paths

    @staticmethod
    def _remove_remote_survey_archives(remote_survey_archive_paths):
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy)  # TODO (NES-956): add only for Limesurvey host?
        # TODO (NES-956): put exception trying to connect
        ssh.connect(
            settings.LIMESURVEY_SERVER['host'], settings.LIMESURVEY_SERVER['port'],
            settings.LIMESURVEY_SERVER['user'], settings.LIMESURVEY_SERVER['password'],
            sock=None)
        sftp = ssh.open_sftp()
        for remote_survey_archive_path in remote_survey_archive_paths:
            # TODO (NES-956): put exception trying to remove
            sftp.remove(remote_survey_archive_path[0])

    def _export_surveys(self):
        """Export experiment surveys archives using LimeSurvey RPC API.
        The archive files are saved in LimeSurvey default temp directory.
        After saved archives are copyed to local NES file system.
        :return: list of survey archive paths
        """
        questionnaire_ids = Questionnaire.objects.filter(
            experiment=self.experiment).values_list('survey_id', flat=True)
        surveys = Survey.objects.filter(id__in=questionnaire_ids)
        questionnaire = Questionnaires()
        remote_archive_paths = []
        for survey in surveys:
            archive_path = questionnaire.export_survey(survey.lime_survey_id)
            if archive_path is not None:
                remote_archive_paths.append((archive_path, str(survey.lime_survey_id),))

        if remote_archive_paths:
            survey_archive_paths = self._copy_from_limesurvey_server(remote_archive_paths)
            self._remove_remote_survey_archives(remote_archive_paths)
            return survey_archive_paths
        else:
            return []  # TODO (NES_956): return empty list?

    def _create_zip_file(self, survey_archives):
        """Create zip file with experiment.json file and subdirs corresponding
        to file paths from models that have FileField fields
        :param survey_archives: list of survey archive paths
        """
        with open(self.get_file_path('json')) as f:
            data = json.load(f)

        indexes = [index for index, dict_ in enumerate(data) if dict_['model'] in MODELS_WITH_FILE_FIELD]
        with zipfile.ZipFile(self.get_file_path(), 'w') as zip_file:
            zip_file.write(self.get_file_path('json').encode('utf-8'), self.FILE_NAME_JSON)
            # Append file subdirs
            for index in indexes:
                # Relative to MEDIA_ROOT
                relative_filepath = data[index]['fields'][MODELS_WITH_FILE_FIELD[data[index]['model']]]
                if relative_filepath is not '':
                    absolute_filepath = path.join(settings.MEDIA_ROOT, relative_filepath)
                    zip_file.write(absolute_filepath, relative_filepath)
            # Append limesurvey archives if they exists
            for survey_archive_path in survey_archives:
                zip_file.write(survey_archive_path, os.path.basename(survey_archive_path))

    def get_file_path(self, type_='zip'):
        if type_ == 'zip':
            return path.join(self.temp_dir, self.FILE_NAME_ZIP)
        elif type_ == 'json':
            return path.join(self.temp_dir, self.FILE_NAME_JSON)

    def export_all(self):
        for key, value in EXPERIMENT_JSON_FILES.items():
            self._generate_fixture(key, value)
        for key, value in PATIENT_JSON_FILES.items():
            self._generate_fixture(key, value, 'patient.')
        for key, value in JSON_FILES_DETACHED_MODELS.items():
            self._generate_detached_fixture(key, value)
        self._generate_keywords_fixture()

        fixtures = []
        for filename in {**EXPERIMENT_JSON_FILES, **PATIENT_JSON_FILES, **JSON_FILES_DETACHED_MODELS}:
            fixtures.append(path.join(self.temp_dir, filename + '.json'))

        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, self.FILE_NAME_JSON), 'w')
        call_command('merge_fixtures', *fixtures)
        sys.stdout = sysout

        # TODO: remove self.FILE_NAME_JSON as they are accessible for all methods in the class
        self._remove_researchproject_keywords_model_from_json(self.FILE_NAME_JSON)
        self._change_group_code_to_null_from_json(self.FILE_NAME_JSON)
        self._remove_survey_code(self.FILE_NAME_JSON)
        self._update_classification_of_diseases_reference(self.FILE_NAME_JSON)
        self._remove_auth_user_model_from_json(self.FILE_NAME_JSON)

        survey_archive_paths = self._export_surveys()
        self._create_zip_file(survey_archive_paths)


class ImportExperiment:
    BAD_JSON_FILE_ERROR_CODE = 1
    FIXTURE_FILE_NAME = 'experiment.json'

    def __init__(self, file_path):
        self.file_path = file_path
        self.temp_dir = tempfile.mkdtemp()
        self.data = []
        self.last_objects_before_import = dict()
        self.new_objects = dict()

    def __del__(self):
        shutil.rmtree(self.temp_dir)

    def _set_last_objects_before_import(self, research_project_id):
        """Identify last objects to deduct after import, so
        we can identify the new objects imported
        :param data: list created with json.loads from json file with
        the objects that will be imported
        """
        self.last_objects_before_import['experiment'] = Experiment.objects.last()
        if not research_project_id:
            self.last_objects_before_import['research_project'] = ResearchProject.objects.last()
        has_groups = next(
            (index for (index, dict_) in enumerate(self.data) if dict_['model'] == 'experiment.group'), None
        )
        has_components = next(
            (index for (index, dict_) in enumerate(self.data) if dict_['model'] == 'experiment.component'), None
        )
        if has_groups:
            self.last_objects_before_import['group'] = Group.objects.last()
        if has_components:
            self.last_objects_before_import['component'] = Component.objects.last()

    @staticmethod
    def _include_human_readables(components):
        """Add the titles of steps (components) of experimental protocol to display
        in import log page
        """
        human_readables = dict(Component.COMPONENT_TYPES)
        for i, component in enumerate(components):
            components[i]['human_readable'] = str(human_readables[component['component_type']])

    def _collect_new_objects(self):
        """Collect new objects to display to user some main objects that was
        imported
        """
        last_experiment = Experiment.objects.last()
        self.new_objects['experiment_id'] = last_experiment.id
        self.new_objects['experiment_title'] = last_experiment.title
        if 'research_project' in self.last_objects_before_import:
            last_study = ResearchProject.objects.last()
            self.new_objects['research_project_id'] = last_study.id
            self.new_objects['research_project_title'] = last_study.title
        else:
            self.new_objects['research_id'] = None
        if 'group' in self.last_objects_before_import:
            if self.last_objects_before_import['group'] is not None:
                last_group_before_import = self.last_objects_before_import['group'].id
                self.new_objects['groups_count'] = Group.objects.filter(id__gt=last_group_before_import).count()
            else:
                self.new_objects['groups_count'] = Group.objects.count()
        else:
            self.new_objects['groups_count'] = None
        if 'component' in self.last_objects_before_import:
            if self.last_objects_before_import['component'] is not None:
                last_component_before_import = self.last_objects_before_import['component'].id
                component_queryset = Component.objects.filter(id__gt=last_component_before_import)
            else:
                component_queryset = Component.objects.all()
            components = component_queryset.values('component_type').annotate(count=Count('component_type'))
            self._include_human_readables(components)
            self.new_objects['components'] = list(components)

        else:
            self.new_objects['components'] = None

    def _update_research_project_pk(self, id_):
        if id_:
            research_project_index = next(
                index for index, dict_ in enumerate(self.data) if dict_['model'] == 'experiment.researchproject'
            )
            del(self.data[research_project_index])
            experiment_index = next(
                index for index, dict_ in enumerate(self.data) if dict_['model'] == 'experiment.experiment'
            )
            self.data[experiment_index]['fields']['research_project'] = id_

    def _verify_keywords(self):
        indexes = [index for (index, dict_) in enumerate(self.data) if dict_['model'] == 'experiment.keyword']
        next_keyword_id = Keyword.objects.last().id + 1 if Keyword.objects.count() > 0 else 1
        indexes_of_keywords_already_updated = []
        for i in indexes:
            # Get the keyword and check on database if the keyword already exists.
            # If exists, update the pk of this keyword to the correspondent in the database
            # otherwise, update the pk of this keyword to next_keyword_id
            old_keyword_id = self.data[i]['pk']
            old_keyword_string = self.data[i]['fields']['name']
            keyword_on_database = Keyword.objects.filter(name=old_keyword_string)

            if keyword_on_database.count() > 0:
                self.data[i]['pk'] = keyword_on_database.first().id
            else:
                self.data[i]['pk'] = next_keyword_id
                next_keyword_id += 1

            # Update all the references to the old keyword to the new one
            for (index_row, dict_) in enumerate(self.data):
                if dict_['model'] == 'experiment.researchproject':
                    for (keyword_index, keyword) in enumerate(dict_['fields']['keywords']):
                        if keyword == old_keyword_id and keyword_index not in indexes_of_keywords_already_updated:
                            self.data[index_row]['fields']['keywords'][keyword_index] = self.data[i]['pk']
                            indexes_of_keywords_already_updated.append(keyword_index)

    def _update_patients_stuff(self, patients_to_update):
        indexes = [index for (index, dict_) in enumerate(self.data) if dict_['model'] == 'patient.patient']

        # Update patient codes
        # TODO (Refactor): Patient model has function to generate random patient code
        patients = Patient.objects.all()
        if patients:
            last_patient_code = patients.order_by('-code').first().code
            if last_patient_code:
                numerical_part_code = int(last_patient_code.split('P')[1])
                next_numerical_part = numerical_part_code + 1
                for i in indexes:
                    if str(self.data[i]['pk']) not in patients_to_update:
                        self.data[i]['fields']['code'] = 'P' + str(next_numerical_part)
                        next_numerical_part += 1

        for i in indexes:
            if str(self.data[i]['pk']) not in patients_to_update:
                if Patient.objects.filter(cpf=self.data[i]['fields']['cpf']):
                    self.data[i]['fields']['cpf'] = None

    def _update_references_to_user(self, request):
        for model in MODELS_WITH_RELATION_TO_AUTH_USER:
            indexes = [index for (index, dict_) in enumerate(self.data) if dict_['model'] == model[0]]
            for i in indexes:
                self.data[i]['fields'][model[1]] = request.user.id

    # def _solve_limey_survey_reference(self, survey_index):
    #     min_limesurvey_id = Survey.objects.all().order_by('lime_survey_id')[0].lime_survey_id
    #     if min_limesurvey_id >= 0:
    #         new_limesurvey_id = -99
    #     else:
    #         min_limesurvey_id -= 1
    #         new_limesurvey_id = min_limesurvey_id
    #     self.data[survey_index]['fields']['lime_survey_id'] = new_limesurvey_id

    # def _make_dummy_reference_to_limesurvey(self):
        # survey_indexes = [index for index, dict_ in enumerate(self.data) if dict_['model'] == 'survey.survey']
        # for survey_index in survey_indexes:
        #     self._solve_limey_survey_reference(survey_index)

    def _update_survey_data(self, surveys_imported):
        next_code = Survey.create_random_survey_code()
        min_limesurvey_id = Survey.objects.all().order_by('lime_survey_id')[0].lime_survey_id
        if min_limesurvey_id >= 0:
            dummy_limesurvey_id = -99
        else:
            dummy_limesurvey_id = min_limesurvey_id

        for key, new_survey in surveys_imported.items():
            next_code = 'Q' + str(int(next_code.split('Q')[1]) + 1)
            self.data[key[0]]['fields']['code'] = next_code
            if new_survey is not None:
                self.data[key[0]]['fields']['lime_survey_id'] = new_survey
            else:
                self.data[key[0]]['fields']['lime_survey_id'] = dummy_limesurvey_id
                dummy_limesurvey_id -= 1

    def _keep_objects_pre_loaded(self):
        """For objects in fixtures initially loaded, check if the objects
        that are to be are already there. This is to avoid duplication of that objects.
        The objects checked here are the ones that can be edited. Objects that are not
        editable are simply ignored when updating indexes in _update_pks method.
        """
        for model, dependent_models in PRE_LOADED_MODELS_FOREIGN_KEYS.items():
            indexes = [index for (index, dict_) in enumerate(self.data) if dict_['model'] == model[0]]
            app_model = model[0].split('.')
            for i in indexes:
                model_class = apps.get_model(app_model[0], app_model[1])
                filter_ = {}
                for field in model[1]:
                    filter_[field] = self.data[i]['fields'][field]
                if not filter_:  # If not filter_, instance have only relational fields
                    instance = model_class.objects.first()
                else:
                    instance = model_class.objects.filter(**filter_).first()
                if instance:
                    # Deal with models that inherit from Multi-table inheritance mode
                    if self.data[i]['model'] in PRE_LOADED_MODELS_INHERITANCE:
                        app_model_inheritade = PRE_LOADED_MODELS_INHERITANCE[self.data[i]['model']][0].split('.')
                        model_class_inheritade = apps.get_model(app_model_inheritade[0], app_model_inheritade[1])
                        index_inheritade = [index for (index, dict_inheritance) in enumerate(self.data) if
                                            dict_inheritance['model'] == PRE_LOADED_MODELS_INHERITANCE[self.data[i][
                                                'model']][0] and dict_inheritance['pk'] == self.data[i]['pk']][0]
                        filter_inheritade = {}
                        for field in PRE_LOADED_MODELS_INHERITANCE[self.data[i]['model']][1]:
                            filter_inheritade[field] = self.data[index_inheritade]['fields'][field]
                        instance_inheritade = model_class_inheritade.objects.filter(**filter_inheritade).first()
                        if instance_inheritade:
                            self.data[index_inheritade]['pk'] = instance.id
                        else:
                            break
                    self.data[i]['pk'], old_id = instance.id, self.data[i]['pk']
                    # Finally, assign the old id to the relation
                    for dependent_model in dependent_models:
                        dependent_indexes = [
                            index for (index, dict_) in enumerate(self.data)
                            if dict_['model'] == dependent_model[0] and dict_['fields'][dependent_model[1]] == old_id
                        ]
                        for dependent_index in dependent_indexes:
                            self.data[dependent_index]['fields'][dependent_model[1]] = self.data[i]['pk']

    def _keep_patients_pre_loaded(self, patients_to_update):
        for model, dependent_models in PRE_LOADED_PATIENT_MODEL.items():
            indexes = [index for (index, dict_) in enumerate(self.data) if dict_['model'] == model[0]]
            for i in indexes:
                list_of_filters = [Q(**{key: val}) for key, val in [('cpf', self.data[i]['fields']['cpf']),
                                                                    ('name', self.data[i]['fields']['name'])]]

                instance = Patient.objects.filter(reduce(or_, list_of_filters)).first()
                if instance and str(instance.id) in patients_to_update:
                    self.data[i]['pk'], old_id = instance.id, self.data[i]['pk']
                    for dependent_model in dependent_models:
                        dependent_indexes = [
                            index for (index, dict_) in enumerate(self.data)
                            if dict_['model'] == dependent_model[0] and dict_['fields'][dependent_model[1]] == old_id
                        ]
                        for dependent_index in dependent_indexes:
                            self.data[dependent_index]['fields'][dependent_model[1]] = self.data[i]['pk']

    def _check_for_duplicates_of_participants(self):
        try:
            with zipfile.ZipFile(self.file_path) as zip_file:
                json_file = zip_file.extract(self.FIXTURE_FILE_NAME, self.temp_dir)
                with open(json_file) as f:
                    data = json.load(f)
        except (ValueError, JSONDecodeError):
            return self.BAD_JSON_FILE_ERROR_CODE, 'Bad json file. Aborting import experiment.', None

        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'patient.patient']

        list_of_participants_with_conflict = []
        for i in indexes:
            list_of_filters = [Q(**{key: val}) for key, val in [('cpf', data[i]['fields']['cpf']),
                                                                ('name', data[i]['fields']['name'])]]

            patient_already_in_database = Patient.objects.filter(reduce(or_, list_of_filters)).first()

            if patient_already_in_database:
                list_of_participants_with_conflict.append(
                    {'id_db': patient_already_in_database.pk,
                     'name_db': patient_already_in_database.name,
                     'code_db': patient_already_in_database.code,
                     'cpf_db': patient_already_in_database.cpf,
                     'id_new': data[i]['pk'],
                     'name_new': data[i]['fields']['name'],
                     'code_new': data[i]['fields']['code'],
                     'cpf_new': data[i]['fields']['cpf'],
                     'selected': None})

        return 0, '', list_of_participants_with_conflict

    def _verify_classification_of_diseases(self):
        indexes = [index for (index, dict_) in enumerate(self.data) if dict_['model'] == 'patient.diagnosis']
        for index in indexes:
            class_of_diseases = ClassificationOfDiseases.objects.filter(
                code=self.data[index]['fields']['classification_of_diseases'][0]
            ).first()
            if not class_of_diseases:
                ClassificationOfDiseases.objects.create(
                    code=self.data[index]['fields']['classification_of_diseases'][0],
                    description='(imported, not recognized)',
                    abbreviated_description='(imported, not recognized)'
                )

    def _update_data_before_importing(self, request, research_project_id, patients_to_update):
        # self._make_dummy_reference_to_limesurvey()
        self._update_research_project_pk(research_project_id)
        self._verify_keywords()
        self._update_references_to_user(request)
        # self._update_survey_data()
        self._keep_objects_pre_loaded()
        self._keep_patients_pre_loaded(patients_to_update)
        self._update_patients_stuff(patients_to_update)
        self._verify_classification_of_diseases()

    @staticmethod
    def _get_first_available_id():
        last_id = 1
        for app in apps.get_app_configs():
            if app.verbose_name in ['Experiment', 'Patient', 'Quiz', 'Survey', 'Team']:
                for model in app.get_models():
                    if 'Goalkeeper' not in model.__name__:  # TODO: ver modelo com referência a outro bd: dá pau
                        last_model = model.objects.last()
                        if last_model and hasattr(last_model, 'id'):
                            last_model_id = last_model.id
                            last_id = last_model_id if last_id < last_model_id else last_id
        return last_id + 1

    def _update_pks(self, digraph, successor, next_id):
        """Recursive function to update models pks based on a directed graph representing
        model relations
        """
        if self.data[successor]['model'] not in ONE_TO_ONE_RELATION and not digraph.node[successor]['pre_loaded']:
            if not digraph.node[successor]['updated']:
                self.data[successor]['pk'] = next_id

                # Patch for repeated next_id in same models
                model = self.data[successor]['model']
                updated_ids = [dict_['pk'] for (index, dict_) in enumerate(self.data) if dict_['model'] == model]
                if next_id in updated_ids:
                    # Prevent from duplicated pks in same model: this is done in the recursive path
                    # TODO: verify better way to update next_id
                    next_id = max(updated_ids) + 1
                    self.data[successor]['pk'] = next_id
                digraph.node[successor]['updated'] = True
        for predecessor in digraph.predecessors(successor):
            if 'relation' in digraph[predecessor][successor]:
                relation = digraph[predecessor][successor]['relation']
                self.data[predecessor]['fields'][relation] = self.data[successor]['pk']
            else:
                self.data[predecessor]['pk'] = self.data[successor]['pk']
            next_id += 1
            self._update_pks(digraph, predecessor, next_id)

    def _build_digraph(self):
        digraph = nx.DiGraph()
        for index_from, dict_ in enumerate(self.data):
            if dict_['model'] in FOREIGN_RELATIONS:
                node_from = dict_['model']
                nodes_to = FOREIGN_RELATIONS[node_from]
                for node_to in nodes_to:
                    index_to = next(
                        (index_foreign for index_foreign, dict_foreign in enumerate(self.data)
                         if dict_foreign['model'] == node_to[0] and dict_foreign['pk'] == dict_['fields'][node_to[1]]),
                        None
                    )
                    if index_to is not None:
                        digraph.add_edge(index_from, index_to)
                        digraph[index_from][index_to]['relation'] = node_to[1]
            if dict_['model'] in ONE_TO_ONE_RELATION:
                node_from = dict_['model']
                node_to = ONE_TO_ONE_RELATION[node_from]
                index_to = next(
                    (index_inheritade for index_inheritade, dict_inheritade in enumerate(self.data)
                     if dict_inheritade['model'] == node_to and dict_inheritade['pk'] == dict_['pk']),
                    None
                )
                if index_to is not None:
                    digraph.add_edge(index_from, index_to)

        for node in digraph.nodes():
            digraph.node[node]['atributes'] = self.data[node]
            digraph.node[node]['updated'] = False
            if self.data[node]['model'] not in PRE_LOADED_MODELS_NOT_EDITABLE:
                digraph.node[node]['pre_loaded'] = False
            else:
                digraph.node[node]['pre_loaded'] = True

        # set digraph.node[node]['pre_loaded'] == True for models inherited
        nodes = [
            node for node in digraph.nodes if self.data[node]['model'] in PRE_LOADED_MODELS_NOT_EDITABLE_INHERITANCE
        ]
        for node in nodes:
            model_inheritances = PRE_LOADED_MODELS_NOT_EDITABLE_INHERITANCE[self.data[node]['model']]
            for model in model_inheritances:
                node_inheritance = next(node_inheritance for node_inheritance in digraph.nodes if self.data[node_inheritance]['model'] == model and
                                        self.data[node]['pk'] == self.data[node_inheritance]['pk'])
                digraph.node[node_inheritance]['pre_loaded'] = True

        return digraph

    def _manage_pks(self, digraph):
        next_id = self._get_first_available_id()
        for model_root_node in MODEL_ROOT_NODES:
            root_nodes = [index for index, dict_ in enumerate(self.data) if dict_['model'] == model_root_node]
            for root_node in root_nodes:
                self._update_pks(digraph, root_node, next_id)
                next_id += 1

    def _upload_files(self):
        indexes = [index for index, dict_ in enumerate(self.data) if dict_['model'] in MODELS_WITH_FILE_FIELD]
        with zipfile.ZipFile(self.file_path) as zip_file:
            for index in indexes:
                relative_path = self.data[index]['fields'][MODELS_WITH_FILE_FIELD[self.data[index]['model']]]
                if relative_path:
                    file_path = zip_file.extract(relative_path, self.temp_dir)
                    app_model = self.data[index]['model'].split('.')
                    model_class = apps.get_model(app_model[0], app_model[1])
                    object_imported = model_class.objects.get(id=self.data[index]['pk'])
                    with File(open(file_path, 'rb')) as f:
                        file_field = MODELS_WITH_FILE_FIELD[self.data[index]['model']]
                        getattr(object_imported, file_field).save(path.basename(file_path), f)
                        object_imported.save()

    def _get_indexes(self, app, model):
        deserialized = json.loads(self.data)
        return [index for (index, dict_) in enumerate(deserialized) if dict_['model'] == app + model]

    def _import_surveys(self):
        """Import surveys to Limesurvey server and call updating references
        in json data
        """
        surveys_imported = dict()
        surveys = Questionnaires()
        indexes = [index for (index, dict_) in enumerate(self.data) if dict_['model'] == 'survey.survey']
        # Does not add try/exception trying to open zipfile here because it
        # was done in import_all method
        with zipfile.ZipFile(self.file_path) as zip_file:
            for index in indexes:
                limesurvey_id = self.data[index]['fields']['lime_survey_id']
                survey_archivename = str(limesurvey_id) + '.lsa'
                if survey_archivename in zip_file.namelist():
                    survey_archive = zip_file.extract(survey_archivename, self.temp_dir)
                    with open(survey_archive, 'rb') as file:
                        encoded_string = base64.b64encode(file.read())
                        encoded_string = encoded_string.decode('utf-8')
                    try:
                        result = surveys.import_survey(encoded_string)
                        # TODO (NES-956): see if this is the value returned allways when could not
                        #  create survey
                        # TODO (NES-956): maybe it's only necessary index
                        surveys_imported[(index, limesurvey_id)] = None if not result else result
                    except:  # TODO (NES-956): specify exception
                        # TODO: return with messages
                        pass
                else:
                    surveys_imported[(index, limesurvey_id)] = None

        if indexes:
            self._update_survey_data(surveys_imported)

    def import_all(self, request, research_project_id=None, patients_to_update=None):
        # TODO: maybe this try in constructor
        try:
            with zipfile.ZipFile(self.file_path) as zip_file:
                json_file = zip_file.extract(self.FIXTURE_FILE_NAME, self.temp_dir)
                with open(json_file) as f:
                    self.data = json.load(f)
                    # To Import Log page
                    self._set_last_objects_before_import(research_project_id)
        except (ValueError, JSONDecodeError):
            return self.BAD_JSON_FILE_ERROR_CODE, 'Bad json file. Aborting import experiment.'

        digraph = self._build_digraph()
        self._manage_pks(digraph)
        self._update_data_before_importing(request, research_project_id, patients_to_update)
        self._import_surveys()

        with open(path.join(self.temp_dir, self.FIXTURE_FILE_NAME), 'w') as file:
            file.write(json.dumps(self.data))

        call_command('loaddata', path.join(self.temp_dir, self.FIXTURE_FILE_NAME))
        self._upload_files()

        self._collect_new_objects()

        return 0, ''

    def get_new_objects(self):
        return self.new_objects
