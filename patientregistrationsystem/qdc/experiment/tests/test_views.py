from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.test import TestCase

from experiment.models import Keyword, GoalkeeperGameConfig, \
    Component, GoalkeeperGame, GoalkeeperPhase, GoalkeeperGameResults, \
    FileFormat, ExperimentResearcher
from configuration.models import LocalInstitution
from custom_user.models import Institution
from custom_user.tests_helper import create_user
from experiment.tests.tests_original import ObjectsFactory

from patient.tests import UtilTests

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
        if settings.PORTAL_API[
                'URL'] and settings.SHOW_SEND_TO_PORTAL_BUTTON:
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
        # for group in Group.objects.filter(name='Attendant'):
            group.user_set.add(self.user)

        self.client.login(username=self.user.username, password='passwd')

        self.research_project = ObjectsFactory.create_research_project()
        self.experiment = ObjectsFactory.create_experiment(
            self.research_project)

    def tearDown(self):
        self.client.logout()

    def test_permissions_research_project_update(self):
        response = self.client.get(reverse('research_project_edit',
                                           kwargs={'research_project_id':
                                                       self.research_project.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertRaises(PermissionDenied)


class ResearchprojectviewviewTest(TestCase):

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
        # for group in Group.objects.filter(name='Attendant'):
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
        self.patient = UtilTests().create_patient_mock(changed_by=self.user)
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
        GoalkeeperGame.objects.filter(code = self.goalkeepergameconfig.game).delete()
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
        # for group in Group.objects.filter(name='Attendant'):
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
        self.patient = UtilTests().create_patient_mock(changed_by=self.user)
        subject = ObjectsFactory.create_subject(self.patient)
        self.subject_of_group = \
            ObjectsFactory.create_subject_of_group(self.group, subject)

    def tearDown(self):
        self.client.logout()

    def test_collaborator_create(self):

        # Insert collaborator
        response = self.client.get(reverse('collaborator_new',
                                           kwargs={'experiment_id':
                                                       self.experiment.id}))
        self.assertEqual(response.status_code, 200)

        collaborators_added = ExperimentResearcher.objects.filter(experiment_id=self.experiment.id)
        collaborators_added_ids = collaborators_added.values_list('researcher_id', flat=True)

        collaborators = User.objects.filter(is_active=True).exclude(pk__in=collaborators_added_ids).order_by(
            'first_name',
            'last_name')
        # collaborators_selected = request.POST.getlist('collaborators')
        if collaborators:
            collaborators_selected = collaborators.first()
            response = self.client.post(reverse('collaborator_new',
                       kwargs={'experiment_id': self.experiment.id}),
                               # 'researcher_id': collaborators_selected}),
            data={'collaborators':collaborators_selected.id,
                  'action': 'save'})
            self.assertEqual(response.status_code, 302)
