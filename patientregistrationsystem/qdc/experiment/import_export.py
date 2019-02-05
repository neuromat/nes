import shutil
import sys
import tempfile
import json
from json import JSONDecodeError
from os import path

from django.core.management import call_command
from django.apps import apps
from django.db.models import Count

from experiment.models import Group, ComponentConfiguration, ResearchProject, Experiment,\
    Keyword, Component, TaskForTheExperimenter, EEG, EMG, TMS, DigitalGamePhase, GenericDataCollection,\
    Subject, SubjectOfGroup, DataConfigurationTree, Manufacturer, TMSSetting, TMSDevice, CoilShape, \
    CoilModel, Material, Equipment
from patient.models import Patient, SocialHistoryData, SocialDemographicData, Telephone,\
    MedicalRecordData, Diagnosis, ClassificationOfDiseases
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

    def export_all(self):
        key_path = 'component_ptr_id__experiment_id__in'

        # Experiment
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

        # Set up
        self.generate_fixture('tms_device.json', 'tmsdevicesetting', 'tms_setting__experiment_id__in')

        # Generate fixture to keywords of the research project
        sysout = sys.stdout
        sys.stdout = open(path.join(self.temp_dir, 'keywords.json'), 'w')
        call_command('dump_object', 'experiment.researchproject_keywords', '--query',
                     '{"researchproject_id__in": ' + str([self.experiment.research_project.id]) + '}')
        sys.stdout = sysout

        list_of_files = ['experimentfixture.json', 'componentconfiguration.json', 'group.json', 'block.json',
                         'instruction.json', 'pause.json', 'questionnaire.json', 'stimulus.json', 'task.json',
                         'task_experiment.json', 'eeg.json', 'emg.json', 'tms.json', 'digital_game_phase.json',
                         'generic_data_collection.json', 'keywords.json', 'participant.json', 'telephone.json',
                         'socialhistorydata.json', 'socialdemographicdata.json', 'diagnosis.json',
                         'tms_device.json', 'dataconfigurationtree.json']

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

    @staticmethod
    def _get_model_name_by_component_type(component_type):
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

    @staticmethod
    def _update_pk_research_project(data, request=None, research_project_id=None):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.researchproject']

        # Update the pk of the research project either to research_project_id, if given, or
        # the id of a new research project
        if research_project_id:
            data[indexes[0]]['pk'] = int(research_project_id)
        else:
            data[indexes[0]]['pk'] = ResearchProject.objects.last().id + 1\
                if ResearchProject.objects.count() > 0 else 1
            data[indexes[0]]['owner'] = request.user.id

        # Update all the references to the old research project to the new one
        for (index_row, dict_) in enumerate(data):
            if dict_['model'] == 'experiment.experiment':
                data[index_row]['fields']['research_project'] = data[indexes[0]]['pk']

    @staticmethod
    def _update_pk_keywords(data):
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
    def _update_pk_experiment(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.experiment']

        # Update the pk of the experiment to the id of a new experiment
        data[indexes[0]]['pk'] = Experiment.objects.last().id + 1 if Experiment.objects.count() > 0 else 1

        # Update all the references to the old experiment to the new one
        for (index_row, dict_) in enumerate(data):
            if "experiment" in data[index_row]['fields']:
                data[index_row]['fields']['experiment'] = data[indexes[0]]['pk']

    @staticmethod
    def _update_pk_group(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.group']

        next_group_id = Group.objects.last().id + 1 if Group.objects.count() > 0 else 1

        indexes_of_groups_already_updated = []
        for i in indexes:
            old_group_id = data[i]['pk']
            data[i]['pk'] = next_group_id

            for (index_row, dict_) in enumerate(data):
                if 'group' in data[index_row]['fields']\
                        and data[index_row]['fields']['group'] == old_group_id\
                        and index_row not in indexes_of_groups_already_updated:
                    data[index_row]['fields']['group'] = next_group_id
                    indexes_of_groups_already_updated.append(index_row)
            next_group_id += 1

    def _update_pk_component(self, data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.component']

        next_component_id = Component.objects.last().id + 1 if Component.objects.count() > 0 else 1

        # It is needed to create a list of items in the json that were already updated, so we don't update twice the
        # same item of the json
        indexes_of_components_already_updated = []
        indexes_of_componentconfigs_with_component_field_updated = []
        indexes_of_componentconfigs_with_parent_field_updated = []
        for i in indexes:
            # Get the old component id and then update each reference to it in the json file
            old_component_id = data[i]['pk']
            data[i]['pk'] = next_component_id
            component_type = self._get_model_name_by_component_type(data[i]['fields']['component_type'])

            for (index_row, dict_) in enumerate(data):
                # Update the component type item
                if dict_['model'] == 'experiment.' + component_type.lower()\
                        and dict_['pk'] == old_component_id\
                        and index_row not in indexes_of_components_already_updated:
                    data[index_row]['pk'] = next_component_id
                    indexes_of_components_already_updated.append(index_row)

                # Update the component configuration 'component' field for that component
                if dict_['model'] == 'experiment.componentconfiguration'\
                        and dict_['fields']['component'] == old_component_id\
                        and index_row not in indexes_of_componentconfigs_with_component_field_updated:
                    data[index_row]['fields']['component'] = next_component_id
                    indexes_of_componentconfigs_with_component_field_updated.append(index_row)

                # Update the component configuration 'parent' field for that component
                if dict_['model'] == 'experiment.componentconfiguration'\
                        and dict_['fields']['parent'] == old_component_id\
                        and index_row not in indexes_of_componentconfigs_with_parent_field_updated:
                    data[index_row]['fields']['parent'] = next_component_id
                    indexes_of_componentconfigs_with_parent_field_updated.append(index_row)

                # Update the pointer to the experimental protocol (which is a component) in group items of the json
                if dict_['model'] == 'experiment.group'\
                        and dict_['fields']['experimental_protocol'] == old_component_id\
                        and index_row not in indexes_of_components_already_updated:
                    data[index_row]['fields']['experimental_protocol'] = next_component_id
                    indexes_of_components_already_updated.append(index_row)
            next_component_id += 1

    @staticmethod
    def _update_pk_component_configuration(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data)
                   if dict_['model'] == 'experiment.componentconfiguration']

        # Update the pk of each component configuration to the id of new component configurations
        next_component_config_id = ComponentConfiguration.objects.last().id + 1 \
            if ComponentConfiguration.objects.count() > 0 else 1
        for i in indexes:
            old_pk = data[i]['pk']
            data[i]['pk'] = next_component_config_id

            for (index_relation, dict_relation) in enumerate(data):
                if dict_relation['model'] == 'experiment.dataconfigurationtree' and \
                        dict_relation['fields']['component_configuration'] == old_pk:
                    data[index_relation]['fields']['component_configuration'] = data[i]['pk']
            next_component_config_id += 1

    @staticmethod
    def _update_pk_dependent_model(data, model):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == model]

        list_of_dependent_models = ['experiment.eegsetting', 'experiment.emgsetting', 'experiment.tmssetting',
                                    'experiment.informationtype', 'experiment.contexttree', 'experiment.stimulustype']
        list_of_dependent_models_fields = ['eeg_setting', 'emg_setting', 'tms_setting',
                                           'information_type', 'context_tree', 'stimulus_type']

        model_ = apps.get_model(model)
        next_model_id = model_.objects.last().id + 1 if model_.objects.count() > 0 else 1

        # Get field name based on the model name
        field = list_of_dependent_models_fields[list_of_dependent_models.index(model)]

        # Update the pk of each dependent model to the id of new dependent model
        indexes_of_dependent_models_already_updated = []
        for i in indexes:
            old_model_id = data[i]['pk']
            data[i]['pk'] = next_model_id

            # Update each item of the json file that have the corresponding field to
            # the dependent model and point to the old_model_id and has not been
            # already updated
            for (index_row, dict_) in enumerate(data):
                if field in data[index_row]['fields']\
                        and data[index_row]['fields'][field] == old_model_id\
                        and index_row not in indexes_of_dependent_models_already_updated:
                    data[index_row]['fields'][field] = next_model_id
                    indexes_of_dependent_models_already_updated.append(index_row)
            next_model_id += 1

    # BRANCH FROM MANUFACTURER

    @staticmethod
    def _update_pk_manufacturer(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.manufacturer']
        field = 'manufacturer'

        next_manufacturer_id = Manufacturer.objects.last().id + 1 if Manufacturer.objects.count() > 0 else 1

        # Update the pk of each dependent model to the id of new manufacturer model
        indexes_of_dependent_models_already_updated = []
        for i in indexes:
            old_manufacturer_id = data[i]['pk']
            manufacturer_already_in_database = Manufacturer.objects.filter(name=data[i]['fields']['name']).first()

            if not manufacturer_already_in_database:
                data[i]['pk'] = next_manufacturer_id
            else:
                data[i]['pk'] = manufacturer_already_in_database.id

            # Update each item of the json file that have the corresponding field to
            # the dependent model and point to the old_model_id and has not been
            # already updated
            for (index_row, dict_) in enumerate(data):
                if field in data[index_row]['fields'] \
                        and data[index_row]['fields'][field] == old_manufacturer_id \
                        and index_row not in indexes_of_dependent_models_already_updated:
                    data[index_row]['fields'][field] = data[i]['pk']
                    indexes_of_dependent_models_already_updated.append(index_row)
            next_manufacturer_id += 1

    @staticmethod
    def _update_pk_equipment(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.equipment']
        fields = ['equipment_ptr', 'equipment']

        next_equipment_id = Equipment.objects.last().id + 1 if Equipment.objects.count() > 0 else 1

        # Update the pk of each dependent model to the id of new manufacturer model
        indexes_of_dependent_models_already_updated = []
        for i in indexes:
            old_equipment_id = data[i]['pk']
            data[i]['pk'] = next_equipment_id

            # Update each item of the json file that have the corresponding field to
            # the dependent model and point to the old_model_id and has not been
            # already updated
            for (index_row, dict_) in enumerate(data):
                for field in fields:
                    if field in data[index_row]['fields'] \
                            and data[index_row]['fields'][field] == old_equipment_id \
                            and index_row not in indexes_of_dependent_models_already_updated:
                        data[index_row]['fields'][field] = data[i]['pk']
                        indexes_of_dependent_models_already_updated.append(index_row)
            next_equipment_id += 1

    @staticmethod
    def _update_pk_material(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.material']
        fields = ['material', 'insulation_material']

        next_material_id = Material.objects.last().id + 1 if Material.objects.count() > 0 else 1

        # Update the pk of each dependent model to the id of new manufacturer model
        indexes_of_dependent_models_already_updated = []
        for i in indexes:
            old_material_id = data[i]['pk']
            material_already_in_database = \
                Material.objects.filter(name=data[i]['fields']['name'],
                                        description=data[i]['fields']['description']).first()

            if not material_already_in_database:
                data[i]['pk'] = next_material_id
            else:
                data[i]['pk'] = material_already_in_database.id

            # Update each item of the json file that have the corresponding field to
            # the dependent model and point to the old_model_id and has not been
            # already updated
            for (index_row, dict_) in enumerate(data):
                for field in fields:
                    if field in data[index_row]['fields'] \
                            and data[index_row]['fields'][field] == old_material_id \
                            and index_row not in indexes_of_dependent_models_already_updated:
                        data[index_row]['fields'][field] = data[i]['pk']
                        indexes_of_dependent_models_already_updated.append(index_row)
            next_material_id += 1

    # BEGIN OF TMS
    @staticmethod
    def _update_pk_tms_setting(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.tmssetting']
        field = 'tms_setting'

        next_tmssetting_id = TMSSetting.objects.last().id + 1 if TMSSetting.objects.count() > 0 else 1

        # Update the pk of each dependent model to the id of new tms_setting
        indexes_of_dependent_models_already_updated = []
        for i in indexes:
            old_tmssetting_id = data[i]['pk']
            data[i]['pk'] = next_tmssetting_id

            # Update each item of the json file that have the corresponding field to
            # the dependent model and point to the old_model_id and has not been
            # already updated
            for (index_row, dict_) in enumerate(data):
                if field in data[index_row]['fields'] \
                        and data[index_row]['fields'][field] == old_tmssetting_id \
                        and index_row not in indexes_of_dependent_models_already_updated:
                    data[index_row]['fields'][field] = next_tmssetting_id
                    indexes_of_dependent_models_already_updated.append(index_row)
                elif dict_['model'] == 'experiment.tmsdevicesetting' \
                        and data[index_row]['pk'] == old_tmssetting_id:
                    data[index_row]['pk'] = next_tmssetting_id
            next_tmssetting_id += 1

    @staticmethod
    def _update_pk_tms_device(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.tmsdevice']
        field = 'tms_device'

        next_tms_device_id = TMSDevice.objects.last().id + 1 if TMSDevice.objects.count() > 0 else 1

        # Update the pk of each dependent model to the id of new manufacturer model
        indexes_of_dependent_models_already_updated = []
        for i in indexes:
            old_tms_device_id = data[i]['pk']

            data[i]['pk'] = next_tms_device_id

            # Update each item of the json file that have the corresponding field to
            # the dependent model and point to the old_model_id and has not been
            # already updated
            for (index_row, dict_) in enumerate(data):
                if field in data[index_row]['fields'] \
                        and data[index_row]['fields'][field] == old_tms_device_id \
                        and index_row not in indexes_of_dependent_models_already_updated:
                    data[index_row]['fields'][field] = data[i]['pk']
                    indexes_of_dependent_models_already_updated.append(index_row)
            next_tms_device_id += 1

    @staticmethod
    def _update_pk_coil_model(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.coilmodel']
        field = 'coil_model'

        next_coil_model_id = CoilModel.objects.last().id + 1 if CoilModel.objects.count() > 0 else 1

        # Update the pk of each dependent model to the id of new manufacturer model
        indexes_of_dependent_models_already_updated = []
        for i in indexes:
            old_coil_model_id = data[i]['pk']
            data[i]['pk'] = next_coil_model_id

            # Update each item of the json file that have the corresponding field to
            # the dependent model and point to the old_model_id and has not been
            # already updated
            for (index_row, dict_) in enumerate(data):
                if field in data[index_row]['fields'] \
                        and data[index_row]['fields'][field] == old_coil_model_id \
                        and index_row not in indexes_of_dependent_models_already_updated:
                    data[index_row]['fields'][field] = data[i]['pk']
                    indexes_of_dependent_models_already_updated.append(index_row)
            next_coil_model_id += 1

    @staticmethod
    def _update_pk_coil_shape(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.coilshape']
        field = 'coil_shape'

        next_coil_shape_id = CoilShape.objects.last().id + 1 if CoilShape.objects.count() > 0 else 1

        # Update the pk of each dependent model to the id of new manufacturer model
        indexes_of_dependent_models_already_updated = []
        for i in indexes:
            old_coil_shape_id = data[i]['pk']
            # As this model is composed only by a simple name field, it makes sense to not create another one if
            # the same name occours in the table of this model, so if there is one, we point the 'new id' to it
            coil_shape_already_in_database = CoilShape.objects.filter(name_pt_br=data[i]['fields']['name_pt_br'],
                                                                      name_en=data[i]['fields']['name_en'],).first()

            if not coil_shape_already_in_database:
                data[i]['pk'] = next_coil_shape_id
            else:
                data[i]['pk'] = coil_shape_already_in_database.id

            # Update each item of the json file that have the corresponding field to
            # the dependent model and point to the old_model_id and has not been
            # already updated
            for (index_row, dict_) in enumerate(data):
                if field in data[index_row]['fields'] \
                        and data[index_row]['fields'][field] == old_coil_shape_id \
                        and index_row not in indexes_of_dependent_models_already_updated:
                    data[index_row]['fields'][field] = data[i]['pk']
                    indexes_of_dependent_models_already_updated.append(index_row)
            next_coil_shape_id += 1
    # END OF TMS

    @staticmethod
    def _update_pk_survey(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'survey.survey']

        if Survey.objects.count() > 0:
            next_survey_id = Survey.objects.last().id + 1
            new_survey_code = int(Survey.objects.all().order_by('-code').first().code.split('Q')[1]) + 1
            min_limesurvey_id = Survey.objects.all().order_by('lime_survey_id')[0].lime_survey_id
        else:
            next_survey_id = 1
            new_survey_code = 1
            min_limesurvey_id = 1

        # Create a dummy limesurvey reference
        if min_limesurvey_id >= 0:
            new_limesurvey_id = -99
        else:
            new_limesurvey_id = min_limesurvey_id - 1

        indexes_of_surveys_already_updated = []
        for i in indexes:
            old_survey_id = data[i]['pk']
            data[i]['pk'] = next_survey_id
            data[i]['fields']['code'] = 'Q' + str(new_survey_code)
            data[i]['fields']['lime_survey_id'] = new_limesurvey_id

            for (index_row, dict_) in enumerate(data):
                if 'survey' in data[index_row]['fields']\
                        and data[index_row]['fields']['survey'] == old_survey_id \
                        and index_row not in indexes_of_surveys_already_updated:
                    data[index_row]['fields']['survey'] = next_survey_id
                    indexes_of_surveys_already_updated.append(index_row)
            next_survey_id += 1
            new_survey_code += 1
            new_limesurvey_id -= 1

    @staticmethod
    def _update_pk_patient(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'patient.patient']

        next_patient_id = Patient.objects.last().id + 1 if Patient.objects.count() > 0 else 1
        new_patient_code = int(Patient.objects.all().order_by('-code').first().code.split('P')[1]) + 1\
            if Patient.objects.count() > 0 else 1

        indexes_of_patient_already_updated = []
        for i in indexes:
            old_patient_id = data[i]['pk']
            data[i]['pk'] = next_patient_id
            data[i]['fields']['code'] = 'P' + str(new_patient_code)
            # TODO: decide if we clear the CPF or we check and decide if we update the patient
            data[i]['fields']['cpf'] = None

            for (index_row, dict_) in enumerate(data):
                if 'patient' in data[index_row]['fields']\
                        and data[index_row]['fields']['patient'] == old_patient_id \
                        and index_row not in indexes_of_patient_already_updated:
                    data[index_row]['fields']['patient'] = next_patient_id
                    indexes_of_patient_already_updated.append(index_row)
            next_patient_id += 1
            new_patient_code += 1

    @staticmethod
    def _update_pk_subject(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.subject']

        next_subject_id = Subject.objects.last().id + 1 if Subject.objects.count() > 0 else 1

        indexes_of_subjects_already_updated = []
        for i in indexes:
            old_subject_id = data[i]['pk']
            data[i]['pk'] = next_subject_id

            for (index_row, dict_) in enumerate(data):
                if 'subject' in data[index_row]['fields']\
                        and data[index_row]['fields']['subject'] == old_subject_id\
                        and index_row not in indexes_of_subjects_already_updated:
                    data[index_row]['fields']['subject'] = next_subject_id
                    indexes_of_subjects_already_updated.append(index_row)
            next_subject_id += 1

    @staticmethod
    def _update_pk_subject_of_group(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.subjectofgroup']

        next_subject_of_group_id = SubjectOfGroup.objects.last().id + 1 if SubjectOfGroup.objects.count() > 0 else 1

        for i in indexes:
            data[i]['pk'] = next_subject_of_group_id
            next_subject_of_group_id += 1

    @staticmethod
    def _update_pk_social_history_data(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'patient.socialhistorydata']

        next_social_history_data_id = SocialHistoryData.objects.last().id + 1\
            if SocialHistoryData.objects.count() > 0 else 1

        for i in indexes:
            data[i]['pk'] = next_social_history_data_id
            next_social_history_data_id += 1

    @staticmethod
    def _update_pk_telephone(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'patient.telephone']

        next_telephone_id = Telephone.objects.last().id + 1\
            if Telephone.objects.count() > 0 else 1

        for i in indexes:
            data[i]['pk'] = next_telephone_id
            next_telephone_id += 1

    @staticmethod
    def _update_pk_social_demographic_data(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'patient.socialdemographicdata']

        next_social_demographic_data_id = SocialDemographicData.objects.last().id + 1\
            if SocialDemographicData.objects.count() > 0 else 1

        for i in indexes:
            data[i]['pk'] = next_social_demographic_data_id
            next_social_demographic_data_id += 1

    @staticmethod
    def _update_pk_diagnosis(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'patient.diagnosis']

        next_diagnosis_id = Diagnosis.objects.last().id + 1\
            if Diagnosis.objects.count() > 0 else 1

        for i in indexes:
            data[i]['pk'] = next_diagnosis_id
            next_diagnosis_id += 1

    @staticmethod
    def _update_pk_classification_of_diseases(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'patient.classificationofdiseases']

        next_classification_of_diseases_id = ClassificationOfDiseases.objects.last().id + 1\
            if ClassificationOfDiseases.objects.count() > 0 else 1

        indexes_of_classifications_of_diseases_already_updated = []
        for i in indexes:
            old_classification_of_diseases_id = data[i]['pk']
            cid10 = ClassificationOfDiseases.objects.filter(code=data[i]['fields']['code']).first()

            if cid10:
                data[i]['pk'] = cid10.id
            else:
                data[i]['pk'] = next_classification_of_diseases_id
                next_classification_of_diseases_id += 1

            for (index_row, dict_) in enumerate(data):
                if dict_['model'] == 'patient.diagnosis'\
                        and dict_['fields']['classification_of_diseases'] == old_classification_of_diseases_id\
                        and index_row not in indexes_of_classifications_of_diseases_already_updated:
                    data[index_row]['fields']['classification_of_diseases'] = data[i]['pk']
                    indexes_of_classifications_of_diseases_already_updated.append(index_row)

    @staticmethod
    def _update_pk_medical_record_data(data):
        # Which elements of the json file ("data") represent this model
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'patient.medicalrecorddata']

        next_medical_record_data_id = MedicalRecordData.objects.last().id + 1\
            if MedicalRecordData.objects.count() > 0 else 1

        for i in indexes:
            old_medical_record_data_id = data[i]['pk']
            data[i]['pk'] = next_medical_record_data_id

            for (index_row, dict_) in enumerate(data):
                if dict_['model'] == 'patient.diagnosis'\
                        and dict_['fields']['medical_record_data'] == old_medical_record_data_id:
                    data[index_row]['fields']['medical_record_data'] = next_medical_record_data_id
            next_medical_record_data_id += 1

    def _update_pk_dataconfiguration_tree(self, data):
        indexes = [index for (index, dict_) in enumerate(data) if dict_['model'] == 'experiment.dataconfigurationtree']

        next_data_con_tree = DataConfigurationTree.objects.last().id + 1 \
            if DataConfigurationTree.objects.count() > 0 else 1

        for i in indexes:
            data[i]['pk'] = next_data_con_tree
            next_data_con_tree += 1

    def _update_pks(self, data, request, research_project_id=None):
        self._update_pk_research_project(data, request, research_project_id)
        self._update_pk_keywords(data)
        self._update_pk_experiment(data)
        self._update_pk_dependent_model(data, 'experiment.eegsetting')
        self._update_pk_dependent_model(data, 'experiment.emgsetting')

        # Update TMS
        self._update_pk_tms_setting(data)
        self._update_pk_tms_device(data)
        self._update_pk_coil_model(data)
        self._update_pk_coil_shape(data)

        self._update_pk_equipment(data)
        self._update_pk_material(data)
        self._update_pk_manufacturer(data)
        self._update_pk_dependent_model(data, 'experiment.informationtype')
        self._update_pk_dependent_model(data, 'experiment.contexttree')
        self._update_pk_dependent_model(data, 'experiment.stimulustype')
        self._update_pk_survey(data)
        self._update_pk_component(data)
        self._update_pk_component_configuration(data)
        self._update_pk_patient(data)
        self._update_pk_subject(data)
        self._update_pk_subject_of_group(data)
        self._update_pk_group(data)
        self._update_pk_social_history_data(data)
        self._update_pk_social_demographic_data(data)
        self._update_pk_telephone(data)
        self._update_pk_diagnosis(data)
        self._update_pk_medical_record_data(data)
        self._update_pk_classification_of_diseases(data)
        self._update_pk_dataconfiguration_tree(data)

    def import_all(self, request, research_project_id=None):
        # TODO: maybe this try in constructor
        try:
            with open(self.file_path) as f:
                data = json.load(f)
                self._set_last_objects_before_import(data, research_project_id)  # to import log page
        except (ValueError, JSONDecodeError):
            return self.BAD_JSON_FILE_ERROR, 'Bad json file. Aborting import experiment.'

        self._update_pks(data, request, research_project_id)
        with open(path.join(self.temp_dir, self.FIXTURE_FILE_NAME), 'w') as file:
            file.write(json.dumps(data))

        call_command('loaddata', path.join(self.temp_dir, self.FIXTURE_FILE_NAME))

        self._collect_new_objects()

        return 0, ''

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
            if self.last_objects_before_import['group']:
                last_group_before_import = self.last_objects_before_import['group'].id
                self.new_objects['groups_count'] = Group.objects.filter(id__gt=last_group_before_import).count()
            else:
                self.new_objects['groups_count'] = Group.objects.count()
        else:
            self.new_objects['groups_count'] = None
        if 'component' in self.last_objects_before_import:
            if self.last_objects_before_import['component']:
                last_component_before_import = self.last_objects_before_import['component'].id
                component_queryset = Component.objects.filter(id__gt=last_component_before_import)
            else:
                component_queryset = Component.objects.all()
            components = component_queryset.values('component_type').annotate(count=Count('component_type'))
            self._include_human_readables(components)
            self.new_objects['components'] = list(components)
        else:
            self.new_objects['components'] = None

    def get_new_objects(self):
        return self.new_objects

    @staticmethod
    def _include_human_readables(components):
        human_readables = dict(Component.COMPONENT_TYPES)
        for i, component in enumerate(components):
            components[i]['human_readable'] = str(human_readables[component['component_type']])
