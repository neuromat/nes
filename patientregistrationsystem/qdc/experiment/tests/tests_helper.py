import datetime
import os
import random
import tempfile
import zipfile

from django.apps import apps
from django.contrib.auth.models import User, Group as UserGroup
from django.core.files import File
from django.db import IntegrityError
from django.test import RequestFactory, TestCase
from faker import Factory

from custom_user.tests.tests_helper import create_user
from experiment.models import (
    ResearchProject,
    Experiment,
    ExperimentResearcher,
    Publication,
    ContextTree,
    EEGSetting,
    EEGAmplifierSetting,
    EMGSetting,
    TMSSetting,
    TMSDevice,
    EMGElectrodeSetting,
    EMGElectrodePlacementSetting,
    StandardizationSystem,
    Muscle,
    MuscleSubdivision,
    MuscleSide,
    EMGElectrodePlacement,
    Component,
    TaskForTheExperimenter,
    DigitalGamePhase,
    GenericDataCollection,
    EEG,
    EMG,
    TMS,
    Group,
    Subject,
    SubjectOfGroup,
    Block,
    Manufacturer,
    Amplifier,
    EEGSolution,
    FilterType,
    Tag,
    ElectrodeModel,
    EEGElectrodeNet,
    EEGElectrodeNetSystem,
    EEGElectrodeLocalizationSystem,
    EEGElectrodePosition,
    EEGElectrodeLayoutSetting,
    EEGElectrodePositionSetting,
    EEGElectrodePositionCollectionStatus,
    Software,
    SoftwareVersion,
    ADConverter,
    Material,
    EEGElectrodeCap,
    EEGCapSize,
    CoilModel,
    CoilShape,
    ComponentConfiguration,
    DataConfigurationTree,
    QuestionnaireResponse,
    InformationType,
    FileFormat,
    GenericDataCollectionData,
    GenericDataCollectionFile,
    EEGData,
    EEGFile,
    EMGData,
    DirectionOfTheInducedCurrent,
    CoilOrientation,
    TMSData,
    BrainAreaSystem,
    BrainArea,
    TMSLocalizationSystem,
    EMGFile,
    DigitalGamePhaseData,
    DigitalGamePhaseFile,
    AdditionalData,
    AdditionalDataFile,
    StimulusType,
    Stimulus,
)
from patient.models import (
    ClassificationOfDiseases,
    MedicalRecordData,
    Diagnosis,
    ComplementaryExam,
    ExamFile,
)
from patient.tests.test_orig import UtilTests
from survey.tests.tests_helper import create_survey
import os


class ExperimentTestCase(TestCase):
    def setUp(self):
        super(ExperimentTestCase, self).setUp()
        # create the groups of users and their permissions
        exec(open(os.getcwd() + "/add_initial_data.py").read())

        self.user, self.user_passwd = create_user(UserGroup.objects.all())

        self.research_project = ObjectsFactory.create_research_project(self.user)
        self.experiment = ObjectsFactory.create_experiment(self.research_project)
        self.root_component = ObjectsFactory.create_block(self.experiment)
        self.group = ObjectsFactory.create_group(self.experiment, self.root_component)

        self.patient = UtilTests().create_patient(changed_by=self.user)
        self.subject = ObjectsFactory.create_subject(self.patient)
        self.subject_of_group = ObjectsFactory.create_subject_of_group(
            self.group, self.subject
        )


USER_USERNAME = "myadmin"
USER_PWD = "mypassword"


class ObjectsFactory(object):
    @staticmethod
    def create_research_project(owner=None):
        """Create a research project to be used in the test

        :return: research project
        """
        research_project = ResearchProject.objects.create(
            title="Research project title",
            description="Research project description",
            start_date=datetime.date.today() - datetime.timedelta(60),
            end_date=datetime.date.today(),
            owner=owner,
        )
        research_project.save()
        return research_project

    @staticmethod
    def create_experiment(research_project):
        """Create an experiment to be used in the test
        :param research_project: research project
        :return: experiment
        """
        experiment = Experiment.objects.create(
            research_project_id=research_project.id,
            title="Experimento-Update",
            description="Descricao do Experimento-Update",
        )
        experiment.changed_by = None
        experiment.save()
        return experiment

    @staticmethod
    def create_experiment_researcher(experiment):
        """Create an experiment researcher to be used in tests
        :param experiment: researcher's experiment
        :return: ExperimentResearcher model instance
        """
        user, passwd = create_user()

        return ExperimentResearcher.objects.create(
            experiment=experiment, researcher=user
        )

    @staticmethod
    def create_publication(list_of_experiments):
        """Create a publication to be used in the test
        :param list_of_experiments: list of experiments
        :return: publication
        """

        publication = Publication.objects.create(
            title="Publication-Update", citation="Citation-Update"
        )
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
            experiment=experiment,
            name="Context tree name",
            description="Context tree description",
        )
        context_tree.save()
        return context_tree

    @staticmethod
    def create_eeg_setting(experiment):
        eeg_setting = EEGSetting.objects.create(
            experiment=experiment,
            name="EEG-Setting name",
            description="EEG-Setting description",
        )
        return eeg_setting

    @staticmethod
    def create_eeg_amplifier_setting(eeg_setting, amplifier):
        # First implementation needed number_of_channels_used=129 for test
        return EEGAmplifierSetting.objects.create(
            eeg_setting=eeg_setting,
            eeg_amplifier=amplifier,
            number_of_channels_used=129,
        )

    @staticmethod
    def create_emg_setting(experiment, acquisition_software_version):
        emg_setting = EMGSetting.objects.create(
            experiment=experiment,
            name="EMG-Setting name",
            description="EMG-Setting description",
            acquisition_software_version=acquisition_software_version,
        )
        return emg_setting

    @staticmethod
    def create_tms_setting(experiment):
        return TMSSetting.objects.create(
            experiment=experiment,
            name="TMS-Setting name",
            description="TMS-Setting description",
        )

    @staticmethod
    def create_tms_device(manufacturer):
        fake = Factory.create()
        TMSDevice.objects.create(
            manufacturer=manufacturer,
            equipment_type=TMSDevice.EQUIPMENT_TYPES[0][0],
            identification=fake.lorem.word(),
            description=fake.text(),
            serial_number=fake.ssn(),
        )

    @staticmethod
    def create_emg_electrode_setting(emg_setting, electrode_model):
        return EMGElectrodeSetting.objects.create(
            emg_setting=emg_setting, electrode=electrode_model
        )

    @staticmethod
    def create_emg_electrode_placement_setting(
        emg_electrode_setting, electrode_placement, muscle_side=None
    ):
        return EMGElectrodePlacementSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting,
            emg_electrode_placement=electrode_placement,
            muscle_side=muscle_side,
            remarks="Remarks electrode placement setting",
        )

    @staticmethod
    def create_standardization_system():
        return StandardizationSystem.objects.create(
            name="Standardization System identification",
            description="Standardization System description",
        )

    @staticmethod
    def create_muscle():
        return Muscle.objects.create(name="Muscle identification")

    @staticmethod
    def create_muscle_subdivision(muscle):
        return MuscleSubdivision.objects.create(
            name="Muscle subdivision identification",
            anatomy_origin="Anatomy origin description",
            anatomy_insertion="Anatomy insertion description",
            anatomy_function="Anatomy function description",
            muscle=muscle,
        )

    @staticmethod
    def create_muscle_side(muscle):
        muscle_side = MuscleSide.objects.create(
            name="Muscle side identification", muscle=muscle
        )
        muscle_side.save()
        return muscle_side

    @staticmethod
    def create_emg_electrode_placement(standardization_system, muscle_subdivision):
        with tempfile.TemporaryDirectory() as tmpdirname:
            bin_file = ObjectsFactory.create_binary_file(tmpdirname)
            emg_ep = EMGElectrodePlacement.objects.create(
                standardization_system=standardization_system,
                muscle_subdivision=muscle_subdivision,
                placement_type=random.choice(EMGElectrodePlacement.PLACEMENT_TYPES)[0],
            )
            with File(open(bin_file.name, "rb")) as f:
                # TODO (NES-987): get os.path.basename(f.name) instead of 'file.bin'
                emg_ep.photo.save("file.bin", f)
            emg_ep.save()
        return emg_ep

    @staticmethod
    def create_component(experiment, component_type, identification=None, kwargs=None):
        fake = Factory.create()

        if component_type == Component.TASK_EXPERIMENT:
            model = TaskForTheExperimenter.__name__
        elif component_type == Component.DIGITAL_GAME_PHASE:
            model = DigitalGamePhase.__name__
        elif component_type == Component.GENERIC_DATA_COLLECTION:
            model = GenericDataCollection.__name__
        elif component_type == Component.EEG:
            model = EEG.__name__
        elif component_type == Component.EMG:
            model = EMG.__name__
        elif component_type == Component.TMS:
            model = TMS.__name__
        else:
            model = component_type

        component = apps.get_model("experiment", model)(
            experiment=experiment,
            identification=identification or fake.ssn(),
            component_type=component_type,
            description=fake.text(max_nb_chars=15),
        )

        if component_type == Component.QUESTIONNAIRE:
            try:
                component.survey = kwargs["survey"]
            except KeyError:
                print("You must specify 'sid' key in kwargs dict")
        elif component_type == Component.GENERIC_DATA_COLLECTION:
            try:
                component.information_type = kwargs["it"]
            except KeyError:
                print("You must specify 'it' key in kwargs dict")
        elif component_type == Component.DIGITAL_GAME_PHASE:
            try:
                component.software_version = kwargs["software_version"]
                component.context_tree = kwargs["context_tree"]
            except KeyError:
                print(
                    "You must specify 'software_version' and 'context_tree' key in kwargs dict"
                )
        elif component_type == Component.EEG:
            try:
                component.eeg_setting = kwargs["eeg_set"]
            except KeyError:
                print("You must specify 'eeg_setting' key in kwargs dict")
        elif component_type == Component.EMG:
            try:
                component.emg_setting = kwargs["emg_set"]
            except KeyError:
                print("You must specify 'emg_setting' key in kwargs dict")
        elif component_type == Component.STIMULUS:
            try:
                component.stimulus_type = kwargs["stimulus_type"]
                component.media_file = kwargs.get("media_file", None)
            except KeyError:
                print(
                    "You must specify 'stimulus_type' and 'media_file' key in kwargs dict"
                )
        elif component_type == Component.TMS:
            try:
                component.tms_setting = kwargs["tms_set"]
            except KeyError:
                print("You must specify 'tms_setting' key in kwargs dict")
        try:
            component.save()
        except IntegrityError:
            print(
                "Have you remembered to give specific attribute for "
                "the specific component?"
            )

        return component

    @staticmethod
    def create_group(experiment, experimental_protocol=None):
        """
        :param experiment: experiment
        :param experimental_protocol: experimental protocol
        :return: group
        """
        fake = Factory.create()

        group = Group.objects.create(
            experiment=experiment,
            title=fake.word(),
            description=fake.text(max_nb_chars=15),
            experimental_protocol=experimental_protocol,
        )
        return group

    @staticmethod
    def create_subject(patient):
        """
        :param patient: Patient model instance
        :return: Subject model instance
        """
        return Subject.objects.create(patient=patient)

    @staticmethod
    def create_subject_of_group(group, subject):
        """
        :param group: Group model instance
        :param subject: Subject model instance
        :return: SubjectOfGroup model instance
        """
        subject_of_group = SubjectOfGroup.objects.create(subject=subject, group=group)
        group.subjectofgroup_set.add(subject_of_group)

        return subject_of_group

    @staticmethod
    def create_block(experiment):
        block = Block.objects.create(
            identification="Block identification",
            description="Block description",
            experiment=experiment,
            component_type=Component.BLOCK,
            type="sequence",
        )
        block.save()
        return block

    @staticmethod
    def create_manufacturer():
        manufacturer = Manufacturer.objects.create(name="Manufacturer name")
        return manufacturer

    @staticmethod
    def create_amplifier(manufacturer):
        amplifier = Amplifier.objects.create(
            manufacturer=manufacturer,
            equipment_type="amplifier",
            identification="Amplifier identification",
        )
        amplifier.save()
        return amplifier

    @staticmethod
    def create_eeg_solution(manufacturer):
        eeg_solution = EEGSolution.objects.create(
            manufacturer=manufacturer, name="Solution name"
        )
        eeg_solution.save()
        return eeg_solution

    @staticmethod
    def create_filter_type():
        filter_type = FilterType.objects.create(name="Filter type name")
        filter_type.save()
        return filter_type

    @staticmethod
    def create_tag(name="TAG name"):
        tag = Tag.objects.create(name=name)
        tag.save()
        return tag

    @staticmethod
    def create_electrode_model():
        electrode_model = ElectrodeModel.objects.create(name="Electrode Model name")
        tagaux = ObjectsFactory.create_tag("EEG")
        electrode_model.tags.add(tagaux)
        electrode_model.save()
        return electrode_model

    @staticmethod
    def create_eeg_electrode_net(manufacturer, electrode_model_default):
        eeg_electrode_net = EEGElectrodeNet.objects.create(
            manufacturer=manufacturer,
            equipment_type="eeg_electrode_net",
            electrode_model_default=electrode_model_default,
            identification="Electrode Net identification",
        )
        eeg_electrode_net.save()
        return eeg_electrode_net

    @staticmethod
    def create_eeg_electrode_net_system(
        eeg_electrode_net, eeg_electrode_localization_system
    ):
        eeg_electrode_net_system = EEGElectrodeNetSystem.objects.create(
            eeg_electrode_net=eeg_electrode_net,
            eeg_electrode_localization_system=eeg_electrode_localization_system,
        )
        eeg_electrode_net_system.save()
        return eeg_electrode_net_system

    @staticmethod
    def create_eeg_electrode_localization_system():
        fake = Factory.create()

        with tempfile.TemporaryDirectory() as tmpdirname:
            bin_file = ObjectsFactory.create_binary_file(tmpdirname)
            eeg_els = EEGElectrodeLocalizationSystem.objects.create(
                name=fake.word(), description=fake.text()
            )
            with File(open(bin_file.name, "rb")) as f:
                eeg_els.map_image_file.save("file.bin", f)
            eeg_els.save()
        return eeg_els

    @staticmethod
    def create_eeg_electrode_position(eeg_electrode_localization_system):
        return EEGElectrodePosition.objects.create(
            eeg_electrode_localization_system=eeg_electrode_localization_system,
            name="Position name",
        )

    @staticmethod
    def create_eeg_electrode_layout_setting(eeg_setting, eeg_electrode_net_system):
        return EEGElectrodeLayoutSetting.objects.create(
            eeg_setting=eeg_setting, eeg_electrode_net_system=eeg_electrode_net_system
        )

    @staticmethod
    def create_eeg_electrode_position_setting(
        eeg_electrode_layout_setting, eeg_electrode_position, electrode_model
    ):
        fake = Factory.create()
        return EEGElectrodePositionSetting.objects.create(
            eeg_electrode_layout_setting=eeg_electrode_layout_setting,
            eeg_electrode_position=eeg_electrode_position,
            electrode_model=electrode_model,
            used=random.choice([True, False]),
            channel_index=fake.pyint(),
        )

    @staticmethod
    def create_eeg_electrode_position_collection_status(
        eeg_data, eeg_electrode_position_setting
    ):
        fake = Factory.create()
        return EEGElectrodePositionCollectionStatus.objects.create(
            eeg_data=eeg_data,
            eeg_electrode_position_setting=eeg_electrode_position_setting,
            worked=random.choice([True, False]),
            channel_index=fake.pyint(),
        )

    @staticmethod
    def create_software(manufacturer):
        software = Software.objects.create(
            manufacturer=manufacturer, name="Software name"
        )
        software.save()
        return software

    @staticmethod
    def create_software_version(software):
        software_version = SoftwareVersion.objects.create(
            software=software, name="Software Version name"
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
            resolution=7,
        )
        ad_converter.save()
        return ad_converter

    @staticmethod
    def system_authentication(instance):
        user = User.objects.create_user(
            username=USER_USERNAME, email="test@dummy.com", password=USER_PWD
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        factory = RequestFactory()
        logged = instance.client.login(username=USER_USERNAME, password=USER_PWD)
        return logged, user, factory

    @staticmethod
    def create_material():
        material = Material.objects.create(name="Material name")
        material.save()
        return material

    @staticmethod
    def create_eeg_electrode_cap(manufacturer, electrode_model, material=None):
        return EEGElectrodeCap.objects.create(
            manufacturer=manufacturer,
            identification="EEG electrode cap identification",
            electrode_model_default=electrode_model,
            material=material,
            equipment_type="eeg_electrode_net",
        )

    @staticmethod
    def create_eeg_electrode_capsize(eeg_electrode_cap):
        fake = Factory.create()
        return EEGCapSize.objects.create(
            eeg_electrode_cap=eeg_electrode_cap,
            size=fake.word(),
            electrode_adjacent_distance=fake.pyfloat(),
        )

    @staticmethod
    def create_coil_model(coil_shape):
        coil_model = CoilModel.objects.create(
            name="Electrode Model name", coil_shape=coil_shape
        )
        coil_model.save()
        return coil_model

    @staticmethod
    def create_coil_shape():
        coil_shape = CoilShape.objects.create(name="Electrode Shape name")
        coil_shape.save()
        return coil_shape

    @staticmethod
    def create_component_configuration(parent, component):
        fake = Factory.create()

        return ComponentConfiguration.objects.create(
            name=fake.word(), parent=parent, component=component
        )

    @staticmethod
    def create_data_configuration_tree(component_config, parent=None):
        return DataConfigurationTree.objects.create(
            component_configuration=component_config,
            code=random.randint(1, 999),
            parent=parent,
        )

    @staticmethod
    def create_questionnaire_response(dct, responsible, token_id, subject_of_group):
        return QuestionnaireResponse.objects.create(
            data_configuration_tree=dct,
            questionnaire_responsible=responsible,
            token_id=token_id,
            subject_of_group=subject_of_group,
            is_completed=datetime.datetime.now().strftime("%c"),
        )

    @staticmethod
    def create_information_type():
        fake = Factory.create()

        return InformationType.objects.create(name=fake.word(), description=fake.text())

    @staticmethod
    def create_file_format():
        fake = Factory.create()
        while True:  # nes_code is unique
            # Change this for changes in real FileFormat objects
            # Mading this way because this data is loaded on NES instalation
            nes_code = random.choice(
                ["txt", "MNE-RawFromBrainVision", "other", "MNE-NEO-RawBinarySignalIO"]
            )
            if not FileFormat.objects.filter(nes_code=nes_code).first():
                break

        return FileFormat.objects.create(
            nes_code=nes_code, name=fake.file_extension(), description=fake.text()
        )

    @staticmethod
    def create_generic_data_collection_data(data_conf_tree, subj_of_group):
        fake = Factory.create()

        file_format = ObjectsFactory.create_file_format()
        return GenericDataCollectionData.objects.create(
            description=fake.text(),
            file_format=file_format,
            file_format_description=fake.text(),
            data_configuration_tree=data_conf_tree,
            subject_of_group=subj_of_group,
        )

    @staticmethod
    def create_binary_file(path, name="file.bin"):
        with open(os.path.join(path, name), "wb") as f:
            f.write(b"carambola")
            return f

    @staticmethod
    def create_csv_file(dir_, name="file.csv"):
        with open(os.path.join(dir_, name), "w") as f:
            f.write("h1,h2\n")
            f.write("v1,v2\n")
            return f

    @staticmethod
    def create_zipfile(zip_dir, file_list):
        zip_file = zipfile.ZipFile(os.path.join(zip_dir, "dummy_file.zip"), "w")
        for file in file_list:
            zip_file.write(file.name, os.path.basename(file.name))
        zip_file.close()
        return zip_file

    @staticmethod
    def create_generic_data_collection_file(gdc_data):
        with tempfile.TemporaryDirectory() as tmpdirname:
            bin_file = ObjectsFactory.create_binary_file(tmpdirname)

            gdcf = GenericDataCollectionFile.objects.create(
                generic_data_collection_data=gdc_data
            )
            with File(open(bin_file.name, "rb")) as f:
                gdcf.file.save("file.bin", f)
            gdcf.save()

        return gdcf

    @staticmethod
    def create_eeg_data(data_conf_tree, subj_of_group, eeg_set, eeg_cap_size=None):
        fake = Factory.create()

        file_format = ObjectsFactory.create_file_format()
        return EEGData.objects.create(
            description=fake.text(),
            file_format=file_format,
            file_format_description=fake.text(),
            data_configuration_tree=data_conf_tree,
            subject_of_group=subj_of_group,
            eeg_setting=eeg_set,
            eeg_cap_size=eeg_cap_size,
        )

    @staticmethod
    def create_eeg_file(eeg_data):
        with tempfile.TemporaryDirectory() as tmpdirname:
            bin_file = ObjectsFactory.create_binary_file(tmpdirname)
            eegf = EEGFile.objects.create(eeg_data=eeg_data)
            with File(open(bin_file.name, "rb")) as f:
                eegf.file.save("file.bin", f)
            eegf.save()

        return eegf

    @staticmethod
    def create_emg_data_collection_data(data_conf_tree, subj_of_group, emg_set):
        fake = Factory.create()

        file_format = ObjectsFactory.create_file_format()
        return EMGData.objects.create(
            description=fake.text(),
            file_format=file_format,
            file_format_description=fake.text(),
            data_configuration_tree=data_conf_tree,
            subject_of_group=subj_of_group,
            emg_setting=emg_set,
        )

    @staticmethod
    def create_tms_data_collection_data(data_conf_tree, subj_of_group, tms_set):
        fake = Factory.create()
        doic = DirectionOfTheInducedCurrent.objects.create(
            name="Direction of Induced Current"
        )
        coilor = CoilOrientation.objects.create(name="Coil Orientation")

        return TMSData.objects.create(
            tms_setting=tms_set,
            data_configuration_tree=data_conf_tree,
            subject_of_group=subj_of_group,
            coil_orientation=coilor,
            description=fake.text(),
            direction_of_induced_current=doic,
        )

    @staticmethod
    def create_tms_localization_system_file():
        brainareasystem = BrainAreaSystem.objects.create(name="Lobo frontal")
        brainarea = BrainArea.objects.create(
            name="Lobo frontal", brain_area_system=brainareasystem
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            bin_file = ObjectsFactory.create_binary_file(tmpdirname)

            tmslsf = TMSLocalizationSystem.objects.create(
                name="TMS name", brain_area=brainarea
            )
            with File(open(bin_file.name, "rb")) as f:
                tmslsf.tms_localization_system_image.save("file.bin", f)
            tmslsf.save()

        return tmslsf

    @staticmethod
    def create_emg_data_collection_file(emg_data):
        with tempfile.TemporaryDirectory() as tmpdirname:
            bin_file = ObjectsFactory.create_binary_file(tmpdirname)
            emgf = EMGFile.objects.create(emg_data=emg_data)
            with File(open(bin_file.name, "rb")) as f:
                emgf.file.save("file.bin", f)
            emgf.save()

        return emgf

    @staticmethod
    def create_digital_game_phase_data(data_conf_tree, subj_of_group):
        fake = Factory.create()

        file_format = ObjectsFactory.create_file_format()
        return DigitalGamePhaseData.objects.create(
            description=fake.text(),
            file_format=file_format,
            file_format_description=fake.text(),
            data_configuration_tree=data_conf_tree,
            subject_of_group=subj_of_group,
        )

    @staticmethod
    def create_digital_game_phase_file(dgp_data, filename=None):
        with tempfile.TemporaryDirectory() as tmpdirname:
            bin_file = ObjectsFactory.create_binary_file(tmpdirname)

            dgpf = DigitalGamePhaseFile.objects.create(digital_game_phase_data=dgp_data)
            with File(open(bin_file.name, "rb")) as f:
                dgpf.file.save(filename if filename else "file.bin", f)
            dgpf.save()

        return dgpf

    @staticmethod
    def create_additional_data_data(data_conf_tree, subj_of_group):
        fake = Factory.create()

        file_format = ObjectsFactory.create_file_format()
        return AdditionalData.objects.create(
            description=fake.text(),
            file_format=file_format,
            file_format_description=fake.text(),
            data_configuration_tree=data_conf_tree,
            subject_of_group=subj_of_group,
        )

    @staticmethod
    def create_additional_data_file(ad_data):
        with tempfile.TemporaryDirectory() as tmpdirname:
            bin_file = ObjectsFactory.create_binary_file(tmpdirname)
            adf = AdditionalDataFile.objects.create(additional_data=ad_data)
            with File(open(bin_file.name, "rb")) as f:
                adf.file.save("file.bin", f)
            adf.save()

        return adf

    @staticmethod
    def create_stimulus_type():
        fake = Factory.create()
        return StimulusType.objects.create(name=fake.word())

    @staticmethod
    def create_stimulus_step(stimulus_type, mediafile):
        return Stimulus.objects.create(
            stimulus_type=stimulus_type, media_file=mediafile
        )

    @staticmethod
    def create_hotspot_data_collection_file(hotspot):
        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(os.path.join(tmpdirname, "file.bin"), "wb") as bin_file:
                bin_file.write(b"carambola")

            with File(open(bin_file.name, "rb")) as f:
                hotspot.hot_spot_map.save("file.bin", f)
            hotspot.save()

        return hotspot

    @staticmethod
    def create_complete_set_of_components(experiment, rootcomponent):
        component1 = ObjectsFactory.create_component(experiment, Component.INSTRUCTION)
        ObjectsFactory.create_component_configuration(rootcomponent, component1)
        component2 = ObjectsFactory.create_component(experiment, Component.PAUSE)
        ObjectsFactory.create_component_configuration(rootcomponent, component2)
        survey = create_survey(123458)
        component3 = ObjectsFactory.create_component(
            experiment, Component.QUESTIONNAIRE, kwargs={"survey": survey}
        )
        ObjectsFactory.create_component_configuration(rootcomponent, component3)
        stimulus_type = ObjectsFactory.create_stimulus_type()
        component4 = ObjectsFactory.create_component(
            experiment, Component.STIMULUS, kwargs={"stimulus_type": stimulus_type}
        )
        ObjectsFactory.create_component_configuration(rootcomponent, component4)
        component5 = ObjectsFactory.create_component(experiment, Component.TASK)
        ObjectsFactory.create_component_configuration(rootcomponent, component5)
        component6 = ObjectsFactory.create_component(
            experiment, Component.TASK_EXPERIMENT
        )
        ObjectsFactory.create_component_configuration(rootcomponent, component6)
        eeg_setting = ObjectsFactory.create_eeg_setting(experiment)
        component9 = ObjectsFactory.create_component(
            experiment, Component.EEG, kwargs={"eeg_set": eeg_setting}
        )
        ObjectsFactory.create_component_configuration(rootcomponent, component9)
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        acquisition_software = ObjectsFactory.create_software_version(software)
        emg_setting = ObjectsFactory.create_emg_setting(
            experiment, acquisition_software
        )
        component10 = ObjectsFactory.create_component(
            experiment, Component.EMG, kwargs={"emg_set": emg_setting}
        )
        ObjectsFactory.create_component_configuration(rootcomponent, component10)
        tms_setting = ObjectsFactory.create_tms_setting(experiment)
        component11 = ObjectsFactory.create_component(
            experiment, Component.TMS, kwargs={"tms_set": tms_setting}
        )
        ObjectsFactory.create_component_configuration(rootcomponent, component11)
        context_tree = ObjectsFactory.create_context_tree(experiment)
        component12 = ObjectsFactory.create_component(
            experiment,
            Component.DIGITAL_GAME_PHASE,
            kwargs={
                "software_version": acquisition_software,
                "context_tree": context_tree,
            },
        )
        ObjectsFactory.create_component_configuration(rootcomponent, component12)
        information_type = ObjectsFactory.create_information_type()
        component13 = ObjectsFactory.create_component(
            experiment,
            Component.GENERIC_DATA_COLLECTION,
            kwargs={"it": information_type},
        )
        ObjectsFactory.create_component_configuration(rootcomponent, component13)

    @staticmethod
    def create_exam_file(patient, user):
        fake = Factory.create()

        cid10 = ClassificationOfDiseases.objects.create(
            # Limit fake.word because len(fake.word) can be more than 10
            code=fake.word(["A021", "B050", "C111"]),
            description=fake.text(),
            abbreviated_description=fake.word(),
        )
        medical_record = MedicalRecordData.objects.create(
            patient=patient, record_responsible=user
        )
        diagnosis = Diagnosis.objects.create(
            medical_record_data=medical_record, classification_of_diseases=cid10
        )
        complementary_exam = ComplementaryExam.objects.create(
            diagnosis=diagnosis, date=datetime.date.today(), description=fake.text()
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            bin_file = ObjectsFactory.create_binary_file(tmpdirname)

            exam_file = ExamFile.objects.create(exam=complementary_exam)
            with File(open(bin_file.name, "rb")) as f:
                exam_file.content.save("file.bin", f)
            exam_file.save()
        return exam_file
