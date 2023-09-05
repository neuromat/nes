# coding=utf-8

from django.contrib.auth.models import User
from django.test import TestCase
from experiment.forms import *
from experiment.forms import NumberOfUsesToInsertForm
from experiment.models import *
from survey.abc_search_engine import Questionnaires

# from .models import Questionnaire, ABCSearchEngine, Survey, ABC


USER_USERNAME = "myadmin"
USER_PWD = "mypassword"


class MaterialRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

    def test_MaterialRegisterForm_is_valid(self):
        material = MaterialRegisterForm(data={"name": "MaterialTest"})
        self.assertTrue(material.is_valid())

    def test_MaterialRegisterForm_is_not_valid(self):
        material = MaterialRegisterForm(data={"name": ""})
        self.assertFalse(material.is_valid())


class MuscleRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

    def test_MuscleRegisterForm_is_valid(self):
        muscle = MuscleRegisterForm(data={"name": "MuscleTest"})
        self.assertTrue(muscle.is_valid())

    def test_MuscleRegisterForm_is_not_valid(self):
        muscle = MuscleRegisterForm(data={"name": ""})
        self.assertFalse(muscle.is_valid())


class MuscleSubdivisionRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

    def test_MuscleSubdivisionRegisterForm_is_valid(self):
        subdivision = MuscleSubdivisionRegisterForm(
            data={"name": "MuscleSubdivisionTest"}
        )
        self.assertTrue(subdivision.is_valid())

    def test_MuscleSubdivisionRegisterForm_is_not_valid(self):
        subdivision = MuscleSubdivisionRegisterForm(data={"name": ""})
        self.assertFalse(subdivision.is_valid())


class MuscleSideRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

    def test_MuscleSideRegisterForm_is_valid(self):
        side = MuscleSideRegisterForm(data={"name": "MuscleSideTest"})
        self.assertTrue(side.is_valid())

    def test_MuscleSideRegisterForm_is_not_valid(self):
        side = MuscleSideRegisterForm(data={"name": ""})
        self.assertFalse(side.is_valid())


class EEGElectrodeLocalizationSystemRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

    def test_EEGElectrodeLocalizationSystemRegisterForm_is_valid(self):
        eegelectrodelocsys = EEGElectrodeLocalizationSystemRegisterForm(
            data={"name": "EEGElectrodeLocSysRegTest"}
        )
        self.assertTrue(eegelectrodelocsys.is_valid())

    def test_EEGElectrodeLocalizationSystemRegisterForm_is_not_valid(self):
        eegelectrodelocsys = EEGElectrodeLocalizationSystemRegisterForm(
            data={"name": ""}
        )
        self.assertFalse(eegelectrodelocsys.is_valid())


class EEGElectrodePositionFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

    def test_EEGElectrodePositionForm_is_valid(self):
        eegelectrodepos = EEGElectrodePositionForm(data={"name": "EEGElectrodePosTest"})
        self.assertTrue(eegelectrodepos.is_valid())

    def test_EEGElectrodePosition_is_not_valid(self):
        eegelectrodepos = EEGElectrodePositionForm(data={"name": ""})
        self.assertFalse(eegelectrodepos.is_valid())


class EMGSurfacePlacementRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

    def test_EMGSurfacePlacementRegisterForm_is_valid(self):
        muscle = Muscle.objects.create(name="Muscle")

        muscle_subdivision = MuscleSubdivision.objects.create(
            name="Muscle Subdivision", muscle=muscle
        )

        emgsurface = EMGSurfacePlacementRegisterForm(
            data={"muscle_subdivision": muscle_subdivision.id}
        )
        self.assertTrue(emgsurface.is_valid())

    def test_EMGSurfacePlacementRegisterForm_is_not_valid(self):
        emgsurface = EMGSurfacePlacementRegisterForm(data={"muscle_subdivision": ""})
        self.assertFalse(emgsurface.is_valid())


class EMGIntramuscularPlacementRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

    def test_EMGIntramuscularPlacementRegisterForm_is_valid(self):
        muscle = Muscle.objects.create(name="Muscle")

        muscle_subdivision: MuscleSubdivision = MuscleSubdivision.objects.create(
            name="Muscle Subdivision", muscle=muscle
        )

        emgintramuscular = EMGSurfacePlacementRegisterForm(
            data={"muscle_subdivision": muscle_subdivision.id}
        )
        self.assertTrue(emgintramuscular.is_valid())

    def test_EMGIntramuscularPlacementRegisterForm_is_not_valid(self):
        emgintramuscular = EMGSurfacePlacementRegisterForm(
            data={"muscle_subdivision": ""}
        )
        self.assertFalse(emgintramuscular.is_valid())


class EMGNeedlePlacementRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

    def test_EMGNeedlePlacementRegisterForm_is_valid(self):
        muscle = Muscle.objects.create(name="Muscle")

        muscle_subdivision = MuscleSubdivision.objects.create(
            name="Muscle Subdivision", muscle=muscle
        )

        emgneedle = EMGSurfacePlacementRegisterForm(
            data={"muscle_subdivision": muscle_subdivision.id}
        )
        self.assertTrue(emgneedle.is_valid())

    def test_EMGNeedlePlacementRegisterForm_is_not_valid(self):
        emgneedle = EMGSurfacePlacementRegisterForm(data={"muscle_subdivision": ""})
        self.assertFalse(emgneedle.is_valid())


class TMSLocalizationSystemFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

        brainareasystem = BrainAreaSystem.objects.create(name="Lobo frontal")

        brainarea = BrainArea.objects.create(
            name="Lobo frontal", brain_area_system=brainareasystem
        )

        self.data = {"name": "TMSLocalizationSystem", "brain_area": brainarea.id}

    def test_TMSLocalizationSystemForm_is_valid(self):
        tmslocalizationsystem = TMSLocalizationSystemForm(data=self.data)
        self.assertTrue(tmslocalizationsystem.is_valid())

    def test_TMSLocalizationSystemForm_is_not_valid_without_name(self):
        self.data["name"] = ""
        tmslocalizationsystem = TMSLocalizationSystemForm(data=self.data)
        self.assertFalse(tmslocalizationsystem.is_valid())

    def test_TMSLocalizationSystemForm_is_not_valid_without_brain_area(self):
        self.data["brain_area"] = ""
        tmslocalizationsystem = TMSLocalizationSystemForm(data=self.data)
        self.assertFalse(tmslocalizationsystem.is_valid())


class ManufacturerRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

        self.data = {"name": "Manufacturer"}

    def test_ManufacturerRegisterForm_is_valid(self):
        manufacturer = ManufacturerRegisterForm(data=self.data)
        self.assertTrue(manufacturer.is_valid())

    def test_ManufacturerRegisterForm_is_not_valid(self):
        self.data["name"] = ""
        manufacturer = ManufacturerRegisterForm(data=self.data)
        self.assertFalse(manufacturer.is_valid())


class ElectrodeModelRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

        self.data = {"name": "ElectrodeModel", "electrode_type": "intramuscular"}

    def test_ElectrodeModelRegisterForm_is_valid(self):
        manufacturer = ElectrodeModelRegisterForm(data=self.data)
        self.assertTrue(manufacturer.is_valid())

    def test_ElectrodeModelRegisterForm_is_not_valid_without_name(self):
        self.data["name"] = ""
        manufacturer = ElectrodeModelRegisterForm(data=self.data)
        self.assertFalse(manufacturer.is_valid())

    def test_ElectrodeModelRegisterForm_is_not_valid_without_electrode_type(self):
        self.data["electrode_type"] = ""
        manufacturer = ElectrodeModelRegisterForm(data=self.data)
        self.assertFalse(manufacturer.is_valid())


class EEGElectrodeNETRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        manufacturer = Manufacturer.objects.create(name="Manufacturer")

        tag = Tag.objects.create(name="EEG")

        electrodemodel = ElectrodeModel.objects.create(
            name="Electrodemodel", electrode_type="surface"
        )
        electrodemodel.tags.set([tag.id])

        self.data = {
            "manufacturer": manufacturer.id,
            "identification": "Identification",
            "electrode_model_default": electrodemodel.id,
        }

    def test_EEGElectrodeNETRegisterForm_is_valid(self):
        eegelectrodenet = EEGElectrodeNETRegisterForm(self.data)
        self.assertTrue(eegelectrodenet.is_valid())

    def test_EEGElectrodeNETRegisterForm_is_not_valid_without_manufacturer(self):
        self.data["manufacturer"] = ""
        eegelectrodenet = EEGElectrodeNETRegisterForm(self.data)
        self.assertFalse(eegelectrodenet.is_valid())

    def test_EEGElectrodeNETRegisterForm_is_not_valid_without_identification(self):
        self.data["identification"] = ""
        eegelectrodenet = EEGElectrodeNETRegisterForm(self.data)
        self.assertFalse(eegelectrodenet.is_valid())

    def test_EEGElectrodeNETRegisterForm_is_not_valid_without_electrode_model_default(
        self,
    ):
        self.data["electrode_model_default"] = ""
        eegelectrodenet = EEGElectrodeNETRegisterForm(self.data)
        self.assertFalse(eegelectrodenet.is_valid())


class EEGSolutionRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        manufacturer = Manufacturer.objects.create(name="Manufacturer")

        self.data = {"name": "EEGSolution", "manufacturer": manufacturer.id}

    def test_EEGSolutionRegisterForm_is_valid(self):
        solution = EEGSolutionRegisterForm(data=self.data)
        self.assertTrue(solution.is_valid())

    def test_EEGSolutionRegisterForm_is_not_valid_without_name(self):
        self.data["name"] = ""
        solution = EEGSolutionRegisterForm(data=self.data)
        self.assertFalse(solution.is_valid())

    def test_EEGSolutionRegisterForm_is_not_valid_without_manufacturer(self):
        self.data["manufacturer"] = ""
        solution = EEGSolutionRegisterForm(data=self.data)
        self.assertFalse(solution.is_valid())


class AmplifierRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

        manufacturer = Manufacturer.objects.create(name="Manufacturer")

        self.data = {"identification": "Amplifier", "manufacturer": manufacturer.id}

    def test_AmplifierRegisterForm_is_valid(self):
        amplifier = AmplifierRegisterForm(data=self.data)
        self.assertTrue(amplifier.is_valid())

    def test_AmplifierRegisterForm_is_not_valid_without_identification(self):
        self.data["identification"] = ""
        amplifier = AmplifierRegisterForm(data=self.data)
        self.assertFalse(amplifier.is_valid())

    def test_AmplifierRegisterForm_is_not_valid_without_manufacturer(self):
        self.data["manufacturer"] = ""
        amplifier = AmplifierRegisterForm(data=self.data)
        self.assertFalse(amplifier.is_valid())


class FilterTypeRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

        self.data = {"name": "Filter"}

    def test_FilterTypeRegisterForm_is_valid(self):
        filtertype = FilterTypeRegisterForm(data=self.data)
        self.assertTrue(filtertype.is_valid())

    def test_FilterTypeRegisterForm_is_not_valid_without_name(self):
        self.data["name"] = ""
        filtertype = FilterTypeRegisterForm(data=self.data)
        self.assertFalse(filtertype.is_valid())


class SoftwareRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

        manufacturer = Manufacturer.objects.create(name="Manufacturer")

        self.data = {"name": "Software", "manufacturer": manufacturer.id}

    def test_SoftwareRegisterForm_is_valid(self):
        software = SoftwareRegisterForm(data=self.data)
        self.assertTrue(software.is_valid())

    def test_SoftwareRegisterForm_is_not_valid_without_name(self):
        self.data["name"] = ""
        software = SoftwareRegisterForm(data=self.data)
        self.assertFalse(software.is_valid())

    def test_SoftwareRegisterForm_is_not_valid_without_manufacturer(self):
        self.data["manufacturer"] = ""
        software = SoftwareRegisterForm(data=self.data)
        self.assertFalse(software.is_valid())


class SoftwareVersionRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

        self.data = {"name": "Software"}

    def test_SoftwareVersionRegisterForm_is_valid(self):
        version = SoftwareVersionRegisterForm(data=self.data)
        self.assertTrue(version.is_valid())

    def test_SoftwareVersionRegisterForm_is_not_valid_without_name(self):
        self.data["name"] = ""
        version = SoftwareVersionRegisterForm(data=self.data)
        self.assertFalse(version.is_valid())


class ADConverterRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

        manufacturer = Manufacturer.objects.create(name="Manufacturer")

        self.data = {"identification": "ADConverter", "manufacturer": manufacturer.id}

    def test_ADConverterRegisterForm_is_valid(self):
        converter = ADConverterRegisterForm(data=self.data)
        self.assertTrue(converter.is_valid())

    def test_ADConverterRegisterForm_is_not_valid_without_identification(self):
        self.data["identification"] = ""
        converter = ADConverterRegisterForm(data=self.data)
        self.assertFalse(converter.is_valid())

    def test_ADConverterRegisterForm_is_not_valid_without_manufacturer(self):
        self.data["manufacturer"] = ""
        converter = ADConverterRegisterForm(data=self.data)
        self.assertFalse(converter.is_valid())


class CoilModelRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

        coilshape = CoilShape.objects.create(name="Coil Shape")

        self.data = {"name": "CoilModel", "coil_shape": coilshape.id}

    def test_CoilModelRegisterForm_is_valid(self):
        coilmodel = CoilModelRegisterForm(data=self.data)
        self.assertTrue(coilmodel.is_valid())

    def test_CoilModelRegisterForm_is_not_valid_without_name(self):
        self.data["name"] = ""
        coilmodel = CoilModelRegisterForm(data=self.data)
        self.assertFalse(coilmodel.is_valid())

    def test_CoilModelRegisterForm_is_not_valid_without_coil_shape(self):
        self.data["coil_shape"] = ""
        coilmodel = CoilModelRegisterForm(data=self.data)
        self.assertFalse(coilmodel.is_valid())


class TMSDeviceRegisterFormValidation(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        self.user.is_staff = True
        self.user.is_superuser = True

        manufacturer = Manufacturer.objects.create(name="Manufacturer")

        self.data = {"identification": "TMSDevice", "manufacturer": manufacturer.id}

    def test_TMSDeviceRegisterForm_is_valid(self):
        tmsdevice = TMSDeviceRegisterForm(data=self.data)
        self.assertTrue(tmsdevice.is_valid())

    def test_TMSDeviceRegisterForm_is_not_valid_without_identification(self):
        self.data["identification"] = ""
        tmsdevice = TMSDeviceRegisterForm(data=self.data)
        self.assertFalse(tmsdevice.is_valid())

    def test_TMSDeviceRegisterForm_is_not_valid_without_manufacturer(self):
        self.data["manufacturer"] = ""
        tmsdevice = TMSDeviceRegisterForm(data=self.data)
        self.assertFalse(tmsdevice.is_valid())


class ResearchProjectFormTest(TestCase):
    def setUp(self):
        self.research_projects = ResearchProject.objects.all()
        # self.research_projects.save()
        self.data = {
            "start_date": "13/07/2018",
            "end_date": "30/07/2018",
            "title": "Experimento TOC",
            "description": "Experimento TOC",
            "owner": "gady",
        }

    def test_ResearchProjectForm_is_valid(self):
        start_date = self.data["start_date"]
        end_date = self.data["end_date"]
        title = self.data["title"]
        description = self.data["description"]
        owner = self.data["owner"]

        research_projects = ResearchProjectForm(
            data={
                "start_date": start_date,
                "end_date": end_date,
                "title": title,
                "description": description,
                "owner": owner,
            }
        )
        self.assertTrue(research_projects.is_valid())

    def test_ResearchProjectForm_is_not_valid(self):
        research_projects = ResearchProjectForm(
            data={
                "start_date": "",
                "end_date": "",
                "title": "",
                "description": "",
                "owner": "",
            }
        )
        self.assertFalse(research_projects.is_valid())

    def test_ResearchProjectForm_is_not_valid_start_date(self):
        research_projects = ResearchProjectForm(
            data={
                "start_date": "07/12/2018",
                "end_date": self.data["end_date"],
                "title": self.data["title"],
                "description": self.data["description"],
                "owner": self.data["owner"],
            }
        )
        self.assertFalse(research_projects.is_valid())
        self.assertTrue(
            research_projects.errors["start_date"]
        )  # True, porque start_date é campo obrigatório

    def test_ResearchProjectForm_is_not_valid_end_date(self):
        research_projects = ResearchProjectForm(
            data={
                "start_date": self.data["start_date"],
                "end_date": "07/30/2018",
                "title": self.data["title"],
                "description": self.data["description"],
                "owner": self.data["owner"],
            }
        )
        self.assertFalse(research_projects.is_valid())
        self.assertEqual(
            research_projects.errors["end_date"], ["Informe uma data válida."]
        )

    def test_ResearchProjectForm_is_not_valid_title(self):
        research_projects = ResearchProjectForm(
            data={
                "start_date": self.data["start_date"],
                "end_date": self.data["end_date"],
                "title": "",
                "description": self.data["description"],
                "owner": self.data["owner"],
            }
        )
        self.assertFalse(research_projects.is_valid())
        self.assertEqual(
            research_projects.errors["title"], ["Este campo é obrigatório."]
        )

    def test_ResearchProjectForm_is_not_valid_description(self):
        research_projects = ResearchProjectForm(
            data={
                "start_date": self.data["start_date"],
                "end_date": self.data["end_date"],
                "title": self.data["title"],
                "description": "",
                "owner": self.data["owner"],
            }
        )
        self.assertFalse(research_projects.is_valid())
        self.assertEqual(
            research_projects.errors["description"], ["Este campo é obrigatório."]
        )

    def test_ResearchProjectForm_is_not_valid_owner(self):
        research_projects = ResearchProjectForm(
            data={
                "start_date": self.data["start_date"],
                "end_date": self.data["end_date"],
                "title": self.data["title"],
                "description": self.data["description"],
                "owner": "",
            }
        )
        self.assertTrue(
            research_projects.is_valid()
        )  # True, porque owner não é campo obrigatório

        # self.assertEqual(research_projects.errors["owner_id"], ["Este campo é obrigatório."])
        # self.assertFalse(research_projects.errors["owner_id"])


class Experiment_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "title": "Experimento TOC",
            "description": "Experimento TOC",
            "source_code_url": "http://www.ime.usp.br",
            "ethics_committee_project_url": "http://www.fm.usp.br",
            "ethics_committee_project_file": "/users/celsovi/documents/unit_tests/links.rtf",
            "is_public": "",
            "data_acquisition_is_concluded": "",
        }
        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )
        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

    def test_ExperimentForm_is_valid(self):
        experimentForm = ExperimentForm(
            data={
                "research_project": self.research_project.id,
                "title": self.data["title"],
                "description": self.data["description"],
                "source_code_url": self.data["source_code_url"],
                "ethics_committee_project_url": self.data[
                    "ethics_committee_project_url"
                ],
                "ethics_committee_project_file": self.data[
                    "ethics_committee_project_file"
                ],
                "is_public": self.data["is_public"],
                "data_acquisition_is_concluded": self.data[
                    "data_acquisition_is_concluded"
                ],
            }
        )
        self.assertTrue(experimentForm.is_valid())

    def test_ExperimentForm_is_not_valid_research_project(self):
        experiment = ExperimentForm(
            data={
                "research_project": "",
                "title": self.data["title"],
                "description": self.data["description"],
                "source_code_url": self.data["source_code_url"],
                "ethics_committee_project_url": self.data[
                    "ethics_committee_project_url"
                ],
                "ethics_committee_project_file": self.data[
                    "ethics_committee_project_file"
                ],
                "is_public": self.data["is_public"],
                "data_acquisition_is_concluded": self.data[
                    "data_acquisition_is_concluded"
                ],
            }
        )
        self.assertFalse(experiment.is_valid())
        self.assertEqual(
            experiment.errors["research_project"], ["Este campo é obrigatório."]
        )

    def test_ExperimentForm_is_not_valid_title(self):
        experiment = ExperimentForm(
            data={
                "research_project": self.research_project.id,
                "title": "",
                "description": self.data["description"],
                "source_code_url": self.data["source_code_url"],
                "ethics_committee_project_url": self.data[
                    "ethics_committee_project_url"
                ],
                "ethics_committee_project_file": self.data[
                    "ethics_committee_project_file"
                ],
                "is_public": self.data["is_public"],
                "data_acquisition_is_concluded": self.data[
                    "data_acquisition_is_concluded"
                ],
            }
        )
        self.assertFalse(experiment.is_valid())
        self.assertEqual(experiment.errors["title"], ["Este campo é obrigatório."])

    def test_ExperimentForm_is_not_valid_description(self):
        experiment = ExperimentForm(
            data={
                "research_project": self.research_project.id,
                "title": self.data["title"],
                "description": "",
                "source_code_url": self.data["source_code_url"],
                "ethics_committee_project_url": self.data[
                    "ethics_committee_project_url"
                ],
                "ethics_committee_project_file": self.data[
                    "ethics_committee_project_file"
                ],
                "is_public": self.data["is_public"],
                "data_acquisition_is_concluded": self.data[
                    "data_acquisition_is_concluded"
                ],
            }
        )
        self.assertFalse(experiment.is_valid())
        self.assertEqual(
            experiment.errors["description"], ["Este campo é obrigatório."]
        )

    def test_ExperimentForm_is_not_valid_source_code_url(self):
        experiment = ExperimentForm(
            data={
                "research_project": self.research_project.id,
                "title": self.data["title"],
                "description": self.data["description"],
                "source_code_url": "",
                "ethics_committee_project_url": self.data[
                    "ethics_committee_project_url"
                ],
                "ethics_committee_project_file": self.data[
                    "ethics_committee_project_file"
                ],
                "is_public": self.data["is_public"],
                "data_acquisition_is_concluded": self.data[
                    "data_acquisition_is_concluded"
                ],
            }
        )
        self.assertTrue(experiment.is_valid())
        s = experiment.data["source_code_url"]
        s.upper()
        self.assertNotEquals(s[:7], "HTTP://", "Informe uma url válida.")

    def test_ExperimentForm_is_not_valid_ethics_committee_project_url(self):
        experiment = ExperimentForm(
            data={
                "research_project": self.research_project.id,
                "title": self.data["title"],
                "description": self.data["description"],
                "source_code_url": self.data["source_code_url"],
                "ethics_committee_project_url": "",
                "ethics_committee_project_file": self.data[
                    "ethics_committee_project_file"
                ],
                "is_public": self.data["is_public"],
                "data_acquisition_is_concluded": self.data[
                    "data_acquisition_is_concluded"
                ],
            }
        )
        self.assertTrue(experiment.is_valid())
        s = experiment.data["ethics_committee_project_url"]
        s.upper()
        self.assertNotEquals(s[:7], "HTTP://", "Informe uma url válida.")

    def test_ExperimentForm_is_not_valid_ethics_committee_project_file(self):
        experiment = ExperimentForm(
            data={
                "research_project": self.research_project.id,
                "title": self.data["title"],
                "description": self.data["description"],
                "source_code_url": self.data["source_code_url"],
                "ethics_committee_project_url": self.data[
                    "ethics_committee_project_url"
                ],
                "ethics_committee_project_file": "",
                "is_public": self.data["is_public"],
                "data_acquisition_is_concluded": self.data[
                    "data_acquisition_is_concluded"
                ],
            }
        )
        self.assertTrue(experiment.is_valid())

    def test_ExperimentForm_is_not_valid_is_public(self):
        experiment = ExperimentForm(
            data={
                "research_project": self.research_project.id,
                "title": self.data["title"],
                "description": self.data["description"],
                "source_code_url": self.data["source_code_url"],
                "ethics_committee_project_url": self.data[
                    "ethics_committee_project_url"
                ],
                "ethics_committee_project_file": self.data[
                    "ethics_committee_project_file"
                ],
                "is_public": "",
                "data_acquisition_is_concluded": self.data[
                    "data_acquisition_is_concluded"
                ],
            }
        )
        self.assertTrue(experiment.is_valid())

    def test_ExperimentForm_is_not_valid_data_acquisition_is_concluded(self):
        experiment = ExperimentForm(
            data={
                "research_project": self.research_project.id,
                "title": self.data["title"],
                "description": self.data["description"],
                "source_code_url": self.data["source_code_url"],
                "ethics_committee_project_url": self.data[
                    "ethics_committee_project_url"
                ],
                "ethics_committee_project_file": self.data[
                    "ethics_committee_project_file"
                ],
                "is_public": self.data["is_public"],
                "data_acquisition_is_concluded": "",
            }
        )
        self.assertTrue(experiment.is_valid())


class GroupAdd_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "title": "Experimento TOC",
            "description": "Experimento TOC",
        }
        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

    def test_GroupForm_is_valid(self):
        title = self.data["title"]
        description = self.data["description"]

        groupAdd_form = GroupForm(data={"title": title, "description": description})
        self.assertTrue(groupAdd_form.is_valid())

    def test_GroupForm_is_not_valid_title(self):
        groupAdd_form = GroupForm(
            data={"title": "", "description": self.data["description"]}
        )
        self.assertFalse(groupAdd_form.is_valid())
        self.assertEqual(groupAdd_form.errors["title"], ["Este campo é obrigatório."])

    def test_GroupForm_is_not_valid_description(self):
        groupAdd_form = GroupForm(data={"title": self.data["title"], "description": ""})
        self.assertFalse(groupAdd_form.is_valid())
        self.assertEqual(
            groupAdd_form.errors["description"], ["Este campo é obrigatório."]
        )


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
#             is_public=True,
#             data_acquisition_is_concluded=True)
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
#             is_public=True,
#             data_acquisition_is_concluded=True)
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
#             is_public=True,
#             data_acquisition_is_concluded=True)
#
#
#     def test_SubjectFormPorPart_is_valid(self):
#         pass
#


class EEGsettings_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }
        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

    def test_EEGsettings_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]

        settingsEEG_form = EEGSettingForm(
            data={"name": name, "description": description}
        )
        self.assertTrue(settingsEEG_form.is_valid())

    def test_EEGsettings_is_not_valid_name(self):
        settingsEEG_form = EEGSettingForm(
            data={"name": "", "description": self.data["description"]}
        )
        self.assertFalse(settingsEEG_form.is_valid())
        self.assertEqual(settingsEEG_form.errors["name"], ["Este campo é obrigatório."])

    def test_EEGsettings_is_not_valid_description(self):
        settingsEEG_form = EEGSettingForm(
            data={"name": self.data["name"], "description": ""}
        )
        self.assertFalse(settingsEEG_form.is_valid())
        self.assertEqual(
            settingsEEG_form.errors["description"], ["Este campo é obrigatório."]
        )


class EEGAmplifierSettings_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
            "gain": "10",
            "sampling_rate": "10",
            "number_of_channels_used": "2",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.eeg_setting = EEGSetting.objects.create(
            experiment=cls.experiment,
            name="EEG-Setting name",
            description="EEG-Setting description",
        )
        cls.manufacturer = Manufacturer.objects.create(name="Manufacturer name")

        cls.amplifier = Amplifier.objects.create(
            manufacturer=cls.manufacturer,
            equipment_type="amplifier",
            identification="Amplifier identification",
        )

    def test_EEGAmplifierSettings_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]
        gain = self.data["gain"]
        sampling_rate = self.data["sampling_rate"]
        number_of_channels_used = self.data["number_of_channels_used"]

        settingsEEGAmplifier_form = EEGAmplifierSettingForm(
            data={
                "name": name,
                "description": description,
                "gain": gain,
                "sampling_rate": sampling_rate,
                "number_of_channels_used": number_of_channels_used,
            }
        )
        self.assertTrue(settingsEEGAmplifier_form.is_valid())

    def test_EEGAmplifierSettings_is_not_valid_gain(self):
        settingsEEGAmplifier_form = EEGAmplifierSettingForm(
            data={
                "name": self.data["name"],
                "description": self.data["description"],
                "gain": "",
                "sampling_rate": self.data["sampling_rate"],
                "number_of_channels_used": self.data["number_of_channels_used"],
            }
        )
        self.assertTrue(settingsEEGAmplifier_form.is_valid())

    def test_EEGAmplifierSettings_is_not_valid_sampling_rate(self):
        settingsEEGAmplifier_form = EEGAmplifierSettingForm(
            data={
                "name": self.data["name"],
                "description": self.data["description"],
                "gain": self.data["gain"],
                "sampling_rate": "",
                "number_of_channels_used": self.data["number_of_channels_used"],
            }
        )
        self.assertTrue(settingsEEGAmplifier_form.is_valid())

    def test_EEGAmplifierSettings_is_not_valid_number_of_channels_used(self):
        settingsEEGAmplifier_form = EEGAmplifierSettingForm(
            data={
                "name": self.data["name"],
                "description": self.data["description"],
                "gain": self.data["gain"],
                "sampling_rate": self.data["sampling_rate"],
                "number_of_channels_used": "",
            }
        )
        self.assertFalse(settingsEEGAmplifier_form.is_valid())
        self.assertEqual(
            settingsEEGAmplifier_form.errors["number_of_channels_used"],
            ["Este campo é obrigatório."],
        )


class EEGFilterSettings_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
            "high_pass": "100",
            "low_pass": "10",
            "low_band_pass": "20",
            "high_band_pass": "80",
            "low_notch": "25",
            "high_notch": "55",
            "order": "3",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.electrode_model = ElectrodeModel.objects.create(name="Electrode Model name")
        cls.tag = Tag.objects.create(name="EEG")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.manufacturer = Manufacturer.objects.create(name="Manufacturer name")

        cls.software = Software.objects.create(
            manufacturer=cls.manufacturer, name="Software name"
        )

        cls.software_version = SoftwareVersion.objects.create(
            software=cls.software, name="Software Version name"
        )

        cls.filter_type = FilterType.objects.create(name="Filter type name")

        cls.eeg_setting = EEGSetting.objects.create(
            experiment=cls.experiment,
            name="EEG-Setting name",
            description="EEG-Setting description",
        )

        cls.eeg_filter_setting = EEGFilterSetting.objects.create(
            eeg_setting=cls.eeg_setting,
            eeg_filter_type=cls.filter_type,
            high_pass=cls.data["high_pass"],
            low_pass=cls.data["low_pass"],
            low_band_pass=cls.data["low_band_pass"],
            high_band_pass=cls.data["high_band_pass"],
            low_notch=cls.data["low_notch"],
            high_notch=cls.data["high_notch"],
            order=cls.data["order"],
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

        settingsEEGFilter_form = EEGFilterSettingForm(
            data={
                "name": name,
                "description": description,
                "high_pass": high_pass,
                "low_pass": low_pass,
                "low_band_pass": low_band_pass,
                "high_band_pass": high_band_pass,
                "low_notch": low_notch,
                "high_notch": high_notch,
                "order": order,
            }
        )
        self.assertTrue(settingsEEGFilter_form.is_valid())


class EMGsettings_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Teste Experimento TOC",
        }
        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.electrode_model = ElectrodeModel.objects.create(name="Electrode Model name")
        cls.tag = Tag.objects.create(name="EMG")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.manufacturer = Manufacturer.objects.create(name="Manufacturer name")

        cls.software = Software.objects.create(
            manufacturer=cls.manufacturer, name="Software name"
        )

        cls.software_version = SoftwareVersion.objects.create(
            software=cls.software, name="Software Version name"
        )

        cls.emg_setting = EMGSetting.objects.create(
            experiment=cls.experiment,
            name="EMG-Setting name",
            description="EMG-Setting description",
            acquisition_software_version=cls.software_version,
        )

    def test_EMGSettings_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]
        acquisition_software_version = self.software_version.id

        settingsEMG_form = EMGSettingForm(
            data={
                "name": name,
                "description": description,
                "acquisition_software_version": acquisition_software_version,
            }
        )
        self.assertTrue(settingsEMG_form.is_valid())

    def test_EMGSettings_is_not_valid_name(self):
        name = self.data["name"]
        description = self.data["description"]
        acquisition_software_version = self.software_version.id

        settingsEMG_form = EMGSettingForm(
            data={
                "name": "",
                "description": description,
                "acquisition_software_version": acquisition_software_version,
            }
        )
        self.assertFalse(settingsEMG_form.is_valid())
        self.assertEqual(settingsEMG_form.errors["name"], ["Este campo é obrigatório."])

    def test_EMGSettings_is_not_valid_description(self):
        name = self.data["name"]
        description = self.data["description"]
        acquisition_software_version = self.software_version.id

        settingsEMG_form = EMGSettingForm(
            data={
                "name": name,
                "description": "",
                "acquisition_software_version": acquisition_software_version,
            }
        )
        self.assertFalse(settingsEMG_form.is_valid())
        self.assertEqual(
            settingsEMG_form.errors["description"], ["Este campo é obrigatório."]
        )

    def test_EMGSettings_is_not_valid_acquisition_software_version(self):
        name = self.data["name"]
        description = self.data["description"]
        acquisition_software_version = self.software_version.id

        settingsEMG_form = EMGSettingForm(
            data={
                "name": name,
                "description": description,
                "acquisition_software_version": "",
            }
        )
        self.assertTrue(
            settingsEMG_form.is_valid()
        )  # pelo forms.py, esse campo não é obrigatorio.


class EMGsettingsElectrodeAdd_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.manufacturer = Manufacturer.objects.create(name="Brain Vision")

        cls.electrode_model = ElectrodeModel.objects.create(name="Electrode Model name")
        cls.tag = Tag.objects.create(name="EMG")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.standardization_system = StandardizationSystem.objects.create(
            name="Standardization System identification",
            description="Standardization System description",
        )

        cls.muscle = Muscle.objects.create(name="Muscle identification")

        cls.muscle_subdivision = MuscleSubdivision.objects.create(
            name="Muscle subdivision identification",
            anatomy_origin="Anatomy origin description",
            anatomy_insertion="Anatomy insertion description",
            anatomy_function="Anatomy function description",
            muscle=cls.muscle,
        )

        cls.muscle_side = MuscleSide.objects.create(
            name="Muscle side identification", muscle=cls.muscle
        )

        cls.emg_electrode_placement = EMGElectrodePlacement.objects.create(
            standardization_system=cls.standardization_system,
            muscle_subdivision=cls.muscle_subdivision,
        )

        cls.data = {
            "name": "Experimento TOC",
            "description": "Teste Experimento TOC",
            "electrode": cls.electrode_model.id,
            "electrode_type": "Surface",
            "emg_electrode_placement": cls.emg_electrode_placement.id,
            "remarks": "Remarks",
            "muscle_side": cls.muscle_side.id,
        }

    def test_EMGsettingsElectrodeAdd_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]
        electrode = self.data["electrode"]

        settingEMG_electrode_add_form = EMGElectrodeSettingForm(
            data={"name": name, "description": description, "electrode": electrode}
        )
        self.assertTrue(settingEMG_electrode_add_form.is_valid())

    def test_EMGsettingsElectrodeAdd_is_valid_eletrode(self):
        name = self.data["name"]
        description = self.data["description"]
        electrode = self.data["electrode"]

        settingEMG_electrode_add_form = EMGElectrodeSettingForm(
            data={"name": name, "description": description, "electrode": ""}
        )
        self.assertFalse(settingEMG_electrode_add_form.is_valid())
        self.assertEqual(
            settingEMG_electrode_add_form.errors["electrode"],
            ["Este campo é obrigatório."],
        )


class EMGDigitalFilterSettings_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
            "high_pass": "100",
            "low_pass": "10",
            "low_band_pass": "20",
            "high_band_pass": "80",
            "low_notch": "25",
            "high_notch": "55",
            "order": "3",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.electrode_model = ElectrodeModel.objects.create(name="Electrode Model name")
        cls.tag = Tag.objects.create(name="EMG")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.manufacturer = Manufacturer.objects.create(name="Manufacturer name")

        cls.software = Software.objects.create(
            manufacturer=cls.manufacturer, name="Software name"
        )

        cls.software_version = SoftwareVersion.objects.create(
            software=cls.software, name="Software Version name"
        )

        cls.emg_setting = EMGSetting.objects.create(
            experiment=cls.experiment,
            name="EMG-Setting name",
            description="EMG-Setting description",
            acquisition_software_version=cls.software_version,
        )

        cls.filter_type = FilterType.objects.create(name="Filter type name")

        cls.emg_digital_filter_setting = EMGDigitalFilterSetting.objects.create(
            emg_setting=cls.emg_setting,
            filter_type=cls.filter_type,
            high_pass=cls.data["high_pass"],
            low_pass=cls.data["low_pass"],
            low_band_pass=cls.data["low_band_pass"],
            high_band_pass=cls.data["high_band_pass"],
            low_notch=cls.data["low_notch"],
            high_notch=cls.data["high_notch"],
            order=cls.data["order"],
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

        settingsEMGDigitalFilter_form = EMGDigitalFilterSettingForm(
            data={
                "name": name,
                "description": description,
                "filter_type": filter_type,
                "high_pass": high_pass,
                "low_pass": low_pass,
                "low_band_pass": low_band_pass,
                "high_band_pass": high_band_pass,
                "low_notch": low_notch,
                "high_notch": high_notch,
                "order": order,
            }
        )
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

        settingsEMGDigitalFilter_form = EMGDigitalFilterSettingForm(
            data={
                "name": name,
                "description": description,
                "filter_type": "",
                "high_pass": high_pass,
                "low_pass": low_pass,
                "low_band_pass": low_band_pass,
                "high_band_pass": high_band_pass,
                "low_notch": low_notch,
                "high_notch": high_notch,
                "order": order,
            }
        )
        self.assertFalse(settingsEMGDigitalFilter_form.is_valid())
        self.assertEqual(
            settingsEMGDigitalFilter_form.errors["filter_type"],
            ["Este campo é obrigatório."],
        )


class EMG_ADConverterSettings_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
            "sampling_rate": "10",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.electrode_model = ElectrodeModel.objects.create(name="Electrode Model name")
        cls.tag = Tag.objects.create(name="EMG")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.manufacturer = Manufacturer.objects.create(name="Manufacturer name")

        cls.software = Software.objects.create(
            manufacturer=cls.manufacturer, name="Software name"
        )

        cls.software_version = SoftwareVersion.objects.create(
            software=cls.software, name="Software Version name"
        )

        cls.emg_setting = EMGSetting.objects.create(
            experiment=cls.experiment,
            name="EMG-Setting name",
            description="EMG-Setting description",
            acquisition_software_version=cls.software_version,
        )

        cls.filter_type = FilterType.objects.create(name="Filter type name")

        cls.ad_converter = ADConverter.objects.create(
            manufacturer=cls.manufacturer,
            equipment_type="ad_converter",
            identification="AD Converter identification",
            signal_to_noise_rate=20,
            sampling_rate=cls.data["sampling_rate"],
            resolution=7,
        )

        cls.emg_ad_converter_setting = EMGADConverterSetting.objects.create(
            emg_setting=cls.emg_setting,
            ad_converter=cls.ad_converter,
            sampling_rate=cls.data["sampling_rate"],
        )

    def test_EMG_ADConverterSettings_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]
        filter_type = self.filter_type.id
        ad_converter = self.emg_ad_converter_setting.ad_converter
        sampling_rate = self.emg_ad_converter_setting.sampling_rate

        settingsEMG_ADConverter_form = EMGADConverterSettingForm(
            data={
                "name": name,
                "description": description,
                "ad_converter": ad_converter,
                "sampling_rate": sampling_rate,
            }
        )
        self.assertTrue(settingsEMG_ADConverter_form.is_valid())

    def test_EMG_ADConverterSettings_is_valid_ad_converter(self):
        name = self.data["name"]
        description = self.data["description"]
        filter_type = self.filter_type.id
        ad_converter = self.emg_ad_converter_setting.ad_converter
        sampling_rate = self.emg_ad_converter_setting.sampling_rate

        settingsEMG_ADConverter_form = EMGADConverterSettingForm(
            data={
                "name": name,
                "description": description,
                "ad_converter": "",
                "sampling_rate": sampling_rate,
            }
        )

        self.assertFalse(settingsEMG_ADConverter_form.is_valid())
        self.assertEqual(
            settingsEMG_ADConverter_form.errors["ad_converter"],
            ["Este campo é obrigatório."],
        )


class TMSSetting_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }
        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

    def test_TMSSetting_is_valid(self):
        name = self.data["name"]
        description = self.data["description"]

        settingTMS_form = TMSSettingForm(
            data={"name": name, "description": description}
        )
        self.assertTrue(settingTMS_form.is_valid())

    def test_TMSSetting_is_not_valid_name(self):
        settingTMS_form = TMSSettingForm(
            data={"name": "", "description": self.data["description"]}
        )
        self.assertFalse(settingTMS_form.is_valid())
        self.assertEqual(settingTMS_form.errors["name"], ["Este campo é obrigatório."])

    def test_TMSSetting_is_not_valid_description(self):
        settingTMS_form = TMSSettingForm(
            data={"name": self.data["name"], "description": ""}
        )
        self.assertFalse(settingTMS_form.is_valid())
        self.assertEqual(
            settingTMS_form.errors["description"], ["Este campo é obrigatório."]
        )


class TMSDevice_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
            "pulse_stimulus_type": "paired_pulse",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.manufacturer = Manufacturer.objects.create(name="Manufacturer name")

        cls.electrode_model = ElectrodeModel.objects.create(name="Electrode Model name")

        cls.tag = Tag.objects.create(name="TMS")
        cls.electrode_model.tags.add(cls.tag)
        cls.electrode_model.save()

        cls.coil_shape = CoilShape.objects.create(name="Electrode Shape name")
        cls.coil_model = CoilModel.objects.create(
            name="Electrode Model name", coil_shape=cls.coil_shape
        )

        cls.tms_setting = TMSSetting.objects.create(experiment=cls.experiment)

        cls.tms_device = TMSDevice.objects.create(
            pulse_type="monophase",
            manufacturer=cls.manufacturer,
            equipment_type="tms_device",
            identification="identification",
        )

        cls.tms_device_setting = TMSDeviceSetting.objects.create(
            tms_setting=cls.tms_setting,
            tms_device=cls.tms_device,
            pulse_stimulus_type=cls.data["pulse_stimulus_type"],
            coil_model=cls.coil_model,
        )

    def test_TMSDevice_is_valid(self):
        tms_device = self.tms_device
        pulse_stimulus_type = self.data["pulse_stimulus_type"]
        coil_model = self.coil_model.id

        deviceTMS_form = TMSDeviceSettingForm(
            data={
                "tms_device": tms_device,
                "coil_model": coil_model,
                "pulse_stimulus_type": pulse_stimulus_type,
            }
        )
        self.assertTrue(deviceTMS_form.is_valid())

    def test_TMSDevice_is_not_valid_tms_device(self):
        tms_device = self.tms_device
        pulse_stimulus_type = self.data["pulse_stimulus_type"]
        coil_model = self.coil_model.id

        deviceTMS_form = TMSDeviceSettingForm(
            data={
                "tms_device": "",
                "pulse_stimulus_type": pulse_stimulus_type,
                "coil_model": coil_model,
            }
        )
        self.assertFalse(deviceTMS_form.is_valid())
        self.assertEqual(
            deviceTMS_form.errors["tms_device"], ["Este campo é obrigatório."]
        )

    def test_TMSDevice_is_not_valid_coil_model(self):
        tms_device = self.tms_device
        pulse_stimulus_type = self.data["pulse_stimulus_type"]
        coil_model = self.coil_model.id

        deviceTMS_form = TMSDeviceSettingForm(
            data={
                "tms_device": tms_device,
                "pulse_stimulus_type": pulse_stimulus_type,
                "coil_model": "",
            }
        )
        self.assertFalse(deviceTMS_form.is_valid())
        self.assertEqual(
            deviceTMS_form.errors["coil_model"], ["Este campo é obrigatório."]
        )


class ContextTrees_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.context_tree = ContextTree.objects.create(
            experiment=cls.experiment,
            name="Context name",
            description="Context description",
        )

    def test_ContextTrees_is_valid(self):
        name = self.context_tree.name
        description = self.context_tree.description

        contextTrees_form = ContextTreeForm(
            data={"name": name, "description": description}
        )
        self.assertTrue(contextTrees_form.is_valid())

    def test_ContextTrees_is_not_valid_name(self):
        name = self.context_tree.name
        description = self.context_tree.description

        contextTrees_form = ContextTreeForm(
            data={"name": "", "description": description}
        )
        self.assertFalse(contextTrees_form.is_valid())
        self.assertEqual(
            contextTrees_form.errors["name"], ["Este campo é obrigatório."]
        )

    def test_ContextTrees_is_not_valid_description(self):
        name = self.context_tree.name
        description = self.context_tree.description

        contextTrees_form = ContextTreeForm(data={"name": name, "description": ""})
        self.assertFalse(contextTrees_form.is_valid())
        self.assertEqual(
            contextTrees_form.errors["description"], ["Este campo é obrigatório."]
        )


class SEP_Block_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            duration_unit=" ",
            description=" ",
            component_type="Set of steps",
        )

        cls.block = Block.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            component_type="Set of steps",
            type="sequence",
            number_of_mandatory_components=None,
        )

    def test_SEP_Block_is_valid(self):
        experiment = self.experiment
        number_of_mandatory_components = self.block.number_of_mandatory_components
        type = self.block.type

        sep_SEP_Block_form = BlockForm(
            data={
                "number_of_mandatory_components": number_of_mandatory_components,
                "type": type,
                "experiment": experiment,
            }
        )
        self.assertTrue(sep_SEP_Block_form.is_valid())

    def test_SEP_Block_is_not_valid_number_of_mandatory_components(self):
        experiment = self.experiment
        number_of_mandatory_components = " "
        type = self.block.type

        sep_SEP_Block_form = BlockForm(
            data={
                "number_of_mandatory_components": number_of_mandatory_components,
                "type": type,
                "experiment": experiment,
            }
        )
        self.assertFalse(sep_SEP_Block_form.is_valid())
        self.assertEqual(
            sep_SEP_Block_form.errors["number_of_mandatory_components"],
            ["Informe um número inteiro."],
        )

    def test_SEP_Block_is_not_valid_type(self):
        experiment = self.experiment
        number_of_mandatory_components = 0
        type = " "

        sep_SEP_Block_form = BlockForm(
            data={
                "number_of_mandatory_components": number_of_mandatory_components,
                "type": type,
                "experiment": experiment,
            }
        )
        self.assertFalse(sep_SEP_Block_form.is_valid())
        self.assertEqual(
            sep_SEP_Block_form.errors["type"],
            ["Faça uma escolha válida.   não é uma das escolhas disponíveis."],
        )


class SEP_Block_Block_Fix_Random_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            duration_unit=" ",
            description=" ",
            component_type="Set of steps",
        )

        cls.block = Block.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            component_type="Set of steps",
            type="sequence",
            number_of_mandatory_components=None,
        )

    def test_SEP_Block_Block_Fix_Random_is_valid(self):
        number_of_uses_to_insert = 1  # valor inicial >=1

        number_of_uses_SEP_Block_Block_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertTrue(number_of_uses_SEP_Block_Block_Fix_Random_form.is_valid())

    def test_SEP_Block_Block_Fix_Random_is_not_valid_number_of_uses_to_insert(self):
        number_of_uses_to_insert = 0  # valor inicial >=1

        number_of_uses_SEP_Block_Block_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertFalse(number_of_uses_SEP_Block_Block_Fix_Random_form.is_valid())
        self.assertEqual(
            number_of_uses_SEP_Block_Block_Fix_Random_form.errors[
                "number_of_uses_to_insert"
            ],
            ["Certifique-se que este valor seja maior ou igual a 1."],
        )


class SEP_Instruction_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            duration_unit="ms",
            duration_value="5",
            description=" ",
            component_type="instruction",
        )

        cls.instruction = Instruction.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            component_type="instruction",
            text="texto",
        )

    def test_SEP_Instruction_is_valid(self):
        text = self.instruction.text
        experiment = self.experiment

        sep_Instruction_form = InstructionForm(
            data={"text": text, "experiment": experiment}
        )
        self.assertTrue(sep_Instruction_form.is_valid())

    def test_SEP_Instruction_is_not_valid_text(self):
        text = ""
        experiment = self.experiment

        sep_Instruction_form = InstructionForm(
            data={"text": text, "experiment": experiment}
        )
        self.assertFalse(sep_Instruction_form.is_valid())
        self.assertEqual(
            sep_Instruction_form.errors["text"], ["Este campo é obrigatório."]
        )

    def test_SEP_Instruction_Fix_Random_is_valid(self):
        number_of_uses_to_insert = 1  # valor inicial >=1

        number_of_uses_SEP_Instruction_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertTrue(number_of_uses_SEP_Instruction_Fix_Random_form.is_valid())

    def test_SEP_Instruction_Fix_Random_is_not_valid_number_of_uses_to_insert(self):
        number_of_uses_to_insert = 0  # valor inicial >=1

        number_of_uses_SEP_Instruction_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertFalse(number_of_uses_SEP_Instruction_Fix_Random_form.is_valid())
        self.assertEqual(
            number_of_uses_SEP_Instruction_Fix_Random_form.errors[
                "number_of_uses_to_insert"
            ],
            ["Certifique-se que este valor seja maior ou igual a 1."],
        )


class SEP_Pause_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            component_type="pause",
        )

    def test_SEP_Pause_is_valid(self):
        # duration_value = self.component.duration_value
        # identification = self.component.identification
        duration_value = "5"
        duration_unit = "ms"
        identification = "Identification"
        experiment = self.experiment
        # component_type = "pause"

        sep_pause_form = ComponentForm(
            data={
                "identification": identification,
                "duration_value": duration_value,
                "duration_unit": duration_unit,
                "experiment": experiment,
            }
        )
        sep_pause_form.component_type = self.component.component_type  # jury-rig
        self.assertTrue(sep_pause_form.is_valid())

    def test_SEP_Pause_is_not_valid_identification(self):
        duration_value = "5"
        identification = ""
        experiment = self.experiment

        sep_pause_form = ComponentForm(
            data={
                "identification": identification,
                "duration_value": duration_value,
                "experiment": experiment,
            }
        )
        sep_pause_form.component_type = self.component.component_type  # jury-rig

        self.assertFalse(sep_pause_form.is_valid())
        self.assertEqual(
            sep_pause_form.errors["identification"], ["Este campo é obrigatório."]
        )

    def test_SEP_Pause_is_not_valid_duration_value(self):
        duration_value = ""
        identification = "identification"
        experiment = self.experiment

        sep_pause_form = ComponentForm(
            data={
                "identification": identification,
                "duration_value": duration_value,
                "experiment": experiment,
            }
        )
        sep_pause_form.component_type = self.component.component_type  # jury-rig

        self.assertFalse(sep_pause_form.is_valid())
        self.assertEqual(
            sep_pause_form.errors["duration_value"],
            ["Tempo da duração deve ser preenchido"],
        )

    def test_SEP_Pause_Fix_Random_is_valid(self):
        number_of_uses_to_insert = 1  # valor inicial >=1

        number_of_uses_SEP_Pause_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertTrue(number_of_uses_SEP_Pause_Fix_Random_form.is_valid())

    def test_SEP_Pause_Fix_Random_is_not_valid_number_of_uses_to_insert(self):
        number_of_uses_to_insert = 0  # valor inicial >=1

        number_of_uses_SEP_Pause_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertFalse(number_of_uses_SEP_Pause_Fix_Random_form.is_valid())
        self.assertEqual(
            number_of_uses_SEP_Pause_Fix_Random_form.errors["number_of_uses_to_insert"],
            ["Certifique-se que este valor seja maior ou igual a 1."],
        )


class SepQuestionnaireFormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {"name": "Experimento TOC", "description": "Experimento TOC"}

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            component_type="questionnaire",
        )

    def test_SEP_Questionnaire_is_valid(self):
        duration_value = "5"
        identification = "Identification"
        experiment = self.experiment

        sep_questionnaire_form = ComponentForm(
            data={
                "identification": identification,
                "duration_value": duration_value,
                "experiment": experiment,
            }
        )
        sep_questionnaire_form.component_type = (
            self.component.component_type
        )  # jury-rig
        self.assertTrue(sep_questionnaire_form.is_valid())

    def test_SEP_Questionnaire_is_not_valid_identification(self):
        duration_value = "5"
        identification = ""
        experiment = self.experiment

        sep_questionnaire_form = ComponentForm(
            data={
                "identification": identification,
                "duration_value": duration_value,
                "experiment": experiment,
            }
        )
        sep_questionnaire_form.component_type = (
            self.component.component_type
        )  # jury-rig

        self.assertFalse(sep_questionnaire_form.is_valid())
        self.assertEqual(
            sep_questionnaire_form.errors["identification"],
            ["Este campo é obrigatório."],
        )

    def test_SEP_Questionnaire_Fix_Random_is_valid(self):
        number_of_uses_to_insert = 1  # valor inicial >=1

        number_of_uses_sep_questionnaire_fix_random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertTrue(number_of_uses_sep_questionnaire_fix_random_form.is_valid())

    def test_SEP_Questionnaire_Fix_Random_is_not_valid_number_of_uses_to_insert(self):
        number_of_uses_to_insert = 0  # valor inicial >=1

        number_of_uses_sep_questionnaire_fix_random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertFalse(number_of_uses_sep_questionnaire_fix_random_form.is_valid())
        self.assertEqual(
            number_of_uses_sep_questionnaire_fix_random_form.errors[
                "number_of_uses_to_insert"
            ],
            ["Certifique-se que este valor seja maior ou igual a 1."],
        )


class SepStimulusFormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            duration_unit="ms",
            duration_value="5",
            description=" ",
            component_type="stimulus",
        )

        cls.stimulus_type = StimulusType.objects.create(name="Visual")

        cls.stimulus = Stimulus.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            component_type="stimulus",
            stimulus_type=cls.stimulus_type,
        )

    def test_SEP_Stimulus_Fix_Random_is_valid(self):
        number_of_uses_to_insert = 1  # valor inicial >=1

        number_of_uses_SEP_Stimulus_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertTrue(number_of_uses_SEP_Stimulus_Fix_Random_form.is_valid())

    def test_SEP_Stimulus_Fix_Random_is_not_valid_number_of_uses_to_insert(self):
        number_of_uses_to_insert = 0  # valor inicial >=1

        number_of_uses_SEP_Stimulus_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertFalse(number_of_uses_SEP_Stimulus_Fix_Random_form.is_valid())
        self.assertEqual(
            number_of_uses_SEP_Stimulus_Fix_Random_form.errors[
                "number_of_uses_to_insert"
            ],
            ["Certifique-se que este valor seja maior ou igual a 1."],
        )

    def test_SEP_Stimulus_is_valid(self):
        stimulus_type = self.stimulus.stimulus_type.id
        experiment = self.experiment

        sep_stimulus_form = StimulusForm(
            data={"stimulus_type": stimulus_type, "experiment": experiment}
        )
        self.assertTrue(sep_stimulus_form.is_valid())

    def test_SEP_Stimulus_is_not_valid_stimulus_type(self):
        stimulus_type = ""
        experiment = self.experiment

        sep_stimulus_form = StimulusForm(
            data={"stimulus_type": stimulus_type, "experiment": experiment}
        )
        self.assertFalse(sep_stimulus_form.is_valid())
        self.assertEqual(
            sep_stimulus_form.errors["stimulus_type"], ["Este campo é obrigatório."]
        )


class SEP_Task_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            component_type="task",
        )

    def test_SEP_Task_is_valid(self):
        identification = "Identification"
        experiment = self.experiment

        sep_task_form = ComponentForm(
            data={"identification": identification, "experiment": experiment}
        )
        sep_task_form.component_type = self.component.component_type  # jury-rig
        self.assertTrue(sep_task_form.is_valid())

    def test_SEP_Task_is_not_valid_identification(self):
        identification = ""
        experiment = self.experiment

        sep_task_form = ComponentForm(
            data={"identification": identification, "experiment": experiment}
        )
        sep_task_form.component_type = self.component.component_type  # jury-rig

        self.assertFalse(sep_task_form.is_valid())
        self.assertEqual(
            sep_task_form.errors["identification"], ["Este campo é obrigatório."]
        )

    def test_SEP_Task_Fix_Random_is_valid(self):
        number_of_uses_to_insert = 1  # valor inicial >=1

        number_of_uses_SEP_Task_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertTrue(number_of_uses_SEP_Task_Fix_Random_form.is_valid())

    def test_SEP_Task_Fix_Random_is_not_valid_number_of_uses_to_insert(self):
        number_of_uses_to_insert = 0  # valor inicial >=1

        number_of_uses_SEP_Task_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertFalse(number_of_uses_SEP_Task_Fix_Random_form.is_valid())
        self.assertEqual(
            number_of_uses_SEP_Task_Fix_Random_form.errors["number_of_uses_to_insert"],
            ["Certifique-se que este valor seja maior ou igual a 1."],
        )


class SEP_Task_Experiment_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            component_type="task_experiment",
        )

    def test_SEP_Task_Experiment_is_valid(self):
        identification = "Identification"
        experiment = self.experiment

        sep_task_experiment_form = ComponentForm(
            data={"identification": identification, "experiment": experiment}
        )
        sep_task_experiment_form.component_type = (
            self.component.component_type
        )  # jury-rig
        self.assertTrue(sep_task_experiment_form.is_valid())

    def test_SEP_Task_Experiment_is_not_valid_identification(self):
        identification = ""
        experiment = self.experiment

        sep_task_experiment_form = ComponentForm(
            data={"identification": identification, "experiment": experiment}
        )
        sep_task_experiment_form.component_type = (
            self.component.component_type
        )  # jury-rig

        self.assertFalse(sep_task_experiment_form.is_valid())
        self.assertEqual(
            sep_task_experiment_form.errors["identification"],
            ["Este campo é obrigatório."],
        )


class SEP_EEG_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            duration_unit="ms",
            duration_value="5",
            description=" ",
            component_type="eeg",
        )

        cls.eeg_setting = EEGSetting.objects.create(
            experiment=cls.experiment, name="EEG Setting", description="description"
        )

        cls.eeg = EEG.objects.create(
            experiment=cls.experiment,
            component_type="eeg",
            identification="Identification",
            eeg_setting=cls.eeg_setting,
        )

    def test_SEP_EEG_is_valid(self):
        experiment = self.experiment
        eeg_setting = self.eeg_setting.id

        sep_eeg_form = EEGForm(
            data={
                "eeg_setting": eeg_setting,
                "identification": "identification",
                "experiment": experiment,
            }
        )
        self.assertTrue(sep_eeg_form.is_valid())

    def test_SEP_EEG_is_not_valid_eeg_setting(self):
        eeg_setting = ""
        experiment = self.experiment

        sep_eeg_form = EEGForm(
            data={
                "eeg_setting": eeg_setting,
                "identification": "identification",
                "experiment": experiment,
            }
        )
        self.assertFalse(sep_eeg_form.is_valid())
        self.assertEqual(
            sep_eeg_form.errors["eeg_setting"], ["Este campo é obrigatório."]
        )

    def test_SEP_EEG_Fix_Random_is_valid(self):
        number_of_uses_to_insert = 1  # valor inicial >=1

        number_of_uses_SEP_EEG_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertTrue(number_of_uses_SEP_EEG_Fix_Random_form.is_valid())

    def test_SEP_EEG_Fix_Random_is_not_valid_number_of_uses_to_insert(self):
        number_of_uses_to_insert = 0  # valor inicial >=1

        number_of_uses_SEP_EEG_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertFalse(number_of_uses_SEP_EEG_Fix_Random_form.is_valid())
        self.assertEqual(
            number_of_uses_SEP_EEG_Fix_Random_form.errors["number_of_uses_to_insert"],
            ["Certifique-se que este valor seja maior ou igual a 1."],
        )


class SEP_EMG_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.manufacturer = Manufacturer.objects.create(name="Manufacturer name")

        cls.software = Software.objects.create(
            manufacturer=cls.manufacturer, name="Software name"
        )

        cls.software_version = SoftwareVersion.objects.create(
            software=cls.software, name="Software Version name"
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            duration_unit="ms",
            duration_value="5",
            description=" ",
            component_type="emg",
        )

        cls.emg_setting = EMGSetting.objects.create(
            experiment=cls.experiment,
            name="EMG Setting",
            description="description",
            acquisition_software_version=cls.software_version,
        )

        cls.emg = EMG.objects.create(
            experiment=cls.experiment,
            component_type="emg",
            identification="Identification",
            emg_setting=cls.emg_setting,
        )

    def test_SEP_EMG_is_valid(self):
        experiment = self.experiment
        emg_setting = self.emg_setting.id

        sep_emg_form = EMGForm(
            data={
                "emg_setting": emg_setting,
                "identification": "identification",
                "experiment": experiment,
            }
        )
        self.assertTrue(sep_emg_form.is_valid())

    def test_SEP_EMG_is_not_valid_emg_setting(self):
        emg_setting = ""
        experiment = self.experiment

        sep_emg_form = EMGForm(
            data={
                "emg_setting": emg_setting,
                "identification": "identification",
                "experiment": experiment,
            }
        )
        self.assertFalse(sep_emg_form.is_valid())
        self.assertEqual(
            sep_emg_form.errors["emg_setting"], ["Este campo é obrigatório."]
        )

    def test_SEP_EMG_Fix_Random_is_valid(self):
        number_of_uses_to_insert = 1  # valor inicial >=1

        number_of_uses_SEP_EMG_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertTrue(number_of_uses_SEP_EMG_Fix_Random_form.is_valid())

    def test_SEP_EMG_Fix_Random_is_not_valid_number_of_uses_to_insert(self):
        number_of_uses_to_insert = 0  # valor inicial >=1

        number_of_uses_SEP_EMG_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertFalse(number_of_uses_SEP_EMG_Fix_Random_form.is_valid())
        self.assertEqual(
            number_of_uses_SEP_EMG_Fix_Random_form.errors["number_of_uses_to_insert"],
            ["Certifique-se que este valor seja maior ou igual a 1."],
        )


class SEP_TMS_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            duration_unit="ms",
            duration_value="5",
            description=" ",
            component_type="tms",
        )

        cls.tms_setting = TMSSetting.objects.create(
            experiment=cls.experiment, name="TMS Setting", description="description"
        )

        cls.tms = TMS.objects.create(
            experiment=cls.experiment,
            component_type="tms",
            identification="Identification",
            tms_setting=cls.tms_setting,
        )

    def test_SEP_TMS_is_valid(self):
        experiment = self.experiment
        tms_setting = self.tms_setting.id

        sep_tms_form = TMSForm(
            data={
                "tms_setting": tms_setting,
                "identification": "identification",
                "experiment": experiment,
            }
        )
        self.assertTrue(sep_tms_form.is_valid())

    def test_SEP_TMS_is_not_valid_tms_setting(self):
        tms_setting = ""
        experiment = self.experiment

        sep_tms_form = TMSForm(
            data={
                "tms_setting": tms_setting,
                "identification": "identification",
                "experiment": experiment,
            }
        )
        self.assertFalse(sep_tms_form.is_valid())
        self.assertEqual(
            sep_tms_form.errors["tms_setting"], ["Este campo é obrigatório."]
        )

    def test_SEP_TMS_Fix_Random_is_valid(self):
        number_of_uses_to_insert = 1  # valor inicial >=1

        number_of_uses_SEP_TMS_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertTrue(number_of_uses_SEP_TMS_Fix_Random_form.is_valid())

    def test_SEP_TMS_Fix_Random_is_not_valid_number_of_uses_to_insert(self):
        number_of_uses_to_insert = 0  # valor inicial >=1

        number_of_uses_SEP_TMS_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertFalse(number_of_uses_SEP_TMS_Fix_Random_form.is_valid())
        self.assertEqual(
            number_of_uses_SEP_TMS_Fix_Random_form.errors["number_of_uses_to_insert"],
            ["Certifique-se que este valor seja maior ou igual a 1."],
        )


class SEP_GenericDataCollection_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            duration_unit="ms",
            duration_value="5",
            description=" ",
            component_type="generic_data_collection",
        )

        cls.information_type = InformationType.objects.create(
            name="Generic Data Collection", description="description"
        )

        cls.gdc = GenericDataCollection.objects.create(
            experiment=cls.experiment,
            component_type="generic_data_collection",
            identification="Identification",
            information_type=cls.information_type,
        )

    def test_SEP_GenericDataCollection_is_valid(self):
        experiment = self.experiment
        information_type = self.information_type.id

        sep_gdc_form = GenericDataCollectionForm(
            data={
                "information_type": information_type,
                "identification": "identification",
                "experiment": experiment,
            }
        )
        self.assertTrue(sep_gdc_form.is_valid())

    def test_SEP_GenericDataCollection_is_not_valid_gdc_setting(self):
        information_type = ""
        experiment = self.experiment

        sep_gdc_form = GenericDataCollectionForm(
            data={
                "information_type": information_type,
                "identification": "identification",
                "experiment": experiment,
            }
        )
        self.assertFalse(sep_gdc_form.is_valid())
        self.assertEqual(
            sep_gdc_form.errors["information_type"], ["Este campo é obrigatório."]
        )

    def test_SEP_GenericDataCollection_Fix_Random_is_valid(self):
        number_of_uses_to_insert = 1  # valor inicial >=1

        number_of_uses_SEP_GenericDataCollection_Fix_Random_form = (
            NumberOfUsesToInsertForm(
                data={"number_of_uses_to_insert": number_of_uses_to_insert}
            )
        )
        self.assertTrue(
            number_of_uses_SEP_GenericDataCollection_Fix_Random_form.is_valid()
        )

    def test_SEP_GenericDataCollection_Fix_Random_is_not_valid_number_of_uses_to_insert(
        self,
    ):
        number_of_uses_to_insert = 0  # valor inicial >=1

        number_of_uses_SEP_GenericDataCollection_Fix_Random_form = (
            NumberOfUsesToInsertForm(
                data={"number_of_uses_to_insert": number_of_uses_to_insert}
            )
        )
        self.assertFalse(
            number_of_uses_SEP_GenericDataCollection_Fix_Random_form.is_valid()
        )
        self.assertEqual(
            number_of_uses_SEP_GenericDataCollection_Fix_Random_form.errors[
                "number_of_uses_to_insert"
            ],
            ["Certifique-se que este valor seja maior ou igual a 1."],
        )


class SEP_DigitalGamePhase_FormTest(TestCase):
    @classmethod
    def setUp(cls):
        cls.data = {
            "name": "Experimento TOC",
            "description": "Experimento TOC",
        }

        cls.research_project = ResearchProject.objects.create(
            title="Research project title",
            start_date=datetime.date.today(),
            description="Research project description",
        )

        cls.experiment = Experiment.objects.create(
            research_project_id=cls.research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
            source_code_url="http://www.if.usp.br",
            ethics_committee_project_url="http://www.fm.usp.br",
            ethics_committee_project_file="/users/celsovi/documents/unit_tests/links.rtf",
            is_public=True,
            data_acquisition_is_concluded=True,
        )

        cls.manufacturer = Manufacturer.objects.create(name="Manufacturer name")

        cls.software = Software.objects.create(
            manufacturer=cls.manufacturer, name="Software name"
        )

        cls.software_version = SoftwareVersion.objects.create(
            software=cls.software, name="Software Version name"
        )

        cls.context_tree = ContextTree.objects.create(
            experiment=cls.experiment,
            name="Context name",
            description="Context description",
        )

        cls.component = Component.objects.create(
            experiment=cls.experiment,
            identification="Identification",
            duration_unit="ms",
            duration_value="5",
            description=" ",
            component_type="digital_game_phase",
        )

        cls.dgp = DigitalGamePhase.objects.create(
            experiment=cls.experiment,
            software_version=cls.software_version,
            context_tree=cls.context_tree,
        )

    def test_SEP_DigitalGamePhase_is_valid(self):
        experiment = self.experiment
        context_tree = self.context_tree.id
        software_version = self.software_version.id

        sep_dgp_form = DigitalGamePhaseForm(
            data={
                "software_version": software_version,
                "context_tree": context_tree,
                "experiment": experiment,
            }
        )
        self.assertTrue(sep_dgp_form.is_valid())

    def test_SEP_DigitalGamePhase_is_not_valid_software_version(self):
        experiment = self.experiment
        context_tree = self.context_tree.id
        software_version = ""

        sep_dgp_form = DigitalGamePhaseForm(
            data={
                "software_version": software_version,
                "context_tree": context_tree,
                "experiment": experiment,
            }
        )
        self.assertFalse(sep_dgp_form.is_valid())
        self.assertEqual(
            sep_dgp_form.errors["software_version"], ["Este campo é obrigatório."]
        )

    def test_SEP_DigitalGamePhase_is_not_valid_context_tree(self):
        experiment = self.experiment
        context_tree = ""
        software_version = self.software_version

        sep_dgp_form = DigitalGamePhaseForm(
            data={
                "software_version": software_version,
                "context_tree": context_tree,
                "experiment": experiment,
            }
        )
        self.assertFalse(sep_dgp_form.is_valid())
        self.assertEqual(
            sep_dgp_form.errors["context_tree"], ["Este campo é obrigatório."]
        )

    def test_SEP_DigitalGamePhase_Fix_Random_is_valid(self):
        number_of_uses_to_insert = 1  # valor inicial >=1

        number_of_uses_SEP_DigitalGamePhase_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertTrue(number_of_uses_SEP_DigitalGamePhase_Fix_Random_form.is_valid())

    def test_SEP_DigitalGamePhase_Fix_Random_is_not_valid_number_of_uses_to_insert(
        self,
    ):
        number_of_uses_to_insert = 0  # valor inicial >=1

        number_of_uses_SEP_DigitalGamePhase_Fix_Random_form = NumberOfUsesToInsertForm(
            data={"number_of_uses_to_insert": number_of_uses_to_insert}
        )
        self.assertFalse(number_of_uses_SEP_DigitalGamePhase_Fix_Random_form.is_valid())
        self.assertEqual(
            number_of_uses_SEP_DigitalGamePhase_Fix_Random_form.errors[
                "number_of_uses_to_insert"
            ],
            ["Certifique-se que este valor seja maior ou igual a 1."],
        )
