import csv
import io
import json
import shutil
import sys
import tempfile
import zipfile
from os import path

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.encoding import smart_str

from custom_user.tests_helper import create_user
from experiment.admin import ResearchProjectResource, ExperimentResource
from experiment.import_export import ImportExperiment, ExportExperiment, ExportExperiment2
from experiment.models import Keyword, GoalkeeperGameConfig, \
    Component, GoalkeeperGame, GoalkeeperPhase, GoalkeeperGameResults, \
    FileFormat, ExperimentResearcher, InformationType, Experiment, ResearchProject
from experiment.models import Group as ExperimentGroup
from configuration.models import LocalInstitution
from custom_user.models import Institution
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
        self.patient = UtilTests().create_patient_mock(changed_by=self.user)
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

        self.research_project = ObjectsFactory.create_research_project()
        self.experiment = ObjectsFactory.create_experiment(self.research_project)
        self.root = ObjectsFactory.create_component(self.experiment, 'block')
        information_type = InformationType.objects.create(name='it')
        self.component = ObjectsFactory.create_component(self.experiment, 'generic_data_collection',
                                                         kwargs={'it': information_type})
        self.componentconfig = ObjectsFactory.create_component_configuration(self.root, self.component)
        self.group = ObjectsFactory.create_group(self.experiment, experimental_protocol=self.root)
        self.client.login(username=user.username, password=passwd)

    def tearDown(self):
        self.client.logout()

    def test_GET_experiment_export_returns_zip_file(self):
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            response.get('Content-Disposition'),
            'attachment; filename=%s' % smart_str('experiment.zip')
        )
        file = io.BytesIO(response.content)
        zip_file = zipfile.ZipFile(file, 'r')
        self.assertIsNone(zip_file.testzip())
        
    def test_GET_experiment_export_returns_research_project_in_zip_file(self):
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        file = io.BytesIO(response.content)
        zip_file = zipfile.ZipFile(file, 'r')
        self.assertTrue(
            any('research_project.csv' in item for item in zip_file.namelist()),
            'research_project.csv not in %s' % str(zip_file.namelist())
        )

    def test_GET_experiment_export_returns_research_project_right_content(self):
        # TODO: testing only for headers, not for values (last is trickier, maybe later)

        # ResearchProject fields that have to be in csv file
        # TODO: get fields like in
        #  test_POST_experiment_import_file_import_experiment_create_model_object_with_right_content
        research_project_fields = ['title', 'description', 'start_date', 'end_date', 'keywords']

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        file = io.BytesIO(response.content)
        zip_file = zipfile.ZipFile(file, 'r')
        temp_dir = tempfile.mkdtemp()
        zip_file.extractall(temp_dir)
        with open(path.join(temp_dir, 'research_project.csv')) as f:
            # must have two lines (one for headers and one for values)
            self.assertEqual(len(f.readlines()), 2)
        with open(path.join(temp_dir, 'research_project.csv')) as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertSetEqual(set(headers), set(research_project_fields))

        shutil.rmtree(temp_dir)

    def test_GET_experiment_export_returns_experiment_in_zip_file(self):
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        file = io.BytesIO(response.content)
        zip_file = zipfile.ZipFile(file, 'r')
        self.assertTrue(
            any('experiment.csv' in item for item in zip_file.namelist()),
            'experiment.csv not in %s' % str(zip_file.namelist())
        )

    def test_GET_experiment_export_returns_experiment_right_content(self):
        # TODO: testing only for headers, not for values (last is trickier, maybe later)

        # Experiment fields that have to be in csv file
        # TODO: get fields like in
        #  test_POST_experiment_import_file_import_experiment_create_model_object_with_right_content
        experiment_fields = [
            'title', 'description', 'is_public', 'data_acquisition_is_concluded', 'source_code_url',
            'ethics_committee_project_url', 'ethics_committee_project_file'
        ]

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        file = io.BytesIO(response.content)
        zip_file = zipfile.ZipFile(file, 'r')
        temp_dir = tempfile.mkdtemp()
        zip_file.extractall(temp_dir)
        with open(path.join(temp_dir, 'experiment.csv')) as f:
            # must have two lines (one for headers and one for values)
            self.assertEqual(len(f.readlines()), 2)
        with open(path.join(temp_dir, 'experiment.csv')) as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertSetEqual(set(headers), set(experiment_fields))

        shutil.rmtree(temp_dir)

    def test_GET_experiment_export_returns_experiment_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file = ObjectsFactory.create_binary_file(temp_dir)
            with File(open(file.name, 'rb')) as f:
                self.experiment.ethics_committee_project_file.save('file.pdf', f)
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        file = io.BytesIO(response.content)
        zip_file = zipfile.ZipFile(file, 'r')
        file_path = self.experiment.ethics_committee_project_file.name
        self.assertTrue(
            any(file_path in item for item in zip_file.namelist()),
            '%s not in %s' % (file_path, str(zip_file.namelist()))
        )

    def test_GET_experiment_export_returns_groups_in_zip_file(self):
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        file = io.BytesIO(response.content)
        zip_file = zipfile.ZipFile(file, 'r')
        self.assertTrue(
            any('groups.csv' in item for item in zip_file.namelist()),
            'groups.csv not in %s' % str(zip_file.namelist())
        )

    def test_GET_experiment_export_returns_groups_right_contents(self):
        # TODO: testing only for headers, not for values (last is trickier, maybe later)

        # ResearchProject fields that have to be in csv file
        groups_fields = ['title', 'description', 'code', 'classification_of_diseases', 'experimental_protocol']

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        file = io.BytesIO(response.content)
        zip_file = zipfile.ZipFile(file, 'r')
        temp_dir = tempfile.mkdtemp()
        zip_file.extractall(temp_dir)
        with open(path.join(temp_dir, 'groups.csv')) as f:
            # must have two lines (one for headers and one for values)
            self.assertEqual(len(f.readlines()), 2)
        with open(path.join(temp_dir, 'groups.csv')) as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertSetEqual(set(headers), set(groups_fields))

        shutil.rmtree(temp_dir)

    def test_GET_experiment_export_returns_components_in_zip_file(self):
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        file = io.BytesIO(response.content)
        zip_file = zipfile.ZipFile(file, 'r')
        self.assertTrue(
            any('components.csv' in item for item in zip_file.namelist()),
            'components.csv not in %s' % str(zip_file.namelist())
        )

        self.assertTrue(
            any('componentsconfig.csv' in item for item in zip_file.namelist()),
            'componentsconfig.csv not in %s' % str(zip_file.namelist())
        )

    def test_GET_experiment_export_returns_components_right_contents(self):
        # TODO: testing only for headers, not for values (last is trickier, maybe later)

        # ResearchProject fields that have to be in csv file
        components_fields = ['id', 'identification', 'description',
                             'duration_value', 'duration_unit',
                             'experiment', 'component_type']

        components_config_fields = ['name', 'number_of_repetitions', 'interval_between_repetitions_value',
                                    'interval_between_repetitions_unit', 'component', 'parent', 'order',
                                    'random_position', 'requires_start_and_end_datetime']

        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        file = io.BytesIO(response.content)
        zip_file = zipfile.ZipFile(file, 'r')
        temp_dir = tempfile.mkdtemp()
        zip_file.extractall(temp_dir)

        with open(path.join(temp_dir, 'components.csv')) as f:
            # must have three lines (one for headers, one for the root component and one for the other component)
            self.assertEqual(len(f.readlines()), 3)

        with open(path.join(temp_dir, 'components.csv')) as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertSetEqual(set(headers), set(components_fields))

        with open(path.join(temp_dir, 'componentsconfig.csv')) as f:
            # must have two lines (one for headers and one for the component)
            self.assertEqual(len(f.readlines()), 2)

        with open(path.join(temp_dir, 'componentsconfig.csv')) as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertSetEqual(set(headers), set(components_config_fields))

        shutil.rmtree(temp_dir)

    def test_GET_experiment_export_removes_temporary_dirs(self):
        response = self.client.get(reverse('experiment_export', kwargs={'experiment_id': self.experiment.id}))
        # TODO: implement it!


class ImportExperimentTest(TestCase):

    def setUp(self):
        # create the groups of users and their permissions
        exec(open('add_initial_data.py').read())

        user, passwd = create_user(Group.objects.all())

        self.research_project = ObjectsFactory.create_research_project()
        self.experiment = ObjectsFactory.create_experiment(self.research_project)
        self.client.login(username=user.username, password=passwd)

    def tearDown(self):
        self.client.logout()

    @staticmethod
    def _create_csv_file(dir_, name):
        with open(path.join(dir_, name), 'w') as f:
            if name == 'research_project.csv':
                f.write('h1,h2,start_date\n')
                f.write('v1,v2,2011-11-11\n')
            return f

    def test_GET_experiment_import_file_uses_correct_template(self):
        response = self.client.get(reverse('experiment_import'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'experiment/experiment_import.html')

    def test_POST_experiment_import_file_has_bad_zip_file_redirects_with_error_message(self):
        temp_dir = tempfile.mkdtemp()
        dummy_file = ObjectsFactory.create_binary_file(temp_dir, 'experiment.zip')

        with open(dummy_file.name, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'zip_file': file}, follow=True)
        self.assertRedirects(response, reverse('experiment_import'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Not a zip file. Aborting import experiment.')

        shutil.rmtree(temp_dir)

    def test_POST_experiment_import_file_has_no_research_project_csv_file_redirects_with_error_message(self):
        temp_dir = tempfile.mkdtemp()
        dummy_file = ObjectsFactory.create_binary_file(temp_dir)
        temp_zip_dir = tempfile.mkdtemp()
        zip_file = ObjectsFactory.create_zipfile(temp_zip_dir, [dummy_file])

        with open(zip_file.filename, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'zip_file': file}, follow=True)
        self.assertRedirects(response, reverse('experiment_import'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(
            message, '%s not found in zip file. Aborting import experiment.' % ImportExperiment.RESEARCH_PROJECT_CSV
        )

        shutil.rmtree(temp_dir)
        shutil.rmtree(temp_zip_dir)

    def test_POST_experiment_import_file_has_no_experiment_csv_files_redirects_with_error_message(self):
        temp_dir = tempfile.mkdtemp()
        dummy_file = ObjectsFactory.create_binary_file(temp_dir, 'research_project.csv')
        temp_zip_dir = tempfile.mkdtemp()
        zip_file = ObjectsFactory.create_zipfile(temp_zip_dir, [dummy_file])

        with open(zip_file.filename, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'zip_file': file}, follow=True)
        self.assertRedirects(response, reverse('experiment_import'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(
            message, '%s not found in zip file. Aborting import experiment.' % ImportExperiment.EXPERIMENT_CSV
        )

        shutil.rmtree(temp_dir)
        shutil.rmtree(temp_zip_dir)

    def test_POST_experiment_import_file_import_bad_research_project_returns_error_message(self):
        temp_dir = tempfile.mkdtemp()
        dummy_csv1 = self._create_csv_file(temp_dir, 'research_project.csv')
        dummy_csv2 = ObjectsFactory.create_csv_file(temp_dir, 'experiment.csv')
        temp_zip_dir = tempfile.mkdtemp()
        zip_file = ObjectsFactory.create_zipfile(temp_zip_dir, [dummy_csv1, dummy_csv2])

        # redirect sys.stderr to avoid display error messages
        stderr_backup, sys.stderr = sys.stderr, open('/dev/null', 'w+')
        with open(zip_file.filename, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'zip_file': file}, follow=True)
        # restore sys.stderr
        sys.stderr.close()
        sys.stderr = stderr_backup

        self.assertRedirects(response, reverse('experiment_import'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(
            message, 'Bad %s file. Aborting import experiment.' % ImportExperiment.RESEARCH_PROJECT_CSV
        )

        shutil.rmtree(temp_dir)
        shutil.rmtree(temp_zip_dir)

    def test_POST_experiment_import_file_import_bad_experiment_returns_error_message(self):
        temp_dir = tempfile.mkdtemp()
        temp_zip_dir = tempfile.mkdtemp()

        dataset = ResearchProjectResource().export(id=self.research_project.id)
        dummy_csv = ObjectsFactory.create_csv_file(temp_dir, 'experiment.csv')
        temp_filename = path.join(temp_dir, ExportExperiment.RESEARCH_PROJECT_CSV)
        with open(temp_filename, 'w') as file:
            file.write(dataset.csv)
        zip_file = ObjectsFactory.create_zipfile(temp_zip_dir, [file, dummy_csv])

        # redirect sys.stderr to avoid display error messages
        stderr_backup, sys.stderr = sys.stderr, open('/dev/null', 'w+')
        with open(zip_file.filename, 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'zip_file': file}, follow=True)
        # restore sys.stderr
        sys.stderr.close()
        sys.stderr = stderr_backup

        self.assertRedirects(response, reverse('experiment_import'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(
            message, 'Bad %s file. Aborting import experiment.' % ImportExperiment.EXPERIMENT_CSV
        )

        shutil.rmtree(temp_dir)
        shutil.rmtree(temp_zip_dir)

    def test_POST_experiment_import_file_import_experiment_create_model_object_with_right_content(self):
        export = ExportExperiment(self.experiment)
        export.export_all()

        with open(path.join(export.temp_dir_zip, export.ZIP_FILE_NAME + '.zip'), 'rb') as file:
            response = self.client.post(reverse('experiment_import'), {'zip_file': file}, follow=True)

        self.assertRedirects(response, reverse('experiment_import'))
        new_research_project = ResearchProject.objects.last()
        new_experiment = Experiment.objects.last()

        # get ResearchProject fields except forward and reverse fields
        fields = set([f.name for f in ResearchProject._meta.get_fields() if not f.is_relation])
        # Excluded fields in ResearchProjectResource.Meta must be excluded
        # from comparison as they will be created
        fields -= set(ResearchProjectResource.Meta.exclude)

        for field in fields:
            self.assertEqual(getattr(self.research_project, field), getattr(new_research_project, field))

        # get ResearchProject fields except forward and reverse fields
        fields = set([f.name for f in Experiment._meta.get_fields() if not f.is_relation])
        # Excluded fields in ExperimentResource.Meta must be excluded
        # from comparison as they will be created
        fields -= set(ExperimentResource.Meta.exclude)

        for field in fields:
            self.assertEqual(
                getattr(self.experiment, field) or '', getattr(new_experiment, field) or ''
            )


class ExportExperimentTest2(TestCase):

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
        response = self.client.get(reverse('experiment_export2', kwargs={'experiment_id': self.experiment.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            response.get('Content-Disposition'),
            'attachment; filename=%s' % smart_str('experiment.json')
        )

    def test_GET_experiment_export_returns_json_file_wo_user_object(self):
        response = self.client.get(reverse('experiment_export2', kwargs={'experiment_id': self.experiment.id}))
        data = json.loads(response.content.decode('utf-8'))
        self.assertIsNone(next((item for item in data if item['model'] == 'auth.user'), None))


class ImportExperimentTest2(TestCase):

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

    def _assert_new_objects(self, old_objects_count):
        self.assertEqual(ResearchProject.objects.count(), old_objects_count['research_project'] + 1)
        self.assertEqual(Experiment.objects.count(), old_objects_count['experiment'] + 1)
        self.assertEqual(ExperimentGroup.objects.count(), old_objects_count['group'] + 1)

    def test_GET_experiment_import_file_uses_correct_template(self):
        response = self.client.get(reverse('experiment_import2'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'experiment/experiment_import2.html')
    
    def test_POST_experiment_import_file_has_not_file_redirects_with_warning_message(self):
        response = self.client.post(reverse('experiment_import2'), {'file': ''}, follow=True)
        self.assertRedirects(response, reverse('experiment_import2'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Please select a json file')

    def test_POST_experiment_import_file_has_bad_json_file_redirects_with_error_message(self):
        temp_dir = tempfile.mkdtemp()
        dummy_file = ObjectsFactory.create_csv_file(temp_dir, 'experiment.json')

        with open(dummy_file.name, 'rb') as file:
            response = self.client.post(reverse('experiment_import2'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('experiment_import2'))
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Bad json file. Aborting import experiment.')

        shutil.rmtree(temp_dir)

    def test_POST_experiment_import_file_creates_new_objects_and_returns_successful_message(self):
        export = ExportExperiment2(self.experiment)
        export.export_all()
        
        file_path = export.get_file_path()

        old_objects_count = {
            'research_project': ResearchProject.objects.count(),
            'experiment': Experiment.objects.count(),
            'group': ExperimentGroup.objects.count()
        }
        with open(file_path, 'rb') as file:
            response = self.client.post(reverse('experiment_import2'), {'file': file}, follow=True)
        self.assertRedirects(response, reverse('experiment_import2'))
        self._assert_new_objects(old_objects_count)
        message = str(list(response.context['messages'])[0])
        self.assertEqual(message, 'Experiment successfully imported. New study was created.')
