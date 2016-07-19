# coding=utf-8
import datetime

from django.test import TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from .models import Experiment, Group, Subject, \
    QuestionnaireResponse, SubjectOfGroup, ComponentConfiguration, ResearchProject, Keyword, StimulusType, \
    Component, Task, TaskForTheExperimenter, Stimulus, Instruction, Pause, Questionnaire, Block, \
    EEG, FileFormat, EEGData, EEGSetting, DataConfigurationTree, EMG, EEGMachine, Manufacturer, Tag, Amplifier, \
    EEGSolution, FilterType, ElectrodeModel, EEGElectrodeNet, EEGElectrodeNetSystem, EEGElectrodeLocalizationSystem, \
    EEGElectrodePosition, Material, EMGSetting, Software, SoftwareVersion
from .views import experiment_update, upload_file, research_project_update

from patient.models import ClassificationOfDiseases
from patient.tests import UtilTests

from survey.models import Survey
from survey.abc_search_engine import Questionnaires

from custom_user.views import User

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
    def create_research_project():
        """
        Create a research project to be used in the test
        :return: research project
        """
        research_project = ResearchProject.objects.create(title="Research project title",
                                                          start_date=datetime.date.today(),
                                                          description="Research project description")
        research_project.save()
        return research_project

    @staticmethod
    def create_experiment(research_project):
        """
        Create an experiment to be used in the test
        :param research_project: research project
        :return: experiment
        """
        experiment = Experiment.objects.create(research_project_id=research_project.id,
                                               title="Experimento-Update",
                                               description="Descricao do Experimento-Update")
        experiment.save()
        return experiment

    @staticmethod
    def create_eeg_setting(experiment):
        eeg_setting = EEGSetting.objects.create(experiment=experiment,
                                                name='EEG-Setting name',
                                                description='EEG-Setting description')
        eeg_setting.save()
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
    def create_group(experiment, experimental_protocol=None):
        """
        :param experiment: experiment
        :param experimental_protocol: experimental protocol
        :return: group
        """
        group = Group.objects.create(experiment=experiment,
                                     title="Group-update",
                                     description="Descricao do Group-update",
                                     experimental_protocol=experimental_protocol)
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
        manufacturer.save()
        return manufacturer

    @staticmethod
    def create_eeg_machine(manufacturer):
        eeg_machine = EEGMachine.objects.create(
            manufacturer=manufacturer,
            equipment_type="eeg_machine",
            identification="EEG machine identification"
        )
        eeg_machine.save()
        return eeg_machine

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
            name="Solution name"
        )
        filter_type.save()
        return filter_type

    @staticmethod
    def create_electrode_model():
        electrode_model = ElectrodeModel.objects.create(
            name="Electrode Model name"
        )
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
        eeg_electrode_net_system = EEGElectrodeLocalizationSystem.objects.create(
            name="Localization System name"
        )
        eeg_electrode_net_system.save()
        return eeg_electrode_net_system

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
    def system_authentication(instance):
        user = User.objects.create_user(username=USER_USERNAME, email='test@dummy.com', password=USER_PWD)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        factory = RequestFactory()
        logged = instance.client.login(username=USER_USERNAME, password=USER_PWD)
        return logged, user, factory


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
            component_configuration = ComponentConfiguration.objects.create(
                name='ComponentConfiguration',
                parent=block,
                component=questionnaire
            )
            component_configuration.save()

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

        # Insert subject in the group
        util = UtilTests()
        patient_mock = util.create_patient_mock(user=self.user)

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
        patient_mock = util.create_patient_mock(user=self.user)

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

        # # View the responses
        # get_data = {'origin': "experiment_questionnaire"}
        # response = self.client.get(reverse('questionnaire_response_view',
        #                                    args=[questionnaire_response.pk, ]), data=get_data)
        #
        # self.assertEqual(response.status_code, 200)


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

        patient_mock = self.util.create_patient_mock(user=self.user)
        self.data = {SEARCH_TEXT: 'Pacient', 'experiment_id': experiment.id, 'group_id': group.id}

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
        patient_mock = util.create_patient_mock(user=self.user)

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
        patient_mock = util.create_patient_mock(user=self.user)

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
        patient_mock = util.create_patient_mock(user=self.user)

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
                     'file_format': file_format.id, 'file': eeg_data.file,
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

        patient_mock = self.util.create_patient_mock(user=self.user)

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

    def test_eeg_setting_eeg_machine(self):

        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)

        manufacturer = ObjectsFactory.create_manufacturer()
        eeg_machine = ObjectsFactory.create_eeg_machine(manufacturer)

        # screen to an (unexisting) eeg_machine_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'eeg_machine')))
        self.assertEqual(response.status_code, 200)

        # create an eeg_machine_setting
        self.data = {'action': 'save', 'equipment_selection': eeg_machine.id, 'number_of_channels_used': "2"}
        response = self.client.post(reverse("view_eeg_setting_type",
                                            args=(eeg_setting.id, 'eeg_machine')), self.data)
        self.assertEqual(response.status_code, 302)

        # screen to view the eeg_machine_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'eeg_machine')))
        self.assertEqual(response.status_code, 200)

        # update the eeg_machine_setting
        response = self.client.get(reverse("edit_eeg_setting_type", args=(eeg_setting.id, 'eeg_machine')))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'equipment_selection': eeg_machine.id, 'number_of_channels_used': "3"}
        response = self.client.post(reverse("edit_eeg_setting_type",
                                            args=(eeg_setting.id, 'eeg_machine')), self.data)
        self.assertEqual(response.status_code, 302)

        # remove an eeg_machine_setting
        self.data = {'action': 'remove-eeg_machine'}
        response = self.client.post(reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_eeg_setting_amplifier(self):
        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)

        manufacturer = ObjectsFactory.create_manufacturer()
        eeg_amplifier = ObjectsFactory.create_amplifier(manufacturer)

        # screen to an (unexisting) eeg_amplifier_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'amplifier')))
        self.assertEqual(response.status_code, 200)

        # create an eeg_amplifier_setting
        self.data = {'action': 'save', 'equipment_selection': eeg_amplifier.id, 'gain': "10"}
        response = self.client.post(reverse("view_eeg_setting_type",
                                            args=(eeg_setting.id, 'amplifier')), self.data)
        self.assertEqual(response.status_code, 302)

        # screen to view the eeg_amplifier_setting
        response = self.client.get(reverse("view_eeg_setting_type", args=(eeg_setting.id, 'amplifier')))
        self.assertEqual(response.status_code, 200)

        # update the eeg_amplifier_setting
        response = self.client.get(reverse("edit_eeg_setting_type", args=(eeg_setting.id, 'amplifier')))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save', 'equipment_selection': eeg_amplifier.id, 'gain': "20"}
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
        electrode_position_1 = ObjectsFactory.create_eeg_electrode_position(eeg_localization_system_new)
        electrode_position_2 = ObjectsFactory.create_eeg_electrode_position(eeg_localization_system_new)
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

        self.data = {'action': 'save', 'position_status_' + str(electrode_position_1.id): 'on'}
        response = self.client.post(reverse("edit_eeg_electrode_position_setting",
                                            args=(eeg_setting.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # configuring the electrodes models

        response = self.client.get(reverse("eeg_electrode_position_setting_model", args=(eeg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("edit_eeg_electrode_position_setting_model", args=(eeg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'electrode_model_' + str(electrode_position_1.id): str(electrode_model.id),
                     'electrode_model_' + str(electrode_position_2.id): str(electrode_model.id)}
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

    def test_eeg_machine_register(self):
        manufacturer = ObjectsFactory.create_manufacturer()

        # list
        response = self.client.get(reverse("eegmachine_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("eegmachine_new", args=()))
        self.assertEqual(response.status_code, 200)

        identification = 'Identification'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification}

        response = self.client.post(reverse("eegmachine_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGMachine.objects.all().count(), 1)

        # view
        eeg_machine = EEGMachine.objects.all().first()

        response = self.client.get(reverse("eegmachine_view", args=(eeg_machine.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("eegmachine_edit", args=(eeg_machine.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification}
        response = self.client.post(reverse("eegmachine_edit", args=(eeg_machine.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        identification = 'Identification changed'
        self.data = {'action': 'save',
                     'manufacturer': str(manufacturer.id),
                     'identification': identification}
        response = self.client.post(reverse("eegmachine_edit", args=(eeg_machine.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("eegmachine_view", args=(eeg_machine.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGMachine.objects.all().count(), 0)

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

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("filtertype_view", args=(filter_type.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FilterType.objects.all().count(), 0)

    def test_electrode_model_register(self):
        # list
        response = self.client.get(reverse("electrodemodel_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("electrodemodel_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = 'Name'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("electrodemodel_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ElectrodeModel.objects.all().count(), 1)

        # view
        electrode_model = ElectrodeModel.objects.all().first()

        response = self.client.get(reverse("electrodemodel_view", args=(electrode_model.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("electrodemodel_edit", args=(electrode_model.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("electrodemodel_edit", args=(electrode_model.id,)), self.data)
        self.assertEqual(response.status_code, 302)

        name = 'Name changed'
        self.data = {'action': 'save',
                     'name': name}
        response = self.client.post(reverse("electrodemodel_edit", args=(electrode_model.id,)), self.data)
        self.assertEqual(response.status_code, 302)

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

        # remove
        self.data = {'action': 'remove'}
        response = self.client.post(reverse("material_view", args=(material.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Material.objects.all().count(), 0)


class EMGEquipmentRegisterTest(TestCase):

    data = {}

    def setUp(self):

        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

