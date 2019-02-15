import json
import shutil
import sys
import tempfile

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.encoding import smart_str
from django.utils.html import strip_tags

from custom_user.tests_helper import create_user
from experiment.import_export import ExportExperiment
from experiment.models import Keyword, GoalkeeperGameConfig, \
    Component, GoalkeeperGame, GoalkeeperPhase, GoalkeeperGameResults, \
    FileFormat, ExperimentResearcher, Experiment, ResearchProject, \
    TMS, ComponentConfiguration, Questionnaire, Subject, SubjectOfGroup, \
    DataConfigurationTree, Manufacturer, Material, TMSDevice, TMSDeviceSetting, \
    CoilModel, CoilShape, TMSSetting, Equipment, EEGSetting, EEGElectrodeLayoutSetting, \
    EEGElectrodeNetSystem, EEGElectrodeNet, ElectrodeModel, ElectrodeConfiguration, \
    EEGElectrodeLocalizationSystem, EEGElectrodePositionSetting, EEGElectrodePosition, \
    EEGFilterSetting, FilterType, Amplifier, EEGAmplifierSetting, EEGSolutionSetting, EEGSolution, \
    EMGSetting, EMGElectrodeSetting, EMGADConverterSetting, ADConverter, EMGDigitalFilterSetting, \
    SoftwareVersion, Software, AmplifierDetectionType, TetheringSystem, Muscle, MuscleSide, \
    MuscleSubdivision, EMGElectrodePlacementSetting, StandardizationSystem, \
    EMGIntramuscularPlacement, EMGNeedlePlacement, EMGSurfacePlacement, EMGAnalogFilterSetting, \
    EMGAmplifierSetting, EMGPreamplifierSetting, EMGPreamplifierFilterSetting, EEG, EMG, Instruction, \
    StimulusType, Stimulus, DigitalGamePhase, ContextTree, InformationType

from experiment.models import Group as ExperimentGroup
from configuration.models import LocalInstitution
from custom_user.models import Institution
from experiment.tests.tests_original import ObjectsFactory
from patient.models import Patient, Telephone, SocialDemographicData, AmountCigarettes, AlcoholFrequency, \
    AlcoholPeriod, SocialHistoryData, MedicalRecordData, Diagnosis

from patient.tests import UtilTests
from survey.models import Survey
from survey.tests.tests_helper import create_survey

USER_USERNAME = 'myadmin'
USER_PWD = 'mypassword'
USER_NEW = 'user_new'


class ScheduleOfSendingListViewTest(TestCase):

    def setUp(self):
        logged, self.user, self.factory = ObjectsFactory.system_authentication(
            self)
        self.assertEqual(logged, True)

    def test_Schedule_of_Sending_List_is_valid(self):
        # Check if list of research projects is empty before inserting any.
        response = self.client.get(reverse('research_project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['research_projects']), 0)

        ObjectsFactory.create_research_project()

        # Check if list of research projects returns one item after inserting one.
        response = self.client.get(reverse('research_project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['research_projects']), 1)

        can_send_to_portal = False
        if settings.PORTAL_API['URL'] and settings.SHOW_SEND_TO_PORTAL_BUTTON:
            can_send_to_portal = True

        # Check if list of research projects returns one item after inserting one.
        response = self.client.get(reverse('schedule_of_sending_list'))
        self.assertEqual(response.status_code, 200)


class PermissionsresearchprojectupdateViewtest(TestCase):

    def setUp(self):
        exec(open('add_initial_data.py').read())
        self.user = User.objects.create_user(
            username='jose', email='jose@test.com', password='passwd'
        )
        user_profile = self.user.user_profile
        user_profile.login_enabled = True

        user_profile.force_password_change = False
        user_profile.save()

        for group in Group.objects.all():
            group.user_set.add(self.user)

        self.client.login(username=self.user.username, password='passwd')

        self.research_project = ObjectsFactory.create_research_project()
        self.experiment = ObjectsFactory.create_experiment(
            self.research_project)

    def tearDown(self):
        self.client.logout()

    def test_permissions_research_project_update(self):
        response = self.client.get(reverse('research_project_edit',
                                           kwargs={'research_project_id': self.research_project.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertRaises(PermissionDenied)


class ResearchProjectViewTest(TestCase):

    def setUp(self):
        exec(open('add_initial_data.py').read())
        self.user = User.objects.create_user(
            username='jose', email='jose@test.com', password='passwd'
        )
        user_profile = self.user.user_profile
        user_profile.login_enabled = True
        user_profile.force_password_change = False
        user_profile.save()

        for group in Group.objects.all():
            group.user_set.add(self.user)

        self.client.login(username=self.user.username, password='passwd')

        self.research_project = ObjectsFactory.create_research_project()
        self.experiment = ObjectsFactory.create_experiment(
            self.research_project)

    def tearDown(self):
        self.client.logout()

    def test_research_project_view_remove_try(self):
        # Insert keyword
        self.assertEqual(Keyword.objects.all().count(), 0)
        self.assertEqual(self.research_project.keywords.count(), 0)
        response = self.client.get(reverse('keyword_new', args=(
            self.research_project.pk, "first_test_keyword")), follow=True)
        # self.assertEqual(response.status_code, 403)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 1)
        self.assertEqual(self.research_project.keywords.count(), 1)

        # Add keyword
        keyword = Keyword.objects.create(name="second_test_keyword")
        keyword.save()
        self.assertEqual(Keyword.objects.all().count(), 2)
        self.assertEqual(self.research_project.keywords.count(), 1)
        response = self.client.get(reverse('keyword_add', args=(
            self.research_project.pk, keyword.id)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Keyword.objects.all().count(), 2)
        self.assertEqual(self.research_project.keywords.count(), 2)

        response = self.client.post(reverse('research_project_view',
                                            kwargs={'research_project_id': self.research_project.pk}),
                                    data={'action': 'remove'})
        self.assertEqual(response.status_code, 302)

    # def test_research_project_view_remove_except(self):
    #
    #     self.research_project_1 = ObjectsFactory.create_research_project()
    #     self.experiment1 = ObjectsFactory.create_experiment(
    #         self.research_project_1)
    #
    #     # Insert keyword in research_project
    #     self.assertEqual(Keyword.objects.all().count(), 0)
    #     self.assertEqual(self.research_project.keywords.count(), 0)
    #     response = self.client.get(reverse('keyword_new', args=(
    #         self.research_project.pk, "first_test_keyword")), follow=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(Keyword.objects.all().count(), 1)
    #     self.assertEqual(self.research_project.keywords.count(), 1)
    #
    #     # Insert then same keyword in research_project_1
    #     # self.assertEqual(Keyword.objects.all().count(), 0)
    #     self.assertEqual(self.research_project_1.keywords.count(), 0)
    #     response = self.client.get(reverse('keyword_new', args=(
    #         self.research_project_1.pk, "first_test_keyword")), follow=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(Keyword.objects.all().count(), 2)
    #     self.assertEqual(self.research_project_1.keywords.count(), 1)
    #
    #     response = self.client.post(reverse('research_project_view',
    #                kwargs={'research_project_id': self.research_project.pk}),
    #                data={'action': 'remove'})
    #
    #     self.assertEqual(response.status_code, 403)


class LoadGameKeeperTest(TestCase):
    def setUp(self):
        exec(open('add_initial_data.py').read())
        self.user = User.objects.create_user(
            username='jose', email='jose@test.com', password='passwd'
        )

        # create experiment/experimental protocol/group
        self.experiment = ObjectsFactory.create_experiment(
            ObjectsFactory.create_research_project(self.user)
        )
        self.root_component = ObjectsFactory.create_block(self.experiment)
        self.group = ObjectsFactory.create_group(
            self.experiment, self.root_component
        )

        # create patient/subject/subject_of_group
        self.patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(self.patient)
        self.subject_of_group = \
            ObjectsFactory.create_subject_of_group(self.group, subject)

        user_profile = self.user.user_profile
        user_profile.login_enabled = True
        user_profile.force_password_change = False
        user_profile.save()

        for group in Group.objects.all():
            group.user_set.add(self.user)

        self.client.login(username=self.user.username, password='passwd')
        self.research_project = ObjectsFactory.create_research_project()
        self.experiment = ObjectsFactory.create_experiment(self.research_project)

        self.idconfig = 0
        self.idgameresult = 0

        GoalkeeperGameConfig.objects.filter(idconfig=self.idconfig).using("goalkeeper").delete()
        GoalkeeperGameConfig.objects.filter(idconfig=self.idconfig).using("goalkeeper").delete()

        self.goalkeepergameconfig = GoalkeeperGameConfig.objects.using("goalkeeper").create(
            idconfig=self.idconfig,
            institution='TESTINST',
            groupcode='TESTGROUP',
            soccerteam='TESTTEAM',
            game='TE',
            phase=0,
            playeralias=self.subject_of_group.subject.patient.code,
            sequexecuted='000100100100',
            gamedata='190101',
            gametime='010101',
            idresult=self.idgameresult,
            playid='TESTEPLAYID',
            sessiontime=0.1,
            relaxtime=0.1,
            playermachine='TESTPLAYERMACHINE',
            gamerandom=100,
            limitplays=1,
            totalcorrect=0,
            successrate=0,
            gamemode=0,
            status=0,
            playstorelax=0,
            scoreboard=True,
            finalscoreboard=0,
            animationtype=0,
            minhits=1
        )

        self.goalkeepergameresults = GoalkeeperGameResults.objects.using("goalkeeper").create(
            idgameresult=self.idgameresult,
            idconfig=self.idconfig,
            move=0,
            timeuntilanykey=0.1,
            timeuntilshowagain=0.1,
            waitedresult=1,
            ehrandom='n',
            optionchoosen=0,
            movementtime=0.1,
            decisiontime=0.1
        )

        self.group.code = GoalkeeperGameConfig.objects.using("goalkeeper").first().groupcode
        self.group.save()

    def test_load_goalkeeper_data(self):
        self.assertEqual(GoalkeeperGameConfig.objects.using("goalkeeper").count(), 1)

        # create digital game phase (dgp) component
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        context_tree = ObjectsFactory.create_context_tree(self.experiment)

        dgp = ObjectsFactory.create_component(
            self.experiment, Component.DIGITAL_GAME_PHASE,
            kwargs={'software_version': software_version, 'context_tree': context_tree}
        )

        # include dgp component in experimental protocol
        component_config = ObjectsFactory.create_component_configuration(
            self.root_component, dgp
        )

        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # Create a instance of institution and local institution
        institution = Institution.objects.create(
            name=self.goalkeepergameconfig.institution,
            acronym='TESTINST',
            country='TESTCOUNTRY',
        )

        LocalInstitution.objects.create(
            code='TESTINST',
            institution=institution)

        # Create a Goalkeeper game
        goalkeepergame = GoalkeeperGame.objects.create(
            code=self.goalkeepergameconfig.game,
            name='TESTGOALKEEPERGAME')

        # Create a phase of the Goalkeeper game
        GoalkeeperPhase.objects.create(
            game=goalkeepergame,
            phase=self.goalkeepergameconfig.phase,
            pk=dct.code
        )

        # Create fileformat in db
        FileFormat.objects.create(nes_code='other')

        response = self.client.post(reverse("load_group_goalkeeper_game_data", args=(self.group.id,)))

        self.assertEqual(response.status_code, 302)

        Institution.objects.filter(name='TESTINSTITUTION').delete()
        LocalInstitution.objects.filter(code='TESTLOCALINST').delete()
        GoalkeeperGame.objects.filter(code=self.goalkeepergameconfig.game).delete()
        GoalkeeperPhase.objects.filter(phase=0).delete()

    def tearDown(self):
        GoalkeeperGameConfig.objects.filter(idconfig=self.idconfig).using("goalkeeper").delete()
        GoalkeeperGameResults.objects.filter(idgameresult=self.idgameresult).using("goalkeeper").delete()


class CollaboratorTest(TestCase):
    def setUp(self):

        exec(open('add_initial_data.py').read())
        self.user = User.objects.create_user(
            username='jose', email='jose@test.com', password='passwd'
        )
        user_profile = self.user.user_profile
        user_profile.login_enabled = True

        user_profile.force_password_change = False
        user_profile.save()

        for group in Group.objects.all():
            group.user_set.add(self.user)

        self.client.login(username=self.user.username, password='passwd')

        self.research_project = ObjectsFactory.create_research_project()

        self.experiment = ObjectsFactory.create_experiment(self.research_project)

        self.researcher = ObjectsFactory.create_experiment_researcher(self.experiment)

        # create experiment/experimental protocol/group
        self.experiment = ObjectsFactory.create_experiment(
            ObjectsFactory.create_research_project(self.user)
        )
        self.root_component = ObjectsFactory.create_block(self.experiment)
        self.group = ObjectsFactory.create_group(
            self.experiment, self.root_component
        )

        # create patient/subject/subject_of_group
        self.patient = UtilTests().create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(self.patient)
        self.subject_of_group = \
            ObjectsFactory.create_subject_of_group(self.group, subject)

    def tearDown(self):
        self.client.logout()

    def test_collaborator_create(self):

        # Insert collaborator
        response = self.client.get(reverse('collaborator_new', kwargs={'experiment_id': self.experiment.id}))
        self.assertEqual(response.status_code, 200)

        collaborators_added = ExperimentResearcher.objects.filter(experiment_id=self.experiment.id)
        collaborators_added_ids = collaborators_added.values_list('researcher_id', flat=True)

        collaborators = User.objects.filter(is_active=True).exclude(pk__in=collaborators_added_ids).order_by(
            'first_name',
            'last_name')
        # collaborators_selected = request.POST.getlist('collaborators')
        if collaborators:
            collaborators_selected = collaborators.first()
            response = self.client.post(
                reverse('collaborator_new', kwargs={'experiment_id': self.experiment.id}),
                data={'collaborators': collaborators_selected.id, 'action': 'save'}
            )
            self.assertEqual(response.status_code, 302)


class ExportExperimentTest(TestCase):

    def setUp(self):
        # create the groups of users and their permissions
        exec(open('add_initial_data.py').read())

        user, passwd = create_user(Group.objects.all())
        self.research_project = ObjectsFactory.create_research_project(owner=user)
        self.experiment = ObjectsFactory.create_experiment(self.research_project)
        self.group = ObjectsFactory.create_group(self.experiment)

        self.client.login(username=user.username, password=passwd)

    def tearDown(self):
        self.client.logout()

    def test_GET_experiment_export_returns_json_file(self):
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            response.get('Content-Disposition'),
            'attachment; filename=%s' % smart_str('experiment.json')
        )

    def test_GET_experiment_export_returns_json_file_wo_user_object(self):
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        data = json.loads(response.content.decode('utf-8'))
        self.assertIsNone(next((item for item in data if item['model'] == 'auth.user'), None))


class ImportExperimentTest(TestCase):

    def setUp(self):
        # create the groups of users and their permissions
        exec(open('add_initial_data.py').read())

        self.user, passwd = create_user(Group.objects.all())
        self.user_importer, passwd = create_user(Group.objects.all())
        self.client.login(username=self.user_importer.username, password=passwd)

        self.stdout_bk, sys.stdout = sys.stdout, open('/dev/null', 'w+')

    def tearDown(self):
        self.client.logout()
        sys.stdout.close()
        sys.stdout = self.stdout_bk

    def _assert_new_objects(self, old_objects_count):
        self.assertEqual(ResearchProject.objects.count(), old_objects_count['research_project'] + 1)

        self.assertEqual(Experiment.objects.count(), old_objects_count['experiment'] + 1)
        self.assertEqual(Experiment.objects.last().research_project.id, ResearchProject.objects.last().id)

        self.assertEqual(
            ExperimentGroup.objects.count(),
            old_objects_count['group']['count'] + len(old_objects_count['group']['objs']))
        for group in old_objects_count['group']['objs']:
            self.assertEqual(Experiment.objects.last().id, group.experiment.id)

    def _assert_steps_imported(self, response):
        self.assertContains(response, '2 passos de <em>Conjunto de passos</em> importados')
        self.assertContains(response, '1 passo de <em>Instrução</em> importado')
        self.assertContains(response, '1 passo de <em>Pausa</em> importado')
        self.assertContains(response, '1 passo de <em>Questionário</em> importado')
        self.assertContains(response, '1 passo de <em>Estímulo</em> importado')
        self.assertContains(response, '1 passo de <em>Tarefa para o participante</em> importado')
        self.assertContains(response, '2 passos de <em>Tarefa para o experimentador</em> importados')
        self.assertContains(response, '1 passo de <em>EEG</em> importado')
        self.assertContains(response, '1 passo de <em>EMG</em> importado')
        self.assertContains(response, '1 passo de <em>TMS</em> importado')
        self.assertContains(response, '1 passo de <em>Fase de jogo do goleiro</em> importado')
        self.assertContains(response, '1 passo de <em>Coleta genérica de dados</em> importado')

    def _create_minimum_objects_to_test_components(self):
        self.research_project = ObjectsFactory.create_research_project(owner=self.user)
        self.experiment = ObjectsFactory.create_experiment(self.research_project)
        self.rootcomponent = ObjectsFactory.create_component(self.experiment, 'block', 'root component')

    def _create_experiment_with_digital_game_phase(self):
        self._create_minimum_objects_to_test_components()

        context_tree = ObjectsFactory.create_context_tree(self.experiment)

        manufacturer = Manufacturer.objects.create(name='TEST_MANUFACTURER')
        software = Software.objects.create(name='TEST_SOFTWARE', manufacturer=manufacturer)
        software_version = SoftwareVersion.objects.create(name='TEST_SOFTWARE_VERSION', software=software)

        digital_game_phase = ObjectsFactory.create_component(self.experiment, 'digital_game_phase',
                                                             kwargs={'context_tree': context_tree,
                                                                     'software_version': software_version})

        ObjectsFactory.create_component_configuration(self.rootcomponent, digital_game_phase)

        return self.experiment

    def _create_experiment_with_tms_setting(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        tms_setting = TMSSetting.objects.create(experiment=experiment,
                                                name='TMS-Setting name',
                                                description='TMS-Setting description')
        manufacturer = Manufacturer.objects.create(name='TEST_MANUFACTURER')
        tms_device = TMSDevice.objects.create(identification='TEST_DEVICE_IDENTIFICATION',
                                              manufacturer=manufacturer)
        material = Material.objects.create(name='TEST_MATERIAL', description='TEST_DESCRIPTION_MATERIAL')
        coil_shape = CoilShape.objects.create(name='TEST_COIL_SHAPE')
        coil_model = CoilModel.objects.create(name='TEST_COIL_MODEL', coil_shape=coil_shape, material=material)

        tms_device_setting = TMSDeviceSetting.objects.create(tms_setting=tms_setting,
                                                             tms_device=tms_device,
                                                             coil_model=coil_model)

        return experiment

    def _create_experiment_with_eeg_setting(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        eeg_setting = EEGSetting.objects.create(experiment=experiment,
                                                name='EEG-Setting name',
                                                description='EEG-Setting description')
        manufacturer = Manufacturer.objects.create(name='TEST_MANUFACTURER')
        material = Material.objects.create(name='TEST_MATERIAL', description='TEST_DESCRIPTION_MATERIAL')
        electrode_config = ElectrodeConfiguration.objects.create(name='Electrode config name')
        electrode_loc_sys = EEGElectrodeLocalizationSystem.objects.create(name='TEST_EEGELocS')

        electrode_model = ElectrodeModel.objects.create(name='TEST_ELECTRODE_MODEL',
                                                        electrode_configuration=electrode_config,
                                                        material=material)
        electrode_net = EEGElectrodeNet.objects.create(identification='TEST_ELECTRODE_NET',
                                                       electrode_model_default=electrode_model,
                                                       manufacturer=manufacturer,
                                                       equipment_type='eeg_electrode_net')
        electrode_net_sys = EEGElectrodeNetSystem.objects.create(eeg_electrode_net=electrode_net,
                                                                 eeg_electrode_localization_system=electrode_loc_sys)
        electrode_pos = EEGElectrodePosition.objects.create(name='TEST_ELECTRODE_POSITION',
                                                            eeg_electrode_localization_system=electrode_loc_sys)
        electrode_layout_sys = EEGElectrodeLayoutSetting.objects.create(eeg_electrode_net_system=electrode_net_sys,
                                                                        eeg_setting=eeg_setting)
        electrode_position_system = EEGElectrodePositionSetting.objects.create(
            eeg_electrode_layout_setting=electrode_layout_sys,
            eeg_electrode_position=electrode_pos,
            electrode_model=electrode_model,
            used=True,
            channel_index=1
        )

        filter_type = FilterType.objects.create(name='TEST_FILTER_TYPE')
        eeg_filter_setting = EEGFilterSetting.objects.create(eeg_setting=eeg_setting,
                                                             eeg_filter_type=filter_type)
        amplifier_detection_type = AmplifierDetectionType.objects.create(name='TEST_AMPLIFIER_DETECTION_TYPE')
        tethering_system = TetheringSystem.objects.create(name='TEST_AMPLIFIER_DETECTION_TYPE')
        amplifier = Amplifier.objects.create(identification='AMPLIFIER',
                                             amplifier_detection_type=amplifier_detection_type,
                                             tethering_system=tethering_system,
                                             manufacturer=manufacturer,
                                             equipment_type='amplifier')
        eeg_amplifier_setting = EEGAmplifierSetting.objects.create(eeg_amplifier=amplifier,
                                                                   eeg_setting=eeg_setting)

        eeg_solution = EEGSolution.objects.create(name='TEST_EEG_SOLUTION',
                                                  manufacturer=manufacturer)
        eeg_solution_setting = EEGSolutionSetting.objects.create(eeg_setting=eeg_setting,
                                                                 eeg_solution=eeg_solution)

        return experiment

    def _create_experiment_with_emg_setting(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        # EMG Setting
        manufacturer = Manufacturer.objects.create(name='TEST_MANUFACTURER')
        software = Software.objects.create(name='TEST_SOFTWARE',
                                           manufacturer=manufacturer)
        software_version = SoftwareVersion.objects.create(name='TEST_SOFTWARE_VERSION',
                                                          software=software)
        emg_setting = EMGSetting.objects.create(experiment=experiment,
                                                name='EMG-Setting name',
                                                description='EMG-Setting description',
                                                acquisition_software_version=software_version)

        # AD converter
        ad_converter = ADConverter.objects.create(identification='TEST_AD_CONVERTER',
                                                  manufacturer=manufacturer,
                                                  equipment_type='ad_converter')
        emg_ad_converter_setting = EMGADConverterSetting.objects.create(ad_converter=ad_converter,
                                                                        emg_setting=emg_setting)

        # Filter type
        filter_type = FilterType.objects.create(name='TEST_FILTER_TYPE')
        emg_digital_filter_setting = EMGDigitalFilterSetting.objects.create(emg_setting=emg_setting,
                                                                            filter_type=filter_type)

        # Electrodes
        material = Material.objects.create(name='TEST_MATERIAL', description='TEST_DESCRIPTION_MATERIAL')
        electrode_config = ElectrodeConfiguration.objects.create(name='Electrode config name')
        electrode_model = ElectrodeModel.objects.create(name='TEST_ELECTRODE_MODEL',
                                                        electrode_configuration=electrode_config,
                                                        material=material)
        emg_electrode_setting_surface = EMGElectrodeSetting.objects.create(emg_setting=emg_setting,
                                                                           electrode=electrode_model)

        emg_electrode_setting_intramuscular = EMGElectrodeSetting.objects.create(emg_setting=emg_setting,
                                                                                 electrode=electrode_model)
        emg_electrode_setting_needle = EMGElectrodeSetting.objects.create(emg_setting=emg_setting,
                                                                          electrode=electrode_model)

        # Muscle
        muscle = Muscle.objects.create(name='TEST_MUSCLE')
        muscle_side = MuscleSide.objects.create(name='TEST_MUSCLE_SIDE',
                                                muscle=muscle)
        muscle_subdivision = MuscleSubdivision.objects.create(name='TEST_MUSCLE_SUBDIVISION',
                                                              muscle=muscle)
        standardization_system = StandardizationSystem.objects.create(name='TEST_STANDARDIZATION_SYSTEM')

        emg_surface_placement = EMGSurfacePlacement.objects.create(standardization_system=standardization_system,
                                                                   muscle_subdivision=muscle_subdivision,
                                                                   placement_type='surface')
        emg_intramuscular_placement = EMGIntramuscularPlacement.objects.create(
            standardization_system=standardization_system,
            muscle_subdivision=muscle_subdivision,
            placement_type='intramuscular')
        emg_needle_placement = EMGNeedlePlacement.objects.create(standardization_system=standardization_system,
                                                                 muscle_subdivision=muscle_subdivision,
                                                                 placement_type='needle')
        emg_electrode_placement_setting_surface = EMGElectrodePlacementSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_surface,
            emg_electrode_placement=emg_surface_placement.emgelectrodeplacement_ptr,
            muscle_side=muscle_side)
        emg_electrode_placement_setting_intramuscular = EMGElectrodePlacementSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_intramuscular,
            emg_electrode_placement=emg_intramuscular_placement.emgelectrodeplacement_ptr,
            muscle_side=muscle_side)
        emg_electrode_placement_setting_needle = \
            EMGElectrodePlacementSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_needle,
            emg_electrode_placement=emg_needle_placement.emgelectrodeplacement_ptr,
            muscle_side=muscle_side)

        # Amplifier
        amplifier_detection_type = AmplifierDetectionType.objects.create(name='TEST_AMPLIFIER_DETECTION_TYPE')
        tethering_system = TetheringSystem.objects.create(name='TEST_THETHERING_SYSTEM')
        amplifier = Amplifier.objects.create(identification='TEST_AMPLIFIER',
                                             amplifier_detection_type=amplifier_detection_type,
                                             tethering_system=tethering_system,
                                             manufacturer=manufacturer,
                                             equipment_type='amplifier')

        emg_amplifier_setting_surface = EMGAmplifierSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_surface,
            amplifier=amplifier)
        emg_amplifier_setting_intramuscular = EMGAmplifierSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_intramuscular,
            amplifier=amplifier)
        emg_amplifier_setting_needle = EMGAmplifierSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_needle,
            amplifier=amplifier)

        EMGAnalogFilterSetting.objects.create(
            emg_electrode_setting=emg_amplifier_setting_surface)
        EMGAnalogFilterSetting.objects.create(
            emg_electrode_setting=emg_amplifier_setting_intramuscular)
        EMGAnalogFilterSetting.objects.create(
            emg_electrode_setting=emg_amplifier_setting_needle)

        emg_pre_amplifier_setting_surface = EMGPreamplifierSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_surface,
            amplifier=amplifier)
        emg_pre_amplifier_setting_intramuscular = EMGPreamplifierSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_intramuscular,
            amplifier=amplifier)
        emg_pre_amplifier_setting_needle = EMGPreamplifierSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_needle,
            amplifier=amplifier)

        EMGPreamplifierFilterSetting.objects.create(
            emg_preamplifier_filter_setting=emg_pre_amplifier_setting_surface)
        EMGPreamplifierFilterSetting.objects.create(
            emg_preamplifier_filter_setting=emg_pre_amplifier_setting_intramuscular)
        EMGPreamplifierFilterSetting.objects.create(
            emg_preamplifier_filter_setting=emg_pre_amplifier_setting_needle)

        return experiment

    def _create_minimum_objects_to_test_questionnaire(self, survey_id=212121):
        ObjectsFactory.create_group(self.experiment, self.rootcomponent)
        survey = create_survey(survey_id)
        questionnaire = ObjectsFactory.create_component(self.experiment, Component.QUESTIONNAIRE,
                                                        kwargs={'survey': survey})
        ObjectsFactory.create_component_configuration(self.rootcomponent, questionnaire)

    def _test_creation_and_linking_between_two_models(self, model_1_name, model_2_name, linking_field,
                                                      _experiment, filter_model_1={},
                                                      flag1=False, flag2=False):
        """
        This test is a general test for testing the sucessfull importation of two linked models
        :param model_1_name: Name of the model inherited by the second model; The one that is being pointed at.
        :param model_2_name: Name of the model that inherits the first model; The one that is pointing to.
        :param linking_field: Name of the field that links both models
        """
        model_1 = apps.get_model(model_1_name)
        model_2 = apps.get_model(model_2_name)

        experiment = _experiment
        export = ExportExperiment(experiment)
        export.export_all()

        file_path = export.get_file_path()

        old_model_1_objects_ids = list(model_1.objects.filter(**filter_model_1).values_list('pk', flat=True))
        old_model_2_objects_ids = list(model_2.objects.values_list('pk', flat=True))

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_model_1_objects = model_1.objects.filter(**filter_model_1).exclude(pk__in=old_model_1_objects_ids)
        new_model_2_objects = model_2.objects.exclude(pk__in=old_model_2_objects_ids)
        if not flag2:  # TODO: refactor to not use flag2
            self.assertNotEqual(0, new_model_1_objects.count())
            self.assertNotEqual(0, new_model_2_objects.count())

        self.assertEqual(model_1.objects.filter(**filter_model_1).count(),
                         len(old_model_1_objects_ids) + new_model_1_objects.count()
                         )
        self.assertEqual(model_2.objects.count(),
                         len(old_model_2_objects_ids) + new_model_2_objects.count()
                         )

        if not flag1: # TODO: refactor to not use flag1
            for item in new_model_1_objects:
                dinamic_filter = {linking_field: item.pk}
                self.assertTrue(new_model_2_objects.filter(**dinamic_filter).exists())
        else:
            new_model_1_ids = new_model_1_objects.values_list('id', flat=True)
            for item in new_model_2_objects:
                self.assertTrue(getattr(item, linking_field).id in new_model_1_ids)

    def _test_creation_of_objects_that_should_not_be_duplicated(self, _experiment, model_name):
        model_ = apps.get_model(model_name)

        experiment = _experiment
        export = ExportExperiment(experiment)
        export.export_all()

        file_path = export.get_file_path()

        # dictionary to test against new objects that might be created bellow
        old_model_ids = list(model_.objects.values_list('pk', flat=True))

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_objects = model_.objects.exclude(pk__in=old_model_ids)

        # The number of new objects in this case is zero because we do not duplicate the objects,
        # as they are allegedly from simple models with only name and/or description or other simple fields
        self.assertEqual(len(new_objects), 0)
        self.assertNotEqual(len(old_model_ids), len(new_objects))

    # Research project, Experiment and Group tests
    def test_GET_experiment_import_file_uses_correct_template(self):
        response = self.client.get(reverse('experiment_import'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'experiment/experiment_import.html')

    def test_POST_experiment_import_file_has_not_file_redirects_with_warning_message(self):
        response = self.client.post(reverse('experiment_import'), {'file': ''}, follow=True)
        self.assertRedirects(response, reverse('experiment_import'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Por favor, selecione um arquivo .json')

    def test_POST_experiment_import_file_has_bad_json_file_redirects_with_error_message(self):
        temp_dir = tempfile.mkdtemp()
        dummy_file = ObjectsFactory.create_csv_file(temp_dir, 'experiment.json')

        with open(dummy_file.name, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('experiment_import'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Bad json file. Aborting import experiment.')

        shutil.rmtree(temp_dir)

    def test_import_of_a_new_experiment_into_an_existent_research_project(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        export = ExportExperiment(experiment)
        export.export_all()

    # Testes a serem revisados
    def test_POST_experiment_import_file_creates_new_experiment_and_returns_successful_message(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()

        file_path = export.get_file_path()

        old_objects_count = {
            'research_project': ResearchProject.objects.count(),
            'experiment': Experiment.objects.count(),
        }
        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))
        self.assertEqual(ResearchProject.objects.count(), old_objects_count['research_project'] + 1)
        self.assertEqual(Experiment.objects.count(), old_objects_count['experiment'] + 1)
        self.assertEqual(Experiment.objects.last().research_project.id, ResearchProject.objects.last().id)

    def test_POST_experiment_import_file_creates_new_groups_and_returns_successful_message(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        group1 = ObjectsFactory.create_group(experiment)
        group2 = ObjectsFactory.create_group(experiment)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # dictionary to test against new objects created bellow
        old_groups_count = ExperimentGroup.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))
        new_groups = ExperimentGroup.objects.exclude(id__in=[group1.id, group2.id])
        self.assertEqual(ExperimentGroup.objects.count(), old_groups_count + new_groups.count())
        for group in new_groups:
            self.assertEqual(Experiment.objects.last().id, group.experiment.id)
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_creates_new_components_and_returns_successful_message(self):
        # We create blocks but could create other type of component
        # TODO: Component can be created without type, but NES should only allow
        #  create a component of a determined type
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        component1 = ObjectsFactory.create_block(experiment)
        component2 = ObjectsFactory.create_block(experiment)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        old_components_count = Component.objects.count()
        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))
        new_components = Component.objects.exclude(id__in=[component1.id, component2.id])
        self.assertEqual(Component.objects.count(), old_components_count + new_components.count())
        for component in new_components:
            self.assertEqual(Experiment.objects.last().id, component.experiment.id)
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_group_has_experimental_protocol_returns_successful_message(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        ep1 = ObjectsFactory.create_block(experiment)
        ep2 = ObjectsFactory.create_block(experiment)
        group1 = ObjectsFactory.create_group(experiment)
        group2 = ObjectsFactory.create_group(experiment, ep1)
        group3 = ObjectsFactory.create_group(experiment, ep2)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))
        new_block_components = Component.objects.exclude(id__in=[ep1.id, ep2.id])
        self.assertEqual(2, new_block_components.count())
        new_groups = ExperimentGroup.objects.exclude(id__in=[group1.id, group2.id, group3.id])
        new_groups_with_exp_prot = [group for group in new_groups if group.experimental_protocol is not None]
        for group in new_groups_with_exp_prot:
            self.assertIn(group.experimental_protocol, new_block_components)
        self.assertNotEqual(
            new_groups_with_exp_prot[0].experimental_protocol, new_groups_with_exp_prot[1].experimental_protocol
        )

    def test_POST_experiment_import_file_creates_root_component_plus_instruction_and_returns_successful_message(self):
        self._create_minimum_objects_to_test_components()
        # Create another component, 'instruction', for this test, but every
        # type, apart from specific parameters, all depend on Component,
        # and only this relation needs to be updated
        instruction_component = ObjectsFactory.create_component(self.experiment, 'instruction')
        ObjectsFactory.create_component_configuration(self.rootcomponent, instruction_component)

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        # dictionary to test against new objects created bellow
        components_before_count = Component.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))
        new_components = Component.objects.exclude(id__in=[self.rootcomponent.id, instruction_component.id])
        self.assertEqual(Component.objects.count(), components_before_count + len(new_components))
        for item in new_components:
            self.assertEqual(Experiment.objects.last().id, item.experiment.id)
        new_rootcomponent = new_components.get(component_type='block')
        new_instruction = new_components.get(component_type='instruction')
        # TODO: make assertion to same Instruction id, Component id
        new_component_configuration = ComponentConfiguration.objects.last()
        self.assertEqual(new_component_configuration.component.id, new_instruction.id)
        self.assertEqual(new_component_configuration.parent.id, new_rootcomponent.id)
        self.assertEqual(new_instruction.experiment.id, Experiment.objects.last().id)

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    # Questionnaire tests
    def test_POST_experiment_import_file_creates_questionnaire_component_returns_successful_message(self):
        self._create_minimum_objects_to_test_components()
        self._create_minimum_objects_to_test_questionnaire()

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        survey_before_count = Survey.objects.count()
        questionnaire_before_count = Questionnaire.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))
        self.assertEqual(Survey.objects.count(), survey_before_count + 1)
        self.assertEqual(Questionnaire.objects.count(), questionnaire_before_count + 1)
        self.assertEqual(Questionnaire.objects.last().survey.id, Survey.objects.last().id)
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_creates_random_code_in_surveys(self):
        self._create_minimum_objects_to_test_components()
        self._create_minimum_objects_to_test_questionnaire()

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        new_survey = Survey.objects.last()
        self.assertTrue(1 <= int(new_survey.code.split('Q')[1]) <= 100000)

    def test_POST_experiment_import_file_creates_dummy_reference_to_limesurvey_questionnaire(self):
        self._create_minimum_objects_to_test_components()
        self._create_minimum_objects_to_test_questionnaire()
        self._create_minimum_objects_to_test_questionnaire(survey_id=121212)

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        new_survey1 = Survey.objects.all().order_by('-id')[1]
        new_survey2 = Survey.objects.all().order_by('-id')[0]
        self.assertEqual(-100, new_survey1.lime_survey_id)
        self.assertEqual(-101, new_survey2.lime_survey_id)

    def test_POST_experiment_import_file_creates_root_component_plus_tms_and_returns_successful_message(self):
        self._create_minimum_objects_to_test_components()
        tms_setting = ObjectsFactory.create_tms_setting(self.experiment)
        tms_component = ObjectsFactory.create_component(self.experiment, 'tms', kwargs={'tms_set': tms_setting})
        ObjectsFactory.create_component_configuration(self.rootcomponent, tms_component)

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        # dictionary to test against new objects created bellow
        components_before_count = Component.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_components = Component.objects.exclude(id__in=[self.rootcomponent.id, tms_component.id])
        self.assertEqual(Component.objects.count(), components_before_count + len(new_components))
        for item in new_components:
            self.assertEqual(Experiment.objects.last().id, item.experiment.id)
        new_rootcomponent = new_components.get(component_type='block')
        new_component = new_components.get(component_type='tms')
        new_tms = TMS.objects.last()
        new_experiment = Experiment.objects.last()
        self.assertEqual(new_component.experiment.id, new_experiment.id)
        new_component_configuration = ComponentConfiguration.objects.last()
        self.assertEqual(new_component_configuration.component.id, new_component.id)
        self.assertEqual(new_component_configuration.parent.id, new_rootcomponent.id)
        self.assertEqual(new_component.id, new_tms.id)
        self.assertEqual(2, TMSSetting.objects.count())
        tms_setting = TMSSetting.objects.last()
        self.assertEqual(new_tms.tms_setting.id, tms_setting.id)
        self.assertEqual(tms_setting.experiment.id, new_experiment.id)

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_creates_root_component_plus_eeg_and_returns_successful_message(self):
        self._create_minimum_objects_to_test_components()
        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)
        eeg_component = ObjectsFactory.create_component(self.experiment, 'eeg', kwargs={'eeg_set': eeg_setting})
        ObjectsFactory.create_component_configuration(self.rootcomponent, eeg_component)

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        # dictionary to test against new objects created bellow
        components_before_count = Component.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_components = Component.objects.exclude(id__in=[self.rootcomponent.id, eeg_component.id])
        self.assertEqual(Component.objects.count(), components_before_count + len(new_components))
        for item in new_components:
            self.assertEqual(Experiment.objects.last().id, item.experiment.id)
        new_rootcomponent = new_components.get(component_type='block')
        new_component = new_components.get(component_type='eeg')
        new_eeg = EEG.objects.last()
        new_experiment = Experiment.objects.last()
        self.assertEqual(new_component.experiment.id, new_experiment.id)
        new_component_configuration = ComponentConfiguration.objects.last()
        self.assertEqual(new_component_configuration.component.id, new_component.id)
        self.assertEqual(new_component_configuration.parent.id, new_rootcomponent.id)
        self.assertEqual(new_component.id, new_eeg.id)
        self.assertEqual(2, EEGSetting.objects.count())
        eeg_setting = EEGSetting.objects.last()
        self.assertEqual(new_eeg.eeg_setting.id, eeg_setting.id)
        self.assertEqual(eeg_setting.experiment.id, new_experiment.id)

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_creates_root_component_plus_emg_and_returns_successful_message1(self):
        # Test until importing tms setting
        self._create_minimum_objects_to_test_components()
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        new_emg_setting = ObjectsFactory.create_emg_setting(self.experiment, software_version)
        emg_component = ObjectsFactory.create_component(self.experiment, 'emg', kwargs={'emg_set': new_emg_setting})
        ObjectsFactory.create_component_configuration(self.rootcomponent, emg_component)

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        # dictionary to test against new objects created bellow
        components_before_count = Component.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_components = Component.objects.exclude(id__in=[self.rootcomponent.id, emg_component.id])
        self.assertEqual(Component.objects.count(), components_before_count + len(new_components))
        for item in new_components:
            self.assertEqual(Experiment.objects.last().id, item.experiment.id)
        new_rootcomponent = new_components.get(component_type='block')
        new_component = new_components.get(component_type='emg')
        new_emg = EMG.objects.last()
        new_experiment = Experiment.objects.last()
        self.assertEqual(new_component.experiment.id, new_experiment.id)
        new_component_configuration = ComponentConfiguration.objects.last()
        self.assertEqual(new_component_configuration.component.id, new_component.id)
        self.assertEqual(new_component_configuration.parent.id, new_rootcomponent.id)
        self.assertEqual(new_component.id, new_emg.id)
        self.assertEqual(2, EMGSetting.objects.count())
        new_emg_setting = EMGSetting.objects.last()
        self.assertEqual(new_emg.emg_setting.id, new_emg_setting.id)
        self.assertEqual(new_emg_setting.experiment.id, new_experiment.id)

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_creates_root_component_plus_emg_and_returns_successful_message2(self):
        # Test all models that tms setting depends on
        self._create_minimum_objects_to_test_components()

        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        emg_setting = ObjectsFactory.create_emg_setting(self.experiment, software_version)
        emg_component = ObjectsFactory.create_component(self.experiment, 'emg', kwargs={'emg_set': emg_setting})
        ObjectsFactory.create_component_configuration(self.rootcomponent, emg_component)

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        self.assertEqual(2, SoftwareVersion.objects.count())
        new_software_version = SoftwareVersion.objects.last()
        self.assertEqual(2, Software.objects.count())
        new_software = Software.objects.last()
        # Compare with 1 because the manufacturer is not updated if Manufacturer.name
        # is the same
        self.assertEqual(1, Manufacturer.objects.count())
        new_manufacturer = Manufacturer.objects.last()
        new_emg_setting = EMGSetting.objects.last()
        self.assertEqual(new_software_version.id, new_emg_setting.acquisition_software_version.id)
        self.assertEqual(new_software.id, new_software_version.software.id)
        self.assertEqual(new_manufacturer.id, new_software.manufacturer.id)

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_creates_experimental_protocols_and_groups_and_returns_successful_message(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent1 = ObjectsFactory.create_component(experiment, 'block', 'root component1')
        rootcomponent2 = ObjectsFactory.create_component(experiment, 'block', 'root component2')
        # Create another component ('instruction', for example)
        component1 = ObjectsFactory.create_component(experiment, 'instruction')
        ObjectsFactory.create_component_configuration(rootcomponent1, component1)
        # Create another component ('instruction', for example)
        component2 = ObjectsFactory.create_component(experiment, 'instruction')
        ObjectsFactory.create_component_configuration(rootcomponent2, component2)

        # Create groups
        group1 = ObjectsFactory.create_group(experiment)
        group2 = ObjectsFactory.create_group(experiment)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # dictionary to test against new components created bellow
        components_before_count = Component.objects.count()
        # dictionary to test against new groups created bellow
        groups_before_count = ExperimentGroup.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))
        new_components = Component.objects.exclude(
            id__in=[rootcomponent1.id, rootcomponent2.id, component1.id, component2.id]
        )
        new_groups = ExperimentGroup.objects.exclude(id__in=[group1.id, group2.id])
        self.assertEqual(Component.objects.count(), components_before_count + len(new_components))
        self.assertEqual(ExperimentGroup.objects.count(), groups_before_count + len(new_groups))

        for item in new_components:
            self.assertEqual(Experiment.objects.last().id, item.experiment.id)
        for item in new_groups:
            self.assertEqual(Experiment.objects.last().id, item.experiment.id)
            self.assertFalse(new_components.filter(id=item.experimental_protocol_id).exists())

        # TODO (NES-908): get by exclude not this way
        new_instructions = Instruction.objects.all().order_by('-id')[:2]
        self.assertEqual(2, new_instructions.count())
        new_instruction_components = \
            Component.objects.filter(component_type='instruction').order_by('-id')[:2]
        for instruction in new_instructions:
            self.assertIn(instruction.id, new_instruction_components.values_list('id', flat=True))

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_creates_experiment_in_existing_study_and_returns_successful_message(self):
        # TODO: this test is only for testing new experiment pertains to existent research project
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        # Create root component (which is a 'block' type and it is the head of the experimental protocol)
        rootcomponent = ObjectsFactory.create_component(experiment, 'block', 'root component')
        # Create another component ('instruction', for example)
        component = ObjectsFactory.create_component(experiment, 'instruction')
        ObjectsFactory.create_component_configuration(rootcomponent, component)
        group1 = ObjectsFactory.create_group(experiment=experiment, experimental_protocol=rootcomponent)
        group2 = ObjectsFactory.create_group(experiment=experiment, experimental_protocol=rootcomponent)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # dictionary to test against new objects created bellow
        old_objects_count = Component.objects.count()
        # dictionary to test against new groups created bellow
        old_groups_count = ExperimentGroup.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import', args=(research_project.id,)),
                                        {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))
        new_components = Component.objects.exclude(id__in=[rootcomponent.id, component.id])
        new_groups = ExperimentGroup.objects.exclude(id__in=[group1.id, group2.id])
        self.assertEqual(
            Component.objects.count(),
            old_objects_count + len(new_components))
        self.assertEqual(
            ExperimentGroup.objects.count(),
            old_groups_count + len(new_groups))

        for item in new_components:
            self.assertEqual(Experiment.objects.last().id, item.experiment.id)
        for item in new_groups:
            self.assertEqual(Experiment.objects.last().id, item.experiment.id)
            self.assertTrue(new_components.filter(id=item.experimental_protocol_id).exists())

        self.assertEqual(research_project.id, Experiment.objects.last().research_project.id)

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso.')

    def test_POST_experiment_import_file_creates_groups_with_experimental_protocol_and_returns_successful_message(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent1 = ObjectsFactory.create_component(experiment, 'block', 'root component1')
        rootcomponent2 = ObjectsFactory.create_component(experiment, 'block', 'root component2')
        group1 = ObjectsFactory.create_group(experiment=experiment, experimental_protocol=rootcomponent1)
        group2 = ObjectsFactory.create_group(experiment=experiment, experimental_protocol=rootcomponent2)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))
        new_components = Component.objects.exclude(id__in=[rootcomponent1.id, rootcomponent2.id])
        new_groups = ExperimentGroup.objects.exclude(id__in=[group1.id, group2.id])
        self.assertEqual(2, len(new_components))

        for group in new_groups:
            self.assertEqual(Experiment.objects.last().id, group.experiment.id)
            self.assertTrue(new_components.filter(id=group.experimental_protocol_id).exists())

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')
    # Fim dos testes a serem revisados

    # Log tests
    def test_POST_experiment_import_file_redirects_to_importing_log_page_1(self):
        # import ResearchProject/Experiment
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

    def test_POST_experiment_import_file_redirects_to_importing_log_page_2(self):
        # import only Experiment
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(
                reverse('experiment_import', args=(research_project.id,)),
                {'file': file}, follow=True
            )
        self.assertRedirects(response, reverse('import_log'))

    def test_POST_experiment_import_file_redirects_for_correct_template_1(self):
        # import ResearchProject/Experiment
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertTemplateUsed(response, 'experiment/import_log.html')

    def test_POST_experiment_import_file_redirects_for_correct_template_2(self):
        # import only Experiment
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(
                reverse('experiment_import', args=(research_project.id,)),
                {'file': file}, follow=True
            )
        self.assertTemplateUsed(response, 'experiment/import_log.html')

    def test_POST_experiment_import_file_returns_log_with_experiment_and_research_project_titles(self):
        # import ResearchProject/Experiment
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertIn(
            '1 Estudo importado: ' + ResearchProject.objects.last().title,
            strip_tags(response.content.decode('utf-8'))
        )
        self.assertIn(
            '1 Experimento importado: ' + Experiment.objects.last().title,
            strip_tags(response.content.decode('utf-8'))
        )

    def test_POST_experiment_import_file_returns_log_with_experiment_title(self):
        # import only Experiment
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(
                reverse('experiment_import', args=(research_project.id,)),
                {'file': file}, follow=True
            )
        self.assertNotIn(
            '1 Estudo importado: ' + ResearchProject.objects.last().title,
            strip_tags(response.content.decode('utf-8'))
        )
        self.assertIn(
            '1 Experimento importado: ' + Experiment.objects.last().title,
            strip_tags(response.content.decode('utf-8'))
        )

    def test_POST_experiment_import_file_returns_research_project_and_experiment_pages_links(self):
        # import ResearchProject/Experiment
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertContains(
            response,
            reverse(
                'research_project_view', kwargs={'research_project_id': ResearchProject.objects.last().id}
            )
        )
        self.assertContains(
            response,
            reverse(
                'experiment_view', kwargs={'experiment_id': Experiment.objects.last().id}
            )
        )

    def test_POST_experiment_import_file_returns_experiment_page_link(self):
        # import only Experiment
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(
                reverse('experiment_import', args=(research_project.id,)),
                {'file': file}, follow=True
            )
        self.assertNotContains(
            response,
            reverse(
                'research_project_view', kwargs={'research_project_id': ResearchProject.objects.last().id}
            )
        )
        self.assertContains(
            response,
            reverse(
                'experiment_view', kwargs={'experiment_id': Experiment.objects.last().id}
            )
        )

    def test_POST_experiment_import_file_returns_log_with_number_of_groups_imported(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        ObjectsFactory.create_group(experiment)
        ObjectsFactory.create_group(experiment)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertContains(response, '2 Grupos importados')

    def test_POST_experiment_import_file_returns_log_with_steps_types_and_number_of_each_step(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        ObjectsFactory.create_research_project(owner=self.user)
        rootcomponent1 = ObjectsFactory.create_component(experiment, 'block', 'root component group 1')
        rootcomponent2 = ObjectsFactory.create_component(experiment, 'block', 'root component group 2')
        ObjectsFactory.create_group(experiment, rootcomponent1)
        ObjectsFactory.create_group(experiment, rootcomponent2)

        # Create experimental protocol steps for the first group (rootcomponent1)
        ObjectsFactory.create_complete_set_of_components(experiment, rootcomponent1)

        # Create one more component to test pluralization
        component = ObjectsFactory.create_component(experiment, Component.TASK_EXPERIMENT)
        ObjectsFactory.create_component_configuration(rootcomponent2, component)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self._assert_steps_imported(response)

    def test_research_project_and_experiment(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        self._test_creation_and_linking_between_two_models('experiment.researchproject',
                                                           'experiment.experiment',
                                                           'research_project',
                                                           experiment)

    def test_successful_message_importing_experiment_into_existent_research_project(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()

        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(
                reverse('experiment_import', kwargs={'research_project_id':research_project.id}),
                {'file': file},follow=True
            )
        self.assertRedirects(response, reverse('import_log'))

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso.')

    def test_successful_message_importing_experiment(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()

        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_experiment_and_group(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        group1 = ObjectsFactory.create_group(experiment)
        group2 = ObjectsFactory.create_group(experiment)

        self._test_creation_and_linking_between_two_models('experiment.experiment',
                                                           'experiment.group',
                                                           'experiment',
                                                           experiment)

    def test_group_and_experimental_protocol(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        root1 = ObjectsFactory.create_block(experiment)
        root2 = ObjectsFactory.create_block(experiment)
        group1 = ObjectsFactory.create_group(experiment, root1)
        group2 = ObjectsFactory.create_group(experiment, root2)
        group3 = ObjectsFactory.create_group(experiment)

        self._test_creation_and_linking_between_two_models('experiment.group',
                                                           'experiment.block',
                                                           'component_ptr__experiment__groups',
                                                           experiment)

    def test_POST_experiment_import_file_creates_experimental_protocol_with_reuse_and_returns_successful_message(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent = ObjectsFactory.create_component(experiment, 'block', 'root component')
        # Create another component ('instruction', for example)
        component1 = ObjectsFactory.create_component(experiment, 'instruction')
        cc1 = ObjectsFactory.create_component_configuration(rootcomponent, component1)
        # And finally the last one Component ('tms', for example)
        component2_tms_setting = ObjectsFactory.create_tms_setting(experiment)
        component2 = ObjectsFactory.create_component(experiment, 'tms', kwargs={'tms_set': component2_tms_setting})
        cc2 = ObjectsFactory.create_component_configuration(rootcomponent, component2)
        # Create a reuse of the step 1
        cc3 = ObjectsFactory.create_component_configuration(rootcomponent, component1)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        old_component_configurations = ComponentConfiguration.objects.filter(id__in=[cc1.id, cc2.id, cc3.id])

        new_instruction_component = Component.objects.filter(component_type='instruction').last()
        self.assertEqual(2, new_instruction_component.configuration.count())
        for component_configuration in new_instruction_component.configuration.all():
            self.assertNotIn(component_configuration, old_component_configurations)

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_creates_groups_with_reuses_of_their_experimental_protocol_and_returns_successful_message(
            self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent1 = ObjectsFactory.create_component(experiment, 'block', 'root component1')
        rootcomponent2 = ObjectsFactory.create_component(experiment, 'block', 'root component2')
        # Create another component ('instruction', for example)
        component1 = ObjectsFactory.create_component(experiment, 'instruction')
        component1_config = ObjectsFactory.create_component_configuration(rootcomponent1, component1)
        # And finally the last one component ('tms', for example)
        component2_tms_setting = ObjectsFactory.create_tms_setting(experiment)
        component2 = ObjectsFactory.create_component(experiment, 'tms', kwargs={'tms_set': component2_tms_setting})
        component2_config = ObjectsFactory.create_component_configuration(rootcomponent1, component2)
        # Create a reuse of the step 1 on the same protocol
        component3_config = ObjectsFactory.create_component_configuration(rootcomponent1, component1)
        # Create a reuse of the step 1 of experimental protocol 1 in group 2
        component4_config = ObjectsFactory.create_component_configuration(rootcomponent2, component1)

        # Create groups
        group1 = ObjectsFactory.create_group(experiment=experiment, experimental_protocol=rootcomponent1)
        group2 = ObjectsFactory.create_group(experiment=experiment, experimental_protocol=rootcomponent2)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # dictionary to test against new objects created bellow
        old_objects_count = Component.objects.count()
        # dictionary to test against new component configurations created bellow
        old_components_configs_count = ComponentConfiguration.objects.count()
        # dictionary to test against new groups created bellow
        old_groups_count = ExperimentGroup.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_components = Component.objects.exclude(id__in=[rootcomponent1.id, rootcomponent2.id,
                                                           component1.id, component2.id])
        new_groups = ExperimentGroup.objects.exclude(id__in=[group1.id, group2.id])
        new_components_configurations = ComponentConfiguration.objects.exclude(id__in=[component1_config.id,
                                                                                       component2_config.id,
                                                                                       component3_config.id,
                                                                                       component4_config.id])
        self.assertEqual(
            Component.objects.count(),
            old_objects_count + len(new_components))
        self.assertEqual(
            ExperimentGroup.objects.count(),
            old_groups_count + len(new_groups))
        self.assertEqual(
            ComponentConfiguration.objects.count(),
            old_components_configs_count + len(new_components_configurations))

        for item in new_components:
            self.assertEqual(Experiment.objects.last().id, item.experiment.id)
        for item in new_groups:
            self.assertEqual(Experiment.objects.last().id, item.experiment.id)
            self.assertTrue(new_components.filter(id=item.experimental_protocol_id).exists())
        for item in new_components_configurations:
            self.assertTrue(Component.objects.filter(id=item.component_id).exists())
            self.assertTrue(ExperimentGroup.objects.filter(experimental_protocol_id=item.parent_id).exists())

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_reuse_keywords_already_in_database_and_returns_successful_message(self):
        keyword1 = Keyword.objects.create(name='Test1')
        keyword2 = Keyword.objects.create(name='Test2')
        research_project = ObjectsFactory.create_research_project(owner=self.user)

        research_project.keywords.add(keyword1)
        research_project.keywords.add(keyword2)
        research_project.save()

        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # dictionary to test against new keywords created bellow
        old_keywords_count = Keyword.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_keywords = Keyword.objects.exclude(id__in=[keyword1.id, keyword2.id])
        self.assertEqual(
            Keyword.objects.count(),
            old_keywords_count + len(new_keywords))
        for item in new_keywords:
            self.assertIn(item, ResearchProject.objects.last().keywords.all())
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_creates_keywords_and_returns_successful_message(self):
        keyword1 = Keyword.objects.create(name='Test1')
        keyword2 = Keyword.objects.create(name='Test2')
        research_project = ObjectsFactory.create_research_project(owner=self.user)

        research_project.keywords.add(keyword1)
        research_project.keywords.add(keyword2)
        research_project.save()

        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Delete the keyword, so it is not reused, but created a new one
        Keyword.objects.filter(id=keyword1.id).delete()
        # dictionary to test against new keywords created bellow
        old_keywords_count = Keyword.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_keywords = Keyword.objects.exclude(id__in=[keyword1.id, keyword2.id])
        self.assertEqual(
            Keyword.objects.count(),
            old_keywords_count + len(new_keywords))
        for item in new_keywords:
            self.assertIn(item, ResearchProject.objects.last().keywords.all())
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    # Components tests
    def test_component_and_block(self):
        self._create_minimum_objects_to_test_components()
        new_component = ObjectsFactory.create_component(self.experiment, 'block')
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.block',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'block'})

    def test_component_and_instruction(self):
        self._create_minimum_objects_to_test_components()
        new_component = ObjectsFactory.create_component(self.experiment, 'instruction')
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.instruction',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'instruction'})

    def test_component_and_pause(self):
        self._create_minimum_objects_to_test_components()
        new_component = ObjectsFactory.create_component(self.experiment, 'pause')
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.pause',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'pause'})

    def test_component_and_task(self):
        self._create_minimum_objects_to_test_components()
        new_component = ObjectsFactory.create_component(self.experiment, 'task')
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.task',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'task'})

    def test_component_and_stimulus(self):
        self._create_minimum_objects_to_test_components()
        stimulus_type = StimulusType.objects.create(name='TEST_STIMULUS_TYPE')
        new_component = ObjectsFactory.create_component(self.experiment, 'stimulus',
                                                        kwargs={'stimulus_type': stimulus_type})
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.stimulus',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'stimulus'})

    def test_component_and_task_experiment(self):
        self._create_minimum_objects_to_test_components()
        new_component = ObjectsFactory.create_component(self.experiment, 'task_experiment')
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.taskfortheexperimenter',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'task_experiment'})

    def test_component_and_eeg(self):
        self._create_minimum_objects_to_test_components()
        eeg_setting = EEGSetting.objects.create(name='TESTE_EEG_SETTING',
                                                experiment=self.experiment)

        new_component = ObjectsFactory.create_component(self.experiment, 'eeg', kwargs={'eeg_set': eeg_setting})
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.eeg',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'eeg'})

    def test_component_and_emg(self):
        self._create_minimum_objects_to_test_components()
        manufacturer = Manufacturer.objects.create(name='TEST_MANUFACTURER')
        software = Software.objects.create(name='TEST_SOFTWARE', manufacturer=manufacturer)
        software_version = SoftwareVersion.objects.create(name='TEST_SOFTWARE_VERSION', software=software)
        emg_setting = EMGSetting.objects.create(name='TESTE_EEG_SETTING',
                                                experiment=self.experiment,
                                                acquisition_software_version=software_version)

        new_component = ObjectsFactory.create_component(self.experiment, 'emg', kwargs={'emg_set': emg_setting})
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.emg',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'emg'})

    def test_component_and_tms(self):
        self._create_minimum_objects_to_test_components()
        tms_setting = TMSSetting.objects.create(name='TESTE_TMS_SETTING',
                                                experiment=self.experiment)

        new_component = ObjectsFactory.create_component(self.experiment, 'tms', kwargs={'tms_set': tms_setting})
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.tms',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'tms'})

    def test_component_and_digital_game_phase(self):
        self._create_minimum_objects_to_test_components()
        manufacturer = Manufacturer.objects.create(name='TEST_MANUFACTURER')
        software = Software.objects.create(name='TEST_SOFTWARE', manufacturer=manufacturer)
        software_version = SoftwareVersion.objects.create(name='TEST_SOFTWARE_VERSION', software=software)
        context_tree = ContextTree.objects.create(name='TEST_CONTEXT_TREE',
                                                  description='DESCRIPTION_CONTEXT_TREE',
                                                  experiment=self.experiment)

        new_component = ObjectsFactory.create_component(self.experiment, 'digital_game_phase',
                                                        kwargs={'software_version': software_version,
                                                                'context_tree': context_tree}
                                                        )
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.digitalgamephase',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'digital_game_phase'})

    def test_component_and_generic_data_collection(self):
        self._create_minimum_objects_to_test_components()
        information_type = InformationType.objects.create(name='TEST_INFORMATION_TYPE',
                                                          description='DESCRIPTION_INFORMATION_TYPE')

        new_component = ObjectsFactory.create_component(self.experiment, 'generic_data_collection',
                                                        kwargs={'it': information_type}
                                                        )
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.genericdatacollection',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'generic_data_collection'})

    def test_component_and_questionnaire(self):
        self._create_minimum_objects_to_test_components()
        self._create_minimum_objects_to_test_questionnaire()
        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.questionnaire',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'questionnaire'})

    # Participants tests
    def test_POST_experiment_import_file_creates_participants_of_groups_and_returns_successful_message(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent1 = ObjectsFactory.create_component(experiment, 'block', 'root component1')
        rootcomponent2 = ObjectsFactory.create_component(experiment, 'block', 'root component2')
        component = ObjectsFactory.create_component(experiment, 'instruction')
        ObjectsFactory.create_component_configuration(rootcomponent1, component)

        # Create groups
        group1 = ObjectsFactory.create_group(experiment=experiment, experimental_protocol=rootcomponent1)
        group2 = ObjectsFactory.create_group(experiment=experiment, experimental_protocol=rootcomponent2)

        # Create participants
        util = UtilTests()
        patient1_mock = util.create_patient(changed_by=self.user)
        patient2_mock = util.create_patient(changed_by=self.user)

        # Remove their CPF, we are simulating a new database
        patient1_mock.cpf = None
        patient2_mock.cpf = None

        patient1_mock.save()
        patient2_mock.save()

        subject_mock1 = Subject.objects.create(patient=patient1_mock)
        subject_mock2 = Subject.objects.create(patient=patient2_mock)

        subject_group1 = SubjectOfGroup(subject=subject_mock1, group=group1)
        subject_group1.save()
        subject_group2 = SubjectOfGroup(subject=subject_mock1, group=group2)
        subject_group2.save()
        subject_group3 = SubjectOfGroup(subject=subject_mock2, group=group2)
        subject_group3.save()

        group1.subjectofgroup_set.add(subject_group1)
        group2.subjectofgroup_set.add(subject_group2)
        group2.subjectofgroup_set.add(subject_group3)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_patients = Patient.objects.exclude(id__in=[patient1_mock.id, patient2_mock.id])
        new_subjects = Subject.objects.exclude(id__in=[subject_mock1.id, subject_mock2.id])
        new_subjectsofgroups = SubjectOfGroup.objects.exclude(id__in=[subject_group1.id,
                                                                      subject_group2.id,
                                                                      subject_group3.id])
        self.assertEqual(2, new_patients.count())
        self.assertEqual(2, new_subjects.count())
        self.assertEqual(3, new_subjectsofgroups.count())

        for item in new_subjectsofgroups:
            self.assertTrue(SubjectOfGroup.objects.filter(id=item.id).exists())
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_creates_patient_with_new_code_and_cpf_cleared(self):
        research_project = ObjectsFactory.create_research_project(self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        group = ObjectsFactory.create_group(experiment)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        ObjectsFactory.create_subject_of_group(group, subject)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        patient_last_code_before = Patient.objects.all().order_by('-code').first().code

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_patients = Patient.objects.exclude(id=patient.id)
        self.assertEqual(1, new_patients.count())

        new_patient_code = 'P' + str(int(patient_last_code_before.split('P')[1]) + 1)
        self.assertEqual(new_patient_code, Patient.objects.last().code)
        self.assertEqual(None, Patient.objects.last().cpf)

    def test_POST_experiment_import_file_creates_participants_of_groups_associates_with_user_that_is_importing(self):
        research_project = ObjectsFactory.create_research_project(self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        group = ObjectsFactory.create_group(experiment)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        ObjectsFactory.create_subject_of_group(group, subject)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        new_patient = Patient.objects.last()
        self.assertEqual(self.user_importer, new_patient.changed_by)

    def test_POST_experiment_import_file_creates_participants_with_personal_data_and_returns_successful_message(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent1 = ObjectsFactory.create_component(experiment, 'block', 'root component1')
        rootcomponent2 = ObjectsFactory.create_component(experiment, 'block', 'root component2')
        # Create another component ('instruction', for example)
        component = ObjectsFactory.create_component(experiment, 'instruction')
        ObjectsFactory.create_component_configuration(rootcomponent1, component)

        # Create groups
        group1 = ObjectsFactory.create_group(experiment=experiment, experimental_protocol=rootcomponent1)
        group2 = ObjectsFactory.create_group(experiment=experiment, experimental_protocol=rootcomponent2)

        util = UtilTests()
        patient1 = util.create_patient(changed_by=self.user)
        patient2 = util.create_patient(changed_by=self.user)

        # Create participants data
        # Telephone
        telephone1 = Telephone.objects.create(patient=patient1, number='987654321', changed_by=self.user)
        telephone2 = Telephone.objects.create(patient=patient2, number='987654321', changed_by=self.user)

        # Social demograph
        sociodemograph1 = SocialDemographicData.objects.create(
            patient=patient1,
            natural_of='Testelândia',
            citizenship='Testense',
            profession='Testador',
            occupation='Testador',
            changed_by=self.user
        )
        sociodemograph2 = SocialDemographicData.objects.create(
            patient=patient2,
            natural_of='Testelândia',
            citizenship='Testense',
            profession='Testador',
            occupation='Testador',
            changed_by=self.user
        )

        # Social history
        amount_cigarettes = AmountCigarettes.objects.create(name='Menos de 1 maço')
        alcohol_frequency = AlcoholFrequency.objects.create(name='Esporadicamente')
        alcohol_period = AlcoholPeriod.objects.create(name='5-10 anos')
        socialhistory1 = SocialHistoryData.objects.create(
            patient=patient1,
            smoker=True,
            amount_cigarettes=amount_cigarettes,
            changed_by=self.user,
            alcoholic=True,
            alcohol_frequency=alcohol_frequency,
            alcohol_period=alcohol_period
        )
        socialhistory2 = SocialHistoryData.objects.create(
            patient=patient2,
            smoker=False,
            amount_cigarettes=None,
            changed_by=self.user,
            alcoholic=False,
            alcohol_frequency=None,
            alcohol_period=None
        )

        # Medical record
        cid10_1 = UtilTests.create_cid10('1')  # TODO (NES-908): create with real code
        cid10_2 = UtilTests.create_cid10('10')
        medicalevaluation1 = MedicalRecordData.objects.create(
            patient=patient1,
            record_responsible=self.user  # TODO (NES-908): see if import with user or None
        )
        diagnosis1 = Diagnosis.objects.create(
            medical_record_data=medicalevaluation1,
            classification_of_diseases=cid10_1
        )

        medicalevaluation2 = MedicalRecordData.objects.create(
            patient=patient2,
            record_responsible=self.user
        )
        diagnosis2 = Diagnosis.objects.create(
            medical_record_data=medicalevaluation2,
            classification_of_diseases=cid10_2
        )

        # Remove their cpfs, we are simulating a new base
        patient1.cpf = None
        patient2.cpf = None
        patient1.save()
        patient2.save()

        subject1 = Subject(patient=patient1)
        subject1.save()
        subject2 = Subject(patient=patient2)
        subject2.save()

        subject_group1 = SubjectOfGroup(subject=subject1, group=group1)
        subject_group1.save()
        subject_group2 = SubjectOfGroup(subject=subject1, group=group2)
        subject_group2.save()
        subject_group3 = SubjectOfGroup(subject=subject2, group=group2)
        subject_group3.save()

        group1.subjectofgroup_set.add(subject_group1)
        group2.subjectofgroup_set.add(subject_group2)
        group2.subjectofgroup_set.add(subject_group3)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_patients = Patient.objects.exclude(id__in=[patient1.id, patient2.id])
        new_telephones = Telephone.objects.exclude(id__in=[telephone1.id, telephone2.id])
        new_socialdemographic = SocialDemographicData.objects.exclude(id__in=[sociodemograph1.id, sociodemograph2.id])
        new_socialhistory = SocialHistoryData.objects.exclude(id__in=[socialhistory1.id, socialhistory2.id])
        new_diagnosis = Diagnosis.objects.exclude(id__in=[diagnosis1.id, diagnosis2.id])
        new_medical_records = MedicalRecordData.objects.exclude(id__in=[medicalevaluation1.id, medicalevaluation2.id])

        self.assertEqual(2, new_patients.count())
        self.assertEqual(2, new_telephones.count())
        self.assertEqual(2, new_socialdemographic.count())
        self.assertEqual(2, new_socialhistory.count())
        self.assertEqual(2, new_medical_records.count())
        self.assertEqual(2, new_diagnosis.count())

        for patient in new_patients:
            self.assertTrue(Telephone.objects.filter(patient_id=patient.id).exists())
            self.assertTrue(SocialDemographicData.objects.filter(patient_id=patient.id).exists())
            self.assertTrue(SocialHistoryData.objects.filter(patient_id=patient.id).exists())
            self.assertTrue(Diagnosis.objects.filter(medical_record_data__patient_id=patient.id).exists())
            self.assertTrue(MedicalRecordData.objects.filter(patient_id=patient.id).exists())

        self.assertNotEqual(new_patients[0].id, new_patients[1].id)
        self.assertNotEqual(new_telephones[0].id, new_telephones[1].id)
        self.assertNotEqual(new_socialdemographic[0].id, new_socialdemographic[1].id)
        self.assertNotEqual(new_socialhistory[0].id, new_socialhistory[1].id)
        self.assertNotEqual(new_medical_records[0].id, new_medical_records[1].id)
        self.assertNotEqual(new_diagnosis[0].id, new_diagnosis[1].id)

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso. Novo estudo criado.')

    def test_POST_experiment_import_file_creates_telephone_with_logged_user(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        group = ObjectsFactory.create_group(experiment)
        ObjectsFactory.create_subject_of_group(group, subject)

        telephone = UtilTests.create_telephone(patient, self.user)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_telephone = Telephone.objects.exclude(id=telephone.id)
        self.assertEqual(1, new_telephone.count())
        self.assertEqual(new_telephone[0].changed_by, self.user_importer)

    def test_POST_experiment_import_file_creates_data_configuration_tree_and_returns_success_message(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent = ObjectsFactory.create_component(experiment, 'block')
        eeg_setting = ObjectsFactory.create_eeg_setting(experiment)
        eeg_component = ObjectsFactory.create_component(experiment, 'eeg', kwargs={'eeg_set': eeg_setting})
        component_config = ObjectsFactory.create_component_configuration(rootcomponent, eeg_component)
        ObjectsFactory.create_data_configuration_tree(component_config)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        self.assertEqual(2, DataConfigurationTree.objects.count())
        self.assertEqual(
            DataConfigurationTree.objects.last().component_configuration.id, ComponentConfiguration.objects.last().id
        )

    # Goalkeeper tests
    def test_software_version_and_digital_game_phase(self):
        self._test_creation_and_linking_between_two_models('experiment.softwareversion',
                                                           'experiment.digitalgamephase',
                                                           'software_version',
                                                           self._create_experiment_with_digital_game_phase())

    def test_context_tree_and_digital_game_phase(self):
        self._test_creation_and_linking_between_two_models('experiment.contexttree',
                                                           'experiment.digitalgamephase',
                                                           'context_tree',
                                                           self._create_experiment_with_digital_game_phase())

    # TMS tests
    def test_material_and_coil_model(self):
        self._test_creation_and_linking_between_two_models('experiment.material',
                                                           'experiment.coilmodel',
                                                           'material_id',
                                                           self._create_experiment_with_tms_setting(),
                                                           flag2=True)

    def test_coil_shape_and_coil_model(self):
        self._test_creation_and_linking_between_two_models('experiment.coilshape',
                                                           'experiment.coilmodel',
                                                           'coil_shape_id',
                                                           self._create_experiment_with_tms_setting())

    def test_coil_model_and_tms_device_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.coilmodel',
                                                           'experiment.tmsdevicesetting',
                                                           'coil_model_id',
                                                           self._create_experiment_with_tms_setting())

    def test_tms_device_and_tms_device_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.tmsdevice',
                                                           'experiment.tmsdevicesetting',
                                                           'tms_device_id',
                                                           self._create_experiment_with_tms_setting())

    def test_tms_setting_and_tms_device_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.tmssetting',
                                                           'experiment.tmsdevicesetting',
                                                           'tms_setting_id',
                                                           self._create_experiment_with_tms_setting())

    def test_experiment_and_tms_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.experiment',
                                                           'experiment.tmssetting',
                                                           'experiment_id',
                                                           self._create_experiment_with_tms_setting())

    def test_import_of_material_when_an_identical_one_is_already_in_the_database(self):
        self._test_creation_of_objects_that_should_not_be_duplicated(self._create_experiment_with_tms_setting(),
                                                                     'experiment.material')

    def test_import_of_manufacturer_when_an_identical_one_is_already_in_the_database(self):
        self._test_creation_of_objects_that_should_not_be_duplicated(self._create_experiment_with_tms_setting(),
                                                                     'experiment.manufacturer')

    # EEG tests
    def test_electrode_configuration_and_electrode_model(self):
        self._test_creation_and_linking_between_two_models('experiment.electrodeconfiguration',
                                                           'experiment.electrodemodel',
                                                           'electrode_configuration_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_material_and_electrode_model(self):
        self._test_creation_and_linking_between_two_models('experiment.material',
                                                           'experiment.electrodemodel',
                                                           'material_id',
                                                           self._create_experiment_with_eeg_setting(),
                                                           flag2=True)

    def test_electrode_model_and_eeg_electrode_position_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.electrodemodel',
                                                           'experiment.eegelectrodepositionsetting',
                                                           'electrode_model_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_electrode_model_and_eeg_electrode_net(self):
        self._test_creation_and_linking_between_two_models('experiment.electrodemodel',
                                                           'experiment.eegelectrodenet',
                                                           'electrode_model_default_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_eeg_electrode_localization_system_and_eeg_electrode_position(self):
        self._test_creation_and_linking_between_two_models('experiment.eegelectrodelocalizationsystem',
                                                           'experiment.eegelectrodeposition',
                                                           'eeg_electrode_localization_system_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_eeg_electrode_localization_system_and_eeg_electrode_net_system(self):
        self._test_creation_and_linking_between_two_models('experiment.eegelectrodelocalizationsystem',
                                                           'experiment.eegelectrodenetsystem',
                                                           'eeg_electrode_localization_system_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_eeg_electrode_net_and_eeg_electrode_net_system(self):
        self._test_creation_and_linking_between_two_models('experiment.eegelectrodenet',
                                                           'experiment.eegelectrodenetsystem',
                                                           'eeg_electrode_net_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_eeg_electrode_net_system_and_eeg_electrode_layout_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.eegelectrodenetsystem',
                                                           'experiment.eegelectrodelayoutsetting',
                                                           'eeg_electrode_net_system_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_eeg_electrode_layout_setting_and_eeg_electrode_position_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.eegelectrodelayoutsetting',
                                                           'experiment.eegelectrodepositionsetting',
                                                           'eeg_electrode_layout_setting_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_eeg_electrode_position_and_eeg_electrode_position_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.eegelectrodeposition',
                                                           'experiment.eegelectrodepositionsetting',
                                                           'eeg_electrode_position_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_eeg_setting_and_eeg_electrode_layout_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.eegsetting',
                                                           'experiment.eegelectrodelayoutsetting',
                                                           'eeg_setting_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_filter_type_and_eeg_filter_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.filtertype',
                                                           'experiment.eegfiltersetting',
                                                           'eeg_filter_type_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_amplifier_and_eeg_amplifier_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.amplifier',
                                                           'experiment.eegamplifiersetting',
                                                           'eeg_amplifier_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_amplifierdetectiontype_and_amplifier(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.amplifierdetectiontype', 'experiment.amplifier', 'amplifier_detection_type_id',
            self._create_experiment_with_eeg_setting()
        )

    def test_tetheringsystem_and_amplifier(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.tetheringsystem', 'experiment.amplifier', 'tethering_system',
            self._create_experiment_with_eeg_setting()
        )

    def test_eeg_solution_and_eeg_solution_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.eegsolution',
                                                           'experiment.eegsolutionsetting',
                                                           'eeg_solution_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_manufacturer_and_eeg_solution(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.manufacturer', 'experiment.eegsolution', 'manufacturer',
            self._create_experiment_with_eeg_setting(), flag2=True
        )

    def test_eeg_setting_and_eeg_filter_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.eegsetting',
                                                           'experiment.eegfiltersetting',
                                                           'eeg_setting',
                                                           self._create_experiment_with_eeg_setting())

    def test_eeg_setting_and_eeg_amplifier_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.eegsetting',
                                                           'experiment.eegamplifiersetting',
                                                           'eeg_setting',
                                                           self._create_experiment_with_eeg_setting())

    def test_eeg_setting_and_eeg_solution_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.eegsetting',
                                                           'experiment.eegsolutionsetting',
                                                           'eeg_setting',
                                                           self._create_experiment_with_eeg_setting())

    def test_experiment_and_eeg_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.experiment',
                                                           'experiment.eegsetting',
                                                           'experiment_id',
                                                           self._create_experiment_with_eeg_setting())

    # EMG tests
    def test_manufacturer_and_software(self):
        self._test_creation_and_linking_between_two_models('experiment.manufacturer',
                                                           'experiment.software',
                                                           'manufacturer',
                                                           self._create_experiment_with_emg_setting(),
                                                           flag2=True)

    def test_software_and_software_version(self):
        self._test_creation_and_linking_between_two_models('experiment.software',
                                                           'experiment.softwareversion',
                                                           'software',
                                                           self._create_experiment_with_emg_setting())

    def test_manufacturer_and_equipment(self):
        self._test_creation_and_linking_between_two_models('experiment.manufacturer',
                                                           'experiment.equipment',
                                                           'manufacturer',
                                                           self._create_experiment_with_emg_setting(),
                                                           flag2=True)

    def test_equipment_and_adconverter(self):
        self._test_creation_and_linking_between_two_models('experiment.equipment',
                                                           'experiment.adconverter',
                                                           'equipment_ptr',
                                                           self._create_experiment_with_emg_setting(),
                                                           {'equipment_type': 'ad_converter'})

    def test_ad_converter_and_emg_ad_converter_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.adconverter',
                                                           'experiment.emgadconvertersetting',
                                                           'ad_converter',
                                                           self._create_experiment_with_emg_setting())

    def test_emg_setting_and_emg_ad_converter_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.emgsetting',
                                                           'experiment.emgadconvertersetting',
                                                           'emg_setting',
                                                           self._create_experiment_with_emg_setting())

    def test_emg_setting_and_emg_digital_filter_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.emgsetting',
                                                           'experiment.emgdigitalfiltersetting',
                                                           'emg_setting',
                                                           self._create_experiment_with_emg_setting())

    def test_filter_type_and_emg_digital_filter_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.filtertype',
                                                           'experiment.emgdigitalfiltersetting',
                                                           'filter_type',
                                                           self._create_experiment_with_emg_setting())

    def test_equipment_and_amplifier(self):
        self._test_creation_and_linking_between_two_models('experiment.equipment',
                                                           'experiment.amplifier',
                                                           'equipment_ptr',
                                                           self._create_experiment_with_emg_setting(),
                                                           {'equipment_type': 'amplifier'})

    def test_amplifier_and_emg_pre_amplifier_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.amplifier',
                                                           'experiment.emgpreamplifiersetting',
                                                           'amplifier',
                                                           self._create_experiment_with_emg_setting())

    def test_emg_pre_amplifier_setting_and_emg_pre_amplifier_filter_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.emgpreamplifiersetting',
                                                           'experiment.emgpreamplifierfiltersetting',
                                                           'emg_preamplifier_filter_setting',
                                                           self._create_experiment_with_emg_setting())

    def test_emg_electrode_setting_and_emg_pre_amplifier_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.emgelectrodesetting',
                                                           'experiment.emgpreamplifiersetting',
                                                           'emg_electrode_setting',
                                                           self._create_experiment_with_emg_setting())

    def test_amplifier_and_emg_amplifier_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.amplifier',
                                                           'experiment.emgamplifiersetting',
                                                           'amplifier',
                                                           self._create_experiment_with_emg_setting())

    def test_emg_amplifier_setting_and_emg_analog_filter_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.emgamplifiersetting',
                                                           'experiment.emganalogfiltersetting',
                                                           'emg_electrode_setting',
                                                           self._create_experiment_with_emg_setting())

    def test_emg_electrode_setting_and_emg_amplifier_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.emgelectrodesetting',
                                                           'experiment.emgamplifiersetting',
                                                           'emg_electrode_setting',
                                                           self._create_experiment_with_emg_setting())

    def test_emg_setting_and_emg_electrode_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.emgsetting',
                                                           'experiment.emgelectrodesetting',
                                                           'emg_setting',
                                                           self._create_experiment_with_emg_setting())

    def test_electrode_model_and_emg_electrode_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.electrodemodel',
                                                           'experiment.emgelectrodesetting',
                                                           'electrode',
                                                           self._create_experiment_with_emg_setting())

    def test_muscle_and_muscleside(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.muscle', 'experiment.muscleside', 'muscle', self._create_experiment_with_emg_setting()
        )

    def test_muscle_and_musclesubdivision(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.muscle', 'experiment.musclesubdivision', 'muscle', self._create_experiment_with_emg_setting()
        )

    def test_muscle_already_existent_doesnot_create_new_muscle(self):
        # TODO: implement it
        pass

    def test_musclesubdivision_and_emgelectrodeplacement(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.musclesubdivision', 'experiment.emgelectrodeplacement', 'muscle_subdivision',
            self._create_experiment_with_emg_setting()
        )

    def test_standardizationsystem_and_emgelectrodeplacement(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.standardizationsystem', 'experiment.emgelectrodeplacement', 'standardization_system',
            self._create_experiment_with_emg_setting()
        )

    def test_emgelectrodesetting_and_emgelectrodeplacementsetting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.emgelectrodesetting', 'experiment.emgelectrodeplacementsetting', 'emg_electrode_setting',
            self._create_experiment_with_emg_setting()
        )

    def test_muscleside_and_emgelectrodeplacementsetting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.muscleside', 'experiment.emgelectrodeplacementsetting', 'muscle_side',
            self._create_experiment_with_emg_setting()
        )

    def test_emgelectrodeplacement_and_emgelectrodeplacementsetting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.emgelectrodeplacement', 'experiment.emgelectrodeplacementsetting', 'emg_electrode_placement',
            self._create_experiment_with_emg_setting()
        )

    def test_emgelectrodeplacement_and_emgintramuscularplacement(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.emgelectrodeplacement', 'experiment.emgintramuscularplacement', 'emgelectrodeplacement_ptr',
            self._create_experiment_with_emg_setting(), flag1=True  # TODO (NES-908): momentarily put this flag
        )

    def test_emgelectrodeplacement_and_emgsurfaceplacement(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.emgelectrodeplacement', 'experiment.emgsurfaceplacement', 'emgelectrodeplacement_ptr',
            self._create_experiment_with_emg_setting(), flag1=True
        )

    def test_emgelectrodeplacement_and_emgneedleplacement(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.emgelectrodeplacement', 'experiment.emgneedleplacement', 'emgelectrodeplacement_ptr',
            self._create_experiment_with_emg_setting(), flag1=True
        )
