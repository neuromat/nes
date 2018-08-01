# coding=utf-8
import datetime
import random

from django.db import IntegrityError
from django.db.models.loading import get_model
from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from faker import Factory

from experiment.models import Experiment, Group, Subject, \
    QuestionnaireResponse, SubjectOfGroup, ComponentConfiguration, \
    ResearchProject, Keyword, StimulusType, \
    Component, Task, TaskForTheExperimenter, Stimulus, Instruction, Pause, \
    Questionnaire, Block, \
    EEG, FileFormat, EEGData, EEGSetting, DataConfigurationTree, EMG, \
    Manufacturer, Tag, Amplifier, \
    EEGSolution, FilterType, ElectrodeModel, EEGElectrodeNet, \
    EEGElectrodeNetSystem, EEGElectrodeLocalizationSystem, \
    EEGElectrodePosition, Material, EMGSetting, Software, SoftwareVersion, \
    ADConverter, EMGElectrodeSetting, \
    StandardizationSystem, MuscleSubdivision, Muscle, MuscleSide, \
    EMGElectrodePlacement, EMGElectrodePlacementSetting, \
    EEGElectrodeCap, EEGCapSize, TMSDevice, CoilModel, CoilShape, Publication, \
    ContextTree, ExperimentResearcher

from .views import experiment_update, upload_file, research_project_update, publication_update, context_tree_update, \
    publication_add_experiment

from custom_user.views import User

from patient.models import ClassificationOfDiseases
from patient.tests import UtilTests

from survey.models import Survey
from survey.abc_search_engine import Questionnaires


LIME_SURVEY_ID = 828636
LIME_SURVEY_ID_WITHOUT_ACCESS_CODE_TABLE = 563235
LIME_SURVEY_ID_INACTIVE = 846317
LIME_SURVEY_ID_WITHOUT_IDENTIFICATION_GROUP = 913841
LIME_SURVEY_TOKEN_ID_1 = 1

CLASSIFICATION_OF_DISEASES_CREATE = 'classification_of_diseases_insert'
CLASSIFICATION_OF_DISEASES_DELETE = 'classification_of_diseases_remove'
EXPERIMENT_NEW = 'experiment_new'

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'

SEARCH_TEXT = 'search_text'
SUBJECT_SEARCH = 'subject_search'


class ObjectsFactory(object):

    @staticmethod
    def create_research_project(owner=None):
        """
        Create a research project to be used in the test
        :return: research project
        """
        research_project = ResearchProject.objects.create(
            title="Research project title",
            description="Research project description",
            start_date=datetime.date.today(),
            owner=owner
        )
        research_project.save()
        return research_project

    @staticmethod
    def create_experiment(research_project):
        """
        Create an experiment to be used in the test
        :param research_project: research project
        :return: experiment
        """
        experiment = Experiment.objects.create(
            research_project_id=research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update"
        )
        experiment.changed_by = None
        experiment.save()
        return experiment

    @staticmethod
    def create_experiment_researcher(experiment):
        """
        Create an experiment researcher to be used in tests
        :param experiment: researcher's experiment
        :return: ExperimentResearcher model instance
        """
        user = User.objects.create_user(
            username='toninho', email='toninho@example.com', password='toninho'
        )
        return ExperimentResearcher.objects.create(
            experiment=experiment, researcher=user
        )


    @staticmethod
    def create_publication(list_of_experiments):
        """
        Create a publication to be used in the test
        :param list_of_experiments: list of experiments
        :return: publication
        """

        publication = Publication.objects.create(title="Publication-Update",
                                                 citation="Citation-Update")
        publication.save()
        for experiment in list_of_experiments:
            publication.experiments.add(experiment)
        return publication

    @staticmethod
    def create_context_tree(experiment):
        """
        Create a context tree for an experiment
        :param experiment: experiment
        :return: new context tree
        """

        context_tree = ContextTree.objects.create(
            experiment=experiment, name="Context tree name", description="Context tree description")
        context_tree.save()
        return context_tree

    @staticmethod
    def create_eeg_setting(experiment):
        eeg_setting = EEGSetting.objects.create(experiment=experiment,
                                                name='EEG-Setting name',
                                                description='EEG-Setting description')
        # eeg_setting.save()
        return eeg_setting

    @staticmethod
    def create_emg_setting(experiment, acquisition_software_version):
        emg_setting = EMGSetting.objects.create(experiment=experiment,
                                                name='EMG-Setting name',
                                                description='EMG-Setting description',
                                                acquisition_software_version=acquisition_software_version,)
        emg_setting.save()
        return emg_setting

    @staticmethod
    def create_emg_electrode_setting(emg_setting, electrode_model):
        emg_electrode_setting = EMGElectrodeSetting.objects.create(emg_setting=emg_setting, electrode=electrode_model)

        emg_electrode_setting.save()
        return emg_electrode_setting

    @staticmethod
    def create_emg_electrode_placement_setting(emg_electrode_setting, electrode_placement, muscle_side):
        emg_electrode_placement_setting = EMGElectrodePlacementSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting,
            emg_electrode_placement=electrode_placement,
            muscle_side=muscle_side,
            remarks="Remarks electrode placement setting")

        emg_electrode_placement_setting.save()
        return emg_electrode_placement_setting

    @staticmethod
    def create_standardization_system():
        standardization_system = StandardizationSystem.objects.create(
            name='Standardization System identification',
            description='Standardization System description'
        )
        standardization_system.save()
        return standardization_system

    @staticmethod
    def create_muscle():
        muscle = Muscle.objects.create(
            name='Muscle identification'
        )
        muscle.save()
        return muscle

    @staticmethod
    def create_muscle_subdivision(muscle):
        muscle_subdivision = MuscleSubdivision.objects.create(
            name='Muscle subdivision identification',
            anatomy_origin='Anatomy origin description',
            anatomy_insertion='Anatomy insertion description',
            anatomy_function='Anatomy function description',
            muscle=muscle
        )
        muscle_subdivision.save()
        return muscle_subdivision

    @staticmethod
    def create_muscle_side(muscle):
        muscle_side = MuscleSide.objects.create(
            name='Muscle side identification',
            muscle=muscle
        )
        muscle_side.save()
        return muscle_side

    @staticmethod
    def create_emg_electrode_placement():

        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        emg_electrode_placement = EMGElectrodePlacement.objects.create(
            standardization_system=standardization_system,
            muscle_subdivision=muscle_subdivision
        )

        emg_electrode_placement.save()
        return emg_electrode_placement

    @staticmethod
    def create_component(experiment, component_type, identification=None,
                         kwargs=None):
        faker = Factory.create()

        # Due to some model Component's constants for component_type being
        # different from models that inheritade from Component model,
        # change the component_type string
        if component_type == Component.TASK_EXPERIMENT:
            component_type = 'taskfortheexperimenter'  # TaskForTheExperimenter
        elif component_type == Component.DIGITAL_GAME_PHASE:
            component_type = 'digitalgamephase'  # DigitalGamePhase
        elif component_type == Component.GENERIC_DATA_COLLECTION:
            component_type = 'genericdatacollection'  # GenericDataCollection

        component = get_model('experiment', component_type)(
            experiment=experiment,
            identification=identification or faker.ssn(),
            component_type=component_type,
            description=faker.text(),
        )

        if component_type == Component.QUESTIONNAIRE:
            try:
                component.survey_id = kwargs['sid']
            except IntegrityError:
                print('You need to specify "survey" argument with a Survey '
                      'object id to create a Questionnaire component')
            except KeyError:
                print('You must specify \'sid\' key in kwargs dict')

        component.save()

        return component

    @staticmethod
    def create_group(experiment, experimental_protocol=None):
        """
        :param experiment: experiment
        :param experimental_protocol: experimental protocol
        :return: group
        """
        group = Group.objects.create(
            experiment=experiment,
            title="Group-update",
            description="Descricao do Group-update",
            experimental_protocol=experimental_protocol
        )
        return group

    @staticmethod
    def create_block(experiment):
        block = Block.objects.create(
            identification='Block identification',
            description='Block description',
            experiment=experiment,
            component_type='block',
            type="sequence"
        )
        block.save()
        return block

    @staticmethod
    def create_manufacturer():
        manufacturer = Manufacturer.objects.create(
            name='Manufacturer name'
        )
        # manufacturer.save()
        return manufacturer

    @staticmethod
    def create_amplifier(manufacturer):
        amplifier = Amplifier.objects.create(
            manufacturer=manufacturer,
            equipment_type="amplifier",
            identification="Amplifier identification"
        )
        amplifier.save()
        return amplifier

    @staticmethod
    def create_eeg_solution(manufacturer):
        eeg_solution = EEGSolution.objects.create(
            manufacturer=manufacturer,
            name="Solution name"
        )
        eeg_solution.save()
        return eeg_solution

    @staticmethod
    def create_filter_type():
        filter_type = FilterType.objects.create(
            name="Filter type name"
        )
        filter_type.save()
        return filter_type

    @staticmethod
    def create_tag(name = 'TAG name'):
        tag = Tag.objects.create(
            name=name
        )
        tag.save()
        return tag

    @staticmethod
    def create_electrode_model():
        electrode_model = ElectrodeModel.objects.create(
            name="Electrode Model name"
        )
        tagaux = ObjectsFactory.create_tag('EEG')
        electrode_model.tags.add(tagaux)
        electrode_model.save()
        return electrode_model

    @staticmethod
    def create_eeg_electrode_net(manufacturer, electrode_model_default):
        eeg_electrode_net = EEGElectrodeNet.objects.create(
            manufacturer=manufacturer,
            equipment_type="eeg_electrode_net",
            electrode_model_default=electrode_model_default,
            identification="Electrode Net identification"
        )
        eeg_electrode_net.save()
        return eeg_electrode_net

    @staticmethod
    def create_eeg_electrode_net_system(eeg_electrode_net, eeg_electrode_localization_system):
        eeg_electrode_net_system = EEGElectrodeNetSystem.objects.create(
            eeg_electrode_net=eeg_electrode_net,
            eeg_electrode_localization_system=eeg_electrode_localization_system
        )
        eeg_electrode_net_system.save()
        return eeg_electrode_net_system

    @staticmethod
    def create_eeg_electrode_localization_system():
        eeg_electrode_localization_system = EEGElectrodeLocalizationSystem.objects.create(
            name="Localization System name"
        )
        eeg_electrode_localization_system.save()
        return eeg_electrode_localization_system

    @staticmethod
    def create_eeg_electrode_position(eeg_electrode_localization_system):
        eeg_electrode_position = EEGElectrodePosition.objects.create(
            eeg_electrode_localization_system=eeg_electrode_localization_system,
            name="Position name"
        )
        eeg_electrode_position.save()
        return eeg_electrode_position

    @staticmethod
    def create_software(manufacturer):
        software = Software.objects.create(
            manufacturer=manufacturer,
            name="Software name"
        )
        software.save()
        return software

    @staticmethod
    def create_software_version(software):
        software_version = SoftwareVersion.objects.create(
            software=software,
            name="Software Version name"
        )
        software_version.save()
        return software_version

    @staticmethod
    def create_ad_converter(manufacturer):
        ad_converter = ADConverter.objects.create(
            manufacturer=manufacturer,
            equipment_type="ad_converter",
            identification="AD Converter identification",
            signal_to_noise_rate=20,
            sampling_rate=10,
            resolution=7
        )
        ad_converter.save()
        return ad_converter

    @staticmethod
    def system_authentication(instance):
        user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        factory = RequestFactory()
        logged = instance.client.login(username=USER_USERNAME, password=USER_PWD)
        return logged, user, factory

    @staticmethod
    def create_material():
        material = Material.objects.create(
            name="Material name"
        )
        material.save()
        return material

    @staticmethod
    def create_eeg_electrode_cap(manufacturer, electrode_model_default):
        eeg_electrode_cap = EEGElectrodeCap.objects.create(
            manufacturer=manufacturer,
            identification="EEG electrode cap identification",
            electrode_model_default=electrode_model_default
        )
        eeg_electrode_cap.save()
        return eeg_electrode_cap

    @staticmethod
    def create_coil_model(coil_shape):
        coil_model = CoilModel.objects.create(
            name="Electrode Model name",
            coil_shape=coil_shape
        )
        coil_model.save()
        return coil_model

    @staticmethod
    def create_coil_shape():
        coil_shape = CoilShape.objects.create(
            name="Electrode Shape name"
        )
        coil_shape.save()
        return coil_shape

    @staticmethod
    def create_component_configuration(parent, component):
        faker = Factory.create()

        return ComponentConfiguration.objects.create(
            name=faker.word(),
            parent=parent,
            component=component
        )

    @staticmethod
    def create_data_configuration_tree(component_config):
        return DataConfigurationTree.objects.create(
            component_configuration=component_config,
            code=random.randint(1, 999)
        )

    @staticmethod
    def create_questionnaire_response(dct, responsible, token_id,
                                      subject_of_group):
        return QuestionnaireResponse.objects.create(
            data_configuration_tree=dct,
            questionnaire_responsible=responsible, token_id=token_id,
            subject_of_group=subject_of_group
        )


class ExperimentalProtocolTest(TestCase):

    data = {}

    def setUp(self):

        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        research_project = ObjectsFactory.create_research_project()

        experiment = ObjectsFactory.create_experiment(research_project)

        self.eeg_setting = ObjectsFactory.create_eeg_setting(experiment)

        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        self.emg_setting = ObjectsFactory.create_emg_setting(experiment, software_version)

    def test_component_list(self):
        experiment = Experiment.objects.first()
        url = reverse("component_list", args=(experiment.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check if there is no item in the table
        self.assertNotContains(response, "<td>")

        ObjectsFactory.create_block(Experiment.objects.first())

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Check if there is a item in the table
        self.assertContains(response, "<td>")

    def test_component_create(self):
        experiment = Experiment.objects.first()

        # screen to create a component
        response = self.client.post(reverse("component_new", args=(experiment.id, "task")))
        self.assertEqual(response.status_code, 200)

        identification = 'Task for the subject identification'
        description = 'Task for the subject description'
        self.data = {'action': 'save', 'identification': identification, 'description': description}
        response = self.client.post(reverse("component_new", args=(experiment.id, "task")), self.data)
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue("/experiment/" + str(experiment.id) + "/components" in response.url)
        self.assertTrue(Task.objects.filter(description=description,
                                            identification=identification).exists())

        identification = 'Task for the experimenter identification'
        description = 'Task for the experimenter description'
        self.data = {'action': 'save', 'identification': identification, 'description': description}
        response = self.client.post(reverse("component_new", args=(experiment.id, "task_experiment")), self.data)
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue("/experiment/" + str(experiment.id) + "/components" in response.url)
        self.assertTrue(TaskForTheExperimenter.objects.filter(description=description,
                                                              identification=identification).exists())

        identification = 'EMG identification'
        description = 'EMG description'
        self.data = {'action': 'save', 'identification': identification, 'description': description,
                     'emg_setting': self.emg_setting.id}
        response = self.client.post(reverse("component_new", args=(experiment.id, "emg")), self.data)
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue("/experiment/" + str(experiment.id) + "/components" in response.url)
        self.assertTrue(EMG.objects.filter(description=description,
                                           identification=identification).exists())

        identification = 'EEG identification'
        description = 'EEG description'
        self.data = {'action': 'save', 'identification': identification, 'description': description,
                     'eeg_setting': self.eeg_setting.id}
        response = self.client.post(reverse("component_new", args=(experiment.id, "eeg")), self.data)
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue("/experiment/" + str(experiment.id) + "/components" in response.url)
        self.assertTrue(EEG.objects.filter(description=description, identification=identification).exists())

        self.data = {'action': 'save', 'identification': 'Instruction identification',
                     'description': 'Instruction description', 'text': 'Instruction text'}
        response = self.client.post(reverse("component_new", args=(experiment.id, "instruction")), self.data)
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue("/experiment/" + str(experiment.id) + "/components" in response.url)
        self.assertTrue(Instruction.objects.filter(text="Instruction text").exists())

        stimulus_type = StimulusType.objects.create(name="Auditivo")
        stimulus_type.save()
        self.data = {'action': 'save', 'identification': 'Stimulus identification',
                     'description': 'Stimulus description', 'stimulus_type': stimulus_type.id}
        response = self.client.post(reverse("component_new", args=(experiment.id, "stimulus")), self.data)
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue("/experiment/" + str(experiment.id) + "/components" in response.url)
        self.assertTrue(Stimulus.objects.filter(identification="Stimulus identification", stimulus_type=1).exists())

        self.data = {'action': 'save', 'identification': 'Pause identification',
                     'description': 'Pause description', 'duration_value': 2, 'duration_unit': 'h'}
        response = self.client.post(reverse("component_new", args=(experiment.id, "pause")), self.data)
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue("/experiment/" + str(experiment.id) + "/components" in response.url)
        self.assertTrue(Pause.objects.filter(identification="Pause identification", duration_value=2).exists())

        # Conecta no Lime Survey
        lime_survey = Questionnaires()

        # Checa se conseguiu conectar no limeSurvey com as credenciais fornecidas no settings.py
        self.assertIsNotNone(lime_survey.session_key, 'Failed to connect LimeSurvey')

        # Cria uma survey no Lime Survey
        survey_id = lime_survey.add_survey(9999, 'Questionario de teste - DjangoTests', 'en', 'G')

        try:
            self.data = {'action': 'save', 'identification': 'Questionnaire identification',
                         'description': 'Questionnaire description', 'questionnaire_selected': survey_id}
            response = self.client.post(reverse("component_new", args=(experiment.id, "questionnaire")), self.data)
            self.assertEqual(response.status_code, 302)
            # Check if redirected to list of components
            self.assertTrue("/experiment/" + str(experiment.id) + "/components" in response.url)
            self.assertTrue(Questionnaire.objects.filter(identification="Questionnaire identification").exists())

            # TODO Adaptar esse teste antigo para cá e verificar o TODO de baixo.
            # Criar um questionario com código do questionário invalido
            # count_before_insert = QuestionnaireConfiguration.objects.all().count()
            # self.data = {'action': 'save', 'number_of_fills': '1', 'questionnaire_selected': 0}
            # response = self.client.post(reverse('questionnaire_new', args=(group.pk,)), self.data, follow=True)
            # self.assertEqual(response.status_code, 200)

            # TODO Verificar este teste, porque está permitindo codigo de questionario do Lime Survey invalido
            # count_after_insert = QuestionnaireConfiguration.objects.all().count()
            # self.assertEqual(count_after_insert,
            #                  count_before_insert + 1)

        finally:
            # Deleta a survey gerada no Lime Survey
            status = lime_survey.delete_survey(survey_id)
            self.assertEqual(status, 'OK')

        self.data = {'action': 'save', 'identification': 'Block identification',
                     'description': 'Block description', 'type': 'sequence'}
        response = self.client.post(reverse("component_new", args=(experiment.id, "block")), self.data)
        self.assertEqual(response.status_code, 302)
        block = Block.objects.filter(identification="Block identification").first()
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)

    def test_component_configuration_create_and_update(self):

        experiment = Experiment.objects.first()
        block = ObjectsFactory.create_block(experiment)

        # Screen to add a component
        response = self.client.get(reverse("component_add_new", args=(block.id, "block")))
        self.assertEqual(response.status_code, 200)

        # Add a new component to the parent
        self.data = {'action': 'save',
                     'identification': 'Block identification',
                     'description': 'Block description',
                     'type': 'sequence',
                     'number_of_uses_to_insert': 1}
        response = self.client.post(reverse("component_add_new", args=(block.id, "block")), self.data)
        self.assertEqual(response.status_code, 302)
        component_configuration = ComponentConfiguration.objects.first()
        # Check if redirected to view parent set of steps
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)
        self.assertTrue(Block.objects.filter(identification="Block identification").exists())
        self.assertEqual(component_configuration.parent.id, block.id)
        self.assertEqual(component_configuration.order, 1)
        self.assertEqual(component_configuration.name, None)

        # Screen to update a component
        response = self.client.get(reverse("component_edit", args=(block.id,)))
        self.assertEqual(response.status_code, 200)

        # Update the component configuration of the recently added component.
        self.data = {'action': 'save', 'identification': 'Block identification', 'description': 'Block description',
                     'type': 'sequence', 'name': 'Use of block in block',
                     'interval_between_repetitions_value': 2, 'interval_between_repetitions_unit': 'min'}
        response = self.client.post(reverse("component_edit", args=(block.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)

        # Screen to reuse a component
        response = self.client.get(reverse("component_reuse", args=(block.id, Block.objects.filter(
            identification="Block identification").first().id)))
        self.assertEqual(response.status_code, 200)

        # Add 3 uses of an existing component to the parent
        self.data = {'number_of_uses_to_insert': 3}
        response = self.client.post(reverse("component_reuse", args=(block.id, Block.objects.filter(
            identification="Block identification").first().id)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComponentConfiguration.objects.count(), 4)

        eeg_setting = ObjectsFactory.create_eeg_setting(experiment)

        # Add an eeg step
        self.data = {'action': 'save',
                     'identification': 'EEG identification',
                     'description': 'EEG description',
                     'type': 'eeg',
                     'eeg_setting': eeg_setting.id,
                     'number_of_uses_to_insert': 1}
        response = self.client.post(reverse("component_add_new", args=(block.id, "eeg")), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComponentConfiguration.objects.count(), 5)

        # Reuse an eeg step
        self.data = {'number_of_uses_to_insert': 1}
        response = self.client.post(reverse("component_reuse", args=(block.id, EEG.objects.filter(
            identification="EEG identification").first().id)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComponentConfiguration.objects.count(), 6)

    def test_block_component_remove(self):
        experiment = Experiment.objects.first()

        task = Task.objects.create(
            identification='Task identification',
            description='Task description',
            experiment=experiment,
            component_type='task'
        )
        task.save()
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Component.objects.count(), 1)

        block = ObjectsFactory.create_block(experiment)

        self.assertEqual(Block.objects.count(), 1)
        self.assertEqual(Component.objects.count(), 2)

        component_configuration = ComponentConfiguration.objects.create(
            name='ComponentConfiguration_name',
            parent=block,
            component=task
        )
        component_configuration.save()
        self.assertEqual(ComponentConfiguration.objects.count(), 1)
        self.assertEqual(component_configuration.order, 1)

        response = self.client.get(reverse("component_view", args=(block.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'remove'}
        response = self.client.post(reverse("component_view", args=(block.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue("/experiment/" + str(experiment.id) + "/components" in response.url)
        self.assertEqual(Block.objects.count(), 0)
        self.assertEqual(Component.objects.count(), 1)
        self.assertEqual(ComponentConfiguration.objects.count(), 0)

        # Screen to update a component
        response = self.client.get(reverse("component_edit", args=(task.id,)))
        self.assertEqual(response.status_code, 200)

        # Updating a component
        response = self.client.post(reverse("component_edit", args=(task.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue("/experiment/" + str(experiment.id) + "/components" in response.url)
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(Component.objects.count(), 0)

    def test_component_configuration_change_order_single_use(self):
        experiment = Experiment.objects.first()

        block = ObjectsFactory.create_block(experiment)

        task = Task.objects.create(
            identification='Task identification',
            description='Task description',
            experiment=experiment,
            component_type='task'
        )
        task.save()

        component_configuration1 = ComponentConfiguration.objects.create(
            name='ComponentConfiguration 1',
            parent=block,
            component=task
        )
        component_configuration1.save()
        self.assertEqual(component_configuration1.order, 1)

        component_configuration2 = ComponentConfiguration.objects.create(
            name='ComponentConfiguration 2',
            parent=block,
            component=task
        )
        component_configuration2.save()
        self.assertEqual(component_configuration2.order, 2)

        response = self.client.get(reverse("component_change_the_order", args=(block.id,
                                                                               "0-1",
                                                                               "up")))
        self.assertEqual(response.status_code, 302)
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)
        self.assertEqual(ComponentConfiguration.objects.get(name="ComponentConfiguration 1").order, 2)
        self.assertEqual(ComponentConfiguration.objects.get(name="ComponentConfiguration 2").order, 1)

        response = self.client.get(reverse("component_change_the_order", args=(block.id,
                                                                               "0-0",
                                                                               "down")))
        self.assertEqual(response.status_code, 302)
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)
        self.assertEqual(ComponentConfiguration.objects.get(name="ComponentConfiguration 1").order, 1)
        self.assertEqual(ComponentConfiguration.objects.get(name="ComponentConfiguration 2").order, 2)

    def test_component_configuration_change_order_accordion(self):
        experiment = Experiment.objects.first()

        block = ObjectsFactory.create_block(experiment)

        task = Task.objects.create(
            identification='Task identification',
            description='Task description',
            experiment=experiment,
            component_type='task'
        )
        task.save()

        component_configuration1 = ComponentConfiguration.objects.create(
            name='ComponentConfiguration 1',
            parent=block,
            component=task
        )
        component_configuration1.save()
        self.assertEqual(component_configuration1.order, 1)

        component_configuration2 = ComponentConfiguration.objects.create(
            name='ComponentConfiguration 2',
            parent=block,
            component=task
        )
        component_configuration2.save()
        self.assertEqual(component_configuration2.order, 2)

        instruction = Instruction.objects.create(
            identification='Instruction identification',
            description='Instruction description',
            experiment=experiment,
            component_type='instruction'
        )
        instruction.save()

        component_configuration3 = ComponentConfiguration.objects.create(
            name='ComponentConfiguration 3',
            parent=block,
            component=instruction
        )
        component_configuration3.save()
        self.assertEqual(component_configuration3.order, 3)

        response = self.client.get(reverse("component_change_the_order", args=(block.id,
                                                                               "0",
                                                                               "down")))
        self.assertEqual(response.status_code, 302)
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)
        self.assertEqual(ComponentConfiguration.objects.get(name="ComponentConfiguration 1").order, 2)
        self.assertEqual(ComponentConfiguration.objects.get(name="ComponentConfiguration 2").order, 3)
        self.assertEqual(ComponentConfiguration.objects.get(name="ComponentConfiguration 3").order, 1)

        response = self.client.get(reverse("component_change_the_order", args=(block.id,
                                                                               "1",
                                                                               "up")))
        self.assertEqual(response.status_code, 302)
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)
        self.assertEqual(ComponentConfiguration.objects.get(name="ComponentConfiguration 1").order, 1)
        self.assertEqual(ComponentConfiguration.objects.get(name="ComponentConfiguration 2").order, 2)
        self.assertEqual(ComponentConfiguration.objects.get(name="ComponentConfiguration 3").order, 3)


class GroupTest(TestCase):

    data = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        research_project = ObjectsFactory.create_research_project()

        ObjectsFactory.create_experiment(research_project)

    def test_group_insert(self):

        experiment = Experiment.objects.first()

        # Screen to insert a group
        response = self.client.get(reverse("group_new", args=(experiment.id,)))
        self.assertEqual(response.status_code, 200)

        # Data about the group
        self.data = {'action': 'save', 'description': 'Description of Group-1', 'title': 'Group-1'}

        # Inserting a group in the experiment
        response = self.client.post(reverse("group_new", args=(experiment.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(experiment.group_set.count(), 1)

    def test_group_update(self):

        experiment = Experiment.objects.first()
        group = ObjectsFactory.create_group(experiment)

        # Screen to update a group
        # request = self.factory.get(reverse('group_edit', args=[group.id, ]))
        # request.user = self.user
        # response = group_update(request, group_id=group.id)
        # self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("group_edit", args=(group.id,)))
        self.assertEqual(response.status_code, 200)

        # New data about the group
        self.data = {'action': 'save', 'description': 'Description of Group-1', 'title': 'Group-1'}

        # Editing a group in the experiment
        response = self.client.post(reverse("group_edit", args=(group.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(experiment.group_set.count(), 1)
        self.assertTrue(Group.objects.filter(title="Group-1", description="Description of Group-1").exists())

        # Trying to editing a group with no changes
        response = self.client.post(reverse("group_edit", args=(group.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_group_remove(self):
        experiment = Experiment.objects.first()

        group = ObjectsFactory.create_group(experiment)

        # New data about the group
        self.data = {'action': 'remove'}

        # Inserting a group in the experiment
        response = self.client.post(reverse("group_view", args=(group.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Group.objects.count(), 0)


class ClassificationOfDiseasesTest(TestCase):
    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

    def test_classification_of_diseases_insert(self):
        """
        Testa a view classification_of_diseases_insert
        """
        research_project = ObjectsFactory.create_research_project()

        experiment = ObjectsFactory.create_experiment(research_project)

        group = ObjectsFactory.create_group(experiment)

        # Criando instancia de ClassificationOfDiseases
        classification_of_diseases = ClassificationOfDiseases.objects.create(code="1", description="test",
                                                                             abbreviated_description="t")
        # Inserindo o classification_of_diseases no group
        response = self.client.get(reverse(CLASSIFICATION_OF_DISEASES_CREATE,
                                           args=(group.id, classification_of_diseases.id)))
        self.assertEqual(response.status_code, 302)

        self.assertEqual(group.classification_of_diseases.count(), 1)

    def test_classification_of_diseases_remove(self):
        """
        Testa a view classification_of_diseases_insert
        """
        research_project = ObjectsFactory.create_research_project()

        experiment = ObjectsFactory.create_experiment(research_project)

        group = ObjectsFactory.create_group(experiment)

        # Criando instancia de ClassificationOfDiseases
        classification_of_diseases = ClassificationOfDiseases.objects.create(code="1", description="test",
                                                                             abbreviated_description="t")
        # Inserindo o classification_of_diseases no group
        response = self.client.get(reverse(CLASSIFICATION_OF_DISEASES_CREATE,
                                           args=(group.id, classification_of_diseases.id)))
        self.assertEqual(response.status_code, 302)

        self.assertEqual(group.classification_of_diseases.count(), 1)

        # Removendo o classification_of_diseases no group
        response = self.client.get(reverse(CLASSIFICATION_OF_DISEASES_DELETE,
                                           args=(group.id, classification_of_diseases.id)))
        self.assertEqual(response.status_code, 302)

        self.assertEqual(group.classification_of_diseases.count(), 0)


class ExperimentTest(TestCase):

    data = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        # Cria um estudo
        self.research_project = ObjectsFactory.create_research_project()

    def test_experiment_list(self):
        """
        Testa a listagem de experimentos
        """

        # lista experimentos do estudo
        response = self.client.get(reverse("research_project_view", args=[self.research_project.pk, ]))
        self.assertEqual(response.status_code, 200)

        # deve retornar vazia
        self.assertEqual(len(response.context['experiments']), 0)

        # cria um experimento
        experiment = ObjectsFactory.create_experiment(self.research_project)

        # lista experimentos: deve retornar 1
        response = self.client.get(reverse("research_project_view", args=[self.research_project.pk, ]))
        self.assertEqual(response.status_code, 200)

        # deve retornar 1 experimento
        self.assertEqual(len(response.context['experiments']), 1)

        self.assertContains(response, experiment.title)

    def test_experiment_create(self):
        """Testa a criacao de um experimento """

        # Abre tela de cadastro de experimento
        response = self.client.get(reverse('experiment_new', args=[self.research_project.pk, ]))
        self.assertEqual(response.status_code, 200)

        # Dados sobre o experimento
        self.data = {'action': 'save', 'description': 'Experimento de Teste', 'title': 'Teste Experimento',
                     'research_project': self.research_project.id}

        # Obtem o total de experimentos existente na tabela
        count_before_insert = Experiment.objects.all().count()

        # Efetua a adicao do experimento
        response = self.client.post(reverse('experiment_new', args=[self.research_project.pk, ]), self.data)

        # Verifica se o status de retorno é adequado
        self.assertEqual(response.status_code, 302)

        # Obtem o toal de experimento após a inclusão
        count_after_insert = Experiment.objects.all().count()

        # Verifica se o experimento foi de fato adicionado
        self.assertEqual(count_after_insert, count_before_insert + 1)

    def test_experiment_update(self):
        """Testa a atualizacao do experimento"""

        experiment = ObjectsFactory.create_experiment(self.research_project)

        # Create an instance of a GET request.
        request = self.factory.get(reverse('experiment_edit', args=[experiment.pk, ]))
        request.user = self.user

        response = experiment_update(request, experiment_id=experiment.pk)
        self.assertEqual(response.status_code, 200)

        # Efetua a atualizacao do experimento
        self.data = {'action': 'save', 'description': 'Experimento de Teste', 'title': 'Teste Experimento',
                     'research_project': self.research_project.id}
        response = self.client.post(reverse('experiment_edit', args=(experiment.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_experiment_remove(self):
        """Testa a exclusao do experimento"""

        experiment = ObjectsFactory.create_experiment(self.research_project)

        count = Experiment.objects.all().count()

        # Remove experimento
        self.data = {'action': 'remove', 'description': 'Experimento de Teste', 'title': 'Teste Experimento',
                     'research_project': self.research_project.id}
        response = self.client.post(reverse('experiment_view', args=(experiment.pk,)), self.data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Experiment.objects.all().count(), count - 1)


class ListOfQuestionnaireFromExperimentalProtocolOfAGroupTest(TestCase):
    lime_survey = None

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        # Conecta no Lime Survey
        self.lime_survey = Questionnaires()

        # Checa se conseguiu conectar no lime Survey com as credenciais fornecidas no settings.py
        self.assertIsNotNone(self.lime_survey.session_key, 'Failed to connect LimeSurvey')

    def test_create_questionnaire_for_a_group(self):
        """Testa a criacao de um questionario para um dado grupo"""

        research_project = ObjectsFactory.create_research_project()

        experiment = ObjectsFactory.create_experiment(research_project)

        # Create the root of the experimental protocol
        block = ObjectsFactory.create_block(Experiment.objects.first())

        # Create a quesitonnaire at LiveSurvey to use in this test.
        survey_title = 'Questionario de teste - DjangoTests'
        sid = self.lime_survey.add_survey(99999, survey_title, 'en', 'G')

        try:
            new_survey, created = Survey.objects.get_or_create(lime_survey_id=sid)

            # Create a questionnaire
            questionnaire = Questionnaire.objects.create(identification='Questionnaire',
                                                         description='Questionnaire description',
                                                         experiment=Experiment.objects.first(),
                                                         component_type='questionnaire',
                                                         survey=new_survey)
            questionnaire.save()

            # Include the questionnaire in the root.
            ComponentConfiguration.objects.create(
                name='ComponentConfiguration',
                parent=block,
                component=questionnaire
            )

            # Criar um grupo mock para ser utilizado no teste
            group = ObjectsFactory.create_group(experiment, block)

            # Abre tela de grupo
            response = self.client.get(reverse('group_view', args=(group.pk,)))
            self.assertEqual(response.status_code, 200)
            # Check if the survey is listed
            self.assertContains(response, survey_title)
        finally:
            # Deleta a survey gerada no Lime Survey
            status = self.lime_survey.delete_survey(sid)
            self.assertEqual(status, 'OK')

    def test_list_questionnaire_of_a_group(self):
        """Test exhibition of a questionnaire of a group"""

        # Create a research project
        research_project = ObjectsFactory.create_research_project()

        # Criar um experimento mock para ser utilizado no teste
        experiment = ObjectsFactory.create_experiment(research_project)

        # Create the root of the experimental protocol
        block = ObjectsFactory.create_block(Experiment.objects.first())

        # Using a known questionnaire at LiveSurvey to use in this test.
        new_survey, created = Survey.objects.get_or_create(lime_survey_id=LIME_SURVEY_ID)

        # Create a questionnaire
        questionnaire = Questionnaire.objects.create(
            identification='Questionnaire',
            description='Questionnaire description',
            experiment=Experiment.objects.first(),
            component_type='questionnaire',
            survey=new_survey
        )
        questionnaire.save()

        # Include the questionnaire in the root.
        component_configuration = ComponentConfiguration.objects.create(
            name='ComponentConfiguration',
            parent=block,
            component=questionnaire
        )
        component_configuration.save()

        data_configuration_tree = DataConfigurationTree.objects.create(
            component_configuration=component_configuration
        )
        data_configuration_tree.save()

        # Create a mock group
        group = ObjectsFactory.create_group(experiment, block)

        # Insert subject in the group
        util = UtilTests()
        patient_mock = util.create_patient_mock(changed_by=self.user)

        subject_mock = Subject(patient=patient_mock)
        subject_mock.save()

        subject_group = SubjectOfGroup(subject=subject_mock, group=group)
        subject_group.save()

        group.subjectofgroup_set.add(subject_group)
        experiment.save()

        # Setting the response
        questionnaire_response = QuestionnaireResponse()
        questionnaire_response.data_configuration_tree = data_configuration_tree
        # questionnaire_response.component_configuration = component_configuration
        questionnaire_response.subject_of_group = subject_group
        questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_1
        questionnaire_response.questionnaire_responsible = self.user
        questionnaire_response.date = datetime.datetime.now()
        questionnaire_response.save()

        # Show questionnaire screen
        response = self.client.get(reverse('questionnaire_view', args=(group.pk, component_configuration.pk)))
        self.assertEqual(response.status_code, 200)

    def test_questionnaire_response_view_response(self):
        """ Testa a visualizacao completa do questionario respondido no Lime Survey"""

        # Create a research project
        research_project = ObjectsFactory.create_research_project()

        # Create a mock experiment
        experiment = ObjectsFactory.create_experiment(research_project)

        # Create the root of the experimental protocol
        block = ObjectsFactory.create_block(Experiment.objects.first())

        # Using a known questionnaire at LiveSurvey to use in this test.
        new_survey, created = Survey.objects.get_or_create(lime_survey_id=LIME_SURVEY_ID)

        # Create a questionnaire
        questionnaire = Questionnaire.objects.create(identification='Questionnaire',
                                                     description='Questionnaire description',
                                                     experiment=Experiment.objects.first(),
                                                     component_type='questionnaire',
                                                     survey=new_survey)
        questionnaire.save()

        # Include the questionnaire in the root.
        component_configuration = ComponentConfiguration.objects.create(
            name='ComponentConfiguration',
            parent=block,
            component=questionnaire
        )
        component_configuration.save()

        data_configuration_tree = DataConfigurationTree.objects.create(
            component_configuration=component_configuration
        )
        data_configuration_tree.save()

        # Create a mock group
        group = ObjectsFactory.create_group(experiment, block)

        # Create a subject to the experiment
        util = UtilTests()
        patient_mock = util.create_patient_mock(changed_by=self.user)
        subject_mock = Subject.objects.create(patient=patient_mock)
        subject_group = SubjectOfGroup.objects.create(
            subject=subject_mock, group=group
        )

        group.subjectofgroup_set.add(subject_group)
        experiment.save()

        # Setting the response
        questionnaire_response = QuestionnaireResponse()
        questionnaire_response.data_configuration_tree = data_configuration_tree
        questionnaire_response.subject_of_group = subject_group
        questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_1
        questionnaire_response.questionnaire_responsible = self.user
        questionnaire_response.date = datetime.datetime.now()
        questionnaire_response.save()


class SubjectTest(TestCase):

    util = UtilTests()
    data = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        # Conecta no Lime Survey
        self.lime_survey = Questionnaires()

        # Checa se conseguiu conectar no lime Survey com as credenciais fornecidas no settings.py
        self.assertIsNotNone(self.lime_survey.session_key, 'Failed to connect LimeSurvey')

        self.tag_eeg = ObjectsFactory.create_tag('EEG')
        # self.tag_eeg.name =

    def test_subject_view_and_search(self):
        """
        Teste de visualizacao de participante após cadastro na base de dados
        """

        # Create a research project
        research_project = ObjectsFactory.create_research_project()

        # Criar um experimento mock para ser utilizado no teste
        experiment = ObjectsFactory.create_experiment(research_project)

        # Criar um grupo mock para ser utilizado no teste
        group = ObjectsFactory.create_group(experiment)

        patient_mock = self.util.create_patient_mock(changed_by=self.user)
        patient_mock.cpf = '374.276.738-08'  # to test search for cpf
        patient_mock.save()
        self.data = {
            SEARCH_TEXT: 'Pacient', 'experiment_id': experiment.id,
            'group_id': group.id
        }

        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, patient_mock.name)
        self.assertEqual(response.context['patients'].count(), 1)

        self.data[SEARCH_TEXT] = 374
        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patients'].count(), 1)
        self.assertContains(response, patient_mock.cpf)

        self.data[SEARCH_TEXT] = ''
        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['patients'], '')

    def test_subject_view(self):
        """
        Test exhibition of subjects of a group
        """

        # Create a research project
        research_project = ObjectsFactory.create_research_project()

        # Criar um experimento mock para ser utilizado no teste
        experiment = ObjectsFactory.create_experiment(research_project)

        # Create the root of the experimental protocol
        block = ObjectsFactory.create_block(Experiment.objects.first())

        # Using a known questionnaire at LiveSurvey to use in this test.
        new_survey, created = Survey.objects.get_or_create(lime_survey_id=LIME_SURVEY_ID)

        # Create a questionnaire
        questionnaire = Questionnaire.objects.create(identification='Questionnaire',
                                                     description='Questionnaire description',
                                                     experiment=Experiment.objects.first(),
                                                     component_type='questionnaire',
                                                     survey=new_survey)
        questionnaire.save()

        # Include the questionnaire in the root.
        component_configuration = ComponentConfiguration.objects.create(
            name='ComponentConfiguration',
            parent=block,
            component=questionnaire
        )
        component_configuration.save()

        data_configuration_tree = DataConfigurationTree.objects.create(
            component_configuration=component_configuration
        )
        data_configuration_tree.save()

        # Create a mock group
        group = ObjectsFactory.create_group(experiment, block)

        # Abre tela de cadastro de participantes com nenhum participante cadastrado a priori
        response = self.client.get(reverse('subjects', args=(group.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['subject_list']), 0)

        # Insert subject in the group
        util = UtilTests()
        patient_mock = util.create_patient_mock(changed_by=self.user)

        count_before_insert_subject = SubjectOfGroup.objects.all().filter(group=group).count()
        response = self.client.post(reverse('subject_insert', args=(group.pk, patient_mock.pk)))
        self.assertEqual(response.status_code, 302)
        count_after_insert_subject = SubjectOfGroup.objects.all().filter(group=group).count()
        self.assertEqual(count_after_insert_subject, count_before_insert_subject + 1)

        # Setting the response
        questionnaire_response = QuestionnaireResponse()
        questionnaire_response.data_configuration_tree = data_configuration_tree
        # questionnaire_response.component_configuration = component_configuration
        questionnaire_response.subject_of_group = SubjectOfGroup.objects.all().first()
        questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_1
        questionnaire_response.questionnaire_responsible = self.user
        questionnaire_response.date = datetime.datetime.now()
        questionnaire_response.save()

        # Reabre a tela de cadastro de participantes - devera conter ao menos um participante cadastrado
        response = self.client.get(reverse('subjects', args=(group.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['subject_list']), 1)

        # Inserir participante ja inserido para o experimento
        count_before_insert_subject = SubjectOfGroup.objects.all().filter(group=group).count()
        response = self.client.post(reverse('subject_insert', args=(group.pk, patient_mock.pk)))
        self.assertEqual(response.status_code, 302)
        count_after_insert_subject = SubjectOfGroup.objects.all().filter(group=group).count()
        self.assertEqual(count_after_insert_subject, count_before_insert_subject)

    def test_questionnaire_fill(self):
        """
        Test of a questionnaire fill
        """

        # Create a research project
        research_project = ObjectsFactory.create_research_project()

        # Criar um experimento mock para ser utilizado no teste
        experiment = ObjectsFactory.create_experiment(research_project)

        # Create the root of the experimental protocol
        block = ObjectsFactory.create_block(Experiment.objects.first())

        # Using a known questionnaires at LiveSurvey to use in this test.
        new_survey, created = \
            Survey.objects.get_or_create(lime_survey_id=LIME_SURVEY_ID)
        new_survey_without_access_table, created = \
            Survey.objects.get_or_create(lime_survey_id=LIME_SURVEY_ID_WITHOUT_ACCESS_CODE_TABLE)
        new_survey_inactive, created = \
            Survey.objects.get_or_create(lime_survey_id=LIME_SURVEY_ID_INACTIVE)
        new_survey_without_identification_group, created = \
            Survey.objects.get_or_create(lime_survey_id=LIME_SURVEY_ID_WITHOUT_IDENTIFICATION_GROUP)

        # Create a questionnaire
        questionnaire = \
            Questionnaire.objects.create(identification='Questionnaire',
                                         description='Questionnaire description',
                                         experiment=Experiment.objects.first(),
                                         component_type='questionnaire',
                                         survey=new_survey)
        questionnaire.save()

        questionnaire_without_access_table = \
            Questionnaire.objects.create(identification='Questionnaire',
                                         description='Questionnaire description',
                                         experiment=Experiment.objects.first(),
                                         component_type='questionnaire',
                                         survey=new_survey_without_access_table)
        questionnaire_without_access_table.save()

        questionnaire_inactive = \
            Questionnaire.objects.create(identification='Questionnaire',
                                         description='Questionnaire description',
                                         experiment=Experiment.objects.first(),
                                         component_type='questionnaire',
                                         survey=new_survey_inactive)
        questionnaire_inactive.save()

        questionnaire_without_identification_group = \
            Questionnaire.objects.create(identification='Questionnaire',
                                         description='Questionnaire description',
                                         experiment=Experiment.objects.first(),
                                         component_type='questionnaire',
                                         survey=new_survey_without_identification_group)
        questionnaire_without_identification_group.save()

        # Include the questionnaire in the root.
        component_configuration = ComponentConfiguration.objects.create(
            name='ComponentConfiguration',
            parent=block,
            component=questionnaire
        )
        component_configuration.save()

        component_configuration_without_access_table = ComponentConfiguration.objects.create(
            name='ComponentConfiguration',
            parent=block,
            component=questionnaire_without_access_table
        )
        component_configuration_without_access_table.save()

        component_configuration_inactive = ComponentConfiguration.objects.create(
            name='ComponentConfiguration',
            parent=block,
            component=questionnaire_inactive
        )
        component_configuration_inactive.save()

        component_configuration_without_identification_group = ComponentConfiguration.objects.create(
            name='ComponentConfiguration',
            parent=block,
            component=questionnaire_without_identification_group
        )
        component_configuration_without_identification_group.save()

        data_configuration_tree = DataConfigurationTree.objects.create(
            component_configuration=component_configuration
        )
        data_configuration_tree.save()

        group = ObjectsFactory.create_group(experiment, block)

        util = UtilTests()
        patient_mock = util.create_patient_mock(changed_by=self.user)

        subject_mock = Subject(patient=patient_mock)
        subject_mock.save()

        subject_group = SubjectOfGroup(subject=subject_mock, group=group)
        subject_group.save()

        group.subjectofgroup_set.add(subject_group)
        experiment.save()

        # Dados para preenchimento da Survey
        self.data = {'date': '29/08/2014', 'action': 'save'}

        # Inicia o preenchimento de uma Survey
        response = self.client.post(reverse('subject_questionnaire_response',
                                            args=[group.pk, subject_mock.pk,
                                                  data_configuration_tree.component_configuration.id, ]), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['FAIL'], False)

        # Inicia o preenchimento de uma Survey without access code table
        response = self.client.post(reverse('subject_questionnaire_response',
                                            args=[group.pk, subject_mock.pk,
                                                  component_configuration_without_access_table.pk, ]), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['FAIL'], True)

        # Inicia o preenchimento de uma Survey inactive
        response = self.client.post(reverse('subject_questionnaire_response',
                                            args=[group.pk, subject_mock.pk,
                                                  component_configuration_inactive.pk, ]), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['FAIL'], True)

        # Inicia o preenchimento de uma Survey without identification group
        response = self.client.post(reverse('subject_questionnaire_response',
                                            args=[group.pk, subject_mock.pk,
                                                  component_configuration_without_identification_group.pk, ]),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['FAIL'], True)

        questionnaire_response = QuestionnaireResponse.objects.all().first()

        # Acessa tela de atualizacao do preenchimento da Survey
        response = self.client.get(reverse('questionnaire_response_edit',
                                           args=[questionnaire_response.pk, ]), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['FAIL'], None)

        # Atualiza o preenchimento da survey
        response = self.client.post(reverse('questionnaire_response_edit',
                                            args=[questionnaire_response.pk, ]), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['FAIL'], False)

        response = self.client.get(reverse('questionnaire_response_edit',
                                           args=[questionnaire_response.pk, ]), self.data)
        self.assertEqual(response.status_code, 200)

        # Show the responses list of a subject
        response = self.client.post(reverse('subject_questionnaire', args=(group.pk, subject_mock.pk)),)
        self.assertEqual(response.status_code, 200)

        # Remove preenchimento da Survey
        count_before_delete_questionnaire_response = QuestionnaireResponse.objects.all().count()

        self.data['action'] = 'remove'
        response = self.client.post(reverse('questionnaire_response_edit',
                                            args=[questionnaire_response.pk, ]), self.data)
        self.assertEqual(response.status_code, 302)

        count_after_delete_questionnaire_response = QuestionnaireResponse.objects.all().count()
        self.assertEqual(count_before_delete_questionnaire_response - 1,
                         count_after_delete_questionnaire_response)

        # Delete participant from a group
        self.data = {'action': 'remove-' + str(subject_mock.pk)}
        count_before_delete_subject = SubjectOfGroup.objects.all().filter(group=group).count()
        response = self.client.post(reverse('subjects', args=(group.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        count_after_delete_subject = SubjectOfGroup.objects.all().filter(group=group).count()
        self.assertEqual(count_before_delete_subject - 1, count_after_delete_subject)

    # def test_questionaire_view(self):
    #     """ Testa a visualizacao completa do questionario respondido no Lime Survey"""
    #
    #     # Create a research project
    #     research_project = ResearchProject.objects.create(title="Research project title",
    #                                                       start_date=datetime.date.today(),
    #                                                       description="Research project description")
    #     research_project.save()
    #
    #     # Criar um experimento mock para ser utilizado no teste
    #     experiment = Experiment.objects.create(title="Experimento-Teste-View",
    #                                            description="Descricao do Experimento-View",
    #                                            research_project=research_project)
    #     experiment.save()
    #
    #     # Criar um grupo mock para ser utilizado no teste
    #     group = Group.objects.create(experiment=experiment,
    #                                  title="Group-update",
    #                                  description="Descricao do Group-update")
    #     group.save()
    #
    #     # Criar um Subject para o experimento
    #     patient_mock = self.util.create_patient_mock(user=self.user)
    #
    #     subject_mock = Subject(patient=patient_mock)
    #     subject_mock.save()
    #
    #     subject_group = SubjectOfGroup(subject=subject_mock, group=group)
    #     subject_group.save()
    #
    #     group.subjectofgroup_set.add(subject_group)
    #     experiment.save()
    #
    #     # Cria um questionario
    #     questionnaire_configuration = QuestionnaireConfiguration(lime_survey_id=LIME_SURVEY_CODE_ID_TEST,
    #                                                              group=group,
    #                                                              number_of_fills=2)
    #     questionnaire_configuration.save()
    #
    #     questionnaire_response = QuestionnaireResponse()
    #     questionnaire_response.questionnaire_configuration = questionnaire_configuration
    #     questionnaire_response.subject_of_group = subject_group
    #     questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_1
    #     questionnaire_response.questionnaire_responsible = self.user
    #     questionnaire_response.date = datetime.datetime.now()
    #     questionnaire_response.save()
    #
    #     # Visualiza preenchimento da Survey
    #     get_data = {'view': "experiment", 'status': "view"}
    #
    #     response = self.client.get(reverse('questionnaire_response_edit',
    #                                        args=[questionnaire_response.pk, ]), data=get_data)
    #     self.assertEqual(response.status_code, 200)
    #
    #     questionnaire_response = QuestionnaireResponse()
    #     questionnaire_response.questionnaire_configuration = questionnaire_configuration
    #     questionnaire_response.subject_of_group = subject_group
    #     questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_2
    #     questionnaire_response.questionnaire_responsible = self.user
    #     questionnaire_response.date = datetime.datetime.now()
    #     questionnaire_response.save()
    #
    #     # Visualiza preenchimento da Survey
    #     response = self.client.get(reverse('questionnaire_response_edit',
    #                                        args=[questionnaire_response.pk, ]), data=get_data)
    #     self.assertEqual(response.status_code, 200)
    #
    #     # Abre tela de cadastro de participantes com nenhum participante cadastrado a priori
    #     response = self.client.get(reverse('subjects', args=(group.pk,)))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.context['subject_list']), 1)

    def test_eeg_data_file(self):
        """
        Test of a EEG data file upload
        """

        research_project = ObjectsFactory.create_research_project()

        experiment = ObjectsFactory.create_experiment(research_project)

        block = ObjectsFactory.create_block(Experiment.objects.first())

        eeg_setting = ObjectsFactory.create_eeg_setting(experiment)

        # EEG step
        eeg_step = EEG.objects.create(experiment=experiment, component_type="eeg", identification="EEG step",
                                      eeg_setting=eeg_setting)

        # Include the EEG step in the root.
        component_configuration = ComponentConfiguration.objects.create(
            name='ComponentConfiguration',
            parent=block,
            component=eeg_step
        )
        component_configuration.save()

        group = ObjectsFactory.create_group(experiment, block)

        util = UtilTests()
        patient_mock = util.create_patient_mock(changed_by=self.user)

        subject_mock = Subject(patient=patient_mock)
        subject_mock.save()

        subject_group = SubjectOfGroup(subject=subject_mock, group=group)
        subject_group.save()

        group.subjectofgroup_set.add(subject_group)
        experiment.save()

        # screen to create an eeg data file
        response = self.client.get(reverse('subject_eeg_data_create',
                                           args=(group.id, subject_mock.id, component_configuration.id)))
        self.assertEqual(response.status_code, 200)

        # trying to create an eeg data file with a date greater than todays' date
        file_format = FileFormat.objects.create(name='Text file', extension='txt')
        file = SimpleUploadedFile('experiment/eeg/eeg_metadata.txt', b'rb')
        self.data = {'date': datetime.date.today() + datetime.timedelta(days=1), 'action': 'save',
                     'description': 'description of the file',
                     'file_format': file_format.id, 'file': file}
        response = self.client.post(reverse('subject_eeg_data_create',
                                            args=(group.id, subject_mock.id, component_configuration.id)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGData.objects.all().count(), 0)
        self.assertGreaterEqual(len(response.context['eeg_data_form'].errors), 1)
        self.assertTrue('date' in response.context['eeg_data_form'].errors)
        self.assertEqual(response.context['eeg_data_form'].errors['date'][0],
                         _("Date cannot be greater than today's date."))

        # create an eeg data file
        tag_eeg = Tag.objects.get(name="EEG")
        file_format = FileFormat.objects.create(name='Text file', extension='txt')
        file_format.tags.add(tag_eeg)
        file = SimpleUploadedFile('experiment/eeg/eeg_metadata.txt', b'rb')
        self.data = {'date': '29/08/2014', 'action': 'save',
                     'description': 'description of the file',
                     'file_format': file_format.id, 'file': file,
                     'file_format_description': 'test',
                     'eeg_setting': eeg_setting.id}
        response = self.client.post(reverse('subject_eeg_data_create',
                                            args=(group.id, subject_mock.id, component_configuration.id)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGData.objects.all().count(), 1)

        # show a eeg data file
        eeg_data = EEGData.objects.all().first()
        response = self.client.get(reverse('eeg_data_view', args=(eeg_data.id, 1)))
        self.assertEqual(response.status_code, 200)

        # screen to edit a eeg data file
        response = self.client.get(reverse('eeg_data_edit', args=(eeg_data.id, 1)))
        self.assertEqual(response.status_code, 200)

        # editing a eeg data file
        self.data = {'date': '30/08/2014', 'action': 'save',
                     'description': 'description of the file',
                     'file_format': file_format.id, 'file': file,
                     'file_format_description': 'teste',
                     'eeg_setting': eeg_setting.id}
        response = self.client.post(reverse('eeg_data_edit', args=(eeg_data.id, 1)), self.data)
        self.assertEqual(response.status_code, 302)

        # list eeg data files
        response = self.client.post(reverse('subject_eeg_view', args=(group.id, subject_mock.id,)))
        self.assertEqual(response.status_code, 200)

        # Show the participants
        response = self.client.get(reverse('subjects', args=(group.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['subject_list']), 1)

        # Trying to delete participant from a group, but there is a eeg file associated
        self.data = {'action': 'remove-' + str(subject_mock.pk)}
        count_before_delete_subject = SubjectOfGroup.objects.all().filter(group=group).count()
        response = self.client.post(reverse('subjects', args=(group.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        count_after_delete_subject = SubjectOfGroup.objects.all().filter(group=group).count()
        self.assertEqual(count_before_delete_subject, count_after_delete_subject)

        # remove eeg data file from a subject
        self.data = {'action': 'remove'}
        response = self.client.post(reverse('eeg_data_view', args=(eeg_data.id, 1)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGData.objects.all().count(), 0)

        # Show the participants
        response = self.client.get(reverse('subjects', args=(group.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['subject_list']), 1)

        # Delete participant from a group
        self.data = {'action': 'remove-' + str(subject_mock.pk)}
        count_before_delete_subject = SubjectOfGroup.objects.all().filter(group=group).count()
        response = self.client.post(reverse('subjects', args=(group.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        count_after_delete_subject = SubjectOfGroup.objects.all().filter(group=group).count()
        self.assertEqual(count_before_delete_subject - 1, count_after_delete_subject)

    def test_subject_upload_consent_file(self):
        """
        Testa o upload de arquivos que corresponde ao formulario de consentimento do participante no experimento
        """

        research_project = ObjectsFactory.create_research_project()

        experiment = ObjectsFactory.create_experiment(research_project)

        group = ObjectsFactory.create_group(experiment)

        patient_mock = self.util.create_patient_mock(changed_by=self.user)

        subject_mock = Subject.objects.all().first()

        if not subject_mock:
            subject_mock = Subject.objects.create(patient=patient_mock)
            subject_mock.patient = patient_mock
            subject_mock.save()

        self.assertEqual(get_object_or_404(Subject, pk=subject_mock.pk), subject_mock)

        subject_group = SubjectOfGroup.objects.all().first()
        if not subject_group:
            subject_group = SubjectOfGroup.objects.create(subject=subject_mock, group=group)

        subject_group.group = group
        subject_group.subject = subject_mock
        subject_group.save()

        # experiment.subjectofexperiment_set.add(subject_group)
        # experiment.save()

        self.assertEqual(get_object_or_404(Experiment, pk=experiment.pk), experiment)
        self.assertEqual(get_object_or_404(SubjectOfGroup, subject=subject_mock, group=group),
                         subject_group)

        # Upload Consent_form
        # Simula click no icone de acesso a pagina de upload do arquivo
        request = self.factory.get(reverse('upload_file', args=[subject_mock.pk, experiment.pk, ]))
        request.user = self.user
        response = upload_file(request, subject_id=subject_mock.pk, group_id=group.pk)

        self.assertEqual(response.status_code, 200)

        # Anexar arquivo
        consent_form_file = SimpleUploadedFile('quiz/consent_form.txt', b'rb')
        self.data = {'action': 'upload', 'consent_form': consent_form_file}
        # url = reverse('upload_file', args=[group.pk, subject_mock.pk])
        # request = self.factory.post(url, self.data)d
        # request.user = self.user
        # response = upload_file(request, subject_id=subject_mock.pk, experiment_id=experiment.pk)
        response = self.client.post(reverse('upload_file', args=[group.pk, subject_mock.pk, ]), self.data, follow=True)
        # print response.content
        self.assertEqual(response.status_code, 200)

        # Remover arquivo
        self.data = {'action': 'remove'}
        response = self.client.post(reverse('upload_file', args=[group.pk, subject_mock.pk, ]), self.data)
        self.assertEqual(response.status_code, 302)


class ResearchProjectTest(TestCase):

    data = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

    def test_research_project_list(self):
        # Check if list of research projects is empty before inserting any.
        response = self.client.get(reverse('research_project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['research_projects']), 0)

        ObjectsFactory.create_research_project()

        # Check if list of research projects returns one item after inserting one.
        response = self.client.get(reverse('research_project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['research_projects']), 1)

    def test_research_project_create(self):
        # Request the research project register screen
        response = self.client.get(reverse('research_project_new'))
        self.assertEqual(response.status_code, 200)

        # POSTing "wrong" action
        self.data = {'action': 'wrong', 'title': 'Research project title', 'start_date': datetime.date.today(),
                     'description': 'Research project description'}
        response = self.client.post(reverse('research_project_new'), self.data)
        self.assertEqual(ResearchProject.objects.all().count(), 0)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Action not available.'))
        self.assertEqual(response.status_code, 200)

        # POSTing missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse('research_project_new'), self.data)
        self.assertEqual(ResearchProject.objects.all().count(), 0)
        self.assertGreaterEqual(len(response.context['research_project_form'].errors), 3)
        self.assertTrue('title' in response.context['research_project_form'].errors)
        self.assertTrue('start_date' in response.context['research_project_form'].errors)
        self.assertTrue('description' in response.context['research_project_form'].errors)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Information not saved.'))
        self.assertEqual(response.status_code, 200)

        # Set research project data
        self.data = {'action': 'save', 'title': 'Research project title', 'start_date': datetime.date.today(),
                     'description': 'Research project description'}

        # Count the number of research projects currently in database
        count_before_insert = ResearchProject.objects.all().count()

        # Add the new research project
        response = self.client.post(reverse('research_project_new'), self.data)
        self.assertEqual(response.status_code, 302)

        # Count the number of research projects currently in database
        count_after_insert = ResearchProject.objects.all().count()

        # Check if it has increased
        self.assertEqual(count_after_insert, count_before_insert + 1)

    def test_research_project_update(self):

        research_project = ObjectsFactory.create_research_project()

        # Create an instance of a GET request.
        request = self.factory.get(reverse('research_project_edit', args=[research_project.pk, ]))
        request.user = self.user

        response = research_project_update(request, research_project_id=research_project.pk)
        self.assertEqual(response.status_code, 200)

        # Update
        self.data = {'action': 'save', 'title': 'New research project title',
                     'start_date': [datetime.date.today() - datetime.timedelta(days=1)],
                     'description': ['New research project description']}
        response = self.client.post(reverse('research_project_edit', args=(research_project.pk,)), self.data,
                                    follow=True)
        self.assertEqual(response.status_code, 200)

    def test_research_project_remove(self):
        # Create a research project to be used in the test
        research_project = ObjectsFactory.create_research_project()

        # Save current number of research projects
        count = ResearchProject.objects.all().count()

        self.data = {'action': 'remove'}
        response = self.client.post(reverse('research_project_view', args=(research_project.pk,)),
                                    self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check if numeber of reserch projets decreased by 1
        self.assertEqual(ResearchProject.objects.all().count(), count - 1)

    def test_research_project_keywords(self):
        # Create a research project to be used in the test
        research_project = ObjectsFactory.create_research_project()

        # Insert keyword
        self.assertEqual(Keyword.objects.all().count(), 0)
        self.assertEqual(research_project.keywords.count(), 0)
        response = self.client.get(reverse('keyword_new', args=(research_project.pk, "test_keyword")), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 1)
        self.assertEqual(research_project.keywords.count(), 1)

        # Add keyword
        keyword = Keyword.objects.create(name="second_test_keyword")
        keyword.save()
        self.assertEqual(Keyword.objects.all().count(), 2)
        self.assertEqual(research_project.keywords.count(), 1)
        response = self.client.get(reverse('keyword_add', args=(research_project.pk, keyword.id)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 2)
        self.assertEqual(research_project.keywords.count(), 2)

        # Create a second research project to be used in the test
        research_project2 = ObjectsFactory.create_research_project()

        # Insert keyword
        response = self.client.get(reverse('keyword_new', args=(research_project2.pk, "third_test_keyword")),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 3)
        self.assertEqual(research_project2.keywords.count(), 1)

        # Add keyword
        response = self.client.get(reverse('keyword_add', args=(research_project2.pk, keyword.id)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 3)
        self.assertEqual(research_project2.keywords.count(), 2)

        # Search keyword using ajax
        self.data = {'search_text': 'test_keyword', 'research_project_id': research_project2.id}
        response = self.client.post(reverse('keywords_search'), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Adicionar nova palavra-chave "test_keyword"')  # Already exists.
        self.assertNotContains(response, "second_test_keyword")  # Already in the project
        self.assertNotContains(response, "third_test_keyword")  # Already in the project
        self.assertContains(response, "test_keyword")  # Should be suggested

        # Add the suggested keyword
        first_quote_index = response.content.index(b'"')
        second_quote_index = response.content.index(b'"', first_quote_index + 1)
        url = response.content[first_quote_index+1:second_quote_index] + b"/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(research_project2.keywords.count(), 3)

        # Remove keyword that is also in another research project
        response = self.client.get(reverse('keyword_remove', args=(research_project2.pk, keyword.id)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 3)
        self.assertEqual(research_project2.keywords.count(), 2)

        # Remove keyword that is not in another research project
        keyword3 = Keyword.objects.get(name="third_test_keyword")
        response = self.client.get(reverse('keyword_remove', args=(research_project2.pk, keyword3.id)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 2)
        self.assertEqual(research_project2.keywords.count(), 1)


class EEGSettingTest(TestCase):

    data = {}

    def setUp(self):

        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        research_project = ObjectsFactory.create_research_project()

        self.experiment = ObjectsFactory.create_experiment(research_project)

    def test_crud_eeg_setting(self):

        # screen to create an eeg_setting
        response = self.client.get(reverse("eeg_setting_new", args=(self.experiment.id,)))
        self.assertEqual(response.status_code, 200)

        name = 'EEG setting name'
        description = 'EEG setting description'
        self.data = {'action': 'save', 'name': name, 'description': description}
        response = self.client.post(reverse("eeg_setting_new", args=(self.experiment.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EEGSetting.objects.filter(name=name, description=description).exists())

        eeg_setting = EEGSetting.objects.filter(name=name, description=description)[0]

        # screen to view an eeg_setting
        response = self.client.get(reverse("eeg_setting_view", args=(eeg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # screen to update an eeg_setting
        response = self.client.get(reverse("eeg_setting_edit", args=(eeg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # update with no changes
        self.data = {'action': 'save', 'name': name, 'description': description}
        response = self.client.post(reverse("eeg_setting_edit", args=(eeg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EEGSetting.objects.filter(name=name, description=description).exists())

        name = 'EEG setting name updated'
        description = 'EEG setting description updated'
        self.data = {'action': 'save', 'name': name, 'description': description}
        response = self.client.post(reverse("eeg_setting_edit", args=(eeg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EEGSetting.objects.filter(name=name, description=description).exists())

        # remove an eeg_setting
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    # def test_eeg_setting_eeg_machine(self):
    #
    #     eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)
    #
    #     manufacturer = ObjectsFactory.create_manufacturer()
    #     eeg_machine = ObjectsFactory.create_eeg_machine(manufacturer)
    #
    #     # screen to an (unexisting) eeg_machine_setting
    #     response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'eeg_machine')))
    #     self.assertEqual(response.status_code, 200)
    #
    #     # create an eeg_machine_setting
    #     self.data = {'action': 'save', 'equipment_selection': eeg_machine.id, 'number_of_channels_used': "2"}
    #     response = self.client.post(reverse("view_eeg_setting_type",
    #                                         args=(eeg_setting.id, 'eeg_machine')), self.data)
    #     self.assertEqual(response.status_code, 302)
    #
    #     # screen to view the eeg_machine_setting
    #     response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'eeg_machine')))
    #     self.assertEqual(response.status_code, 200)
    #
    #     # update the eeg_machine_setting
    #     response = self.client.get(reverse("edit_eeg_setting_type", args=(eeg_setting.id, 'eeg_machine')))
    #     self.assertEqual(response.status_code, 200)
    #
    #     self.data = {'action': 'save', 'equipment_selection': eeg_machine.id, 'number_of_channels_used': "3"}
    #     response = self.client.post(reverse("edit_eeg_setting_type",
    #                                         args=(eeg_setting.id, 'eeg_machine')), self.data)
    #     self.assertEqual(response.status_code, 302)
    #
    #     # remove an eeg_machine_setting
    #     self.data = {'action': 'remove-eeg_machine'}
    #     response = self.client.post(reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data)
    #     self.assertEqual(response.status_code, 302)

    def test_eeg_setting_amplifier(self):
        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)

        manufacturer = ObjectsFactory.create_manufacturer()
        eeg_amplifier = ObjectsFactory.create_amplifier(manufacturer)

        # screen to an (unexisting) eeg_amplifier_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'amplifier')))
        self.assertEqual(response.status_code, 200)

        # create an eeg_amplifier_setting
        self.data = {'action': 'save', 'equipment_selection': eeg_amplifier.id, 'gain': "10",
                     'number_of_channels_used': "2"}
        response = self.client.post(reverse("view_eeg_setting_type",
                                            args=(eeg_setting.id, 'amplifier')), self.data)
        self.assertEqual(response.status_code, 302)

        # screen to view the eeg_amplifier_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'amplifier')))
        self.assertEqual(response.status_code, 200)

        # update the eeg_amplifier_setting
        response = self.client.get(reverse("edit_eeg_setting_type", args=(eeg_setting.id, 'amplifier')))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'equipment_selection': eeg_amplifier.id, 'gain': "20",
                     'number_of_channels_used': "3"}
        response = self.client.post(reverse("edit_eeg_setting_type",
                                            args=(eeg_setting.id, 'amplifier')), self.data)
        self.assertEqual(response.status_code, 302)

        # remove an eeg_amplifier_setting
        self.data = {'action': 'remove-eeg_amplifier'}
        response = self.client.post(reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_eeg_setting_eeg_solution(self):
        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)

        manufacturer = ObjectsFactory.create_manufacturer()
        eeg_solution = ObjectsFactory.create_eeg_solution(manufacturer)

        # screen to an (unexisting) eeg_solution_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'eeg_solution')))
        self.assertEqual(response.status_code, 200)

        # create an eeg_solution_setting
        self.data = {'action': 'save', 'solution_selection': eeg_solution.id}
        response = self.client.post(reverse("view_eeg_setting_type",
                                            args=(eeg_setting.id, 'eeg_solution')), self.data)
        self.assertEqual(response.status_code, 302)

        # screen to view the eeg_solution_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'eeg_solution')))
        self.assertEqual(response.status_code, 200)

        # update the eeg_solution_setting
        response = self.client.get(reverse("edit_eeg_setting_type", args=(eeg_setting.id, 'eeg_solution')))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'solution_selection': eeg_solution.id}
        response = self.client.post(reverse("edit_eeg_setting_type",
                                            args=(eeg_setting.id, 'eeg_solution')), self.data)
        self.assertEqual(response.status_code, 302)

        # remove an eeg_solution_setting
        self.data = {'action': 'remove-eeg_solution'}
        response = self.client.post(reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_eeg_setting_eeg_filter(self):
        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)

        filter_type = ObjectsFactory.create_filter_type()

        # screen to an (unexisting) eeg_filter_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'filter')))
        self.assertEqual(response.status_code, 200)

        # create an eeg_filter_setting
        self.data = {'action': 'save', 'filter_selection': filter_type.id,
                     'high_pass': '80', 'low_pass': '20', 'order': '2'}
        response = self.client.post(reverse("view_eeg_setting_type",
                                            args=(eeg_setting.id, 'filter')), self.data)
        self.assertEqual(response.status_code, 302)

        # screen to view the eeg_filter_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'filter')))
        self.assertEqual(response.status_code, 200)

        # update the eeg_filter_setting
        response = self.client.get(reverse("edit_eeg_setting_type", args=(eeg_setting.id, 'filter')))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'filter_selection': filter_type.id,
                     'high_pass': '90', 'low_pass': '20', 'order': '2'}
        response = self.client.post(reverse("edit_eeg_setting_type",
                                            args=(eeg_setting.id, 'filter')), self.data)
        self.assertEqual(response.status_code, 302)

        # remove an eeg_filter_setting
        self.data = {'action': 'remove-eeg_filter'}
        response = self.client.post(reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_eeg_setting_eeg_net_system(self):
        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)

        manufacturer = ObjectsFactory.create_manufacturer()
        electrode_model = ObjectsFactory.create_electrode_model()
        eeg_electrode_net = ObjectsFactory.create_eeg_electrode_net(manufacturer, electrode_model)
        eeg_localization_system = ObjectsFactory.create_eeg_electrode_localization_system()

        # creating 2 positions to configure be configured when the setting is created
        ObjectsFactory.create_eeg_electrode_position(eeg_localization_system)
        ObjectsFactory.create_eeg_electrode_position(eeg_localization_system)

        ObjectsFactory.create_eeg_electrode_net_system(eeg_electrode_net, eeg_localization_system)

        # screen to an (unexisting) eeg_electrode_net_system_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'eeg_electrode_net_system')))
        self.assertEqual(response.status_code, 200)

        # create an eeg_electrode_net_system_setting
        self.data = {'action': 'save', 'equipment_selection': eeg_electrode_net.id,
                     'localization_system_selection': eeg_localization_system.id}
        response = self.client.post(reverse("view_eeg_setting_type",
                                            args=(eeg_setting.id, 'eeg_electrode_net_system')), self.data)
        self.assertEqual(response.status_code, 302)

        # screen to view the eeg_electrode_net_system_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'eeg_electrode_net_system')))
        self.assertEqual(response.status_code, 200)

        # update the eeg_electrode_net_system_setting with another localization system

        eeg_localization_system_new = ObjectsFactory.create_eeg_electrode_localization_system()
        ObjectsFactory.create_eeg_electrode_position(eeg_localization_system_new)
        ObjectsFactory.create_eeg_electrode_position(eeg_localization_system_new)
        ObjectsFactory.create_eeg_electrode_net_system(eeg_electrode_net, eeg_localization_system_new)

        response = self.client.get(reverse("edit_eeg_setting_type",
                                           args=(eeg_setting.id, 'eeg_electrode_net_system')))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'equipment_selection': eeg_electrode_net.id,
                     'localization_system_selection': eeg_localization_system_new.id}
        response = self.client.post(reverse("edit_eeg_setting_type",
                                            args=(eeg_setting.id, 'eeg_electrode_net_system')), self.data)
        self.assertEqual(response.status_code, 302)

        # configuring the used electrodes
        response = self.client.get(reverse("eeg_electrode_position_setting", args=(eeg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("edit_eeg_electrode_position_setting", args=(eeg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        position_setting_list = []
        for position_setting in eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
            position_setting_list.append(position_setting)

        self.data = {'action': 'save', 'position_status_' + str(position_setting_list[0].id): 'on'}
        response = self.client.post(reverse("edit_eeg_electrode_position_setting",
                                            args=(eeg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # configuring the electrodes models

        response = self.client.get(reverse("eeg_electrode_position_setting_model", args=(eeg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("edit_eeg_electrode_position_setting_model", args=(eeg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'electrode_model_' + str(position_setting_list[0].id): str(electrode_model.id),
                     'electrode_model_' + str(position_setting_list[1].id): str(electrode_model.id)}
        response = self.client.post(reverse("edit_eeg_electrode_position_setting_model",
                                            args=(eeg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # remove an eeg_electrode_net_system_setting
        self.data = {'action': 'remove-eeg_electrode_net_system'}
        response = self.client.post(reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)


class EEGEquipmentRegisterTest(TestCase):

    data = {}

    def setUp(self):

        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

    def test_manufacturer_register(self):

        # list
        response = self.client.get(reverse("manufacturer_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("manufacturer_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save', 'name': name}

        response = self.client.post(reverse("manufacturer_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Manufacturer.objects.all().count(), 1)

        # view
        manufacturer = Manufacturer.objects.all().first()

        response = self.client.get(reverse("manufacturer_view", args=(manufacturer.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("manufacturer_edit", args=(manufacturer.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'name': name}
        response = self.client.post(reverse("manufacturer_edit", args=(manufacturer.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save', 'name': name}
        response = self.client.post(reverse("manufacturer_edit", args=(manufacturer.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("manufacturer_view", args=(manufacturer.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Manufacturer.objects.all().count(), 0)


    def test_amplifier_register(self):
        manufacturer = ObjectsFactory.create_manufacturer()

        # list
        response = self.client.get(reverse("amplifier_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("amplifier_new", args=()))
        self.assertEqual(response.status_code, 200)

        identification = 'Identification'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification,
                     'tag_1': 'on', 'tag_2': 'on'}

        response = self.client.post(reverse("amplifier_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Amplifier.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("amplifier_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Amplifier.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("amplifier_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Amplifier.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        amplifier = Amplifier.objects.all().first()

        response = self.client.get(reverse("amplifier_view", args=(amplifier.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("amplifier_edit", args=(amplifier.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification,
                     'tag_1': 'on', 'tag_2': 'on'}
        response = self.client.post(reverse("amplifier_edit", args=(amplifier.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        identification = 'Identification changed'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification,
                     'tag_1': 'on', 'tag_2': 'on'}
        response = self.client.post(reverse("amplifier_edit", args=(amplifier.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("amplifier_edit", args=(amplifier.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(Amplifier, pk=amplifier.id).identification, identification)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("amplifier_view", args=(amplifier.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Amplifier.objects.all().count(), 0)

    def test_eeg_solution_register(self):
        manufacturer = ObjectsFactory.create_manufacturer()

        # list
        response = self.client.get(reverse("eegsolution_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("eegsolution_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'name': name}

        response = self.client.post(reverse("eegsolution_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGSolution.objects.all().count(), 1)

        # view
        eeg_solution = EEGSolution.objects.all().first()

        response = self.client.get(reverse("eegsolution_view", args=(eeg_solution.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("eegsolution_edit", args=(eeg_solution.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'name': name}
        response = self.client.post(reverse("eegsolution_edit", args=(eeg_solution.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'name': name}
        response = self.client.post(reverse("eegsolution_edit", args=(eeg_solution.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("eegsolution_view", args=(eeg_solution.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGSolution.objects.all().count(), 0)

    def test_filter_type_register(self):
        # list
        response = self.client.get(reverse("filtertype_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("filtertype_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name}

        response = self.client.post(reverse("filtertype_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FilterType.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("filtertype_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FilterType.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("filtertype_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FilterType.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        filter_type = FilterType.objects.all().first()

        response = self.client.get(reverse("filtertype_view", args=(filter_type.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("filtertype_edit", args=(filter_type.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("filtertype_edit", args=(filter_type.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("filtertype_edit", args=(filter_type.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("filtertype_edit", args=(filter_type.id,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(FilterType, pk=filter_type.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("filtertype_view", args=(filter_type.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FilterType.objects.all().count(), 0)

    def test_standardization_system_register(self):
        # list
        response = self.client.get(reverse("standardization_system_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("standardization_system_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name}

        number_of_registers = StandardizationSystem.objects.all().count()

        response = self.client.post(reverse("standardization_system_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(StandardizationSystem.objects.all().count(), number_of_registers + 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("standardization_system_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StandardizationSystem.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("standardization_system_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(StandardizationSystem.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        standardization_system = StandardizationSystem.objects.all().first()

        response = self.client.get(reverse("standardization_system_view", args=(standardization_system.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("standardization_system_edit", args=(standardization_system.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("standardization_system_edit", args=(standardization_system.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("standardization_system_edit", args=(standardization_system.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("standardization_system_edit", args=(standardization_system.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(StandardizationSystem, pk=standardization_system.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("standardization_system_view", args=(standardization_system.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(StandardizationSystem.objects.all().count(), number_of_registers)

    def test_emg_surface_electrode_placement_register(self):

        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        muscle_subdivision_2 = ObjectsFactory.create_muscle_subdivision(muscle)

        # create surface
        response = self.client.get(reverse("emg_electrode_placement_new",
                                           args=(standardization_system.id, 'surface')))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'muscle_subdivision': str(muscle_subdivision.id)}

        number_of_registers = EMGElectrodePlacement.objects.all().count()

        response = self.client.post(reverse("emg_electrode_placement_new",
                                            args=(standardization_system.id, 'surface')), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers + 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("emg_electrode_placement_new",
                                            args=(standardization_system.id, 'surface')), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("emg_electrode_placement_new",
                                            args=(standardization_system.id, 'surface')), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        emg_electrode_placement = EMGElectrodePlacement.objects.filter(
            standardization_system=standardization_system).first()

        response = self.client.get(reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'muscle_subdivision': str(muscle_subdivision.id)}
        response = self.client.post(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        self.data = {'action': 'save',
                     'muscle_subdivision': str(muscle_subdivision_2.id)}
        response = self.client.post(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(EMGElectrodePlacement, pk=emg_electrode_placement.id).muscle_subdivision.id,
                         muscle_subdivision_2.id)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers)

    def test_emg_intramuscular_electrode_placement_register(self):
        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        muscle_subdivision_2 = ObjectsFactory.create_muscle_subdivision(muscle)

        # create surface
        response = self.client.get(reverse("emg_electrode_placement_new",
                                           args=(standardization_system.id, 'intramuscular')))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'muscle_subdivision': str(muscle_subdivision.id)}

        number_of_registers = EMGElectrodePlacement.objects.all().count()

        response = self.client.post(reverse("emg_electrode_placement_new",
                                            args=(standardization_system.id, 'intramuscular')), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers + 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("emg_electrode_placement_new",
                                            args=(standardization_system.id, 'intramuscular')), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("emg_electrode_placement_new",
                                            args=(standardization_system.id, 'intramuscular')), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        emg_electrode_placement = EMGElectrodePlacement.objects.filter(
            standardization_system=standardization_system).first()

        response = self.client.get(reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'muscle_subdivision': str(muscle_subdivision.id)}
        response = self.client.post(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        self.data = {'action': 'save',
                     'muscle_subdivision': str(muscle_subdivision_2.id)}
        response = self.client.post(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(EMGElectrodePlacement, pk=emg_electrode_placement.id).muscle_subdivision.id,
                         muscle_subdivision_2.id)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers)

    def test_emg_needle_electrode_placement_register(self):
        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        muscle_subdivision_2 = ObjectsFactory.create_muscle_subdivision(muscle)

        # create surface
        response = self.client.get(reverse("emg_electrode_placement_new",
                                           args=(standardization_system.id, 'needle')))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'muscle_subdivision': str(muscle_subdivision.id)}

        number_of_registers = EMGElectrodePlacement.objects.all().count()

        response = self.client.post(reverse("emg_electrode_placement_new",
                                            args=(standardization_system.id, 'needle')), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers + 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("emg_electrode_placement_new",
                                            args=(standardization_system.id, 'needle')), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("emg_electrode_placement_new",
                                            args=(standardization_system.id, 'needle')), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        emg_electrode_placement = EMGElectrodePlacement.objects.filter(
            standardization_system=standardization_system).first()

        response = self.client.get(reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'muscle_subdivision': str(muscle_subdivision.id)}
        response = self.client.post(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        self.data = {'action': 'save',
                     'muscle_subdivision': str(muscle_subdivision_2.id)}
        response = self.client.post(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(EMGElectrodePlacement, pk=emg_electrode_placement.id).muscle_subdivision.id,
                         muscle_subdivision_2.id)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EMGElectrodePlacement.objects.all().count(), number_of_registers)

    def test_muscle_register(self):
        # list
        response = self.client.get(reverse("muscle_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("muscle_new", args=()))
        self.assertEqual(response.status_code, 200)

        number_of_registers = Muscle.objects.all().count()

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name}

        response = self.client.post(reverse("muscle_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Muscle.objects.all().count(), number_of_registers + 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("muscle_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Muscle.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("muscle_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Muscle.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        muscle = Muscle.objects.all().first()

        response = self.client.get(reverse("muscle_view", args=(muscle.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("muscle_edit", args=(muscle.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("muscle_edit", args=(muscle.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("muscle_edit", args=(muscle.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("muscle_edit", args=(muscle.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(Muscle, pk=muscle.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("muscle_view", args=(muscle.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Muscle.objects.all().count(), number_of_registers)

    def test_muscle_subdivision_register(self):
        muscle = ObjectsFactory.create_muscle()

        # create
        response = self.client.get(reverse("muscle_subdivision_new", args=(muscle.id,)))
        self.assertEqual(response.status_code, 200)

        number_of_registers = MuscleSubdivision.objects.all().count()

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name}

        response = self.client.post(reverse("muscle_subdivision_new", args=(muscle.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MuscleSubdivision.objects.all().count(), number_of_registers + 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("muscle_subdivision_new", args=(muscle.id,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MuscleSubdivision.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("muscle_subdivision_new", args=(muscle.id,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MuscleSubdivision.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        muscle_subdivision = MuscleSubdivision.objects.filter(muscle=muscle).first()

        response = self.client.get(reverse("muscle_subdivision_view", args=(muscle_subdivision.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("muscle_subdivision_edit", args=(muscle_subdivision.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("muscle_subdivision_edit", args=(muscle_subdivision.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("muscle_subdivision_edit", args=(muscle_subdivision.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("muscle_subdivision_edit", args=(muscle_subdivision.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(MuscleSubdivision, pk=muscle_subdivision.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("muscle_subdivision_view", args=(muscle_subdivision.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MuscleSubdivision.objects.all().count(), number_of_registers)

    def test_muscle_side_register(self):
        muscle = ObjectsFactory.create_muscle()

        # create
        response = self.client.get(reverse("muscle_side_new", args=(muscle.id,)))
        self.assertEqual(response.status_code, 200)

        number_of_registers = MuscleSide.objects.all().count()

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name}

        response = self.client.post(reverse("muscle_side_new", args=(muscle.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MuscleSide.objects.all().count(), number_of_registers + 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("muscle_side_new", args=(muscle.id,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MuscleSide.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("muscle_side_new", args=(muscle.id,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MuscleSide.objects.all().count(), number_of_registers + 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        muscle_side = MuscleSide.objects.filter(muscle=muscle).first()

        response = self.client.get(reverse("muscle_side_view", args=(muscle_side.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("muscle_side_edit", args=(muscle_side.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("muscle_side_edit", args=(muscle_side.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("muscle_side_edit", args=(muscle_side.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("muscle_side_edit", args=(muscle_side.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(MuscleSide, pk=muscle_side.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("muscle_side_view", args=(muscle_side.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MuscleSide.objects.all().count(), number_of_registers)

    def test_software_register(self):
        manufacturer = ObjectsFactory.create_manufacturer()

        # list
        response = self.client.get(reverse("software_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("software_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'name': name}

        response = self.client.post(reverse("software_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Software.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("software_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Software.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("software_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Software.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        software = Software.objects.all().first()

        response = self.client.get(reverse("software_view", args=(software.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("software_edit", args=(software.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'name': name}
        response = self.client.post(reverse("software_edit", args=(software.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'name': name}
        response = self.client.post(reverse("software_edit", args=(software.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("software_edit", args=(software.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(Software, pk=software.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("software_view", args=(software.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Software.objects.all().count(), 0)

    def test_software_version_register(self):

        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)

        # create
        response = self.client.get(reverse("software_version_new", args=(software.id,)))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name}

        response = self.client.post(reverse("software_version_new", args=(software.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SoftwareVersion.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("software_version_new", args=(software.id,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SoftwareVersion.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("software_version_new", args=(software.id,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SoftwareVersion.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        software_version = SoftwareVersion.objects.filter(software=software).first()

        response = self.client.get(reverse("software_version_view", args=(software_version.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("software_version_edit", args=(software_version.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("software_version_edit", args=(software_version.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("software_version_edit", args=(software_version.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("software_version_edit", args=(software_version.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(SoftwareVersion, pk=software_version.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("software_version_view", args=(software_version.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SoftwareVersion.objects.all().count(), 0)

    def test_electrode_model_register(self):
        # list
        response = self.client.get(reverse("electrodemodel_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("electrodemodel_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name,
                     'electrode_type': 'surface'}
        response = self.client.post(reverse("electrodemodel_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ElectrodeModel.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("electrodemodel_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ElectrodeModel.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("electrodemodel_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ElectrodeModel.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        electrode_model = ElectrodeModel.objects.all().first()

        response = self.client.get(reverse("electrodemodel_view", args=(electrode_model.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("electrodemodel_edit", args=(electrode_model.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name,
                     'electrode_type': 'surface'}
        response = self.client.post(reverse("electrodemodel_edit", args=(electrode_model.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name,
                     'electrode_type': 'surface'}
        response = self.client.post(reverse("electrodemodel_edit", args=(electrode_model.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("electrodemodel_edit", args=(electrode_model.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(ElectrodeModel, pk=electrode_model.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("electrodemodel_view", args=(electrode_model.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ElectrodeModel.objects.all().count(), 0)

    def test_material_register(self):
        # list
        response = self.client.get(reverse("material_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("material_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("material_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Material.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("material_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Material.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("material_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Material.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        material = Material.objects.all().first()

        response = self.client.get(reverse("material_view", args=(material.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("material_edit", args=(material.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("material_edit", args=(material.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("material_edit", args=(material.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("material_edit", args=(material.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(Material, pk=material.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("material_view", args=(material.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Material.objects.all().count(), 0)

    def test_electrode_net_register(self):
        manufacturer = ObjectsFactory.create_manufacturer()
        electrode_model = ObjectsFactory.create_electrode_model()

        # list
        response = self.client.get(reverse("eegelectrodenet_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("eegelectrodenet_new", args=()))
        self.assertEqual(response.status_code, 200)

        identification = 'Identification'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification,
                     'electrode_model_default': str(electrode_model.id)
                    }

        response = self.client.post(reverse("eegelectrodenet_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("eegelectrodenet_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("eegelectrodenet_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        electrode_net = EEGElectrodeNet.objects.all().first()

        response = self.client.get(reverse("eegelectrodenet_view", args=(electrode_net.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("eegelectrodenet_edit", args=(electrode_net.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification,
                     'electrode_model_default': str(electrode_model.id)}
        response = self.client.post(reverse("eegelectrodenet_edit", args=(electrode_net.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        identification = 'Identification changed'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification,
                     'electrode_model_default': str(electrode_model.id)}
        response = self.client.post(reverse("eegelectrodenet_edit", args=(electrode_net.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("eegelectrodenet_edit", args=(electrode_net.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(EEGElectrodeNet, pk=electrode_net.id).identification, identification)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("eegelectrodenet_view", args=(electrode_net.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 0)

    def test_electrode_net_register_cap(self):

        manufacturer = ObjectsFactory.create_manufacturer()
        electrode_model = ObjectsFactory.create_electrode_model()
        material = ObjectsFactory.create_material()
        material_2 = ObjectsFactory.create_material()

        electrode_localization_system = ObjectsFactory.create_eeg_electrode_localization_system()
        electrode_localization_system_2 = ObjectsFactory.create_eeg_electrode_localization_system()

        # create a electrode_net (cap)

        response = self.client.get(reverse("eegelectrodenet_new", args=()))
        self.assertEqual(response.status_code, 200)

        identification = 'Identification'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification,
                     'electrode_model_default': str(electrode_model.id),
                     'cap_flag': 'on',
                     'material': str(material.id),
                     'localization_system_' + str(electrode_localization_system.id): 'on'}

        response = self.client.post(reverse("eegelectrodenet_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 1)
        self.assertEqual(EEGElectrodeCap.objects.all().count(), 1)

        # view
        electrode_net = EEGElectrodeCap.objects.all().first()

        response = self.client.get(reverse("eegelectrodenet_view", args=(electrode_net.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("eegelectrodenet_edit", args=(electrode_net.id,)))
        self.assertEqual(response.status_code, 200)

        identification = 'Identification changed'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification,
                     'electrode_model_default': str(electrode_model.id),
                     'cap_flag': 'on',
                     'material': str(material_2.id),
                     'localization_system_' + str(electrode_localization_system_2.id): 'on'}
        response = self.client.post(reverse("eegelectrodenet_edit", args=(electrode_net.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("eegelectrodenet_view", args=(electrode_net.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 0)

    def test_cap_size_register(self):

        manufacturer = ObjectsFactory.create_manufacturer()
        electrode_model = ObjectsFactory.create_electrode_model()
        eeg_electrode_cap = ObjectsFactory.create_eeg_electrode_cap(manufacturer, electrode_model)

        # create
        response = self.client.get(reverse("eegelectrodenet_add_size", args=(eeg_electrode_cap.id,)))
        self.assertEqual(response.status_code, 200)

        size = 'Size'
        self.data = {'action': 'save',
                     'size': size}

        response = self.client.post(reverse("eegelectrodenet_add_size", args=(eeg_electrode_cap.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGCapSize.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("eegelectrodenet_add_size", args=(eeg_electrode_cap.id,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGCapSize.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("eegelectrodenet_add_size", args=(eeg_electrode_cap.id,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGCapSize.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        cap_size = EEGCapSize.objects.filter(eeg_electrode_cap=eeg_electrode_cap).first()

        response = self.client.get(reverse("eegelectrodenet_cap_size_view", args=(cap_size.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("eegelectrodenet_cap_size_edit", args=(cap_size.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'size': size}
        response = self.client.post(reverse("eegelectrodenet_cap_size_edit", args=(cap_size.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        size = 'Size changed'
        self.data = {'action': 'save',
                     'size': size}
        response = self.client.post(reverse("eegelectrodenet_cap_size_edit", args=(cap_size.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("eegelectrodenet_cap_size_edit", args=(cap_size.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(EEGCapSize, pk=cap_size.id).size, size)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("eegelectrodenet_cap_size_view", args=(cap_size.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGCapSize.objects.all().count(), 0)

    def test_ad_converter_register(self):
        manufacturer = ObjectsFactory.create_manufacturer()

        # list
        response = self.client.get(reverse("ad_converter_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("ad_converter_new", args=()))
        self.assertEqual(response.status_code, 200)

        identification = 'Identification'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification}

        response = self.client.post(reverse("ad_converter_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ADConverter.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("ad_converter_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ADConverter.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("ad_converter_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ADConverter.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        ad_converter = ADConverter.objects.all().first()

        response = self.client.get(reverse("ad_converter_view", args=(ad_converter.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("ad_converter_edit", args=(ad_converter.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification}
        response = self.client.post(reverse("ad_converter_edit", args=(ad_converter.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        identification = 'Identification changed'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification}
        response = self.client.post(reverse("ad_converter_edit", args=(ad_converter.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("ad_converter_edit", args=(ad_converter.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(ADConverter, pk=ad_converter.id).identification, identification)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("ad_converter_view", args=(ad_converter.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ADConverter.objects.all().count(), 0)

    def test_coil_model_register(self):
        coil_shape = ObjectsFactory.create_coil_shape()

        # list
        response = self.client.get(reverse("coil_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("coil_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name,
                     'coil_shape': str(coil_shape.id)}

        response = self.client.post(reverse("coil_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CoilModel.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("coil_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CoilModel.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("coil_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CoilModel.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        coil_model = CoilModel.objects.all().first()

        response = self.client.get(reverse("coil_view", args=(coil_model.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("coil_edit", args=(coil_model.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name,
                     'coil_shape': str(coil_shape.id)}
        response = self.client.post(reverse("coil_edit", args=(coil_model.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name,
                     'coil_shape': str(coil_shape.id)}
        response = self.client.post(reverse("coil_edit", args=(coil_model.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("coil_edit", args=(coil_model.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(CoilModel, pk=coil_model.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("coil_view", args=(coil_model.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CoilModel.objects.all().count(), 0)

    def test_tms_device_register(self):
        manufacturer = ObjectsFactory.create_manufacturer()
        coil_shape = ObjectsFactory.create_coil_shape()
        coil_model = ObjectsFactory.create_coil_model(CoilShape.objects.all().first())

        # list
        response = self.client.get(reverse("tmsdevice_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("tmsdevice_new", args=()))
        self.assertEqual(response.status_code, 200)

        identification = 'Identification'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification,
                     'coil_model': str(coil_model.id)}

        response = self.client.post(reverse("tmsdevice_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TMSDevice.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("tmsdevice_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TMSDevice.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("tmsdevice_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TMSDevice.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        tms_device = TMSDevice.objects.all().first()

        response = self.client.get(reverse("tmsdevice_view", args=(tms_device.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("tmsdevice_edit", args=(tms_device.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification,
                     'coil_model': str(coil_model.id)}
        response = self.client.post(reverse("tmsdevice_edit", args=(tms_device.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        identification = 'Identification changed'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification,
                     'coil_model': str(coil_model.id)}
        response = self.client.post(reverse("tmsdevice_edit", args=(tms_device.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("tmsdevice_edit", args=(tms_device.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(TMSDevice, pk=tms_device.id).identification, identification)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("tmsdevice_view", args=(tms_device.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TMSDevice.objects.all().count(), 0)

    def test_eeg_electrode_localization_system_register(self):

        # list
        response = self.client.get(reverse("eeg_electrode_localization_system_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("eeg_electrode_localization_system_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name}

        response = self.client.post(reverse("eeg_electrode_localization_system_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeLocalizationSystem.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("eeg_electrode_localization_system_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodeLocalizationSystem.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("eeg_electrode_localization_system_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodeLocalizationSystem.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        eeg_electrode_localization_system = EEGElectrodeLocalizationSystem.objects.all().first()

        response = self.client.get(reverse("eeg_electrode_localization_system_view",
                                           args=(eeg_electrode_localization_system.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("eeg_electrode_localization_system_edit",
                                           args=(eeg_electrode_localization_system.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("eeg_electrode_localization_system_edit",
                                            args=(eeg_electrode_localization_system.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("eeg_electrode_localization_system_edit",
                                            args=(eeg_electrode_localization_system.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("eeg_electrode_localization_system_edit",
                                            args=(eeg_electrode_localization_system.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(EEGElectrodeLocalizationSystem,
                                           pk=eeg_electrode_localization_system.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("eeg_electrode_localization_system_view",
                                            args=(eeg_electrode_localization_system.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeLocalizationSystem.objects.all().count(), 0)

    def test_eeg_electrode_position_register(self):
        eeg_electrode_localization_system = ObjectsFactory.create_eeg_electrode_localization_system()

        # create
        response = self.client.get(reverse("eeg_electrode_position_create",
                                           args=(eeg_electrode_localization_system.id,)))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name}

        response = self.client.post(reverse("eeg_electrode_position_create",
                                            args=(eeg_electrode_localization_system.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodePosition.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {'action': 'save'}

        response = self.client.post(reverse("eeg_electrode_position_create",
                                            args=(eeg_electrode_localization_system.id,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodePosition.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Information not saved.'))

        # create with wrong action
        self.data = {'action': 'wrong'}

        response = self.client.post(reverse("eeg_electrode_position_create",
                                            args=(eeg_electrode_localization_system.id,)), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodePosition.objects.all().count(), 1)
        self.assertEqual(str(list(response.context['messages'])[-1]), _('Action not available.'))

        # view
        eeg_electrode_position = EEGElectrodePosition.objects.filter(
            eeg_electrode_localization_system=eeg_electrode_localization_system).first()

        response = self.client.get(reverse("eeg_electrode_position_view", args=(eeg_electrode_position.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("eeg_electrode_position_edit", args=(eeg_electrode_position.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("eeg_electrode_position_edit", args=(eeg_electrode_position.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("eeg_electrode_position_edit", args=(eeg_electrode_position.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse("eeg_electrode_position_edit", args=(eeg_electrode_position.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(EEGElectrodePosition, pk=eeg_electrode_position.id).name, name)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("eeg_electrode_position_view", args=(eeg_electrode_position.id,)),
                                    self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodePosition.objects.all().count(), 0)


class EMGSettingTest(TestCase):

    data = {}

    def setUp(self):

        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        research_project = ObjectsFactory.create_research_project()

        self.experiment = ObjectsFactory.create_experiment(research_project)

        self.manufacturer = ObjectsFactory.create_manufacturer()
        self.software = ObjectsFactory.create_software(self.manufacturer)
        self.software_version = ObjectsFactory.create_software_version(self.software)
        self.tag_emg = ObjectsFactory.create_tag('EMG')

    def test_crud_emg_setting(self):

        # create emg setting
        response = self.client.get(reverse("emg_setting_new", args=(self.experiment.id,)))
        self.assertEqual(response.status_code, 200)

        name = 'EMG setting name'
        description = 'EMG setting description'
        self.data = {'action': 'save', 'name': name, 'description': description,
                     'software_version': self.software_version.id}
        response = self.client.post(reverse("emg_setting_new", args=(self.experiment.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EMGSetting.objects.filter(name=name, description=description).exists())

        emg_setting = EMGSetting.objects.filter(name=name, description=description)[0]

        # view an emg setting
        response = self.client.get(reverse("emg_setting_view", args=(emg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # update an emg setting
        response = self.client.get(reverse("emg_setting_edit", args=(emg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # update with no changes
        self.data = {'action': 'save', 'name': name, 'description': description,
                     'software_version': self.software_version.id}
        response = self.client.post(reverse("emg_setting_edit", args=(emg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EMGSetting.objects.filter(name=name, description=description).exists())

        name = 'EMG setting name updated'
        description = 'EMG setting description updated'
        self.data = {'action': 'save', 'name': name, 'description': description,
                     'software_version': self.software_version.id}
        response = self.client.post(reverse("emg_setting_edit", args=(emg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(EMGSetting.objects.filter(name=name, description=description).exists())

        # remove an emg setting
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("emg_setting_view", args=(emg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_emg_setting_digital_filter(self):
        emg_setting = ObjectsFactory.create_emg_setting(self.experiment, self.software_version)

        filter_type = ObjectsFactory.create_filter_type()

        # create an emg digital filter setting
        self.data = {'action': 'save', 'filter_type': filter_type.id,
                     'high_pass': '80', 'low_pass': '20', 'band_pass':  '7',  'order': '2', 'notch': '5'}
        response = self.client.post(reverse("emg_setting_digital_filter", args=(emg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # screen to view the emg digital filter setting
        response = self.client.get(reverse("emg_setting_digital_filter", args=(emg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # update the emg digital filter setting
        response = self.client.get(reverse("emg_setting_digital_filter_edit", args=(emg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'filter_type': filter_type.id,
                     'high_pass': '90', 'low_pass': '20', 'order': '2', 'notch': '7'}
        response = self.client.post(reverse("emg_setting_digital_filter_edit",
                                            args=(emg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # remove an emg digital filter setting
        self.data = {'action': 'remove-digital_filter'}
        response = self.client.post(reverse("emg_setting_view", args=(emg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_emg_setting_ad_converter(self):
        emg_setting = ObjectsFactory.create_emg_setting(self.experiment, self.software_version)
        manufacturer = ObjectsFactory.create_manufacturer()

        ad_converter = ObjectsFactory.create_ad_converter(manufacturer)

        # create an emg AD converter setting
        self.data = {'action': 'save', 'ad_converter': ad_converter.id, 'sampling_rate': '10'}
        response = self.client.post(reverse("emg_setting_ad_converter", args=(emg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # screen to view the emg AD converter  setting
        response = self.client.get(reverse("emg_setting_ad_converter", args=(emg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # update the emg AD converter  setting
        response = self.client.get(reverse("emg_setting_ad_converter_edit", args=(emg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'ad_converter': ad_converter.id, 'sampling_rate': '20'}
        response = self.client.post(reverse("emg_setting_ad_converter_edit",
                                            args=(emg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # remove an emg AD converter setting
        self.data = {'action': 'remove-ad_converter'}
        response = self.client.post(reverse("emg_setting_view", args=(emg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_emg_setting_electrode(self):
        emg_setting = ObjectsFactory.create_emg_setting(self.experiment, self.software_version)
        electrode_model = ObjectsFactory.create_electrode_model()
        tag_emg = Tag.objects.get(name="EMG")
        electrode_model.tags.add(tag_emg)

        electrode_placement = ObjectsFactory.create_emg_electrode_placement()
        muscle_side = ObjectsFactory.create_muscle_side(electrode_placement.muscle_subdivision.muscle)

        self.data = {'action': 'save', 'electrode': electrode_model.id,
                     'emg_electrode_placement': electrode_placement.id,
                     'remarks': "Remarks", 'muscle_side': muscle_side.id}

        response = self.client.post(reverse("emg_setting_electrode_add", args=(emg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        emg_electrode_setting = EMGElectrodeSetting.objects.all().first()

        # screen to view the emg electrode  setting
        response = self.client.get(reverse("emg_electrode_setting_view", args=(emg_electrode_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # update the emg electrode setting
        response = self.client.get(reverse("emg_electrode_setting_edit", args=(emg_electrode_setting.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'electrode': electrode_model.id,
                     'emg_electrode_placement': electrode_placement.id,
                     'remarks': "Remarks", 'muscle_side': muscle_side.id}

        response = self.client.post(reverse("emg_electrode_setting_edit",
                                            args=(emg_electrode_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # remove an emg electrode setting
        self.data = {'action': 'remove-electrode-' + str(emg_electrode_setting.id)}

        response = self.client.post(reverse("emg_setting_view", args=(emg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_emg_setting_preamplifier(self):
        emg_setting = ObjectsFactory.create_emg_setting(self.experiment, self.software_version)
        manufacturer = ObjectsFactory.create_manufacturer()
        amplifier = ObjectsFactory.create_amplifier(manufacturer)
        tag_emg = Tag.objects.get(name="EMG")
        amplifier.tags.add(tag_emg)

        electrode_model = ObjectsFactory.create_electrode_model()

        emg_electrode_setting = ObjectsFactory.create_emg_electrode_setting(emg_setting, electrode_model)

        electrode_placement = ObjectsFactory.create_emg_electrode_placement()
        muscle_side = ObjectsFactory.create_muscle_side(electrode_placement.muscle_subdivision.muscle)
        ObjectsFactory.create_emg_electrode_placement_setting(emg_electrode_setting, electrode_placement, muscle_side)

        # create an emg  preamplifier setting
        self.data = {'action': 'save', 'amplifier': amplifier.id, 'gain': "10"}
        response = self.client.post(reverse("emg_electrode_setting_preamplifier",
                                            args=(emg_electrode_setting.id, )), self.data)
        self.assertEqual(response.status_code, 302)

        # screen to view the emg  preamplifier setting
        response = self.client.get(reverse("emg_electrode_setting_preamplifier", args=(emg_electrode_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # update the emg  preamplifier setting
        response = self.client.get(reverse("emg_electrode_setting_preamplifier_edit",
                                           args=(emg_electrode_setting.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'amplifier': amplifier.id, 'gain': "20"}
        response = self.client.post(reverse("emg_electrode_setting_preamplifier_edit",
                                            args=(emg_electrode_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # remove an emg  preamplifier setting
        self.data = {'action': 'remove-preamplifier'}
        response = self.client.post(reverse("emg_electrode_setting_view",
                                            args=(emg_electrode_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_emg_setting_amplifier(self):
        emg_setting = ObjectsFactory.create_emg_setting(self.experiment, self.software_version)
        manufacturer = ObjectsFactory.create_manufacturer()
        amplifier = ObjectsFactory.create_amplifier(manufacturer)
        tag_emg = Tag.objects.get(name="EMG")
        amplifier.tags.add(tag_emg)

        electrode_model = ObjectsFactory.create_electrode_model()
        tag_emg = Tag.objects.get(name="EMG")
        electrode_model.tags.add(tag_emg)

        emg_electrode_setting = ObjectsFactory.create_emg_electrode_setting(emg_setting, electrode_model)

        # create an emg amplifier setting
        self.data = {'action': 'save', 'amplifier': amplifier.id, 'gain': "10"}
        response = self.client.post(reverse("emg_electrode_setting_amplifier",
                                            args=(emg_electrode_setting.id, )), self.data)
        self.assertEqual(response.status_code, 302)

        # screen to view the emg amplifier setting
        response = self.client.get(reverse("emg_electrode_setting_amplifier", args=(emg_electrode_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # update the emg amplifier setting
        response = self.client.get(reverse("emg_electrode_setting_amplifier_edit",
                                           args=(emg_electrode_setting.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'amplifier': amplifier.id, 'gain': "20"}
        response = self.client.post(reverse("emg_electrode_setting_amplifier_edit",
                                            args=(emg_electrode_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # remove an emg  amplifier setting

        electrode_placement = ObjectsFactory.create_emg_electrode_placement()
        muscle_side = ObjectsFactory.create_muscle_side(electrode_placement.muscle_subdivision.muscle)
        ObjectsFactory.create_emg_electrode_placement_setting(emg_electrode_setting, electrode_placement, muscle_side)
        self.data = {'action': 'remove-amplifier'}
        response = self.client.post(reverse("emg_electrode_setting_view",
                                            args=(emg_electrode_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)


class PublicationTest(TestCase):

    data = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

    def test_publication_list(self):
        # Check if list of publications is empty before inserting any.
        response = self.client.get(reverse('publication_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['publications']), 0)

        ObjectsFactory.create_research_project()

        Publication.objects.create(title="Publication title", citation="Publication citation")

        # Check if list of publications returns one item after inserting one.
        response = self.client.get(reverse('publication_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['publications']), 1)

    def test_publication_create(self):
        # Request the publication register screen
        response = self.client.get(reverse('publication_new'))
        self.assertEqual(response.status_code, 200)

        # POSTing "wrong" action
        self.data = {'action': 'wrong', 'title': 'Publication title', 'citation': 'Publication citation'}
        response = self.client.post(reverse('publication_new'), self.data)
        self.assertEqual(Publication.objects.all().count(), 0)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Action not available.'))
        self.assertEqual(response.status_code, 200)

        # POSTing missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse('publication_new'), self.data)
        self.assertEqual(Publication.objects.all().count(), 0)
        self.assertGreaterEqual(len(response.context['publication_form'].errors), 2)
        self.assertTrue('title' in response.context['publication_form'].errors)
        self.assertTrue('citation' in response.context['publication_form'].errors)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Information not saved.'))
        self.assertEqual(response.status_code, 200)

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)

        # Set publication data
        self.data = {'action': 'save', 'title': 'Publication title', 'citation': 'Publication citation',
                     'experiments': str(experiment.id)}

        # Count the number of publication currently in database
        count_before_insert = Publication.objects.all().count()

        # Add the new publication
        response = self.client.post(reverse('publication_new'), self.data)
        self.assertEqual(response.status_code, 302)

        # Count the number of publication currently in database
        count_after_insert = Publication.objects.all().count()

        # Check if it has increased
        self.assertEqual(count_after_insert, count_before_insert + 1)

    def test_publication_update(self):

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        publication = ObjectsFactory.create_publication([experiment])

        # Create an instance of a GET request.
        request = self.factory.get(reverse('publication_edit', args=[publication.pk, ]))
        request.user = self.user

        response = publication_update(request, publication_id=publication.pk)
        self.assertEqual(response.status_code, 200)

        # Update with changes
        self.data = {'action': 'save', 'title': 'New publication title',
                     'citation': 'New citation',
                     'experiments': str(experiment.id)}
        response = self.client.post(reverse('publication_edit', args=(publication.pk,)), self.data, follow=True)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Publication updated successfully.'))
        self.assertEqual(response.status_code, 200)

        # Update with no changes
        response = self.client.post(reverse('publication_edit', args=(publication.pk,)), self.data, follow=True)
        self.assertEqual(str(list(response.context['messages'])[0]), _('There is no changes to save.'))
        self.assertEqual(response.status_code, 200)

    def test_publication_remove(self):
        # Create a publication to be used in the test
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        publication = ObjectsFactory.create_publication([experiment])

        # Save current number of publications
        count = Publication.objects.all().count()

        self.data = {'action': 'remove'}
        response = self.client.post(reverse('publication_view', args=(publication.pk,)),
                                    self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check if number of publications decreased by 1
        self.assertEqual(Publication.objects.all().count(), count - 1)

    def test_publication_add_experiment(self):
        # Create a publication to be used in the test
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        publication = ObjectsFactory.create_publication([])

        # Create an instance of a GET request.
        request = self.factory.get(reverse('publication_add_experiment', args=[publication.pk, ]))
        request.user = self.user

        response = publication_add_experiment(request, publication_id=publication.pk)
        self.assertEqual(response.status_code, 200)

        # Add an experiment to the publication
        self.data = {'action': 'add-experiment',
                     'experiment_selected': str(experiment.id)}
        response = self.client.post(reverse('publication_add_experiment', args=(publication.pk,)),
                                    self.data, follow=True)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Experiment included successfully.'))
        self.assertEqual(response.status_code, 200)

        # Try to add the same experiment to the publication
        response = self.client.post(reverse('publication_add_experiment', args=(publication.pk,)),
                                    self.data, follow=True)
        self.assertEqual(str(list(response.context['messages'])[0]),
                         _('Experiment already included in the publication.'))
        self.assertEqual(response.status_code, 200)

        # Save current number of experiments related to the publication
        count = publication.experiments.count()

        self.data = {'action': 'remove-' + str(experiment.id)}
        response = self.client.post(reverse('publication_view', args=(publication.pk,)),
                                    self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check if number of publications decreased by 1
        self.assertEqual(publication.experiments.count(), count - 1)


class ContextTreeTest(TestCase):

    data = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

    def test_context_tree_list(self):

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)

        # Check if list of context trees is empty before inserting any.
        response = self.client.get(reverse('experiment_view', args=[experiment.pk, ]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['context_tree_list']), 0)

        ContextTree.objects.create(experiment=experiment, name='Context name', description='Context description')

        # Check if list of context trees returns one item after inserting one.
        response = self.client.get(reverse('experiment_view', args=[experiment.pk, ]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['context_tree_list']), 1)

    def test_context_tree_create(self):

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)

        # Request the context tree register screen
        response = self.client.get(reverse('context_tree_new', args=[experiment.pk, ]))
        self.assertEqual(response.status_code, 200)

        # POSTing "wrong" action
        self.data = {'action': 'wrong', 'name': 'Context tree name', 'description': 'Context tree description'}
        response = self.client.post(reverse('context_tree_new', args=[experiment.pk, ]), self.data)
        self.assertEqual(ContextTree.objects.all().count(), 0)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Action not available.'))
        self.assertEqual(response.status_code, 200)

        # POSTing missing information
        self.data = {'action': 'save'}
        response = self.client.post(reverse('context_tree_new', args=[experiment.pk, ]), self.data)
        self.assertEqual(ContextTree.objects.all().count(), 0)
        self.assertGreaterEqual(len(response.context['context_tree_form'].errors), 2)
        self.assertTrue('name' in response.context['context_tree_form'].errors)
        self.assertTrue('description' in response.context['context_tree_form'].errors)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Information not saved.'))
        self.assertEqual(response.status_code, 200)

        # Set context tree data
        self.data = {'action': 'save', 'name': 'Context tree name', 'description': 'Context tree description'}

        # Count the number of context tree currently in database
        count_before_insert = ContextTree.objects.all().count()

        # Add the new context tree
        response = self.client.post(reverse('context_tree_new', args=[experiment.pk, ]), self.data)
        self.assertEqual(response.status_code, 302)

        # Count the number of context tree currently in database
        count_after_insert = ContextTree.objects.all().count()

        # Check if it has increased
        self.assertEqual(count_after_insert, count_before_insert + 1)

    def test_context_tree_update(self):

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        context_tree = ObjectsFactory.create_context_tree(experiment)

        # Create an instance of a GET request.
        request = self.factory.get(reverse('context_tree_edit', args=[context_tree.pk, ]))
        request.user = self.user

        response = context_tree_update(request, context_tree_id=context_tree.pk)
        self.assertEqual(response.status_code, 200)

        # Update with changes
        self.data = {'action': 'save', 'name': 'New context tree name',
                     'description': 'New context tree description'}
        response = self.client.post(reverse('context_tree_edit', args=(context_tree.pk,)), self.data, follow=True)
        self.assertEqual(str(list(response.context['messages'])[0]), _('Context tree updated successfully.'))
        self.assertEqual(response.status_code, 200)

        # Update with no changes
        response = self.client.post(reverse('context_tree_edit', args=(context_tree.pk,)), self.data, follow=True)
        self.assertEqual(str(list(response.context['messages'])[0]), _('There is no changes to save.'))
        self.assertEqual(response.status_code, 200)

    def test_context_tree_remove(self):
        # Create a context tree to be used in the test
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        context_tree = ObjectsFactory.create_context_tree(experiment)

        # Save current number of context trees
        count = ContextTree.objects.all().count()

        self.data = {'action': 'remove'}
        response = self.client.post(reverse('context_tree_view', args=(context_tree.pk,)),
                                    self.data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check if number of context trees decreased by 1
        self.assertEqual(ContextTree.objects.all().count(), count - 1)
