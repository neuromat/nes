import shutil
import sys
import tempfile
import json
from json import JSONDecodeError
from os import path

import networkx as nx
from django.core.management import call_command
from django.apps import apps
from django.db.models import Count

from experiment.models import Group, ResearchProject, Experiment, \
    Keyword, Component
from experiment.import_export_model_relations import one_to_one_relation, foreign_relations, model_root_nodes, \
    experiment_json_files, patient_json_files, json_files_detached_models, pre_loaded_models
from patient.models import Patient, ClassificationOfDiseases
from survey.models import Survey


class ExportExperiment:

    FILE_NAME = 'experiment.json'

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

    def export_all(self):
        for key, value in experiment_json_files.items():
            self._generate_fixture(key, value)
        for key, value in patient_json_files.items():
            self._generate_fixture(key, value, 'patient.')
        for key, value in json_files_detached_models.items():
            self._generate_detached_fixture(key, value)

        # Generate fixture to keywords of the research project
        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, 'keywords.json'), 'w')
        call_command('dump_object', 'experiment.researchproject_keywords', '--query',
                     '{"researchproject_id__in": ' + str([self.experiment.research_project.id]) + '}')
        sys.stdout = sysout

        fixtures = []
        for filename in {**experiment_json_files, **patient_json_files, **json_files_detached_models}:
            fixtures.append(path.join(self.temp_dir, filename + '.json'))

        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, self.FILE_NAME), 'w')
        call_command('merge_fixtures', *fixtures)
        sys.stdout = sysout

        self._remove_researchproject_keywords_model_from_json(self.FILE_NAME)
        self._change_group_code_to_null_from_json(self.FILE_NAME)
        self._remove_survey_code(self.FILE_NAME)
        self._update_classification_of_diseases_reference(self.FILE_NAME)
        self._remove_auth_user_model_from_json(self.FILE_NAME)

    def get_file_path(self):
        return path.join(self.temp_dir, self.FILE_NAME)


class ImportExperiment:
    BAD_JSON_FILE_ERROR = 1
    FIXTURE_FILE_NAME = 'experiment.json'
    PRE_LOADED_MODELS = pre_loaded_models

    def __init__(self, file_path):
        self.file_path = file_path
        self.temp_dir = tempfile.mkdtemp()
        self.last_objects_before_import = dict()
        self.new_objects = dict()

    def __del__(self):
        shutil.rmtree(self.temp_dir)

    def _set_last_objects_before_import(self, data, research_project_id):
        """Identify last objects to deduct after import, so
        we can identify the new objects imported
        :param data: list created with json.loads from json file with
        the objects that will be imported
        """
        self.last_objects_before_import['experiment'] = Experiment.objects.last()
        if not research_project_id:
            self.last_objects_before_import['research_project'] = ResearchProject.objects.last()
        has_groups = next(
            (index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.group'), None
        )
        has_components = next(
            (index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.component'), None
        )
        if has_groups:
            self.last_objects_before_import['group'] = Group.objects.last()
        if has_components:
            self.last_objects_before_import['component'] = Component.objects.last()

    @staticmethod
    def _include_human_readables(components):
        human_readables = dict(Component.COMPONENT_TYPES)
        for i, component in enumerate(components):
            components[i]['human_readable'] = str(human_readables[component['component_type']])

    def _collect_new_objects(self):
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
            last_group_before_import = self.last_objects_before_import['group'].id
            self.new_objects['groups_count'] = Group.objects.filter(id__gt=last_group_before_import).count()
        else:
            self.new_objects['groups_count'] = None
        if 'component' in self.last_objects_before_import:
            last_component_before_import = self.last_objects_before_import['component'].id
            component_queryset = Component.objects.filter(id__gt=last_component_before_import)
            components = component_queryset.values('component_type').annotate(count=Count('component_type'))
            self._include_human_readables(components)
            self.new_objects['components'] = list(components)

        else:
            self.new_objects['components'] = None

    @staticmethod
    def _update_research_project_pk(data, id_):
        if id_:
            research_project_index = next(
                index for index, dict_ in enumerate(data) if dict_['model'] == 'experiment.researchproject'
            )
            del(data[research_project_index])
            experiment_index = next(
                index for index, dict_ in enumerate(data) if dict_['model'] == 'experiment.experiment'
            )
            data[experiment_index]['fields']['research_project'] = id_

    @staticmethod
    def _verify_keywords(data):
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.keyword']
        next_keyword_id = Keyword.objects.last().id + 1 if Keyword.objects.count() > 0 else 1
        indexes_of_keywords_already_updated = []
        for i in indexes:
            # Get the keyword and check on database if the keyword already exists
            # If exists, update the pk of this keyword to the correspondent in the database
            # otherwise, update the pk of this keyword to next_keyword_id
            old_keyword_id = data[i]['pk']
            old_keyword_string = data[i]['fields']['name']
            keyword_on_database = Keyword.objects.filter(name=old_keyword_string)

            if keyword_on_database.count() > 0:
                data[i]['pk'] = keyword_on_database.first().id
            else:
                data[i]['pk'] = next_keyword_id
                next_keyword_id += 1

            # Update all the references to the old keyword to the new one
            for (index_row, dict_) in enumerate(data):
                if dict_['model'] == 'experiment.researchproject':
                    for (keyword_index, keyword) in enumerate(dict_['fields']['keywords']):
                        if keyword == old_keyword_id and keyword_index not in indexes_of_keywords_already_updated:
                            data[index_row]['fields']['keywords'][keyword_index] = data[i]['pk']
                            indexes_of_keywords_already_updated.append(keyword_index)

    @staticmethod
    def _update_patients_stuff(data):
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'patient.patient']

        # Update patient codes
        # TODO (Refactor): Patient model has function to generate random patient code
        patients = Patient.objects.all()
        if patients:
            last_patient_code = patients.order_by('-code').first().code
            if last_patient_code:
                numerical_part_code = int(last_patient_code.split('P')[1])
                next_numerical_part = numerical_part_code + 1
                for i in indexes:
                    data[i]['fields']['code'] = 'P' + str(next_numerical_part)
                    next_numerical_part += 1

        for i in indexes:
            data[i]['fields']['cpf'] = None

    @staticmethod
    def _update_references_to_user(data, request):
        models_with_user_reference = [
            ('patient.patient', 'changed_by'), ('patient.telephone', 'changed_by'),
            ('patient.medicalrecorddata', 'record_responsible')
        ]
        for model in models_with_user_reference:
            indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] in model[0]]
            for i in indexes:
                data[i]['fields'][model[1]] = request.user.id

    @staticmethod
    def _solve_limey_survey_reference(data, survey_index):
        min_limesurvey_id = Survey.objects.all().order_by('lime_survey_id')[0].lime_survey_id
        if min_limesurvey_id >= 0:
            new_limesurvey_id = -99
        else:
            min_limesurvey_id -= 1
            new_limesurvey_id = min_limesurvey_id
        data[survey_index]['fields']['lime_survey_id'] = new_limesurvey_id

    def _make_dummy_reference_to_limesurvey(self, data):
        survey_indexes = [index for index, dict_ in enumerate(data) if dict_['model'] == 'survey.survey']
        for survey_index in survey_indexes:
            self._solve_limey_survey_reference(data, survey_index)

    @staticmethod
    def _update_survey_stuff(data):
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'survey.survey']

        if indexes:
            # Update survey codes
            next_code = Survey.create_random_survey_code()

            # Update lime survey ids
            min_limesurvey_id = Survey.objects.all().order_by('lime_survey_id')[0].lime_survey_id
            if min_limesurvey_id >= 0:
                new_limesurvey_id = -99
            else:
                new_limesurvey_id = min_limesurvey_id

            for i in indexes:
                data[i]['fields']['code'] = next_code
                next_code = 'Q' + str(int(next_code.split('Q')[1]) + 1)
                new_limesurvey_id -= 1
                data[i]['fields']['lime_survey_id'] = new_limesurvey_id

    def _keep_objects_pre_loaded(self, data):
        for model, dependent_models in self.PRE_LOADED_MODELS.items():
            indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == model[0]]
            app_model = model[0].split('.')
            for i in indexes:
                model_class = apps.get_model(app_model[0], app_model[1])
                instance = model_class
                filter_ = {}
                for field in model[1]:
                    filter_[field] = data[i]['fields'][field]
                instance = instance.objects.filter(**filter_).first()
                if instance:
                    data[i]['pk'], old_id = instance.id, data[i]['pk']
                    for dependent_model in dependent_models:
                        dependent_indexes = [
                            index for (index, dict_) in enumerate(data)
                            if dict_['model'] == dependent_model[0] and dict_['fields'][dependent_model[1]] == old_id
                        ]
                        for dependent_index in dependent_indexes:
                            data[dependent_index]['fields'][dependent_model[1]] = data[i]['pk']

    @staticmethod
    def _verify_classification_of_diseases(data):
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'patient.diagnosis']
        for index in indexes:
            class_of_diseases = ClassificationOfDiseases.objects.filter(
                code=data[index]['fields']['classification_of_diseases'][0]
            ).first()
            if not class_of_diseases:
                ClassificationOfDiseases.objects.create(
                    code=data[index]['fields']['classification_of_diseases'][0],
                    description='(imported, not recognized)',
                    abbreviated_description='(imported, not recognized)'
                )

    def _manage_last_stuffs_before_importing(self, request, data, research_project_id):
        self._make_dummy_reference_to_limesurvey(data)
        self._update_research_project_pk(data, research_project_id)
        self._verify_keywords(data)
        self._update_patients_stuff(data)
        self._update_references_to_user(data, request)
        self._update_survey_stuff(data)
        self._keep_objects_pre_loaded(data)
        self._verify_classification_of_diseases(data)

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

    def _update_pks(self, DG, data, successor, next_id):
        # TODO: see if it's worth to put this list in class level
        if data[successor]['model'] not in one_to_one_relation:
            if not DG.node[successor]['updated']:
                data[successor]['pk'] = next_id

                # Patch for repeated next_id in same models
                model = data[successor]['model']
                updated_ids = [dict_['pk'] for (index, dict_) in enumerate(data) if dict_['model'] == model]
                if next_id in updated_ids:
                    # Prevent from duplicated pks in same model: this is done in the recursive path
                    # TODO: verify better way to update nex_id
                    next_id = max(updated_ids) + 1
                    data[successor]['pk'] = next_id
                DG.node[successor]['updated'] = True
        for predecessor in DG.predecessors(successor):
            if 'relation' in DG[predecessor][successor]:
                relation = DG[predecessor][successor]['relation']
                data[predecessor]['fields'][relation] = data[successor]['pk']
            else:
                data[predecessor]['pk'] = data[successor]['pk']
            next_id += 1
            self._update_pks(DG, data, predecessor, next_id)

    @staticmethod
    def _build_digraph(data):
        dg = nx.DiGraph()
        for index_from, dict_ in enumerate(data):
            if dict_['model'] in foreign_relations:
                node_from = dict_['model']
                nodes_to = foreign_relations[node_from]
                for node_to in nodes_to:
                    index_to = next(
                        (index_foreign for index_foreign, dict_foreign in enumerate(data)
                         if dict_foreign['model'] == node_to[0] and dict_foreign['pk'] == dict_['fields'][node_to[1]]),
                        None
                    )
                    if index_to is not None:
                        dg.add_edge(index_from, index_to)
                        dg[index_from][index_to]['relation'] = node_to[1]
            if dict_['model'] in one_to_one_relation:
                node_from = dict_['model']
                node_to = one_to_one_relation[node_from]
                index_to = next(
                    (index_inheritade for index_inheritade, dict_inheritade in enumerate(data)
                     if dict_inheritade['model'] == node_to and dict_inheritade['pk'] == dict_['pk']),
                    None
                )
                if index_to is not None:
                    dg.add_edge(index_from, index_to)

        for node in dg.nodes():
            dg.node[node]['atributes'] = data[node]
            dg.node[node]['updated'] = False

        return dg

    def _manage_pks(self, dg, data):
        next_id = self._get_first_available_id()
        for model_root_node in model_root_nodes:
            root_nodes = [index for index, dict_ in enumerate(data) if dict_['model'] == model_root_node]
            for root_node in root_nodes:
                self._update_pks(dg, data, root_node, next_id)
                next_id += 1

    def import_all(self, request, research_project_id=None):
        # TODO: maybe this try in constructor
        try:
            with open(self.file_path) as f:
                data = json.load(f)
                # To import log page
                self._set_last_objects_before_import(data, research_project_id)
        except (ValueError, JSONDecodeError):
            return self.BAD_JSON_FILE_ERROR, 'Bad json file. Aborting import experiment.'

        dg = self._build_digraph(data)
        self._manage_pks(dg, data)
        self._manage_last_stuffs_before_importing(request, data, research_project_id)

        with open(path.join(self.temp_dir, self.FIXTURE_FILE_NAME), 'w') as file:
            file.write(json.dumps(data))

        call_command('loaddata', path.join(self.temp_dir, self.FIXTURE_FILE_NAME))

        self._collect_new_objects()

        return 0, ''

    def get_new_objects(self):
        return self.new_objects
