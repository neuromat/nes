# coding=utf-8
import datetime
import shutil
import tempfile
from typing import Any

from unittest.mock import patch

from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

from experiment.models import (
    Experiment,
    Group,
    Subject,
    QuestionnaireResponse,
    SubjectOfGroup,
    ComponentConfiguration,
    ResearchProject,
    Keyword,
    StimulusType,
    Component,
    Task,
    TaskForTheExperimenter,
    Stimulus,
    Instruction,
    Pause,
    Questionnaire,
    Block,
    EEG,
    FileFormat,
    EEGData,
    EEGSetting,
    DataConfigurationTree,
    EMG,
    Manufacturer,
    Tag,
    Amplifier,
    EEGSolution,
    FilterType,
    ElectrodeModel,
    EEGElectrodeNet,
    EEGElectrodeLocalizationSystem,
    EEGElectrodePosition,
    Material,
    EMGSetting,
    Software,
    SoftwareVersion,
    ADConverter,
    EMGElectrodeSetting,
    StandardizationSystem,
    MuscleSubdivision,
    Muscle,
    MuscleSide,
    EMGElectrodePlacement,
    EEGElectrodeCap,
    EEGCapSize,
    TMSDevice,
    CoilModel,
    Publication,
    ContextTree,
)
from experiment.tests.tests_helper import ObjectsFactory

from experiment.views import (
    experiment_update,
    upload_file,
    research_project_update,
    publication_update,
    context_tree_update,
    publication_add_experiment,
)

from patient.models import ClassificationOfDiseases
from patient.tests.test_orig import UtilTests

from survey.models import Survey
from survey.abc_search_engine import Questionnaires

# TODO (NES-995): it is creating one more here TEMP_MEDIA_ROOT
TEMP_MEDIA_ROOT = tempfile.mkdtemp()
LIME_SURVEY_ID = 828636
LIME_SURVEY_ID_WITHOUT_ACCESS_CODE_TABLE = 563235
LIME_SURVEY_ID_INACTIVE = 846317
LIME_SURVEY_ID_WITHOUT_IDENTIFICATION_GROUP = 913841
LIME_SURVEY_TOKEN_ID_1 = 1

CLASSIFICATION_OF_DISEASES_CREATE = "classification_of_diseases_insert"
CLASSIFICATION_OF_DISEASES_DELETE = "classification_of_diseases_remove"
EXPERIMENT_NEW = "experiment_new"

USER_USERNAME = "myadmin"
USER_PWD = "mypassword"

SEARCH_TEXT = "search_text"
SUBJECT_SEARCH = "subject_search"


class ExperimentalProtocolTest(TestCase):
    data: dict[str, Any] = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        research_project = ObjectsFactory.create_research_project()

        experiment = ObjectsFactory.create_experiment(research_project)

        self.eeg_setting = ObjectsFactory.create_eeg_setting(experiment)

        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        self.emg_setting = ObjectsFactory.create_emg_setting(
            experiment, software_version
        )

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
        response = self.client.post(
            reverse("component_new", args=(experiment.id, "task"))
        )
        self.assertEqual(response.status_code, 200)

        identification = "Task for the subject identification"
        description = "Task for the subject description"
        self.data = {
            "action": "save",
            "identification": identification,
            "description": description,
        }
        response = self.client.post(
            reverse("component_new", args=(experiment.id, "task")), self.data
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue(
            "/experiment/" + str(experiment.id) + "/components" in response.url
        )
        self.assertTrue(
            Task.objects.filter(
                description=description, identification=identification
            ).exists()
        )

        identification = "Task for the experimenter identification"
        description = "Task for the experimenter description"
        self.data = {
            "action": "save",
            "identification": identification,
            "description": description,
        }
        response = self.client.post(
            reverse("component_new", args=(experiment.id, "task_experiment")), self.data
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue(
            "/experiment/" + str(experiment.id) + "/components" in response.url
        )
        self.assertTrue(
            TaskForTheExperimenter.objects.filter(
                description=description, identification=identification
            ).exists()
        )

        identification = "EMG identification"
        description = "EMG description"
        self.data = {
            "action": "save",
            "identification": identification,
            "description": description,
            "emg_setting": self.emg_setting.id,
        }
        response = self.client.post(
            reverse("component_new", args=(experiment.id, "emg")), self.data
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue(
            "/experiment/" + str(experiment.id) + "/components" in response.url
        )
        self.assertTrue(
            EMG.objects.filter(
                description=description, identification=identification
            ).exists()
        )

        identification = "EEG identification"
        description = "EEG description"
        self.data = {
            "action": "save",
            "identification": identification,
            "description": description,
            "eeg_setting": self.eeg_setting.id,
        }
        response = self.client.post(
            reverse("component_new", args=(experiment.id, "eeg")), self.data
        )
        self.assertEqual(response.status_code, 302)
        # check if redirected to list of components
        self.assertTrue(
            "/experiment/" + str(experiment.id) + "/components" in response.url
        )
        self.assertTrue(
            EEG.objects.filter(
                description=description, identification=identification
            ).exists()
        )

        self.data = {
            "action": "save",
            "identification": "Instruction identification",
            "description": "Instruction description",
            "text": "Instruction text",
        }
        response = self.client.post(
            reverse("component_new", args=(experiment.id, "instruction")), self.data
        )
        self.assertEqual(response.status_code, 302)
        # check if redirected to list of components
        self.assertTrue(
            "/experiment/" + str(experiment.id) + "/components" in response.url
        )
        self.assertTrue(Instruction.objects.filter(text="Instruction text").exists())

        stimulus_type = StimulusType.objects.create(name="Auditivo")
        stimulus_type.save()
        self.data = {
            "action": "save",
            "identification": "Stimulus identification",
            "description": "Stimulus description",
            "stimulus_type": stimulus_type.id,
        }
        response = self.client.post(
            reverse("component_new", args=(experiment.id, "stimulus")), self.data
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue(
            "/experiment/" + str(experiment.id) + "/components" in response.url
        )
        self.assertTrue(
            Stimulus.objects.filter(
                identification="Stimulus identification", stimulus_type=stimulus_type
            ).exists()
        )

        self.data = {
            "action": "save",
            "identification": "Pause identification",
            "description": "Pause description",
            "duration_value": 2,
            "duration_unit": "h",
        }
        response = self.client.post(
            reverse("component_new", args=(experiment.id, "pause")), self.data
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue(
            "/experiment/" + str(experiment.id) + "/components" in response.url
        )
        self.assertTrue(
            Pause.objects.filter(
                identification="Pause identification", duration_value=2
            ).exists()
        )

        # Conecta no Lime Survey
        lime_survey = Questionnaires()

        # Checa se conseguiu conectar no limeSurvey com as credenciais fornecidas no settings.py
        self.assertIsNotNone(lime_survey.session_key, "Failed to connect LimeSurvey")

        # Cria uma survey no Lime Survey
        survey_id = lime_survey.add_survey(
            9999, "Questionario de teste - DjangoTests", "en", "G"
        )

        try:
            self.data = {
                "action": "save",
                "identification": "Questionnaire identification",
                "description": "Questionnaire description",
                "questionnaire_selected": survey_id,
            }
            response = self.client.post(
                reverse("component_new", args=(experiment.id, "questionnaire")),
                self.data,
            )
            self.assertEqual(response.status_code, 302)
            # Check if redirected to list of components
            self.assertTrue(
                "/experiment/" + str(experiment.id) + "/components" in response.url
            )
            self.assertTrue(
                Questionnaire.objects.filter(
                    identification="Questionnaire identification"
                ).exists()
            )

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
            self.assertEqual(status, "OK")

        self.data = {
            "action": "save",
            "identification": "Block identification",
            "description": "Block description",
            "type": "sequence",
        }
        response = self.client.post(
            reverse("component_new", args=(experiment.id, "block")), self.data
        )
        self.assertEqual(response.status_code, 302)
        block = Block.objects.filter(identification="Block identification").first()
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)

    def test_component_configuration_create_and_update(self):
        experiment = Experiment.objects.first()
        block = ObjectsFactory.create_block(experiment)

        # Screen to add a component
        response = self.client.get(
            reverse("component_add_new", args=(block.id, "block"))
        )
        self.assertEqual(response.status_code, 200)

        # Add a new component to the parent
        self.data = {
            "action": "save",
            "identification": "Block identification",
            "description": "Block description",
            "type": "sequence",
            "number_of_uses_to_insert": 1,
        }
        response = self.client.post(
            reverse("component_add_new", args=(block.id, "block")), self.data
        )
        self.assertEqual(response.status_code, 302)
        component_configuration = ComponentConfiguration.objects.first()
        # Check if redirected to view parent set of steps
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)
        self.assertTrue(
            Block.objects.filter(identification="Block identification").exists()
        )
        self.assertEqual(component_configuration.parent.id, block.id)
        self.assertEqual(component_configuration.order, 1)
        self.assertEqual(component_configuration.name, None)

        # Screen to update a component
        response = self.client.get(reverse("component_edit", args=(block.id,)))
        self.assertEqual(response.status_code, 200)

        # Update the component configuration of the recently added component.
        self.data = {
            "action": "save",
            "identification": "Block identification",
            "description": "Block description",
            "type": "sequence",
            "name": "Use of block in block",
            "interval_between_repetitions_value": 2,
            "interval_between_repetitions_unit": "min",
        }
        response = self.client.post(
            reverse("component_edit", args=(block.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)

        # Screen to reuse a component
        response = self.client.get(
            reverse(
                "component_reuse",
                args=(
                    block.id,
                    Block.objects.filter(identification="Block identification")
                    .first()
                    .id,
                ),
            )
        )
        self.assertEqual(response.status_code, 200)

        # Add 3 uses of an existing component to the parent
        self.data = {"number_of_uses_to_insert": 3}
        response = self.client.post(
            reverse(
                "component_reuse",
                args=(
                    block.id,
                    Block.objects.filter(identification="Block identification")
                    .first()
                    .id,
                ),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComponentConfiguration.objects.count(), 4)

        eeg_setting = ObjectsFactory.create_eeg_setting(experiment)

        # Add an eeg step
        self.data = {
            "action": "save",
            "identification": "EEG identification",
            "description": "EEG description",
            "type": "eeg",
            "eeg_setting": eeg_setting.id,
            "number_of_uses_to_insert": 1,
        }
        response = self.client.post(
            reverse("component_add_new", args=(block.id, "eeg")), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComponentConfiguration.objects.count(), 5)

        # Reuse an eeg step
        self.data = {"number_of_uses_to_insert": 1}
        response = self.client.post(
            reverse(
                "component_reuse",
                args=(
                    block.id,
                    EEG.objects.filter(identification="EEG identification").first().id,
                ),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ComponentConfiguration.objects.count(), 6)

    def test_block_component_remove(self):
        experiment = Experiment.objects.first()

        task = Task.objects.create(
            identification="Task identification",
            description="Task description",
            experiment=experiment,
            component_type="task",
        )
        task.save()
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Component.objects.count(), 1)

        block = ObjectsFactory.create_block(experiment)

        self.assertEqual(Block.objects.count(), 1)
        self.assertEqual(Component.objects.count(), 2)

        component_configuration = ComponentConfiguration.objects.create(
            name="ComponentConfiguration_name", parent=block, component=task
        )
        component_configuration.save()
        self.assertEqual(ComponentConfiguration.objects.count(), 1)
        self.assertEqual(component_configuration.order, 1)

        response = self.client.get(reverse("component_view", args=(block.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("component_view", args=(block.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue(
            "/experiment/" + str(experiment.id) + "/components" in response.url
        )
        self.assertEqual(Block.objects.count(), 0)
        self.assertEqual(Component.objects.count(), 1)
        self.assertEqual(ComponentConfiguration.objects.count(), 0)

        # Screen to update a component
        response = self.client.get(reverse("component_edit", args=(task.id,)))
        self.assertEqual(response.status_code, 200)

        # Updating a component
        response = self.client.post(
            reverse("component_edit", args=(task.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to list of components
        self.assertTrue(
            "/experiment/" + str(experiment.id) + "/components" in response.url
        )
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(Component.objects.count(), 0)

    def test_component_configuration_change_order_single_use(self):
        experiment = Experiment.objects.first()

        block = ObjectsFactory.create_block(experiment)

        task = Task.objects.create(
            identification="Task identification",
            description="Task description",
            experiment=experiment,
            component_type="task",
        )
        task.save()

        component_configuration1 = ComponentConfiguration.objects.create(
            name="ComponentConfiguration 1", parent=block, component=task
        )
        component_configuration1.save()
        self.assertEqual(component_configuration1.order, 1)

        component_configuration2 = ComponentConfiguration.objects.create(
            name="ComponentConfiguration 2", parent=block, component=task
        )
        component_configuration2.save()
        self.assertEqual(component_configuration2.order, 2)

        response = self.client.get(
            reverse("component_change_the_order", args=(block.id, "0-1", "up"))
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)
        self.assertEqual(
            ComponentConfiguration.objects.get(name="ComponentConfiguration 1").order, 2
        )
        self.assertEqual(
            ComponentConfiguration.objects.get(name="ComponentConfiguration 2").order, 1
        )

        response = self.client.get(
            reverse("component_change_the_order", args=(block.id, "0-0", "down"))
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)
        self.assertEqual(
            ComponentConfiguration.objects.get(name="ComponentConfiguration 1").order, 1
        )
        self.assertEqual(
            ComponentConfiguration.objects.get(name="ComponentConfiguration 2").order, 2
        )

    def test_component_configuration_change_order_accordion(self):
        experiment = Experiment.objects.first()

        block = ObjectsFactory.create_block(experiment)

        task = Task.objects.create(
            identification="Task identification",
            description="Task description",
            experiment=experiment,
            component_type="task",
        )
        task.save()

        component_configuration1 = ComponentConfiguration.objects.create(
            name="ComponentConfiguration 1", parent=block, component=task
        )
        component_configuration1.save()
        self.assertEqual(component_configuration1.order, 1)

        component_configuration2 = ComponentConfiguration.objects.create(
            name="ComponentConfiguration 2", parent=block, component=task
        )
        component_configuration2.save()
        self.assertEqual(component_configuration2.order, 2)

        instruction = Instruction.objects.create(
            identification="Instruction identification",
            description="Instruction description",
            experiment=experiment,
            component_type="instruction",
        )
        instruction.save()

        component_configuration3 = ComponentConfiguration.objects.create(
            name="ComponentConfiguration 3", parent=block, component=instruction
        )
        component_configuration3.save()
        self.assertEqual(component_configuration3.order, 3)

        response = self.client.get(
            reverse("component_change_the_order", args=(block.id, "0", "down"))
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)
        self.assertEqual(
            ComponentConfiguration.objects.get(name="ComponentConfiguration 1").order, 2
        )
        self.assertEqual(
            ComponentConfiguration.objects.get(name="ComponentConfiguration 2").order, 3
        )
        self.assertEqual(
            ComponentConfiguration.objects.get(name="ComponentConfiguration 3").order, 1
        )

        response = self.client.get(
            reverse("component_change_the_order", args=(block.id, "1", "up"))
        )
        self.assertEqual(response.status_code, 302)
        # Check if redirected to view block
        self.assertTrue("/experiment/component/" + str(block.id) in response.url)
        self.assertEqual(
            ComponentConfiguration.objects.get(name="ComponentConfiguration 1").order, 1
        )
        self.assertEqual(
            ComponentConfiguration.objects.get(name="ComponentConfiguration 2").order, 2
        )
        self.assertEqual(
            ComponentConfiguration.objects.get(name="ComponentConfiguration 3").order, 3
        )


class GroupTest(TestCase):
    data: dict[str, Any] = {}

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
        self.data = {
            "action": "save",
            "description": "Description of Group-1",
            "title": "Group-1",
        }

        # Inserting a group in the experiment
        response = self.client.post(
            reverse("group_new", args=(experiment.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(experiment.groups.count(), 1)

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
        self.data = {
            "action": "save",
            "description": "Description of Group-1",
            "title": "Group-1",
        }

        # Editing a group in the experiment
        response = self.client.post(reverse("group_edit", args=(group.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(experiment.groups.count(), 1)
        self.assertTrue(
            Group.objects.filter(
                title="Group-1", description="Description of Group-1"
            ).exists()
        )

        # Trying to editing a group with no changes
        response = self.client.post(reverse("group_edit", args=(group.id,)), self.data)
        self.assertEqual(response.status_code, 302)

    def test_group_remove(self):
        experiment = Experiment.objects.first()

        group = ObjectsFactory.create_group(experiment)

        # New data about the group
        self.data = {"action": "remove"}

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
        classification_of_diseases = ClassificationOfDiseases.objects.create(
            code="1", description="test", abbreviated_description="t"
        )
        # Inserindo o classification_of_diseases no group
        response = self.client.get(
            reverse(
                CLASSIFICATION_OF_DISEASES_CREATE,
                args=(group.id, classification_of_diseases.id),
            )
        )
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
        classification_of_diseases = ClassificationOfDiseases.objects.create(
            code="1", description="test", abbreviated_description="t"
        )
        # Inserindo o classification_of_diseases no group
        response = self.client.get(
            reverse(
                CLASSIFICATION_OF_DISEASES_CREATE,
                args=(group.id, classification_of_diseases.id),
            )
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(group.classification_of_diseases.count(), 1)

        # Removendo o classification_of_diseases no group
        response = self.client.get(
            reverse(
                CLASSIFICATION_OF_DISEASES_DELETE,
                args=(group.id, classification_of_diseases.id),
            )
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(group.classification_of_diseases.count(), 0)


class ExperimentTest(TestCase):
    data: dict[str, Any] = {}

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
        response = self.client.get(
            reverse(
                "research_project_view",
                args=[
                    self.research_project.pk,
                ],
            )
        )
        self.assertEqual(response.status_code, 200)

        # deve retornar vazia
        self.assertEqual(len(response.context["experiments"]), 0)

        # cria um experimento
        experiment = ObjectsFactory.create_experiment(self.research_project)

        # lista experimentos: deve retornar 1
        response = self.client.get(
            reverse(
                "research_project_view",
                args=[
                    self.research_project.pk,
                ],
            )
        )
        self.assertEqual(response.status_code, 200)

        # deve retornar 1 experimento
        self.assertEqual(len(response.context["experiments"]), 1)

        self.assertContains(response, experiment.title)

    def test_experiment_create(self):
        """Testa a criacao de um experimento"""

        # Abre tela de cadastro de experimento
        response = self.client.get(
            reverse(
                "experiment_new",
                args=[
                    self.research_project.pk,
                ],
            )
        )
        self.assertEqual(response.status_code, 200)

        # Dados sobre o experimento
        self.data = {
            "action": "save",
            "description": "Experimento de Teste",
            "title": "Teste Experimento",
            "research_project": self.research_project.id,
        }

        # Obtem o total de experimentos existente na tabela
        count_before_insert = Experiment.objects.all().count()

        # Efetua a adicao do experimento
        response = self.client.post(
            reverse(
                "experiment_new",
                args=[
                    self.research_project.pk,
                ],
            ),
            self.data,
        )

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
        request = self.factory.get(
            reverse(
                "experiment_edit",
                args=[
                    experiment.pk,
                ],
            )
        )
        request.user = self.user

        response = experiment_update(request, experiment_id=experiment.pk)
        self.assertEqual(response.status_code, 200)

        # Efetua a atualizacao do experimento
        self.data = {
            "action": "save",
            "description": "Experimento de Teste",
            "title": "Teste Experimento",
            "research_project": self.research_project.id,
        }
        response = self.client.post(
            reverse("experiment_edit", args=(experiment.pk,)), self.data, follow=True
        )
        self.assertEqual(response.status_code, 200)

    def test_experiment_remove(self):
        """Testa a exclusao do experimento"""

        experiment = ObjectsFactory.create_experiment(self.research_project)

        count = Experiment.objects.all().count()

        # Remove experimento
        self.data = {
            "action": "remove",
            "description": "Experimento de Teste",
            "title": "Teste Experimento",
            "research_project": self.research_project.id,
        }
        response = self.client.post(
            reverse("experiment_view", args=(experiment.pk,)), self.data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Experiment.objects.all().count(), count - 1)


class ListOfQuestionnaireFromExperimentalProtocolOfAGroupTest(TestCase):
    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        self.lime_survey = Questionnaires()

    def test_create_questionnaire_for_a_group(self):
        """Testa a criacao de um questionario para um dado grupo"""

        research_project = ObjectsFactory.create_research_project()

        experiment = ObjectsFactory.create_experiment(research_project)

        # Create the root of the experimental protocol
        block = ObjectsFactory.create_block(Experiment.objects.first())

        # Create a quesitonnaire at LiveSurvey to use in this test.
        survey_title = "Questionario de teste - DjangoTests"
        sid = self.lime_survey.add_survey(99999, survey_title, "en", "G")

        try:
            new_survey, created = Survey.objects.get_or_create(lime_survey_id=sid)

            # Create a questionnaire
            questionnaire = Questionnaire.objects.create(
                identification="Questionnaire",
                description="Questionnaire description",
                experiment=Experiment.objects.first(),
                component_type="questionnaire",
                survey=new_survey,
            )
            questionnaire.save()

            # Include the questionnaire in the root.
            ComponentConfiguration.objects.create(
                name="ComponentConfiguration", parent=block, component=questionnaire
            )

            # Criar um grupo mock para ser utilizado no teste
            group = ObjectsFactory.create_group(experiment, block)

            # Abre tela de grupo
            response = self.client.get(reverse("group_view", args=(group.pk,)))
            self.assertEqual(response.status_code, 200)
            # Check if the survey is listed
            self.assertContains(response, survey_title)
        finally:
            # Deleta a survey gerada no Lime Survey
            status = self.lime_survey.delete_survey(sid)
            self.assertEqual(status, "OK")

    @patch("survey.abc_search_engine.Server")
    def test_list_questionnaire_of_a_group(self, mockServer):
        """Test exhibition of a questionnaire of a group"""
        mockServer.return_value.get_participant_properties.return_value = {
            "token": "abc",
            "completed": "2018-05-15 15:51",
        }
        mockServer.return_value.export_responses_by_token.return_value = (
            "ImFjcXVpc2l0aW9uZGF0ZSIKIjIwMTktMDEtMDMgMDA6MDA6MDAi"
        )
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        block = ObjectsFactory.create_block(Experiment.objects.first())
        new_survey, created = Survey.objects.get_or_create(
            lime_survey_id=LIME_SURVEY_ID
        )

        questionnaire = Questionnaire.objects.create(
            identification="Questionnaire",
            description="Questionnaire description",
            experiment=Experiment.objects.first(),
            component_type="questionnaire",
            survey=new_survey,
        )

        component_configuration = ComponentConfiguration.objects.create(
            name="ComponentConfiguration", parent=block, component=questionnaire
        )
        data_configuration_tree = DataConfigurationTree.objects.create(
            component_configuration=component_configuration
        )
        group = ObjectsFactory.create_group(experiment, block)
        util = UtilTests()
        patient = util.create_patient(changed_by=self.user)
        subject = Subject(patient=patient)
        subject.save()

        subject_group = SubjectOfGroup(subject=subject, group=group)
        subject_group.save()

        group.subjectofgroup_set.add(subject_group)
        experiment.save()

        questionnaire_response = QuestionnaireResponse()
        questionnaire_response.data_configuration_tree = data_configuration_tree
        questionnaire_response.subject_of_group = subject_group
        questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_1
        questionnaire_response.questionnaire_responsible = self.user
        questionnaire_response.date = datetime.datetime.now()
        questionnaire_response.save()

        response = self.client.get(
            reverse("questionnaire_view", args=(group.pk, component_configuration.pk))
        )
        self.assertEqual(response.status_code, 200)

    def test_questionnaire_response_view_response(self):
        """Testa a visualizacao completa do questionario respondido no Lime
        Survey
        """
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        block = ObjectsFactory.create_block(Experiment.objects.first())
        new_survey, created = Survey.objects.get_or_create(
            lime_survey_id=LIME_SURVEY_ID
        )
        questionnaire = Questionnaire.objects.create(
            identification="Questionnaire",
            description="Questionnaire description",
            experiment=Experiment.objects.first(),
            component_type="questionnaire",
            survey=new_survey,
        )

        component_configuration = ComponentConfiguration.objects.create(
            name="ComponentConfiguration", parent=block, component=questionnaire
        )

        data_configuration_tree = DataConfigurationTree.objects.create(
            component_configuration=component_configuration
        )
        group = ObjectsFactory.create_group(experiment, block)

        util = UtilTests()
        patient_mock = util.create_patient(changed_by=self.user)
        subject_mock = Subject.objects.create(patient=patient_mock)
        subject_group = SubjectOfGroup.objects.create(subject=subject_mock, group=group)

        group.subjectofgroup_set.add(subject_group)
        experiment.save()

        questionnaire_response = QuestionnaireResponse()
        questionnaire_response.data_configuration_tree = data_configuration_tree
        questionnaire_response.subject_of_group = subject_group
        questionnaire_response.token_id = LIME_SURVEY_TOKEN_ID_1
        questionnaire_response.questionnaire_responsible = self.user
        questionnaire_response.date = datetime.datetime.now()
        questionnaire_response.save()


class SubjectTest(TestCase):
    util = UtilTests()
    data: dict[str, Any] = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        # Conecta no Lime Survey
        self.lime_survey = Questionnaires()

        # Checa se conseguiu conectar no lime Survey com as credenciais fornecidas no settings.py
        self.assertIsNotNone(
            self.lime_survey.session_key, "Failed to connect LimeSurvey"
        )

        self.tag_eeg = ObjectsFactory.create_tag("EEG")

    def test_subject_view_and_search(self):
        """Teste de visualizacao de participante após cadastro na base de dados"""

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        group = ObjectsFactory.create_group(experiment)

        patient = self.util.create_patient(changed_by=self.user)
        patient.cpf = "374.276.738-08"  # To test search for cpf
        patient.save()
        self.data = {
            SEARCH_TEXT: patient.name,
            "experiment_id": experiment.id,
            "group_id": group.id,
        }

        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, patient.name)
        self.assertEqual(response.context["patients"].count(), 1)

        self.data[SEARCH_TEXT] = 374
        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["patients"].count(), 1)
        self.assertContains(response, patient.cpf)

        self.data[SEARCH_TEXT] = ""
        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["patients"], "")

    def test_subject_search_on_group_already_with_subject_being_searched(self):
        """
        Teste de visualizacao de participante após cadastro na base de dados
        """

        # Create a research project
        research_project = ObjectsFactory.create_research_project()

        # Criar um experimento mock para ser utilizado no teste
        experiment = ObjectsFactory.create_experiment(research_project)

        # Criar um grupo mock para ser utilizado no teste
        group = ObjectsFactory.create_group(experiment)

        patient_mock = self.util.create_patient(changed_by=self.user)
        patient_mock.cpf = "374.276.738-08"  # to test search for cpf
        patient_mock.save()

        subject = Subject()
        subject.patient = patient_mock
        subject.save()

        SubjectOfGroup(subject=subject, group=group).save()

        self.data = {
            SEARCH_TEXT: "Pacient",
            "experiment_id": experiment.id,
            "group_id": group.id,
        }

        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, patient_mock.name)
        self.assertEqual(response.context["patients"].count(), 0)

        self.data[SEARCH_TEXT] = 374
        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["patients"].count(), 0)
        self.assertNotContains(response, patient_mock.cpf)

        self.data[SEARCH_TEXT] = ""
        response = self.client.post(reverse(SUBJECT_SEARCH), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["patients"], "")

    def test_subject_view(self):
        """Test exhibition of subjects of a group"""

        # Create a research project
        research_project = ObjectsFactory.create_research_project()

        # Criar um experimento mock para ser utilizado no teste
        experiment = ObjectsFactory.create_experiment(research_project)

        # Create the root of the experimental protocol
        block = ObjectsFactory.create_block(Experiment.objects.first())

        # Using a known questionnaire at LiveSurvey to use in this test.
        new_survey, created = Survey.objects.get_or_create(
            lime_survey_id=LIME_SURVEY_ID
        )

        # Create a questionnaire
        questionnaire = Questionnaire.objects.create(
            identification="Questionnaire",
            description="Questionnaire description",
            experiment=Experiment.objects.first(),
            component_type="questionnaire",
            survey=new_survey,
        )
        questionnaire.save()

        # Include the questionnaire in the root.
        component_configuration = ComponentConfiguration.objects.create(
            name="ComponentConfiguration", parent=block, component=questionnaire
        )
        component_configuration.save()

        data_configuration_tree = DataConfigurationTree.objects.create(
            component_configuration=component_configuration
        )
        data_configuration_tree.save()

        # Create a mock group
        group = ObjectsFactory.create_group(experiment, block)

        # Abre tela de cadastro de participantes com nenhum participante cadastrado a priori
        response = self.client.get(reverse("subjects", args=(group.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["subject_list"]), 0)

        # Insert subject in the group
        util = UtilTests()
        patient_mock = util.create_patient(changed_by=self.user)

        count_before_insert_subject = (
            SubjectOfGroup.objects.all().filter(group=group).count()
        )
        response = self.client.post(
            reverse("subject_insert", args=(group.pk, patient_mock.pk))
        )
        self.assertEqual(response.status_code, 302)
        count_after_insert_subject = (
            SubjectOfGroup.objects.all().filter(group=group).count()
        )
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
        response = self.client.get(reverse("subjects", args=(group.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["subject_list"]), 1)

        # Inserir participante ja inserido para o experimento
        count_before_insert_subject = (
            SubjectOfGroup.objects.all().filter(group=group).count()
        )
        response = self.client.post(
            reverse("subject_insert", args=(group.pk, patient_mock.pk))
        )
        self.assertEqual(response.status_code, 302)
        count_after_insert_subject = (
            SubjectOfGroup.objects.all().filter(group=group).count()
        )
        self.assertEqual(count_after_insert_subject, count_before_insert_subject)

    @patch("survey.abc_search_engine.Server")
    def test_questionnaire_fill(self, mockServer):
        mockServer.return_value.get_session_key.return_value = (
            "fmhcr2qv7tz37b3zpkhfz3t6rjj26eri"
        )
        mockServer.return_value.get_language_properties.side_effect = [
            {"surveyls_title": "NES-TestCase (used by automated tests)"},
            {
                "surveyls_title": "NES-TestCase (used by automated tests) - "
                "Survey without access code table"
            },
            {
                "surveyls_title": "NES-TestCase (used by automated tests) - "
                "Survey inactive"
            },
            {
                "surveyls_title": "NES-TestCase (used by automated tests) - "
                "Survey without identification group"
            },
            {"surveyls_title": "NES-TestCase (used by automated tests)"},
            {"surveyls_title": "NES-TestCase (used by automated tests)"},
            {"surveyls_title": "NES-TestCase (used by automated tests)"},
            {"surveyls_title": "NES-TestCase (used by automated tests)"},
            {
                "surveyls_title": "NES-TestCase (used by automated tests) - "
                "Survey without access code table"
            },
            {
                "surveyls_title": "NES-TestCase (used by automated tests) - "
                "Survey inactive"
            },
            {
                "surveyls_title": "NES-TestCase (used by automated tests) - "
                "Survey without identification group"
            },
            {"surveyls_title": "NES-TestCase (used by automated tests)"},
        ]
        mockServer.return_value.get_summary.side_effect = [
            1,
            {"status": "No available data"},
            0,
            0,
        ]
        mockServer.return_value.get_survey_properties.side_effect = [
            {"active": "Y"},
            {"language": "en", "additional_languages": ""},
            {"active": "N"},
            {"active": "Y"},
            {"language": "en", "additional_languages": ""},
            {"language": "en", "additional_languages": ""},
            {"language": "en", "additional_languages": ""},
            {"language": "en", "additional_languages": ""},
            {"language": "en", "additional_languages": ""},
            {"language": "en", "additional_languages": ""},
        ]
        mockServer.return_value.list_groups.side_effect = [
            [
                {
                    "group_order": 1,
                    "language": "pt-BR",
                    "sid": 828636,
                    "description": "Teste de dominância manual baseado em "
                    "Oldfield (1971)",
                    "id": {"language": "pt-BR", "gid": 1118},
                    "randomization_group": "",
                    "grelevance": "",
                    "group_name": "Teste de Lateralidade (Oldfield)",
                    "gid": 1118,
                },
                {
                    "group_order": 0,
                    "language": "pt-BR",
                    "sid": 828636,
                    "description": "",
                    "id": {"language": "pt-BR", "gid": 1119},
                    "randomization_group": "",
                    "grelevance": "",
                    "group_name": "Identification",
                    "gid": 1119,
                },
            ],
            [
                {
                    "group_order": 0,
                    "language": "pt-BR",
                    "sid": 913841,
                    "description": "Teste de dominância manual baseado em Oldfield (1971)",
                    "id": {"language": "pt-BR", "gid": 1140},
                    "randomization_group": "",
                    "grelevance": "",
                    "group_name": "Teste de Lateralidade (Oldfield)",
                    "gid": 1140,
                }
            ],
        ]
        mockServer.return_value.list_questions.side_effect = [
            [
                {
                    "help": "",
                    "relevance": "1",
                    "title": "tendenciacanhoto",
                    "question_order": 3,
                    "qid": 7622,
                    "preg": "",
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7622},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "Y",
                    "sid": 828636,
                    "question": "Você já teve alguma tendência de ser canhoto?",
                    "other": "N",
                    "type": "Y",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "1",
                    "title": "canhotofamilia",
                    "question_order": 4,
                    "qid": 7623,
                    "preg": "",
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7623},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "Y",
                    "sid": 828636,
                    "question": "Existe alguém canhoto na família?",
                    "other": "N",
                    "type": "Y",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "1",
                    "title": "idteste",
                    "question_order": 7,
                    "qid": 7625,
                    "preg": "",
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7625},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "Y",
                    "sid": 828636,
                    "question": "Indicar a preferência manual nas seguintes atividades assinalando + na coluna apropriada. Quando a preferência for tão forte de modo a não ser capaz de usar a outra mão assinale + +. Se não existir preferência, assinale + nas duas colunas.",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "1",
                    "title": "formulaoldfield0",
                    "question_order": 20,
                    "qid": 7629,
                    "preg": "",
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7629},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "{if(is_empty(idteste_1_0.value),0,intval(idteste_1_0.value)) + if(is_empty(idteste_2_0.value),0,intval(idteste_2_0.value)) + if(is_empty(idteste_3_0.value),0,intval(idteste_3_0.value)) + if(is_empty(idteste_4_0.value),0,intval(idteste_4_0.value)) + if(is_empty(idteste_5_0.value),0,intval(idteste_5_0.value)) + if(is_empty(idteste_6_0.value),0,intval(idteste_6_0.value)) + if(is_empty(idteste_7_0.value),0,intval(idteste_7_0.value)) + if(is_empty(idteste_8_0.value),0,intval(idteste_8_0.value)) + if(is_empty(idteste_9_0.value),0,intval(idteste_9_0.value)) + if(is_empty(idteste_10_0.value),0,intval(idteste_10_0.value)) + if(is_empty(idteste_11_0.value),0,intval(idteste_11_0.value)) + if(is_empty(idteste_12_0.value),0,intval(idteste_12_0.value)) + if(is_empty(idteste_13_0.value),0,intval(idteste_13_0.value)) + if(is_empty(idteste_14_0.value),0,intval(idteste_14_0.value)) + if(is_empty(idteste_15_0.value),0,intval(idteste_15_0.value)) + if(is_empty(idteste_16_0.value),0,intval(idteste_16_0.value)) + if(is_empty(idteste_17_0.value),0,intval(idteste_17_0.value)) + if(is_empty(idteste_18_0.value),0,intval(idteste_18_0.value)) + if(is_empty(idteste_19_0.value),0,intval(idteste_19_0.value))}",
                    "other": "N",
                    "type": "*",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "1",
                    "title": "formulaoldfield",
                    "question_order": 22,
                    "qid": 7630,
                    "preg": "",
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7630},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "{if(is_empty(idteste_1_1.value),0,intval(idteste_1_1.value)) + if(is_empty(idteste_2_1.value),0,intval(idteste_2_1.value)) + if(is_empty(idteste_3_1.value),0,intval(idteste_3_1.value)) + if(is_empty(idteste_4_1.value),0,intval(idteste_4_1.value)) + if(is_empty(idteste_5_1.value),0,intval(idteste_5_1.value)) + if(is_empty(idteste_6_1.value),0,intval(idteste_6_1.value)) + if(is_empty(idteste_7_1.value),0,intval(idteste_7_1.value)) + if(is_empty(idteste_8_1.value),0,intval(idteste_8_1.value)) + if(is_empty(idteste_9_1.value),0,intval(idteste_9_1.value)) + if(is_empty(idteste_10_1.value),0,intval(idteste_10_1.value)) + if(is_empty(idteste_11_1.value),0,intval(idteste_11_1.value)) + if(is_empty(idteste_12_1.value),0,intval(idteste_12_1.value)) + if(is_empty(idteste_13_1.value),0,intval(idteste_13_1.value)) + if(is_empty(idteste_14_1.value),0,intval(idteste_14_1.value)) + if(is_empty(idteste_15_1.value),0,intval(idteste_15_1.value)) + if(is_empty(idteste_16_1.value),0,intval(idteste_16_1.value)) + if(is_empty(idteste_17_1.value),0,intval(idteste_17_1.value)) + if(is_empty(idteste_18_1.value),0,intval(idteste_18_1.value)) + if(is_empty(idteste_19_1.value),0,intval(idteste_19_1.value))}",
                    "other": "N",
                    "type": "*",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "",
                    "title": "pontuacaoold",
                    "question_order": 24,
                    "qid": 7631,
                    "preg": "",
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7631},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": '<p>\n\t{if(((formulaoldfield0+formulaoldfield)==0),"",round(((formulaoldfield0-formulaoldfield)/(formulaoldfield0+formulaoldfield)*100),2))}</p>\n',
                    "other": "N",
                    "type": "*",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "",
                    "title": "MsgPontuacaoold",
                    "question_order": 26,
                    "qid": 7632,
                    "preg": "",
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7632},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": '<div>\n\t<span style="color:#ff0000;"><strong>Pontuação:</strong></span><strong> </strong>{pontuacaoold}</div>\n',
                    "other": "N",
                    "type": "X",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "1",
                    "question_order": 1,
                    "qid": 7633,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7633},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Escrever",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "2",
                    "question_order": 2,
                    "qid": 7634,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7634},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Desenhar",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "3",
                    "question_order": 3,
                    "qid": 7635,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7635},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Jogar uma pedra",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "4",
                    "question_order": 4,
                    "qid": 7636,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7636},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Usar uma tesoura",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "5",
                    "question_order": 5,
                    "qid": 7637,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7637},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Usar um pente",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "6",
                    "question_order": 6,
                    "qid": 7638,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7638},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Usar uma escova de dentes",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "7",
                    "question_order": 7,
                    "qid": 7639,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7639},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Usar uma faca (sem uso do garfo)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "8",
                    "question_order": 8,
                    "qid": 7640,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7640},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Usar uma colher",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "9",
                    "question_order": 9,
                    "qid": 7641,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7641},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Usar um martelo",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "10",
                    "question_order": 10,
                    "qid": 7642,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7642},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Usar uma chave de fenda",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "11",
                    "question_order": 11,
                    "qid": 7643,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7643},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Usar uma raquete de tênis",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "12",
                    "question_order": 12,
                    "qid": 7644,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7644},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Usar uma faca (com garfo)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "13",
                    "question_order": 13,
                    "qid": 7645,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7645},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Usar uma vassoura (ver mão superior)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "14",
                    "question_order": 14,
                    "qid": 7646,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7646},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Usar um ancinho (ver mão superior)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "15",
                    "question_order": 15,
                    "qid": 7647,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7647},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Acender um fósforo",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "16",
                    "question_order": 16,
                    "qid": 7648,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7648},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Abrir um vidro com tampa (mão da tampa)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "17",
                    "question_order": 17,
                    "qid": 7649,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7649},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Dar cartas",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "18",
                    "question_order": 18,
                    "qid": 7650,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7650},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Enfiar a linha na agulha (mão que segura ou que move)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "19",
                    "question_order": 19,
                    "qid": 7651,
                    "preg": None,
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7651},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Com que pé você prefere chutar?",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7625,
                },
                {
                    "help": "",
                    "relevance": '((828636X1118X7623.NAOK == "Y"))',
                    "title": "famliacanhoto2",
                    "question_order": 5,
                    "qid": 7624,
                    "preg": "",
                    "gid": 1118,
                    "id": {"language": "pt-BR", "qid": 7624},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Quem?",
                    "other": "N",
                    "type": "S",
                    "parent_qid": 0,
                },
            ],
            [
                {
                    "help": "",
                    "relevance": "1",
                    "title": "fileUpload",
                    "question_order": 4,
                    "qid": 91282,
                    "preg": "",
                    "gid": 1119,
                    "id": {"language": "pt-BR", "qid": 91282},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 828636,
                    "question": "Has fileupload question?",
                    "other": "N",
                    "type": "|",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "1",
                    "title": "responsibleid",
                    "question_order": 0,
                    "qid": 7626,
                    "preg": "",
                    "gid": 1119,
                    "id": {"language": "pt-BR", "qid": 7626},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "Y",
                    "sid": 828636,
                    "question": "<b>Número do avaliador</b>",
                    "other": "N",
                    "type": "N",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "1",
                    "title": "acquisitiondate",
                    "question_order": 1,
                    "qid": 7627,
                    "preg": "",
                    "gid": 1119,
                    "id": {"language": "pt-BR", "qid": 7627},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "Y",
                    "sid": 828636,
                    "question": "<strong>Data:</strong><br />\n",
                    "other": "N",
                    "type": "D",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "1",
                    "title": "subjectid",
                    "question_order": 3,
                    "qid": 7628,
                    "preg": "",
                    "gid": 1119,
                    "id": {"language": "pt-BR", "qid": 7628},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "Y",
                    "sid": 828636,
                    "question": "<b>Número do participante:</b>",
                    "other": "N",
                    "type": "N",
                    "parent_qid": 0,
                },
            ],
            [
                {
                    "help": "",
                    "relevance": "1",
                    "title": "tendenciacanhoto",
                    "question_order": 3,
                    "qid": 7768,
                    "preg": "",
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7768},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "Y",
                    "sid": 913841,
                    "question": "Você já teve alguma tendência de ser canhoto?",
                    "other": "N",
                    "type": "Y",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "1",
                    "title": "canhotofamilia",
                    "question_order": 4,
                    "qid": 7769,
                    "preg": "",
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7769},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "Y",
                    "sid": 913841,
                    "question": "Existe alguém canhoto na família?",
                    "other": "N",
                    "type": "Y",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "1",
                    "title": "idteste",
                    "question_order": 7,
                    "qid": 7771,
                    "preg": "",
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7771},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "Y",
                    "sid": 913841,
                    "question": "Indicar a preferência manual nas seguintes atividades assinalando + na coluna apropriada. Quando a preferência for tão forte de modo a não ser capaz de usar a outra mão assinale + +. Se não existir preferência, assinale + nas duas colunas.",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "1",
                    "title": "formulaoldfield0",
                    "question_order": 20,
                    "qid": 7775,
                    "preg": "",
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7775},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "{if(is_empty(idteste_1_0.value),0,intval(idteste_1_0.value)) + if(is_empty(idteste_2_0.value),0,intval(idteste_2_0.value)) + if(is_empty(idteste_3_0.value),0,intval(idteste_3_0.value)) + if(is_empty(idteste_4_0.value),0,intval(idteste_4_0.value)) + if(is_empty(idteste_5_0.value),0,intval(idteste_5_0.value)) + if(is_empty(idteste_6_0.value),0,intval(idteste_6_0.value)) + if(is_empty(idteste_7_0.value),0,intval(idteste_7_0.value)) + if(is_empty(idteste_8_0.value),0,intval(idteste_8_0.value)) + if(is_empty(idteste_9_0.value),0,intval(idteste_9_0.value)) + if(is_empty(idteste_10_0.value),0,intval(idteste_10_0.value)) + if(is_empty(idteste_11_0.value),0,intval(idteste_11_0.value)) + if(is_empty(idteste_12_0.value),0,intval(idteste_12_0.value)) + if(is_empty(idteste_13_0.value),0,intval(idteste_13_0.value)) + if(is_empty(idteste_14_0.value),0,intval(idteste_14_0.value)) + if(is_empty(idteste_15_0.value),0,intval(idteste_15_0.value)) + if(is_empty(idteste_16_0.value),0,intval(idteste_16_0.value)) + if(is_empty(idteste_17_0.value),0,intval(idteste_17_0.value)) + if(is_empty(idteste_18_0.value),0,intval(idteste_18_0.value)) + if(is_empty(idteste_19_0.value),0,intval(idteste_19_0.value))}",
                    "other": "N",
                    "type": "*",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "1",
                    "title": "formulaoldfield",
                    "question_order": 22,
                    "qid": 7776,
                    "preg": "",
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7776},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "{if(is_empty(idteste_1_1.value),0,intval(idteste_1_1.value)) + if(is_empty(idteste_2_1.value),0,intval(idteste_2_1.value)) + if(is_empty(idteste_3_1.value),0,intval(idteste_3_1.value)) + if(is_empty(idteste_4_1.value),0,intval(idteste_4_1.value)) + if(is_empty(idteste_5_1.value),0,intval(idteste_5_1.value)) + if(is_empty(idteste_6_1.value),0,intval(idteste_6_1.value)) + if(is_empty(idteste_7_1.value),0,intval(idteste_7_1.value)) + if(is_empty(idteste_8_1.value),0,intval(idteste_8_1.value)) + if(is_empty(idteste_9_1.value),0,intval(idteste_9_1.value)) + if(is_empty(idteste_10_1.value),0,intval(idteste_10_1.value)) + if(is_empty(idteste_11_1.value),0,intval(idteste_11_1.value)) + if(is_empty(idteste_12_1.value),0,intval(idteste_12_1.value)) + if(is_empty(idteste_13_1.value),0,intval(idteste_13_1.value)) + if(is_empty(idteste_14_1.value),0,intval(idteste_14_1.value)) + if(is_empty(idteste_15_1.value),0,intval(idteste_15_1.value)) + if(is_empty(idteste_16_1.value),0,intval(idteste_16_1.value)) + if(is_empty(idteste_17_1.value),0,intval(idteste_17_1.value)) + if(is_empty(idteste_18_1.value),0,intval(idteste_18_1.value)) + if(is_empty(idteste_19_1.value),0,intval(idteste_19_1.value))}",
                    "other": "N",
                    "type": "*",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "",
                    "title": "pontuacaoold",
                    "question_order": 24,
                    "qid": 7777,
                    "preg": "",
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7777},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": '<p>\n\t{if(((formulaoldfield0+formulaoldfield)==0),"",round(((formulaoldfield0-formulaoldfield)/(formulaoldfield0+formulaoldfield)*100),2))}</p>\n',
                    "other": "N",
                    "type": "*",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": "",
                    "title": "MsgPontuacaoold",
                    "question_order": 26,
                    "qid": 7778,
                    "preg": "",
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7778},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": '<div>\n\t<span style="color:#ff0000;"><strong>Pontuação:</strong></span><strong> </strong>{pontuacaoold}</div>\n',
                    "other": "N",
                    "type": "X",
                    "parent_qid": 0,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "1",
                    "question_order": 1,
                    "qid": 7779,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7779},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Escrever",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "2",
                    "question_order": 2,
                    "qid": 7780,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7780},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Desenhar",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "3",
                    "question_order": 3,
                    "qid": 7781,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7781},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Jogar uma pedra",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "4",
                    "question_order": 4,
                    "qid": 7782,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7782},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Usar uma tesoura",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "5",
                    "question_order": 5,
                    "qid": 7783,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7783},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Usar um pente",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "6",
                    "question_order": 6,
                    "qid": 7784,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7784},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Usar uma escova de dentes",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "7",
                    "question_order": 7,
                    "qid": 7785,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7785},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Usar uma faca (sem uso do garfo)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "8",
                    "question_order": 8,
                    "qid": 7786,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7786},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Usar uma colher",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "9",
                    "question_order": 9,
                    "qid": 7787,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7787},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Usar um martelo",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "10",
                    "question_order": 10,
                    "qid": 7788,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7788},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Usar uma chave de fenda",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "11",
                    "question_order": 11,
                    "qid": 7789,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7789},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Usar uma raquete de tênis",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "12",
                    "question_order": 12,
                    "qid": 7790,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7790},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Usar uma faca (com garfo)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "13",
                    "question_order": 13,
                    "qid": 7791,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7791},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Usar uma vassoura (ver mão superior)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "14",
                    "question_order": 14,
                    "qid": 7792,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7792},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Usar um ancinho (ver mão superior)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "15",
                    "question_order": 15,
                    "qid": 7793,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7793},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Acender um fósforo",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "16",
                    "question_order": 16,
                    "qid": 7794,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7794},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Abrir um vidro com tampa (mão da tampa)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "17",
                    "question_order": 17,
                    "qid": 7795,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7795},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Dar cartas",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "18",
                    "question_order": 18,
                    "qid": 7796,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7796},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Enfiar a linha na agulha (mão que segura ou que move)",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": None,
                    "title": "19",
                    "question_order": 19,
                    "qid": 7797,
                    "preg": None,
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7797},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Com que pé você prefere chutar?",
                    "other": "N",
                    "type": "1",
                    "parent_qid": 7771,
                },
                {
                    "help": "",
                    "relevance": '((913841X1140X7769.NAOK == "Y"))',
                    "title": "famliacanhoto2",
                    "question_order": 5,
                    "qid": 7770,
                    "preg": "",
                    "gid": 1140,
                    "id": {"language": "pt-BR", "qid": 7770},
                    "scale_id": 0,
                    "modulename": None,
                    "same_default": 0,
                    "language": "pt-BR",
                    "mandatory": "N",
                    "sid": 913841,
                    "question": "Quem?",
                    "other": "N",
                    "type": "S",
                    "parent_qid": 0,
                },
            ],
        ]
        mockServer.return_value.get_question_properties.side_effect = [
            {
                "other": "N",
                "title": "tendenciacanhoto",
                "attributes_lang": "No available attributes",
                "question_order": 3,
                "question": "Você já teve alguma tendência de ser canhoto?",
                "type": "Y",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "canhotofamilia",
                "attributes_lang": "No available attributes",
                "question_order": 4,
                "question": "Existe alguém canhoto na família?",
                "type": "Y",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "idteste",
                "attributes_lang": {
                    "dualscale_headerB": "Membro esquerdo",
                    "dualscale_headerA": "Membro direito",
                },
                "question_order": 7,
                "question": "Indicar a preferência manual nas seguintes "
                "atividades assinalando + na coluna apropriada. "
                "Quando a preferência for tão forte de modo a "
                "não ser capaz de usar a outra mão assinale + +. "
                "Se não existir preferência, assinale + nas duas "
                "colunas.",
                "type": "1",
                "answeroptions": {
                    "ESQ0": {
                        "assessment_value": 0,
                        "scale_id": 1,
                        "answer": "0",
                        "order": 1,
                    },
                    "DIR2": {
                        "assessment_value": 2,
                        "scale_id": 0,
                        "answer": "++",
                        "order": 3,
                    },
                    "ESQ1": {
                        "assessment_value": 1,
                        "scale_id": 1,
                        "answer": "+",
                        "order": 2,
                    },
                    "DIR1": {
                        "assessment_value": 1,
                        "scale_id": 0,
                        "answer": "+",
                        "order": 2,
                    },
                    "DIR0": {
                        "assessment_value": 0,
                        "scale_id": 0,
                        "answer": "0",
                        "order": 1,
                    },
                    "ESQ2": {
                        "assessment_value": 2,
                        "scale_id": 1,
                        "answer": "++",
                        "order": 3,
                    },
                },
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": {
                    "7646": {
                        "question": "Usar um ancinho (ver mão superior)",
                        "scale_id": 0,
                        "title": "14",
                    },
                    "7650": {
                        "question": "Enfiar a linha na agulha (mão que segura ou que move)",
                        "scale_id": 0,
                        "title": "18",
                    },
                    "7639": {
                        "question": "Usar uma faca (sem uso do garfo)",
                        "scale_id": 0,
                        "title": "7",
                    },
                    "7641": {
                        "question": "Usar um martelo",
                        "scale_id": 0,
                        "title": "9",
                    },
                    "7651": {
                        "question": "Com que pé você prefere chutar?",
                        "scale_id": 0,
                        "title": "19",
                    },
                    "7634": {"question": "Desenhar", "scale_id": 0, "title": "2"},
                    "7633": {"question": "Escrever", "scale_id": 0, "title": "1"},
                    "7644": {
                        "question": "Usar uma faca (com garfo)",
                        "scale_id": 0,
                        "title": "12",
                    },
                    "7642": {
                        "question": "Usar uma chave de fenda",
                        "scale_id": 0,
                        "title": "10",
                    },
                    "7637": {"question": "Usar um pente", "scale_id": 0, "title": "5"},
                    "7635": {
                        "question": "Jogar uma pedra",
                        "scale_id": 0,
                        "title": "3",
                    },
                    "7647": {
                        "question": "Acender um fósforo",
                        "scale_id": 0,
                        "title": "15",
                    },
                    "7649": {"question": "Dar cartas", "scale_id": 0, "title": "17"},
                    "7636": {
                        "question": "Usar uma tesoura",
                        "scale_id": 0,
                        "title": "4",
                    },
                    "7645": {
                        "question": "Usar uma vassoura (ver mão superior)",
                        "scale_id": 0,
                        "title": "13",
                    },
                    "7643": {
                        "question": "Usar uma raquete de tênis",
                        "scale_id": 0,
                        "title": "11",
                    },
                    "7648": {
                        "question": "Abrir um vidro com tampa (mão da tampa)",
                        "scale_id": 0,
                        "title": "16",
                    },
                    "7640": {
                        "question": "Usar uma colher",
                        "scale_id": 0,
                        "title": "8",
                    },
                    "7638": {
                        "question": "Usar uma escova de dentes",
                        "scale_id": 0,
                        "title": "6",
                    },
                },
            },
            {
                "other": "N",
                "title": "formulaoldfield0",
                "attributes_lang": "No available attributes",
                "question_order": 20,
                "question": "{if(is_empty(idteste_1_0.value),0,intval(idteste_1_0.value)) + if(is_empty(idteste_2_0.value),0,intval(idteste_2_0.value)) + if(is_empty(idteste_3_0.value),0,intval(idteste_3_0.value)) + if(is_empty(idteste_4_0.value),0,intval(idteste_4_0.value)) + if(is_empty(idteste_5_0.value),0,intval(idteste_5_0.value)) + if(is_empty(idteste_6_0.value),0,intval(idteste_6_0.value)) + if(is_empty(idteste_7_0.value),0,intval(idteste_7_0.value)) + if(is_empty(idteste_8_0.value),0,intval(idteste_8_0.value)) + if(is_empty(idteste_9_0.value),0,intval(idteste_9_0.value)) + if(is_empty(idteste_10_0.value),0,intval(idteste_10_0.value)) + if(is_empty(idteste_11_0.value),0,intval(idteste_11_0.value)) + if(is_empty(idteste_12_0.value),0,intval(idteste_12_0.value)) + if(is_empty(idteste_13_0.value),0,intval(idteste_13_0.value)) + if(is_empty(idteste_14_0.value),0,intval(idteste_14_0.value)) + if(is_empty(idteste_15_0.value),0,intval(idteste_15_0.value)) + if(is_empty(idteste_16_0.value),0,intval(idteste_16_0.value)) + if(is_empty(idteste_17_0.value),0,intval(idteste_17_0.value)) + if(is_empty(idteste_18_0.value),0,intval(idteste_18_0.value)) + if(is_empty(idteste_19_0.value),0,intval(idteste_19_0.value))}",
                "type": "*",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": {"hidden": "1"},
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "formulaoldfield",
                "attributes_lang": "No available attributes",
                "question_order": 22,
                "question": "{if(is_empty(idteste_1_1.value),0,intval(idteste_1_1.value)) + if(is_empty(idteste_2_1.value),0,intval(idteste_2_1.value)) + if(is_empty(idteste_3_1.value),0,intval(idteste_3_1.value)) + if(is_empty(idteste_4_1.value),0,intval(idteste_4_1.value)) + if(is_empty(idteste_5_1.value),0,intval(idteste_5_1.value)) + if(is_empty(idteste_6_1.value),0,intval(idteste_6_1.value)) + if(is_empty(idteste_7_1.value),0,intval(idteste_7_1.value)) + if(is_empty(idteste_8_1.value),0,intval(idteste_8_1.value)) + if(is_empty(idteste_9_1.value),0,intval(idteste_9_1.value)) + if(is_empty(idteste_10_1.value),0,intval(idteste_10_1.value)) + if(is_empty(idteste_11_1.value),0,intval(idteste_11_1.value)) + if(is_empty(idteste_12_1.value),0,intval(idteste_12_1.value)) + if(is_empty(idteste_13_1.value),0,intval(idteste_13_1.value)) + if(is_empty(idteste_14_1.value),0,intval(idteste_14_1.value)) + if(is_empty(idteste_15_1.value),0,intval(idteste_15_1.value)) + if(is_empty(idteste_16_1.value),0,intval(idteste_16_1.value)) + if(is_empty(idteste_17_1.value),0,intval(idteste_17_1.value)) + if(is_empty(idteste_18_1.value),0,intval(idteste_18_1.value)) + if(is_empty(idteste_19_1.value),0,intval(idteste_19_1.value))}",
                "type": "*",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": {"hidden": "1"},
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "pontuacaoold",
                "attributes_lang": "No available attributes",
                "question_order": 24,
                "question": '<p>\n\t{if(((formulaoldfield0+formulaoldfield)==0),"",round(((formulaoldfield0-formulaoldfield)/(formulaoldfield0+formulaoldfield)*100),2))}</p>\n',
                "type": "*",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": {"hidden": "1"},
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "MsgPontuacaoold",
                "attributes_lang": "No available attributes",
                "question_order": 26,
                "question": '<div>\n\t<span style="color:#ff0000;"><strong>Pontuação:</strong></span><strong> </strong>{pontuacaoold}</div>\n',
                "type": "X",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "1",
                "attributes_lang": "No available attributes",
                "question_order": 1,
                "question": "Escrever",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "2",
                "attributes_lang": "No available attributes",
                "question_order": 2,
                "question": "Desenhar",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "3",
                "attributes_lang": "No available attributes",
                "question_order": 3,
                "question": "Jogar uma pedra",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "4",
                "attributes_lang": "No available attributes",
                "question_order": 4,
                "question": "Usar uma tesoura",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "5",
                "attributes_lang": "No available attributes",
                "question_order": 5,
                "question": "Usar um pente",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "6",
                "attributes_lang": "No available attributes",
                "question_order": 6,
                "question": "Usar uma escova de dentes",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "7",
                "attributes_lang": "No available attributes",
                "question_order": 7,
                "question": "Usar uma faca (sem uso do garfo)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "8",
                "attributes_lang": "No available attributes",
                "question_order": 8,
                "question": "Usar uma colher",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "9",
                "attributes_lang": "No available attributes",
                "question_order": 9,
                "question": "Usar um martelo",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "10",
                "attributes_lang": "No available attributes",
                "question_order": 10,
                "question": "Usar uma chave de fenda",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "11",
                "attributes_lang": "No available attributes",
                "question_order": 11,
                "question": "Usar uma raquete de tênis",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "12",
                "attributes_lang": "No available attributes",
                "question_order": 12,
                "question": "Usar uma faca (com garfo)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "12",
                "attributes_lang": "No available attributes",
                "question_order": 12,
                "question": "Usar uma faca (com garfo)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "14",
                "attributes_lang": "No available attributes",
                "question_order": 14,
                "question": "Usar um ancinho (ver mão superior)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "15",
                "attributes_lang": "No available attributes",
                "question_order": 15,
                "question": "Acender um fósforo",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "16",
                "attributes_lang": "No available attributes",
                "question_order": 16,
                "question": "Abrir um vidro com tampa (mão da tampa)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "17",
                "attributes_lang": "No available attributes",
                "question_order": 17,
                "question": "Dar cartas",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "18",
                "attributes_lang": "No available attributes",
                "question_order": 18,
                "question": "Enfiar a linha na agulha (mão que segura ou que move)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "19",
                "attributes_lang": "No available attributes",
                "question_order": 19,
                "question": "Com que pé você prefere chutar?",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "famliacanhoto2",
                "attributes_lang": "No available attributes",
                "question_order": 5,
                "question": "Quem?",
                "type": "S",
                "answeroptions": "No available answer options",
                "gid": 1118,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "fileUpload",
                "attributes_lang": "No available attributes",
                "question_order": 4,
                "question": "Has fileupload question?",
                "type": "|",
                "answeroptions": "No available answer options",
                "gid": 1119,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "responsibleid",
                "attributes_lang": "No available attributes",
                "question_order": 0,
                "question": "<b>Número do avaliador</b>",
                "type": "N",
                "answeroptions": "No available answer options",
                "gid": 1119,
                "attributes": {"hidden": "1"},
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "acquisitiondate",
                "attributes_lang": "No available attributes",
                "question_order": 1,
                "question": "<strong>Data:</strong><br />\n",
                "type": "D",
                "answeroptions": "No available answer options",
                "gid": 1119,
                "attributes": {"hidden": "1"},
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "subjectid",
                "attributes_lang": "No available attributes",
                "question_order": 3,
                "question": "<b>Número do participante:</b>",
                "type": "N",
                "answeroptions": "No available answer options",
                "gid": 1119,
                "attributes": {"hidden": "1"},
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "tendenciacanhoto",
                "attributes_lang": "No available attributes",
                "question_order": 3,
                "question": "Você já teve alguma tendência de ser canhoto?",
                "type": "Y",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "canhotofamilia",
                "attributes_lang": "No available attributes",
                "question_order": 4,
                "question": "Existe alguém canhoto na família?",
                "type": "Y",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "idteste",
                "attributes_lang": {
                    "dualscale_headerB": "Membro esquerdo",
                    "dualscale_headerA": "Membro direito",
                },
                "question_order": 7,
                "question": "Indicar a preferência manual nas seguintes atividades assinalando + na coluna apropriada. Quando a preferência for tão forte de modo a não ser capaz de usar a outra mão assinale + +. Se não existir preferência, assinale + nas duas colunas.",
                "type": "1",
                "answeroptions": {
                    "ESQ0": {
                        "assessment_value": 0,
                        "scale_id": 1,
                        "answer": "0",
                        "order": 1,
                    },
                    "DIR2": {
                        "assessment_value": 2,
                        "scale_id": 0,
                        "answer": "++",
                        "order": 3,
                    },
                    "ESQ1": {
                        "assessment_value": 1,
                        "scale_id": 1,
                        "answer": "+",
                        "order": 2,
                    },
                    "DIR1": {
                        "assessment_value": 1,
                        "scale_id": 0,
                        "answer": "+",
                        "order": 2,
                    },
                    "DIR0": {
                        "assessment_value": 0,
                        "scale_id": 0,
                        "answer": "0",
                        "order": 1,
                    },
                    "ESQ2": {
                        "assessment_value": 2,
                        "scale_id": 1,
                        "answer": "++",
                        "order": 3,
                    },
                },
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": {
                    "7780": {"question": "Desenhar", "scale_id": 0, "title": "2"},
                    "7785": {
                        "question": "Usar uma faca (sem uso do garfo)",
                        "scale_id": 0,
                        "title": "7",
                    },
                    "7796": {
                        "question": "Enfiar a linha na agulha (mão que segura ou que move)",
                        "scale_id": 0,
                        "title": "18",
                    },
                    "7789": {
                        "question": "Usar uma raquete de tênis",
                        "scale_id": 0,
                        "title": "11",
                    },
                    "7784": {
                        "question": "Usar uma escova de dentes",
                        "scale_id": 0,
                        "title": "6",
                    },
                    "7790": {
                        "question": "Usar uma faca (com garfo)",
                        "scale_id": 0,
                        "title": "12",
                    },
                    "7797": {
                        "question": "Com que pé você prefere chutar?",
                        "scale_id": 0,
                        "title": "19",
                    },
                    "7791": {
                        "question": "Usar uma vassoura (ver mão superior)",
                        "scale_id": 0,
                        "title": "13",
                    },
                    "7781": {
                        "question": "Jogar uma pedra",
                        "scale_id": 0,
                        "title": "3",
                    },
                    "7792": {
                        "question": "Usar um ancinho (ver mão superior)",
                        "scale_id": 0,
                        "title": "14",
                    },
                    "7788": {
                        "question": "Usar uma chave de fenda",
                        "scale_id": 0,
                        "title": "10",
                    },
                    "7794": {
                        "question": "Abrir um vidro com tampa (mão da tampa)",
                        "scale_id": 0,
                        "title": "16",
                    },
                    "7782": {
                        "question": "Usar uma tesoura",
                        "scale_id": 0,
                        "title": "4",
                    },
                    "7793": {
                        "question": "Acender um fósforo",
                        "scale_id": 0,
                        "title": "15",
                    },
                    "7795": {"question": "Dar cartas", "scale_id": 0, "title": "17"},
                    "7783": {"question": "Usar um pente", "scale_id": 0, "title": "5"},
                    "7786": {
                        "question": "Usar uma colher",
                        "scale_id": 0,
                        "title": "8",
                    },
                    "7779": {"question": "Escrever", "scale_id": 0, "title": "1"},
                    "7787": {
                        "question": "Usar um martelo",
                        "scale_id": 0,
                        "title": "9",
                    },
                },
            },
            {
                "other": "N",
                "title": "formulaoldfield0",
                "attributes_lang": "No available attributes",
                "question_order": 20,
                "question": "{if(is_empty(idteste_1_0.value),0,intval(idteste_1_0.value)) + if(is_empty(idteste_2_0.value),0,intval(idteste_2_0.value)) + if(is_empty(idteste_3_0.value),0,intval(idteste_3_0.value)) + if(is_empty(idteste_4_0.value),0,intval(idteste_4_0.value)) + if(is_empty(idteste_5_0.value),0,intval(idteste_5_0.value)) + if(is_empty(idteste_6_0.value),0,intval(idteste_6_0.value)) + if(is_empty(idteste_7_0.value),0,intval(idteste_7_0.value)) + if(is_empty(idteste_8_0.value),0,intval(idteste_8_0.value)) + if(is_empty(idteste_9_0.value),0,intval(idteste_9_0.value)) + if(is_empty(idteste_10_0.value),0,intval(idteste_10_0.value)) + if(is_empty(idteste_11_0.value),0,intval(idteste_11_0.value)) + if(is_empty(idteste_12_0.value),0,intval(idteste_12_0.value)) + if(is_empty(idteste_13_0.value),0,intval(idteste_13_0.value)) + if(is_empty(idteste_14_0.value),0,intval(idteste_14_0.value)) + if(is_empty(idteste_15_0.value),0,intval(idteste_15_0.value)) + if(is_empty(idteste_16_0.value),0,intval(idteste_16_0.value)) + if(is_empty(idteste_17_0.value),0,intval(idteste_17_0.value)) + if(is_empty(idteste_18_0.value),0,intval(idteste_18_0.value)) + if(is_empty(idteste_19_0.value),0,intval(idteste_19_0.value))}",
                "type": "*",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": {"hidden": "1"},
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "formulaoldfield",
                "attributes_lang": "No available attributes",
                "question_order": 22,
                "question": "{if(is_empty(idteste_1_1.value),0,intval(idteste_1_1.value)) + if(is_empty(idteste_2_1.value),0,intval(idteste_2_1.value)) + if(is_empty(idteste_3_1.value),0,intval(idteste_3_1.value)) + if(is_empty(idteste_4_1.value),0,intval(idteste_4_1.value)) + if(is_empty(idteste_5_1.value),0,intval(idteste_5_1.value)) + if(is_empty(idteste_6_1.value),0,intval(idteste_6_1.value)) + if(is_empty(idteste_7_1.value),0,intval(idteste_7_1.value)) + if(is_empty(idteste_8_1.value),0,intval(idteste_8_1.value)) + if(is_empty(idteste_9_1.value),0,intval(idteste_9_1.value)) + if(is_empty(idteste_10_1.value),0,intval(idteste_10_1.value)) + if(is_empty(idteste_11_1.value),0,intval(idteste_11_1.value)) + if(is_empty(idteste_12_1.value),0,intval(idteste_12_1.value)) + if(is_empty(idteste_13_1.value),0,intval(idteste_13_1.value)) + if(is_empty(idteste_14_1.value),0,intval(idteste_14_1.value)) + if(is_empty(idteste_15_1.value),0,intval(idteste_15_1.value)) + if(is_empty(idteste_16_1.value),0,intval(idteste_16_1.value)) + if(is_empty(idteste_17_1.value),0,intval(idteste_17_1.value)) + if(is_empty(idteste_18_1.value),0,intval(idteste_18_1.value)) + if(is_empty(idteste_19_1.value),0,intval(idteste_19_1.value))}",
                "type": "*",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": {"hidden": "1"},
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "pontuacaoold",
                "attributes_lang": "No available attributes",
                "question_order": 24,
                "question": '<p>\n\t{if(((formulaoldfield0+formulaoldfield)==0),"",round(((formulaoldfield0-formulaoldfield)/(formulaoldfield0+formulaoldfield)*100),2))}</p>\n',
                "type": "*",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": {"hidden": "1"},
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "MsgPontuacaoold",
                "attributes_lang": "No available attributes",
                "question_order": 26,
                "question": '<div>\n\t<span style="color:#ff0000;"><strong>Pontuação:</strong></span><strong> </strong>{pontuacaoold}</div>\n',
                "type": "X",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "1",
                "attributes_lang": "No available attributes",
                "question_order": 1,
                "question": "Escrever",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "2",
                "attributes_lang": "No available attributes",
                "question_order": 2,
                "question": "Desenhar",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "3",
                "attributes_lang": "No available attributes",
                "question_order": 3,
                "question": "Jogar uma pedra",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "4",
                "attributes_lang": "No available attributes",
                "question_order": 4,
                "question": "Usar uma tesoura",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "5",
                "attributes_lang": "No available attributes",
                "question_order": 5,
                "question": "Usar um pente",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "6",
                "attributes_lang": "No available attributes",
                "question_order": 6,
                "question": "Usar uma escova de dentes",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "7",
                "attributes_lang": "No available attributes",
                "question_order": 7,
                "question": "Usar uma faca (sem uso do garfo)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "8",
                "attributes_lang": "No available attributes",
                "question_order": 8,
                "question": "Usar uma colher",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "9",
                "attributes_lang": "No available attributes",
                "question_order": 9,
                "question": "Usar um martelo",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "10",
                "attributes_lang": "No available attributes",
                "question_order": 10,
                "question": "Usar uma chave de fenda",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "11",
                "attributes_lang": "No available attributes",
                "question_order": 11,
                "question": "Usar uma raquete de tênis",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "12",
                "attributes_lang": "No available attributes",
                "question_order": 12,
                "question": "Usar uma faca (com garfo)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "13",
                "attributes_lang": "No available attributes",
                "question_order": 13,
                "question": "Usar uma vassoura (ver mão superior)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "14",
                "attributes_lang": "No available attributes",
                "question_order": 14,
                "question": "Usar um ancinho (ver mão superior)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "15",
                "attributes_lang": "No available attributes",
                "question_order": 15,
                "question": "Acender um fósforo",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "16",
                "attributes_lang": "No available attributes",
                "question_order": 16,
                "question": "Abrir um vidro com tampa (mão da tampa)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "17",
                "attributes_lang": "No available attributes",
                "question_order": 17,
                "question": "Dar cartas",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "18",
                "attributes_lang": "No available attributes",
                "question_order": 18,
                "question": "Enfiar a linha na agulha (mão que segura ou que move)",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "19",
                "attributes_lang": "No available attributes",
                "question_order": 19,
                "question": "Com que pé você prefere chutar?",
                "type": "1",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
            {
                "other": "N",
                "title": "famliacanhoto2",
                "attributes_lang": "No available attributes",
                "question_order": 5,
                "question": "Quem?",
                "type": "S",
                "answeroptions": "No available answer options",
                "gid": 1140,
                "attributes": "No available attributes",
                "subquestions": "No available answers",
            },
        ]
        mockServer.return_value.add_participants.return_value = [
            {
                "remindersent": "N",
                "completed": "N",
                "blacklisted": None,
                "participant_id": None,
                "remindercount": 0,
                "lastname": "",
                "sent": "N",
                "usesleft": 1,
                "validuntil": None,
                "language": None,
                "emailstatus": "OK",
                "validfrom": None,
                "token": "kMR34vg97KnCOOK",
                "tid": "867",
                "mpid": None,
                "email": "",
                "firstname": "",
            }
        ]
        mockServer.return_value.get_participant_properties.side_effect = [
            {"token": "kMR34vg97KnCOOK"},
            {"token": "kMR34vg97KnCOOK", "completed": "N"},
            {"token": "kMR34vg97KnCOOK", "completed": "N"},
            {"token": "kMR34vg97KnCOOK"},
            {"token": "kMR34vg97KnCOOK", "completed": "N"},
            {"token": "kMR34vg97KnCOOK", "completed": "N"},
            {"token": "kMR34vg97KnCOOK", "completed": "N"},
        ]
        mockServer.return_value.delete_participants.return_value = {"867": "Deleted"}

        # Create a research project
        research_project = ObjectsFactory.create_research_project()

        # Criar um experimento mock para ser utilizado no teste
        experiment = ObjectsFactory.create_experiment(research_project)

        # Create the root of the experimental protocol
        block = ObjectsFactory.create_block(Experiment.objects.first())

        # Using a known questionnaires at LimeSurvey to use in this test.
        new_survey, created = Survey.objects.get_or_create(
            lime_survey_id=LIME_SURVEY_ID
        )
        new_survey_without_access_table, created = Survey.objects.get_or_create(
            lime_survey_id=LIME_SURVEY_ID_WITHOUT_ACCESS_CODE_TABLE
        )
        new_survey_inactive, created = Survey.objects.get_or_create(
            lime_survey_id=LIME_SURVEY_ID_INACTIVE
        )
        new_survey_without_identification_group, created = Survey.objects.get_or_create(
            lime_survey_id=LIME_SURVEY_ID_WITHOUT_IDENTIFICATION_GROUP
        )

        # Create a questionnaire
        questionnaire = Questionnaire.objects.create(
            identification="Questionnaire",
            description="Questionnaire description",
            experiment=Experiment.objects.first(),
            component_type="questionnaire",
            survey=new_survey,
        )
        questionnaire.save()

        questionnaire_without_access_table = Questionnaire.objects.create(
            identification="Questionnaire",
            description="Questionnaire description",
            experiment=Experiment.objects.first(),
            component_type="questionnaire",
            survey=new_survey_without_access_table,
        )
        questionnaire_without_access_table.save()

        questionnaire_inactive = Questionnaire.objects.create(
            identification="Questionnaire",
            description="Questionnaire description",
            experiment=Experiment.objects.first(),
            component_type="questionnaire",
            survey=new_survey_inactive,
        )
        questionnaire_inactive.save()

        questionnaire_without_identification_group = Questionnaire.objects.create(
            identification="Questionnaire",
            description="Questionnaire description",
            experiment=Experiment.objects.first(),
            component_type="questionnaire",
            survey=new_survey_without_identification_group,
        )
        questionnaire_without_identification_group.save()

        # Include the questionnaire in the root.
        component_configuration = ComponentConfiguration.objects.create(
            name="ComponentConfiguration", parent=block, component=questionnaire
        )
        component_configuration.save()

        component_configuration_without_access_table = (
            ComponentConfiguration.objects.create(
                name="ComponentConfiguration",
                parent=block,
                component=questionnaire_without_access_table,
            )
        )
        component_configuration_without_access_table.save()

        component_configuration_inactive = ComponentConfiguration.objects.create(
            name="ComponentConfiguration",
            parent=block,
            component=questionnaire_inactive,
        )
        component_configuration_inactive.save()

        component_configuration_without_identification_group = (
            ComponentConfiguration.objects.create(
                name="ComponentConfiguration",
                parent=block,
                component=questionnaire_without_identification_group,
            )
        )
        component_configuration_without_identification_group.save()

        data_configuration_tree = DataConfigurationTree.objects.create(
            component_configuration=component_configuration
        )
        data_configuration_tree.save()

        group = ObjectsFactory.create_group(experiment, block)

        util = UtilTests()
        patient_mock = util.create_patient(changed_by=self.user)

        subject = Subject(patient=patient_mock)
        subject.save()

        subject_group = SubjectOfGroup(subject=subject, group=group)
        subject_group.save()

        group.subjectofgroup_set.add(subject_group)
        experiment.save()

        # Dados para preenchimento da Survey
        self.data = {"date": "29/08/2014", "action": "save"}

        # Inicia o preenchimento de uma Survey
        response = self.client.post(
            reverse(
                "subject_questionnaire_response",
                args=[
                    group.pk,
                    subject.pk,
                    data_configuration_tree.component_configuration.id,
                ],
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["FAIL"], False)

        # Inicia o preenchimento de uma Survey without access code table
        response = self.client.post(
            reverse(
                "subject_questionnaire_response",
                args=[
                    group.pk,
                    subject.pk,
                    component_configuration_without_access_table.pk,
                ],
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["FAIL"], True)

        # Inicia o preenchimento de uma Survey inactive
        response = self.client.post(
            reverse(
                "subject_questionnaire_response",
                args=[
                    group.pk,
                    subject.pk,
                    component_configuration_inactive.pk,
                ],
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["FAIL"], True)

        # Inicia o preenchimento de uma Survey without identification group
        response = self.client.post(
            reverse(
                "subject_questionnaire_response",
                args=[
                    group.pk,
                    subject.pk,
                    component_configuration_without_identification_group.pk,
                ],
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["FAIL"], True)

        questionnaire_response = QuestionnaireResponse.objects.all().first()

        # Acessa tela de atualizacao do preenchimento da Survey
        response = self.client.get(
            reverse(
                "questionnaire_response_edit",
                args=[
                    questionnaire_response.pk,
                ],
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["FAIL"], None)

        # Atualiza o preenchimento da survey
        response = self.client.post(
            reverse(
                "questionnaire_response_edit",
                args=[
                    questionnaire_response.pk,
                ],
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["FAIL"], False)

        response = self.client.get(
            reverse(
                "questionnaire_response_edit",
                args=[
                    questionnaire_response.pk,
                ],
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)

        # Show the responses list of a subject
        response = self.client.post(
            reverse("subject_questionnaire", args=(group.pk, subject.pk)),
        )
        self.assertEqual(response.status_code, 200)

        # Remove preenchimento da Survey
        count_before_delete_questionnaire_response = (
            QuestionnaireResponse.objects.all().count()
        )

        self.data["action"] = "remove"
        response = self.client.post(
            reverse(
                "questionnaire_response_edit",
                args=[
                    questionnaire_response.pk,
                ],
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        count_after_delete_questionnaire_response = (
            QuestionnaireResponse.objects.all().count()
        )
        self.assertEqual(
            count_before_delete_questionnaire_response - 1,
            count_after_delete_questionnaire_response,
        )

        # Delete participant from a group
        self.data = {"action": "remove-" + str(subject.pk)}
        count_before_delete_subject = (
            SubjectOfGroup.objects.all().filter(group=group).count()
        )
        response = self.client.post(reverse("subjects", args=(group.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        count_after_delete_subject = (
            SubjectOfGroup.objects.all().filter(group=group).count()
        )
        self.assertEqual(count_before_delete_subject - 1, count_after_delete_subject)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_eeg_data_file(self):
        research_project = ObjectsFactory.create_research_project()

        experiment = ObjectsFactory.create_experiment(research_project)

        block = ObjectsFactory.create_block(Experiment.objects.first())

        eeg_setting = ObjectsFactory.create_eeg_setting(experiment)

        # EEG step
        eeg_step = EEG.objects.create(
            experiment=experiment,
            component_type="eeg",
            identification="EEG step",
            eeg_setting=eeg_setting,
        )

        # Include the EEG step in the root.
        component_configuration = ComponentConfiguration.objects.create(
            name="ComponentConfiguration", parent=block, component=eeg_step
        )
        component_configuration.save()

        group = ObjectsFactory.create_group(experiment, block)

        util = UtilTests()
        patient_mock = util.create_patient(changed_by=self.user)

        subject_mock = Subject(patient=patient_mock)
        subject_mock.save()

        subject_group = SubjectOfGroup(subject=subject_mock, group=group)
        subject_group.save()

        group.subjectofgroup_set.add(subject_group)
        experiment.save()

        # screen to create an eeg data file
        response = self.client.get(
            reverse(
                "subject_eeg_data_create",
                args=(group.id, subject_mock.id, component_configuration.id),
            )
        )
        self.assertEqual(response.status_code, 200)

        # trying to create an eeg data file with a date greater than todays' date
        file_format = FileFormat.objects.create(name="Text file", extension="txt")
        file = SimpleUploadedFile("experiment/eeg/eeg_metadata.txt", b"rb")
        self.data = {
            "date": datetime.date.today() + datetime.timedelta(days=1),
            "action": "save",
            "description": "description of the file",
            "file_format": file_format.id,
            "file": file,
        }
        response = self.client.post(
            reverse(
                "subject_eeg_data_create",
                args=(group.id, subject_mock.id, component_configuration.id),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGData.objects.all().count(), 0)
        self.assertGreaterEqual(len(response.context["eeg_data_form"].errors), 1)
        self.assertTrue("date" in response.context["eeg_data_form"].errors)
        self.assertEqual(
            response.context["eeg_data_form"].errors["date"][0],
            _("Date cannot be greater than today's date."),
        )

        # create an eeg data file
        tag_eeg = Tag.objects.get(name="EEG")
        file_format = FileFormat.objects.create(name="Text file", extension="txt")
        file_format.tags.add(tag_eeg)
        file = SimpleUploadedFile("experiment/eeg/eeg_metadata.txt", b"rb")
        self.data = {
            "date": "29/08/2014",
            "action": "save",
            "description": "description of the file",
            "file_format": file_format.id,
            "file": file,
            "file_format_description": "test",
            "eeg_setting": eeg_setting.id,
        }
        response = self.client.post(
            reverse(
                "subject_eeg_data_create",
                args=(group.id, subject_mock.id, component_configuration.id),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGData.objects.all().count(), 1)

        # show a eeg data file
        eeg_data = EEGData.objects.all().first()
        response = self.client.get(reverse("eeg_data_view", args=(eeg_data.id, 1)))
        self.assertEqual(response.status_code, 200)

        # screen to edit a eeg data file
        response = self.client.get(reverse("eeg_data_edit", args=(eeg_data.id, 1)))
        self.assertEqual(response.status_code, 200)

        # editing a eeg data file
        self.data = {
            "date": "30/08/2014",
            "action": "save",
            "description": "description of the file",
            "file_format": file_format.id,
            "file": file,
            "file_format_description": "teste",
            "eeg_setting": eeg_setting.id,
        }
        response = self.client.post(
            reverse("eeg_data_edit", args=(eeg_data.id, 1)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # list eeg data files
        response = self.client.post(
            reverse(
                "subject_eeg_view",
                args=(
                    group.id,
                    subject_mock.id,
                ),
            )
        )
        self.assertEqual(response.status_code, 200)

        # Show the participants
        response = self.client.get(reverse("subjects", args=(group.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["subject_list"]), 1)

        # Trying to delete participant from a group, but there is a eeg file associated
        self.data = {"action": "remove-" + str(subject_mock.pk)}
        count_before_delete_subject = (
            SubjectOfGroup.objects.all().filter(group=group).count()
        )
        response = self.client.post(reverse("subjects", args=(group.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        count_after_delete_subject = (
            SubjectOfGroup.objects.all().filter(group=group).count()
        )
        self.assertEqual(count_before_delete_subject, count_after_delete_subject)

        # remove eeg data file from a subject
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("eeg_data_view", args=(eeg_data.id, 1)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGData.objects.all().count(), 0)

        # Show the participants
        response = self.client.get(reverse("subjects", args=(group.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["subject_list"]), 1)

        # Delete participant from a group
        self.data = {"action": "remove-" + str(subject_mock.pk)}
        count_before_delete_subject = (
            SubjectOfGroup.objects.all().filter(group=group).count()
        )
        response = self.client.post(reverse("subjects", args=(group.pk,)), self.data)
        self.assertEqual(response.status_code, 302)
        count_after_delete_subject = (
            SubjectOfGroup.objects.all().filter(group=group).count()
        )
        self.assertEqual(count_before_delete_subject - 1, count_after_delete_subject)

    def test_subject_upload_consent_file(self):
        """
        Testa o upload de arquivos que corresponde ao formulario de consentimento do participante no experimento
        """

        research_project = ObjectsFactory.create_research_project()

        experiment = ObjectsFactory.create_experiment(research_project)

        group = ObjectsFactory.create_group(experiment)

        patient_mock = self.util.create_patient(changed_by=self.user)

        subject_mock = Subject.objects.all().first()

        if not subject_mock:
            subject_mock = Subject.objects.create(patient=patient_mock)
            subject_mock.patient = patient_mock
            subject_mock.save()

        self.assertEqual(get_object_or_404(Subject, pk=subject_mock.pk), subject_mock)

        subject_group = SubjectOfGroup.objects.all().first()
        if not subject_group:
            subject_group = SubjectOfGroup.objects.create(
                subject=subject_mock, group=group
            )

        subject_group.group = group
        subject_group.subject = subject_mock
        subject_group.save()

        # experiment.subjectofexperiment_set.add(subject_group)
        # experiment.save()

        self.assertEqual(get_object_or_404(Experiment, pk=experiment.pk), experiment)
        self.assertEqual(
            get_object_or_404(SubjectOfGroup, subject=subject_mock, group=group),
            subject_group,
        )

        # Upload Consent_form
        # Simula click no icone de acesso a pagina de upload do arquivo
        request = self.factory.get(
            reverse(
                "upload_file",
                args=[
                    subject_mock.pk,
                    experiment.pk,
                ],
            )
        )
        request.user = self.user
        response = upload_file(request, subject_id=subject_mock.pk, group_id=group.pk)

        self.assertEqual(response.status_code, 200)

        # Anexar arquivo
        consent_form_file = SimpleUploadedFile("data/consent_form.txt", b"rb")
        self.data = {"action": "upload", "consent_form": consent_form_file}
        # url = reverse('upload_file', args=[group.pk, subject_mock.pk])
        # request = self.factory.post(url, self.data)d
        # request.user = self.user
        # response = upload_file(request, subject_id=subject_mock.pk, experiment_id=experiment.pk)
        response = self.client.post(
            reverse(
                "upload_file",
                args=[
                    group.pk,
                    subject_mock.pk,
                ],
            ),
            self.data,
            follow=True,
        )
        # print response.content
        self.assertEqual(response.status_code, 200)

        # Remover arquivo
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse(
                "upload_file",
                args=[
                    group.pk,
                    subject_mock.pk,
                ],
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)


class ResearchProjectTest(TestCase):
    data: dict[str, Any] = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

    def test_research_project_list(self):
        # Check if list of research projects is empty before inserting any.
        response = self.client.get(reverse("research_project_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["research_projects"]), 0)

        ObjectsFactory.create_research_project()

        # Check if list of research projects returns one item after inserting one.
        response = self.client.get(reverse("research_project_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["research_projects"]), 1)

    def test_research_project_create(self):
        # Request the research project register screen
        response = self.client.get(reverse("research_project_new"))
        self.assertEqual(response.status_code, 200)

        # POSTing "wrong" action
        self.data = {
            "action": "wrong",
            "title": "Research project title",
            "start_date": datetime.date.today(),
            "description": "Research project description",
        }
        response = self.client.post(reverse("research_project_new"), self.data)
        self.assertEqual(ResearchProject.objects.all().count(), 0)
        self.assertEqual(
            str(list(response.context["messages"])[0]), _("Action not available.")
        )
        self.assertEqual(response.status_code, 200)

        # POSTing missing information
        self.data = {"action": "save"}
        response = self.client.post(reverse("research_project_new"), self.data)
        self.assertEqual(ResearchProject.objects.all().count(), 0)
        self.assertGreaterEqual(
            len(response.context["research_project_form"].errors), 3
        )
        self.assertTrue("title" in response.context["research_project_form"].errors)
        self.assertTrue(
            "start_date" in response.context["research_project_form"].errors
        )
        self.assertTrue(
            "description" in response.context["research_project_form"].errors
        )
        self.assertEqual(
            str(list(response.context["messages"])[0]), _("Information not saved.")
        )
        self.assertEqual(response.status_code, 200)

        # Set research project data
        self.data = {
            "action": "save",
            "title": "Research project title",
            "start_date": datetime.date.today(),
            "description": "Research project description",
        }

        # Count the number of research projects currently in database
        count_before_insert = ResearchProject.objects.all().count()

        # Add the new research project
        response = self.client.post(reverse("research_project_new"), self.data)
        self.assertEqual(response.status_code, 302)

        # Count the number of research projects currently in database
        count_after_insert = ResearchProject.objects.all().count()

        # Check if it has increased
        self.assertEqual(count_after_insert, count_before_insert + 1)

    def test_research_project_update(self):
        research_project = ObjectsFactory.create_research_project()

        # Create an instance of a GET request.
        request = self.factory.get(
            reverse(
                "research_project_edit",
                args=[
                    research_project.pk,
                ],
            )
        )
        request.user = self.user

        response = research_project_update(
            request, research_project_id=research_project.pk
        )
        self.assertEqual(response.status_code, 200)

        # Update
        self.data = {
            "action": "save",
            "title": "New research project title",
            "start_date": [datetime.date.today() - datetime.timedelta(days=1)],
            "description": ["New research project description"],
        }
        response = self.client.post(
            reverse("research_project_edit", args=(research_project.pk,)),
            self.data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

    def test_research_project_remove(self):
        # Create a research project to be used in the test
        research_project = ObjectsFactory.create_research_project()

        # Save current number of research projects
        count = ResearchProject.objects.all().count()

        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("research_project_view", args=(research_project.pk,)),
            self.data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        # Check if numeber of reserch projets decreased by 1
        self.assertEqual(ResearchProject.objects.all().count(), count - 1)

    def test_research_project_keywords(self):
        # Create a research project to be used in the test
        research_project = ObjectsFactory.create_research_project()

        # Insert keyword
        self.assertEqual(Keyword.objects.all().count(), 0)
        self.assertEqual(research_project.keywords.count(), 0)
        response = self.client.get(
            reverse("keyword_new", args=(research_project.pk, "test_keyword")),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 1)
        self.assertEqual(research_project.keywords.count(), 1)

        # Add keyword
        keyword = Keyword.objects.create(name="second_test_keyword")
        keyword.save()
        self.assertEqual(Keyword.objects.all().count(), 2)
        self.assertEqual(research_project.keywords.count(), 1)
        response = self.client.get(
            reverse("keyword_add", args=(research_project.pk, keyword.id)), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 2)
        self.assertEqual(research_project.keywords.count(), 2)

        # Create a second research project to be used in the test
        research_project2 = ObjectsFactory.create_research_project()

        # Insert keyword
        response = self.client.get(
            reverse("keyword_new", args=(research_project2.pk, "third_test_keyword")),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 3)
        self.assertEqual(research_project2.keywords.count(), 1)

        # Add keyword
        response = self.client.get(
            reverse("keyword_add", args=(research_project2.pk, keyword.id)), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 3)
        self.assertEqual(research_project2.keywords.count(), 2)

        # Search keyword using ajax
        self.data = {
            "search_text": "test_keyword",
            "research_project_id": research_project2.id,
        }
        response = self.client.post(reverse("keywords_search"), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response, 'Adicionar nova palavra-chave "test_keyword"'
        )  # Already exists.
        self.assertNotContains(
            response, "second_test_keyword"
        )  # Already in the project
        self.assertNotContains(response, "third_test_keyword")  # Already in the project
        self.assertContains(response, "test_keyword")  # Should be suggested

        # Add the suggested keyword
        first_quote_index = response.content.index(b'"')
        second_quote_index = response.content.index(b'"', first_quote_index + 1)
        url = response.content[first_quote_index + 1 : second_quote_index] + b"/"
        response = self.client.get(url.decode("utf-8"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(research_project2.keywords.count(), 3)

        # Remove keyword that is also in another research project
        response = self.client.get(
            reverse("keyword_remove", args=(research_project2.pk, keyword.id)),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 3)
        self.assertEqual(research_project2.keywords.count(), 2)

        # Remove keyword that is not in another research project
        keyword3 = Keyword.objects.get(name="third_test_keyword")
        response = self.client.get(
            reverse("keyword_remove", args=(research_project2.pk, keyword3.id)),
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 2)
        self.assertEqual(research_project2.keywords.count(), 1)


class EEGSettingTest(TestCase):
    data: dict[str, Any] = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        research_project = ObjectsFactory.create_research_project()

        self.experiment = ObjectsFactory.create_experiment(research_project)

    def test_crud_eeg_setting(self):
        # screen to create an eeg_setting
        response = self.client.get(
            reverse("eeg_setting_new", args=(self.experiment.id,))
        )
        self.assertEqual(response.status_code, 200)

        name = "EEG setting name"
        description = "EEG setting description"
        self.data = {"action": "save", "name": name, "description": description}
        response = self.client.post(
            reverse("eeg_setting_new", args=(self.experiment.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            EEGSetting.objects.filter(name=name, description=description).exists()
        )

        eeg_setting = EEGSetting.objects.filter(name=name, description=description)[0]

        # screen to view an eeg_setting
        response = self.client.get(reverse("eeg_setting_view", args=(eeg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # screen to update an eeg_setting
        response = self.client.get(reverse("eeg_setting_edit", args=(eeg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # update with no changes
        self.data = {"action": "save", "name": name, "description": description}
        response = self.client.post(
            reverse("eeg_setting_edit", args=(eeg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            EEGSetting.objects.filter(name=name, description=description).exists()
        )

        name = "EEG setting name updated"
        description = "EEG setting description updated"
        self.data = {"action": "save", "name": name, "description": description}
        response = self.client.post(
            reverse("eeg_setting_edit", args=(eeg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            EEGSetting.objects.filter(name=name, description=description).exists()
        )

        # remove an eeg_setting
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data
        )
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
        response = self.client.get(
            reverse("view_eeg_setting_type", args=(eeg_setting.id, "amplifier"))
        )
        self.assertEqual(response.status_code, 200)

        # create an eeg_amplifier_setting
        self.data = {
            "action": "save",
            "equipment_selection": eeg_amplifier.id,
            "gain": "10",
            "number_of_channels_used": "2",
        }
        response = self.client.post(
            reverse("view_eeg_setting_type", args=(eeg_setting.id, "amplifier")),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # screen to view the eeg_amplifier_setting
        response = self.client.get(
            reverse("view_eeg_setting_type", args=(eeg_setting.id, "amplifier"))
        )
        self.assertEqual(response.status_code, 200)

        # update the eeg_amplifier_setting
        response = self.client.get(
            reverse("edit_eeg_setting_type", args=(eeg_setting.id, "amplifier"))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "equipment_selection": eeg_amplifier.id,
            "gain": "20",
            "number_of_channels_used": "3",
        }
        response = self.client.post(
            reverse("edit_eeg_setting_type", args=(eeg_setting.id, "amplifier")),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # remove an eeg_amplifier_setting
        self.data = {"action": "remove-eeg_amplifier"}
        response = self.client.post(
            reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

    def test_eeg_setting_eeg_solution(self):
        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)

        manufacturer = ObjectsFactory.create_manufacturer()
        eeg_solution = ObjectsFactory.create_eeg_solution(manufacturer)

        # screen to an (unexisting) eeg_solution_setting
        response = self.client.get(
            reverse("view_eeg_setting_type", args=(eeg_setting.id, "eeg_solution"))
        )
        self.assertEqual(response.status_code, 200)

        # create an eeg_solution_setting
        self.data = {"action": "save", "solution_selection": eeg_solution.id}
        response = self.client.post(
            reverse("view_eeg_setting_type", args=(eeg_setting.id, "eeg_solution")),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # screen to view the eeg_solution_setting
        response = self.client.get(
            reverse("view_eeg_setting_type", args=(eeg_setting.id, "eeg_solution"))
        )
        self.assertEqual(response.status_code, 200)

        # update the eeg_solution_setting
        response = self.client.get(
            reverse("edit_eeg_setting_type", args=(eeg_setting.id, "eeg_solution"))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "solution_selection": eeg_solution.id}
        response = self.client.post(
            reverse("edit_eeg_setting_type", args=(eeg_setting.id, "eeg_solution")),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # remove an eeg_solution_setting
        self.data = {"action": "remove-eeg_solution"}
        response = self.client.post(
            reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

    def test_eeg_setting_eeg_filter(self):
        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)

        filter_type = ObjectsFactory.create_filter_type()

        # screen to an (unexisting) eeg_filter_setting
        response = self.client.get(
            reverse("view_eeg_setting_type", args=(eeg_setting.id, "filter"))
        )
        self.assertEqual(response.status_code, 200)

        # create an eeg_filter_setting
        self.data = {
            "action": "save",
            "filter_selection": filter_type.id,
            "high_pass": "80",
            "low_pass": "20",
            "order": "2",
        }
        response = self.client.post(
            reverse("view_eeg_setting_type", args=(eeg_setting.id, "filter")), self.data
        )
        self.assertEqual(response.status_code, 302)

        # screen to view the eeg_filter_setting
        response = self.client.get(
            reverse("view_eeg_setting_type", args=(eeg_setting.id, "filter"))
        )
        self.assertEqual(response.status_code, 200)

        # update the eeg_filter_setting
        response = self.client.get(
            reverse("edit_eeg_setting_type", args=(eeg_setting.id, "filter"))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "filter_selection": filter_type.id,
            "high_pass": "90",
            "low_pass": "20",
            "order": "2",
        }
        response = self.client.post(
            reverse("edit_eeg_setting_type", args=(eeg_setting.id, "filter")), self.data
        )
        self.assertEqual(response.status_code, 302)

        # remove an eeg_filter_setting
        self.data = {"action": "remove-eeg_filter"}
        response = self.client.post(
            reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

    def test_eeg_setting_eeg_net_system(self):
        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)

        manufacturer = ObjectsFactory.create_manufacturer()
        electrode_model = ObjectsFactory.create_electrode_model()
        eeg_electrode_net = ObjectsFactory.create_eeg_electrode_net(
            manufacturer, electrode_model
        )
        eeg_localization_system = (
            ObjectsFactory.create_eeg_electrode_localization_system()
        )

        # creating 2 positions to configure be configured when the setting is created
        ObjectsFactory.create_eeg_electrode_position(eeg_localization_system)
        ObjectsFactory.create_eeg_electrode_position(eeg_localization_system)

        ObjectsFactory.create_eeg_electrode_net_system(
            eeg_electrode_net, eeg_localization_system
        )

        # screen to an (unexisting) eeg_electrode_net_system_setting
        response = self.client.get(
            reverse(
                "view_eeg_setting_type",
                args=(eeg_setting.id, "eeg_electrode_net_system"),
            )
        )
        self.assertEqual(response.status_code, 200)

        # create an eeg_electrode_net_system_setting
        self.data = {
            "action": "save",
            "equipment_selection": eeg_electrode_net.id,
            "localization_system_selection": eeg_localization_system.id,
        }
        response = self.client.post(
            reverse(
                "view_eeg_setting_type",
                args=(eeg_setting.id, "eeg_electrode_net_system"),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # screen to view the eeg_electrode_net_system_setting
        response = self.client.get(
            reverse(
                "view_eeg_setting_type",
                args=(eeg_setting.id, "eeg_electrode_net_system"),
            )
        )
        self.assertEqual(response.status_code, 200)

        # update the eeg_electrode_net_system_setting with another localization system

        eeg_localization_system_new = (
            ObjectsFactory.create_eeg_electrode_localization_system()
        )
        ObjectsFactory.create_eeg_electrode_position(eeg_localization_system_new)
        ObjectsFactory.create_eeg_electrode_position(eeg_localization_system_new)
        ObjectsFactory.create_eeg_electrode_net_system(
            eeg_electrode_net, eeg_localization_system_new
        )

        response = self.client.get(
            reverse(
                "edit_eeg_setting_type",
                args=(eeg_setting.id, "eeg_electrode_net_system"),
            )
        )
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "equipment_selection": eeg_electrode_net.id,
            "localization_system_selection": eeg_localization_system_new.id,
        }
        response = self.client.post(
            reverse(
                "edit_eeg_setting_type",
                args=(eeg_setting.id, "eeg_electrode_net_system"),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # configuring the used electrodes
        response = self.client.get(
            reverse("eeg_electrode_position_setting", args=(eeg_setting.id,))
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("edit_eeg_electrode_position_setting", args=(eeg_setting.id,))
        )
        self.assertEqual(response.status_code, 200)

        position_setting_list = []
        for (
            position_setting
        ) in eeg_setting.eeg_electrode_layout_setting.positions_setting.all():
            position_setting_list.append(position_setting)

        self.data = {
            "action": "save",
            "position_status_" + str(position_setting_list[0].id): "on",
        }
        response = self.client.post(
            reverse("edit_eeg_electrode_position_setting", args=(eeg_setting.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # configuring the electrodes models

        response = self.client.get(
            reverse("eeg_electrode_position_setting_model", args=(eeg_setting.id,))
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse("edit_eeg_electrode_position_setting_model", args=(eeg_setting.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "electrode_model_"
            + str(position_setting_list[0].id): str(electrode_model.id),
            "electrode_model_"
            + str(position_setting_list[1].id): str(electrode_model.id),
        }
        response = self.client.post(
            reverse(
                "edit_eeg_electrode_position_setting_model", args=(eeg_setting.id,)
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # remove an eeg_electrode_net_system_setting
        self.data = {"action": "remove-eeg_electrode_net_system"}
        response = self.client.post(
            reverse("eeg_setting_view", args=(eeg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)


class EEGEquipmentRegisterTest(TestCase):
    data: dict[str, Any] = {}

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

        name = "Name"
        self.data = {"action": "save", "name": name}

        response = self.client.post(reverse("manufacturer_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Manufacturer.objects.all().count(), 1)

        # view
        manufacturer = Manufacturer.objects.all().first()

        response = self.client.get(
            reverse("manufacturer_view", args=(manufacturer.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("manufacturer_edit", args=(manufacturer.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("manufacturer_edit", args=(manufacturer.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("manufacturer_edit", args=(manufacturer.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("manufacturer_view", args=(manufacturer.id,)), self.data
        )
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

        identification = "Identification"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
            "tag_1": "on",
            "tag_2": "on",
        }

        response = self.client.post(reverse("amplifier_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Amplifier.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(reverse("amplifier_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Amplifier.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(reverse("amplifier_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Amplifier.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        amplifier = Amplifier.objects.all().first()

        response = self.client.get(reverse("amplifier_view", args=(amplifier.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("amplifier_edit", args=(amplifier.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
            "tag_1": "on",
            "tag_2": "on",
        }
        response = self.client.post(
            reverse("amplifier_edit", args=(amplifier.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        identification = "Identification changed"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
            "tag_1": "on",
            "tag_2": "on",
        }
        response = self.client.post(
            reverse("amplifier_edit", args=(amplifier.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("amplifier_edit", args=(amplifier.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(Amplifier, pk=amplifier.id).identification, identification
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("amplifier_view", args=(amplifier.id,)), self.data
        )
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

        name = "Name"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "name": name,
        }

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

        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "name": name,
        }
        response = self.client.post(
            reverse("eegsolution_edit", args=(eeg_solution.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "name": name,
        }
        response = self.client.post(
            reverse("eegsolution_edit", args=(eeg_solution.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("eegsolution_view", args=(eeg_solution.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGSolution.objects.all().count(), 0)

    def test_filter_type_register(self):
        # list
        response = self.client.get(reverse("filtertype_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("filtertype_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = "Name"
        self.data = {"action": "save", "name": name}

        response = self.client.post(reverse("filtertype_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FilterType.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(reverse("filtertype_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FilterType.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(reverse("filtertype_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FilterType.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        filter_type = FilterType.objects.all().first()

        response = self.client.get(reverse("filtertype_view", args=(filter_type.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("filtertype_edit", args=(filter_type.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("filtertype_edit", args=(filter_type.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("filtertype_edit", args=(filter_type.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("filtertype_edit", args=(filter_type.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(FilterType, pk=filter_type.id).name, name)

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("filtertype_view", args=(filter_type.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FilterType.objects.all().count(), 0)

    def test_standardization_system_register(self):
        # list
        response = self.client.get(reverse("standardization_system_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("standardization_system_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = "Name"
        self.data = {"action": "save", "name": name}

        number_of_registers = StandardizationSystem.objects.all().count()

        response = self.client.post(
            reverse("standardization_system_new", args=()), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            StandardizationSystem.objects.all().count(), number_of_registers + 1
        )

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(
            reverse("standardization_system_new", args=()), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            StandardizationSystem.objects.all().count(), number_of_registers + 1
        )
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(
            reverse("standardization_system_new", args=()), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            StandardizationSystem.objects.all().count(), number_of_registers + 1
        )
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        standardization_system = StandardizationSystem.objects.all().first()

        response = self.client.get(
            reverse("standardization_system_view", args=(standardization_system.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("standardization_system_edit", args=(standardization_system.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("standardization_system_edit", args=(standardization_system.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("standardization_system_edit", args=(standardization_system.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("standardization_system_edit", args=(standardization_system.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(StandardizationSystem, pk=standardization_system.id).name,
            name,
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("standardization_system_view", args=(standardization_system.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            StandardizationSystem.objects.all().count(), number_of_registers
        )

    def test_emg_surface_electrode_placement_register(self):
        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        muscle_subdivision_2 = ObjectsFactory.create_muscle_subdivision(muscle)

        # create surface
        response = self.client.get(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "surface"),
            )
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "muscle_subdivision": str(muscle_subdivision.id)}

        number_of_registers = EMGElectrodePlacement.objects.all().count()

        response = self.client.post(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "surface"),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers + 1
        )

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "surface"),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers + 1
        )
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "surface"),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers + 1
        )
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        emg_electrode_placement = EMGElectrodePlacement.objects.filter(
            standardization_system=standardization_system
        ).first()

        response = self.client.get(
            reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "muscle_subdivision": str(muscle_subdivision.id)}
        response = self.client.post(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        self.data = {
            "action": "save",
            "muscle_subdivision": str(muscle_subdivision_2.id),
        }
        response = self.client.post(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(
                EMGElectrodePlacement, pk=emg_electrode_placement.id
            ).muscle_subdivision.id,
            muscle_subdivision_2.id,
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers
        )

    def test_emg_intramuscular_electrode_placement_register(self):
        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        muscle_subdivision_2 = ObjectsFactory.create_muscle_subdivision(muscle)

        # create surface
        response = self.client.get(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "intramuscular"),
            )
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "muscle_subdivision": str(muscle_subdivision.id)}

        number_of_registers = EMGElectrodePlacement.objects.all().count()

        response = self.client.post(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "intramuscular"),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers + 1
        )

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "intramuscular"),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers + 1
        )
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "intramuscular"),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers + 1
        )
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        emg_electrode_placement = EMGElectrodePlacement.objects.filter(
            standardization_system=standardization_system
        ).first()

        response = self.client.get(
            reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "muscle_subdivision": str(muscle_subdivision.id)}
        response = self.client.post(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        self.data = {
            "action": "save",
            "muscle_subdivision": str(muscle_subdivision_2.id),
        }
        response = self.client.post(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(
                EMGElectrodePlacement, pk=emg_electrode_placement.id
            ).muscle_subdivision.id,
            muscle_subdivision_2.id,
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers
        )

    def test_emg_needle_electrode_placement_register(self):
        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        muscle_subdivision_2 = ObjectsFactory.create_muscle_subdivision(muscle)

        # create surface
        response = self.client.get(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "needle"),
            )
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "muscle_subdivision": str(muscle_subdivision.id)}

        number_of_registers = EMGElectrodePlacement.objects.all().count()

        response = self.client.post(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "needle"),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers + 1
        )

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "needle"),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers + 1
        )
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(
            reverse(
                "emg_electrode_placement_new",
                args=(standardization_system.id, "needle"),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers + 1
        )
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        emg_electrode_placement = EMGElectrodePlacement.objects.filter(
            standardization_system=standardization_system
        ).first()

        response = self.client.get(
            reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "muscle_subdivision": str(muscle_subdivision.id)}
        response = self.client.post(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        self.data = {
            "action": "save",
            "muscle_subdivision": str(muscle_subdivision_2.id),
        }
        response = self.client.post(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("emg_electrode_placement_edit", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(
                EMGElectrodePlacement, pk=emg_electrode_placement.id
            ).muscle_subdivision.id,
            muscle_subdivision_2.id,
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("emg_electrode_placement_view", args=(emg_electrode_placement.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            EMGElectrodePlacement.objects.all().count(), number_of_registers
        )

    def test_muscle_register(self):
        # list
        response = self.client.get(reverse("muscle_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("muscle_new", args=()))
        self.assertEqual(response.status_code, 200)

        number_of_registers = Muscle.objects.all().count()

        name = "Name"
        self.data = {"action": "save", "name": name}

        response = self.client.post(reverse("muscle_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Muscle.objects.all().count(), number_of_registers + 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(reverse("muscle_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Muscle.objects.all().count(), number_of_registers + 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(reverse("muscle_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Muscle.objects.all().count(), number_of_registers + 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        muscle = Muscle.objects.all().first()

        response = self.client.get(reverse("muscle_view", args=(muscle.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("muscle_edit", args=(muscle.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("muscle_edit", args=(muscle.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("muscle_edit", args=(muscle.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("muscle_edit", args=(muscle.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(Muscle, pk=muscle.id).name, name)

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("muscle_view", args=(muscle.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Muscle.objects.all().count(), number_of_registers)

    def test_muscle_subdivision_register(self):
        muscle = ObjectsFactory.create_muscle()

        # create
        response = self.client.get(reverse("muscle_subdivision_new", args=(muscle.id,)))
        self.assertEqual(response.status_code, 200)

        number_of_registers = MuscleSubdivision.objects.all().count()

        name = "Name"
        self.data = {"action": "save", "name": name}

        response = self.client.post(
            reverse("muscle_subdivision_new", args=(muscle.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            MuscleSubdivision.objects.all().count(), number_of_registers + 1
        )

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(
            reverse("muscle_subdivision_new", args=(muscle.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            MuscleSubdivision.objects.all().count(), number_of_registers + 1
        )
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(
            reverse("muscle_subdivision_new", args=(muscle.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            MuscleSubdivision.objects.all().count(), number_of_registers + 1
        )
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        muscle_subdivision = MuscleSubdivision.objects.filter(muscle=muscle).first()

        response = self.client.get(
            reverse("muscle_subdivision_view", args=(muscle_subdivision.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("muscle_subdivision_edit", args=(muscle_subdivision.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("muscle_subdivision_edit", args=(muscle_subdivision.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("muscle_subdivision_edit", args=(muscle_subdivision.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("muscle_subdivision_edit", args=(muscle_subdivision.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(MuscleSubdivision, pk=muscle_subdivision.id).name, name
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("muscle_subdivision_view", args=(muscle_subdivision.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MuscleSubdivision.objects.all().count(), number_of_registers)

    def test_muscle_side_register(self):
        muscle = ObjectsFactory.create_muscle()

        # create
        response = self.client.get(reverse("muscle_side_new", args=(muscle.id,)))
        self.assertEqual(response.status_code, 200)

        number_of_registers = MuscleSide.objects.all().count()

        name = "Name"
        self.data = {"action": "save", "name": name}

        response = self.client.post(
            reverse("muscle_side_new", args=(muscle.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(MuscleSide.objects.all().count(), number_of_registers + 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(
            reverse("muscle_side_new", args=(muscle.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MuscleSide.objects.all().count(), number_of_registers + 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(
            reverse("muscle_side_new", args=(muscle.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MuscleSide.objects.all().count(), number_of_registers + 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        muscle_side = MuscleSide.objects.filter(muscle=muscle).first()

        response = self.client.get(reverse("muscle_side_view", args=(muscle_side.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("muscle_side_edit", args=(muscle_side.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("muscle_side_edit", args=(muscle_side.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("muscle_side_edit", args=(muscle_side.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("muscle_side_edit", args=(muscle_side.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(MuscleSide, pk=muscle_side.id).name, name)

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("muscle_side_view", args=(muscle_side.id,)), self.data
        )
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

        name = "Name"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "name": name,
        }

        response = self.client.post(reverse("software_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Software.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(reverse("software_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Software.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(reverse("software_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Software.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        software = Software.objects.all().first()

        response = self.client.get(reverse("software_view", args=(software.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("software_edit", args=(software.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "name": name,
        }
        response = self.client.post(
            reverse("software_edit", args=(software.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "name": name,
        }
        response = self.client.post(
            reverse("software_edit", args=(software.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("software_edit", args=(software.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(Software, pk=software.id).name, name)

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("software_view", args=(software.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Software.objects.all().count(), 0)

    def test_software_version_register(self):
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)

        # create
        response = self.client.get(reverse("software_version_new", args=(software.id,)))
        self.assertEqual(response.status_code, 200)

        name = "Name"
        self.data = {"action": "save", "name": name}

        response = self.client.post(
            reverse("software_version_new", args=(software.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SoftwareVersion.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(
            reverse("software_version_new", args=(software.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SoftwareVersion.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(
            reverse("software_version_new", args=(software.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(SoftwareVersion.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        software_version = SoftwareVersion.objects.filter(software=software).first()

        response = self.client.get(
            reverse("software_version_view", args=(software_version.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("software_version_edit", args=(software_version.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("software_version_edit", args=(software_version.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("software_version_edit", args=(software_version.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("software_version_edit", args=(software_version.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(SoftwareVersion, pk=software_version.id).name, name
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("software_version_view", args=(software_version.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(SoftwareVersion.objects.all().count(), 0)

    def test_electrode_model_register(self):
        # list
        response = self.client.get(reverse("electrodemodel_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("electrodemodel_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = "Name"
        self.data = {"action": "save", "name": name, "electrode_type": "surface"}
        response = self.client.post(reverse("electrodemodel_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ElectrodeModel.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(reverse("electrodemodel_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ElectrodeModel.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(reverse("electrodemodel_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ElectrodeModel.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        electrode_model = ElectrodeModel.objects.all().first()

        response = self.client.get(
            reverse("electrodemodel_view", args=(electrode_model.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("electrodemodel_edit", args=(electrode_model.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name, "electrode_type": "surface"}
        response = self.client.post(
            reverse("electrodemodel_edit", args=(electrode_model.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name, "electrode_type": "surface"}
        response = self.client.post(
            reverse("electrodemodel_edit", args=(electrode_model.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("electrodemodel_edit", args=(electrode_model.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(ElectrodeModel, pk=electrode_model.id).name, name
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("electrodemodel_view", args=(electrode_model.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ElectrodeModel.objects.all().count(), 0)

    def test_material_register(self):
        # list
        response = self.client.get(reverse("material_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("material_new", args=()))
        self.assertEqual(response.status_code, 200)

        name = "Name"
        self.data = {"action": "save", "name": name}
        response = self.client.post(reverse("material_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Material.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(reverse("material_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Material.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(reverse("material_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Material.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        material = Material.objects.all().first()

        response = self.client.get(reverse("material_view", args=(material.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("material_edit", args=(material.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("material_edit", args=(material.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("material_edit", args=(material.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("material_edit", args=(material.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(Material, pk=material.id).name, name)

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("material_view", args=(material.id,)), self.data
        )
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

        identification = "Identification"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
            "electrode_model_default": str(electrode_model.id),
        }

        response = self.client.post(reverse("eegelectrodenet_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(reverse("eegelectrodenet_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(reverse("eegelectrodenet_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        electrode_net = EEGElectrodeNet.objects.all().first()

        response = self.client.get(
            reverse("eegelectrodenet_view", args=(electrode_net.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("eegelectrodenet_edit", args=(electrode_net.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
            "electrode_model_default": str(electrode_model.id),
        }
        response = self.client.post(
            reverse("eegelectrodenet_edit", args=(electrode_net.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        identification = "Identification changed"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
            "electrode_model_default": str(electrode_model.id),
        }
        response = self.client.post(
            reverse("eegelectrodenet_edit", args=(electrode_net.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("eegelectrodenet_edit", args=(electrode_net.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(EEGElectrodeNet, pk=electrode_net.id).identification,
            identification,
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("eegelectrodenet_view", args=(electrode_net.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 0)

    def test_electrode_net_register_cap(self):
        manufacturer = ObjectsFactory.create_manufacturer()
        electrode_model = ObjectsFactory.create_electrode_model()
        material = ObjectsFactory.create_material()
        material_2 = ObjectsFactory.create_material()

        electrode_localization_system = (
            ObjectsFactory.create_eeg_electrode_localization_system()
        )
        electrode_localization_system_2 = (
            ObjectsFactory.create_eeg_electrode_localization_system()
        )

        # create a electrode_net (cap)

        response = self.client.get(reverse("eegelectrodenet_new", args=()))
        self.assertEqual(response.status_code, 200)

        identification = "Identification"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
            "electrode_model_default": str(electrode_model.id),
            "cap_flag": "on",
            "material": str(material.id),
            "localization_system_" + str(electrode_localization_system.id): "on",
        }

        response = self.client.post(reverse("eegelectrodenet_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 1)
        self.assertEqual(EEGElectrodeCap.objects.all().count(), 1)

        # view
        electrode_net = EEGElectrodeCap.objects.all().first()

        response = self.client.get(
            reverse("eegelectrodenet_view", args=(electrode_net.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("eegelectrodenet_edit", args=(electrode_net.id,))
        )
        self.assertEqual(response.status_code, 200)

        identification = "Identification changed"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
            "electrode_model_default": str(electrode_model.id),
            "cap_flag": "on",
            "material": str(material_2.id),
            "localization_system_" + str(electrode_localization_system_2.id): "on",
        }
        response = self.client.post(
            reverse("eegelectrodenet_edit", args=(electrode_net.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("eegelectrodenet_view", args=(electrode_net.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeNet.objects.all().count(), 0)

    def test_cap_size_register(self):
        manufacturer = ObjectsFactory.create_manufacturer()
        electrode_model = ObjectsFactory.create_electrode_model()
        eeg_electrode_cap = ObjectsFactory.create_eeg_electrode_cap(
            manufacturer, electrode_model
        )

        # create
        response = self.client.get(
            reverse("eegelectrodenet_add_size", args=(eeg_electrode_cap.id,))
        )
        self.assertEqual(response.status_code, 200)

        size = "Size"
        self.data = {"action": "save", "size": size}

        response = self.client.post(
            reverse("eegelectrodenet_add_size", args=(eeg_electrode_cap.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGCapSize.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(
            reverse("eegelectrodenet_add_size", args=(eeg_electrode_cap.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGCapSize.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(
            reverse("eegelectrodenet_add_size", args=(eeg_electrode_cap.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGCapSize.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        cap_size = EEGCapSize.objects.filter(
            eeg_electrode_cap=eeg_electrode_cap
        ).first()

        response = self.client.get(
            reverse("eegelectrodenet_cap_size_view", args=(cap_size.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("eegelectrodenet_cap_size_edit", args=(cap_size.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "size": size}
        response = self.client.post(
            reverse("eegelectrodenet_cap_size_edit", args=(cap_size.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        size = "Size changed"
        self.data = {"action": "save", "size": size}
        response = self.client.post(
            reverse("eegelectrodenet_cap_size_edit", args=(cap_size.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("eegelectrodenet_cap_size_edit", args=(cap_size.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(EEGCapSize, pk=cap_size.id).size, size)

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("eegelectrodenet_cap_size_view", args=(cap_size.id,)), self.data
        )
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

        identification = "Identification"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
        }

        response = self.client.post(reverse("ad_converter_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ADConverter.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(reverse("ad_converter_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ADConverter.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(reverse("ad_converter_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ADConverter.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        ad_converter = ADConverter.objects.all().first()

        response = self.client.get(
            reverse("ad_converter_view", args=(ad_converter.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("ad_converter_edit", args=(ad_converter.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
        }
        response = self.client.post(
            reverse("ad_converter_edit", args=(ad_converter.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        identification = "Identification changed"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
        }
        response = self.client.post(
            reverse("ad_converter_edit", args=(ad_converter.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("ad_converter_edit", args=(ad_converter.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(ADConverter, pk=ad_converter.id).identification,
            identification,
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("ad_converter_view", args=(ad_converter.id,)), self.data
        )
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

        name = "Name"
        self.data = {"action": "save", "name": name, "coil_shape": str(coil_shape.id)}

        response = self.client.post(reverse("coil_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CoilModel.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(reverse("coil_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CoilModel.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(reverse("coil_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CoilModel.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        coil_model = CoilModel.objects.all().first()

        response = self.client.get(reverse("coil_view", args=(coil_model.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("coil_edit", args=(coil_model.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name, "coil_shape": str(coil_shape.id)}
        response = self.client.post(
            reverse("coil_edit", args=(coil_model.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name, "coil_shape": str(coil_shape.id)}
        response = self.client.post(
            reverse("coil_edit", args=(coil_model.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("coil_edit", args=(coil_model.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_object_or_404(CoilModel, pk=coil_model.id).name, name)

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("coil_view", args=(coil_model.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CoilModel.objects.all().count(), 0)

    def test_tms_device_register(self):
        manufacturer = ObjectsFactory.create_manufacturer()
        coil_shape = ObjectsFactory.create_coil_shape()
        coil_model = ObjectsFactory.create_coil_model(coil_shape)

        # list
        response = self.client.get(reverse("tmsdevice_list", args=()))
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(reverse("tmsdevice_new", args=()))
        self.assertEqual(response.status_code, 200)

        identification = "Identification"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
            "coil_model": str(coil_model.id),
        }

        response = self.client.post(reverse("tmsdevice_new", args=()), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TMSDevice.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(reverse("tmsdevice_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TMSDevice.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(reverse("tmsdevice_new", args=()), self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TMSDevice.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        tms_device = TMSDevice.objects.all().first()

        response = self.client.get(reverse("tmsdevice_view", args=(tms_device.id,)))
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(reverse("tmsdevice_edit", args=(tms_device.id,)))
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
            "coil_model": str(coil_model.id),
        }
        response = self.client.post(
            reverse("tmsdevice_edit", args=(tms_device.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        identification = "Identification changed"
        self.data = {
            "action": "save",
            "manufacturer": str(manufacturer.id),
            "identification": identification,
            "coil_model": str(coil_model.id),
        }
        response = self.client.post(
            reverse("tmsdevice_edit", args=(tms_device.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("tmsdevice_edit", args=(tms_device.id,)), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(TMSDevice, pk=tms_device.id).identification,
            identification,
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("tmsdevice_view", args=(tms_device.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(TMSDevice.objects.all().count(), 0)

    def test_eeg_electrode_localization_system_register(self):
        # list
        response = self.client.get(
            reverse("eeg_electrode_localization_system_list", args=())
        )
        self.assertEqual(response.status_code, 200)

        # create
        response = self.client.get(
            reverse("eeg_electrode_localization_system_new", args=())
        )
        self.assertEqual(response.status_code, 200)

        name = "Name"
        self.data = {"action": "save", "name": name}

        response = self.client.post(
            reverse("eeg_electrode_localization_system_new", args=()), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeLocalizationSystem.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(
            reverse("eeg_electrode_localization_system_new", args=()), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodeLocalizationSystem.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(
            reverse("eeg_electrode_localization_system_new", args=()), self.data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodeLocalizationSystem.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        eeg_electrode_localization_system = (
            EEGElectrodeLocalizationSystem.objects.all().first()
        )

        response = self.client.get(
            reverse(
                "eeg_electrode_localization_system_view",
                args=(eeg_electrode_localization_system.id,),
            )
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse(
                "eeg_electrode_localization_system_edit",
                args=(eeg_electrode_localization_system.id,),
            )
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse(
                "eeg_electrode_localization_system_edit",
                args=(eeg_electrode_localization_system.id,),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse(
                "eeg_electrode_localization_system_edit",
                args=(eeg_electrode_localization_system.id,),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse(
                "eeg_electrode_localization_system_edit",
                args=(eeg_electrode_localization_system.id,),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(
                EEGElectrodeLocalizationSystem, pk=eeg_electrode_localization_system.id
            ).name,
            name,
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse(
                "eeg_electrode_localization_system_view",
                args=(eeg_electrode_localization_system.id,),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodeLocalizationSystem.objects.all().count(), 0)

    def test_eeg_electrode_position_register(self):
        eeg_electrode_localization_system = (
            ObjectsFactory.create_eeg_electrode_localization_system()
        )

        # create
        response = self.client.get(
            reverse(
                "eeg_electrode_position_create",
                args=(eeg_electrode_localization_system.id,),
            )
        )
        self.assertEqual(response.status_code, 200)

        name = "Name"
        self.data = {"action": "save", "name": name}

        response = self.client.post(
            reverse(
                "eeg_electrode_position_create",
                args=(eeg_electrode_localization_system.id,),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodePosition.objects.all().count(), 1)

        # create (trying) but missing information
        self.data = {"action": "save"}

        response = self.client.post(
            reverse(
                "eeg_electrode_position_create",
                args=(eeg_electrode_localization_system.id,),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodePosition.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Information not saved.")
        )

        # create with wrong action
        self.data = {"action": "wrong"}

        response = self.client.post(
            reverse(
                "eeg_electrode_position_create",
                args=(eeg_electrode_localization_system.id,),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EEGElectrodePosition.objects.all().count(), 1)
        self.assertEqual(
            str(list(response.context["messages"])[-1]), _("Action not available.")
        )

        # view
        eeg_electrode_position = EEGElectrodePosition.objects.filter(
            eeg_electrode_localization_system=eeg_electrode_localization_system
        ).first()

        response = self.client.get(
            reverse("eeg_electrode_position_view", args=(eeg_electrode_position.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update
        response = self.client.get(
            reverse("eeg_electrode_position_edit", args=(eeg_electrode_position.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("eeg_electrode_position_edit", args=(eeg_electrode_position.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        name = "Name changed"
        self.data = {"action": "save", "name": name}
        response = self.client.post(
            reverse("eeg_electrode_position_edit", args=(eeg_electrode_position.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # update (trying) but missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse("eeg_electrode_position_edit", args=(eeg_electrode_position.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_object_or_404(EEGElectrodePosition, pk=eeg_electrode_position.id).name,
            name,
        )

        # remove
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("eeg_electrode_position_view", args=(eeg_electrode_position.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EEGElectrodePosition.objects.all().count(), 0)


class EMGSettingTest(TestCase):
    data: dict[str, Any] = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

        research_project = ObjectsFactory.create_research_project()

        self.experiment = ObjectsFactory.create_experiment(research_project)

        self.manufacturer = ObjectsFactory.create_manufacturer()
        self.software = ObjectsFactory.create_software(self.manufacturer)
        self.software_version = ObjectsFactory.create_software_version(self.software)
        self.tag_emg = ObjectsFactory.create_tag("EMG")

    def test_crud_emg_setting(self):
        # create emg setting
        response = self.client.get(
            reverse("emg_setting_new", args=(self.experiment.id,))
        )
        self.assertEqual(response.status_code, 200)

        name = "EMG setting name"
        description = "EMG setting description"
        self.data = {
            "action": "save",
            "name": name,
            "description": description,
            "software_version": self.software_version.id,
        }
        response = self.client.post(
            reverse("emg_setting_new", args=(self.experiment.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            EMGSetting.objects.filter(name=name, description=description).exists()
        )

        emg_setting = EMGSetting.objects.filter(name=name, description=description)[0]

        # view an emg setting
        response = self.client.get(reverse("emg_setting_view", args=(emg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # update an emg setting
        response = self.client.get(reverse("emg_setting_edit", args=(emg_setting.id,)))
        self.assertEqual(response.status_code, 200)

        # update with no changes
        self.data = {
            "action": "save",
            "name": name,
            "description": description,
            "software_version": self.software_version.id,
        }
        response = self.client.post(
            reverse("emg_setting_edit", args=(emg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            EMGSetting.objects.filter(name=name, description=description).exists()
        )

        name = "EMG setting name updated"
        description = "EMG setting description updated"
        self.data = {
            "action": "save",
            "name": name,
            "description": description,
            "software_version": self.software_version.id,
        }
        response = self.client.post(
            reverse("emg_setting_edit", args=(emg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            EMGSetting.objects.filter(name=name, description=description).exists()
        )

        # remove an emg setting
        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("emg_setting_view", args=(emg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

    def test_emg_setting_digital_filter(self):
        emg_setting = ObjectsFactory.create_emg_setting(
            self.experiment, self.software_version
        )

        filter_type = ObjectsFactory.create_filter_type()

        # create an emg digital filter setting
        self.data = {
            "action": "save",
            "filter_type": filter_type.id,
            "high_pass": "80",
            "low_pass": "20",
            "band_pass": "7",
            "order": "2",
            "notch": "5",
        }
        response = self.client.post(
            reverse("emg_setting_digital_filter", args=(emg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # screen to view the emg digital filter setting
        response = self.client.get(
            reverse("emg_setting_digital_filter", args=(emg_setting.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update the emg digital filter setting
        response = self.client.get(
            reverse("emg_setting_digital_filter_edit", args=(emg_setting.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "filter_type": filter_type.id,
            "high_pass": "90",
            "low_pass": "20",
            "order": "2",
            "notch": "7",
        }
        response = self.client.post(
            reverse("emg_setting_digital_filter_edit", args=(emg_setting.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # remove an emg digital filter setting
        self.data = {"action": "remove-digital_filter"}
        response = self.client.post(
            reverse("emg_setting_view", args=(emg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

    def test_emg_setting_ad_converter(self):
        emg_setting = ObjectsFactory.create_emg_setting(
            self.experiment, self.software_version
        )
        manufacturer = ObjectsFactory.create_manufacturer()

        ad_converter = ObjectsFactory.create_ad_converter(manufacturer)

        # create an emg AD converter setting
        self.data = {
            "action": "save",
            "ad_converter": ad_converter.id,
            "sampling_rate": "10",
        }
        response = self.client.post(
            reverse("emg_setting_ad_converter", args=(emg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # screen to view the emg AD converter  setting
        response = self.client.get(
            reverse("emg_setting_ad_converter", args=(emg_setting.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update the emg AD converter  setting
        response = self.client.get(
            reverse("emg_setting_ad_converter_edit", args=(emg_setting.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "ad_converter": ad_converter.id,
            "sampling_rate": "20",
        }
        response = self.client.post(
            reverse("emg_setting_ad_converter_edit", args=(emg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        # remove an emg AD converter setting
        self.data = {"action": "remove-ad_converter"}
        response = self.client.post(
            reverse("emg_setting_view", args=(emg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

    def test_emg_setting_electrode(self):
        emg_setting = ObjectsFactory.create_emg_setting(
            self.experiment, self.software_version
        )
        electrode_model = ObjectsFactory.create_electrode_model()
        tag_emg = Tag.objects.get(name="EMG")
        electrode_model.tags.add(tag_emg)

        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        electrode_placement = ObjectsFactory.create_emg_electrode_placement(
            standardization_system, muscle_subdivision
        )
        muscle_side = ObjectsFactory.create_muscle_side(
            electrode_placement.muscle_subdivision.muscle
        )

        self.data = {
            "action": "save",
            "electrode": electrode_model.id,
            "emg_electrode_placement": electrode_placement.id,
            "remarks": "Remarks",
            "muscle_side": muscle_side.id,
        }

        response = self.client.post(
            reverse("emg_setting_electrode_add", args=(emg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

        emg_electrode_setting = EMGElectrodeSetting.objects.all().first()

        # screen to view the emg electrode  setting
        response = self.client.get(
            reverse("emg_electrode_setting_view", args=(emg_electrode_setting.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update the emg electrode setting
        response = self.client.get(
            reverse("emg_electrode_setting_edit", args=(emg_electrode_setting.id,))
        )
        self.assertEqual(response.status_code, 200)

        self.data = {
            "action": "save",
            "electrode": electrode_model.id,
            "emg_electrode_placement": electrode_placement.id,
            "remarks": "Remarks",
            "muscle_side": muscle_side.id,
        }

        response = self.client.post(
            reverse("emg_electrode_setting_edit", args=(emg_electrode_setting.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # remove an emg electrode setting
        self.data = {"action": "remove-electrode-" + str(emg_electrode_setting.id)}

        response = self.client.post(
            reverse("emg_setting_view", args=(emg_setting.id,)), self.data
        )
        self.assertEqual(response.status_code, 302)

    def test_emg_setting_preamplifier(self):
        emg_setting = ObjectsFactory.create_emg_setting(
            self.experiment, self.software_version
        )
        manufacturer = ObjectsFactory.create_manufacturer()
        amplifier = ObjectsFactory.create_amplifier(manufacturer)
        tag_emg = Tag.objects.get(name="EMG")
        amplifier.tags.add(tag_emg)

        electrode_model = ObjectsFactory.create_electrode_model()

        emg_electrode_setting = ObjectsFactory.create_emg_electrode_setting(
            emg_setting, electrode_model
        )

        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        electrode_placement = ObjectsFactory.create_emg_electrode_placement(
            standardization_system, muscle_subdivision
        )
        muscle_side = ObjectsFactory.create_muscle_side(
            electrode_placement.muscle_subdivision.muscle
        )
        ObjectsFactory.create_emg_electrode_placement_setting(
            emg_electrode_setting, electrode_placement, muscle_side
        )

        # create an emg  preamplifier setting
        self.data = {"action": "save", "amplifier": amplifier.id, "gain": "10"}
        response = self.client.post(
            reverse(
                "emg_electrode_setting_preamplifier", args=(emg_electrode_setting.id,)
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # screen to view the emg  preamplifier setting
        response = self.client.get(
            reverse(
                "emg_electrode_setting_preamplifier", args=(emg_electrode_setting.id,)
            )
        )
        self.assertEqual(response.status_code, 200)

        # update the emg  preamplifier setting
        response = self.client.get(
            reverse(
                "emg_electrode_setting_preamplifier_edit",
                args=(emg_electrode_setting.id,),
            )
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "amplifier": amplifier.id, "gain": "20"}
        response = self.client.post(
            reverse(
                "emg_electrode_setting_preamplifier_edit",
                args=(emg_electrode_setting.id,),
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # remove an emg  preamplifier setting
        self.data = {"action": "remove-preamplifier"}
        response = self.client.post(
            reverse("emg_electrode_setting_view", args=(emg_electrode_setting.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

    def test_emg_setting_amplifier(self):
        emg_setting = ObjectsFactory.create_emg_setting(
            self.experiment, self.software_version
        )
        manufacturer = ObjectsFactory.create_manufacturer()
        amplifier = ObjectsFactory.create_amplifier(manufacturer)
        tag_emg = Tag.objects.get(name="EMG")
        amplifier.tags.add(tag_emg)

        electrode_model = ObjectsFactory.create_electrode_model()
        tag_emg = Tag.objects.get(name="EMG")
        electrode_model.tags.add(tag_emg)

        emg_electrode_setting = ObjectsFactory.create_emg_electrode_setting(
            emg_setting, electrode_model
        )

        # create an emg amplifier setting
        self.data = {"action": "save", "amplifier": amplifier.id, "gain": "10"}
        response = self.client.post(
            reverse(
                "emg_electrode_setting_amplifier", args=(emg_electrode_setting.id,)
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # screen to view the emg amplifier setting
        response = self.client.get(
            reverse("emg_electrode_setting_amplifier", args=(emg_electrode_setting.id,))
        )
        self.assertEqual(response.status_code, 200)

        # update the emg amplifier setting
        response = self.client.get(
            reverse(
                "emg_electrode_setting_amplifier_edit", args=(emg_electrode_setting.id,)
            )
        )
        self.assertEqual(response.status_code, 200)

        self.data = {"action": "save", "amplifier": amplifier.id, "gain": "20"}
        response = self.client.post(
            reverse(
                "emg_electrode_setting_amplifier_edit", args=(emg_electrode_setting.id,)
            ),
            self.data,
        )
        self.assertEqual(response.status_code, 302)

        # remove an emg  amplifier setting

        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        electrode_placement = ObjectsFactory.create_emg_electrode_placement(
            standardization_system, muscle_subdivision
        )
        muscle_side = ObjectsFactory.create_muscle_side(
            electrode_placement.muscle_subdivision.muscle
        )
        ObjectsFactory.create_emg_electrode_placement_setting(
            emg_electrode_setting, electrode_placement, muscle_side
        )
        self.data = {"action": "remove-amplifier"}
        response = self.client.post(
            reverse("emg_electrode_setting_view", args=(emg_electrode_setting.id,)),
            self.data,
        )
        self.assertEqual(response.status_code, 302)


class PublicationTest(TestCase):
    data: dict[str, Any] = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

    def test_publication_list(self):
        # Check if list of publications is empty before inserting any.
        response = self.client.get(reverse("publication_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["publications"]), 0)

        ObjectsFactory.create_research_project()

        Publication.objects.create(
            title="Publication title", citation="Publication citation"
        )

        # Check if list of publications returns one item after inserting one.
        response = self.client.get(reverse("publication_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["publications"]), 1)

    def test_publication_create(self):
        # Request the publication register screen
        response = self.client.get(reverse("publication_new"))
        self.assertEqual(response.status_code, 200)

        # POSTing "wrong" action
        self.data = {
            "action": "wrong",
            "title": "Publication title",
            "citation": "Publication citation",
        }
        response = self.client.post(reverse("publication_new"), self.data)
        self.assertEqual(Publication.objects.all().count(), 0)
        self.assertEqual(
            str(list(response.context["messages"])[0]), _("Action not available.")
        )
        self.assertEqual(response.status_code, 200)

        # POSTing missing information
        self.data = {"action": "save"}
        response = self.client.post(reverse("publication_new"), self.data)
        self.assertEqual(Publication.objects.all().count(), 0)
        self.assertGreaterEqual(len(response.context["publication_form"].errors), 2)
        self.assertTrue("title" in response.context["publication_form"].errors)
        self.assertTrue("citation" in response.context["publication_form"].errors)
        self.assertEqual(
            str(list(response.context["messages"])[0]), _("Information not saved.")
        )
        self.assertEqual(response.status_code, 200)

        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)

        # Set publication data
        self.data = {
            "action": "save",
            "title": "Publication title",
            "citation": "Publication citation",
            "experiments": str(experiment.id),
        }

        # Count the number of publication currently in database
        count_before_insert = Publication.objects.all().count()

        # Add the new publication
        response = self.client.post(reverse("publication_new"), self.data)
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
        request = self.factory.get(
            reverse(
                "publication_edit",
                args=[
                    publication.pk,
                ],
            )
        )
        request.user = self.user

        response = publication_update(request, publication_id=publication.pk)
        self.assertEqual(response.status_code, 200)

        # Update with changes
        self.data = {
            "action": "save",
            "title": "New publication title",
            "citation": "New citation",
            "experiments": str(experiment.id),
        }
        response = self.client.post(
            reverse("publication_edit", args=(publication.pk,)), self.data, follow=True
        )
        self.assertEqual(
            str(list(response.context["messages"])[0]),
            _("Publication updated successfully."),
        )
        self.assertEqual(response.status_code, 200)

        # Update with no changes
        response = self.client.post(
            reverse("publication_edit", args=(publication.pk,)), self.data, follow=True
        )
        self.assertEqual(
            str(list(response.context["messages"])[0]),
            _("There is no changes to save."),
        )
        self.assertEqual(response.status_code, 200)

    def test_publication_remove(self):
        # Create a publication to be used in the test
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        publication = ObjectsFactory.create_publication([experiment])

        # Save current number of publications
        count = Publication.objects.all().count()

        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("publication_view", args=(publication.pk,)), self.data, follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Check if number of publications decreased by 1
        self.assertEqual(Publication.objects.all().count(), count - 1)

    def test_publication_add_experiment(self):
        # Create a publication to be used in the test
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        publication = ObjectsFactory.create_publication([])

        # Create an instance of a GET request.
        request = self.factory.get(
            reverse(
                "publication_add_experiment",
                args=[
                    publication.pk,
                ],
            )
        )
        request.user = self.user

        response = publication_add_experiment(request, publication_id=publication.pk)
        self.assertEqual(response.status_code, 200)

        # Add an experiment to the publication
        self.data = {
            "action": "add-experiment",
            "experiment_selected": str(experiment.id),
        }
        response = self.client.post(
            reverse("publication_add_experiment", args=(publication.pk,)),
            self.data,
            follow=True,
        )
        self.assertEqual(
            str(list(response.context["messages"])[0]),
            _("Experiment included successfully."),
        )
        self.assertEqual(response.status_code, 200)

        # Try to add the same experiment to the publication
        response = self.client.post(
            reverse("publication_add_experiment", args=(publication.pk,)),
            self.data,
            follow=True,
        )
        self.assertEqual(
            str(list(response.context["messages"])[0]),
            _("Experiment already included in the publication."),
        )
        self.assertEqual(response.status_code, 200)

        # Save current number of experiments related to the publication
        count = publication.experiments.count()

        self.data = {"action": "remove-" + str(experiment.id)}
        response = self.client.post(
            reverse("publication_view", args=(publication.pk,)), self.data, follow=True
        )
        self.assertEqual(response.status_code, 200)

        # Check if number of publications decreased by 1
        self.assertEqual(publication.experiments.count(), count - 1)


class ContextTreeTest(TestCase):
    data: dict[str, Any] = {}

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(self)
        self.assertEqual(logged, True)

    def test_context_tree_list(self):
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)

        # Check if list of context trees is empty before inserting any.
        response = self.client.get(
            reverse(
                "experiment_view",
                args=[
                    experiment.pk,
                ],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["context_tree_list"]), 0)

        ContextTree.objects.create(
            experiment=experiment,
            name="Context name",
            description="Context description",
        )

        # Check if list of context trees returns one item after inserting one.
        response = self.client.get(
            reverse(
                "experiment_view",
                args=[
                    experiment.pk,
                ],
            )
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["context_tree_list"]), 1)

    def test_context_tree_create(self):
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)

        # Request the context tree register screen
        response = self.client.get(
            reverse(
                "context_tree_new",
                args=[
                    experiment.pk,
                ],
            )
        )
        self.assertEqual(response.status_code, 200)

        # POSTing "wrong" action
        self.data = {
            "action": "wrong",
            "name": "Context tree name",
            "description": "Context tree description",
        }
        response = self.client.post(
            reverse(
                "context_tree_new",
                args=[
                    experiment.pk,
                ],
            ),
            self.data,
        )
        self.assertEqual(ContextTree.objects.all().count(), 0)
        self.assertEqual(
            str(list(response.context["messages"])[0]), _("Action not available.")
        )
        self.assertEqual(response.status_code, 200)

        # POSTing missing information
        self.data = {"action": "save"}
        response = self.client.post(
            reverse(
                "context_tree_new",
                args=[
                    experiment.pk,
                ],
            ),
            self.data,
        )
        self.assertEqual(ContextTree.objects.all().count(), 0)
        self.assertGreaterEqual(len(response.context["context_tree_form"].errors), 2)
        self.assertTrue("name" in response.context["context_tree_form"].errors)
        self.assertTrue("description" in response.context["context_tree_form"].errors)
        self.assertEqual(
            str(list(response.context["messages"])[0]), _("Information not saved.")
        )
        self.assertEqual(response.status_code, 200)

        # Set context tree data
        self.data = {
            "action": "save",
            "name": "Context tree name",
            "description": "Context tree description",
        }

        # Count the number of context tree currently in database
        count_before_insert = ContextTree.objects.all().count()

        # Add the new context tree
        response = self.client.post(
            reverse(
                "context_tree_new",
                args=[
                    experiment.pk,
                ],
            ),
            self.data,
        )
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
        request = self.factory.get(
            reverse(
                "context_tree_edit",
                args=[
                    context_tree.pk,
                ],
            )
        )
        request.user = self.user

        response = context_tree_update(request, context_tree_id=context_tree.pk)
        self.assertEqual(response.status_code, 200)

        # Update with changes
        self.data = {
            "action": "save",
            "name": "New context tree name",
            "description": "New context tree description",
        }
        response = self.client.post(
            reverse("context_tree_edit", args=(context_tree.pk,)),
            self.data,
            follow=True,
        )
        self.assertEqual(
            str(list(response.context["messages"])[0]),
            _("Context tree updated successfully."),
        )
        self.assertEqual(response.status_code, 200)

        # Update with no changes
        response = self.client.post(
            reverse("context_tree_edit", args=(context_tree.pk,)),
            self.data,
            follow=True,
        )
        self.assertEqual(
            str(list(response.context["messages"])[0]),
            _("There is no changes to save."),
        )
        self.assertEqual(response.status_code, 200)

    def test_context_tree_remove(self):
        # Create a context tree to be used in the test
        research_project = ObjectsFactory.create_research_project()
        experiment = ObjectsFactory.create_experiment(research_project)
        context_tree = ObjectsFactory.create_context_tree(experiment)

        # Save current number of context trees
        count = ContextTree.objects.all().count()

        self.data = {"action": "remove"}
        response = self.client.post(
            reverse("context_tree_view", args=(context_tree.pk,)),
            self.data,
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        # Check if number of context trees decreased by 1
        self.assertEqual(ContextTree.objects.all().count(), count - 1)


def tearDownModule():
    shutil.rmtree(TEMP_MEDIA_ROOT)
