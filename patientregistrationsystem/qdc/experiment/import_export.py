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
    Keyword, Component, Manufacturer, Material
from patient.models import Patient, ClassificationOfDiseases
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

    def generate_patient_fixture(self, filename, element, key_path):
        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, filename), 'w')
        call_command('dump_object', 'patient.' + element, '--query',
                     '{"' + key_path + '": ' + str([self.experiment.id]) + '}'
                     )
        sys.stdout = sysout

    def generate_detached_fixture(self, filename, element, key_path, parent_model, filename_parent):
        with open(path.join(self.temp_dir, filename_parent)) as file:
            data = json.load(file)
        parent_ids = [dict_['pk'] for index, dict_ in enumerate(data) if dict_['model'] == parent_model]

        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, filename), 'w')
        call_command('dump_object', 'experiment.' + element, '--query', '{"' + key_path + '": ' + str(parent_ids) + '}')
        sys.stdout = sysout

    def _remove_auth_user_model_from_json(self, filename):
        with open(path.join(self.temp_dir, filename)) as f:
            data = f.read().replace('\n', '')

        deserialized = json.loads(data)
        key = next((index for (index, d) in enumerate(deserialized) if d['model'] == 'auth.user'), None)
        del (deserialized[key])

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
        for i in indexes:
            pk = serialized[i]['fields']['classification_of_diseases']
            code = ClassificationOfDiseases.objects.get(id=int(pk)).code
            # make a list with one element as natural key in dumped data has to be a list
            serialized[i]['fields']['classification_of_diseases'] = [code]

        # Remove ClassificationOfDiseases items: these data are preloaded in database
        i = True
        while i:
            i = next(
                (index for (index, dict_) in enumerate(serialized) if dict_['model'] ==
                 'patient.classificationofdiseases'), None)
            if i is None:
                break
            del serialized[i]

        with open(path.join(self.temp_dir, filename), 'w') as f:
            f.write(json.dumps(serialized))

    def export_all(self):
        key_path = 'component_ptr_id__experiment_id__in'

        self.generate_fixture('experimentfixture.json', 'experiment', 'id__in')
        self.generate_fixture('componentconfiguration.json', 'componentconfiguration',
                              'component_id__experiment_id__in')
        self.generate_fixture('dataconfigurationtree.json', 'dataconfigurationtree',
                              'component_configuration__component__experiment_id__in')
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
        self.generate_fixture('participant.json', 'subjectofgroup', 'group_id__experiment_id__in')

        # Patient
        self.generate_patient_fixture('telephone.json', 'telephone',
                                      'patient__subject__subjectofgroup__group__experiment_id__in')
        self.generate_patient_fixture('socialhistorydata.json', 'socialhistorydata',
                                      'patient__subject__subjectofgroup__group__experiment_id__in')
        self.generate_patient_fixture('socialdemographicdata.json', 'socialdemographicdata',
                                      'patient__subject__subjectofgroup__group__experiment_id__in')
        self.generate_patient_fixture('diagnosis.json', 'diagnosis',
                                      'medical_record_data__patient__subject__subjectofgroup__group__experiment_id__in')

        # TMS
        self.generate_fixture('tms_device.json', 'tmsdevicesetting', 'tms_setting__experiment_id__in')
        self.generate_fixture('tms_setting.json', 'tmssetting', 'experiment_id__in')

        # EEG
        self.generate_fixture('eeg_amplifier_setting.json', 'eegamplifiersetting', 'eeg_setting__experiment_id__in')
        self.generate_fixture('eeg_solution_setting.json', 'eegsolutionsetting', 'eeg_setting__experiment_id__in')
        self.generate_fixture('eeg_filter_setting.json', 'eegfiltersetting', 'eeg_setting__experiment_id__in')
        self.generate_fixture('eeg_electrode_layout_setting.json', 'eegelectrodelayoutsetting',
                              'eeg_setting__experiment_id__in')
        self.generate_fixture('eeg_electrode_position_setting.json', 'eegelectrodepositionsetting',
                              'eeg_electrode_layout_setting__eeg_setting__experiment_id__in')
        self.generate_fixture('eeg_setting.json', 'eegsetting', 'experiment_id__in')

        # EMG
        self.generate_fixture('emg_setting.json', 'emgsetting', 'experiment_id__in')
        self.generate_fixture('emg_ad_converter_setting.json', 'emgadconvertersetting',
                              'emg_setting__experiment_id__in')
        self.generate_fixture('emg_digital_filter_setting.json', 'emgdigitalfiltersetting',
                              'emg_setting__experiment_id__in')
        self.generate_fixture('emg_pre_amplifier_filter_setting.json', 'emgpreamplifierfiltersetting',
                              'emg_preamplifier_filter_setting__emg_electrode_setting__emg_setting__experiment_id__in')
        self.generate_fixture('emg_amplifier_analog_filter_setting.json','emganalogfiltersetting',
                              'emg_electrode_setting__emg_electrode_setting__emg_setting__experiment_id__in')
        self.generate_fixture('emg_electrodeplacementsetting.json', 'emgelectrodeplacementsetting',
                              'emg_electrode_setting__emg_setting__experiment_id__in')
        self.generate_detached_fixture(
            'emg_intramuscularplacement.json', 'emgintramuscularplacement', 'emgelectrodeplacement_ptr__in',
            'experiment.emgelectrodeplacement', 'emg_electrodeplacementsetting.json'
        )
        self.generate_detached_fixture(
            'emg_surfaceplacement.json', 'emgsurfaceplacement', 'emgelectrodeplacement_ptr__in',
            'experiment.emgelectrodeplacement', 'emg_electrodeplacementsetting.json'
        )
        self.generate_detached_fixture(
            'emg_needleplacement.json', 'emgneedleplacement', 'emgelectrodeplacement_ptr__in',
            'experiment.emgelectrodeplacement', 'emg_electrodeplacementsetting.json'
        )

        # Generate fixture to keywords of the research project
        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, 'keywords.json'), 'w')
        call_command('dump_object', 'experiment.researchproject_keywords', '--query',
                     '{"researchproject_id__in": ' + str([self.experiment.research_project.id]) + '}')
        sys.stdout = sysout

        # TODO: refactor to use this list with generate_fixture
        list_of_files = ['experimentfixture.json', 'componentconfiguration.json', 'group.json', 'block.json',
                         'instruction.json', 'pause.json', 'questionnaire.json', 'stimulus.json', 'task.json',
                         'task_experiment.json', 'eeg.json', 'emg.json', 'tms.json', 'digital_game_phase.json',
                         'generic_data_collection.json', 'keywords.json', 'participant.json', 'telephone.json',
                         'socialhistorydata.json', 'socialdemographicdata.json', 'dataconfigurationtree.json',
                         'diagnosis.json', 'tms_device.json', 'tms_setting.json', 'eeg_amplifier_setting.json',
                         'eeg_solution_setting.json', 'eeg_filter_setting.json', 'eeg_electrode_layout_setting.json',
                         'eeg_electrode_position_setting.json', 'eeg_setting.json', 'emg_setting.json',
                         'emg_ad_converter_setting.json', 'emg_digital_filter_setting.json',
                         'emg_pre_amplifier_filter_setting.json', 'emg_amplifier_analog_filter_setting.json',
                         'emg_electrodeplacementsetting.json', 'emg_intramuscularplacement.json',
                         'emg_surfaceplacement.json', 'emg_needleplacement.json']

        fixtures = []
        for filename in list_of_files:
            fixtures.append(path.join(self.temp_dir, filename))

        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, self.FILE_NAME), 'w')
        call_command('merge_fixtures', *fixtures)
        sys.stdout = sysout

        self._remove_auth_user_model_from_json(self.FILE_NAME)
        self._remove_researchproject_keywords_model_from_json(self.FILE_NAME)
        self._change_group_code_to_null_from_json(self.FILE_NAME)
        self._remove_survey_code(self.FILE_NAME)
        self._update_classification_of_diseases_reference(self.FILE_NAME)

    def get_file_path(self):
        return path.join(self.temp_dir, self.FILE_NAME)


class ImportExperiment:
    BAD_JSON_FILE_ERROR = 1
    FIXTURE_FILE_NAME = 'experiment.json'

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
    def _update_pk_keywords(data):  # TODO: to be used when updating pks
        # Which elements of the json file ("data") represent this model
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

        # Clear CPFs
        for i in indexes:
            data[i]['fields']['cpf'] = None

    @staticmethod
    def _update_model_user(data, request):
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'patient.telephone']
        for i in indexes:
            data[i]['fields']['changed_by'] = request.user.id

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
                new_limesurvey_id = 1

            for i in indexes:
                data[i]['fields']['code'] = next_code
                next_code = 'Q' + str(int(next_code.split('Q')[1]) + 1)
                data[i]['fields']['lime_survey_id'] = new_limesurvey_id
                new_limesurvey_id -= 1

    @staticmethod
    def _keep_manufacturer(data):
        dependent_models = [
            ('experiment.equipment', 'manufacturer'), ('experiment.eegsolution', 'manufacturer'),
            ('experiment.software', 'manufacturer')
        ]
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] in 'experiment.manufacturer']

        for i in indexes:
            # TODO: when and if change Manufacturer model name field to unique
            #  change to 'objects.get'
            instance = Manufacturer.objects.filter(name=data[i]['fields']['name']).first()
            if instance:
                data[i]['pk'], old_id = instance.id, data[i]['pk']
                for model in dependent_models:
                    dependent_indexes = [
                        index for (index, dict_) in enumerate(data)
                        if dict_['model'] == model[0] and dict_['fields'][model[1]] == old_id
                    ]
                    for dependent_index in dependent_indexes:
                        data[dependent_index]['fields'][model[1]] = data[i]['pk']

    @staticmethod
    def _keep_material(data):
        dependent_models = [
            ('experiment.electrodemodel', 'material'), ('experiment.intramuscularelectrode', 'insulation_material'),
            ('experiment.eegelectrodecap', 'material'), ('experiment.coilmodel', 'material')
        ]
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] in 'experiment.material']

        for i in indexes:
            instance = Material.objects.filter(
                name=data[i]['fields']['name'], description=data[i]['fields']['description']
            ).first()
            if instance:
                data[i]['pk'], old_id = instance.id, data[i]['pk']
                for model in dependent_models:
                    dependent_indexes = [
                        index for (index, dict_) in enumerate(data)
                        if dict_['model'] == model[0] and dict_['fields'][model[1]] == old_id
                    ]
                    for dependent_index in dependent_indexes:
                        data[dependent_index]['fields'][model[1]] = data[i]['pk']

    def _keep_objects_pre_loaded(self, data):
        self._keep_manufacturer(data)
        self._keep_material(data)

    def _manage_last_stuffs_before_importing(self, request, data, research_project_id):
        self._make_dummy_reference_to_limesurvey(data)
        self._update_research_project_pk(data, research_project_id)
        self._verify_keywords(data)
        self._update_patients_stuff(data)
        self._update_model_user(data, request)
        self._update_survey_stuff(data)
        self._keep_objects_pre_loaded(data)

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
        if data[successor]['model'] not in [
            'experiment.block', 'experiment.instruction', 'experiment.questionnaire',
            'experiment.tms', 'experiment.eeg', 'experiment.emg', 'experiment.tmsdevicesetting',
            'experiment.tmsdevice', 'experiment.eegelectrodelayoutsetting', 'experiment.eegelectrodenet',
            'experiment.eegfiltersetting', 'experiment.eegamplifiersetting', 'experiment.amplifier',
            'experiment.eegsolutionsetting', 'experiment.adconverter', 'experiment.emgadconvertersetting',
            'experiment.emgdigitalfiltersetting', 'experiment.emgelectrodeplacementsetting',
            'experiment.emgamplifiersetting', 'experiment.emganalogfiltersetting',
            'experiment.emgpreamplifiersetting', 'experiment.emgpreamplifierfiltersetting',
            'experiment.digitalgamephase', 'experiment.pause',
            'experiment.eegsolutionsetting', 'experiment.emgelectrodeplacementsetting',
            'experiment.emgintramuscularplacement', 'experiment.emgsurfaceplacement', 'experiment.emgneedleplacement'
        ]:
            if not DG.node[successor]['updated']:
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

    def _build_graph(self, request, data, research_project_id):
        model_root_nodes = [
            'experiment.researchproject', 'experiment.manufacturer', 'survey.survey', 'experiment.coilshape',
            'experiment.material', 'experiment.electrodeconfiguration', 'experiment.eegelectrodelocalizationsystem',
            'experiment.filtertype', 'experiment.amplifierdetectiontype', 'experiment.tetheringsystem',
            'experiment.muscle', 'experiment.standardizationsystem',
            'patient.patient'
        ]
        foreign_relations = {
            'experiment.researchproject': [['', '']],
            'experiment.experiment': [['experiment.researchproject', 'research_project']],
            'experiment.group': [
                ['experiment.experiment', 'experiment'], ['experiment.component', 'experimental_protocol']
            ],
            'experiment.component': [['experiment.experiment', 'experiment']],
            'experiment.componentconfiguration': [
                ['experiment.component', 'component'], ['experiment.component', 'parent']
            ],
            'experiment.questionnaire': [['survey.survey', 'survey']],
            'survey.survey': [['', '']],

            'experiment.digitalgamephase': [
                ['experiment.contexttree', 'context_tree'],
                ['experiment.softwareversion', 'software_version']
            ],
            'experiment.contexttree': [['experiment.experiment', 'experiment']],
            # TMS
            'experiment.tms': [['experiment.tmssetting', 'tms_setting']],
            'experiment.tmssetting': [['experiment.experiment', 'experiment']],
            'experiment.tmsdevicesetting': [
                ['experiment.coilmodel', 'coil_model'], ['experiment.tmsdevice', 'tms_device']
            ],
            'experiment.coilmodel': [['experiment.coilshape', 'coil_shape'], ['experiment.material', 'material']],
            'experiment.coilshape': [['', '']],
            'experiment.material': [['', '']],
            # EEG
            'experiment.eeg': [['experiment.eegsetting', 'eeg_setting']],
            'experiment.eegsetting': [['experiment.experiment', 'experiment']],
            'experiment.eegelectrodepositionsetting': [
                ['experiment.electrodemodel', 'electrode_model'],
                ['experiment.eegelectrodelayoutsetting', 'eeg_electrode_layout_setting'],
                ['experiment.eegelectrodeposition', 'eeg_electrode_position']
            ],
            'experiment.eegelectrodelayoutsetting': [['experiment.eegelectrodenetsystem', 'eeg_electrode_net_system']],
            'experiment.eegelectrodeposition': [
                ['experiment.eegelectrodelocalizationsystem', 'eeg_electrode_localization_system']
            ],
            'experiment.eegelectrodenetsystem': [
                ['experiment.eegelectrodelocalizationsystem', 'eeg_electrode_localization_system'],
                ['experiment.eegelectrodenet', 'eeg_electrode_net']
            ],
            'experiment.eegelectrodenet': [['experiment.electrodemodel', 'electrode_model_default']],
            'experiment.eegfiltersetting': [['experiment.filtertype', 'eeg_filter_type']],
            'experiment.eegamplifiersetting': [['experiment.amplifier', 'eeg_amplifier']],
            'experiment.amplifier': [
                ['experiment.amplifierdetectiontype', 'amplifier_detection_type'],
                ['experiment.tetheringsystem', 'tethering_system']
            ],
            'experiment.eegsolutionsetting': [['experiment.eegsolution', 'eeg_solution']],
            'experiment.eegsolution': [['experiment.manufacturer', 'manufacturer']],
            # EMG
            'experiment.emg': [['experiment.emgsetting', 'emg_setting']],
            'experiment.emgsetting': [
                ['experiment.experiment', 'experiment'], ['experiment.softwareversion', 'acquisition_software_version'],
            ],
            'experiment.muscle': [['', '']],
            'experiment.standardizationsystem': [['', '']],
            'experiment.muscleside': [['experiment.muscle', 'muscle']],
            'experiment.musclesubdivision': [['experiment.muscle', 'muscle']],
            'experiment.emgelectrodeplacement': [
                ['experiment.musclesubdivision', 'muscle_subdivision'],
                ['experiment.standardizationsystem', 'standardization_system']
            ],
            'experiment.emgelectrodesetting': [
                ['experiment.emgsetting', 'emg_setting'], ['experiment.electrodemodel', 'electrode']
            ],
            'experiment.emgpreamplifiersetting': [['experiment.amplifier', 'amplifier']],
            'experiment.emgelectrodeplacementsetting': [
                ['experiment.muscleside', 'muscle_side'],
                ['experiment.emgelectrodeplacement', 'emg_electrode_placement']
            ],
            'experiment.softwareversion': [['experiment.software', 'software']],
            'experiment.software': [['experiment.manufacturer', 'manufacturer']],
            'experiment.manufacturer': [['', '']],
            'experiment.equipment': [['experiment.manufacturer', 'manufacturer']],
            'experiment.electrodemodel': [
                ['experiment.material', 'material'], ['experiment.electrodeconfiguration', 'electrode_configuration']],

            'experiment.emgadconvertersetting': [['experiment.adconverter', 'ad_converter']],
            'experiment.emgdigitalfiltersetting': [['experiment.filtertype', 'filter_type']],
            'experiment.filtertype': [['', '']],

            'experiment.tetheringsystem': [['','']],
            'experiment.amplifierdetectiontype': [['', '']],
            'experiment.emgamplifiersetting': [['experiment.amplifier', 'amplifier']],

            # Participants
            'experiment.subject': [['patient.patient', 'patient']],
            'experiment.subjectofgroup': [['experiment.subject', 'subject'], ['experiment.group', 'group']],
            'patient.patient': [['', '']],
            'patient.telephone': [['patient.patient', 'patient']],
            'patient.socialdemographicdata': [['patient.patient', 'patient']],
            'patient.socialhistorydata': [['patient.patient', 'patient']],
            'patient.medicalrecorddata': [['patient.patient', 'patient']],
            'patient.diagnosis': [
                ['patient.medicalrecorddata', 'medical_record_data'],
            ],
            # Data collections
            'experiment.dataconfigurationtree': [['experiment.componentconfiguration', 'component_configuration']]
        }
        one_to_one_relation = {
            # Multi table inheritance
            'experiment.block': 'experiment.component',
            'experiment.instruction': 'experiment.component',
            'experiment.pause': 'experiment.component',
            'experiment.questionnaire': 'experiment.component',
            'experiment.stimulus': 'experiment.component',
            'experiment.task': 'experiment.component',
            'experiment.task_experiment': 'experiment.component',
            'experiment.eeg': 'experiment.component',
            'experiment.tms': 'experiment.component',
            'experiment.emg': 'experiment.component',
            'experiment.digitalgamephase': 'experiment.component',
            'experiment.genericdatacollection': 'experiment.component',
            'experiment.tmsdevice': 'experiment.equipment',
            'experiment.eegelectrodenet': 'experiment.equipment',
            'experiment.amplifier': 'experiment.equipment',
            'experiment.emgintramuscularplacement': 'experiment.emgelectrodeplacement',
            'experiment.emgsurfaceplacement': 'experiment.emgelectrodeplacement',
            'experiment.emgneedleplacement': 'experiment.emgelectrodeplacement',
            'experiment.adconverter': 'experiment.equipment',
            # OneToOneField
            'experiment.tmsdevicesetting': 'experiment.tmssetting',
            'experiment.eegelectrodelayoutsetting': 'experiment.eegsetting',
            'experiment.eegfiltersetting': 'experiment.eegsetting',
            'experiment.eegamplifiersetting': 'experiment.eegsetting',
            'experiment.eegsolutionsetting': 'experiment.eegsetting',
            'experiment.emgadconvertersetting': 'experiment.emgsetting',
            'experiment.emgdigitalfiltersetting': 'experiment.emgsetting',
            'experiment.emgamplifiersetting': 'experiment.emgelectrodesetting',
            'experiment.emganalogfiltersetting': 'experiment.emgamplifiersetting',
            'experiment.emgpreamplifiersetting': 'experiment.emgelectrodesetting',
            'experiment.emgpreamplifierfiltersetting': 'experiment.emgpreamplifiersetting',
            'experiment.emgelectrodeplacementsetting': 'experiment.emgelectrodesetting',
        }

        DG = nx.DiGraph()
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
                        DG.add_edge(index_from, index_to)
                        DG[index_from][index_to]['relation'] = node_to[1]
            if dict_['model'] in one_to_one_relation:
                node_from = dict_['model']
                node_to = one_to_one_relation[node_from]
                index_to = next(
                    (index_inheritade for index_inheritade, dict_inheritade in enumerate(data)
                     if dict_inheritade['model'] == node_to and dict_inheritade['pk'] == dict_['pk']),
                    None
                )
                if index_to is not None:
                    DG.add_edge(index_from, index_to)

        for node in DG.nodes():
            DG.node[node]['atributes'] = data[node]
            DG.node[node]['updated'] = False

        next_id = self._get_first_available_id()
        for model_root_node in model_root_nodes:
            root_nodes = [index for index, dict_ in enumerate(data) if dict_['model'] == model_root_node]
            for root_node in root_nodes:
                self._update_pks(DG, data, root_node, next_id)
                next_id += 1

        self._manage_last_stuffs_before_importing(request, data, research_project_id)

    def import_all(self, request, research_project_id=None):
        # TODO: maybe this try in constructor
        try:
            with open(self.file_path) as f:
                data = json.load(f)
                # To import log page
                self._set_last_objects_before_import(data, research_project_id)
        except (ValueError, JSONDecodeError):
            return self.BAD_JSON_FILE_ERROR, 'Bad json file. Aborting import experiment.'

        self._build_graph(request, data, research_project_id)
        with open(path.join(self.temp_dir, self.FIXTURE_FILE_NAME), 'w') as file:
            file.write(json.dumps(data))

        call_command('loaddata', path.join(self.temp_dir, self.FIXTURE_FILE_NAME))

        self._collect_new_objects()

        return 0, ''

    def get_new_objects(self):
        return self.new_objects
