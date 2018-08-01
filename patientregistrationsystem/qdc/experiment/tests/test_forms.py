# coding=utf-8
import datetime

from django.test import TestCase
# from django import forms

from django.shortcuts import get_object_or_404

from experiment.forms import ResearchProjectForm, ExperimentForm, GroupForm, EEGSettingForm, \
    EEGAmplifierSettingForm, EEGFilterSettingForm, EMGSettingForm, EMGElectrodeSettingForm, \
    ElectrodeModelForm, EMGElectrodePlacementSettingForm, EMGDigitalFilterSettingForm, \
    EMGADConverterSettingForm, TMSSettingForm, TMSDeviceSettingForm, ContextTreeForm,  \
    ComponentForm, BlockForm

from experiment.models import ResearchProject, Experiment, ExperimentResearcher, EEGSetting, EEGAmplifierSetting, \
    Manufacturer, Amplifier, EEGFilterSetting, EEGElectrodeNet, EEGElectrodeLocalizationSystem, EEGElectrodeNetSystem, \
    ElectrodeModel, Tag, EMGSetting, EMGElectrodeSetting, Muscle, StandardizationSystem, MuscleSubdivision, MuscleSide, \
    EMGElectrodePlacement, Software, SoftwareVersion, EMGDigitalFilterSetting, FilterType, ADConverter, \
    EMGADConverterSetting, TMSDevice, TMSDeviceSetting, TMSSetting, CoilShape, CoilModel, Equipment, \
    ContextTree, Block, Component


class ResearchProject_FormTest(TestCase):

   def setUp(self):
       self.research_projects = ResearchProject.objects.all()
       # self.research_projects.save()
       self.data = {
           'start_date': '13/07/2018',
           'end_date': '30/07/2018',
           'title': 'Experimento TOC',
           'description': 'Experimento TOC',
           'owner': 'gady'}

   def test_ResearchProjectForm_is_valid(self):
       start_date  = self.data["start_date"]
       end_date = self.data["end_date"]
       title = self.data["title"]
       description = self.data["description"]
       owner = self.data["owner"]

       research_projects = ResearchProjectForm(data={'start_date': start_date, 'end_date': end_date, 'title': title, 'description': description, 'owner': owner})
       self.assertTrue(research_projects.is_valid())

   def test_ResearchProjectForm_is_not_valid(self):
       research_projects = ResearchProjectForm(data={'start_date': "", 'end_date': "", 'title': "", 'description': "", 'owner': ""})
       self.assertFalse(research_projects.is_valid())

   def test_ResearchProjectForm_is_not_valid_start_date(self):
       research_projects = ResearchProjectForm(data={'start_date': "07/12/2018", 'end_date': self.data["end_date"], 'title': self.data["title"], 'description': self.data["description"], 'owner': self.data["owner"]})
       self.assertFalse(research_projects.is_valid())
       self.assertTrue(research_projects.errors["start_date"]) #True, porque start_date é campo obrigatório

   def test_ResearchProjectForm_is_not_valid_end_date(self):
       research_projects = ResearchProjectForm(data={'start_date': self.data["start_date"], 'end_date': "07/30/2018", 'title': self.data["title"], 'description': self.data["description"], 'owner': self.data["owner"]})
       self.assertFalse(research_projects.is_valid())
       self.assertEqual(research_projects.errors["end_date"], ["Informe uma data válida."])

   def test_ResearchProjectForm_is_not_valid_title(self):
       research_projects = ResearchProjectForm(
           data={
               'start_date': self.data["start_date"],
               'end_date': self.data["end_date"],
               'title': "",
               'description': self.data["description"],
               'owner': self.data["owner"]}
       )
       self.assertFalse(research_projects.is_valid())
       self.assertEqual(research_projects.errors["title"], ["Este campo é obrigatório."])

   def test_ResearchProjectForm_is_not_valid_description(self):
       research_projects = ResearchProjectForm(data={'start_date': self.data["start_date"], 'end_date': self.data["end_date"], 'title': self.data["title"], 'description': "", 'owner': self.data["owner"]})
       self.assertFalse(research_projects.is_valid())
       self.assertEqual(research_projects.errors["description"], ["Este campo é obrigatório."])

   def test_ResearchProjectForm_is_not_valid_owner(self):
       research_projects = ResearchProjectForm(data={'start_date': self.data["start_date"], 'end_date': self.data["end_date"], 'title': self.data["title"], 'description': self.data["description"], 'owner': ""})
       self.assertTrue(research_projects.is_valid()) # True, porque owner não é campo obrigatório

       # self.assertEqual(research_projects.errors["owner_id"], ["Este campo é obrigatório."])
       # self.assertFalse(research_projects.errors["owner_id"])

class Experiment_FormTest(TestCase):

   @classmethod
   def setUp(cls):
       cls.data = {
           'title': 'Experimento TOC',
           'description': 'Experimento TOC',
           'source_code_url': 'http://www.ime.usp.br',
           'ethics_committee_project_url': 'http://www.fm.usp.br',
           'ethics_committee_project_file':'/users/celsovi/documents/unit_tests/links.rtf',
           'is_public': '',
           'data_acquisition_is_concluded':''
       }
       cls.research_project = ResearchProject.objects.create(
           title="Research project title", start_date=datetime.date.today(),
           description="Research project description"
       )

       cls.experiment = Experiment.objects.create(
           research_project_id=cls.research_project.id,
           title="Experimento-Update",
           description="Descricao do Experimento-Update",
           source_code_url="http://www.if.usp.br",
           ethics_committee_project_url="http://www.fm.usp.br",
           ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
           is_public=" ",
           data_acquisition_is_concluded=" ")


   def test_ExperimentForm_is_valid(self):
       experimentForm = ExperimentForm(data={'research_project':self.research_project.id,'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file':self.data["ethics_committee_project_file"], 'is_public':self.data["is_public"], 'data_acquisition_is_concluded':self.data["data_acquisition_is_concluded"]})
       self.assertTrue(experimentForm.is_valid())

   def test_ExperimentForm_is_not_valid_research_project(self):
       experiment = ExperimentForm(data={'research_project':"", 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertFalse(experiment.is_valid())
       self.assertEqual(experiment.errors["research_project"], ["Este campo é obrigatório."])

   def test_ExperimentForm_is_not_valid_title(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': "", 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertFalse(experiment.is_valid())
       self.assertEqual(experiment.errors["title"], ["Este campo é obrigatório."])

   def test_ExperimentForm_is_not_valid_description(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': "", 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertFalse(experiment.is_valid())
       self.assertEqual(experiment.errors["description"], ["Este campo é obrigatório."])

   def test_ExperimentForm_is_not_valid_source_code_url(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': "", 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertTrue(experiment.is_valid())
       s = experiment.data["source_code_url"]
       s.upper()
       self.assertNotEquals(s[ : 7],"HTTP://", "Informe uma url válida.")

   def test_ExperimentForm_is_not_valid_ethics_committee_project_url(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': "", 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertTrue(experiment.is_valid())
       s = experiment.data["ethics_committee_project_url"]
       s.upper()
       self.assertNotEquals(s[ : 7],"HTTP://", "Informe uma url válida.")

   def test_ExperimentForm_is_not_valid_ethics_committee_project_file(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': "", 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertTrue(experiment.is_valid())

   def test_ExperimentForm_is_not_valid_is_public(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': "", 'data_acquisition_is_concluded': self.data["data_acquisition_is_concluded"]})
       self.assertTrue(experiment.is_valid())

   def test_ExperimentForm_is_not_valid_data_acquisition_is_concluded(self):
       experiment = ExperimentForm(data={'research_project':self.research_project.id, 'title': self.data["title"], 'description': self.data["description"], 'source_code_url': self.data["source_code_url"], 'ethics_committee_project_url': self.data["ethics_committee_project_url"], 'ethics_committee_project_file': self.data["ethics_committee_project_file"], 'is_public': self.data["is_public"], 'data_acquisition_is_concluded': ""})
       self.assertTrue(experiment.is_valid())


class GroupAdd_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'title': 'Experimento TOC',
            'description': 'Experimento TOC',

        }
        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")


    def test_GroupForm_is_valid(self):
        title = self.data["title"]
        description = self.data["description"]

        groupAdd_form = GroupForm(data={'title': title, 'description': description})
        self.assertTrue(groupAdd_form.is_valid())

    def test_GroupForm_is_not_valid_title(self):
       groupAdd_form = GroupForm(data={'title': "", 'description': self.data["description"]})
       self.assertFalse(groupAdd_form.is_valid())
       self.assertEqual(groupAdd_form.errors["title"], ["Este campo é obrigatório."])

    def test_GroupForm_is_not_valid_description(self):
       groupAdd_form = GroupForm(data={'title': self.data["title"], 'description': ""})
       self.assertFalse(groupAdd_form.is_valid())
       self.assertEqual(groupAdd_form.errors["description"], ["Este campo é obrigatório."])

# class InclusaoCriteria_FormTest(TestCase):
#
#     @classmethod
#     def setUp(cls):
#         cls.data = {
#             'title': 'Experimento TOC',
#             'description': 'Experimento TOC',
#
#         }
#         cls.research_project = ResearchProject.objects.create(
#             title="Research project title", start_date=datetime.date.today(),
#             description="Research project description"
#         )
#
#         cls.experiment = Experiment.objects.create(
#             research_project_id=cls.research_project.id,
#             title="Experimento-Update",
#             description="Descricao do Experimento-Update",
#             source_code_url="http://www.if.usp.br",
#             ethics_committee_project_url="http://www.fm.usp.br",
#             ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
#             is_public=" ",
#             data_acquisition_is_concluded=" ")
#
#
#     def test_InclusaoCriteria_is_valid(self):
#         s = user_form.id["search-results-diseases"]
#         s.upper()
#         self.assertNotEquals(s[: 7], "HTTP://", "Informe uma url válida.")
#
#
# class CollaboratorAdd_FormTest(TestCase):
#
#     @classmethod
#     def setUp(cls):
#         cls.data = {
#             'title': 'Experimento TOC',
#             'description': 'Experimento TOC',
#             'source_code_url': 'http://www.ime.usp.br',
#             'ethics_committee_project_url': 'http://www.fm.usp.br',
#             'ethics_committee_project_file': '/users/celsovi/documents/unit_tests/links.rtf',
#             'is_public': '',
#             'data_acquisition_is_concluded': ''
#         }
#         cls.research_project = ResearchProject.objects.create(
#             title="Research project title", start_date=datetime.date.today(),
#             description="Research project description"
#         )
#
#         cls.experiment = Experiment.objects.create(
#             research_project_id=cls.research_project.id,
#             title="Experimento-Update",
#             description="Descricao do Experimento-Update",
#             source_code_url="http://www.if.usp.br",
#             ethics_committee_project_url="http://www.fm.usp.br",
#             ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
#             is_public=" ",
#             data_acquisition_is_concluded=" ")
#
#         cls.collaborators_added = ExperimentResearcher.objects.filter(experiment_id=cls.experiment.id)
#
#
#     def test_CollaboratorForm_is_valid(self):
#         pass
#
#
# class Subject_FormTest(TestCase):
#
#     @classmethod
#     def setUp(cls):
#         cls.data = {
#             'title': 'Experimento TOC',
#             'description': 'Experimento TOC',
#
#         }
#         cls.research_project = ResearchProject.objects.create(
#             title="Research project title", start_date=datetime.date.today(),
#             description="Research project description"
#         )
#
#         cls.experiment = Experiment.objects.create(
#             research_project_id=cls.research_project.id,
#             title="Experimento-Update",
#             description="Descricao do Experimento-Update",
#             source_code_url="http://www.if.usp.br",
#             ethics_committee_project_url="http://www.fm.usp.br",
#             ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
#             is_public=" ",
#             data_acquisition_is_concluded=" ")
#
#
#     def test_SubjectFormPorPart_is_valid(self):
#         pass
#
class EEGsettings_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'name': 'Experimento TOC',
            'description': 'Experimento TOC',

        }
        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")


    def test_EEGsettings_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]

        settingsEEG_form = EEGSettingForm(data={'name': name, 'description': description})
        self.assertTrue(settingsEEG_form.is_valid())

    def test_EEGsettings_is_not_valid_name(self):
        settingsEEG_form = EEGSettingForm(data={'name': "", 'description': self.data["description"]})
        self.assertFalse(settingsEEG_form.is_valid())
        self.assertEqual(settingsEEG_form.errors["name"], ["Este campo é obrigatório."])

    def test_EEGsettings_is_not_valid_description(self):
        settingsEEG_form = EEGSettingForm(data={'name': self.data["name"], 'description': ""})
        self.assertFalse(settingsEEG_form.is_valid())
        self.assertEqual(settingsEEG_form.errors["description"], ["Este campo é obrigatório."])


class EEGAmplifierSettings_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'name': 'Experimento TOC',
            'description': 'Experimento TOC',
            'gain': '10',
            'sampling_rate': '10',
            'number_of_channels_used': '2',
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")


        cls.eeg_setting = EEGSetting.objects.create(experiment=cls.experiment,
                                                name='EEG-Setting name',
                                                description='EEG-Setting description')
        cls.manufacturer = Manufacturer.objects.create(name='Manufacturer name')

        cls.amplifier = Amplifier.objects.create(manufacturer=cls.manufacturer,
                                                equipment_type="amplifier",
                                                identification="Amplifier identification")


    def test_EEGAmplifierSettings_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]
        gain = self.data["gain"]
        sampling_rate = self.data["sampling_rate"]
        number_of_channels_used = self.data["number_of_channels_used"]


        settingsEEGAmplifier_form = EEGAmplifierSettingForm(data={'name': name, 'description': description,
                                                            'gain': gain, 'sampling_rate': sampling_rate,
                                                            'number_of_channels_used': number_of_channels_used})
        self.assertTrue(settingsEEGAmplifier_form.is_valid())

    def test_EEGAmplifierSettings_is_not_valid_gain(self):
        settingsEEGAmplifier_form = EEGAmplifierSettingForm(data={'name': self.data["name"], 'description': self.data["description"],
                                                            'gain': "", 'sampling_rate': self.data["sampling_rate"],
                                                            'number_of_channels_used': self.data["number_of_channels_used"]})
        self.assertTrue(settingsEEGAmplifier_form.is_valid())

    def test_EEGAmplifierSettings_is_not_valid_sampling_rate(self):
        settingsEEGAmplifier_form = EEGAmplifierSettingForm(data={'name': self.data["name"], 'description': self.data["description"],
                                                            'gain': self.data["gain"], 'sampling_rate': "",
                                                            'number_of_channels_used': self.data["number_of_channels_used"]})
        self.assertTrue(settingsEEGAmplifier_form.is_valid())

    def test_EEGAmplifierSettings_is_not_valid_number_of_channels_used(self):
        settingsEEGAmplifier_form = EEGAmplifierSettingForm(data={'name': self.data["name"], 'description': self.data["description"],
                                                            'gain': self.data["gain"], 'sampling_rate': self.data["sampling_rate"],
                                                            'number_of_channels_used': ""})
        self.assertFalse(settingsEEGAmplifier_form.is_valid())
        self.assertEqual(settingsEEGAmplifier_form.errors["number_of_channels_used"], ["Este campo é obrigatório."])


class EEGFilterSettings_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'name': 'Experimento TOC',
            'description': 'Experimento TOC',
            'high_pass': '100',
            'low_pass': '10',
            'low_band_pass': '20',
            'high_band_pass': '80',
            'low_notch': '25',
            'high_notch': '55',
            'order': '3',
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")


        cls.electrode_model = ElectrodeModel.objects.create(
            name="Electrode Model name"
        )
        cls.tag = Tag.objects.create(name="EEG")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.manufacturer = Manufacturer.objects.create(name='Manufacturer name')

        cls.software = Software.objects.create(
            manufacturer=cls.manufacturer,
            name="Software name"
        )

        cls.software_version = SoftwareVersion.objects.create(
            software=cls.software,
            name="Software Version name"
        )

        cls.filter_type = FilterType.objects.create(
            name="Filter type name"
        )

        cls.eeg_setting = EEGSetting.objects.create(experiment=cls.experiment,
                                                name='EEG-Setting name',
                                                description='EEG-Setting description')

        cls.eeg_filter_setting = EEGFilterSetting.objects.create(eeg_setting=cls.eeg_setting,
                                                            eeg_filter_type=cls.filter_type,
                                                            high_pass = cls.data["high_pass"],
                                                            low_pass = cls.data["low_pass"],
                                                            low_band_pass = cls.data["low_band_pass"],
                                                            high_band_pass = cls.data["high_band_pass"],
                                                            low_notch = cls.data["low_notch"],
                                                            high_notch = cls.data["high_notch"],
                                                            order = cls.data["order"]
        )


    def test_EEGFilterSettings_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]
        # filter_type = self.filter_type.id
        high_pass = self.eeg_filter_setting.high_pass
        low_pass = self.eeg_filter_setting.low_pass
        low_band_pass = self.eeg_filter_setting.low_band_pass
        high_band_pass = self.eeg_filter_setting.high_band_pass
        low_notch = self.eeg_filter_setting.low_notch
        high_notch = self.eeg_filter_setting.high_notch
        order = self.eeg_filter_setting.order

        settingsEEGFilter_form = EEGFilterSettingForm(data={'name': name, 'description': description,
                                                            'high_pass': high_pass,
                                                            'low_pass': low_pass,
                                                            'low_band_pass': low_band_pass,
                                                            'high_band_pass': high_band_pass,
                                                            'low_notch': low_notch,
                                                            'high_notch': high_notch,
                                                            'order': order}
        )
        self.assertTrue(settingsEEGFilter_form.is_valid())


class EMGsettings_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'name': 'Experimento TOC',
            'description': 'Teste Experimento TOC',
        }
        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")

        cls.electrode_model = ElectrodeModel.objects.create(
            name="Electrode Model name"
        )
        cls.tag = Tag.objects.create(name="EMG")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.manufacturer = Manufacturer.objects.create(name='Manufacturer name')

        cls.software = Software.objects.create(
            manufacturer=cls.manufacturer,
            name="Software name"
        )

        cls.software_version = SoftwareVersion.objects.create(
            software=cls.software,
            name="Software Version name"
        )

        cls.emg_setting = EMGSetting.objects.create(experiment=cls.experiment,
                                                name='EMG-Setting name',
                                                description='EMG-Setting description',
                                                acquisition_software_version=cls.software_version)

    def test_EMGSettings_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]
        acquisition_software_version = self.software_version.id

        settingsEMG_form = EMGSettingForm(data={'name': name, 'description': description, 'acquisition_software_version': acquisition_software_version})
        self.assertTrue(settingsEMG_form.is_valid())

    def test_EMGSettings_is_not_valid_name(self):
        name = self.data["name"]
        description = self.data["description"]
        acquisition_software_version = self.software_version.id

        settingsEMG_form = EMGSettingForm(data={'name': "", 'description': description, 'acquisition_software_version': acquisition_software_version})
        self.assertFalse(settingsEMG_form.is_valid())
        self.assertEqual(settingsEMG_form.errors["name"], ["Este campo é obrigatório."])

    def test_EMGSettings_is_not_valid_description(self):
        name = self.data["name"]
        description = self.data["description"]
        acquisition_software_version = self.software_version.id

        settingsEMG_form = EMGSettingForm(data={'name': name, 'description': "", 'acquisition_software_version': acquisition_software_version})
        self.assertFalse(settingsEMG_form.is_valid())
        self.assertEqual(settingsEMG_form.errors["description"], ["Este campo é obrigatório."])

    def test_EMGSettings_is_not_valid_acquisition_software_version(self):
        name = self.data["name"]
        description = self.data["description"]
        acquisition_software_version = self.software_version.id

        settingsEMG_form = EMGSettingForm(data={'name': name, 'description': description, 'acquisition_software_version': ""})
        self.assertTrue(settingsEMG_form.is_valid()) #pelo forms.py, esse campo não é obrigatorio.


class EMGsettingsElectrodeAdd_FormTest(TestCase):

    @classmethod
    def setUp(cls):

        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")

        cls.manufacturer = Manufacturer.objects.create(name='Brain Vision')

        cls.electrode_model = ElectrodeModel.objects.create(
            name="Electrode Model name"
        )
        cls.tag = Tag.objects.create(name="EMG")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.standardization_system = StandardizationSystem.objects.create(
            name='Standardization System identification',
            description='Standardization System description'
        )

        cls.muscle = Muscle.objects.create(name='Muscle identification')

        cls.muscle_subdivision = MuscleSubdivision.objects.create(
            name='Muscle subdivision identification',
            anatomy_origin='Anatomy origin description',
            anatomy_insertion='Anatomy insertion description',
            anatomy_function='Anatomy function description',
            muscle=cls.muscle
        )

        cls.muscle_side = MuscleSide.objects.create(
            name='Muscle side identification',
            muscle=cls.muscle
        )

        cls.emg_electrode_placement = EMGElectrodePlacement.objects.create(
            standardization_system=cls.standardization_system,
            muscle_subdivision=cls.muscle_subdivision
        )

        cls.data = {
            'name': 'Experimento TOC',
            'description': 'Teste Experimento TOC',
            'electrode': cls.electrode_model.id,
            'electrode_type': 'Surface',
            'emg_electrode_placement': cls.emg_electrode_placement.id,
            'remarks': 'Remarks',
            'muscle_side': cls.muscle_side.id
        }

    def test_EMGsettingsElectrodeAdd_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]
        electrode = self.data["electrode"]

        settingEMG_electrode_add_form = EMGElectrodeSettingForm(data={'name': name, 'description': description, 'electrode': electrode})
        self.assertTrue(settingEMG_electrode_add_form.is_valid())

    def test_EMGsettingsElectrodeAdd_is_valid_eletrode(self):
        name = self.data["name"]
        description = self.data["description"]
        electrode = self.data["electrode"]

        settingEMG_electrode_add_form = EMGElectrodeSettingForm(data={'name': name, 'description': description, 'electrode': ""})
        self.assertFalse(settingEMG_electrode_add_form.is_valid())
        self.assertEqual(settingEMG_electrode_add_form.errors["electrode"], ["Este campo é obrigatório."])


class EMGDigitalFilterSettings_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'name': 'Experimento TOC',
            'description': 'Experimento TOC',
            'high_pass': '100',
            'low_pass': '10',
            'low_band_pass': '20',
            'high_band_pass': '80',
            'low_notch': '25',
            'high_notch': '55',
            'order': '3',
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")

        cls.electrode_model = ElectrodeModel.objects.create(
            name="Electrode Model name"
        )
        cls.tag = Tag.objects.create(name="EMG")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.manufacturer = Manufacturer.objects.create(name='Manufacturer name')

        cls.software = Software.objects.create(
            manufacturer=cls.manufacturer,
            name="Software name"
        )

        cls.software_version = SoftwareVersion.objects.create(
            software=cls.software,
            name="Software Version name"
        )

        cls.emg_setting = EMGSetting.objects.create(experiment=cls.experiment,
                                                name='EMG-Setting name',
                                                description='EMG-Setting description',
                                                acquisition_software_version=cls.software_version)


        cls.filter_type = FilterType.objects.create(
            name="Filter type name"
        )

        cls.emg_digital_filter_setting = EMGDigitalFilterSetting.objects.create(emg_setting=cls.emg_setting,
                                                                             filter_type=cls.filter_type,
                                                                             high_pass = cls.data["high_pass"],
                                                                             low_pass = cls.data["low_pass"],
                                                                             low_band_pass = cls.data["low_band_pass"],
                                                                             high_band_pass = cls.data["high_band_pass"],
                                                                             low_notch = cls.data["low_notch"],
                                                                             high_notch = cls.data["high_notch"],
                                                                             order = cls.data["order"]
        )

    def test_EMGDigitalFilterSettings_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]
        filter_type = self.filter_type.id
        high_pass = self.emg_digital_filter_setting.high_pass
        low_pass = self.emg_digital_filter_setting.low_pass
        low_band_pass = self.emg_digital_filter_setting.low_band_pass
        high_band_pass = self.emg_digital_filter_setting.high_band_pass
        low_notch = self.emg_digital_filter_setting.low_notch
        high_notch = self.emg_digital_filter_setting.high_notch
        order = self.emg_digital_filter_setting.order

        settingsEMGDigitalFilter_form = EMGDigitalFilterSettingForm(data={'name': name, 'description': description,
                                                            'filter_type': filter_type,
                                                            'high_pass': high_pass,
                                                            'low_pass': low_pass,
                                                            'low_band_pass': low_band_pass,
                                                            'high_band_pass': high_band_pass,
                                                            'low_notch': low_notch,
                                                            'high_notch': high_notch,
                                                            'order': order})
        self.assertTrue(settingsEMGDigitalFilter_form.is_valid())

    def test_EMGDigitalFilterSettings_is_valid_filter_type(self):
        name = self.data["name"]
        description = self.data["description"]
        filter_type = self.filter_type.id
        high_pass = self.emg_digital_filter_setting.high_pass
        low_pass = self.emg_digital_filter_setting.low_pass
        low_band_pass = self.emg_digital_filter_setting.low_band_pass
        high_band_pass = self.emg_digital_filter_setting.high_band_pass
        low_notch = self.emg_digital_filter_setting.low_notch
        high_notch = self.emg_digital_filter_setting.high_notch
        order = self.emg_digital_filter_setting.order

        settingsEMGDigitalFilter_form = EMGDigitalFilterSettingForm(data={'name': name, 'description': description,
                                                            'filter_type': "",
                                                            'high_pass': high_pass,
                                                            'low_pass': low_pass,
                                                            'low_band_pass': low_band_pass,
                                                            'high_band_pass': high_band_pass,
                                                            'low_notch': low_notch,
                                                            'high_notch': high_notch,
                                                            'order': order})
        self.assertFalse(settingsEMGDigitalFilter_form.is_valid())
        self.assertEqual(settingsEMGDigitalFilter_form.errors["filter_type"], ["Este campo é obrigatório."])

class EMG_ADConverterSettings_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'name': 'Experimento TOC',
            'description': 'Experimento TOC',
            'sampling_rate': '10',
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")

        cls.electrode_model = ElectrodeModel.objects.create(
            name="Electrode Model name"
        )
        cls.tag = Tag.objects.create(name="EMG")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.manufacturer = Manufacturer.objects.create(name='Manufacturer name')

        cls.software = Software.objects.create(
            manufacturer=cls.manufacturer,
            name="Software name"
        )

        cls.software_version = SoftwareVersion.objects.create(
            software=cls.software,
            name="Software Version name"
        )

        cls.emg_setting = EMGSetting.objects.create(experiment=cls.experiment,
                                                name='EMG-Setting name',
                                                description='EMG-Setting description',
                                                acquisition_software_version=cls.software_version)

        cls.filter_type = FilterType.objects.create(
            name="Filter type name"
        )

        cls.ad_converter = ADConverter.objects.create(manufacturer=cls.manufacturer,
                                                  equipment_type="ad_converter",
                                                  identification="AD Converter identification",
                                                  signal_to_noise_rate=20,
                                                  sampling_rate=cls.data["sampling_rate"],
                                                  resolution=7
        )

        cls.emg_ad_converter_setting = EMGADConverterSetting.objects.create(emg_setting=cls.emg_setting,
                                                                            ad_converter=cls.ad_converter,
                                                                            sampling_rate=cls.data["sampling_rate"]
        )


    def test_EMG_ADConverterSettings_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]
        filter_type = self.filter_type.id
        ad_converter = self.emg_ad_converter_setting.ad_converter
        sampling_rate = self.emg_ad_converter_setting.sampling_rate


        settingsEMG_ADConverter_form = EMGADConverterSettingForm(data={'name': name, 'description': description,
                                                            'ad_converter': ad_converter,
                                                            'sampling_rate': sampling_rate}
        )
        self.assertTrue(settingsEMG_ADConverter_form.is_valid())

    def test_EMG_ADConverterSettings_is_valid_ad_converter(self):
        name = self.data["name"]
        description = self.data["description"]
        filter_type = self.filter_type.id
        ad_converter = self.emg_ad_converter_setting.ad_converter
        sampling_rate = self.emg_ad_converter_setting.sampling_rate

        settingsEMG_ADConverter_form = EMGADConverterSettingForm(data={'name': name, 'description': description,
                                                            'ad_converter': "",
                                                            'sampling_rate': sampling_rate}
        )

        self.assertFalse(settingsEMG_ADConverter_form.is_valid())
        self.assertEqual(settingsEMG_ADConverter_form.errors["ad_converter"], ["Este campo é obrigatório."])


class TMSSetting_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'name': 'Experimento TOC',
            'description': 'Experimento TOC',

        }
        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")


    def test_TMSSetting_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]

        settingTMS_form = TMSSettingForm(data={'name': name, 'description': description})
        self.assertTrue(settingTMS_form.is_valid())

    def test_TMSSetting_is_not_valid_name(self):
        settingTMS_form = TMSSettingForm(data={'name': "", 'description': self.data["description"]})
        self.assertFalse(settingTMS_form.is_valid())
        self.assertEqual(settingTMS_form.errors["name"], ["Este campo é obrigatório."])

    def test_TMSSetting_is_not_valid_description(self):
        settingTMS_form = TMSSettingForm(data={'name': self.data["name"], 'description': ""})
        self.assertFalse(settingTMS_form.is_valid())
        self.assertEqual(settingTMS_form.errors["description"], ["Este campo é obrigatório."])


class TMSDevice_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'name': 'Experimento TOC',
            'description': 'Experimento TOC',
            'pulse_stimulus_type': 'paired_pulse',
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")



        cls.manufacturer = Manufacturer.objects.create(name='Manufacturer name')

        cls.electrode_model = ElectrodeModel.objects.create(
            name="Electrode Model name"
        )

        cls.tag = Tag.objects.create(name="TMS")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.coil_shape = CoilShape.objects.create(name="Electrode Shape name")
        cls.coil_model = CoilModel.objects.create(name="Electrode Model name",
                                            coil_shape=cls.coil_shape
        )

        cls.tms_setting = TMSSetting.objects.create(experiment=cls.experiment)

        cls.tms_device = TMSDevice.objects.create(pulse_type="monophase", manufacturer=cls.manufacturer,
                                                  equipment_type="tms_device", identification='identification')

        cls.tms_device_setting = TMSDeviceSetting.objects.create(tms_setting=cls.tms_setting,
                                                    tms_device=cls.tms_device,
                                                    pulse_stimulus_type=cls.data["pulse_stimulus_type"],
                                                    coil_model=cls.coil_model
        )

    def test_TMSDevice_is_valid(self):
        tms_device = self.tms_device
        pulse_stimulus_type = self.data["pulse_stimulus_type"]
        coil_model = self.coil_model.id

        deviceTMS_form = TMSDeviceSettingForm(data={'tms_device': tms_device,
                                                    'coil_model': coil_model,
                                                    'pulse_stimulus_type': pulse_stimulus_type
                                                    })
        self.assertTrue(deviceTMS_form.is_valid())


    def test_TMSDevice_is_not_valid_tms_device(self):
        tms_device = self.tms_device
        pulse_stimulus_type = self.data["pulse_stimulus_type"]
        coil_model = self.coil_model.id

        deviceTMS_form = TMSDeviceSettingForm(data={'tms_device': "",
                                                    'pulse_stimulus_type': pulse_stimulus_type,
                                                    'coil_model': coil_model
                                                    })
        self.assertFalse(deviceTMS_form.is_valid())
        self.assertEqual(deviceTMS_form.errors["tms_device"], ["Este campo é obrigatório."])


    def test_TMSDevice_is_not_valid_coil_model(self):
        tms_device = self.tms_device
        pulse_stimulus_type = self.data["pulse_stimulus_type"]
        coil_model = self.coil_model.id

        deviceTMS_form = TMSDeviceSettingForm(data={'tms_device': tms_device,
                                                    'pulse_stimulus_type': pulse_stimulus_type,
                                                    'coil_model': ""
                                                    })
        self.assertFalse(deviceTMS_form.is_valid())
        self.assertEqual(deviceTMS_form.errors["coil_model"], ["Este campo é obrigatório."])


class ContextTrees_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'name': 'Experimento TOC',
            'description': 'Experimento TOC',
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")


        cls.context_tree=ContextTree.objects.create(experiment=cls.experiment, name='Context name', description='Context description')

    def test_ContextTrees_is_valid(self):
        name = self.context_tree.name
        description = self.context_tree.description

        contextTrees_form = ContextTreeForm(data={'name': name, 'description': description})
        self.assertTrue(contextTrees_form.is_valid())

    def test_ContextTrees_is_not_valid_name(self):
        name = self.context_tree.name
        description = self.context_tree.description

        contextTrees_form = ContextTreeForm(data={'name': "", 'description': description})
        self.assertFalse(contextTrees_form.is_valid())
        self.assertEqual(contextTrees_form.errors["name"], ["Este campo é obrigatório."])

    def test_ContextTrees_is_not_valid_description(self):
        name = self.context_tree.name
        description = self.context_tree.description

        contextTrees_form = ContextTreeForm(data={'name': name, 'description': ""})
        self.assertFalse(contextTrees_form.is_valid())
        self.assertEqual(contextTrees_form.errors["description"], ["Este campo é obrigatório."])


class SEP_Block_FormTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.data = {
            'name': 'Experimento TOC',
            'description': 'Experimento TOC',
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title", start_date=datetime.date.today(),
            description="Research project description"
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=" ",
            data_acquisition_is_concluded=" ")


        cls.component=Component.objects.create(experiment=cls.experiment, identification="Identification",  duration_unit=" ", description=" ", component_type="Set of steps")

        cls.block = Block.objects.create(experiment=cls.experiment,
                                         identification="Identification",
                                         component_type="Set of steps",
                                         type="sequence",
                                         number_of_mandatory_components=0
        )

    def test_SEP_Block_is_valid(self):
        experiment = self.experiment
        number_of_mandatory_components = self.block.number_of_mandatory_components
        type = self.block.type


        sep_SEP_Block_form = BlockForm(data={'number_of_mandatory_components': number_of_mandatory_components,
                                             'type': type,
                                             'experiment': experiment
        })
        self.assertTrue(sep_SEP_Block_form.is_valid())

    def test_SEP_Block_is_not_valid_number_of_mandatory_components(self):
        experiment = self.experiment
        number_of_mandatory_components = " "
        type = self.block.type

        sep_SEP_Block_form = BlockForm(data={'number_of_mandatory_components': number_of_mandatory_components,
                                             'type': type,
                                             'experiment': experiment
        })
        self.assertFalse(sep_SEP_Block_form.is_valid())
        self.assertEqual(sep_SEP_Block_form.errors["number_of_mandatory_components"], ["Informe um número inteiro."])

    def test_SEP_Block_is_not_valid_type(self):
        experiment = self.experiment
        number_of_mandatory_components = 0
        type = " "

        sep_SEP_Block_form = BlockForm(data={'number_of_mandatory_components': number_of_mandatory_components,
                                             'type': type,
                                             'experiment': experiment
        })
        self.assertFalse(sep_SEP_Block_form.is_valid())
        self.assertEqual(sep_SEP_Block_form.errors["type"], ["Faça uma escolha válida.   não é uma das escolhas disponíveis."])


# class SEP_Block_Block_Fix_FormTest(TestCase):
#
#     @classmethod
#     def setUp(cls):
#         cls.data = {
#             'name': 'Experimento TOC',
#             'description': 'Experimento TOC',
#         }
#
#         cls.research_project = ResearchProject.objects.create(
#             title="Research project title", start_date=datetime.date.today(),
#             description="Research project description"
#         )
#
#         cls.experiment = Experiment.objects.create(
#             research_project_id=cls.research_project.id,
#             title="Experimento-Update",
#             description="Descricao do Experimento-Update",
#             source_code_url="http://www.if.usp.br",
#             ethics_committee_project_url="http://www.fm.usp.br",
#             ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
#             is_public=" ",
#             data_acquisition_is_concluded=" ")


