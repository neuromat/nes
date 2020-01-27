import io
import json
import shutil
import sys
import tempfile
import zipfile
import os
from unittest import skip
from unittest.mock import patch, call

from django.apps import apps
from django.contrib.auth.models import Group, User
from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.core.files import File
from django.test import TestCase, override_settings
from django.utils.encoding import smart_str
from django.utils.html import strip_tags
from django.conf import settings
from faker import Factory

from custom_user.tests_helper import create_user
from experiment.import_export import ExportExperiment
from experiment.models import Keyword, GoalkeeperGameConfig, \
    Component, GoalkeeperGame, GoalkeeperPhase, GoalkeeperGameResults, \
    FileFormat, ExperimentResearcher, Experiment, ResearchProject, \
    TMS, ComponentConfiguration, Questionnaire, Subject, SubjectOfGroup, \
    Manufacturer, Material, TMSDevice, TMSDeviceSetting, \
    CoilModel, CoilShape, TMSSetting, EEGSetting, EEGElectrodeLayoutSetting, \
    EEGElectrodeNetSystem, EEGElectrodeNet, ElectrodeModel, ElectrodeConfiguration, \
    EEGElectrodeLocalizationSystem, EEGElectrodePositionSetting, EEGElectrodePosition, \
    EEGFilterSetting, FilterType, Amplifier, EEGAmplifierSetting, EEGSolutionSetting, EEGSolution, \
    EMGSetting, EMGElectrodeSetting, EMGADConverterSetting, ADConverter, EMGDigitalFilterSetting, \
    SoftwareVersion, Software, AmplifierDetectionType, TetheringSystem, Muscle, MuscleSide, \
    MuscleSubdivision, EMGElectrodePlacementSetting, StandardizationSystem, \
    EMGIntramuscularPlacement, EMGNeedlePlacement, EMGSurfacePlacement, EMGAnalogFilterSetting, \
    EMGAmplifierSetting, EMGPreamplifierSetting, EMGPreamplifierFilterSetting, EEG, EMG, Instruction, \
    StimulusType, ContextTree, EMGElectrodePlacement, Equipment, DataConfigurationTree, EEGData, \
    HotSpot, ComponentAdditionalFile, TMSLocalizationSystem, EEGFile, EEGCapSize, \
    EEGElectrodeCap, EEGElectrodePositionCollectionStatus, EMGFile, \
    DigitalGamePhaseFile, GenericDataCollectionFile, AdditionalDataFile, Stimulus, QuestionnaireResponse, EMGData

from experiment.models import Group as ExperimentGroup
from configuration.models import LocalInstitution
from custom_user.models import Institution
from experiment.tests.tests_helper import ObjectsFactory
from patient.models import Patient, Telephone, SocialDemographicData, AmountCigarettes, AlcoholFrequency, \
    AlcoholPeriod, SocialHistoryData, MedicalRecordData, Diagnosis, ClassificationOfDiseases, FleshTone, Payment, \
    Religion, Schooling, ExamFile

from patient.tests.tests_orig import UtilTests
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
        self.group = ObjectsFactory.create_group(self.experiment, self.root_component)

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

    def tearDown(self):
        GoalkeeperGameConfig.objects.filter(idconfig=self.idconfig).using("goalkeeper").delete()
        GoalkeeperGameResults.objects.filter(idgameresult=self.idgameresult).using("goalkeeper").delete()

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
    TEMP_MEDIA_ROOT = tempfile.mkdtemp()

    def setUp(self):
        # create the groups of users and their permissions
        exec(open('add_initial_data.py').read())

        self.user, passwd = create_user(Group.objects.all())
        self.research_project = ObjectsFactory.create_research_project(owner=self.user)
        self.experiment = ObjectsFactory.create_experiment(self.research_project)
        self.group = ObjectsFactory.create_group(self.experiment)

        self.client.login(username=self.user.username, password=passwd)

    def tearDown(self):
        self.client.logout()

    def _create_minimum_objects_to_test_patient(self, patient):
        # TODO: equal to the one in ImportExperimentTest
        subject = ObjectsFactory.create_subject(patient)
        return ObjectsFactory.create_subject_of_group(self.group, subject)

    @staticmethod
    def set_export_survey_mock_value(mockServer, side_effect=False):
        first_survey = \
            'UEsDBAoAAAAIAKKGo0737UEwugoAAKk9AAARAAAAc3VydmV5XzkxNTMyNS5sc3PtW21z27gR/n6/AvWXtDM+Ky9Np83ofFVs56oZx8lZ' \
            'StLMzY0GIiEJNUXIIChbl8l/v8ULARCkQCptr0l69+FCYZ8FFosHi12QHn5/v87QlvCCsvy7o0cnD48QyROW0nz53dGb6Ytv/3r0/ek3w' \
            '5Ql5Zrk4vQbNLykazIp+Zbszlky3W3Iqf41HDQlAD9//lZ3f/r4L0+GA/cTZBnOlyVekgJ+uF+nJB8O7A+ADXzccMlZudEaC0qyVD2a5x' \
            'yvyemSpsOB+xlIi6hUdT6Tj50gxlPCI6iUFAmnGwFzjaCqqUUgHOcpW9NfsOxqpgaPGkcyssV5EnZpfmrPcXZn/AZP6gEcS9PT4R9+Ojs' \
            'fTUc/Pfr559PhQDZpYeEL//bo6ZPHTxWisAjnOgccp0AauqCJsl136WC+nvJmY3hPpMGeUwemyTLFKhM9kkchNdGmGwfWhMpnumU4qLyyz' \
            'z2P/yPueUF5IZCSHOCbx5+Hb9SD2pEDuyWHtyUpZB+x/Xkb3YEbzIEzszioYxNHpQICU0xMRRaTVzOMTYGTZUS8IllsAzOxisaVNawVFoz' \
            'vehjZGaR6hJ8iwRmZxZcD/jdLyQKXmYgFsj2RqTY7lpYZaQnAneHrthm+bu3uc6xymIcK40l6b+VYoJT0ctIrJRX6LFRiSS8n56TYwG6h' \
            '84zQVGMVwEzJLKPDXzs8qgdXlJfrOeHP9MQrRTN7IGS1nyX7qmdFtdBY3agBlmsO9F6BnKBuaRirHtbMqYWrvrGp4l/YqW03MI+DDagvM' \
            'xGv4mK4kk6w9yS4bZ4E/3umnXcwDSe3JS2oXAZYOdKDayOngaTKsBCc5cvTZ2ChfhrOOQIufV6Ue/TVU+7JZ0K5ruBWlPN/kUT0CmyvMR' \
            'c0oRuci/bANpxL4s1PPy+yPfnqyfbn34xsYU5dJ9u0g2wLmUv/aBaiB+F07l21I7ZAwAu0qLXmmHLyeRHuS49u4AKb4UWKrRq9nn4hFCx' \
            'IAofrARycKIUvj4SPv14SelWtX8s6V2AhOJ2Xgnx6iWu7iGC2OCtj8j2F279XJVnDHGRF09SsoJNqtDIx7Ew3flrq/BsPH6ZR/53hWwhV' \
            '59CwUFemMTrFrztwuqax6whyv4EIUsTqdwHZl0rxO0Yha0yzGChn+W5NfyExexf4XrCYnPE1jt0jFHhLBAVzlrFJCbLeZPE59bj9wGmqK' \
            'iCczewtdOzSFwYEb65jFzylPCfYDY0Om2XsDuI7LUT0/kbhpD9imFIwnUPP1EJ3QDlJgS5JFCZHheNnG70Eo7nAeXFHeMxhkPGnaWyGnC' \
            'xKHuPcppxnNIGZCXAWPHRClxxvVjFYBh1paOwWT6yzru1QkDyFEx7O8zXuuDMU7AaOI+2ujXxDAgsfvynDRUGKQr6Vic1Fkg1vRLLCcZA' \
            'aP9bRnJVgz6wzAlShzbuNjnWr+jO3YCQaFhQyZ64wjKLVfOCEX4pVbIFW7O7envMdQHXLTfNFbFiJy5lexw7YLezJhKWxJdY+h1DXDdpw' \
            'lgAdICZ2QnGSwL+i4x68hl2xIhYPatgNELMvFijOd12vyGoaQNUux96RLGFRl0kUOGwJvIuZWhGD5im5j+ByvKVLRcmUZDh2L58DK3dzh' \
            'nn0PJfRFYKwwAsI/jCVTUY6XLRkbJkRDKfUTobAQuyi7zACON7QGxKa3ZlJdpdWKmXw7hPlT4hrXJYYOqdSAA+s9rjTSHhePHry96VsPQ' \
            'FHOCUNNJo26QiLHk+ioSr1qOoknWc4nR+Ujmmtyg+baYR9+yJTDZqEwyFNcaIrwUp6WJ3Uln9UE7DJRmibE2igzThCoBOY0fy0o+HNmtB' \
            'TkK4IS0knMMAgCQmLuYbcqVUJScMeX+aZIxOTVtuVoKqdXXYSYmsyDddZSgg0rVXpKfOUEGJazaBBptIYOJT7ajpraVcxMsMsm72EYE9ib' \
            'g2qHCZcPScw+yBIZEJ8Q252RHtSE2rvg5k1dXlOY1U9kWO6TnfaqG4kFqqTnhakEWign/l0xKYaVGsHCc7Ab65nMwPfazp18erLp85VRm' \
            'aWppbCNBamLnUqNplxGs+thhM6hSqracRBX+bgVXbj4P+0cCvz/esSmHCEhtyNYo76tllXIgeuTvw2tJWZewL/5N/3NlMLtUKQAoQqod' \
            'go2WwgnLIn8QJbS07QGnbbcLqbtjwhtLUV06qu84b9F2juYqO643BnGBGiOjr3XXoolayY6YeOLxAqcJ8PGips16ceFtjvUy4LN9QT5D5' \
            '6i1HBIXb2hcYrYR92oMkqHM1ovqWCzOR7u0OV+uM5gaQpPXAQrXQIXqcpBw/TeeMSaJhT78BxjFYv7kEu130jVqFt+S3Puj6l90yl0zP/' \
            'JOqayz69nirVWVgcMo5V6uMEnUd2Og18hZNV2wVKd+3TiE3tpVATFujvLQOaiEAzePekX2fqr2/rHfivoNoi2iCUeeGrITOxqtEOEaetLT' \
            'ZMI+S4yYxlo375LxjaVJ8GCIJojjAqWmbZ7C0ynPfVDMEcfXgxvp5Mr0YvLz4em09azD87VqIVFDFoTkiOtHIasemkrj5dESNAtEBqIdJ' \
            'nRnb0YfLm+u3FezXsUV2vkp1fTM6ux6+n41dXIWRas+EYwTmPC4ISSO5vkPQbDJ3R/AYsh4wgsGtCIaHiJNsF0/0wOn85vlIWoT/qHxcv' \
            'R+PLj3+q47496D+jdKZMW8G40oEpUyZq71Q+MdN+c335sT7geIHkUoASBBx0Jz8SaS6CWIGTjbtxngI6f+DAUCUSCiuJ8x1aQ92oV1ORr' \
            'Kh7T72CZTKRggxFOdHa9+r19NWb6V77MHQ7z3ByIystIAoE4r7GhmZ+onXjK2nc/q3Rviu8I9n/1FA2En7gFvT7igzWewteg0Nyke3QHb' \
            'EbUPq69yZ8RyRpgHQrLJDd0JJHOyKQSZHlrrZ0PNYrQouVXhFprx5TdiFqmxoqgSxDeAszw/KjTCgmykyjqw4EviHK1t+jw/9LdNi/Mfb' \
            'tCS9d9b4P0eZqKdcHon/N0j6M31V0tN578D0rjxHjqIC0gOUElbIMlz7nSPWI5D0YVM/Hem9V/bcflTkQENxmua+Jj3zChxuF2W3qL+N' \
            'xnc9uUWAFngXU7aCOMluuvb0qQXjOSlEfDjxADdVoqrhWzTScpyQYbC1KtsZi7SZ4AA8Qzhl3e5LlkIYK5O8uXP3U++skts7tS+yXJW6Z' \
            'zzzuyI+N1Ao6u2Ur2Ccb98f3Ws+xsXuzq+4gwSqKBxG7LVK3kUc5X82sKhpAv9AZnLyQTk/QdIUh9smeoUjwHZAvT+L8WJRcfkjVzhM1h' \
            '+jCgoNrC3tw4I2sSCPFt4WjV5vU9T2Idyu5ryRs/BWCXIX5mhbyz/mUJ82i+KuhBox3Gx/ajfoPAhs8cM0I5eTOLfQdLrRNQvJEmrRzbE' \
            'YPfMMeBM4/2xPd9emQMZy2HUnXF5evRufNuBLrrSBESeA0oFualjizE7D9vh1fvLu+mLx+dTW5OKx3efnX2f3F+Xi6v/u3FHzqXkOg+U5' \
            'HWjmMPKHdgTwdTceT6fhsYg+9vcvYXOX6RcAnsQtyLLGS0yszUTTGDwaIWPA7yb4UktU78TJpZ6R5kwQFA+RxS8jqctm5tHbj/sjAdj+6' \
            'mry7uJ6Onl+2BCtHkCC4+ldMje9SW0Edl+QtN+PDgfuz618BUEsDBAoAAAAIAKKGo04Kn8n72AYAAINUAAAbAAAAc3VydmV5XzkxNTMyN' \
            'V9yZXNwb25zZXMubHNy7ZzpbtpKFMe/9yly8z3FKzZXlIqwBDCLy2qoqqsBD8Z4wwsG/AZ9jPuxuo+RF7uENHW2oWZKEBolQgmOzxjkn/' \
            '5nzjLj7Oe1ZV6E0PN1x/50SX+kLi+gPXFU3dY+Xfa65Svx8nPuQ1Z1JksL2kEuW9ct2Fl6IdwUnUl3s4C5NvQXju1DP5t6eTJbvO7fXz3' \
            'HpNlsKj7MmsDWlkCDfvw2B+1s6tdB/HZr4j18Si471aGpPvy1gQVzuppNxUePTgSOcXfJV8/5y7GlByoIIMLABH6w2H46anwAvODhGyJs' \
            'MjTPMrxCK/TvDJjfGbD7DRiF+50B/8Qg9XAbPWd1/zuX1dVc9q+vhWK+m//KCd++ba3u/rW7i/EZxfPtyNOAVilSecPfmf00ie9pbE5nR' \
            'OqKorevC4r6e/faDXls+3Cr41HMzib+/5O7HZtB+/5aT8/+E9/3R1f8SP362Q16YhUfMI+GUMz2e6evKO7pV39iHB+w8cgMT3Ms+gPZeN' \
            'gWXDwMPLHbnYoP+Nhu/Mxueyq1I/gCI8OgMEq2UDR7Qt8f3NSWqwzRGGnximKvKPFQjPThCKtOkJRiASyem6JBskg9TmHYcuY3I1vaAId' \
            'uEQ2Soa5oBkePHM8IZ6FHFoVRXw0m6Y27aEcKlZ42iMaIq0fucIR1YI3VpBwbemKQNIrjdXMNpHUjyHRaotDKk80xc0UJ29cJ/GoFmqaT' \
            'EOPA8Uw1uSSRJBeKUglCYyR36Oqw+E7yOCTH5u2/Sf3qS9M9HDmkaw0Dc94D8AYUoJKXiQcpnibUKXl+AC/ydrByvCAh0dEK6shBe6IfF' \
            'NrRJkyPZmJYrXJWc9wmHi2ORjESka3wfiTX6HNTNEekRDtCG9SBI8yacFyc1N45Hovj84gGjTF57MOKKIzauD0Ck7E06JRUoXJDNMa72g' \
            'BOLkKzmfNIRXgUxXQ4nOVbosvlN5w6rRJNcStGmsKYL3kMhOY0MUX4ooqABolUY1ky+V5JYlqdbqk/7hLNkaF2lbqDneqeDzudFDkkwo' \
            'GgNSym2V5YfVauWGQjPG2xtaTb/gFRa2KYGRRLI3KackEtAS8fGT7haYi4mxxPkoa8EUcmjRSlra3ldN4begAYrkg2SMz5EcOvWkljVfu' \
            'AMh2Fgihoo6UaihrkBTaQObIhnk6NSzshRHUJkyccSJ+6sUy7rHSHTc11qxEgmuLd/MjjNT+oM/KrNLJ0rjHdCR0qX6J0p2126kTDxJU' \
            'kRqCTXJJwuU4+PSIbkulVdWzJsNI326pcIztmJSB9pJENkMiWpx7dHLOaBnvl9ynySHq057f/JVXkJjlGZI1cHoldRWpExVpVoUKPeIw4' \
            'nWWMcPUP2h/gwPYHg6wPqNFmwhUqRTAreMUWJJvt6VIRDVhJfa0KzUOcLbIDModFNnLgNqcsaxEIyCZ5OpXKnm5BD1zcLSBdQj/x4qwO1' \
            'Ja2ih63p5iHTDmVtTYQZYtiBxXQ5cmOb7GTFVbkz6I9QiPbI5zY6dca+ci4duRS3yEaI65SceLboyNkkGWDlcIKX7ShS5VLmmGkyUaIOW' \
            '1iRLa3Pxa+bjpJ883ooDQFWY7NXG9gqPbHXaV+M5wVyIZ5Oj1OkgZAyREiSwYFBoByNJqrG2Hqj8x3hK8gxFj8CszF7E1qBiwyxrE6HW6' \
            '4ZqjZlKrcDDZkk8T0rBgkYZB40WRwkFdFZpbTydq/1pX1tAzT8vI9yjkSyDfLLDlksHPNu3NjUbuRQR6uMi7RJP9gDQGN0SPpJQ11igd0' \
            'u2gkSa8PynW9S+UrurTe8ESTPGGN4Pb7QWHr6KCZEtntqrlMswuKTNiQmKBrkA0Tc6bEkeRBLLtgmTydRAY9M8Ob8w7vDtJc4GjveymPh' \
            'PL2e+JyXfcQTTJITbIZduG1Ru5UdAMJkL1++YQgX6GDAvnK/tk9zhXZulRNFtTarlHPeCYssWSDPJ1zfaseNIcE2YWqVBNba4MeOpFLdo' \
            'PrD2rmOAtgW/bzmBTpXVfPt17u0SSyD11eDUaZQXGyLIRuqJG9VuunJk+0OeSEO/E4JN6W0DcXopCXuJbOFwSi8WKnmVyaFs+hNcIi+9B' \
            'jQaD7LRiVw4ZdDySyMVKYGM+lSckim5TNudzLT9r1Zr2nS9eVd4yvqpHmKYxNlQkxPm+g7HGqSDUGfXnm99wlBQUbQrIrPvhOleYy57O+' \
            'mUU2KqMOb1jAY6R2zWZMshfG4j+pB0uTx3etPLJIYNQL1nzMVTUNVO1Sh2yMmJo8l03OHHKC/FKQ+iWd8df1Ca2QvjkW37OyZ/EYOw7pU' \
            '62IG9cjxdczRsc2tHeMx8N4pAkydf+EydSjR3imfj1Q9MP/UEsDBAoAAAAIAKKGo06JJeyIvAUAAPpMAAAYAAAAc3VydmV5XzkxNTMyNV' \
            '90b2tlbnMubHN07ZxZj9o6GIbv+ys4cz+HbGRBlIp9CUtKAgSq6sgkJoRsZCFAfn0hzAxDq0PPxXEtSyPNhR1/2eZx8Pe+dlL5cvTcQgq' \
            'j2A78z0/039RTAfpGYNq+9flpqrWfxacv1U8VMzD2HvST6qdCZWB7UN1HKTw1A0M77WBVCxzox5Xiry3n8GZ9dj18leHZSvFWPbe5wLf2' \
            'wILxuXKrVaFfKb5VzmHF93GVJD9bvsfahq6ZF1/KPvBgNbHNSvFW/al1B6LENuwd8JN/Hgau7ShOLqUHMS74bQj0gO3+rj1OQLKPH0TlN' \
            '/3wQq7/oQchKxcYjmvHCXx01/GZ8oPmCHq2b54J/rcwI9g/jDMCb+fCx1e0j2HswvWjw6TAtc11FHi/izlfzUMY3u6XLvFSvXa4KDi8dL' \
            'dzKS+c+6NtVit/fWs0a1rtG/39e7VSvGy6Nr51ouLLhtce81rP8d9Vrn3hdsixnB/zfdvLiS994hZXHx2BfBwmkjoWhXHteiF5yDX8guw' \
            'WPcrb4+sznd/QO7I/h9213YfnhG/x1F38tfG6wxvqWzBD0eIzJTzTUoHmyiyX73uLu+73iv/nc7xtz3EUX3n8GxgGI5idrneT1FkqKt1b' \
            'NAkDUypTDEowLD4wy1PKLzdi2utx3mg1IQ8MixIMhw+MKkzAAATCZgRXTaP/AeYOTAkfmLbslqYtmRmrWmu20ggCw1IFWigzFEowPD4wT' \
            'haMlIbZAlEtc2KFGDDnP6ZA82VaQAlGwAdGsJZ7MxUtWBLYROGIA8OIKMGI+MBYjGbQqf4149WJqw6IA8Mi/SmT8IHJfGUd0aMVa1lw2i' \
            'bviWGRpss0hY+MshQ1XR5mzX5Pp9KIJDJsgRLLLI+UDEbtv4VNNgvgIgJtKwMJeWSQjjI0RvHPieqsPzwnZfVAac0CwshIZQrpMENjVP' \
            '9S/QRT86xi9EFnsWl8kLkng1H+NxgA2tlya56Edbx0ySJDU2Ua7TiDUf+vjWNct/Xjug15ZU/Yr9mFDFKZSWM0AKIZaA9sjap1bfl4KhF' \
            'HhkGbNWN0ADZOtC0FpXDOc0lgSR9k7slgtABYid1F42W4FsNEBh3yyCC1mWmMHoDsC013Kszieae/P5D2zNBlCuk4w2D0AOzD3OBP4W6S' \
            '6RS/HpJHBqnSZDB6AHaauNspgB3QgHqNpCkAhsr1DFoyGD0APl1samMx5Gonzlz3SCLDFCgBcQbAYPQA5r51VPhatIgAcEKRPDJo18xg9' \
            'AD4Q2/lKbA7cyem0vfIIkPziN0ZBqMHYGYng2t0m2DTiJpj+EHmngxGD+Cgs8JXaxFS7ZblODx5ZGikZDB6AJ6qcosjQ23WVLczP32QuS' \
            'eD0QPoh8xIA00mHcpMojnEkUGcAWD0AEyXBf1J6AykyIUtljwySD0AFqMH0D7Ml9K8aewbaZhagAwy0jPFPdPUZbYZMRmMHsBKEOjZGGb' \
            'tdOgPEpkkMuKFTAlpbsZi9ABGW2VaMyaD0WBqy/UuYWSk8oviQEUGoweQqSXHAxEjT/o+4xKiNHMyDHdZbF5CmgGwGD2ANUzHwbaz9OUT' \
            'COgxYWRExEqTxegBWKvJEhgrea62TKFLyMzZlQz/B8YZjB7AyXP9tq4tRlYY9jKScjNGymcB0L5shtED0I/WXFQ8ip13gVYiZMH5K5nLO' \
            'IN0VROLUWlq0JT74vjo0IsgCwlxNN/I8GUa6TPDYVSaY2Hm7kShJnNju9QQCCJzed+sVGbRvqGJUWkmM2UTT8M9BQUfQkLWm70ngzRr5j' \
            'Aqza8Nedaymfg4MGidlHc035FBq2c4jErTy7jVINNjW3JU37E+yNyTwag09Sj2s8gCVrdJ1ZyYMDLnDACpnuEwKs25YA09ZjTZeTNW6ZL' \
            'kzvwRMhiVZr0Ubp1dv6OAGjxIIXlk0GbNGOc0nUHD2664nmWBnt9SiSPzv8xp5oX8g2HF1y+GVYq375j9AFBLAQIUAAoAAAAIAKKGo073' \
            '7UEwugoAAKk9AAARAAAAAAAAAAAAAAAAAAAAAABzdXJ2ZXlfOTE1MzI1Lmxzc1BLAQIUAAoAAAAIAKKGo04Kn8n72AYAAINUAAAbAAAAA' \
            'AAAAAAAAAAAAOkKAABzdXJ2ZXlfOTE1MzI1X3Jlc3BvbnNlcy5sc3JQSwECFAAKAAAACACihqNOiSXsiLwFAAD6TAAAGAAAAAAAAAAAAA' \
            'AAAAD6EQAAc3VydmV5XzkxNTMyNV90b2tlbnMubHN0UEsFBgAAAAADAAMAzgAAAOwXAAAAAA=='

        second_survey = \
            'UEsDBAoAAAAIAKKGo0737UEwugoAAKk9AAARAAAAc3VydmV5XzkxNTMyNS5sc3PtW21z27gR/n6/AvWXtDM+Ky9Np83ofFVs56oZx8lZ' \
            'StLMzY0GIiEJNUXIIChbl8l/v8ULARCkQCptr0l69+FCYZ8FFosHi12QHn5/v87QlvCCsvy7o0cnD48QyROW0nz53dGb6Ytv/3r0/ek3w' \
            '5Ql5Zrk4vQbNLykazIp+Zbszlky3W3Iqf41HDQlAD9//lZ3f/r4L0+GA/cTZBnOlyVekgJ+uF+nJB8O7A+ADXzccMlZudEaC0qyVD2a5x' \
            'yvyemSpsOB+xlIi6hUdT6Tj50gxlPCI6iUFAmnGwFzjaCqqUUgHOcpW9NfsOxqpgaPGkcyssV5EnZpfmrPcXZn/AZP6gEcS9PT4R9+Ojs' \
            'fTUc/Pfr559PhQDZpYeEL//bo6ZPHTxWisAjnOgccp0AauqCJsl136WC+nvJmY3hPpMGeUwemyTLFKhM9kkchNdGmGwfWhMpnumU4qLyyz' \
            'z2P/yPueUF5IZCSHOCbx5+Hb9SD2pEDuyWHtyUpZB+x/Xkb3YEbzIEzszioYxNHpQICU0xMRRaTVzOMTYGTZUS8IllsAzOxisaVNawVFoz' \
            'vehjZGaR6hJ8iwRmZxZcD/jdLyQKXmYgFsj2RqTY7lpYZaQnAneHrthm+bu3uc6xymIcK40l6b+VYoJT0ctIrJRX6LFRiSS8n56TYwG6h' \
            '84zQVGMVwEzJLKPDXzs8qgdXlJfrOeHP9MQrRTN7IGS1nyX7qmdFtdBY3agBlmsO9F6BnKBuaRirHtbMqYWrvrGp4l/YqW03MI+DDagvM' \
            'xGv4mK4kk6w9yS4bZ4E/3umnXcwDSe3JS2oXAZYOdKDayOngaTKsBCc5cvTZ2ChfhrOOQIufV6Ue/TVU+7JZ0K5ruBWlPN/kUT0CmyvMR' \
            'c0oRuci/bANpxL4s1PPy+yPfnqyfbn34xsYU5dJ9u0g2wLmUv/aBaiB+F07l21I7ZAwAu0qLXmmHLyeRHuS49u4AKb4UWKrRq9nn4hFCx' \
            'IAofrARycKIUvj4SPv14SelWtX8s6V2AhOJ2Xgnx6iWu7iGC2OCtj8j2F279XJVnDHGRF09SsoJNqtDIx7Ew3flrq/BsPH6ZR/53hWwhV' \
            '59CwUFemMTrFrztwuqax6whyv4EIUsTqdwHZl0rxO0Yha0yzGChn+W5NfyExexf4XrCYnPE1jt0jFHhLBAVzlrFJCbLeZPE59bj9wGmqK' \
            'iCczewtdOzSFwYEb65jFzylPCfYDY0Om2XsDuI7LUT0/kbhpD9imFIwnUPP1EJ3QDlJgS5JFCZHheNnG70Eo7nAeXFHeMxhkPGnaWyGnC' \
            'xKHuPcppxnNIGZCXAWPHRClxxvVjFYBh1paOwWT6yzru1QkDyFEx7O8zXuuDMU7AaOI+2ujXxDAgsfvynDRUGKQr6Vic1Fkg1vRLLCcZA' \
            'aP9bRnJVgz6wzAlShzbuNjnWr+jO3YCQaFhQyZ64wjKLVfOCEX4pVbIFW7O7envMdQHXLTfNFbFiJy5lexw7YLezJhKWxJdY+h1DXDdpw' \
            'lgAdICZ2QnGSwL+i4x68hl2xIhYPatgNELMvFijOd12vyGoaQNUux96RLGFRl0kUOGwJvIuZWhGD5im5j+ByvKVLRcmUZDh2L58DK3dzh' \
            'nn0PJfRFYKwwAsI/jCVTUY6XLRkbJkRDKfUTobAQuyi7zACON7QGxKa3ZlJdpdWKmXw7hPlT4hrXJYYOqdSAA+s9rjTSHhePHry96VsPQ' \
            'FHOCUNNJo26QiLHk+ioSr1qOoknWc4nR+Ujmmtyg+baYR9+yJTDZqEwyFNcaIrwUp6WJ3Uln9UE7DJRmibE2igzThCoBOY0fy0o+HNmtB' \
            'TkK4IS0knMMAgCQmLuYbcqVUJScMeX+aZIxOTVtuVoKqdXXYSYmsyDddZSgg0rVXpKfOUEGJazaBBptIYOJT7ajpraVcxMsMsm72EYE9ib' \
            'g2qHCZcPScw+yBIZEJ8Q252RHtSE2rvg5k1dXlOY1U9kWO6TnfaqG4kFqqTnhakEWign/l0xKYaVGsHCc7Ab65nMwPfazp18erLp85VRm' \
            'aWppbCNBamLnUqNplxGs+thhM6hSqracRBX+bgVXbj4P+0cCvz/esSmHCEhtyNYo76tllXIgeuTvw2tJWZewL/5N/3NlMLtUKQAoQqod' \
            'go2WwgnLIn8QJbS07QGnbbcLqbtjwhtLUV06qu84b9F2juYqO643BnGBGiOjr3XXoolayY6YeOLxAqcJ8PGips16ceFtjvUy4LN9QT5D5' \
            '6i1HBIXb2hcYrYR92oMkqHM1ovqWCzOR7u0OV+uM5gaQpPXAQrXQIXqcpBw/TeeMSaJhT78BxjFYv7kEu130jVqFt+S3Puj6l90yl0zP/' \
            'JOqayz69nirVWVgcMo5V6uMEnUd2Og18hZNV2wVKd+3TiE3tpVATFujvLQOaiEAzePekX2fqr2/rHfivoNoi2iCUeeGrITOxqtEOEaetLT' \
            'ZMI+S4yYxlo375LxjaVJ8GCIJojjAqWmbZ7C0ynPfVDMEcfXgxvp5Mr0YvLz4em09azD87VqIVFDFoTkiOtHIasemkrj5dESNAtEBqIdJ' \
            'nRnb0YfLm+u3FezXsUV2vkp1fTM6ux6+n41dXIWRas+EYwTmPC4ISSO5vkPQbDJ3R/AYsh4wgsGtCIaHiJNsF0/0wOn85vlIWoT/qHxcv' \
            'R+PLj3+q47496D+jdKZMW8G40oEpUyZq71Q+MdN+c335sT7geIHkUoASBBx0Jz8SaS6CWIGTjbtxngI6f+DAUCUSCiuJ8x1aQ92oV1ORr' \
            'Kh7T72CZTKRggxFOdHa9+r19NWb6V77MHQ7z3ByIystIAoE4r7GhmZ+onXjK2nc/q3Rviu8I9n/1FA2En7gFvT7igzWewteg0Nyke3QHb' \
            'EbUPq69yZ8RyRpgHQrLJDd0JJHOyKQSZHlrrZ0PNYrQouVXhFprx5TdiFqmxoqgSxDeAszw/KjTCgmykyjqw4EviHK1t+jw/9LdNi/Mfb' \
            'tCS9d9b4P0eZqKdcHon/N0j6M31V0tN578D0rjxHjqIC0gOUElbIMlz7nSPWI5D0YVM/Hem9V/bcflTkQENxmua+Jj3zChxuF2W3qL+N' \
            'xnc9uUWAFngXU7aCOMluuvb0qQXjOSlEfDjxADdVoqrhWzTScpyQYbC1KtsZi7SZ4AA8Qzhl3e5LlkIYK5O8uXP3U++skts7tS+yXJW6Z' \
            'zzzuyI+N1Ao6u2Ur2Ccb98f3Ws+xsXuzq+4gwSqKBxG7LVK3kUc5X82sKhpAv9AZnLyQTk/QdIUh9smeoUjwHZAvT+L8WJRcfkjVzhM1h' \
            '+jCgoNrC3tw4I2sSCPFt4WjV5vU9T2Idyu5ryRs/BWCXIX5mhbyz/mUJ82i+KuhBox3Gx/ajfoPAhs8cM0I5eTOLfQdLrRNQvJEmrRzbE' \
            'YPfMMeBM4/2xPd9emQMZy2HUnXF5evRufNuBLrrSBESeA0oFualjizE7D9vh1fvLu+mLx+dTW5OKx3efnX2f3F+Xi6v/u3FHzqXkOg+U5' \
            'HWjmMPKHdgTwdTceT6fhsYg+9vcvYXOX6RcAnsQtyLLGS0yszUTTGDwaIWPA7yb4UktU78TJpZ6R5kwQFA+RxS8jqctm5tHbj/sjAdj+6' \
            'mry7uJ6Onl+2BCtHkCC4+ldMje9SW0Edl+QtN+PDgfuz618BUEsDBAoAAAAIAKKGo04Kn8n72AYAAINUAAAbAAAAc3VydmV5XzkxNTMyN' \
            'V9yZXNwb25zZXMubHNy7ZzpbtpKFMe/9yly8z3FKzZXlIqwBDCLy2qoqqsBD8Z4wwsG/AZ9jPuxuo+RF7uENHW2oWZKEBolQgmOzxjkn/' \
            '5nzjLj7Oe1ZV6E0PN1x/50SX+kLi+gPXFU3dY+Xfa65Svx8nPuQ1Z1JksL2kEuW9ct2Fl6IdwUnUl3s4C5NvQXju1DP5t6eTJbvO7fXz3' \
            'HpNlsKj7MmsDWlkCDfvw2B+1s6tdB/HZr4j18Si471aGpPvy1gQVzuppNxUePTgSOcXfJV8/5y7GlByoIIMLABH6w2H46anwAvODhGyJs' \
            'MjTPMrxCK/TvDJjfGbD7DRiF+50B/8Qg9XAbPWd1/zuX1dVc9q+vhWK+m//KCd++ba3u/rW7i/EZxfPtyNOAVilSecPfmf00ie9pbE5nR' \
            'OqKorevC4r6e/faDXls+3Cr41HMzib+/5O7HZtB+/5aT8/+E9/3R1f8SP362Q16YhUfMI+GUMz2e6evKO7pV39iHB+w8cgMT3Ms+gPZeN' \
            'gWXDwMPLHbnYoP+Nhu/Mxueyq1I/gCI8OgMEq2UDR7Qt8f3NSWqwzRGGnximKvKPFQjPThCKtOkJRiASyem6JBskg9TmHYcuY3I1vaAId' \
            'uEQ2Soa5oBkePHM8IZ6FHFoVRXw0m6Y27aEcKlZ42iMaIq0fucIR1YI3VpBwbemKQNIrjdXMNpHUjyHRaotDKk80xc0UJ29cJ/GoFmqaT' \
            'EOPA8Uw1uSSRJBeKUglCYyR36Oqw+E7yOCTH5u2/Sf3qS9M9HDmkaw0Dc94D8AYUoJKXiQcpnibUKXl+AC/ydrByvCAh0dEK6shBe6IfF' \
            'NrRJkyPZmJYrXJWc9wmHi2ORjESka3wfiTX6HNTNEekRDtCG9SBI8yacFyc1N45Hovj84gGjTF57MOKKIzauD0Ck7E06JRUoXJDNMa72g' \
            'BOLkKzmfNIRXgUxXQ4nOVbosvlN5w6rRJNcStGmsKYL3kMhOY0MUX4ooqABolUY1ky+V5JYlqdbqk/7hLNkaF2lbqDneqeDzudFDkkwo' \
            'GgNSym2V5YfVauWGQjPG2xtaTb/gFRa2KYGRRLI3KackEtAS8fGT7haYi4mxxPkoa8EUcmjRSlra3ldN4begAYrkg2SMz5EcOvWkljVfu' \
            'AMh2Fgihoo6UaihrkBTaQObIhnk6NSzshRHUJkyccSJ+6sUy7rHSHTc11qxEgmuLd/MjjNT+oM/KrNLJ0rjHdCR0qX6J0p2126kTDxJU' \
            'kRqCTXJJwuU4+PSIbkulVdWzJsNI326pcIztmJSB9pJENkMiWpx7dHLOaBnvl9ynySHq057f/JVXkJjlGZI1cHoldRWpExVpVoUKPeIw4' \
            'nWWMcPUP2h/gwPYHg6wPqNFmwhUqRTAreMUWJJvt6VIRDVhJfa0KzUOcLbIDModFNnLgNqcsaxEIyCZ5OpXKnm5BD1zcLSBdQj/x4qwO1' \
            'Ja2ih63p5iHTDmVtTYQZYtiBxXQ5cmOb7GTFVbkz6I9QiPbI5zY6dca+ci4duRS3yEaI65SceLboyNkkGWDlcIKX7ShS5VLmmGkyUaIOW' \
            '1iRLa3Pxa+bjpJ883ooDQFWY7NXG9gqPbHXaV+M5wVyIZ5Oj1OkgZAyREiSwYFBoByNJqrG2Hqj8x3hK8gxFj8CszF7E1qBiwyxrE6HW6' \
            '4ZqjZlKrcDDZkk8T0rBgkYZB40WRwkFdFZpbTydq/1pX1tAzT8vI9yjkSyDfLLDlksHPNu3NjUbuRQR6uMi7RJP9gDQGN0SPpJQ11igd0' \
            'u2gkSa8PynW9S+UrurTe8ESTPGGN4Pb7QWHr6KCZEtntqrlMswuKTNiQmKBrkA0Tc6bEkeRBLLtgmTydRAY9M8Ob8w7vDtJc4GjveymPh' \
            'PL2e+JyXfcQTTJITbIZduG1Ru5UdAMJkL1++YQgX6GDAvnK/tk9zhXZulRNFtTarlHPeCYssWSDPJ1zfaseNIcE2YWqVBNba4MeOpFLdo' \
            'PrD2rmOAtgW/bzmBTpXVfPt17u0SSyD11eDUaZQXGyLIRuqJG9VuunJk+0OeSEO/E4JN6W0DcXopCXuJbOFwSi8WKnmVyaFs+hNcIi+9B' \
            'jQaD7LRiVw4ZdDySyMVKYGM+lSckim5TNudzLT9r1Zr2nS9eVd4yvqpHmKYxNlQkxPm+g7HGqSDUGfXnm99wlBQUbQrIrPvhOleYy57O+' \
            'mUU2KqMOb1jAY6R2zWZMshfG4j+pB0uTx3etPLJIYNQL1nzMVTUNVO1Sh2yMmJo8l03OHHKC/FKQ+iWd8df1Ca2QvjkW37OyZ/EYOw7pU' \
            '62IG9cjxdczRsc2tHeMx8N4pAkydf+EydSjR3imfj1Q9MP/UEsDBAoAAAAIAKKGo06JJeyIvAUAAPpMAAAYAAAAc3VydmV5XzkxNTMyNV' \
            '90b2tlbnMubHN07ZxZj9o6GIbv+ys4cz+HbGRBlIp9CUtKAgSq6sgkJoRsZCFAfn0hzAxDq0PPxXEtSyPNhR1/2eZx8Pe+dlL5cvTcQgq' \
            'j2A78z0/039RTAfpGYNq+9flpqrWfxacv1U8VMzD2HvST6qdCZWB7UN1HKTw1A0M77WBVCxzox5Xiry3n8GZ9dj18leHZSvFWPbe5wLf2' \
            'wILxuXKrVaFfKb5VzmHF93GVJD9bvsfahq6ZF1/KPvBgNbHNSvFW/al1B6LENuwd8JN/Hgau7ShOLqUHMS74bQj0gO3+rj1OQLKPH0TlN' \
            '/3wQq7/oQchKxcYjmvHCXx01/GZ8oPmCHq2b54J/rcwI9g/jDMCb+fCx1e0j2HswvWjw6TAtc11FHi/izlfzUMY3u6XLvFSvXa4KDi8dL' \
            'dzKS+c+6NtVit/fWs0a1rtG/39e7VSvGy6Nr51ouLLhtce81rP8d9Vrn3hdsixnB/zfdvLiS994hZXHx2BfBwmkjoWhXHteiF5yDX8guw' \
            'WPcrb4+sznd/QO7I/h9213YfnhG/x1F38tfG6wxvqWzBD0eIzJTzTUoHmyiyX73uLu+73iv/nc7xtz3EUX3n8GxgGI5idrneT1FkqKt1b' \
            'NAkDUypTDEowLD4wy1PKLzdi2utx3mg1IQ8MixIMhw+MKkzAAATCZgRXTaP/AeYOTAkfmLbslqYtmRmrWmu20ggCw1IFWigzFEowPD4wT' \
            'haMlIbZAlEtc2KFGDDnP6ZA82VaQAlGwAdGsJZ7MxUtWBLYROGIA8OIKMGI+MBYjGbQqf4149WJqw6IA8Mi/SmT8IHJfGUd0aMVa1lw2i' \
            'bviWGRpss0hY+MshQ1XR5mzX5Pp9KIJDJsgRLLLI+UDEbtv4VNNgvgIgJtKwMJeWSQjjI0RvHPieqsPzwnZfVAac0CwshIZQrpMENjVP' \
            '9S/QRT86xi9EFnsWl8kLkng1H+NxgA2tlya56Edbx0ySJDU2Ua7TiDUf+vjWNct/Xjug15ZU/Yr9mFDFKZSWM0AKIZaA9sjap1bfl4KhF' \
            'HhkGbNWN0ADZOtC0FpXDOc0lgSR9k7slgtABYid1F42W4FsNEBh3yyCC1mWmMHoDsC013Kszieae/P5D2zNBlCuk4w2D0AOzD3OBP4W6S' \
            '6RS/HpJHBqnSZDB6AHaauNspgB3QgHqNpCkAhsr1DFoyGD0APl1samMx5Gonzlz3SCLDFCgBcQbAYPQA5r51VPhatIgAcEKRPDJo18xg9' \
            'AD4Q2/lKbA7cyem0vfIIkPziN0ZBqMHYGYng2t0m2DTiJpj+EHmngxGD+Cgs8JXaxFS7ZblODx5ZGikZDB6AJ6qcosjQ23WVLczP32QuS' \
            'eD0QPoh8xIA00mHcpMojnEkUGcAWD0AEyXBf1J6AykyIUtljwySD0AFqMH0D7Ml9K8aewbaZhagAwy0jPFPdPUZbYZMRmMHsBKEOjZGGb' \
            'tdOgPEpkkMuKFTAlpbsZi9ABGW2VaMyaD0WBqy/UuYWSk8oviQEUGoweQqSXHAxEjT/o+4xKiNHMyDHdZbF5CmgGwGD2ANUzHwbaz9OUT' \
            'COgxYWRExEqTxegBWKvJEhgrea62TKFLyMzZlQz/B8YZjB7AyXP9tq4tRlYY9jKScjNGymcB0L5shtED0I/WXFQ8ip13gVYiZMH5K5nLO' \
            'IN0VROLUWlq0JT74vjo0IsgCwlxNN/I8GUa6TPDYVSaY2Hm7kShJnNju9QQCCJzed+sVGbRvqGJUWkmM2UTT8M9BQUfQkLWm70ngzRr5j' \
            'Aqza8Nedaymfg4MGidlHc035FBq2c4jErTy7jVINNjW3JU37E+yNyTwag09Sj2s8gCVrdJ1ZyYMDLnDACpnuEwKs25YA09ZjTZeTNW6ZL' \
            'kzvwRMhiVZr0Ubp1dv6OAGjxIIXlk0GbNGOc0nUHD2664nmWBnt9SiSPzv8xp5oX8g2HF1y+GVYq375j9AFBLAQIUAAoAAAAIAKKGo073' \
            '7UEwugoAAKk9AAARAAAAAAAAAAAAAAAAAAAAAABzdXJ2ZXlfOTE1MzI1Lmxzc1BLAQIUAAoAAAAIAKKGo04Kn8n72AYAAINUAAAbAAAAA' \
            'AAAAAAAAAAAAOkKAABzdXJ2ZXlfOTE1MzI1X3Jlc3BvbnNlcy5sc3JQSwECFAAKAAAACACihqNOiSXsiLwFAAD6TAAAGAAAAAAAAAAAAA' \
            'AAAAD6EQAAc3VydmV5XzkxNTMyNV90b2tlbnMubHN0UEsFBgAAAAADAAMAzgAAAOwXAAAAAA=='

        if side_effect:
            mockServer.return_value.export_survey.side_effect = [first_survey, second_survey]
        else:
            mockServer.return_value.export_survey.return_value = first_survey

    def test_GET_experiment_export_returns_zip_file(self):
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.get('Content-Disposition'), 'attachment; filename=%s' % smart_str('experiment.zip'))
        # get zipped file to test against its content
        file = io.BytesIO(response.content)
        zipped_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zipped_file.testzip())

    def test_GET_experiment_export_returns_json_inside_zip_file(self):
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        zipped_file = zipfile.ZipFile(io.BytesIO(response.content), 'r')
        json_file = zipped_file.namelist()[0]  # There's only one file archived
        self.assertEqual('experiment.json', json_file)

    # TODO: NES-946: see if it's deprecated or have to check for all user objects, not only one
    def test_GET_experiment_export_returns_json_file_without_user_object(self):
        temp_dir = tempfile.mkdtemp()
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        zipped_file = zipfile.ZipFile(io.BytesIO(response.content), 'r')
        zipped_file.extractall(temp_dir)
        with open(os.path.join(temp_dir, ExportExperiment.FILE_NAME_JSON)) as file:
            data = json.loads(file.read().replace('\n', ''))
            self.assertIsNone(next((item for item in data if item['model'] == 'auth.user'), None))

        shutil.rmtree(temp_dir)

    def test_remove_all_auth_user_items_before_export(self):
        temp_dir = tempfile.mkdtemp()

        patient = UtilTests.create_patient(changed_by=self.user)
        user2, passwd2 = create_user(Group.objects.all())
        UtilTests.create_telephone(patient, changed_by=user2)
        user3, passwd3 = create_user(Group.objects.all())
        medical_record = UtilTests.create_medical_record(user3, patient)
        UtilTests.create_diagnosis(medical_record)

        research_project = ObjectsFactory.create_research_project(self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        group = ObjectsFactory.create_group(experiment)
        subject = ObjectsFactory.create_subject(patient)
        ObjectsFactory.create_subject_of_group(group, subject)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        zipped_file = zipfile.ZipFile(file_path, 'r')
        zipped_file.extractall(temp_dir)
        with open(os.path.join(temp_dir, export.FILE_NAME_JSON)) as file:
            data = file.read().replace('\n', '')

        deserialized = json.loads(data)
        self.assertIsNone(
            next((index for (index, dict_) in enumerate(deserialized) if dict_['model'] == 'auth.user'), None)
        )

        shutil.rmtree(temp_dir)

    def test_diagnosis_classification_of_diseases_references_points_to_natural_key_code(self):
        temp_dir = tempfile.mkdtemp()

        patient = UtilTests.create_patient(changed_by=self.user)
        medical_record = UtilTests.create_medical_record(self.user, patient)
        diagnosis = UtilTests.create_diagnosis(medical_record)

        self._create_minimum_objects_to_test_patient(patient)

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        zipped_file = zipfile.ZipFile(file_path, 'r')
        zipped_file.extractall(temp_dir)
        with open(os.path.join(temp_dir, export.FILE_NAME_JSON)) as file:
            data = file.read().replace('\n', '')

        deserialized = json.loads(data)
        self.assertIsNone(
            next((index for (index, dict_) in enumerate(deserialized) if dict_['model'] == 'auth.user'), None)
        )

        deserialized = json.loads(data)
        index = next((index for (index, dict_) in enumerate(deserialized) if dict_['model'] == 'patient.diagnosis'),
                     None)
        code = deserialized[index]['fields']['classification_of_diseases'][0]
        self.assertEqual(diagnosis.classification_of_diseases.code, code)

        shutil.rmtree(temp_dir)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_experiment_has_file_creates_corresponding_dir_file_in_experiment_zip_file(self):
        self.experiment.ethics_committee_project_file = SimpleUploadedFile('file.bin', b'binnary content')
        self.experiment.save()

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        zipped_file = zipfile.ZipFile(io.BytesIO(response.content), 'r')
        file_path = self.experiment.ethics_committee_project_file.name
        self.assertTrue(
            file_path in [subdir for subdir in zipped_file.namelist()],
            '%s not in %s' % (file_path, zipped_file.namelist()))

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    def test_experiment_has_not_file_does_not_creates_corresponding_dir_file_in_experiment_zip_file(self):
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zipped_file:
            self.assertTrue(
                ExportExperiment.FILE_NAME_JSON in [file for file in zipped_file.namelist()],
                '%s not in %s' % (ExportExperiment.FILE_NAME_JSON, zipped_file.namelist()))
            self.assertEqual(1, len(zipped_file.namelist()))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_eeg_has_data_collection_files_creates_corresponding_file_paths_in_zip_file(self):
        rootcomponent = ObjectsFactory.create_component(self.experiment, 'block', 'root component')
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = ObjectsFactory.create_subject_of_group(self.group, subject)
        eeg_set = ObjectsFactory.create_eeg_setting(self.experiment)
        component = ObjectsFactory.create_component(self.experiment, 'eeg', kwargs={'eeg_set': eeg_set})
        component_configuration = ObjectsFactory.create_component_configuration(rootcomponent, component)
        dct = ObjectsFactory.create_data_configuration_tree(component_configuration)
        eeg_data = ObjectsFactory.create_eeg_data(dct, subject_of_group, eeg_set)
        eeg_file = ObjectsFactory.create_eeg_file(eeg_data)
        eeg_els = ObjectsFactory.create_eeg_electrode_localization_system()
        manufacturer = ObjectsFactory.create_manufacturer()
        eeg_electrode_model = ObjectsFactory.create_electrode_model()
        eeg_electrode_cap = ObjectsFactory.create_eeg_electrode_cap(manufacturer, eeg_electrode_model)
        eeg_electrode_net_system = ObjectsFactory.create_eeg_electrode_net_system(
            eeg_electrode_cap, eeg_els
        )
        eeg_electrode_localization_system = ObjectsFactory.create_eeg_electrode_localization_system()
        ObjectsFactory.create_eeg_electrode_position(eeg_electrode_localization_system)
        ObjectsFactory.create_eeg_electrode_layout_setting(
            eeg_set, eeg_electrode_net_system
        )

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zipped_file:
            self.assertTrue(
                eeg_file.file.name in [subdir for subdir in zipped_file.namelist()],
                '%s not in %s' % (eeg_file.file.name, zipped_file.namelist()))
            self.assertTrue(
                eeg_els.map_image_file.name in [subdir for subdir in zipped_file.namelist()],
                '%s not in %s' % (eeg_els.map_image_file.name, zipped_file.namelist()))

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    def test_eeg_has_not_data_collection_files_does_not_create_corresponding_file_paths_in_zip_file(self):
        rootcomponent = ObjectsFactory.create_component(self.experiment, 'block', 'root component')
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = ObjectsFactory.create_subject_of_group(self.group, subject)
        eeg_set = ObjectsFactory.create_eeg_setting(self.experiment)
        component = ObjectsFactory.create_component(self.experiment, 'eeg', kwargs={'eeg_set': eeg_set})
        component_configuration = ObjectsFactory.create_component_configuration(rootcomponent, component)
        dct = ObjectsFactory.create_data_configuration_tree(component_configuration)
        eeg_data = ObjectsFactory.create_eeg_data(dct, subject_of_group, eeg_set)
        eeg_file = ObjectsFactory.create_eeg_file(eeg_data)
        eeg_file.file = ''
        eeg_file.save()
        eeg_els = ObjectsFactory.create_eeg_electrode_localization_system()
        eeg_els.map_image_file = ''
        eeg_els.save()
        manufacturer = ObjectsFactory.create_manufacturer()
        eeg_electrode_model = ObjectsFactory.create_electrode_model()
        eeg_electrode_cap = ObjectsFactory.create_eeg_electrode_cap(manufacturer, eeg_electrode_model)
        eeg_electrode_net_system = ObjectsFactory.create_eeg_electrode_net_system(
            eeg_electrode_cap, eeg_els
        )
        eeg_electrode_localization_system = ObjectsFactory.create_eeg_electrode_localization_system()
        ObjectsFactory.create_eeg_electrode_position(eeg_electrode_localization_system)
        ObjectsFactory.create_eeg_electrode_layout_setting(
            eeg_set, eeg_electrode_net_system
        )

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zipped_file:
            self.assertEqual(1, len(zipped_file.namelist()))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_emg_has_data_collection_files_creates_corresponding_file_paths_in_zip_file(self):
        patient = UtilTests.create_patient(changed_by=self.user)
        self._create_minimum_objects_to_test_patient(patient)
        rootcomponent = ObjectsFactory.create_component(self.experiment, 'block', 'root component')
        subject_of_group = SubjectOfGroup.objects.last()
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        emg_setting = ObjectsFactory.create_emg_setting(self.experiment, software_version)
        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        electrode_model = ObjectsFactory.create_electrode_model()
        emg_electrode_setting = ObjectsFactory.create_emg_electrode_setting(emg_setting, electrode_model)
        emg_ep = ObjectsFactory.create_emg_electrode_placement(standardization_system, muscle_subdivision)
        ObjectsFactory.create_emg_electrode_placement_setting(emg_electrode_setting, emg_ep)
        emg_step = ObjectsFactory.create_component(self.experiment, 'emg', kwargs={'emg_set': emg_setting})
        component_config = ObjectsFactory.create_component_configuration(rootcomponent, emg_step)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        emg_data = ObjectsFactory.create_emg_data_collection_data(dct, subject_of_group, emg_setting)
        emg_file = ObjectsFactory.create_emg_data_collection_file(emg_data)

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zipped_file:
            self.assertTrue(
                emg_file.file.name in [subdir for subdir in zipped_file.namelist()],
                '%s not in %s' % (emg_file.file.name, zipped_file.namelist()))
            self.assertTrue(
                emg_ep.photo.name in [subdir for subdir in zipped_file.namelist()],
                '%s not in %s' % (emg_ep.photo.name, zipped_file.namelist()))

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_emg_has_not_data_collection_files_does_not_create_corresponding_file_paths_in_zip_file(self):
        patient = UtilTests.create_patient(changed_by=self.user)
        subject_of_group = self._create_minimum_objects_to_test_patient(patient)
        rootcomponent = ObjectsFactory.create_component(self.experiment, 'block', 'root component')
        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        emg_setting = ObjectsFactory.create_emg_setting(self.experiment, software_version)
        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        electrode_model = ObjectsFactory.create_electrode_model()
        emg_electrode_setting = ObjectsFactory.create_emg_electrode_setting(emg_setting, electrode_model)
        emg_ep = ObjectsFactory.create_emg_electrode_placement(standardization_system, muscle_subdivision)
        emg_ep.photo = ''
        emg_ep.save()
        ObjectsFactory.create_emg_electrode_placement_setting(emg_electrode_setting, emg_ep)
        emg_step = ObjectsFactory.create_component(self.experiment, 'emg', kwargs={'emg_set': emg_setting})
        component_config = ObjectsFactory.create_component_configuration(rootcomponent, emg_step)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        emg_data = ObjectsFactory.create_emg_data_collection_data(dct, subject_of_group, emg_setting)
        emg_file = ObjectsFactory.create_emg_data_collection_file(emg_data)
        emg_file.file = ''
        emg_file.save()

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zipped_file:
            self.assertEqual(1, len(zipped_file.namelist()))

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @patch('survey.abc_search_engine.Server')
    def test_experiment_has_questionnaire_step_sends_base64_encoded_limesurvey_lsa_files_from_limesurvey(self, mockServer):
        # TODO (NES-966): solve temp dir created misteriously
        patient = UtilTests.create_patient(changed_by=self.user)
        self._create_minimum_objects_to_test_patient(patient)
        rootcomponent = ObjectsFactory.create_component(self.experiment, 'block', 'root component')

        # First survey
        survey1 = create_survey()
        questionnaire_step1 = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE, kwargs={'survey': survey1})
        ObjectsFactory.create_component_configuration(rootcomponent, questionnaire_step1)
        # Second survey
        survey2 = create_survey(505050)
        questionnaire_step2 = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE, kwargs={'survey': survey2})
        ObjectsFactory.create_component_configuration(rootcomponent, questionnaire_step2)

        self.set_export_survey_mock_value(mockServer, True)

        export = ExportExperiment(self.experiment)
        export.export_all()

        self.assertTrue(mockServer.return_value.export_survey.called)
        self.assertTrue(
            mockServer.return_value.export_survey.mock_calls,
            [call(survey1.lime_survey_id), call(survey2.lime_survey_id)])
        self.assertIn('%s.lsa' % survey1.lime_survey_id, os.listdir(export.temp_dir))
        self.assertIn('%s.lsa' % survey2.lime_survey_id, os.listdir(export.temp_dir))

    @patch('survey.abc_search_engine.Server')
    def test_experiment_has_questionnaire_step_add_survey_archive_in_experiment_zip_file(self, mockServer):
        patient = UtilTests.create_patient(changed_by=self.user)
        self._create_minimum_objects_to_test_patient(patient)
        rootcomponent = ObjectsFactory.create_component(self.experiment, 'block', 'root component')

        # First survey
        survey1 = create_survey()
        questionnaire_step1 = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE,
            kwargs={'survey': survey1})
        ObjectsFactory.create_component_configuration(rootcomponent, questionnaire_step1)
        # Second survey
        survey2 = create_survey(505050)
        questionnaire_step2 = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE,
            kwargs={'survey': survey2})
        ObjectsFactory.create_component_configuration(rootcomponent, questionnaire_step2)

        self.set_export_survey_mock_value(mockServer, True)

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))

        self.assertTrue(mockServer.return_value.export_survey.called)
        self.assertTrue(mockServer.return_value.export_survey.call_args, call(survey1.lime_survey_id))
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zipped_file:
            self.assertEqual(3, len(zipped_file.namelist()))
            self.assertIn('%s.lsa' % survey1.lime_survey_id, zipped_file.namelist())
            self.assertIn('%s.lsa' % survey2.lime_survey_id, zipped_file.namelist())

    @patch('survey.abc_search_engine.Server')
    def test_call_export_survey_rpc_method_uses_correct_url(self, mockServer):
        patient = UtilTests.create_patient(changed_by=self.user)
        self._create_minimum_objects_to_test_patient(patient)
        rootcomponent = ObjectsFactory.create_component(self.experiment, 'block', 'root component')
        survey = create_survey()
        questionnaire_step = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE,
            kwargs={'survey': survey})
        ObjectsFactory.create_component_configuration(rootcomponent, questionnaire_step)

        self.set_export_survey_mock_value(mockServer)

        self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))

        def check_right_url():
            self.assertEqual(mockServer.call_args, call(
                settings.LIMESURVEY['URL_API']
                + '/index.php/plugins/unsecure?plugin=extendRemoteControl&function=action'))

        mockServer.return_value.export_survey.side_effect = check_right_url()
        mockServer.return_value.export_survey.assert_called_once_with(
            mockServer.return_value.get_session_key.return_value, survey.lime_survey_id)

    @patch('survey.abc_search_engine.Server')
    def test_export_all_generates_partial_fixture_with_questionnaire_response_data(self, mockServer):
        patient = UtilTests.create_patient(self.user)
        subject_of_group = self._create_minimum_objects_to_test_patient(patient)
        survey = create_survey()
        rootcomponent = ObjectsFactory.create_component(self.experiment, 'block', 'root component')
        questionnaire = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE, kwargs={'survey': survey}
        )
        component_config = ObjectsFactory.create_component_configuration(rootcomponent, questionnaire)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        ObjectsFactory.create_questionnaire_response(
            dct, self.user, token_id=212121, subject_of_group=subject_of_group)

        self.set_export_survey_mock_value(mockServer)

        export = ExportExperiment(self.experiment)
        export.export_all()

        self.assertIn('questionnaireresponse.json', os.listdir(export.temp_dir))

    @patch('survey.abc_search_engine.Server')
    def test_export_survey_stablish_limesurvey_connection_fails_display_warning_message(self, mockServer):
        patient = UtilTests.create_patient(changed_by=self.user)
        self._create_minimum_objects_to_test_patient(patient)
        rootcomponent = ObjectsFactory.create_component(self.experiment, 'block', 'root component')
        survey = create_survey()
        questionnaire_step = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE, kwargs={'survey': survey})
        ObjectsFactory.create_component_configuration(rootcomponent, questionnaire_step)

        mockServer.return_value.get_session_key.return_value = {'status': 'Invalid user name or password'}

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(
            message, 'Não foi possível exportar dados do LimeSurvey. Por favor tente novamente. Se '
                     'o problema persistir entre em contato com o administrador de sistemas.')

    # CONTINUE: keep with tests for errors in consuming LimeSurvey API
    @patch('survey.abc_search_engine.Server')
    def test_export_survey_returns_error_from_api_display_warning_message(self, mockServer):
        patient = UtilTests.create_patient(changed_by=self.user)
        self._create_minimum_objects_to_test_patient(patient)
        rootcomponent = ObjectsFactory.create_component(self.experiment, 'block', 'root component')
        survey = create_survey()
        questionnaire_step = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE,
            kwargs={'survey': survey})
        ObjectsFactory.create_component_configuration(rootcomponent, questionnaire_step)

        mockServer.return_value.get_session_key.return_value = 'idheugd835[djgh'
        # API returns a series of pairs {'status': <error>}. As in
        # ABCSearchEngine we treat all errors the same manner, we
        # give a generic pair: {'status': 'Error'}
        mockServer.return_value.export_survey.return_value = {'status': 'Error'}

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(
            message, 'Não foi possível exportar dados do LimeSurvey. Por favor tente novamente. Se '
                     'o problema persistir entre em contato com o administrador de sistemas.')


class ImportExperimentTest(TestCase):
    TEMP_MEDIA_ROOT = tempfile.mkdtemp()

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

        TMSDeviceSetting.objects.create(
            tms_setting=tms_setting, tms_device=tms_device, coil_model=coil_model
        )

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

        electrode_model = ElectrodeModel.objects.create(
            name='TEST_ELECTRODE_MODEL',
            electrode_configuration=electrode_config,
            material=material)
        eeg_electrode_cap = ObjectsFactory.create_eeg_electrode_cap(
            manufacturer=manufacturer, electrode_model=electrode_model, material=material)
        ObjectsFactory.create_eeg_electrode_capsize(eeg_electrode_cap)
        electrode_net_sys = EEGElectrodeNetSystem.objects.create(
            eeg_electrode_net=eeg_electrode_cap, eeg_electrode_localization_system=electrode_loc_sys)
        electrode_pos = EEGElectrodePosition.objects.create(
            name='TEST_ELECTRODE_POSITION', eeg_electrode_localization_system=electrode_loc_sys)
        electrode_layout_sys = EEGElectrodeLayoutSetting.objects.create(
            eeg_electrode_net_system=electrode_net_sys, eeg_setting=eeg_setting)
        EEGElectrodePositionSetting.objects.create(
            eeg_electrode_layout_setting=electrode_layout_sys, eeg_electrode_position=electrode_pos,
            electrode_model=electrode_model, used=True, channel_index=1
        )

        filter_type = FilterType.objects.create(name='TEST_FILTER_TYPE')
        EEGFilterSetting.objects.create(eeg_setting=eeg_setting,
                                        eeg_filter_type=filter_type)
        amplifier_detection_type = AmplifierDetectionType.objects.create(name='TEST_AMPLIFIER_DETECTION_TYPE')
        tethering_system = TetheringSystem.objects.create(name='TEST_AMPLIFIER_DETECTION_TYPE')
        amplifier = Amplifier.objects.create(identification='AMPLIFIER',
                                             amplifier_detection_type=amplifier_detection_type,
                                             tethering_system=tethering_system,
                                             manufacturer=manufacturer,
                                             equipment_type='amplifier')
        EEGAmplifierSetting.objects.create(eeg_amplifier=amplifier,
                                           eeg_setting=eeg_setting)

        eeg_solution = EEGSolution.objects.create(name='TEST_EEG_SOLUTION',
                                                  manufacturer=manufacturer)
        EEGSolutionSetting.objects.create(eeg_setting=eeg_setting, eeg_solution=eeg_solution)

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
        EMGADConverterSetting.objects.create(ad_converter=ad_converter,
                                             emg_setting=emg_setting)

        # Filter type
        filter_type = FilterType.objects.create(name='TEST_FILTER_TYPE')
        EMGDigitalFilterSetting.objects.create(emg_setting=emg_setting,
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
        muscle = ObjectsFactory.create_muscle()
        muscle_side = MuscleSide.objects.create(name='TEST_MUSCLE_SIDE',
                                                muscle=muscle)
        muscle_subdivision = MuscleSubdivision.objects.create(name='TEST_MUSCLE_SUBDIVISION',
                                                              muscle=muscle)
        standardization_system = StandardizationSystem.objects.create(name='TEST_STANDARDIZATION_SYSTEM')

        emg_intramuscular_placement = EMGIntramuscularPlacement.objects.create(
            standardization_system=standardization_system,
            muscle_subdivision=muscle_subdivision,
            placement_type='intramuscular'
        )
        emg_needle_placement = EMGNeedlePlacement.objects.create(
            standardization_system=standardization_system,
            muscle_subdivision=muscle_subdivision,
            placement_type='needle'
        )
        emg_surface_placement = EMGSurfacePlacement.objects.create(
            standardization_system=standardization_system,
            muscle_subdivision=muscle_subdivision,
            placement_type='surface'
        )
        EMGElectrodePlacementSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_intramuscular,
            emg_electrode_placement=emg_intramuscular_placement.emgelectrodeplacement_ptr,
            muscle_side=muscle_side)
        EMGElectrodePlacementSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_needle,
            emg_electrode_placement=emg_needle_placement.emgelectrodeplacement_ptr,
            muscle_side=muscle_side)
        # Keep this created lastly for tests below
        EMGElectrodePlacementSetting.objects.create(
            emg_electrode_setting=emg_electrode_setting_surface,
            emg_electrode_placement=emg_surface_placement.emgelectrodeplacement_ptr,
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

    # TODO (NES-956): remove survey_id
    def _create_minimum_objects_to_test_questionnaire(self, survey_id=None):
        ObjectsFactory.create_group(self.experiment, self.rootcomponent)
        survey = create_survey(survey_id) if survey_id else create_survey()
        questionnaire = ObjectsFactory.create_component(self.experiment, Component.QUESTIONNAIRE,
                                                        kwargs={'survey': survey})
        ObjectsFactory.create_component_configuration(self.rootcomponent, questionnaire)

    def _create_minimum_objects_to_test_patient(self, patient):
        research_project = ObjectsFactory.create_research_project(self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        group = ObjectsFactory.create_group(experiment)
        subject = ObjectsFactory.create_subject(patient)
        ObjectsFactory.create_subject_of_group(group, subject)

        return experiment

    def _test_creation_and_linking_between_two_models(self, model_1_name, model_2_name, linking_field,
                                                      experiment_, filter_model_1={}, flag1=False,
                                                      to_create1=True, to_create2=True, resolve_patients=True):
        """
        This test is a general test for testing the sucessfull importation of two linked models
        :param model_1_name: Name of the model inherited by the second model; The one that is being pointed at.
        :param model_2_name: Name of the model that inherits the first model; The one that is pointing to.
        :param linking_field: Name of the field that links both models
        :param experiment_: Experiment object
        :param flag1: Boolean to determine if the filter must use linking field or "id"
        :param to_create1: Boolean that determine if the first model is not created
        :param to_create2: Boolean that determine if the second model is not created
        :param resolve_patients: Boolean that determine if the patients will be duplicated
        """
        model_1 = apps.get_model(model_1_name)
        model_2 = apps.get_model(model_2_name)

        experiment = experiment_
        export = ExportExperiment(experiment)
        export.export_all()

        file_path = export.get_file_path()

        old_model_1_objects_ids = list(model_1.objects.filter(**filter_model_1).values_list('pk', flat=True))
        old_model_2_objects_ids = list(model_2.objects.values_list('pk', flat=True))

        with open(file_path, 'rb') as file:
            if resolve_patients:
                session = self.client.session
                session['patients'] = []
                session['patients_conflicts_resolved'] = True
                session['file_name'] = file.name
                session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_model_1_objects = model_1.objects.filter(**filter_model_1).exclude(pk__in=old_model_1_objects_ids)
        new_model_2_objects = model_2.objects.exclude(pk__in=old_model_2_objects_ids)
        if to_create1:  # TODO: refactor to not use to_create1
            self.assertNotEqual(0, new_model_1_objects.count())
        else:
            self.assertEqual(0, new_model_1_objects.count())
        if to_create2:
            self.assertNotEqual(0, new_model_2_objects.count())
        else:
            self.assertEqual(0, new_model_2_objects.count())

        self.assertEqual(
            model_1.objects.filter(**filter_model_1).count(),
            len(old_model_1_objects_ids) + new_model_1_objects.count()
        )
        self.assertEqual(
            model_2.objects.count(),
            len(old_model_2_objects_ids) + new_model_2_objects.count()
        )

        if not flag1:  # TODO: refactor to not use flag1
            for item in new_model_1_objects:
                dinamic_filter = {linking_field: item.pk}
                self.assertTrue(new_model_2_objects.filter(**dinamic_filter).exists())
        else:
            new_model_1_ids = new_model_1_objects.values_list('id', flat=True)
            for item in new_model_2_objects:
                self.assertTrue(getattr(item, linking_field).id in new_model_1_ids)

    def _test_creation_of_objects_that_should_not_be_duplicated(self, experiment, model_name):
        model = apps.get_model(model_name)

        export = ExportExperiment(experiment)
        export.export_all()

        file_path = export.get_file_path()

        # dictionary to test against new objects that might be created bellow
        old_model_ids = list(model.objects.values_list('pk', flat=True))

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_objects = model.objects.exclude(pk__in=old_model_ids)

        # The number of new objects in this case is zero because we do not duplicate the objects,
        # as they are allegedly from simple models with only name and/or description or other simple fields
        self.assertEqual(len(new_objects), 0)
        self.assertNotEqual(len(old_model_ids), len(new_objects))

    def _set_objects_to_test_limesurvey_calls(self, mockServer):
        self._set_constants()

        patient = UtilTests.create_patient(changed_by=self.user)
        experiment = self._create_minimum_objects_to_test_patient(patient)
        subject_of_group = SubjectOfGroup.objects.last()
        rootcomponent = ObjectsFactory.create_component(experiment, 'block', 'root component')
        survey = create_survey()
        questionnaire_step = ObjectsFactory.create_component(
            experiment, Component.QUESTIONNAIRE, kwargs={'survey': survey})
        component_config = ObjectsFactory.create_component_configuration(rootcomponent, questionnaire_step)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        ObjectsFactory.create_questionnaire_response(dct, self.user, self.TOKEN_ID_KEEPED, subject_of_group)

        ExportExperimentTest.set_export_survey_mock_value(mockServer)

        return experiment

    # Research project, Experiment and Group tests
    def test_GET_experiment_import_file_uses_correct_template(self):
        response = self.client.get(reverse('experiment_import'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'experiment/experiment_import.html')

    def test_POST_experiment_import_file_has_not_file_redirects_with_warning_message(self):
        response = self.client.post(reverse('experiment_import'), {'file': ''}, follow=True)
        self.assertRedirects(response, reverse('experiment_import'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Por favor, selecione um arquivo .zip')

    def test_POST_experiment_import_file_has_bad_json_file_redirects_with_error_message(self):
        temp_dir = tempfile.mkdtemp()
        json_filename = 'experiment.json'
        zip_filename = 'experiment.zip'
        dummy_json_file = ObjectsFactory.create_csv_file(temp_dir, json_filename)
        with zipfile.ZipFile(os.path.join(temp_dir, zip_filename), 'w') as zip_file:
            zip_file.write(dummy_json_file.name, json_filename)
        with open(os.path.join(temp_dir, zip_filename), 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('experiment_import'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Arquivo json danificado. Abortando importação do experimento.')

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

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_POST_experiment_import_file_creates_new_experiment_with_ethics_committee_project_file(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        experiment.ethics_committee_project_file = SimpleUploadedFile('file.bin', b'binnary content')
        experiment.save()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # Remove experiment exported file, so we guarantee
        # that the experiment imported has correct file uploaded
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, experiment.ethics_committee_project_file.name))

        experiment_imported = Experiment.objects.last()
        filepath = os.path.join(self.TEMP_MEDIA_ROOT, experiment_imported.ethics_committee_project_file.name)
        self.assertTrue(os.path.exists(filepath))

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

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

        # Dictionary to test against new objects created bellow
        old_objects_count = Component.objects.count()
        # Dictionary to test against new groups created bellow
        old_groups_count = ExperimentGroup.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(
                reverse('experiment_import', args=(research_project.id,)),
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

    def test_POST_experiment_import_file_redirects_to_correct_template_1(self):
        # import ResearchProject/Experiment
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertTemplateUsed(response, 'experiment/import_log.html')

    def test_POST_experiment_import_file_redirects_to_correct_template_2(self):
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

    @patch('survey.abc_search_engine.Server')
    def test_POST_experiment_import_file_returns_log_with_steps_types_and_number_of_each_step(self, mockServer):
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

        mockServer.return_value.export_survey.return_value = {'status': 'Error: Invalid survey ID'}

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self._assert_steps_imported(response)  # related to objects created above

    def test_POST_experiment_import_file_import_all_when_there_is_not_previous_objects(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent = ObjectsFactory.create_component(experiment, 'block', 'root component group 1')
        group = ObjectsFactory.create_group(experiment, rootcomponent)
        component = ObjectsFactory.create_component(experiment, 'instruction')
        component_config = ObjectsFactory.create_component_configuration(rootcomponent, component)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Remove objects
        research_project.delete()
        experiment.delete()
        rootcomponent.delete()
        group.delete()
        component.delete()
        component_config.delete()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        self.assertEqual(1, ResearchProject.objects.count())
        self.assertEqual(1, Experiment.objects.count())
        self.assertEqual(2, Component.objects.count())
        self.assertEqual(1, ExperimentGroup.objects.count())
        self.assertEqual(1, ComponentConfiguration.objects.count())

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
                reverse('experiment_import', kwargs={'research_project_id': research_project.id}),
                {'file': file}, follow=True
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
        ObjectsFactory.create_group(experiment)
        ObjectsFactory.create_group(experiment)

        self._test_creation_and_linking_between_two_models('experiment.experiment',
                                                           'experiment.group',
                                                           'experiment',
                                                           experiment)

    def test_group_and_experimental_protocol(self):
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        root1 = ObjectsFactory.create_block(experiment)
        root2 = ObjectsFactory.create_block(experiment)
        ObjectsFactory.create_group(experiment, root1)
        ObjectsFactory.create_group(experiment, root2)
        ObjectsFactory.create_group(experiment)

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

    # Questionnaire tests
    @patch('survey.abc_search_engine.Server')
    def test_POST_experiment_import_file_creates_questionnaire_component_returns_successful_message(self, mockServer):
        self._create_minimum_objects_to_test_components()
        self._create_minimum_objects_to_test_questionnaire()

        mockServer.return_value.export_survey.return_value = {'status': 'Error: Invalid survey ID'}

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

    @patch('survey.abc_search_engine.Server')
    def test_POST_experiment_import_file_creates_random_code_in_surveys(self, mockServer):
        self._create_minimum_objects_to_test_components()
        self._create_minimum_objects_to_test_questionnaire()

        mockServer.return_value.export_survey.return_value = {'status': 'Error: Invalid survey ID'}

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        new_survey = Survey.objects.last()
        self.assertTrue(1 <= int(new_survey.code.split('Q')[1]) <= 100000)

    @patch('survey.abc_search_engine.Server')
    def test_POST_experiment_import_file_creates_dummy_reference_to_limesurvey_questionnaire(self, mockServer):
        self._create_minimum_objects_to_test_components()
        self._create_minimum_objects_to_test_questionnaire()
        self._create_minimum_objects_to_test_questionnaire(survey_id=121212)

        mockServer.return_value.export_survey.return_value = {'status': 'Error: Invalid survey ID'}

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        new_survey1 = Survey.objects.order_by('-id')[1]
        new_survey2 = Survey.objects.order_by('-id')[0]
        self.assertEqual(-99, new_survey1.lime_survey_id)
        self.assertEqual(-100, new_survey2.lime_survey_id)

    @staticmethod
    def _get_relations_questionnaire_response():
        return {
            ComponentConfiguration: [(DataConfigurationTree, 'component_configuration')],
            DataConfigurationTree: [(QuestionnaireResponse, 'data_configuration_tree')],
            SubjectOfGroup: [(QuestionnaireResponse, 'subject_of_group')],
        }

    @patch('survey.abc_search_engine.Server')
    def test_import_questionnaire_response(self, mockServer):
        self._create_minimum_objects_to_test_components()
        group = ObjectsFactory.create_group(self.experiment)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = ObjectsFactory.create_subject_of_group(group, subject)
        survey = create_survey()
        questionnaire = ObjectsFactory.create_component(
            self.experiment, Component.QUESTIONNAIRE, kwargs={'survey': survey}
        )
        component_config = ObjectsFactory.create_component_configuration(self.rootcomponent, questionnaire)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)
        ObjectsFactory.create_questionnaire_response(dct, self.user, 212121, subject_of_group)

        relations = self._get_relations_questionnaire_response()

        # Return error for it's not necessary survey mock
        mockServer.return_value.export_survey.return_value = {'status': 'Error: Invalid survey ID'}

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        for model in relations:
            self.assertEqual(2, model.objects.count(), model)
            model_instance = model.objects.last()
            for dependent_model in relations[model]:
                self.assertEqual(2, dependent_model[0].objects.count(), (model, dependent_model))
                dependent_model_instance = dependent_model[0].objects.last()
                reference = getattr(dependent_model_instance, dependent_model[1])
                self.assertEqual(reference, model_instance, '%s not equal %s' % (reference, model_instance))

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

    def test_component_and_stimulus_creating_stimulus_type(self):
        self._create_minimum_objects_to_test_components()
        stimulus_type = ObjectsFactory.create_stimulus_type()
        new_component = ObjectsFactory.create_component(self.experiment, 'stimulus',
                                                        kwargs={'stimulus_type': stimulus_type})
        ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.stimulus',
                                                           'component_ptr_id',
                                                           self.experiment,
                                                           {'component_type': 'stimulus'})

    def test_component_and_stimulus_not_creating_stimulus_type(self):
        self._create_minimum_objects_to_test_components()
        # In fixtures this is the stimulus types id pre_loaded
        for i in StimulusType.objects.values_list('id', flat=True):
            stimulus_type = ObjectsFactory.create_stimulus_type()
            stimulus_type.id = i
            stimulus_type.save()
            new_component = ObjectsFactory.create_component(
                self.experiment, 'stimulus', kwargs={'stimulus_type': stimulus_type}
            )
            ObjectsFactory.create_component_configuration(self.rootcomponent, new_component)

            self._test_creation_and_linking_between_two_models(
                'experiment.component', 'experiment.stimulus', 'component_ptr_id',
                self.experiment, {'component_type': 'stimulus'}, to_create2=False
            )

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

    @patch('survey.abc_search_engine.Server')
    def test_component_and_questionnaire(self, mockServer):
        self._create_minimum_objects_to_test_components()
        self._create_minimum_objects_to_test_questionnaire()

        mockServer.return_value.export_survey.return_value = {'status': 'Error: Invalid survey ID'}

        self._test_creation_and_linking_between_two_models(
            'experiment.component', 'experiment.questionnaire', 'component_ptr_id',
            self.experiment, {'component_type': 'questionnaire'})

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
            session = self.client.session
            session['patients'] = []
            session['patients_conflicts_resolved'] = True
            session['file_name'] = file.name
            session.save()

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
            session = self.client.session
            session['patients'] = []
            session['patients_conflicts_resolved'] = True
            session['file_name'] = file.name
            session.save()
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
            session = self.client.session
            session['patients'] = []
            session['patients_conflicts_resolved'] = True
            session['file_name'] = file.name
            session.save()
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
        flesh_tone = FleshTone.objects.create(name='Yellow')
        payment = Payment.objects.create(name='SUS')
        religion = Religion.objects.create(name='No religion')
        schooling = Schooling.objects.create(name='Superior Completo')
        sociodemograph1 = SocialDemographicData.objects.create(
            patient=patient1,
            natural_of='Testelândia',
            citizenship='Testense',
            profession='Testador',
            occupation='Testador',
            flesh_tone=flesh_tone,
            payment=payment,
            religion=religion,
            schooling=schooling,
            changed_by=self.user
        )
        sociodemograph2 = SocialDemographicData.objects.create(
            patient=patient2,
            natural_of='Testelândia',
            citizenship='Testense',
            profession='Testador',
            occupation='Testador',
            flesh_tone=flesh_tone,
            payment=payment,
            religion=religion,
            schooling=schooling,
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
            session = self.client.session
            session['patients'] = []
            session['patients_conflicts_resolved'] = True
            session['file_name'] = file.name
            session.save()

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
            session = self.client.session
            session['patients'] = []
            session['patients_conflicts_resolved'] = True
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_telephone = Telephone.objects.exclude(id=telephone.id)
        self.assertEqual(1, new_telephone.count())
        self.assertEqual(new_telephone[0].changed_by, self.user_importer)

    def test_POST_experiment_import_file_overwrites_participant(self):
        patient = UtilTests.create_patient(changed_by=self.user)
        experiment = self._create_minimum_objects_to_test_patient(patient)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            session = self.client.session
            session['patients_conflicts_resolved'] = True
            session['file_name'] = file.name
            session.save()
            response = self.client.post(
                reverse('experiment_import'), {'file': file, 'from[]': [patient.id]}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_participant = Patient.objects.exclude(id=patient.id)
        self.assertEqual(0, new_participant.count())

    def test_POST_experiment_import_file_brings_right_partincipants_in_conflict_page(self):
        patient1 = UtilTests.create_patient(changed_by=self.user)
        patient1.cpf = None
        patient1.save()
        self._create_minimum_objects_to_test_patient(patient1)
        patient2 = UtilTests.create_patient(changed_by=self.user)
        patient2.name = patient1.name
        patient2.cpf = None
        patient2.save()
        experiment2 = self._create_minimum_objects_to_test_patient(patient2)

        export = ExportExperiment(experiment2)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            response = self.client.post(
                reverse('experiment_import'), {'file': file}, follow=True)
        existing_patients = response.context['patients']
        self.assertEqual(patient2.id, existing_patients[0]['id_db'])

        shutil.rmtree(self.TEMP_MEDIA_ROOT)
        # TODO (NES-977): remove temp dir that left

    def test_POST_experiment_import_file_overwrites_participant_and_does_not_create_new_subject(self):
        patient = UtilTests.create_patient(changed_by=self.user)
        experiment = self._create_minimum_objects_to_test_patient(patient)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            session = self.client.session
            session['patients_conflicts_resolved'] = True
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file, 'from[]': [patient.id]},
                                        follow=True)
        self.assertRedirects(response, reverse('import_log'))

        self.assertEqual(1, Subject.objects.count())

    def test_POST_experiment_import_file_duplicates_participant(self):
        patient = UtilTests.create_patient(changed_by=self.user)
        experiment = self._create_minimum_objects_to_test_patient(patient)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            session = self.client.session
            session['patients_conflicts_resolved'] = True
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file, 'from[]': []}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_participant = Patient.objects.exclude(id=patient.id)
        self.assertEqual(1, new_participant.count())

    # Goalkeeper tests
    def test_software_version_and_digital_game_phase(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.softwareversion', 'experiment.digitalgamephase',
            'software_version', self._create_experiment_with_digital_game_phase())

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
                                                           to_create1=False)

    def test_coil_shape_and_coil_model(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.coilshape', 'experiment.coilmodel', 'coil_shape_id',
            self._create_experiment_with_tms_setting(), to_create1=False
        )

    def test_coil_model_and_tms_device_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.coilmodel',
                                                           'experiment.tmsdevicesetting',
                                                           'coil_model_id',
                                                           self._create_experiment_with_tms_setting())

    def test_tms_device_and_tms_device_setting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.tmsdevice', 'experiment.tmsdevicesetting', 'tms_device_id',
            self._create_experiment_with_tms_setting()
        )

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

    # EEG tests
    def test_electrode_configuration_and_electrode_model(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.electrodeconfiguration', 'experiment.electrodemodel', 'electrode_configuration_id',
            self._create_experiment_with_eeg_setting(), to_create1=False, to_create2=False, flag1=True
        )

    def test_material_and_electrode_model(self):
        self._test_creation_and_linking_between_two_models('experiment.material',
                                                           'experiment.electrodemodel',
                                                           'material_id',
                                                           self._create_experiment_with_eeg_setting(),
                                                           to_create1=False, to_create2=False)

    def test_electrode_model_and_eeg_electrode_position_setting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.electrodemodel', 'experiment.eegelectrodepositionsetting', 'electrode_model_id',
            self._create_experiment_with_eeg_setting(), to_create1=False
        )

    def test_electrode_model_and_eeg_electrode_net(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.electrodemodel', 'experiment.eegelectrodenet', 'electrode_model_default_id',
            self._create_experiment_with_eeg_setting(), to_create1=False, to_create2=False
        )

    def test_eeg_electrode_localization_system_and_eeg_electrode_position(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.eegelectrodelocalizationsystem', 'experiment.eegelectrodeposition',
            'eeg_electrode_localization_system_id',
            self._create_experiment_with_eeg_setting(), to_create1=False, to_create2=False
        )

    def test_eeg_electrode_localization_system_and_eeg_electrode_net_system(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.eegelectrodelocalizationsystem', 'experiment.eegelectrodenetsystem',
            'eeg_electrode_localization_system_id',
            self._create_experiment_with_eeg_setting(), to_create1=False, to_create2=False
        )

    def test_eeg_electrode_net_and_eeg_electrode_net_system(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.eegelectrodenet', 'experiment.eegelectrodenetsystem', 'eeg_electrode_net_id',
            self._create_experiment_with_eeg_setting(), to_create1=False, to_create2=False
        )

    @skip  # TODO: test when implementing exporting/importing data collections
    def test_eeg_electrode_net_and_eeg_electrode_cap(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.eegelectrodenet', 'experiment.eegelectrodecap', 'electrodenet_ptr',
            self._create_experiment_with_eeg_setting()
        )

    def test_eeg_electrode_net_system_and_eeg_electrode_layout_setting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.eegelectrodenetsystem', 'experiment.eegelectrodelayoutsetting', 'eeg_electrode_net_system_id',
            self._create_experiment_with_eeg_setting(), to_create1=False
        )

    def test_eeg_electrode_layout_setting_and_eeg_electrode_position_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.eegelectrodelayoutsetting',
                                                           'experiment.eegelectrodepositionsetting',
                                                           'eeg_electrode_layout_setting_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_eeg_electrode_position_and_eeg_electrode_position_setting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.eegelectrodeposition', 'experiment.eegelectrodepositionsetting', 'eeg_electrode_position_id',
            self._create_experiment_with_eeg_setting(), to_create1=False
        )

    def test_eeg_setting_and_eeg_electrode_layout_setting(self):
        self._test_creation_and_linking_between_two_models('experiment.eegsetting',
                                                           'experiment.eegelectrodelayoutsetting',
                                                           'eeg_setting_id',
                                                           self._create_experiment_with_eeg_setting())

    def test_filter_type_and_eeg_filter_setting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.filtertype', 'experiment.eegfiltersetting', 'eeg_filter_type_id',
            self._create_experiment_with_eeg_setting(), to_create1=False
        )

    def test_amplifier_and_eeg_amplifier_setting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.amplifier', 'experiment.eegamplifiersetting', 'eeg_amplifier_id',
            self._create_experiment_with_eeg_setting(), to_create1=False
        )

    def test_amplifierdetectiontype_and_amplifier(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.amplifierdetectiontype', 'experiment.amplifier', 'amplifier_detection_type_id',
            self._create_experiment_with_eeg_setting(), to_create1=False, to_create2=False, flag1=True
        )

    def test_tetheringsystem_and_amplifier(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.tetheringsystem', 'experiment.amplifier', 'tethering_system',
            self._create_experiment_with_eeg_setting(), to_create1=False, to_create2=False, flag1=True
        )

    def test_eeg_solution_and_eeg_solution_setting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.eegsolution', 'experiment.eegsolutionsetting', 'eeg_solution_id',
            self._create_experiment_with_eeg_setting(), to_create1=False
        )

    def test_manufacturer_and_eeg_solution(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.manufacturer', 'experiment.eegsolution', 'manufacturer',
            self._create_experiment_with_eeg_setting(), to_create1=False, to_create2=False
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
                                                           to_create1=False)

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
                                                           to_create1=False)

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
        self._test_creation_and_linking_between_two_models(
            'experiment.filtertype', 'experiment.emgdigitalfiltersetting', 'filter_type',
            self._create_experiment_with_emg_setting(), to_create1=False
        )

    def test_equipment_and_amplifier(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.equipment', 'experiment.amplifier', 'equipment_ptr',
            self._create_experiment_with_emg_setting(),
            {'equipment_type': 'amplifier'}, to_create1=False, to_create2=False
        )

    def test_amplifier_and_emg_pre_amplifier_setting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.amplifier', 'experiment.emgpreamplifiersetting', 'amplifier',
            self._create_experiment_with_emg_setting(), to_create1=False
        )

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
        self._test_creation_and_linking_between_two_models(
            'experiment.amplifier', 'experiment.emgamplifiersetting', 'amplifier',
            self._create_experiment_with_emg_setting(), to_create1=False
        )

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
        self._test_creation_and_linking_between_two_models(
            'experiment.electrodemodel', 'experiment.emgelectrodesetting', 'electrode',
            self._create_experiment_with_emg_setting(), to_create1=False
        )

    def test_musclesubdivision_and_emgelectrodeplacement(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.musclesubdivision', 'experiment.emgelectrodeplacement', 'muscle_subdivision',
            self._create_experiment_with_emg_setting(), to_create1=False
        )

    def test_standardizationsystem_and_emgelectrodeplacement(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.standardizationsystem', 'experiment.emgelectrodeplacement', 'standardization_system',
            self._create_experiment_with_emg_setting(), to_create1=False
        )

    def test_emgelectrodesetting_and_emgelectrodeplacementsetting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.emgelectrodesetting', 'experiment.emgelectrodeplacementsetting', 'emg_electrode_setting',
            self._create_experiment_with_emg_setting()
        )

    def test_muscleside_and_emgelectrodeplacementsetting(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.muscleside', 'experiment.emgelectrodeplacementsetting', 'muscle_side',
            self._create_experiment_with_emg_setting(), to_create1=False
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
            self._create_experiment_with_emg_setting(), flag1=True, to_create2=False
        )

    def test_emgelectrodeplacement_and_emgneedleplacement(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.emgelectrodeplacement', 'experiment.emgneedleplacement', 'emgelectrodeplacement_ptr',
            self._create_experiment_with_emg_setting(), flag1=True
        )

    def test_muscle_and_muscleside(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.muscle', 'experiment.muscleside', 'muscle', self._create_experiment_with_emg_setting(),
            to_create1=False, to_create2=False
        )

    def test_muscle_and_musclesubdivision(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.muscle', 'experiment.musclesubdivision', 'muscle', self._create_experiment_with_emg_setting(),
            to_create1=False, to_create2=False
        )

    def test_manufacturer_imported_does_not_exist_create_new1(self):
        # First test uses things creates for EEG setting
        # manufacturer was created related with EEGSolution and EEGElectrodeNet(Equipment)
        # (see import_export_model_relations.py)
        experiment = self._create_experiment_with_eeg_setting()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Changes name simulating importing without his existence
        manufacturer = Manufacturer.objects.last()
        manufacturer.name = 'new manufacturer'
        manufacturer.save()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # One manufacturer was created in _create_experiment_with_eeg_setting method
        self.assertEqual(2, Manufacturer.objects.count())
        manufacturer = Manufacturer.objects.last()
        self.assertEqual(EEGElectrodeNet.objects.last().manufacturer, manufacturer)
        self.assertEqual(EEGSolution.objects.last().manufacturer, manufacturer)

    def test_material_imported_does_not_exist_create_new1(self):
        # First test uses things creates for EEG setting:
        # material was created related with ElectrodeModel
        experiment = self._create_experiment_with_eeg_setting()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Changes description simulating importing without existence
        material = Material.objects.last()
        material.description = 'new description'
        material.save()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        self.assertEqual(2, Material.objects.count())
        material = Material.objects.last()
        self.assertEqual(ElectrodeModel.objects.last().material, material)
        # TODO: test when importing/exporting data collections
        # self.assertEqual(EEGElectrodeCap.objects.last().material, material)

    @staticmethod
    def _get_pre_loaded_models_emg_editable():
        # For the dict keys we select one to change for the tests
        return {
            (Manufacturer, 'name', 1): [(Equipment, 'manufacturer', 1), (Software, 'manufacturer', 1)],
            (Material, 'description', 1): [(ElectrodeModel, 'material', 1)],
            (Muscle, 'name', 1): [(MuscleSide, 'muscle', 1), (MuscleSubdivision, 'muscle', 1)],
            (MuscleSide, 'name', 1): [(EMGElectrodePlacementSetting, 'muscle_side', 3)],
            (MuscleSubdivision, 'anatomy_origin', 1): [(EMGElectrodePlacement, 'muscle_subdivision', 3)],
            (EMGSurfacePlacement, 'location', 1): [(EMGElectrodePlacementSetting, 'emg_electrode_placement', 1)],
            (FilterType, 'description', 1): [(EMGDigitalFilterSetting, 'filter_type', 1)],
            (ElectrodeModel, 'description', 1): [(EMGElectrodeSetting, 'electrode', 3)],
            (Amplifier, 'input_impedance_unit', 1): [
                (EMGAmplifierSetting, 'amplifier', 3), (EMGPreamplifierSetting, 'amplifier', 3)
            ],
            (StandardizationSystem, 'description', 1): [(EMGElectrodePlacement, 'standardization_system', 3)]
        }

    @staticmethod
    def _get_pre_loaded_models_emg_not_editable():
        # Not editable models does not need the second element of the tupple, as in editable ones
        # because they are not tested against creating new models.
        return {
            (TetheringSystem, '', 1): [(Amplifier, 'tethering_system', 1)],
            (AmplifierDetectionType, '', 1): [(Amplifier, 'amplifier_detection_type', 1)],
            (ElectrodeConfiguration, '', 1): [(ElectrodeModel, 'electrode_configuration', 1)]
        }

    def test_preloaded_object_is_equal_to_the_one_imported_keeps_object_and_references_emg(self):
        experiment = self._create_experiment_with_emg_setting()

        pre_loaded_models_editable = self._get_pre_loaded_models_emg_editable()
        pre_loaded_models_not_editable = self._get_pre_loaded_models_emg_not_editable()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        pre_loaded_models = {**pre_loaded_models_editable, **pre_loaded_models_not_editable}
        for model in pre_loaded_models:
            self.assertEqual(model[2], model[0].objects.count(), model[0])
            model_instance = model[0].objects.last()
            for dependent_model in pre_loaded_models[model]:
                dependent_model_instances = dependent_model[0].objects.order_by('-pk')[:dependent_model[2]]
                for dependent_model_instance in dependent_model_instances:
                    reference = getattr(dependent_model_instance, dependent_model[1])
                    # for EMGElectrodePlacement we need to take the EMGSurfacePlacement inherited
                    if isinstance(reference, EMGElectrodePlacement):
                        reference = EMGSurfacePlacement.objects.last()
                    # TODO: explain why pks
                    self.assertEqual(reference.pk, model_instance.pk, '%s not equal %s' % (reference, model_instance))

    def test_object_imported_does_not_exist_create_new_emg(self):
        experiment = self._create_experiment_with_emg_setting()

        pre_loaded_models = self._get_pre_loaded_models_emg_editable()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        faker = Factory.create()
        for model in pre_loaded_models:
            # Changes field value to test for newly created instances
            instance = model[0].objects.last()
            # TODO (future):If a new model included in pre_loaded_models does
            #  not have text field, assign another faker
            instance.__dict__[model[1]] = faker.word()
            instance.save()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        for model in pre_loaded_models:
            self.assertEqual(2, model[0].objects.count(), model[0])
            model_instance = model[0].objects.last()
            for dependent_model in pre_loaded_models[model]:
                dependent_model_instances = dependent_model[0].objects.order_by('-pk')[:dependent_model[2]]
                for dependent_model_instance in dependent_model_instances:
                    reference = getattr(dependent_model_instance, dependent_model[1])
                    # for EMGElectrodePlacement we need to take the EMGSurfacePlacement inherited
                    if isinstance(reference, EMGElectrodePlacement):
                        reference = EMGSurfacePlacement.objects.last()
                    self.assertEqual(reference.pk, model_instance.pk, '%s not equal %s' % (reference, model_instance))

    @staticmethod
    def _get_pre_loaded_models_eeg_editable():
        # For the dict keys we select one to change for the tests
        return {
            (Manufacturer, 'name', 1): [
                (EEGElectrodeNet, 'manufacturer', 1), (Amplifier, 'manufacturer', 1), (EEGSolution, 'manufacturer', 1)
            ],
            (Material, 'description', 1): [(ElectrodeModel, 'material', 1)],
            (FilterType, 'description', 1): [(EEGFilterSetting, 'eeg_filter_type', 1)],
            (ElectrodeModel, 'description', 1): [
                (EEGElectrodeNet, 'electrode_model_default', 1), (EEGElectrodePositionSetting, 'electrode_model', 1)
            ],
            (EEGSolution, 'components', 1): [(EEGSolutionSetting, 'eeg_solution', 1)],
            (EEGElectrodeLocalizationSystem, 'description', 1): [
                (EEGElectrodeNetSystem, 'eeg_electrode_localization_system', 1),
                (EEGElectrodePosition, 'eeg_electrode_localization_system', 1)
            ],
            (EEGElectrodePosition, 'name', 1): [(EEGElectrodePositionSetting, 'eeg_electrode_position', 1)],
            (Amplifier, 'input_impedance_unit', 1): [(EEGAmplifierSetting, 'eeg_amplifier', 1)],
            (EEGElectrodeNet, 'identification', 1): [(EEGElectrodeNetSystem, 'eeg_electrode_net', 1)],
        }

    @staticmethod
    def _get_pre_loaded_models_eeg_not_editable():
        # Not editable models does not need the second element of the tupple, as in editable ones
        # because they are not tested against creating new models.
        return {
            (EEGElectrodeNetSystem, '', 1): [(EEGElectrodeLayoutSetting, 'eeg_electrode_net_system', 1)],
            (TetheringSystem, '', 1): [(Amplifier, 'tethering_system', 1)],
            (AmplifierDetectionType, '', 1): [(Amplifier, 'amplifier_detection_type', 1)],
            (ElectrodeConfiguration, '', 1): [(ElectrodeModel, 'electrode_configuration', 1)],
            (EEGElectrodeCap, '', 1): [(EEGCapSize, 'eeg_electrode_cap', 1)],
        }

    def test_preloaded_object_is_equal_to_the_one_imported_keeps_object_and_references_eeg(self):
        experiment = self._create_experiment_with_eeg_setting()

        pre_loaded_models_editable = self._get_pre_loaded_models_eeg_editable()
        pre_loaded_models_not_editable = self._get_pre_loaded_models_eeg_not_editable()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        pre_loaded_models = {**pre_loaded_models_editable, **pre_loaded_models_not_editable}
        for model in pre_loaded_models:
            self.assertEqual(model[2], model[0].objects.count(), model[0])
            model_instance = model[0].objects.last()
            for dependent_model in pre_loaded_models[model]:
                dependent_model_instances = dependent_model[0].objects.order_by('-pk')[:dependent_model[2]]
                for dependent_model_instance in dependent_model_instances:
                    reference = getattr(dependent_model_instance, dependent_model[1])
                    self.assertEqual(reference, model_instance, 'dependent model: %s' % (dependent_model_instance))

    def test_object_imported_does_not_exist_create_new_eeg(self):
        experiment = self._create_experiment_with_eeg_setting()

        pre_loaded_models = self._get_pre_loaded_models_eeg_editable()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        faker = Factory.create()
        for model in pre_loaded_models:
            # Changes field value to test for newly created instances
            instance = model[0].objects.last()
            # TODO (future):If a new model included in pre_loaded_models does
            #  not have text field, assign another faker
            instance.__dict__[model[1]] = faker.word()
            instance.save()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        for model in pre_loaded_models:
            self.assertEqual(2, model[0].objects.count(), model[0])
            model_instance = model[0].objects.last()
            for dependent_model in pre_loaded_models[model]:
                dependent_model_instances = dependent_model[0].objects.order_by('-pk')[:dependent_model[2]]
                for dependent_model_instance in dependent_model_instances:
                    reference = getattr(dependent_model_instance, dependent_model[1])
                    self.assertEqual(reference, model_instance, '%s not equal %s' % (reference, model_instance))

    def test_import_eegelectrodelocalizationsystem_has_some_different_position_create_new(self):
        experiment = self._create_experiment_with_eeg_setting()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        electrode_loc_sys = EEGElectrodeLocalizationSystem.objects.last()
        electrode_pos = electrode_loc_sys.electrode_positions.first()
        electrode_pos.coordinate_x = 21
        electrode_pos.save()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        self.assertEqual(2, EEGElectrodeLocalizationSystem.objects.count())
        new_electrode_loc_sys = EEGElectrodeLocalizationSystem.objects.last()
        new_electrode_pos = EEGElectrodePosition.objects.last()
        self.assertEqual(new_electrode_pos.eeg_electrode_localization_system, new_electrode_loc_sys)
        new_eegelectrodenetsystem = EEGElectrodeNetSystem.objects.last()
        self.assertEqual(new_eegelectrodenetsystem.eeg_electrode_localization_system, new_electrode_loc_sys)

    @staticmethod
    def _get_pre_loaded_models_tms_editable():
        return {
            # TMSDevice related model is refered as experiment.equipment in
            # PRE_LOADED_MODELS_FOREIGN_KEYS as in json experiment.equipment is
            # a model separated from experiment.tmsdevice
            (Manufacturer, 'name', 1): [(TMSDevice, 'manufacturer', 1)],
            (Material, 'description', 1): [(CoilModel, 'material', 1)],
        }

    @staticmethod
    def _get_pre_loaded_models_tms_not_editable():
        return {
            (CoilShape, '', 1): [(CoilModel, 'coil_shape', 1)]
        }

    def test_preloaded_object_is_equal_to_the_one_imported_keeps_object_and_references_tms(self):
        experiment = self._create_experiment_with_tms_setting()

        pre_loaded_models_editable = self._get_pre_loaded_models_tms_editable()
        pre_loaded_models_not_editable = self._get_pre_loaded_models_tms_not_editable()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        pre_loaded_models = {**pre_loaded_models_editable, **pre_loaded_models_not_editable}
        for model in pre_loaded_models:
            self.assertEqual(model[2], model[0].objects.count(), model[0])
            model_instance = model[0].objects.last()
            for dependent_model in pre_loaded_models[model]:
                dependent_model_instances = dependent_model[0].objects.order_by('-pk')[:dependent_model[2]]
                for dependent_model_instance in dependent_model_instances:
                    reference = getattr(dependent_model_instance, dependent_model[1])
                    self.assertEqual(reference, model_instance, '%s not equal %s' % (reference, model_instance))

    def test_object_imported_does_not_exist_create_new_tms(self):
        experiment = self._create_experiment_with_tms_setting()

        pre_loaded_models = self._get_pre_loaded_models_tms_editable()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        faker = Factory.create()
        for model in pre_loaded_models:
            # Changes field value to test for newly created instances
            instance = model[0].objects.last()
            # TODO (future):If a new model included in pre_loaded_models does
            #  not have text field, assign another faker
            instance.__dict__[model[1]] = faker.word()
            instance.save()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        for model in pre_loaded_models:
            self.assertEqual(2, model[0].objects.count(), model[0])
            model_instance = model[0].objects.last()
            for dependent_model in pre_loaded_models[model]:
                dependent_model_instances = dependent_model[0].objects.order_by('-pk')[:dependent_model[2]]
                for dependent_model_instance in dependent_model_instances:
                    reference = getattr(dependent_model_instance, dependent_model[1])
                    self.assertEqual(reference, model_instance, '%s not equal %s' % (reference, model_instance))

    def test_preloaded_material_is_equal_to_the_one_imported_keeps_object_and_references2(self):
        # Second test uses things creates for TMS setting
        # material created related with CoilModel
        experiment = self._create_experiment_with_tms_setting()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        self.assertEqual(1, Material.objects.count())
        material = Material.objects.last()
        self.assertEqual(CoilModel.objects.last().material, material)

    def test_material_imported_does_not_exist_create_new2(self):
        # First test uses things creates for TMS setting:
        # material was created related with CoilModel
        experiment = self._create_experiment_with_tms_setting()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Changes description simulating importing without existence
        material = Material.objects.last()
        material.description = 'new description'
        material.save()

        with open(file_path, 'rb') as file:
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        self.assertEqual(2, Material.objects.count())
        material = Material.objects.last()
        self.assertEqual(CoilModel.objects.last().material, material)
        # TODO: test when importing/exporting data collections
        # self.assertEqual(EEGElectrodeCap.objects.last().material, material)

    def test_change_user_references_to_logged_user_before_import_experiment(self):
        patient = UtilTests.create_patient(changed_by=self.user)
        UtilTests.create_telephone(patient, changed_by=self.user)
        medical_record = UtilTests.create_medical_record(self.user, patient)
        UtilTests.create_diagnosis(medical_record)

        experiment = self._create_minimum_objects_to_test_patient(patient)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            session = self.client.session
            session['patients'] = []
            session['patients_conflicts_resolved'] = True
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        self.assertEqual(Patient.objects.last().changed_by, self.user_importer)
        self.assertEqual(Telephone.objects.last().changed_by, self.user_importer)
        self.assertEqual(MedicalRecordData.objects.last().record_responsible, self.user_importer)

    def test_diagnosis_classification_of_diseases_references_points_to_code_already_existent_imports_successfully(self):
        patient = UtilTests.create_patient(changed_by=self.user)
        medical_record = UtilTests.create_medical_record(self.user, patient)
        cid10 = UtilTests.create_cid10('A01')
        UtilTests.create_diagnosis(medical_record, cid10)

        experiment = self._create_minimum_objects_to_test_patient(patient)

        cid10_count = ClassificationOfDiseases.objects.count()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        with open(file_path, 'rb') as file:
            session = self.client.session
            session['patients'] = []
            session['patients_conflicts_resolved'] = True
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        self.assertEqual(ClassificationOfDiseases.objects.count(), cid10_count)

    def test_classification_of_diseases_references_creates_new_entries_if_code_not_exists(self):
        patient = UtilTests.create_patient(changed_by=self.user)
        medical_record = UtilTests.create_medical_record(self.user, patient)
        cid10 = UtilTests.create_cid10('A01')
        UtilTests.create_diagnosis(medical_record, cid10)

        experiment = self._create_minimum_objects_to_test_patient(patient)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Changes created classification of diseases code to test below
        cid10.code = 'A21'
        cid10.save()

        with open(file_path, 'rb') as file:
            session = self.client.session
            session['patients'] = []
            session['patients_conflicts_resolved'] = True
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        self.assertEqual(2, ClassificationOfDiseases.objects.count())
        new_cid10 = ClassificationOfDiseases.objects.last()
        self.assertEqual(new_cid10.code, 'A01')
        self.assertEqual(new_cid10.description, '(imported, not recognized)')
        self.assertEqual(new_cid10.abbreviated_description, '(imported, not recognized)')

    def test_error_loading_fixture_display_error_message(self):
        # TODO: implement it!
        pass

    # Tests for TMS data collection
    def _create_tms_data_collection_objects(self):
        # Create base objects for an experiment with one step of tms
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent = ObjectsFactory.create_component(experiment, 'block', 'root component')
        tms_setting = ObjectsFactory.create_tms_setting(experiment)
        tms_step = ObjectsFactory.create_component(experiment, 'tms', kwargs={'tms_set': tms_setting})
        component_configuration = ObjectsFactory.create_component_configuration(rootcomponent, tms_step)
        self.dct = ObjectsFactory.create_data_configuration_tree(component_configuration)

        # Create objects for the tms data
        group = ObjectsFactory.create_group(experiment)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        self.subject_of_group = ObjectsFactory.create_subject_of_group(group, subject)
        tms_data = ObjectsFactory.create_tms_data_collection_data(self.dct, self.subject_of_group, tms_setting)

        # Create objects for the hotspot (optional, but desired step of the tms data)
        tms_local_sys = ObjectsFactory.create_tms_localization_system_file()

        hotspot = HotSpot.objects.create(
            tms_data=tms_data,
            name="TMS Data Collection File",
            tms_localization_system=tms_local_sys)

        ObjectsFactory.create_hotspot_data_collection_file(hotspot)

        return experiment

    def test_component_and_component_configuration(self):
        self._create_minimum_objects_to_test_components()
        tms_setting = ObjectsFactory.create_tms_setting(self.experiment)
        tms = ObjectsFactory.create_component(self.experiment, 'tms', kwargs={'tms_set': tms_setting})
        component_config = ObjectsFactory.create_component_configuration(self.rootcomponent, tms)

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        old_components = Component.objects.count()
        old_componentsconfiguration = ComponentConfiguration.objects.count()

        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import', args=(self.research_project.id,)),
                                        {'file': file}, follow=True)
        self.assertRedirects(response, reverse('import_log'))

        new_components = Component.objects.exclude(id__in=[self.rootcomponent.id, tms.id])
        new_componentconfiguration = ComponentConfiguration.objects.exclude(id=component_config.id)

        self.assertEqual(
            Component.objects.count(),
            old_components + len(new_components))
        self.assertEqual(
            ComponentConfiguration.objects.count(),
            old_componentsconfiguration + len(new_componentconfiguration))

        for item in new_components:
            self.assertEqual(Experiment.objects.last().id, item.experiment.id)
        for item in new_componentconfiguration:
            self.assertTrue(new_components.filter(id=item.component_id).exists())

        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experimento importado com sucesso.')

    def test_component_configuration_and_data_configuration_tree(self):
        self._test_creation_and_linking_between_two_models('experiment.componentconfiguration',
                                                           'experiment.dataconfigurationtree',
                                                           'component_configuration',
                                                           self._create_tms_data_collection_objects())

    def test_data_configuration_tree_and_tms_data(self):
        self._test_creation_and_linking_between_two_models('experiment.dataconfigurationtree',
                                                           'experiment.tmsdata',
                                                           'data_configuration_tree',
                                                           self._create_tms_data_collection_objects())

    def test_coil_orientation_and_tms_data(self):
        self._test_creation_and_linking_between_two_models('experiment.coilorientation',
                                                           'experiment.tmsdata',
                                                           'coil_orientation',
                                                           self._create_tms_data_collection_objects(),
                                                           to_create1=False)

    def test_direction_of_the_induced_current_and_tms_data(self):
        self._test_creation_and_linking_between_two_models('experiment.directionoftheinducedcurrent',
                                                           'experiment.tmsdata',
                                                           'direction_of_induced_current',
                                                           self._create_tms_data_collection_objects())

    def test_tms_setting_and_tms_data(self):
        self._test_creation_and_linking_between_two_models('experiment.tmssetting',
                                                           'experiment.tmsdata',
                                                           'tms_setting',
                                                           self._create_tms_data_collection_objects())

    def test_tms_data_and_hotspot(self):
        self._test_creation_and_linking_between_two_models('experiment.tmsdata',
                                                           'experiment.hotspot',
                                                           'tms_data',
                                                           self._create_tms_data_collection_objects())

    def test_brain_area_system_and_brain_area(self):
        self._test_creation_and_linking_between_two_models('experiment.brainareasystem',
                                                           'experiment.brainarea',
                                                           'brain_area_system',
                                                           self._create_tms_data_collection_objects())

    def test_brain_area_and_tms_localization_system(self):
        self._test_creation_and_linking_between_two_models('experiment.brainarea',
                                                           'experiment.tmslocalizationsystem',
                                                           'brain_area',
                                                           self._create_tms_data_collection_objects())

    def test_tms_localization_system_and_hotspot(self):
        self._test_creation_and_linking_between_two_models('experiment.tmslocalizationsystem',
                                                           'experiment.hotspot',
                                                           'tms_localization_system',
                                                           self._create_tms_data_collection_objects())

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_import_tms_data_collection_files(self):
        experiment = self._create_tms_data_collection_objects()

        # Created right above: to remove files below
        tms_ls = TMSLocalizationSystem.objects.last()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # Remove exported files, so we guarantee
        # that the new ones imported have correct files uploaded
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, tms_ls.tms_localization_system_image.name))

        tms_file_imported = TMSLocalizationSystem.objects.last()
        filepath = os.path.join(self.TEMP_MEDIA_ROOT, tms_file_imported.tms_localization_system_image.name)
        self.assertTrue(os.path.exists(filepath))

    # Tests for Additional data collection
    def _create_additional_data_collection_objects(self):
        # Create objects for the additional data
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        group = ObjectsFactory.create_group(experiment)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = ObjectsFactory.create_subject_of_group(group, subject)
        additional_data = ObjectsFactory.create_additional_data_data(None, subject_of_group)
        ObjectsFactory.create_additional_data_file(additional_data)

        return experiment

    def test_data_configuration_tree_and_additional_data(self):
        # Additional data doesn't need a data configuration tree to exist,
        # unless they are associated to a step
        experiment = self._create_tms_data_collection_objects()
        additional_data = ObjectsFactory.create_additional_data_data(self.dct, self.subject_of_group)
        ObjectsFactory.create_additional_data_file(additional_data)

        self._test_creation_and_linking_between_two_models('experiment.dataconfigurationtree',
                                                           'experiment.additionaldata',
                                                           'data_configuration_tree',
                                                           experiment)

    def test_subject_of_group_and_additional_data(self):
        self._test_creation_and_linking_between_two_models('experiment.subjectofgroup',
                                                           'experiment.additionaldata',
                                                           'subject_of_group',
                                                           self._create_additional_data_collection_objects())

    def test_file_format_and_additional_data(self):
        self._test_creation_and_linking_between_two_models('experiment.fileformat',
                                                           'experiment.additionaldata',
                                                           'file_format',
                                                           self._create_additional_data_collection_objects(),
                                                           to_create1=False)

    def test_additional_data_and_additional_data_file(self):
        self._test_creation_and_linking_between_two_models('experiment.additionaldata',
                                                           'experiment.additionaldatafile',
                                                           'additional_data',
                                                           self._create_additional_data_collection_objects())

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_import_additional_data_collection_files(self):
        experiment = self._create_additional_data_collection_objects()

        # Created right above: to remove files below
        adc = AdditionalDataFile.objects.last()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # Remove exported files, so we guarantee
        # that the new ones imported have correct files uploaded
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, adc.file.name))

        adc_file_imported = AdditionalDataFile.objects.last()
        filepath = os.path.join(self.TEMP_MEDIA_ROOT, adc_file_imported.file.name)
        self.assertTrue(os.path.exists(filepath))

    # Tests for Digital Game Phase data collection
    def _create_digital_game_phase_data_collection_objects(self):
        # Create base objects for an experiment with one step of digital_phase_data
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent = ObjectsFactory.create_component(experiment, 'block', 'root component')

        context_tree = ObjectsFactory.create_context_tree(experiment)
        # Create file to context tree
        with tempfile.TemporaryDirectory() as tmpdirname:
            bin_file = ObjectsFactory.create_binary_file(tmpdirname)
            with File(open(bin_file.name, 'rb')) as f:
                context_tree.setting_file.save('file.bin', f)
            context_tree.save()

        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)

        digital_game_phase_step = ObjectsFactory.create_component(
            experiment,
            'digital_game_phase',
            kwargs={'software_version': software_version, 'context_tree': context_tree})
        component_configuration = ObjectsFactory.create_component_configuration(rootcomponent,
                                                                                digital_game_phase_step)
        dct = ObjectsFactory.create_data_configuration_tree(component_configuration)

        # Create objects for the digital game phase data
        group = ObjectsFactory.create_group(experiment)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = ObjectsFactory.create_subject_of_group(group, subject)
        digital_game_phase_data = ObjectsFactory.create_digital_game_phase_data(dct, subject_of_group)
        ObjectsFactory.create_digital_game_phase_file(digital_game_phase_data)

        return experiment

    def test_additional_data_and_additional_data_file(self):
        self._test_creation_and_linking_between_two_models('experiment.additionaldata',
                                                           'experiment.additionaldatafile',
                                                           'additional_data',
                                                           self._create_additional_data_collection_objects())

    def test_data_configuration_tree_and_digital_game_phase_data(self):
        self._test_creation_and_linking_between_two_models('experiment.dataconfigurationtree',
                                                           'experiment.digitalgamephasedata',
                                                           'data_configuration_tree',
                                                           self._create_digital_game_phase_data_collection_objects())

    def test_subject_of_group_and_digital_game_phase_data(self):
        self._test_creation_and_linking_between_two_models('experiment.subjectofgroup',
                                                           'experiment.digitalgamephasedata',
                                                           'subject_of_group',
                                                           self._create_digital_game_phase_data_collection_objects())

    def test_file_format_and_digital_game_phase_data(self):
        self._test_creation_and_linking_between_two_models('experiment.fileformat',
                                                           'experiment.digitalgamephasedata',
                                                           'file_format',
                                                           self._create_digital_game_phase_data_collection_objects(),
                                                           to_create1=False)

    def test_digital_game_phase_data_and_digital_game_phase_data_file(self):
        self._test_creation_and_linking_between_two_models('experiment.digitalgamephasedata',
                                                           'experiment.digitalgamephasefile',
                                                           'digital_game_phase_data',
                                                           self._create_digital_game_phase_data_collection_objects())

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_import_digital_game_phase_data_collection_files(self):
        experiment = self._create_digital_game_phase_data_collection_objects()

        # Created right above: to remove files below
        dgpf = DigitalGamePhaseFile.objects.last()
        contexttreefile = ContextTree.objects.last()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # Remove exported files, so we guarantee
        # that the new ones imported have correct files uploaded
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, dgpf.file.name))
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, contexttreefile.setting_file.name))

        dgp_file_imported = DigitalGamePhaseFile.objects.last()
        contexttree_file_imported = ContextTree.objects.last()
        filepath1 = os.path.join(self.TEMP_MEDIA_ROOT, dgp_file_imported.file.name)
        filepath2 = os.path.join(self.TEMP_MEDIA_ROOT, contexttree_file_imported.setting_file.name)
        self.assertTrue(os.path.exists(filepath1))
        self.assertTrue(os.path.exists(filepath2))

    # Tests for Generic Data collection
    def _create_generic_data_collection_objects(self):
        # Create base objects for an experiment with one step of generic data collection
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent = ObjectsFactory.create_component(experiment, 'block', 'root component')

        information_type = ObjectsFactory.create_information_type()

        generic_data_collection_step = ObjectsFactory.create_component(
            experiment,
            'generic_data_collection',
            kwargs={'it': information_type})
        component_configuration = ObjectsFactory.create_component_configuration(
            rootcomponent,
            generic_data_collection_step)
        dct = ObjectsFactory.create_data_configuration_tree(component_configuration)

        # Create objects for the generic data collection
        group = ObjectsFactory.create_group(experiment)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = ObjectsFactory.create_subject_of_group(group, subject)
        generic_data_collection_data = ObjectsFactory.create_generic_data_collection_data(dct, subject_of_group)
        ObjectsFactory.create_generic_data_collection_file(generic_data_collection_data)

        return experiment

    def test_data_configuration_tree_and_generic_data_collection(self):
        self._test_creation_and_linking_between_two_models('experiment.dataconfigurationtree',
                                                           'experiment.genericdatacollectiondata',
                                                           'data_configuration_tree',
                                                           self._create_generic_data_collection_objects())

    def test_subject_of_group_and_generic_data_collection(self):
        self._test_creation_and_linking_between_two_models('experiment.subjectofgroup',
                                                           'experiment.genericdatacollectiondata',
                                                           'subject_of_group',
                                                           self._create_generic_data_collection_objects())

    def test_file_format_and_generic_data_collection(self):
        self._test_creation_and_linking_between_two_models('experiment.fileformat',
                                                           'experiment.genericdatacollectiondata',
                                                           'file_format',
                                                           self._create_generic_data_collection_objects(),
                                                           to_create1=False)

    def test_generic_data_collection_data_and_generic_data_collection_file(self):
        self._test_creation_and_linking_between_two_models('experiment.genericdatacollectiondata',
                                                           'experiment.genericdatacollectionfile',
                                                           'generic_data_collection_data',
                                                           self._create_generic_data_collection_objects())

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_import_generic_data_collection_files(self):
        experiment = self._create_generic_data_collection_objects()

        # Created right above: to remove files below
        gdc = GenericDataCollectionFile.objects.last()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # Remove exported files, so we guarantee
        # that the new ones imported have correct files uploaded
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, gdc.file.name))

        gdc_file_imported = GenericDataCollectionFile.objects.last()
        filepath = os.path.join(self.TEMP_MEDIA_ROOT, gdc_file_imported.file.name)
        self.assertTrue(os.path.exists(filepath))

    # Tests for EMG data collection
    def _create_emg_data_collection_related_objects(self):
        # Create base objects for an experiment with one step of emg
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent = ObjectsFactory.create_component(experiment, 'block', 'root component')

        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)
        emg_setting = ObjectsFactory.create_emg_setting(experiment, software_version)
        emg_step = ObjectsFactory.create_component(experiment, 'emg', kwargs={'emg_set': emg_setting})

        component_config = ObjectsFactory.create_component_configuration(rootcomponent, emg_step)
        dct = ObjectsFactory.create_data_configuration_tree(component_config)

        # Create objects for the emg data collection
        group = ObjectsFactory.create_group(experiment)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        subject_of_group = ObjectsFactory.create_subject_of_group(group, subject)
        emg_data = ObjectsFactory.create_emg_data_collection_data(dct, subject_of_group, emg_setting)
        ObjectsFactory.create_emg_data_collection_file(emg_data)

        return experiment

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_import_emg_data_collection_files(self):
        experiment = self._create_emg_data_collection_related_objects()
        emg_setting = EMGSetting.objects.last()
        emg_file = EMGFile.objects.last()

        standardization_system = ObjectsFactory.create_standardization_system()
        muscle = ObjectsFactory.create_muscle()
        muscle_subdivision = ObjectsFactory.create_muscle_subdivision(muscle)
        electrode_model = ObjectsFactory.create_electrode_model()
        emg_electrode_setting = ObjectsFactory.create_emg_electrode_setting(emg_setting, electrode_model)
        emg_ep = ObjectsFactory.create_emg_electrode_placement(standardization_system, muscle_subdivision)
        ObjectsFactory.create_emg_electrode_placement_setting(emg_electrode_setting, emg_ep)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # Remove exported files, so we guarantee
        # that the new ones imported have correct files uploaded
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, emg_file.file.name))
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, emg_ep.photo.name))

        emg_file_imported = EMGFile.objects.last()
        emg_ep_imported = EMGElectrodePlacement.objects.last()
        filepath1 = os.path.join(self.TEMP_MEDIA_ROOT, emg_file_imported.file.name)
        filepath2 = os.path.join(self.TEMP_MEDIA_ROOT, emg_ep_imported.photo.name)
        self.assertTrue(os.path.exists(filepath1))
        self.assertTrue(os.path.exists(filepath2))

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_import_fileformat_nes_code_already_exists_keeps_entry_in_database(self):
        experiment = self._create_emg_data_collection_related_objects()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path_json = export.get_file_path('json')
        file_path = export.get_file_path()

        file_format_instance = FileFormat.objects.last()

        # Open experiment.json, change experiment.fileformat pk and save in experiment.zip
        with open(file_path_json) as file:
            data = file.read().replace('\n', '')
        serialized = json.loads(data)
        index = next(index for (index, dict_) in enumerate(serialized) if dict_['model'] == 'experiment.fileformat')
        serialized[index]['pk'] = serialized[index]['pk'] + 1
        with open(file_path_json, 'w') as file:
            file.write(json.dumps(serialized))
        # Redirect sys.stderr to doesn't display warning message when write experiment.json to zip file
        stderr_bk, sys.stderr = sys.stderr, open('/dev/null', 'w+')
        with zipfile.ZipFile(export.get_file_path(), 'a') as zip_file:
            zip_file.write(export.get_file_path('json').encode('utf-8'), export.FILE_NAME_JSON)
        sys.stderr = stderr_bk

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        self.assertEqual(1, FileFormat.objects.count())
        self.assertEqual(file_format_instance, EMGData.objects.last().file_format)

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    def test_data_configuration_tree_and_emg_data(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.dataconfigurationtree', 'experiment.emgdata', 'data_configuration_tree',
            self._create_emg_data_collection_related_objects())

    def test_subject_of_group_and_emg_data(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.subjectofgroup', 'experiment.emgdata', 'subject_of_group',
            self._create_emg_data_collection_related_objects())

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_file_format_and_emg_data(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.fileformat', 'experiment.emgdata', 'file_format',
            self._create_emg_data_collection_related_objects(), to_create1=False)

        shutil.rmtree(self.TEMP_MEDIA_ROOT)

    def test_emg_setting_and_emg_data(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.emgsetting', 'experiment.emgdata', 'emg_setting',
            self._create_emg_data_collection_related_objects())

    def test_emg_data_and_emg_file(self):
        self._test_creation_and_linking_between_two_models(
            'experiment.emgdata', 'experiment.emgfile', 'emg_data',
            self._create_emg_data_collection_related_objects())

    def _create_eeg_data_collection_related_objects(self):
        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)
        eeg_step = ObjectsFactory.create_component(self.experiment, 'eeg', kwargs={'eeg_set': eeg_setting})
        component_configuration = ObjectsFactory.create_component_configuration(self.rootcomponent, eeg_step)
        dct = ObjectsFactory.create_data_configuration_tree(component_configuration)
        manufacturer = ObjectsFactory.create_manufacturer()
        eeg_electrode_model = ObjectsFactory.create_electrode_model()
        eeg_electrode_cap = ObjectsFactory.create_eeg_electrode_cap(manufacturer, eeg_electrode_model)
        eeg_cap_size = ObjectsFactory.create_eeg_electrode_capsize(eeg_electrode_cap)
        eeg_data = ObjectsFactory.create_eeg_data(dct, self.subject_of_group, eeg_setting, eeg_cap_size)
        ObjectsFactory.create_eeg_file(eeg_data)
        eeg_electrode_localization_system = ObjectsFactory.create_eeg_electrode_localization_system()
        eeg_electrode_net_system = ObjectsFactory.create_eeg_electrode_net_system(
            eeg_electrode_cap, eeg_electrode_localization_system
        )
        eeg_electrode_position = ObjectsFactory.create_eeg_electrode_position(eeg_electrode_localization_system)
        eeg_electrode_layout_setting = ObjectsFactory.create_eeg_electrode_layout_setting(
            eeg_setting, eeg_electrode_net_system
        )
        eeg_electrode_position_setting = ObjectsFactory.create_eeg_electrode_position_setting(
            eeg_electrode_layout_setting, eeg_electrode_position, eeg_electrode_model
        )
        ObjectsFactory.create_eeg_electrode_position_collection_status(eeg_data, eeg_electrode_position_setting)

    @staticmethod
    def _get_relations_eegdata():
        return {
            ComponentConfiguration: [(DataConfigurationTree, 'component_configuration')],
            # DataConfigurationTree: [(DataConfigurationTree, 'parent')],
            DataConfigurationTree: [(EEGData, 'data_configuration_tree')],
            # TODO: FileFormat: test in preloaded models not editable
            EEGSetting: [(EEGData, 'eeg_setting')],
            SubjectOfGroup: [(EEGData, 'subject_of_group')],
            EEGData: [(EEGFile, 'eeg_data'), (EEGElectrodePositionCollectionStatus, 'eeg_data')],
            EEGElectrodePositionSetting: [(EEGElectrodePositionCollectionStatus, 'eeg_electrode_position_setting')],
            EEGCapSize: [(EEGData, 'eeg_cap_size')],
            EEGElectrodeCap: [(EEGCapSize, 'eeg_electrode_cap')]  # EEGElectrodeCap: preloaded model not editable
        }

    # Tests for EEG data collections related models
    def test_import_eeg_data_collection_related_models(self):
        self._create_minimum_objects_to_test_components()
        group = ObjectsFactory.create_group(self.experiment)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        self.subject_of_group = ObjectsFactory.create_subject_of_group(group, subject)
        self._create_eeg_data_collection_related_objects()

        relations = self._get_relations_eegdata()
        pre_loaded_models = [key[0] for key in self._get_pre_loaded_models_eeg_not_editable().keys()]

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        for model in relations:
            model_num = 1 if model in pre_loaded_models else 2
            self.assertEqual(model_num, model.objects.count(), model)
            model_instance = model.objects.last()
            for dependent_model in relations[model]:
                self.assertEqual(2, dependent_model[0].objects.count(), dependent_model)
                dependent_model_instance = dependent_model[0].objects.last()
                reference = getattr(dependent_model_instance, dependent_model[1])
                self.assertEqual(reference, model_instance, '%s not equal %s' % (reference, model_instance))

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_import_eeg_data_collection_files(self):
        self._create_minimum_objects_to_test_components()
        group = ObjectsFactory.create_group(self.experiment)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        self.subject_of_group = ObjectsFactory.create_subject_of_group(group, subject)
        self._create_eeg_data_collection_related_objects()
        # Created right above: to remove files below
        eeg_file = EEGFile.objects.last()
        eeg_els = EEGElectrodeLocalizationSystem.objects.last()

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # Remove exported files, so we guarantee
        # that the new ones imported have correct files uploaded
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, eeg_file.file.name))
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, eeg_els.map_image_file.name))

        eeg_file_imported = EEGFile.objects.last()
        eeg_els_imported = EEGElectrodeLocalizationSystem.objects.last()
        filepath1 = os.path.join(self.TEMP_MEDIA_ROOT, eeg_file_imported.file.name)
        filepath2 = os.path.join(self.TEMP_MEDIA_ROOT, eeg_els_imported.map_image_file.name)
        self.assertTrue(os.path.exists(filepath1))
        self.assertTrue(os.path.exists(filepath2))

    def test_import_data_configuration_tree_with_parent_data_configuration_tree(self):
        self._create_minimum_objects_to_test_components()
        group = ObjectsFactory.create_group(self.experiment)
        patient1 = UtilTests.create_patient(changed_by=self.user)
        patient2 = UtilTests.create_patient(changed_by=self.user)
        subject1 = ObjectsFactory.create_subject(patient1)
        subject2 = ObjectsFactory.create_subject(patient2)
        self.subject_of_group = ObjectsFactory.create_subject_of_group(group, subject1)
        subject_of_group2 = ObjectsFactory.create_subject_of_group(group, subject2)
        eeg_setting = ObjectsFactory.create_eeg_setting(self.experiment)
        eeg_step = ObjectsFactory.create_component(self.experiment, 'eeg', kwargs={'eeg_set': eeg_setting})
        component_configuration1 = ObjectsFactory.create_component_configuration(self.rootcomponent, eeg_step)
        component_configuration2 = ObjectsFactory.create_component_configuration(self.rootcomponent, eeg_step)
        dct1 = ObjectsFactory.create_data_configuration_tree(component_configuration1)
        dct2 = ObjectsFactory.create_data_configuration_tree(component_configuration2, dct1)
        ObjectsFactory.create_eeg_data(dct1, self.subject_of_group, eeg_setting)
        ObjectsFactory.create_eeg_data(dct2, subject_of_group2, eeg_setting)

        ids_objects_before = list(DataConfigurationTree.objects.values_list('id', flat=True))

        export = ExportExperiment(self.experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        self.assertEqual(4, DataConfigurationTree.objects.count())
        objects_after = DataConfigurationTree.objects.exclude(pk__in=ids_objects_before)
        dct_parent = objects_after.get(parent=None)
        dct_children = objects_after.exclude(pk=dct_parent.id).first()
        self.assertEqual(dct_children.parent, dct_parent)

    # Tests for Component Additional Data
    def _create_all_data_collections(self):
        # Base elements
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)
        rootcomponent = ObjectsFactory.create_component(experiment, 'block', 'root component')
        group = ObjectsFactory.create_group(experiment)

        # TMS
        tms_setting = ObjectsFactory.create_tms_setting(experiment)
        tms_step = ObjectsFactory.create_component(experiment, 'tms', kwargs={'tms_set': tms_setting})
        tms_component_configuration = ObjectsFactory.create_component_configuration(rootcomponent, tms_step)
        tms_dct = ObjectsFactory.create_data_configuration_tree(tms_component_configuration)

        manufacturer = ObjectsFactory.create_manufacturer()
        software = ObjectsFactory.create_software(manufacturer)
        software_version = ObjectsFactory.create_software_version(software)

        # EMG
        emg_setting = ObjectsFactory.create_emg_setting(experiment, software_version)
        emg_step = ObjectsFactory.create_component(experiment, 'emg', kwargs={'emg_set': emg_setting})
        emg_component_config = ObjectsFactory.create_component_configuration(rootcomponent, emg_step)
        emg_dct = ObjectsFactory.create_data_configuration_tree(emg_component_config)

        # EEG
        eeg_setting = ObjectsFactory.create_eeg_setting(experiment)
        eeg_step = ObjectsFactory.create_component(experiment, 'eeg', kwargs={'eeg_set': eeg_setting})
        eeg_component_config = ObjectsFactory.create_component_configuration(rootcomponent, eeg_step)
        eeg_dct = ObjectsFactory.create_data_configuration_tree(eeg_component_config)

        # Digital Game Phase
        context_tree = ObjectsFactory.create_context_tree(experiment)
        digital_game_phase_step = ObjectsFactory.create_component(
            experiment,
            'digital_game_phase',
            kwargs={'software_version': software_version, 'context_tree': context_tree})
        dgp_component_configuration = ObjectsFactory.create_component_configuration(
            rootcomponent,
            digital_game_phase_step)
        dgp_dct = ObjectsFactory.create_data_configuration_tree(dgp_component_configuration)

        # Generic Data Collection
        information_type = ObjectsFactory.create_information_type()
        generic_data_collection_step = ObjectsFactory.create_component(
            experiment,
            'generic_data_collection',
            kwargs={'it': information_type})
        gdc_component_configuration = ObjectsFactory.create_component_configuration(
            rootcomponent,
            generic_data_collection_step)
        gdc_dct = ObjectsFactory.create_data_configuration_tree(gdc_component_configuration)

        # Task for the Experimenter
        task_experimenter_step = ObjectsFactory.create_component(experiment, 'task_experiment')
        task_experimenter_component_configuration = ObjectsFactory.create_component_configuration(
            rootcomponent, task_experimenter_step)

        # Task for the Participant
        task_step = ObjectsFactory.create_component(experiment, 'task')
        task_component_configuration = ObjectsFactory.create_component_configuration(rootcomponent, task_step)

        # Pause
        pause_step = ObjectsFactory.create_component(experiment, 'pause')
        pause_component_configuration = ObjectsFactory.create_component_configuration(rootcomponent, pause_step)

        # Instruction
        instruction_step = ObjectsFactory.create_component(experiment, 'instruction')
        instruction_component_configuration = ObjectsFactory.create_component_configuration(
            rootcomponent,
            instruction_step)

        # Stimulus
        stimulus_type = ObjectsFactory.create_stimulus_type()

        stimulus_step = ObjectsFactory.create_component(experiment, 'stimulus', kwargs={'stimulus_type': stimulus_type})
        stimulus_component_configuration = ObjectsFactory.create_component_configuration(rootcomponent, stimulus_step)

        # Block
        block_step = ObjectsFactory.create_component(experiment, 'block', 'another block component')
        block_component_configuration = ObjectsFactory.create_component_configuration(rootcomponent, block_step)

        dict_ = [
            ['rootcomponent', rootcomponent],
            ['block', block_step],
            ['tms', tms_step],
            ['emg', emg_step],
            ['eeg', eeg_step],
            ['gdp', digital_game_phase_step],
            ['gdc', generic_data_collection_step],
            ['task_experimenter', task_experimenter_step],
            ['task', task_step],
            ['pause', pause_step],
            ['instruction', instruction_step],
            ['stimulus', stimulus_step],
        ]

        with tempfile.TemporaryDirectory() as tmpdirname:
            for component in dict_:
                with open(os.path.join(tmpdirname, component[0] + 'adf.bin'), 'wb') as f:
                    f.write(b'carambola')

                with File(open(f.name, 'rb')) as file:
                    ComponentAdditionalFile.objects.create(component=component[1], file=file)

        return experiment

    def test_component_additional_data_for_each_component_with_additional_data(self):
        self._test_creation_and_linking_between_two_models('experiment.component',
                                                           'experiment.componentadditionalfile',
                                                           'component',
                                                           self._create_all_data_collections())

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_import_component_additional_data_collection_files(self):
        experiment = self._create_all_data_collections()

        # Created right above: to remove files below
        component_ad_files_ids = ComponentAdditionalFile.objects.all().values_list('id', flat=True)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # Remove exported files, so we guarantee
        # that the new ones imported have correct files uploaded
        for component_ad_file_id in component_ad_files_ids:
            os.remove(os.path.join(
                self.TEMP_MEDIA_ROOT,
                ComponentAdditionalFile.objects.get(id=component_ad_file_id).file.name))

        component_files_imported = ComponentAdditionalFile.objects.exclude(id__in=component_ad_files_ids)
        for component_file_imported in component_files_imported:
            filepath = os.path.join(self.TEMP_MEDIA_ROOT, component_file_imported.file.name)
            self.assertTrue(os.path.exists(filepath))

    # Tests for Other models with file
    def _create_stimulus_step_with_media_file(self):
        # Base elements
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        # Stimulus
        stimulus_type = ObjectsFactory.create_stimulus_type()

        with tempfile.TemporaryDirectory() as tmpdirname:
            with open(os.path.join(tmpdirname, 'stimulus_media_file.bin'), 'wb') as f:
                f.write(b'carambola')
            with File(open(f.name, 'rb')) as file:
                ObjectsFactory.create_component(experiment, 'stimulus', kwargs={
                    'stimulus_type': stimulus_type,
                    'media_file': file})

        return experiment

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_import_media_file_from_stimulus(self):
        experiment = self._create_stimulus_step_with_media_file()

        # Created right above: to remove files below
        stimulus = Stimulus.objects.last()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # Remove exported files, so we guarantee
        # that the new ones imported have correct files uploaded
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, stimulus.media_file.name))

        stimulus_imported = Stimulus.objects.last()
        filepath = os.path.join(self.TEMP_MEDIA_ROOT, stimulus_imported.media_file.name)
        self.assertTrue(os.path.exists(filepath))

    def _create_exam_file_of_patient(self):
        # Create objects for the exam file
        research_project = ObjectsFactory.create_research_project(owner=self.user)
        experiment = ObjectsFactory.create_experiment(research_project)

        group = ObjectsFactory.create_group(experiment)
        patient = UtilTests.create_patient(changed_by=self.user)
        subject = ObjectsFactory.create_subject(patient)
        ObjectsFactory.create_subject_of_group(group, subject)

        ObjectsFactory.create_exam_file(patient, self.user)

        return experiment

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_import_exam_file(self):
        experiment = self._create_exam_file_of_patient()

        # Created right above: to remove files below
        exam_file = ExamFile.objects.last()

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # Remove exported files, so we guarantee
        # that the new ones imported have correct files uploaded
        os.remove(os.path.join(self.TEMP_MEDIA_ROOT, exam_file.content.name))

        exam_file_imported = ExamFile.objects.last()
        filepath = os.path.join(self.TEMP_MEDIA_ROOT, exam_file_imported.content.name)
        self.assertTrue(os.path.exists(filepath))

    @patch('survey.abc_search_engine.Server')
    def test_import_experiment_with_questionnaire_import_limesurvey_survey_reference(self, mockServer):
        patient = UtilTests.create_patient(changed_by=self.user)
        experiment = self._create_minimum_objects_to_test_patient(patient)
        rootcomponent = ObjectsFactory.create_component(experiment, 'block', 'root component')

        survey1 = create_survey()
        questionnaire_step1 = ObjectsFactory.create_component(
            experiment, Component.QUESTIONNAIRE, kwargs={'survey': survey1}
        )
        ObjectsFactory.create_component_configuration(rootcomponent, questionnaire_step1)
        survey2 = create_survey(111111)
        questionnaire_step2 = ObjectsFactory.create_component(
            experiment, Component.QUESTIONNAIRE, kwargs={'survey': survey2}
        )
        ObjectsFactory.create_component_configuration(rootcomponent, questionnaire_step2)

        ExportExperimentTest.set_export_survey_mock_value(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        mockServer.return_value.import_survey.side_effect = [505050, 100000]

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        self.assertTrue(mockServer.return_value.import_survey.called)
        # Pass representing base64 encoded string of lsa archive
        self.assertTrue(
            mockServer.return_value.import_survey.mock_calls, [call('ldg69aesf0adfakhf'), call('adadfl0e9843ljfdasf')])
        self.assertEqual(1, Survey.objects.filter(lime_survey_id=505050).count())
        self.assertEqual(1, Survey.objects.filter(lime_survey_id=100000).count())

    def test_import_has_not_limesurvey_survey_archive_import_experiment_and_display_message_that_could_not_import_limesurvey_survey(
            self):
        # TODO (NES-956): implement it!
        pass

    def _set_constants(self):
        self.SESSION_KEY = 'idheugd835[djgh'
        self.TOKEN_KEEPED = 'BNxaKxMt9SO87OA'
        self.TOKEN_ID_KEEPED = 1
        self.TOKEN_NOT_KEEPED = '5NxeKxMtaSOp7OA'
        self.TOKEN_ID_NOT_KEEPED = 2
        self.SURVEY_ID = 505050
        self.QUESTION_SUBJECT_ID = 7
        self.QUESTION_RESPONSIBLE_ID = 8
        self.GROUP_ID = 1410
        self.LIMESURVEY_RESPONSES_IDS_DELETED = [1, 2]

    def _set_mocks(self, mockServer):
        mockServer.return_value.get_session_key.return_value = self.SESSION_KEY
        mockServer.return_value.import_survey.return_value = self.SURVEY_ID
        mockServer.return_value.list_participants.return_value = \
            [
                {
                    'token': self.TOKEN_KEEPED,
                    'participant_info': {'lastname': '', 'email': '', 'firstname': ''},
                    'tid': self.TOKEN_ID_KEEPED,
                },
                {
                    'token': self.TOKEN_NOT_KEEPED,
                    'participant_info': {'lastname': '', 'email': '', 'firstname': ''},
                    'tid': self.TOKEN_ID_NOT_KEEPED
                }
            ]
        mockServer.return_value.get_participant_properties.return_value = {'token': self.TOKEN_KEEPED}
        mockServer.return_value.list_groups.return_value = [
            {
                'group_order': 1, 'gid': self.GROUP_ID, 'grelevance': '',
                'id': {'gid': self.GROUP_ID, 'language': 'en'},
                'language': 'en', 'sid': self.SURVEY_ID, 'randomization_group': '',
                'group_name': 'Identification', 'description': ''
            },
            {
                'group_order': 2, 'gid': 1411, 'grelevance': '',
                'id': {'gid': 1411, 'language': 'en'},
                'language': 'en', 'sid': self.SURVEY_ID, 'randomization_group': '',
                'group_name': 'First group', 'description': ''
            }
        ]
        mockServer.return_value.list_questions.return_value = [
            {
                'qid': self.QUESTION_RESPONSIBLE_ID, 'question_order': 0,
                'id': {'qid': self.QUESTION_RESPONSIBLE_ID, 'language': 'en'},
                'same_default': 0, 'relevance': '1', 'question': 'Responsible Identification number:',
                'type': 'N', 'help': '', 'scale_id': 0, 'parent_qid': 0, 'other': 'N', 'language': 'en',
                'gid': self.GROUP_ID, 'modulename': None, 'sid': self.SURVEY_ID, 'title': 'responsibleid',
                'mandatory': 'Y',
                'preg': ''
            },
            {
                'qid': 3848, 'question_order': 1,
                'id': {'qid': 3848, 'language': 'en'},
                'same_default': 0, 'relevance': '1', 'question': 'Acquisition date<strong>:</strong><br />\n',
                'type': 'D', 'help': '', 'scale_id': 0, 'parent_qid': 0, 'other': 'N', 'language': 'en',
                'gid': self.GROUP_ID, 'modulename': None, 'sid': self.SURVEY_ID, 'title': 'acquisitiondate',
                'mandatory': 'Y',
                'preg': ''
            },
            {
                'qid': self.QUESTION_SUBJECT_ID, 'question_order': 2,
                'id': {'qid': self.QUESTION_SUBJECT_ID, 'language': 'en'},
                'same_default': 0, 'relevance': '1', 'question': 'Participant Identification number<b>:</b>',
                'type': 'N', 'help': '', 'scale_id': 0, 'parent_qid': 0, 'other': 'N', 'language': 'en',
                'gid': self.GROUP_ID, 'modulename': None, 'sid': self.SURVEY_ID, 'title': 'subjectid', 'mandatory': 'Y',
                'preg': ''
            }
        ]

        mockServer.return_value.update_response.return_value = {'status': 'OK'}

        mockServer.return_value.delete_participants.return_value = [{'status': 'Deleted'}]
        # Get responses from questionnaire for tokens that will be deleted
        # The string corresponds to:
        # b'"id","submitdate","lastpage","startlanguage","token","responsibleid","acquisitiondate","subjectid","firstQuestion","secondQuestion"\n
        # "1","1980-01-01 00:00:00","2","en","5NxeKxMtaSOp7OA", "2","2018-03-08 00:00:00","5","c","d"\n
        # "2","1980-01-01 00:00:00","2","en","5NxeKxMtaSOp7OA","7","2018-03-08 00:00:00", "5", "c","d"\n\n'
        mockServer.return_value.export_responses_by_token.return_value = \
            b'ImlkIiwic3VibWl0ZGF0ZSIsImxhc3RwYWdlIiwic3RhcnRsYW5ndWFnZSIsInRv' \
            b'a2VuIiwicmVzcG9uc2libGVpZCIsImFjcXVpc2l0aW9uZGF0ZSIsInN1YmplY3Rp' \
            b'ZCIsImZpcnN0UXVlc3Rpb24iLCJzZWNvbmRRdWVzdGlvbiIKIjEiLCIxOTgwLTAx' \
            b'LTAxIDAwOjAwOjAwIiwiMiIsImVuIiwiNU54ZUt4TXRhU09wN09BIiwiMiIsIjIw' \
            b'MTgtMDMtMDggMDA6MDA6MDAiLCI1IiwiYyIsImQiCiIyIiwiMTk4MC0wMS0wMSAw' \
            b'MDowMDowMCIsIjIiLCJlbiIsIjVOeGVLeE10YVNPcDdPQSIsIjciLCIyMDE4LTAz' \
            b'LTA4IDAwOjAwOjAwIiwiNSIsImMiLCJkIgoK'.decode()

        # Mock deleted responses ids return value. There are two ids, 1 and 2.
        # Only two was deleted
        mockServer.return_value.delete_responses.return_value = {'status': 'OK'}

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_keeps_only_responses_from_experiment_participants1(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # First list item corresponds to the token id 1, second item, to the token id 2
        self.assertTrue(mockServer.return_value.list_participants.called)
        self.assertEqual(
            mockServer.return_value.list_participants.call_args,
            call(self.SESSION_KEY, self.SURVEY_ID, 0, 99999999))

        # Delete token of other experiments
        self.assertTrue(mockServer.return_value.delete_participants.called)
        self.assertEqual(mockServer.return_value.delete_participants.call_args, call(
            self.SESSION_KEY, self.SURVEY_ID, [self.TOKEN_ID_NOT_KEEPED]))
        # Ensures that delete_participants was called only once
        self.assertEqual(mockServer.return_value.delete_participants.call_count, 1)

        # Mock Remote Control export_responses method with B64 encoded string.
        # This corresponds to two responses, the responses of the token that was deleted.
        self.assertTrue(mockServer.return_value.export_responses_by_token.called)
        self.assertEqual(
            mockServer.return_value.export_responses_by_token.call_args, call(
                self.SESSION_KEY, self.SURVEY_ID, 'csv', self.TOKEN_NOT_KEEPED, None, 'complete'))

        self.assertTrue(mockServer.return_value.delete_responses.called)
        self.assertEqual(mockServer.return_value.delete_responses.call_args, call(
            self.SESSION_KEY, self.SURVEY_ID, self.LIMESURVEY_RESPONSES_IDS_DELETED))

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_keeps_only_responses_from_experiment_participants2(self, mockServer):
        """Test keeping participants with same questionnaire used in 2 groups"""

        self._set_constants()
        self.OTHER_TOKEN_ID_KEEPED = 3
        self.OTHER_TOKEN_KEEPED = '9d6dggfllsiryt0y7df'

        # First objects
        patient1 = UtilTests.create_patient(changed_by=self.user)
        experiment = self._create_minimum_objects_to_test_patient(patient1)
        subject_of_group1 = SubjectOfGroup.objects.last()
        rootcomponent1 = ObjectsFactory.create_component(experiment, 'block', 'root component')
        survey1 = create_survey()
        questionnaire_step1 = ObjectsFactory.create_component(
            experiment, Component.QUESTIONNAIRE, kwargs={'survey': survey1}
        )
        component_config1 = ObjectsFactory.create_component_configuration(rootcomponent1, questionnaire_step1)
        dct1 = ObjectsFactory.create_data_configuration_tree(component_config1)
        ObjectsFactory.create_questionnaire_response(dct1, self.user, self.TOKEN_ID_KEEPED, subject_of_group1)

        # Second objects
        patient2 = UtilTests.create_patient(changed_by=self.user)
        group2 = ObjectsFactory.create_group(experiment)
        subject2 = ObjectsFactory.create_subject(patient2)
        subject_of_group2 = ObjectsFactory.create_subject_of_group(group2, subject2)
        rootcomponent2 = ObjectsFactory.create_component(experiment, 'block', 'root component')
        questionnaire_step2 = ObjectsFactory.create_component(
            experiment, Component.QUESTIONNAIRE, kwargs={'survey': survey1}
        )
        component_config2 = ObjectsFactory.create_component_configuration(rootcomponent2, questionnaire_step2)
        dct2 = ObjectsFactory.create_data_configuration_tree(component_config2)
        ObjectsFactory.create_questionnaire_response(dct2, self.user, self.OTHER_TOKEN_ID_KEEPED, subject_of_group2)

        ExportExperimentTest.set_export_survey_mock_value(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # Changing some mock's
        mockServer.return_value.list_participants.return_value = \
            [
                {
                    'token': self.TOKEN_KEEPED,
                    'participant_info': {'lastname': '', 'email': '', 'firstname': ''},
                    'tid': self.TOKEN_ID_KEEPED,
                },
                {
                    'token': self.OTHER_TOKEN_KEEPED,
                    'participant_info': {'lastname': '', 'email': '', 'firstname': ''},
                    'tid': self.OTHER_TOKEN_ID_KEEPED,
                },
                {
                    'token': self.TOKEN_NOT_KEEPED,
                    'participant_info': {'lastname': '', 'email': '', 'firstname': ''},
                    'tid': self.TOKEN_ID_NOT_KEEPED
                }
            ]

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        # First list item corresponds to the token id 1, second item, to the token id 2
        self.assertTrue(mockServer.return_value.list_participants.called)
        self.assertEqual(
            mockServer.return_value.list_participants.call_args,
            call(self.SESSION_KEY, self.SURVEY_ID, 0, 99999999))
        # Delete token of other experiments
        self.assertTrue(mockServer.return_value.delete_participants.called)
        # Ensures that delete_participants was called only once ...
        self.assertEqual(mockServer.return_value.delete_participants.call_count, 1)
        # ... with this arguments
        self.assertEqual(mockServer.return_value.delete_participants.call_args, call(
            self.SESSION_KEY, self.SURVEY_ID, [self.TOKEN_ID_NOT_KEEPED]))

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_update_responses_call_right_url(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        def check_right_url():
            self.assertEqual(mockServer.call_args, call(
                settings.LIMESURVEY['URL_API']
                + '/index.php/plugins/unsecure?plugin=extendRemoteControl&function=action'))

        mockServer.return_value.update_response.side_effect = check_right_url()

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_updates_responses_subjectid_and_responsibleid(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        new_subject = Subject.objects.last()

        self.assertTrue(mockServer.return_value.update_response.called)
        self.assertEqual(mockServer.return_value.update_response.call_args, call(
            self.SESSION_KEY, self.SURVEY_ID,
            {
                'token': self.TOKEN_KEEPED,
                str(self.SURVEY_ID) + 'X' + str(self.GROUP_ID) + 'X' + str(self.QUESTION_SUBJECT_ID): new_subject.id,
                str(self.SURVEY_ID) + 'X' + str(self.GROUP_ID) + 'X' + str(self.QUESTION_RESPONSIBLE_ID):
                    self.user_importer.id

            }
        ))

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_stablish_limesurvey_connection_fails_display_warning_message(self, mockServer):
        patient = UtilTests.create_patient(changed_by=self.user)
        experiment = self._create_minimum_objects_to_test_patient(patient)
        rootcomponent = ObjectsFactory.create_component(experiment, 'block', 'root component')
        survey = create_survey()
        questionnaire_step = ObjectsFactory.create_component(
            experiment, Component.QUESTIONNAIRE, kwargs={'survey': survey})
        ObjectsFactory.create_component_configuration(rootcomponent, questionnaire_step)

        mockServer.return_value.get_session_key.return_value = {'status': 'Invalid user name or password'}

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(
            message, 'Não foi possível importar os questionários do LimeSurvey. Somente os dados '
                     'do Experimento foram importados. Você pode remover o experimento importado e '
                     'tentar novamente. Se o problemapersistir por favor entre em contato com o '
                     'administrador de sistemas.')

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_call_import_survey_fails_display_warning_message(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # There is another returned value with other error status but we treat
        # the difference between error and success considering error a dict returned.
        mockServer.return_value.import_survey.return_value = {'status': 'No permission'}

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(
            message, 'Não foi possível importar os questionários do LimeSurvey. Somente os dados '
                     'do Experimento foram importados. Você pode remover o experimento importado e '
                     'tentar novamente. Se o problemapersistir por favor entre em contato com o '
                     'administrador de sistemas.')

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_call_list_participants_fails_display_warning_message(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # There is other returned values with other error status but we treat
        # the difference between error and success considering error a dict returned.
        mockServer.return_value.list_participants.return_value = {'status': 'Error: No token table'}

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Não foi possível remove todos os dados de participantes extras.')

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_call_delete_participant_fails_display_warning_message(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # There is other returned values with other error status but we treat
        # the difference between error and success considering error a dict returned.
        mockServer.return_value.delete_participants.return_value = {'status': 'Error: No token table'}

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Não foi possível remove todos os dados de participantes extras.')
    
    @patch('survey.abc_search_engine.Server')
    def test_import_survey_call_export_responses_by_token_fails_display_warning_message(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # There is other returned values with other error status but we treat
        # the difference between error and success considering error a dict returned.
        mockServer.return_value.export_responses_by_token.return_value = {'status': 'No Response found for Token'}

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Não foi possível remove todos os dados de participantes extras.')

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_call_delete_responses_fails_display_warning_message(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # There is other returned values with other error status but we treat
        # the difference between error and success considering error a dict returned.
        mockServer.return_value.delete_responses.return_value = {'status': 'Error: during response deletion'}

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Não foi possível remove todos os dados de participantes extras.')

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_call_get_participant_properties_fails_display_warning_message(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # There is other returned values with other error status but we treat
        # the difference between error and success considering error a dict returned.
        mockServer.return_value.list_groups.return_value = {'status': 'Error: Invalid tokenid'}

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Não foi possível atualizar as questões de identificação para todas as respostas.')

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_call_list_questions_fails_display_warning_message(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # There is other returned values with other error status but we treat
        # the difference between error and success considering error a dict returned.
        mockServer.return_value.list_questions.return_value = {'status': 'No questions found'}

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Não foi possível atualizar as questões de identificação para todas as '
                                  'respostas.')

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_has_not_Identification_group_display_warning_message(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # There is other returned values with other error status but we treat
        # the difference between error and success considering error a dict returned.
        mockServer.return_value.list_groups.return_value = [{
                'group_order': 2, 'gid': 1411, 'grelevance': '',
                'id': {'gid': 1411, 'language': 'en'},
                'language': 'en', 'sid': self.SURVEY_ID, 'randomization_group': '',
                'group_name': 'First group', 'description': ''
            }]

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Não foi possível atualizar as questões de identificação para todas as respostas.')

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_has_not_Identification_question_display_warning_message(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # There is other returned values with other error status but we treat
        # the difference between error and success considering error a dict returned.
        mockServer.return_value.list_questions.return_value = [
            {
                'qid': 3848, 'question_order': 1,
                'id': {'qid': 3848, 'language': 'en'},
                'same_default': 0, 'relevance': '1', 'question': 'Acquisition date<strong>:</strong><br />\n',
                'type': 'D', 'help': '', 'scale_id': 0, 'parent_qid': 0, 'other': 'N', 'language': 'en',
                'gid': self.GROUP_ID, 'modulename': None, 'sid': self.SURVEY_ID, 'title': 'acquisitiondate',
                'mandatory': 'Y',
                'preg': ''
            },
            {
                'qid': self.QUESTION_SUBJECT_ID, 'question_order': 2,
                'id': {'qid': self.QUESTION_SUBJECT_ID, 'language': 'en'},
                'same_default': 0, 'relevance': '1', 'question': 'Participant Identification number<b>:</b>',
                'type': 'N', 'help': '', 'scale_id': 0, 'parent_qid': 0, 'other': 'N', 'language': 'en',
                'gid': self.GROUP_ID, 'modulename': None, 'sid': self.SURVEY_ID, 'title': 'subjectid', 'mandatory': 'Y',
                'preg': ''
            }
        ]

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Não foi possível atualizar as questões de identificação para todas as '
                                  'respostas.')

    @patch('survey.abc_search_engine.Server')
    def test_import_survey_call_update_response_fails_display_warning_message(self, mockServer):
        experiment = self._set_objects_to_test_limesurvey_calls(mockServer)

        export = ExportExperiment(experiment)
        export.export_all()
        file_path = export.get_file_path()

        self._set_mocks(mockServer)

        # There is other returned values with other error status but we treat
        # the difference between error and success considering error a dict returned.
        mockServer.return_value.update_response.return_value = {'status': 'Unable to edit response'}

        # Add session variables related to updating/overwrite patients when importing
        session = self.client.session
        session['patients'] = []
        session['patients_conflicts_resolved'] = True
        with open(file_path, 'rb') as file:
            session['file_name'] = file.name
            session.save()
            response = self.client.post(reverse('experiment_import'), {'file': file}, follow=True)

        message = str(list(get_messages(response.wsgi_request))[0])
        self.assertEqual(message, 'Não foi possível atualizar todas as respostas.')
